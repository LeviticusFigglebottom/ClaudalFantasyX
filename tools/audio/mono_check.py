#!/usr/bin/env python3
"""Mono fold-down check (the Lead's 10-30 21:25 accessibility item; the `mono_audio` setting).

A player on one speaker, one ear or the mono setting hears (L + R) / 2. Synthesized stereo can lose a part to that
fold: a voice panned wide on decorrelated reverb only thins, but an anti-phase pair (a Haas trick, a widened pad)
cancels. For every rendered .ogg this measures:
  - the integrated loudness lost by the fold (stereo as two channels against the folded mono), and
  - each 400 ms window's own loss to the fold, judged only where the file is clearly sounding (within
    WINDOW_FLOOR_DB of its loudest window): a reverb tail may wander out of phase unheard, a phrase may not.
A file fails when the fold loses more than MAX_LOSS_LU over the whole, or a sounding window loses more than
MAX_WINDOW_LOSS_DB (the part goes missing: L and R nearly cancel). A window losing more than THIN_DB is reported as
thinning (the part is quieter in mono for a moment, still there). Mono files pass by definition.

    python3 tools/audio/mono_check.py [--only music,act2] [--md report.md] [-j 4]
"""

from __future__ import annotations

import argparse
import glob
import os
import sys
from concurrent.futures import ProcessPoolExecutor

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from synth.dsp import SR  # noqa: E402
from synth.loudness import integrated_lufs  # noqa: E402
from synth.mixer import read_audio  # noqa: E402

ROOT = os.path.normpath(os.path.join(HERE, "..", ".."))
AUDIO = os.path.join(ROOT, "assets", "audio")
# Uncorrelated stereo folds 3 LU down; more than this is a part going missing.
MAX_LOSS_LU = 4.5
# A sounding window losing this much to the fold has a part going missing (L/R correlation about -0.7 or lower).
MAX_WINDOW_LOSS_DB = 8.0
# A sounding window losing this much thins in mono (reported, not failed).
THIN_DB = 4.0
# Windows quieter than this under the file's peak window are tails and noise floor, not judged.
WINDOW_FLOOR_DB = 20.0
WINDOW_S = 0.4


def measure(path: str) -> dict:
    x = read_audio(path, channels=2)
    l, r = x[:, 0], x[:, 1]
    row = {"path": os.path.relpath(path, ROOT), "loss_lu": 0.0, "worst_db": 0.0, "worst_at": 0.0, "mono": False}
    if np.allclose(l, r, atol=1e-6):
        row["mono"] = True
        return row
    mono = 0.5 * (l + r)
    stereo_lufs = integrated_lufs(x)
    mono_lufs = integrated_lufs(np.stack([mono, mono], axis=1))
    if np.isfinite(stereo_lufs) and np.isfinite(mono_lufs):
        row["loss_lu"] = round(float(stereo_lufs - mono_lufs), 2)
    n = int(WINDOW_S * SR)
    wins = []  # [start s, stereo energy, mono loss dB]
    for s in range(0, len(l) - n + 1, n // 2):
        a, b, m = l[s:s + n], r[s:s + n], mono[s:s + n]
        e = float(np.sum(a * a) + np.sum(b * b))
        if e > 0:
            wins.append((s / SR, e, 10 * np.log10(max(2 * float(np.sum(m * m)) / e, 1e-12))))
    if wins:
        floor = max(w[1] for w in wins) * 10 ** (-WINDOW_FLOOR_DB / 10.0)
        judged = [w for w in wins if w[1] >= floor]
        worst = min(judged, key=lambda w: w[2])
        row["worst_db"] = round(-float(worst[2]), 1)
        row["worst_at"] = round(float(worst[0]), 1)
    return row


def failing(row: dict) -> list[str]:
    why = []
    if row["loss_lu"] > MAX_LOSS_LU:
        why.append(f"folds {row['loss_lu']} LU down (> {MAX_LOSS_LU})")
    if row["worst_db"] > MAX_WINDOW_LOSS_DB:
        why.append(
            f"at {row['worst_at']} s it loses {row['worst_db']} dB in mono (> {MAX_WINDOW_LOSS_DB}: a part goes missing)"
        )
    return why


def files(only: list[str]) -> list[str]:
    out = sorted(glob.glob(os.path.join(AUDIO, "**", "*.ogg"), recursive=True))
    if only:
        out = [p for p in out if any(f"/{o}/" in p or os.path.basename(p).startswith(o) for o in only)]
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--only", default="", help="comma-separated folders or name prefixes")
    ap.add_argument("--md", default="", help="write the failing rows (and a summary) as Markdown here")
    ap.add_argument("-j", type=int, default=4)
    a = ap.parse_args(argv)
    paths = files([o for o in a.only.split(",") if o])
    with ProcessPoolExecutor(max_workers=max(1, a.j)) as ex:
        rows = list(ex.map(measure, paths, chunksize=8))
    bad = [(r, failing(r)) for r in rows if failing(r)]
    stereo = [r for r in rows if not r["mono"]]
    worst = sorted(stereo, key=lambda r: -r["loss_lu"])[:5]
    thin = sorted((r for r in stereo if THIN_DB < r["worst_db"] <= MAX_WINDOW_LOSS_DB), key=lambda r: -r["worst_db"])
    lines = [
        f"{len(rows)} files, {len(stereo)} stereo; {len(bad)} fail the mono fold "
        f"(loss > {MAX_LOSS_LU} LU, or a sounding window losing > {MAX_WINDOW_LOSS_DB} dB)."
    ]
    lines += [f"  FAIL {r['path']}: {'; '.join(w)}" for r, w in bad]
    lines += [f"  thins {r['path']}: {r['worst_db']} dB for a moment at {r['worst_at']} s" for r in thin]
    lines += ["  largest losses: " + ", ".join(f"{os.path.basename(r['path'])} {r['loss_lu']}" for r in worst)]
    print("\n".join(lines))
    if a.md:
        with open(a.md, "w") as f:
            f.write("# Mono fold-down check\n\n" + "\n".join(f"- {x.strip()}" for x in lines) + "\n")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
