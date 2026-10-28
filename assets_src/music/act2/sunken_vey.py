"""`sunken_vey` (final): Ch11, Sunken Vey, the drowned galleries of the great Lit Age city (M3-AUD-840; the
M3-AUD-804 sketch grown into a full piece; act_outline Ch11, bible §5.6): a 156.5 s seamless loop.

Original composition for this project (SPEC §2, §9). The sketch's material (assets_src/music/sunken_vey.py: the
glass song, the chords, the conduits, the bubbles, every voice and level) is imported from it, not retyped, and the
sketch file is untouched. Original-material check: the new section's song (bars 17-23) turns the song's cell over
(the falling third becomes a rising one, Db-Eb-F) and comes down through the Dorian sixth, C natural, to rest on it;
the low glass under it is a plain falling scale, one note a bar (contrary motion); the deep (bars 25-28) has only
the song's first cell, an octave down. None of it is taken from any melody we know; the glass harmonica is the
game's own voice for glimmer (sefir_theme.py), through act2_voices.glass. Nothing else is borrowed.

The brief (as the sketch): the largest Lit Age ruin still above water; towered stone galleries chest-deep in a
turquoise lagoon, wrapped in strangler-fig roots, the old ceramic conduits still pulsing faintly with bound light.
Silent, gorgeous and dead. Submerged, glassy and slow: everything but the glass is heard as if through water, and
nothing has an attack except the drowned bell and the roots. In the final the light in the conduits is the
development's subject: the new song climbs to the highest note in the cue (F5) and settles on the C natural.

E-flat Dorian (Eb F Gb Ab Bb C Db; the raised sixth, C natural, is the light still in the conduits), 3/4 at 46 BPM
(a bar is 3.913 s), 40 bars. The sketch's palette, unchanged: the glass and the low glass, the underwater drone on
Eb and Bb, the dark string pad, the drowned bell (synth.bells.tower_bell), the roots (a muted low pluck every other
bar), the conduits (Bb5 and Eb6 pulsing once every two beats) and far bubbles.

Form (bars):
*  1-4   the galleries: drone, pad, the bell, conduits, bubbles (the sketch's bars 1-4)
*  5-15  the song: A (5-8), A' with the low glass and the bell (9-12), its last phrase rising to the Dorian sixth and
         settling on Bb (13-15) (the sketch's bars 5-15)
* 16     silence over A-flat major (the sketch's bar 16)
* 17-24  C, new: the cell turned upward over Gb Db Ab Bbm Fm Gb Ab Ab, the low glass falling against it, resting on
         C natural (bar 23); bar 24 is silence
* 25-28  the deep: no song; the bell a third time (bar 25), the song's first cell far below in the low glass over
         Bbm Ab Gb Ab
* 29-36  A'', the song's first eight bars again, the low glass doubling all of it
* 37-39  the song's last phrase, rising to C and settling on Bb
* 40     silence over A-flat major, which leads back to bar 1's E-flat minor

Loop: LOOPSTART = 0 and LOOPLENGTH = the whole file. The file starts a sixteenth before bar 1's downbeat (the
sidecar's `downbeat_offset_s`), so the wrap seam falls in a quiet sixteenth. Vorbis q3.

Render:  python3 assets_src/music/act2/sunken_vey.py   (or tools/audio/render_all.py --act2 --only act2/sunken_vey)
"""
from __future__ import annotations

import importlib.util
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools", "audio"))


from synth.bells import tower_bell  # noqa: E402
from synth.dsp import bq_highpass, bq_lowpass, filt, rng  # noqa: E402
from synth.electric import string_pluck  # noqa: E402
from synth.looping import LoopMixer  # noqa: E402
from synth.pad import pad_chord, string_body  # noqa: E402
from synth.reverb import ModFDNReverb  # noqa: E402
from synth.score import n  # noqa: E402


