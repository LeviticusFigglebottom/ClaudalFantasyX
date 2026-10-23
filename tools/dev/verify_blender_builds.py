#!/usr/bin/env python3
"""Re-verify Blender-generated assets (M1-QA-02, ADR 0005): rebuild them from assets_src/ in a
scratch copy of the repo with the pinned Blender, then compare every output with the committed file.

    python3 tools/dev/verify_blender_builds.py            # only jobs whose sources/outputs changed
    python3 tools/dev/verify_blender_builds.py --all      # every job
    python3 tools/dev/verify_blender_builds.py --job base_body --job asha
    python3 tools/dev/verify_blender_builds.py --list

Jobs are data: tools/dev/blender_builds.json. The working tree is never written: assets_src/ is
copied into a temporary root and each build writes there (the scripts resolve paths from their own
location). A run starts with "{blender}" (a Blender script) or "{python}" (a plain numpy/Pillow
step that follows a Blender run in the same job, e.g. Asha's textures). A committed output passes
when the rebuild is byte-identical, or, for a job that declares a "tolerance", when the glTF matches
within it (named float attributes only, e.g. TANGENT). A job with an "expected_failure" (a tracking
task plus the failure's signature: a build error whose log holds a given line, or a mismatch of
exactly the listed files and glTF accessors) is reported as KNOWN and does not fail the gate. A
failure with any other signature fails, and so does a job that passes again, until the marker is
removed. Before any build, a coverage check (no Blender) fails the gate when a tracked .glb under
assets/ or a bpy script under assets_src/ belongs to no job and is not listed in "coverage_exempt".
See docs/kb/qa/blender_builds.md.
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
import re
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
RUNNERS = ("{blender}", "{python}")
KIND_BUILD_ERROR = "build_error"
KIND_MISMATCH = "mismatch"
# A Python file that uses Blender's API: it must be under some job's sources (or exempt).
BPY_IMPORT = re.compile(r"^\s*(?:import|from)\s+(?:bpy|bmesh|mathutils)\b", re.MULTILINE)
# Signatures of non-glTF differences (a glTF difference is the list of accessors that differ).
SIG_NOT_PRODUCED = "<not produced>"
SIG_NOT_COMMITTED = "<not committed>"
SIG_BYTES = "<bytes>"


# ---------------------------------------------------------------------------------------------
# Manifest and change detection
# ---------------------------------------------------------------------------------------------
def _check_known(job: dict) -> None:
    known = job.get("expected_failure")
    if known is None:
        return
    jid = job["id"]
    if not (known.get("task") and known.get("why")):
        raise ValueError(f"job {jid}: expected_failure needs 'task' and 'why'")
    kind = known.get("kind")
    if kind == KIND_BUILD_ERROR:
        if not isinstance(known.get("log_contains"), str) or not known["log_contains"].strip():
            raise ValueError(f"job {jid}: a build_error expected_failure needs 'log_contains' (a line of its log)")
    elif kind == KIND_MISMATCH:
        differs = known.get("differs")
        if not isinstance(differs, dict) or not differs or not all(
                isinstance(v, list) and v and all(isinstance(s, str) for s in v) for v in differs.values()):
            raise ValueError(f"job {jid}: a mismatch expected_failure needs 'differs': {{path: [accessor, ...]}}")
        stray = [p for p in differs if not matches(p, job["outputs"])]
        if stray:
            raise ValueError(f"job {jid}: expected_failure lists paths outside its outputs: {', '.join(stray)}")
    else:
        raise ValueError(f"job {jid}: expected_failure 'kind' must be '{KIND_BUILD_ERROR}' or '{KIND_MISMATCH}'")


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
            if run[0] not in RUNNERS:
                raise ValueError(f"job {job['id']}: every run starts with '{{blender}}' or '{{python}}'")
        if job["runs"][0][0] != "{blender}":
            raise ValueError(f"job {job['id']}: the first run must be a Blender run")
        _check_known(job)
        threads = job.get("threads", data.get("default_threads", 0))
        if not isinstance(threads, int) or isinstance(threads, bool) or threads < 0:
            raise ValueError(f"job {job['id']}: threads must be an int >= 0 (0 = Blender's default)")
        tol = job.get("tolerance")
        if tol is not None and not (tol.get("attributes") and tol.get("why") and float(tol.get("abs", 0)) > 0):
            raise ValueError(f"job {job['id']}: tolerance needs 'abs' > 0, 'attributes' and 'why'")
    for ex in data.get("coverage_exempt", []):
        if not (ex.get("path") and ex.get("why")):
            raise ValueError("coverage_exempt entries need 'path' and 'why'")
    return data


def run_script(run: list[str]) -> str:
    """The script a run executes: the arg after --python for Blender, the first arg for {python}."""
    if run[0] == "{python}":
        return run[1]
    return run[run.index("--python") + 1]


def _tracked(root: Path, top: str, suffix: str) -> list[str]:
    """Files under `top` ending in `suffix` that git tracks or would add (untracked, not ignored);
    every file on disk when `root` is not a git checkout."""
    try:
        # A pathspec '*' spans directories, so this is every <top>/**/*<suffix>.
        out = subprocess.run(["git", "ls-files", "--cached", "--others", "--exclude-standard", "--", f"{top}/*{suffix}"],
                             cwd=root, capture_output=True, text=True, check=True).stdout.splitlines()
    except (OSError, subprocess.CalledProcessError):
        out = [p.relative_to(root).as_posix() for p in (root / top).rglob(f"*{suffix}")]
    return sorted({p for p in out if (root / p).is_file()})


def coverage_errors(manifest: dict, root: Path = ROOT) -> list[str]:
    """Every .glb under assets/ must be some job's output, and every assets_src/ script that imports
    Blender's API must be some job's source, unless "coverage_exempt" lists it with a reason. Without
    this, a new generator would go unverified and nothing would say so (M1-QA-06)."""
    jobs = manifest["jobs"]
    exempt = [ex["path"] for ex in manifest.get("coverage_exempt", [])]
    outputs = [o for j in jobs for o in j["outputs"]]
    sources = [s for j in jobs for s in j["sources"]]
    errs = []
    for rel in _tracked(root, "assets", ".glb"):
        if not matches(rel, outputs) and not matches(rel, exempt):
            errs.append(f"{rel}: no job in {MANIFEST.name} rebuilds it (add a job, or a coverage_exempt entry with a why)")
    for rel in _tracked(root, "assets_src", ".py"):
        if matches(rel, sources) or matches(rel, exempt):
            continue
        try:
            text = (root / rel).read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        if BPY_IMPORT.search(text):
            errs.append(f"{rel}: imports Blender's API but no job lists it in 'sources' (add it, or a coverage_exempt entry)")
    return errs


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


def glb_differences(a: bytes, b: bytes, tolerance: dict | None) -> list[str]:
    """Every part of two .glb files that differs, as a sorted signature: "<mesh>.<ATTRIBUTE>" (or
    "accessor <i>") for each accessor whose metadata or data differ (a tolerated attribute only when
    it is beyond the tolerance), "<json:key>" for any other top-level glTF key, and
    "<accessor count>". compare_glb stops at the first kind of difference; a known failure needs all
    of them, so that a new one is not hidden behind it."""
    import numpy as np  # noqa: PLC0415

    tol = float((tolerance or {}).get("abs", 0.0))
    loose_attrs = set((tolerance or {}).get("attributes", []))
    ja, ba = read_glb(a)
    jb, bb = read_glb(b)
    names = accessor_names(ja)
    acc_a, acc_b = ja.get("accessors", []), jb.get("accessors", [])
    views_a, views_b = ja.get("bufferViews", []), jb.get("bufferViews", [])
    out = {f"<json:{k}>" for k in set(ja) | set(jb)
           if k not in ("accessors", "bufferViews", "buffers") and ja.get(k) != jb.get(k)}
    if len(acc_a) != len(acc_b):
        out.add("<accessor count>")

    def data(js_views: list, blob: bytes, acc: dict) -> bytes:
        if "bufferView" not in acc or acc["bufferView"] >= len(js_views):
            return b""
        v = js_views[acc["bufferView"]]
        start = v.get("byteOffset", 0) + acc.get("byteOffset", 0)
        return blob[start: v.get("byteOffset", 0) + v["byteLength"]]

    for i, (x, y) in enumerate(zip(acc_a, acc_b)):
        name = names.get(i, f"accessor {i}")
        loose = x.get("componentType") == GL_FLOAT and name.rsplit(".", 1)[-1] in loose_attrs
        da, db = data(views_a, ba, x), data(views_b, bb, y)
        meta_x = {k: v for k, v in x.items() if k not in ("bufferView", "byteOffset") and not (loose and k in ("min", "max"))}
        meta_y = {k: v for k, v in y.items() if k not in ("bufferView", "byteOffset") and not (loose and k in ("min", "max"))}
        if meta_x != meta_y or len(da) != len(db):
            out.add(name)
        elif da != db:
            if not loose:
                out.add(name)
            else:
                fa = np.frombuffer(da[: len(da) // 4 * 4], dtype="<f4").astype(np.float64)
                fb = np.frombuffer(db[: len(db) // 4 * 4], dtype="<f4").astype(np.float64)
                if fa.size and float(np.max(np.abs(fa - fb))) > tol:
                    out.add(name)
        elif loose and any(abs(p - q) > tol for k in ("min", "max") if k in x for p, q in zip(x[k], y.get(k, []))):
            out.add(name)
    return sorted(out)


def compare_file(committed: Path, rebuilt: Path, tolerance: dict | None) -> tuple[str, str, list[str]]:
    """Returns (status, detail, signature); status is 'identical', 'tolerance' or 'DIFF', and the
    signature (for DIFF) names what differs: the glTF accessors, or "<bytes>" for other files."""
    a, b = committed.read_bytes(), rebuilt.read_bytes()
    if a == b:
        return "identical", "", []
    detail = f"sha256 {hashlib.sha256(a).hexdigest()[:12]} committed vs {hashlib.sha256(b).hexdigest()[:12]} rebuilt"
    if committed.suffix == ".glb":
        try:
            ok, why = compare_glb(a, b, tolerance)
            sig = [] if ok else glb_differences(a, b, tolerance)
        except (ValueError, struct.error, KeyError, IndexError) as exc:
            ok, why, sig = False, f"cannot parse glb: {exc}", [SIG_BYTES]
        if ok:
            return "tolerance", why, []
        return "DIFF", f"{detail}; {why}", sig or [SIG_BYTES]
    return "DIFF", detail, [SIG_BYTES]


def known_verdict(known: dict, res: dict, log_text: str) -> tuple[bool, str]:
    """Whether a failing job fails the way its expected_failure says. (True, why) is KNOWN;
    (False, why) is a new failure signature, which fails the gate."""
    if known["kind"] == KIND_BUILD_ERROR:
        if not res["error"].startswith("build exited"):
            return False, f"expected a build error, got: {res['error'] or 'a mismatch'}"
        if known["log_contains"] not in log_text:
            return False, f"the build failed, but its log does not contain the known line {known['log_contains']!r}"
        return True, "the build fails with the known error"
    if res["error"]:
        return False, f"expected a mismatch, got: {res['error']}"
    got = {f["path"]: f.get("signature", []) for f in res["files"] if f["status"] == "DIFF"}
    want = {p: sorted(v) for p, v in known["differs"].items()}
    problems = []
    for path in sorted(set(got) | set(want)):
        if path not in got:
            problems.append(f"{path} no longer differs")
        elif path not in want:
            problems.append(f"{path} differs too ({', '.join(got[path])})")
        elif got[path] != want[path]:
            new = sorted(set(got[path]) - set(want[path]))
            gone = sorted(set(want[path]) - set(got[path]))
            problems.append(f"{path}: " + "; ".join(
                ([f"now also differs in {', '.join(new)}"] if new else []) + ([f"no longer in {', '.join(gone)}"] if gone else [])))
    if problems:
        return False, "the mismatch changed: " + " | ".join(problems)
    return True, "the same files and accessors differ as recorded"


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


def job_threads(job: dict, manifest: dict) -> int:
    """Blender's thread count for a job: its own "threads", else the manifest's "default_threads"."""
    return int(job.get("threads", manifest.get("default_threads", 0)))


def expand(run: list[str], blender: str, scratch: Path, threads: int = 0) -> list[str]:
    """argv for one run. A Blender run gets `--threads N` when threads > 0 (M1-QA-06): Blender's
    default is the host's CPU count, and some of its results depend on it (see blender_builds.md)."""
    if run[0] == "{python}":
        head = [sys.executable]
    else:
        head = [blender, *(["--threads", str(threads)] if threads > 0 else []), *BLENDER_FLAGS]
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
                cmd = expand(run, blender, scratch, job_threads(job, manifest))
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
                    status, detail, sig = "DIFF", "committed but not produced by the build", [SIG_NOT_PRODUCED]
                elif rel not in want:
                    status, detail, sig = "DIFF", "produced by the build but not committed", [SIG_NOT_COMMITTED]
                else:
                    status, detail, sig = compare_file(ROOT / rel, sandbox / rel, job.get("tolerance"))
                entry = {"path": rel, "status": status, "detail": detail}
                if status == "DIFF":
                    entry["signature"] = sig
                result["files"].append(entry)
                if status == "DIFF":
                    result["ok"] = False
                if keep is not None and rel in got:
                    (keep / rel).parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(sandbox / rel, keep / rel)
            if not want:
                result.update(ok=False, error="no committed outputs match the job's 'outputs'")
    result["seconds"] = round(time.monotonic() - t0, 1)
    result["log"] = str(log)
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
    ap.add_argument("--coverage-only", action="store_true", help="only check that every .glb and bpy script has a job")
    args = ap.parse_args(argv)
    manifest = load_manifest()
    jobs = manifest["jobs"]
    if args.list:
        for j in jobs:
            print(f"{j['id']:<12} {j.get('owner', ''):<12} {', '.join(j['outputs'])}")
        return 0
    uncovered = coverage_errors(manifest)
    for e in uncovered:
        print(f"BLENDER UNCOVERED {e}")
    if args.coverage_only:
        print(f"Blender coverage: {len(uncovered)} uncovered")
        return EXIT_MISMATCH if uncovered else 0
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
        return EXIT_MISMATCH if uncovered else 0
    blender = find_blender(manifest)
    if not blender:
        print("Blender not found (python3 tools/dev/fetch_blender.py, or set HYMN_BLENDER)")
        return EXIT_MISMATCH if uncovered else EXIT_NO_BLENDER
    version = blender_version(blender)
    if version != manifest["blender_version"]:
        print(f"Blender {version or '?'} at {blender} is not the pinned {manifest['blender_version']}")
        return EXIT_MISMATCH if uncovered else EXIT_NO_BLENDER
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
        as_known, why = False, ""
        if known and not res["ok"]:
            log_text = Path(res["log"]).read_text(encoding="utf-8", errors="replace") if Path(res["log"]).exists() else ""
            as_known, why = known_verdict(known, res, log_text)
        res["known"] = as_known
        tag = "ok  " if res["ok"] else ("KNOWN" if as_known else "FAIL")
        print(f"BLENDER {tag} {res['id']}  {res['seconds']} s  {summary}")
        if res["error"]:
            print(f"    {res['error']}")
        for f in res["files"]:
            if f["status"] != "identical":
                sig = f"  [{', '.join(f['signature'])}]" if f.get("signature") else ""
                print(f"    {f['status']:<9} {f['path']}  {f['detail']}{sig}")
        if known and res["ok"]:
            # Passing now: make the author drop the marker so a later regression is caught again.
            print(f"    passes now: remove its expected_failure ({known['task']}) from {MANIFEST.relative_to(ROOT)}")
            failed += 1
        elif as_known:
            print(f"    expected failure, tracked in {known['task']} ({why}): {known['why']}")
        elif known:
            print(f"    NEW failure signature, not the one tracked in {known['task']}: {why}")
            failed += 1
        elif not res["ok"]:
            failed += 1
    if args.report:
        report = {"blender": version, "uncovered": uncovered, "jobs": results}
        args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"Blender builds: {len(results)} job(s), {failed} failed, {len(uncovered)} uncovered, "
          f"{sum(r['seconds'] for r in results):.0f} s")
    return EXIT_MISMATCH if failed or uncovered else 0


def _on_sigterm(_signum: int, _frame: object) -> None:
    # subprocess.run kills its child on any exception, so this stops the running Blender too.
    raise KeyboardInterrupt("SIGTERM")


if __name__ == "__main__":
    signal.signal(signal.SIGTERM, _on_sigterm)
    sys.exit(main())
