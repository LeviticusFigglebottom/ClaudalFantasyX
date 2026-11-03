"""`storm_battle`: the fights inside the Undertow's storm (the human's playtest FAST-TRACK, 2026-11-03; M3-AUD-865).
Ch1's scuttlers after the Rising (C1-13) and every fight started in a storm-variant zone (Ch1 Oruvel after the
gulls, Ch8 Corrow and the headland after the beacon) play this in place of the uplifting `battle_standard_v2`.

Original composition for this project (SPEC §2, §9). It is a battle variant of our own `undertow_rising`
(undertow_rising.py, imported, nothing re-typed): its brass line (BRASS), its held clusters (CLUSTERS), its run's
roots (RUN_ROOT), its brass model (low_brass) and the storm's mode, G octatonic (half-whole: G Ab Bb B C# D E F),
which only the Undertow's cues use. No existing melody is quoted or imitated.

The brief: tense, dread, the Undertow's motif; a fight, so it must move, but "it hurries, it never charges"
(undertow_rising's run brief) holds here too: no fanfare, no major chord, no heroic rising sequence.

* **Tempo.** 96 BPM in 4/4, exactly twice the Rising's 48, so a battle bar is half a Rising bar. The brass line keeps
  its own absolute timing (one Rising bar = two battle bars, 5 s) and stays the slow, heavy thing in the room, while
  everything under it runs at the battle's speed. The loop is the Rising's 14 bars as 28 battle bars: 70 s.
* **Stem material, re-voiced for a fight:**
  - the brass line in trombones and tuba as in the Rising, and from bar 17 (the Rising's tritone section, C#) horns
    double it an octave up, so the line comes forward for the loop's second half;
  - the clusters, bowed in sixteenth-note tremolo (6.4 Hz, a whole number of cycles per loop) instead of held;
  - the run: muted low strings in sixteenths leaning on the minor second (G G G Ab), its root following RUN_ROOT;
    from bar 17 the violas double it two octaves up;
  - the pulse, the Rising's limp sped up: the big drum on eighths 1, 4 and 7 of each bar (3 + 3 + 2), frame-drum
    teks on the eighths, ghosts between, a sixteenth-note fill into every fourth bar; the sub heartbeat under the big
    drum's first two strokes; the large gong at bars 1 and 17.
* **Form (bars):** 1-8 the line from G | 9-16 a minor third up, from Bb | 17-24 the tritone, C#, horns and violas in,
  the cluster widest | 25-28 the rise: the brass held on G, the full cluster swelling, the drums rolling into bar 1.
  The intro is the loop's own last two bars (the rise, 5 s), so the first-play splice carries the same tails
  (LoopMixer's rule) and a battle opens on the storm already standing up.

Mastering: -16 LUFS integrated over intro + loop (targets.py `music/*.ogg`), wrap-aware limiting to -2 dBFS
(master_loop), Vorbis q3.5. Plain git under assets/audio/music/ (not an LFS path; about 1.2 MB).

Render:  python3 assets_src/music/storm_battle.py   (or tools/audio/render_all.py --only storm_battle)
"""
from __future__ import annotations

import importlib.util
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools", "audio"))

import numpy as np  # noqa: E402

from synth.drums import big_drum, frame_drum  # noqa: E402
from synth.dsp import SR, bq_highpass, bq_lowpass, filt, rng  # noqa: E402
from synth.electric import bass_note  # noqa: E402
from synth.gongs import large_gong  # noqa: E402
from synth.looping import LoopMixer, master_loop, write_loop_sidecar  # noqa: E402
from synth.mixer import measure, write_ogg  # noqa: E402
from synth.pad import pad_chord, string_body  # noqa: E402
from synth.reverb import ModFDNReverb  # noqa: E402
from synth.score import n  # noqa: E402

_spec = importlib.util.spec_from_file_location("undertow_rising", os.path.join(HERE, "undertow_rising.py"))
UR = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(UR)

OUT = os.path.join(ROOT, "assets", "audio", "music", "storm_battle.ogg")
SEED = 20261960
TARGET_LUFS = -16.0
BPM = 2 * UR.BPM                      # 96: twice the Rising's tempo
BEAT = 60.0 / BPM
BAR = 4 * BEAT                        # 2.5 s
BARS = 2 * UR.BARS                    # 28: the Rising's 14 bars, each two battle bars
LOOP_S = BARS * BAR                   # 70 s, the Rising's loop length
RISE_BARS = 4                         # the loop's last bars (the Rising's bars 13-14): the rise
INTRO_BARS = 2                        # the intro: the loop's last two bars
INTRO_S = INTRO_BARS * BAR
FORWARD_BAR = 17                      # the tritone section: horns and violas in
GONG_BARS = (1, 17)
KICKS = ((0, 0.92), (3, 0.62), (6, 0.74))       # (eighth, velocity): 3 + 3 + 2, the Rising's limp sped up
TREM_HZ = BPM / 60.0 * 4                         # sixteenths: 6.4 Hz, 448 whole cycles per loop
TREM_DEPTH = 0.55


