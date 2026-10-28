"""`iskarra_spire`: Ch19 "Iskarra", the Lamp Spire, a dungeon climb to shut down the founders' anchor-engine
(M3-AUD-856; act3_plan.md §2, act_outline Ch19, docs/kb/art/environments/iskarra.md §3): a 129.2 s seamless loop.

Original composition for this project (SPEC §2, §9). Original-material check: the only tune not written here is the
Order's hum (motifs.py ORDER_HUM), imported and never retyped; the engine sounds it, stretched to a bar a beat, as
the drone under everything. The escapement's tick is the Lamp Engine's own (act2/lamp_engine.py `tick`, loaded from
it, not copied) and the stroke is Lowlight's (act2_voices.engine_thud), so the founders' machine is that machine's
family. Everything else was written for this cue and shares no phrase with the game's other themes or any melody we
know: the climb figure (four lamps a bar, rising through each chord), the chord plan, and the glass's lamp line,
which climbs a step every four bars (B5 C6 D6 E6, then G6 over it). The style evoked is a slow clockwork under held
glass and an organ-like hum; nothing is quoted.

The brief: Iskarra's Lamp Spire, 112 m over the drowned city, climbed to its crown, where the founders' anchor-engine
stands: a salt-glass column round a bound core, caged in three bronze rings. A bound-light machine: steady glass
tones (bound light never pulses), a lamp-engine's tick, and under it the Order's hum as a drone the founders' faith
left behind. Rising tension for a climb, not a fight: no drums, no bass line; the tension is the ticking thickening,
the hum lifting a fourth, the glass climbing and the climb figure moving up an octave.

Bound light never pulses, so every held tone in this cue is steady: no vibrato, no tremolo, no detuned twins, no
swell once a tone is in. The glass and the hum are **tuned just to E** (B a 3/2, C 8/5, D 9/5, G 6/5, A 4/3, F# 9/8
over E) so that no two held tones beat against each other; the loop-long ones are snapped to whole cycles per loop.

E minor (aeolian; the top section's B chord takes D#). 4/4 at 104 BPM (twice motifs.ORDER_HUM_BPM, so the hum's
beat is one bar here; a bar is 2.308 s), 56 bars.

Ensemble (all synthesized; no samples):
* the engine's hum: an organ-like tone of odd-heavy harmonics (conduit_hum's spectrum, steady), a pedal E2-B2 held
  through the whole loop, and ORDER_HUM an octave down, one beat to a bar (A: on G; A': a fourth up, on C);
* the escapement: the Lamp Engine's brass tick and tock, in quarters, then eighths, then with the off-sixteenths;
* the stroke: Lowlight's engine stroke on bar downbeats, then on 1 and 3, then softly on every beat at the top;
* the climb: a hand-damped metallophone, four lamps a bar rising through the chord (E4 octave, then E5 in A');
* the glass: steady bound tones, E5 always, B5 from bar 13, and the lamp line in A' and at the top;
* low bowed strings doubling the hum in A' and holding B at the top; a low kettle gong at each section's start;
* the open air at the crown: a thin high wind (act2_voices.wind).

Form (bars):
*  1-4   the engine: the pedal hum, the tick in quarters, the stroke on 1 and 3, the glass's E5
*  5-22  A: ORDER_HUM in the hum (G2 ...), the tick in eighths, the stroke on each downbeat, the climb figure
         (Em Em C C D D Em Em C C Am Am Bm Bm C C Em Em), the glass adds B5 at 13
* 23-26  the landing: the climb stops, the tick back in quarters, the hum holds E
* 27-44  A': ORDER_HUM a fourth up (C3 ...) doubled by the low strings, the climb an octave up, the stroke on 1
         and 3, the off-sixteenths from 35, the glass's lamp line B5 | C6 | D6 | E6
* 45-52  the top: B B C C B B B B; the hum and the strings on B, the stroke on every beat, the glass holds E6 and G6
* 53-56  the turn: everything falls away to the engine as it was in bar 1 (the pedal, the quarters, E5)

Loop: LOOPSTART = 0 and LOOPLENGTH = the whole file. The file starts half an eighth before bar 1's downbeat (the
sidecar's `downbeat_offset_s`), so the wrap seam falls between two quarter ticks.

Render:  python3 assets_src/music/act3/iskarra_spire.py   (or tools/audio/render_all.py --act3 --only
act3/iskarra_spire)
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

import numpy as np  # noqa: E402

from motifs import ORDER_HUM, ORDER_HUM_BPM  # noqa: E402
from synth.dsp import SR, bq_highpass, bq_lowpass, filt, midi_to_hz, rng  # noqa: E402
from synth.gongs import kettle_gong  # noqa: E402
from synth.looping import LoopMixer  # noqa: E402
from synth.metallophone import metallophone_note  # noqa: E402
from synth.pad import pad_chord, string_body  # noqa: E402
from synth.reverb import ModFDNReverb  # noqa: E402
from synth.score import n  # noqa: E402


def _mod(name: str, path: str):
    spec = importlib.util.spec_from_file_location(f"_act3_{name}", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


V = _mod("act2_voices", os.path.join(MUSIC, "act2_voices.py"))            # engine_thud, wind, snap, finish()
LE = _mod("lamp_engine", os.path.join(MUSIC, "act2", "lamp_engine.py"))    # the Lamp Engine's escapement tick

OUT = os.path.join(ROOT, "assets", "audio", "music", "act3", "iskarra_spire.ogg")
SEED = 20261857
TARGET_LUFS = -16.0
QUALITY = 3.0
BPM = 2.0 * ORDER_HUM_BPM            # one hum beat is one bar
BEAT = 60.0 / BPM
E8 = BEAT / 2
BAR_BEATS = 4
BAR = BAR_BEATS * BEAT
BARS = 56
LOOP_S = BARS * BAR
LEAD_IN_E = 0.5
HUM_SHIFT = -12                      # ORDER_HUM an octave down in the engine
HUM_BARS = {5: 0, 27: 5}             # where the hum starts, and its transposition (A': a fourth up)
SECTION = ["I"] * 4 + ["A"] * 18 + ["L"] * 4 + ["A2"] * 18 + ["T"] * 8 + ["R"] * 4
## the climb's chord, bar by bar (None: no climb figure); A and A' share the plan
_CLIMB_A = ["Em", "Em", "C", "C", "D", "D", "Em", "Em", "C", "C", "Am", "Am", "Bm", "Bm", "C", "C", "Em", "Em"]
CHORDS = [None] * 4 + _CLIMB_A + [None] * 4 + _CLIMB_A + ["B", "B", "C", "C", "B", "B", "B", "B"] + [None] * 4
CHORD_TONES = {"Em": ("E", 0, 3, 7), "C": ("C", 0, 4, 7), "D": ("D", 0, 4, 7), "Am": ("A", 0, 3, 7),
               "Bm": ("B", 0, 3, 7), "B": ("B", 0, 4, 7)}
## just ratios over E, by semitones above E (so no two held tones beat)
JI = {0: 1.0, 2: 9 / 8, 3: 6 / 5, 5: 4 / 3, 7: 3 / 2, 8: 8 / 5, 10: 9 / 5, 11: 15 / 8}
E_REF = 40                           # E2
## the glass's lamp line: (first bar, last bar, pitch); E5 sounds through the whole loop
GLASS = [(13, 52, "B5"), (27, 30, "B5"), (31, 34, "C6"), (35, 38, "D6"), (39, 52, "E6"), (45, 52, "G6")]
GONGS = {5: "E2", 27: "E2", 45: "B1"}


def t_of(bar: int, e: float = 1.0) -> float:
    """Seconds from the loop start to eighth `e` (1-based) of `bar`."""
    return (bar - 1) * BAR + (e - 1) * E8


def ji_hz(m: float) -> float:
    """The just-tuned frequency of MIDI note m over E (equal-tempered for a step JI does not name)."""
    k = int(round(m)) - E_REF
    pc = k % 12
    if pc not in JI:
        return midi_to_hz(m)
    return midi_to_hz(E_REF) * 2.0 ** (k // 12) * JI[pc]


def organ_partials(f0: float) -> list[tuple[int, float]]:
    """The engine's hum spectrum (conduit_hum's: odd harmonics strong, darkened), held steady."""
    return [(k, (1.0 if k % 2 else 0.45) / k ** 0.9 / (1 + (k * f0 / 900.0) ** 2)) for k in range(1, 13)]


def pedal_hum(seed: int) -> np.ndarray:
    """The engine's pedal, E2 and B2 (just), at a constant level for the whole loop, every partial snapped to whole
    cycles per loop. Stereo, exactly one loop long."""
    g = rng(seed)
    N = int(round(LOOP_S * SR))
    t = np.arange(N) / SR
    out = np.zeros((N, 2))
    for side, (m, lvl) in enumerate(((E_REF, 1.0), (E_REF + 7, 0.5))):
        f0 = ji_hz(m)
        for k, a in organ_partials(f0):
            s = lvl * a * np.sin(2 * np.pi * V.snap(k * f0, LOOP_S) * t + g.uniform(0, 6.28))
            out[:, side] += s
            out[:, 1 - side] += 0.7 * s
    return 0.05 * out


def organ_note(m: float, dur: float, vel: float, seed: int, attack: float = 0.6, release: float = 0.9) -> np.ndarray:
    """One held note of the engine's hum: the pedal's spectrum on m (just), a slow onset, then constant. Mono."""
    g = rng(seed)
    f0 = ji_hz(m)
    N = int((dur + release * 3) * SR)
    t = np.arange(N) / SR
    x = sum(a * np.sin(2 * np.pi * k * f0 * t + g.uniform(0, 6.28)) for k, a in organ_partials(f0))
    env = np.clip(t / attack, 0, 1) ** 2 * np.where(t > dur, np.exp(-(t - dur) / release), 1.0)
    return 0.05 * vel * x * env


def bound_tone(m: float, dur: float, vel: float, seed: int, fade: float = 1.4) -> np.ndarray:
    """A bound light in the glass: a pure tone (just over E) with a faint octave, faded in, then constant (no vibrato,
    no shimmer), faded out. Mono."""
    g = rng(seed)
    f = ji_hz(m)
    N = int((dur + fade) * SR)
    t = np.arange(N) / SR
    x = np.sin(2 * np.pi * f * t + g.uniform(0, 6.28)) + 0.12 * np.sin(2 * np.pi * 2 * f * t + g.uniform(0, 6.28))
    env = np.clip(t / fade, 0, 1) ** 2 * np.clip((dur + fade - t) / fade, 0, 1) ** 2
    return 0.05 * vel * x * env


def steady_e5(seed: int) -> np.ndarray:
    """The glass's E5 for the whole loop (the lamp that is always lit): constant, snapped to whole cycles. Stereo."""
    g = rng(seed)
    N = int(round(LOOP_S * SR))
    t = np.arange(N) / SR
    f = ji_hz(n("E5"))
    s = np.sin(2 * np.pi * V.snap(f, LOOP_S) * t + g.uniform(0, 6.28)) \
        + 0.12 * np.sin(2 * np.pi * V.snap(2 * f, LOOP_S) * t + g.uniform(0, 6.28))
    return 0.05 * np.stack([s * 0.8, s * 0.6], axis=1)


