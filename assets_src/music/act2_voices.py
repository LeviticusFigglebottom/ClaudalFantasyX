"""Act II sketch kit (M3-AUD-804): the instrument voices and the loop plumbing shared by the six Act II sketches.

Not a cue: it renders nothing on its own. ossa_fen.py, reedhollow.py, sunken_vey.py, lowlight.py, keth_pass.py and
quellan.py load it (like haluna_village.py loads haluna_theme.py). Every voice here is synthesized from the
tools/audio/synth primitives; no samples, no sample packs, no generated audio.

Voices invented for Act II:
* `reed_pipe`: a double-reed pipe of the fen (nasal, buzzy, a little flat at the ends of notes), additive;
* `kirru_whistle`: the Kirru's whistled song, rendered a phrase at a time: a near-pure tone that glides between
  notes and scoops up into the "rising" ones, with a tongue-click at each phrase start (bible §8: whistle-clicks);
* `root_harp`: the Kirru root-harp, gut strings strung across a mangrove-root frame over water and plucked with long
  webbed fingers; the player presses the string after the pluck, so many notes bend *up* into pitch;
* `gourd`: a water-gourd drum (a gourd floated in a basin and struck: the pitch drops as the water inside moves);
* `tongue_click`: a short, pitched click;
* `glass`: a glass harmonica (the same recipe as sefir_theme.py's, copied so that cue stays frozen);
* `engine_thud`, `conduit_hum`: the Lamp Engine's dead pulse and its failing hum (Lowlight);
* `herd_bell`: a woolback's wooden-clappered bell (Quellan);
* `ten_string` / `strum`: a small, bright, paired-course highland lute and its strum (Quellan);
* textures (one loop long, seamless): `insects`, `wind`, `cord_song`, `periodic_drone`, `deep_cold`.
"""
from __future__ import annotations

import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools", "audio"))

import numpy as np  # noqa: E402

from synth.dsp import (SR, bq_bandpass, bq_highpass, bq_lowpass, fft_convolve, filt, midi_to_hz, rng,  # noqa: E402
                       smooth_noise)
from synth.electric import string_pluck  # noqa: E402
from synth.looping import LoopMixer, master_loop, write_loop_sidecar  # noqa: E402
from synth.mixer import measure, write_ogg  # noqa: E402
from synth.water import bubble  # noqa: E402

## breath_flute's tone starts after its breath (0.05-0.08 s): its notes are placed this much early
FLUTE_PRE = 0.065
## the glass swells in over ~0.45 s: placed this much early so the swell peaks near the beat
GLASS_PRE = 0.12


# --------------------------------------------------------------------------- #
# loop plumbing
# --------------------------------------------------------------------------- #
def snap(f: float, loop_s: float) -> float:
    """Nearest frequency with a whole number of cycles per loop (so a sustained tone wraps without a seam)."""
    return max(1.0, round(f * loop_s)) / loop_s


def fold(x: np.ndarray, N: int, k: int) -> np.ndarray:
    """A texture rendered N + k samples long folded to exactly N: its extra k samples are crossfaded into the
    start, so the sample after the last one continues it (the wrap is seamless)."""
    w = np.linspace(0, 1, k)
    if x.ndim == 2:
        w = w[:, None]
    out = x[:N].copy()
    out[:k] = x[:k] * w + x[N:N + k] * (1 - w)
    return out


