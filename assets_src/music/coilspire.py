"""`coilspire`: Ch8, the Coilspire temple at Corrow before the storm (M3-AUD-19; act_outline Ch8): a 73 s seamless loop.

Original composition for this project (SPEC §2, §9). The climbing flute line, the 3+3+2 flue ostinato, the rising
bass and the hum below were written for this temple and are not derived from any existing tune.
Original-material check: the tune is one two-bar cell of our own (a leap up a fourth that falls back by step)
repeated a step higher each time, the way the beacon's fire climbs the spire; sequences like this are a common
technique, and no phrase here follows a melody we know. The style evoked is a tense processional over an ostinato;
nothing is quoted. Its only links to other cues are deliberate and our own: the key is F-sharp minor, the
dominant of Corrow's B minor (corrow_seawall.py), so the temple sounds like the seawall's question left open, and
the beacon is the same kettle gong on F#.

The brief: Coilspire is the spiral temple in the seawall city. Its trial is to open and close the copper flues so
the beacon's fire climbs the spire (Asha binds Virel, Fire, here), and Liss finds Wenna's scratched line-marks in
its stone. The storm is coming for the wall. Tense, ascending, salt and stone: everything in the cue climbs, and
nothing arrives.

F-sharp minor (Aeolian, with C-sharp major as the dominant: E# is its one borrowed note; the B section brightens
once to B major, D#), 4/4 at 92 BPM (a bar is 2.609 s), 28 bars.

Ensemble (all synthesized; no samples):
* breath flute, high and hard-blown (C#5-E6): the wind drawn up the flues; the tune;
* the flues: damped copper bars (a hard, hand-damped metallophone) in a running 3+3+2 eighth-note ostinato on the
  chord tones, climbing within each bar;
* the stone: a fingered bass on the rising roots, a big drum and frame drums on the 3+3+2 accents;
* a high string pad, tight and close-voiced (the tension under the climb);
* women and men humming the rising bass in long notes in B (the Order hums; only Cantors sing, bible §4);
* the salt: a surf wash against the spire's foot every two bars, low and wide;
* the beacon: a kettle gong on F# at each section, a large gong at bars 1 and 13.

Form (bars): 1-4 the flues (ostinato, drums, surf) | 5-12 A, the cell climbing from C#5 to G#5 | 13-20 B, higher,
the hum enters, the one bright B major | 21-24 the climb to E6, the fire at the top | 25-28 the flute's last high
notes falling away over the ostinato; C-sharp major (bars 27-28) leads back to bar 1's F-sharp minor.

Loop: LOOPSTART = 0 and LOOPLENGTH = the whole file. The file starts a sixteenth before bar 1's downbeat (the
sidecar's `downbeat_offset_s`), so the wrap seam falls in a quiet sixteenth.

Render:  python3 assets_src/music/coilspire.py   (or tools/audio/render_all.py --only coilspire)
"""
from __future__ import annotations

import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools", "audio"))

import numpy as np  # noqa: E402

from synth.drums import big_drum, frame_drum  # noqa: E402
from synth.dsp import SR, bq_bandpass, bq_highpass, bq_lowpass, bq_peak, filt, rng  # noqa: E402
from synth.electric import bass_note  # noqa: E402
from synth.gongs import kettle_gong, large_gong  # noqa: E402
from synth.looping import LoopMixer, master_loop, write_loop_sidecar  # noqa: E402
from synth.metallophone import metallophone_note  # noqa: E402
from synth.mixer import measure, write_ogg  # noqa: E402
from synth.pad import pad_chord, string_body  # noqa: E402
from synth.reverb import ModFDNReverb  # noqa: E402
from synth.score import n  # noqa: E402
from synth.voice import hum_ensemble  # noqa: E402
from synth.winds import breath_flute  # noqa: E402

OUT = os.path.join(ROOT, "assets", "audio", "music", "coilspire.ogg")
SEED = 20261242
TARGET_LUFS = -16.0
BPM = 92.0
BEAT = 60.0 / BPM
BAR = 4 * BEAT
BARS = 28
LOOP_S = BARS * BAR
## breath_flute's tone starts after its breath (0.05-0.08 s): notes are placed this much early.
FLUTE_PRE = 0.065
## the file starts this many beats before bar 1's downbeat (see render())
LEAD_IN_BEATS = 0.25