def hum_line(bar: int, shift: int) -> list[tuple[float, float, float]]:
    """ORDER_HUM from `bar`, one beat a bar, transposed: [(t, dur, midi)]."""
    out, pos = [], t_of(bar)
    for m, beats in ORDER_HUM:
        d = beats * BAR
        out.append((pos, d, float(m + HUM_SHIFT + shift)))
        pos += d
    return out


def climb_notes(ch: str, octave: int) -> list[int]:
    """The climb figure: four lamps rising through the chord (root, third, fifth, octave) from `octave`."""
    root, *iv = CHORD_TONES[ch]
    r = n(f"{root}{octave}")
    if r > n(f"E{octave}") + 7:          # keep every chord's root within a sixth over E
        r -= 12
    return [r + iv[0], r + iv[1], r + iv[2], r + 12]


def build(mx: LoopMixer) -> None:
    g = rng(SEED)
    mx.add("hum", pedal_hum(SEED + 1), 0.0)
    mx.add("glass", steady_e5(SEED + 2), 0.0, gain=0.8)
    mx.add("air", V.wind(LOOP_S, SEED + 3, lo_hz=900.0, hi_hz=4200.0, gusts=(3, 7, 2), hi_level=0.35), 0.0)
    # the hum sounds ORDER_HUM; between its statements it holds E (the landing) and B (the top)
    held = [(t_of(23), 4 * BAR, n("E3")), (t_of(45), 8 * BAR, n("B2"))]
    for k, (bar, shift) in enumerate(HUM_BARS.items()):
        for i, (t0, d, m) in enumerate(hum_line(bar, shift)):
            mx.add("hum", organ_note(m, d + 0.15, 0.85, SEED + 100 + 20 * k + i), t0 - 0.3)
            if shift:                                   # A': the low strings double the hum
                x = pad_chord([m], d * 0.98, 0.6, seed=SEED + 300 + i, voices=4, spread_cents=5.0, attack=0.8,
                              release=1.2, width=0.5)
                mx.add("strings", x, t0 - 0.2)
    for i, (t0, d, m) in enumerate(held):
        mx.add("hum", organ_note(m, d - 0.3, 0.8, SEED + 160 + i), t0 - 0.3)
    x = pad_chord([n("B1"), n("F#2")], 8 * BAR - 0.4, 0.6, seed=SEED + 350, voices=4, spread_cents=5.0, attack=1.2,
                  release=1.6, width=0.6)
    mx.add("strings", x, t_of(45) - 0.2)
    # the glass's lamp line
    for i, (b0, b1, p) in enumerate(GLASS):
        dur = (b1 - b0 + 1) * BAR - 1.4
        mx.add("glass", bound_tone(n(p), dur, 0.7, SEED + 200 + i), t_of(b0) - 0.6,
               pan=(-0.4, 0.3, 0.45, -0.2, 0.2, -0.45)[i])
    # the escapement
    v_i = 0
    for bar in range(1, BARS + 1):
        sec = SECTION[bar - 1]
        for e in range(1, 9):
            on_q = e % 2 == 1
            if sec in ("I", "L", "R") and not on_q:
                continue
            vel = (0.7 if e in (1, 5) else 0.5 if on_q else 0.38) * float(g.uniform(0.92, 1.05))
            mx.add("tick", LE.tick(not on_q if sec not in ("I", "L", "R") else e in (3, 7), vel, v_i), t_of(bar, e),
                   pan=0.25 if on_q else -0.25)
            v_i += 1
            if (sec == "A2" and bar >= 35) or sec == "T":         # the off-sixteenths
                vv = (0.22 if sec == "A2" else 0.3) * float(g.uniform(0.9, 1.05))
                mx.add("tick", LE.tick(True, vv, v_i), t_of(bar, e) + E8 / 2, pan=0.05)
                v_i += 1
    # the stroke
    for bar in range(1, BARS + 1):
        sec = SECTION[bar - 1]
        beats = {"I": (0, 2), "A": (0,), "L": (0,), "A2": (0, 2), "T": (0, 1, 2, 3), "R": (0,)}[sec]
        if sec == "I" and bar % 2 == 0:
            beats = (0,)
        for b in beats:
            vel = (0.8 if b == 0 else 0.6 if b == 2 else 0.4) * float(g.uniform(0.92, 1.04))
            mx.add("engine", V.engine_thud(g, vel), t_of(bar, 1 + 2 * b) + float(g.normal(0, 0.004)), pan=-0.05)
    # the climb
    for bar in range(1, BARS + 1):
        ch = CHORDS[bar - 1]
        if ch is None:
            continue
        octave = 4 if SECTION[bar - 1] == "A" else 5
        for j, m in enumerate(climb_notes(ch, octave)):
            x = metallophone_note(m, (0.42 + 0.06 * j) * float(g.uniform(0.94, 1.04)),
                                  seed=SEED + 1000 + 4 * bar + j, decay=2.2, hardness=0.35, ombak_hz=0.0,
                                  damp_at=BEAT * 0.9, pair=False)
            mx.add("climb", x, t_of(bar, 1 + 2 * j) + float(g.normal(0, 0.003)), pan=-0.45 + 0.3 * j)
    # a low gong at each section's start
    for k, (bar, p) in enumerate(GONGS.items()):
        mx.add("gong", kettle_gong(n(p), 0.55, seed=SEED + 1500 + k, t60=3.0), t_of(bar) - 0.005, pan=-0.15)