def finish(mx: LoopMixer, name: str, out_path: str, bpm: float, bar_beats: int, bars: int, lead_in_s: float,
           target_lufs: float, reverb, return_db: float, verbose: bool, stats: dict | None,
           quality: float = 3.0, ceiling_db: float = -2.0) -> dict:
    """Render, start the file `lead_in_s` before bar 1's downbeat, master, write the .ogg and its sidecar."""
    _, loop = mx.render(reverb=reverb, reverb_return_db=return_db)
    lead_in = int(round(lead_in_s * SR))
    loop = np.roll(loop, lead_in, axis=0)
    rep: dict = {}
    _, loop = master_loop(np.zeros((0, 2)), loop, target_lufs, ceiling_db=ceiling_db, report=rep)
    L = len(loop)
    write_ogg(out_path, loop, quality=quality, tags={"LOOPSTART": "0", "LOOPLENGTH": str(L)})
    write_loop_sidecar(os.path.splitext(out_path)[0] + ".loop.json", SR, 0, L, bpm, bar_beats,
                       extra={"loop_bars": bars, "downbeat_offset_s": lead_in / SR})
    m = measure(loop)
    if stats is not None:
        stats["bus_lufs"] = dict(mx.bus_lufs)
        stats["limiter"] = rep
    if verbose:
        print(f"{name}: {m['seconds']:.2f}s  {m['integrated_lufs']:.2f} LUFS  TP {m['true_peak_dbtp']:.2f} dBTP"
              f"  limiter {rep}")
        print("  buses", {k: round(v, 1) for k, v in mx.bus_lufs.items()})
    return m


def body_ir(modes, seed: int, length: float = 0.2, scale: float = 0.08) -> np.ndarray:
    """A resonant body: an impulse plus decaying modes (f, q, amplitude)."""
    g = rng(seed)
    t = np.arange(int(length * SR)) / SR
    ir = np.zeros(len(t))
    ir[0] = 1.0
    for f, q, a in modes:
        d = q / (np.pi * f)
        ir += a * np.sin(2 * np.pi * f * t + g.uniform(0, 0.4)) * np.exp(-t / d) * scale
    return ir / np.abs(ir).max()


def bend(x: np.ndarray, cents0: float, tau: float) -> np.ndarray:
    """Read x at a varying rate so its pitch starts `cents0` off and settles exponentially (time constant tau)."""
    t = np.arange(len(x)) / SR
    rate = 2 ** (cents0 * np.exp(-t / tau) / 1200.0)
    pos = np.cumsum(rate) - rate[0]
    pos = pos[pos < len(x) - 1]
    return np.interp(pos, np.arange(len(x)), x)


# --------------------------------------------------------------------------- #
# melodic voices
# --------------------------------------------------------------------------- #
def reed_pipe(m: float, dur: float, vel: float, seed: int, attack: float = 0.06, release: float = 0.12,
              sag_cents: float = 18.0, nasal: float = 1.0) -> np.ndarray:
    """A fen pipe with a double reed: a full harmonic spectrum with a nasal formant (~1.1 and ~2.7 kHz), a reed
    buzz that grows with breath pressure, a small pitch sag at the end of each note (the lip relaxes) and a little
    air. Mono."""
    g = rng(seed)
    f0 = midi_to_hz(m)
    N = int((dur + 5 * release + 0.03) * SR)
    t = np.arange(N) / SR
    wob = 1.0 + 0.04 * smooth_noise(N, 2.5, g)
    P = np.clip(t / attack, 0, 1) ** 1.4 * np.where(t > dur, np.exp(-(t - dur) / release), 1.0) * wob * vel
    vib_on = np.clip((t - 0.4) / 0.5, 0, 1)
    cents = (-12.0 * np.exp(-t / 0.05) + 6.0 * vib_on * np.sin(2 * np.pi * 5.1 * t + g.uniform(0, 6))
             - sag_cents * np.clip((t - dur + 0.15) / 0.3, 0, 1) + 3.0 * smooth_noise(N, 0.8, g))
    ph = 2 * np.pi * np.cumsum(f0 * 2 ** (cents / 1200.0)) / SR
    K = int(max(1, min(36, 7000.0 / f0)))
    y = np.zeros(N)
    for k in range(1, K + 1):
        fk = k * f0
        a = k ** -0.9 * (1.0 + nasal * 2.2 * np.exp(-((fk - 1100.0) / 380.0) ** 2)
                         + nasal * 1.0 * np.exp(-((fk - 2700.0) / 700.0) ** 2)) / (1.0 + (fk / 4200.0) ** 4)
        y += a * P ** (1.0 + 0.14 * (k - 1)) * np.sin(k * ph + 0.2 * k)
    air = filt(g.standard_normal(N), [bq_bandpass(1800.0, 0.7)]) * P * 0.02
    out = y + air
    k2 = int(0.006 * SR)
    out[-k2:] *= np.linspace(1, 0, k2)
    return 0.16 * out


