"""'Grand' piano: a modal string model driven by a nonlinear hammer, plus a
synthesized soundboard, sympathetic resonance, dampers and pedal noise.

This replaces the additive `piano.py` (kept frozen so the M1 sketch still
renders byte-identically for A/B listening). Per note:

1. **Hammer.** A lumped felt hammer (mass M, force F = K x^p) hits the
   string group, which loads it as an impedance n*Z with the inverted
   reflection from the near (agraffe) end arriving after p_s/f0 seconds.
   The ODE is integrated at 4x the sample rate for the 0.5-6 ms of contact.
   Harder blows compress the felt further into its stiff, nonlinear region,
   so the force pulse gets shorter and the spectrum brighter: velocity-
   dependent timbre comes from physics, not from a tone control.
2. **Strings.** 1, 2 or 3 unison strings by register, each detuned by a
   fraction of a cent, all struck in phase (so the "prompt" sound starts
   coherent and the strings drift apart: Weinreich's two-stage decay).
   Partials follow the stiff-string law f_n = n f0 sqrt(1 + B n^2) with B
   from a register table. Decay per partial is sigma = sigma_1 + b3 (w^2 -
   w_1^2) (the Chaigne-Askenfelt loss form) for the slow "aftersound"
   component, `prompt` times faster for the coherent component. A small
   amplitude-dependent pitch glide (tension modulation) is added.
3. **Commuted excitation.** The note is the string modal impulse response
   (weighted by the strike-position comb sin(n pi p_s)) convolved with the
   hammer force pulse, so attack phase and spectrum are consistent.
4. **Dampers.** A continuous damper engagement d(t) from key-up and the
   (possibly half-) pedal depth scales a frequency-dependent damping rate.
   Notes above E6 have no dampers, as on a real grand. A damper-felt noise
   is added when the damper lands.

Per bus (`PianoBody`): a stereo modal soundboard IR (Poisson-spaced modes,
Q falling with frequency, radiation tilt), a sympathetic-resonance IR (every
string's low partials ringing when the pedal is down; the undamped top
strings always), and pedal mechanism noise.

The slow parts of each partial (decays, beating, damping, glide) are built
on a 32x decimated grid and interpolated, which keeps a note to a few tens
of milliseconds of numpy work.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from functools import lru_cache

import numpy as np

from .dsp import SR, bq_bandpass, bq_highpass, bq_highshelf, bq_lowpass, bq_peak, fft_convolve, filt, midi_to_hz, rng

DEC = 32                 # decimation of the slow-envelope grid
DAMPER_TOP = 88          # E6: keys above this have no dampers
MAX_LEN = 26.0           # seconds; nothing rings longer than this


def _lin(m: float, table) -> float:
    return float(np.interp(m, [a for a, _ in table], [b for _, b in table]))


def _log(m: float, table) -> float:
    return float(np.exp(np.interp(m, [a for a, _ in table], [math.log(b) for _, b in table])))


# Register tables (MIDI note, value). Physical reference values, approximate
# (concert-grand measurements in the literature scatter by about 2x).
B_TABLE = [(21, 3.0e-4), (33, 1.5e-4), (40, 1.1e-4), (48, 1.6e-4), (60, 3.8e-4), (72, 8.5e-4),
           (84, 2.4e-3), (96, 7.0e-3), (108, 2.0e-2)]
T60_AFTER = [(21, 30.0), (33, 24.0), (48, 18.0), (60, 14.0), (72, 9.0), (84, 5.0), (96, 2.6), (108, 1.0)]
PROMPT = [(21, 2.5), (60, 3.5), (84, 3.0), (96, 2.0), (108, 1.3)]       # fast/slow decay ratio
AFTER_SHARE = [(21, 0.20), (60, 0.20), (84, 0.25), (108, 0.40)]          # aftersound amplitude share
HAMMER_M = [(21, 11e-3), (60, 8.7e-3), (108, 5.5e-3)]                    # kg
HAMMER_P = [(21, 2.2), (60, 2.5), (108, 3.0)]                            # felt exponent
HAMMER_K = [(21, 4e8), (36, 1e9), (60, 4e9), (84, 3e10), (108, 1e12)]    # N / m^p
STRING_Z = [(21, 9.0), (45, 4.0), (60, 2.1), (84, 1.6), (108, 1.2)]      # kg/s per string
STRIKE_POS = [(21, 0.125), (60, 0.118), (84, 0.10), (108, 0.065)]        # fraction of length
B3 = 1.0e-8               # s, frequency-squared loss term
# Loudness trim by register so equal velocities give roughly equal K-weighted
# loudness (calibrated with tools/audio/measure_quality.py --calibrate).
LEVEL_TRIM_DB = [(21, 8.7), (33, 4.1), (45, 1.3), (57, 0.3), (69, 1.2), (81, 3.9), (93, 8.5), (108, 17.0)]


def inharmonicity(m: float) -> float:
    return _log(m, B_TABLE)


def strings_for(m: float) -> int:
    return 1 if m < 32 else 2 if m < 45 else 3


def hammer_velocity(vel: float) -> float:
    """Key velocity 0..1 to hammer speed (m/s): about 0.25 m/s (ppp) to 6 m/s (fff)."""
    return 0.25 * 24.0 ** float(np.clip(vel, 0.0, 1.0))


def hammer_force(m: float, vel: float, sr: int = SR, over: int = 4) -> np.ndarray:
    """Force pulse (N) at sample rate `sr`, from a 4x-oversampled contact simulation."""
    f0 = midi_to_hz(m)
    M, p, K = _log(m, HAMMER_M), _lin(m, HAMMER_P), _log(m, HAMMER_K)
    Z = _log(m, STRING_Z) * strings_for(m)
    fs = sr * over
    dt = 1.0 / fs
    d = int(round(_lin(m, STRIKE_POS) / f0 * fs))     # near-end round trip
    nmax = int(0.012 * fs)
    F = np.zeros(nmax)
    xi, vh, y = 0.0, hammer_velocity(vel), 0.0
    end = nmax
    started = False
    for i in range(nmax):
        c = xi - y
        f = K * c ** p if c > 0 else 0.0
        F[i] = f
        if f > 0:
            started = True
        elif started and i > 8 and vh < 0:
            end = i
            break
        vh -= f / M * dt
        xi += vh * dt
        y += (f - (F[i - d] if i >= d else 0.0)) / (2 * Z) * dt
    F = F[: end + (-end) % over]
    return F.reshape(-1, over).sum(axis=1) * dt        # impulse per output sample (N s)


@dataclass
class PedalCurve:
    """Sustain-pedal depth over absolute time: 0 = up (dampers on), 1 = fully down."""
    times: np.ndarray
    depth: np.ndarray

    def at(self, t: np.ndarray) -> np.ndarray:
        return np.interp(t, self.times, self.depth, left=self.depth[0], right=self.depth[-1])

    @staticmethod
    def up() -> "PedalCurve":
        return PedalCurve(np.array([0.0, 1.0]), np.array([0.0, 0.0]))


def damper_engagement(pedal_depth: np.ndarray) -> np.ndarray:
    """How hard the damper presses for a released key, given pedal depth (half-pedal aware)."""
    return np.clip((0.62 - pedal_depth) / 0.42, 0.0, 1.0) ** 1.5


def grand_note(m: float, vel: float, key_up: float, seed: int = 0, t_abs: float = 0.0,
               pedal: PedalCurve | None = None, sr: int = SR, brightness: float = 1.0,
               max_partials: int = 64) -> np.ndarray:
    """One note's bridge signal (mono, attack near index 0; the soundboard is per bus).

    m       MIDI pitch (fractional allowed)
    vel     key velocity 0..1 (mapped to hammer speed)
    key_up  seconds after onset when the key is released
    t_abs   onset in absolute seconds (to read `pedal`)
    """
    g = rng(seed)
    pedal = pedal or PedalCurve.up()
    f0 = midi_to_hz(m)
    B = inharmonicity(m) * (1 + g.uniform(-0.03, 0.03))
    ns = strings_for(m)
    ps = _lin(m, STRIKE_POS) * (1 + g.uniform(-0.03, 0.03))
    n = np.arange(1, max_partials + 1, dtype=np.float64)
    fn = n * f0 * np.sqrt(1 + B * n * n)
    keep = fn < min(0.45 * sr, 16000.0)
    n, fn = n[keep], fn[keep]
    w = 2 * np.pi * fn

    sig1 = 6.91 / _log(m, T60_AFTER)
    s_slow = sig1 + B3 * (w ** 2 - w[0] ** 2)
    s_fast = s_slow * _lin(m, PROMPT)
    h = _lin(m, AFTER_SHARE)
    reg = float(np.clip((m - 21) / 87.0, 0, 1))
    s_damp = (1 + fn / 3000.0) / (0.035 + 0.22 * (1 - reg) ** 2)
    if m > DAMPER_TOP:
        s_damp[:] = 0.0

    # damper engagement on the slow grid, integrated (exp(-s_damp * integral) is the damping gain)
    key_up = max(key_up, 0.02)
    nat = float(7.5 / s_slow[0]) + 0.1
    total = min(MAX_LEN, nat)
    nd = int(total * sr / DEC) + 2
    td = np.arange(nd) * DEC / sr
    key = np.clip((td - key_up) / 0.012, 0.0, 1.0)            # damper lands over ~12 ms
    d = key * damper_engagement(pedal.at(t_abs + td))
    dint = np.concatenate([[0.0], np.cumsum(0.5 * (d[1:] + d[:-1]) * DEC / sr)])

    # string detunings (cents), aftersound mode offset, tension glide
    det = g.normal(0.0, 0.55, ns)
    det -= det.mean()
    det_after = g.normal(0.0, 0.25)
    glide_c = (3.0 - 2.0 * reg) * float(np.clip(vel, 0, 1)) ** 2

    amp_comb = np.abs(np.sin(np.pi * n * ps)) + 0.015
    amp_comb *= 1.0 / (1.0 + (fn / (9000.0 * brightness)) ** 4)   # string termination losses at the top

    # how long until every partial is ~80 dB down (decides the buffer length)
    env_bound = np.zeros(nd)
    for k in range(len(n)):
        env_bound += amp_comb[k] * np.exp(-s_slow[k] * td - s_damp[k] * dint)
    below = np.nonzero(env_bound < env_bound[0] * 1e-4)[0]
    N = min(int(total * sr), int((below[0] if len(below) else nd - 1) * DEC) + DEC)
    N = max(N, int(0.05 * sr))
    t = np.arange(N) / sr
    tdN = td[: N // DEC + 2]
    ir = np.zeros(N)

    glide = glide_c * np.exp(-2.0 * s_fast[0] * tdN)
    glide_phase = np.cumsum(glide) * DEC / sr                     # cents * s
    for k in range(len(n)):
        a = amp_comb[k]
        # where this partial drops below -90 dB re its start
        lk = np.exp(-s_slow[k] * tdN - s_damp[k] * dint[: len(tdN)])
        alive = np.nonzero(lk > 3e-5)[0]
        if len(alive) == 0:
            continue
        nk = min(N, int((alive[-1] + 1) * DEC))
        if nk < 64:
            continue
        j = int(math.ceil(nk / DEC)) + 1
        tt = tdN[:j]
        cents_to_rad = w[k] * math.log(2) / 1200.0
        # coherent "prompt" part: strings start in phase and drift apart
        z = np.zeros(j, dtype=np.complex128)
        for s in range(ns):
            z += np.exp(1j * det[s] * cents_to_rad * tt)
        z *= (1 - h) * np.exp(-s_fast[k] * tt) / ns
        z += h * np.exp(-s_slow[k] * tt) * np.exp(1j * det_after * cents_to_rad * tt)
        z *= np.exp(-s_damp[k] * dint[:j]) * np.exp(1j * cents_to_rad * glide_phase[:j])
        re = np.interp(t[:nk], tt, z.real)
        im = np.interp(t[:nk], tt, z.imag)
        ph = w[k] * t[:nk]
        ir[:nk] += a * (re * np.sin(ph) + im * np.cos(ph))

    F = hammer_force(m, vel, sr)
    out = fft_convolve(ir, F)[:N]
    # felt/key knock: the force pulse itself reaches the board, about 26 dB under
    # the string onset in the middle, relatively stronger in the treble
    knock_db = _lin(m, [(21, -30.0), (60, -26.0), (108, -22.0)])
    onset = float(np.abs(out[: int(0.01 * sr)]).max())
    out[: len(F)] += F / max(F.max(), 1e-12) * onset * 10 ** (knock_db / 20)
    # damper-felt noise where the damper lands (scaled by what is still ringing)
    landed = np.nonzero(d > 0.5)[0]
    if len(landed) and m <= DAMPER_TOP:
        tl = float(td[landed[0]])
        s0 = int(tl * sr)
        if s0 < N - 64:
            ring = float(np.interp(tl, td, env_bound) / env_bound[0])
            nn = min(int(0.06 * sr), N - s0)
            tn = np.arange(nn) / sr
            nz = filt(g.standard_normal(nn), [bq_bandpass(260 + 3 * f0 if f0 < 300 else 1150, 0.9, sr)], sr=sr)
            amp = 0.012 * F.sum() * (0.25 + 0.75 * math.sqrt(ring))
            out[s0: s0 + nn] += amp * nz * np.exp(-tn / 0.018) * (1 - np.exp(-tn / 0.002))
    k = min(int(0.02 * sr), N // 4)
    out[-k:] *= np.linspace(1, 0, k) ** 2
    # bridge force per unit hammer impulse scales with f0 (2 f0 F for an ideal string)
    return out * (f0 / 261.63) * 10 ** (_lin(m, LEVEL_TRIM_DB) / 20) * 2.0


# --------------------------------------------------------------------------- #
# Body: soundboard, sympathetic strings, pedal noise
# --------------------------------------------------------------------------- #
def soundboard_ir_modal(seed: int = 4242, length: float = 0.45, sr: int = SR) -> np.ndarray:
    """Stereo modal soundboard response (N, 2).

    Modes start at ~48 Hz with Poisson spacing (mean 38 Hz, a little denser
    higher up), loss factor rising with frequency (Q ~ 45 at 100 Hz falling
    to ~ 10 at 5 kHz), and a radiation tilt (+6 dB/oct up to ~900 Hz, then
    gently falling). The two channels are two "microphone" positions: same
    mode frequencies, independent random mode shapes, which decorrelates them
    the way a real board does. A direct path keeps the board from
    over-colouring.
    """
    g = rng(seed)
    n = int(length * sr)
    t = np.arange(n) / sr
    f = 48.0
    out = np.zeros((n, 2))
    while f < 9000:
        q = 45.0 / (1 + (f / 900.0) ** 0.6)
        sig = math.pi * f / q
        spacing = 38.0 / (1 + f / 4000.0) + 4.0
        # target smooth power response: radiation rises ~6 dB/oct to ~1.4 kHz, then falls gently
        rad = (f / 1400.0) / (1 + (f / 1400.0) ** 1.5)
        amp = rad * math.sqrt(2 * sig * spacing)   # equal-energy modes -> smooth response = rad
        m = int(min(n, 9.0 / sig * sr))
        env = np.exp(-sig * t[:m])
        ph = g.uniform(0, 2 * np.pi)
        s = np.sin(2 * np.pi * f * t[:m] + ph) * env
        a_l = g.normal()
        out[:m, 0] += amp * a_l * s
        out[:m, 1] += amp * (0.6 * a_l + 0.8 * g.normal()) * s   # mic correlation ~0.6
        f += g.exponential(spacing - 4.0) + 4.0
    out = filt(out, [bq_lowpass(7000, 0.7, sr), bq_highpass(40, 0.7, sr)], sr=sr)
    out /= np.sqrt((out ** 2).sum(axis=0, keepdims=True))
    direct = 0.70
    out *= math.sqrt(1 - direct ** 2)
    out[0] += direct
    # radiation efficiency rises with frequency over the whole board, not only in the modal part
    out = filt(out, [bq_highshelf(1100, 7.0, 0.7, sr), bq_lowpass(9000, 0.7, sr)], tail=0.05, sr=sr)
    return out


def sympathetic_ir(pedal_down: bool, seed: int = 777, length: float = 6.0, sr: int = SR) -> np.ndarray:
    """Stereo IR of the free strings' low partials, driven from the bridge.

    pedal_down=True: all 88 strings are free. False: only the undamped top
    strings (above E6). Each string's partials 1..8 (below 5 kHz) ring with
    the string's own aftersound decay; coupling falls as 1/k.
    """
    g = rng(seed + (1 if pedal_down else 0))
    n = int(length * sr)
    td = np.arange(n // DEC + 2) * DEC / sr
    t = np.arange(n) / sr
    out = np.zeros((n, 2))
    lo = 21 if pedal_down else DAMPER_TOP + 1
    for m in range(lo, 109):
        f0 = midi_to_hz(m)
        B = inharmonicity(m)
        sig1 = 6.91 / _log(m, T60_AFTER)
        pan = (m - 64) / 60.0
        for k in range(1, 9):
            f = k * f0 * math.sqrt(1 + B * k * k)
            if f > 5000:
                break
            w = 2 * np.pi * f
            sig = sig1 + B3 * (w ** 2 - (2 * np.pi * f0) ** 2)
            nk = int(min(n, 7.0 / sig * sr))
            env = np.interp(t[:nk], td, np.exp(-sig * td))
            s = np.sin(w * t[:nk] + g.uniform(0, 2 * np.pi)) * env / k
            out[:nk, 0] += (0.5 - 0.4 * pan) * s
            out[:nk, 1] += (0.5 + 0.4 * pan) * s
    return out / max(np.abs(out).max(), 1e-9) * 0.05


@lru_cache(maxsize=4)
def _body_irs(seed: int, sr: int) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    return soundboard_ir_modal(seed, sr=sr), sympathetic_ir(True, seed, sr=sr), sympathetic_ir(False, seed, sr=sr)


class PianoBody:
    """Bus processor: soundboard convolution, sympathetic halo, pedal noise.

    Linear in its input (fixed gains), so a piano split across several buses
    (for example melody and accompaniment, to measure voicing) sums to the
    same result as one bus. `sym_db` is the sympathetic IR gain; at the
    default it sits about 20-26 dB under the board output in pedalled
    passages (measured by tools/audio/measure_quality.py).
    """

    def __init__(self, pedal: PedalCurve, seed: int = 4242, sym_db: float = -56.0, sr: int = SR,
                 pedal_noise_db: float = -66.0):
        self.pedal = pedal
        self.sr = sr
        self.seed = seed
        self.board, self.sym_down, self.sym_up = _body_irs(seed, sr)
        self.sym_gain = 10 ** (sym_db / 20)
        self.pedal_noise_gain = 10 ** (pedal_noise_db / 20)
        self.last_sym_ratio_db = float("nan")

    def __call__(self, x: np.ndarray) -> np.ndarray:
        sr = self.sr
        mono_in = x.mean(axis=1)
        y = np.zeros_like(x)
        for c in range(2):
            y[:, c] = fft_convolve(x[:, c], self.board[:, c])[: len(x)]
        p = self.pedal.at(np.arange(len(x)) / sr)
        free = 1.0 - damper_engagement(p)
        drive = mono_in * free
        sym = np.zeros_like(x)
        for c in range(2):
            sym[:, c] = (fft_convolve(drive, self.sym_down[:, c])[: len(x)] * free
                         + fft_convolve(mono_in, self.sym_up[:, c])[: len(x)])
        sym *= self.sym_gain
        ey, es = float((y ** 2).sum()), float((sym ** 2).sum())
        if ey > 0 and es > 0:
            self.last_sym_ratio_db = 10 * math.log10(es / ey)
        return y + sym + self.pedal_noise(len(x))

    def pedal_noise(self, n: int) -> np.ndarray:
        """Dampers lifting (a soft felt 'whoosh') and landing (a low thud) at each pedal move."""
        sr = self.sr
        g = rng(self.seed + 99)
        out = np.zeros((n, 2))
        tg = self.pedal.times
        dp = np.diff(self.pedal.depth)
        # find the starts of large moves on the pedal curve
        moves = []
        last = -1.0
        for i in range(len(dp)):
            if abs(dp[i]) > 0 and tg[i] - last > 0.08:
                seg = self.pedal.depth[i: i + 40]
                change = float(seg[-1] - seg[0]) if len(seg) > 1 else 0.0
                if abs(change) > 0.3:
                    moves.append((float(tg[i]), change))
                    last = float(tg[i])
        for t0, change in moves:
            s = int(t0 * sr)
            m = min(int(0.25 * sr), n - s)
            if m <= 0:
                continue
            tt = np.arange(m) / sr
            nz = g.standard_normal(m)
            if change > 0:   # lift: breathy felt release + faint mechanism click
                sig = filt(nz, [bq_bandpass(700, 0.7, sr), bq_lowpass(2500, 0.7, sr)], sr=sr)
                env = (1 - np.exp(-tt / 0.02)) * np.exp(-tt / 0.07)
            else:            # land: low thud
                sig = filt(nz, [bq_peak(110, 9, 1.5, sr), bq_lowpass(400, 0.7, sr)], sr=sr)
                env = (1 - np.exp(-tt / 0.004)) * np.exp(-tt / 0.045)
            sig = sig / (np.std(sig) + 1e-12) * env * self.pedal_noise_gain * abs(change)
            out[s: s + m, 0] += sig
            out[s: s + m, 1] += 0.85 * sig
        return out
