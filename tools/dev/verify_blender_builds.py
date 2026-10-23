#!/usr/bin/env python3
"""Re-verify Blender-generated assets (M1-QA-02, ADR 0005): rebuild them from assets_src/ in a
scratch copy of the repo with the pinned Blender, then compare every output with the committed file.

    python3 tools/dev/verify_blender_builds.py            # only jobs whose sources/outputs changed
    python3 tools/dev/verify_blender_builds.py --all      # every job
    python3 tools/dev/verify_blender_builds.py --job base_body --job asha
    python3 tools/dev/verify_blender_builds.py --list

Jobs are data: tools/dev/blender_builds.json. The working tree is never written: assets_src/ is
copied into a temporary root and each build writes there (the scripts resolve paths from their own
location). A committed output passes when the rebuild is byte-identical, or, for a job that declares
a "tolerance", when the glTF matches within it (named float attributes only, e.g. TANGENT). A job
with an "expected_failure" (a tracking task) is reported as KNOWN and does not fail the gate; once
it passes, the gate fails until the marker is removed. See docs/kb/qa/blender_builds.md.
"Changed" means touched since the merge-base with the base ref ($HYMN_BLENDER_BASE, else main or
origin/main), or modified in the working tree. With no base ref, every job runs.

Exit codes: 0 all verified (or nothing to do), 1 a mismatch or a failed build, 3 Blender missing or
not the pinned version (callers print SKIP). SIGTERM (e.g. from `timeout`) kills the running build.
"""
from __future__ import annotations

import argparse
import fnmatch
import hashlib
import json
import os
import shutil
import signal
import struct
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "tools" / "dev" / "blender_builds.json"
BLENDER_FLAGS = ["--background", "--factory-startup", "--python-exit-code", "1"]
DEFAULT_BASES = ["main", "origin/main"]
GLB_MAGIC = 0x46546C67
GLB_JSON_CHUNK = 0x4E4F534A
GLB_BIN_CHUNK = 0x004E4942
GL_FLOAT = 5126
EXIT_MISMATCH = 1
EXIT_NO_BLENDER = 3


# ---------------------------------------------------------------------------------------------
# Manifest and change detection
# ---------------------------------------------------------------------------------------------
def load_manifest(path: Path = MANIFEST) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    ids = [j["id"] for j in data["jobs"]]
    if len(ids) != len(set(ids)):
        raise ValueError(f"duplicate job ids in {path}")
    for job in data["jobs"]:
        for key in ("id", "sources", "outputs", "runs"):
            if not job.get(key):
                raise ValueError(f"job {job.get('id', '?')}: missing '{key}'")
        for run in job["runs"]:
            if run[0] != "{blender}":
                raise ValueError(f"job {job['id']}: every run starts with '{{blender}}'")
        known = job.get("expected_failure")
        if known is not None and not (known.get("task") and known.get("why")):
            raise ValueError(f"job {job['id']}: expected_failure needs 'task' and 'why'")
        tol = job.get("tolerance")
        if tol is not None and not (tol.get("attributes") and tol.get("why") and float(tol.get("abs", 0)) > 0):
            raise ValueError(f"job {job['id']}: tolerance needs 'abs' > 0, 'attributes' and 'why'")
    return data


def matches(path: str, patterns: list[str]) -> bool:
    """fnmatch where '**' spans directories and '*' does not."""
    for pat in patterns:
        if pat.endswith("/**"):
            if path.startswith(pat[:-2]):
                return True
        elif fnmatch.fnmatchcase(path, pat) and "/" not in path[len(pat.rsplit("/", 1)[0]) + 1:]:
            return True
    return False


def select_jobs(jobs: list[dict], changed: list[str] | None) -> list[dict]:
    """Jobs whose sources or outputs include a changed path (all jobs when changed is None)."""
    if changed is None:
        return list(jobs)
    return [j for j in jobs if any(matches(p, j["sources"] + j["outputs"]) for p in changed)]


def _git(*args: str) -> str:
    out = subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True, check=False)
    if out.returncode != 0:
        raise RuntimeError(out.stderr.strip())
    return out.stdout


def changed_paths(base: str | None) -> tuple[list[str] | None, str]:
    """Paths changed since merge-base(base, HEAD) plus working-tree changes; None = unknown."""
    candidates = [base] if base else DEFAULT_BASES
    for ref in candidates:
        try:
            mb = _git("merge-base", ref, "HEAD").strip()
        except RuntimeError:
            continue
        committed = _git("diff", "--name-only", mb, "HEAD").split()
        dirty = _git("diff", "--name-only", "HEAD").split()
        untracked = _git("ls-files", "--others", "--exclude-standard").split()
        return sorted(set(committed + dirty + untracked)), f"{ref} ({mb[:8]})"
    return None, "none found"


