"""`peace_wedding` (final): Ch14 "The Peace Wedding", the ceremony in the Lacquer Court at dusk (M3-AUD-842;
act_outline Ch14, act2_finals.md): a 131 s seamless loop, grown from the M3-AUD-805 sketch
(assets_src/music/peace_wedding.py). This is the ceremony's loop; the break at the trap is a later, separate cue.

Original composition for this project (SPEC §2, §9). Original-material check: the dance tune (B-D-G rising, F#-E-D,
E-C-A, G-F# ...), its close on G, its dark answer over E-flat and C minor, the A' that has caught the minor, the
zither's bass-chord-chord pattern, the voicings and the hummed motif are the sketch's, imported from it, not retyped.
Written new for this final: the couple's tune of bars 17-24 (B-E-G rising on E minor, G-E, D-B-D, A held; G-B-E,
E-D-C, C-E-A, F#-D#), played again on the zither's high course in bars 25-32 under a flute descant of held notes
(B-C-B-A-G-G-C-A), the alto a third under the dance tune in bars 33-40, and the second dark episode of bars 51-58
(G-B-flat, G-F-E-flat, C-E-flat-A-flat, A-flat-G, G-E-flat-B-flat, C-E-flat, then D-F#-A as the light comes back).
The only borrowed line is our own: High Warden Sefir's motif (sefir_theme.py MOTIF, G C D E D C#), hummed in G (D G A
B A G#) as the sketch hums it. The style evoked is a slow, formal court dance in triple time with plucked strings and
bronze; no phrase is quoted from any existing music.

The brief (the sketch's, unchanged): a gorgeous ceremony at dusk on still water; Liss's brother Tobin marries Merel
Dask, a Warden's daughter, for his people's peace. Sefir officiates. The Conclave springs the trap. It must be a real
dance, beautiful enough that the player wants the peace too, and a trap: the ground is giving way under it the whole
time.

So the final gives the peace more room before it takes it away. After the sketch's A, the couple's tune turns to E
minor, tender rather than sad, and is answered on the zither's high strings under a slow flute descant (the vows on
the water); then the dance returns with a second flute in thirds, the whole court dancing. Only then does B turn to
E-flat and C minor, and the Stillguard's damped gong begins to step every two beats against the dance's three; the
congregation hums Sefir's motif, its G# held over C minor until it is the chord's own A-flat; and the new episode
keeps the decline going (E-flat, C minor, A-flat, F minor) with the gong still stepping, louder, for sixteen bars
in all, before the light comes back on D and the sketch's A' (its third bar caught in the minor) ends on the
dominant, never on G, which is the next loop's first bar.

G major, 3/4 at 88 BPM (a bar is 2.05 s), 64 bars. Ensemble (all synthesized; no samples): the sketch's, plus the
zither's high course as a solo voice (bars 25-32) and a second breath flute (bars 33-40).

Form (bars): 1-2 the dance alone (G) | 3-10 A (G D Am Em C G Am D) | 11-16 A, its first half and a close on G | 17-24
C, the couple's tune (Em C G D Em C Am B7) | 25-32 C', on the zither, the flute's descant over it (Em C G D Em C Am D7)
| 33-40 A2, the dance tune in two flutes | 41-42 the dance alone | 43-46 B (Eb Cm Ab Bb7), the gong begins | 47-50
the motif hummed (G Em C Cm) | 51-58 D, the decline (Eb Cm Ab Fm Eb Cm D D7), the gong stepping on, the Order humming
the roots | 59-64 A' (G D Cm Em Am-D7 D7), which leads back to bar 1's G.

Loop: LOOPSTART = 0 and LOOPLENGTH = the whole file. The file starts a sixteenth before bar 1's downbeat (the
sidecar's `downbeat_offset_s`), so the wrap seam falls before the dance's downbeat, not on it.

Render:  python3 assets_src/music/act2/peace_wedding.py  (or tools/audio/render_all.py --act2 --only act2/peace_wedding)
"""
from __future__ import annotations

