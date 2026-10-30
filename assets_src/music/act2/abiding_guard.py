"""`abiding_guard`: Sefir's Abiding guard at the Drowned Choir, then the storm waking early (M4-A2P-092;
act2_plan.md §2 Ch16; the cue sheet §3): two synchronized stems, an 80 s loop.

Original composition for this project (SPEC §2, §9). The march, the stab pattern and the form were written for this
fight. Our own lines are imported, never retyped: ORDER_HUM (motifs.py), hummed in canon by the guard, and the
storm's surge from undertows_reach.py (Act I's Undertow, the same storm). Nothing is taken from any existing music.

The brief (act2_plan Ch16): Sefir's elite guard, disciplined, faithful, terrible; then the storm wakes early as Imra's
heart falters, Kerrid holds the line, and the party is swept away (a scripted escape, as Ch8's Reach).
* **Stem 1, the guard:** A minor (the Hush's key, the Choir's), 4/4 at 96 BPM. A low frame-drum march (dum on 1 and
  3, rolls into each fourth bar); the guard's own hum, ORDER_HUM's first six notes, in a two-voice canon a bar apart,
  low and close; kettle gongs on each bar's downbeat, damped; the stab of a low metallophone on the minor roots.
* **Stem 2, the storm waking** (its row brings it in over 4 s): the Undertow's surge, one a bar, breaking through the
  march, and a big drum on the surges' peaks. It is the same storm as Act I's `undertows_reach`, heard coming early.
  96 BPM here makes a 4/4 bar exactly the Reach's 12/8 bar (2.5 s), so the surge fits bar for bar.

A minor, 4/4 at 96 BPM (a bar is 2.5 s), 32 bars. The stems share one limiter gain curve from the full stack. Vorbis
q3; the stack is -16 LUFS. Plain git (ADR 0175).

Render:  python3 tools/audio/render_all.py --only abiding_guard
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

from motifs import ORDER_HUM  # noqa: E402
from synth.drums import big_drum, frame_drum  # noqa: E402
from synth.dsp import SR, bq_highpass, bq_lowpass, db_to_lin, filt, rng  # noqa: E402
from synth.gongs import kettle_gong  # noqa: E402
from synth.looping import LoopMixer, write_loop_sidecar  # noqa: E402
from synth.loudness import integrated_lufs  # noqa: E402
from synth.metallophone import metallophone_note  # noqa: E402
from synth.mixer import limit_gain, measure, write_ogg  # noqa: E402
from synth.reverb import ModFDNReverb  # noqa: E402
from synth.score import n  # noqa: E402
from synth.voice import hum_ensemble  # noqa: E402


def _mod(name: str, path: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


UR = _mod("undertows_reach", os.path.join(MUSIC, "undertows_reach.py"))   # surge(), its 2.5 s bar

OUT = os.path.join(ROOT, "assets", "audio", "act2", "music", "abiding_guard_p1.ogg")
OUT2 = os.path.join(ROOT, "assets", "audio", "act2", "music", "abiding_guard_p2.ogg")
SEED = 20262030
TARGET_LUFS = -16.0
BPM = 96.0
BEAT = 60.0 / BPM
BAR = 4 * BEAT
BARS = 32
LOOP_S = BARS * BAR
LEAD_IN_S = BEAT / 4
CHORDS = ["Am", "Am", "F", "E", "Am", "Dm", "E", "E"] * 4
ROOTS = {"Am": "A1", "F": "F1", "E": "E1", "Dm": "D2"}
HUM_BARS = (1, 9, 17, 25)
GAINS = {"march": -4.0, "gong": -8.0, "hum": -2.0, "stab": -9.0, "surge": -4.0, "big": -4.0}


def t_of(bar: int, beat: float = 0.0) -> float:
    return (bar - 1) * BAR + beat * BEAT


def build_p1(mx: LoopMixer) -> None:
    g = rng(SEED + 1)
    for bar, ch in enumerate(CHORDS, start=1):
        for beat in (0, 2):
            mx.add("march", frame_drum("dum", 0.6 * float(g.uniform(0.94, 1.03)), variant=bar % 3, size=1.2, seed=SEED + 10),
                   t_of(bar, beat), pan=-0.1)
        if bar % 4 == 0:                                                     # the roll into each fourth bar
            for s in range(7):                                            # ends a sixteenth early: the seam's breath
                mx.add("march", frame_drum("tek", 0.25 + 0.05 * s, variant=s % 4, seed=SEED + 11), t_of(bar, 2 + s / 4),
                       pan=0.15)
        mx.add("gong", kettle_gong(n(ROOTS[ch]) + 12, 0.45, seed=SEED + 20 + bar % 4, t60=1.2, damp_at=0.8), t_of(bar),
               pan=0.25)
        if ch in ("Am", "Dm") and bar % 2 == 1:
            mx.add("stab", metallophone_note(n(ROOTS[ch]) + 24, 0.55, seed=SEED + 30 + bar, decay=1.4, hardness=0.75,
                                             damp_at=0.35), t_of(bar, 1), pan=-0.25)
    line = [(float(m) - 12, 2 * BEAT) for m, _ in ORDER_HUM[:6]]              # the guard's hum, in canon
    for k, bar in enumerate(HUM_BARS):
        for v, lag in enumerate((0.0, BAR)):
            mx.add("hum", hum_ensemble(line, voices=10, seed=SEED + 100 + 10 * k + v, register="low", spread=0.6),
                   t_of(bar) + lag, pan=-0.35 + 0.7 * v)


def build_p2(mx: LoopMixer) -> None:
    g = rng(SEED + 2)
    for bar in range(1, BARS + 1):
        mx.add("surge", UR.surge(g), t_of(bar), pan=float(g.uniform(-0.3, 0.3)))
        mx.add("big", big_drum(0.75, variant=bar % 4, seed=SEED + 40), t_of(bar) + UR.t_of(1, 7), pan=0.0)


def _bus_setup(mx: LoopMixer, stem: int) -> None:
    G = GAINS
    if stem == 1:
        mx.bus("march", G["march"], send=0.15)
        mx.bus("gong", G["gong"], send=0.3, process=lambda x: filt(x, [bq_lowpass(1800, 0.7)]))
        mx.bus("hum", G["hum"], send=0.35, process=lambda x: filt(x, [bq_lowpass(1600, 0.7)]))
        mx.bus("stab", G["stab"], send=0.3, process=lambda x: filt(x, [bq_lowpass(5000, 0.7)]))
    else:
        mx.bus("surge", G["surge"], send=0.25, process=lambda x: filt(x, [bq_highpass(120, 0.7), bq_lowpass(3000, 0.7)]))
        mx.bus("big", G["big"], send=0.2, process=lambda x: filt(x, [bq_lowpass(2000, 0.7)]))


def render(out_path: str = OUT, verbose: bool = True, stats: dict | None = None) -> dict:
    loops = []
    for stem, build in ((1, build_p1), (2, build_p2)):
        mx = LoopMixer(intro_s=0.0, loop_s=LOOP_S, preroll_s=8.0)
        _bus_setup(mx, stem)
        build(mx)
        bowl = ModFDNReverb(rt60=3.0, rt60_high=1.0, predelay=0.04, size=1.6, mod_depth=8.0, mod_rate=0.3,
                            early_level=0.2, lowcut=100.0, seed=SEED % 9973)
        _, loop = mx.render(reverb=bowl, reverb_return_db=-3.0)
        loops.append(loop)
        del mx
    lead_in = int(round(LEAD_IN_S * SR))
    loops = [np.roll(x, lead_in, axis=0) for x in loops]
    full = loops[0] + loops[1]
    gain = db_to_lin(TARGET_LUFS - integrated_lufs(full))
    ctx = int(0.05 * SR)
    L = len(full)
    for _ in range(4):                    # one limiter gain curve for both stems, from the full stack (wrap-aware)
        f = full * gain
        lg = limit_gain(np.concatenate([f[-ctx:], f, f[:ctx]]), -3.0)[ctx: ctx + L]   # drums overshoot when decoded
        cur = integrated_lufs(f * lg[:, None])
        if abs(cur - TARGET_LUFS) < 0.1:
            break
        gain *= db_to_lin(TARGET_LUFS - cur)
    stems = [s * gain * lg[:, None] for s in loops]
    paths = [out_path, os.path.join(os.path.dirname(out_path), os.path.basename(OUT2))]
    extra = {"stems_of": "abiding_guard", "loop_bars": BARS, "downbeat_offset_s": lead_in / SR}
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    for x, p in zip(stems, paths):
        write_ogg(p, x, quality=3.0, tags={"LOOPSTART": "0", "LOOPLENGTH": str(L)})
        write_loop_sidecar(os.path.splitext(p)[0] + ".loop.json", SR, 0, L, BPM, 4, extra=extra)
    m = measure(stems[0] + stems[1])
    if stats is not None:
        stats["stem1_lufs"] = measure(stems[0])["integrated_lufs"]
    if verbose:
        print(f"abiding_guard: stack {m['integrated_lufs']:.2f} LUFS  TP {m['true_peak_dbtp']:.2f}")
    return m


if __name__ == "__main__":
    render()
