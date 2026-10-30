"""`farewell_tide`: Ch10 C3, the Kirru farewell-tide at dusk (M4-A2P-090; act2_plan.md §2 Ch10; the cue sheet,
docs/kb/plan/act2/audio/act2_cue_sheet.md): a ~90 s through-composed cue, the act's first showpiece.

Original composition for this project (SPEC §2, §9). The clutch's rising line and the Kirru palette (whistle, root-harp,
gourd, tongue-clicks, the breathing drone) come from reedhollow.py and act2_voices.py, imported, never retyped. New
here: the cue's form, and the Letting's first cell (motifs.letting(): MEL_A's first cell turned upward, the Eighth
Verse's figure) carried into the Kirru mode by its rhythm and contour. Step, step, leap, step, step back, then the leap
to the octave, held open: C#5 D#5 F#5 B5 C#6 B5 C#6. The Kirru mode (A B C# D# F#, G# only as the top of a rise) has
no E, F or G, so the cell keeps its shape and takes the mode's notes. That way the Letting is first heard here,
sung by a people who let their dead go up, long before anyone names it. No melody is taken from any existing tune.

The brief (bible §8; act2_plan Ch10): the clutch sings their dead off at dusk with a wordless rising song, then turns
its back, and the motes lift straight up into the stars; Asha can't stop looking. It must read as the opposite of
the Ch9 Ebbing (that drifts seaward; this rises). So the music only rises. Its phrases end in silence, it never comes
down to rest, and it ends on the rise held open, then the backs turned: clicks and the harp's root alone.

5/4 at 60 BPM (a bar is 5.0 s), grouped 3+2 like reedhollow; 18 bars, about 90 s, then the tail.
*  1-2   dusk: the drone on A and the harp's root; clicks
*  3-6   the rite begins: the clutch's rising line (reedhollow's CLUTCH), the harp's figure under it
*  7-10  the motes lift: the whistle sings the Letting's cell; high metallophone motes rise one by one
* 11-14  the breath flute takes the cell up a step (onto D#5) while the clutch climbs on to G#4, the top of a rise
* 15-16  the rise held open: the clutch on G#, the flute on the octave, the drone gone; no resolution
* 17-18  the backs turned: only clicks and the harp's root A; then silence

Not a loop: `music.json` gives it a beat grid (60 BPM, its downbeat) so MusicDeck's changes into and out of it land on
the beat. Vorbis q3, -16 LUFS integrated.

Render:  python3 tools/audio/render_all.py --only farewell_tide
"""
from __future__ import annotations

import importlib.util
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools", "audio"))
sys.path.insert(0, os.path.join(ROOT, "assets_src", "music"))

import numpy as np  # noqa: E402

from synth.dsp import SR, bq_highpass, bq_lowpass, filt, rng  # noqa: E402
from synth.loudness import integrated_lufs  # noqa: E402
from synth.metallophone import metallophone_note  # noqa: E402
from synth.mixer import Mixer, measure, normalize_integrated, write_ogg  # noqa: E402
from synth.reverb import ModFDNReverb  # noqa: E402
from synth.score import n  # noqa: E402
from synth.voice import hum_ensemble  # noqa: E402
from synth.winds import breath_flute  # noqa: E402


