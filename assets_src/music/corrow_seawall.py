"""`corrow_seawall`: Corrow Bastion and the seawall before the storm (M3-AUD-04; act_outline Ch8, bible §5.4): a 75.8 s
seamless area loop.

Original composition for this project (SPEC §2, §9). The ground bass, the flute's four phrases, the hummed chorale
and the ostinato were written for this town and are not derived from any existing tune. The brief: Corrow's
defence has been the same for nine hundred years (light the Coilspire beacon; get the low town up the Fisher Stair
onto the wall before the sea does). The wall's carved Watchers have closed eyes and open mouths, as if humming. The
cue is for walking the town before the storm: steady, weathered, dutiful, not afraid yet and not hopeful either.

So the piece is a ground: one four-bar bass line (B D | A F# | G E G | F#) that comes round six times and never
changes, while everything above it varies. Each statement ends on the dominant (F#) and climbs back to B at the
next, so the loop has no last bar, only the next time round.

B minor (Aeolian; the F# chord takes A#, its only borrowed note), 4/4 at 76 BPM (a bar is 3.158 s), 24 bars.

Ensemble (all synthesized; no samples):
* breath flute, low (B3-D5) and darker than Haluna's: the tune, a fisher's whistle rather than a festival flute;
* the Watchers: men humming a slow descending chorale (F# E D C#) from the fourth statement, women a third above
  from the fifth (the Order hums; only Cantors sing, bible §4). The Bastion is a Stillguard garrison;
* muted plucked strings in eighths (rope and block: the town's work);
* fingered bass on the ground; a kettle gong (the beacon) at each statement, a large gong at bars 1 and 13;
* frame drum footsteps on every beat (dum on 1 and 3), the big drum at each statement: the stair.

Form (statements of 4 bars): 1 the town (bass, plucks, steps) | 2 tune a | 3 tune b | 4 the Watchers hum alone over
the ground | 5 tune a' with the men and women | 6 tune c (highest), the hum lets go, into the wrap.

Loop: LOOPSTART = 0 and LOOPLENGTH = the whole file. The file starts a sixteenth before bar 1's downbeat (the
sidecar's `downbeat_offset_s`), so the wrap seam falls in a quiet sixteenth.

Render:  python3 assets_src/music/corrow_seawall.py   (or tools/audio/render_all.py)
"""
from __future__ import annotations

import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools", "audio"))

import numpy as np  # noqa: E402

from synth.drums import big_drum, frame_drum  # noqa: E402
from synth.dsp import SR, bq_highpass, bq_lowpass, bq_peak, filt, rng  # noqa: E402
from synth.electric import bass_note, string_pluck  # noqa: E402
from synth.gongs import kettle_gong, large_gong  # noqa: E402
from synth.looping import LoopMixer, master_loop, write_loop_sidecar  # noqa: E402
from synth.mixer import measure, write_ogg  # noqa: E402
from synth.reverb import ModFDNReverb  # noqa: E402
from synth.score import n  # noqa: E402
from synth.voice import hum_ensemble  # noqa: E402
from synth.winds import breath_flute  # noqa: E402

OUT = os.path.join(ROOT, "assets", "audio", "music", "corrow_seawall.ogg")
SEED = 20261203
TARGET_LUFS = -16.0
BPM = 76.0
BEAT = 60.0 / BPM
BAR = 4 * BEAT
STATEMENTS = 6
BARS = 4 * STATEMENTS
LOOP_S = BARS * BAR
## breath_flute's tone starts after its breath (0.05-0.08 s): notes are placed this much early.
FLUTE_PRE = 0.065
## the file starts this many beats before bar 1's downbeat (see render())
LEAD_IN_BEATS = 0.25

## the ground: (pitch, beats) per bar, the same every statement
GROUND = [[("B1", 3), ("D2", 1)], [("A1", 2), ("F#1", 2)], [("G1", 2), ("E1", 1), ("G1", 1)], [("F#1", 4)]]
## the harmony by half bar, and its tones for the plucks (root, fifth, octave)
HALVES = [("Bm", "Bm"), ("A", "F#m"), ("G", "Em"), ("F#", "F#")]
TONES = {"Bm": ["B3", "F#4", "B4"], "A": ["A3", "E4", "A4"], "F#m": ["F#3", "C#4", "F#4"],
         "G": ["G3", "D4", "G4"], "Em": ["E3", "B3", "E4"], "F#": ["F#3", "C#4", "F#4"]}
PLUCK = [0, 1, 2, 1]                     # indices into TONES per eighth, each half bar

TUNE_A = [[("F#4", 2), ("D4", 1), ("E4", 1)], [("E4", 1.5), ("F#4", .5), ("C#4", 2)],
          [("D4", 1), ("B3", 1), ("E4", 1), ("G4", 1)], [("F#4", 3), (None, 1)]]
