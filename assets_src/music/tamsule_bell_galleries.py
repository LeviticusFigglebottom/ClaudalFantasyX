"""`tamsule_bell_galleries`: Ch7, the galleries inside the great Tamsule Bell (M3-AUD-19; act_outline Ch7): an 80 s
seamless loop.

Original composition for this project (SPEC §2, §9). The flute's song, the bronze drone and the gallery echo below
were written for this place and are not derived from any existing tune. Original-material check: the A section's
line (E-D-C falling to A, then G-C-E rising to D) and the B section's major answer (C#-E, F#-A) were written for this
cue; they share no phrase with the Tidecup's song or the Tamsule town tune (tidecup_match.py SONG_A, tamsule.py
TUNE_A), and no melody we know. The style evoked is a slow, spacious lament over a drone; nothing is quoted. Its only
links are deliberate and our own: the Bell itself is the same instrument as in the Tidecup and the town
(synth.bells.tower_bell, prime A2, dark 0.35), and the drone is made of that bell's own partials.

The brief: the galleries ring the Reefball arena inside the Tamsule Bell; this is the cue for walking them, not for
the match (that is tidecup_match). Toma, who played here for Haluna as a boy, watches from the galleries beside
Asha; Liss notes aloud that the Bell is glimmer-tech, and nobody answers; under the Bell are Oruvel's empty
moorings. Resonant, hollow, bronze: the player is inside an instrument.

So the harmony comes from the Bell. A struck bell has a minor-third partial (the tierce, 1.2 x the prime) and, an
octave and a third up, a major one (the deciem, 2.5 x): the Bell holds both C and C# at once. The drone is the
Bell's hum, prime, tierce, quint and nominal, sustained; the A sections are A minor (the tierce leads); in B the
tierce sinks and the deciem rises, and the music turns to A major for eight bars; then the tierce comes back.

A minor / A major (the third is the Bell's), 3/4 at 54 BPM (a bar is 3.333 s), 24 bars. Apart from the Tidecup (A
minor, 4/4 at 112, drums) and the town (A dorian, 7/8, a hammered dulcimer): no drums at all, the slowest pulse in
Ch7, and the third that changes.

Ensemble (all synthesized; no samples):
* the Bell's drone: its partials as sustained doublets that beat slowly (every frequency is snapped to a whole
  number of cycles per loop, so the drone is exactly periodic), breathing on a 13.3 s cycle;
* the Bell: one padded strike at bars 1 and 13, softly at 21;
* breath flute, middle register (G#4-A5): the song;
* the gallery: every long flute note comes back a beat later from the other side, darker and quieter, the way a
  sound runs round a curved wall;
* glimmer glass: soft bars doubling the song's long notes an octave up in B and A';
* a low plucked string on each bar's root, open and long.

Form (bars): 1-4 the Bell (the strike, the drone, glass glints) | 5-12 A, A minor | 13-20 B, A major (the deciem) |
21-24 A', A minor, the song's last phrase falling to B over E, which leads back to bar 1's A.

Loop: LOOPSTART = 0 and LOOPLENGTH = the whole file. The file starts a sixteenth before bar 1's downbeat (the
sidecar's `downbeat_offset_s`), so the wrap seam falls in a quiet sixteenth, not on the Bell's strike.

Render:  python3 assets_src/music/tamsule_bell_galleries.py   (or tools/audio/render_all.py --only bell_galleries)
"""
from __future__ import annotations

import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools", "audio"))

import numpy as np  # noqa: E402

from synth.bells import tower_bell  # noqa: E402
from synth.dsp import SR, bq_highpass, bq_lowpass, bq_peak, filt, midi_to_hz, rng  # noqa: E402
from synth.electric import string_pluck  # noqa: E402
from synth.looping import LoopMixer, master_loop, write_loop_sidecar  # noqa: E402
from synth.metallophone import metallophone_note  # noqa: E402
from synth.mixer import measure, write_ogg  # noqa: E402
from synth.reverb import ModFDNReverb  # noqa: E402
from synth.score import n  # noqa: E402
from synth.winds import breath_flute  # noqa: E402

