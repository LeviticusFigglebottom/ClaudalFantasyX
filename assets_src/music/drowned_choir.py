"""`drowned_choir`: Ch16, the Drowned Choir, a ring of colossal stone figures standing in the water, mouths open,
around a sunken amphitheatre (M3-AUD-805; act_outline Ch16, bible §5.8): a 61 s seamless loop. An Act II sketch, for
the human to judge the direction.

Original composition for this project (SPEC §2, §9). Original-material check: the line the women hum is our own
Hush theme's first phrase (hush_theme_v2.py MEL_A), slowed to 47 BPM; its harmony follows that cue's left hand
(A F C E D A E E). The men's roots, the open-vowel chords of bars 13-16 (F major, then E major: a Phrygian close)
and the single sung cell are written for this cue, the cell being the Hush's own first three notes (E-D-C). The
style evoked is a slow choral lament heard through water; no phrase is quoted from any existing music.

The brief: this is where every Cantor ends, and where the Hush was first sung: Kesh sang herself into the storm's
centre here as its first heart. Asha binds her and learns from inside what the Hush truly does. Awe and grief: the
song's true home, and a grave.

So the cue is the Hush sung by the stones, from under the water. The Order hums (bible §4) and only Cantors sing, so
for most of the loop the choir hums with closed mouths, as the Order taught; in bars 13-16 the mouths open (the
figures' mouths are open): the voices sing open vowels, u to o to a, on F major and E major, and one distant voice
sings the Hush's first cell. Everything is heard through water: the choir is low-passed, and the filter breathes
open once a loop, widest in bars 13-15, then closes again.

A minor (the Hush's key), 3/4 at 47 BPM (a bar is 3.83 s), 16 bars.

Ensemble (all synthesized; no samples):
* the men: a hummed congregation on the roots (A for bars 1-4, then the Hush's bass), loop-wrapped so nobody
  breathes at the seam;
* the women: a hummed congregation on the Hush's first phrase (bars 5-12);
* the stones: six sung voices on open vowels (bars 13-16), F major then E major, and one alto on E-D-C;
* the deep: a large gong at bars 1 and 9, very dark, and slow bubbles rising.

Form (bars): 1-4 the deep, the men on A | 5-12 the women hum the Hush (Am F C Em Dm Am E E) | 13-14 the mouths open:
F major, u-o-a, and the Cantor's cell | 15-16 E major, closing back to the hum, which leads to bar 1's A.

Loop: LOOPSTART = 0 and LOOPLENGTH = the whole file. The file starts a sixteenth before bar 1's downbeat (the
sidecar's `downbeat_offset_s`), so the seam falls just before the gong, not on it.

Render:  python3 assets_src/music/drowned_choir.py   (or tools/audio/render_all.py --only drowned_choir)
"""
from __future__ import annotations

import importlib.util
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(ROOT, "tools", "audio"))

import numpy as np  # noqa: E402

from synth.dsp import SR, bq_highpass, bq_lowpass, filt, rng  # noqa: E402
from synth.gongs import large_gong  # noqa: E402
from synth.looping import LoopMixer, master_loop, write_loop_sidecar  # noqa: E402
from synth.mixer import measure, write_ogg  # noqa: E402
from synth.reverb import ModFDNReverb  # noqa: E402
from synth.score import n  # noqa: E402
from synth.voice import hum_ensemble, sing  # noqa: E402
from synth.water import bubble  # noqa: E402


