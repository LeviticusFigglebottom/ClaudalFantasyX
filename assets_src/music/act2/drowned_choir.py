"""`drowned_choir` (final): Ch16, the Drowned Choir, a ring of colossal stone figures standing in the water, mouths
open, around a sunken amphitheatre (M3-AUD-843; act_outline Ch16, bible §5.8): a 153 s seamless loop, grown from
the Act II sketch `assets_src/music/drowned_choir.py` (M3-AUD-805).

Original composition for this project (SPEC §2, §9). Original-material check: every line the choir hums or sings is
our own Hush theme (hush_theme_v2.py MEL_A, MEL_B, MEL_C and its INNER voice), imported from that file, never
retyped; its harmony follows that cue's left hand (LH bars 3-24). The sketch's own material (the men's roots, the
stones' F-major and E-major open-vowel chords, the vowels and the Cantor's E-D-C cell) is imported from the sketch.
New here: the men's roots and the stones' voicings for the Hush's second and third phrases, and the form. The style
evoked is a slow choral lament heard through water; no phrase is quoted from any existing music.

The brief (unchanged from the sketch): this is where every Cantor ends, and where the Hush was first sung: Kesh sang
herself into the storm's centre here as its first heart. Asha binds her and learns from inside what the Hush truly
does. Awe and grief: the song's true home, and a grave.

So the cue is the Hush sung by the stones, from under the water. The Order hums (bible §4) and only Cantors sing, so
the choir hums with closed mouths, as the Order taught: the women carry the Hush's first phrase (bars 5-12) and its
second, rising to the high A (bars 17-24), a tenor line humming its inner voice under the second. Twice the mouths
open (the figures' mouths are open) and the voices sing open vowels, never words: in bars 13-16, as in the sketch,
F major then E major and the Cantor's three-note cell; and in bars 25-32, the passage grown: the stones sing the
Hush's last phrase's chords (Am F Dm E F Am) on u, o, then a held (u-o-a-a-a-o), one Cantor above them sings
MEL_C itself on open vowels, and the stones close it on the sketch's Phrygian F-to-E (o, then u). Everything is
heard through water: the choir is low-passed, and the filter opens three times a loop: a little in bars 13-15, a
little at the Hush's high A (bars 19-21), and widest in bars 26-31, then closes again.

A minor (the Hush's key), 3/4 at 47 BPM (a bar is 3.83 s), 40 bars.

Ensemble (all synthesized; no samples): the sketch's: the men (a hummed congregation on the roots, loop-wrapped so
nobody breathes at the seam, with a fifth above), the women (a hummed congregation on the Hush), the stones (six
sung voices on open vowels), one Cantor (alto in bars 13-14, soprano in bars 25-30), and the deep (a large gong, now
every eight bars, and slow bubbles rising); new: the tenors (a hummed congregation on the Hush's INNER voice).

Form (bars):
  1-4   the deep, the men on A (the gong)
  5-12  A: the women hum MEL_A (Am F C Em Dm Am E E)
  13-16 B: the mouths open: F major, u-o-a, and the Cantor's cell (E-D-C); E major, closing back to the hum
  17-24 A2: the women hum MEL_B to the high A (F G Em Am Dm G C G#), the tenors on its inner voice (the gong)
  25-30 C: the mouths open wide: the stones on Am F Dm E F Am, u-o-a-a-a-o, the Cantor sings MEL_C (the gong)
  31-32 the stones' F, then E: the Phrygian close, the filter closing
  33-36 the women hum the Hush's first cell once more, quietly (Am Am F E) (the gong)
  37-40 the deep, the men on A, which is bar 1

Loop: LOOPSTART = 0 and LOOPLENGTH = the whole file. The file starts a sixteenth before bar 1's downbeat (the
sidecar's `downbeat_offset_s`), so the seam falls just before the gong, not on it.

Render:  python3 assets_src/music/act2/drowned_choir.py   (or tools/audio/render_all.py --act2 --only
act2/drowned_choir)
"""
from __future__ import annotations

