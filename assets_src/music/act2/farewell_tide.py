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

**In two parts (M4-CIN-1301, cinematics' request).** The rite is held: scene time runs only while the player holds,
and at the top note the prompt changes to "Release". The clutch turns its back when the player lets go, so the top
note can't be at a fixed time in one file:
* `farewell_tide` is the gathering: bars 1-14 as composed (the clutch climbs to F#, a step short of the top), then a
  4-bar loop (20 s) that holds for as long as the player does: the drone on A, the harp's root and a quiet figure, the
  clutch humming on F# and D# (the rise waiting), and the motes still lifting one by one;
* `farewell_tide_release` starts on the release (`@music farewell_tide_release`, its fade short): the same drone
  crossfading in under the top note (the clutch on G#, the flute on D#6, held open about 4.5 s while the clutch
  turns), then the backs turned (clicks and the harp's root alone) and silence. It never resolves down. Its drone is
  the gathering's own (the same pitches and partials), so the two join at any moment of the loop; MusicDeck lands the
  change on the gathering's next half-beat (at most 0.5 s).

5/4 at 60 BPM (a bar is 5.0 s), grouped 3+2 like reedhollow; the gathering is 14 bars (70 s) and the 4-bar loop.
*  1-2   dusk: the drone on A and the harp's root; clicks
*  3-6   the rite begins: the clutch's rising line (reedhollow's CLUTCH), the harp's figure under it
*  7-10  the motes lift: the whistle sings the Letting's cell; high metallophone motes rise one by one
* 11-14  the breath flute takes the cell up a step (onto D#5) while the clutch climbs again, to F#
* loop   held: the clutch on F# and D#, the drone, the harp's root, the motes lifting; waiting for the release
* release the top note (G#, the flute's D#6) held open; the backs turned: only clicks and the harp's root A; silence

`farewell_tide` loops (its .loop.json and `music.json` beat grid: 60 BPM); the release is a one-shot. Vorbis q3. The
gathering is -16 LUFS integrated; the release is set by its top note, 1 LU over the gathering loop (targets.py holds
the release to its measured momentary max).

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

from synth.dsp import SR, bq_highpass, bq_lowpass, db_to_lin, filt, rng  # noqa: E402
from synth.looping import LoopMixer, master_loop, write_loop_sidecar  # noqa: E402
from synth.loudness import integrated_lufs  # noqa: E402
from synth.metallophone import metallophone_note  # noqa: E402
from synth.mixer import Mixer, limit, measure, write_ogg  # noqa: E402
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
OUT_RELEASE = os.path.join(ROOT, "assets", "audio", "act2", "music", "farewell_tide_release.ogg")
SEED = 20261910
TARGET_LUFS = -16.0
BPM = 60.0
BEAT = 60.0 / BPM
BAR = 5 * BEAT
INTRO_BARS = 14
LOOP_BARS = 4
LOOP_S = LOOP_BARS * BAR
RELEASE_S = 18.0
TOP_HOLD_S = 4.5             # the top note held while the clutch turns (T04, about 4 s)
LEAD_S = BEAT / 4            # the loop starts a sixteenth before its downbeat, so no attack sits on the seam
TOP_OVER_LU = 1.0            # the release's top note (its first TOP_HOLD_S) sits this far over the gathering loop
DRONE = [(n("A2"), 1.0), (n("C#3"), 0.3), (n("F#3"), 0.25)]
DOWNBEAT_S = 0.5            # the file starts half a second before bar 1, so the first harp root keeps its attack
FLUTE_PRE = 0.065           # the breath flute speaks this late (Act I's measurement)
# The Letting's first cell in the Kirru mode: motifs.letting()'s rhythm (2, .5, .5, 2, .5, .5, 3 beats) and contour
LETTING_KIRRU = [("C#5", 2.0), ("D#5", 0.5), ("F#5", 0.5), ("B5", 2.0), ("C#6", 0.5), ("B5", 0.5), ("C#6", 3.0)]
LETTING_KIRRU_UP = [("D#5", 2.0), ("F#5", 0.5), ("A5", 0.5), ("C#6", 2.0), ("D#6", 0.5), ("C#6", 0.5), ("D#6", 5.0)]
HOLD = ("F#4", "D#4")                         # the loop's hum: the rise waiting on F# and D#, a step under the top
TOP = ("G#4", "D#6")                          # the clutch's top of a rise and the flute's octave, on the release
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


def _drone(sec: float, seed: int) -> np.ndarray:
    return V.periodic_drone(sec, DRONE, seed, partials=5, breath_s=12.0)


def build(mx: LoopMixer) -> None:
    g = rng(SEED)
    body = V.root_harp_body(SK.SEED + 5)
    # the drone on A runs from bar 1 through the loop
    intro_drone = _drone(INTRO_BARS * BAR, SEED + 3)
    k = int(4.0 * SR)
    intro_drone[:k] *= np.linspace(0, 1, k)[:, None] ** 2
    mx.add("drone", intro_drone, t_of(1), part="intro")
    mx.add("drone", _drone(LOOP_S, SEED + 4), LEAD_S - DOWNBEAT_S)
    # the harp: its root on every bar's downbeat, its rising figure under the rite (bars 3-14), quieter in the loop
    for bar in range(1, INTRO_BARS + LOOP_BARS + 1):
        loop = bar > INTRO_BARS
        at = (bar - INTRO_BARS - 1) * BAR + LEAD_S if loop else t_of(bar)
        part = "loop" if loop else "intro"
        root_vel = 0.4 if loop else 0.55
        mx.add("harp", V.root_harp(n("A2"), root_vel * float(g.uniform(0.92, 1.04)), SEED + 100 + bar, body), at,
               part=part)
        if 3 <= bar:
            ch = "B" if bar in (6, 10, 13) else "F#m" if bar in (8, 12, 16) else "A"
            tones = [n(p) for p in SK.HARP[ch].split()]
            for eighth, idx, vel, rise in SK.HARP_PAT:
                v = vel * float(g.uniform(0.85, 1.02)) * (0.8 if bar < 7 else 0.4 if loop else 1.0)
                mx.add("harp", V.root_harp(tones[idx], v, SEED + 1000 + 16 * bar + eighth, body, rise_cents=rise),
                       at + eighth / 2 * BEAT + float(g.normal(0, 0.007)), pan=-0.25 + 0.12 * idx, part=part)
    # the clutch: the rising line (3-6), and again at 10, a step short of the top; then the loop's held hum
    mx.add("clutch", _clutch([(p, b) for p, b in SK.CLUTCH], SEED + 11, 1.5), t_of(3) - 0.2, part="intro")
    mx.add("clutch", _clutch([(p, b) for p, b in SK.CLUTCH], SEED + 12, 4.0), t_of(10) - 0.2, part="intro")
    for k, p in enumerate(HOLD):                    # a steady chord: the clutch's breaths never fall together
        hold = hum_ensemble([(n(p), LOOP_S)], voices=8, seed=SEED + 13 + k, register="high", spread=0.9, loop=True)
        mx.add("clutch", hold * (0.8 if k else 1.0), LEAD_S)
    # the whistle: the Letting's cell as the motes lift (bar 7), and once more (bar 9)
    for k, start in enumerate((7, 9)):
        notes, pos = [], 0.0
        for p, beats in LETTING_KIRRU:
            notes.append((pos * BEAT, beats * BEAT * 0.97, n(p), 0.72 * float(g.uniform(0.94, 1.03)), beats >= 2.0))
            pos += beats
        mx.add("whistle", V.kirru_whistle(notes, SEED + 600 + k, vib_cents=18.0), t_of(start), pan=-0.3 + 0.6 * k,
               part="intro")
    # the breath flute takes the cell up a step (bar 11); its last note waits for the release
    pos = 0.0
    for i, (p, beats) in enumerate(LETTING_KIRRU_UP[:-1]):
        x = breath_flute(n(p), beats * BEAT, 0.5 * float(g.uniform(0.96, 1.03)), seed=SEED + 300 + i, breath=0.25,
                         scoop_cents=25.0, vib_cents=12.0, swell=0.2 if beats >= 2 else 0.0, attack=0.14, release=0.3)
        mx.add("flute", x, t_of(11) + pos * BEAT - FLUTE_PRE, pan=0.1, part="intro")
        pos += beats
    # the motes: high tones rising one by one through the mode, from the lift (bar 7) and on through the loop
    mote_notes = ["A5", "C#6", "D#6", "F#6", "A6", "B6", "C#7", "D#7", "F#7"]
    t, i = t_of(7), 0
    while t < t_of(INTRO_BARS + 1):
        m = n(mote_notes[min(len(mote_notes) - 1, i // 3 + int(g.integers(0, 2)))])
        mx.add("motes", metallophone_note(m, 0.35 * float(g.uniform(0.7, 1.0)), seed=SEED + 700 + i, decay=3.5,
                                          hardness=0.3, pair=False), t, pan=float(g.uniform(-0.8, 0.8)), part="intro")
        t += float(g.uniform(1.6, 2.3))
        i += 1
    t = 0.7 + LEAD_S
    while t < LOOP_S - 1.0:
        m = n(mote_notes[3 + int(g.integers(0, 6))])
        mx.add("motes", metallophone_note(m, 0.3 * float(g.uniform(0.7, 1.0)), seed=SEED + 760 + i, decay=3.5,
                                          hardness=0.3, pair=False), t, pan=float(g.uniform(-0.8, 0.8)))
        t += float(g.uniform(2.0, 3.0))
        i += 1
    # the clicks: the Kirru on the offbeats at dusk
    for bar in (1, 2):
        for s in sorted(int(v) for v in g.choice([1, 3, 5, 7, 9], size=2, replace=False)):
            f = float(g.choice([1900.0, 2600.0]))
            mx.add("clicks", V.tongue_click(g, float(g.uniform(0.5, 0.9)), f), t_of(bar, s / 2) + float(g.normal(0, 0.01)),
                   pan=float(g.uniform(-0.7, 0.7)), part="intro")


def build_release(mx: Mixer) -> None:
    g = rng(SEED + 5000)
    body = V.root_harp_body(SK.SEED + 5)
    drone = _drone(TOP_HOLD_S + 3.0, SEED + 4)          # the gathering's own drone, letting go under the top note
    k = int(3.0 * SR)
    drone[-k:] *= np.linspace(1, 0, k)[:, None] ** 2
    mx.add("drone", drone, 0.0)
    top = hum_ensemble([(n(TOP[0]), TOP_HOLD_S + 1.0)], voices=10, seed=SEED + 5010, register="high", spread=0.9)
    env = np.ones(len(top))
    a = int(0.4 * SR)
    env[:a] = np.linspace(0, 1, a) ** 1.5
    r0 = int((TOP_HOLD_S - 0.5) * SR)
    env[r0:] *= np.linspace(1, 0, len(top) - r0) ** 1.5
    mx.add("clutch", top * env[:, None], 0.05)
    mx.add("flute", breath_flute(n(TOP[1]), TOP_HOLD_S, 0.5, seed=SEED + 5020, breath=0.25, scoop_cents=25.0,
                                 vib_cents=12.0, swell=0.2, attack=0.3, release=0.9), 0.1 - FLUTE_PRE, pan=0.1)
    for i, m in enumerate(("C#7", "D#7", "F#7")):                 # the last motes go up and are gone
        mx.add("motes", metallophone_note(n(m), 0.3, seed=SEED + 5030 + i, decay=3.0, hardness=0.3, pair=False),
               0.6 + 1.1 * i, pan=-0.5 + 0.5 * i)
    # the backs turned: only clicks and the harp's root A
    for k2, at in enumerate((TOP_HOLD_S + 0.5, TOP_HOLD_S + 0.5 + BAR)):
        mx.add("harp", V.root_harp(n("A2"), 0.5 - 0.1 * k2, SEED + 5040 + k2, body), at)
        for s in sorted(int(v) for v in g.choice([1, 3, 5, 7, 9], size=4, replace=False)):
            f = float(g.choice([1900.0, 2600.0]))
            mx.add("clicks", V.tongue_click(g, float(g.uniform(0.5, 0.9)), f), at + s / 2 * BEAT + float(g.normal(0, 0.01)),
                   pan=float(g.uniform(-0.7, 0.7)))


def _buses(mx) -> None:
    mx.bus("drone", GAINS["drone"], send=0.3, process=lambda x: filt(x, [bq_lowpass(1500, 0.7)]))
    mx.bus("harp", GAINS["harp"], send=0.35, process=lambda x: filt(x, [bq_lowpass(4500, 0.7)]))
    mx.bus("clutch", GAINS["clutch"], send=0.6)
    mx.bus("whistle", GAINS["whistle"], send=0.4, process=lambda x: filt(x, [bq_highpass(200, 0.7),
                                                                         bq_lowpass(5000, 0.7)]))
    mx.bus("flute", GAINS["flute"], send=0.45, process=lambda x: filt(x, [bq_highpass(180, 0.7)]))
    mx.bus("motes", GAINS["motes"], send=0.6, process=lambda x: filt(x, [bq_lowpass(7000, 0.7)]))
    mx.bus("clicks", GAINS["clicks"], send=0.4, process=lambda x: filt(x, [bq_lowpass(5000, 0.7)]))


def _dusk() -> ModFDNReverb:
    return ModFDNReverb(rt60=3.4, rt60_high=1.2, predelay=0.04, size=1.6, mod_depth=9.0, mod_rate=0.35,
                        early_level=0.2, lowcut=120.0, seed=SEED % 9973)


def render(out_path: str = OUT, verbose: bool = True, stats: dict | None = None) -> dict:
    mx = LoopMixer(intro_s=t_of(INTRO_BARS + 1) - LEAD_S, loop_s=LOOP_S, intro_tail_s=6.0, preroll_s=8.0)
    _buses(mx)
    build(mx)
    intro, loop = mx.render(reverb=_dusk(), reverb_return_db=-2.0)
    intro, loop = master_loop(intro, loop, TARGET_LUFS, ceiling_db=-2.0)
    y = np.concatenate([intro, loop])
    S, L = len(intro), len(loop)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    write_ogg(out_path, y, quality=3.0, tags={"LOOPSTART": str(S), "LOOPLENGTH": str(L)})
    write_loop_sidecar(os.path.splitext(out_path)[0] + ".loop.json", SR, S, L, BPM, 5,
                       extra={"intro_bars": INTRO_BARS, "loop_bars": LOOP_BARS, "downbeat_offset_s": DOWNBEAT_S})
    m = measure(y)
    loop_lufs = integrated_lufs(loop)
    # the release: its top note set 1 LU over the gathering loop, so letting go lifts, wherever in the loop it comes
    rx = Mixer(RELEASE_S + 6.0)
    _buses(rx)
    build_release(rx)
    rel = rx.render(reverb=_dusk(), reverb_return_db=-2.0)
    env = np.abs(rel).max(axis=1)
    last = int(np.nonzero(env > 10 ** (-70 / 20))[0][-1]) + int(0.2 * SR)
    rel = rel[: min(last, len(rel))]
    k = int(2.0 * SR)
    rel[-k:] *= np.linspace(1, 0, k)[:, None] ** 2
    rel = rel * db_to_lin(loop_lufs + TOP_OVER_LU - integrated_lufs(rel[: int(TOP_HOLD_S * SR)]))
    rel = limit(rel, -2.0)
    write_ogg(os.path.join(os.path.dirname(out_path), os.path.basename(OUT_RELEASE)), rel, quality=3.0)
    mr = measure(rel)
    if stats is not None:
        stats["loop_lufs"] = loop_lufs
        stats["release"] = mr
    if verbose:
        print(f"farewell_tide: {m['seconds']:.2f}s  {m['integrated_lufs']:.2f} LUFS  TP {m['true_peak_dbtp']:.2f}  "
              f"loop {loop_lufs:.2f} LUFS")
        print(f"farewell_tide_release: {mr['seconds']:.2f}s  Mmax {mr['momentary_max_lufs']:.2f}  "
              f"TP {mr['true_peak_dbtp']:.2f}")
    return m


if __name__ == "__main__":
    render()
