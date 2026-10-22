#!/usr/bin/env python3
"""Regenerate every synthesized audio asset, deterministically.

    python3 tools/audio/render_all.py                 # render + verify
    python3 tools/audio/render_all.py --determinism   # also render a second copy to a temp
                                                      # dir and compare SHA-256 byte-for-byte

All randomness uses fixed seeds; Vorbis is encoded with ffmpeg's bit-exact
flags, so the same numpy + ffmpeg/libvorbis versions give identical bytes.
After rendering, each .ogg is decoded back and its loudness re-measured, so
the numbers printed are for the shipped files, not the float mix.
Requires: python3, numpy, ffmpeg with libvorbis.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import os
import sys
import tempfile

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools", "audio"))

from synth.loudness import integrated_lufs, momentary_max_lufs, self_test, true_peak_dbtp  # noqa: E402
from synth.mixer import read_audio  # noqa: E402

SIZE_BUDGET = 3 * 1024 * 1024

# (module source, output file names relative to the module's output dir, kind)
JOBS = [
    ("assets_src/music/hush_theme_sketch.py", "assets/audio/music", ["hush_theme_sketch.ogg"], "music"),
    ("assets_src/sfx/ui_sfx.py", "assets/audio/sfx",
     ["ui_cursor.ogg", "ui_confirm.ogg", "ui_cancel.ogg", "text_blip.ogg"], "sfx"),
]


def _load(path):
    spec = importlib.util.spec_from_file_location(os.path.splitext(os.path.basename(path))[0],
                                                  os.path.join(ROOT, path))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _render_job(src, out_dir, files, kind):
    mod = _load(src)
    if kind == "music":
        mod.render(os.path.join(out_dir, files[0]), verbose=False)
    else:
        mod.render(out_dir, verbose=False)


def _sha(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--determinism", action="store_true", help="render twice and compare bytes")
    args = ap.parse_args()

    self_test()  # BS.1770 meter sanity (48 kHz coefficients, 997 Hz reference)

    rows, total, ok = [], 0, True
    for src, rel_dir, files, kind in JOBS:
        out_dir = os.path.join(ROOT, rel_dir)
        print(f"rendering {src} ...", flush=True)
        _render_job(src, out_dir, files, kind)
        for f in files:
            p = os.path.join(out_dir, f)
            if not os.path.isfile(p):
                print(f"MISSING {p}")
                ok = False
                continue
            size = os.path.getsize(p)
            total += size
            ch = 2 if kind == "music" else 1
            y = read_audio(p, channels=ch)
            rows.append((os.path.join(rel_dir, f), size, len(y) / 44100, integrated_lufs(y) if kind == "music"
                         else None, momentary_max_lufs(y), true_peak_dbtp(y), _sha(p)))

    print()
    print(f"{'file':44} {'bytes':>8} {'sec':>6} {'I LUFS':>7} {'Mmax':>7} {'TPdB':>6}  sha256[:12]")
    for path, size, sec, il, mm, tp, sha in rows:
        ils = f"{il:7.2f}" if il is not None else "      -"
        print(f"{path:44} {size:8d} {sec:6.2f} {ils} {mm:7.2f} {tp:6.2f}  {sha[:12]}")
    print(f"total {total} bytes ({total / 1048576:.2f} MiB), budget {SIZE_BUDGET / 1048576:.0f} MiB")
    if total > SIZE_BUDGET:
        print("FAIL: over size budget")
        ok = False

    if args.determinism:
        with tempfile.TemporaryDirectory() as td:
            for src, rel_dir, files, kind in JOBS:
                _render_job(src, td, files, kind)
                for f in files:
                    a, b = _sha(os.path.join(ROOT, rel_dir, f)), _sha(os.path.join(td, f))
                    same = a == b
                    ok &= same
                    print(f"determinism {f}: {'identical' if same else 'DIFFERENT'}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
