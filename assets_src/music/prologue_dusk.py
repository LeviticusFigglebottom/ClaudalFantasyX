"""`prologue_dusk`: the prologue's score (M3-AUD-862; prologue_dead_city.dlg, ADR 0017 §(e)): a 30.5 s intro and a
24 s seamless loop.

Original composition for this project (SPEC §2): built from our own Hush theme (hush_theme_v2.py, MEL_A, its first
phrase), not from any existing melody. This is the first music after the title: the drowned plaza of Iskarra at
dusk, seven people keeping their vigils apart, Rhen crossing the plaza to Asha on the steps, his lantern catching,
the only flame in the frame, and his older voice saying the one line. It is the game's first promise, so the Hush
is heard **in its own register** (E5 down to G4, as the title's piano plays it), tender and not grand, on a single
breath flute over a low string drone on A: one voice in a dead city. Ch9's `iskarra_vigil` echoes this scene later,
darker (MEL_A two octaves down, under the sea); this cue shares its world (the drone on A, the glass over the voice's
band, the motes that rise) but states the theme first, and in the light.

**The line splits the phrase.** MEL_A's first half (E D C | A G A | G C D | E G) plays while Rhen crosses and ends
on its rising G as the lantern catches; the lantern brings the cue's first chord (F major seventh, strings), the
first warmth, which dies away before he speaks. Under the line the music leaves the voice its band (300 Hz to
3 kHz): only the drone and the bass under it, the warmth's low F, and a faint glass halo above it. When the glimmer
rises the motes rise with it, and MEL_A's second half answers (F E D | C B A | B D E | E) over Dm, Am/C, Esus and E,
a half close: a promise, left open on the fifth. The loop is the plaza after it: the drone on A breathing, the halo,
two small rising glass figures, nothing in the voice's band, so it can hold under the line if the player lingers,
and the scene's fade-out and the router's fade take it away.

Timeline (s; the .dlg's timeline in brackets): 0-4.5 the drone breathes in under the fade-in [@fade in 3.0, @wait
1.5] | 3.0 MEL_A begins, the flute alone | [4.5-11.5 Rhen walks to Asha, the camera's 7 s blend; @wait 1.0] |
12.4 the first half's last note, the rising G | 12.5 the lantern catches [@light on 1.4]: the strings' first chord
blooms, the halo enters; the chord has died away by 14.5 | 14.5-19.5 the hollow under the line [about 5 s of
VO] | 19.5 the glimmer rises: three rising glass figures (twelve motes) | 19.8 MEL_A's second half; Dm, Am/C, Esus, E |
[23.5-26.0 @fade out 2.5] | 27.3-29.3 the last E, held, and its fade | 30.5 = LOOPSTART: the loop (24 s), the drone
alone with the halo, rising figures at loop 3.0 and 12.5 s.

Key A minor (Aeolian, major V at the half close), 3/4, the melody at 72 BPM with rubato; the loop is unmetred.

How the intro meets the loop: the bed (drone, low strings, halo) is built as exactly periodic one-loop signals, and
the intro plays the same signals tiled backwards from LOOPSTART (with fade-ins at the start), so the splice carries
identical tails. The scene's own layers (flute, the chords, the glimmer) are mixed apart with their own plaza
reverb and are silent before LOOPSTART.

Render:  python3 assets_src/music/prologue_dusk.py   (or tools/audio/render_all.py --only prologue_dusk)
"""
from __future__ import annotations

import importlib.util
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools", "audio"))

import numpy as np  # noqa: E402

from synth.dsp import SR, bq_highpass, bq_lowpass, db_to_lin, filt, midi_to_hz, rng  # noqa: E402
from synth.looping import LoopMixer, master_loop, write_loop_sidecar  # noqa: E402
from synth.loudness import integrated_lufs  # noqa: E402
from synth.metallophone import metallophone_note  # noqa: E402
from synth.mixer import Mixer, measure, write_ogg  # noqa: E402
from synth.pad import pad_chord, string_body  # noqa: E402
from synth.reverb import ModFDNReverb  # noqa: E402
from synth.score import n  # noqa: E402
from synth.winds import breath_flute  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))


