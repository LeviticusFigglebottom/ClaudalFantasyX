"""`kerrid_at_sea`: Ch15 C3, the reveal (M4-A2P-090; act2_plan.md §2 Ch15; ADR 0020, 0022; the cue sheet): about
270 s, a bed for a voice under Kerrid's telling. It is the act's emotional peak, and it never says so.

Original composition for this project (SPEC §2, §9). The bowed string and its cello body are kerrid_stair.py's, and
his tread is motifs.py's KERRID_STAIR (D3 falling a fourth to A2, one note a stride, at KERRID_STAIR_BPM), both
imported, never retyped. The held chords and the motes' scatter were written for this scene. There is no melody:
nothing here can be a tune, so none is borrowed.

The brief (act2_plan Ch15; kerrid.md §Act II): past midnight the unlamped barge drifts over the shoal of an old
Rising's held dead. Held motes drift toward him, a few of his own leave his hands through the rope-burns, sideways,
and he sits, holds his hands still, and tells them about Corrow in 1001. Nobody performs a rite and nobody attacks.
It is the act's longest dialogue scene: Story's script (ch15_the_shoal.dlg) starts the cue in its first node and
carries it through the confession, with all its remembered lines, into `ch15_still_below`, which silences it over 6 s:
about four minutes on the longest path (tools/audio/act1_playthrough.py --act 2). So the music is a bed for a voice,
as Act I's iskarra_vigil is:
* a dark, low string pad in D minor that moves only every ~45 s (Dm, B-flat, G minor, back to D minor, twice), held
  under 900 Hz;
* his bowed string, long and slow, a few held notes of the chord, never a line;
* his tread, far below: from about 30 s the stair's frame drum and the bowed D-A figure walk, and each stride takes
  longer than the last, until at about 125 s, inside the confession, they stop. He has stopped walking.
* the held motes: a scatter of faint high glass tones in D minor, each panned further across than the last
  (sideways, never rising, never falling: held, bible's visual rule);
* the voice band (300 Hz to 3 kHz) is left clear for his words.

D minor, free: the tread starts at 48 BPM and slows, so the cue row's `beat` is "free". About 270 s, ending in
silence (the script's own `@music silence fade=6.0` usually ends it first). Vorbis q3, -16 LUFS integrated.

Render:  python3 tools/audio/render_all.py --only kerrid_at_sea
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

import numpy as np  # noqa: E402

from motifs import KERRID_STAIR, KERRID_STAIR_BPM  # noqa: E402
from synth.drums import frame_drum  # noqa: E402
from synth.dsp import SR, bq_highpass, bq_lowpass, filt, rng  # noqa: E402
from synth.loudness import integrated_lufs  # noqa: E402
from synth.metallophone import metallophone_note  # noqa: E402
from synth.mixer import Mixer, measure, normalize_integrated, write_ogg  # noqa: E402
from synth.pad import pad_chord, string_body  # noqa: E402
from synth.reverb import ModFDNReverb  # noqa: E402
from synth.score import n  # noqa: E402


def _mod(name: str, path: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


KS = _mod("kerrid_stair", os.path.join(MUSIC, "kerrid_stair.py"))   # bowed() and cello_body()

OUT = os.path.join(ROOT, "assets", "audio", "act2", "music", "kerrid_at_sea.ogg")
SEED = 20261930
TARGET_LUFS = -16.0
LENGTH_S = 270.0
CHORDS = [(0.0, ["D2", "A2", "F3"]), (45.0, ["Bb1", "F2", "D3"]), (90.0, ["G1", "D2", "Bb2"]),
          (135.0, ["D2", "A2", "F3"]), (180.0, ["Bb1", "F2", "D3"]), (220.0, ["G1", "D2", "Bb2"]),
          (245.0, ["D2", "A2", "F3"])]
HELD = [(5.0, "D3", 16.0), (24.0, "F3", 12.0), (46.0, "D3", 14.0), (66.0, "F3", 10.0), (92.0, "D3", 16.0),
        (114.0, "Bb2", 12.0), (138.0, "A2", 18.0), (164.0, "D3", 14.0), (184.0, "F3", 12.0), (204.0, "D3", 14.0),
        (224.0, "Bb2", 14.0), (246.0, "A2", 16.0)]            # his string: a few held notes of the chord, never a line
TREAD_FROM, TREAD_TO = 30.0, 125.0
STRIDE_SLOWS = 1.09                                         # each stride this much longer than the last
GAINS = {"pad": -2.0, "bow": -4.0, "tread": -3.0, "figure": -4.0, "motes": -8.0}


def tread_times() -> list[float]:
    """The tread's steps: KERRID_STAIR's pace at first, each step a little longer, until TREAD_TO."""
    beat = 60.0 / KERRID_STAIR_BPM
    out, t = [], TREAD_FROM
    while t < TREAD_TO:
        out.append(t)
        t += beat
        beat *= STRIDE_SLOWS
    return out


def build(mx: Mixer) -> None:
    g = rng(SEED)
    # the pad: a chord every ~37 s, each crossfading into the next
    for i, (t0, chord) in enumerate(CHORDS):
        t1 = CHORDS[i + 1][0] if i + 1 < len(CHORDS) else LENGTH_S - 6.0
        x = pad_chord([n(p) for p in chord], t1 - t0 + 2.0, 0.45, seed=SEED + 10 + i, attack=4.0, release=4.0)
        mx.add("pad", x, t0)
    # his string: long held notes
    for i, (t0, p, dur) in enumerate(HELD):
        x = KS.bowed(n(p), dur, 0.42 * float(g.uniform(0.94, 1.04)), seed=SEED + 100 + i, attack=1.6, release=2.4)
        mx.add("bow", x, t0 - KS.BOW_PRE, pan=-0.15)
    # the tread: the stair's drum on every step, the figure one note a stride, slowing until it stops
    steps = tread_times()
    for k, t in enumerate(steps):
        vel = (0.5 if k % 2 == 0 else 0.36) * (1.0 - 0.4 * k / len(steps))
        mx.add("tread", frame_drum("dum", vel, variant=k % 4, size=1.3, seed=SEED + 200), t + float(g.normal(0, 0.004)))
        if k % 2 == 0:
            m, _ = KERRID_STAIR[(k // 2) % len(KERRID_STAIR)]
            stride = (steps[k + 1] - t) * 2 if k + 1 < len(steps) else 2.5
            x = KS.bowed(float(m), stride * 0.95, 0.34 * (1.0 - 0.35 * k / len(steps)), seed=SEED + 300 + k,
                         attack=0.3, release=1.2)
            mx.add("figure", x, t - KS.BOW_PRE, pan=0.1)
    # the held motes: faint glass in D minor, each panned further across than the last (sideways)
    pool = ["D6", "F6", "A6", "C7", "D7", "E6", "A6"]
    t, pan, k = 18.0, -0.85, 0
    while t < LENGTH_S - 15.0:
        x = metallophone_note(n(pool[k % len(pool)]), 0.2 * float(g.uniform(0.6, 1.0)), seed=SEED + 400 + k, decay=4.0,
                              hardness=0.2, pair=False)
        mx.add("motes", x, t, pan=pan)
        pan = pan + 0.11 if pan < 0.85 else -0.85
        t += float(g.uniform(4.0, 8.0))
        k += 1


def render(out_path: str = OUT, verbose: bool = True, stats: dict | None = None) -> dict:
    mx = Mixer(LENGTH_S + 8.0)
    mx.bus("pad", GAINS["pad"], send=0.45, process=lambda x: string_body(x, cutoff=900.0))
    mx.bus("bow", GAINS["bow"], send=0.4, process=lambda x: filt(KS.cello_body(x), [bq_lowpass(1000, 0.7)]))  # under the voice
    mx.bus("tread", GAINS["tread"], send=0.3, process=lambda x: filt(x, [bq_lowpass(600, 0.7)]))   # far below
    mx.bus("figure", GAINS["figure"], send=0.45, process=lambda x: filt(KS.cello_body(x), [bq_lowpass(700, 0.7)]))
    mx.bus("motes", GAINS["motes"], send=0.7, process=lambda x: filt(x, [bq_highpass(3000, 0.7)]))  # above the voice
    build(mx)
    night = ModFDNReverb(rt60=4.2, rt60_high=1.0, predelay=0.05, size=1.6, mod_depth=10.0, mod_rate=0.25,
                         early_level=0.12, lowcut=80.0, seed=SEED % 9973)
    bus_lufs = {name: integrated_lufs((b.process(b.buf) if b.process else b.buf) * 10 ** (b.gain_db / 20))
                for name, b in mx.buses.items()}
    master = mx.render(reverb=night, reverb_return_db=-2.0)
    env = np.abs(master).max(axis=1)
    last = int(np.nonzero(env > 10 ** (-70 / 20))[0][-1]) + int(0.2 * SR)
    master = master[: min(last, len(master))]
    k = int(6.0 * SR)
    master[-k:] *= np.linspace(1, 0, k)[:, None] ** 2
    master = normalize_integrated(master, TARGET_LUFS, ceiling_db=-2.0)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    write_ogg(out_path, master, quality=3.0)
    m = measure(master)
    if stats is not None:
        stats["bus_lufs"] = bus_lufs
    if verbose:
        print(f"kerrid_at_sea: {m['seconds']:.2f}s  {m['integrated_lufs']:.2f} LUFS  TP {m['true_peak_dbtp']:.2f}")
    return m


if __name__ == "__main__":
    render()