def tongue_click(g, vel: float, f: float = 2400.0) -> np.ndarray:
    """A Kirru tongue-click: a hard, very short pitched pop (two damped modes and a burst of noise). Mono."""
    N = int(0.06 * SR)
    t = np.arange(N) / SR
    b = float(g.uniform(0.94, 1.06))
    x = (np.sin(2 * np.pi * f * b * t) * np.exp(-t / 0.006) + 0.5 * np.sin(2 * np.pi * f * 1.62 * b * t)
         * np.exp(-t / 0.004))
    nn = int(0.003 * SR)
    x[:nn] += 0.6 * g.standard_normal(nn) * np.linspace(1, 0, nn)
    return 0.35 * vel * x


def kirru_whistle(notes: list[tuple[float, float, float, float, bool]], seed: int, glide: float = 0.05,
                  vib_cents: float = 20.0, breath: float = 0.04, click: bool = True) -> np.ndarray:
    """A whistled phrase. notes: [(start_s, dur_s, midi, vel, rise)], times relative to the phrase. Legato notes
    (gap < 40 ms) glide into each other; a `rise` note starts a whole tone below and slides up into its pitch (the
    Kirru song climbs). A near-pure tone (a faint 2nd and 3rd harmonic), slow wide vibrato on long notes, a thread
    of breath, and a tongue-click at the phrase start. Mono."""
    g = rng(seed)
    notes = sorted(notes)
    end = max(s + d for s, d, _, _, _ in notes)
    N = int((end + 0.6) * SR)
    t = np.arange(N) / SR
    target = np.full(N, notes[0][2])
    amp = np.zeros(N)
    prev_end = -1.0
    for s, d, m, v, rise in notes:
        a, e = int(s * SR), min(N, int((s + d + 0.5) * SR))
        target[a:] = m
        att = 0.012 if s - prev_end < 0.04 else 0.035
        seg = np.arange(e - a) / SR
        env = np.clip(seg / att, 0, 1) * np.where(seg > d, np.exp(-(seg - d) / 0.07), 1.0)
        amp[a:e] = np.maximum(amp[a:e], v * env)
        if rise:
            k = int(0.16 * SR)
            r = np.arange(min(k, N - a)) / SR
            target[a:a + len(r)] = m - 2.0 * np.exp(-r / 0.05)
        prev_end = s + d
    # portamento: smooth the step curve with a one-pole glide
    alpha = 1.0 - np.exp(-1.0 / (glide * SR))
    pitch = np.empty(N)
    acc = target[0]
    for i0 in range(0, N, 64):          # block-wise one-pole (the glide is far slower than 64 samples)
        acc = acc + (target[i0] - acc) * (1 - (1 - alpha) ** 64)
        pitch[i0:i0 + 64] = acc
    vib = vib_cents * np.clip(smooth_noise(N, 0.5, g) * 0.5 + 0.5, 0, 1) * np.sin(2 * np.pi * 5.6 * t)
    f = midi_to_hz(0) * 2 ** ((pitch * 100 + vib + 3 * smooth_noise(N, 1.2, g)) / 1200.0)
    ph = 2 * np.pi * np.cumsum(f) / SR
    amp = filt(amp, [bq_lowpass(60.0, 0.7)])
    tone = np.sin(ph) + 0.05 * np.sin(2 * ph + 0.4) + 0.015 * np.sin(3 * ph)
    air = filt(g.standard_normal(N), [bq_bandpass(3500.0, 0.6)]) * breath
    out = amp * (tone + air)
    if click:
        c = tongue_click(g, 0.7, 2200.0)
        s0 = max(0, int(notes[0][0] * SR) - int(0.03 * SR))
        out[s0:s0 + len(c)] += c[: N - s0]
    k2 = int(0.01 * SR)
    out[-k2:] *= np.linspace(1, 0, k2)
    return 0.22 * out


