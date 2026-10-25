"""`ashcrown`: Ch5, the Ashcrown temple under the falling ash (M3-AUD-19; act_outline Ch5): an 80 s seamless loop.

Original composition for this project (SPEC §2, §9). The flute's call, its answers, the copper-bowl figures, the
drone and the gong cycle below were written for this temple and are not derived from any existing tune.
Original-material check: the tune is built from two cells of our own (a rising call, Bb-C-Db held, and its falling
answer, Eb-Db-Bb) that come from this cue's scale, not from any melody we know; the ritual style (a hummed drone, a
slow gong cycle, a breathy flute over it) is evoked, never quoted. Nothing here is borrowed from another cue, except
the instruments and the shared idea of copper on the mountain.

The brief: Ashcrown is the stair-mountain above Pemakar, dark volcanic stone with copper veins and an ash plume,
and the Cinder Matron's home. Its trial is to catch a strike from the plume at the crown and walk it down the
copper veins tier by tier before it fades (Asha binds Kahre, Lightning, here). Warm-dark, ritual, smouldering: the
heat is under the stone, not on show. It is the same mountain as the Terraces of Ash and the same fight as the
Cinder Matron, so it shares their copper (kettle gongs, a large gong) and the terraces' scale: F Gb Bb C Db are all
in this cue's B-flat minor, so the temple sounds like the festival's grave notes heard from the top of the stair.

B-flat minor (Aeolian: Bb C Db Eb F Gb Ab; the F chord at the cadences takes A natural), 4/4 at 60 BPM (a bar is
4 s), 20 bars. A different place from every earlier cue: the slowest metred loop in Act I, and the only one in
B-flat minor.

Ensemble (all synthesized; no samples):
* breath flute in its warm middle (Db4-Bb5), breathy and close: the tune, a call and its answer;
* copper bowls: soft, long, slowly beating bars (a soft-mallet metallophone) in short falling figures, more of
  them where the flute rests; they stand for the copper veins carrying the strike down the mountain;
* the embers: a dark low string pad on root and fifth that swells and sinks with each chord (the heat under the
  crust); a men's hum on Bb and F from the B section (the Order hums; only Cantors sing, bible §4);
* copper: a kettle gong on beats 1 and 3, a large gong every four bars; a big drum's slow heartbeat on 1 and a
  frame drum's ghost on the "and" of 4 (the processional step); in B a low rumble of the plume swells under bars
  13 and 15.

Form (bars): 1-4 the embers (pad, gongs, bowls; no tune) | 5-12 A, the flute (call, answer, call higher, the F
cadence) | 13-16 B, higher, the hum enters and the plume rumbles | 17-20 A', the call once more and a falling
close to F, which leads back to bar 1's B-flat minor.

Loop: LOOPSTART = 0 and LOOPLENGTH = the whole file. The file starts a sixteenth before bar 1's downbeat (the
sidecar's `downbeat_offset_s`), so the wrap seam falls in a quiet sixteenth.

Render:  python3 assets_src/music/ashcrown.py   (or tools/audio/render_all.py --only ashcrown)
"""
from __future__ import annotations

import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools", "audio"))

import numpy as np  # noqa: E402

from synth.drums import big_drum, frame_drum  # noqa: E402
from synth.dsp import SR, bq_highpass, bq_lowpass, bq_peak, filt, rng  # noqa: E402
from synth.gongs import kettle_gong, large_gong  # noqa: E402
from synth.looping import LoopMixer, master_loop, write_loop_sidecar  # noqa: E402
from synth.metallophone import metallophone_note  # noqa: E402
from synth.mixer import measure, write_ogg  # noqa: E402
from synth.pad import pad_chord, string_body  # noqa: E402
from synth.reverb import ModFDNReverb  # noqa: E402
from synth.score import n  # noqa: E402
from synth.voice import hum_ensemble  # noqa: E402
from synth.winds import breath_flute  # noqa: E402

OUT = os.path.join(ROOT, "assets", "audio", "music", "ashcrown.ogg")
SEED = 20261241
TARGET_LUFS = -16.0
BPM = 60.0
BEAT = 60.0 / BPM
BAR = 4 * BEAT
BARS = 20
LOOP_S = BARS * BAR
## breath_flute's tone starts after its breath (0.05-0.08 s): notes are placed this much early.
FLUTE_PRE = 0.065
## the file starts this many beats before bar 1's downbeat (see render())
LEAD_IN_BEATS = 0.25

