"""Reefball's sounds (M3-AUD-06; SPEC §6.10, story N-12: the arena is a water sphere hung over the drop, the ball is a
woven float, and a score brings it up through the ring at the surface; Ch7's Tidecup opens with the naming rite).

All synthesized here and in tools/audio/synth/ (SPEC §2, §9: no samples, no recordings, no generated audio). The
crowd is many independent formant voices (synth/voice.py `sing`: vowels and nasals only, no consonants, everything
above ~2.5 kHz rolled off and far back), so it reads as people and never as words. The whistle is an original reed
pipe (an additive reed tone with a breath edge), not a sports whistle: no pea, no trill, and no brand's sound.

assets/audio/sfx/reefball/ (mono -18 LUFS momentary max unless noted; peaks <= -1.5 dBFS; Vorbis q4):
    ball_kick_1..3     a foot on the woven float under water: the float's dull thump, the weave's crunch, the
                       water it shoves, bubbles shaken out of the weave
    ball_push_1..2     a head or shoulder push: a longer, softer contact and more water moved
    ball_catch_1..2    hands closing on the float: two palm slaps and the fibre creaking under the grip
    ball_shot_1..2     a hard shot: a heavy strike, a pressure whomp, a cavitating rush and a bubble trail
    ball_score         the ball brought up: its bubble trail rising, the surface breaking, and the ring's soft bronze
    sphere_enter       a player diving into the sphere: the splash in the air, the muffle closing, the sphere's
                       whole volume sloshing
    sphere_exit        breaking out of the sphere's skin: bubbles, the muffle opening, the sheet of water, drops
    sphere_swim_1..3   swimming strokes inside the sphere (-20 LUFS momentary max)
    crowd_murmur       stereo seamless 36 s loop, -26 LUFS integrated (<= -6 dBFS): the stands before play, ~56 far
                       talkers and a babble floor (Ambience bus)
    crowd_excited      stereo seamless 36 s loop, -23 LUFS integrated: ~80 talkers pitched up and pushed, swelling
                       with play, scattered calls and claps (Ambience bus; 3 LU over the murmur so a crossfade rises)
    crowd_cheer_1..2   stereo: the stands erupt (a score)
    crowd_groan        stereo: a falling groan (a miss)
    crowd_gasp         stereo: a sharp collective intake of breath (a near thing), then talk starting up again
    whistle_start      the reed pipe's call: a held note stepping up a fourth (-17 LUFS momentary max)
    whistle_short      one short note: play stops (-17)
    whistle_end        three falling notes, the last held: the match is over (-17)
    naming_rite        stereo, 12 s: the stands talking; one low bell; the talk thins and a hush passes along the
                       stands; only the bell is left, ringing out. The game stops the crowd bed when it plays.

Render:  python3 assets_src/sfx/reefball_sfx.py   (or tools/audio/render_all.py --only reefball_sfx)
"""
from __future__ import annotations

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools", "audio"))
sys.path.insert(0, HERE)

import numpy as np  # noqa: E402

from field_ambience import plfo, stereo_noise, stick_slip, upsample4  # noqa: E402
from synth.bells import tower_bell  # noqa: E402
from synth.dsp import SR, bq_bandpass, bq_highpass, bq_lowpass, bq_peak, filt, pan_mono, rng  # noqa: E402
from synth.gongs import kettle_gong  # noqa: E402
from synth.looping import LoopMixer, master_loop, write_loop_sidecar  # noqa: E402
from synth.mixer import measure, normalize_momentary, write_ogg  # noqa: E402
from synth.reverb import ModFDNReverb  # noqa: E402
from synth.voice import sing  # noqa: E402
from synth.water import drip  # noqa: E402
from underwater_sfx import (_n, _t, bubble_cloud, bubble_train, env_swell, muffle, noise, place,  # noqa: E402
                            splash_air, stroke, uw_room)

OUT_DIR = os.path.join(ROOT, "assets", "audio", "sfx", "reefball")
SEED = 20261207
SFX_TARGET, SWIM_TARGET, WHISTLE_TARGET, CEILING = -18.0, -20.0, -17.0, -1.5
BEDS = {"crowd_murmur": (36.0, -26.0), "crowd_excited": (36.0, -23.0)}
BED_CEILING, BED_QUALITY = -6.0, 1.0
VOWELS = ["a", "e", "o", "u", "i", "a", "o", "m", "n"]