TUNE_B = [[("B4", 2), ("A4", 1), ("F#4", 1)], [("A4", 1), ("G4", .5), ("F#4", .5), ("E4", 1), ("C#4", 1)],
          [("D4", 1.5), ("E4", .5), ("B3", 2)], [("C#4", 1), ("D4", 1), ("C#4", 2)]]
TUNE_A2 = [[("F#4", 2), ("D4", 1), ("E4", 1)], [("E4", 1.5), ("F#4", .5), ("C#4", 2)],
           [("G4", 2), ("E4", 2)], [("F#4", 4)]]
TUNE_C = [[("D5", 2), ("C#5", 1), ("B4", 1)], [("A4", 2), ("F#4", 2)],
          [("G4", 1), ("F#4", 1), ("E4", 1), ("D4", 1)], [("C#4", 3), (None, 1)]]
MEN = ["F#3", "E3", "D3", "C#3"]         # the Watchers' chorale, one pitch a bar
WOMEN = ["D4", "C#4", "B3", "A#3"]


def t_of(bar: int, beat: float = 0.0) -> float:
    return (bar - 1) * BAR + beat * BEAT


def add_tune(mx: LoopMixer, bars: list, start_bar: int, seed: int, vel: float, pan: float = -0.08) -> None:
    g = rng(seed)
    first = True
    for i, bar in enumerate(bars):
        pos = t_of(start_bar + i)
        for p, beats in bar:
            d = beats * BEAT
            if p is None:
                pos += d
                first = True
                continue
            v = vel * g.uniform(0.93, 1.04) * (1.05 if beats >= 2 else 1.0)
            x = breath_flute(n(p), d * 0.95 + 0.03, v, seed=seed + int(round(pos * 1000)), breath=0.5,
                             scoop_cents=40.0 if first else 12.0, vib_cents=9.0 if beats >= 2 else 3.0, vib_rate=4.2,
                             swell=0.25 if beats >= 3 else 0.0, attack=0.07 if first else 0.04, release=0.35,
                             beta=0.48)
            mx.add("flute", x, pos - FLUTE_PRE + float(g.normal(0, 0.004)), pan=pan)
            pos += d
            first = False


def hum_part(pitches: list, bars: int, voices: int, seed: int, register: str, fade_in: float,
             fade_out_bar: int) -> np.ndarray:
    """A hum over `bars` bars of the chorale (one pitch a bar, cycling), faded in, let go from `fade_out_bar`."""
    line = [(n(pitches[k % len(pitches)]), BAR) for k in range(bars)]
    x = hum_ensemble(line, voices=voices, seed=seed, register=register, spread=0.9)
    env = np.ones(len(x))
    k = int(fade_in * SR)
    env[:k] = np.linspace(0, 1, k) ** 2
    s = int(fade_out_bar * BAR * SR)
    env[s:] = np.exp(-np.arange(len(env) - s) / SR / 1.2)
    return x * env[:, None]


def build(mx: LoopMixer) -> None:
    g = rng(SEED)
    for st in range(STATEMENTS):
        for k in range(4):
            bar = 4 * st + k + 1
            # the ground
            pos = 0.0
            for p, beats in GROUND[k]:
                v = (0.58 if pos == 0 else 0.44) * g.uniform(0.95, 1.04)
                x = bass_note(n(p), beats * BEAT * 0.92, v, seed=SEED + 30000 + 10 * bar + int(pos), mute=0.2)
                mx.add("bass", x, t_of(bar, pos) + 0.004, pan=0.0)
                pos += beats
            # rope and block: muted plucks in eighths (only on the beats while the Watchers hum alone)
            for half, chord in enumerate(HALVES[k]):
                tones = TONES[chord]
                for e, idx in enumerate(PLUCK):
                    if st == 3 and e % 2:
                        continue
                    if st == 0 and k < 2 and half == 1 and e >= 2:
                        continue
                    v = (0.50 if e == 0 else 0.36) * g.uniform(0.9, 1.06)
                    x = string_pluck(n(tones[idx]), BEAT * 0.48, v, seed=SEED + 20000 + 40 * bar + 4 * half + e,
                                     pick_pos=0.14, t60=1.6, mute=0.42, max_f=4500.0, release=0.04)
                    mx.add("pluck", x, t_of(bar, 2 * half + e / 2) + float(g.normal(0, 0.004)),
                           pan=0.28 if e % 2 else 0.18)
            # the stair: a step on every beat, the weight on 1 and 3
            for b in range(4):
                stroke, v = ("dum", 0.32 if b == 0 else 0.24) if b in (0, 2) else ("tek", 0.25)
                x = frame_drum(stroke, v * g.uniform(0.9, 1.08), variant=bar * 4 + b, seed=SEED + 1)
                mx.add("drums", x, t_of(bar, b) + float(g.normal(0, 0.005)), pan=-0.1 if stroke == "tek" else 0.05)
                if b == 2 and k == 3:
                    x = frame_drum("ghost", 0.15, variant=bar, seed=SEED + 1)
                    mx.add("drums", x, t_of(bar, 3.5), pan=-0.12)
            if k == 0:
                mx.add("drums", big_drum(0.40 if st in (0, 3) else 0.32, variant=st, seed=SEED + 2), t_of(bar))
        # the beacon: a kettle gong on F# at each statement; the large gong at statements 1 and 4
        mx.add("gong", kettle_gong(n("F#4"), 0.30, seed=SEED + 400 + st, t60=3.0), t_of(4 * st + 1, 0.0), pan=0.35)
    for bar in (1, 13):
        mx.add("gong", large_gong(n("B1"), 0.30, seed=SEED + 500 + bar, t60=9.0), t_of(bar), pan=-0.15)
    # the tune
    add_tune(mx, TUNE_A, 5, SEED + 600, 0.52)
    add_tune(mx, TUNE_B, 9, SEED + 700, 0.54)
    add_tune(mx, TUNE_A2, 17, SEED + 800, 0.52)
    add_tune(mx, TUNE_C, 21, SEED + 900, 0.56)
    # the Watchers
    mx.add("hum", hum_part(MEN, 12, 12, SEED + 11, "low", 3.0, 11), t_of(13) - 0.15)
    mx.add("hum", hum_part(WOMEN, 8, 8, SEED + 12, "high", 3.0, 7), t_of(17) - 0.1)


