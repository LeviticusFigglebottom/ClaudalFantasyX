"""`unlamped` (final): Ch15 "Unlamped", the open sea at night aboard the bridal barge (M3-AUD-843; act_outline Ch15):
a 155 s seamless loop, grown from the Act II sketch `assets_src/music/unlamped.py` (M3-AUD-805).

Original composition for this project (SPEC §2, §9). Original-material check: the flute's vigil (Bb held, Cb-Bb-Gb-F
falling to Eb; then Gb-Ab-Bb rising to Eb and sinking to Ab), the rocking pad and the sea-glow figures are the
sketch's, imported from it (VIGIL, CHORDS, PAD, MOTES), not retyped. The new material of bars 15-22 (the flute
climbing from Eb4 through the vigil's own Bb-Gb cell to Gb5 and settling on D, the leading tone the sketch never
sounds; the pad's turn through F-flat major to B-flat major; the denser rising glow) was written for this final and
shares no phrase with the game's other themes or any melody we know. The style evoked is still a slow, unmetred
nocturne over a drone; nothing is quoted.

The brief (unchanged from the sketch): the barge carries no lamp, and nobody dares strike one. They drift south
through the night with Tobin's body under Merel's bridal cloth; the only light is the sea-glow. Past midnight the
barge drifts over a shoal where an old Rising's dead are still held, and the motes come up off the water toward
Kerrid. No pulse at all: nobody is rowing. The final gives the shoal its own passage: the middle of the night,
where the glow is thickest and the flute climbs out of its vigil and is left hanging on a leading tone that only the
pad, a bar later, resolves.

E-flat minor, notated 4/4 at 51 BPM (a bar is 4.71 s), 33 bars (an odd number again: the loop never settles into
pairs). Nothing marks a beat. The sea swells once a bar, as in the sketch.

Ensemble (all synthesized; no samples), the sketch's: the sea (its `sea`, swelling once a bar over the longer loop),
the bowed low E-flat drone (its `drone`, here breathing down under bars 20-22 so the B-flat chord is heard against a
thinner pedal), the rocking pad, the sea-glow (soft metallophone, rising figures), and the low breath flute.

Form (bars):
  1-13  A + B: the sketch whole: 1-2 the sea and the drone | 3-6 the vigil, sinking to Eb | 7 the sea, a few motes |
        8-12 the motes gather, the flute rises to Eb5 and sinks to Ab | 13 the drone
  14    the sea and the drone
  15-22 C, over the shoal: Cb Abm Cb Fb Abm Cb Bb Bb; the flute climbs Eb4-Gb5 (bar 20, the cue's highest note) and
        falls to D5 (bar 22), unresolved; the glow is thickest in bars 18-21
  23-24 the lull: Ebm, Cb; the pad resolves what the flute left; two last motes
  25-28 A': the vigil again (Ebm Cb Ebm Abm), each long note answered a moment later by one mote above it
  29-32 B': the rise without its pickup (Abm Cb Ebm Abm): Bb-Db, Eb5, Db-Bb, Ab, unresolved
  33    the drone, which is bar 1

Loop: LOOPSTART = 0 and LOOPLENGTH = the whole file. The file starts a sixteenth before bar 1's downbeat (the
sidecar's `downbeat_offset_s`); nothing is struck there, so the seam falls inside the sea's wash.

Render:  python3 assets_src/music/act2/unlamped.py   (or tools/audio/render_all.py --act2 --only act2/unlamped)
"""
from __future__ import annotations

