"""`unlamped`: Ch15 "Unlamped", the open sea at night aboard the bridal barge (M3-AUD-805; act_outline Ch15): a 61 s
seamless loop. An Act II sketch, for the human to judge the direction.

Original composition for this project (SPEC §2, §9). Original-material check: the flute's line (Bb held, Cb-Bb-Gb-F
falling to Eb; then Gb-Ab-Bb rising to Eb and sinking to Ab) and the rocking two-chord pad were written for this
cue; they share no phrase with the game's other themes and no melody we know. The style evoked is a slow, unmetred
nocturne over a drone; nothing is quoted.

The brief: the barge carries no lamp (wedding barges never do), and nobody dares strike one. They drift south through
the night with Tobin's body under Merel's bridal cloth. The only light is the sea-glow. Past midnight the barge drifts
over a shoal where an old Rising's dead are still held, and the motes come up off the water toward Kerrid. Dark,
drifting, and grieving, with no pulse at all: nobody is rowing.

So: E-flat minor (the darkest key in the score so far), notated 4/4 at 51 BPM (a bar is 4.71 s), 13 bars, an odd
number, so the loop never settles into pairs. Nothing marks a beat. The pad rocks between E-flat minor and C-flat
over a held E-flat, the way a barge rocks with nobody steering. The sea is filtered noise that swells once a bar.
The sea-glow is soft glass bars, always *rising* (the held dead come up off the water, as they drift toward Kerrid),
sparse in the first half and gathering in bars 8-11. The flute is low, in its breathy bottom octave: someone
keeping a vigil, not a song.

Ensemble (all synthesized; no samples):
* the sea: band-limited noise, a low wash and a high hiss, swelling once a bar (exactly periodic over the loop);
* a bowed low drone on E-flat (its harmonics, slowly beating, very dark), and the rocking pad (Ebm, Cb/Eb,
  Ebm, Abm/Eb ...);
* sea-glow: soft glass bars (metallophone, hardness 0.1, long), rising figures of two to four notes;
* breath flute, low register (Eb4-Eb5): the vigil, bars 3-6 and 8-12.

Form (bars): 1-2 the sea and the drone | 3-6 the flute's first line, sinking to Eb | 7 the sea alone, a few motes |
8-12 the motes gather; the flute rises to Eb5 and sinks to Ab, unresolved | 13 the drone, which is bar 1.

Loop: LOOPSTART = 0 and LOOPLENGTH = the whole file. The file starts a sixteenth before bar 1's downbeat (the
sidecar's `downbeat_offset_s`); nothing is struck there, so the seam falls inside the sea's wash.

Render:  python3 assets_src/music/unlamped.py   (or tools/audio/render_all.py --only unlamped)
"""
from __future__ import annotations

import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools", "audio"))

import numpy as np  # noqa: E402

from synth.dsp import SR, bq_bandpass, bq_highpass, bq_lowpass, bq_peak, filt, midi_to_hz, rng  # noqa: E402
from synth.looping import LoopMixer, master_loop, write_loop_sidecar  # noqa: E402
from synth.metallophone import metallophone_note  # noqa: E402
from synth.mixer import measure, write_ogg  # noqa: E402
from synth.pad import pad_chord, string_body  # noqa: E402
from synth.reverb import ModFDNReverb  # noqa: E402
from synth.score import n  # noqa: E402
from synth.winds import breath_flute  # noqa: E402

OUT = os.path.join(ROOT, "assets", "audio", "music", "unlamped.ogg")
SEED = 20261513
TARGET_LUFS = -16.0
BPM = 51.0
BEAT = 60.0 / BPM
BAR = 4 * BEAT
BARS = 13
LOOP_S = BARS * BAR
## breath_flute's tone starts after its breath (0.05-0.08 s): notes are placed this much early.
FLUTE_PRE = 0.065
## the file starts this many beats before bar 1's downbeat (see render())
LEAD_IN_BEATS = 0.25
QUALITY = 3.0  # mix.md §5's sparse-cue quality

CHORDS = ["Ebm", "Cb", "Ebm", "Cb", "Ebm", "Abm", "Ebm", "Cb", "Abm", "Cb", "Ebm", "Abm", "Ebm"]
PAD = {"Ebm": "Bb2 Gb3 Bb3", "Cb": "Gb2 Eb3 Gb3", "Abm": "Ab2 Eb3 Cb4"}
## sea-glow: (bar, beat, rising notes)
MOTES = [(2, 2.5, "Bb5 Eb6"), (4, 1.0, "Gb5 Bb5"), (5, 3.0, "Eb6 Gb6"), (7, 0.5, "Bb5 Db6 Eb6"),
         (7, 2.5, "Gb5 Bb5 Eb6"), (8, 1.5, "Eb6 Gb6 Bb6"), (9, 0.0, "Ab5 Cb6 Eb6"), (9, 2.0, "Bb5 Eb6 Gb6"),
         (10, 0.5, "Gb5 Bb5 Db6 Eb6"), (10, 3.0, "Cb6 Eb6"), (11, 1.0, "Eb6 Gb6 Bb6"), (11, 3.0, "Bb5 Db6"),
         (12, 1.5, "Ab5 Cb6 Eb6")]
