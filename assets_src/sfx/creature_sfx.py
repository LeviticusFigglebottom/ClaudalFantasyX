"""Creature voices and movement (M3-AUD-14): the slice's foes and the Act I bestiary (docs/kb/art/creatures/, the
creatures track's sheets; game/data/battle/enemies.json; strings.csv LORE_*).

All synthesized here and in tools/audio/synth/ (SPEC §2, §9): no samples, no recordings, no generated audio, and no
real animal's call copied. Each creature is a physical or source-filter model with its own numbers (CREATURES):
- carapace: modal clicks through shell resonances (taps, claw snaps, mandible chatter), stick-slip scrapes, froth of
  Minnaert bubbles (synth/water.py);
- wet bodies: sticky low-passed noise, suction pops (a sine whose pitch rises as the seal breaks), gurgles of large
  bubbles, sinking bubble trains;
- throats: an additive glottal source shaped by formant resonances, with jitter, roughness and period doubling (the
  eel's purr, the harrier's rasping call, the hound's growl and bark, the wraith's moan through the shrouds);
- wings: filtered noise bursts, a strong downstroke and a weak upstroke, with a feather or paper rustle on top;
- bronze: the Drownbell's hood is synth/bells.py's tower bell (minor-third tierce), struck dark or damped, and pitch
  bent down for its death; wood and rope are modal knocks and stick-slip creaks; fire is crackle and roar.

assets/audio/sfx/creatures/<creature>_<event>_<n>.ogg (mono, Vorbis q4, <= -2.5 dBFS sample peak, so <= -1 dBTP):
    voices  idle, attack, hurt, death         -18 LUFS momentary max (idle -20: it sits under the battle)
    movement skitter, slither, wingbeat, ...  -21 LUFS momentary max (it repeats on every action)
The slice's five foes have idle 1, attack 2, hurt 3, death 1, movement 3; the Act I foes idle 1, attack 2, hurt 2,
death 1, movement 2. Palette variants (wreck_crab, wallcrab, wall_polyp, stormgull) reuse their parent's set at another
pitch (game/data/audio/creature_voices.json), as their models reuse the parent's rig.

Render:  python3 tools/audio/render_all.py --only creature_sfx   (or python3 assets_src/sfx/creature_sfx.py [filter])
"""
from __future__ import annotations

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools", "audio"))
sys.path.insert(0, HERE)

import numpy as np  # noqa: E402

from field_ambience import modal, stick_slip  # noqa: E402
from synth.bells import tower_bell  # noqa: E402
from synth.dsp import SR, bq_bandpass, bq_highpass, bq_lowpass, bq_peak, filt, rng, smooth_noise  # noqa: E402
from synth.mixer import measure, normalize_momentary, write_ogg  # noqa: E402
from synth.reverb import ModFDNReverb  # noqa: E402
from synth.water import drip  # noqa: E402
from underwater_sfx import _n, _t, bubble_cloud, bubble_train, env_swell, muffle, noise, place  # noqa: E402

OUT_DIR = os.path.join(ROOT, "assets", "audio", "sfx", "creatures")
SEED = 20261414
VOICE, IDLE, MOVE = -18.0, -20.0, -21.0
CEILING = -2.5
QUALITY = 4.0
SLICE = ("reef_crab", "lantern_eel", "gull_harrier", "spawn_polyp", "drownbell")
# The movement word each family's files use.
MOVE_WORD = {"crab": "skitter", "eel": "slither", "bird": "wingbeat", "moth": "flutter", "polyp": "squelch",
             "leech": "flap", "bell": "shift", "wraith": "creak", "reach": "surge", "matron": "grind",
             "tortoise": "plod", "sparker": "scurry", "swarm": "shimmer", "skipper": "hop", "hound": "pad"}

# Each creature: its family and the numbers that make it itself. size scales bodies and slows gaits; pitch scales
# every resonance and voice; spawn makes an Undertow-spawn (wet, darker, a low moan under it).
CREATURES: dict[str, dict] = {
    "reef_crab": dict(family="crab", size=1.0, pitch=1.0, legs=3),
    "scuttler": dict(family="crab", size=0.7, pitch=1.25, legs=7, spawn=True, roll=True),
    "tide_crawler": dict(family="crab", size=1.1, pitch=0.85, legs=4, spawn=True),
    "bottle_hermit": dict(family="crab", size=0.6, pitch=1.3, legs=3, glass=True),
    "lantern_eel": dict(family="eel", size=1.0, pitch=1.0, lure=True),
    "hullgnaw": dict(family="eel", size=2.0, pitch=0.6, ribs=True, spawn=True),
    "gull_harrier": dict(family="bird", size=1.0, pitch=1.0),
    "squall_wing": dict(family="bird", size=1.1, pitch=0.8, spawn=True),
    "ashwing": dict(family="moth", size=1.2, pitch=0.85, rate=11.0),
    "flue_moth": dict(family="moth", size=0.8, pitch=1.15, rate=17.0, soot=True),
    "spawn_polyp": dict(family="polyp", size=1.0, pitch=1.0, spawn=True),
    "oil_slug": dict(family="polyp", size=1.0, pitch=0.7, viscous=True),
    "tower_limpet": dict(family="polyp", size=1.4, pitch=0.8, shell=True),
    "sail_leech": dict(family="leech", size=1.0, pitch=1.0, spawn=True),
    "drownbell": dict(family="bell", size=2.4, pitch=1.0, spawn=True),
    "spar_wraith": dict(family="wraith", size=2.0, pitch=1.0, spawn=True),
    "undertows_reach": dict(family="reach", size=4.0, pitch=1.0, spawn=True),
    "cinder_matron": dict(family="matron", size=2.5, pitch=1.0),
    "slag_tortoise": dict(family="tortoise", size=1.4, pitch=1.0),
    "vein_sparker": dict(family="sparker", size=0.8, pitch=1.0),
    "glassfry": dict(family="swarm", size=0.5, pitch=1.0),
    "shoal_skipper": dict(family="skipper", size=0.8, pitch=1.0),
    "raid_hound": dict(family="hound", size=1.0, pitch=1.0),
}


# --------------------------------------------------------------------------- building blocks


def buf(sec: float) -> np.ndarray:
    return np.zeros(_n(sec))


def room(x: np.ndarray, seed: int, mix: float = 0.12, tail: float = 0.35, rt60: float = 0.8) -> np.ndarray:
    """The battle's open air (a short, sparse FDN folded to mono), `tail` seconds appended."""
    rv = ModFDNReverb(rt60=rt60, rt60_high=rt60 * 0.5, predelay=0.018, size=1.3, mod_depth=4.0, mod_rate=0.3,
                      early_level=0.3, lowcut=150.0, highcut=6500.0, seed=seed)
    xs = np.concatenate([x, np.zeros(_n(tail))])
    wet = rv.process(np.stack([xs, xs], 1), tail=0.0)[: len(xs)].mean(axis=1)
    return (1 - mix) * xs + mix * wet


def finish(x: np.ndarray, target: float) -> np.ndarray:
    k = min(len(x) // 3, _n(0.05))
    x = x.copy()
    x[-k:] *= np.linspace(1, 0, k) ** 2
    x = filt(x, [bq_highpass(35, 0.7)])
    for _ in range(4):  # a peaky transient loses level in the limiter: go again until the target holds
        x = normalize_momentary(x, target, ceiling_db=CEILING)
    return x


def unit(x: np.ndarray) -> np.ndarray:
    return x / (np.abs(x).max() + 1e-12)


def warp(x: np.ndarray, r0: float, r1: float) -> np.ndarray:
    """Plays x at a rate gliding r0 -> r1 (a pitch bend, as a slowing tape)."""
    n_out = int(len(x) / ((r0 + r1) / 2.0)) - 2
    pos = np.cumsum(np.linspace(r0, r1, n_out))
    pos = pos[pos < len(x) - 1]
    return np.interp(pos, np.arange(len(x)), x)


def tap(g: np.random.Generator, freqs, decays, amp: float = 1.0, click: float = 0.5, jit: float = 0.06):
    """One hard-body tap (a leg tip, a claw, a plate): decaying shell modes, a little detuned each time."""
    s = 1.0 + float(g.uniform(-jit, jit))
    fs = [f * s for f in freqs if f * s < 0.45 * SR]
    amps = [float(g.uniform(0.5, 1.0)) / (i + 1) ** 0.7 for i in range(len(fs))]  # the low modes carry the knock
    return amp * unit(modal(fs, decays[: len(fs)], amps, max(decays) * 6 + 0.01, g, click=click))


def thump(g: np.random.Generator, f_from: float, f_to: float, tau: float, click: float = 0.3, sec: float = 0.4):
    """A body landing or striking: a pitch-dropping low sine and a short low knock."""
    n = _n(sec)
    t = _t(n)
    f = f_to + (f_from - f_to) * np.exp(-t / 0.025)
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / tau)
    k = _n(0.02)
    body[:k] += click * filt(g.standard_normal(k), [bq_lowpass(1100, 0.7)]) * np.exp(-_t(k) / 0.004)
    return body * np.minimum(1.0, t / 0.0006)


def train(g: np.random.Generator, sec: float, rate0: float, rate1: float, freqs, decays, amp_end: float = 1.0,
          jitter: float = 0.25, click: float = 0.4) -> np.ndarray:
    """A click train whose rate glides rate0 -> rate1 (mandibles chattering, legs rattling to a stop)."""
    out = buf(sec + 0.1)
    tt = 0.0
    while tt < sec:
        u = tt / sec
        rate = rate0 + (rate1 - rate0) * u
        a = 1.0 + (amp_end - 1.0) * u
        place(out, tap(g, freqs, decays, a * float(g.uniform(0.5, 1.0)), click), tt)
        tt += (1.0 / rate) * float(1.0 + g.uniform(-jitter, jitter))
    return out