def finish(x: np.ndarray, target: float = SFX_TARGET, fade_s: float = 0.06) -> np.ndarray:
    k = min(len(x) // 3, _n(fade_s))
    x = x.copy()
    x[-k:] *= (np.linspace(1, 0, k) ** 2)[:, None] if x.ndim == 2 else np.linspace(1, 0, k) ** 2
    x = filt(x, [bq_highpass(30, 0.7)])
    for _ in range(3):  # a peaky transient loses level in the limiter: go again until the target holds
        x = normalize_momentary(x, target, ceiling_db=CEILING)
    return x


def arena(x: np.ndarray, seed: int, mix: float = 0.3, tail: float = 1.6) -> np.ndarray:
    """The open arena around the stands (stereo in, stereo out, tail appended)."""
    rv = ModFDNReverb(rt60=2.2, rt60_high=0.9, predelay=0.035, size=2.0, mod_depth=7.0, mod_rate=0.3,
                      early_level=0.3, lowcut=150.0, highcut=5000.0, seed=seed)
    xs = np.concatenate([x, np.zeros((_n(tail), 2))])
    return (1 - mix) * xs + mix * rv.process(xs, tail=0.0)[: len(xs)]


# --------------------------------------------------------------------------- the ball


def thump(g: np.random.Generator, f_from: float, f_to: float, tau: float, click: float, sec: float = 0.5):
    """The float's body under a blow: a pitch-dropping low sine and a short knock."""
    n = _n(sec)
    t = _t(n)
    f = f_to + (f_from - f_to) * np.exp(-t / 0.025)
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / tau)
    k = _n(0.02)
    body[:k] += click * filt(g.standard_normal(k), [bq_lowpass(1200, 0.7)]) * np.exp(-_t(k) / 0.004)
    return body * np.minimum(1.0, t / 0.0006)


def crunch(g: np.random.Generator, sec: float, fc: float, amp: float = 1.0) -> np.ndarray:
    """The woven float's fibres crackling under the blow: dense tiny clicks through the weave's band."""
    n = _n(sec + 0.05)
    imp = np.where(g.random(n) < 3500.0 / SR, g.uniform(-1, 1, n), 0.0)
    y = filt(imp, [bq_bandpass(fc, 1.6), bq_highpass(300, 0.7)])
    return amp * y / (np.abs(y).max() + 1e-12) * np.exp(-_t(n) / sec * 3)


def ball_kick(v: int) -> np.ndarray:
    g = rng(SEED + 10 + v)
    s = (0.95, 1.0, 1.08)[v]
    n = _n(1.1)
    x = np.zeros(n)
    place(x, thump(g, 160 * s, 88 * s, 0.05, 0.6), 0.0)
    place(x, crunch(g, 0.025, 1100 * s, 0.35), 0.0)
    place(x, stroke(g, 0.8, bright=1400.0), -0.15, gain=0.6)
    place(x, bubble_cloud(g, _n(0.4), 60.0, 1.5, 3.5, env=np.exp(-_t(_n(0.4)) / 0.12), amp=0.35), 0.005)
    return finish(uw_room(filt(x, [bq_lowpass(3200, 0.6)]), SEED + 20 + v, rt60=1.1, mix=0.22, tail=0.6))


def ball_push(v: int) -> np.ndarray:
    g = rng(SEED + 30 + v)
    n = _n(1.3)
    x = np.zeros(n)
    place(x, thump(g, 118 * (1 + 0.06 * v), 72, 0.085, 0.25), 0.02)
    place(x, crunch(g, 0.04, 850, 0.18), 0.02)
    place(x, stroke(g, 1.2, bright=1200.0), -0.1, gain=0.9)
    place(x, bubble_cloud(g, _n(0.6), 50.0, 1.6, 4.5, env=np.exp(-_t(_n(0.6)) / 0.2), amp=0.35), 0.03)
    return finish(uw_room(filt(x, [bq_lowpass(2800, 0.6)]), SEED + 40 + v, rt60=1.1, mix=0.24, tail=0.6))