CHORDS = (["F#m", "F#m", "D", "C#"]
          + ["F#m", "D", "E", "C#m", "A", "Bm", "C#", "C#"]
          + ["F#m", "E", "A", "B", "Bm", "C#", "D", "C#"]
          + ["F#m", "D", "E", "C#"]
          + ["F#m", "D", "C#", "C#"])
SECTION = ["I"] * 4 + ["A"] * 8 + ["B"] * 8 + ["C"] * 4 + ["T"] * 4
ROOTS = {"F#m": "F#1", "D": "D2", "E": "E2", "C#m": "C#2", "C#": "C#2", "A": "A1", "Bm": "B1", "B": "B1"}
## the flues' ostinato: chord tones climbing within the bar, 3+3+2 eighths
TONES = {"F#m": ["F#4", "A4", "C#5", "F#5"], "D": ["D4", "F#4", "A4", "D5"], "E": ["E4", "G#4", "B4", "E5"],
         "C#m": ["C#4", "E4", "G#4", "C#5"], "C#": ["C#4", "E#4", "G#4", "C#5"], "A": ["A3", "C#4", "E4", "A4"],
         "Bm": ["B3", "D4", "F#4", "B4"], "B": ["B3", "D#4", "F#4", "B4"]}
RUN = [0, 1, 2, 1, 2, 3, 2, 3]       # indices into TONES per eighth: each group of the 3+3+2 starts a step higher
ACCENTS = (0, 3, 6)                  # the 3+3+2 group starts (eighths)
## the pad: close, high voicings
PAD = {"F#m": "A3 C#4 F#4", "D": "A3 D4 F#4", "E": "G#3 B3 E4", "C#m": "G#3 C#4 E4", "C#": "G#3 C#4 E#4",
       "A": "A3 C#4 E4", "Bm": "B3 D4 F#4", "B": "B3 D#4 F#4"}

## the tune: one list per bar of (pitch | None, beats); the cell climbs a step each time
TUNE_A = [
    [("C#5", 2), ("F#5", 1), ("E5", 1)],
    [("F#5", 1.5), ("E5", .5), ("D5", 2)],
    [("D5", 2), ("G#5", 1), ("F#5", 1)],
    [("G#5", 1.5), ("F#5", .5), ("E5", 2)],
    [("E5", 2), ("A5", 1), ("G#5", 1)],
    [("A5", 1.5), ("G#5", .5), ("F#5", 2)],
    [("G#5", 1), ("F#5", 1), ("E#5", 1), ("G#5", 1)],
    [("G#5", 3), (None, 1)],
]
TUNE_B = [
    [("A5", 2), ("C#6", 2)],
    [("B5", 3), ("G#5", 1)],
    [("C#6", 2), ("E6", 2)],
    [("D#6", 3), ("C#6", 1)],
    [("D6", 2), ("C#6", 1), ("B5", 1)],
    [("C#6", 2), ("G#5", 2)],
    [("A5", 2), ("F#5", 2)],
    [("G#5", 2), ("E#5", 1), (None, 1)],
]
TUNE_C = [
    [("F#5", 1), ("G#5", 1), ("A5", 1), ("B5", 1)],
    [("C#6", 1), ("D6", 1), ("E6", 2)],
    [("E6", 2), ("D6", 1), ("B5", 1)],
    [("C#6", 4)],
]
TUNE_T = [
    [("A5", 3), ("G#5", 1)],
    [("F#5", 3), (None, 1)],
]
## the hum in B: the rising roots, an octave and more up, one a bar (men), a tenth above (women)
MEN = ["F#2", "G#2", "A2", "B2", "B2", "C#3", "D3", "C#3"]
WOMEN = ["A3", "B3", "C#4", "D#4", "D4", "E#4", "F#4", "E#4"]


def t_of(bar: int, beat: float = 0.0) -> float:
    return (bar - 1) * BAR + beat * BEAT


