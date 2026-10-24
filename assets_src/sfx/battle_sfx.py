"""Battle sound effects for the M2-RND-03/04 VFX library (M2-AUD-04; score-as-code for SFX).

Every sound is synthesized here from the tools/audio/synth library: no samples, no sample packs, no
CC0 audio, no AI generation (SPEC section 2). They reuse the score's palette on purpose, so a battle
sounds like the same world as the music: metallophone bars and gongs for light and bronze, Minnaert
bubbles and filtered noise for the sea, a bell model (minor-third "tierce" partials, like a cast bell)
for the Drownbell.

Original-material check (SPEC section 2): the few pitched figures (Shallows Verse's rising line, the
preemptive and victory figures, the Vowbound's call) are short pentatonic or open-fifth gestures
written for this file. None quotes or is derived from an existing melody.

Outputs (mono, 44.1 kHz, Ogg Vorbis q4) under assets/audio/sfx/:
    battle/hit_<element>_<n>.ogg   element hits (none, fire, ice, lightning, water, holy), 2-3 variants each
    battle/lamp_dive.ogg, shallows_verse.ogg, read.ogg, heal.ogg, status_apply.ogg, ko_release.ogg
    battle/stinger_ambush.ogg (+ _soft: no sub-bass), stinger_preemptive.ogg
    battle/drownbell_toll.ogg (+ _soft), toll_gather.ogg, rim_crack_<n>.ogg, rim_break.ogg,
    battle/polyp_rise.ogg, polyp_mend.ogg, floodnet.ogg, flood.ogg (+ flood_soft: no sub-bass),
    battle/bell_release.ogg, vowbound_call.ogg, vowbound_dismiss.ogg, victory.ogg, defeat.ogg, escape.ogg
    drownbell_toll.ogg            the far, underwater toll for the cutscene's `@sfx drownbell_toll`
Loudness (docs/kb/audio/mix.md section 2, measured on the decoded file by render_all.py): combat SFX
-18 LUFS momentary max; stingers, the toll and the victory sting -16; quiet textures (Read, status,
the gather, the mend) lower, as listed in SFX below. Rendered at a -2 dBFS sample-peak ceiling, so the
decoded true peaks stay at or under -1 dBTP.

Render:  python3 assets_src/sfx/battle_sfx.py   (or tools/audio/render_all.py --only battle_sfx)
"""
from __future__ import annotations

import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools", "audio"))

import numpy as np  # noqa: E402

from synth.dsp import (SR, bq_bandpass, bq_highpass, bq_highshelf, bq_lowpass, bq_peak, filt,  # noqa: E402
                       midi_to_hz, rng, smooth_noise)
from synth.gongs import kettle_gong, large_gong  # noqa: E402
from synth.metallophone import metallophone_note  # noqa: E402
from synth.mixer import measure, normalize_momentary, write_ogg  # noqa: E402
from synth.reverb import ModFDNReverb  # noqa: E402
from synth.score import n  # noqa: E402
from synth.water import bubble, drip  # noqa: E402

OUT_DIR = os.path.join(ROOT, "assets", "audio", "sfx")
SUB = "battle"
SEED = 7713
COMBAT = -18.0
STING = -16.0
QUIET = -21.0
CEILING = -2.0
QUALITY = 4.0


# --------------------------------------------------------------------------- helpers


def _t(N):
    return np.arange(N) / SR


def _n(sec):
    return int(sec * SR)


def _place(buf, x, t, gain=1.0):
    s = int(t * SR)
    if s >= len(buf):
        return
    e = min(len(buf), s + len(x))
    buf[s:e] += gain * x[: e - s]


def _noise(g, N):
    return g.standard_normal(N)


def _decay(N, tau, attack=0.0005):
    t = _t(N)
    return np.exp(-t / tau) * np.minimum(1.0, t / attack if attack > 0 else 1.0)


def _swell(N, peak_at, rise_pow=2.0, fall_tau=0.3):
    """0 -> 1 at peak_at (power curve), then an exponential fall."""
    t = _t(N)
    up = np.clip(t / peak_at, 0, 1) ** rise_pow
    down = np.where(t > peak_at, np.exp(-(t - peak_at) / fall_tau), 1.0)
    return up * down


def _sine_glide(N, f_from, f_to, curve=1.0, phase=0.0):
    t = _t(N)
    u = (t / t[-1]) ** curve if N > 1 else t
    f = f_from * (f_to / f_from) ** u
    return np.sin(2 * np.pi * np.cumsum(f) / SR + phase)


def _sweep_band(x, f_from, f_to, q=2.0, steps=24):
    """A band-pass that glides from f_from to f_to: crossfaded fixed bands (FFT filters are LTI)."""
    N = len(x)
    out = np.zeros(N)
    pos = np.linspace(0, 1, N)
    for i in range(steps):
        c = i / (steps - 1)
        fc = f_from * (f_to / f_from) ** c
        w = np.clip(1 - np.abs(pos - c) * (steps - 1), 0, 1)
        out += w * filt(x, [bq_bandpass(fc, q)])
    return out


