"""`kesh_first_voice`: Ch21 H03, Kesh's fight, the first Vowbound called out of the sleeve one last time (M5-A3P-1951;
act3_ending.md H03; docs/kb/audio/lamptongue.md; ADR 0208). A loop of 60 s.

Original composition for this project (SPEC §2). Its tune is the game's own and is loaded, never retyped: the Hush's
first cell (hush_theme_v2.py MEL_A, E D C | A G A), the cell every verse is built on. Each verse's first line is sung
to it, moved up the A minor scale one step per verse, in Lamptongue from act3/lamptongue.py. The ostinato, the
harmony and the arrangement were written for this cue.

The brief (act3_ending.md H03): "*Music:* `kesh_first_voice` (boss, all seven verse phrases in turn, one per element
phase), then `release_sting`." Kesh: "Make them strong, then. All of you. Hit me as hard as you can." She has stayed
a thousand years, and she is glad of the fight. Her Swell, *The Seven*, sings all seven verses at once; this is the
seven in turn. So:
* a driving ostinato in 3+3+2 (frame drums, the big drum on each bar's first stroke, low strings on the root);
* seven sections of four bars, one verse each (lamptongue.md §2's verses 1–7, Ilun's to her own). The stones'
  choir, men and women, sings the verse's first line over two bars, and the metallophone answers it over the next
  two. Each section's harmony and its line sit one step higher in A minor than the last (A, B, C, D, E, F, G),
  so the seven climb;
* the seventh, *Una kor, una kor* (her own), is the fullest: every layer, the choir doubled, the line at its top;
* the loop's return drops back to Ilun's verse on A.
Her cycle (combat's BattleCycle) changes element every turn she acts, faster than a sung line, so the verses run in
their own time rather than switching on each turn. A hook to her cycle would need a signal from combat (see the task).

A minor, 4/4 at 112 BPM (a bar 2.14 s), 28 bars.

Render:  python3 assets_src/music/act3/kesh_first_voice.py   (or tools/audio/render_all.py --only kesh_first_voice)
"""
from __future__ import annotations