import importlib.util
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
MUSIC = os.path.dirname(HERE)
ROOT = os.path.abspath(os.path.join(MUSIC, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools", "audio"))

from synth.drums import frame_drum  # noqa: E402
from synth.dsp import bq_highpass, bq_lowpass, bq_peak, filt, rng  # noqa: E402
from synth.electric import string_pluck  # noqa: E402
from synth.gongs import kettle_gong  # noqa: E402
from synth.looping import LoopMixer  # noqa: E402
from synth.pad import pad_chord, string_body  # noqa: E402
from synth.reverb import ModFDNReverb  # noqa: E402
from synth.score import n  # noqa: E402
from synth.voice import hum_ensemble  # noqa: E402


def _mod(name: str, path: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


S = _mod("peace_wedding_sketch", os.path.join(MUSIC, "peace_wedding.py"))   # the sketch: its material, never edited
V = _mod("act2_voices", os.path.join(MUSIC, "act2_voices.py"))              # V.finish: the sketches' render path

OUT = os.path.join(ROOT, "assets", "audio", "music", "act2", "peace_wedding.ogg")
SEED = 20261442
TARGET_LUFS = S.TARGET_LUFS
BPM = S.BPM
BEAT = S.BEAT
BAR = S.BAR
BARS = 64
LOOP_S = BARS * BAR
LEAD_IN_BEATS = S.LEAD_IN_BEATS
QUALITY = S.QUALITY

COUPLE_CHORDS = ["Em", "C", "G", "D", "Em", "C", "Am", "B7"]
D_CHORDS = ["Eb", "Cm", "Ab", "Fm", "Eb", "Cm", "D", "D7"]
CHORDS = (S.CHORDS[:16] + COUPLE_CHORDS + COUPLE_CHORDS[:7] + ["D7"] + S.A_CHORDS + ["G", "G"] + S.CHORDS[16:24]
          + D_CHORDS + S.CHORDS[24:])
ZITHER = {**S.ZITHER, "B7": ("B2", "A3 D#4 F#4"), "Fm": ("F2", "Ab3 C4 F4")}
PAD = {k: v[1] for k, v in ZITHER.items()}
## the couple's tune (bars 17-24): one list per bar of (pitch | None, beats)
COUPLE = [
    [("B4", 1), ("E5", 1), ("G5", 1)],
    [("G5", 2), ("E5", 1)],
    [("D5", 1.5), ("B4", .5), ("D5", 1)],
    [("A4", 3)],
    [("G4", 1), ("B4", 1), ("E5", 1)],
    [("E5", 1.5), ("D5", .5), ("C5", 1)],
    [("C5", 1), ("E5", 1), ("A5", 1)],
    [("F#5", 2), ("D#5", 1)],
]
## C' (bars 25-32): the same tune on the zither, its last bar turned to D7; the flute's descant over it
COUPLE_ZITHER = COUPLE[:7] + [[("F#5", 2), ("D5", 1)]]
DESCANT = [[("B5", 3)], [("C6", 3)], [("B5", 3)], [("A5", 3)], [("G5", 3)], [("G5", 3)], [("C6", 3)], [("A5", 3)]]
## A2 (bars 33-40): the alto a third (or a sixth) under the dance tune
ALTO_A = [
    [("D5", 2), ("B4", 1)],
    [("A4", 3)],
    [("C5", 2), ("E5", 1)],
    [("B4", 3)],
    [("C5", 1.5), ("B4", .5), ("A4", 1)],
    [("G4", 1), ("F#4", 1), ("G4", 1)],
    [("A4", 1), ("C5", 1), ("B4", 1)],
    [("F#4", 3)],
]
## D (bars 51-58): the decline, after the sketch's B
TUNE_D = [
    [("G5", 2), ("Bb5", 1)],
    [("G5", 1.5), ("F5", .5), ("Eb5", 1)],
    [("C5", 1), ("Eb5", 1), ("Ab5", 1)],
    [("Ab5", 2), ("G5", 1)],
    [("G5", 1), ("Eb5", 1), ("Bb4", 1)],
    [("C5", 2), ("Eb5", 1)],
    [("D5", 1), ("F#5", 1), ("A5", 1)],
    [("A5", 2), (None, 1)],
]
B_BAR, MOTIF_BAR, D_BAR = 43, 47, 51
GONG_BARS = (B_BAR, D_BAR + 8)              # the Stillguard's step: every two beats from B to the end of D
## the Order's roots: B's (the sketch's), then D's
B_ROOTS = ["Eb2", "C3", "Ab2", "Bb2"]
D_ROOTS = ["Eb2", "C3", "Ab2", "F2", "Eb2", "C3", "D3", "D3"]

# The sketch's bus gains (set from its measured bus loudness). The new voices each play 8 bars of 64, so they were set
# from their whole-loop bus loudness plus 9 LU: the zither's solo about level with the tune while it carries it, the
# descant about 5 LU under the solo, the alto about 5 LU under the tune.
GAINS = {**S.GAINS, "solo": 2.5, "descant": -12.5, "alto": -11.5}


def t_of(bar: int, beat: float = 0.0) -> float:
    return (bar - 1) * BAR + beat * BEAT


class _Renamed:
    """The mixer seen through other bus names, so the sketch's add_tune can play a second flute line."""

    def __init__(self, mx: LoopMixer, names: dict):
        self.mx, self.names = mx, names

    def add(self, bus: str, *args, **kw) -> None:
        self.mx.add(self.names.get(bus, bus), *args, **kw)


def zither_solo(mx: LoopMixer, bars: list, start_bar: int, seed: int, vel: float) -> None:
    """A melody on the zither's high course: each note plucked, a long note re-struck softly on each later beat."""
    g = rng(seed)
    for i, bar in enumerate(bars):
        pos = 0.0
        for k, (p, beats) in enumerate(bar):
            for r in range(int(beats)):
                v = vel * g.uniform(0.94, 1.05) * (1.06 if k == 0 else 1.0) * (0.55 if r else 1.0)
                x = string_pluck(n(p), (beats - r) * BEAT * 0.95 + 0.1, v, seed=seed + 50 * i + 7 * k + r,
                                 pick_pos=0.11, t60=2.4, B=5e-5, max_f=6500.0, release=0.25)
                mx.add("solo", x, t_of(start_bar + i, pos + r) + float(g.normal(0.008, 0.004)), pan=-0.25)
            pos += beats


def build(mx: LoopMixer) -> None:
    g = rng(SEED)
    for bar, ch in enumerate(CHORDS, start=1):
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
        mx.add("drum", frame_drum("dum", 0.5 * g.uniform(0.9, 1.05), variant=bar % 3, seed=SEED + 300),
               t_of(bar) + float(g.normal(0.006, 0.004)), pan=-0.1)
        mx.add("drum", frame_drum("tek", 0.28 * g.uniform(0.9, 1.05), variant=bar % 2, seed=SEED + 301),
               t_of(bar, 2) + float(g.normal(0.006, 0.004)), pan=0.2)
    # the Stillguard's step: every two beats (2 against the dance's 3), growing a little through B and D
    steps = (GONG_BARS[1] - GONG_BARS[0]) * 3 // 2
    for k in range(steps):
        x = kettle_gong(n("D2"), 0.36 * (0.72 + 0.36 * k / (steps - 1)), seed=SEED + 400 + k, t60=1.4, damp_at=0.55)
        mx.add("gong", x, t_of(GONG_BARS[0]) + 2 * k * BEAT + float(g.normal(0.0, 0.003)), pan=-0.3)
    # the tunes: the sketch's, then the new ones, on the sketch's own add_tune
    S.add_tune(mx, S.TUNE_A, 3, SEED + 600, 0.5, gilded=True)
    S.add_tune(mx, S.TUNE_A[:4] + S.TUNE_A_CLOSE, 11, SEED + 620, 0.48, gilded=True)
    S.add_tune(mx, COUPLE, 17, SEED + 700, 0.47, gilded=True)
    zither_solo(mx, COUPLE_ZITHER, 25, SEED + 720, 0.5)
    S.add_tune(_Renamed(mx, {"flute": "descant"}), DESCANT, 25, SEED + 740, 0.4, gilded=False)
    S.add_tune(mx, S.TUNE_A, 33, SEED + 760, 0.5, gilded=True)
    S.add_tune(_Renamed(mx, {"flute": "alto"}), ALTO_A, 33, SEED + 780, 0.42, gilded=False)
    S.add_tune(mx, S.TUNE_B, B_BAR, SEED + 640, 0.5, gilded=False)
    S.add_tune(mx, TUNE_D, D_BAR, SEED + 800, 0.5, gilded=False)
    S.add_tune(mx, S.TUNE_A2, D_BAR + 8, SEED + 660, 0.47, gilded=True)
    # the Order's hum: B's roots, Sefir's motif in G (its G# held into the Cm bar), then D's roots
    for bar, roots, seed in ((B_BAR, B_ROOTS, SEED + 1), (D_BAR, D_ROOTS, SEED + 4)):
        mx.add("hum", hum_ensemble([(n(p), BAR) for p in roots], voices=10, seed=seed, register="low", spread=0.8),
               t_of(bar) - 0.15)
    line = [(n(p), b * BEAT) for p, b in S.MOTIF_G]
    line[-1] = (line[-1][0], line[-1][1] + 3 * BEAT)
    mx.add("hum", hum_ensemble(line, voices=12, seed=SEED + 2, register="low", spread=0.9), t_of(MOTIF_BAR) - 0.15)


def render(out_path: str = OUT, verbose: bool = True, stats: dict | None = None) -> dict:
    mx = LoopMixer(intro_s=0.0, loop_s=LOOP_S, preroll_s=8.0)
    G = GAINS
    flute_eq = lambda x: filt(x, [bq_highpass(200, 0.7), bq_peak(1500, 1.0, 1.0), bq_lowpass(7000, 0.7)])  # noqa
    mx.bus("flute", G["flute"], send=0.32, process=flute_eq)
    mx.bus("descant", G["descant"], send=0.45, process=flute_eq)
    mx.bus("alto", G["alto"], send=0.36, process=flute_eq)
    mx.bus("zither", G["zither"], send=0.28, process=lambda x: filt(x, [bq_highpass(70, 0.7), bq_lowpass(5000, 0.7)]))
    mx.bus("solo", G["solo"], send=0.34, process=lambda x: filt(x, [bq_highpass(150, 0.7), bq_lowpass(6500, 0.7)]))
    mx.bus("bars", G["bars"], send=0.5, process=lambda x: filt(x, [bq_lowpass(6500, 0.7)]))
    mx.bus("drum", G["drum"], send=0.2)
    mx.bus("pad", G["pad"], send=0.45, process=lambda x: string_body(x, cutoff=1600.0))
    mx.bus("hum", G["hum"], send=0.5, process=lambda x: filt(x, [bq_lowpass(2400, 0.7)]))
    mx.bus("gong", G["gong"], send=0.3, process=lambda x: filt(x, [bq_lowpass(1500, 0.7)]))
    build(mx)
    court = ModFDNReverb(rt60=2.8, rt60_high=1.2, predelay=0.03, size=1.2, mod_depth=8.0, mod_rate=0.4,
                         early_level=0.3, lowcut=100.0, seed=SEED % 9973)
    return V.finish(mx, "peace_wedding (final)", out_path, BPM, 3, BARS, LEAD_IN_BEATS * BEAT, TARGET_LUFS, court,
                    -3.0, verbose, stats, quality=QUALITY)


if __name__ == "__main__":
    render(sys.argv[1] if len(sys.argv) > 1 else OUT)
