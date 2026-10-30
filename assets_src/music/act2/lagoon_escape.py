"""`lagoon_escape`: Ch14 C4-C6, the cut barge across the still lagoon (M4-A2P-090; act2_plan.md §2 Ch14; the cue
sheet): about 120 s, through-composed, in three sections cut to the scenes.

Original composition for this project (SPEC §2, §9). The couple's tune is act2/peace_wedding.py's COUPLE (imported),
Merel's held string is kerrid_stair.py's bowed() through its body (imported), and the rest was written for this cue.
No phrase is taken from any existing music.

The brief (act2_plan Ch14): Merel cuts her bridal barge loose and poles the party out. Every stroke of the pole is the
first ripple in four hundred years; the bells ring; the whole city comes to its windows; Merel stays to drop the
water-gate and is taken in wedding red. Terror and wonder at once. So:
* **the pulse is the pole.** A low frame drum and a soft glass ring on every stroke (every two beats), the ripple
  heard as music; the water itself is the SFX layer's;
* **C4, the first ripple (bars 1-10, E minor):** the strokes alone over a low E-minor pad, the glass ring rising a
  step every few strokes;
* **C5, the bells and the windows (bars 11-22):** Ansedra's tower bells enter one by one, dark over water, and the
  couple's tune comes back on the breath flute, reborn out of the wedding's 3/4 into the strokes' 4/4, over
  E minor, C, G and D;
* **C6, Merel at the gate (bars 23-33, C minor):** the bells stop and the strokes thin to one a bar. Her string holds a
  few long notes (G, A-flat, G) over C minor and A-flat. The cue ends on a held C minor, which hands straight to
  `malcor_venn` (the Warden's barge closes, C minor) or to the scene's silence.

4/4 at 72 BPM (a bar is 3.33 s), 36 bars. Not a loop: its row's `beat` grid (72 BPM, the downbeat) lets the deck land
changes on its beat. Vorbis q3, -16 LUFS integrated.

Render:  python3 tools/audio/render_all.py --only lagoon_escape
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

from synth.bells import tower_bell  # noqa: E402
from synth.drums import frame_drum  # noqa: E402
from synth.dsp import SR, bq_highpass, bq_lowpass, bq_peak, filt, rng  # noqa: E402
from synth.loudness import integrated_lufs  # noqa: E402
from synth.metallophone import metallophone_note  # noqa: E402
from synth.mixer import Mixer, measure, normalize_integrated, write_ogg  # noqa: E402
from synth.pad import pad_chord, string_body  # noqa: E402
from synth.reverb import ModFDNReverb  # noqa: E402
from synth.score import n  # noqa: E402
from synth.winds import breath_flute  # noqa: E402


def _mod(name: str, path: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


PW = _mod("peace_wedding_final", os.path.join(HERE, "peace_wedding.py"))    # COUPLE
KS = _mod("kerrid_stair", os.path.join(MUSIC, "kerrid_stair.py"))           # bowed(), cello_body()

OUT = os.path.join(ROOT, "assets", "audio", "act2", "music", "lagoon_escape.ogg")
SEED = 20261940
TARGET_LUFS = -16.0
BPM = 72.0
BEAT = 60.0 / BPM
BAR = 4 * BEAT
BARS = 36
LEAD_S = 0.25
FLUTE_PRE = 0.065
C4, C5, C6, END = 1, 11, 23, 34
CHORDS = (["Em"] * 10 + ["Em", "C", "G", "D", "Em", "C", "G", "D", "Em", "C", "Am", "B"] +
          ["Cm", "Cm", "Ab", "Ab", "Cm", "Ab", "Fm", "Cm", "Ab", "Cm", "Cm"] + ["Cm", "Cm", "Cm"])
PADS = {"Em": "E2 B2 G3", "C": "C2 G2 E3", "G": "G1 D2 B2", "D": "D2 A2 F#3", "Am": "A1 E2 C3", "B": "B1 F#2 D#3",
        "Cm": "C2 G2 Eb3", "Ab": "Ab1 Eb2 C3", "Fm": "F1 C2 Ab2"}
BELLS = [(11, "E3"), (12, "B3"), (14, "G3"), (15, "E4"), (16, "B2"), (18, "D4"), (19, "G4"), (21, "E3")]
MEREL = [(24, "G3", 6.0), (26, "Ab3", 6.0), (28, "G3", 9.0), (31, "C3", 8.0)]
RIPPLE = ["B5", "B5", "C6", "D6", "E6", "E6", "F#6", "G6"]
GAINS = {"pad": -6.0, "pole": -4.0, "ripple": -12.0, "bells": -8.0, "flute": 0.0, "merel": -1.0}


def t_of(bar: int, beat: float = 0.0) -> float:
    return LEAD_S + (bar - 1) * BAR + beat * BEAT


def build(mx: Mixer) -> None:
    g = rng(SEED)
    for bar, ch in enumerate(CHORDS, start=1):                              # the pad, a chord a bar
        x = pad_chord([n(p) for p in PADS[ch].split()], BAR * 1.02, 0.42, seed=SEED + 10 + bar, attack=1.0,
                      release=1.6)
        mx.add("pad", x, t_of(bar) - 0.15)
    # the pole: a stroke every two beats until Merel's section, then one a bar, stopping at the end
    k = 0
    for bar in range(1, END):
        strokes = (0.0,) if bar >= C6 else (0.0, 2.0)
        for beat in strokes:
            t = t_of(bar, beat)
            mx.add("pole", frame_drum("dum", 0.5 * float(g.uniform(0.9, 1.05)), variant=k % 4, size=1.2,
                                      seed=SEED + 100), t + float(g.normal(0, 0.005)), pan=-0.1)
            if bar < C6:                                                    # the ripple: a soft glass ring
                m = n(RIPPLE[min(len(RIPPLE) - 1, k // 4)])
                mx.add("ripple", metallophone_note(m, 0.25, seed=SEED + 200 + k, decay=2.5, hardness=0.15, pair=False),
                       t + 0.08, pan=float(g.uniform(-0.5, 0.5)))
            k += 1
    # C5: the city's bells, one by one, dark over the water
    for i, (bar, p) in enumerate(BELLS):
        mx.add("bells", tower_bell(n(p), 0.6, seed=SEED + 300 + i, t60=8.0, dark=0.45), t_of(bar, float(i % 2)),
               pan=-0.8 + 0.22 * i)
    # C5: the couple's tune reborn on the flute: the wedding's 3-beat bars now on the strokes' pulse
    pos = t_of(C5 + 2)
    for i, bar in enumerate(PW.COUPLE):
        for k2, (p, beats) in enumerate(bar):
            d = beats * BEAT * (4.0 / 3.0)                                  # three beats become a 4/4 bar
            x = breath_flute(n(p), d * 0.92 + 0.04, 0.48 * float(g.uniform(0.95, 1.04)), seed=SEED + 400 + 10 * i + k2,
                             breath=0.3, scoop_cents=20.0, vib_cents=12.0 if beats >= 2 else 5.0, swell=0.2 if beats >= 3
                             else 0.0, attack=0.07, release=0.45)
            mx.add("flute", x, pos - FLUTE_PRE + float(g.normal(0, 0.006)), pan=0.1)
            pos += d
    # C6: Merel at the gate: her string's few held notes over C minor
    for i, (bar, p, dur) in enumerate(MEREL):
        x = KS.bowed(n(p), dur, 0.42, seed=SEED + 500 + i, attack=0.9, release=2.0)
        mx.add("merel", x, t_of(bar) - KS.BOW_PRE, pan=-0.2)


def render(out_path: str = OUT, verbose: bool = True, stats: dict | None = None) -> dict:
    mx = Mixer(t_of(BARS + 1) + 8.0)
    mx.bus("pad", GAINS["pad"], send=0.45, process=lambda x: string_body(x, cutoff=1400.0))
    mx.bus("pole", GAINS["pole"], send=0.35, process=lambda x: filt(x, [bq_lowpass(900, 0.7)]))
    mx.bus("ripple", GAINS["ripple"], send=0.7, process=lambda x: filt(x, [bq_highpass(800, 0.7)]))
    mx.bus("bells", GAINS["bells"], send=0.6, process=lambda x: filt(x, [bq_lowpass(5000, 0.7)]))
    mx.bus("flute", GAINS["flute"], send=0.4, process=lambda x: filt(x, [bq_highpass(200, 0.7), bq_peak(1500, 1.0, 1.0),
                                                                     bq_lowpass(7000, 0.7)]))
    mx.bus("merel", GAINS["merel"], send=0.45, process=lambda x: filt(KS.cello_body(x), [bq_lowpass(2800, 0.7)]))
    build(mx)
    lagoon = ModFDNReverb(rt60=4.5, rt60_high=1.4, predelay=0.06, size=1.8, mod_depth=9.0, mod_rate=0.3,
                          early_level=0.15, lowcut=90.0, seed=SEED % 9973)
    bus_lufs = {name: integrated_lufs((b.process(b.buf) if b.process else b.buf) * 10 ** (b.gain_db / 20))
                for name, b in mx.buses.items()}
    master = mx.render(reverb=lagoon, reverb_return_db=-2.0)
    env = np.abs(master).max(axis=1)
    last = int(np.nonzero(env > 10 ** (-70 / 20))[0][-1]) + int(0.2 * SR)
    master = master[: min(last, len(master))]
    k = int(4.0 * SR)
    master[-k:] *= np.linspace(1, 0, k)[:, None] ** 2
    master = normalize_integrated(master, TARGET_LUFS, ceiling_db=-2.0)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    write_ogg(out_path, master, quality=3.0)
    m = measure(master)
    if stats is not None:
        stats["bus_lufs"] = bus_lufs
    if verbose:
        print(f"lagoon_escape: {m['seconds']:.2f}s  {m['integrated_lufs']:.2f} LUFS  TP {m['true_peak_dbtp']:.2f}")
    return m


if __name__ == "__main__":
    render()