import importlib.util
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
MUSIC = os.path.dirname(HERE)
ROOT = os.path.abspath(os.path.join(MUSIC, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools", "audio"))
sys.path.insert(0, MUSIC)
sys.path.insert(0, HERE)

import numpy as np  # noqa: E402

import lamptongue as LT  # noqa: E402
from motifs import LETTING_FROM, _degree, _note  # noqa: E402
from synth.drums import big_drum, frame_drum  # noqa: E402
from synth.dsp import SR, bq_highpass, bq_lowpass, filt, rng  # noqa: E402
from synth.looping import LoopMixer, master_loop, write_loop_sidecar  # noqa: E402
from synth.metallophone import metallophone_note  # noqa: E402
from synth.mixer import measure, write_ogg  # noqa: E402
from synth.pad import pad_chord, string_body  # noqa: E402
from synth.reverb import ModFDNReverb  # noqa: E402
from synth.score import n  # noqa: E402
from synth.voice import sing  # noqa: E402


def _load(name: str):
    spec = importlib.util.spec_from_file_location(name, os.path.join(MUSIC, f"{name}.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


HUSH = _load("hush_theme_v2")
OUT = os.path.join(ROOT, "assets", "audio", "act3", "music", "kesh_first_voice.ogg")
SEED = 20261034
TARGET_LUFS = -16.0
BPM = 112.0
BEAT = 60.0 / BPM
BAR = 4 * BEAT
SECTION_BARS = 4
VERSES = 7
LOOP_S = VERSES * SECTION_BARS * BAR
# The loop's seam sits half a beat before the first downbeat (music.json downbeat_offset_s), so the return from her
# fullest verse to Ilun's is a downbeat inside the loop, not a pile of onsets on the seam itself.
OFFSET_S = BEAT * 0.5
ROOTS = ["A", "B", "C", "D", "E", "F", "G"]          # each section's root, a step up the scale
# 3+3+2 in eighths: the strokes of a bar, (eighth, stroke, velocity)
OSTINATO = [(0, "dum", 0.9), (3, "dum", 0.7), (6, "tek", 0.6), (2, "tek", 0.35), (5, "tek", 0.35), (7, "tek", 0.4)]
# From measured bus loudness: the choir at L, the frame drums L-3, the big drum L-4, the low strings and the
# metallophone L-6, the pad L-9.
GAINS = {"choir": 0.0, "drums": 12.4, "big": 12.8, "low": 21.4, "pad": 16.7, "metal": 9.3}


def cell() -> list[tuple[str, float]]:
    return [(p, float(b)) for p, b, *_ in HUSH.MEL_A[:LETTING_FROM]]


def verse_line(verse: int) -> list[tuple[float, float, str, str]]:
    """The verse's first line to the Hush's cell moved up `verse - 1` steps: [(midi, beats, vowel, coda)] over two
    bars (8 beats). A line with more syllables than the cell has notes repeats the cell's tail; the last is held."""
    syl = LT.line_syllables(LT.VERSES[verse][0])
    c = cell()
    shift = verse - 1
    pitches = [_note(_degree(p) + shift) for p, _ in c]
    while len(pitches) < len(syl):
        pitches += pitches[-2:]
    pitches = pitches[: len(syl)]
    beats = [b for _, b in c]
    while len(beats) < len(syl):
        beats += [0.5, 0.5]
    beats = beats[: len(syl)]
    beats[-1] += 8.0 - sum(beats)
    return [(float(n(p)), b, v, coda) for p, b, (v, coda) in zip(pitches, beats, syl)]


def build(mx, g) -> None:
    for s in range(VERSES):
        verse = s + 1
        t0 = OFFSET_S + s * SECTION_BARS * BAR
        root = ROOTS[s]
        full = verse == VERSES
        r2, r3 = n(f"{root}2"), n(f"{root}3")
        fifth = _note(_degree(f"{root}3") + 4)
        # the pad and the low strings on the section's root
        mx.add("pad", pad_chord([r3, n(fifth), r3 + 12], SECTION_BARS * BAR, vel=0.45 + 0.05 * full, seed=SEED + s,
                                attack=0.4, release=1.0), t0)
        for b in range(SECTION_BARS):
            tb = t0 + b * BAR
            for e, stroke, v in OSTINATO:
                mx.add("drums", frame_drum(stroke, v * (1.1 if full else 1.0), variant=(b + e) % 4,
                                           seed=SEED + 100 * s + 10 * b + e), tb + e * BEAT / 2,
                       pan=-0.2 if stroke == "dum" else 0.25)
            mx.add("big", big_drum(0.6 + 0.2 * full, variant=b % 3, seed=SEED + 300 + 10 * s + b), tb)
            for e in (0, 3, 6):                                           # the low strings on the 3+3+2
                mx.add("low", pad_chord([r2], BEAT * 1.3, vel=0.55, seed=SEED + 400 + 30 * s + 3 * b + e // 3,
                                        attack=0.02, release=0.25, voices=2), tb + e * BEAT / 2)
        # the stones' choir sings the verse's first line over bars 1-2
        t = t0
        line = verse_line(verse)
        singers = 6 if full else 4
        for i, (m, beats, v, coda) in enumerate(line):
            d = beats * BEAT * 0.95
            ph = LT.choir_phonemes([(v, coda)], [d])
            for c in range(singers):
                octave = -12 if c % 2 == 0 else 0                        # the men an octave under the women
                y = sing(ph, [(m + octave + float(g.normal(0, 0.05)), d)], vel=0.65, seed=SEED + 1000 + 50 * s + 7 * i + c,
                         scale=1.0 if octave else 1.17, tilt=1.6, breath=0.05, vib_cents=10.0, vib_rate=5.2,
                         release=0.25)
                mx.add("choir", y, t + 0.015 * c, pan=float(np.linspace(-0.5, 0.5, singers)[c]))
            t += beats * BEAT
        # the metallophone answers it over bars 3-4, an octave up, quicker
        t = t0 + 2 * BAR
        for i, (m, beats, _, _) in enumerate(line):
            mx.add("metal", metallophone_note(m + 12, vel=0.5, seed=SEED + 2000 + 20 * s + i), t, pan=0.3)
            t += min(beats, 2.0) * BEAT * 0.75


def render(out_path: str = OUT, verbose: bool = True, stats: dict | None = None) -> dict:
    g = rng(SEED)
    mx = LoopMixer(intro_s=0.0, loop_s=LOOP_S, preroll_s=6.0)
    G = GAINS
    mx.bus("choir", G["choir"], send=0.4, process=lambda x: filt(x, [bq_highpass(90, 0.7), bq_lowpass(6000, 0.7)]))
    mx.bus("drums", G["drums"], send=0.2, process=lambda x: filt(x, [bq_highpass(40, 0.7)]))
    mx.bus("big", G["big"], send=0.25, process=lambda x: filt(x, [bq_highpass(30, 0.7), bq_lowpass(2500, 0.7)]))
    mx.bus("low", G["low"], send=0.2, process=lambda x: string_body(x, cutoff=900.0))
    mx.bus("pad", G["pad"], send=0.45, process=lambda x: string_body(x, cutoff=2600.0))
    mx.bus("metal", G["metal"], send=0.4, process=lambda x: filt(x, [bq_highpass(200, 0.7)]))
    build(mx, g)
    hall = ModFDNReverb(rt60=2.6, rt60_high=1.2, predelay=0.025, size=1.1, mod_depth=7.0, mod_rate=0.5,
                        early_level=0.25, lowcut=100.0, width=0.75, seed=SEED % 9973)
    _, loop = mx.render(reverb=hall, reverb_return_db=-3.0)
    _, loop = master_loop(np.zeros((0, 2)), loop, TARGET_LUFS, ceiling_db=-2.0, report={})
    L = len(loop)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    write_ogg(out_path, loop, quality=3.0, tags={"LOOPSTART": "0", "LOOPLENGTH": str(L)})
    write_loop_sidecar(os.path.splitext(out_path)[0] + ".loop.json", SR, 0, L, BPM, 4)
    m = measure(loop)
    if stats is not None:
        stats["bus_lufs"] = dict(mx.bus_lufs)
    if verbose:
        print(f"kesh_first_voice: {m['seconds']:.2f}s  {m['integrated_lufs']:.2f} LUFS  TP {m['true_peak_dbtp']:.2f}")
    return m


if __name__ == "__main__":
    render()
