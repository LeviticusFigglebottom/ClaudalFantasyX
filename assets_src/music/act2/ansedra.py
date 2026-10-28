"""`ansedra` (final): Ch13 "Gold and Lacquer", the holy city of Ansedra (M3-AUD-842; act_outline Ch13, act2_finals.md):
a 152 s seamless loop, grown from the M3-AUD-805 sketch (assets_src/music/ansedra.py).

Original composition for this project (SPEC §2, §9). Original-material check: the court tune (C-G, F-E-D-E, A held,
the Lydian lift D-E-F# to G), its last phrase, the bowls' four-note figure, the chords and the voicings are the
sketch's, imported from it, not retyped. Written new for this final: the barge song of bars 17-24 (E-A, G-F-E-F, E
held, the climb D-F-A and its fall G-F-D over B-flat), the second flute's line a third and a sixth under the court
tune in bars 29-36, and the bowls' figure moved to B-flat and to G with a suspended fourth. The only other borrowed
material is our own: High Warden Sefir's motif (sefir_theme.py: G4 C5 D5 E5 D5 C#5, its C# held over F) and his
glass harmonica, both reached through the sketch's own import of sefir_theme. The style evoked is a slow ceremonial
procession with gamelan-like bronze bars; no phrase is quoted from any existing music.

The brief (the sketch's, unchanged): a city of perfect stillness on a lagoon kept flat by machines under it.
Bowl-domes on red-lacquer tiers; barges poled, never rowed; no seabirds, no dogs, no children's games. Sefir hosts
the party. Ceremonial, opulent, and a little hollow: the gold is real, and nothing is alive under it.

So the final grows without ever moving forward. The bowls ring the same figure on every bar of all forty (it changes
chord, never pattern); the men hum C and G under the whole loop, even under the barge song's A minor and B-flat (the
lagoon held level whatever floats on it). The new section is the barges: the court tune's opening leap and turn
sung on A minor and F, a darker, slower glide, that climbs once and falls back on the B-flat (lacquer: the
flattened seventh, gold over the C pedal) to a suspended G that never quite resolves. Then the congregation hums
Sefir's motif with no glass at all (the Order present without him) until the glass enters on its C# alone. When the
court tune returns it is doubled by a second flute in thirds and sixths, fuller and no more alive, and the close
passes through the motif's D-flat once more before the tune's last phrase leads back to bar 1.

C major, 4/4 at 63 BPM (a bar is 3.81 s), 40 bars. Ensemble (all synthesized; no samples): the sketch's, plus a
second breath flute (the court's alto) in A'.

Form (bars): 1-2 the bowls and the hum, the bell | 3-10 A, the court tune (C F F C Dm Am D G) | 11-14 B, the motif
on glass (C Em F Dbmaj7) | 15-16 the tune's last phrase over G | 17-24 C, the barge song (Am F Am F Dm Bb Gsus4 G),
a soft bell at 17 | 25-28 B', the motif hummed alone, the glass only on its C# (C Em F Dbmaj7) | 29-36 A', the court
tune in two flutes (C F F C Dm Am D G), the large gong at 35 | 37-40 the motif's D and C# on glass (F Dbmaj7), then
the tune's last phrase over G, which leads back to bar 1's C.

Loop: LOOPSTART = 0 and LOOPLENGTH = the whole file. The file starts a sixteenth before bar 1's downbeat (the
sidecar's `downbeat_offset_s`), so the wrap seam falls in a quiet sixteenth, not on the bell.

Render:  python3 assets_src/music/act2/ansedra.py   (or tools/audio/render_all.py --act2 --only act2/ansedra)
"""
from __future__ import annotations