def root_harp(m: float, vel: float, seed: int, body: np.ndarray, rise_cents: float = 0.0, ring: float = 2.4,
              t60: float = 2.2) -> np.ndarray:
    """A root-harp string: a gut-like pluck (soft, mid pick position, quick top decay) through the frame and the
    water's hollow, optionally pressed up into pitch from `rise_cents` below after the pluck. Mono."""
    x = string_pluck(m, ring, vel, seed=seed, pick_pos=0.21, t60=t60, B=4e-5, max_f=5000.0, release=0.3)
    if rise_cents:
        x = bend(x, -rise_cents, 0.11)
    return fft_convolve(x, body)[: len(x) + 3000]


def root_harp_body(seed: int) -> np.ndarray:
    """The root-harp's frame over water: low, hollow and soft (no bright bridge ring)."""
    return body_ir(((120.0, 9, 0.8), (240.0, 11, 0.7), (410.0, 9, 0.5), (700.0, 7, 0.3), (1300.0, 5, 0.12)), seed)


def gourd(m: float, vel: float, seed: int) -> np.ndarray:
    """A floating water-gourd struck with the palm: a low thump whose pitch falls as the water inside swings,
    a soft slap, and a bubble or two after. Mono."""
    g = rng(seed)
    N = int(0.9 * SR)
    t = np.arange(N) / SR
    f0 = midi_to_hz(m)
    f = f0 * (1.0 + 0.35 * np.exp(-t / 0.04)) * (1.0 - 0.04 * np.sin(2 * np.pi * 3.0 * t) * np.exp(-t / 0.3))
    ph = 2 * np.pi * np.cumsum(f) / SR
    x = np.sin(ph) * np.exp(-t / 0.22) + 0.3 * np.sin(2.3 * ph + 0.5) * np.exp(-t / 0.06)
    nn = int(0.012 * SR)
    slap = filt(g.standard_normal(nn), [bq_lowpass(1800.0, 0.7)]) * np.linspace(1, 0, nn) ** 2
    x[:nn] += 0.5 * slap
    for _ in range(int(g.integers(1, 3))):
        b = bubble(float(g.uniform(2.5, 5.0)), 0.08, rise=float(g.uniform(0.05, 0.12)))
        s = int(g.uniform(0.08, 0.3) * SR)
        e = min(N, s + len(b))
        x[s:e] += b[: e - s]
    return 0.5 * vel * x


def glass(m: float, dur: float, vel: float, seed: int) -> np.ndarray:
    """A glass harmonica: a near-pure tone that swells in (no attack), a faint octave, a slow shimmer; mono
    (sefir_theme.py's recipe)."""
    g = rng(seed)
    f = midi_to_hz(m)
    N = int((dur + 2.5) * SR)
    t = np.arange(N) / SR
    env = np.clip(t / 0.45, 0, 1) ** 2 * np.where(t > dur, np.exp(-(t - dur) / 0.8), 1.0)
    vib = 1 + 0.0012 * np.sin(2 * np.pi * 4.2 * t + g.uniform(0, 6)) * np.clip(t / 1.5, 0, 1)
    wob = 1 + 0.06 * smooth_noise(N, 1.3, g)
    ph = 2 * np.pi * f * np.cumsum(vib) / SR
    x = np.sin(ph) + 0.18 * np.sin(2 * ph + 0.3) + 0.05 * np.sin(3 * ph + 1.1)
    k = int(0.05 * SR)
    out = vel * env * wob * x
    out[-k:] *= np.linspace(1, 0, k)
    return 0.3 * out


def ten_string_body(seed: int) -> np.ndarray:
    """A small, deep-backed highland lute: a bright, boxy top, higher modes than the coast's lutes."""
    return body_ir(((210.0, 10, 0.7), (420.0, 12, 0.6), (760.0, 9, 0.5), (1500.0, 7, 0.35), (3100.0, 5, 0.2)), seed,
                   length=0.16, scale=0.09)


