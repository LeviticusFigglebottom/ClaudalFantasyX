"""`peace_wedding`: Ch14 "The Peace Wedding", the ceremony in the Lacquer Court at dusk (M3-AUD-805; act_outline Ch14):
a 61 s seamless loop. An Act II sketch, for the human to judge the direction.

Original composition for this project (SPEC §2, §9). Original-material check: the dance tune (B-D-G rising, F#-E-D,
E-C-A, G-F# ...), its dark answer over E-flat and C minor, and the zither's bass-chord-chord pattern were written for
this cue. The only borrowed line is our own: High Warden Sefir's motif (sefir_theme.py MOTIF, G C D E D C#), hummed
here in G (D G A B A G#) while he officiates. The style evoked is a slow, formal court dance in triple time with
plucked strings and bronze; no phrase is quoted from any existing music.

The brief: a gorgeous ceremony at dusk on still water; Liss's brother Tobin marries Merel Dask, a Warden's daughter,
for his people's peace. Sefir officiates. The Conclave springs the trap. It must be a real dance, beautiful enough
that the player wants the peace too, and a trap: the ground is giving way under it the whole time.

So: G major, 3/4 at 88 BPM (a bar is 2.05 s), 30 bars. The A section is honestly lovely. Then in B the dance turns
to E-flat major and C minor (the flattened sixth and the minor fourth: the colours of decline), and under it a
damped low gong begins to step every two beats, against the dance's three: something keeping a different time
in the same room. The congregation hums Sefir's motif, and its last note, G#, is held over C until it turns into Ab,
the C minor chord's own note: his wrong note becomes the ground. When the tune comes back (A'), its third bar has
caught the minor (E-flat, A-flat), and it ends on the dominant, never on G, which is the next loop's first bar.

Ensemble (all synthesized; no samples):
* the court zither: plucked strings, bass on 1 and the chord on 2 and 3 (the dance itself);
* breath flute: the tune;
* gilded bars: paired metallophone bars doubling the tune's downbeats an octave up (A sections);
* a frame drum, soft: a low stroke on 1 and a rim on 3;
* a warm string pad under the chords;
* the Order's hum (bars 17-24): men on the roots, then the motif;
* the Stillguard's step (bars 17-24): a hand-damped low kettle gong every two beats.

Form (bars): 1-2 the dance alone (G) | 3-10 A (G D Am Em C G Am D) | 11-16 A, its first half and a close on G |
17-20 B (Eb Cm Ab Bb7), the gong begins | 21-24 the motif hummed (G Em C Cm) | 25-30 A' (G D Cm Em Am-D7 D7), which
leads back to bar 1's G.

Loop: LOOPSTART = 0 and LOOPLENGTH = the whole file. The file starts a sixteenth before bar 1's downbeat (the
sidecar's `downbeat_offset_s`), so the wrap seam falls before the dance's downbeat, not on it.

Render:  python3 assets_src/music/peace_wedding.py   (or tools/audio/render_all.py --only peace_wedding)
"""
from __future__ import annotations

import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools", "audio"))

import numpy as np  # noqa: E402

from synth.drums import frame_drum  # noqa: E402
from synth.dsp import SR, bq_highpass, bq_lowpass, bq_peak, filt, rng  # noqa: E402
from synth.electric import string_pluck  # noqa: E402
from synth.gongs import kettle_gong  # noqa: E402
from synth.looping import LoopMixer, master_loop, write_loop_sidecar  # noqa: E402
from synth.metallophone import metallophone_note  # noqa: E402
from synth.mixer import measure, write_ogg  # noqa: E402
from synth.pad import pad_chord, string_body  # noqa: E402
from synth.reverb import ModFDNReverb  # noqa: E402
from synth.score import n  # noqa: E402
from synth.voice import hum_ensemble  # noqa: E402
from synth.winds import breath_flute  # noqa: E402

