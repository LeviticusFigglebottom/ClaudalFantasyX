"""`ansedra`: Ch13 "Gold and Lacquer", the holy city of Ansedra (M3-AUD-805; act_outline Ch13): a 61 s seamless loop.
An Act II sketch, for the human to judge the direction.

Original composition for this project (SPEC §2, §9). Original-material check: the court tune below (C-G, F-E-D-E,
A held, then the Lydian lift D-E-F# to G) and the bowls' four-note figure (G-C-E-D) were written for this cue. The
only borrowed material is our own: High Warden Sefir's motif (sefir_theme.py: G4 C5 D5 E5 D5 C#5, its C# held over F)
and that cue's glass harmonica, whose voice is imported from it. The bowls' figure is the motif's first four notes
reordered, so the city rings with its Warden before he is heard. The style evoked is a slow ceremonial procession
with gamelan-like bronze bars; no phrase is quoted from any existing music.

The brief: a city of perfect stillness on a lagoon kept flat by machines under it. Bowl-domes, inverted gilded bowls
on red-lacquer tiers; barges poled, never rowed; no seabirds, no dogs, no children's games. Sefir hosts the party.
Ceremonial, opulent, and a little hollow: the gold is real, and nothing is alive under it.

So the music is rich and nothing in it moves forward. C major, the Order's pure key (sefir_theme), 4/4 at 63 BPM
(a bar is 3.81 s), 16 bars. The bowls ring the same figure on every bar (the city's stillness: it changes chord, never
pattern). The bass never leaves C and G except under the motif (the lagoon held level). The hollowness is in the
voicing: open fifths in the hum, no third in the low register, and the motif's C#, the one wrong note, which in bar
14 becomes the root of a glowing D-flat major seventh (all gold, nowhere to go) before the court tune comes back.

Ensemble (all synthesized; no samples):
* gilded bowls: paired metallophone bars (a slow beat between each pair, gamelan-like), the four-note figure in
  quarters on every bar, high and soft;
* the court tune: breath flute, middle register, bars 3-10 and 15-16;
* the Order's hum: men on C and G for the whole loop (the Order hums; only Cantors sing, bible §4); in bars 11-14 a
  congregation hums Sefir's motif an octave down under the glass;
* Sefir's glass harmonica (from sefir_theme): the motif in bars 11-14;
* lacquer: a warm string pad on the chords, low in the mix;
* the Sanctum: a padded tower bell at bar 1, a kettle gong on beat 3 of every other bar, a large gong at bar 9.

Form (bars): 1-2 the bowls and the hum, the bell | 3-10 A, the court tune (C F F C Dm Am D G) | 11-14 B, the motif on
glass (C Em F Dbmaj7) | 15-16 the tune's last phrase over G, which leads back to bar 1's C.

Loop: LOOPSTART = 0 and LOOPLENGTH = the whole file. The file starts a sixteenth before bar 1's downbeat (the
sidecar's `downbeat_offset_s`), so the wrap seam falls in a quiet sixteenth, not on the bell.

Render:  python3 assets_src/music/ansedra.py   (or tools/audio/render_all.py --only ansedra)
"""
from __future__ import annotations

import importlib.util
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(ROOT, "tools", "audio"))

import numpy as np  # noqa: E402

from synth.bells import tower_bell  # noqa: E402
from synth.dsp import SR, bq_highpass, bq_lowpass, bq_peak, filt, rng  # noqa: E402
from synth.gongs import kettle_gong, large_gong  # noqa: E402
from synth.looping import LoopMixer, master_loop, write_loop_sidecar  # noqa: E402
from synth.metallophone import metallophone_note  # noqa: E402
from synth.mixer import measure, write_ogg  # noqa: E402
from synth.pad import pad_chord, string_body  # noqa: E402
from synth.reverb import ModFDNReverb  # noqa: E402
from synth.score import n  # noqa: E402
from synth.voice import hum_ensemble  # noqa: E402
from synth.winds import breath_flute  # noqa: E402