# Bus gains from measured bus loudness (render(stats=...)["bus_lufs"], each bus gated where it plays), relative to
# the hum (0 LU): the glass -4, the climb -5, the strings -6, the tick -10, the stroke -9, the gong -10, the air -20.
GAINS = {"hum": 0.0, "glass": -1.6, "climb": -2.1, "strings": 1.7, "tick": -6.4, "engine": -15.9, "gong": -8.9,
         "air": -6.2}


def render(out_path: str = OUT, verbose: bool = True, stats: dict | None = None) -> dict:
    mx = LoopMixer(intro_s=0.0, loop_s=LOOP_S, preroll_s=8.0)
    G = GAINS
    mx.bus("hum", G["hum"], send=0.25, process=lambda x: filt(x, [bq_highpass(35, 0.7), bq_lowpass(1400, 0.7)]))
    mx.bus("glass", G["glass"], send=0.45, process=lambda x: filt(x, [bq_highpass(300, 0.7)]))
    mx.bus("climb", G["climb"], send=0.35, process=lambda x: filt(x, [bq_highpass(200, 0.7)]))
    mx.bus("strings", G["strings"], send=0.3, process=lambda x: string_body(x, cutoff=1100.0))
    mx.bus("tick", G["tick"], send=0.15, process=lambda x: filt(x, [bq_highpass(800, 0.7)]))
    mx.bus("engine", G["engine"], send=0.25, process=lambda x: filt(x, [bq_highpass(32, 0.7), bq_lowpass(1200, 0.7)]))
    mx.bus("gong", G["gong"], send=0.4, process=lambda x: filt(x, [bq_highpass(60, 0.7)]))
    mx.bus("air", G["air"], send=0.1, process=lambda x: filt(x, [bq_highpass(500, 0.7)]))
    build(mx)
    hall = ModFDNReverb(rt60=3.0, rt60_high=1.1, predelay=0.03, size=1.4, mod_depth=6.0, mod_rate=0.3,
                        early_level=0.3, lowcut=90.0, seed=SEED % 9973)    # a tall ceramic drum, open at the top
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    return V.finish(mx, "iskarra_spire", out_path, BPM, BAR_BEATS, BARS, LEAD_IN_E * E8, TARGET_LUFS, hall, -3.0,
                    verbose, stats, quality=QUALITY)


if __name__ == "__main__":
    render(sys.argv[1] if len(sys.argv) > 1 else OUT)