OUT = os.path.join(ROOT, "assets", "audio", "music", "peace_wedding.ogg")
SEED = 20261413
TARGET_LUFS = -16.0
BPM = 88.0
BEAT = 60.0 / BPM
BAR = 3 * BEAT
BARS = 30
LOOP_S = BARS * BAR
## breath_flute's tone starts after its breath (0.05-0.08 s): notes are placed this much early.
FLUTE_PRE = 0.065
## the file starts this many beats before bar 1's downbeat (see render())
LEAD_IN_BEATS = 0.25
QUALITY = 3.0  # mix.md §5's sparse-cue quality

A_CHORDS = ["G", "D", "Am", "Em", "C", "G", "Am", "D"]
CHORDS = (["G", "G"] + A_CHORDS + A_CHORDS[:4] + ["Am", "G"] + ["Eb", "Cm", "Ab", "Bb7"] + ["G", "Em", "C", "Cm"]
          + ["G", "D", "Cm", "Em", "Am", "D7"])
SECTION = ["I"] * 2 + ["A"] * 14 + ["B"] * 8 + ["A2"] * 6
## zither voicings: (bass, chord)
ZITHER = {"G": ("G2", "B3 D4 G4"), "D": ("D2", "A3 D4 F#4"), "Am": ("A2", "A3 C4 E4"), "Em": ("E2", "G3 B3 E4"),
          "C": ("C3", "G3 C4 E4"), "Eb": ("Eb2", "G3 Bb3 Eb4"), "Cm": ("C3", "G3 C4 Eb4"), "Ab": ("Ab2", "Ab3 C4 Eb4"),
          "Bb7": ("Bb2", "Ab3 D4 F4"), "D7": ("D2", "A3 C4 F#4")}
PAD = {k: v[1] for k, v in ZITHER.items()}
## the tune: one list per bar of (pitch | None, beats)
TUNE_A = [
    [("B4", 1), ("D5", 1), ("G5", 1)],
    [("F#5", 1.5), ("E5", .5), ("D5", 1)],
    [("E5", 1), ("C5", 1), ("A5", 1)],
    [("G5", 2), ("F#5", 1)],
    [("E5", 1.5), ("D5", .5), ("C5", 1)],
    [("B4", 1), ("A4", 1), ("B4", 1)],
    [("C5", 1), ("E5", 1), ("D5", 1)],
    [("D5", 3)],
]
TUNE_A_CLOSE = [[("C5", 1), ("A4", 1), ("F#4", 1)], [("G4", 3)]]
TUNE_B = [
    [("G5", 2), ("F5", 1)],
    [("Eb5", 2), ("D5", 1)],
    [("C5", 1), ("Eb5", 1), ("Ab5", 1)],
    [("F5", 2), (None, 1)],
]
TUNE_A2 = TUNE_A[:2] + [[("Eb5", 1), ("C5", 1), ("Ab5", 1)], [("G5", 2), ("F#5", 1)],
                        [("A4", 1.5), ("C5", .5), ("F#4", 1)], [("D5", 2), (None, 1)]]
## Sefir's motif in G (sefir_theme MOTIF up a fifth, an octave down): D G A B A G#, in beats
MOTIF_G = [("D3", 2), ("G3", 2), ("A3", 1), ("B3", 1), ("A3", 4), ("G#3", 2)]

# Bus gains were set from measured bus loudness (render(stats=...)["bus_lufs"], the whole loop) for these levels
# relative to the tune (flute 0 LU): the zither -5, the gilded bars -10, the drum -12, the pad -12, the hum -9 (eight
# bars of thirty), the Stillguard's gong -14.
GAINS = {"flute": 0.0, "zither": 1.6, "bars": 0.0, "drum": -7.4, "pad": -0.9, "hum": -7.4, "gong": -8.2}


def t_of(bar: int, beat: float = 0.0) -> float:
    return (bar - 1) * BAR + beat * BEAT