def crackle(g: np.random.Generator, sec: float, rate: float, fc: float, q: float = 0.9, tau: float = 0.0):
    n = _n(sec)
    cnt = int(rate * sec)
    imp = np.zeros(n)
    pos = g.integers(0, n, cnt)
    imp[pos] = g.uniform(-1, 1, cnt) * g.uniform(0.2, 1.0, cnt) ** 2
    y = filt(imp, [bq_bandpass(fc, q)])
    return unit(y) * (np.exp(-_t(n) / tau) if tau > 0 else 1.0)


def burst(g: np.random.Generator, sec: float, sections, attack: float, decay: float) -> np.ndarray:
    n = _n(sec)
    t = _t(n)
    env = np.clip(t / max(attack, 1e-4), 0, 1) * np.exp(-np.maximum(t - attack, 0) / decay)
    return unit(noise(g, n, sections)) * env


def throat(g: np.random.Generator, dur: float, f0, formants, rough: float = 0.0, sub: float = 0.0,
           breath: float = 0.0, jitter: float = 0.01, attack: float = 0.015, release: float = 0.06,
           tilt: float = 0.8, kmax_hz: float = 9000.0, rough_hz: float = 70.0) -> np.ndarray:
    """A voiced call: an additive glottal source (harmonics k^-tilt) under formant resonances [(Hz, bandwidth,
    gain)], f0 a function of u in 0..1. rough: amplitude roughness at rough_hz; sub: period doubling (a growl's
    subharmonic); breath: the same formants on noise."""
    n = _n(dur)
    t = _t(n)
    u = t / dur
    f = np.asarray(f0(u), dtype=float) * (1 + jitter * smooth_noise(n, 35.0, g))
    ph = 2 * np.pi * np.cumsum(f) / SR
    y = np.zeros(n)
    kmax = int(min(80, kmax_hz / max(float(f.min()), 20.0)))
    for k in range(1, kmax + 1):
        fk = k * f
        w = sum(a / (1.0 + ((fk - F) / B) ** 2) for F, B, a in formants) * k ** -tilt * (fk < 0.45 * SR)
        y += w * np.sin(k * ph + float(g.uniform(0, 6.28)))
    if sub > 0:
        y *= 1.0 + sub * np.sin(ph / 2.0)
    if rough > 0:
        y *= 1.0 + rough * (0.6 * np.sin(2 * np.pi * rough_hz * t) + 0.4 * smooth_noise(n, rough_hz * 1.7, g))
    y = unit(y)
    if breath > 0:
        nz = g.standard_normal(n)
        br = sum(a * filt(nz, [bq_bandpass(F, max(F / B, 0.5))]) for F, B, a in formants)
        y = y + breath * unit(br)
    env = np.clip(t / attack, 0, 1) * np.clip((dur - t) / release, 0, 1) ** 1.5
    return y * env


def contour(start: float, top: float, end: float, peak_at: float = 0.2):
    """f0 rising start -> top by peak_at, then falling to end."""
    def f(u):
        up = start + (top - start) * np.clip(u / peak_at, 0, 1) ** 0.7
        down = top + (end - top) * np.clip((u - peak_at) / (1 - peak_at), 0, 1) ** 1.2
        return np.where(u < peak_at, up, down)
    return f


def glide(a: float, b: float, curve: float = 1.0):
    return lambda u: a * (b / a) ** (u ** curve)


def wobble(base: float, depth: float, hz: float, g: np.random.Generator):
    ph = float(g.uniform(0, 6.28))
    return lambda u: base * (1 + depth * np.sin(2 * np.pi * hz * u + ph))


def pop(g: np.random.Generator, f0: float, dur: float = 0.06, rise: float = 1.6) -> np.ndarray:
    """A suction seal breaking: a short sine whose pitch rises as the cavity opens, and a tiny click."""
    n = _n(dur)
    t = _t(n)
    f = f0 * (1 + (rise - 1) * np.clip(t / dur, 0, 1) ** 0.5)
    y = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / (dur * 0.35)) * np.minimum(1, t / 0.0008)
    k = _n(0.003)
    y[:k] += 0.3 * g.standard_normal(k) * np.linspace(1, 0, k)
    return y


def wet(g: np.random.Generator, sec: float, fc: float, stick: float = 40.0) -> np.ndarray:
    """Sticky wet flesh moving: low-passed noise gated by a fast random (the surface sticking and letting go)."""
    n = _n(sec)
    gate = np.clip(smooth_noise(n, stick, g), 0, 1) ** 1.5
    return unit(noise(g, n, [bq_lowpass(fc, 0.7), bq_highpass(80, 0.7)]) * gate)


def gurgle(g: np.random.Generator, sec: float, rate: float, r_lo: float, r_hi: float, amp: float = 1.0):
    n = _n(sec)
    return bubble_cloud(g, n, rate, r_lo, r_hi, env=env_swell(n, sec * 0.25, 1.0, sec * 0.5), amp=amp)


def beats(g: np.random.Generator, count: int, rate: float, fc: float, q: float = 0.8, up: float = 0.35,
          rustle: float = 0.15, rustle_fc: float = 4200.0, decay: float = 1.0, rate_end: float | None = None):
    """Wingbeats: a filtered noise burst per downstroke (and a weaker one per upstroke), feathers or paper on top.
    decay < 1 fades each beat; rate_end slows them (a bird going down)."""
    rate_end = rate if rate_end is None else rate_end
    times, tt = [], 0.0
    for i in range(count):
        times.append(tt)
        tt += 1.0 / (rate + (rate_end - rate) * i / max(1, count - 1)) * float(g.uniform(0.94, 1.06))
    out = buf(tt + 0.4)
    for i, at in enumerate(times):
        per = 1.0 / (rate + (rate_end - rate) * i / max(1, count - 1))
        a = decay ** i
        d = burst(g, per * 0.9, [bq_bandpass(fc, q), bq_lowpass(fc * 4, 0.7)], per * 0.2, per * 0.18)
        place(out, a * d, at)
        place(out, a * up * burst(g, per * 0.6, [bq_bandpass(fc * 1.3, q)], per * 0.15, per * 0.12), at + per * 0.5)
        if rustle > 0:
            r = burst(g, per * 0.5, [bq_bandpass(rustle_fc, 1.2)], 0.004, per * 0.12)
            r *= 1 + 0.6 * np.sin(2 * np.pi * 130 * _t(len(r)))
            place(out, a * rustle * r, at + per * 0.05)
    return out


def creak(g: np.random.Generator, dur: float, lo: float, hi: float, body, amp: float = 1.0) -> np.ndarray:
    return amp * stick_slip(g, dur, lo, hi, body, q=7.0)


WOOD = [(310, 1.0), (690, 0.7), (1240, 0.4), (2100, 0.2)]
ROPE = [(520, 1.0), (980, 0.6), (1800, 0.3)]


def roar(g: np.random.Generator, sec: float, fc: float, flicker: float = 9.0) -> np.ndarray:
    """Fire or a mass of water: broadband noise under a low-pass, its level flickering."""
    n = _n(sec)
    x = noise(g, n, [bq_lowpass(fc, 0.6), bq_highpass(50, 0.7)])
    return unit(x) * (0.75 + 0.25 * smooth_noise(n, flicker, g))


# --------------------------------------------------------------------------- families
# Each family has idle(p, v, g), attack, hurt, death and move; p is the creature's CREATURES row, v the variant.