def _tail_fade(x, sec=0.03):
    k = min(len(x) // 3, _n(sec))
    x[-k:] *= np.linspace(1, 0, k) ** 2
    return x


def _room(x, rt60=0.9, mix=0.2, seed=1, predelay=0.012, size=0.6, high=4000.0, tail=0.0):
    """Mono in, mono out: a modulated FDN (the score's hall) folded to mono, tail appended if asked."""
    wet = ModFDNReverb(rt60=rt60, rt60_high=rt60 * 0.45, predelay=predelay, size=size, early_level=0.2,
                       lowcut=180.0, highcut=high, seed=seed).process(np.stack([x, x], 1), tail=tail)
    wet = wet.mean(axis=1)
    dry = np.concatenate([x, np.zeros(len(wet) - len(x))])
    return (1 - mix) * dry + mix * wet


def _thump(f_from, f_to, tau, N, g, click=0.3):
    """A body impact: a pitch-dropping sine and a short low noise knock."""
    t = _t(N)
    body = _sine_glide(N, f_from, f_to, 0.35) * np.exp(-t / tau)
    k = min(N, _n(0.02))
    knock = np.zeros(N)
    knock[:k] = filt(_noise(g, k), [bq_lowpass(900, 0.7)]) * np.exp(-_t(k) / 0.004)
    return (body + click * knock) * np.minimum(1.0, t / 0.0006)


def _bubbles(g, N, count, r_lo, r_hi, t_lo, t_hi, amp=1.0, grow=0.0):
    """`count` Minnaert bubbles, radii in mm; grow > 0 makes later ones bigger (a surge)."""
    out = np.zeros(N)
    for _ in range(count):
        at = g.uniform(t_lo, t_hi)
        u = (at - t_lo) / max(t_hi - t_lo, 1e-6)
        r = g.uniform(r_lo, r_hi) * (1 + grow * u)
        _place(out, bubble(r, g.uniform(0.3, 1.0) * amp, rise=g.uniform(0.05, 0.15)), at)
    return out


def _bell_partials(f0, dur, g, t60=6.0, bright=1.0, glide_cents=0.0):
    """A cast bell: hum, prime, minor-third tierce, quint, nominal and upper partials, each a beating pair.

    Ratios are the classic tuned-bell set (an acoustic fact, not anyone's sound): hum 0.5, prime 1,
    tierce 1.2, quint 1.5, nominal 2, then 2.5, 2.67, 3.0, 4.0. Higher partials die sooner.
    """
    N = _n(dur)
    t = _t(N)
    parts = [(0.5, 0.9, 1.0), (1.0, 0.55, 0.62), (1.2, 0.5, 0.42), (1.5, 0.22, 0.33), (2.0, 0.42, 0.26),
             (2.5, 0.16 * bright, 0.15), (2.67, 0.12 * bright, 0.13), (3.0, 0.09 * bright, 0.1),
             (4.0, 0.06 * bright, 0.07)]
    gl = 2 ** (-glide_cents / 1200 * (1 - np.exp(-t / max(dur * 0.5, 1e-3))))
    ph = 2 * np.pi * np.cumsum(gl) / SR
    out = np.zeros(N)
    for r, a, rt in parts:
        f = f0 * r * (1 + g.uniform(-0.002, 0.002))
        if f > 0.45 * SR:
            continue
        split = g.uniform(0.2, 0.9) * r
        env = np.exp(-6.91 * t / (t60 * rt))
        out += a * env * 0.5 * (np.sin(f * ph + g.uniform(0, 6.28)) + np.sin((f + split) * ph + g.uniform(0, 6.28)))
    k = _n(0.015)
    out[:k] += 0.25 * filt(_noise(g, k), [bq_bandpass(f0 * 6, 0.8)]) * np.exp(-_t(k) / 0.003)
    return out * np.minimum(1.0, t / 0.003)


def _glass(f, dur, g, attack=0.004, t60=1.2, partials=((1.0, 1.0), (2.32, 0.35), (4.25, 0.12))):
    """A glassy tone: a few inharmonic, slightly beating sines (a struck or bowed glass)."""
    N = _n(dur)
    t = _t(N)
    out = np.zeros(N)
    for r, a in partials:
        ff = f * r
        if ff > 0.45 * SR:
            continue
        beat = g.uniform(0.3, 1.5)
        out += a * np.exp(-6.91 * t / (t60 / r ** 0.5)) * 0.5 * (
            np.sin(2 * np.pi * ff * t + g.uniform(0, 6.28)) + np.sin(2 * np.pi * (ff + beat) * t + g.uniform(0, 6.28)))
    return out * np.clip(t / attack, 0, 1) ** 2


def _crackle(g, N, rate_hz, tau, f_band=3500.0, q=0.9, env=None):
    """Sparse, random clicks (Poisson) through a band: crackle and sparks."""
    imp = np.zeros(N)
    cnt = int(rate_hz * N / SR)
    pos = g.integers(0, N, cnt)
    imp[pos] = g.uniform(-1, 1, cnt) * g.uniform(0.2, 1.0, cnt) ** 2
    x = filt(imp, [bq_bandpass(f_band, q)])
    if env is not None:
        x *= env
    return x * np.exp(-_t(N) / tau) if tau > 0 else x


# --------------------------------------------------------------------------- element hits


def hit_none(v):
    """A blunt, foam-white impact: a low body thump, a mid knock, a short foam fizz."""
    g = rng(SEED + 100 + v)
    N = _n(0.55)
    buf = np.zeros(N)
    buf += 0.9 * _thump(g.uniform(120, 150), g.uniform(52, 62), 0.07, N, g, click=0.6)
    k = _n(0.05)
    knock = filt(_noise(g, k), [bq_bandpass(g.uniform(900, 1400), 1.3)]) * _decay(k, 0.009)
    _place(buf, 0.5 * knock, 0.0)
    fizz = filt(_noise(g, N), [bq_highpass(3500, 0.7), bq_lowpass(9000, 0.7)])
    fizz *= _swell(N, 0.02, 1.0, 0.09) * (0.6 + 0.4 * smooth_noise(N, 60, g))
    buf += 0.10 * fizz + 0.6 * _bubbles(g, N, 10, 0.6, 1.4, 0.01, 0.2, amp=0.15)
    return _tail_fade(_room(buf, 0.6, 0.12, SEED + 101 + v))


def hit_fire(v):
    """A flare and crackle: a rising roar (ember to dusk gold, rising), embers popping, a warm thump."""
    g = rng(SEED + 200 + v)
    N = _n(0.75)
    t = _t(N)
    roar = _sweep_band(_noise(g, N), g.uniform(350, 450), g.uniform(1600, 2100), q=1.1, steps=16)
    roar *= _swell(N, 0.06, 1.5, 0.18) * (0.75 + 0.25 * smooth_noise(N, 25, g))
    buf = 0.7 * roar
    buf += 0.55 * _thump(110, 60, 0.06, N, g, click=0.4)
    buf += 0.9 * _crackle(g, N, 160, 0.25, f_band=2800, q=0.7, env=np.clip(t / 0.03, 0, 1))
    buf += 0.25 * filt(_noise(g, N), [bq_lowpass(300, 0.7)]) * _swell(N, 0.04, 1.0, 0.2)
    return _tail_fade(_room(buf, 0.7, 0.14, SEED + 201 + v))


def hit_ice(v):
    """Salt glass: a hard, bright strike, a cluster of glassy modes, and shards falling and tinkling."""
    g = rng(SEED + 300 + v)
    N = _n(0.9)
    buf = np.zeros(N)
    k = _n(0.012)
    _place(buf, 0.2 * filt(_noise(g, k), [bq_highpass(2500, 0.7)]) * _decay(k, 0.002), 0.0)
    buf += 0.35 * _thump(180, 120, 0.03, N, g, click=0.2)
    base = g.uniform(2300, 2900)
    for r in (1.0, 1.37, 1.81, 2.43):
        _place(buf, 0.22 * _glass(base * r * g.uniform(0.98, 1.02), 0.5, g, attack=0.002, t60=0.35), 0.0)
    for i in range(7):
        at = 0.05 + i * g.uniform(0.04, 0.08)
        f = base * g.uniform(1.4, 2.6) * (1 - 0.04 * i)
        _place(buf, 0.12 * (0.85 ** i) * _glass(f, 0.25, g, attack=0.0003, t60=0.12), at)
    return _tail_fade(_room(buf, 1.0, 0.18, SEED + 301 + v, high=7000))


def hit_lightning(v):
    """A starlight crackle: fast and brief, a dense crackle burst with a few high star points."""
    g = rng(SEED + 400 + v)
    N = _n(0.5)
    t = _t(N)
    env = np.clip(t / 0.002, 0, 1) * np.exp(-t / 0.06)
    buf = 0.6 * _crackle(g, N, 2500, 0.0, f_band=g.uniform(3000, 4200), q=0.6, env=env)
    buf += 0.5 * _crackle(g, N, 600, 0.0, f_band=1400, q=0.8, env=env)
    buf += 0.3 * _thump(200, 90, 0.03, N, g, click=0.5)
    for _ in range(4):
        f = g.uniform(4200, 7000)
        _place(buf, 0.05 * np.sin(2 * np.pi * f * _t(_n(0.2))) * _decay(_n(0.2), 0.04), g.uniform(0.0, 0.08))
    buf = filt(buf, [bq_highshelf(9000, -4)])
    return _tail_fade(_room(buf, 0.6, 0.15, SEED + 401 + v, high=8000))


def hit_water(v):
    """A spray: a turquoise splash burst, a body slap, falling droplets."""
    g = rng(SEED + 500 + v)
    N = _n(0.8)
    t = _t(N)
    buf = 0.5 * _thump(130, 70, 0.05, N, g, click=0.3)
    spray = filt(_noise(g, N), [bq_highpass(900, 0.7), bq_lowpass(7500, 0.7)])
    spray *= np.clip(t / 0.004, 0, 1) * np.exp(-t / 0.08) * (0.6 + 0.4 * smooth_noise(N, 90, g))
    buf += 0.45 * spray
    buf += 0.9 * _bubbles(g, N, 22, 0.8, 2.4, 0.005, 0.25, amp=0.25)
    for i in range(6):
        _place(buf, drip(g.uniform(0.3, 0.7), g.uniform(1.6, 3.2), seed=SEED + 510 + 10 * v + i),
               0.2 + g.uniform(0, 0.4))
    return _tail_fade(_room(buf, 0.7, 0.14, SEED + 501 + v))


def hit_holy(v):
    """A sun-gold chime: a soft impact, a bright metallophone dyad (a fifth), a rising shimmer."""
    g = rng(SEED + 600 + v)
    N = _n(1.1)
    buf = 0.35 * _thump(160, 90, 0.04, N, g, click=0.3)
    root = [n("E6"), n("D6"), n("F#6")][v % 3]
    _place(buf, metallophone_note(root, 0.7, seed=SEED + 610 + v, decay=0.9, hardness=0.55, ombak_hz=6.0), 0.0)
    _place(buf, metallophone_note(root + 7, 0.55, seed=SEED + 620 + v, decay=0.8, hardness=0.5, ombak_hz=6.5), 0.03)
    M = _n(0.6)
    shim = sum(np.sin(2 * np.pi * np.cumsum(midi_to_hz(root + 12) * r * np.linspace(1.0, 1.06, M)) / SR)
               for r in (1.0, 1.5, 2.0))
    _place(buf, 0.04 * shim * _swell(M, 0.12, 1.5, 0.15), 0.02)
    buf = filt(buf, [bq_highpass(200, 0.7)])
    return _tail_fade(_room(buf, 1.2, 0.2, SEED + 601 + v, high=8000))


# --------------------------------------------------------------------------- signature skills


def lamp_dive():
    """Rhen's Swell: an oil lamp's warm whoosh (flame, never glimmer), the dive, a heavy splash."""
    g = rng(SEED + 700)
    N = _n(2.0)
    t = _t(N)
    buf = np.zeros(N)
    # the lamp: a low, soft flame roar that flickers and swells (oil light: warm, no sparkle tones)
    M = _n(0.9)
    flame = filt(_noise(g, M), [bq_lowpass(700, 0.7), bq_highpass(90, 0.7), bq_peak(300, 4, 1.0)])
    flame *= _swell(M, 0.6, 1.6, 0.12) * (0.7 + 0.3 * smooth_noise(M, 14, g))
    _place(buf, 0.9 * flame, 0.0)
    # the dive: a whoosh falling in pitch
    D = _n(0.45)
    whoosh = _sweep_band(_noise(g, D), 2400, 380, q=1.6, steps=20) * _swell(D, 0.32, 2.0, 0.05)
    _place(buf, 0.8 * whoosh, 0.5)
    # the splash
    S = N - _n(0.92)
    sp = np.zeros(S)
    sp += 1.0 * _thump(95, 45, 0.11, S, g, click=0.6)
    burst = filt(_noise(g, S), [bq_highpass(500, 0.7), bq_lowpass(6000, 0.7)])
    sp += 0.6 * burst * np.clip(_t(S) / 0.005, 0, 1) * np.exp(-_t(S) / 0.14)
    sp += 1.0 * _bubbles(g, S, 40, 1.2, 4.5, 0.0, 0.45, amp=0.25)
    for i in range(8):
        _place(sp, drip(g.uniform(0.3, 0.6), g.uniform(2.0, 4.0), seed=SEED + 710 + i), 0.3 + g.uniform(0, 0.6))
    _place(buf, sp, 0.92)
    buf *= np.minimum(1.0, t / 0.01)
    return _tail_fade(_room(buf, 1.0, 0.16, SEED + 701), 0.15)


def shallows_verse():
    """Asha's Swell: shallow water lapping, and a soft rising metallophone line (original, pentatonic)."""
    g = rng(SEED + 800)
    N = _n(2.8)
    t = _t(N)
    lap_env = 0.55 + 0.45 * np.sin(2 * np.pi * 1.3 * t - 1.2) ** 2
    lap = filt(_noise(g, N), [bq_lowpass(1400, 0.7), bq_highpass(150, 0.7)]) * lap_env
    lap *= _swell(N, 0.4, 1.2, 1.4)
    buf = 0.35 * lap
    buf += 0.7 * _bubbles(g, N, 30, 1.5, 3.5, 0.1, 2.2, amp=0.12)
    # E5 F#5 A5 B5 E6: a plain rising pentatonic line, unevenly spaced like lapping
    line = [("E5", 0.10), ("F#5", 0.42), ("A5", 0.70), ("B5", 1.05), ("E6", 1.38)]
    for i, (note, at) in enumerate(line):
        vel = 0.35 + 0.06 * i
        _place(buf, metallophone_note(n(note), vel, seed=SEED + 810 + i, decay=1.4, hardness=0.3, ombak_hz=5.0), at)
    buf = filt(buf, [bq_highpass(120, 0.7)])
    return _tail_fade(_room(buf, 1.8, 0.28, SEED + 801, high=6000), 0.2)


def read_still():
    """Read: a still ring of gold points, soft small bells placed evenly, nothing moving."""
    g = rng(SEED + 900)
    N = _n(1.8)
    buf = np.zeros(N)
    pts = [n("B6"), n("E7"), n("F#7"), n("B6"), n("E7")]
    for i, m in enumerate(pts):
        _place(buf, 0.3 * _glass(midi_to_hz(m), 1.2, g, attack=0.002, t60=0.9,
                                 partials=((1.0, 1.0), (2.76, 0.18), (5.4, 0.05))), 0.04 + 0.13 * i)
    buf = filt(buf, [bq_highpass(400, 0.7)])
    return _tail_fade(_room(buf, 1.6, 0.3, SEED + 901, high=9000), 0.2)


def heal():
    """HP restored: a rising shimmer over a warm, soft chime."""
    g = rng(SEED + 1000)
    N = _n(1.5)
    t = _t(N)
    buf = np.zeros(N)
    shim = np.zeros(N)
    for i in range(9):
        f0 = midi_to_hz(n("A5")) * 2 ** (g.uniform(0, 24) / 12)
        shim += g.uniform(0.4, 1.0) * np.sin(2 * np.pi * np.cumsum(f0 * (1 + 0.25 * (t / t[-1]) ** 1.5)) / SR
                                             + g.uniform(0, 6.28))
    shim *= _swell(N, 0.5, 1.5, 0.35) * (0.7 + 0.3 * smooth_noise(N, 18, g))
    buf += 0.06 * shim
    for i, m in enumerate((n("A5"), n("C#6"), n("E6"))):
        _place(buf, metallophone_note(m, 0.4, seed=SEED + 1010 + i, decay=1.0, hardness=0.25, ombak_hz=5.0),
               0.05 + 0.12 * i)
    air = filt(_noise(g, N), [bq_bandpass(6000, 1.0)]) * _swell(N, 0.5, 1.5, 0.3)
    buf += 0.03 * air
    buf = filt(buf, [bq_highpass(250, 0.7)])
    return _tail_fade(_room(buf, 1.4, 0.25, SEED + 1001, high=9000), 0.15)


def status_apply():
    """A status added: sinking and dull, a muffled tone gliding down, a soft low knock."""
    g = rng(SEED + 1100)
    N = _n(0.9)
    t = _t(N)
    tone = _sine_glide(N, 420, 170, 0.6) + 0.4 * _sine_glide(N, 630, 240, 0.6, 1.0)
    tone *= _swell(N, 0.05, 1.0, 0.28)
    buf = 0.5 * filt(tone, [bq_lowpass(800, 0.7)])
    buf += 0.45 * _thump(90, 55, 0.08, N, g, click=0.3)
    mud = filt(_noise(g, N), [bq_lowpass(500, 0.7)]) * _swell(N, 0.08, 1.0, 0.25)
    buf += 0.2 * mud
    buf *= np.minimum(1.0, t / 0.004)
    return _tail_fade(_room(buf, 0.9, 0.18, SEED + 1101, high=3000), 0.1)


def ko_release():
    """A KO: the fighter's light released, airy motes rising slowly; sad, never a buzzer."""
    g = rng(SEED + 1200)
    N = _n(2.4)
    t = _t(N)
    breath = _sweep_band(_noise(g, N), 500, 3200, q=1.2, steps=16) * _swell(N, 0.5, 1.5, 0.8)
    buf = 0.25 * breath
    # a falling minor third underneath (B4 -> G#4), soft and short
    _place(buf, metallophone_note(n("B4"), 0.35, seed=SEED + 1210, decay=1.6, hardness=0.15, ombak_hz=3.0), 0.0)
    _place(buf, metallophone_note(n("G#4"), 0.3, seed=SEED + 1211, decay=1.8, hardness=0.12, ombak_hz=3.0), 0.32)
    # rising motes
    for i in range(10):
        at = 0.25 + i * 0.15 + g.uniform(-0.03, 0.03)
        M = _n(0.6)
        f0 = midi_to_hz(n("E6")) * 2 ** (g.uniform(-3, 9) / 12)
        mote = _sine_glide(M, f0, f0 * 1.12, 1.0, g.uniform(0, 6.28)) * _swell(M, 0.12, 1.5, 0.15)
        _place(buf, 0.06 * (1 - 0.05 * i) * mote, at)
    buf = filt(buf, [bq_highpass(180, 0.7)])
    return _tail_fade(_room(buf, 2.2, 0.32, SEED + 1201, high=8000), 0.3)


def bell_release():
    """The Drownbell dies: bell partials sliding seaward and down, a wash drawing away."""
    g = rng(SEED + 1300)
    N = _n(3.4)
    t = _t(N)
    b = _bell_partials(midi_to_hz(n("E3")), 3.4, g, t60=4.0, bright=0.6, glide_cents=700)
    buf = 0.6 * b
    wash = _sweep_band(_noise(g, N), 1800, 250, q=0.9, steps=16) * _swell(N, 0.5, 1.0, 1.2)
    buf += 0.25 * wash
    for i in range(8):
        M = _n(0.8)
        f0 = midi_to_hz(n("C#6")) * 2 ** (g.uniform(-5, 5) / 12)
        _place(buf, 0.03 * _sine_glide(M, f0, f0 * 0.82, 1.0) * _swell(M, 0.1, 1.0, 0.25), 0.3 + 0.25 * i)
    buf *= np.exp(-t / 2.2) * 0.4 + 0.6 * np.exp(-t / 6.0)
    buf = filt(buf, [bq_highpass(45, 0.7)])
    return _tail_fade(_room(buf, 2.6, 0.3, SEED + 1301, high=5000), 0.4)


# --------------------------------------------------------------------------- openings


def stinger_ambush(soft=False):
    """An ambush: dark, lacquer-red; a low gong, a low drum, and a held tension cluster (minor seconds)."""
    g = rng(SEED + 1400)
    N = _n(2.6)
    t = _t(N)
    buf = np.zeros(N)
    _place(buf, 0.8 * large_gong(n("D2"), 0.9, seed=SEED + 1410, t60=3.0)[:N], 0.0)
    buf += 0.7 * _thump(70, 38, 0.25, N, g, click=0.4)
    cluster = np.zeros(N)
    for m in (n("D4"), n("D#4"), n("A4"), n("A#4")):
        f = midi_to_hz(m)
        trem = 1 + 0.25 * np.sin(2 * np.pi * g.uniform(5.5, 7.0) * t)
        cluster += trem * (np.sin(2 * np.pi * f * t) + 0.3 * np.sin(4 * np.pi * f * t + 1.0))
    cluster = filt(cluster, [bq_lowpass(1800, 0.7)]) * _swell(N, 0.9, 1.6, 0.7)
    buf += 0.12 * cluster
    hiss = filt(_noise(g, N), [bq_bandpass(2500, 1.5)]) * _swell(N, 0.8, 2.0, 0.5)
    buf += 0.06 * hiss
    if soft:
        buf = filt(buf, [bq_highpass(140, 0.9), bq_highpass(140, 0.9)])
    return _tail_fade(_room(buf, 1.8, 0.22, SEED + 1401, high=5000), 0.3)


def stinger_preemptive():
    """A preemptive strike: bright, sun-gold; a quick rising metallophone figure and a kettle gong."""
    g = rng(SEED + 1500)
    N = _n(1.9)
    buf = np.zeros(N)
    for i, (note, at) in enumerate([("D6", 0.0), ("E6", 0.07), ("A6", 0.14)]):
        _place(buf, metallophone_note(n(note), 0.6 + 0.08 * i, seed=SEED + 1510 + i, decay=1.3, hardness=0.7,
                                      ombak_hz=6.5), at)
    _place(buf, 0.6 * kettle_gong(n("A4"), 0.6, seed=SEED + 1520, t60=1.6), 0.14)
    M = _n(0.9)
    shim = filt(_noise(g, M), [bq_bandpass(7000, 1.2)]) * _swell(M, 0.2, 1.5, 0.25)
    _place(buf, 0.05 * shim, 0.12)
    buf = filt(buf, [bq_highpass(200, 0.7)])
    return _tail_fade(_room(buf, 1.3, 0.22, SEED + 1501, high=9000), 0.25)


# --------------------------------------------------------------------------- the Drownbell


def _toll_dry(g, dur):
    """The struck bell (E2's hum an octave down: a huge bell) plus the slap of its sound off the water."""
    f0 = midi_to_hz(n("E2"))
    b = _bell_partials(f0, dur, g, t60=7.0, bright=1.0, glide_cents=8)
    N = len(b)
    knock = filt(_noise(g, _n(0.05)), [bq_lowpass(600, 0.7)]) * _decay(_n(0.05), 0.012)
    b[: len(knock)] += 0.4 * knock
    slap = np.zeros(N)
    d = _n(0.11)
    slap[d:] = filt(b[: N - d], [bq_lowpass(1500, 0.7)])
    return b + 0.35 * slap


def drownbell_toll(soft=False):
    """The toll in battle: a huge pitched bell heard across water (a long, wide hall)."""
    g = rng(SEED + 1600)
    x = _toll_dry(g, 6.0)
    if soft:
        x = filt(x, [bq_highpass(110, 0.9), bq_highpass(110, 0.9)])
    x = filt(x, [bq_highpass(30, 0.7)])
    return _tail_fade(_room(x, 4.5, 0.35, SEED + 1601, predelay=0.05, size=1.0, high=4500), 0.5)


def drownbell_toll_far():
    """The cutscene's toll: the same bell far off and heard from under the water (muffled, late, washed)."""
    g = rng(SEED + 1600)
    x = _toll_dry(g, 6.5)
    x = filt(x, [bq_lowpass(520, 0.8), bq_lowpass(700, 0.6), bq_highpass(35, 0.7), bq_peak(160, 3, 0.8)])
    N = len(x)
    t = _t(N)
    x *= np.clip(t / 0.25, 0, 1) ** 1.5           # distance: the transient is smeared away
    x *= 1 + 0.08 * smooth_noise(N, 1.2, g)        # a slow underwater waver
    pad = np.zeros(_n(0.3))
    x = np.concatenate([pad, x])
    return _tail_fade(_room(x, 5.5, 0.55, SEED + 1602, predelay=0.08, size=1.0, high=1500), 0.6)


def toll_gather():
    """The toll gathers: held motes drawn down the hood, a low hum swelling."""
    g = rng(SEED + 1700)
    N = _n(2.4)
    t = _t(N)
    f0 = midi_to_hz(n("E2"))
    hum = np.zeros(N)
    for k, a in ((1, 1.0), (2, 0.5), (3, 0.3), (4, 0.15), (6, 0.06)):
        hum += a * 0.5 * (np.sin(2 * np.pi * f0 * k * t) + np.sin(2 * np.pi * (f0 * k + 0.4 * k) * t + 1.3))
    hum *= _swell(N, 1.8, 2.0, 0.25)
    buf = 0.6 * hum
    for i in range(7):
        M = _n(0.7)
        f1 = midi_to_hz(n("B5")) * 2 ** (g.uniform(-4, 4) / 12)
        _place(buf, 0.03 * _sine_glide(M, f1, f1 * 0.7, 1.2) * _swell(M, 0.15, 1.5, 0.2), 0.1 + 0.24 * i)
    buf = filt(buf, [bq_highpass(35, 0.7)])
    return _tail_fade(_room(buf, 1.8, 0.2, SEED + 1701, high=3000), 0.25)


def rim_crack(v):
    """A landed rim hit: a stone and bronze crack, a short bronze ring, sparks."""
    g = rng(SEED + 1800 + v)
    N = _n(0.7)
    buf = np.zeros(N)
    k = _n(0.02)
    crack = filt(_noise(g, k), [bq_bandpass(g.uniform(2200, 3200), 0.9)]) * _decay(k, 0.003, 0.0002)
    _place(buf, 0.4 * crack, 0.0)
    buf += 0.5 * _thump(160, 100, 0.03, N, g, click=0.6)
    t = _t(N)
    for r, a, tau in ((1.0, 1.0, 0.25), (1.58, 0.6, 0.16), (2.31, 0.4, 0.1), (3.07, 0.25, 0.07)):
        f = g.uniform(820, 980) * r
        buf += 0.12 * a * np.sin(2 * np.pi * f * t + g.uniform(0, 6.28)) * _decay(N, tau)
    buf += 0.7 * _crackle(g, N, 220, 0.12, f_band=5000, q=0.8)
    return _tail_fade(_room(buf, 0.8, 0.15, SEED + 1801 + v, high=7000))


def rim_break():
    """The third rim hit breaks the charge: a bigger crack, a cyan burst rushing out, the bronze ringing."""
    g = rng(SEED + 1900)
    N = _n(1.7)
    t = _t(N)
    buf = np.zeros(N)
    k = _n(0.04)
    crack = filt(_noise(g, k), [bq_bandpass(1800, 0.6)]) * _decay(k, 0.006, 0.0002)
    _place(buf, 1.0 * crack, 0.0)
    buf += 0.8 * _thump(120, 50, 0.12, N, g, click=0.8)
    burst = _sweep_band(_noise(g, N), 600, 5000, q=1.0, steps=18) * _swell(N, 0.12, 1.0, 0.3)
    buf += 0.35 * burst
    for r, a, tau in ((1.0, 1.0, 0.7), (1.58, 0.6, 0.45), (2.31, 0.4, 0.3), (3.07, 0.25, 0.2)):
        buf += 0.14 * a * np.sin(2 * np.pi * 700 * r * t + g.uniform(0, 6.28)) * _decay(N, tau)
    for m in (n("C#6"), n("G#6"), n("D#7")):
        _place(buf, 0.08 * _glass(midi_to_hz(m), 1.2, g, attack=0.002, t60=0.9), 0.03)
    buf += 0.6 * _crackle(g, N, 300, 0.2, f_band=5500, q=0.8)
    return _tail_fade(_room(buf, 1.4, 0.2, SEED + 1901, high=8000), 0.25)


def polyp_rise():
    """A polyp rises from the water: a wet, bubbling surge."""
    g = rng(SEED + 2000)
    N = _n(1.5)
    surge = filt(_noise(g, N), [bq_lowpass(900, 0.7), bq_highpass(80, 0.7)]) * _swell(N, 0.7, 1.8, 0.25)
    buf = 0.5 * surge
    buf += 1.0 * _bubbles(g, N, 60, 1.5, 3.5, 0.0, 0.95, amp=0.18, grow=1.5)
    buf += 0.35 * _sweep_band(_noise(g, N), 300, 1200, q=1.5, steps=12) * _swell(N, 0.8, 2.0, 0.2)
    buf += 0.3 * _thump(80, 50, 0.15, N, g, click=0.2) * (_t(N) > 0.0)
    return _tail_fade(_room(buf, 1.0, 0.15, SEED + 2001, high=4000), 0.2)


def polyp_mend():
    """A polyp mends the bell: a stream of held motes from polyp to bell, sinking a little as they go."""
    g = rng(SEED + 2100)
    N = _n(1.8)
    buf = np.zeros(N)
    for i in range(14):
        at = 0.05 + i * 0.08 + g.uniform(-0.015, 0.015)
        M = _n(0.4)
        f0 = midi_to_hz(n("G#5")) * 2 ** (g.uniform(-2, 5) / 12) * (1 - 0.01 * i)
        _place(buf, 0.08 * _sine_glide(M, f0, f0 * 0.93, 1.0, g.uniform(0, 6.28)) * _swell(M, 0.04, 1.0, 0.12), at)
    hum = filt(_noise(g, N), [bq_bandpass(700, 2.0)]) * _swell(N, 0.6, 1.5, 0.6)
    buf += 0.12 * hum
    buf += 0.5 * _bubbles(g, N, 14, 2.0, 3.5, 0.0, 1.2, amp=0.1)
    buf = filt(buf, [bq_highpass(200, 0.7)])
    return _tail_fade(_room(buf, 1.2, 0.22, SEED + 2101, high=7000), 0.2)


def floodnet():
    """Call Ilun, Floodnet: bound light threads laid on the water, a glassy net that holds, then lets go."""
    g = rng(SEED + 2200)
    N = _n(3.2)
    t = _t(N)
    buf = np.zeros(N)
    # the net: sustained glass tones on an open, still chord, each thread fading in a little later
    for i, m in enumerate((n("E5"), n("B5"), n("F#6"), n("G#6"), n("C#7"), n("E7"))):
        x = _glass(midi_to_hz(m), 3.0, g, attack=0.25 + 0.05 * i, t60=6.0)
        x *= _swell(len(x), 1.2, 1.0, 1.4)
        _place(buf, 0.09 * x, 0.06 * i)
    # threads being laid: quick, soft glass ticks
    for i in range(12):
        f = midi_to_hz(n("B6")) * 2 ** (g.uniform(-5, 7) / 12)
        _place(buf, 0.05 * _glass(f, 0.3, g, attack=0.001, t60=0.2), 0.02 + 0.07 * i)
    lap = filt(_noise(g, N), [bq_lowpass(1100, 0.7), bq_highpass(150, 0.7)])
    lap *= (0.6 + 0.4 * np.sin(2 * np.pi * 0.9 * t) ** 2) * _swell(N, 0.6, 1.0, 1.8)
    buf += 0.12 * lap
    buf = filt(buf, [bq_highpass(150, 0.7)])
    return _tail_fade(_room(buf, 2.4, 0.3, SEED + 2201, high=9000), 0.4)


def flood(soft=False):
    """The Flood: the water rising around the dais, a long low surge over 7 s (sub-bass dropped when soft)."""
    g = rng(SEED + 2300)
    N = _n(7.5)
    t = _t(N)
    rise = np.clip(t / 6.0, 0, 1)
    shape = (0.5 - 0.5 * np.cos(np.pi * rise)) * np.where(t > 6.3, np.exp(-(t - 6.3) / 0.45), 1.0)
    shape = shape * 0.85 + 0.15 * np.clip(t / 0.6, 0, 1) * np.where(t > 6.3, np.exp(-(t - 6.3) / 0.45), 1.0)
    buf = np.zeros(N)
    noise = _noise(g, N)
    # body of the water: low noise whose band climbs as it rises
    body = np.zeros(N)
    steps = 10
    for i in range(steps):
        c = i / (steps - 1)
        fc = 220 * (900 / 220) ** c
        w = np.clip(1 - np.abs(rise - c) * (steps - 1), 0, 1)
        body += w * filt(noise, [bq_lowpass(fc, 0.8)])
    body *= 1 + 0.35 * np.sin(2 * np.pi * 0.42 * t + 0.4 * smooth_noise(N, 0.5, g))  # slow swells
    buf += 0.6 * body
    # turbulence: a mid wash with a slow shimmer
    wash = filt(_noise(g, N), [bq_bandpass(1300, 0.9)]) * (0.6 + 0.4 * smooth_noise(N, 3.0, g))
    buf += 0.12 * wash * rise
    buf += 0.8 * _bubbles(g, N, 90, 2.0, 6.0, 0.4, 6.4, amp=0.12, grow=0.5)
    if not soft:
        sub = np.sin(2 * np.pi * np.cumsum(36 + 10 * rise + 1.5 * smooth_noise(N, 0.8, g)) / SR)
        buf += 0.7 * sub * (0.4 + 0.6 * rise)
    buf *= shape
    if soft:
        buf = filt(buf, [bq_highpass(90, 0.9), bq_highpass(90, 0.9)])
    else:
        buf = filt(buf, [bq_highpass(24, 0.7)])
    return _tail_fade(_room(buf, 2.0, 0.18, SEED + 2301, high=3500), 0.4)


# --------------------------------------------------------------------------- the Vowbound


def vowbound_call():
    """A Vowbound answers: glass and water rising together, solemn (open fifths, slow)."""
    g = rng(SEED + 2400)
    N = _n(2.8)
    t = _t(N)
    buf = np.zeros(N)
    for i, (m, at) in enumerate(((n("A3"), 0.0), (n("E4"), 0.25), (n("A4"), 0.5), (n("B4"), 0.8),
                                 (n("E5"), 1.1))):
        x = _glass(midi_to_hz(m), 2.6 - at, g, attack=0.35, t60=4.0)
        _place(buf, 0.12 * (0.9 ** i) * x * _swell(len(x), 1.0, 1.0, 1.0), at)
    rush = _sweep_band(_noise(g, N), 250, 2200, q=1.0, steps=16) * _swell(N, 1.4, 2.0, 0.6)
    buf += 0.22 * rush
    buf += 0.6 * _bubbles(g, N, 30, 1.0, 3.0, 0.3, 1.6, amp=0.12, grow=-0.5)
    buf += 0.25 * _thump(70, 45, 0.4, N, g, click=0.0) * np.clip(t / 0.3, 0, 1)
    buf = filt(buf, [bq_highpass(55, 0.7)])
    return _tail_fade(_room(buf, 2.4, 0.3, SEED + 2401, high=7000), 0.4)


def vowbound_dismiss():
    """A Vowbound goes back: gently falling away, glass tones stepping down, the water letting go."""
    g = rng(SEED + 2500)
    N = _n(2.0)
    buf = np.zeros(N)
    for i, (m, at) in enumerate(((n("E5"), 0.0), (n("B4"), 0.2), (n("A4"), 0.42), (n("E4"), 0.66))):
        x = _glass(midi_to_hz(m), 1.4, g, attack=0.03, t60=1.8)
        _place(buf, 0.1 * (0.85 ** i) * x, at)
    ebb = _sweep_band(_noise(g, N), 1800, 300, q=1.0, steps=14) * _swell(N, 0.25, 1.0, 0.6)
    buf += 0.14 * ebb
    buf = filt(buf, [bq_highpass(120, 0.7)])
    return _tail_fade(_room(buf, 2.0, 0.3, SEED + 2501, high=7000), 0.3)


# --------------------------------------------------------------------------- outcomes


def victory():
    """Victory, under 3 s: a short, original sun-gold figure (D5 E5 A5, then a held fifth) over a soft gong.
    Relief more than triumph (pillar 1)."""
    g = rng(SEED + 2600)
    N = _n(2.9)
    buf = np.zeros(N)
    for i, (note, at, vel) in enumerate([("D5", 0.0, 0.55), ("E5", 0.16, 0.55), ("A5", 0.32, 0.7)]):
        _place(buf, metallophone_note(n(note), vel, seed=SEED + 2610 + i, decay=1.6, hardness=0.55, ombak_hz=6.0),
               at)
    for i, note in enumerate(("D5", "A5", "E6")):
        _place(buf, metallophone_note(n(note), 0.55, seed=SEED + 2620 + i, decay=2.4, hardness=0.4, ombak_hz=5.5),
               0.62 + 0.02 * i)
    _place(buf, 0.45 * kettle_gong(n("D4"), 0.55, seed=SEED + 2630, t60=2.2), 0.62)
    M = _n(1.4)
    shim = filt(_noise(g, M), [bq_bandpass(6500, 1.4)]) * _swell(M, 0.3, 1.5, 0.4)
    _place(buf, 0.03 * shim, 0.62)
    buf = filt(buf, [bq_highpass(120, 0.7)])
    return _tail_fade(_room(buf, 1.6, 0.24, SEED + 2601, high=9000)[:N], 0.5)


def defeat():
    """Defeat: a soft falling, low bars stepping down under a muffled breath."""
    g = rng(SEED + 2700)
    N = _n(2.8)
    buf = np.zeros(N)
    for i, (note, at) in enumerate([("A4", 0.0), ("E4", 0.4), ("C4", 0.85), ("A3", 1.35)]):
        _place(buf, metallophone_note(n(note), 0.45 - 0.04 * i, seed=SEED + 2710 + i, decay=2.0, hardness=0.12,
                                      ombak_hz=3.0), at)
    breath = filt(_noise(g, N), [bq_bandpass(900, 1.2)]) * _swell(N, 0.6, 1.0, 1.0)
    buf += 0.05 * breath
    buf = filt(buf, [bq_lowpass(2200, 0.7), bq_highpass(90, 0.7)])
    return _tail_fade(_room(buf, 2.2, 0.3, SEED + 2701, high=4000), 0.4)


def escape():
    """The party escapes: a quick wash drawing away."""
    g = rng(SEED + 2800)
    N = _n(1.0)
    w = _sweep_band(_noise(g, N), 1600, 350, q=1.2, steps=14) * _swell(N, 0.15, 1.0, 0.3)
    buf = 0.6 * w + 0.4 * _bubbles(g, N, 12, 1.5, 3.0, 0.05, 0.5, amp=0.12)
    return _tail_fade(_room(buf, 0.9, 0.18, SEED + 2801, high=5000), 0.15)


# --------------------------------------------------------------------------- the set


def _variants(name, fn, count, target=COMBAT):
    return {f"{SUB}/{name}_{i + 1}": ((lambda i=i: fn(i)), target) for i in range(count)}


SFX: dict = {}
SFX.update(_variants("hit_none", hit_none, 3))
SFX.update(_variants("hit_fire", hit_fire, 3))
SFX.update(_variants("hit_ice", hit_ice, 3))
SFX.update(_variants("hit_lightning", hit_lightning, 3))
SFX.update(_variants("hit_water", hit_water, 3))
SFX.update(_variants("hit_holy", hit_holy, 2))
SFX.update({
    f"{SUB}/lamp_dive": (lamp_dive, COMBAT),
    f"{SUB}/shallows_verse": (shallows_verse, COMBAT),
    f"{SUB}/read": (read_still, QUIET),
    f"{SUB}/heal": (heal, -19.0),
    f"{SUB}/status_apply": (status_apply, -20.0),
    f"{SUB}/ko_release": (ko_release, COMBAT),
    f"{SUB}/bell_release": (bell_release, STING),
    f"{SUB}/stinger_ambush": (stinger_ambush, STING),
    f"{SUB}/stinger_ambush_soft": ((lambda: stinger_ambush(True)), -17.0),
    f"{SUB}/stinger_preemptive": (stinger_preemptive, STING),
    f"{SUB}/drownbell_toll": (drownbell_toll, STING),
    f"{SUB}/drownbell_toll_soft": ((lambda: drownbell_toll(True)), -17.0),
    f"{SUB}/toll_gather": (toll_gather, QUIET),
})
SFX.update(_variants("rim_crack", rim_crack, 3))
SFX.update({
    f"{SUB}/rim_break": (rim_break, COMBAT),
    f"{SUB}/polyp_rise": (polyp_rise, -19.0),
    f"{SUB}/polyp_mend": (polyp_mend, QUIET),
    f"{SUB}/floodnet": (floodnet, COMBAT),
    f"{SUB}/flood": (flood, COMBAT),
    f"{SUB}/flood_soft": ((lambda: flood(True)), -20.0),
    f"{SUB}/vowbound_call": (vowbound_call, COMBAT),
    f"{SUB}/vowbound_dismiss": (vowbound_dismiss, -19.0),
    f"{SUB}/victory": (victory, STING),
    f"{SUB}/defeat": (defeat, COMBAT),
    f"{SUB}/escape": (escape, -19.0),
    "drownbell_toll": (drownbell_toll_far, COMBAT),
})

# render_all.py's JOBS entry lists these (relative to assets/audio/sfx).
FILES = [name + ".ogg" for name in SFX]


def render(out_dir: str = OUT_DIR, verbose: bool = True, only: str = "") -> dict:
    res = {}
    for name, (fn, target) in SFX.items():
        if only and only not in name:
            continue
        x = normalize_momentary(fn(), target, ceiling_db=CEILING)
        path = os.path.join(out_dir, name + ".ogg")
        write_ogg(path, x, quality=QUALITY)
        m = measure(x)
        res[name] = m
        if verbose:
            print(f"{name}: {m['seconds']:.3f}s  momentary max {m['momentary_max_lufs']:.2f} LUFS  "
                  f"peak {m['sample_peak_dbfs']:.2f} dBFS", flush=True)
    return res


if __name__ == "__main__":
    render(only=sys.argv[1] if len(sys.argv) > 1 else "")