CHORDS = (["Bbm", "Bbm", "Gb", "Bbm"]
          + ["Bbm", "Gb", "Db", "Ab", "Bbm", "Gb", "Ebm", "F"]
          + ["Gb", "Db", "Ebm", "F"]
          + ["Bbm", "Gb", "Ebm", "F"])
SECTION = ["I"] * 4 + ["A"] * 8 + ["B"] * 4 + ["A2"] * 4
## the pad: root, fifth, octave (and the third, low and soft), in the low register
PAD = {"Bbm": "Bb1 F2 Bb2 Db3", "Gb": "Gb1 Db2 Gb2 Bb2", "Db": "Db2 Ab2 Db3 F3", "Ab": "Ab1 Eb2 Ab2 C3",
       "Ebm": "Eb2 Bb2 Eb3 Gb3", "F": "F1 C2 F2 A2"}
GONG = {"Bbm": ("Bb2", "F3"), "Gb": ("Gb2", "Db3"), "Db": ("Db3", "Ab3"), "Ab": ("Ab2", "Eb3"),
        "Ebm": ("Eb3", "Bb2"), "F": ("F2", "C3")}
## the copper bowls' notes: the scale's upper tones; the F bars borrow A natural
BOWLS = ["Bb4", "C5", "Db5", "F5", "Gb5", "Ab5", "Bb5"]
BOWLS_F = ["A4", "C5", "Eb5", "F5", "A5", "C6"]

## the tune: one list per bar of (pitch | None, beats)
TUNE_A = [
    [("Bb4", 1.5), ("C5", .5), ("Db5", 2)],                  # the call
    [("Eb5", 1), ("Db5", 1), ("Bb4", 2)],                    # its answer
    [("Ab4", 1.5), ("Bb4", .5), ("Db5", 1), ("F5", 1)],      # the call, reaching
    [("Eb5", 3), (None, 1)],
    [("F5", 1.5), ("Gb5", .5), ("F5", 1), ("Db5", 1)],
    [("Eb5", 1), ("Db5", .5), ("C5", .5), ("Bb4", 2)],
    [("Gb4", 1), ("Ab4", 1), ("Bb4", 1), ("Db5", 1)],
    [("C5", 3), (None, 1)],                                  # the F cadence, open
]
TUNE_B = [
    [("Bb5", 2), ("Ab5", 1), ("Gb5", 1)],
    [("F5", 2), ("Ab5", 1), ("F5", 1)],
    [("Eb5", 1), ("F5", 1), ("Gb5", 1), ("Eb5", 1)],
    [("F5", 2), ("Eb5", 1), ("C5", 1)],
]
TUNE_A2 = [
    [("Bb4", 1.5), ("C5", .5), ("Db5", 2)],
    [("Eb5", 1), ("Db5", 1), ("Bb4", 2)],
    [("Gb4", 1), ("F4", 1), ("Eb4", 1), ("Db4", 1)],
    [("C4", 1), ("F4", 2), (None, 1)],
]
## the men's hum in B and A' (one pitch a bar): Bb and F, the drone of the temple, leaning on the chord
HUM = ["Bb2", "Ab2", "Bb2", "A2", "Bb2", "Bb2", "Bb2", "A2"]


def t_of(bar: int, beat: float = 0.0) -> float:
    return (bar - 1) * BAR + beat * BEAT


def add_tune(mx: LoopMixer, bars: list, start_bar: int, seed: int, vel: float, pan: float = -0.06) -> None:
    g = rng(seed)
    first = True
    for i, bar in enumerate(bars):
        pos = t_of(start_bar + i)
        for p, beats in bar:
            d = beats * BEAT
            if p is None:
                pos += d
                first = True
                continue
            v = vel * g.uniform(0.94, 1.04) * (1.04 if beats >= 2 else 1.0)
            x = breath_flute(n(p), d * 0.96 + 0.03, v, seed=seed + int(round(pos * 1000)), breath=0.55,
                             scoop_cents=50.0 if first else 15.0, vib_cents=11.0 if beats >= 2 else 4.0,
                             vib_rate=4.0, swell=0.3 if beats >= 2 else 0.0, attack=0.10 if first else 0.05,
                             release=0.45, beta=0.5)
            mx.add("flute", x, pos - FLUTE_PRE + float(g.normal(0, 0.005)), pan=pan)
            pos += d
            first = False