import importlib.util
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
MUSIC = os.path.dirname(HERE)
ROOT = os.path.abspath(os.path.join(MUSIC, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools", "audio"))

import numpy as np  # noqa: E402

from synth.dsp import SR, bq_highpass, bq_lowpass, bq_peak, filt, rng  # noqa: E402
from synth.looping import LoopMixer  # noqa: E402
from synth.metallophone import metallophone_note  # noqa: E402
from synth.pad import pad_chord, string_body  # noqa: E402
from synth.reverb import ModFDNReverb  # noqa: E402
from synth.score import n  # noqa: E402
from synth.winds import breath_flute  # noqa: E402


def _mod(name: str):
    spec = importlib.util.spec_from_file_location(f"_act2_{name}", os.path.join(MUSIC, f"{name}.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


SK = _mod("unlamped")        # the sketch: its material, voices and balance
V = _mod("act2_voices")      # the Act II kit: finish()

OUT = os.path.join(ROOT, "assets", "audio", "music", "act2", "unlamped.ogg")
SEED = 20261543
TARGET_LUFS = -16.0
BPM = SK.BPM
BEAT = SK.BEAT
BAR = SK.BAR
BARS = 33
LOOP_S = BARS * BAR
FLUTE_PRE = SK.FLUTE_PRE
LEAD_IN_BEATS = SK.LEAD_IN_BEATS
QUALITY = SK.QUALITY

## the pad, bar by bar: the sketch's 13 bars, then the shoal, the lull and the returns
CHORDS = (SK.CHORDS + ["Ebm"] + ["Cb", "Abm", "Cb", "Fb", "Abm", "Cb", "Bb", "Bb"] + ["Ebm", "Cb"]
          + SK.CHORDS[2:6] + SK.CHORDS[8:12] + ["Ebm"])
PAD = dict(SK.PAD, Fb="Fb2 Cb3 Ab3", Bb="Bb2 F3 D4")

## C, over the shoal (bars 15-22): the flute climbs out of the vigil and is left on the leading tone
SHOAL = {
    15: [(None, 1), ("Eb4", 1.5), ("Gb4", 1.5)],
    16: [("Ab4", 3), ("Cb5", 1)],
    17: [("Bb4", 2), ("Gb4", 2)],
    18: [("Ab4", 4)],
    19: [("Cb5", 2), ("Db5", 1), ("Eb5", 1)],
    20: [("Gb5", 4)],
    21: [("F5", 3), ("Eb5", 1)],
    22: [("D5", 3), (None, 1)],
}
## the whole flute part: the sketch's vigil (bars 3-12), the shoal, A' (the vigil's bars 3-6) and B' (its bars 9-12)
FLUTE = dict(SK.VIGIL)
FLUTE.update(SHOAL)
FLUTE.update({b + 22: SK.VIGIL[b] for b in (3, 4, 5, 6)})
FLUTE.update({b + 20: SK.VIGIL[b] for b in (9, 10, 11, 12)})

## sea-glow: the sketch's motes (bars 2-12), then the shoal's, gathering, and the lull's
MOTES = list(SK.MOTES) + [
    (15, 1.5, "Gb5 Cb6"), (15, 3.5, "Eb6 Gb6"), (16, 0.5, "Ab5 Cb6 Eb6"), (16, 2.5, "Eb6 Ab6"),
    (17, 1.0, "Gb5 Bb5 Eb6"), (17, 3.0, "Cb6 Eb6 Gb6"),
    (18, 0.0, "Ab5 Cb6 Eb6"), (18, 1.5, "Fb5 Ab5 Cb6"), (18, 3.0, "Cb6 Eb6 Ab6"),
    (19, 0.5, "Eb5 Ab5 Cb6 Eb6"), (19, 2.0, "Ab5 Cb6 Eb6"), (19, 3.5, "Cb6 Eb6"),
    (20, 0.0, "Gb5 Bb5 Eb6 Gb6"), (20, 1.5, "Eb6 Gb6 Bb6"), (20, 3.0, "Bb5 Eb6 Gb6"),
    (21, 0.5, "F5 Bb5 D6"), (21, 2.0, "Bb5 D6 F6"), (21, 3.5, "D6 F6 Bb6"),
    (22, 1.0, "F5 Bb5 D6 F6"),
    (23, 1.0, "Bb5 Eb6 Gb6"), (24, 2.0, "Gb5 Bb5"),
    (31, 2.5, "Eb6 Gb6"), (32, 1.0, "Cb6 Eb6"),
]
## A' (bars 25-28): each long flute note is answered by one mote above it, this many beats later
ECHO_DELAY = 1.25
ECHO_BARS = (25, 26, 27, 28)

## the sketch's balance; the glow's integrated level rises with its longer part, so it comes down a little
GAINS = dict(SK.GAINS, glow=SK.GAINS["glow"] - 1.0)


def t_of(bar: int, beat: float = 0.0) -> float:
    return (bar - 1) * BAR + beat * BEAT


def _circular_dip(L: int, centre_s: float, width_s: float, depth: float) -> np.ndarray:
    """1 everywhere but a smooth (Gaussian) dip of `depth` at `centre_s`, measured circularly round the loop."""
    t = np.arange(L) / SR
    d = (t - centre_s + LOOP_S / 2) % LOOP_S - LOOP_S / 2
    return 1.0 - depth * np.exp(-0.5 * (d / (width_s / 2)) ** 2)


def sea(L: int, seed: int) -> np.ndarray:
    """The sketch's sea, swelling once a bar over this loop: its swell count is the sketch module's BARS, read when
    it is called, so this module's own copy of the sketch is told the final's bar count."""
    SK.BARS = BARS
    return SK.sea(L, seed)


def build(mx: LoopMixer) -> None:
    g = rng(SEED)
    L = mx.L
    mx.add("sea", sea(L, SEED + 1), 0.0)
    dr = SK.drone(L, SEED + 2) * _circular_dip(L, t_of(21, 2.0), 2.4 * BAR, 0.55)[:, None]
    mx.add("drone", dr, 0.0)
    for bar, ch in enumerate(CHORDS, start=1):
        x = pad_chord([n(p) for p in PAD[ch].split()], BAR * 0.96, 0.5, seed=SEED + 100 + bar, attack=2.0,
                      release=2.4, voices=3, spread_cents=8.0)
        mx.add("pad", x, t_of(bar) - 0.8)
    for i, (bar, beat, notes) in enumerate(MOTES):
        for j, p in enumerate(notes.split()):
            v = 0.26 * g.uniform(0.8, 1.05) * (0.9 ** j)
            x = metallophone_note(n(p), v, seed=SEED + 500 + 10 * i + j, decay=5.5, hardness=0.1, ombak_hz=1.6)
            mx.add("glow", x, t_of(bar, beat + 0.42 * j) + float(g.normal(0, 0.02)),
                   pan=float(np.clip(-0.6 + 0.12 * (i % 13) + 0.15 * j, -0.8, 0.8)))
    for bar in sorted(FLUTE):
        pos, first = t_of(bar), True
        for p, beats in FLUTE[bar]:
            d = beats * BEAT
            if p is None:
                pos += d
                first = True
                continue
            x = breath_flute(n(p), d * 0.95 + 0.05, 0.5 * g.uniform(0.95, 1.04), seed=SEED + 700 + int(pos * 100),
                             breath=0.55, scoop_cents=45.0 if first else 15.0, vib_cents=8.0, vib_rate=4.0,
                             swell=0.35 if beats >= 3 else 0.1, attack=0.14 if first else 0.08, release=0.9,
                             beta=0.5)
            mx.add("flute", x, pos - FLUTE_PRE + float(g.normal(0, 0.008)), pan=0.1)
            if bar in ECHO_BARS and beats >= 2:
                # a mote answers the vigil: the same pitch class, an octave and more above
                e = metallophone_note(n(p) + 24, 0.2 * g.uniform(0.85, 1.0), seed=SEED + 900 + int(pos * 10),
                                      decay=5.0, hardness=0.1, ombak_hz=1.6)
                mx.add("glow", e, pos + ECHO_DELAY * BEAT + float(g.normal(0, 0.02)),
                       pan=float(g.uniform(-0.6, 0.6)))
            pos += d
            first = False


def render(out_path: str = OUT, verbose: bool = True, stats: dict | None = None) -> dict:
    mx = LoopMixer(intro_s=0.0, loop_s=LOOP_S, preroll_s=12.0)
    G = GAINS
    mx.bus("flute", G["flute"], send=0.45, process=lambda x: filt(x, [bq_highpass(150, 0.7), bq_peak(900, 1.5, 1.0),
                                                                       bq_lowpass(4500, 0.7)]))
    mx.bus("pad", G["pad"], send=0.5, process=lambda x: string_body(x, cutoff=1100.0))
    mx.bus("drone", G["drone"], send=0.3, process=lambda x: filt(x, [bq_lowpass(700, 0.7)]))
    mx.bus("sea", G["sea"], send=0.15)
    mx.bus("glow", G["glow"], send=0.7, process=lambda x: filt(x, [bq_highpass(400, 0.7), bq_lowpass(5000, 0.7)]))
    build(mx)
    night = ModFDNReverb(rt60=5.5, rt60_high=1.5, predelay=0.06, size=1.6, mod_depth=12.0, mod_rate=0.25,
                         early_level=0.15, lowcut=80.0, seed=SEED % 9973)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    return V.finish(mx, "unlamped (final)", out_path, BPM, 4, BARS, LEAD_IN_BEATS * BEAT, TARGET_LUFS, night, -2.0,
                    verbose, stats, quality=QUALITY)


if __name__ == "__main__":
    render(sys.argv[1] if len(sys.argv) > 1 else OUT)