def t_of(bar: int, beat: float = 0.0) -> float:
    """Seconds from the loop start to `beat` (0-based) of battle bar `bar` (1-based)."""
    return (bar - 1) * BAR + beat * BEAT


def rising_bar(bar: int) -> int:
    """The Rising's bar (1-based) that battle bar `bar` sits in."""
    return (bar - 1) // 2 + 1


def tremolo(x: np.ndarray, t0: float) -> np.ndarray:
    """Bowed sixteenth tremolo on a pad that starts t0 s into the loop (locked to the loop's sixteenth grid)."""
    t = t0 + np.arange(len(x)) / SR
    env = 1.0 - TREM_DEPTH * (0.5 - 0.5 * np.cos(2 * np.pi * TREM_HZ * t)) ** 1.5
    return x * env[:, None]


def events() -> list[tuple[str, np.ndarray, float, float]]:
    """The loop's events: (bus, signal, loop time, pan). The Rising's times stay absolute (its bar = 5 s)."""
    ev = []
    for i, (t0, d, m) in enumerate(UR._brass_events(UR.BRASS, 1)):
        long = d >= 6 * UR.BEAT
        voices = [(0, -0.25, 0.9, 0.0, "brass"), (0, 0.15, 0.84, 0.05, "brass"), (-12, 0.0, 0.92, -0.03, "tuba")]
        if t0 >= t_of(FORWARD_BAR) - 1e-6:
            voices.append((12, 0.3, 0.7, 0.04, "horn"))
        for j, (dm, pan, v, det, bus) in enumerate(voices):
            x = UR.low_brass(m + dm + det, d * 0.95, v, SEED + 100 * i + j, attack=1.2 if long else 0.18,
                             swell=0.7 if long else 0.2, release=0.45 if long else 0.25)
            ev.append((bus, x, t0 + 0.01 * j, pan))
    for k, (rbar, rbars, pitches, att) in enumerate(UR.CLUSTERS):
        t0 = UR.t_of(rbar)
        x = pad_chord([n(p) for p in pitches], rbars * UR.BAR - 0.3, 0.85, seed=SEED + 2000 + k, voices=5,
                      spread_cents=12.0, attack=min(att, 2.0) if rbar < 13 else att, release=1.2, width=0.85)
        ev.append(("cluster", tremolo(x, t0), t0, 0.0))
    g = rng(SEED + 1)
    root = n("G1")
    for bar in range(1, BARS + 1):
        rb = rising_bar(bar)
        if rb in UR.RUN_ROOT and bar % 2 == 1:
            root = n(UR.RUN_ROOT[rb])
        for s in range(16):
            off = 1 if s % 4 == 3 else 0                              # G G G Ab: the minor second leaned on
            v = (0.66 if s % 4 == 0 else 0.44) * g.uniform(0.92, 1.05)
            x = bass_note(root + 12 + off, BEAT / 4 * 0.8, v, seed=SEED + 5000 + 16 * bar + s, mute=0.7)
            ev.append(("run", x, t_of(bar, s / 4) + 0.002, 0.2 if s % 2 else -0.15))
            if bar >= FORWARD_BAR and bar <= BARS - RISE_BARS:
                y = bass_note(root + 36 + off, BEAT / 4 * 0.7, v * 0.8, seed=SEED + 7000 + 16 * bar + s, mute=0.5)
                ev.append(("viola", y, t_of(bar, s / 4) + 0.004, -0.35 if s % 2 else 0.35))
        fill = bar % 4 == 0
        for e8, v in KICKS:
            ev.append(("pulse", big_drum(v, variant=8 * bar + e8, seed=SEED + 4), t_of(bar, e8 / 2), 0.0))
        for h, sv in ((0, 1.0), (1.5, 0.7)):                          # the heartbeat under the first two strokes
            tt = np.arange(int(0.9 * SR)) / SR
            sub = np.sin(2 * np.pi * (36.0 + 10.0 * np.exp(-tt / 0.15)) * tt) * np.exp(-tt / 0.28)
            sub *= np.minimum(1.0, tt / 0.008)
            ev.append(("sub", sub * sv, t_of(bar, h), 0.0))
        for s in range(16):
            if fill and s >= 12:                                      # the fill into the next four bars
                st, dv = "tek", 0.22 + 0.06 * (s - 12)
            elif s % 2 == 0:
                st, dv = ("tek", 0.36) if s % 4 == 2 else ("dum" if s == 8 else "tek", 0.3)
            else:
                st, dv = "ghost", 0.12
            ev.append(("ticks", frame_drum(st, dv * g.uniform(0.88, 1.08), variant=bar * 16 + s, seed=SEED + 6),
                       t_of(bar, s / 4), 0.3 if st == "tek" else -0.3))
        if bar > BARS - 2:                                            # the rise's roll into bar 1
            for s in range(16):
                vr = 0.15 + 0.35 * ((bar - (BARS - 1)) * 16 + s) / 32.0
                ev.append(("roll", big_drum(vr, variant=900 + 16 * bar + s, seed=SEED + 9), t_of(bar, s / 4), 0.1))
    for bar in GONG_BARS:
        ev.append(("gong", large_gong(n("G1"), 0.6, seed=SEED + 80 + bar, t60=8.0), t_of(bar), -0.1))
    return ev