def add_tune(mx: LoopMixer, bars: list, start_bar: int, seed: int, vel: float, gilded: bool) -> None:
    g = rng(seed)
    first = True
    for i, bar in enumerate(bars):
        pos = t_of(start_bar + i)
        for k, (p, beats) in enumerate(bar):
            d = beats * BEAT
            if p is None:
                pos += d
                first = True
                continue
            v = vel * g.uniform(0.95, 1.04) * (1.05 if k == 0 else 1.0)
            x = breath_flute(n(p), d * 0.92 + 0.04, v, seed=seed + int(round(pos * 1000)), breath=0.36,
                             scoop_cents=30.0 if first else 8.0, vib_cents=12.0 if beats >= 2 else 4.0, vib_rate=4.8,
                             swell=0.2 if beats >= 3 else 0.0, attack=0.07 if first else 0.04, release=0.45,
                             beta=0.55)
            mx.add("flute", x, pos - FLUTE_PRE + float(g.normal(0, 0.006)), pan=-0.12)
            if gilded and k == 0:
                y = metallophone_note(n(p) + 12, 0.3 * g.uniform(0.9, 1.05), seed=seed + 7 + int(pos * 100),
                                      decay=3.0, hardness=0.3, ombak_hz=3.6)
                mx.add("bars", y, pos + 0.01, pan=0.35)
            pos += d
            first = False


def build(mx: LoopMixer) -> None:
    g = rng(SEED)
    for bar, (ch, sec) in enumerate(zip(CHORDS, SECTION), start=1):
        bass, chord = ZITHER[ch]
        x = string_pluck(n(bass), 2.6 * BEAT, 0.55 * g.uniform(0.95, 1.04), seed=SEED + 100 + bar, pick_pos=0.18,
                         t60=3.5, B=4e-5, max_f=3500.0, release=0.3)
        mx.add("zither", x, t_of(bar) + float(g.normal(0.008, 0.004)), pan=0.05)
        for beat in (1, 2):
            for j, p in enumerate(chord.split()):     # a light strum, low to high
                x = string_pluck(n(p), 0.8 * BEAT, (0.32 if beat == 1 else 0.27) * g.uniform(0.92, 1.05),
                                 seed=SEED + 1000 + 10 * bar + 3 * beat + j, pick_pos=0.14, t60=1.6, mute=0.25,
                                 B=5e-5, max_f=5000.0, release=0.15)
                mx.add("zither", x, t_of(bar, beat) + 0.012 * j + float(g.normal(0.01, 0.004)), pan=0.3 + 0.1 * j)
        x = pad_chord([n(p) - 12 for p in PAD[ch].split()], BAR * 0.98, 0.45, seed=SEED + 200 + bar, attack=0.8,
                      release=1.4)
        mx.add("pad", x, t_of(bar) - 0.2)
        # the drum: low on 1, rim on 3
        mx.add("drum", frame_drum("dum", 0.5 * g.uniform(0.9, 1.05), variant=bar % 3, seed=SEED + 300),
               t_of(bar) + float(g.normal(0.006, 0.004)), pan=-0.1)
        mx.add("drum", frame_drum("tek", 0.28 * g.uniform(0.9, 1.05), variant=bar % 2, seed=SEED + 301),
               t_of(bar, 2) + float(g.normal(0.006, 0.004)), pan=0.2)
    # the Stillguard's step: every two beats through B (2 against the dance's 3)
    for k in range(12):
        ts = t_of(17) + 2 * k * BEAT
        x = kettle_gong(n("D2"), 0.36 * (0.75 + 0.25 * k / 11), seed=SEED + 400 + k, t60=1.4, damp_at=0.55)
        mx.add("gong", x, ts + float(g.normal(0.0, 0.003)), pan=-0.3)
    # the tune
    add_tune(mx, TUNE_A, 3, SEED + 600, 0.5, gilded=True)
    add_tune(mx, TUNE_A[:4] + TUNE_A_CLOSE, 11, SEED + 620, 0.48, gilded=True)
    add_tune(mx, TUNE_B, 17, SEED + 640, 0.5, gilded=False)
    add_tune(mx, TUNE_A2, 25, SEED + 660, 0.47, gilded=True)
    # the Order's hum: the roots of B (bars 17-20), then Sefir's motif in G (bars 21-24), its G# held into the Cm bar
    roots = [(n("Eb2"), BAR), (n("C2") + 12, BAR), (n("Ab2"), BAR), (n("Bb2"), BAR)]
    mx.add("hum", hum_ensemble(roots, voices=10, seed=SEED + 1, register="low", spread=0.8), t_of(17) - 0.15)
    line = [(n(p), b * BEAT) for p, b in MOTIF_G]
    line[-1] = (line[-1][0], line[-1][1] + 3 * BEAT)
    mx.add("hum", hum_ensemble(line, voices=12, seed=SEED + 2, register="low", spread=0.9), t_of(21) - 0.15)


