"""`goodbye_dace`: the Ending's E2, Dace turns around (M5-A3P-1952; act3_ending.md E2; ADR 0208). About 100 s, not
looped.

Original composition for this project (SPEC §2). Its two tunes are the game's own, loaded and never retyped:
* Dace's current-song (motifs.py `CURRENT_SONG`), the Saltwright sung chart he taught Rhen for reading water;
* the Velamir lullaby (hush_first_verse.py `VERSE`, lines 1–2): the tune Imra hummed at Haluna, which Dace took home
  to Oruvel and hummed to Rhen every night (decisions_log N-11).
The harp's setting, the harmony and the form were written for this cue.

The brief (act3_ending.md E2): "With Imra gone, Dace's hands are free for the first time in eleven years, and he turns
around... *Music:* `goodbye_dace`. Dace's current-song from Ch1 on plucked strings, and inside it, for four bars, the
lullaby tune, the thing that tied two families together without either child knowing."

The two tunes share their notes: the current-song is in D dorian and the lullaby in A minor, and those are the same
seven notes. So the lullaby passes through the middle of his song without the harmony changing key, as if it had
always been in it. Both run in 3/4 (each current-song phrase is two bars; the last is held to three).
* bars 1–2: plucked low strings alone on D, a slow arpeggio: the boat before anyone speaks;
* bars 3–9: the current-song on the harp (a small plucked harp: string_pluck through pilgrims_wake's soundbox),
  over plucked arpeggios: Dm | Am | C | G | Am | C | Dm;
* bars 10–13: inside it, the lullaby. The harp plays its first two lines (E D C | A G A | G C D | E G E) over the
  same plucked arpeggios, on its own harmony (Am | F | C | Em);
* bars 14–20: the current-song again, warmer, a low string pad under the plucking now;
* bars 21–27: once more, slower at the end, the last phrase held home on D. A D chord with no third, open, is left
  ringing: neither the minor of the song nor a major it never had.

D dorian (and A minor inside it), 3/4 at 60 BPM, slowing over the last phrase.

Render:  python3 assets_src/music/act3/goodbye_dace.py   (or tools/audio/render_all.py --only goodbye_dace)
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

from levels import bus_levels  # noqa: E402
from motifs import CURRENT_SONG  # noqa: E402
from synth.dsp import SR, bq_highpass, fft_convolve, filt, rng  # noqa: E402
from synth.electric import string_pluck  # noqa: E402
from synth.mixer import Mixer, measure, normalize_integrated, write_ogg  # noqa: E402
from synth.pad import pad_chord, string_body  # noqa: E402
from synth.reverb import ModFDNReverb  # noqa: E402
from synth.score import n  # noqa: E402


def _load(name: str):
    spec = importlib.util.spec_from_file_location(name, os.path.join(MUSIC, f"{name}.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


FV = _load("hush_first_verse")
PW = _load("pilgrims_wake")
OUT = os.path.join(ROOT, "assets", "audio", "act3", "music", "goodbye_dace.ogg")
SEED = 20261037
TARGET_LUFS = -18.0         # a plucked goodbye: quieter than a scene cue, so its plucks peak near -7 (targets.py)
BPM = 60.0
BEAT = 60.0 / BPM
BAR = 3 * BEAT
SONG_CHORDS = ["D2 A2 F3 C4", "A1 E2 C3 G3", "C2 G2 E3 B3", "G1 D2 B2 F3", "A1 E2 C3 G3", "C2 G2 E3 B3", "D2 A2 F3 E4"]
LULLABY_CHORDS = ["A1 E2 C3 B3", "F1 C2 A2 E3", "C2 G2 E3 D4", "E1 B1 G2 D3"]
# From measured bus loudness (levels.bus_levels): the harp's melody at L, the arpeggios L-6, the pad L-9.
GAINS = {"harp": 0.0, "arps": -10.0, "pad": 7.5}


def harp(m: float, dur: float, vel: float, seed: int, body: np.ndarray) -> np.ndarray:
    x = string_pluck(m, dur, vel, seed=seed, pick_pos=0.18, t60=3.5, B=4e-5, max_f=7000.0)
    return fft_convolve(x, body)[: len(x) + 4000]


def song_notes(t0: float, slow_end: bool = False) -> tuple[list[tuple[float, float, float]], float]:
    """The current-song from t0 as [(t, dur, midi)], each phrase two bars (the last three), and its end."""
    out = []
    t = t0
    for pi, phrase in enumerate(CURRENT_SONG):
        span = 2 * BAR if pi < 2 else 3 * BAR
        used = sum(b for _, b in phrase) * BEAT
        for k, (m, beats) in enumerate(phrase):
            d = beats * BEAT
            if k == len(phrase) - 1:
                d += span - used
            stretch = 1.0 + (0.25 * k / len(phrase) if slow_end and pi == 2 else 0.0)
            out.append((t, d * stretch, float(m)))
            t += beats * BEAT * stretch
        t = t0 + sum(2 * BAR if q < 2 else 3 * BAR for q in range(pi + 1))
    return out, t


def lullaby_notes(t0: float) -> list[tuple[float, float, float]]:
    out = []
    t = t0
    for line in FV.VERSE[:2]:
        for p, beats in line:
            out.append((t, beats * BEAT, float(n(p))))
            t += beats * BEAT
    return out


def arpeggio(mx, chord: str, t0: float, bar_s: float, vel: float, seed: int, body: np.ndarray) -> None:
    ps = [n(x) for x in chord.split()]
    pattern = [ps[0], ps[1], ps[2], ps[3], ps[2], ps[1]]
    for i, m in enumerate(pattern):
        # the root no harder than the rest: a plucked low root under the melody's first note was the cue's loudest peak
        mx.add("arps", harp(float(m), bar_s, vel * 0.7, seed + i, body), t0 + i * bar_s / 6,
               pan=float(np.clip((m - 50) / 40.0, -0.4, 0.4)))


def render(out_path: str = OUT, verbose: bool = True, stats: dict | None = None) -> dict:
    g = rng(SEED)
    body = PW.harp_body(SEED + 5)
    t = 1.0
    plan = []                                         # (kind, t0)
    plan.append(("intro", t))
    t += 2 * BAR
    plan.append(("song", t))
    t += 7 * BAR
    plan.append(("lullaby", t))
    t += 4 * BAR
    plan.append(("song_pad", t))
    t += 7 * BAR
    plan.append(("song_last", t))
    t += 7 * BAR
    end_t = t
    length = end_t + 10.0
    mx = Mixer(length)
    mx.bus("harp", GAINS["harp"], send=0.4, process=lambda x: filt(x, [bq_highpass(90, 0.7)]))
    mx.bus("arps", GAINS["arps"], send=0.35, process=lambda x: filt(x, [bq_highpass(45, 0.7)]))
    mx.bus("pad", GAINS["pad"], send=0.45, process=lambda x: string_body(x, cutoff=1500.0))
    for kind, t0 in plan:
        if kind == "intro":
            for b in range(2):
                arpeggio(mx, "D2 A2 D3 F3", t0 + b * BAR, BAR, 0.45, SEED + 10 * b, body)
            continue
        if kind == "lullaby":
            for b, ch in enumerate(LULLABY_CHORDS):
                arpeggio(mx, ch, t0 + b * BAR, BAR, 0.45, SEED + 200 + 10 * b, body)
            for i, (tn, d, m) in enumerate(lullaby_notes(t0)):
                mx.add("harp", harp(m, d + 1.0, 0.62, SEED + 300 + i, body), tn + float(g.normal(0, 0.008)), pan=-0.1)
            continue
        notes, _ = song_notes(t0, slow_end=kind == "song_last")
        for b, ch in enumerate(SONG_CHORDS):
            arpeggio(mx, ch, t0 + b * BAR, BAR, 0.42, SEED + 400 + 100 * len(kind) + 10 * b, body)
            if kind in ("song_pad", "song_last"):
                mx.add("pad", pad_chord([n(x) + 12 for x in ch.split()[1:]], BAR * 1.02, vel=0.4,
                                        seed=SEED + 600 + 10 * b + len(kind), attack=1.0, release=1.4), t0 + b * BAR)
        for i, (tn, d, m) in enumerate(notes):
            mx.add("harp", harp(m, d + 1.0, 0.6, SEED + 700 + 37 * len(kind) + i, body),
                   tn + float(g.normal(0, 0.008)), pan=-0.1)
    # home on D: an open D chord, no third, left ringing
    for j, p in enumerate(["D2", "A2", "D3", "A3", "D4"]):
        mx.add("arps", harp(float(n(p)), 8.0, 0.5 - 0.05 * j, SEED + 900 + j, body), end_t + 0.15 * j)
    hall = ModFDNReverb(rt60=3.0, rt60_high=1.3, predelay=0.03, size=1.15, mod_depth=8.0, mod_rate=0.4,
                        early_level=0.22, lowcut=80.0, width=0.75, seed=SEED % 9973)
    y = mx.render(reverb=hall, reverb_return_db=-2.0)
    fade = int(3.0 * SR)
    y[-fade:] *= np.linspace(1.0, 0.0, fade)[:, None]
    y = normalize_integrated(y, TARGET_LUFS, ceiling_db=-2.0)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    write_ogg(out_path, y, quality=3.0)
    m = measure(y)
    if stats is not None:
        stats["bus_lufs"] = bus_levels(mx)
    if verbose:
        print(f"goodbye_dace: {m['seconds']:.1f}s  {m['integrated_lufs']:.2f} LUFS  TP {m['true_peak_dbtp']:.2f}")
    return m


if __name__ == "__main__":
    render()
