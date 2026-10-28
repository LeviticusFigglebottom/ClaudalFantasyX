"""A prototype of ADR 0172 (proposed): render the shipped audio at build time from its sources instead of committing it.

Nothing uses this yet; assets/audio/ stays committed (ADR 0171). It answers the ADR's questions with numbers:
how long a cold build takes on 4 CPUs, what a source change costs, and whether a render on another machine gives the
committed bytes.

    --write-manifest M   hash every file render_all.py's JOBS name, as committed, into M, with each job's input key
    --ensure             make every job's files exist under --out-root with the manifest's sha256: a file already
                         there and matching is kept; otherwise the job is rendered (or taken from the cache), in
                         parallel (--jobs, default 4), and checked against the manifest
    --plan               print which jobs --ensure would render and why, without rendering

A job's input key is the sha256 of its source and of every repo-local Python module it imports, followed through
assets_src/sfx, assets_src/music and tools/audio (synth/ included), plus the numpy version and the ffmpeg version line:
a change to synth/dsp.py re-renders every job that imports it and nothing else. The cache is
$HYMN_AUDIO_CACHE (default ~/.cache/hymn-undertow/audio_render)/<key>/.

Example (a cold build of the music into a scratch tree):
    python3 tools/audio/build_render.py --write-manifest $S/manifest.json
    python3 tools/audio/build_render.py --ensure --manifest $S/manifest.json --out-root $S/tree --only assets_src/music
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from concurrent.futures import ProcessPoolExecutor, as_completed

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)

SEARCH = [os.path.join(ROOT, d) for d in ("assets_src/sfx", "assets_src/music", "tools/audio")]
DEFAULT_CACHE = os.path.join(os.path.expanduser("~"), ".cache", "hymn-undertow", "audio_render")


def _jobs() -> list[tuple]:
    import render_all
    return list(render_all.JOBS)


def _sha_file(path: str) -> str:
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def _resolve(name: str, near: str) -> str | None:
    """The repo-local file a dotted import names (synth.dsp -> tools/audio/synth/dsp.py), or None (numpy, os)."""
    rel = name.replace(".", os.sep)
    for d in [near] + SEARCH:
        for cand in (os.path.join(d, rel + ".py"), os.path.join(d, rel, "__init__.py")):
            if os.path.isfile(cand):
                return os.path.abspath(cand)
    return None


def closure(src: str) -> list[str]:
    """src and every repo-local module it imports, transitively, sorted (repo-relative)."""
    seen: set[str] = set()
    todo = [os.path.abspath(os.path.join(ROOT, src))]
    while todo:
        path = todo.pop()
        if path in seen:
            continue
        seen.add(path)
        with open(path, encoding="utf-8") as f:
            tree = ast.parse(f.read(), path)
        near = os.path.dirname(path)
        for node in ast.walk(tree):
            names: list[str] = []
            if isinstance(node, ast.Import):
                names = [a.name for a in node.names]
            elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
                names = [node.module] + [f"{node.module}.{a.name}" for a in node.names]
            for n in names:
                hit = _resolve(n, near)
                if hit and hit not in seen:
                    todo.append(hit)
    return sorted(os.path.relpath(p, ROOT) for p in seen)


def toolchain() -> str:
    import numpy
    ff = shutil.which("ffmpeg")
    line = subprocess.run([ff, "-version"], capture_output=True, text=True).stdout.splitlines()[0] if ff else "none"
    return f"numpy {numpy.__version__}; {line}; python {sys.version_info.major}.{sys.version_info.minor}"


def input_key(src: str, chain: str) -> str:
    h = hashlib.sha256(chain.encode())
    for rel in closure(src):
        h.update(rel.encode() + b"\0" + _sha_file(os.path.join(ROOT, rel)).encode())
    return h.hexdigest()


def write_manifest(path: str) -> dict:
    chain = toolchain()
    out = {"version": 1, "toolchain": chain, "jobs": {}}
    for src, rel_dir, files, _kind in _jobs():
        out["jobs"][src] = {"key": input_key(src, chain), "inputs": closure(src),
                            "files": {os.path.join(rel_dir, f): _sha_file(os.path.join(ROOT, rel_dir, f))
                                      for f in files}}
    with open(path, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)
        f.write("\n")
    return out


def _render_into(job: tuple, dest: str) -> float:
    """Render one job into dest in this (worker) process; seconds taken."""
    import render_all
    src, _rel_dir, files, kind = job
    t0 = time.monotonic()
    render_all._render_job(src, dest, files, kind)
    return time.monotonic() - t0


def _needs(row: dict, out_root: str) -> list[str]:
    """The manifest files missing or different under out_root."""
    bad = []
    for rel, sha in row["files"].items():
        p = os.path.join(out_root, rel)
        if not os.path.isfile(p) or _sha_file(p) != sha:
            bad.append(rel)
    return bad


def ensure(manifest: dict, out_root: str, cache: str, workers: int, only: str = "", plan: bool = False) -> int:
    chain = toolchain()
    if chain != manifest["toolchain"]:
        print(f"toolchain differs from the manifest's:\n  here      {chain}\n  manifest  {manifest['toolchain']}")
    todo, problems = [], 0
    for job in _jobs():
        src, rel_dir, files, _kind = job
        if only and only not in src:
            continue
        row = manifest["jobs"].get(src)
        if row is None:
            print(f"NOT IN MANIFEST {src}")
            problems += 1
            continue
        if not _needs(row, out_root):
            continue
        key = input_key(src, chain)
        if key != row["key"]:
            print(f"STALE {src}: its sources changed since the manifest (write it again)")
        hit = os.path.join(cache, key)
        if all(os.path.isfile(os.path.join(hit, f)) for f in files):
            if not plan:
                _place(hit, files, os.path.join(out_root, rel_dir))
            print(f"cache {src}")
            continue
        todo.append((job, hit))
        print(f"render {src}")
    if plan or not todo:
        return problems
    t0 = time.monotonic()
    busy = 0.0
    with ProcessPoolExecutor(max_workers=workers, max_tasks_per_child=1) as ex:  # each job in a fresh process
        futs = {}
        for job, hit in sorted(todo, key=lambda jh: -_cost_hint(jh[0])):
            tmp = tempfile.mkdtemp(prefix="hymn_render_")
            futs[ex.submit(_render_into, job, tmp)] = (job, hit, tmp)
        for fut in as_completed(futs):
            job, hit, tmp = futs[fut]
            src, rel_dir, files, _kind = job
            sec = fut.result()
            busy += sec
            os.makedirs(hit, exist_ok=True)
            _place(tmp, files, hit)
            shutil.rmtree(tmp, ignore_errors=True)
            _place(hit, files, os.path.join(out_root, rel_dir))
            row = manifest["jobs"][src]
            drift = _needs(row, out_root)
            problems += len(drift)
            print(f"{sec:7.1f}s {src}" + (f"  DIFFERENT from the manifest: {', '.join(drift)}" if drift else ""),
                  flush=True)
    wall = time.monotonic() - t0
    print(f"{len(todo)} jobs: {wall:.0f} s wall on {workers} workers, {busy:.0f} s of job time")
    return problems


def _cost_hint(job: tuple) -> int:
    """Longest first, so the pool does not end on one long cue: music is the slow kind."""
    return {"music_loop": 3, "music": 2, "ambience_loop": 2}.get(job[3], 1)


def _place(src_dir: str, files: list[str], dest_dir: str) -> None:
    for f in files:
        d = os.path.join(dest_dir, f)
        os.makedirs(os.path.dirname(d), exist_ok=True)
        shutil.copyfile(os.path.join(src_dir, f), d)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--write-manifest", metavar="PATH")
    ap.add_argument("--ensure", action="store_true")
    ap.add_argument("--plan", action="store_true")
    ap.add_argument("--manifest", metavar="PATH")
    ap.add_argument("--out-root", default=ROOT, help="the tree the files land in (default: the repo)")
    ap.add_argument("--cache", default=os.environ.get("HYMN_AUDIO_CACHE", DEFAULT_CACHE))
    ap.add_argument("--jobs", type=int, default=4)
    ap.add_argument("--only", default="", help="only the jobs whose source path contains this text")
    a = ap.parse_args()
    if a.write_manifest:
        m = write_manifest(a.write_manifest)
        print(f"{a.write_manifest}: {len(m['jobs'])} jobs, {sum(len(r['files']) for r in m['jobs'].values())} files")
        return 0
    if not a.manifest or not (a.ensure or a.plan):
        ap.error("--write-manifest PATH, or --ensure/--plan with --manifest PATH")
    with open(a.manifest, encoding="utf-8") as f:
        manifest = json.load(f)
    return 1 if ensure(manifest, a.out_root, a.cache, a.jobs, a.only, a.plan) else 0


if __name__ == "__main__":
    sys.exit(main())
