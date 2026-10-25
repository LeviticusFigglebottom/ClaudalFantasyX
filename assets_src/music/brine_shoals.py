"""`brine_shoals`: the Brine Shoals, a route of wrecks and mud-flats (M3-AUD-11; act_outline Ch6 "Salt Edict", zone
`ch06/brine_shoals`): a 72.7 s seamless field loop.

Original composition for this project (SPEC §2, §9). The lute's tune, the ground of the bass and the harmony were
written for this route and are not derived from any existing tune. The brief: low tide over a graveyard of hulls,
mud that holds each step; ahead, smoke from the Order's raid on a Saltwright salvage camp. The cue walks toward the
fire without knowing yet what is burning: heavy, wary, salt-stained, not a battle.

C-sharp minor (Aeolian), 5/4 at 66 BPM grouped 3+2 (a bar is 4.55 s): the long step and the pull of the foot out of
the mud. In the smoke passage the D major chord (the flattened second, Neapolitan) sits over a C# pedal: the one
borrowed colour, a sourness on the air. 16 bars.

Ensemble (all synthesized; no samples):
* a salvage lute (plucked strings through a small wooden body): the tune, its long notes picked in tremolo, the
  way a Saltwright plays on a cold beach;
* a low string pad: the hulls, groaning in the mud;
* a muted fingered bass on the 3+2 (root, then the fifth on beat 4);
* a large frame drum: the steps (on 1 and 4) and the mud letting go (ghosts after each);
* a kettle gong struck and damped like a ship's plate, at bars 1 and 9; a large gong at the smoke (bar 11);
* embers: sparse crackle through the smoke passage, thinning into the wrap.

Form: 1-2 the flats (bass, steps, pad) | 3-6 the tune (A) | 7-10 the tune, higher (A') | 11-14 the smoke: D over C#,
the lute's tremolo highest, the crackle | 15-16 the flats again, the tune silent; G# minor leans back into bar 1.

Loop: LOOPSTART = 0 and LOOPLENGTH = the whole file.

Render:  python3 assets_src/music/brine_shoals.py   (or tools/audio/render_all.py --only brine_shoals)
"""
from __future__ import annotations

import importlib.util
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools", "audio"))

import numpy as np  # noqa: E402

from synth.drums import frame_drum  # noqa: E402
from synth.dsp import SR, bq_bandpass, bq_highpass, bq_lowpass, bq_peak, fft_convolve, filt, rng  # noqa: E402
from synth.electric import bass_note, string_pluck  # noqa: E402
from synth.gongs import kettle_gong, large_gong  # noqa: E402
from synth.looping import LoopMixer, master_loop, write_loop_sidecar  # noqa: E402
from synth.mixer import measure, write_ogg  # noqa: E402
from synth.pad import pad_chord, string_body  # noqa: E402
from synth.reverb import ModFDNReverb  # noqa: E402
from synth.score import n  # noqa: E402

_spec = importlib.util.spec_from_file_location("haluna_village", os.path.join(os.path.dirname(__file__),
                                                                               "haluna_village.py"))
HV = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(HV)

OUT = os.path.join(ROOT, "assets", "audio", "music", "brine_shoals.ogg")
SEED = 20261263
TARGET_LUFS = -16.0
BPM = 66.0
BEAT = 60.0 / BPM
BAR = 5 * BEAT
BARS = 16
LOOP_S = BARS * BAR
SIXTEENTH = BEAT / 4
## The file starts this long before bar 1's downbeat (0 = on it); see render_all's seam flux gate.
DOWNBEAT_OFFSET_S = 0.0

CHORDS = (["C#m", "C#m"] + ["C#m", "A", "F#m", "G#m"] + ["C#m", "A", "B", "C#m"] + ["D/C#", "C#m", "D/C#", "B"]
          + ["C#m", "G#m"])
BASS = {"C#m": [("C#2", 3), ("G#1", 2)], "A": [("A1", 3), ("E2", 2)], "F#m": [("F#1", 3), ("C#2", 2)],
        "G#m": [("G#1", 3), ("D#2", 2)], "B": [("B1", 3), ("F#1", 2)], "D/C#": [("C#2", 3), ("C#2", 2)]}
PAD = {"C#m": "C#3 G#3 E4", "A": "A2 E3 C#4", "F#m": "F#2 C#3 A3", "G#m": "G#2 D#3 B3", "B": "B2 F#3 D#4",
       "D/C#": "D3 F#3 A3"}

## the tune, (pitch, beats) per bar (5 beats a bar); None is a rest. Notes of 2 beats or more are picked in tremolo.
TUNE_A = [[("G#4", 1.5), ("E4", .5), ("F#4", 1), ("G#4", 2)],
          [("A4", 1), ("B4", .5), ("C#5", 1.5), ("B4", 1), ("A4", 1)],
          [("F#4", 3), ("E4", 1), ("C#4", 1)], [("D#4", 2), ("E4", 1), ("D#4", 2)]]