def add_bowls(mx: LoopMixer, g, bar: int, chord: str, count: int) -> None:
    """Short falling figures on the copper bowls, scattered across the bar."""
    pool = BOWLS_F if chord == "F" else BOWLS
    for j in range(count):
        top = int(g.integers(2, len(pool)))
        length = int(g.integers(2, 4))
        start = t_of(bar, float(g.uniform(0.4, 1.4)) + 2.0 * j)
        pan = float(g.uniform(-0.6, 0.6))
        step = BEAT * float(g.uniform(0.45, 0.7))
        for k in range(length):
            idx = top - k
            if idx < 0:
                break
            x = metallophone_note(n(pool[idx]), 0.24 * g.uniform(0.85, 1.05) * (1 - 0.12 * k),
                                  seed=SEED + 5000 + 10 * bar + 100 * j + k, decay=5.0, hardness=0.12,
                                  ombak_hz=1.6)
            mx.add("bowls", x, start + k * step + float(g.normal(0, 0.01)), pan=pan - 0.05 * k)


def rumble(seconds: float, seed: int) -> np.ndarray:
    """The plume: a low, slowly swelling band of noise (felt more than heard)."""
    g = rng(seed)
    N = int(seconds * SR)
    x = filt(g.standard_normal(N), [bq_lowpass(140, 0.7), bq_lowpass(140, 0.7), bq_highpass(35, 0.7)])
    t = np.arange(N) / N
    env = np.sin(np.pi * t) ** 2
    x = x * env / (np.abs(x).max() + 1e-9)
    side = filt(g.standard_normal(N), [bq_lowpass(140, 0.7), bq_lowpass(140, 0.7), bq_highpass(35, 0.7)])
    side = side * env / (np.abs(side).max() + 1e-9)
    return np.stack([x + 0.35 * side, x - 0.35 * side], axis=1)


def build(mx: LoopMixer) -> None:
    g = rng(SEED)
    for bar, (ch, sec) in enumerate(zip(CHORDS, SECTION), start=1):
        # the embers: a pad chord per bar, swelling in and sinking out
        x = pad_chord([n(p) for p in PAD[ch].split()], BAR * 0.92, 0.5, seed=SEED + 200 + bar, voices=4,
                      attack=1.6, release=1.6, width=0.7)
        mx.add("pad", x, t_of(bar) - 0.3)
        # copper: a kettle gong on 1 and 3
        lo, hi = GONG[ch]
        mx.add("gong", kettle_gong(n(lo), 0.30 * g.uniform(0.92, 1.04), seed=SEED + 400 + bar, t60=3.2), t_of(bar),
               pan=0.25)
        mx.add("gong", kettle_gong(n(hi), 0.20 * g.uniform(0.9, 1.05), seed=SEED + 450 + bar, t60=2.6),
               t_of(bar, 2), pan=-0.3)
        # the heartbeat: the big drum on 1, a frame-drum ghost on the "and" of 4 (into the next bar)
        mx.add("drums", big_drum(0.34 if bar % 4 == 1 else 0.26, variant=bar, seed=SEED + 2), t_of(bar), pan=0.0)
        if sec != "I" or bar >= 3:
            x = frame_drum("ghost", 0.16 * g.uniform(0.9, 1.1), variant=bar, size=1.25, seed=SEED + 1)
            mx.add("drums", x, t_of(bar, 3.5) + float(g.normal(0, 0.006)), pan=-0.12)
            x = frame_drum("dum", 0.22 * g.uniform(0.9, 1.1), variant=bar + 3, size=1.25, seed=SEED + 1)
            mx.add("drums", x, t_of(bar, 2) + float(g.normal(0, 0.006)), pan=-0.08)
        # the bowls: more where the flute rests
        count = 2 if sec == "I" else (1 if bar in (8, 12, 16, 19, 20) or bar % 2 == 0 else 0)
        add_bowls(mx, g, bar, ch, count)
    for bar in (1, 5, 9, 13, 17):
        mx.add("gong", large_gong(n("Bb1"), 0.32 if bar in (1, 13) else 0.24, seed=SEED + 500 + bar, t60=9.0),
               t_of(bar), pan=-0.1)
    # the plume, under B
    for bar in (13, 15):
        mx.add("rumble", rumble(2 * BAR, SEED + 700 + bar), t_of(bar) - 0.5)
    # the tune
    add_tune(mx, TUNE_A, 5, SEED + 600, 0.52)
    add_tune(mx, TUNE_B, 13, SEED + 650, 0.56)
    add_tune(mx, TUNE_A2, 17, SEED + 680, 0.50)
    # the hum, under B and A'
    line = [(n(p), BAR) for p in HUM]
    men = hum_ensemble(line, voices=12, seed=SEED + 11, register="low", spread=0.85)
    env = np.ones(len(men))
    k = int(3.0 * SR)
    env[:k] = np.linspace(0, 1, k) ** 2
    s = int(7.4 * BAR * SR)
    env[s:] = np.exp(-np.arange(len(env) - s) / SR / 1.0)
    mx.add("hum", men * env[:, None], t_of(13) - 0.2)


