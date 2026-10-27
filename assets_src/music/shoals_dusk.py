"""`shoals_dusk`: the Brine Shoals at night, the camp on the wreck-ridge (M3-AUD-821; act1_ch06.md B08, §6), a 63.6 s
loop.

Original composition for this project (SPEC §2, §9): the reed plays the Brine Shoals' own tune (brine_shoals.py
TUNE_A, imported, not re-typed), written for this route and not derived from any existing tune; the tide was made
for this cue.

The brief (act1_ch06.md §6): "Night bed. The field bed (brine_shoals.py) thinned to one reed and the tide. B09
drops even that to tide ambience." After a bad day: the party round a small oil fire on a high hull, Kerrid standing
at the seaward end, Liss not at the fire (ch06_ridge_camp.dlg, `@music shoals_dusk fade=2.0`). B09, the burned lamp,
plays `@music silence` and the `tide_ambience` SFX, so this cue needs no variant for it.

What is left of the field bed: its key (C-sharp minor), its 5/4 grouped 3+2 at 66 BPM (a bar is 4.55 s), and its
tune; the lute, the bass, the steps, the hulls' pad and the gongs are gone. One low reed (a double-reed pipe,
act2_voices.py `reed_pipe`, its nasal formant softened) plays TUNE_A an octave down, alone, with long rests; under it
and between, the tide comes in over the mud flats: a slow wash that swells and draws back, small laps at the crests,
a drip off a hull.

Form (14 bars): 1-3 the tide | 4-7 the reed, TUNE_A (the four bars) | 8-9 the tide | 10-11 the reed, TUNE_A's first
two bars, the last note held | 12-14 the tide, into the wrap. Loop: LOOPSTART = 0 and LOOPLENGTH = the whole file;
the tide is seamless across the wrap (rendered longer and folded) and the reed is silent there.

Render:  python3 assets_src/music/shoals_dusk.py   (or tools/audio/render_all.py --only shoals_dusk)
"""
from __future__ import annotations

import importlib.util
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools", "audio"))

import numpy as np  # noqa: E402

from synth.dsp import SR, bq_bandpass, bq_highpass, bq_lowpass, db_to_lin, filt, rng, smooth_noise  # noqa: E402
from synth.looping import LoopMixer, master_loop, write_loop_sidecar  # noqa: E402
from synth.loudness import integrated_lufs  # noqa: E402
from synth.mixer import measure, write_ogg  # noqa: E402
from synth.reverb import ModFDNReverb  # noqa: E402
from synth.score import n  # noqa: E402
from synth.water import bubble, drip  # noqa: E402