def ball_catch(v: int) -> np.ndarray:
    g = rng(SEED + 50 + v)
    n = _n(0.9)
    x = np.zeros(n)
    for i, at in enumerate((0.0, 0.016 + 0.006 * v)):
        slap = filt(g.standard_normal(_n(0.01)), [bq_lowpass(1900, 0.7)]) * np.exp(-_t(_n(0.01)) / 0.0025)
        place(x, 0.5 * slap, at)
        place(x, thump(g, 105, 78, 0.03, 0.1, 0.2), at, gain=0.8 - 0.25 * i)
    creak = stick_slip(g, 0.22 + 0.04 * v, 90, 300, [(950, 1.0), (1500, 0.6), (2300, 0.3)], q=7.0)
    place(x, creak, 0.04, gain=0.12)
    place(x, stroke(g, 0.6, bright=1100.0), -0.2, gain=0.35)
    return finish(uw_room(filt(x, [bq_lowpass(3000, 0.6)]), SEED + 60 + v, rt60=1.0, mix=0.2, tail=0.5))


def ball_shot(v: int) -> np.ndarray:
    g = rng(SEED + 70 + v)
    n = _n(1.6)
    t = _t(n)
    x = np.zeros(n)
    place(x, thump(g, 200 * (1 + 0.05 * v), 82, 0.045, 1.0), 0.0)
    place(x, crunch(g, 0.03, 1300, 0.55), 0.0)
    whomp = np.sin(2 * np.pi * 52 * t) * np.exp(-t / 0.14) * np.minimum(1, t / 0.004)
    x += 0.5 * whomp
    # the rush: the float tearing through the water, falling in pitch as it slows
    rush = noise(g, n, [bq_highpass(150, 0.7)])
    band = muffle(rush, 2400.0, 380.0, 0.02, 0.65)
    x += 0.45 * band * env_swell(n, 0.04, 1.0, 0.28)
    place(x, bubble_train(g, 26, 1.2, 2.6, (0.012, 0.03), amp=0.45, fade=0.8), 0.02)
    return finish(uw_room(filt(x, [bq_lowpass(3600, 0.6)]), SEED + 80 + v, rt60=1.2, mix=0.25, tail=0.6))


def ball_score() -> np.ndarray:
    g = rng(SEED + 90)
    n = _n(3.0)
    t = _t(n)
    brk = 0.55
    under = np.zeros(n)
    place(under, bubble_train(g, 20, 1.6, 3.2, (0.02, 0.035), amp=0.5), 0.0)
    place(under, stroke(g, 1.0, bright=1300.0), -0.1, gain=0.5)
    under = filt(under * (t < brk + 0.02), [bq_lowpass(1600, 0.6)])
    over = np.zeros(n)
    spray = noise(g, n, [bq_highpass(600, 0.7), bq_lowpass(9000, 0.7)])
    over += 0.5 * spray * (t >= brk) * np.exp(-np.maximum(t - brk, 0) / 0.18)
    for _ in range(10):
        place(over, drip(float(g.uniform(0.3, 0.8)), float(g.uniform(1.6, 3.5)), seed=int(g.integers(1 << 30))),
              brk + 0.05 + float(g.uniform(0, 1.3)), gain=2.0)
    ring = kettle_gong(79.0, vel=0.5, seed=SEED + 91, t60=2.2)
    place(over, ring, brk + 0.03, gain=0.35)
    x = under + muffle(over, 1600.0, 11000.0, brk - 0.02, brk + 0.1)
    st = np.stack([x, x], 1)
    return finish(arena(st, SEED + 92, mix=0.18, tail=0.8)[:, 0], fade_s=0.4)


# --------------------------------------------------------------------------- the sphere's water


def slosh(g: np.random.Generator, n: int, at: float, hz: float = 2.4) -> np.ndarray:
    """The whole sphere wobbling after a body goes through its skin: a low surge that swings and dies."""
    t = _t(n)
    d = np.maximum(t - at, 0)
    e = (t >= at) * np.clip(d / 0.08, 0, 1) * np.exp(-d / 0.7) * (0.6 + 0.4 * np.cos(2 * np.pi * hz * d))
    return noise(g, n, [bq_lowpass(200, 0.7), bq_highpass(30, 0.7)]) * e


def sphere_enter() -> np.ndarray:
    g = rng(SEED + 100)
    n = _n(3.0)
    t = _t(n)
    x = np.zeros(n)
    place(x, splash_air(g, 1.15), 0.0)
    env = np.clip((t - 0.08) / 0.05, 0, 1) * np.exp(-np.maximum(t - 0.13, 0) / 0.4)
    x += bubble_cloud(g, n, 380.0, 1.4, 6.5, env=env, amp=0.45)
    x += 0.55 * slosh(g, n, 0.12)
    x = muffle(x, 11000.0, 1400.0, 0.13, 0.42)
    return finish(uw_room(x, SEED + 101, rt60=1.3, mix=0.3), fade_s=0.4)