class Crab:
    """Shelled walkers: the reef crab, the scuttler (a 14-legged sea-louse that rolls up when struck), the tide
    crawler (high-legged spawn), the bottle hermit (a hermit crab in a lamp glass)."""

    @staticmethod
    def shell(p):
        k = p["pitch"] / p["size"] ** 0.3
        return [1300 * k, 2300 * k, 3600 * k, 5600 * k], [0.008, 0.006, 0.004, 0.0028]

    @classmethod
    def idle(cls, p, v, g):
        fr, de = cls.shell(p)
        x = buf(1.4)
        place(x, train(g, 0.35, 32, 26, fr, de, 0.6), 0.05, 0.5)
        place(x, train(g, 0.25, 28, 20, fr, de, 0.5), 0.6, 0.4)
        place(x, gurgle(g, 1.0, 45, 0.7 / p["pitch"], 1.5 / p["pitch"], 0.5), 0.15, 0.6)
        if p.get("spawn"):
            place(x, throat(g, 0.9, wobble(62 * p["pitch"], 0.05, 1.5, g), [(330, 110, 1.0), (760, 180, 0.4)],
                            rough=0.5, sub=0.4, breath=0.35, attack=0.15, release=0.3), 0.2, 0.35)
        if p.get("glass"):
            place(x, glass_ring(g, 1650 * p["pitch"], 1.1, 0.3), 0.35, 0.25)
        return x

    @classmethod
    def attack(cls, p, v, g):
        fr, de = cls.shell(p)
        x = buf(1.0)
        s = 1.0 + 0.07 * v
        place(x, creak(g, 0.14, 260 * s, 900 * s, [(fr[0] * 0.6, 1.0), (fr[1] * 0.6, 0.6)]), 0.0, 0.35)
        snap_at = 0.15 + 0.02 * v
        place(x, tap(g, [f * 0.75 * s for f in fr], [d * 1.8 for d in de], 1.0, click=1.0), snap_at)
        place(x, thump(g, 200 * p["pitch"], 95 * p["pitch"], 0.04 * p["size"], 0.5), snap_at, 0.7)
        place(x, train(g, 0.18, 40, 30, fr, de, 0.4), snap_at + 0.08, 0.35)
        if p.get("spawn"):
            place(x, burst(g, 0.3, [bq_bandpass(2400, 1.0)], 0.02, 0.08), snap_at - 0.05, 0.25)
            place(x, wet(g, 0.2, 900, 50), snap_at, 0.3)
        if p.get("glass"):
            place(x, glass_ring(g, 2300 * p["pitch"] * s, 0.6, 0.15), snap_at, 0.4)
        return x

    @classmethod
    def hurt(cls, p, v, g):
        fr, de = cls.shell(p)
        x = buf(0.8)
        s = 1.0 - 0.05 * v
        place(x, tap(g, [f * 0.55 * s for f in fr], [d * 2.5 for d in de], 1.0, click=0.9), 0.0)
        place(x, crackle(g, 0.05, 900, 3000 * p["pitch"], tau=0.02), 0.0, 0.5)
        place(x, train(g, 0.3, 48, 30, fr, de, 0.5, jitter=0.35), 0.05, 0.55)
        place(x, gurgle(g, 0.35, 120, 0.6, 1.3, 0.5), 0.06, 0.6)
        if p.get("roll"):  # the plates clatter as it rolls up
            for i in range(6):
                place(x, tap(g, [f * 0.8 for f in fr], de, 0.7, 0.6), 0.03 + 0.12 * (0.82 ** i) * i)
        if p.get("spawn"):
            place(x, throat(g, 0.35, glide(95 * p["pitch"], 70 * p["pitch"]), [(360, 120, 1.0), (850, 200, 0.4)],
                            rough=0.7, sub=0.5, breath=0.4), 0.03, 0.4)
        if p.get("glass"):
            place(x, glass_ring(g, 1900 * p["pitch"] * s, 0.5, 0.2), 0.0, 0.5)
        return x

    @classmethod
    def death(cls, p, v, g):
        fr, de = cls.shell(p)
        x = buf(2.0)
        place(x, train(g, 1.2, 40, 5, fr, de, 0.15, jitter=0.4), 0.0, 0.6)
        place(x, gurgle(g, 1.2, 50, 0.8, 1.8, 0.5), 0.1, 0.5)
        place(x, thump(g, 130 * p["pitch"], 70 * p["pitch"], 0.06 * p["size"], 0.4), 1.25, 0.6)
        place(x, tap(g, [f * 0.6 for f in fr], de, 0.6, 0.5), 1.26)
        if p.get("spawn"):
            place(x, throat(g, 1.4, glide(90 * p["pitch"], 48 * p["pitch"]), [(340, 110, 1.0), (720, 170, 0.5)],
                            rough=0.4, sub=0.3, breath=0.5, attack=0.1, release=0.5), 0.2, 0.45)
            place(x, bubble_train(g, 8, 2.5, 4.0, (0.06, 0.12), amp=0.4, fade=0.7), 0.6)
        if p.get("glass"):
            place(x, warp(glass_ring(g, 1650 * p["pitch"], 1.6, 0.3), 1.0, 0.85), 0.3, 0.35)
        return x

    @classmethod
    def move(cls, p, v, g):
        fr, de = cls.shell(p)
        sec = 0.95
        x = buf(sec + 0.2)
        stride = 0.1 * p["size"] ** 0.5 * (1.0 + 0.08 * v)
        legs = p.get("legs", 3)
        tt = 0.0
        while tt < sec:
            for j in range(legs):
                at = tt + j * float(g.uniform(0.008, 0.02)) * (3.0 / legs) ** 0.5
                place(x, tap(g, fr, de, float(g.uniform(0.35, 1.0)), 0.5, jit=0.1), at)
                if p.get("glass") and g.random() < 0.3:
                    place(x, glass_ring(g, 2100 * p["pitch"] * float(g.uniform(0.95, 1.05)), 0.25, 0.08), at, 0.3)
                if p.get("spawn") and g.random() < 0.35:
                    place(x, drip(0.5, float(g.uniform(1.0, 1.6)), seed=int(g.integers(1 << 30))), at, 1.5)
            tt += stride * float(g.uniform(0.85, 1.15))
        sand = noise(g, len(x), [bq_bandpass(2400, 0.8)]) * 0.02 * np.clip(_t(len(x)) / 0.05, 0, 1)
        return x + sand * (_t(len(x)) < sec)


def glass_ring(g: np.random.Generator, f: float, dur: float, amp: float = 1.0) -> np.ndarray:
    """A struck lamp glass: a few inharmonic, beating partials."""
    n = _n(dur)
    t = _t(n)
    y = np.zeros(n)
    for r, a in ((1.0, 1.0), (2.32, 0.4), (4.25, 0.15)):
        ff = f * r
        if ff < 0.45 * SR:
            beat = float(g.uniform(0.4, 1.6))
            y += a * np.exp(-6.91 * t / (dur / r ** 0.5)) * 0.5 * (
                np.sin(2 * np.pi * ff * t + float(g.uniform(0, 6.28))) + np.sin(2 * np.pi * (ff + beat) * t))
    return amp * y * np.clip(t / 0.002, 0, 1)


class Eel:
    """Long swimmers: the lantern eel (a cold lure-light), Hullgnaw (a spawn eel grown through a ship's ribs)."""

    F = [(320, 120, 1.0), (850, 220, 0.45), (2200, 400, 0.12)]

    @classmethod
    def fm(cls, p):
        return [(F * p["pitch"], B, a) for F, B, a in cls.F]

    @classmethod
    def idle(cls, p, v, g):
        x = buf(1.6)
        place(x, throat(g, 1.3, wobble(72 * p["pitch"], 0.06, 1.2, g), cls.fm(p), rough=0.45, sub=0.35,
                        breath=0.35, attack=0.2, release=0.4), 0.05, 0.8)
        place(x, bubble_train(g, 6, 3.0 * p["size"] ** 0.3, 5.0 * p["size"] ** 0.3, (0.12, 0.2), amp=0.5), 0.25)
        if p.get("lure"):
            place(x, lure(g, 1.5, 0.35), 0.0)
        if p.get("ribs"):
            place(x, creak(g, 0.9, 40, 140, WOOD, 0.5), 0.4)
        return x

    @classmethod
    def attack(cls, p, v, g):
        x = buf(1.1)
        n = _n(0.4)
        rush = muffle(noise(g, n, [bq_highpass(120, 0.7)]), 500.0, 2800.0, 0.0, 0.3) * env_swell(n, 0.3, 2.0, 0.08)
        place(x, unit(rush), 0.0, 0.6)
        at = 0.3 + 0.03 * v
        teeth = [1250 * p["pitch"], 2350 * p["pitch"], 3700 * p["pitch"]]
        place(x, tap(g, teeth, [0.006, 0.004, 0.003], 1.0, click=1.0), at)
        place(x, thump(g, 150 * p["pitch"], 70 * p["pitch"], 0.05 * p["size"] ** 0.5, 0.5), at, 0.8)
        place(x, throat(g, 0.4, glide(140 * p["pitch"], 95 * p["pitch"]), cls.fm(p), rough=0.6, sub=0.4,
                        breath=0.6), at - 0.12, 0.45)
        if p.get("lure"):
            place(x, lure(g, 0.5, 0.4, flare=True), 0.0)
        if p.get("ribs"):
            place(x, tap(g, [180, 420, 900], [0.05, 0.03, 0.02], 0.9, click=0.8), at + 0.01, 0.8)
            place(x, crackle(g, 0.12, 400, 1500, tau=0.05), at, 0.4)
        return x

    @classmethod
    def hurt(cls, p, v, g):
        x = buf(0.9)
        place(x, burst(g, 0.25, [bq_highpass(500, 0.7), bq_lowpass(7000, 0.7)], 0.003, 0.05), 0.0, 0.6)
        place(x, throat(g, 0.38 + 0.04 * v, glide((125 + 15 * v) * p["pitch"], 80 * p["pitch"]), cls.fm(p),
                        rough=0.7, sub=0.5, breath=0.4), 0.03, 0.9)
        place(x, gurgle(g, 0.4, 90, 2.0, 4.5, 0.6), 0.05, 0.6)
        if p.get("ribs"):
            place(x, tap(g, [210, 480, 1050], [0.04, 0.03, 0.02], 0.9, click=0.9), 0.0, 0.7)
        return x

    @classmethod
    def death(cls, p, v, g):
        x = buf(2.6)
        place(x, throat(g, 1.9, glide(115 * p["pitch"], 42 * p["pitch"], 0.8), cls.fm(p), rough=0.35, sub=0.3,
                        breath=0.45, attack=0.05, release=0.7), 0.0, 0.9)
        place(x, bubble_train(g, 14, 3.0, 6.0, (0.05, 0.11), amp=0.45, fade=0.8), 0.5)
        m = Eel.move(p, 9, g)
        place(x, (m * np.exp(-_t(len(m)) / 0.4))[: _n(1.0)], 0.0, 0.4)
        if p.get("lure"):
            place(x, warp(lure(g, 1.8, 0.4), 1.0, 0.7), 0.1)
        if p.get("ribs"):
            for at in (0.35, 0.6, 0.78):
                place(x, tap(g, [170, 400, 880], [0.06, 0.04, 0.02], 0.7, click=0.8), at, 0.6)
        return x

    @staticmethod
    def move(p, v, g):
        sec = 1.1
        n = _n(sec)
        t = _t(n)
        body = noise(g, n, [bq_bandpass(700 * p["pitch"], 0.7), bq_lowpass(2600, 0.7)])
        hz = (2.4 + 0.3 * (v % 3)) / p["size"] ** 0.3
        und = (0.5 + 0.5 * np.sin(2 * np.pi * hz * t + float(g.uniform(0, 6)))) ** 1.5
        sheen = noise(g, n, [bq_highpass(3000, 0.7)])
        x = (unit(body) + 0.15 * unit(sheen)) * und * env_swell(n, 0.35, 1.5, 0.5)
        for _ in range(3):
            place(x, drip(0.5, float(g.uniform(1.6, 3.0)), seed=int(g.integers(1 << 30))), float(g.uniform(0.1, 0.9)),
                  1.2)
        if p.get("ribs"):
            place(x, creak(g, 0.7, 50, 160, WOOD, 0.5), 0.2)
        return x