# ---------------------------------------------------------------------------------------------
# Comparison
# ---------------------------------------------------------------------------------------------
def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_glb(data: bytes) -> tuple[dict, bytes]:
    magic, _version, total = struct.unpack_from("<III", data, 0)
    if magic != GLB_MAGIC:
        raise ValueError("not a .glb")
    off, js, binc = 12, None, b""
    while off < total:
        length, kind = struct.unpack_from("<II", data, off)
        chunk = data[off + 8: off + 8 + length]
        if kind == GLB_JSON_CHUNK:
            js = json.loads(chunk)
        elif kind == GLB_BIN_CHUNK:
            binc = chunk
        off += 8 + length
    if js is None:
        raise ValueError("glb has no JSON chunk")
    return js, binc


def accessor_names(js: dict) -> dict[int, str]:
    """accessor index -> "<mesh>.<ATTRIBUTE>" (or "<mesh>.indices", "accessor <i>")."""
    names: dict[int, str] = {}
    for mesh in js.get("meshes", []):
        for prim in mesh.get("primitives", []):
            for attr, idx in prim.get("attributes", {}).items():
                names.setdefault(idx, f"{mesh.get('name', '?')}.{attr}")
            if "indices" in prim:
                names.setdefault(prim["indices"], f"{mesh.get('name', '?')}.indices")
    return names


def compare_glb(a: bytes, b: bytes, tolerance: dict | None) -> tuple[bool, str]:
    """Structural glTF compare. The JSON must be equal; buffer data must be equal, except float
    accessors of an attribute named in tolerance["attributes"] (e.g. TANGENT), which may differ by
    tolerance["abs"] (their accessor min/max too). Returns (ok, detail naming what differs)."""
    import numpy as np  # noqa: PLC0415 (only needed on a byte mismatch)

    tol = float((tolerance or {}).get("abs", 0.0))
    loose_attrs = set((tolerance or {}).get("attributes", []))
    ja, ba = read_glb(a)
    jb, bb = read_glb(b)
    names = accessor_names(ja)
    acc_a, acc_b = ja.get("accessors", []), jb.get("accessors", [])
    views = ja.get("bufferViews", [])

    def loose(i: int) -> bool:
        acc = acc_a[i]
        return (acc.get("componentType") == GL_FLOAT and "byteStride" not in views[acc.get("bufferView", 0)]
                and names.get(i, "").rsplit(".", 1)[-1] in loose_attrs)

    def strip(js: dict) -> dict:
        out = dict(js)
        out["accessors"] = [
            {k: v for k, v in acc.items() if not (k in ("min", "max") and loose(i))}
            for i, acc in enumerate(js.get("accessors", []))
        ]
        return out

    if len(acc_a) != len(acc_b) or strip(ja) != strip(jb):
        keys = sorted(k for k in set(ja) | set(jb) if strip(ja).get(k) != strip(jb).get(k)) if len(acc_a) == len(acc_b) else ["accessors"]
        if keys == ["accessors"] and len(acc_a) == len(acc_b):
            bad = [names.get(i, f"accessor {i}") for i, (x, y) in enumerate(zip(strip(ja)["accessors"], strip(jb)["accessors"])) if x != y]
            return False, f"accessor metadata differs: {', '.join(bad[:6])}"
        return False, f"glTF structure differs (keys: {', '.join(keys)})"
    view_users: dict[int, list[int]] = {}
    for i, acc in enumerate(acc_a):
        if "bufferView" in acc:
            view_users.setdefault(acc["bufferView"], []).append(i)
    strict_bad: list[str] = []
    worst, worst_name = 0.0, ""
    for v, view in enumerate(views):
        start = view.get("byteOffset", 0)
        end = start + view["byteLength"]
        if ba[start:end] == bb[start:end]:
            continue
        users = view_users.get(v, [])
        label = ", ".join(names.get(i, f"accessor {i}") for i in users) or f"bufferView {v}"
        if not users or not all(loose(i) for i in users):
            strict_bad.append(label)
            continue
        fa = np.frombuffer(ba[start:end], dtype="<f4").astype(np.float64)
        fb = np.frombuffer(bb[start:end], dtype="<f4").astype(np.float64)
        err = float(np.max(np.abs(fa - fb)))
        if err > worst:
            worst, worst_name = err, label
    for i, (x, y) in enumerate(zip(acc_a, acc_b)):
        if loose(i):
            for key in ("min", "max"):
                if key in x:
                    worst = max(worst, max(abs(p - q) for p, q in zip(x[key], y[key])))
    if strict_bad:
        return False, f"data differs: {', '.join(strict_bad[:6])}"
    if worst > tol:
        return False, f"{worst_name} differs by up to {worst:.3g} > tolerance {tol:g}"
    return True, f"within tolerance ({worst_name or 'min/max'} max error {worst:.3g} <= {tol:g})"


