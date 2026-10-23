#!/usr/bin/env python3
"""Reproduce the vendored MPFB2 CC0 data subset (M1-CHR-03, ADR 0021).

    python3 tools/fetch_mpfb2.py            # fetch the pinned commit and (re)write the vendored files
    python3 tools/fetch_mpfb2.py --check    # verify the vendored files against MANIFEST.json (no network)

Only **asset data** is copied: the base mesh, the targets, the Rigify weights and three uv-layer
face sets, which MPFB2's LICENSE.md (section C) and LICENSE.ASSETS.md release under CC0 1.0.
No MPFB2 program code (GPLv3: every .py, shell script and configuration file) is copied, read
or imported by anything in this repository; our own readers are in
assets_src/characters/base_body/mpfb_data.py.

The clone goes to a temporary directory outside the repository and is deleted afterwards.
Files over the 5 MB plain-blob cap (ADR 0005) are stored gzip-compressed, deterministically
(no timestamp, no file name in the header), with `.gz` appended; MANIFEST.json records the
sha256 of both the upstream file and the stored file.
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import io
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / "assets_src" / "third_party" / "mpfb2"
REPO = "https://github.com/makehumancommunity/mpfb2"
COMMIT = "b1a2dc98776da9d1eea751b159d42cf61778fe2e"  # main, 2026-10-20
DATA_PREFIX = "src/mpfb/data/"
MAX_PLAIN = 5 * 1024 * 1024

LICENSE_FILES = ["LICENSE.md", "LICENSE.ASSETS.md"]
ETHNIC = ("african", "asian", "caucasian")
# Paths under src/mpfb/data/. Keep this list to what the build actually reads.
DATA_FILES = (
    ["3dobjs/base.obj", "rigs/rigify/weights.human_toes.json"]
    + [f"uv_layers/{n}.json.gz" for n in ("lips_solid", "face_solid", "scalp_solid")]
    + [f"targets/macrodetails/{e}-{g}-young.target.gz" for e in ETHNIC for g in ("female", "male")]
    + [f"targets/macrodetails/universal-{g}-young-{m}muscle-{w}weight.target.gz"
       for g in ("female", "male") for m in ("min", "average", "max") for w in ("min", "average", "max")
       if not (m == "average" and w == "average")]
    + [f"targets/expression/units/{e}/{u}.target.gz" for e in ETHNIC for u in (
        "eyebrows-left-inner-up", "eyebrows-right-inner-up", "eyebrows-left-extern-up", "eyebrows-right-extern-up",
        "eyebrows-left-down", "eyebrows-right-down", "nose-left-elevation", "nose-right-elevation",
        "mouth-corner-puller", "mouth-depression", "mouth-retraction", "mouth-pursing",
        "mouth-elevation", "mouth-depression-retraction")]
)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def stored_name(rel: str, size: int) -> str:
    return rel + ".gz" if size > MAX_PLAIN else rel


def gzip_det(data: bytes) -> bytes:
    buf = io.BytesIO()
    with gzip.GzipFile(filename="", mode="wb", fileobj=buf, compresslevel=9, mtime=0) as gz:
        gz.write(data)
    return buf.getvalue()


def fetch() -> int:
    with tempfile.TemporaryDirectory(prefix="mpfb2_") as tmp:
        src = Path(tmp) / "mpfb2"
        src.mkdir()
        git = ["git", "-C", str(src)]
        subprocess.run(git + ["init", "-q"], check=True)
        subprocess.run(git + ["remote", "add", "origin", REPO], check=True)
        subprocess.run(git + ["fetch", "-q", "--depth", "1", "origin", COMMIT], check=True)
        subprocess.run(git + ["checkout", "-q", "FETCH_HEAD"], check=True)
        head = subprocess.run(git + ["rev-parse", "HEAD"], check=True, capture_output=True, text=True).stdout.strip()
        if head != COMMIT:
            print(f"fetched {head}, expected {COMMIT}", file=sys.stderr)
            return 1
        if (DEST / "data").exists():
            shutil.rmtree(DEST / "data")
        files = []
        for rel in LICENSE_FILES:
            data = (src / rel).read_bytes()
            (DEST / rel).parent.mkdir(parents=True, exist_ok=True)
            (DEST / rel).write_bytes(data)
            files.append({"upstream": rel, "stored": rel, "sha256": sha256(data), "stored_sha256": sha256(data)})
        for rel in DATA_FILES:
            data = (src / DATA_PREFIX / rel).read_bytes()
            name = stored_name(rel, len(data))
            out = gzip_det(data) if name != rel else data
            path = DEST / "data" / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(out)
            files.append({"upstream": DATA_PREFIX + rel, "stored": "data/" + name, "sha256": sha256(data),
                          "stored_sha256": sha256(out)})
    manifest = {
        "source": REPO,
        "commit": COMMIT,
        "license": "CC0 1.0 Universal (MPFB2 LICENSE.md section C, LICENSE.ASSETS.md); program code not vendored",
        "files": files,
    }
    (DEST / "MANIFEST.json").write_text(json.dumps(manifest, indent=1) + "\n", encoding="utf-8")
    total = sum((DEST / f["stored"]).stat().st_size for f in files)
    print(f"vendored {len(files)} files ({total / 1e6:.2f} MB) from {REPO}@{COMMIT[:12]} into "
          f"{DEST.relative_to(ROOT)}")
    return 0


def check() -> int:
    manifest = json.loads((DEST / "MANIFEST.json").read_text(encoding="utf-8"))
    bad = 0
    if manifest["commit"] != COMMIT:
        print(f"MANIFEST commit {manifest['commit']} != pinned {COMMIT}")
        bad += 1
    expected = {stored for stored in [*LICENSE_FILES]} | {f["stored"] for f in manifest["files"]}
    for f in manifest["files"]:
        p = DEST / f["stored"]
        if not p.exists():
            print(f"missing {f['stored']}")
            bad += 1
            continue
        data = p.read_bytes()
        if sha256(data) != f["stored_sha256"]:
            print(f"changed {f['stored']}")
            bad += 1
        if p.stat().st_size > MAX_PLAIN:
            print(f"over 5 MB: {f['stored']}")
            bad += 1
    listed = {f["upstream"].removeprefix(DATA_PREFIX) for f in manifest["files"]}
    for rel in DATA_FILES:
        if rel not in listed:
            print(f"not vendored yet: {rel} (run without --check)")
            bad += 1
    for p in sorted((DEST / "data").rglob("*")):
        if p.is_file() and p.relative_to(DEST).as_posix() not in expected:
            print(f"unlisted file: {p.relative_to(ROOT)}")
            bad += 1
    for p in sorted(DEST.rglob("*.py")) + sorted(DEST.rglob("*.sh")):
        print(f"program code must not be vendored: {p.relative_to(ROOT)}")
        bad += 1
    print("mpfb2 vendored data: OK" if not bad else f"mpfb2 vendored data: {bad} problem(s)")
    return 1 if bad else 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()
    return check() if args.check else fetch()


if __name__ == "__main__":
    raise SystemExit(main())