def lure(g: np.random.Generator, dur: float, amp: float, flare: bool = False) -> np.ndarray:
    """The lantern eel's cold light as a sound: a pure, slowly beating glass hum that swells."""
    n = _n(dur)
    t = _t(n)
    y = np.sin(2 * np.pi * 880 * t) + 0.9 * np.sin(2 * np.pi * 881.3 * t) + 0.25 * np.sin(2 * np.pi * 1320.7 * t)
    e = env_swell(n, dur * (0.3 if flare else 0.5), 2.0, dur * 0.25)
    return amp * unit(y) * e


class Bird:
    """Sea-birds: the gull harrier (storm-fattened, rasping), the squall wing (a gull-shaped hole in the rain)."""

    @staticmethod
    def fm(p):
        k = p["pitch"]
        return [(1750 * k, 500, 0.7), (2900 * k, 700, 1.0), (4300 * k, 900, 0.35)]

    @classmethod
    def call(cls, p, g, dur, top, fall, rough):
        k = p["pitch"]
        y = throat(g, dur, contour(top * 0.72 * k, top * k, top * (1 - fall) * k, 0.18), cls.fm(p), rough=rough,
                   breath=0.08, jitter=0.02, tilt=1.0, rough_hz=float(g.uniform(55, 85)), attack=0.01, release=0.05)
        if p.get("spawn"):  # hollow: the call heard through rain, half voice, half wind
            y = filt(y, [bq_lowpass(2600, 0.7)]) * 0.7 + 0.5 * unit(noise(g, len(y), [bq_bandpass(top * k, 2.0)])) * (
                np.abs(y) > 0.05)
        return y

    @classmethod
    def idle(cls, p, v, g):
        x = buf(1.3)
        place(x, cls.call(p, g, 0.2, 1350, 0.25, 0.45), 0.0, 0.8)
        place(x, cls.call(p, g, 0.3, 1450, 0.32, 0.5), 0.3, 1.0)
        place(x, beats(g, 2, 3.4 / p["size"] ** 0.4, 480, rustle=0.12), 0.75, 0.5)
        if p.get("spawn"):
            place(x, rain(g, 1.3, 0.12), 0.0)
        return x

    @classmethod
    def attack(cls, p, v, g):
        x = buf(1.2)
        n = _n(0.4)
        fold = muffle(noise(g, n, [bq_highpass(200, 0.7)]), 400.0, 2200.0, 0.0, 0.35) * env_swell(n, 0.33, 2.0, 0.06)
        place(x, unit(fold), 0.0, 0.6)
        place(x, cls.call(p, g, 0.45, 1500 + 80 * v, 0.4, 0.65), 0.28, 1.0)
        for i in range(3):  # the talons raking
            place(x, creak(g, 0.05, 600, 1600, [(2400, 1.0), (3800, 0.5)], 0.35), 0.36 + 0.06 * i + 0.01 * v)
        if p.get("spawn"):
            place(x, rain(g, 1.2, 0.15), 0.0)
        return x

    @classmethod
    def hurt(cls, p, v, g):
        x = buf(0.8)
        place(x, cls.call(p, g, 0.16 + 0.03 * v, 1700 + 100 * v, 0.45, 0.85), 0.0, 1.0)
        place(x, beats(g, 3, 9.0, 560, up=0.5, rustle=0.3, decay=0.8), 0.04, 0.5)
        return x

    @classmethod
    def death(cls, p, v, g):
        x = buf(2.4)
        place(x, cls.call(p, g, 0.9, 1400, 0.6, 0.75), 0.0, 1.0)
        place(x, beats(g, 6, 6.0, 500, rustle=0.2, decay=0.75, rate_end=2.2), 0.2, 0.55)
        place(x, thump(g, 110, 70, 0.05, 0.4), 1.75, 0.45)
        if p.get("spawn"):
            place(x, rain(g, 2.0, 0.12), 0.0)
        return x

    @staticmethod
    def move(p, v, g):
        x = beats(g, 3 + (v % 2), 3.2 / p["size"] ** 0.4 * (1 + 0.05 * v), 450 / p["size"] ** 0.3, rustle=0.15)
        if p.get("spawn"):
            x = x + rain(g, len(x) / SR, 0.1)
        return x


def rain(g: np.random.Generator, sec: float, amp: float) -> np.ndarray:
    """Rain on water: a soft hiss and scattered tiny drops."""
    n = _n(sec)
    x = 0.4 * unit(noise(g, n, [bq_highpass(2500, 0.7), bq_lowpass(9000, 0.7)]))
    for _ in range(int(25 * sec)):
        place(x, drip(float(g.uniform(0.2, 0.6)), float(g.uniform(0.8, 1.6)), seed=int(g.integers(1 << 30))),
              float(g.uniform(0, sec)), 2.0)
    return amp * x * np.clip(_t(n) / 0.1, 0, 1)


class Moth:
    """Dusty fliers: the ashwing (broad, grey, ash for wing-dust), the flue moth (the Coilspire's sooty one)."""

    @staticmethod
    def flutter(p, g, sec, rate0, rate1=None, amp_end=1.0, irregular=0.06):
        rate1 = rate0 if rate1 is None else rate1
        x = buf(sec + 0.2)
        tt = 0.0
        hi = 2600 * p["pitch"] * (0.7 if p.get("soot") else 1.0)
        while tt < sec:
            u = tt / sec
            a = 1.0 + (amp_end - 1.0) * u
            place(x, a * burst(g, 0.04, [bq_bandpass(hi, 0.9)], 0.003, 0.012), tt)
            place(x, a * 0.6 * burst(g, 0.06, [bq_lowpass(260, 0.7)], 0.006, 0.02), tt)
            tt += 1.0 / (rate0 + (rate1 - rate0) * u) * float(g.uniform(1 - irregular, 1 + irregular))
        return x

    @classmethod
    def dust(cls, p, g, sec, amp):
        y = crackle(g, sec, 160, 5200 * p["pitch"], 1.2)
        if p.get("soot"):
            y = y + 0.6 * crackle(g, sec, 30, 1600, 1.5)  # embers in the soot
        return amp * y * np.clip(_t(len(y)) / 0.05, 0, 1)

    @classmethod
    def idle(cls, p, v, g):
        x = buf(1.3)
        place(x, cls.flutter(p, g, 0.3, p["rate"]), 0.0)
        place(x, cls.flutter(p, g, 0.35, p["rate"] * 1.05), 0.6)
        place(x, cls.dust(p, g, 1.1, 0.15), 0.1)
        return x

    @classmethod
    def attack(cls, p, v, g):
        x = buf(1.0)
        n = _n(0.45)
        puff = noise(g, n, [bq_highpass(700, 0.7), bq_lowpass(7000, 0.7)]) * env_swell(n, 0.06 + 0.02 * v, 1.0, 0.12)
        place(x, cls.flutter(p, g, 0.3, p["rate"] * 1.4), 0.0, 0.8)
        place(x, unit(puff), 0.22, 0.8)
        place(x, crackle(g, 0.03, 1500, 3000, tau=0.01), 0.22, 0.5)
        place(x, cls.dust(p, g, 0.6, 0.25), 0.25)
        return x

    @classmethod
    def hurt(cls, p, v, g):
        x = buf(0.8)
        place(x, crackle(g, 0.07, 1200, 2400 * p["pitch"], tau=0.03), 0.0, 0.8)
        place(x, cls.flutter(p, g, 0.4, p["rate"] * 1.6, irregular=0.35), 0.02)
        place(x, creak(g, 0.08 + 0.02 * v, 900, 2400, [(3400 * p["pitch"], 1.0), (5200, 0.4)], 0.4), 0.05)
        return x

    @classmethod
    def death(cls, p, v, g):
        x = buf(2.2)
        place(x, cls.flutter(p, g, 1.5, p["rate"], 3.0, amp_end=0.2, irregular=0.2), 0.0)
        place(x, cls.dust(p, g, 1.8, 0.18) * np.linspace(1, 0.2, _n(1.8)), 0.2)
        place(x, burst(g, 0.12, [bq_bandpass(1200, 0.8)], 0.004, 0.03), 1.6, 0.4)
        return x

    @classmethod
    def move(cls, p, v, g):
        return cls.flutter(p, g, 0.8 + 0.1 * v, p["rate"] * (1 + 0.04 * v))