## the flute's vigil: one list per bar of (pitch | None, beats)
VIGIL = {
    3: [("Bb4", 3), ("Cb5", 1)],
    4: [("Bb4", 2), ("Gb4", 2)],
    5: [("F4", 4)],
    6: [("Eb4", 3), (None, 1)],
    8: [(None, 1), ("Gb4", 1.5), ("Ab4", 1.5)],
    9: [("Bb4", 3), ("Db5", 1)],
    10: [("Eb5", 4)],
    11: [("Db5", 2), ("Bb4", 2)],
    12: [("Ab4", 3), (None, 1)],
}

# Bus gains were set from measured bus loudness (render(stats=...)["bus_lufs"], the whole loop) for these levels
# relative to the flute (0 LU; it plays nine bars of thirteen): the rocking pad -8, the drone -9, the sea -9, the
# sea-glow -12.
GAINS = {"flute": 0.0, "pad": 3.6, "drone": -21.6, "sea": -19.0, "glow": -1.7}


def t_of(bar: int, beat: float = 0.0) -> float:
    return (bar - 1) * BAR + beat * BEAT


def _circ(x: np.ndarray, sections, pre_s: float = 2.0) -> np.ndarray:
    """Filter a periodic signal (one cycle) in steady state: its own last seconds are fed in first."""
    k = int(pre_s * SR)
    y = filt(np.concatenate([x[-k:], x]), sections)
    return y[k: k + len(x)]


def sea(L: int, seed: int) -> np.ndarray:
    """The open sea at night: a low wash and a quieter hiss, each swelling once a bar (13 swells a loop, the hiss a
    little behind the wash, the way a wave breaks after it lifts). Exactly periodic over L samples. Stereo."""
    g = rng(seed)
    t = np.arange(L) / SR
    Ls = L / SR
    out = np.zeros((L, 2))
    # one sea, heard from the middle of it: the two channels share most of their noise (a wide but coherent wash)
    wash0 = _circ(g.standard_normal(L), [bq_lowpass(380, 0.7), bq_highpass(40, 0.7)])
    hiss0 = _circ(g.standard_normal(L), [bq_bandpass(2600, 0.5), bq_lowpass(5000, 0.7)])
    for ch in range(2):
        wash = 0.85 * wash0 + 0.5 * _circ(g.standard_normal(L), [bq_lowpass(380, 0.7), bq_highpass(40, 0.7)])
        hiss = 0.9 * hiss0 + 0.3 * _circ(g.standard_normal(L), [bq_bandpass(2600, 0.5), bq_lowpass(5000, 0.7)])
        ph = g.uniform(0, 0.4)
        lift = 0.55 + 0.45 * np.cos(2 * np.pi * (BARS * t / Ls - ph)) ** 2
        brk = (0.5 + 0.5 * np.cos(2 * np.pi * (BARS * t / Ls - ph - 0.18))) ** 3
        slow = 0.85 + 0.15 * np.cos(2 * np.pi * 3 * t / Ls + g.uniform(0, 6.28))
        out[:, ch] = (wash / np.std(wash) * lift + 0.25 * hiss / np.std(hiss) * brk) * slow
    return out / np.abs(out).max()


def drone(L: int, seed: int) -> np.ndarray:
    """A bowed low E-flat (Eb1 with its octave): harmonics as slowly beating doublets, every frequency snapped to a
    whole number of cycles per loop so the drone is exactly periodic, breathing on a slow cycle. Stereo."""
    g = rng(seed)
    t = np.arange(L) / SR
    Ls = L / SR
    f1 = midi_to_hz(n("Eb1"))
    out = np.zeros((L, 2))
    for k in range(1, 11):
        f = round(f1 * k * Ls) / Ls
        s = round(float(g.uniform(0.08, 0.25)) * Ls) / Ls
        a = (1.0 / k) * (1.6 if k == 2 else 1.0)
        lfo = 1.0 + 0.2 * np.cos(2 * np.pi * int(g.integers(2, 6)) * t / Ls + g.uniform(0, 6.28))
        for ch in range(2):
            ph0, ph1 = g.uniform(0, 2 * np.pi, 2)
            out[:, ch] += a * lfo * 0.5 * (np.sin(2 * np.pi * f * t + ph0) + np.sin(2 * np.pi * (f + s) * t + ph1))
    return out / np.abs(out).max()