def sphere_exit() -> np.ndarray:
    g = rng(SEED + 110)
    n = _n(3.0)
    t = _t(n)
    brk = 0.5
    under = np.zeros(n)
    place(under, stroke(g, 1.3, bright=1400.0), -0.15, gain=0.9)
    under += bubble_cloud(g, n, 150.0, 1.6, 5.0, env=np.clip(t / 0.25, 0, 1) * (t < brk) + 1e-3, amp=0.4) * (t < brk)
    under = filt(uw_room(under, SEED + 111, mix=0.3, tail=0.0)[:n], [bq_lowpass(1500, 0.6)])
    over = np.zeros(n)
    sheet = noise(g, n, [bq_highpass(700, 0.7), bq_lowpass(8500, 0.7)])
    over += 0.55 * sheet * (t >= brk) * np.clip((t - brk) / 0.02, 0, 1) * np.exp(-np.maximum(t - brk, 0) / 0.3)
    over += 0.35 * slosh(g, n, brk, 2.1)
    for i in range(12):  # drops falling away below the sphere: later ones farther and fainter
        at = brk + 0.1 + float(g.uniform(0, 1.8))
        place(over, drip(float(g.uniform(0.3, 0.8)), float(g.uniform(1.8, 4.0)), seed=int(g.integers(1 << 30))), at,
              gain=2.0 * np.exp(-(at - brk) / 1.2))
    x = under + muffle(over, 1600.0, 12000.0, brk - 0.02, brk + 0.1)
    st = np.stack([x, x], 1)
    return finish(arena(st, SEED + 112, mix=0.15, tail=0.6)[:, 0], fade_s=0.3)


def sphere_swim(v: int) -> np.ndarray:
    g = rng(SEED + 120 + v)
    n = _n(1.6)
    x = np.zeros(n)
    place(x, stroke(g, (1.2, 1.3, 1.15)[v], bright=1700.0), 0.0)
    for j in range(2):  # the legs' flutter under the pull
        place(x, stroke(g, 0.5, bright=1200.0), 0.12 + 0.22 * j + float(g.uniform(0, 0.05)), gain=0.4)
    return finish(uw_room(x, SEED + 130 + v, rt60=1.2, mix=0.28, tail=0.5), target=SWIM_TARGET, fade_s=0.2)


# --------------------------------------------------------------------------- the crowd


def phrase(g: np.random.Generator, high: bool, excited: bool) -> np.ndarray:
    """One person in the stands talking: vowel and nasal syllables on a speech contour (no consonants, so no words).
    Excited talk is higher, brighter, wider in pitch and pushed harder."""
    syl = int(g.integers(4, 12))
    base = (float(g.uniform(55, 61)) if high else float(g.uniform(45, 51))) + (4.0 if excited else 0.0)
    span = 5.0 if excited else 3.0
    phon, pitch = [], []
    for i in range(syl):
        d = float(g.uniform(0.1, 0.22))
        phon.append((str(g.choice(VOWELS)), d))
        pitch.append((base + span * (0.5 - i / syl) + float(g.normal(0, 1.4 if excited else 1.0)), d))
    y = sing(phon, pitch, vel=0.9 if excited else 0.6, seed=int(g.integers(1 << 30)), sr=11025,
             scale=1.17 if high else 1.0, tilt=1.2 if excited else 1.6, breath=0.15, vib_cents=0.0,
             jitter_cents=14.0, max_f=3200.0, dec=16, release=0.12)
    return filt(upsample4(y), [bq_highpass(150, 0.7)])


def call(g: np.random.Generator, high: bool, rise: float, fall: float, dur: float, vowels=("e", "a")) -> np.ndarray:
    """A shout from one person: an open vowel whose pitch jumps up (or down), held, then let go."""
    base = float(g.uniform(57, 63)) if not high else float(g.uniform(64, 70))
    a = 0.12 * dur
    phon = [(vowels[0], a), (vowels[1], dur - a)]
    pitch = [(base, a), (base + rise, 0.35 * dur), (base + rise + fall, 0.53 * dur)]
    y = sing(phon, pitch, vel=1.0, seed=int(g.integers(1 << 30)), sr=11025, scale=1.17 if high else 1.0, tilt=1.0,
             breath=0.25, vib_cents=8.0, vib_rate=float(g.uniform(4.5, 6.0)), jitter_cents=20.0, max_f=4200.0,
             dec=16, release=0.25)
    return filt(upsample4(y), [bq_highpass(160, 0.7)])