def render(out_path: str = OUT, verbose: bool = True, stats: dict | None = None) -> dict:
    mx = LoopMixer(intro_s=0.0, loop_s=LOOP_S, preroll_s=8.0)
    G = GAINS
    mx.bus("flute", G["flute"], send=0.32, process=lambda x: filt(x, [bq_highpass(200, 0.7), bq_peak(1500, 1.0, 1.0),
                                                                       bq_lowpass(7000, 0.7)]))
    mx.bus("zither", G["zither"], send=0.28, process=lambda x: filt(x, [bq_highpass(70, 0.7), bq_lowpass(5000, 0.7)]))
    mx.bus("bars", G["bars"], send=0.5, process=lambda x: filt(x, [bq_lowpass(6500, 0.7)]))
    mx.bus("drum", G["drum"], send=0.2)
    mx.bus("pad", G["pad"], send=0.45, process=lambda x: string_body(x, cutoff=1600.0))
    mx.bus("hum", G["hum"], send=0.5, process=lambda x: filt(x, [bq_lowpass(2400, 0.7)]))
    mx.bus("gong", G["gong"], send=0.3, process=lambda x: filt(x, [bq_lowpass(1500, 0.7)]))
    build(mx)
    court = ModFDNReverb(rt60=2.8, rt60_high=1.2, predelay=0.03, size=1.2, mod_depth=8.0, mod_rate=0.4,
                         early_level=0.3, lowcut=100.0, seed=SEED % 9973)
    _, loop = mx.render(reverb=court, reverb_return_db=-3.0)
    lead_in = int(round(LEAD_IN_BEATS * BEAT * SR))
    loop = np.roll(loop, lead_in, axis=0)
    rep: dict = {}
    _, loop = master_loop(np.zeros((0, 2)), loop, TARGET_LUFS, ceiling_db=-2.0, report=rep)
    L = len(loop)
    write_ogg(out_path, loop, quality=QUALITY, tags={"LOOPSTART": "0", "LOOPLENGTH": str(L)})
    write_loop_sidecar(os.path.splitext(out_path)[0] + ".loop.json", SR, 0, L, BPM, 3,
                       extra={"loop_bars": BARS, "downbeat_offset_s": lead_in / SR})
    m = measure(loop)
    if stats is not None:
        stats["bus_lufs"] = dict(mx.bus_lufs)
        stats["limiter"] = rep
    if verbose:
        print(f"peace_wedding: {m['seconds']:.2f}s  {m['integrated_lufs']:.2f} LUFS  TP {m['true_peak_dbtp']:.2f} dBTP"
              f"  limiter {rep}")
        print("  buses", {k: round(v, 1) for k, v in mx.bus_lufs.items()})
    return m


if __name__ == "__main__":
    render(sys.argv[1] if len(sys.argv) > 1 else OUT)
