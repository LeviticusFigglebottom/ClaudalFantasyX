"""`virel_summon`: the sting when Asha calls Virel, the Fire Vowbound, in battle (M3-AUD-822; act1_ch08.md B16, the
Undertow's Reach's phase 2), 5.8 s.

Original (SPEC §2). The brief: "Sailcloth snapping, a hiss of fire, the Hush's first phrase on the reed." Virel is a
long ribbon-serpent of sailcloth panels with fire along every seam. So the sting opens with the cloth: four snaps as
the panels fill and unfurl, each a hard crack with a short flutter after it, closer together as she uncoils; the
seams catch with a rising hiss of fire and a scatter of crackle. Over it the spire reed (virel_bound.py `spire_reed`,
the voice of her binding) plays the Hush theme's first six notes (hush_theme_v2.py MEL_A, read from that file, in
virel_bound's F-sharp minor: C#6 B5 A5 | F#5 E5 F#5), quicker and harder-blown than at the binding, and holds the
last F#, while the fire flares once and settles. It plays over the ducked boss cue (undertow_reach's stem 2 drops
to drone and percussion for it).

Stereo, at the music target (-16 LUFS integrated, like ilun_summon), on the Music bus; battle_sfx.json
`vowbound_stings` plays it as the sfx.json row `virel_summon`.

Render:  python3 assets_src/music/virel_summon.py   (or tools/audio/render_all.py --only virel_summon)
"""
from __future__ import annotations

import importlib.util
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools", "audio"))

import numpy as np  # noqa: E402

from synth.dsp import SR, bq_bandpass, bq_highpass, bq_lowpass, bq_peak, filt, rng, smooth_noise  # noqa: E402
from synth.mixer import Mixer, measure, normalize_integrated, write_ogg  # noqa: E402
from synth.reverb import ModFDNReverb  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))