def ten_string(m: float, dur: float, vel: float, seed: int, body: np.ndarray, mute: float = 0.0) -> np.ndarray:
    """One paired course (two strings a few cents apart) plucked near the bridge, through the body. Mono."""
    a = string_pluck(m, dur, vel, seed=seed, pick_pos=0.09, t60=1.2, mute=mute, B=1.4e-4, max_f=8000.0,
                     release=0.05)
    b = string_pluck(m + 0.05, dur, vel * 0.85, seed=seed + 1, pick_pos=0.1, t60=1.1, mute=mute, B=1.4e-4,
                     max_f=8000.0, release=0.05)
    k = int(0.002 * SR)
    x = np.zeros(len(a) + k)
    x[: len(a)] += a
    x[k: k + len(b)] += b
    return fft_convolve(x, body)[: len(x) + 2500]


def strum(notes: list[float], dur: float, vel: float, seed: int, body: np.ndarray, up: bool = False,
          mute: float = 0.0, spread: float = 0.011) -> np.ndarray:
    """A strum across the courses: low to high (down) or high to low and lighter (up), a few ms apart. Mono."""
    g = rng(seed)
    order = list(reversed(notes)) if up else list(notes)
    parts = []
    for i, m in enumerate(order):
        v = vel * (0.75 if up else 1.0) * (1.0 - 0.06 * i) * float(g.uniform(0.9, 1.05))
        parts.append((int((i * spread + float(g.uniform(0, 0.002))) * SR),
                      ten_string(m, dur, v, seed + 13 * i, body, mute)))
    N = max(s + len(x) for s, x in parts)
    out = np.zeros(N)
    for s, x in parts:
        out[s:s + len(x)] += x
    return out


# --------------------------------------------------------------------------- #
# percussion and machines
# --------------------------------------------------------------------------- #
def engine_thud(g, vel: float) -> np.ndarray:
    """The Lamp Engine's stroke, heard through water: a low, sagging thump (a piston in a flooded cylinder), a
    muffled valve clank a moment later, and a wet hiss. Mono."""
    N = int(1.2 * SR)
    t = np.arange(N) / SR
    f = 46.0 * (1.0 + 0.5 * np.exp(-t / 0.05)) * float(g.uniform(0.97, 1.02))
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.28) * np.minimum(1.0, t / 0.004)
    s = int(float(g.uniform(0.07, 0.1)) * SR)
    tc = np.arange(N - s) / SR
    b = float(g.uniform(0.95, 1.05))
    clank = sum(a * np.sin(2 * np.pi * fr * b * tc) * np.exp(-tc / d)
                for fr, a, d in ((310.0, 1.0, 0.09), (737.0, 0.6, 0.05), (1290.0, 0.3, 0.03)))
    x[s:] += 0.16 * clank
    hiss = filt(g.standard_normal(N), [bq_bandpass(900.0, 0.8)]) * np.exp(-t / 0.15) * 0.05
    return vel * (x + hiss)


def conduit_hum(loop_s: float, root: float, g, flicker_hz: tuple = (0.37, 0.91, 2.3)) -> np.ndarray:
    """A dead machine's hum: a buzzing harmonic series on `root` (odd harmonics strong, as in a choked coil),
    darkened, with a flicker made of a few slow whole-cycle modulations that sometimes dip almost to nothing.
    Exactly one loop long, stereo."""
    N = int(round(loop_s * SR))
    t = np.arange(N) / SR
    f0 = midi_to_hz(root)
    flick = np.ones(N)
    for k, fh in enumerate(flicker_hz):
        flick *= 0.78 + 0.22 * np.sin(2 * np.pi * snap(fh, loop_s) * t + g.uniform(0, 6.28))
    flick = np.clip((flick - 0.45) / 0.55, 0, 1) ** 1.5
    out = np.zeros((N, 2))
    for k in range(1, 15):
        a = (1.0 if k % 2 else 0.45) / k ** 0.9 / (1 + (k * f0 / 900.0) ** 2)
        for side, det in ((0, 0.0), (1, 0.13 * k)):
            fk = snap(k * f0 + det, loop_s)
            s = a * np.sin(2 * np.pi * fk * t + g.uniform(0, 6.28))
            out[:, side] += s
            out[:, 1 - side] += 0.55 * s
    return 0.05 * out * flick[:, None]


