"""`credits_suite`: the credits (M5-A3P-1952; act3_ending.md CR; ADR 0208). About 6.5 minutes, not looped.

The brief (act3_ending.md CR): "*Music:* `credits_suite`, a suite of the game's themes, ending on the lullaby phrase
on piano."

A suite of the game's themes, made from the themes themselves: excerpts of the shipped cues, each rendered
from its own source in assets_src/music (so this file is reproducible from source through them), joined by
crossfades in the order the pilgrimage met them. Then one new passage, the lullaby on the piano, closes the game.
* `haluna_dawn`: the star-path, the homecoming tune of Ch2's beach (where the game will end);
* `oruvel_theme`: Rhen's home, the raft-town's tune;
* `kerrid_stair`: Kerrid's tread, the stair-watch walking in;
* `ysolde_theme`: Ysolde's ink;
* `liss_theme`: Liss in the burned camp;
* `farewell_tide`: the Kirru's farewell, the backs turned;
* `the_kite`: the Kite in flight;
* `hush_theme_v2`: the Hush itself;
* the close, new here: the lullaby's first phrase (hush_first_verse.py `VERSE` line 1, E D C | A G A, the tune both
  children were sung to sleep with) on the piano alone, slow, its A held over an open A minor ninth and left to
  ring. It is the only thing in the suite that is new, and the last sound of the game before E7's lamp.
Each excerpt fades in over 4 s and out over 5 s, overlapping the next; the suite is normalised as a whole, so every
theme keeps the level it had in the game. The order and the excerpts are the only composition in the joins; the
piano close is original (SPEC §2) and states the game's own tune.

Render:  python3 assets_src/music/act3/credits_suite.py   (or tools/audio/render_all.py --only credits_suite)
         It reads the shipped renders of the cues above: render them first if they change.
"""
from __future__ import annotations