import importlib.util
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
MUSIC = os.path.dirname(HERE)
ROOT = os.path.abspath(os.path.join(MUSIC, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools", "audio"))

from synth.bells import tower_bell  # noqa: E402
from synth.dsp import bq_highpass, bq_lowpass, bq_peak, filt, rng  # noqa: E402
from synth.gongs import kettle_gong, large_gong  # noqa: E402
from synth.looping import LoopMixer  # noqa: E402
from synth.metallophone import metallophone_note  # noqa: E402
from synth.pad import pad_chord, string_body  # noqa: E402
from synth.reverb import ModFDNReverb  # noqa: E402
from synth.score import n  # noqa: E402
from synth.voice import hum_ensemble  # noqa: E402
from synth.winds import breath_flute  # noqa: E402


def _mod(name: str, path: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


S = _mod("ansedra_sketch", os.path.join(MUSIC, "ansedra.py"))       # the sketch: its material, never edited
V = _mod("act2_voices", os.path.join(MUSIC, "act2_voices.py"))      # V.finish: the sketches' render path
SEFIR = S.SEFIR                                                     # Sefir's motif and glass, as the sketch has them

OUT = os.path.join(ROOT, "assets", "audio", "music", "act2", "ansedra.ogg")
SEED = 20261342
TARGET_LUFS = S.TARGET_LUFS
BPM = S.BPM
BEAT = S.BEAT
BAR = S.BAR
BARS = 40
LOOP_S = BARS * BAR
FLUTE_PRE = S.FLUTE_PRE
LEAD_IN_BEATS = S.LEAD_IN_BEATS
QUALITY = S.QUALITY

## the sketch's sections, by bar of this final: (first bar here, first bar in the sketch, bars)
A_BARS = [(3, 3, 8), (29, 3, 8)]            # the court tune
CLOSE = [(15, 15, 2), (39, 15, 2)]          # its last phrase over G
BARGE_CHORDS = ["Am", "F", "Am", "F", "Dm", "Bb", "Gsus", "G"]
CHORDS = (S.CHORDS[:16] + BARGE_CHORDS + S.CHORDS[10:14] + S.CHORDS[2:10] + ["F", "Db", "G", "G"])
PAD = {**S.PAD, "Bb": "Bb2 F3 D4", "Gsus": "G2 D3 C4"}
BOWLS = {**S.BOWLS, "Bb": "F5 Bb5 D6 C6", "Gsus": "G5 C6 D6 C6"}
## the barge song (bars 17-24): one list per bar of (pitch | None, beats)
BARGE = {
    17: [("E5", 2), ("A5", 2)],
    18: [("G5", 1.5), ("F5", .5), ("E5", 1), ("F5", 1)],
    19: [("E5", 3), ("C5", 1)],
    20: [("C5", 4)],
    21: [("D5", 2), ("F5", 1), ("A5", 1)],
    22: [("G5", 1.5), ("F5", .5), ("D5", 2)],
    23: [("C5", 2), ("D5", 2)],
    24: [("B4", 3), (None, 1)],
}
## the court's alto under the tune's return: per sketch bar (3-10) of the tune, a third or a sixth under it
ALTO = {
    3: [("G4", 2), ("E5", 2)],
    4: [("C5", 1.5), ("C5", .5), ("A4", 1), ("C5", 1)],
    5: [("F5", 3), ("E5", 1)],
    6: [("C5", 4)],
    7: [("D5", 2), ("F5", 1), ("E5", 1)],
    8: [("C5", 1.5), ("B4", .5), ("A4", 2)],
    9: [("A4", 2), ("A4", 1), ("D5", 1)],
    10: [("D5", 3), (None, 1)],
}
MOTIF_GLASS = (11,)             # the motif on glass, with the congregation under it
MOTIF_HUMMED = (25,)            # the congregation alone; the glass only on the C#
BELLS = [(1, 0.55), (17, 0.32)]
LARGE_GONGS = (9, 35)

# The sketch's bus gains (set from its measured bus loudness); the alto sits about 5 LU under the court tune while
# both play (it plays 8 bars of 40, the tune 26).
GAINS = {**S.GAINS, "alto": -9.0}


def t_of(bar: int, beat: float = 0.0) -> float:
    return (bar - 1) * BAR + beat * BEAT


def add_line(mx: LoopMixer, bus: str, bar: int, notes: list, g, vel: float, pan: float, seed: int = 400) -> None:
    """One bar of a flute line, phrased as the sketch phrases its court tune."""
    pos, first = t_of(bar), True
    for p, beats in notes:
        d = beats * BEAT
        if p is None:
            pos += d
            first = True
            continue
        x = breath_flute(n(p), d * 0.95 + 0.04, vel * g.uniform(0.95, 1.04), seed=SEED + seed + int(pos * 100),
                         breath=0.38, scoop_cents=35.0 if first else 10.0, vib_cents=11.0 if beats >= 2 else 5.0,
                         vib_rate=4.6, swell=0.25 if beats >= 3 else 0.0, attack=0.08 if first else 0.05,
                         release=0.6, beta=0.55)
        mx.add(bus, x, pos - FLUTE_PRE + float(g.normal(0, 0.005)), pan=pan)
        pos += d
        first = False


def build(mx: LoopMixer) -> None:
    g = rng(SEED)
    # the Order's hum: C and G for the whole loop, an open fifth (loop=True: nobody breathes at the seam)
    mx.add("hum", hum_ensemble([(n("C3"), LOOP_S)], voices=12, seed=SEED + 1, register="low", loop=True), 0.0)
    mx.add("hum", 0.7 * hum_ensemble([(n("G2"), LOOP_S)], voices=8, seed=SEED + 2, register="low", loop=True), 0.0)
    for bar, ch in enumerate(CHORDS, start=1):
        x = pad_chord([n(p) for p in PAD[ch].split()], BAR * 0.98, 0.5, seed=SEED + 100 + bar, attack=1.0,
                      release=1.6)
        mx.add("pad", x, t_of(bar) - 0.3)
        # the bowls: the same figure on every bar, moved to the chord
        for k, p in enumerate(BOWLS[ch].split()):
            v = (0.42 if k == 0 else 0.32) * g.uniform(0.92, 1.04)
            x = metallophone_note(n(p), v, seed=SEED + 1000 + 10 * bar + k, decay=3.8, hardness=0.35, ombak_hz=3.2)
            mx.add("bowls", x, t_of(bar, k) + float(g.normal(0.0, 0.006)), pan=-0.45 + 0.3 * k)
        if bar % 2 == 0:
            mx.add("gong", kettle_gong(n("G3"), 0.3, seed=SEED + 200 + bar, t60=2.6), t_of(bar, 2), pan=0.3)
    for i, bar in enumerate(LARGE_GONGS):
        mx.add("gong", large_gong(n("C2"), 0.32 - 0.03 * i, seed=SEED + 300 + i, t60=9.0), t_of(bar), pan=-0.1)
    for i, (bar, v) in enumerate(BELLS):
        mx.add("bell", tower_bell(n("C3"), v, seed=SEED + 310 + i, t60=8.0, dark=0.5), t_of(bar), pan=-0.2)
    # the court tune and its last phrase (the sketch's TUNE), the alto under the return
    for start, sk, length in A_BARS + CLOSE:
        for k in range(length):
            add_line(mx, "flute", start + k, S.TUNE[sk + k], g, 0.5, -0.1)
            if start == A_BARS[1][0]:
                add_line(mx, "alto", start + k, ALTO[sk + k], g, 0.42, 0.25, seed=40000)
    for bar, notes in BARGE.items():
        add_line(mx, "flute", bar, notes, g, 0.46, -0.05)
    # Sefir's motif: on glass with the congregation an octave down (B), then the congregation alone (B')
    line = [(n(p) - 12, b * BEAT) for p, b in SEFIR.MOTIF]
    for i, bar in enumerate(MOTIF_GLASS + MOTIF_HUMMED):
        mx.add("hum_motif", hum_ensemble(line, voices=10 + 2 * i, seed=SEED + 3 + i, register="low", spread=0.9),
               t_of(bar) - 0.2)
        pos = t_of(bar)
        for k, (p, beats) in enumerate(SEFIR.MOTIF):
            if bar in MOTIF_GLASS or k == len(SEFIR.MOTIF) - 1:
                mx.add("glass", SEFIR.glass(n(p) + 12, beats * BEAT * 0.98, 0.8, seed=SEED + 500 + 10 * i + k), pos,
                       pan=0.15)
            pos += beats * BEAT
    # the close: the motif's D and its C# once more on glass, over F and the D-flat chord
    for k, p in enumerate(("D5", "C#5")):
        mx.add("glass", SEFIR.glass(n(p) + 12, 4 * BEAT * 0.98, 0.7, seed=SEED + 560 + k), t_of(37 + k), pan=0.15)


def render(out_path: str = OUT, verbose: bool = True, stats: dict | None = None) -> dict:
    mx = LoopMixer(intro_s=0.0, loop_s=LOOP_S, preroll_s=12.0)
    G = GAINS
    flute_eq = lambda x: filt(x, [bq_highpass(200, 0.7), bq_peak(1500, 1.0, 1.0), bq_lowpass(7000, 0.7)])  # noqa
    mx.bus("flute", G["flute"], send=0.40, process=flute_eq)
    mx.bus("alto", G["alto"], send=0.45, process=flute_eq)
    mx.bus("glass", G["glass"], send=0.55, process=lambda x: filt(x, [bq_highpass(250, 0.7)]))
    mx.bus("hum_motif", G["hum_motif"], send=0.6)
    mx.bus("bowls", G["bowls"], send=0.55, process=lambda x: filt(x, [bq_lowpass(6000, 0.7)]))
    mx.bus("hum", G["hum"], send=0.5, process=lambda x: filt(x, [bq_lowpass(2200, 0.7)]))
    mx.bus("pad", G["pad"], send=0.5, process=lambda x: string_body(x, cutoff=1800.0))
    mx.bus("bell", G["bell"], send=0.5)
    mx.bus("gong", G["gong"], send=0.45)
    build(mx)
    hall = ModFDNReverb(rt60=4.8, rt60_high=1.8, predelay=0.05, size=1.5, mod_depth=10.0, mod_rate=0.3,
                        early_level=0.25, lowcut=90.0, seed=SEED % 9973)
    return V.finish(mx, "ansedra (final)", out_path, BPM, 4, BARS, LEAD_IN_BEATS * BEAT, TARGET_LUFS, hall, -2.0,
                    verbose, stats, quality=QUALITY)


if __name__ == "__main__":
    render(sys.argv[1] if len(sys.argv) > 1 else OUT)
