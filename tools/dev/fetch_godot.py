#!/usr/bin/env python3
"""Fetch the pinned Godot (ADR 0001) into a private sysroot, for containers that cannot
reach GitHub releases or godotengine.org (the cloud agent sandbox).

How: Ubuntu's archive carries a distro build `godot <PINNED_DEB>`. It needs a newer glibc
than the host, so we resolve its whole dependency closure from the Ubuntu release that
ships it, unpack every .deb into a sysroot, and run the binary through the sysroot's own
dynamic loader. Nothing is installed system-wide and no root is needed.

Usage:  python3 tools/dev/fetch_godot.py [--dest DIR]
Then:   <DEST>/godot --version      (wrapper script; put DEST on PATH as `godot`)

Caveat: this is the Debian/Ubuntu "+ds" build of the same engine version (some vendored
thirdparty libs are system libs). CI still uses the official build; treat any behaviour
difference as a bug to report in docs/kb/tech/engine.md.
"""
from __future__ import annotations

import argparse
import lzma
import os
import re
import stat
import subprocess
import sys
import urllib.request
from pathlib import Path

BASE = "https://archive.ubuntu.com/ubuntu/"
PACKAGE = "godot"
PINNED_DEB = "4.6.3+ds-2"
DISTS = ["stonking", "resolute", "tenacious", "devel"]
COMPONENTS = ["main", "universe"]


def load_index(dist: str) -> dict[str, dict[str, str]]:
    db: dict[str, dict[str, str]] = {}
    for comp in COMPONENTS:
        for suite in (dist, f"{dist}-updates"):
            url = f"{BASE}dists/{suite}/{comp}/binary-amd64/Packages.xz"
            try:
                raw = urllib.request.urlopen(url, timeout=180).read()
            except OSError:
                continue
            for block in lzma.decompress(raw).decode("utf-8", "replace").split("\n\n"):
                fields: dict[str, str] = {}
                for line in block.splitlines():
                    if line[:1] in (" ", "\t"):
                        continue
                    key, _, val = line.partition(": ")
                    fields[key] = val
                if "Package" not in fields:
                    continue
                db[fields["Package"]] = fields
                for prov in fields.get("Provides", "").split(","):
                    name = prov.strip().split(" ")[0]
                    if name:
                        db.setdefault("virtual:" + name, fields)
    return db


def closure(db: dict[str, dict[str, str]], root: str) -> dict[str, dict[str, str]]:
    seen: dict[str, dict[str, str]] = {}
    stack = [root]
    while stack:
        name = stack.pop()
        f = db.get(name) or db.get("virtual:" + name)
        if not f or f["Package"] in seen:
            continue
        seen[f["Package"]] = f
        for field in ("Pre-Depends", "Depends"):
            for dep in f.get(field, "").split(","):
                first = dep.split("|")[0].strip()
                if first:
                    stack.append(re.split(r"[ (:]", first)[0])
    return seen


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dest", type=Path, default=Path.home() / ".cache" / "hymn" / f"godot-{PINNED_DEB}")
    args = ap.parse_args()
    dest: Path = args.dest
    sysroot, debs = dest / "sysroot", dest / "debs"
    wrapper = dest / "godot"
    if wrapper.exists():
        print(f"already fetched: {wrapper}")
        return 0
    for dist in DISTS:
        db = load_index(dist)
        if db.get(PACKAGE, {}).get("Version") == PINNED_DEB:
            break
    else:
        print(f"no Ubuntu dist in {DISTS} ships {PACKAGE} {PINNED_DEB}", file=sys.stderr)
        return 1
    pkgs = closure(db, PACKAGE)
    print(f"{dist}: {len(pkgs)} packages")
    sysroot.mkdir(parents=True, exist_ok=True)
    debs.mkdir(parents=True, exist_ok=True)
    for f in pkgs.values():
        deb = debs / os.path.basename(f["Filename"])
        if not deb.exists():
            urllib.request.urlretrieve(BASE + f["Filename"], deb)
        subprocess.run(["dpkg-deb", "-x", str(deb), str(sysroot)], check=True)
    lib = sysroot / "usr" / "lib" / "x86_64-linux-gnu"
    libpath = ":".join(str(p) for p in (lib, sysroot / "lib" / "x86_64-linux-gnu", lib / "pulseaudio"))
    wrapper.write_text(
        "#!/bin/sh\n"
        f'exec "{lib}/ld-linux-x86-64.so.2" --library-path "{libpath}" "{sysroot}/usr/bin/godot" "$@"\n'
    )
    wrapper.chmod(wrapper.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    out = subprocess.run([str(wrapper), "--version"], capture_output=True, text=True)
    print(f"{wrapper}: {out.stdout.strip() or out.stderr.strip()}")
    return 0 if out.returncode == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