def clap(g: np.random.Generator) -> np.ndarray:
    n = _n(0.04)
    y = filt(g.standard_normal(n), [bq_bandpass(float(g.uniform(1100, 2200)), 1.1)]) * np.exp(-_t(n) / 0.008)
    return y * np.minimum(1, _t(n) / 0.0005)


def babble(g: np.random.Generator, L: int) -> np.ndarray:
    """The crowd's floor: many more voices than are rendered one by one, as speech-shaped noise."""
    return stereo_noise(L, g, [bq_peak(500, 6.0, 1.0), bq_peak(1400, 4.0, 1.2), bq_lowpass(2200, 0.7),
                               bq_highpass(140, 0.7)], 0.35)


DIST = {"near": 2600.0, "mid": 1700.0, "far": 1000.0}


def _crowd_buses(mx, gain_db: float) -> None:
    for i, (k, fc) in enumerate(DIST.items()):
        mx.bus(k, gain_db - 3.0 * i, send=0.3 + 0.15 * i, process=lambda x, f=fc: filt(x, [bq_lowpass(f, 0.7)]))


def crowd_bed(name: str, g: np.random.Generator) -> tuple[LoopMixer, ModFDNReverb]:
    loop_s = BEDS[name][0]
    excited = name == "crowd_excited"
    mx = LoopMixer(intro_s=0.0, loop_s=loop_s, preroll_s=6.0)
    L = mx.L
    _crowd_buses(mx, 0.0)
    mx.bus("floor", -10.0 if excited else -12.0, send=0.3)
    swell = 0.5 + 0.5 * plfo(L, 0.12, g) if excited else np.ones(L)
    floor = babble(g, L) * (0.75 + 0.25 * swell)[:, None]
    mx.add("floor", floor, 0.0)
    for i in range(80 if excited else 56):
        dist = ["near", "mid", "mid", "far", "far"][int(g.integers(0, 5))]
        pan = float(g.uniform(-1, 1))
        lvl = float(g.uniform(0.4, 1.0))
        high = bool(g.random() < 0.5)
        t = float(g.uniform(0, 4.0))
        end = t + loop_s - float(g.uniform(0.3, 1.0))
        while t < end:
            p = phrase(g, high, excited)
            sw = float(swell[_n(t % loop_s) % L])
            mx.add(dist, p, t, pan=pan, gain=lvl * (0.45 + 0.55 * sw))
            t += len(p) / SR + float(g.uniform(0.25, 1.6 if not excited else 0.9))
    if excited:
        mx.bus("calls", -4.0, send=0.45, process=lambda x: filt(x, [bq_lowpass(3000, 0.7)]))
        mx.bus("claps", -18.0, send=0.4)
        for _ in range(26):
            t = float(g.uniform(0, loop_s))
            sw = float(swell[_n(t) % L])
            if g.random() > sw:
                continue
            c = call(g, bool(g.random() < 0.5), float(g.uniform(2, 6)), float(g.uniform(-4, -1)),
                     float(g.uniform(0.4, 0.9)))
            mx.add("calls", c, t, pan=float(g.uniform(-0.9, 0.9)), gain=float(g.uniform(0.3, 0.8)))
        tt = 0.0
        while tt < loop_s:
            sw = float(swell[_n(tt) % L])
            if g.random() < sw ** 2:
                mx.add("claps", clap(g), tt, pan=float(g.uniform(-1, 1)), gain=float(g.uniform(0.2, 1.0)))
            tt += float(g.exponential(1 / 14.0))
    verb = ModFDNReverb(rt60=2.2, rt60_high=0.9, predelay=0.035, size=2.0, mod_depth=7.0, mod_rate=0.3,
                        early_level=0.3, lowcut=150.0, highcut=5000.0, seed=SEED % 9973 + (2 if excited else 1))
    return mx, verb


def _stereo(n: int) -> np.ndarray:
    return np.zeros((n, 2))


def _put(buf: np.ndarray, x: np.ndarray, t: float, pan: float, gain: float, fc: float | None = None) -> None:
    if fc:
        x = filt(x, [bq_lowpass(fc, 0.7)])
    place(buf, gain * pan_mono(x, pan), t)