def herd_bell(g, vel: float, f: float) -> np.ndarray:
    """A woolback's bell: a hollow wooden-clappered clonk (inharmonic modes, short), mono."""
    N = int(0.9 * SR)
    t = np.arange(N) / SR
    b = float(g.uniform(0.97, 1.03))
    x = sum(a * np.sin(2 * np.pi * f * r * b * t + g.uniform(0, 6)) * np.exp(-t / d)
            for r, a, d in ((1.0, 1.0, 0.32), (1.52, 0.55, 0.2), (2.17, 0.4, 0.12), (2.93, 0.25, 0.08),
                            (4.1, 0.12, 0.05)))
    nn = int(0.004 * SR)
    x[:nn] += 0.4 * g.standard_normal(nn) * np.linspace(1, 0, nn)
    return 0.3 * vel * x


# --------------------------------------------------------------------------- #
# textures, each exactly one loop long and seamless
# --------------------------------------------------------------------------- #
def periodic_drone(loop_s: float, pitches: list[tuple[float, float]], seed: int, partials: int = 6,
                   breath_s: float = 16.0, tilt: float = 0.55) -> np.ndarray:
    """A held, breathing drone on [(midi, level)]: additive partials snapped to whole cycles per loop, a detuned
    twin per partial across the stereo field, upper partials swelling with a slow breath. Stereo."""
    g = rng(seed)
    N = int(round(loop_s * SR))
    t = np.arange(N) / SR
    out = np.zeros((N, 2))
    breath = 0.5 - 0.5 * np.cos(2 * np.pi * snap(1.0 / breath_s, loop_s) * t + g.uniform(0, 6.28))
    for root, lvl in pitches:
        f0 = midi_to_hz(root)
        for k in range(1, partials + 1):
            a = tilt ** (k - 1)
            for side, det in ((0, 0.0), (1, 0.08 + 0.03 * k)):
                f = snap(f0 * k + det, loop_s)
                swell = 1.0 + (0.5 * (k - 1) / max(1, partials - 1)) * (breath - 0.5) * 2
                s = lvl * a * swell * np.sin(2 * np.pi * f * t + g.uniform(0, 2 * np.pi))
                out[:, side] += s
                out[:, 1 - side] += 0.6 * s
    return out * 0.05


def insects(loop_s: float, seed: int) -> np.ndarray:
    """Insects implied, not sampled: two high stridulation bands (narrow noise gated by fast pulse trains), one in
    irregular clusters, one a faint, breathing bed, plus a lower, slower 'frog' purr. Stereo, one loop long."""
    g = rng(seed)
    N = int(round(loop_s * SR))
    k = int(0.5 * SR)
    M = N + k
    t = np.arange(M) / SR
    out = np.zeros((M, 2))
    # (1) clustered chirps, 5.2 kHz, 34 pulses/s, bursts of 0.3-1.1 s every 1.5-4 s, wandering in the field
    gate = np.zeros(M)
    pans = np.zeros(M)
    pos = float(g.uniform(0, 1.0))
    while pos < M / SR:
        ln = float(g.uniform(0.3, 1.1))
        a, b = int(pos * SR), min(M, int((pos + ln) * SR))
        seg = np.arange(b - a) / SR
        gate[a:b] = np.sin(np.pi * seg / ln) ** 0.6 * float(g.uniform(0.5, 1.0))
        pans[a:b] = float(g.uniform(-0.8, 0.8))
        pos += ln + float(g.uniform(1.5, 4.0))
    pulse = np.abs(np.sin(np.pi * 34.0 * t)) ** 10
    band = filt(g.standard_normal(M), [bq_bandpass(5200.0, 4.0), bq_bandpass(5200.0, 4.0)])
    x = band * pulse * gate
    out[:, 0] += x * (1 - pans) / 2
    out[:, 1] += x * (1 + pans) / 2
    # (2) a faint bed: 7.4 kHz, 21 pulses/s, breathing slowly
    for ch in range(2):
        bed = filt(g.standard_normal(M), [bq_bandpass(7400.0 * (1 + 0.03 * ch), 5.0)])
        pul = np.abs(np.sin(np.pi * (21.0 + 1.3 * ch) * t)) ** 6
        br = 0.5 + 0.5 * np.sin(2 * np.pi * t / 9.0 + ch * 2.1)
        out[:, ch] += 0.35 * bed * pul * br
    # (3) a low purr (a frog's slow trill), now and then, far off
    gate = np.zeros(M)
    pos = float(g.uniform(2.0, 5.0))
    while pos < M / SR:
        ln = float(g.uniform(0.8, 1.8))
        a, b = int(pos * SR), min(M, int((pos + ln) * SR))
        seg = np.arange(b - a) / SR
        gate[a:b] = np.sin(np.pi * seg / ln) ** 2
        pos += ln + float(g.uniform(4.0, 9.0))
    purr = filt(g.standard_normal(M), [bq_bandpass(620.0, 3.0)]) * np.abs(np.sin(np.pi * 13.0 * t)) ** 4 * gate
    out[:, 0] += 1.6 * purr * 0.7
    out[:, 1] += 1.6 * purr * 0.4
    return fold(out, N, k) * 0.06


