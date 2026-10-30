"""`sefir_go_home`: Ch16 C5, Sefir's temptation (M4-A2P-090; act2_plan.md §2 Ch16; ADR 0204 §10; the cue sheet):
about 2 min. The Long Stillness offered as a gift, at its warmest, and frightening because it is kind.

Original composition for this project (SPEC §2, §9). The only borrowed lines are our own: High Warden Sefir's motif
(sefir_theme.py MOTIF: G4 C5 D5 E5 D5, slipping a half step to C#5, held over F, a leading tone that never leads), and
the Order's congregational tune ORDER_HUM (motifs.py), both imported. The lullaby's chords and voicings were written
for this scene. Nothing is taken from any existing music.

**The one time the Order sings** (ADR 0204 §10). The Order hums; only Cantors sing (bible §4). Here, once, the
congregation **sings** ORDER_HUM as a lullaby: that is what the temptation costs, said in sound. Narrative confirms in
review.

The brief (act2_plan Ch16): Sefir arrives at the Choir and offers "go home", the Long Stillness, as a gift; Asha
refuses; Ysolde: "Then who does it take?"; Kerrid: "I carried her up so you could do this." Said, never drawn. The
scene cuts to silence on the refusal (the sequencer's `@music silence`), so the cue only has to be the offer:
* bars 1-4: the grand piano alone, a lullaby's broken chords in 3/4 (C, A minor, F, G);
* bars 5-10: Sefir's motif in the right hand over C and F, ending on its held C# over F: the warmth with the wrong
  note in it;
* bars 11-28: the lullaby. ORDER_HUM is sung by many, men and women, slow and close, over the piano and a warm
  pad (every note of the tune lies in C major);
* bars 29-35: the singing stops; the piano states the motif once more, and the C# is left hanging.

C major, 3/4 at 52 BPM (a bar is 3.46 s), 35 bars, about 2 min. The cue row's beat grid is 52 BPM. Vorbis q3,
-16 LUFS integrated. Plain git (ADR 0175).

Render:  python3 tools/audio/render_all.py --only sefir_go_home
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

from motifs import ORDER_HUM  # noqa: E402
from synth.dsp import bq_highpass, bq_lowpass, filt, rng  # noqa: E402
from synth.grand import PianoBody  # noqa: E402
from synth.loudness import integrated_lufs  # noqa: E402
from synth.mixer import Mixer  # noqa: E402
from synth.pad import pad_chord, string_body  # noqa: E402
from synth.parallel import render_jobs  # noqa: E402
from synth.performance import plan_pedal  # noqa: E402
from synth.reverb import ModFDNReverb  # noqa: E402
from synth.score import n  # noqa: E402
from synth.voice import sing  # noqa: E402


def _mod(name: str, path: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


SEFIR = _mod("sefir_theme", os.path.join(MUSIC, "sefir_theme.py"))           # MOTIF
HFV = _mod("hush_first_verse", os.path.join(MUSIC, "hush_first_verse.py"))     # _piano_jobs(), _finish()

OUT = os.path.join(ROOT, "assets", "audio", "act2", "music", "sefir_go_home.ogg")
SEED = 20262000
BPM = 52.0
BEAT = 60.0 / BPM
BAR = 3 * BEAT
BARS = 35
T0 = 0.6
CHORDS = (["C", "Am", "F", "G"] + ["C", "C", "F", "F", "F", "F"] +
          ["C", "Am", "F", "G", "C", "Am", "Dm", "G", "C", "Em", "F", "G", "C", "Am", "F", "G", "C", "C"] +
          ["C", "C", "F", "F", "F", "F", "F"])
LH = {"C": "C3 G3 E4", "Am": "A2 E3 C4", "F": "F2 C3 A3", "G": "G2 D3 B3", "Dm": "D3 A3 F4", "Em": "E3 B3 G4"}
PAD = {"C": "C3 E3 G3", "Am": "A2 C3 E3", "F": "F2 A2 C3", "G": "G2 B2 D3", "Dm": "D3 F3 A3", "Em": "E3 G3 B3"}
MOTIF_AT = (5, 29)
SING_AT = (11, 20)        # the lullaby sung twice, the second time from bar 20
SING_STRETCH = 1.5          # ORDER_HUM's beats lengthened for the lullaby
VOWELS = ["o", "a", "u", "a", "o", "e", "a", "u", "o", "a"]
# Bus gains from measured bus loudness (render(stats=...)): the piano leads (about -18 LUFS on its bus), the choir
# 2 LU under it, the pad about 12 under. The grand piano model's raw level is far below a voice's, hence its gain.
GAINS = {"piano": 35.0, "pad": 6.0, "choir": -10.0}


def t_of(bar: int, beat: float = 0.0) -> float:
    return T0 + (bar - 1) * BAR + beat * BEAT


def piano_notes(g) -> list[dict]:
    notes = []
    for bar, ch in enumerate(CHORDS, start=1):
        for i, p in enumerate(LH[ch].split()):                                 # a lullaby's broken chord
            notes.append(dict(m=n(p), vel=(0.27 if i == 0 else 0.19) * float(g.uniform(0.93, 1.05)),
                              t0=t_of(bar, i) + float(g.normal(0, 0.008)), key_up=BAR * (1.0 if i == 0 else 0.6),
                              role="bass" if i == 0 else "acc"))
    for start in MOTIF_AT:                                                     # Sefir's motif, the C# held
        pos = t_of(start)
        for k, (p, beats) in enumerate(SEFIR.MOTIF):
            notes.append(dict(m=n(p), vel=0.33 * float(g.uniform(0.95, 1.04)), t0=pos + float(g.normal(0, 0.006)),
                              key_up=beats * BEAT * (1.0 if k == len(SEFIR.MOTIF) - 1 else 0.9), role="mel"))
            pos += beats * BEAT
    return sorted(notes, key=lambda d: d["t0"])


def add_choir(mx: Mixer, g) -> None:
    line = [(float(m), b * BEAT * SING_STRETCH) for m, b in ORDER_HUM]
    for v in range(10):                                                        # the congregation, men and women
        female = v % 2 == 1
        shift = 12.0 if female else 0.0
        cents = float(g.normal(0, 7))
        ph = [(VOWELS[i % len(VOWELS)], d) for i, (_, d) in enumerate(line)]
        pi = [(m + shift + cents / 100.0, d) for m, d in line]
        x = sing(ph, pi, vel=0.5, seed=SEED + 500 + v, scale=1.17 if female else 1.0, vib_cents=10.0)
        for k, bar in enumerate(SING_AT):
            mx.add("choir", x * (1.0 if k == 0 else 0.85), t_of(bar) + float(g.uniform(0, 0.15)),
                   pan=float(g.uniform(-0.8, 0.8)))


def render(out_path: str = OUT, verbose: bool = True, stats: dict | None = None) -> dict:
    g = rng(SEED)
    notes = piano_notes(g)
    changes = [t_of(b) for b in range(2, BARS + 1)]
    pedal = plan_pedal(changes, start=T0, end_release=t_of(BARS + 1), release_len=4.0, g=g, half={0})
    mx = Mixer(t_of(BARS + 1) + 8.0)
    mx.bus("piano", GAINS["piano"], send=0.3, process=PianoBody(pedal))
    mx.bus("pad", GAINS["pad"], send=0.45, process=lambda x: string_body(x, cutoff=1400.0))
    mx.bus("choir", GAINS["choir"], send=0.5, process=lambda x: filt(x, [bq_highpass(120, 0.7), bq_lowpass(5000, 0.7)]))
    for nt, x in zip(notes, render_jobs(HFV._piano_jobs(notes, pedal, SEED + 5))):
        mx.add("piano", x, nt["t0"], pan=float(np.clip((nt["m"] - 64) / 60.0, -0.3, 0.3)))
    for bar, ch in enumerate(CHORDS, start=1):
        if SING_AT[0] <= bar < MOTIF_AT[1]:
            mx.add("pad", pad_chord([n(p) for p in PAD[ch].split()], BAR * 1.02, 0.4, seed=SEED + 300 + bar,
                                    attack=1.0, release=1.5), t_of(bar) - 0.1)
    add_choir(mx, g)
    hall = ModFDNReverb(rt60=3.2, rt60_high=1.4, predelay=0.03, size=1.3, mod_depth=8.0, mod_rate=0.4,
                        early_level=0.2, lowcut=90.0, seed=SEED % 9973)
    bus_lufs = {name: integrated_lufs((b.process(b.buf) if b.process else b.buf) * 10 ** (b.gain_db / 20))
                for name, b in mx.buses.items()}
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    m = HFV._finish(mx, hall, out_path, 3.0)
    if stats is not None:
        stats["bus_lufs"] = bus_lufs
    if verbose:
        print("  buses", {k: round(v, 1) for k, v in bus_lufs.items()})
        print(f"sefir_go_home: {m['seconds']:.1f}s  {m['integrated_lufs']:.2f} LUFS  TP {m['true_peak_dbtp']:.2f} dBTP")
    return m


if __name__ == "__main__":
    render()
