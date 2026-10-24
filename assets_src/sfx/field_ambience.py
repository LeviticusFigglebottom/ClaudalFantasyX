"""Field ambience beds (M2-AUD-05): six seamless stereo loops for Haluna and the Shell Shrine.

Everything here is synthesized from noise, oscillators and simple physical models in this file and
tools/audio/synth/ (SPEC §2, §9: no samples, no recordings, no generated audio). Each bed is one loop body
(LOOPSTART = 0, LOOPLENGTH = the whole file) built so that the sample after the last is the first:

* **Continuous layers are periodic by construction.** Noise is shaped in the frequency domain on the loop's own
  FFT grid (`circ_noise`), so it is a circular signal, and every modulator is a sum of whole cycles per loop
  (`plfo`, `snap`). Products and sums of periodic signals stay periodic.
* **Events wrap.** Calls, hits, creaks, drips and chirps are placed with `LoopMixer.add`, which adds modulo the
  loop length, and the bus filters and the reverb run in steady state (LoopMixer's wrap-around pre-roll).
* **Master.** `master_loop` to -26 LUFS integrated with a -6 dBFS ceiling (mix.md §2, ambience loops),
  then Ogg Vorbis stereo with LOOPSTART/LOOPLENGTH tags and a `.loop.json` sidecar. The beds use q1, not mix.md's
  q3 for ambient material: they are noise-dominated, so Vorbis spends close to its nominal rate on them, and q3 put
  the six at 3.1 MiB against the 2.5 MiB budget (q1: 2.36 MiB). They play at -26 LUFS under music.

Beds (assets/audio/ambience/):
    haluna_day.ogg       48 s  village life far off: palm rustle in the trade wind, gull-like calls (synthesized
                               glides with a rough voice), distant mallet work on a hull, rope creak, and a few
                               people talking somewhere, murmured as unintelligible formant hum (no words)
    haluna_night.ogg     44 s  crickets (pulsed chirps from four individuals and a soft tree-cricket trill),
                               water lapping the shore, and a lamp-lit quiet: one far-off pair of voices, a shutter
    surf.ogg             42 s  beach waves: six breakers with their own periods (6-8 s), each a swell, a break,
                               the foam run-up and a fizzing backwash, over a distant roar
    dock.ogg             40 s  water slapping the pilings on an 8-swell cycle, plank and piling creak, rope strain,
                               a moored hull knocking now and then
    shrine_interior.ogg  45 s  still water, two distant drips (Minnaert bubbles) and strays, stone room tone; sparse,
                               because it plays under the temple cue
    wind.ogg             40 s  a neutral wind bed (banded noise with gusts, a faint whistle at the peaks); the runtime
                               scales its level with the zone's wind speed (ambience.json `wind`)

Render:  python3 assets_src/sfx/field_ambience.py   (or tools/audio/render_all.py --only field_ambience)
"""
from __future__ import annotations

import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools", "audio"))

import numpy as np  # noqa: E402

from synth.dsp import (SR, bq_bandpass, bq_highpass, bq_lowpass, bq_peak, filt, freq_response,  # noqa: E402
                       rng)
from synth.looping import LoopMixer, master_loop, write_loop_sidecar  # noqa: E402
from synth.mixer import measure, write_ogg  # noqa: E402
from synth.reverb import ModFDNReverb  # noqa: E402
from synth.voice import sing  # noqa: E402
from synth.water import bubble, drip  # noqa: E402

OUT_DIR = os.path.join(ROOT, "assets", "audio", "ambience")
SEED = 20261124
TARGET_LUFS = -26.0
CEILING_DB = -6.0
QUALITY = 1.0  # see the module docstring: q3 would put the six beds at 3.1 MiB
LOOPS = {"haluna_day": 48.0, "haluna_night": 44.0, "surf": 42.0, "dock": 40.0, "shrine_interior": 45.0,
         "wind": 40.0}