def _load(name: str):
    spec = importlib.util.spec_from_file_location(name, os.path.join(os.path.dirname(__file__), name + ".py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


BS = _load("brine_shoals")
AV = _load("act2_voices")

OUT = os.path.join(ROOT, "assets", "audio", "music", "shoals_dusk.ogg")
SEED = 20261827
TARGET_LUFS = -16.0
BPM = BS.BPM
BEAT = BS.BEAT
BAR = BS.BAR
BARS = 14
LOOP_S = BARS * BAR
REED_PRE = 0.03                 # the reed's pressure builds over its attack: placed a little early
SWELLS = 7                      # the tide's swells a loop


def t_of(bar: int, beat: float = 0.0) -> float:
    return (bar - 1) * BAR + beat * BEAT


def tide(g, loop_s: float) -> np.ndarray:
    """The tide over the flats: a wash (two bands of noise) that swells and draws back SWELLS times a loop, exactly
    one loop long and seamless (rendered longer and folded). Stereo."""
    N = int(round(loop_s * SR))
    k = int(3.0 * SR)
    M = N + k
    t = np.arange(M) / SR
    period = loop_s / SWELLS
    phase = (t % period) / period
    swell = np.where(phase < 0.4, (phase / 0.4) ** 1.5, np.exp(-(phase - 0.4) / 0.22))
    out = np.zeros((M, 2))
    for side in (0, 1):
        low = filt(g.standard_normal(M), [bq_highpass(90, 0.7), bq_lowpass(600, 0.7)])
        hi = filt(g.standard_normal(M), [bq_bandpass(1800, 0.6), bq_lowpass(5000, 0.7)])
        wob = 0.8 + 0.2 * smooth_noise(M, 0.6, g)
        out[:, side] = (0.6 * low + 0.35 * hi * swell) * (0.35 + 0.65 * swell) * wob
    return AV.fold(out, N, k)


def lap(g, size: float) -> np.ndarray:
    """A small wave lapping against a hull: a soft slap of band noise and a few bubbles. Mono."""
    N = int(1.2 * SR)
    t = np.arange(N) / SR
    env = np.clip(t / 0.04, 0, 1) * np.exp(-t / (0.18 * size))
    y = filt(g.standard_normal(N), [bq_bandpass(700 + 500 * size, 0.7)]) * env
    for _ in range(int(5 * size)):
        b = bubble(float(g.uniform(2.0, 6.0)), amp=float(g.uniform(0.1, 0.3)), rise=0.1)
        s = int(float(g.uniform(0.03, 0.5)) * SR)
        e = min(N, s + len(b))
        y[s:e] += b[: e - s]
    return y


def build(mx: LoopMixer) -> None:
    g = rng(SEED)
    mx.add("tide", tide(rng(SEED + 1), LOOP_S), 0.0)
    period = LOOP_S / SWELLS
    for i in range(SWELLS):
        crest = i * period + 0.4 * period
        for j in range(int(g.integers(1, 4))):
            mx.add("laps", lap(g, float(g.uniform(0.6, 1.2))), crest + float(g.uniform(-0.6, 1.6)),
                   pan=float(g.uniform(-0.7, 0.7)))
    for at in (t_of(2, 3.2), t_of(9, 1.5), t_of(12, 4.0)):
        mx.add("laps", drip(vel=0.4, radius_mm=float(g.uniform(2.0, 3.0)), seed=int(g.integers(1 << 30))) * 0.5, at,
               pan=float(g.uniform(-0.5, 0.5)))
    # the reed: TUNE_A an octave down at bars 4-7, its first two bars at 10-11 (the last note held)
    for bars, start, vel in ((BS.TUNE_A, 4, 0.55), (BS.TUNE_A[:2], 10, 0.5)):
        rg = rng(SEED + 100 * start)
        for i, bar in enumerate(bars):
            pos = 0.0
            for k, (p, beats) in enumerate(bar):
                if p is not None:
                    last = start == 10 and i == len(bars) - 1 and k == len(bar) - 1
                    d = beats * BEAT * (2.2 if last else 0.96)
                    v = vel * rg.uniform(0.94, 1.04) * (1.05 if pos == 0 else 1.0)
                    x = AV.reed_pipe(n(p) - 12, d, v, seed=SEED + 500 + 100 * start + 10 * i + k, attack=0.09,
                                     release=0.35 if last else 0.16, sag_cents=12.0, nasal=0.55)
                    mx.add("reed", x, t_of(start + i, pos) - REED_PRE + float(rg.normal(0, 0.008)), pan=-0.08)
                pos += beats


# Bus gains were set from measured bus loudness (render(stats=...)["bus_lufs"]): the reed at L (over the bars it
# plays), the tide L-6 over the loop (it carries the bed where the reed rests), the laps and drips L-14.
GAINS = {"reed": 0.0, "tide": -8.1, "laps": -19.2}


def render(out_path: str = OUT, verbose: bool = True, stats: dict | None = None) -> dict:
    mx = LoopMixer(intro_s=0.0, loop_s=LOOP_S, preroll_s=8.0)
    mx.bus("reed", GAINS["reed"], send=0.35, process=lambda x: filt(x, [bq_highpass(110, 0.7),
                                                                        bq_lowpass(4500, 0.7)]))
    mx.bus("tide", GAINS["tide"], send=0.10, process=lambda x: filt(x, [bq_highpass(60, 0.7)]))
    mx.bus("laps", GAINS["laps"], send=0.30)
    build(mx)
    night = ModFDNReverb(rt60=2.4, rt60_high=0.9, predelay=0.03, size=1.1, mod_depth=7.0, mod_rate=0.4,
                         early_level=0.15, lowcut=120.0, seed=SEED % 9973)
    _, loop = mx.render(reverb=night, reverb_return_db=-3.0)
    rep: dict = {}
    _, loop = master_loop(np.zeros((0, 2)), loop, TARGET_LUFS, ceiling_db=-2.0, report=rep)
    L = len(loop)
    write_ogg(out_path, loop, quality=3.0, tags={"LOOPSTART": "0", "LOOPLENGTH": str(L)})
    write_loop_sidecar(os.path.splitext(out_path)[0] + ".loop.json", SR, 0, L, BPM, 5,
                       extra={"loop_bars": BARS, "meter": "5/4 (3+2)", "downbeat_offset_s": 0.0})
    m = measure(loop)
    if stats is not None:
        stats["bus_lufs"] = _bus_stats(mx)
        stats["limiter"] = rep
    if verbose:
        print(f"shoals_dusk: {m['seconds']:.2f}s  {m['integrated_lufs']:.2f} LUFS  TP {m['true_peak_dbtp']:.2f} dBTP"
              f"  limiter {rep}")
    return m


def _bus_stats(mx: LoopMixer) -> dict:
    out = {}
    a, e = int(t_of(4) * SR), int(t_of(8) * SR)
    for b in mx.buses.values():
        x = db_to_lin(b.gain_db) * (b.process(b.loop) if b.process else b.loop)
        out[b.name] = integrated_lufs(x[a:e] if b.name == "reed" else x)
    return out


if __name__ == "__main__":
    st: dict = {}
    render(stats=st)
    print("  buses", {k: round(v, 1) for k, v in st["bus_lufs"].items()})