TUNE_A2 = [[("C#5", 1.5), ("B4", .5), ("G#4", 1), ("E4", 2)], [("E4", 1), ("F#4", .5), ("G#4", .5), ("A4", 1),
                                                              ("C#5", 2)],
           [("D#5", 3), ("C#5", 1), ("B4", 1)], [("C#5", 3), (None, 2)]]
SMOKE = [[("A4", 2), ("F#4", 1), ("D5", 2)], [("C#5", 4), (None, 1)], [("F#4", 1), ("A4", 1), ("D5", 1), ("E5", 2)],
         [("D#5", 3), ("B4", 2)]]


def t_of(bar: int, beat: float = 0.0) -> float:
    return (bar - 1) * BAR + beat * BEAT + DOWNBEAT_OFFSET_S


_VOICING: dict[float, float] = {}


def voicing(m: float, body: np.ndarray) -> float:
    """The luthier's evening: the small body's modes make some notes ring far louder than others (F#4 and C# by up to
    6 dB). Each pitch gets a gain that takes away most of its body boost, measured on a reference pluck (cached)."""
    if m not in _VOICING:
        x = string_pluck(m, BEAT, 0.5, seed=3, pick_pos=0.12, t60=2.6, max_f=6500.0, release=0.2)
        y = filt(fft_convolve(x, body), [bq_highpass(160, 0.7)])
        _VOICING[m] = float((np.sqrt(np.mean(x ** 2)) / np.sqrt(np.mean(y ** 2))) ** 0.8)
    return _VOICING[m]


def lute_note(mx: LoopMixer, body: np.ndarray, m: float, beats: float, t0: float, vel: float, seed: int,
              g: np.random.Generator) -> None:
    """One note of the tune: a single pluck under 2 beats, else a sixteenth tremolo that settles after its attack."""
    gain = voicing(m, body)
    if beats < 2:
        x = string_pluck(m, beats * BEAT, vel, seed=seed, pick_pos=0.12, t60=2.6, max_f=6500.0, release=0.2)
        mx.add("lute", fft_convolve(x, body)[: len(x) + 4000], t0 + float(g.normal(0, 0.006)), pan=0.15, gain=gain)
        return
    count = int(round(beats * 4))
    for k in range(count):
        v = vel * (1.0 if k == 0 else 0.62 + 0.10 * np.cos(np.pi * k / 2)) * g.uniform(0.9, 1.08)
        last = k == count - 1
        x = string_pluck(m, SIXTEENTH * (2.5 if last else 1.05), v, seed=seed + k, pick_pos=0.12 if k == 0 else 0.09,
                         t60=1.4, max_f=6000.0, release=0.12 if last else 0.04)
        mx.add("lute", fft_convolve(x, body)[: len(x) + 4000], t0 + k * SIXTEENTH + float(g.normal(0, 0.004)),
               pan=0.15 + (0.03 if k % 2 else 0.0), gain=gain)


def add_tune(mx: LoopMixer, body: np.ndarray, bars: list, start_bar: int, seed: int, vel: float) -> None:
    g = rng(seed)
    for i, bar in enumerate(bars):
        pos = 0.0
        for p, beats in bar:
            if p is not None:
                v = vel * g.uniform(0.94, 1.04) * (1.06 if pos == 0 else 1.0)
                lute_note(mx, body, n(p), beats, t_of(start_bar + i, pos), v, seed + 100 * i + int(pos * 4), g)
            pos += beats


def embers(mx: LoopMixer) -> None:
    """Crackle: short bursts of band-passed noise at random moments, densest in the smoke (bars 11-14)."""
    g = rng(SEED + 77)
    for bar in range(10, 17):
        density = {10: 3, 11: 9, 12: 12, 13: 12, 14: 10, 15: 5, 16: 2}[bar]
        for _ in range(density):
            t = t_of(bar, float(g.uniform(0, 5)))
            k = int(g.uniform(0.0015, 0.006) * SR)
            burst = g.standard_normal(k) * np.exp(-np.arange(k) / (k / 3.0))
            fc = float(g.uniform(1800, 5200))
            x = filt(burst, [bq_bandpass(fc, 1.4), bq_highpass(900, 0.7)]) * g.uniform(0.3, 1.0)
            mx.add("embers", x, t, pan=float(g.uniform(-0.6, 0.6)))