def _mod(name: str, path: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


SK = _mod("sunken_vey_sketch", os.path.join(HERE, "..", "sunken_vey.py"))
V = SK.V

OUT = os.path.join(ROOT, "assets", "audio", "music", "act2", "sunken_vey.ogg")
SEED = SK.SEED + 840_000
TARGET_LUFS = SK.TARGET_LUFS
BPM, BEAT, BAR = SK.BPM, SK.BEAT, SK.BAR
BARS = 40
LOOP_S = BARS * BAR
LEAD_IN_BEATS = SK.LEAD_IN_BEATS
QUALITY = SK.QUALITY
t_of = SK.t_of

CHORDS = (SK.CHORDS
          + ["Gb", "Db", "Ab", "Bbm", "Fm", "Gb", "Ab", "Ab"]
          + ["Bbm", "Ab", "Gb", "Ab"]
          + SK.CHORDS[4:12]
          + SK.CHORDS[12:16])
assert len(CHORDS) == BARS
PAD = dict(SK.PAD, Fm="F2 C3 F3 Ab3")
ROOTS = dict(SK.ROOTS, Fm="F1")

## the new section's song: the cell turned upward, coming down to rest on the Dorian sixth
SONG_C = [
    [("Db5", 2), ("Eb5", 1)],
    [("F5", 3)],
    [("Eb5", 1), ("C5", 1), ("Ab4", 1)],
    [("Bb4", 3)],
    [("Ab4", 2), ("C5", 1)],
    [("Db5", 1.5), ("Bb4", 1.5)],
    [("C5", 3)],                                # the light, held
]
## the low glass under it: one note a bar, falling against the rising song
LOW_C = ["Gb3", "F3", "Eb3", "Db3", "C3", "Db3", "Eb3"]
## the deep: the song's first cell, far below
DEEP = [(26, [("Bb3", 2), ("Ab3", 1)]), (27, [("Gb3", 3)])]
## (bars of the song, first bar, low glass doubles the long notes from this bar, or every note)
SONG_PLAN = [(SK.SONG, 5, 9, False), (SK.SONG[:8], 29, 29, True), (SK.SONG[8:], 37, 37, False)]
BELLS = ((1, 0.7), (9, 0.55), (25, 0.6))


def add_song(mx: LoopMixer, song: list, first: int, low_from: int, low_all: bool, seed: int) -> None:
    """The sketch's glass writer, placed anywhere: the low glass doubles the long notes (or all) from `low_from`."""
    g = rng(seed)
    for i, bar in enumerate(song):
        b = first + i
        pos = t_of(b)
        for p, beats in bar:
            d = beats * BEAT
            v = 0.7 * float(g.uniform(0.92, 1.04))
            mx.add("glass", V.glass(n(p), d * 0.98, v, seed + 100 + int(round(pos * 100))), pos - V.GLASS_PRE,
                   pan=-0.1)
            if b >= low_from and (low_all or beats >= 2):
                mx.add("glass_low", V.glass(n(p) - 12, d * 0.98, v * (0.85 if low_all else 1.0),
                                            seed + 200 + int(round(pos * 100))), pos - V.GLASS_PRE + 0.03, pan=0.25)
            pos += d


def add_low(mx: LoopMixer, notes: list, seed: int, vel: float) -> None:
    """Single low-glass notes: (bar, [(pitch, beats)])."""
    g = rng(seed)
    for bar, line in notes:
        pos = t_of(bar)
        for p, beats in line:
            d = beats * BEAT
            mx.add("glass_low", V.glass(n(p), d * 0.98, vel * float(g.uniform(0.92, 1.04)),
                                        seed + int(round(pos * 100))), pos - V.GLASS_PRE, pan=0.25)
            pos += d


def on_final_loop(fn, *args):
    """Run one of the sketch's loop-length writers (SK.conduits, SK.add_bubbles) on the final's loop: they read the
    sketch module's LOOP_S, which is set to the final's for the call and restored after."""
    old = SK.LOOP_S
    SK.LOOP_S = LOOP_S
    try:
        return fn(*args)
    finally:
        SK.LOOP_S = old


def build(mx: LoopMixer) -> None:
    g = rng(SEED)
    mx.add("drone", V.periodic_drone(LOOP_S, [(n("Eb2"), 1.0), (n("Bb2"), 0.4)], SEED + 3, partials=5,
                                     breath_s=LOOP_S / 10), 0.0)
    mx.add("conduits", on_final_loop(SK.conduits), 0.0)
    for bar, ch in enumerate(CHORDS, start=1):
        x = pad_chord([n(p) for p in PAD[ch].split()], BAR * 0.96, 0.45, seed=SEED + 200 + bar, voices=4,
                      attack=2.0, release=2.0, width=0.85)
        mx.add("pad", x, t_of(bar) - 0.5)
        if bar % 2 == 1:
            x = string_pluck(n(ROOTS[ch]), BAR, 0.5 * float(g.uniform(0.9, 1.05)), seed=SEED + 300 + bar,
                             pick_pos=0.22, t60=2.5, mute=0.4, B=1e-4, max_f=1500.0, release=0.2)
            mx.add("roots", x, t_of(bar) + float(g.normal(0, 0.01)), pan=0.05)
    for bar, vel in BELLS:
        mx.add("bell", tower_bell(n("Eb3"), vel, seed=SEED + 500 + bar, t60=8.0, dark=0.9), t_of(bar), pan=-0.2)
    on_final_loop(SK.add_bubbles, mx, rng(SEED + 40))
    for k, (song, first, low_from, low_all) in enumerate(SONG_PLAN):
        add_song(mx, song, first, low_from, low_all, (SK.SEED + 600) if k == 0 else SEED + 600 + 100 * k)
    add_song(mx, SONG_C, 17, 99, False, SEED + 1000)
    add_low(mx, [(17 + i, [(p, 3)]) for i, p in enumerate(LOW_C)], SEED + 1100, 0.5)
    add_low(mx, DEEP, SEED + 1200, 0.55)


def render(out_path: str = OUT, verbose: bool = True, stats: dict | None = None) -> dict:
    mx = LoopMixer(intro_s=0.0, loop_s=LOOP_S, preroll_s=12.0)
    G = SK.GAINS
    water = [bq_lowpass(520, 0.7), bq_lowpass(700, 0.7)]
    mx.bus("glass", G["glass"], send=0.55, process=lambda x: filt(x, [bq_highpass(180, 0.7)]))
    mx.bus("glass_low", G["glass_low"], send=0.55, process=lambda x: filt(x, [bq_lowpass(1800, 0.7)]))
    mx.bus("drone", G["drone"], send=0.25, process=lambda x: filt(x, water))
    mx.bus("pad", G["pad"], send=0.45, process=lambda x: string_body(x, cutoff=700.0))
    mx.bus("bell", G["bell"], send=0.6, process=lambda x: filt(x, [bq_lowpass(900, 0.7)]))
    mx.bus("roots", G["roots"], send=0.3, process=lambda x: filt(x, water))
    mx.bus("conduits", G["conduits"], send=0.5)
    mx.bus("bubbles", G["bubbles"], send=0.4, process=lambda x: filt(x, [bq_lowpass(1600, 0.7)]))
    build(mx)
    hall = ModFDNReverb(rt60=4.6, rt60_high=1.2, predelay=0.045, size=1.4, mod_depth=10.0, mod_rate=0.3,
                        early_level=0.2, lowcut=90.0, seed=SK.SEED % 9973)
    return V.finish(mx, "sunken_vey (final)", out_path, BPM, 3, BARS, LEAD_IN_BEATS * BEAT, TARGET_LUFS, hall, -2.0,
                    verbose, stats, quality=QUALITY)


if __name__ == "__main__":
    render(sys.argv[1] if len(sys.argv) > 1 else OUT)