OUT = os.path.join(ROOT, "assets", "audio", "music", "tamsule_bell_galleries.ogg")
SEED = 20261243
TARGET_LUFS = -16.0
BPM = 54.0
BEAT = 60.0 / BPM
BAR = 3 * BEAT
BARS = 24
LOOP_S = BARS * BAR
BELL_PRIME = "A2"             # the Tamsule Bell (tidecup_match.py, tamsule.py)
## breath_flute's tone starts after its breath (0.05-0.08 s): notes are placed this much early.
FLUTE_PRE = 0.065
## the file starts this many beats before bar 1's downbeat (see render())
LEAD_IN_BEATS = 0.25
## the gallery: a long note comes back this many beats later, from the other side
ECHO_BEATS = 1.0

CHORDS = (["A5", "A5", "A5", "A5"]
          + ["A5", "F", "C", "G", "A5", "F", "Dm", "E"]
          + ["A", "D", "F#m", "E", "A", "D", "Bm", "E"]
          + ["Am", "F", "Dm", "E"])
SECTION = ["I"] * 4 + ["A"] * 8 + ["B"] * 8 + ["A2"] * 4
ROOTS = {"A5": "A1", "Am": "A1", "A": "A1", "F": "F1", "C": "C2", "G": "G1", "Dm": "D2", "D": "D2", "E": "E1",
         "F#m": "F#1", "Bm": "B1"}
## the drone: the Bell's partials (name, ratio to the prime, level, doublet split in Hz)
DRONE = [("hum", 0.5, 1.0, 0.10), ("prime", 1.0, 0.55, 0.15), ("tierce", 1.2, 0.50, 0.2), ("quint", 1.5, 0.22, 0.0),
         ("nominal", 2.0, 0.30, 0.25), ("deciem", 2.5, 0.40, 0.3)]
GLINT = ["A5", "C6", "E6", "A6", "B5", "E5"]

## the song: one list per bar of (pitch | None, beats)
TUNE_A = [
    [("E5", 2), ("D5", 1)],
    [("C5", 2), ("A4", 1)],
    [("G4", 1), ("C5", 1), ("E5", 1)],
    [("D5", 2), (None, 1)],
    [("E5", 1), ("A5", 1.5), ("G5", .5)],
    [("F5", 1), ("E5", 1), ("C5", 1)],
    [("D5", 1.5), ("E5", .5), ("F5", 1)],
    [("E5", 2), (None, 1)],
]
TUNE_B = [
    [("C#5", 2), ("E5", 1)],
    [("F#5", 2), ("A5", 1)],
    [("G#5", 1), ("F#5", 1), ("C#5", 1)],
    [("B4", 2), (None, 1)],
    [("C#5", 1), ("E5", 1), ("A5", 1)],
    [("A5", 1.5), ("F#5", .5), ("D5", 1)],
    [("F#5", 2), ("D5", 1)],
    [("E5", 2), (None, 1)],
]
TUNE_A2 = [
    [("C5", 2), ("B4", 1)],
    [("A4", 3)],
    [("D5", 2), ("C5", 1)],
    [("B4", 2), (None, 1)],
]


def t_of(bar: int, beat: float = 0.0) -> float:
    return (bar - 1) * BAR + beat * BEAT


