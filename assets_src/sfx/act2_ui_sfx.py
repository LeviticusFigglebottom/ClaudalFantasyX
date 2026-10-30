"""Act II's menu sounds (M4-AUD-1080, the request from ui-menus): the document reader's found hand and its mark.

The reader (game/ui/codex/document_reader.gd) lays the founders' ledger beside the Cantor roll in the Archive (Ch13).
When the player sees the same hand on both, the hook plays `ui_hand_found`; a mark set, moved or cleared plays
`ui_mark`. Both are from ui_sfx.py's palette (the metallophone the menus already speak with), so they sound like the
same world:

    ui_hand_found   quiet and certain, nothing triumphant: one bar on D5 (lamp_archive's D minor) struck, and then
                    the same bar struck again, exactly, a little softer: the same hand twice. Damped, with a breath of
                    paper under it.
    ui_mark         a pen's mark: a short nib stroke on paper and the nib's tiny tick lifting off.

Synthesized here and in tools/audio/synth/ (SPEC §2, §9). assets/audio/sfx/ui_<name>.ogg (mono, 44.1 kHz), at the UI
level, -20 LUFS momentary max (targets.py `sfx/ui_*.ogg`), sample peaks under -3 dBFS.

Render:  python3 tools/audio/render_all.py --only act2_ui_sfx
"""
from __future__ import annotations

import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools", "audio"))

import numpy as np  # noqa: E402

from synth.dsp import SR, bq_bandpass, bq_highpass, bq_lowpass, filt, rng  # noqa: E402
from synth.metallophone import metallophone_note  # noqa: E402
from synth.mixer import measure, normalize_momentary, write_ogg  # noqa: E402
from synth.score import n  # noqa: E402

OUT_DIR = os.path.join(ROOT, "assets", "audio", "sfx")
SEED = 20262600
UI_TARGET = -20.0
MARK_TARGET = -24.0      # under the found hand: a mark is set often


def _place(buf: np.ndarray, x: np.ndarray, t: float, gain: float = 1.0) -> None:
    i = int(t * SR)
    k = min(len(x), len(buf) - i)
    buf[i: i + k] += gain * x[:k]


def ui_hand_found() -> np.ndarray:
    g = rng(SEED + 1)
    buf = np.zeros(int(1.6 * SR))
    for k, (at, vel) in enumerate(((0.0, 0.5), (0.34, 0.42))):           # the same hand, twice
        _place(buf, metallophone_note(n("D5"), vel, seed=SEED + 10, decay=0.9, hardness=0.3, ombak_hz=3.0,
                                      damp_at=0.55), at)
    k = int(0.5 * SR)
    paper = filt(g.standard_normal(k), [bq_bandpass(2400, 0.7), bq_lowpass(5000, 0.7)])
    paper *= np.sin(np.pi * np.arange(k) / k) ** 2
    _place(buf, paper / (np.abs(paper).max() + 1e-9), 0.05, 0.05)        # a breath of paper under it
    j = int(0.02 * SR)
    buf[-j:] *= np.linspace(1, 0, j)
    return buf


def ui_mark() -> np.ndarray:
    g = rng(SEED + 2)
    buf = np.zeros(int(0.35 * SR))
    k = int(0.12 * SR)
    t = np.arange(k) / SR
    stroke = filt(g.standard_normal(k), [bq_bandpass(3200, 1.2), bq_highpass(1200, 0.7)])
    stroke *= np.clip(t / 0.01, 0, 1) * np.exp(-t / 0.05) * (1 + 0.4 * np.sin(2 * np.pi * 45 * t))
    _place(buf, stroke / (np.abs(stroke).max() + 1e-9), 0.0)
    _place(buf, metallophone_note(n("A6"), 0.25, seed=SEED + 20, decay=0.12, hardness=0.8, pair=False), 0.11, 0.3)
    j = int(0.02 * SR)
    buf[-j:] *= np.linspace(1, 0, j)
    return buf


SFX = {"ui_hand_found": (ui_hand_found, UI_TARGET), "ui_mark": (ui_mark, MARK_TARGET)}
FILES = [f"{name}.ogg" for name in SFX]


def render(out_dir: str = OUT_DIR, verbose: bool = True) -> dict:
    os.makedirs(out_dir, exist_ok=True)
    res = {}
    for name, (fn, target) in SFX.items():
        x = normalize_momentary(fn(), target, ceiling_db=-3.0)
        write_ogg(os.path.join(out_dir, name + ".ogg"), x, quality=4.0)
        res[name] = m = measure(x)
        if verbose:
            print(f"{name}: {m['seconds']:.2f}s  Mmax {m['momentary_max_lufs']:.2f}  peak {m['sample_peak_dbfs']:.2f}")
    return res


if __name__ == "__main__":
    render()
