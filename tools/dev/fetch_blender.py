#!/usr/bin/env python3
"""Fetch Blender (headless asset pipeline, ADR 0005) into a private sysroot, the same way
tools/dev/fetch_godot.py fetches Godot: Ubuntu archive package + full dependency closure,
run through the sysroot's own loader. No root, nothing installed system-wide.

Usage:  python3 tools/dev/fetch_blender.py [--dest DIR]
Then:   <DEST>/blender --background --factory-startup --python-expr "import bpy; print(bpy.app.version_string)"
"""
from __future__ import annotations

import argparse
import stat
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import fetch_godot as fg  # noqa: E402  (shared archive/closure helpers)

PACKAGE = "blender"
PINNED_DEB = "5.0.1+dfsg-5"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dest", type=Path, default=Path.home() / ".cache" / "hymn" / f"blender-{PINNED_DEB}")
    args = ap.parse_args()
    dest: Path = args.dest
    sysroot, debs, wrapper = dest / "sysroot", dest / "debs", dest / "blender"
    if wrapper.exists():
        print(f"already fetched: {wrapper}")
        return 0
    for dist in fg.DISTS:
        db = fg.load_index(dist)
        if db.get(PACKAGE, {}).get("Version") == PINNED_DEB:
            break
    else:
        print(f"no Ubuntu dist in {fg.DISTS} ships {PACKAGE} {PINNED_DEB}", file=sys.stderr)
        return 1
    pkgs = fg.closure(db, PACKAGE)
    print(f"{dist}: {len(pkgs)} packages")
    sysroot.mkdir(parents=True, exist_ok=True)
    debs.mkdir(parents=True, exist_ok=True)
    import os
    import urllib.request
    for f in pkgs.values():
        deb = debs / os.path.basename(f["Filename"])
        if not deb.exists():
            urllib.request.urlretrieve(fg.BASE + f["Filename"], deb)
        subprocess.run(["dpkg-deb", "-x", str(deb), str(sysroot)], check=True)
    lib = sysroot / "usr" / "lib" / "x86_64-linux-gnu"
    extra = [p for p in lib.iterdir() if p.is_dir() and any(p.glob("*.so*"))]
    libpath = ":".join(str(p) for p in [lib, sysroot / "lib" / "x86_64-linux-gnu", *extra])
    pyver = sorted((sysroot / "usr" / "lib").glob("python3.*"))
    pyhome = f'export PYTHONHOME="{sysroot}/usr"\n' if pyver else ""
    wrapper.write_text(
        "#!/bin/sh\n"
        + pyhome
        + f'export BLENDER_SYSTEM_RESOURCES="{sysroot}/usr/share/blender"\n'
        + f'exec "{lib}/ld-linux-x86-64.so.2" --library-path "{libpath}" "{sysroot}/usr/bin/blender" "$@"\n'
    )
    wrapper.chmod(wrapper.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    out = subprocess.run([str(wrapper), "--background", "--factory-startup", "--version"],
                         capture_output=True, text=True)
    print(f"{wrapper}: {(out.stdout or out.stderr).strip().splitlines()[:1]}")
    return 0 if out.returncode == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