import importlib.util
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
MUSIC = os.path.dirname(HERE)
ROOT = os.path.abspath(os.path.join(MUSIC, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools", "audio"))
sys.path.insert(0, MUSIC)
sys.path.insert(0, HERE)

import numpy as np  # noqa: E402

from synth.dsp import SR, rng  # noqa: E402
from synth.grand import MAX_LEN, PedalCurve, PianoBody, grand_note  # noqa: E402
from synth.loudness import integrated_lufs  # noqa: E402
from synth.mixer import Mixer, measure, normalize_integrated, read_audio, write_ogg  # noqa: E402
from synth.parallel import render_jobs  # noqa: E402
from synth.performance import plan_pedal  # noqa: E402
from synth.reverb import ModFDNReverb  # noqa: E402
from synth.score import n  # noqa: E402


def _load(name: str):
    spec = importlib.util.spec_from_file_location(name, os.path.join(MUSIC, f"{name}.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


FV = _load("hush_first_verse")
OUT = os.path.join(ROOT, "assets", "audio", "act3", "music", "credits_suite.ogg")
SEED = 20261038
TARGET_LUFS = -16.0
FADE_IN_S = 4.0
FADE_OUT_S = 5.0
# (shipped render, excerpt start s, excerpt length s), in the order the pilgrimage met them
SUITE = [
    ("assets/audio/music/haluna_dawn.ogg", 0.0, 48.0),
    ("assets/audio/music/oruvel_theme.ogg", 5.0, 44.0),
    ("assets/audio/music/kerrid_stair.ogg", 0.0, 30.0),
    ("assets/audio/music/ysolde_theme.ogg", 0.0, 46.0),
    ("assets/audio/music/liss_theme.ogg", 0.0, 44.0),
    ("assets/audio/act2/music/farewell_tide.ogg", 0.0, 46.0),
    ("assets/audio/music/act3/the_kite.ogg", 0.0, 46.0),
    ("assets/audio/music/hush_theme_v2.ogg", 0.0, 52.0),
]
CLOSE_BPM = 46.0


def excerpt(path: str, start: float, length: float) -> np.ndarray:
    x = read_audio(os.path.join(ROOT, path), channels=2)
    a = int(start * SR)
    y = x[a: a + int(length * SR)].copy()
    # every theme at the level it had in the game (each cue is mastered to -16), then the joins' fades
    lu = integrated_lufs(y)
    if np.isfinite(lu):
        y *= 10 ** ((TARGET_LUFS - lu) / 20.0)
    fi, fo = int(FADE_IN_S * SR), int(FADE_OUT_S * SR)
    y[:fi] *= np.linspace(0.0, 1.0, fi)[:, None] ** 2
    y[-fo:] *= np.linspace(1.0, 0.0, fo)[:, None] ** 2
    return y


def piano_close(seed: int) -> np.ndarray:
    """The lullaby's first phrase on the piano alone, its A held over an open A minor ninth."""
    g = rng(seed)
    beat = 60.0 / CLOSE_BPM
    notes = []
    t = 0.8
    for p, beats in FV.VERSE[0]:
        notes.append(dict(m=n(p), vel=0.34, t0=t + float(g.normal(0, 0.006)), key_up=beats * beat + 0.04))
        t += beats * beat
    end_t = t - FV.VERSE[0][-1][1] * beat
    for j, p in enumerate(["A1", "E2", "A2", "E3", "B3", "C4"]):
        notes.append(dict(m=n(p), vel=0.24 - 0.02 * j, t0=end_t + 0.1 * j, key_up=10.0))
    pedal = plan_pedal([end_t], start=0.8, end_release=end_t + 11.0, release_len=3.5, g=g)
    length = end_t + 16.0
    mx = Mixer(length)
    mx.bus("piano", 25.2, send=0.3, process=PianoBody(pedal))
    jobs = []
    for k, nt in enumerate(notes):
        msk = (pedal.times >= nt["t0"] - 0.01) & (pedal.times <= nt["t0"] + MAX_LEN + 0.01)
        jobs.append((grand_note, dict(m=nt["m"], vel=nt["vel"], key_up=nt["key_up"], seed=seed + 7919 * k,
                                      t_abs=nt["t0"], pedal=PedalCurve(pedal.times[msk].copy(),
                                                                       pedal.depth[msk].copy()))))
    for nt, x in zip(notes, render_jobs(jobs)):
        mx.add("piano", x, nt["t0"], pan=float(np.clip((nt["m"] - 64) / 60.0, -0.3, 0.3)))
    hall = ModFDNReverb(rt60=3.2, rt60_high=1.3, predelay=0.03, size=1.15, mod_depth=8.0, mod_rate=0.4,
                        early_level=0.22, lowcut=80.0, width=0.75, seed=seed % 9973)
    y = mx.render(reverb=hall, reverb_return_db=-2.0)
    lu = integrated_lufs(y)
    return y * 10 ** ((TARGET_LUFS - 2.0 - lu) / 20.0)        # a little under the themes: the last, quiet word


def render(out_path: str = OUT, verbose: bool = True, stats: dict | None = None) -> dict:
    parts = [excerpt(p, s, d) for p, s, d in SUITE] + [piano_close(SEED)]
    step = [len(p) - int(FADE_OUT_S * SR * 0.8) for p in parts[:-1]]
    total = sum(step) + len(parts[-1])
    y = np.zeros((total, 2))
    at = 0
    starts = []
    for k, p in enumerate(parts):
        starts.append(at / SR)
        y[at: at + len(p)] += p
        if k < len(step):
            at += step[k]
    fade = int(2.0 * SR)
    y[-fade:] *= np.linspace(1.0, 0.0, fade)[:, None]
    y = normalize_integrated(y, TARGET_LUFS, ceiling_db=-2.0)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    write_ogg(out_path, y, quality=2.5)
    m = measure(y)
    if stats is not None:
        stats["starts"] = starts
    if verbose:
        print(f"credits_suite: {m['seconds']:.1f}s  {m['integrated_lufs']:.2f} LUFS  TP {m['true_peak_dbtp']:.2f}"
              f"  piano close at {starts[-1]:.1f}s")
    return m


if __name__ == "__main__":
    render()