class Polyp:
    """Wet clingers: the spawn-polyp (soft cyan mouths in the floodwater), the oil slug (viscous, slow), the tower
    limpet (a cartwheel shell clamped to the stair)."""

    @staticmethod
    def k(p):
        return p["pitch"] * (0.75 if p.get("viscous") else 1.0)

    @classmethod
    def idle(cls, p, v, g):
        k = cls.k(p)
        x = buf(1.5)
        for i, at in enumerate((0.05, 0.42, 0.8)):
            place(x, pop(g, (360 + 60 * i) * k, 0.09 if p.get("viscous") else 0.06), at, 0.6)
        place(x, gurgle(g, 1.2, 25 if p.get("viscous") else 40, 3.0 / k, 7.0 / k, 0.6), 0.1)
        place(x, wet(g, 0.9, 700 * k, 18 if p.get("viscous") else 30) * env_swell(_n(0.9), 0.4, 1.5, 0.3), 0.2, 0.3)
        if p.get("shell"):
            place(x, tap(g, [720 * k, 1580 * k, 2700 * k], [0.02, 0.012, 0.008], 0.5, 0.6), 0.6)
        if p.get("spawn"):
            place(x, throat(g, 1.0, wobble(58 * k, 0.04, 1.0, g), [(300, 100, 1.0), (700, 160, 0.3)], rough=0.3,
                            sub=0.4, breath=0.5, attack=0.3, release=0.4), 0.2, 0.25)
        return x

    @classmethod
    def attack(cls, p, v, g):
        k = cls.k(p)
        x = buf(1.0)
        at = 0.12 + 0.03 * v
        place(x, wet(g, 0.18, 1100 * k, 50) * np.linspace(0, 1, _n(0.18)) ** 2, at - 0.17, 0.4)
        place(x, burst(g, 0.2, [bq_lowpass(1500 * k, 0.7)], 0.002, 0.04), at, 0.8)
        place(x, thump(g, 170 * k, 90 * k, 0.04, 0.4), at, 0.7)
        place(x, pop(g, 300 * k, 0.08, 1.9), at + 0.06, 0.8)
        place(x, gurgle(g, 0.4, 120, 1.5, 3.5, 0.5), at + 0.02)
        if p.get("shell"):
            place(x, tap(g, [700 * k, 1500 * k, 2600 * k], [0.03, 0.015, 0.01], 1.0, 0.9), at, 0.8)
        if p.get("spawn"):
            place(x, train(g, 0.15, 45, 35, [900, 1700], [0.006, 0.004], 0.5), at + 0.02, 0.3)
        return x

    @classmethod
    def hurt(cls, p, v, g):
        k = cls.k(p)
        x = buf(0.8)
        place(x, wet(g, 0.14, 1300 * k, 70), 0.0, 0.7)
        place(x, pop(g, (420 - 40 * v) * k, 0.1, 0.6), 0.01, 0.8)
        place(x, gurgle(g, 0.3, 200, 1.2, 3.0, 0.6), 0.02)
        place(x, burst(g, 0.25, [bq_bandpass(2600, 1.2)], 0.01, 0.06), 0.03, 0.2)
        if p.get("shell"):
            place(x, tap(g, [650 * k, 1450 * k, 2500 * k], [0.025, 0.012, 0.008], 0.8, 0.9), 0.0, 0.6)
        return x

    @classmethod
    def death(cls, p, v, g):
        k = cls.k(p)
        x = buf(2.2)
        n = _n(1.5)
        deflate = muffle(noise(g, n, [bq_highpass(80, 0.7)]), 1500.0 * k, 220.0 * k, 0.0, 1.3)
        place(x, unit(deflate) * env_swell(n, 0.08, 1.0, 0.6), 0.0, 0.6)
        place(x, gurgle(g, 1.4, 60, 2.0 / k, 6.0 / k, 0.6) * np.linspace(1, 0.3, _n(1.4)), 0.05)
        place(x, pop(g, 260 * k, 0.07), 1.55, 0.5)
        if p.get("spawn"):
            place(x, throat(g, 1.3, glide(70 * k, 40 * k), [(300, 100, 1.0), (680, 150, 0.3)], rough=0.3, sub=0.4,
                            breath=0.5, attack=0.05, release=0.5), 0.05, 0.4)
        if p.get("shell"):
            place(x, tap(g, [600 * k, 1350 * k], [0.04, 0.02], 0.7, 0.6), 1.5, 0.6)
            place(x, thump(g, 120, 60, 0.08, 0.3), 1.5, 0.5)
        return x

    @classmethod
    def move(cls, p, v, g):
        k = cls.k(p)
        x = buf(1.2)
        count = 2 if p.get("viscous") else 3
        for i in range(count):
            at = 0.05 + i * (0.42 if p.get("viscous") else 0.3) + float(g.uniform(-0.03, 0.03))
            d = 0.25 if p.get("viscous") else 0.16
            place(x, wet(g, d, 900 * k, 25 if p.get("viscous") else 45) * env_swell(_n(d), d * 0.4, 1.0, d * 0.3),
                  at, 0.8)
            place(x, pop(g, float(g.uniform(320, 460)) * k, 0.06), at + d * 0.6, 0.5)
            if p.get("shell"):
                place(x, creak(g, 0.18, 90, 260, [(800 * k, 1.0), (1600 * k, 0.5)], 0.3), at)
        place(x, gurgle(g, 1.0, 30, 1.2, 3.0, 0.3), 0.1)
        return x


class Leech:
    """The sail leech: a flat ray-shaped spawn that clings to wet canvas and drops from the yards."""

    @staticmethod
    def flap(g, count, rate, amp_end=1.0, rate_end=None):
        x = beats(g, count, rate, 260, q=0.7, up=0.3, rustle=0.0, decay=amp_end ** (1 / max(1, count)),
                  rate_end=rate_end)
        per = 1.0 / rate
        for i in range(count):
            place(x, burst(g, 0.08, [bq_lowpass(1600, 0.7)], 0.002, 0.02) * amp_end ** (i / max(1, count)),
                  i * per + per * 0.1, 0.35)
        return x

    @classmethod
    def idle(cls, p, v, g):
        x = buf(1.3)
        place(x, Polyp.idle(p, v, g)[: _n(1.1)], 0.0, 0.6)
        n = _n(0.6)
        canvas = noise(g, n, [bq_bandpass(320, 0.8)]) * (0.6 + 0.4 * np.sin(2 * np.pi * 17 * _t(n))) * env_swell(
            n, 0.25, 1.5, 0.2)
        place(x, unit(canvas), 0.5, 0.4)
        return x

    @classmethod
    def attack(cls, p, v, g):
        x = buf(1.1)
        n = _n(0.45)
        drop = muffle(noise(g, n, [bq_highpass(150, 0.7)]), 300.0, 1600.0, 0.0, 0.4) * env_swell(n, 0.4, 2.0, 0.05)
        place(x, unit(drop), 0.0, 0.6)
        place(x, Polyp.attack(p, v, g), 0.3)
        return x

    @classmethod
    def hurt(cls, p, v, g):
        x = Polyp.hurt(p, v, g)
        place(x, cls.flap(g, 2, 7.0, 0.6), 0.03, 0.5)
        return x

    @classmethod
    def death(cls, p, v, g):
        x = Polyp.death(p, v, g)
        place(x, cls.flap(g, 4, 4.0, 0.3, rate_end=1.8), 0.0, 0.6)
        return x

    @classmethod
    def move(cls, p, v, g):
        return cls.flap(g, 3, 2.6 * (1 + 0.06 * v))


class Bell:
    """The Drownbell: a temple bell the sea kept, walked on six short black legs by the dark mass under its rim,
    a rotten bell-rope trailing into the water. Its toll is battle_sfx.py's; these are its body."""

    LEGS = [1500, 2600, 3900], [0.005, 0.004, 0.003]

    @classmethod
    def idle(cls, p, v, g):
        x = buf(2.6)
        place(x, tower_bell(38.0, vel=0.3, seed=SEED + 501, t60=3.0, dark=0.75)[: _n(2.4)], 0.1, 0.35)
        place(x, cls.legs(g, 0.6, 0.7), 0.3, 0.6)
        place(x, creak(g, 0.7, 30, 110, ROPE, 0.4), 0.9)
        place(x, slosh(g, 2.0, 0.4), 0.0)
        place(x, throat(g, 1.6, wobble(48, 0.04, 0.8, g), [(280, 90, 1.0), (620, 140, 0.4)], rough=0.3, sub=0.4,
                        breath=0.5, attack=0.4, release=0.6), 0.5, 0.3)
        return x

    @classmethod
    def legs(cls, g, sec, wetness):
        x = train(g, sec, 14, 10, cls.LEGS[0], cls.LEGS[1], 0.7, jitter=0.4, click=0.3)
        for _ in range(int(sec * 8 * wetness)):
            place(x, drip(0.5, float(g.uniform(1.4, 2.5)), seed=int(g.integers(1 << 30))), float(g.uniform(0, sec)),
                  1.4)
        return x

    @classmethod
    def attack(cls, p, v, g):  # hood_slam's tell: it rears on its legs, the bronze grinding on its own lip
        x = buf(1.6)
        place(x, cls.legs(g, 0.45, 1.0), 0.0, 0.7)
        place(x, creak(g, 0.5, 40 + 10 * v, 160, [(380, 1.0), (760, 0.6), (1150, 0.4)], 0.6), 0.05)
        place(x, throat(g, 0.8, glide(55, 75 + 8 * v), [(300, 100, 1.0), (650, 140, 0.5)], rough=0.6, sub=0.5,
                        breath=0.6, attack=0.2, release=0.2), 0.15, 0.6)
        place(x, tower_bell(43.0 + v, vel=0.45, seed=SEED + 510 + v, t60=1.8, dark=0.6)[: _n(1.1)], 0.3, 0.3)
        return x

    @classmethod
    def hurt(cls, p, v, g):  # a damped bronze clank, the mass under the rim recoiling
        x = buf(1.4)
        clank = tower_bell(50.0 + 1.5 * v, vel=0.8, seed=SEED + 520 + v, t60=0.9, dark=0.35)[: _n(1.0)]
        place(x, clank * np.exp(-_t(len(clank)) / 0.25), 0.0, 0.8)
        place(x, cls.legs(g, 0.3, 0.6), 0.04, 0.6)
        place(x, throat(g, 0.4, glide(80 + 6 * v, 55), [(320, 110, 1.0), (700, 150, 0.4)], rough=0.7, sub=0.5,
                        breath=0.5), 0.05, 0.6)
        return x

    @classmethod
    def death(cls, p, v, g):  # the bell's voice bent down and drowned; the legs give; bubbles rise as it settles
        x = buf(4.2)
        bell = tower_bell(41.0, vel=0.7, seed=SEED + 530, t60=4.0, dark=0.45)
        place(x, warp(bell, 1.0, 0.82)[: _n(3.8)], 0.0, 0.55)
        place(x, throat(g, 2.6, glide(70, 34, 0.7), [(290, 90, 1.0), (640, 140, 0.4)], rough=0.35, sub=0.4,
                        breath=0.5, attack=0.1, release=1.0), 0.1, 0.5)
        legs = cls.legs(g, 0.8, 0.8)
        place(x, legs * np.linspace(1, 0.2, len(legs)), 0.2, 0.5)
        place(x, bubble_train(g, 18, 4.0, 8.0, (0.05, 0.12), amp=0.5, fade=0.7), 1.2)
        place(x, slosh(g, 3.0, 0.6), 0.8)
        return x

    @classmethod
    def move(cls, p, v, g):
        x = buf(1.5)
        place(x, cls.legs(g, 0.9 + 0.1 * v, 1.0), 0.0, 0.8)
        place(x, creak(g, 0.8, 30 + 8 * v, 120, ROPE, 0.4), 0.15)
        place(x, slosh(g, 1.3, 0.5), 0.0)
        return x