def _mod(name: str):
    spec = importlib.util.spec_from_file_location(name, os.path.join(HERE, f"{name}.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


HUSH = _mod("hush_theme_v2")

OUT = os.path.join(ROOT, "assets", "audio", "music", "drowned_choir.ogg")
SEED = 20261623
TARGET_LUFS = -16.0
BPM = 47.0
BEAT = 60.0 / BPM
BAR = 3 * BEAT
BARS = 16
LOOP_S = BARS * BAR
## the file starts this many beats before bar 1's downbeat (see render())
LEAD_IN_BEATS = 0.25
QUALITY = 3.0  # mix.md §5's sparse-cue quality

## the men's roots, one per bar (bars 5-12 follow the Hush's left hand, hush_theme_v2 LH bars 3-10)
ROOTS = ["A2", "A2", "A2", "A2", "A2", "F2", "C3", "E2", "D2", "A2", "E2", "E2", "F2", "F2", "E2", "E2"]
## the stones' open-vowel chords (bars 13-14 F, bars 15-16 E), one voice per note
STONES = [(13, ["F2", "C3", "A3", "C4", "F4", "A4"]), (15, ["E2", "B2", "G#3", "B3", "E4", "G#4"])]
VOWELS = [("u", 0.30), ("o", 0.35), ("a", 0.35)]       # fractions of the chord's length
## the Cantor's cell (the Hush's E-D-C), bar 13 beat 1
CELL = [("E4", 2.0), ("D4", 0.5), ("C4", 2.5)]

# Bus gains were set from measured bus loudness (render(stats=...)["bus_lufs"], the whole loop) for these levels
# relative to the women's Hush (0 LU, eight bars of sixteen): the men -3, the stones -4 (four bars), the Cantor -9,
# the gong -12, the bubbles -18.
GAINS = {"women": 20.0, "men": 9.5, "stones": -9.5, "cantor": -6.9, "gong": -4.7, "bubbles": -9.3}


def t_of(bar: int, beat: float = 0.0) -> float:
    return (bar - 1) * BAR + beat * BEAT


def _wrap(L: int, x: np.ndarray, start: float) -> np.ndarray:
    """x (mono or stereo) placed at `start` seconds in a stereo loop of L samples, wrapped past the end."""
    st = np.repeat(x[:, None], 2, axis=1) if x.ndim == 1 else x
    out = np.zeros((L, 2))
    s = int(round(start * SR)) % L
    pos = 0
    while pos < len(st):
        take = min(L - s, len(st) - pos)
        out[s: s + take] += st[pos: pos + take]
        pos += take
        s = 0
    return out


def under_water(x: np.ndarray) -> np.ndarray:
    """The loop (L x 2) heard through water: a dark and a less dark low-pass, crossfaded by a curve that opens once a
    loop (widest in bars 13-15). Filtered in steady state (the loop's own end is fed in first), so it stays periodic."""
    L = len(x)
    k = int(2.0 * SR)
    ext = np.concatenate([x[-k:], x])
    dark = filt(ext, [bq_lowpass(950, 0.7), bq_lowpass(1400, 0.6)])[k: k + L]
    clear = filt(ext, [bq_lowpass(3000, 0.7)])[k: k + L]
    t = np.arange(L) / SR
    centre, width = t_of(14, 1.5), 2.2 * BAR
    d = (t - centre + LOOP_S / 2) % LOOP_S - LOOP_S / 2        # circular distance from the centre
    w = 0.15 + 0.85 * np.exp(-0.5 * (d / (width / 2)) ** 2)
    return dark * (1 - w)[:, None] + clear * w[:, None]


def build(mx: LoopMixer) -> None:
    g = rng(SEED)
    L = mx.L
    choir = np.zeros((L, 2))
    # the men: the roots, loop-wrapped (nobody breathes at the seam), with a fifth above in the low register
    roots = [(n(p), BAR) for p in ROOTS]
    choir += hum_ensemble(roots, voices=14, seed=SEED + 1, register="low", loop=True)[:L] * 1.0
    fifths = [(n(p) + 7, BAR) for p in ROOTS]
    choir += 0.45 * hum_ensemble(fifths, voices=8, seed=SEED + 2, register="low", loop=True)[:L]
    men = choir.copy()
    # the women: the Hush's first phrase (hush_theme_v2 MEL_A), bars 5-12
    line = [(n(p), beats * BEAT) for p, beats, _ in HUSH.MEL_A]
    women = _wrap(L, hum_ensemble(line, voices=12, seed=SEED + 3, register="high", spread=0.9), t_of(5) - 0.2)
    # the stones: the mouths open, u-o-a, on F then E
    stones = np.zeros((L, 2))
    for ci, (bar, chord) in enumerate(STONES):
        dur = 2 * BAR
        for vi, p in enumerate(chord):
            ph = [(v, f * dur) for v, f in VOWELS]
            x = sing(ph, [(n(p), dur)], vel=0.7 * g.uniform(0.9, 1.05), seed=SEED + 100 + 10 * ci + vi,
                     scale=1.0 if n(p) < 57 else 1.15, tilt=1.8, breath=0.08, vib_cents=14.0,
                     vib_rate=float(g.uniform(4.4, 5.4)), release=0.9)
            pan = -0.7 + 0.28 * vi
            th = (pan + 1) * np.pi / 4
            stones += _wrap(L, np.stack([x * np.cos(th), x * np.sin(th)], axis=1),
                            t_of(bar) - 0.3 + float(g.normal(0, 0.06)))
    # the Cantor: one alto, far off, on the Hush's first cell
    pits = [(n(p), b * BEAT) for p, b in CELL]
    total = sum(d for _, d in pits)
    x = sing([("a", total * 0.7), ("o", total * 0.3)], pits, vel=0.6, seed=SEED + 200, scale=1.17, tilt=1.7,
             breath=0.1, vib_cents=20.0, vib_rate=5.0, release=1.0)
    cantor = _wrap(L, x * 0.9, t_of(13, 1))
    for bus, sig in (("men", men), ("women", women), ("stones", stones), ("cantor", cantor)):
        mx.add(bus, under_water(sig), 0.0)
    # the deep
    for bar, v in ((1, 0.42), (9, 0.32)):
        mx.add("gong", large_gong(n("A1"), v, seed=SEED + 300 + bar, t60=11.0), t_of(bar), pan=-0.05)
    for i in range(22):
        ts = float(g.uniform(0, LOOP_S))
        b = bubble(float(g.uniform(2.5, 6.0)), float(g.uniform(0.3, 0.8)), rise=0.2)
        mx.add("bubbles", b, ts, pan=float(g.uniform(-0.8, 0.8)))


def render(out_path: str = OUT, verbose: bool = True, stats: dict | None = None) -> dict:
    mx = LoopMixer(intro_s=0.0, loop_s=LOOP_S, preroll_s=14.0)
    G = GAINS
    mx.bus("women", G["women"], send=0.6)
    mx.bus("men", G["men"], send=0.55, process=lambda x: filt(x, [bq_highpass(60, 0.7)]))
    mx.bus("stones", G["stones"], send=0.7)
    mx.bus("cantor", G["cantor"], send=0.8)
    mx.bus("gong", G["gong"], send=0.5, process=lambda x: filt(x, [bq_lowpass(700, 0.7)]))
    mx.bus("bubbles", G["bubbles"], send=0.4, process=lambda x: filt(x, [bq_lowpass(1500, 0.7)]))
    build(mx)
    amphitheatre = ModFDNReverb(rt60=6.5, rt60_high=1.4, predelay=0.07, size=1.8, mod_depth=14.0, mod_rate=0.22,
                                early_level=0.2, lowcut=70.0, seed=SEED % 9973)
    _, loop = mx.render(reverb=amphitheatre, reverb_return_db=-1.5)
    lead_in = int(round(LEAD_IN_BEATS * BEAT * SR))
    loop = np.roll(loop, lead_in, axis=0)
    rep: dict = {}
    _, loop = master_loop(np.zeros((0, 2)), loop, TARGET_LUFS, ceiling_db=-2.0, report=rep)
    L = len(loop)
    write_ogg(out_path, loop, quality=QUALITY, tags={"LOOPSTART": "0", "LOOPLENGTH": str(L)})
    write_loop_sidecar(os.path.splitext(out_path)[0] + ".loop.json", SR, 0, L, BPM, 3,
                       extra={"loop_bars": BARS, "downbeat_offset_s": lead_in / SR})
    m = measure(loop)
    if stats is not None:
        stats["bus_lufs"] = dict(mx.bus_lufs)
        stats["limiter"] = rep
    if verbose:
        print(f"drowned_choir: {m['seconds']:.2f}s  {m['integrated_lufs']:.2f} LUFS  TP {m['true_peak_dbtp']:.2f} dBTP"
              f"  limiter {rep}")
        print("  buses", {k: round(v, 1) for k, v in mx.bus_lufs.items()})
    return m


if __name__ == "__main__":
    render(sys.argv[1] if len(sys.argv) > 1 else OUT)