def _mod(name: str, path: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


SK = _mod("reedhollow_sketch", os.path.join(HERE, "..", "reedhollow.py"))
V = _mod("act2_voices", os.path.join(HERE, "..", "act2_voices.py"))

OUT = os.path.join(ROOT, "assets", "audio", "act2", "music", "farewell_tide.ogg")
SEED = 20261910
TARGET_LUFS = -16.0
BPM = 60.0
BEAT = 60.0 / BPM
BAR = 5 * BEAT
BARS = 18
DOWNBEAT_S = 0.5            # the file starts half a second before bar 1, so the first harp root keeps its attack
FLUTE_PRE = 0.065           # the breath flute speaks this late (Act I's measurement)
# The Letting's first cell in the Kirru mode: motifs.letting()'s rhythm (2, .5, .5, 2, .5, .5, 3 beats) and contour
LETTING_KIRRU = [("C#5", 2.0), ("D#5", 0.5), ("F#5", 0.5), ("B5", 2.0), ("C#6", 0.5), ("B5", 0.5), ("C#6", 3.0)]
LETTING_KIRRU_UP = [("D#5", 2.0), ("F#5", 0.5), ("A5", 0.5), ("C#6", 2.0), ("D#6", 0.5), ("C#6", 0.5), ("D#6", 5.0)]
CLUTCH_RISE = SK.CLUTCH + [("G#4", 10)]       # reedhollow's second rising: one step further, to the top of a rise
GAINS = {"drone": -14.0, "harp": -11.0, "clutch": 1.0, "whistle": 0.0, "flute": -2.0, "motes": -7.0, "clicks": -3.0}


def t_of(bar: int, beat: float = 0.0) -> float:
    return DOWNBEAT_S + (bar - 1) * BAR + beat * BEAT


def _clutch(line: list, seed: int, fade_out_s: float) -> np.ndarray:
    x = hum_ensemble([(n(p), b * BEAT) for p, b in line], voices=10, seed=seed, register="high", spread=0.9)
    env = np.ones(len(x))
    k = int(3.0 * SR)
    env[:k] = np.linspace(0, 1, k) ** 2
    s = max(0, len(x) - int(fade_out_s * SR))
    env[s:] *= np.linspace(1, 0, len(x) - s) ** 1.5
    return x * env[:, None]


def build(mx: Mixer) -> None:
    g = rng(SEED)
    # 1-14: the drone on A (C# and F# over it), gone before the held rise
    drone = V.periodic_drone(14 * BAR, [(n("A2"), 1.0), (n("C#3"), 0.3), (n("F#3"), 0.25)], SEED + 3, partials=5,
                             breath_s=12.0)
    k = int(4.0 * SR)
    drone[:k] *= np.linspace(0, 1, k)[:, None] ** 2
    drone[-k:] *= np.linspace(1, 0, k)[:, None] ** 2
    mx.add("drone", drone, t_of(1))
    # the harp: its root on every bar's downbeat, its rising figure under the rite (bars 3-14)
    body = V.root_harp_body(SK.SEED + 5)
    for bar in range(1, BARS + 1):
        mx.add("harp", V.root_harp(n("A2"), 0.55 * float(g.uniform(0.92, 1.04)), SEED + 100 + bar, body), t_of(bar))
        if 3 <= bar <= 14:
            ch = "B" if bar in (6, 10, 13) else "F#m" if bar in (8, 12) else "A"
            tones = [n(p) for p in SK.HARP[ch].split()]
            for eighth, idx, vel, rise in SK.HARP_PAT:
                v = vel * float(g.uniform(0.85, 1.02)) * (0.8 if bar < 7 else 1.0)
                mx.add("harp", V.root_harp(tones[idx], v, SEED + 1000 + 16 * bar + eighth, body, rise_cents=rise),
                       t_of(bar, eighth / 2) + float(g.normal(0, 0.007)), pan=-0.25 + 0.12 * idx)
    # the clutch: the rising line (3-6), then on to G#, the top of a rise, held through 15-16
    mx.add("clutch", _clutch([(p, b) for p, b in SK.CLUTCH], SEED + 11, 1.5), t_of(3) - 0.2)
    mx.add("clutch", _clutch(CLUTCH_RISE, SEED + 12, 3.0), t_of(10) - 0.2)
    # the whistle: the Letting's cell as the motes lift (bar 7), and once more (bar 9)
    for k, start in enumerate((7, 9)):
        notes, pos = [], 0.0
        for p, beats in LETTING_KIRRU:
            notes.append((pos * BEAT, beats * BEAT * 0.97, n(p), 0.72 * float(g.uniform(0.94, 1.03)), beats >= 2.0))
            pos += beats
        mx.add("whistle", V.kirru_whistle(notes, SEED + 600 + k, vib_cents=18.0), t_of(start), pan=-0.3 + 0.6 * k)
    # the breath flute takes the cell up a step (bar 11), and holds the octave open through the held rise
    pos = 0.0
    for i, (p, beats) in enumerate(LETTING_KIRRU_UP):
        dur = beats * BEAT + (2.0 * BAR if i == len(LETTING_KIRRU_UP) - 1 else 0.0)
        x = breath_flute(n(p), dur, 0.5 * float(g.uniform(0.96, 1.03)), seed=SEED + 300 + i, breath=0.25,
                         scoop_cents=25.0, vib_cents=12.0, swell=0.2 if beats >= 2 else 0.0, attack=0.14,
                         release=0.9 if i == len(LETTING_KIRRU_UP) - 1 else 0.3)
        mx.add("flute", x, t_of(11) + pos * BEAT - FLUTE_PRE, pan=0.1)
        pos += beats
    # the motes: high metallophone tones rising one by one through the mode, from the lift to the held rise
    mote_notes = ["A5", "C#6", "D#6", "F#6", "A6", "B6", "C#7", "D#7", "F#7"]
    for i in range(22):
        t = t_of(7) + i * float(g.uniform(1.6, 2.3))
        if t > t_of(16, 4):
            break
        m = n(mote_notes[min(len(mote_notes) - 1, i // 3 + int(g.integers(0, 2)))])
        mx.add("motes", metallophone_note(m, 0.35 * float(g.uniform(0.7, 1.0)), seed=SEED + 700 + i, decay=3.5,
                                          hardness=0.3, pair=False), t, pan=float(g.uniform(-0.8, 0.8)))
    # the clicks: the Kirru on the offbeats; at the end, the backs turned, more of them and nothing else
    for bar in list(range(1, 3)) + [17, 18]:
        for s in sorted(int(v) for v in g.choice([1, 3, 5, 7, 9], size=4 if bar >= 17 else 2, replace=False)):
            f = float(g.choice([1900.0, 2600.0]))
            mx.add("clicks", V.tongue_click(g, float(g.uniform(0.5, 0.9)), f), t_of(bar, s / 2) + float(g.normal(0, 0.01)),
                   pan=float(g.uniform(-0.7, 0.7)))


def render(out_path: str = OUT, verbose: bool = True, stats: dict | None = None) -> dict:
    mx = Mixer(t_of(BARS + 1) + 6.0)
    mx.bus("drone", GAINS["drone"], send=0.3, process=lambda x: filt(x, [bq_lowpass(1500, 0.7)]))
    mx.bus("harp", GAINS["harp"], send=0.35, process=lambda x: filt(x, [bq_lowpass(4500, 0.7)]))
    mx.bus("clutch", GAINS["clutch"], send=0.6)
    mx.bus("whistle", GAINS["whistle"], send=0.4, process=lambda x: filt(x, [bq_highpass(200, 0.7),
                                                                         bq_lowpass(5000, 0.7)]))
    mx.bus("flute", GAINS["flute"], send=0.45, process=lambda x: filt(x, [bq_highpass(180, 0.7)]))
    mx.bus("motes", GAINS["motes"], send=0.6, process=lambda x: filt(x, [bq_lowpass(7000, 0.7)]))
    mx.bus("clicks", GAINS["clicks"], send=0.4, process=lambda x: filt(x, [bq_lowpass(5000, 0.7)]))
    build(mx)
    dusk = ModFDNReverb(rt60=3.4, rt60_high=1.2, predelay=0.04, size=1.6, mod_depth=9.0, mod_rate=0.35,
                        early_level=0.2, lowcut=120.0, seed=SEED % 9973)
    bus_lufs = {name: integrated_lufs((b.process(b.buf) if b.process else b.buf) * 10 ** (b.gain_db / 20))
                for name, b in mx.buses.items()}
    master = mx.render(reverb=dusk, reverb_return_db=-2.0)
    env = np.abs(master).max(axis=1)
    last = int(np.nonzero(env > 10 ** (-70 / 20))[0][-1]) + int(0.2 * SR)
    master = master[: min(last, len(master))]
    k = int(2.0 * SR)
    master[-k:] *= np.linspace(1, 0, k)[:, None] ** 2
    master = normalize_integrated(master, TARGET_LUFS, ceiling_db=-2.0)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    write_ogg(out_path, master, quality=3.0)
    m = measure(master)
    if stats is not None:
        stats["bus_lufs"] = bus_lufs
    if verbose:
        print(f"farewell_tide: {m['seconds']:.2f}s  {m['integrated_lufs']:.2f} LUFS  TP {m['true_peak_dbtp']:.2f}")
    return m


if __name__ == "__main__":
    render()