import importlib.util
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
MUSIC = os.path.dirname(HERE)
ROOT = os.path.abspath(os.path.join(MUSIC, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools", "audio"))

import numpy as np  # noqa: E402

from synth.dsp import SR, bq_highpass, bq_lowpass, filt, rng  # noqa: E402
from synth.gongs import large_gong  # noqa: E402
from synth.looping import LoopMixer  # noqa: E402
from synth.reverb import ModFDNReverb  # noqa: E402
from synth.score import n  # noqa: E402
from synth.voice import hum_ensemble, sing  # noqa: E402
from synth.water import bubble  # noqa: E402


def _mod(name: str):
    spec = importlib.util.spec_from_file_location(f"_act2_{name}", os.path.join(MUSIC, f"{name}.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


SK = _mod("drowned_choir")   # the sketch: its material, voices and balance
HUSH = SK.HUSH               # the Hush (hush_theme_v2), as the sketch loaded it
V = _mod("act2_voices")      # the Act II kit: finish()

OUT = os.path.join(ROOT, "assets", "audio", "music", "act2", "drowned_choir.ogg")
SEED = 20261653
TARGET_LUFS = -16.0
BPM = SK.BPM
BEAT = SK.BEAT
BAR = SK.BAR
BARS = 40
LOOP_S = BARS * BAR
LEAD_IN_BEATS = SK.LEAD_IN_BEATS
QUALITY = SK.QUALITY


def _bass(hush_bar: int) -> str:
    """The Hush's left-hand bass note for one of its bars (hush_theme_v2 LH)."""
    return HUSH.LH[hush_bar].split()[0]


## the men's roots, one per bar: the sketch's 16, the Hush's bass for its second and third phrases (LH bars 11-18,
## 19-24), the sketch's F-E close, then the cell's bars and the deep
ROOTS = (SK.ROOTS + [_bass(b) for b in range(11, 19)] + [_bass(b) for b in range(19, 25)] + ["F2", "E2"]
         + ["A2", "A2", "F2", "E2"] + ["A2"] * 4)
## the stones: the sketch's two chords (bars 13 and 15), and C's (bars 25-32), one voice per note, voice-led
STONES_C = [("A2", "E3", "A3", "C4", "E4", "A4"), ("F2", "C3", "A3", "C4", "F4", "A4"),
            ("D2", "A2", "A3", "D4", "F4", "A4"), ("E2", "B2", "G#3", "B3", "E4", "G#4"),
            ("F2", "C3", "A3", "C4", "F4", "A4"), ("A2", "E3", "A3", "C4", "E4", "A4")]
STONES_C += [tuple(SK.STONES[0][1]), tuple(SK.STONES[1][1])]       # bars 31-32: the sketch's F, then E
C_BAR = 25
## C's vowels, one per bar (bars 25-32): the mouths open, stay open, and close
C_VOWELS = ["u", "o", "a", "a", "a", "o", "o", "u"]
## the hum's cell once more (bars 33-36): MEL_A's first three notes, then its A held
CELL_HUM = list(HUSH.MEL_A[:3]) + [("A4", 6, 0.4)]
## the filter: (centre bar, beat, width in bars, how far it opens 0..1): the sketch's opening, MEL_B's high A and C's
OPENINGS = [(14, 1.5, 2.2, 0.6), (20, 1.0, 2.5, 0.35), (28, 1.5, 6.0, 1.0)]
## MEL_B's hum, against MEL_A's: its high notes lose more to the water, so it is sung a little fuller
MEL_B_LIFT = 1.25
GONGS = [(1, 0.42), (9, 0.30), (17, 0.34), (25, 0.38), (33, 0.28)]

## the sketch's balance, and the tenors: a low-register hum carries far more level than the women's high one, so their
## bus sits near 0 dB for about -6 LU under the women while they hum (measured, render(stats=...)["bus_lufs"])
GAINS = dict(SK.GAINS, tenors=0.0)
## C's Cantor, against the sketch's cantor bus (set for a three-note cell): a little above the stones' momentary level
CANTOR_C = 0.45


def t_of(bar: int, beat: float = 0.0) -> float:
    return (bar - 1) * BAR + beat * BEAT


def _wrap(L: int, x: np.ndarray, start: float) -> np.ndarray:
    return SK._wrap(L, x, start)


def under_water(x: np.ndarray) -> np.ndarray:
    """The sketch's water, opening twice a loop: a dark and a less dark low-pass of the loop (L x 2), crossfaded by a
    curve of circular Gaussian openings (OPENINGS). Filtered in steady state, so it stays periodic."""
    L = len(x)
    k = int(2.0 * SR)
    ext = np.concatenate([x[-k:], x])
    dark = filt(ext, [bq_lowpass(950, 0.7), bq_lowpass(1400, 0.6)])[k: k + L]
    clear = filt(ext, [bq_lowpass(3000, 0.7)])[k: k + L]
    t = np.arange(L) / SR
    w = np.full(L, 0.15)
    for bar, beat, width, depth in OPENINGS:
        d = (t - t_of(bar, beat) + LOOP_S / 2) % LOOP_S - LOOP_S / 2
        w += 0.85 * depth * np.exp(-0.5 * (d / (width * BAR / 2)) ** 2)
    w = np.clip(w, 0.0, 1.0)
    return dark * (1 - w)[:, None] + clear * w[:, None]


def _place(L: int, x: np.ndarray, pan: float, start: float) -> np.ndarray:
    th = (pan + 1) * np.pi / 4
    return _wrap(L, np.stack([x * np.cos(th), x * np.sin(th)], axis=1), start)


def _hush_line(mel) -> list[tuple[float, float]]:
    return [(n(p), beats * BEAT) for p, beats, _ in mel]


def build(mx: LoopMixer) -> None:
    g = rng(SEED)
    L = mx.L
    # the men: the roots, loop-wrapped (nobody breathes at the seam), with a fifth above in the low register
    men = hum_ensemble([(n(p), BAR) for p in ROOTS], voices=14, seed=SEED + 1, register="low", loop=True)[:L]
    men += 0.45 * hum_ensemble([(n(p) + 7, BAR) for p in ROOTS], voices=8, seed=SEED + 2, register="low",
                               loop=True)[:L]
    # the women: MEL_A (bars 5-12), MEL_B (bars 17-24), the cell once more (bars 33-36, fewer and quieter)
    women = _wrap(L, hum_ensemble(_hush_line(HUSH.MEL_A), voices=12, seed=SEED + 3, register="high", spread=0.9),
                  t_of(5) - 0.2)
    women += MEL_B_LIFT * _wrap(L, hum_ensemble(_hush_line(HUSH.MEL_B), voices=12, seed=SEED + 4, register="high",
                                                spread=0.9), t_of(17) - 0.2)
    women += 0.6 * _wrap(L, hum_ensemble(_hush_line(CELL_HUM), voices=8, seed=SEED + 5, register="high",
                                         spread=0.7), t_of(33) - 0.2)
    # the tenors: the Hush's inner voice under MEL_B (INNER's lower note of each bar, LH bars 11-18 -> 17-24)
    inner = [(n(HUSH.INNER[b].split()[0]), BAR) for b in range(11, 19)]
    tenors = _wrap(L, hum_ensemble(inner, voices=8, seed=SEED + 6, register="low", spread=0.6), t_of(17) - 0.2)
    # the stones, B: the sketch's F then E, u-o-a
    stones = np.zeros((L, 2))
    for ci, (bar, chord) in enumerate(SK.STONES):
        dur = 2 * BAR
        for vi, p in enumerate(chord):
            ph = [(v, f * dur) for v, f in SK.VOWELS]
            x = sing(ph, [(n(p), dur)], vel=0.7 * g.uniform(0.9, 1.05), seed=SEED + 100 + 10 * ci + vi,
                     scale=1.0 if n(p) < 57 else 1.15, tilt=1.8, breath=0.08, vib_cents=14.0,
                     vib_rate=float(g.uniform(4.4, 5.4)), release=0.9)
            stones += _place(L, x, -0.7 + 0.28 * vi, t_of(bar) - 0.3 + float(g.normal(0, 0.06)))
    # the stones, C: eight bars, each voice one long breathless line through the chords and the vowels
    for vi in range(6):
        pits = [(n(ch[vi]), BAR) for ch in STONES_C]
        ph = [(v, BAR) for v in C_VOWELS]
        x = sing(ph, pits, vel=0.7 * g.uniform(0.9, 1.05), seed=SEED + 150 + vi,
                 scale=1.0 if n(STONES_C[0][vi]) < 57 else 1.15, tilt=1.8, breath=0.08, vib_cents=14.0,
                 vib_rate=float(g.uniform(4.4, 5.4)), release=1.1)
        stones += _place(L, x, -0.7 + 0.28 * vi, t_of(C_BAR) - 0.3 + float(g.normal(0, 0.06)))
    # the Cantor, B: one alto, far off, on the Hush's first cell (the sketch's)
    cell = [(n(p), b * BEAT) for p, b in SK.CELL]
    tot = sum(d for _, d in cell)
    x = sing([("a", tot * 0.7), ("o", tot * 0.3)], cell, vel=0.6, seed=SEED + 200, scale=1.17, tilt=1.7,
             breath=0.1, vib_cents=20.0, vib_rate=5.0, release=1.0)
    cantor = _wrap(L, x * 0.9, t_of(13, 1))
    # the Cantor, C: one soprano sings MEL_C itself, open vowels only, a vowel to a two-bar phrase
    line = _hush_line(HUSH.MEL_C)
    tot = sum(d for _, d in line)
    vow = [("a", 2 * BAR), ("o", 2 * BAR), ("a", tot - 4 * BAR)]
    x = sing(vow, line, vel=0.6, seed=SEED + 210, scale=1.2, tilt=1.7, breath=0.1, vib_cents=20.0, vib_rate=5.1,
             release=1.4)
    cantor += _wrap(L, x * CANTOR_C, t_of(C_BAR) - 0.05)
    for bus, sig in (("men", men), ("women", women), ("tenors", tenors), ("stones", stones), ("cantor", cantor)):
        mx.add(bus, under_water(sig), 0.0)
    # the deep
    for bar, v in GONGS:
        mx.add("gong", large_gong(n("A1"), v, seed=SEED + 300 + bar, t60=11.0), t_of(bar), pan=-0.05)
    for _ in range(55):
        ts = float(g.uniform(0, LOOP_S))
        b = bubble(float(g.uniform(2.5, 6.0)), float(g.uniform(0.3, 0.8)), rise=0.2)
        mx.add("bubbles", b, ts, pan=float(g.uniform(-0.8, 0.8)))


def render(out_path: str = OUT, verbose: bool = True, stats: dict | None = None) -> dict:
    mx = LoopMixer(intro_s=0.0, loop_s=LOOP_S, preroll_s=14.0)
    G = GAINS
    mx.bus("women", G["women"], send=0.6)
    mx.bus("tenors", G["tenors"], send=0.6, process=lambda x: filt(x, [bq_highpass(90, 0.7)]))
    mx.bus("men", G["men"], send=0.55, process=lambda x: filt(x, [bq_highpass(60, 0.7)]))
    mx.bus("stones", G["stones"], send=0.7)
    mx.bus("cantor", G["cantor"], send=0.8)
    mx.bus("gong", G["gong"], send=0.5, process=lambda x: filt(x, [bq_lowpass(700, 0.7)]))
    mx.bus("bubbles", G["bubbles"], send=0.4, process=lambda x: filt(x, [bq_lowpass(1500, 0.7)]))
    build(mx)
    amphitheatre = ModFDNReverb(rt60=6.5, rt60_high=1.4, predelay=0.07, size=1.8, mod_depth=14.0, mod_rate=0.22,
                                early_level=0.2, lowcut=70.0, seed=SEED % 9973)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    return V.finish(mx, "drowned_choir (final)", out_path, BPM, 3, BARS, LEAD_IN_BEATS * BEAT, TARGET_LUFS,
                    amphitheatre, -1.5, verbose, stats, quality=QUALITY)


if __name__ == "__main__":
    render(sys.argv[1] if len(sys.argv) > 1 else OUT)