def crowd_cheer(v: int) -> np.ndarray:
    g = rng(SEED + 200 + v)
    n = _n(4.2)
    t = _t(n)
    buf = _stereo(n)
    for _ in range(64):
        at = abs(float(g.normal(0.08, 0.07)))
        dur = float(g.uniform(0.8, 2.2))
        c = call(g, bool(g.random() < 0.5), float(g.uniform(3, 8)), float(g.uniform(-3, 0)), dur,
                 vowels=(str(g.choice(["e", "a", "o"])), str(g.choice(["a", "o", "a"]))))
        _put(buf, c, at, float(g.uniform(-1, 1)), float(g.uniform(0.3, 1.0)), DIST[str(g.choice(list(DIST)))])
    roar = stereo_noise(n, g, [bq_peak(700, 5.0, 0.8), bq_lowpass(3000, 0.7), bq_highpass(220, 0.7)], 0.3)
    buf += 0.06 * roar * env_swell(n, 0.35, 1.2, 1.1)[:, None]
    tt = 0.3
    while tt < 3.6:
        _put(buf, clap(g), tt, float(g.uniform(-1, 1)), float(g.uniform(0.1, 0.4)) * np.exp(-(tt - 0.3) / 1.6))
        tt += float(g.exponential(1 / 45.0))
    return finish(arena(buf * np.minimum(1, t / 0.02)[:, None], SEED + 210 + v, mix=0.3), fade_s=0.8)


def crowd_groan() -> np.ndarray:
    g = rng(SEED + 220)
    n = _n(3.4)
    buf = _stereo(n)
    for _ in range(56):
        at = abs(float(g.normal(0.06, 0.06)))
        dur = float(g.uniform(1.0, 1.9))
        c = call(g, bool(g.random() < 0.5), float(g.uniform(0.5, 2.0)), -float(g.uniform(5, 8)), dur,
                 vowels=("o", "u"))
        _put(buf, c, at, float(g.uniform(-1, 1)), float(g.uniform(0.3, 1.0)), DIST[str(g.choice(list(DIST)))] * 0.8)
    roar = stereo_noise(n, g, [bq_peak(450, 5.0, 0.8), bq_lowpass(1600, 0.7), bq_highpass(160, 0.7)], 0.3)
    buf += 0.05 * roar * env_swell(n, 0.4, 1.2, 0.9)[:, None]
    return finish(arena(buf, SEED + 221, mix=0.3), fade_s=0.8)


def inhale(g: np.random.Generator, sec: float) -> np.ndarray:
    """One sharp intake of breath: unvoiced air through an open /a/ mouth, rising, cut off at the top."""
    n = _n(sec + 0.02)
    t = _t(n)
    s = float(g.uniform(0.9, 1.15))
    y = sum(w * filt(g.standard_normal(n), [bq_bandpass(f * s, 3.0)]) for f, w in ((750, 0.8), (1150, 0.6),
                                                                                   (2500, 0.5), (3400, 0.25)))
    e = np.clip(t / sec, 0, 1) ** 1.8 * (t < sec)
    return y * e


def crowd_gasp() -> np.ndarray:
    g = rng(SEED + 230)
    n = _n(2.6)
    buf = _stereo(n)
    for _ in range(50):
        at = abs(float(g.normal(0.03, 0.03)))
        _put(buf, inhale(g, float(g.uniform(0.22, 0.42))), at, float(g.uniform(-1, 1)), float(g.uniform(0.3, 1.0)),
             DIST[str(g.choice(list(DIST)))] * 1.3)
    for _ in range(12):  # then the talk starts up again
        _put(buf, phrase(g, bool(g.random() < 0.5), True), float(g.uniform(0.7, 1.3)), float(g.uniform(-1, 1)),
             float(g.uniform(0.15, 0.4)), DIST["mid"])
    return finish(arena(buf, SEED + 231, mix=0.3), fade_s=0.6)


# --------------------------------------------------------------------------- the whistle