def build(mx: LoopMixer) -> None:
    g = rng(SEED)
    mx.add("sea", sea(mx.L, SEED + 1), 0.0)
    mx.add("drone", drone(mx.L, SEED + 2), 0.0)
    for bar, ch in enumerate(CHORDS, start=1):
        x = pad_chord([n(p) for p in PAD[ch].split()], BAR * 0.96, 0.5, seed=SEED + 100 + bar, attack=2.0,
                      release=2.4, voices=3, spread_cents=8.0)
        mx.add("pad", x, t_of(bar) - 0.8)
    for i, (bar, beat, notes) in enumerate(MOTES):
        for j, p in enumerate(notes.split()):
            v = 0.26 * g.uniform(0.8, 1.05) * (0.9 ** j)
            x = metallophone_note(n(p), v, seed=SEED + 500 + 10 * i + j, decay=5.5, hardness=0.1, ombak_hz=1.6)
            mx.add("glow", x, t_of(bar, beat + 0.42 * j) + float(g.normal(0, 0.02)),
                   pan=float(np.clip(-0.6 + 0.12 * i + 0.15 * j, -0.8, 0.8)))
    for bar, notes in VIGIL.items():
        pos, first = t_of(bar), True
        for p, beats in notes:
            d = beats * BEAT
            if p is None:
                pos += d
                first = True
                continue
            x = breath_flute(n(p), d * 0.95 + 0.05, 0.5 * g.uniform(0.95, 1.04), seed=SEED + 700 + int(pos * 100),
                             breath=0.55, scoop_cents=45.0 if first else 15.0, vib_cents=8.0, vib_rate=4.0,
                             swell=0.35 if beats >= 3 else 0.1, attack=0.14 if first else 0.08, release=0.9,
                             beta=0.5)
            mx.add("flute", x, pos - FLUTE_PRE + float(g.normal(0, 0.008)), pan=0.1)
            pos += d
            first = False


def render(out_path: str = OUT, verbose: bool = True, stats: dict | None = None) -> dict:
    mx = LoopMixer(intro_s=0.0, loop_s=LOOP_S, preroll_s=12.0)
    G = GAINS
    mx.bus("flute", G["flute"], send=0.45, process=lambda x: filt(x, [bq_highpass(150, 0.7), bq_peak(900, 1.5, 1.0),
                                                                       bq_lowpass(4500, 0.7)]))
    mx.bus("pad", G["pad"], send=0.5, process=lambda x: string_body(x, cutoff=1100.0))
    mx.bus("drone", G["drone"], send=0.3, process=lambda x: filt(x, [bq_lowpass(700, 0.7)]))
    mx.bus("sea", G["sea"], send=0.15)
    mx.bus("glow", G["glow"], send=0.7, process=lambda x: filt(x, [bq_highpass(400, 0.7), bq_lowpass(5000, 0.7)]))
    build(mx)
    night = ModFDNReverb(rt60=5.5, rt60_high=1.5, predelay=0.06, size=1.6, mod_depth=12.0, mod_rate=0.25,
                         early_level=0.15, lowcut=80.0, seed=SEED % 9973)
    _, loop = mx.render(reverb=night, reverb_return_db=-2.0)
    lead_in = int(round(LEAD_IN_BEATS * BEAT * SR))
    loop = np.roll(loop, lead_in, axis=0)
    rep: dict = {}
    _, loop = master_loop(np.zeros((0, 2)), loop, TARGET_LUFS, ceiling_db=-2.0, report=rep)
    L = len(loop)
    write_ogg(out_path, loop, quality=QUALITY, tags={"LOOPSTART": "0", "LOOPLENGTH": str(L)})
    write_loop_sidecar(os.path.splitext(out_path)[0] + ".loop.json", SR, 0, L, BPM, 4,
                       extra={"loop_bars": BARS, "downbeat_offset_s": lead_in / SR})
    m = measure(loop)
    if stats is not None:
        stats["bus_lufs"] = dict(mx.bus_lufs)
        stats["limiter"] = rep
    if verbose:
        print(f"unlamped: {m['seconds']:.2f}s  {m['integrated_lufs']:.2f} LUFS  TP {m['true_peak_dbtp']:.2f} dBTP"
              f"  limiter {rep}")
        print("  buses", {k: round(v, 1) for k, v in mx.bus_lufs.items()})
    return m


if __name__ == "__main__":
    render(sys.argv[1] if len(sys.argv) > 1 else OUT)