def add_tune(mx: LoopMixer, bars: list, start_bar: int, seed: int, vel: float, glass: bool = False,
             pan: float = -0.15) -> None:
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
            v = vel * g.uniform(0.94, 1.04) * (1.04 if beats >= 2 else 1.0)
            x = breath_flute(n(p), d * 0.96 + 0.03, v, seed=seed + int(round(pos * 1000)), breath=0.45,
                             scoop_cents=40.0 if first else 12.0, vib_cents=10.0 if beats >= 2 else 4.0,
                             vib_rate=4.4, swell=0.3 if beats >= 2 else 0.0, attack=0.09 if first else 0.05,
                             release=0.5, beta=0.52)
            ts = pos - FLUTE_PRE + float(g.normal(0, 0.005))
            mx.add("flute", x, ts, pan=pan)
            if beats >= 2:      # the gallery returns it, a beat later, from the other side
                mx.add("echo", x, ts + ECHO_BEATS * BEAT, pan=-pan * 4)
            if glass and beats >= 2:
                y = metallophone_note(n(p) + 12, 0.22 * g.uniform(0.9, 1.05), seed=seed + 7 + int(pos * 100),
                                      decay=4.0, hardness=0.25, ombak_hz=2.2)
                mx.add("glass", y, pos + 0.01, pan=0.4)
            pos += d
            first = False


def drone(L: int, seed: int) -> np.ndarray:
    """The Bell's partials, sustained and exactly periodic over the loop (L samples). In B (bars 13-20) the tierce
    (the minor third) sinks and the deciem (the major third) rises."""
    g = rng(seed)
    Ls = L / SR
    t = np.arange(L) / SR
    f1 = midi_to_hz(n(BELL_PRIME))
    b0, b1, fade = t_of(13), t_of(21), 3.0

    def ramp(x):            # 0 before b0, 1 inside B, back to 0 after b1, raised-cosine edges
        up = np.clip((x - b0 + fade / 2) / fade, 0, 1)
        down = np.clip((x - b1 + fade / 2) / fade, 0, 1)
        return 0.5 - 0.5 * np.cos(np.pi * (up - down))

    major = ramp(t)
    breathe = 0.82 + 0.18 * np.cos(2 * np.pi * 6 * t / Ls)          # six breaths a loop
    out = np.zeros((L, 2))
    for name, r, a, split in DRONE:
        f = round(f1 * r * Ls) / Ls
        s = round(split * Ls) / Ls
        lvl = a * (1 - 0.85 * major if name == "tierce" else 0.15 + 0.85 * major if name == "deciem" else 1.0)
        lfo = 1.0 + 0.12 * np.cos(2 * np.pi * (round(Ls / float(g.uniform(9, 17)))) * t / Ls + g.uniform(0, 6.28))
        for ch in range(2):
            ph0, ph1 = g.uniform(0, 2 * np.pi, 2)
            mode = np.sin(2 * np.pi * f * t + ph0) + (np.sin(2 * np.pi * (f + s) * t + ph1) if s > 0 else 0)
            out[:, ch] += lvl * lfo * mode * (0.5 if s > 0 else 1.0)
    return out * breathe[:, None] / np.abs(out).max()


def build(mx: LoopMixer) -> None:
    g = rng(SEED)
    mx.add("drone", drone(mx.L, SEED + 3), 0.0)
    for bar, (ch, sec) in enumerate(zip(CHORDS, SECTION), start=1):
        # the low string on each root (and its fifth on beat 2, except in the intro)
        r = n(ROOTS[ch])
        x = string_pluck(r + 12, 2.6 * BEAT, 0.5 * g.uniform(0.94, 1.04), seed=SEED + 3000 + bar, pick_pos=0.15,
                         t60=5.0, B=4e-5, max_f=3000.0, release=0.4)
        mx.add("low", x, t_of(bar) + 0.01, pan=0.1)
        if sec != "I":
            x = string_pluck(r + 19, 1.6 * BEAT, 0.3, seed=SEED + 3100 + bar, pick_pos=0.15, t60=4.0, B=4e-5,
                             max_f=3000.0, release=0.4)
            mx.add("low", x, t_of(bar, 1) + 0.01, pan=0.2)
        # glimmer glass: a glint or two where the song rests
        glints = 2 if sec == "I" else (1 if bar in (8, 12, 16, 20, 24) else 0)
        for j in range(glints):
            p = GLINT[int(g.integers(0, 4 if ch in ("A5", "Am", "F", "C", "Dm") else 6))]
            if sec == "B" and p == "C6":
                p = "C#6"
            x = metallophone_note(n(p), 0.18 * g.uniform(0.85, 1.05), seed=SEED + 5000 + 10 * bar + j, decay=4.5,
                                  hardness=0.25, ombak_hz=2.2)
            mx.add("glass", x, t_of(bar, float(g.uniform(0.5, 2.6))), pan=float(g.uniform(-0.7, 0.7)))
    # the Bell
    for bar, v in ((1, 0.75), (13, 0.6), (21, 0.45)):
        mx.add("bell", tower_bell(n(BELL_PRIME), v, seed=SEED + 400 + bar, t60=9.0, dark=0.35), t_of(bar), pan=-0.05)
    # the song
    add_tune(mx, TUNE_A, 5, SEED + 600, 0.50)
    add_tune(mx, TUNE_B, 13, SEED + 650, 0.53, glass=True)
    add_tune(mx, TUNE_A2, 21, SEED + 680, 0.48, glass=True)