def build(mx: LoopMixer) -> None:
    g = rng(SEED)
    body = HV.lute_body(SEED + 5)
    for bar, ch in enumerate(CHORDS, start=1):
        smoke = 11 <= bar <= 14
        # the hulls
        x = pad_chord([n(p) for p in PAD[ch].split()], BAR * 0.92, 0.5, seed=SEED + 200 + bar, attack=1.4,
                      release=1.8, spread_cents=8.0 if not smoke else 13.0)
        mx.add("pad", x, t_of(bar) - 0.3)
        # the ground
        pos = 0.0
        for p, beats in BASS[ch]:
            v = (0.60 if pos == 0 else 0.46) * g.uniform(0.95, 1.04)
            x = bass_note(n(p), beats * BEAT * 0.9, v, seed=SEED + 300 + 10 * bar + int(pos), mute=0.35)
            mx.add("bass", x, t_of(bar, pos) + 0.006, pan=0.0)
            pos += beats
        # the steps, and the mud letting go
        for beat, stroke, v in ((0, "dum", 0.36), (1.5, "ghost", 0.11), (3, "dum", 0.27), (4.5, "ghost", 0.09)):
            if bar <= 2 and stroke == "ghost":
                continue
            x = frame_drum(stroke, v * g.uniform(0.9, 1.08), variant=4 * bar + int(beat), size=1.4, seed=SEED + 1)
            mx.add("drum", x, t_of(bar, beat) + float(g.normal(0, 0.006)), pan=-0.08)
    # the tune
    add_tune(mx, body, TUNE_A, 3, SEED + 600, 0.55)
    add_tune(mx, body, TUNE_A2, 7, SEED + 700, 0.57)
    add_tune(mx, body, SMOKE, 11, SEED + 800, 0.58)
    # the wrecks: a plate struck and damped; the large gong at the smoke
    for bar, v in ((1, 0.30), (9, 0.26)):
        mx.add("gong", kettle_gong(n("C#4"), v, seed=SEED + 400 + bar, t60=2.6, damp_at=1.2), t_of(bar, 0.0), pan=0.3)
    mx.add("gong", large_gong(n("C#2"), 0.30, seed=SEED + 500, t60=9.0), t_of(11), pan=-0.2)
    embers(mx)


# Bus gains were set from measured bus loudness (render(stats=...)["bus_lufs"]) for these levels relative to the
# lute (0 LU; its notes are evened by `voicing`, as F#4 rang 10 LU over the median momentary loudness):
# the pad -7, the bass -7, the steps -9, the gongs -12, the embers -15 (measured where they crackle).
def render(out_path: str = OUT, verbose: bool = True, stats: dict | None = None) -> dict:
    mx = LoopMixer(intro_s=0.0, loop_s=LOOP_S, preroll_s=10.0)
    mx.bus("lute", 4.8, send=0.28, process=lambda x: filt(x, [bq_highpass(160, 0.7), bq_peak(2600, 1.0, 1.0)]))
    mx.bus("pad", -0.6, send=0.30, process=lambda x: string_body(x, cutoff=1300.0))
    mx.bus("bass", -3.6, send=0.05, process=lambda x: filt(x, [bq_lowpass(800, 0.7)]))
    mx.bus("drum", -3.7, send=0.22, process=lambda x: filt(x, [bq_lowpass(3000, 0.7)]))
    mx.bus("gong", -14.1, send=0.5)
    mx.bus("embers", -7.3, send=0.25)
    build(mx)
    flats = ModFDNReverb(rt60=1.8, rt60_high=0.7, predelay=0.02, size=0.95, mod_depth=7.0, mod_rate=0.4,
                         early_level=0.15, lowcut=120.0, seed=SEED % 9973)
    _, loop = mx.render(reverb=flats, reverb_return_db=-4.0)
    rep: dict = {}
    _, loop = master_loop(np.zeros((0, 2)), loop, TARGET_LUFS, ceiling_db=-2.0, report=rep)
    L = len(loop)
    write_ogg(out_path, loop, quality=3.0, tags={"LOOPSTART": "0", "LOOPLENGTH": str(L)})
    write_loop_sidecar(os.path.splitext(out_path)[0] + ".loop.json", SR, 0, L, BPM, 5,
                       extra={"loop_bars": BARS, "meter": "5/4 (3+2)", "downbeat_offset_s": DOWNBEAT_OFFSET_S})
    m = measure(loop)
    if stats is not None:
        stats["bus_lufs"] = dict(mx.bus_lufs)
        stats["limiter"] = rep
    if verbose:
        print(f"brine_shoals: {m['seconds']:.2f}s  {m['integrated_lufs']:.2f} LUFS  TP {m['true_peak_dbtp']:.2f}"
              f" dBTP  limiter {rep}")
        print("  buses", {k: round(v, 1) for k, v in mx.bus_lufs.items()})
    return m


if __name__ == "__main__":
    render()