## Bus gains (dB), from a render's measured bus loudness to land PLAN (LU against the trombones, the lead).
GAINS = {"brass": 0.0, "tuba": 0.7, "horn": 0.2, "cluster": 10.0, "run": 7.8, "viola": 3.8, "pulse": 3.5,
         "sub": -6.2, "ticks": 15.3, "roll": 0.0, "gong": -8.5}
PLAN = {"brass": 0.0, "tuba": -4.0, "horn": -4.0, "cluster": -7.0, "run": -3.0, "viola": -9.0, "pulse": -3.0,
        "sub": -10.0, "ticks": -8.0, "roll": -10.0, "gong": -13.0}


def _bus_setup(mx: LoopMixer) -> None:
    G = GAINS
    mx.bus("brass", G["brass"], send=0.3, process=lambda x: filt(x, [bq_highpass(60, 0.7), bq_lowpass(5000, 0.7)]))
    mx.bus("tuba", G["tuba"], send=0.25, process=lambda x: filt(x, [bq_highpass(30, 0.7), bq_lowpass(2500, 0.7)]))
    mx.bus("horn", G["horn"], send=0.35, process=lambda x: filt(x, [bq_highpass(120, 0.7), bq_lowpass(4500, 0.7)]))
    mx.bus("cluster", G["cluster"], send=0.35, process=lambda x: string_body(x, cutoff=1400.0))
    mx.bus("run", G["run"], send=0.1, process=lambda x: filt(x, [bq_highpass(45, 0.7), bq_lowpass(2400, 0.7)]))
    mx.bus("viola", G["viola"], send=0.2, process=lambda x: filt(x, [bq_highpass(200, 0.7), bq_lowpass(5000, 0.7)]))
    mx.bus("pulse", G["pulse"], send=0.2, process=lambda x: filt(x, [bq_highpass(30, 0.7), bq_lowpass(1800, 0.7)]))
    mx.bus("sub", G["sub"], send=0.0, process=lambda x: filt(x, [bq_lowpass(120, 0.7)]))
    mx.bus("ticks", G["ticks"], send=0.12, process=lambda x: filt(x, [bq_lowpass(5500, 0.7)]))
    mx.bus("roll", G["roll"], send=0.25, process=lambda x: filt(x, [bq_highpass(35, 0.7), bq_lowpass(1500, 0.7)]))
    mx.bus("gong", G["gong"], send=0.4)


def render(out_path: str = OUT, verbose: bool = True, stats: dict | None = None) -> dict:
    mx = LoopMixer(intro_s=INTRO_S, loop_s=LOOP_S, preroll_s=8.0)
    _bus_setup(mx)
    intro_from = LOOP_S - INTRO_S
    for bus, x, t, pan in events():
        mx.add(bus, x, t, pan=pan)
        if t + len(x) / SR > intro_from:                              # the intro is the loop's last two bars, with
            mx.add(bus, x, t - intro_from, pan=pan, part="intro")     # the tails of what rings into them
    hall = ModFDNReverb(rt60=2.2, rt60_high=0.8, predelay=0.025, size=1.1, mod_depth=8.0, mod_rate=0.4,
                        early_level=0.3, lowcut=90.0, seed=SEED % 9973)
    intro, loop = mx.render(reverb=hall, reverb_return_db=-3.0)
    rep: dict = {}
    intro, loop = master_loop(intro, loop, TARGET_LUFS, ceiling_db=-2.0, report=rep)
    y = np.concatenate([intro, loop])
    S, L = len(intro), len(loop)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    write_ogg(out_path, y, quality=3.5, tags={"LOOPSTART": str(S), "LOOPLENGTH": str(L)})
    write_loop_sidecar(os.path.splitext(out_path)[0] + ".loop.json", SR, S, L, BPM, 4,
                       extra={"intro_bars": INTRO_BARS, "loop_bars": BARS, "variant_of": "undertow_rising"})
    m = measure(y)
    if stats is not None:
        stats["bus_lufs"] = dict(mx.bus_lufs)
        stats["limiter"] = rep
        stats["splice_residual_db"] = mx.splice_residual_db
    if verbose:
        lead = mx.bus_lufs["brass"]
        print(f"storm_battle: {m['seconds']:.2f}s (intro {S / SR:.2f}s + loop {L / SR:.2f}s)  "
              f"{m['integrated_lufs']:.2f} LUFS  TP {m['true_peak_dbtp']:.2f} dBTP  limiter {rep}  "
              f"splice residual {mx.splice_residual_db:.1f} dB")
        print("  buses (LU vs the brass)", {k: round(v - lead, 1) for k, v in mx.bus_lufs.items()})
        print("  off plan (LU)", {k: round(mx.bus_lufs[k] - lead - PLAN[k], 1) for k in PLAN})
    return m


if __name__ == "__main__":
    render(sys.argv[1] if len(sys.argv) > 1 else OUT)