def reed_pipe(g: np.random.Generator, notes: list[tuple[float, float]], gap: float = 0.035,
              vel: float = 0.9) -> np.ndarray:
    """An original reed pipe: odd-strong harmonics (a reed on a narrow bore), a breath edge, a scooped attack,
    tongued breaks (`gap` s) between notes and a little delayed vibrato. notes = [(hz, seconds)]."""
    notes = [(hz, d + (gap if i < len(notes) - 1 else 0.0)) for i, (hz, d) in enumerate(notes)]
    total = sum(d for _, d in notes)
    n = _n(total + 0.5)
    t = _t(n)
    f = np.full(n, notes[0][0])
    amp = np.zeros(n)
    edges = np.cumsum([0.0] + [d for _, d in notes])
    for (hz, _), a, b in zip(notes, edges[:-1], edges[1:]):
        m = (t >= a) & (t < b)
        f[m] = hz
        local = t[m] - a
        tail = b - t[m] - (gap if b < edges[-1] else 0.0)
        amp[m] = np.clip(local / 0.025, 0, 1) * np.clip(tail / 0.02, 0, 1) ** 0.7
    k = _n(0.018)
    f = np.convolve(np.pad(f, (k, k), mode="edge"), np.ones(k) / k, mode="same")[k:-k]
    scoop = 1 - 0.025 * np.exp(-t / 0.05)
    vib = 1 + 0.0035 * np.clip((t - 0.25) / 0.3, 0, 1) * np.sin(2 * np.pi * 5.6 * t)
    ph = 2 * np.pi * np.cumsum(f * scoop * vib) / SR
    tone = np.zeros(n)
    for h in range(1, 9):
        if h * f.max() > 0.45 * SR:
            break
        w = h ** -0.9 if h % 2 else 0.3 * h ** -1.3
        tone += w * np.sin(h * ph + float(g.uniform(0, 6.28)))
    tone *= 1 + 0.05 * np.sin(ph * 0.5)  # a faint reed roughness under the note
    edge = filt(g.standard_normal(n), [bq_bandpass(float(notes[0][0]) * 2.0, 1.5), bq_highpass(1200, 0.7)])
    a = np.convolve(amp, np.ones(_n(0.004)) / _n(0.004), mode="same")
    return vel * (tone + 0.04 * edge / (np.std(edge) + 1e-9)) * a


def whistle(kind: str) -> np.ndarray:
    g = rng(SEED + 300 + ["start", "short", "end"].index(kind))
    notes = {"start": [(1175.0, 0.42), (1568.0, 0.78)], "short": [(1568.0, 0.3)],
             "end": [(1568.0, 0.2), (1397.0, 0.2), (1175.0, 0.85)]}[kind]
    x = reed_pipe(g, notes)
    st = np.stack([x, x], 1)
    return finish(arena(st, SEED + 310, mix=0.22, tail=1.0)[:, 0], target=WHISTLE_TARGET, fade_s=0.5)


# --------------------------------------------------------------------------- the naming rite


def naming_rite() -> np.ndarray:
    """The stands talking; one low bell; the talk thins and a hush passes along the stands; only the bell is left."""
    g = rng(SEED + 400)
    sec = 12.0
    n = _n(sec)
    bell_at = 1.2
    buf = _stereo(n)
    for _ in range(36):
        pan = float(g.uniform(-1, 1))
        lvl = float(g.uniform(0.3, 0.8))
        high = bool(g.random() < 0.5)
        fc = DIST[str(g.choice(list(DIST)))]
        stop = bell_at + 0.4 + float(g.gamma(2.0, 0.55))
        tt = float(g.uniform(-1.5, 0.3))
        while tt < stop:
            p = phrase(g, high, False)
            keep = _n(stop - tt)
            if keep < len(p):
                p = p[:keep].copy()
                k = min(len(p), _n(0.15))
                p[-k:] *= np.linspace(1, 0, k)
            _put(buf, p, tt, pan, lvl * 0.22, fc)
            tt += len(p) / SR + float(g.uniform(0.3, 1.4))
    floor = stereo_noise(n, g, [bq_peak(500, 6.0, 1.0), bq_lowpass(1800, 0.7), bq_highpass(140, 0.7)], 0.35)
    fade = np.clip(1 - (_t(n) - bell_at - 0.6) / 2.6, 0, 1) ** 1.5
    buf += 0.012 * floor * fade[:, None]
    for _ in range(16):  # the hush: people quieting their neighbours, passing along the stands
        at = bell_at + 0.5 + float(g.gamma(2.0, 0.45))
        d = float(g.uniform(0.35, 0.9))
        m = _n(d)
        sh = filt(g.standard_normal(m), [bq_bandpass(float(g.uniform(2800, 4200)), 1.3), bq_highpass(1800, 0.7)])
        sh *= np.sin(np.pi * _t(m) / d) ** 1.5
        _put(buf, sh, at, float(g.uniform(-1, 1)), float(g.uniform(0.012, 0.03)), 6000.0)
    air = stereo_noise(n, g, [bq_lowpass(400, 0.7), bq_highpass(60, 0.7)], 0.6)
    buf += 0.0025 * air
    bell = tower_bell(40.0, vel=0.9, seed=SEED + 401, t60=10.0, dark=0.35)
    place(buf, pan_mono(bell, 0.0), bell_at, gain=0.6)
    buf = arena(buf, SEED + 402, mix=0.28, tail=0.0)[:n]
    return finish(buf, fade_s=1.6)