# Bus gains were set from measured bus loudness (render(stats=...)["bus_lufs"]) for these levels relative to the
# flute (0 LU, measured over the whole loop; it rests in the first four bars): the drone -8, the Bell -9 (three
# strikes a loop), the gallery echo -10, the low string -10, glass -13.
def render(out_path: str = OUT, verbose: bool = True, stats: dict | None = None) -> dict:
    mx = LoopMixer(intro_s=0.0, loop_s=LOOP_S, preroll_s=12.0)
    mx.bus("flute", 0.0, send=0.35, process=lambda x: filt(x, [bq_highpass(180, 0.7), bq_peak(1600, 1.0, 1.0),
                                                                 bq_lowpass(6500, 0.7)]))
    mx.bus("echo", -8.9, send=0.80, process=lambda x: filt(x, [bq_highpass(300, 0.7), bq_lowpass(2200, 0.7)]))
    mx.bus("drone", -20.0, send=0.35, process=lambda x: filt(x, [bq_lowpass(1500, 0.7)]))
    mx.bus("bell", -10.5, send=0.50)
    mx.bus("low", -1.9, send=0.35, process=lambda x: filt(x, [bq_lowpass(1600, 0.7)]))
    mx.bus("glass", 1.4, send=0.60)
    build(mx)
    bronze = ModFDNReverb(rt60=4.5, rt60_high=1.6, predelay=0.05, size=1.4, mod_depth=10.0, mod_rate=0.35,
                          early_level=0.3, lowcut=90.0, seed=SEED % 9973)
    _, loop = mx.render(reverb=bronze, reverb_return_db=-2.0)
    # The loop is periodic, so it may start anywhere: a sixteenth before bar 1's downbeat, so the wrap seam falls in
    # a quiet sixteenth instead of on the Bell's strike.
    lead_in = int(round(LEAD_IN_BEATS * BEAT * SR))
    loop = np.roll(loop, lead_in, axis=0)
    rep: dict = {}
    _, loop = master_loop(np.zeros((0, 2)), loop, TARGET_LUFS, ceiling_db=-2.0, report=rep)
    L = len(loop)
    write_ogg(out_path, loop, quality=3.0, tags={"LOOPSTART": "0", "LOOPLENGTH": str(L)})
    write_loop_sidecar(os.path.splitext(out_path)[0] + ".loop.json", SR, 0, L, BPM, 3,
                       extra={"loop_bars": BARS, "downbeat_offset_s": lead_in / SR})
    m = measure(loop)
    if stats is not None:
        stats["bus_lufs"] = dict(mx.bus_lufs)
        stats["limiter"] = rep
    if verbose:
        print(f"tamsule_bell_galleries: {m['seconds']:.2f}s  {m['integrated_lufs']:.2f} LUFS"
              f"  TP {m['true_peak_dbtp']:.2f} dBTP  limiter {rep}")
        print("  buses", {k: round(v, 1) for k, v in mx.bus_lufs.items()})
    return m


if __name__ == "__main__":
    render(sys.argv[1] if len(sys.argv) > 1 else OUT)
