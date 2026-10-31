"""`sefir_theme`: High Warden Sefir Aurane's motif and its first full statement (M3-AUD-03; act_outline.md Ch6),
a 71 s seamless loop.

Original composition for this project (SPEC §2); the motif was written for this character and is not derived from
any existing melody. Ch6: his white barge is poled up the shoal channel through the smoke and leaves no wake; he
puts out a fire with one sentence and is gentle, correct, and terrible. The Order hums; only Cantors sing (bible §4),
so his music is hummed by a congregation and rung on glass: nothing struck hard, nothing with an attack (no wake).

**The motif** (C major, the only cue in it: the Order's pure key): G4 C5 D5 E5 D5 C#5. It rises in calm, consonant
steps toward D, and then slips a half step to C#, held, over an F major chord: a leading tone that never leads
anywhere, the one wrong note in a beautiful line. Where the Hush falls by step from a long note, Sefir's line rises
by step to one: the same shape, turned upward, which the player should feel before they can name it.

Statement (4/4 at 54 BPM, 16 bars): 1-2 a men's hum on C and G swells in | 3-6 the motif on a glass harmonica, the
women humming it a fifth below | 7-8 the harmony drifts C -> Ab -> F under the held C# | 9-12 the congregation hums
the motif an octave down while the glass answers with its first three notes turned downward | 13-16 the hum on C
with an F# laid over it (a cold Lydian colour), fading into the wrap.

**Variants for later chapters** (documented, rendered when their scenes exist): (a) the motif alone on glass, for
his entrances; (b) hummed only, when the Order is present without him; (c) under his fight, the motif's six notes as
a 5/4 ostinato in low bells, the C# struck on the downbeat.

Render:  python3 assets_src/music/sefir_theme.py   (or tools/audio/render_all.py)
"""
from __future__ import annotations

import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools", "audio"))

import numpy as np  # noqa: E402

from synth.dsp import SR, bq_highpass, bq_lowpass, filt, midi_to_hz, rng, smooth_noise  # noqa: E402
from synth.looping import LoopMixer, master_loop, write_loop_sidecar  # noqa: E402
from synth.mixer import measure, write_ogg  # noqa: E402
from synth.reverb import ModFDNReverb  # noqa: E402
from synth.score import n  # noqa: E402
from synth.voice import hum_ensemble  # noqa: E402

OUT = os.path.join(ROOT, "assets", "audio", "music", "sefir_theme.ogg")
SEED = 20261113
TARGET_LUFS = -16.0
BPM = 54.0
BEAT = 60.0 / BPM
BAR = 4 * BEAT
BARS = 16
LOOP_S = BARS * BAR
MOTIF = [("G4", 2), ("C5", 2), ("D5", 1), ("E5", 1), ("D5", 4), ("C#5", 6)]       # beats
ANSWER = [("D5", 2), ("C5", 2), ("G4", 4)]
FIFTH_BELOW = {"G4": "C4", "C5": "F4", "D5": "G4", "E5": "A4", "C#5": "F#4"}


def t_of(bar: int, beat: float = 0.0) -> float:
    return (bar - 1) * BAR + beat * BEAT


def glass(m: float, dur: float, vel: float, seed: int, sr: int = SR) -> np.ndarray:
    """A glass harmonica: a near-pure tone that swells in (no attack), a faint octave, a slow shimmer; mono."""
    g = rng(seed)
    f = midi_to_hz(m)
    N = int((dur + 2.5) * sr)
    t = np.arange(N) / sr
    env = np.clip(t / 0.45, 0, 1) ** 2 * np.where(t > dur, np.exp(-(t - dur) / 0.8), 1.0)
    vib = 1 + 0.0012 * np.sin(2 * np.pi * 4.2 * t + g.uniform(0, 6)) * np.clip(t / 1.5, 0, 1)
    wob = 1 + 0.06 * smooth_noise(N, 1.3, g, sr)
    ph = 2 * np.pi * f * np.cumsum(vib) / sr
    x = np.sin(ph) + 0.18 * np.sin(2 * ph + 0.3) + 0.05 * np.sin(3 * ph + 1.1)
    k = int(0.05 * sr)
    out = vel * env * wob * x
    out[-k:] *= np.linspace(1, 0, k)
    return 0.3 * out


def _line(notes: list, start_bar: int) -> list[tuple[float, float, float]]:
    out, pos = [], 0.0
    for p, beats in notes:
        out.append((t_of(start_bar, pos), beats * BEAT, n(p)))
        pos += beats
    return out