def compare_file(committed: Path, rebuilt: Path, tolerance: dict | None) -> tuple[str, str]:
    """Returns (status, detail); status is 'identical', 'tolerance' or 'DIFF'."""
    a, b = committed.read_bytes(), rebuilt.read_bytes()
    if a == b:
        return "identical", ""
    detail = f"sha256 {hashlib.sha256(a).hexdigest()[:12]} committed vs {hashlib.sha256(b).hexdigest()[:12]} rebuilt"
    if committed.suffix == ".glb":
        try:
            ok, why = compare_glb(a, b, tolerance)
        except (ValueError, struct.error, KeyError, IndexError) as exc:
            ok, why = False, f"cannot parse glb: {exc}"
        if ok:
            return "tolerance", why
        return "DIFF", f"{detail}; {why}"
    return "DIFF", detail


# ---------------------------------------------------------------------------------------------
# Building
# ---------------------------------------------------------------------------------------------
def find_blender(manifest: dict) -> str | None:
    env = os.environ.get("HYMN_BLENDER")
    if env:
        return env
    wrapper = Path.home() / ".cache" / "hymn" / f"blender-{manifest['blender_deb']}" / "blender"
    if wrapper.exists():
        return str(wrapper)
    return shutil.which("blender")


def blender_version(blender: str) -> str:
    out = subprocess.run([blender, "--background", "--factory-startup", "--version"],
                         capture_output=True, text=True, check=False)
    for line in (out.stdout + out.stderr).splitlines():
        if line.startswith("Blender "):
            return line.split()[1]
    return ""


def expand(run: list[str], blender: str, scratch: Path) -> list[str]:
    head = [blender, *BLENDER_FLAGS]
    return head + [arg.replace("{scratch}", str(scratch)) for arg in run[1:]]


def committed_outputs(job: dict, root: Path) -> list[str]:
    found = []
    for pat in job["outputs"]:
        parent = pat.rsplit("/", 1)[0]
        base = root / parent
        if base.is_dir():
            found += [f"{parent}/{p.name}" for p in base.iterdir() if p.is_file() and matches(f"{parent}/{p.name}", [pat])]
    return sorted(set(found))


