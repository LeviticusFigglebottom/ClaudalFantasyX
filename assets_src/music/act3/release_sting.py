"""`release_sting`: a Vowbound let go (M5-A3P-1950; act3_ch20.md, act3_ending.md H03; ADR 0208). About 10 s, not
looped, started with `fade=0.0` on the release line.

Original composition for this project (SPEC §2). The tune is the game's own, loaded and never retyped: motifs.py
`letting()`, the Hush's first cell turned upward with its close on E6. Everything else was written for this cue.

It plays seven times: Ilun, Kahre, Virel, Nhoa, Hesk and Ethren in Ch20, then Kesh in Ch21, "the last and longest"
(act3_ending.md H03). Each time a friend leaves Asha's sleeve and its motes spiral up (`glimmer_lift spiral_up`, the
scene's 6–8 s wait), so the sting is the Letting stated once, without a voice, rising with the motes:
* 0 s: a soft low C under the release line, and the strings open from A minor to C major (A3 C4 E4 to G3 C4 E4)
  over 2 s: what was held lets go;
* 0.6 s: the Letting's cell climbs on the metallophone, light and unhurried (E5 F5 G5 | B5 C6 B5), each note leaving
  a glass harmonic a fifth above, sounding on as the motes do;
* 5 s: the close, E6, on glass and metallophone together, left to ring; the strings thin under it to the C and E;
* 7–10 s: nothing more is played; the hall carries the last E up and away.
It never cadences: no V–I and no drum. Being let go isn't a victory.

C major (from A minor), the Letting's own rhythm at 54 BPM (the_letting.py's tempo: a beat 1.11 s).

Render:  python3 assets_src/music/act3/release_sting.py   (or tools/audio/render_all.py --only release_sting)
"""
from __future__ import annotations

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
MUSIC = os.path.dirname(HERE)
ROOT = os.path.abspath(os.path.join(MUSIC, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools", "audio"))
sys.path.insert(0, MUSIC)
sys.path.insert(0, HERE)

import numpy as np  # noqa: E402

from motifs import letting  # noqa: E402
from synth.dsp import SR, bq_highpass, bq_lowpass, filt, rng  # noqa: E402
from synth.metallophone import metallophone_note  # noqa: E402
from synth.mixer import Mixer, measure, normalize_momentary, write_ogg  # noqa: E402
from synth.pad import pad_chord, string_body  # noqa: E402
from synth.reverb import ModFDNReverb  # noqa: E402
from synth.score import n  # noqa: E402
from levels import bus_levels  # noqa: E402
from the_letting import BPM, glass  # noqa: E402

OUT = os.path.join(ROOT, "assets", "audio", "act3", "music", "release_sting.ogg")
SEED = 20261031
TARGET_LUFS = -18.0          # momentary max: a sting under a spoken line, never over it (targets.py)
BEAT = 0.85 * 60.0 / BPM     # a little quicker than the sung verse: a statement, not a song
CELL_AT = 0.6
LENGTH = 10.5
# From measured bus loudness (levels.bus_levels): the metallophone's cell at L, the glass L-4, the strings L-6, the low
# strings L-9.
GAINS = {"metal": 0.0, "glass": -12.9, "strings": 4.4, "low": 5.8}


def render(out_path: str = OUT, verbose: bool = True, stats: dict | None = None) -> dict:
    g = rng(SEED)
    mx = Mixer(LENGTH)
    mx.bus("metal", GAINS["metal"], send=0.45, process=lambda x: filt(x, [bq_highpass(200, 0.7)]))
    mx.bus("glass", GAINS["glass"], send=0.7)
    mx.bus("strings", GAINS["strings"], send=0.5, process=lambda x: string_body(x, cutoff=2400.0))
    mx.bus("low", GAINS["low"], send=0.3, process=lambda x: string_body(x, cutoff=600.0))
    cell = letting()
    t = CELL_AT
    for i, (p, beats) in enumerate(cell):
        m = float(n(p))
        last = i == len(cell) - 1
        mx.add("metal", metallophone_note(m, vel=0.55 if not last else 0.62, seed=SEED + i), t + float(g.normal(0, 0.008)),
               pan=float(np.clip((m - 76) / 30.0, -0.3, 0.3)))
        ring = 4.0 if last else max(1.0, beats * BEAT * 1.5)
        mx.add("glass", glass(m + (0 if last else 7), ring, 0.55 if not last else 0.7, SEED + 50 + i), t + 0.05,
               pan=0.25 - 0.08 * i)
        t += beats * BEAT if not last else 0.0
    close_at = t
    # the strings let go: A minor opens to C major, then thin under the close to C and E
    mx.add("strings", pad_chord([n("A3"), n("C4"), n("E4")], 1.6, vel=0.4, seed=SEED + 100, attack=0.4, release=1.2), 0.0)
    mx.add("strings", pad_chord([n("G3"), n("C4"), n("E4")], close_at - 1.4, vel=0.42, seed=SEED + 101, attack=1.2,
                                release=1.5), 1.4)
    mx.add("strings", pad_chord([n("C4"), n("E4")], 3.5, vel=0.36, seed=SEED + 102, attack=0.8, release=2.5), close_at)
    mx.add("low", pad_chord([n("C2"), n("C3")], close_at + 1.0, vel=0.4, seed=SEED + 103, attack=0.6, release=2.5,
                            voices=2), 0.0)
    hall = ModFDNReverb(rt60=4.2, rt60_high=1.8, predelay=0.03, size=1.3, mod_depth=9.0, mod_rate=0.4,
                        early_level=0.22, lowcut=100.0, width=0.75, seed=SEED % 9973)
    y = mx.render(reverb=hall, reverb_return_db=-1.5)
    fade = int(1.2 * SR)
    y[-fade:] *= np.linspace(1.0, 0.0, fade)[:, None]
    y = normalize_momentary(y, TARGET_LUFS, ceiling_db=-3.0)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    write_ogg(out_path, y, quality=3.0)
    m = measure(y)
    if stats is not None:
        stats["bus_lufs"] = bus_levels(mx)
        stats["close_at"] = close_at
    if verbose:
        print(f"release_sting: {m['seconds']:.2f}s  M max {m['momentary_max_lufs']:.2f}  TP {m['true_peak_dbtp']:.2f}"
              f"  close at {close_at:.2f}s")
    return m


if __name__ == "__main__":
    render()