def build(mx: LoopMixer) -> None:
    g = rng(SEED)
    drone = [(n("C3"), 2 * BAR), (n("C3"), 4 * BAR), (n("C3"), 2 * BAR), (n("C3"), 4 * BAR), (n("C3"), 4 * BAR)]
    men = hum_ensemble(drone, voices=14, seed=SEED + 1, register="low", loop=True)
    mx.add("hum", men, 0.0)
    fifth = hum_ensemble([(n("G2"), LOOP_S)], voices=8, seed=SEED + 2, register="low", loop=True)
    mx.add("hum", fifth * 0.6, 0.0)
    # bars 7-8: the harmony drifts C -> Ab -> F (low hum on the new roots, over the held C#)
    for bar, root in ((7, "Ab2"), (8, "F2")):
        x = hum_ensemble([(n(root), BAR)], voices=8, seed=SEED + 10 + bar, register="low")
        env = np.ones(len(x))
        k = int(0.8 * SR)
        env[:k] = np.linspace(0, 1, k) ** 2
        env[-k:] *= np.linspace(1, 0, k) ** 2
        mx.add("hum_root", x * env[:, None], t_of(bar) - 0.3)
    for i, (t0, d, m) in enumerate(_line(MOTIF, 3)):
        mx.add("glass", glass(m, d * 0.98, 0.8, seed=SEED + 100 + i), t0, pan=-0.1)
    women = hum_ensemble([(n(FIFTH_BELOW[p]), b * BEAT) for p, b in MOTIF], voices=8, seed=SEED + 3, register="high",
                         spread=0.8)
    mx.add("hum_hi", women, t_of(3) - 0.2)
    congregation = hum_ensemble([(n(p) - 12, b * BEAT) for p, b in MOTIF], voices=12, seed=SEED + 4, register="low",
                                spread=0.9)
    mx.add("hum_motif", congregation, t_of(9) - 0.2)
    for i, (t0, d, m) in enumerate(_line(ANSWER, 10)):
        mx.add("glass", glass(m + 12, d * 0.98, 0.55, seed=SEED + 200 + i), t0, pan=0.35)
    for i, (t0, d, m) in enumerate(_line([("F#5", 12)], 13)):
        mx.add("glass", glass(m, d, 0.45, seed=SEED + 300 + i), t0 + float(g.uniform(0, 0.1)), pan=0.2)


# Bus gains from measured bus loudness: the glass line at L, the men's hum L-5, the women's hum L-6, the hummed
# motif (bars 9-12) L-2, the drifting roots L-6.
def render(out_path: str = OUT, verbose: bool = True, stats: dict | None = None) -> dict:
    mx = LoopMixer(intro_s=0.0, loop_s=LOOP_S, preroll_s=10.0)
    mx.bus("glass", 0.0, send=0.55, process=lambda x: filt(x, [bq_highpass(200, 0.7)]))
    mx.bus("hum", 5.3, send=0.6, process=lambda x: filt(x, [bq_lowpass(2500, 0.7)]))
    mx.bus("hum_hi", 2.1, send=0.7)
    mx.bus("hum_motif", 3.4, send=0.7)
    mx.bus("hum_root", 6.2, send=0.6)
    build(mx)
    # width 0.7 (the Lead's 10-30 21:25 accessibility item, tools/audio/mono_check.py): at full width the hall's late
    # field under the bar-9 hum went out of phase for a moment and lost 8.5 dB in mono; at 0.7 the worst moment is a
    # 6.4 dB thinning and the cue keeps its hall.
    hall = ModFDNReverb(rt60=4.5, rt60_high=1.8, predelay=0.04, size=1.3, mod_depth=10.0, mod_rate=0.35,
                        early_level=0.2, lowcut=80.0, width=0.7, seed=SEED % 9973)
    _, loop = mx.render(reverb=hall, reverb_return_db=-1.0)
    rep: dict = {}
    _, loop = master_loop(np.zeros((0, 2)), loop, TARGET_LUFS, ceiling_db=-2.0, report=rep)
    L = len(loop)
    write_ogg(out_path, loop, quality=3.0, tags={"LOOPSTART": "0", "LOOPLENGTH": str(L)})
    write_loop_sidecar(os.path.splitext(out_path)[0] + ".loop.json", SR, 0, L, BPM, 4)
    m = measure(loop)
    if stats is not None:
        stats["bus_lufs"] = dict(mx.bus_lufs)
    if verbose:
        print(f"sefir_theme: {m['seconds']:.2f}s  {m['integrated_lufs']:.2f} LUFS  TP {m['true_peak_dbtp']:.2f} dBTP"
              f"  limiter {rep}")
        print("  buses", {k: round(v, 1) for k, v in mx.bus_lufs.items()})
    return m


if __name__ == "__main__":
    render()