def _mod(name: str):
    spec = importlib.util.spec_from_file_location(name, os.path.join(HERE, f"{name}.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


SEFIR = _mod("sefir_theme")

OUT = os.path.join(ROOT, "assets", "audio", "music", "ansedra.ogg")
SEED = 20261313
TARGET_LUFS = -16.0
BPM = 63.0
BEAT = 60.0 / BPM
BAR = 4 * BEAT
BARS = 16
LOOP_S = BARS * BAR
## breath_flute's tone starts after its breath (0.05-0.08 s): notes are placed this much early.
FLUTE_PRE = 0.065
## the file starts this many beats before bar 1's downbeat (see render())
LEAD_IN_BEATS = 0.25
QUALITY = 3.0  # mix.md §5's sparse-cue quality

CHORDS = ["C", "C", "C", "F", "F", "C", "Dm", "Am", "D", "G", "C", "Em", "F", "Db", "G", "G"]
PAD = {"C": "C3 G3 E4", "F": "F3 C4 A4", "Dm": "D3 A3 F4", "Am": "A2 E3 C4", "D": "D3 A3 F#4", "G": "G2 D3 B3",
       "Em": "E3 B3 G4", "Db": "Db3 Ab3 F4 C5"}
## the bowls' figure per chord (G-C-E-D on C, moved to each chord's own tones)
BOWLS = {"C": "G5 C6 E6 D6", "F": "A5 C6 F6 E6", "Dm": "A5 D6 F6 E6", "Am": "A5 C6 E6 D6", "D": "A5 D6 F#6 E6",
         "G": "G5 B5 D6 C6", "Em": "G5 B5 E6 D6", "Db": "Ab5 C6 F6 Eb6"}
## the court tune: one list per bar of (pitch | None, beats)
TUNE = {
    3: [("C5", 2), ("G5", 2)],
    4: [("F5", 1.5), ("E5", .5), ("D5", 1), ("E5", 1)],
    5: [("A5", 3), ("G5", 1)],
    6: [("E5", 4)],
    7: [("F5", 2), ("A5", 1), ("G5", 1)],
    8: [("E5", 1.5), ("D5", .5), ("C5", 2)],
    9: [("D5", 2), ("E5", 1), ("F#5", 1)],
    10: [("G5", 3), (None, 1)],
    15: [("F5", 2), ("E5", 1), ("C5", 1)],
    16: [("D5", 3), (None, 1)],
}

# Bus gains were set from measured bus loudness (render(stats=...)["bus_lufs"], the whole loop) for these levels
# relative to the court tune (flute 0 LU; it rests six bars of sixteen): the glass motif -3 (four bars), the hummed
# motif -6, the bowls -6, the men's hum -8, the pad -11, the bell -14, the gongs -13.
GAINS = {"flute": 0.0, "glass": -11.7, "hum_motif": -5.8, "bowls": 0.8, "hum": -4.7, "pad": -1.6, "bell": -12.5,
         "gong": -9.4}


def t_of(bar: int, beat: float = 0.0) -> float:
    return (bar - 1) * BAR + beat * BEAT


def build(mx: LoopMixer) -> None:
    g = rng(SEED)
    # the Order's hum: C and G for the whole loop, an open fifth (loop=True: nobody breathes at the seam)
    mx.add("hum", hum_ensemble([(n("C3"), LOOP_S)], voices=12, seed=SEED + 1, register="low", loop=True), 0.0)
    mx.add("hum", 0.7 * hum_ensemble([(n("G2"), LOOP_S)], voices=8, seed=SEED + 2, register="low", loop=True), 0.0)
    for bar, ch in enumerate(CHORDS, start=1):
        # lacquer: the pad on the chord
        x = pad_chord([n(p) for p in PAD[ch].split()], BAR * 0.98, 0.5, seed=SEED + 100 + bar, attack=1.0,
                      release=1.6)
        mx.add("pad", x, t_of(bar) - 0.3)
        # the bowls: the figure in quarters, the first stroke a touch stronger
        for k, p in enumerate(BOWLS[ch].split()):
            v = (0.42 if k == 0 else 0.32) * g.uniform(0.92, 1.04)
            x = metallophone_note(n(p), v, seed=SEED + 1000 + 10 * bar + k, decay=3.8, hardness=0.35, ombak_hz=3.2)
            mx.add("bowls", x, t_of(bar, k) + float(g.normal(0.0, 0.006)), pan=-0.45 + 0.3 * k)
        # the Sanctum's kettle gong on beat 3 of every other bar
        if bar % 2 == 0:
            mx.add("gong", kettle_gong(n("G3"), 0.3, seed=SEED + 200 + bar, t60=2.6), t_of(bar, 2), pan=0.3)
    mx.add("gong", large_gong(n("C2"), 0.32, seed=SEED + 300, t60=9.0), t_of(9), pan=-0.1)
    mx.add("bell", tower_bell(n("C3"), 0.55, seed=SEED + 310, t60=8.0, dark=0.5), t_of(1), pan=-0.2)
    # the court tune
    for bar, notes in TUNE.items():
        pos, first = t_of(bar), True
        for p, beats in notes:
            d = beats * BEAT
            if p is None:
                pos += d
                first = True
                continue
            x = breath_flute(n(p), d * 0.95 + 0.04, 0.5 * g.uniform(0.95, 1.04), seed=SEED + 400 + int(pos * 100),
                             breath=0.38, scoop_cents=35.0 if first else 10.0, vib_cents=11.0 if beats >= 2 else 5.0,
                             vib_rate=4.6, swell=0.25 if beats >= 3 else 0.0, attack=0.08 if first else 0.05,
                             release=0.6, beta=0.55)
            mx.add("flute", x, pos - FLUTE_PRE + float(g.normal(0, 0.005)), pan=-0.1)
            pos += d
            first = False
    # Sefir's motif on his glass (bars 11-14), the congregation an octave down under it
    pos = t_of(11)
    for i, (p, beats) in enumerate(SEFIR.MOTIF):
        mx.add("glass", SEFIR.glass(n(p) + 12, beats * BEAT * 0.98, 0.8, seed=SEED + 500 + i), pos, pan=0.15)
        pos += beats * BEAT
    line = [(n(p) - 12, b * BEAT) for p, b in SEFIR.MOTIF]
    mx.add("hum_motif", hum_ensemble(line, voices=10, seed=SEED + 3, register="low", spread=0.9), t_of(11) - 0.2)


def render(out_path: str = OUT, verbose: bool = True, stats: dict | None = None) -> dict:
    mx = LoopMixer(intro_s=0.0, loop_s=LOOP_S, preroll_s=12.0)
    G = GAINS
    mx.bus("flute", G["flute"], send=0.40, process=lambda x: filt(x, [bq_highpass(200, 0.7), bq_peak(1500, 1.0, 1.0),
                                                                       bq_lowpass(7000, 0.7)]))
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
    _, loop = mx.render(reverb=hall, reverb_return_db=-2.0)
    # The loop is periodic, so it may start anywhere: a sixteenth before bar 1's downbeat.
    lead_in = int(round(LEAD_IN_BEATS * BEAT * SR))
    loop = np.roll(loop, lead_in, axis=0)
    rep: dict = {}
    _, loop = master_loop(np.zeros((0, 2)), loop, TARGET_LUFS, ceiling_db=-2.0, report=rep)
    L = len(loop)
    write_ogg(out_path, loop, quality=QUALITY, tags={"LOOPSTART": "0", "LOOPLENGTH": str(L)})
    write_loop_sidecar(os.path.splitext(out_path)[0] + ".loop.json", SR, 0, L, BPM, 4,
                       extra={"loop_bars": BARS, "downbeat_offset_s": lead_in / SR})
    m = measure(loop)
    if stats is not None:
        stats["bus_lufs"] = dict(mx.bus_lufs)
        stats["limiter"] = rep
    if verbose:
        print(f"ansedra: {m['seconds']:.2f}s  {m['integrated_lufs']:.2f} LUFS  TP {m['true_peak_dbtp']:.2f} dBTP"
              f"  limiter {rep}")
        print("  buses", {k: round(v, 1) for k, v in mx.bus_lufs.items()})
    return m


if __name__ == "__main__":
    render(sys.argv[1] if len(sys.argv) > 1 else OUT)
