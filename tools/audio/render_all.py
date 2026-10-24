#!/usr/bin/env python3
"""Regenerate every synthesized audio asset, deterministically.

    python3 tools/audio/render_all.py                 # render + verify
    python3 tools/audio/render_all.py --determinism   # also render a second copy to a temp
                                                      # dir and compare SHA-256 byte-for-byte
    python3 tools/audio/render_all.py --only battle   # just the jobs whose source path matches

All randomness uses fixed seeds; Vorbis is encoded with ffmpeg's bit-exact
flags, so the same numpy + ffmpeg/libvorbis versions give identical bytes.
After rendering, each .ogg is decoded back and its loudness re-measured, so
the numbers printed are for the shipped files, not the float mix.

Looping cues ("music_loop") also write a sidecar <name>.loop.json and carry
LOOPSTART / LOOPLENGTH Vorbis comments (in samples). Verification decodes
each loop and checks its exact length, the tags, and the continuity of the
wrap seam, and copies the loop settings into the Godot .import file if one
exists (re-run `godot --headless --path . --import` afterwards).
Requires: python3, numpy, ffmpeg with libvorbis (ffprobe for the tag check).
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools", "audio"))

from synth.analysis import loop_seam_report  # noqa: E402
from synth.loudness import integrated_lufs, momentary_max_lufs, self_test, true_peak_dbtp  # noqa: E402
from synth.mixer import read_audio  # noqa: E402

SIZE_BUDGET = 16 * 1024 * 1024       # all shipped audio for the M2 slice (mix.md §5)
NEW_AUDIO_BUDGET = 4 * 1024 * 1024   # the three M1-AUD-02 cues together
M1_AUD_02 = ("hush_theme_v2", "battle_standard", "temple_trial")

# (module source, output dir, output file names, kind)
JOBS = [
    ("assets_src/music/hush_theme_sketch.py", "assets/audio/music", ["hush_theme_sketch.ogg"], "music"),
    ("assets_src/sfx/ui_sfx.py", "assets/audio/sfx",
     ["ui_cursor.ogg", "ui_confirm.ogg", "ui_cancel.ogg", "text_blip.ogg"], "sfx"),
    ("assets_src/music/hush_theme_v2.py", "assets/audio/music", ["hush_theme_v2.ogg"], "music"),
    ("assets_src/music/battle_standard.py", "assets/audio/music",
     ["battle_standard.ogg", "battle_standard.loop.json"], "music_loop"),
    ("assets_src/music/temple_trial.py", "assets/audio/music",
     ["temple_trial.ogg", "temple_trial.loop.json"], "music_loop"),
    ("assets_src/music/shell_shrine_interior.py", "assets/audio/music",
     ["shell_shrine_interior.ogg", "shell_shrine_interior.loop.json"], "music_loop"),
    ("assets_src/sfx/shrine_sfx.py", "assets/audio/sfx/shrine",
     ["shrine_stone_turn_1.ogg", "shrine_stone_turn_2.ogg", "shrine_stone_turn_3.ogg", "shrine_pour.ogg",
      "shrine_spill.ogg", "shrine_drain.ogg", "shrine_side_drain.ogg", "shrine_door.ogg", "shrine_charm.ogg"], "sfx"),
    ("assets_src/sfx/shrine_pool_fill.py", "assets/audio/sfx/shrine",
     ["shrine_pool_fill.ogg", "shrine_pool_fill.loop.json"], "music_loop"),
]


def _load(path):
    spec = importlib.util.spec_from_file_location(os.path.splitext(os.path.basename(path))[0],
                                                  os.path.join(ROOT, path))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _render_job(src, out_dir, files, kind):
    mod = _load(src)
    if kind in ("music", "music_loop"):
        mod.render(os.path.join(out_dir, files[0]), verbose=False)
    else:
        mod.render(out_dir, verbose=False)


def _sha(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def _vorbis_tags(path: str) -> dict:
    probe = shutil.which("ffprobe")
    if not probe:
        return {}
    out = subprocess.run([probe, "-v", "error", "-show_entries", "stream_tags", "-of", "json", path],
                         capture_output=True, text=True, check=True).stdout
    tags = {}
    for st in json.loads(out).get("streams", []):
        tags.update({k.upper(): v for k, v in st.get("tags", {}).items()})
    return tags


def _check_loop(ogg: str, y) -> list[str]:
    """Verify a looping cue against its sidecar. Returns a list of problems."""
    problems = []
    with open(os.path.splitext(ogg)[0] + ".loop.json", encoding="utf-8") as f:
        meta = json.load(f)
    S, L, total = meta["loop_start_samples"], meta["loop_length_samples"], meta["total_samples"]
    if len(y) != total or S + L != total:
        problems.append(f"length {len(y)} != sidecar total {total} (start {S} + length {L})")
    tags = _vorbis_tags(ogg)
    if tags and (tags.get("LOOPSTART") != str(S) or tags.get("LOOPLENGTH") != str(L)):
        problems.append(f"Vorbis tags {tags.get('LOOPSTART')}/{tags.get('LOOPLENGTH')} != sidecar {S}/{L}")
    seam = loop_seam_report(y, S)
    print(f"  loop {os.path.basename(ogg)}: start {S}, length {L} ({L / 44100:.2f} s), "
          f"seam jump x{seam['jump_ratio']:.2f}, flux x{seam['flux_ratio']:.2f}, tags {'ok' if tags else 'n/a'}")
    if seam["flux_ratio"] > 3.0:
        problems.append(f"seam spectral flux {seam['flux_ratio']:.2f}x the median (click or gap?)")
    _sync_import(ogg, meta)
    return problems


def _sync_import(ogg: str, meta: dict) -> None:
    """Copy loop settings into Godot's .import file (if Godot has imported the file already)."""
    imp = ogg + ".import"
    if not os.path.isfile(imp):
        return
    with open(imp, encoding="utf-8") as f:
        txt = f.read()
    want = {"loop": "true", "loop_offset": repr(float(meta["loop_offset_seconds"])),
            "bpm": repr(float(meta["bpm"])), "beat_count": str(int(meta["beat_count"])),
            "bar_beats": str(int(meta["bar_beats"]))}
    new = txt
    for k, v in want.items():
        new = re.sub(rf"(?m)^{k}=.*$", f"{k}={v}", new)
    if new != txt:
        with open(imp, "w", encoding="utf-8") as f:
            f.write(new)
        print(f"  updated {os.path.relpath(imp, ROOT)} (re-run godot --headless --path . --import)")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--determinism", action="store_true", help="render twice and compare bytes")
    ap.add_argument("--only", default="", help="only the jobs whose source path contains this text")
    args = ap.parse_args()

    self_test()  # BS.1770 meter sanity (48 kHz coefficients, 997 Hz reference)

    jobs = [j for j in JOBS if not args.only or args.only in j[0]]
    rows, total, new_total, ok = [], 0, 0, True
    for src, rel_dir, files, kind in jobs:
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
            if f.startswith(M1_AUD_02):
                new_total += size
            if f.endswith(".json"):
                rows.append((os.path.join(rel_dir, f), size, None, None, None, None, _sha(p)))
                continue
            y = read_audio(p, channels=1 if kind == "sfx" else 2)
            if kind == "music_loop":
                for prob in _check_loop(p, y):
                    print(f"FAIL {f}: {prob}")
                    ok = False
            rows.append((os.path.join(rel_dir, f), size, len(y) / 44100,
                         integrated_lufs(y) if kind != "sfx" else None, momentary_max_lufs(y), true_peak_dbtp(y),
                         _sha(p)))

    print()
    print(f"{'file':48} {'bytes':>8} {'sec':>6} {'I LUFS':>7} {'Mmax':>7} {'TPdB':>6}  sha256[:12]")
    for path, size, sec, il, mm, tp, sha in rows:
        if sec is None:
            print(f"{path:48} {size:8d} {'':>6} {'':>7} {'':>7} {'':>6}  {sha[:12]}")
            continue
        ils = f"{il:7.2f}" if il is not None else "      -"
        print(f"{path:48} {size:8d} {sec:6.2f} {ils} {mm:7.2f} {tp:6.2f}  {sha[:12]}")
        if il is not None and os.path.basename(path).startswith(M1_AUD_02) and (abs(il + 16.0) > 0.5 or tp > -1.0):
            print(f"FAIL {path}: outside -16 +- 0.5 LUFS, or true peak above -1 dBTP")
            ok = False
    if not args.only:
        print(f"total {total} bytes ({total / 1048576:.2f} MiB), budget {SIZE_BUDGET / 1048576:.0f} MiB; "
              f"M1-AUD-02 cues {new_total / 1048576:.2f} MiB, budget {NEW_AUDIO_BUDGET / 1048576:.0f} MiB")
        if total > SIZE_BUDGET or new_total > NEW_AUDIO_BUDGET:
            print("FAIL: over size budget")
            ok = False

    if args.determinism:
        with tempfile.TemporaryDirectory() as td:
            for src, rel_dir, files, kind in jobs:
                _render_job(src, td, files, kind)
                for f in files:
                    a, b = _sha(os.path.join(ROOT, rel_dir, f)), _sha(os.path.join(td, f))
                    same = a == b
                    ok &= same
                    print(f"determinism {f}: {'identical' if same else 'DIFFERENT'}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