def _mod(name: str):
    spec = importlib.util.spec_from_file_location(name, os.path.join(HERE, f"{name}.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


HUSH = _mod("hush_theme_v2")

OUT = os.path.join(ROOT, "assets", "lfs", "audio", "music", "prologue_dusk.ogg")
SEED = 20261028
TARGET_LUFS = -16.0
BPM = 72.0
BEAT = 60.0 / BPM
INTRO_S = 30.5
LOOP_S = 24.0
VOICE_BAND = (300.0, 3000.0)
LOW_LP = 300.0            # the low layers stay under this
HIGH_HP = 2400.0          # the glass stays over this
## breath_flute's tone starts after its breath (0.05-0.08 s): its notes are placed this much early
FLUTE_PRE = 0.065

# The scene, in file seconds (prologue_dead_city.dlg's timeline, as in the docstring)
MEL_T1 = 3.0              # MEL_A's first half
LANTERN_T = 12.5          # @light LanternLight on 1.4
LINE_T = (14.5, 19.5)     # the narrator's line (about 5 s)
GLIMMER_T = 19.5          # @vfx glimmer_lift
MEL_T2 = 19.8             # MEL_A's second half
HALF = 11                 # MEL_A's first eleven notes are its first half (bars 1-4: E D C | A G A | G C D | E G)
LONG_STRETCH = 1.05       # a long note (2 beats or more) leans a little long
LANTERN_FERMATA = 1.4     # the first half's last note, the rising G, held as the lantern catches
SECOND_BEAT = 0.8         # the answer moves on a little (75 BPM) ...
SECOND_RIT = (1.05, 1.1, 1.16)  # ... and slows into its last bar
LAST_HOLD = 2.0           # the last E (s)
SCENE_FADE = (29.8, 30.5)  # the scene layers are silent before LOOPSTART

# Harmony (pitch names), each (file s, dur s, notes)
LANTERN_CHORD = ["F3", "A3", "C4", "E4"]          # F major seventh: the first warmth
LOW_LANTERN = ["F2", "C3"]                        # its bass stays under the line
ANSWER = [["D3", "F3", "A3"], ["C3", "E3", "A3"], ["E3", "A3", "B3"], ["E3", "G#3", "B3", "D4"]]
ANSWER_BASS = [["D2", "A2"], ["C2", "G2"], ["E2", "B2"], ["E2", "B2"]]
# The glass: the glimmer's three rising figures (twelve motes, as the vfx's count), and the loop's two
GLIMMER = [["E7", "G7", "B7", "E8"], ["G7", "B7", "D8", "E8"], ["E7", "A7", "B7", "E8"]]
GLIMMER_AT = [GLIMMER_T + 0.1, GLIMMER_T + 1.5, GLIMMER_T + 3.0]
LOOP_RISE = [(3.0, ["E7", "A7", "C8"]), (12.5, ["G7", "B7", "E8"])]
HALO = [("A7", 1.0), ("E7", 0.75), ("C8", 0.4)]   # the loop's glass halo, slowly beating pairs
DRONE = [("A2", 1.0), ("E3", 0.7)]                # the low strings' drone (under LOW_LP)
SUB = [("A1", 1.0), ("E2", 0.4)]                  # a quiet sine sub under them


def low_band(x: np.ndarray) -> np.ndarray:
    return filt(x, [bq_highpass(35, 0.7), bq_lowpass(LOW_LP, 0.6), bq_lowpass(LOW_LP * 1.25, 0.7)])


def high_band(x: np.ndarray) -> np.ndarray:
    return filt(x, [bq_highpass(HIGH_HP, 0.6), bq_highpass(HIGH_HP * 0.9, 0.7), bq_lowpass(11000, 0.7)])


def flute_band(x: np.ndarray) -> np.ndarray:
    return filt(x, [bq_highpass(220, 0.7), bq_lowpass(7000, 0.7)])


def _snap(f: float) -> float:
    return max(1.0, round(f * LOOP_S)) / LOOP_S


def _smooth(t: np.ndarray, a: float, b: float) -> np.ndarray:
    x = np.clip((t - a) / (b - a), 0, 1)
    return x * x * (3 - 2 * x)


def _circ(buf: np.ndarray, sig: np.ndarray, t0: float) -> None:
    """Add a stereo signal into a one-loop buffer, wrapping."""
    L = len(buf)
    s = int(round(t0 * SR)) % L
    pos = 0
    while pos < len(sig):
        take = min(L - s, len(sig) - pos)
        buf[s: s + take] += sig[pos: pos + take]
        pos += take
        s = 0


# --------------------------------------------------------------------------- #
# The bed: exactly periodic one-loop signals (the intro tiles them backwards)
# --------------------------------------------------------------------------- #
def strings_drone() -> np.ndarray:
    """Low strings on A (A2, E3), sul tasto: two long overlapping bows a loop, so the drone breathes. Periodic."""
    L = int(round(LOOP_S * SR))
    buf = np.zeros((L, 2))
    for k, t0 in enumerate((0.0, LOOP_S / 2)):
        x = pad_chord([n(p) for p, _ in DRONE], LOOP_S / 2 + 1.0, vel=0.6, seed=SEED + 10 + k, voices=4,
                      spread_cents=6.0, attack=3.0, release=3.0, width=0.5)
        _circ(buf, x, t0)
    return buf


def sub_drone() -> np.ndarray:
    """A1 and E2 as sines (each a slowly beating pair), breathing on a 12 s cycle. Periodic, stereo."""
    g = rng(SEED + 20)
    L = int(round(LOOP_S * SR))
    t = np.arange(L) / SR
    out = np.zeros((L, 2))
    breath = 0.5 - 0.5 * np.cos(2 * np.pi * _snap(1 / 12.0) * t)
    for p, lvl in SUB:
        f0 = midi_to_hz(n(p))
        for side, det in ((0, 0.0), (1, 0.08)):
            s = lvl * (0.7 + 0.3 * breath) * np.sin(2 * np.pi * _snap(f0 + det) * t + g.uniform(0, 6.28))
            out[:, side] += s
            out[:, 1 - side] += 0.5 * s
    return out * 0.05


def halo() -> np.ndarray:
    """A faint high halo of glass tones, each a slowly beating pair, swelling in and out. Periodic, stereo."""
    g = rng(SEED + 30)
    L = int(round(LOOP_S * SR))
    t = np.arange(L) / SR
    out = np.zeros((L, 2))
    for k, (p, lvl) in enumerate(HALO):
        f0 = midi_to_hz(n(p))
        sw = 0.5 - 0.5 * np.cos(2 * np.pi * _snap(1 / (8.0 + 4.0 * k)) * t + g.uniform(0, 6.28))
        s = lvl * sw * (np.sin(2 * np.pi * _snap(f0) * t + g.uniform(0, 6.28))
                        + 0.8 * np.sin(2 * np.pi * _snap(f0 + 0.5 + 0.25 * k) * t + g.uniform(0, 6.28)))
        out[:, k % 2] += s
        out[:, 1 - k % 2] += 0.5 * s
    return out * 0.02


def _tile_back(sig: np.ndarray, env: np.ndarray) -> np.ndarray:
    """The periodic signal tiled so that sample INTRO_S is the loop's first sample, times env (intro long)."""
    S = int(round(INTRO_S * SR))
    idx = (np.arange(S) - S) % len(sig)
    return sig[idx] * env[:, None]


def glass(notes: list[str], vel: float, seed: int) -> list[np.ndarray]:
    return [metallophone_note(n(p), vel + 0.03 * j, seed=seed + j, decay=4.0, hardness=0.2, ombak_hz=3.5)
            for j, p in enumerate(notes)]


# --------------------------------------------------------------------------- #
# The scene: MEL_A, the chords, the glimmer (intro only)
# --------------------------------------------------------------------------- #
def melody() -> list[tuple[float, float, float, float]]:
    """MEL_A as [(t, dur, midi, vel)]: its first half from MEL_T1, the second half from MEL_T2 (the line between)."""
    out, pos = [], MEL_T1
    for i, (p, beats, v) in enumerate(HUSH.MEL_A[:HALF]):
        d = beats * BEAT * (LONG_STRETCH if beats >= 2 else 1.0)
        if i == HALF - 1:
            d = beats * BEAT * LANTERN_FERMATA
        out.append((pos, d, n(p), v))
        pos += d
    second = HUSH.MEL_A[HALF:]
    pos = MEL_T2
    for i, (p, beats, v) in enumerate(second):
        k = i - (len(second) - 1 - len(SECOND_RIT))       # the last bar's three notes slow, then the held E
        d = beats * SECOND_BEAT * (SECOND_RIT[k] if 0 <= k < len(SECOND_RIT) else 1.0)
        if i == len(second) - 1:
            d = LAST_HOLD
        out.append((pos, d, n(p), v))
        pos += d
    return out


def answer_times(line: list) -> list[float]:
    """The second half's chord changes: on each of its bars' downbeats (F, C, B and the last E)."""
    second = line[HALF:]
    starts, beat = [], 0.0
    for (t, _, _, _), (_, beats, _) in zip(second, HUSH.MEL_A[HALF:]):
        if abs(beat % 3) < 1e-6:
            starts.append(t)
        beat += beats
    return starts


def scene(line: list) -> tuple[np.ndarray, dict]:
    """The scene's own layers, mixed apart with their own plaza reverb; silent before LOOPSTART."""
    g = rng(SEED + 1)
    mx = Mixer(INTRO_S)
    mx.bus("flute", SCENE_GAINS["flute"], send=0.36, process=flute_band)
    mx.bus("warm", SCENE_GAINS["warm"], send=0.5, process=lambda x: string_body(x, cutoff=1800.0))
    mx.bus("low", SCENE_GAINS["low"], send=0.25, process=low_band)
    mx.bus("glimmer", SCENE_GAINS["glimmer"], send=0.55, process=high_band)
    first = True
    for i, (t0, d, m, v) in enumerate(line):
        long_ = d >= 1.4
        last = i == len(line) - 1
        x = breath_flute(m, d * 0.97 + 0.05, 0.42 + 0.5 * v, seed=SEED + 200 + 7 * i, breath=0.4,
                         scoop_cents=50.0 if first else 18.0, vib_cents=11.0 if long_ else 4.0, vib_rate=4.3,
                         swell=0.25 if long_ and not last else 0.0, attack=0.12 if first else 0.05,
                         release=0.9 if last else 0.5 if i == HALF - 1 else 0.4)
        mx.add("flute", x, t0 - FLUTE_PRE + float(g.normal(0, 0.006)), pan=-0.08)
        first = i == HALF - 1
    # the lantern: the first chord, which has gone before the line; its bass stays under the line
    x = pad_chord([n(p) for p in LANTERN_CHORD], 1.1, vel=0.75, seed=SEED + 300, voices=4, spread_cents=8.0,
                  attack=0.7, release=0.9)
    mx.add("warm", x, LANTERN_T)
    starts = answer_times(line)
    x = pad_chord([n(p) for p in LOW_LANTERN], starts[0] - LANTERN_T + 0.4, vel=0.7, seed=SEED + 310, voices=4,
                  spread_cents=6.0, attack=1.2, release=1.4, width=0.5)
    mx.add("low", x, LANTERN_T)
    # the answer: Dm, Am/C, Esus, E
    ends = starts[1:] + [line[-1][0] + line[-1][1]]
    for k, (a, b) in enumerate(zip(starts, ends)):
        x = pad_chord([n(p) for p in ANSWER[k]], b - a + 0.3, vel=0.5, seed=SEED + 320 + k, voices=4,
                      spread_cents=8.0, attack=0.9 if k else 1.4, release=1.2 if k < 3 else 1.6)
        mx.add("warm", x, a - 0.15)
        x = pad_chord([n(p) for p in ANSWER_BASS[k]], b - a + 0.3, vel=0.7, seed=SEED + 330 + k, voices=4,
                      spread_cents=6.0, attack=0.9, release=1.4 if k < 3 else 1.8, width=0.5)
        mx.add("low", x, a - 0.15)
    # the glimmer rises: three rising figures, twelve motes
    for k, (t, fig) in enumerate(zip(GLIMMER_AT, GLIMMER)):
        for j, x in enumerate(glass(fig, 0.2, SEED + 400 + 10 * k)):
            mx.add("glimmer", x, t + 0.26 * j + float(g.normal(0, 0.01)), pan=-0.45 + 0.3 * j)
    plaza = ModFDNReverb(rt60=3.0, rt60_high=1.3, predelay=0.03, size=1.2, mod_depth=9.0, mod_rate=0.4,
                         early_level=0.2, lowcut=60.0, seed=(SEED + 7) % 9973)
    st = {f"scene_{k}": _bus_lufs(b.buf, b.process, b.gain_db) for k, b in mx.buses.items()}
    out = mx.render(reverb=plaza, reverb_return_db=-2.0)
    t = np.arange(len(out)) / SR
    out *= (1.0 - _smooth(t, *SCENE_FADE))[:, None]
    return out, st


def _bus_lufs(buf: np.ndarray, process, gain_db: float) -> float:
    x = (process(buf) if process else buf) * db_to_lin(gain_db)
    return float(integrated_lufs(x)) if np.any(x) else float("-inf")


def build_bed(mx: LoopMixer) -> None:
    S = int(round(INTRO_S * SR))
    t = np.arange(S) / SR
    fade_in = _smooth(t, 0.0, 4.5)
    for bus, sig, env in (("drone", strings_drone(), fade_in), ("sub", sub_drone(), fade_in),
                          ("halo", halo(), _smooth(t, LANTERN_T - 0.2, LANTERN_T + 3.5))):
        mx.add(bus, sig, 0.0)
        mx.add(bus, _tile_back(sig, env), 0.0, part="intro")
    # the loop's rising figures (early in the loop, so their tails end before the loop does: not in the intro)
    for k, (t0, fig) in enumerate(LOOP_RISE):
        for j, x in enumerate(glass(fig, 0.17, SEED + 500 + 10 * k)):
            mx.add("motes", x, t0 + 0.32 * j, pan=-0.3 + 0.3 * j)


# Bus gains from measured bus loudness (render(stats=...)): the flute at L; the lantern's chord and the answer's
# strings L-9, their bass L-8, the glimmer L-8; the bed's low strings L-10, the sub L-14, the halo L-14, the loop's
# figures L-12. The loop alone is about 8 LU under the intro (-22 against -14 LUFS): a quiet plaza that a voice can
# sit on.
SCENE_GAINS = {"flute": 0.0, "warm": 1.5, "low": 2.6, "glimmer": -2.0}
BED_GAINS = {"drone": 3.0, "sub": -6.5, "halo": -1.5, "motes": -0.8}


def render(out_path: str = OUT, verbose: bool = True, stats: dict | None = None) -> dict:
    line = melody()
    mx = LoopMixer(intro_s=INTRO_S, loop_s=LOOP_S, intro_tail_s=6.0, preroll_s=8.0)
    mx.bus("drone", BED_GAINS["drone"], send=0.25, process=low_band)
    mx.bus("sub", BED_GAINS["sub"], send=0.1, process=low_band)
    mx.bus("halo", BED_GAINS["halo"], send=0.4, process=high_band)
    mx.bus("motes", BED_GAINS["motes"], send=0.55, process=high_band)
    build_bed(mx)
    hall = ModFDNReverb(rt60=3.0, rt60_high=1.3, predelay=0.03, size=1.2, mod_depth=9.0, mod_rate=0.4,
                        early_level=0.2, lowcut=60.0, seed=SEED % 9973)
    intro, loop = mx.render(reverb=hall, reverb_return_db=-2.0)
    sc, st = scene(line)
    intro = intro + sc[: len(intro)]
    rep: dict = {}
    intro, loop = master_loop(intro, loop, TARGET_LUFS, ceiling_db=-2.0, report=rep)
    y = np.concatenate([intro, loop])
    S, L = len(intro), len(loop)
    write_ogg(out_path, y, quality=3.0, tags={"LOOPSTART": str(S), "LOOPLENGTH": str(L)})
    write_loop_sidecar(os.path.splitext(out_path)[0] + ".loop.json", SR, S, L, BPM, 3,
                       extra={"intro_s": INTRO_S, "line_s": list(LINE_T)})
    m = measure(y)
    st.update({f"bed_{k}": v for k, v in mx.bus_lufs.items()})
    st["splice_residual_db"] = mx.splice_residual_db
    st["limiter"] = rep
    st["loop_lufs"] = float(integrated_lufs(loop))
    st["intro_lufs"] = float(integrated_lufs(intro))
    st.update(_band_report(y))
    if stats is not None:
        stats.update(st)
    if verbose:
        print("  stats", {k: (round(v, 2) if isinstance(v, float) else v) for k, v in st.items()})
        print(f"prologue_dusk: {m['seconds']:.2f}s  {m['integrated_lufs']:.2f} LUFS  TP {m['true_peak_dbtp']:.2f} dBTP"
              f"  loop {S}+{L}  splice {mx.splice_residual_db:.1f} dB")
    return m


def _band_report(y: np.ndarray) -> dict:
    """The voice's band (300 Hz-3 kHz) under the line, against the same band under MEL_A's first half."""
    lo, hi = VOICE_BAND
    b = filt(y.mean(axis=1), [bq_highpass(lo, 0.7), bq_highpass(lo, 0.7), bq_lowpass(hi, 0.7), bq_lowpass(hi, 0.7)])

    def rms_db(a: float, e: float) -> float:
        s = b[int(a * SR): int(e * SR)]
        return float(10 * np.log10((s ** 2).mean() + 1e-20))

    mel = rms_db(MEL_T1, LANTERN_T)
    return {"band_under_line_db_vs_melody": rms_db(LINE_T[0] + 0.1, LINE_T[1]) - mel,
            "band_loop_db_vs_melody": rms_db(INTRO_S, INTRO_S + LOOP_S) - mel}


if __name__ == "__main__":
    render(sys.argv[1] if len(sys.argv) > 1 else OUT)