def slosh(g: np.random.Generator, sec: float, amp: float, hz: float = 1.8) -> np.ndarray:
    """Water moved by a heavy body: a low surge that swings and dies, and a little splash on top."""
    n = _n(sec)
    t = _t(n)
    e = np.clip(t / 0.1, 0, 1) * np.exp(-t / (sec * 0.45)) * (0.6 + 0.4 * np.cos(2 * np.pi * hz * t))
    lo = unit(noise(g, n, [bq_lowpass(420, 0.7), bq_highpass(40, 0.7)]))
    hi = unit(noise(g, n, [bq_bandpass(1400, 0.7)]))
    return amp * (lo + 0.25 * hi) * e


class Wraith:
    """The Spar-Wraith: a spawn tangled in a dead ship's rigging, its body hung in the shrouds, spars for limbs.
    The wind through the shrouds is its voice."""

    F = [(380, 120, 1.0), (800, 180, 0.5), (2500, 500, 0.1)]

    @classmethod
    def moan(cls, g, dur, f0):
        return throat(g, dur, f0, cls.F, rough=0.2, sub=0.15, breath=1.2, jitter=0.03, attack=dur * 0.3,
                      release=dur * 0.35, tilt=1.2)

    @classmethod
    def idle(cls, p, v, g):
        x = buf(2.0)
        place(x, cls.moan(g, 1.6, wobble(190, 0.06, 1.3, g)), 0.1, 0.7)
        place(x, creak(g, 0.8, 35, 130, WOOD, 0.6), 0.2)
        place(x, creak(g, 0.5, 60, 200, ROPE, 0.4), 1.1)
        return x

    @classmethod
    def attack(cls, p, v, g):
        x = buf(1.4)
        place(x, creak(g, 0.35, 50, 220, WOOD, 0.7), 0.0)
        n = _n(0.3)
        whip = muffle(noise(g, n, [bq_highpass(300, 0.7)]), 800.0, 5000.0, 0.0, 0.25) * env_swell(n, 0.26, 3.0, 0.02)
        place(x, unit(whip), 0.25 + 0.02 * v, 0.7)
        place(x, tap(g, [1800, 3100, 5200], [0.004, 0.003, 0.002], 1.0, click=1.0), 0.51 + 0.02 * v)
        place(x, cls.moan(g, 0.8, contour(170, 260 + 20 * v, 150, 0.4)), 0.1, 0.8)
        return x

    @classmethod
    def hurt(cls, p, v, g):
        x = buf(1.0)
        place(x, tap(g, [240, 560, 1150, 2000], [0.05, 0.035, 0.02, 0.012], 1.0, click=1.0), 0.0)
        place(x, crackle(g, 0.15, 500, 1700, tau=0.06), 0.0, 0.5)
        place(x, cls.moan(g, 0.5, glide(260 + 20 * v, 180)), 0.03, 0.8)
        return x

    @classmethod
    def death(cls, p, v, g):
        x = buf(3.4)
        place(x, cls.moan(g, 2.6, glide(240, 90, 0.8)), 0.0, 0.8)
        for i, at in enumerate((0.4, 0.75, 1.0, 1.5, 1.7)):
            place(x, tap(g, [200 - 15 * i, 470, 980], [0.07, 0.04, 0.02], 0.8, click=0.9), at, 0.7)
            place(x, thump(g, 120, 60, 0.07, 0.3), at, 0.4)
        place(x, creak(g, 1.2, 25, 100, WOOD, 0.6), 0.2)
        return x

    @classmethod
    def move(cls, p, v, g):
        x = buf(1.3)
        place(x, creak(g, 0.9 + 0.1 * v, 30, 140, WOOD, 0.8), 0.0)
        place(x, creak(g, 0.6, 50, 190, ROPE, 0.6), 0.3)
        n = _n(1.0)
        place(x, unit(noise(g, n, [bq_bandpass(900, 1.5)])) * env_swell(n, 0.5, 1.5, 0.3) * 0.25, 0.1)
        return x


class Reach:
    """The Undertow's Reach: a colossal limb of the storm, black water and spawn reaching over the seawall."""

    @classmethod
    def groan(cls, g, dur, f0):
        return throat(g, dur, f0, [(220, 80, 1.0), (520, 120, 0.5), (1100, 200, 0.15)], rough=0.5, sub=0.6,
                      breath=0.7, attack=dur * 0.25, release=dur * 0.4, kmax_hz=4000)

    @classmethod
    def idle(cls, p, v, g):
        x = buf(2.6)
        n = _n(2.4)
        place(x, roar(g, 2.4, 700, 3.0) * env_swell(n, 1.0, 1.5, 0.8), 0.0, 0.6)
        place(x, cls.groan(g, 2.0, wobble(40, 0.05, 0.7, g)), 0.2, 0.6)
        place(x, rain(g, 2.4, 0.15), 0.0)
        return x

    @classmethod
    def attack(cls, p, v, g):
        x = buf(2.2)
        n = _n(0.8)
        lift = muffle(noise(g, n, [bq_highpass(60, 0.7)]), 300.0, 2500.0, 0.0, 0.7) * env_swell(n, 0.75, 2.0, 0.1)
        place(x, unit(lift), 0.0, 0.7)
        crash = burst(g, 1.2, [bq_highpass(80, 0.7), bq_lowpass(6000, 0.7)], 0.005, 0.35)
        place(x, crash, 0.75 + 0.03 * v, 0.9)
        place(x, thump(g, 80, 40, 0.2, 0.5, sec=0.8), 0.75 + 0.03 * v, 0.8)
        place(x, cls.groan(g, 1.0, contour(38, 58 + 4 * v, 35, 0.6)), 0.1, 0.7)
        return x

    @classmethod
    def hurt(cls, p, v, g):
        x = buf(1.5)
        place(x, roar(g, 0.9, 1400, 14.0) * np.exp(-_t(_n(0.9)) / 0.3), 0.0, 0.7)
        place(x, gurgle(g, 0.8, 120, 4.0, 9.0, 0.6), 0.05)
        place(x, cls.groan(g, 0.8, glide(62 + 5 * v, 40)), 0.05, 0.8)
        return x

    @classmethod
    def death(cls, p, v, g):
        x = buf(4.6)
        n = _n(4.0)
        place(x, muffle(roar(g, 4.0, 3000, 2.0), 3000.0, 250.0, 0.2, 3.5) * np.exp(-_t(n) / 1.8), 0.0, 0.8)
        place(x, cls.groan(g, 3.4, glide(55, 26, 0.7)), 0.1, 0.8)
        place(x, bubble_train(g, 20, 5.0, 10.0, (0.06, 0.14), amp=0.4, fade=0.8), 1.5)
        return x

    @classmethod
    def move(cls, p, v, g):
        n = _n(1.6)
        x = roar(g, 1.6, 900 + 100 * v, 4.0) * env_swell(n, 0.7, 1.5, 0.5)
        return x + slosh(g, 1.6, 0.6, hz=1.2)


class Matron:
    """The Cinder Matron: a magma-crusted temple guardian construct. Stone grinds, the crust ticks as it cools,
    the magma under it bubbles and roars."""

    STONE = [420, 980, 1700, 2900], [0.03, 0.02, 0.012, 0.008]

    @classmethod
    def magma(cls, g, sec, amp):
        x = buf(sec)
        tt = 0.0
        while tt < sec:
            gain = float(g.uniform(0.3, 1))
            place(x, pop(g, float(g.uniform(110, 190)), float(g.uniform(0.08, 0.15)), 1.4), tt, gain)
            tt += float(g.exponential(0.12))
        return amp * x + amp * 0.5 * roar(g, sec, 900, 8.0)

    @classmethod
    def idle(cls, p, v, g):
        x = buf(2.0)
        place(x, cls.magma(g, 1.8, 0.6), 0.0)
        for _ in range(5):
            place(x, tap(g, cls.STONE[0], cls.STONE[1], 0.3, 0.6), float(g.uniform(0.1, 1.7)))
        place(x, creak(g, 0.7, 20, 70, [(260, 1.0), (520, 0.6), (900, 0.3)], 0.5), 0.6)
        return x

    @classmethod
    def attack(cls, p, v, g):
        x = buf(1.8)
        place(x, creak(g, 0.6, 25, 90 + 10 * v, [(240, 1.0), (500, 0.6), (880, 0.3)], 0.8), 0.0)
        n = _n(0.6)
        whoosh = muffle(roar(g, 0.6, 3000, 12), 600.0, 3500.0, 0.0, 0.5) * env_swell(n, 0.5, 2.0, 0.1)
        place(x, whoosh, 0.25, 0.7)
        at = 0.8 + 0.04 * v
        place(x, thump(g, 110, 48, 0.15, 0.6, sec=0.7), at, 1.0)
        place(x, tap(g, cls.STONE[0], [d * 2 for d in cls.STONE[1]], 0.8, 1.0), at, 0.6)
        place(x, crackle(g, 0.4, 300, 2200, tau=0.15), at, 0.4)
        return x

    @classmethod
    def hurt(cls, p, v, g):
        x = buf(1.2)
        place(x, tap(g, [f * (1 - 0.05 * v) for f in cls.STONE[0]], [d * 1.5 for d in cls.STONE[1]], 1.0, 1.0), 0.0)
        place(x, thump(g, 120, 55, 0.12, 0.5, sec=0.6), 0.0, 0.8)
        place(x, crackle(g, 0.25, 900, 2200, tau=0.08), 0.0, 0.35)
        n = _n(0.8)
        place(x, unit(noise(g, n, [bq_bandpass(3000, 0.8), bq_lowpass(6000, 0.7)])) * env_swell(n, 0.05, 1.0, 0.3),
              0.04, 0.12)  # steam
        place(x, cls.magma(g, 0.6, 0.4), 0.05)
        return x

    @classmethod
    def death(cls, p, v, g):
        x = buf(4.0)
        for i in range(26):  # the crust coming down in pieces
            at = 0.1 + 2.4 * (i / 26) ** 1.4 + float(g.uniform(-0.04, 0.04))
            place(x, tap(g, [f * float(g.uniform(0.6, 1.1)) for f in cls.STONE[0]], cls.STONE[1], 1 - 0.6 * i / 26,
                         0.8), at, 0.5)
        place(x, thump(g, 90, 40, 0.3, 0.6, sec=1.2), 0.15, 0.8)
        n = _n(3.2)
        place(x, unit(noise(g, n, [bq_bandpass(2600, 0.8), bq_lowpass(5500, 0.7)])) * env_swell(n, 0.4, 1.0, 1.2),
              0.3, 0.12)  # quenched
        place(x, cls.magma(g, 2.5, 0.5) * np.linspace(1, 0, _n(2.5)), 0.0)
        place(x, creak(g, 1.6, 15, 50, [(200, 1.0), (420, 0.5)], 0.6), 0.5)
        return x

    @classmethod
    def move(cls, p, v, g):
        x = buf(1.5)
        place(x, creak(g, 1.1, 18 + 4 * v, 70, [(230, 1.0), (480, 0.6), (850, 0.3)], 0.7), 0.0)
        for at in (0.2, 0.85):
            place(x, thump(g, 95, 45, 0.12, 0.5, sec=0.5), at + 0.03 * v, 0.9)
        place(x, cls.magma(g, 1.3, 0.25), 0.1)
        return x