def run_job(job: dict, blender: str, manifest: dict, log_dir: Path, timeout_s: float, keep: Path | None = None) -> dict:
    t0 = time.monotonic()
    result = {"id": job["id"], "ok": True, "files": [], "error": "", "seconds": 0.0}
    with tempfile.TemporaryDirectory(prefix=f"hymn_blender_{job['id']}_") as tmp:
        sandbox = Path(tmp) / "repo"
        scratch = Path(tmp) / "scratch"
        scratch.mkdir()
        for rel in manifest["copy_into_sandbox"]:
            shutil.copytree(ROOT / rel, sandbox / rel, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
        for pat in job["outputs"]:
            (sandbox / pat.rsplit("/", 1)[0]).mkdir(parents=True, exist_ok=True)
        log = log_dir / f"blender_{job['id']}.log"
        with log.open("w", encoding="utf-8") as fh:
            for run in job["runs"]:
                cmd = expand(run, blender, scratch)
                fh.write("$ " + " ".join(cmd) + "\n")
                fh.flush()
                left = timeout_s - (time.monotonic() - t0)
                try:
                    proc = subprocess.run(cmd, cwd=sandbox, stdout=fh, stderr=subprocess.STDOUT,
                                          timeout=max(left, 1.0), check=False)
                except subprocess.TimeoutExpired:
                    result.update(ok=False, error=f"timed out after {timeout_s:.0f} s (log: {log})")
                    break
                if proc.returncode != 0:
                    result.update(ok=False, error=f"build exited {proc.returncode} (log: {log})")
                    break
        if result["ok"]:
            want = committed_outputs(job, ROOT)
            got = committed_outputs(job, sandbox)
            for rel in sorted(set(want) | set(got)):
                if rel not in got:
                    status, detail = "DIFF", "committed but not produced by the build"
                elif rel not in want:
                    status, detail = "DIFF", "produced by the build but not committed"
                else:
                    status, detail = compare_file(ROOT / rel, sandbox / rel, job.get("tolerance"))
                result["files"].append({"path": rel, "status": status, "detail": detail})
                if status == "DIFF":
                    result["ok"] = False
                if keep is not None and rel in got:
                    (keep / rel).parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(sandbox / rel, keep / rel)
            if not want:
                result.update(ok=False, error="no committed outputs match the job's 'outputs'")
    result["seconds"] = round(time.monotonic() - t0, 1)
    return result


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--all", action="store_true", help="run every job, changed or not")
    ap.add_argument("--job", action="append", default=[], help="run this job (repeatable)")
    ap.add_argument("--base", default=os.environ.get("HYMN_BLENDER_BASE"), help="base ref for change detection")
    ap.add_argument("--timeout", type=float, default=float(os.environ.get("HYMN_BLENDER_JOB_TIMEOUT", "900")),
                    help="seconds per job (default 900, $HYMN_BLENDER_JOB_TIMEOUT)")
    ap.add_argument("--log-dir", type=Path, default=Path(os.environ.get("TMPDIR", tempfile.gettempdir())))
    ap.add_argument("--report", type=Path, help="write a JSON report here")
    ap.add_argument("--keep", type=Path, help="copy the rebuilt outputs here (diagnosis)")
    ap.add_argument("--list", action="store_true")
    args = ap.parse_args(argv)
    manifest = load_manifest()
    jobs = manifest["jobs"]
    if args.list:
        for j in jobs:
            print(f"{j['id']:<12} {j.get('owner', ''):<12} {', '.join(j['outputs'])}")
        return 0
    if args.job:
        unknown = sorted(set(args.job) - {j["id"] for j in jobs})
        if unknown:
            ap.error(f"unknown job(s): {', '.join(unknown)}")
        todo = [j for j in jobs if j["id"] in args.job]
    elif args.all:
        todo = list(jobs)
    else:
        changed, base = changed_paths(args.base)
        todo = select_jobs(jobs, changed)
        print(f"base ref: {base}; " + ("no base ref, running every job" if changed is None
                                         else f"{len(changed)} changed path(s)"))
    if not todo:
        print("no Blender job touched by this change: nothing to rebuild")
        return 0
    blender = find_blender(manifest)
    if not blender:
        print("Blender not found (python3 tools/dev/fetch_blender.py, or set HYMN_BLENDER)")
        return EXIT_NO_BLENDER
    version = blender_version(blender)
    if version != manifest["blender_version"]:
        print(f"Blender {version or '?'} at {blender} is not the pinned {manifest['blender_version']}")
        return EXIT_NO_BLENDER
    args.log_dir.mkdir(parents=True, exist_ok=True)
    print(f"Blender {version}: {', '.join(j['id'] for j in todo)}")
    results, failed = [], 0
    for job in todo:
        res = run_job(job, blender, manifest, args.log_dir, args.timeout, args.keep)
        results.append(res)
        counts: dict[str, int] = {}
        for f in res["files"]:
            counts[f["status"]] = counts.get(f["status"], 0) + 1
        summary = ", ".join(f"{n} {s}" for s, n in sorted(counts.items()))
        known = job.get("expected_failure")
        res["expected_failure"] = bool(known)
        tag = "ok  " if res["ok"] else ("KNOWN" if known else "FAIL")
        print(f"BLENDER {tag} {res['id']}  {res['seconds']} s  {summary}")
        if res["error"]:
            print(f"    {res['error']}")
        for f in res["files"]:
            if f["status"] != "identical":
                print(f"    {f['status']:<9} {f['path']}  {f['detail']}")
        if known and res["ok"]:
            # Passing now: make the author drop the marker so a later regression is caught again.
            print(f"    passes now: remove its expected_failure ({known['task']}) from {MANIFEST.relative_to(ROOT)}")
            failed += 1
        elif known:
            print(f"    expected failure, tracked in {known['task']}: {known['why']}")
        elif not res["ok"]:
            failed += 1
    if args.report:
        args.report.write_text(json.dumps({"blender": version, "jobs": results}, indent=2) + "\n", encoding="utf-8")
    print(f"Blender builds: {len(results)} job(s), {failed} failed, {sum(r['seconds'] for r in results):.0f} s")
    return EXIT_MISMATCH if failed else 0


def _on_sigterm(_signum: int, _frame: object) -> None:
    # subprocess.run kills its child on any exception, so this stops the running Blender too.
    raise KeyboardInterrupt("SIGTERM")


if __name__ == "__main__":
    signal.signal(signal.SIGTERM, _on_sigterm)
    sys.exit(main())