# Bus gains were set from measured bus loudness (render(stats=...)["bus_lufs"]) for these levels relative to the
# flute (0 LU, measured over the whole loop; it rests in the first four bars): pad -9, copper bowls -9, the hum -8
# (it sounds only in the last eight bars), gongs -10, drums -12, the plume -16.
def render(out_path: str = OUT, verbose: bool = True, stats: dict | None = None) -> dict:
    mx = LoopMixer(intro_s=0.0, loop_s=LOOP_S, preroll_s=12.0)
    mx.bus("flute", 0.0, send=0.36, process=lambda x: filt(x, [bq_highpass(160, 0.7), bq_peak(1500, 1.5, 1.0),
                                                                 bq_lowpass(6000, 0.7)]))
    mx.bus("pad", 4.4, send=0.45, process=lambda x: string_body(x, cutoff=1300.0))
    mx.bus("bowls", 2.9, send=0.60)
    mx.bus("hum", -1.1, send=0.70)
    mx.bus("gong", -5.8, send=0.45)
    mx.bus("drums", -0.8, send=0.30, process=lambda x: filt(x, [bq_lowpass(2500, 0.7)]))
    mx.bus("rumble", -25.3, send=0.20)
    build(mx)
    hall = ModFDNReverb(rt60=3.8, rt60_high=1.3, predelay=0.035, size=1.25, mod_depth=9.0, mod_rate=0.4,
                        early_level=0.25, lowcut=90.0, seed=SEED % 9973)
    _, loop = mx.render(reverb=hall, reverb_return_db=-2.5)
    # The loop is periodic, so it may start anywhere: a sixteenth before bar 1's downbeat, so the wrap seam falls in
    # a quiet sixteenth instead of on the gongs, the big drum and the pad at once.
    lead_in = int(round(LEAD_IN_BEATS * BEAT * SR))
    loop = np.roll(loop, lead_in, axis=0)
    rep: dict = {}
    _, loop = master_loop(np.zeros((0, 2)), loop, TARGET_LUFS, ceiling_db=-2.0, report=rep)
    L = len(loop)
    write_ogg(out_path, loop, quality=3.0, tags={"LOOPSTART": "0", "LOOPLENGTH": str(L)})
    write_loop_sidecar(os.path.splitext(out_path)[0] + ".loop.json", SR, 0, L, BPM, 4,
                       extra={"loop_bars": BARS, "downbeat_offset_s": lead_in / SR})
    m = measure(loop)
    if stats is not None:
        stats["bus_lufs"] = dict(mx.bus_lufs)
        stats["limiter"] = rep
    if verbose:
        print(f"ashcrown: {m['seconds']:.2f}s  {m['integrated_lufs']:.2f} LUFS  TP {m['true_peak_dbtp']:.2f} dBTP"
              f"  limiter {rep}")
        print("  buses", {k: round(v, 1) for k, v in mx.bus_lufs.items()})
    return m


if __name__ == "__main__":
    render(sys.argv[1] if len(sys.argv) > 1 else OUT)