class Tortoise:
    """The slag tortoise: a terrace tortoise under a shell of cooled slag. A slow hiss, a horny beak."""

    SLAG = [900, 1900, 3300], [0.012, 0.008, 0.005]

    @staticmethod
    def hiss(g, sec, amp=1.0):
        n = _n(sec)
        return amp * unit(noise(g, n, [bq_bandpass(3400, 1.0), bq_peak(5200, 4.0, 1.5)])) * env_swell(
            n, sec * 0.3, 1.2, sec * 0.3)

    @classmethod
    def idle(cls, p, v, g):
        x = buf(1.8)
        place(x, cls.hiss(g, 1.0, 0.5), 0.1)
        place(x, throat(g, 0.9, wobble(85, 0.03, 1.0, g), [(450, 140, 1.0), (1100, 250, 0.3)], rough=0.3,
                        breath=0.8, attack=0.3, release=0.3), 0.2, 0.4)
        for _ in range(4):
            place(x, tap(g, cls.SLAG[0], cls.SLAG[1], 0.35, 0.5), float(g.uniform(0.2, 1.5)))
        return x

    @classmethod
    def attack(cls, p, v, g):
        x = buf(1.0)
        place(x, cls.hiss(g, 0.35, 0.6), 0.0)
        at = 0.3 + 0.03 * v
        place(x, tap(g, [1100, 2200, 3600], [0.008, 0.005, 0.003], 1.0, 1.0), at)  # the beak
        place(x, thump(g, 140, 70, 0.06, 0.5), at, 0.8)
        place(x, train(g, 0.2, 30, 20, cls.SLAG[0], cls.SLAG[1], 0.4), at + 0.02, 0.4)
        return x

    @classmethod
    def hurt(cls, p, v, g):
        x = buf(0.9)
        place(x, tap(g, [f * (0.8 - 0.05 * v) for f in cls.SLAG[0]], [d * 2 for d in cls.SLAG[1]], 1.0, 0.9), 0.0)
        place(x, cls.hiss(g, 0.45 + 0.05 * v, 0.45), 0.02)
        place(x, thump(g, 130, 65, 0.06, 0.4), 0.0, 0.6)
        place(x, crackle(g, 0.12, 500, 2000, tau=0.05), 0.0, 0.4)
        return x

    @classmethod
    def death(cls, p, v, g):
        x = buf(2.8)
        place(x, cls.hiss(g, 1.8, 0.6) * np.linspace(1, 0.3, _n(1.8)), 0.0)
        place(x, throat(g, 1.6, glide(90, 50), [(430, 130, 1.0), (1000, 220, 0.3)], rough=0.4, breath=1.0,
                        attack=0.1, release=0.6), 0.1, 0.5)
        place(x, thump(g, 100, 50, 0.12, 0.5, sec=0.6), 1.9, 0.8)
        place(x, train(g, 0.4, 25, 8, cls.SLAG[0], cls.SLAG[1], 0.2), 1.92, 0.5)
        return x

    @classmethod
    def move(cls, p, v, g):
        x = buf(1.4)
        for i, at in enumerate((0.05, 0.6)):
            place(x, thump(g, 120, 60, 0.07, 0.6), at + 0.04 * v, 0.9)
            place(x, train(g, 0.15, 30, 20, cls.SLAG[0], cls.SLAG[1], 0.4), at + 0.01, 0.5)
            place(x, burst(g, 0.12, [bq_bandpass(2400, 0.8)], 0.01, 0.04), at, 0.2)
        return x


class Sparker:
    """The vein sparker: a lean terrace lizard that soaks the copper veins' charge into its coiled tail and spits
    it out as lightning."""

    @staticmethod
    def zap(g, sec, amp=1.0, buzz=110.0):
        n = _n(sec)
        t = _t(n)
        arcs = crackle(g, sec, 2200, 3500, 0.7)
        hum = np.sign(np.sin(2 * np.pi * buzz * t)) * (smooth_noise(n, 40, g) > 0.1)
        hum = filt(hum, [bq_bandpass(buzz * 6, 1.2)])
        return amp * (arcs + 0.5 * unit(hum)) * env_swell(n, 0.01, 1.0, sec * 0.4)

    @staticmethod
    def hiss(g, sec, amp=1.0):
        n = _n(sec)
        return amp * unit(noise(g, n, [bq_bandpass(4200, 1.2)])) * env_swell(n, 0.03, 1.0, sec * 0.35)

    @classmethod
    def idle(cls, p, v, g):
        x = buf(1.4)
        for at in (0.1, 0.55, 0.9):
            place(x, cls.zap(g, 0.12, 0.4), at)
        place(x, cls.hiss(g, 0.4, 0.4), 0.3)
        place(x, Sparker.move(p, 7, g)[: _n(0.4)], 0.8, 0.5)
        return x

    @classmethod
    def attack(cls, p, v, g):
        x = buf(1.0)
        place(x, cls.hiss(g, 0.25, 0.6), 0.0)
        place(x, tap(g, [1500, 2900, 4600], [0.005, 0.003, 0.002], 1.0, 1.0), 0.22 + 0.02 * v)
        place(x, cls.zap(g, 0.35, 0.9, 110 + 15 * v), 0.24 + 0.02 * v)
        return x

    @classmethod
    def hurt(cls, p, v, g):
        x = buf(0.8)
        place(x, cls.hiss(g, 0.3 + 0.05 * v, 1.0), 0.0)
        place(x, cls.zap(g, 0.25, 0.6), 0.05)
        return x

    @classmethod
    def death(cls, p, v, g):
        x = buf(2.0)
        place(x, cls.zap(g, 1.4, 0.8, 90) * np.linspace(1, 0, _n(1.4)) ** 2, 0.0)
        place(x, cls.hiss(g, 0.9, 0.6), 0.05)
        place(x, thump(g, 160, 80, 0.04, 0.4), 1.2, 0.5)
        return x

    @staticmethod
    def move(p, v, g):
        x = buf(0.9)
        tt = 0.0
        while tt < 0.75:
            place(x, tap(g, [2100, 3600, 5400], [0.003, 0.002, 0.0015], float(g.uniform(0.4, 1.0)), 0.2), tt)
            tt += float(g.uniform(0.045, 0.075)) * (1 + 0.05 * v)
        return filt(x, [bq_lowpass(6500, 0.7)])  # claws on stone, not clicks: no inter-sample overs


class Swarm:
    """The glassfry: a shoal of finger-long glass shrimp drawn to lamp light, a loose cloud that tightens to strike.
    Many tiny glassy ticks; their density is the cloud's."""

    @staticmethod
    def cloud(g, sec, rate0, rate1, amp0=1.0, amp1=1.0, f_lo=4200.0, f_hi=7800.0):
        x = buf(sec + 0.1)
        tt = 0.0
        while tt < sec:
            u = tt / sec
            f = float(np.exp(g.uniform(np.log(f_lo), np.log(f_hi))))
            a = (amp0 + (amp1 - amp0) * u) * float(g.uniform(0.3, 1.0))
            place(x, glass_ring(g, f, float(g.uniform(0.03, 0.07)), a), tt)
            tt += float(g.exponential(1.0 / (rate0 + (rate1 - rate0) * u)))
        return x

    @classmethod
    def water(cls, g, sec, amp):
        n = _n(sec)
        return amp * unit(noise(g, n, [bq_bandpass(800, 0.7)])) * env_swell(n, sec * 0.4, 1.5, sec * 0.3)

    @classmethod
    def idle(cls, p, v, g):
        return cls.cloud(g, 1.3, 25, 25, 0.6, 0.6) + np.pad(cls.water(g, 1.3, 0.15), (0, _n(0.1)))

    @classmethod
    def attack(cls, p, v, g):
        x = buf(1.0)
        place(x, cls.cloud(g, 0.5, 30, 220 + 30 * v, 0.5, 1.0), 0.0)
        n = _n(0.5)
        rush = muffle(noise(g, n, [bq_highpass(200, 0.7)]), 500.0, 2400.0, 0.0, 0.45) * env_swell(n, 0.45, 2.0, 0.05)
        place(x, unit(rush), 0.05, 0.5)
        place(x, cls.cloud(g, 0.08, 400, 400, 1.0, 1.0, 3000, 6000), 0.5, 0.9)
        return x

    @classmethod
    def hurt(cls, p, v, g):
        x = cls.cloud(g, 0.5, 300, 20, 1.0, 0.3, 3600 - 300 * v, 8000)
        place(x, burst(g, 0.2, [bq_bandpass(1200, 0.7)], 0.003, 0.05), 0.0, 0.4)
        return x

    @classmethod
    def death(cls, p, v, g):
        x = cls.cloud(g, 2.0, 120, 3, 1.0, 0.1)
        place(x, cls.water(g, 1.8, 0.2), 0.0)
        return x

    @classmethod
    def move(cls, p, v, g):
        x = cls.cloud(g, 0.9, 60 + 10 * v, 60, 0.6, 0.6)
        place(x, cls.water(g, 0.9, 0.3), 0.0)
        return x