def add_tune(mx: LoopMixer, bars: list, start_bar: int, seed: int, vel: float, pan: float = -0.1) -> None:
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
            v = vel * g.uniform(0.94, 1.04) * (1.05 if beats >= 2 else 1.0)
            x = breath_flute(n(p), d * 0.95 + 0.03, v, seed=seed + int(round(pos * 1000)), breath=0.42,
                             scoop_cents=35.0 if first else 10.0, vib_cents=12.0 if beats >= 2 else 3.0,
                             vib_rate=5.0, swell=0.35 if beats >= 3 else 0.1 if beats >= 2 else 0.0,
                             attack=0.06 if first else 0.035, release=0.3, beta=0.62)
            mx.add("flute", x, pos - FLUTE_PRE + float(g.normal(0, 0.004)), pan=pan)
            pos += d
            first = False


def surf(seconds: float, seed: int) -> np.ndarray:
    """The salt: one wash of surf at the spire's foot (band-limited noise, a slow rise and a long fall)."""
    g = rng(seed)
    N = int(seconds * SR)
    t = np.arange(N) / SR
    env = (1 - np.exp(-t / 0.6)) * np.exp(-t / (seconds * 0.35))
    env /= env.max()
    chans = []
    for _ in range(2):
        x = filt(g.standard_normal(N), [bq_bandpass(700, 0.5), bq_lowpass(2400, 0.7), bq_highpass(160, 0.7)])
        chans.append(x * env / (np.abs(x).max() + 1e-9))
    out = np.stack(chans, axis=1)
    k = int(0.3 * SR)
    out[-k:] *= np.linspace(1, 0, k)[:, None] ** 2
    return out


def hum_part(pitches: list, voices: int, seed: int, register: str) -> np.ndarray:
    line = [(n(p), BAR) for p in pitches]
    x = hum_ensemble(line, voices=voices, seed=seed, register=register, spread=0.9)
    env = np.ones(len(x))
    k = int(2.5 * SR)
    env[:k] = np.linspace(0, 1, k) ** 2
    s = int((len(pitches) - 0.6) * BAR * SR)
    env[s:] = np.exp(-np.arange(len(env) - s) / SR / 0.9)
    return x * env[:, None]


def build(mx: LoopMixer) -> None:
    g = rng(SEED)
    for bar, (ch, sec) in enumerate(zip(CHORDS, SECTION), start=1):
        root = n(ROOTS[ch])
        # the stone: the bass on 1 and on the 3+3+2 accents
        for e in ACCENTS:
            v = (0.60 if e == 0 else 0.44) * g.uniform(0.95, 1.04)
            dur = (3 if e < 6 else 2) * BEAT / 2 * 0.9
            x = bass_note(root + (12 if e == 6 and sec in ("B", "C") else 0), dur, v,
                          seed=SEED + 30000 + 10 * bar + e, mute=0.25)
            mx.add("bass", x, t_of(bar, e / 2) + 0.004)
        # the flues: damped copper in eighths (only the accents in the tail's last bar, to thin the wrap)
        tones = TONES[ch]
        for e, idx in enumerate(RUN):
            if sec == "T" and bar == 28 and e not in ACCENTS:
                continue
            v = (0.42 if e in ACCENTS else 0.28) * g.uniform(0.9, 1.06)
            x = metallophone_note(n(tones[idx]), v, seed=SEED + 20000 + 10 * bar + e, decay=1.4, hardness=0.55,
                                  ombak_hz=4.0, damp_at=BEAT / 2 * 0.85)
            mx.add("flues", x, t_of(bar, e / 2) + float(g.normal(0, 0.003)), pan=0.3 if e % 2 else 0.12)
        # drums: the big drum on 1 (and the 3+3+2's third group in B and C), frame drums on the accents
        bd = 0.42 if bar % 4 == 1 else 0.32
        mx.add("drums", big_drum(bd * g.uniform(0.95, 1.03), variant=bar, seed=SEED + 2), t_of(bar))
        if sec in ("B", "C"):
            mx.add("drums", big_drum(0.24, variant=bar + 1, seed=SEED + 2), t_of(bar, 3.0))
        for e in range(8):
            if e in ACCENTS:
                stroke, v = ("dum", 0.30) if e == 0 else ("tek", 0.26)
            elif sec in ("I", "T") or e % 2 == 0:
                continue
            else:
                stroke, v = "ghost", 0.13
            x = frame_drum(stroke, v * g.uniform(0.9, 1.08), variant=bar * 8 + e, seed=SEED + 1)
            mx.add("drums", x, t_of(bar, e / 2) + float(g.normal(0, 0.004)), pan=-0.15)
        # the pad (not in the intro)
        if sec != "I":
            x = pad_chord([n(p) for p in PAD[ch].split()], BAR * 0.95, 0.5, seed=SEED + 200 + bar, voices=4,
                          attack=0.9, release=1.0, width=0.8)
            mx.add("pad", x, t_of(bar) - 0.1)
        # the beacon
        if sec != SECTION[bar - 2] or bar == 1:
            mx.add("gong", kettle_gong(n("F#3"), 0.32, seed=SEED + 400 + bar, t60=3.2), t_of(bar), pan=0.35)
    for bar in (1, 13):
        mx.add("gong", large_gong(n("F#1"), 0.30, seed=SEED + 500 + bar, t60=8.0), t_of(bar), pan=-0.15)
    # the salt: a wash every two bars, alternating sides
    for k, bar in enumerate(range(1, BARS + 1, 2)):
        x = surf(2 * BAR, SEED + 800 + bar) * g.uniform(0.75, 1.0)
        pan = np.array([1.0, 0.55]) if k % 2 else np.array([0.55, 1.0])
        mx.add("surf", x * pan[None, :], t_of(bar, 0.5))
    # the tune
    add_tune(mx, TUNE_A, 5, SEED + 600, 0.50)
    add_tune(mx, TUNE_B, 13, SEED + 650, 0.54)
    add_tune(mx, TUNE_C, 21, SEED + 680, 0.58)
    add_tune(mx, TUNE_T, 25, SEED + 690, 0.46)
    # the hum, under B
    mx.add("hum", hum_part(MEN, 10, SEED + 11, "low"), t_of(13) - 0.15)
    mx.add("hum", hum_part(WOMEN, 8, SEED + 12, "high"), t_of(13) - 0.1)


