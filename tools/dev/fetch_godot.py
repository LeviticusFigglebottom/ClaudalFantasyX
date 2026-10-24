#!/usr/bin/env python3
"""Fetch the pinned Godot (ADR 0001) into a private sysroot, for containers that cannot
reach GitHub releases or godotengine.org (the cloud agent sandbox).

How: Ubuntu's archive carries a distro build `godot <PINNED_DEB>`. It needs a newer glibc
than the host, so we resolve its whole dependency closure from the Ubuntu release that
ships it, unpack every .deb into a sysroot, and run the binary through the sysroot's own
dynamic loader. Nothing is installed system-wide and no root is needed.

Usage:  python3 tools/dev/fetch_godot.py [--dest DIR]
Then:   <DEST>/godot --version      (wrapper script; put DEST on PATH as `godot`)

Official builds (the 4.7.2 port, M3): where GitHub releases are reachable,
        python3 tools/dev/fetch_godot.py --official 4.7.2 [--dest DIR] [--templates]
downloads the official Linux x86_64 editor (and, with --templates, the export templates) from
github.com/godotengine/godot/releases, checks each file's SHA-512 against the release's own
SHA512-SUMS.txt (refusing on a mismatch or a file missing from it), and unzips the editor into DEST
with the same `godot` wrapper.

Caveat: this is the Debian/Ubuntu "+ds" build of the same engine version (some vendored
thirdparty libs are system libs). CI still uses the official build; treat any behaviour
difference as a bug to report in docs/kb/tech/engine.md.
"""
from __future__ import annotations

import argparse
import hashlib
import lzma
import os
import re
import stat
import subprocess
import sys
import urllib.request
import zipfile
from pathlib import Path

BASE = "https://archive.ubuntu.com/ubuntu/"
PACKAGE = "godot"
PINNED_DEB = "4.6.3+ds-2"
DISTS = ["stonking", "resolute", "tenacious", "devel"]
COMPONENTS = ["main", "universe"]
RELEASES = "https://github.com/godotengine/godot/releases/download/"
SUMS = "SHA512-SUMS.txt"


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


def parse_sums(text: str) -> dict[str, str]:
    """`<sha512 hex>  <file name>` lines (sha512sum's format) -> {file name: lowercase hex}."""
    out: dict[str, str] = {}
    for line in text.splitlines():
        parts = line.strip().split()
        if len(parts) == 2 and re.fullmatch(r"[0-9a-fA-F]{128}", parts[0]):
            out[parts[1].lstrip("*")] = parts[0].lower()
    return out


def sha512_of(path: Path) -> str:
    h = hashlib.sha512()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def verify(path: Path, sums: dict[str, str]) -> None:
    """Raises ValueError unless `path`'s SHA-512 is the one the release lists for its name."""
    want = sums.get(path.name)
    if want is None:
        raise ValueError(f"{path.name} is not in {SUMS}")
    got = sha512_of(path)
    if got != want:
        raise ValueError(f"{path.name}: SHA-512 {got} != {want} (the release's)")


def official_names(version: str) -> tuple[str, str]:
    """The release's Linux x86_64 editor zip and its export templates, for e.g. "4.7.2"."""
    return f"Godot_v{version}-stable_linux.x86_64.zip", f"Godot_v{version}-stable_export_templates.tpz"


def fetch_official(version: str, dest: Path, templates: bool) -> int:
    base = f"{RELEASES}{version}-stable/"
    dest.mkdir(parents=True, exist_ok=True)
    sums = parse_sums(urllib.request.urlopen(base + SUMS, timeout=180).read().decode("utf-8", "replace"))
    editor, tpz = official_names(version)
    for name in [editor] + ([tpz] if templates else []):
        target = dest / name
        if not target.exists():
            print(f"downloading {name}")
            urllib.request.urlretrieve(base + name, target)
        verify(target, sums)
        print(f"{name}: SHA-512 matches {SUMS}")
    with zipfile.ZipFile(dest / editor) as z:
        z.extractall(dest)
        binary = dest / next(n for n in z.namelist() if not n.endswith("/"))
    binary.chmod(binary.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    wrapper = dest / "godot"
    wrapper.write_text(f'#!/bin/sh\nexec "{binary}" "$@"\n')
    wrapper.chmod(wrapper.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    if sys.platform != "linux":
        # A Linux editor (verified above) cannot run here; a Windows or macOS host fetches it for a Linux box/CI.
        print(f"{binary}: verified; not runnable on {sys.platform}")
        return 0
    out = subprocess.run([str(wrapper), "--version"], capture_output=True, text=True)
    print(f"{wrapper}: {out.stdout.strip() or out.stderr.strip()}")
    return 0 if out.returncode == 0 else 1


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dest", type=Path, default=None)
    ap.add_argument("--official", metavar="VERSION", help="the official GitHub release, e.g. 4.7.2 (SHA-512 checked)")
    ap.add_argument("--templates", action="store_true", help="with --official: the export templates too")
    args = ap.parse_args()
    if args.official:
        dest = args.dest or Path.home() / ".cache" / "hymn" / f"godot-{args.official}-official"
        return fetch_official(args.official, dest, args.templates)
    dest: Path = args.dest or Path.home() / ".cache" / "hymn" / f"godot-{PINNED_DEB}"
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