# Bus gains were set from measured bus loudness (render(stats=...)["bus_lufs"]) for these levels relative to the
# flute (0 LU): the hum -5 (measured over the whole loop; it sounds in the last half), plucks -9, bass -7,
# drums -10 (the steps; their hits still take up to ~4 dB of fast limiting on 0.5 % of samples), gongs -12.
def render(out_path: str = OUT, verbose: bool = True, stats: dict | None = None) -> dict:
    mx = LoopMixer(intro_s=0.0, loop_s=LOOP_S, preroll_s=10.0)
    mx.bus("flute", 0.0, send=0.32, process=lambda x: filt(x, [bq_highpass(150, 0.7), bq_peak(1800, 1.5, 1.0),
                                                                 bq_lowpass(6500, 0.7)]))
    mx.bus("hum", -5.8, send=0.70)
    mx.bus("pluck", 3.5, send=0.18, process=lambda x: filt(x, [bq_highpass(140, 0.7), bq_lowpass(4200, 0.7)]))
    mx.bus("bass", -0.4, send=0.05, process=lambda x: filt(x, [bq_lowpass(900, 0.7)]))
    mx.bus("drums", 0.6, send=0.22, process=lambda x: filt(x, [bq_lowpass(4500, 0.7)]))
    mx.bus("gong", -10.5, send=0.45)
    build(mx)
    wall = ModFDNReverb(rt60=2.2, rt60_high=0.9, predelay=0.025, size=1.0, mod_depth=8.0, mod_rate=0.5,
                        early_level=0.34, lowcut=110.0, seed=SEED % 9973)
    _, loop = mx.render(reverb=wall, reverb_return_db=-3.0)
    # The loop is periodic, so it may start anywhere: it starts a sixteenth before bar 1's downbeat, so the wrap seam
    # falls in a quiet sixteenth instead of on the loop's heaviest attack (big drum, both gongs and the bass at once).
    lead_in = int(round(LEAD_IN_BEATS * BEAT * SR))
    loop = np.roll(loop, lead_in, axis=0)
    rep: dict = {}
    _, loop = master_loop(np.zeros((0, 2)), loop, TARGET_LUFS, ceiling_db=-2.0, report=rep)
    L = len(loop)
    write_ogg(out_path, loop, quality=3.0, tags={"LOOPSTART": "0", "LOOPLENGTH": str(L)})
    write_loop_sidecar(os.path.splitext(out_path)[0] + ".loop.json", SR, 0, L, BPM, 4,
                       extra={"loop_bars": BARS, "downbeat_offset_s": lead_in / SR})
    m = measure(loop)
    if stats is not None:
        stats["bus_lufs"] = dict(mx.bus_lufs)
        stats["limiter"] = rep
    if verbose:
        print(f"corrow_seawall: {m['seconds']:.2f}s  {m['integrated_lufs']:.2f} LUFS  TP {m['true_peak_dbtp']:.2f}"
              f" dBTP  limiter {rep}")
        print("  buses", {k: round(v, 1) for k, v in mx.bus_lufs.items()})
    return m


if __name__ == "__main__":
    render()