# Bus gains were set from measured bus loudness (render(stats=...)["bus_lufs"]) for these levels relative to the
# flute (0 LU, measured over the whole loop; it rests in the first four bars): the flues -7, bass -8, drums -7,
# pad -12, the hum -9 (it sounds only in B), gongs -13, surf -17.
def render(out_path: str = OUT, verbose: bool = True, stats: dict | None = None) -> dict:
    mx = LoopMixer(intro_s=0.0, loop_s=LOOP_S, preroll_s=10.0)
    mx.bus("flute", 0.0, send=0.30, process=lambda x: filt(x, [bq_highpass(220, 0.7), bq_peak(2200, 1.0, 1.0),
                                                                 bq_lowpass(7000, 0.7)]))
    mx.bus("flues", 2.4, send=0.25, process=lambda x: filt(x, [bq_highpass(200, 0.7), bq_lowpass(6000, 0.7)]))
    mx.bus("bass", -1.0, send=0.05, process=lambda x: filt(x, [bq_lowpass(900, 0.7)]))
    mx.bus("drums", 1.0, send=0.22, process=lambda x: filt(x, [bq_lowpass(4000, 0.7)]))
    mx.bus("pad", -1.6, send=0.40, process=lambda x: string_body(x, cutoff=2600.0))
    mx.bus("hum", -9.6, send=0.65)
    mx.bus("gong", -9.3, send=0.45)
    mx.bus("surf", -23.4, send=0.30)
    build(mx)
    spire = ModFDNReverb(rt60=2.6, rt60_high=1.0, predelay=0.03, size=1.1, mod_depth=8.0, mod_rate=0.5,
                         early_level=0.35, lowcut=110.0, seed=SEED % 9973)
    _, loop = mx.render(reverb=spire, reverb_return_db=-3.0)
    # The loop is periodic, so it may start anywhere: a sixteenth before bar 1's downbeat, so the wrap seam falls in
    # a quiet sixteenth instead of on the downbeat's drums, gongs and bass at once.
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
        print(f"coilspire: {m['seconds']:.2f}s  {m['integrated_lufs']:.2f} LUFS  TP {m['true_peak_dbtp']:.2f} dBTP"
              f"  limiter {rep}")
        print("  buses", {k: round(v, 1) for k, v in mx.bus_lufs.items()})
    return m


if __name__ == "__main__":
    render(sys.argv[1] if len(sys.argv) > 1 else OUT)