def wind(loop_s: float, seed: int, lo_hz: float = 380.0, hi_hz: float = 1900.0, gusts: tuple = (4, 11, 3),
         hi_level: float = 0.25) -> np.ndarray:
    """Wind: noise through a low band and a thin high band, breathing and gusting on whole cycles per loop.
    Stereo, one loop long (the saltgrass recipe, with its rates as parameters)."""
    g = rng(seed)
    N = int(round(loop_s * SR))
    k = int(0.5 * SR)
    t = np.arange(N + k) / SR
    out = np.zeros((N + k, 2))
    a, b, c = gusts
    for ch in range(2):
        lo = filt(g.standard_normal(N + k), [bq_bandpass(lo_hz, 0.5), bq_lowpass(1500, 0.6)])
        hi = filt(g.standard_normal(N + k), [bq_bandpass(hi_hz, 1.2)])
        breath = 0.55 + 0.45 * np.sin(2 * np.pi * a * t / loop_s + ch * 0.9) ** 2
        gust = 0.7 + 0.3 * np.sin(2 * np.pi * b * t / loop_s + 1.3 + ch) * np.sin(2 * np.pi * c * t / loop_s)
        out[:, ch] = (lo + hi_level * hi * breath) * breath * gust
    return fold(out, N, k) * 0.05


def cord_song(loop_s: float, pitches: list[float], seed: int, q: float = 40.0) -> np.ndarray:
    """Wind in the pass-cords: very narrow bands of noise at the given pitches (whistling, never quite a note),
    each swelling and fading on its own slow whole-cycle gust. Stereo, one loop long."""
    g = rng(seed)
    N = int(round(loop_s * SR))
    k = int(0.5 * SR)
    t = np.arange(N + k) / SR
    out = np.zeros((N + k, 2))
    for i, m in enumerate(pitches):
        f = midi_to_hz(m)
        x = filt(g.standard_normal(N + k), [bq_bandpass(f, q), bq_bandpass(f, q)])
        x /= np.abs(x).max() + 1e-9
        cyc = int(g.integers(2, 6))
        env = np.clip(np.sin(2 * np.pi * cyc * t / loop_s + g.uniform(0, 6.28)), 0, 1) ** 2
        p = float(g.uniform(-0.7, 0.7))
        out[:, 0] += x * env * (1 - p) / 2
        out[:, 1] += x * env * (1 + p) / 2
    return fold(out, N, k) * 0.12


def deep_cold(loop_s: float, seed: int) -> np.ndarray:
    """The deep's cold welling up: a very low, slowly heaving band of noise (felt more than heard). Stereo."""
    g = rng(seed)
    N = int(round(loop_s * SR))
    k = int(0.5 * SR)
    t = np.arange(N + k) / SR
    out = np.zeros((N + k, 2))
    for ch in range(2):
        x = filt(g.standard_normal(N + k), [bq_lowpass(160.0, 0.7), bq_lowpass(160.0, 0.7), bq_highpass(30.0, 0.7)])
        x /= np.abs(x).max() + 1e-9
        heave = 0.5 + 0.5 * np.sin(2 * np.pi * 3 * t / loop_s + ch * 1.4) ** 2
        out[:, ch] = x * heave
    return fold(out, N, k) * 0.3