class Skipper:
    """The shoal skipper: a mudskipper grown to a dog's size, salt-crusted, hopping the flats. A wet gulp of a voice."""

    @staticmethod
    def gulp(g, dur, f0, amp=1.0):
        return amp * throat(g, dur, f0, [(600, 180, 1.0), (1400, 300, 0.4)], rough=0.5, sub=0.3, breath=0.3,
                            attack=0.01, release=0.04)

    @staticmethod
    def splat(g, amp=1.0):
        x = buf(0.4)
        place(x, burst(g, 0.15, [bq_lowpass(1300, 0.7)], 0.002, 0.03), 0.0, 1.0)
        place(x, thump(g, 150, 85, 0.04, 0.4, sec=0.3), 0.0, 0.8)
        place(x, pop(g, float(g.uniform(260, 360)), 0.05), 0.02, 0.5)
        return amp * x

    @classmethod
    def idle(cls, p, v, g):
        x = buf(1.2)
        place(x, cls.gulp(g, 0.12, glide(150, 120)), 0.05, 0.8)
        place(x, cls.gulp(g, 0.1, glide(165, 130)), 0.35, 0.6)
        place(x, gurgle(g, 0.8, 20, 3.0, 5.0, 0.4), 0.3)
        return x

    @classmethod
    def attack(cls, p, v, g):
        x = buf(0.9)
        place(x, cls.splat(g, 0.6), 0.0)
        place(x, cls.splat(g, 1.0), 0.28 + 0.02 * v)
        place(x, tap(g, [1300, 2500], [0.005, 0.003], 0.8, 1.0), 0.3 + 0.02 * v)
        place(x, cls.gulp(g, 0.15, glide(180 + 10 * v, 140)), 0.3, 0.6)
        return x

    @classmethod
    def hurt(cls, p, v, g):
        x = buf(0.7)
        place(x, cls.gulp(g, 0.2, contour(220, 300 + 20 * v, 180, 0.3)), 0.0, 1.0)
        place(x, cls.splat(g, 0.6), 0.02)
        return x

    @classmethod
    def death(cls, p, v, g):
        x = buf(2.2)
        place(x, cls.gulp(g, 0.5, glide(160, 90)), 0.0, 0.9)
        for i, at in enumerate((0.45, 0.85, 1.35)):
            place(x, cls.splat(g, 0.7 * 0.7 ** i), at)
        place(x, gurgle(g, 1.0, 25, 3.0, 6.0, 0.4), 0.6)
        return x

    @classmethod
    def move(cls, p, v, g):
        x = buf(1.2)
        for i, at in enumerate((0.0, 0.32, 0.62)):
            place(x, cls.splat(g, float(g.uniform(0.6, 1.0))), at + 0.03 * v * i)
        return x


class Hound:
    """The raid hound: the Order raid's lean coursing dog in a branded leather harness."""

    F = [(520, 160, 1.0), (1350, 260, 0.6), (2500, 420, 0.25)]

    @classmethod
    def bark(cls, g, f0, dur=0.16):
        return throat(g, dur, glide(f0, f0 * 0.75), cls.F, rough=0.5, sub=0.25, breath=0.35, attack=0.005,
                      release=0.05)

    @classmethod
    def growl(cls, g, dur, f0):
        return throat(g, dur, wobble(f0, 0.05, 3.0, g), [(450, 140, 1.0), (1100, 220, 0.5)], rough=0.9, sub=0.8,
                      breath=0.5, attack=0.08, release=0.15, rough_hz=28.0)

    @staticmethod
    def jingle(g, amp=1.0):
        x = buf(0.3)
        for i in range(3):
            place(x, tap(g, [3100, 4700, 6900], [0.03, 0.02, 0.012], float(g.uniform(0.4, 1.0)), 0.2),
                  0.02 * i + float(g.uniform(0, 0.01)))
        return amp * x

    @classmethod
    def idle(cls, p, v, g):
        x = buf(1.4)
        place(x, cls.growl(g, 1.1, 95), 0.05, 0.9)
        place(x, cls.jingle(g, 0.25), 0.6)
        return x

    @classmethod
    def attack(cls, p, v, g):
        x = buf(1.0)
        place(x, cls.growl(g, 0.3, 110), 0.0, 0.6)
        place(x, cls.bark(g, 420 + 30 * v), 0.25, 1.0)
        place(x, tap(g, [1400, 2700, 4100], [0.006, 0.004, 0.003], 0.6, 1.0), 0.45)  # teeth meeting
        place(x, Hound.move(p, 5, g)[: _n(0.4)], 0.0, 0.5)
        return x

    @classmethod
    def hurt(cls, p, v, g):
        x = buf(0.8)
        place(x, throat(g, 0.22 + 0.04 * v, contour(800, 1250 + 80 * v, 700, 0.25), cls.F, rough=0.3, breath=0.3,
                        attack=0.005, release=0.05), 0.0, 1.0)
        place(x, cls.jingle(g, 0.4), 0.02)
        return x

    @classmethod
    def death(cls, p, v, g):
        x = buf(2.4)
        place(x, throat(g, 1.6, lambda u: 950 * (1 - 0.35 * u) * (1 + 0.04 * np.sin(2 * np.pi * 5 * u)), cls.F,
                        rough=0.15, breath=0.6, attack=0.05, release=0.7), 0.0, 0.8)
        place(x, thump(g, 110, 60, 0.08, 0.5), 1.3, 0.6)
        place(x, cls.jingle(g, 0.5), 1.31)
        return x

    @staticmethod
    def move(p, v, g):
        x = buf(1.0)
        tt = 0.0
        while tt < 0.85:  # a trot on deck boards: four pads a stride
            for j in range(4):
                place(x, thump(g, 220, 130, 0.015, 0.6, sec=0.08), tt + j * 0.06 + float(g.uniform(0, 0.01)),
                      float(g.uniform(0.4, 0.8)))
                place(x, tap(g, [1800, 2900], [0.003, 0.002], 0.25, 0.3), tt + j * 0.06)  # claws
            place(x, Hound.jingle(g, 0.25), tt)
            tt += 0.32 * (1 + 0.05 * v)
        return x


FAMILIES = {"crab": Crab, "eel": Eel, "bird": Bird, "moth": Moth, "polyp": Polyp, "leech": Leech, "bell": Bell,
            "wraith": Wraith, "reach": Reach, "matron": Matron, "tortoise": Tortoise, "sparker": Sparker,
            "swarm": Swarm, "skipper": Skipper, "hound": Hound}


# --------------------------------------------------------------------------- the set


def counts(cid: str) -> dict[str, int]:
    if cid in SLICE:
        return {"idle": 1, "attack": 2, "hurt": 3, "death": 1, "move": 3}
    return {"idle": 1, "attack": 2, "hurt": 2, "death": 1, "move": 2}


def target(event: str) -> float:
    return {"idle": IDLE, "move": MOVE}.get(event, VOICE)


def build() -> dict:
    """{file stem: (callable, target)} for every file, in a fixed order."""
    out: dict = {}
    for ci, (cid, p) in enumerate(CREATURES.items()):
        fam = FAMILIES[p["family"]]
        for ei, (event, count) in enumerate(counts(cid).items()):
            word = MOVE_WORD[p["family"]] if event == "move" else event
            for v in range(count):
                seed = SEED + 1000 * ci + 100 * ei + v

                def fn(fam=fam, event=event, p=p, v=v, seed=seed) -> np.ndarray:
                    g = rng(seed)
                    x = getattr(fam, event)(p, v, g)
                    big = p["size"] >= 2.0
                    return room(x, seed + 7, mix=0.16 if big else 0.1, tail=0.6 if big else 0.3,
                                rt60=1.2 if big else 0.7)

                out[f"{cid}_{word}_{v + 1}"] = (fn, target(event))
    return out


SFX = build()
FILES = [name + ".ogg" for name in SFX]


def render(out_dir: str = OUT_DIR, verbose: bool = True, only: str = "") -> dict:
    os.makedirs(out_dir, exist_ok=True)
    res = {}
    for name, (fn, tgt) in SFX.items():
        if only and only not in name:
            continue
        x = finish(fn(), tgt)
        write_ogg(os.path.join(out_dir, name + ".ogg"), x, quality=QUALITY)
        m = measure(x)
        res[name] = m
        if verbose:
            print(f"{name}: {m['seconds']:.2f}s  Mmax {m['momentary_max_lufs']:.2f}  "
                  f"peak {m['sample_peak_dbfs']:.2f}", flush=True)
    return res


if __name__ == "__main__":
    render(only=sys.argv[1] if len(sys.argv) > 1 else "")