def float_ring_bell() -> np.ndarray:
    """The little bell at the scoring ring (M3-AUD-824; act1_ch07.md §6): the float strikes the ring, the bell swings
    twice on its bracket and rings over the arena; small and bright, above the score's splash."""
    g = rng(SEED + 95)
    n = _n(3.2)
    x = np.zeros(n)
    for k, (at, vel) in enumerate(((0.0, 0.55), (0.42, 0.35))):
        place(x, tower_bell(88.0, vel, seed=SEED + 96 + k, t60=2.4, dark=0.15), at)
    st = np.stack([x, x], 1)
    return finish(arena(st, SEED + 97, mix=0.22, tail=0.8)[:, 0], fade_s=0.4)


# --------------------------------------------------------------------------- render

ONE_SHOTS = {
    **{f"ball_kick_{v + 1}": (lambda i=v: ball_kick(i)) for v in range(3)},
    **{f"ball_push_{v + 1}": (lambda i=v: ball_push(i)) for v in range(2)},
    **{f"ball_catch_{v + 1}": (lambda i=v: ball_catch(i)) for v in range(2)},
    **{f"ball_shot_{v + 1}": (lambda i=v: ball_shot(i)) for v in range(2)},
    "ball_score": ball_score,
    "sphere_enter": sphere_enter,
    "sphere_exit": sphere_exit,
    **{f"sphere_swim_{v + 1}": (lambda i=v: sphere_swim(i)) for v in range(3)},
    "crowd_cheer_1": lambda: crowd_cheer(0),
    "crowd_cheer_2": lambda: crowd_cheer(1),
    "crowd_groan": crowd_groan,
    "crowd_gasp": crowd_gasp,
    "whistle_start": lambda: whistle("start"),
    "whistle_short": lambda: whistle("short"),
    "whistle_end": lambda: whistle("end"),
    "naming_rite": naming_rite,
    "float_ring_bell": float_ring_bell,
}


def render_bed(name: str, out_dir: str = OUT_DIR, verbose: bool = True) -> dict:
    g = rng(SEED + 101 * (list(BEDS).index(name) + 1))
    mx, verb = crowd_bed(name, g)
    _, loop = mx.render(reverb=verb, reverb_return_db=-3.0, hp_hz=60.0)
    rep: dict = {}
    _, loop = master_loop(np.zeros((0, 2)), loop, BEDS[name][1], ceiling_db=BED_CEILING, report=rep)
    L = len(loop)
    write_ogg(os.path.join(out_dir, name + ".ogg"), loop, quality=BED_QUALITY,
              tags={"LOOPSTART": "0", "LOOPLENGTH": str(L)})
    write_loop_sidecar(os.path.join(out_dir, name + ".loop.json"), SR, 0, L, None, None)
    m = measure(loop)
    if verbose:
        print(f"{name}: {m['seconds']:.2f}s  {m['integrated_lufs']:.2f} LUFS  peak {m['sample_peak_dbfs']:.2f} dBFS  "
              f"limited {100 * rep.get('fraction_limited', 0):.2f} %")
    return m


def render(out_dir: str = OUT_DIR, verbose: bool = True) -> dict:
    os.makedirs(out_dir, exist_ok=True)
    res = {}
    for name, fn in ONE_SHOTS.items():
        x = fn()
        write_ogg(os.path.join(out_dir, name + ".ogg"), x, quality=4.0)
        res[name] = measure(x)
        if verbose:
            print(f"{name}: {res[name]['seconds']:.2f}s  Mmax {res[name]['momentary_max_lufs']:.2f}  "
                  f"peak {res[name]['sample_peak_dbfs']:.2f}")
    for name in BEDS:
        res[name] = render_bed(name, out_dir, verbose)
    return res


if __name__ == "__main__":
    render()