# --------------------------------------------------------------------------- periodic building blocks


def circ_noise(L: int, g: np.random.Generator, sections) -> np.ndarray:
    """White noise of exactly L samples shaped by biquads on the loop's own FFT grid: a circular signal (its
    end runs into its start), unit RMS."""
    X = np.fft.rfft(g.standard_normal(L))
    X *= np.abs(freq_response(sections, L)) if sections else 1.0
    X[0] = 0.0
    x = np.fft.irfft(X, L)
    return x / (np.std(x) + 1e-12)


def stereo_noise(L: int, g: np.random.Generator, sections, corr: float = 0.4) -> np.ndarray:
    """(L, 2) circular noise whose channels correlate by about `corr`."""
    c, a, b = (circ_noise(L, g, sections) for _ in range(3))
    k = np.sqrt(corr)
    m = np.sqrt(1 - corr)
    return np.stack([k * c + m * a, k * c + m * b], axis=1)


def plfo(L: int, hz: float, g: np.random.Generator) -> np.ndarray:
    """A slow random wobble in [-1, 1] made only of whole cycles per loop up to `hz` (periodic)."""
    K = max(1, int(round(hz * L / SR)))
    X = np.zeros(L // 2 + 1, dtype=np.complex128)
    k = np.arange(1, K + 1)
    X[1: K + 1] = (g.standard_normal(K) + 1j * g.standard_normal(K)) / np.sqrt(k)
    x = np.fft.irfft(X, L)
    return x / (np.abs(x).max() + 1e-12)


def snap(hz: float, L: int) -> float:
    """The nearest frequency with a whole number of cycles in L samples."""
    return max(1, round(hz * L / SR)) * SR / L


def schedule(L: int, period: float, g: np.random.Generator, jitter: float = 0.08) -> list[float]:
    """Event times (s) over one loop at about `period`, the count rounded so the loop holds whole periods."""
    n = max(1, int(round(L / SR / period)))
    p = L / SR / n
    return [(i + float(g.uniform(-jitter, jitter))) * p % (L / SR) for i in range(n)]


def env_ad(n: int, attack: float, decay: float) -> np.ndarray:
    t = np.arange(n) / SR
    return np.clip(t / max(attack, 1e-4), 0, 1) * np.exp(-np.maximum(t - attack, 0) / decay)


def burst(g: np.random.Generator, sec: float, sections, attack: float, decay: float) -> np.ndarray:
    n = int(sec * SR)
    return filt(g.standard_normal(n), sections) * env_ad(n, attack, decay)


def modal(freqs, decays, amps, sec: float, g: np.random.Generator, click: float = 0.0) -> np.ndarray:
    """A struck body: decaying sinusoids at random phase (plus an optional noise click)."""
    n = int(sec * SR)
    t = np.arange(n) / SR
    y = np.zeros(n)
    for f, d, a in zip(freqs, decays, amps):
        y += a * np.exp(-t / d) * np.sin(2 * np.pi * f * t + g.uniform(0, 6.28))
    if click > 0:
        k = int(0.003 * SR)
        y[:k] += click * g.standard_normal(k) * np.linspace(1, 0, k)
    return y * np.minimum(1.0, t / 0.0007)


def stick_slip(g: np.random.Generator, dur: float, lo: float, hi: float, body, q: float = 6.0) -> np.ndarray:
    """A creak: friction releasing as an impulse train whose rate glides lo -> hi -> lo, through body
    resonances (wood or rope fibre)."""
    n = int(dur * SR)
    t = np.arange(n) / SR
    shape = np.sin(np.pi * t / dur) ** 1.5
    rate = lo + (hi - lo) * shape
    rate *= 1 + 0.15 * np.cumsum(g.standard_normal(n)) / np.sqrt(n) * 0.3
    ph = np.cumsum(np.maximum(rate, 1.0)) / SR
    imp = np.zeros(n)
    hits = np.nonzero(np.diff(np.floor(ph)) > 0)[0] + 1
    imp[hits] = g.uniform(0.5, 1.0, len(hits))
    y = sum(a * filt(imp, [bq_bandpass(f, q)]) for f, a in body)
    y = y * shape * np.clip(t / 0.03, 0, 1)
    return y / (np.abs(y).max() + 1e-12)


def upsample4(x: np.ndarray) -> np.ndarray:
    """11.025 kHz -> 44.1 kHz by zero-padding the spectrum (exact band-limited interpolation)."""
    n = len(x) * 4
    X = np.fft.rfft(x)
    Xu = np.zeros(n // 2 + 1, dtype=np.complex128)
    Xu[: len(X)] = X
    return np.fft.irfft(Xu, n) * 4


# --------------------------------------------------------------------------- sources


def gull_call(g: np.random.Generator) -> np.ndarray:
    """A gull-like call series: 2-5 'kyow' notes, each a fast rise and a long fall of a rough, bright voice
    (harmonics weighted by a 2.8 kHz resonance, amplitude roughness at ~70 Hz, a little breath)."""
    notes = int(g.integers(2, 6))
    out = []
    for i in range(notes):
        dur = float(g.uniform(0.22, 0.42)) * (1.25 if i == 0 else 1.0)
        n = int(dur * SR)
        t = np.arange(n) / SR
        top = float(g.uniform(1250, 1650)) * (1.0 - 0.04 * i)
        f0 = top * (0.72 + 0.28 * np.minimum(1, t / 0.05)) * (1 - 0.32 * np.clip((t - 0.05) / dur, 0, 1) ** 1.3)
        ph = 2 * np.pi * np.cumsum(f0) / SR
        y = np.zeros(n)
        for k in range(1, 7):
            fk = k * f0.mean()
            w = (k ** -1.1) * (1.0 / (1.0 + ((fk - 2800.0) / 1400.0) ** 2) + 0.2)
            y += w * np.sin(k * ph)
        rough = 1 + 0.35 * np.sin(2 * np.pi * float(g.uniform(55, 85)) * t)
        env = np.clip(t / 0.02, 0, 1) * np.clip((dur - t) / 0.08, 0, 1) ** 1.5
        y = y * rough * env + 0.04 * filt(g.standard_normal(n), [bq_bandpass(3000, 1.0)]) * env
        out.append(y)
        out.append(np.zeros(int(float(g.uniform(0.08, 0.2)) * SR)))
    return np.concatenate(out)


def mallet_cluster(g: np.random.Generator) -> np.ndarray:
    """A run of 4-8 mallet blows on a hull plank, with the slap of a house wall 0.16 s later."""
    hits = int(g.integers(4, 9))
    gap = float(g.uniform(0.5, 0.75))
    buf = np.zeros(int((hits * gap + 1.0) * SR))
    base = float(g.uniform(0.9, 1.15))
    for i in range(hits):
        f = [180 * base, 410 * base, 760 * base, 1250 * base]
        hit = modal(f, [0.09, 0.05, 0.03, 0.018], [1.0, 0.6, 0.35, 0.2], 0.35, g, click=0.5)
        s = int((i * gap + float(g.uniform(-0.03, 0.03)) + 0.03) * SR)
        v = float(g.uniform(0.6, 1.0))
        buf[s: s + len(hit)] += v * hit[: len(buf) - s]
    echo = int(0.16 * SR)
    buf[echo:] += 0.25 * buf[:-echo]
    return buf


def murmur_phrase(g: np.random.Generator, high: bool) -> np.ndarray:
    """One person talking far off: 1.5-3 s of vowel and nasal syllables on a speech-like falling contour. With
    no consonants and everything above ~1 kHz gone, it reads as voices, never as words."""
    syl = int(g.integers(6, 14))
    phon, pitch = [], []
    base = float(g.uniform(55, 60)) if high else float(g.uniform(45, 50))
    for i in range(syl):
        d = float(g.uniform(0.11, 0.24))
        phon.append((str(g.choice(["a", "e", "o", "u", "i", "m", "n", "a", "o"])), d))
        fall = -3.0 * i / syl
        pitch.append((base + fall + float(g.normal(0, 1.2)), d))
    y = sing(phon, pitch, vel=0.6, seed=int(g.integers(1 << 30)), sr=11025, scale=1.17 if high else 1.0,
             tilt=1.6, breath=0.1, vib_cents=0.0, jitter_cents=12.0, max_f=2400.0, dec=16, release=0.15)
    return filt(upsample4(y), [bq_lowpass(950, 0.7), bq_highpass(140, 0.7)])


def cricket_chirp(g: np.random.Generator, carrier: float, pulses: int, rate: float) -> np.ndarray:
    """A field-cricket chirp: `pulses` tone pulses at `rate` Hz, each a sin^2 burst with a small downward glide."""
    pl = 0.6 / rate
    n = int((pulses / rate + 0.02) * SR)
    y = np.zeros(n)
    for i in range(pulses):
        m = int(pl * SR)
        t = np.arange(m) / SR
        f = carrier * (1 - 0.015 * t / pl)
        p = np.sin(np.pi * t / pl) ** 2 * np.sin(2 * np.pi * np.cumsum(f) / SR) * (0.8 + 0.2 * g.random())
        s = int(i / rate * SR)
        y[s: s + m] += p
    return y


def lap(g: np.random.Generator, size: float = 1.0) -> np.ndarray:
    """A wavelet against the sand or a hull: a low water burst, one to three bubbles, a little spray."""
    y = burst(g, 0.6, [bq_lowpass(520 * size ** -0.3, 0.7), bq_highpass(70, 0.7)], 0.04, 0.16 * size)
    for _ in range(int(g.integers(1, 4))):
        b = bubble(float(g.uniform(4.0, 9.0)), float(g.uniform(0.15, 0.4)), rise=0.08)
        s = int(float(g.uniform(0.02, 0.18)) * SR)
        y[s: s + len(b)] += b[: len(y) - s]
    y[: int(0.06 * SR)] += 0.12 * burst(g, 0.06, [bq_bandpass(3500, 0.8)], 0.005, 0.02)
    return y


def slap(g: np.random.Generator) -> np.ndarray:
    """Water slapping a piling: a sharp low burst through the hollow of the post, bubbles, spray."""
    y = burst(g, 0.5, [bq_lowpass(950, 0.7)], 0.004, 0.06)
    y = 0.6 * y + filt(y, [bq_bandpass(float(g.uniform(240, 420)), 4.0)]) * 1.6
    for _ in range(int(g.integers(1, 3))):
        b = bubble(float(g.uniform(3.0, 7.0)), float(g.uniform(0.2, 0.4)), rise=0.1)
        s = int(float(g.uniform(0.01, 0.08)) * SR)
        y[s: s + len(b)] += b[: len(y) - s]
    y[: int(0.05 * SR)] += 0.2 * burst(g, 0.05, [bq_bandpass(4000, 0.8)], 0.002, 0.015)
    return y


# --------------------------------------------------------------------------- beds


def _mixer(name: str) -> tuple[LoopMixer, int]:
    mx = LoopMixer(intro_s=0.0, loop_s=LOOPS[name], preroll_s=6.0)
    return mx, mx.L


def _outdoor(seed: int) -> ModFDNReverb:
    return ModFDNReverb(rt60=1.1, rt60_high=0.5, predelay=0.03, size=1.6, mod_depth=6.0, mod_rate=0.3,
                        early_level=0.35, lowcut=150.0, highcut=6000.0, seed=seed)


def haluna_day(g: np.random.Generator) -> tuple[LoopMixer, ModFDNReverb]:
    mx, L = _mixer("haluna_day")
    far = lambda x: filt(x, [bq_lowpass(2600, 0.7)])  # noqa: E731
    mx.bus("air", -14.0)
    mx.bus("palms", -9.0, send=0.1)
    mx.bus("gulls", -13.0, send=0.35, process=lambda x: filt(x, [bq_lowpass(4200, 0.7)]))
    mx.bus("work", -17.0, send=0.4, process=far)
    mx.bus("rope", -20.0, send=0.25, process=far)
    mx.bus("voices", -12.0, send=0.45)
    # the town's air: a soft low noise floor that breathes with the trade wind
    gust = 0.5 + 0.5 * plfo(L, 0.12, g)
    mx.add("air", stereo_noise(L, g, [bq_lowpass(420, 0.6), bq_highpass(60, 0.7)], 0.6) * (0.8 + 0.2 * gust)[:, None],
           0.0)
    # palm rustle: bright noise with a leaf-clatter grain, louder in the gusts
    clat = np.abs(circ_noise(L, g, [bq_lowpass(28, 0.7)]))
    clat = clat / clat.max()
    leaves = stereo_noise(L, g, [bq_bandpass(4200, 0.6), bq_highpass(1800, 0.7)], 0.25)
    mx.add("palms", leaves * ((0.25 + 0.75 * clat) * (0.2 + 0.8 * gust ** 1.5))[:, None], 0.0)
    for t in schedule(L, 10.0, g, 0.3):
        mx.add("gulls", gull_call(g), t, pan=float(g.uniform(-0.8, 0.8)), gain=float(g.uniform(0.5, 1.0)))
    for t in (6.0, 29.5):
        mx.add("work", mallet_cluster(g), t + float(g.uniform(-1, 1)), pan=float(g.uniform(-0.6, -0.2)))
    for t in (3.0, 17.0, 38.0):
        c = stick_slip(g, float(g.uniform(0.6, 1.1)), 18, 70, [(420, 1.0), (880, 0.6), (1500, 0.3)])
        mx.add("rope", c, t, pan=float(g.uniform(0.2, 0.7)))
    t = 1.0
    while t < LOOPS["haluna_day"] - 2.0:
        hi = bool(g.random() < 0.5)
        mx.add("voices", murmur_phrase(g, hi), t, pan=float(g.uniform(-0.5, 0.5)), gain=float(g.uniform(0.5, 1.0)))
        t += float(g.uniform(2.0, 5.5))
    return mx, _outdoor(SEED % 9973 + 1)


def haluna_night(g: np.random.Generator) -> tuple[LoopMixer, ModFDNReverb]:
    mx, L = _mixer("haluna_night")
    loop_s = LOOPS["haluna_night"]
    mx.bus("floor", -16.0)
    mx.bus("crickets", -12.0, send=0.2)
    mx.bus("trill", -24.0, send=0.3, process=lambda x: filt(x, [bq_lowpass(5000, 0.7)]))
    mx.bus("water", -10.0, send=0.15)
    mx.bus("far", -22.0, send=0.5, process=lambda x: filt(x, [bq_lowpass(1800, 0.7)]))
    mx.add("floor", stereo_noise(L, g, [bq_lowpass(260, 0.6), bq_highpass(45, 0.7)], 0.7), 0.0)
    # four crickets, each at its own pitch, chirp rate and pulse count; each rests now and then
    for c in range(4):
        carrier = float(g.uniform(4100, 5000))
        period = float(g.uniform(0.5, 0.85))
        pulses = int(g.integers(3, 5))
        rate = float(g.uniform(26, 34))
        pan = float(g.uniform(-0.9, 0.9))
        lvl = float(g.uniform(0.35, 1.0))
        rest_at = float(g.uniform(0, loop_s))
        rest_len = float(g.uniform(2.0, 5.0))
        for t in schedule(L, period, g, 0.06):
            if (t - rest_at) % loop_s < rest_len:
                continue
            mx.add("crickets", cricket_chirp(g, carrier, pulses, rate), t, pan=pan, gain=lvl)
    # a tree cricket's soft continuous trill, snapped to whole cycles per loop
    tt = np.arange(L) / SR
    car = snap(2900.0, L)
    pr = snap(46.0, L)
    trill = np.sin(2 * np.pi * car * tt) * np.sin(np.pi * pr * tt) ** 4 * (0.6 + 0.4 * plfo(L, 0.05, g))
    mx.add("trill", np.stack([0.8 * trill, 0.5 * trill], axis=1), 0.0)
    for t in schedule(L, 1.7, g, 0.35):
        mx.add("water", lap(g, float(g.uniform(0.7, 1.2))), t, pan=float(g.uniform(-0.4, 0.4)),
               gain=float(g.uniform(0.4, 1.0)))
    # the lamp-lit quiet: one far-off pair of voices, and a shutter set to
    for i, t in enumerate((12.0, 14.6, 16.9)):
        mx.add("far", murmur_phrase(g, i == 1), t, pan=-0.5 + 0.2 * i, gain=0.8)
    knock = modal([140, 310, 620], [0.06, 0.04, 0.02], [1.0, 0.5, 0.25], 0.3, g, click=0.3)
    mx.add("far", knock, 31.0, pan=0.6, gain=0.8)
    mx.add("far", 0.6 * knock, 31.18, pan=0.6)
    return mx, _outdoor(SEED % 9973 + 2)


def surf(g: np.random.Generator) -> tuple[LoopMixer, ModFDNReverb]:
    mx, L = _mixer("surf")
    loop_s = LOOPS["surf"]
    mx.bus("roar", -12.0)
    mx.bus("waves", 0.0, send=0.1)
    mx.add("roar", stereo_noise(L, g, [bq_lowpass(380, 0.6), bq_highpass(40, 0.7)], 0.5)
           * (0.85 + 0.15 * plfo(L, 0.05, g))[:, None], 0.0)
    low = stereo_noise(L, g, [bq_lowpass(600, 0.6), bq_highpass(60, 0.7)], 0.5)
    crash = stereo_noise(L, g, [bq_lowpass(4500, 0.6), bq_highpass(200, 0.7)], 0.35)
    foam = stereo_noise(L, g, [bq_bandpass(2600, 0.7), bq_highpass(900, 0.7)], 0.2)
    # fizz: the backwash's bubbles and sand as sparse crackle (thresholded high noise)
    fz = circ_noise(L, g, [bq_highpass(3000, 0.7)])
    fizz = np.where(np.abs(fz) > 2.6, fz, 0.0)
    fizz = filt(fizz, [bq_lowpass(9000, 0.7)])
    fizz = np.stack([np.roll(fizz, 300), fizz], axis=1)
    # six waves whose periods (6-8 s) add up to the loop exactly
    per = g.uniform(6.0, 8.0, 6)
    per *= loop_s / per.sum()
    starts = np.concatenate([[0.0], np.cumsum(per)[:-1]]) + 1.5
    tt = np.arange(L) / SR
    e_low, e_crash, e_foam, e_fizz = (np.zeros((L, 2)) for _ in range(4))
    for s, p in zip(starts, per):
        size = float(g.uniform(0.6, 1.0))
        pan = float(g.uniform(-0.5, 0.5))
        lr = np.array([np.cos((pan + 1) * np.pi / 4), np.sin((pan + 1) * np.pi / 4)]) * np.sqrt(2)
        d = (tt - s) % loop_s       # time since this wave's break, wrapped
        pre = (tt - s) % loop_s - loop_s  # negative: time before the break (the swell)
        swell = np.exp(-((pre + 0.0) / 1.4) ** 2) * (pre > -4.0)
        brk = np.where(d < p, np.clip(d / 0.12, 0, 1) * np.exp(-d / 0.9), 0.0)
        run = np.where(d < p, np.clip((d - 0.2) / 0.5, 0, 1) * np.exp(-np.maximum(d - 0.7, 0) / 1.6), 0.0)
        back = np.where(d < p, np.exp(-((d - 2.6) / 1.2) ** 2), 0.0)
        e_low += size * (0.5 * swell + 0.8 * brk + 0.3 * run)[:, None] * lr
        e_crash += size * brk[:, None] * lr
        e_foam += size * run[:, None] * lr
        e_fizz += size * back[:, None] * lr
    mx.add("waves", 0.9 * low * e_low + 0.7 * crash * e_crash + 0.45 * foam * e_foam + 0.8 * fizz * e_fizz, 0.0)
    return mx, _outdoor(SEED % 9973 + 3)


def dock(g: np.random.Generator) -> tuple[LoopMixer, ModFDNReverb]:
    mx, L = _mixer("dock")
    loop_s = LOOPS["dock"]
    mx.bus("water", -14.0)
    mx.bus("slaps", -2.0, send=0.15)
    mx.bus("wood", -14.0, send=0.25, process=lambda x: filt(x, [bq_peak(300, 3.0, 1.0), bq_lowpass(2400, 0.7)]))
    mx.bus("rope", -20.0, send=0.2)
    swell_hz = snap(0.2, L)  # an 8-swell cycle over the loop (5 s)
    tt = np.arange(L) / SR
    swell = 0.5 + 0.5 * np.sin(2 * np.pi * swell_hz * tt)
    mx.add("water", stereo_noise(L, g, [bq_lowpass(700, 0.6), bq_highpass(60, 0.7)], 0.5)
           * (0.5 + 0.5 * swell)[:, None], 0.0)
    for k in range(8):
        crest = (k + 0.25) / swell_hz
        for j in range(int(g.integers(2, 4))):
            mx.add("slaps", slap(g), crest + j * float(g.uniform(0.35, 0.8)) + float(g.uniform(-0.1, 0.1)),
                   pan=float(g.uniform(-0.7, 0.7)), gain=float(g.uniform(0.4, 1.0)))
    for t in (2.2, 13.0, 21.4, 33.0):
        c = stick_slip(g, float(g.uniform(0.7, 1.4)), 12, 55, [(180, 1.0), (360, 0.6), (560, 0.35)], q=5.0)
        mx.add("wood", c, t, pan=float(g.uniform(-0.6, 0.6)), gain=float(g.uniform(0.6, 1.0)))
    for t in (7.5, 26.0, 36.2):
        c = stick_slip(g, float(g.uniform(0.4, 0.9)), 70, 210, [(760, 1.0), (1350, 0.7), (2100, 0.35)], q=8.0)
        mx.add("rope", c, t, pan=float(g.uniform(0.2, 0.8)))
    for t in (10.4, 30.8):
        hull = modal([88, 162, 300], [0.18, 0.1, 0.05], [1.0, 0.6, 0.3], 0.8, g, click=0.15)
        mx.add("wood", 2.5 * hull, t % loop_s, pan=-0.3)
    return mx, _outdoor(SEED % 9973 + 4)


def shrine_interior(g: np.random.Generator) -> tuple[LoopMixer, ModFDNReverb]:
    mx, L = _mixer("shrine_interior")
    mx.bus("room", -6.0)
    mx.bus("drips", -8.0, send=0.7, process=lambda x: filt(x, [bq_highpass(300, 0.7)]))
    mx.bus("water", -16.0, send=0.4)
    tone = stereo_noise(L, g, [bq_lowpass(220, 0.6), bq_highpass(35, 0.7)], 0.8)
    hum = stereo_noise(L, g, [bq_bandpass(92, 6.0)], 0.9)  # the room's lowest mode, barely there
    mx.add("room", (tone + 0.4 * hum) * (0.9 + 0.1 * plfo(L, 0.04, g))[:, None], 0.0)
    for period, r, vel, pan in ((4.2, 2.4, 0.5, -0.5), (6.6, 1.7, 0.35, 0.45)):
        for t in schedule(L, period, g, 0.05):
            mx.add("drips", drip(vel, r, seed=int(g.integers(1 << 30))), t, pan=pan)
    for t in (9.3, 27.7):
        mx.add("drips", drip(0.25, float(g.uniform(1.4, 3.2)), seed=int(g.integers(1 << 30))), t,
               pan=float(g.uniform(-0.8, 0.8)))
    for t in (5.0, 21.0, 37.0):
        mx.add("water", 0.5 * lap(g, 0.6), t, pan=float(g.uniform(-0.3, 0.3)))
    hall = ModFDNReverb(rt60=3.4, rt60_high=1.4, predelay=0.04, size=1.3, mod_depth=8.0, mod_rate=0.35,
                        early_level=0.3, lowcut=120.0, seed=SEED % 9973 + 5)
    return mx, hall


def wind(g: np.random.Generator) -> tuple[LoopMixer, None]:
    mx, L = _mixer("wind")
    mx.bus("wind", 0.0)
    gust = 0.5 + 0.5 * plfo(L, 0.1, g)
    out = np.zeros((L, 2))
    for i, (f, q, w) in enumerate(((180, 0.9, 1.0), (320, 1.0, 0.8), (550, 1.1, 0.6), (900, 1.2, 0.42),
                                   (1500, 1.2, 0.26), (2500, 1.0, 0.14))):
        band = stereo_noise(L, g, [bq_bandpass(f, q)], 0.3)
        own = 0.5 + 0.5 * plfo(L, 0.18, g)
        bright = gust ** (1.0 + 0.5 * i)  # stronger gusts are brighter
        out += w * band * (0.35 + 0.45 * bright + 0.2 * own)[:, None]
    peak = np.clip((gust - 0.65) / 0.35, 0, 1) ** 2
    for f in (720.0, 1060.0):
        whistle = stereo_noise(L, g, [bq_bandpass(f, 28.0)], 0.8)
        out += 0.12 * whistle * peak[:, None]
    mx.add("wind", out, 0.0)
    return mx, None


BEDS = {"haluna_day": haluna_day, "haluna_night": haluna_night, "surf": surf, "dock": dock,
        "shrine_interior": shrine_interior, "wind": wind}


def render_bed(name: str, out_dir: str = OUT_DIR, verbose: bool = True) -> dict:
    g = rng(SEED + 101 * (list(BEDS).index(name) + 1))
    mx, verb = BEDS[name](g)
    _, loop = mx.render(reverb=verb, reverb_return_db=-4.0, hp_hz=30.0)
    rep: dict = {}
    _, loop = master_loop(np.zeros((0, 2)), loop, TARGET_LUFS, ceiling_db=CEILING_DB, report=rep)
    L = len(loop)
    path = os.path.join(out_dir, name + ".ogg")
    write_ogg(path, loop, quality=QUALITY, tags={"LOOPSTART": "0", "LOOPLENGTH": str(L)})
    write_loop_sidecar(os.path.join(out_dir, name + ".loop.json"), SR, 0, L, None, None)
    m = measure(loop)
    m["limiter"] = rep
    if verbose:
        print(f"{name}: {m['seconds']:.2f}s  {m['integrated_lufs']:.2f} LUFS  peak {m['sample_peak_dbfs']:.2f} dBFS  "
              f"limited {100 * rep.get('fraction_limited', 0):.2f} %")
    return m


def render(out_dir: str = OUT_DIR, verbose: bool = True) -> dict:
    return {name: render_bed(name, out_dir, verbose) for name in BEDS}


if __name__ == "__main__":
    only = sys.argv[1:]
    for bed in BEDS:
        if not only or bed in only:
            render_bed(bed)