def _mod(name: str):
    spec = importlib.util.spec_from_file_location(name, os.path.join(HERE, f"{name}.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


VB = _mod("virel_bound")
HUSH = VB.HUSH

OUT = os.path.join(ROOT, "assets", "audio", "sfx", "virel_summon.ogg")
SEED = 20261823
TARGET_LUFS = -16.0
LENGTH = 5.8
BEAT = 0.4                    # one beat of MEL_A here (s): 150 BPM, quicker than the binding
PHRASE_T0 = 0.95
LAST_HOLD = 1.0
SNAPS = [(0.0, 0.75), (0.28, 0.85), (0.5, 0.95), (0.68, 1.0)]   # the panels filling (time s, strength)
FLARE_T = 2.9                 # the fire flares once, under the phrase's fourth note


def cloth_snap(g, strength: float) -> np.ndarray:
    """A sail panel filling: a short low push of air, a hard broadband crack, and a flutter (the cloth's edge beating
    at 14-24 Hz) dying away. Mono."""
    N = int(0.6 * SR)
    t = np.arange(N) / SR
    push_n = int(0.07 * SR)
    push = filt(g.standard_normal(push_n + 256), [bq_lowpass(500.0, 0.7)])[:push_n]
    push *= np.linspace(0, 1, push_n) ** 2 * 0.5
    crack = filt(g.standard_normal(N), [bq_highpass(350.0, 0.7), bq_peak(1400.0, 6.0, 0.8), bq_lowpass(7000.0, 0.7)])
    crack *= np.exp(-t / 0.018) * np.minimum(1.0, t / 0.0004)
    rate = float(g.uniform(14.0, 24.0))
    flut = filt(g.standard_normal(N), [bq_bandpass(900.0, 0.6)])
    flut *= (0.5 + 0.5 * np.sin(2 * np.pi * rate * t)) ** 3 * np.exp(-t / 0.13) * np.clip(t / 0.02, 0, 1) * 0.45
    out = np.zeros(push_n + N)
    out[:push_n] += push
    out[push_n:] += crack + flut
    return strength * out / (np.abs(out).max() + 1e-9)


def fire(g, seconds: float) -> np.ndarray:
    """The seams catching: a broad hiss that rises from the first snap, flares once at FLARE_T and settles, with a
    lower roar under the flare. Mono."""
    N = int(seconds * SR)
    t = np.arange(N) / SR
    hiss = filt(g.standard_normal(N), [bq_highpass(2200.0, 0.7), bq_peak(5500.0, 3.0, 0.8)])
    hiss /= np.std(hiss) + 1e-9
    roar = filt(g.standard_normal(N), [bq_bandpass(260.0, 0.6), bq_lowpass(700.0, 0.7)])
    roar /= np.std(roar) + 1e-9
    rise = np.clip((t - 0.1) / 1.0, 0, 1) ** 1.5
    flare = np.exp(-((t - FLARE_T) / 0.35) ** 2)
    settle = np.where(t > FLARE_T, 0.55 + 0.45 * np.exp(-(t - FLARE_T) / 0.6), 1.0)
    wob = 1.0 + 0.25 * smooth_noise(N, 6.0, g)
    return (0.6 * hiss * rise * settle * wob + 0.9 * hiss * flare + 0.8 * roar * (0.3 * rise + flare)) * \
        np.minimum(1.0, (N - np.arange(N)) / (0.6 * SR))


def crackle(g, seconds: float, density: float) -> np.ndarray:
    """Short band-limited pops (fire in cloth), denser around the flare. Mono."""
    N = int(seconds * SR)
    out = np.zeros(N)
    tt = 0.3
    while tt < seconds - 0.6:
        k = int(g.uniform(0.002, 0.007) * SR)
        pop = filt(g.standard_normal(k + 64), [bq_bandpass(float(g.uniform(1800, 6000)), 1.3)])[:k]
        pop *= np.exp(-np.arange(k) / (0.25 * k)) * g.uniform(0.2, 1.0)
        s = int(tt * SR)
        out[s: s + k] += pop
        near = np.exp(-((tt - FLARE_T) / 0.6) ** 2)
        tt += float(g.exponential(1.0 / (density * (0.5 + 1.5 * near))))
    return out


# Bus gains from measured bus loudness (HUSH._bus_stats, gated integrated per bus): the reed is the lead (0 LU); the
# cloth snaps -4 (they are short: their peaks sit near the reed's), the fire -9, crackle -16.
GAINS = {"reed": 0.0, "cloth": 6.3, "fire": -20.2, "crackle": -1.2}


def render(out_path: str = OUT, verbose: bool = True, stats: dict | None = None) -> dict:
    g = rng(SEED)
    mx = Mixer(LENGTH + 0.5)
    mx.bus("reed", GAINS["reed"], send=0.3, process=lambda x: filt(x, [bq_highpass(400, 0.7), bq_peak(2800, 1.0, 1.0)]))
    mx.bus("cloth", GAINS["cloth"], send=0.25)
    mx.bus("fire", GAINS["fire"], send=0.2, process=lambda x: filt(x, [bq_highpass(120, 0.7)]))
    mx.bus("crackle", GAINS["crackle"], send=0.15, process=lambda x: filt(x, [bq_highpass(1200, 0.7)]))
    for i, (t, s) in enumerate(SNAPS):
        mx.add("cloth", cloth_snap(rng(SEED + 10 + i), s), t, pan=(-0.55, 0.35, -0.15, 0.2)[i])
    mx.add("fire", fire(rng(SEED + 20), LENGTH), 0.0, pan=0.0)
    mx.add("crackle", crackle(rng(SEED + 21), LENGTH, 30.0), 0.0, pan=-0.4)
    mx.add("crackle", crackle(rng(SEED + 22), LENGTH, 30.0), 0.0, pan=0.4)
    for i, (t0, d, m, v) in enumerate(VB.reed_phrase(PHRASE_T0, BEAT, LAST_HOLD)):
        x = VB.spire_reed(m, d + 0.02, 0.7 + 0.6 * v, SEED + 30 + i, attack=0.035, scoop_cents=40.0 if i == 0 else 20.0,
                          vib_cents=11.0 if d > 0.6 else 3.0, vib_rate=5.8)
        mx.add("reed", x, t0 - VB.REED_PRE + float(g.normal(0, 0.003)), pan=0.0)
    hall = ModFDNReverb(rt60=2.2, rt60_high=1.0, predelay=0.02, size=1.0, mod_depth=8.0, mod_rate=0.5,
                        early_level=0.3, lowcut=110.0, seed=SEED % 9973)
    st: dict = {}
    HUSH._bus_stats(mx, st)
    y = mx.render(reverb=hall, reverb_return_db=-3.0)[: int(LENGTH * SR)]
    k = int(1.0 * SR)
    y[-k:] *= np.linspace(1, 0, k)[:, None] ** 2
    y = normalize_integrated(y, TARGET_LUFS, ceiling_db=-2.0)
    write_ogg(out_path, y, quality=4.0)
    m = measure(y)
    if stats is not None:
        stats.update(st)
    if verbose:
        lead = st.get("bus_reed_lufs", 0.0)
        print(f"virel_summon: {m['seconds']:.2f}s  {m['integrated_lufs']:.2f} LUFS  Mmax {m['momentary_max_lufs']:.2f}"
              f"  TP {m['true_peak_dbtp']:.2f}")
        print("  buses (LU vs the reed)", {k[4:-5]: round(v - lead, 1) for k, v in st.items()})
    return m


if __name__ == "__main__":
    render()
