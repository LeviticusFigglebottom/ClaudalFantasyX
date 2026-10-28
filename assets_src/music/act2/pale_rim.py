"""`pale_rim` (final): Ch16 "The Edge of the World", the Pale Rim, the white shallows (M3-AUD-843; act_outline Ch16):
a 155 s seamless loop, grown from the Act II sketch `assets_src/music/pale_rim.py` (M3-AUD-805).

Original composition for this project (SPEC §2, §9). Original-material check: the flute's three short calls (B-E;
F#-E-B; C#-B, then A# once), the halo and the floor are the sketch's, imported from it (CALLS, HALO, FLOOR, and its
`sustained` and `wade` voices), not retyped. The new material (bars 16-22, two flutes trading the calls' cells,
turned and answered; the glare, a second halo on B; the floor's one move, to an open fifth on B; and the third
call's last return in bars 27-29, which lets its G# be held and then falls through F# to the low E) was written for
this final and shares no phrase with the game's other themes or any melody we know. The style evoked is still a
near-static drone piece with distant wind voices; nothing is quoted.

The brief (unchanged from the sketch): the southern edge of the known sea. Days of wading, ankle- to waist-deep,
over white sand under a white sky; the horizon goes white. Kerrid walks last in the line, as on a stair, behind
Asha, toward the Choir where the woman he got up his stair was spent. Bleached, vast, almost silent. The final adds
the middle of a long day's wading: the glare thickens, the four ahead draw away (their steps go far and dim) while
Kerrid's stay close, and a second, farther flute answers the first, as if the white itself called back.

E, with no third for most of the loop (fifths and octaves only: the white), 4/4 at 51 BPM (a bar is 4.71 s),
33 bars. The only pulse is the wading: five walkers, a step every beat and a half each, a little irregular.

Ensemble (all synthesized; no samples): the sketch's halo (high sine doublets), floor (E1-B1-E2), wading (noise
swashes and small bubbles) and far breath flute; new here: the glare (B6-F#7-B7 doublets, swelling in bars 15-24),
the floor's B fifth (B0-F#1-B1, bars 17-23) and a second flute, farther still (bars 17-21).

Form (bars):
  1-13  A: the sketch whole: 1-2 the halo and the wading | 3-4 the first call | 5-6 wading | 7-8 the second call |
        9 wading | 10-11 the third call (A#, G#) | 12-13 wading
  14-15 wading; the glare begins
  16-22 C, the white noon: the four ahead draw away, Kerrid's steps stay near; the floor moves to B; the near flute
        and the far flute trade the calls: 16 B-E | 17 (far) E-B | 19 F#-B-A#-F# | 20 (far) C#-B | 22 E-F#-E-B
  23-26 wading; the glare and the floor's B fade; the four come back near
  27-29 A': the third call's last return: C#-B-A#, G# held, F#, and down to the low E
  30-33 wading, the halo and the floor alone, which is bar 1

Loop: LOOPSTART = 0 and LOOPLENGTH = the whole file. The file starts a sixteenth before bar 1's downbeat (the
sidecar's `downbeat_offset_s`), between two steps (nobody's foot lands within 0.6 beats of the seam), so the seam
falls in the halo alone.

Render:  python3 assets_src/music/act2/pale_rim.py   (or tools/audio/render_all.py --act2 --only act2/pale_rim)
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

from synth.dsp import SR, bq_highpass, bq_lowpass, filt, rng  # noqa: E402
from synth.looping import LoopMixer  # noqa: E402
from synth.reverb import ModFDNReverb  # noqa: E402
from synth.score import n  # noqa: E402
from synth.winds import breath_flute  # noqa: E402


def _mod(name: str):
    spec = importlib.util.spec_from_file_location(f"_act2_{name}", os.path.join(MUSIC, f"{name}.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


SK = _mod("pale_rim")        # the sketch: its material, voices and balance
V = _mod("act2_voices")      # the Act II kit: finish()

OUT = os.path.join(ROOT, "assets", "audio", "music", "act2", "pale_rim.ogg")
SEED = 20261643
TARGET_LUFS = -16.0
BPM = SK.BPM
BEAT = SK.BEAT
BAR = SK.BAR
BARS = 33
LOOP_S = BARS * BAR
FLUTE_PRE = SK.FLUTE_PRE
LEAD_IN_BEATS = SK.LEAD_IN_BEATS
QUALITY = SK.QUALITY

## the glare: a second halo, on B (note, level, doublet split in Hz); and the floor's B fifth
GLARE = [("B6", 1.0, 0.27), ("F#7", 0.5, 0.52), ("B7", 0.18, 0.7)]
FLOOR_B = [("B0", 1.0), ("F#1", 0.6), ("B1", 0.45)]
## (centre bar, width in bars) of each swell; each is a smooth bump measured circularly round the loop
GLARE_SWELL = (19.5, 9.0)
FLOOR_SWELL = (20.0, 6.0)
## the four ahead draw away (their steps go to the far bus) around here
AHEAD = (19.0, 8.0)

## the calls: the sketch's three (bars 3, 7, 10), then C's exchange and A', as (bar, beat, voice, [(pitch, beats)])
CALLS = [(bar, beat, "near", notes) for bar, beat, notes in SK.CALLS] + [
    (16, 1.0, "near", [("B4", 2), ("E5", 4)]),
    (17, 2.5, "far", [("E5", 2), ("B4", 5)]),
    (19, 0.0, "near", [("F#5", 1.5), ("B5", 1.5), ("A#5", 1), ("F#5", 4)]),
    (20, 3.0, "far", [("C#5", 2), ("B4", 5)]),
    (22, 0.0, "near", [("E5", 1.5), ("F#5", 1.5), ("E5", 1), ("B4", 5)]),
    (27, 0.0, "near", [("C#5", 2), ("B4", 2), ("A#4", 1), ("G#4", 3), ("F#4", 1), ("E4", 6)]),
]

## the sketch's balance; the far flute and the far steps sit under their near twins, the glare under the halo
GAINS = dict(SK.GAINS, far=SK.GAINS["flute"] - 5.0, wade_far=SK.GAINS["wade"] - 3.0, glare=SK.GAINS["halo"] - 2.0,
             floor_b=SK.GAINS["floor"])


def t_of(bar: int, beat: float = 0.0) -> float:
    return (bar - 1) * BAR + beat * BEAT


def bump(L: int, centre_bar: float, width_bars: float) -> np.ndarray:
    """A smooth raised-cosine swell, 0 outside `width_bars` round `centre_bar` (circular), 1 at its centre."""
    t = np.arange(L) / SR
    c = t_of(1) + (centre_bar - 1) * BAR
    d = (t - c + LOOP_S / 2) % LOOP_S - LOOP_S / 2
    h = width_bars * BAR / 2
    return np.where(np.abs(d) < h, 0.5 + 0.5 * np.cos(np.pi * d / h), 0.0)


def build(mx: LoopMixer) -> None:
    g = rng(SEED)
    L = mx.L
    fl = bump(L, *FLOOR_SWELL)[:, None]
    mx.add("halo", SK.sustained(L, SK.HALO, SEED + 1, cycles=(3, 7)), 0.0)
    mx.add("glare", SK.sustained(L, GLARE, SEED + 3, cycles=(4, 9)) * bump(L, *GLARE_SWELL)[:, None], 0.0)
    mx.add("floor", SK.sustained(L, SK.FLOOR, SEED + 2, cycles=(2, 4)) * (1.0 - 0.8 * fl), 0.0)
    mx.add("floor_b", SK.sustained(L, FLOOR_B, SEED + 4, cycles=(2, 4)) * fl, 0.0)
    # wading: five walkers, a step every 1.5 beats each, each on its own phase; the last one (Kerrid) a little behind.
    # Around AHEAD the four in front draw away: each step is shared between the near bus and the far one.
    total_beats = BARS * 4
    steps = int(round(total_beats / 1.5))
    for w in range(5):
        phase = (0.2 + 0.29 * w) % 1.5
        for k in range(steps):
            beat = (phase + 1.5 * k) % total_beats
            if beat > total_beats - 0.6 or beat < 0.6:     # nobody's foot lands at the seam
                continue
            v = (0.55 if w < 4 else 0.4) * g.uniform(0.7, 1.05)
            ts = beat * BEAT + float(g.normal(0, 0.05))
            pan = float(-0.5 + 0.25 * w + g.normal(0, 0.05))
            x = SK.wade(SEED + 100 + 1000 * w + k, v)
            bar = 1 + beat / 4
            d = abs(bar - AHEAD[0])
            a = 0.5 + 0.5 * np.cos(np.pi * d / (AHEAD[1] / 2)) if (w < 4 and d < AHEAD[1] / 2) else 0.0
            if a < 0.999:
                mx.add("wade", x * (1.0 - a), ts, pan=pan)
            if a > 0.001:
                mx.add("wade_far", x * a, ts, pan=float(np.clip(pan * 0.5, -0.4, 0.4)))
    for i, (bar, beat, voice, notes) in enumerate(CALLS):
        pos, first = t_of(bar, beat), True
        for p, beats in notes:
            d = beats * BEAT
            x = breath_flute(n(p), d * 0.95, 0.42 * g.uniform(0.95, 1.04), seed=SEED + 500 + int(pos * 100),
                             breath=0.6 if voice == "near" else 0.7, scoop_cents=40.0 if first else 12.0,
                             vib_cents=6.0, vib_rate=4.2 if voice == "near" else 3.8,
                             swell=0.4 if beats >= 4 else 0.15, attack=0.2 if first else 0.1, release=1.2, beta=0.5)
            pan = (0.35 - 0.3 * (i % 3)) if voice == "near" else -0.55
            mx.add("flute" if voice == "near" else "far", x, pos - FLUTE_PRE + float(g.normal(0, 0.01)), pan=pan)
            pos += d
            first = False


def render(out_path: str = OUT, verbose: bool = True, stats: dict | None = None) -> dict:
    mx = LoopMixer(intro_s=0.0, loop_s=LOOP_S, preroll_s=14.0)
    G = GAINS
    mx.bus("flute", G["flute"], send=0.85, process=lambda x: filt(x, [bq_highpass(250, 0.7), bq_lowpass(3200, 0.7)]))
    mx.bus("far", G["far"], send=1.0, process=lambda x: filt(x, [bq_highpass(320, 0.7), bq_lowpass(2200, 0.7)]))
    mx.bus("halo", G["halo"], send=0.4)
    mx.bus("glare", G["glare"], send=0.45)
    mx.bus("floor", G["floor"], send=0.1, process=lambda x: filt(x, [bq_lowpass(300, 0.7)]))
    mx.bus("floor_b", G["floor_b"], send=0.1, process=lambda x: filt(x, [bq_lowpass(300, 0.7)]))
    mx.bus("wade", G["wade"], send=0.2, process=lambda x: filt(x, [bq_highpass(150, 0.7), bq_lowpass(2600, 0.7)]))
    mx.bus("wade_far", G["wade_far"], send=0.55,
           process=lambda x: filt(x, [bq_highpass(220, 0.7), bq_lowpass(1500, 0.7)]))
    build(mx)
    white = ModFDNReverb(rt60=7.0, rt60_high=2.0, predelay=0.08, size=1.8, mod_depth=12.0, mod_rate=0.2,
                         early_level=0.05, lowcut=120.0, seed=SEED % 9973)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    return V.finish(mx, "pale_rim (final)", out_path, BPM, 4, BARS, LEAD_IN_BEATS * BEAT, TARGET_LUFS, white, -1.0,
                    verbose, stats, quality=QUALITY)


if __name__ == "__main__":
    render(sys.argv[1] if len(sys.argv) > 1 else OUT)
