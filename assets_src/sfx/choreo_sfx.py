"""Battle choreography sounds (M3-AUD-13; score-as-code for SFX): the motion layer under M2-AUD-04's hits.

The battle-presentation track's BattleChoreo plays each action as beats (approach, strike, contact, recover,
return, a KO collapse; docs/kb/tech/battle_presentation.md on claude/battle-presentation). BattleVfx already plays
the element hit (battle_sfx.py) on the contact, so these are the *other* layers, listened for by
game/audio/choreo_audio.gd from game/data/audio/choreo_sfx.json:
    whoosh_<style>_<n>   the strike's swing, timed so its crest lands on the contact (PEAKS below)
    accent_<weapon>_<n>  the weapon's own touch on the contact, softer than the hit it sits on
    step_sand_<n>        footfalls on battle sand (the approach, the return, a walk-in, a step-off)
    ko_collapse_<n>      a felled fighter going down into sand and shallow water
    swell_<hero>         a short, bright accent on each Swell finisher's contact, over its own VFX sound
    toll_wave            the Drownbell's toll ring passing the party (on the toll's contact)
    flood_surge          the Flood's surge attacks (flood_surge, undertow_surge) on their contact
    flood_brace_<n>      the water against each member's legs as the party braces at the Flood
    vowbound_beckon      the caller's call; vowbound_rise(_long) Ilun's rise (the short and the first-call
                         entry), vowbound_sink his dismissal, vowbound_fall his fall (tipped back, drawn under)

Every sound is synthesized here from the tools/audio/synth library: no samples, no sample packs, no CC0 audio,
no AI generation (SPEC section 2). Original-material check: the only pitched figures (the Swell accents' dyads,
the beckon's rising fifth) are two- or three-note intervals written for this file; none quotes a melody.

Weapons (game/data/items/equipment.json gear_types; docs/kb/story/characters/kerrid.md): Rhen's twin reef-hooks
(and the brass-and-glass lantern on his shoulder), Asha's lantern staff, Toma's boarding spear and tide shield,
Ysolde's lacquer book (her casts: a focus, ink and a glint), Kerrid's anchor-cleaver (armour breaking), and the
creatures' claws and teeth, plus the Drownbell's bronze hood.

Outputs (mono, 44.1 kHz, Ogg Vorbis q4) under assets/audio/sfx/choreo/. Loudness (docs/kb/audio/mix.md section 2,
measured on the decoded file by render_all.py, rules in tools/audio/targets.py): whooshes -20 LUFS momentary max,
accents and footfalls -21 (a layer under the -18 hit), KO, toll wave, surge and the Vowbound's rise and fall -18,
the Swell accents -19. Rendered at a -2 dBFS sample-peak ceiling, so decoded true peaks stay under -1 dBTP.

Render:  python3 assets_src/sfx/choreo_sfx.py   (or tools/audio/render_all.py --only choreo_sfx)
"""
from __future__ import annotations

import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools", "audio"))

import numpy as np  # noqa: E402

from synth.dsp import (SR, bq_bandpass, bq_highpass, bq_highshelf, bq_lowpass, bq_peak, filt,  # noqa: E402
                       rng, smooth_noise)
from synth.gongs import kettle_gong  # noqa: E402
from synth.metallophone import metallophone_note  # noqa: E402
from synth.mixer import measure, normalize_momentary, write_ogg  # noqa: E402
from synth.reverb import ModFDNReverb  # noqa: E402
from synth.score import n  # noqa: E402
from synth.water import bubble, drip  # noqa: E402
from synth.winds import breath_flute  # noqa: E402

OUT_DIR = os.path.join(ROOT, "assets", "audio", "sfx")
SUB = "choreo"
SEED = 31313
WHOOSH = -20.0
LAYER = -21.0
BODY = -18.0
BRIGHT = -19.0
CEILING = -2.0
QUALITY = 4.0
# Seconds from a whoosh's start to its crest (choreo_sfx.json `peaks` must match: the listener starts each whoosh
# that much before the contact).
PEAKS = {"melee": 0.12, "heavy": 0.22, "cast": 0.30, "throw": 0.10, "guard": 0.14}


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


def _crest(N, peak_at, rise_pow=2.0, fall_tau=0.05):
    """0 -> 1 at peak_at (power curve), then an exponential fall: a swing's envelope."""
    t = _t(N)
    up = np.clip(t / peak_at, 0, 1) ** rise_pow
    down = np.where(t > peak_at, np.exp(-(t - peak_at) / fall_tau), 1.0)
    return up * down


def _sweep_band(x, f_from, f_to, q=2.0, steps=20, shape=None):
    """A band-pass gliding f_from -> f_to (crossfaded fixed bands). `shape` maps 0..1 time to 0..1 glide."""
    N = len(x)
    out = np.zeros(N)
    pos = np.linspace(0, 1, N)
    if shape is not None:
        pos = shape(pos)
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


def _room(x, rt60=0.7, mix=0.14, seed=1, high=5000.0, tail=0.0):
    """Mono in, mono out: the open-air battle room (a short modulated FDN), folded to mono."""
    wet = ModFDNReverb(rt60=rt60, rt60_high=rt60 * 0.45, predelay=0.012, size=0.6, early_level=0.2,
                       lowcut=180.0, highcut=high, seed=seed).process(np.stack([x, x], 1), tail=tail)
    wet = wet.mean(axis=1)
    dry = np.concatenate([x, np.zeros(len(wet) - len(x))])
    return (1 - mix) * dry + mix * wet


def _thump(f_from, f_to, tau, N, g, click=0.3):
    """A body impact: a pitch-dropping sine and a short low noise knock."""
    t = _t(N)
    f = f_from * (f_to / f_from) ** ((t / t[-1]) ** 0.35)
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / tau)
    k = min(N, _n(0.02))
    knock = np.zeros(N)
    knock[:k] = filt(_noise(g, k), [bq_lowpass(900, 0.7)]) * np.exp(-_t(k) / 0.004)
    return (body + click * knock) * np.minimum(1.0, t / 0.0006)


def _modes(freqs, amps, taus, N, g):
    """A struck object: a few decaying sine modes (metal, wood, shell)."""
    t = _t(N)
    out = np.zeros(N)
    for f, a, tau in zip(freqs, amps, taus):
        out += a * np.sin(2 * np.pi * f * t + g.uniform(0, 6.28)) * np.exp(-t / tau)
    return out * np.minimum(1.0, t / 0.0004)


def _burst(g, N, lo, hi, tau, attack=0.0005):
    return filt(_noise(g, N), [bq_highpass(lo, 0.7), bq_lowpass(hi, 0.7)]) * _decay(N, tau, attack)


def _bubbles(g, N, count, r_lo, r_hi, t_lo, t_hi, amp=1.0, grow=0.0):
    out = np.zeros(N)
    for _ in range(count):
        at = g.uniform(t_lo, t_hi)
        u = (at - t_lo) / max(t_hi - t_lo, 1e-6)
        r = g.uniform(r_lo, r_hi) * (1 + grow * u)
        _place(out, bubble(r, g.uniform(0.3, 1.0) * amp, rise=g.uniform(0.05, 0.15)), at)
    return out


def _grains(g, N, rate_hz, band, q=0.8, tau=0.0):
    """Sparse clicks through a band: sand grains, paper fibres, grit."""
    imp = np.zeros(N)
    cnt = max(1, int(rate_hz * N / SR))
    pos = g.integers(0, N, cnt)
    imp[pos] = g.uniform(-1, 1, cnt) * g.uniform(0.2, 1.0, cnt) ** 2
    x = filt(imp, [bq_bandpass(band, q)])
    return x * np.exp(-_t(N) / tau) if tau > 0 else x


def _glint(f, dur, g, t60=0.6, attack=0.002):
    """A glassy tone: two inharmonic partials, slightly beating."""
    N = _n(dur)
    t = _t(N)
    out = np.zeros(N)
    for r, a in ((1.0, 1.0), (2.32, 0.3)):
        b = g.uniform(0.4, 1.4)
        out += a * np.exp(-6.91 * t / (t60 / r ** 0.5)) * 0.5 * (
            np.sin(2 * np.pi * f * r * t + g.uniform(0, 6.28)) + np.sin(2 * np.pi * (f * r + b) * t))
    return out * np.clip(t / attack, 0, 1) ** 2


# --------------------------------------------------------------------------- strike whooshes


def _whoosh(g, dur, peak, f_from, f_to, q, fall_tau, body=0.0):
    N = _n(dur)
    w = _sweep_band(_noise(g, N), f_from, f_to, q=q, steps=18)
    w *= _crest(N, peak, 2.2, fall_tau) * (0.85 + 0.15 * smooth_noise(N, 40, g))
    if body:
        w += body * filt(_noise(g, N), [bq_lowpass(260, 0.7)]) * _crest(N, peak, 2.0, fall_tau * 1.3)
    return w


def whoosh_melee(v):
    """A quick swing: a band of air rising and snapping past, crest at PEAKS['melee']."""
    g = rng(SEED + 100 + v)
    w = _whoosh(g, 0.32, PEAKS["melee"], g.uniform(500, 650), g.uniform(2600, 3300), 1.7, 0.035)
    return _tail_fade(_room(w, 0.5, 0.1, SEED + 101 + v))


def whoosh_heavy(v):
    """A heavy swing (a finisher, the anchor-cleaver, the bell's hood): lower, slower, with weight under it."""
    g = rng(SEED + 200 + v)
    w = _whoosh(g, 0.5, PEAKS["heavy"], g.uniform(220, 280), g.uniform(1200, 1500), 1.3, 0.06, body=0.5)
    return _tail_fade(_room(w, 0.6, 0.12, SEED + 201 + v))


def whoosh_cast(v):
    """A cast's gather: an airy swell drawing in, a faint breath of tone at the crest, then it lets go."""
    g = rng(SEED + 300 + v)
    N = _n(0.46)
    p = PEAKS["cast"]
    w = _sweep_band(_noise(g, N), 900, 4200, q=2.4, steps=18) * _crest(N, p, 1.6, 0.05)
    t = _t(N)
    f0 = [1046.5, 1174.7][v % 2]
    tone = sum(a * np.sin(2 * np.pi * f0 * r * t) for r, a in ((1.0, 1.0), (1.5, 0.4)))
    w += 0.05 * tone * _crest(N, p, 2.5, 0.04)
    w = filt(w, [bq_highpass(300, 0.7)])
    return _tail_fade(_room(w, 0.8, 0.18, SEED + 301 + v, high=7000))


def whoosh_throw(v):
    """An item thrown or a shot let go: a short, high flick."""
    g = rng(SEED + 400 + v)
    w = _whoosh(g, 0.26, PEAKS["throw"], g.uniform(1400, 1700), g.uniform(4800, 5800), 2.2, 0.025)
    return _tail_fade(_room(w, 0.4, 0.08, SEED + 401 + v))


def whoosh_guard(v):
    """Setting a guard: cloth and leather drawn tight, a short low push of air."""
    g = rng(SEED + 500 + v)
    N = _n(0.36)
    w = _whoosh(g, 0.36, PEAKS["guard"], 300, 900, 1.1, 0.05, body=0.3)
    w += 0.5 * _grains(g, N, 900, 2400, 0.7) * _crest(N, PEAKS["guard"], 1.5, 0.06)
    return _tail_fade(_room(w, 0.4, 0.08, SEED + 501 + v))


# --------------------------------------------------------------------------- contact accents


def accent_hooks(v):
    """Rhen's twin reef-hooks: two quick bites of bright steel, the lantern's glass ticking on his shoulder."""
    g = rng(SEED + 1000 + v)
    N = _n(0.42)
    buf = np.zeros(N)
    for i, at in enumerate((0.0, g.uniform(0.028, 0.042))):
        k = _n(0.2)
        f = g.uniform(2100, 2600) * (1.0 + 0.07 * i)
        hit = _modes([f, f * 1.53, f * 2.21], [0.5, 0.3, 0.18], [0.05, 0.035, 0.02], k, g)
        hit += 0.8 * _burst(g, k, 2500, 9000, 0.006)
        _place(buf, (1.0 - 0.25 * i) * hit, at)
    _place(buf, 0.12 * _glint(g.uniform(3300, 3600), 0.3, g, t60=0.25), 0.06)
    buf = filt(buf, [bq_highpass(400, 0.7)])
    return _tail_fade(_room(buf, 0.5, 0.1, SEED + 1001 + v))


def accent_staff(v):
    """Asha's lantern staff: a hollow wooden knock, the shell-bell at its head answering softly."""
    g = rng(SEED + 1100 + v)
    N = _n(0.5)
    buf = _modes([g.uniform(620, 700), g.uniform(1500, 1650), 2900], [0.7, 0.35, 0.1], [0.035, 0.02, 0.01], N, g)
    buf += 0.4 * _thump(200, 140, 0.03, N, g, click=0.4)
    _place(buf, 0.1 * _glint(g.uniform(2500, 2700), 0.4, g, t60=0.35), 0.015)
    return _tail_fade(_room(buf, 0.5, 0.1, SEED + 1101 + v))


def accent_spear(v):
    """Toma's boarding spear: the shaft's thud through the hands and the iron point's short bite."""
    g = rng(SEED + 1200 + v)
    N = _n(0.42)
    buf = 0.8 * _thump(g.uniform(210, 240), 120, 0.05, N, g, click=0.5)
    k = _n(0.08)
    point = _modes([g.uniform(3400, 3900), 5200], [0.4, 0.2], [0.012, 0.008], k, g) + 0.6 * _burst(g, k, 3000, 9000,
                                                                                                  0.004)
    _place(buf, point, 0.0)
    _place(buf, 0.2 * _grains(g, _n(0.12), 1500, 1800, 0.8, tau=0.03), 0.01)
    return _tail_fade(_room(buf, 0.5, 0.1, SEED + 1201 + v))


def accent_shield(v):
    """Toma's tide shield set against the blow: old turtle shell, hollow and low, a scrape of its rim."""
    g = rng(SEED + 1300 + v)
    N = _n(0.5)
    buf = _modes([g.uniform(170, 190), g.uniform(410, 450), 980], [0.8, 0.45, 0.15], [0.09, 0.05, 0.02], N, g)
    buf += 0.5 * _burst(g, N, 200, 1500, 0.01)
    k = _n(0.18)
    scrape = _sweep_band(_noise(g, k), 2600, 1500, q=3.0, steps=10) * _crest(k, 0.03, 1.0, 0.05)
    _place(buf, 0.25 * scrape, 0.02)
    return _tail_fade(_room(buf, 0.5, 0.1, SEED + 1301 + v))


def accent_book(v):
    """Ysolde's lacquer book struck flat: a leather slap and the pages' flutter."""
    g = rng(SEED + 1400 + v)
    N = _n(0.36)
    buf = _burst(g, N, 150, 2200, 0.03, 0.002) + 0.3 * _thump(180, 110, 0.04, N, g, click=0.2)
    flutter = _grains(g, N, 4000, 4500, 0.7) * _crest(N, 0.04, 1.0, 0.09)
    buf += 0.6 * flutter
    return _tail_fade(_room(buf, 0.4, 0.08, SEED + 1401 + v))


def accent_focus(v):
    """Ysolde's focus released into a cast: a flick of the page and a glint where the written light goes."""
    g = rng(SEED + 1500 + v)
    N = _n(0.55)
    buf = 0.3 * _grains(g, N, 3000, 5200, 0.8, tau=0.04)
    f = [2793.8, 3135.9][v % 2]
    _place(buf, 0.35 * _glint(f, 0.5, g, t60=0.45), 0.0)
    _place(buf, 0.2 * _glint(f * 1.5, 0.4, g, t60=0.3), 0.03)
    buf = filt(buf, [bq_highpass(600, 0.7)])
    return _tail_fade(_room(buf, 0.8, 0.2, SEED + 1501 + v, high=9000))


def accent_cleaver(v):
    """Kerrid's anchor-cleaver: old anchor iron, a deep strike and the crunch of armour giving way."""
    g = rng(SEED + 1600 + v)
    N = _n(0.75)
    buf = 1.0 * _thump(g.uniform(100, 115), 48, 0.1, N, g, click=0.7)
    buf += _modes([g.uniform(680, 720), 1130, 1840, 2620], [0.3, 0.22, 0.12, 0.06], [0.2, 0.14, 0.08, 0.05], N, g)
    crunch = _grains(g, N, 1800, 2000, 0.6) * _crest(N, 0.012, 1.0, 0.06)
    buf += 0.6 * crunch + 0.25 * _grains(g, N, 400, 5000, 0.9) * _crest(N, 0.05, 1.0, 0.12)
    return _tail_fade(_room(buf, 0.7, 0.12, SEED + 1601 + v))


def accent_claw(v):
    """A creature's claws or talons: three rakes, fast and dry, high to mid."""
    g = rng(SEED + 1700 + v)
    N = _n(0.36)
    buf = np.zeros(N)
    for i in range(3):
        k = _n(0.07)
        r = _sweep_band(_noise(g, k), g.uniform(5200, 6200), g.uniform(1800, 2300), q=2.5, steps=8)
        _place(buf, (1 - 0.2 * i) * r * _crest(k, 0.008, 1.0, 0.02), 0.022 * i + g.uniform(0, 0.006))
    buf += 0.3 * _thump(160, 100, 0.02, N, g, click=0.3)
    return _tail_fade(_room(buf, 0.4, 0.08, SEED + 1701 + v))


def accent_teeth(v):
    """A bite: a hard snap of jaws and a short wet squeeze."""
    g = rng(SEED + 1800 + v)
    N = _n(0.36)
    buf = np.zeros(N)
    _place(buf, _modes([g.uniform(1800, 2200), 3700], [0.5, 0.3], [0.006, 0.004], _n(0.03), g), 0.0)
    _place(buf, 0.6 * _modes([g.uniform(1500, 1700)], [0.5], [0.005], _n(0.03), g), 0.018)
    k = _n(0.2)
    wet = filt(_noise(g, k), [bq_bandpass(g.uniform(500, 650), 2.0)]) * _crest(k, 0.03, 1.0, 0.07)
    _place(buf, 1.2 * wet, 0.02)
    _place(buf, 0.4 * _bubbles(g, k, 4, 0.9, 1.6, 0.0, 0.08, amp=0.4), 0.03)
    return _tail_fade(_room(buf, 0.4, 0.08, SEED + 1801 + v))


def accent_bell_hood(v):
    """The Drownbell's hood slammed down: dull bronze, damped at once by the water in it."""
    g = rng(SEED + 1900 + v)
    N = _n(0.7)
    f0 = g.uniform(104, 112)
    buf = _modes([f0, f0 * 2.0, f0 * 2.4, f0 * 3.0, f0 * 4.1], [0.6, 0.4, 0.3, 0.12, 0.08],
                 [0.18, 0.12, 0.1, 0.06, 0.04], N, g)
    buf += 0.7 * _thump(90, 50, 0.08, N, g, click=0.5)
    buf += 0.3 * _bubbles(g, N, 8, 2.0, 4.0, 0.03, 0.25, amp=0.3)
    buf = filt(buf, [bq_lowpass(2500, 0.7)])
    return _tail_fade(_room(buf, 0.8, 0.14, SEED + 1901 + v))


def accent_guard(v):
    """A guard set by anyone without a shield: cloth and leather pulled in, the weight settling."""
    g = rng(SEED + 2000 + v)
    N = _n(0.36)
    buf = 0.6 * _thump(140, 95, 0.035, N, g, click=0.3)
    buf += 0.4 * _grains(g, N, 1400, 2000, 0.7) * _crest(N, 0.02, 1.0, 0.06)
    return _tail_fade(_room(buf, 0.4, 0.08, SEED + 2001 + v))


# --------------------------------------------------------------------------- footfalls, the KO


def step_sand(v):
    """One footfall on the battle's sand, damp near the waterline: a soft crunch of grains and a little give."""
    g = rng(SEED + 3000 + v)
    N = _n(0.22)
    t = _t(N)
    heel = filt(_noise(g, N), [bq_lowpass(g.uniform(700, 900), 0.7)]) * _decay(N, 0.02, 0.002)
    grain = _grains(g, N, g.uniform(2500, 3500), g.uniform(2600, 3400), 0.8) * _crest(N, 0.012, 1.0, 0.04)
    squish = filt(_noise(g, N), [bq_bandpass(g.uniform(380, 460), 1.6)]) * _crest(N, 0.04, 1.2, 0.04)
    buf = 0.8 * heel + 0.6 * grain + 0.25 * squish
    buf *= np.minimum(1.0, t / 0.003)
    return _tail_fade(_room(buf, 0.3, 0.06, SEED + 3001 + v))


def ko_collapse(v):
    """A fighter goes down: the knees into sand, then the body into the shallows, the water closing round it."""
    g = rng(SEED + 3100 + v)
    N = _n(1.25)
    buf = np.zeros(N)
    k = _n(0.25)
    knees = 0.6 * _thump(120, 75, 0.04, k, g, click=0.4) + 0.3 * _grains(g, k, 2200, 2400, 0.8, tau=0.04)
    _place(buf, knees, 0.0)
    S = N - _n(0.2)
    sp = 0.9 * _thump(g.uniform(85, 100), 45, 0.1, S, g, click=0.5)
    sp += 0.5 * _burst(g, S, 400, 5000, 0.11, 0.004) * (0.7 + 0.3 * smooth_noise(S, 50, g))
    sp += 0.8 * _bubbles(g, S, 26, 1.2, 3.6, 0.0, 0.4, amp=0.22)
    for i in range(5):
        _place(sp, 0.7 * drip(g.uniform(0.25, 0.5), g.uniform(2.0, 3.5), seed=SEED + 3110 + 10 * v + i),
               0.35 + g.uniform(0, 0.5))
    _place(buf, sp, 0.2 + g.uniform(0, 0.03))
    buf = filt(buf, [bq_highshelf(6000, -4)])
    return _tail_fade(_room(buf, 0.8, 0.14, SEED + 3101 + v), 0.2)


# --------------------------------------------------------------------------- Swell accents (short and bright)


def _bright(g, notes, seed, decay=0.9, hardness=0.6, extra=None):
    N = _n(0.9)
    buf = np.zeros(N)
    for i, (note, at, vel) in enumerate(notes):
        _place(buf, metallophone_note(n(note), vel, seed=seed + i, decay=decay, hardness=hardness, ombak_hz=6.5), at)
    if extra is not None:
        buf += extra[:N] if len(extra) >= N else np.concatenate([extra, np.zeros(N - len(extra))])
    buf = filt(buf, [bq_highpass(350, 0.7)])
    return _tail_fade(_room(buf, 1.0, 0.18, seed + 50, high=9000), 0.2)


def swell_rhen():
    """Lamp Dive's landing: a bright brass glint over the splash, the lantern flaring (A5 over E6)."""
    g = rng(SEED + 4000)
    N = _n(0.9)
    clink = np.zeros(N)
    _place(clink, 0.3 * _glint(3520.0, 0.4, g, t60=0.3), 0.0)
    return _bright(g, [("A5", 0.0, 0.6), ("E6", 0.025, 0.55)], SEED + 4010, extra=clink)


def swell_asha():
    """Shallows Verse's close: three shell-bells catching the light, close together (G6, D7, A6)."""
    g = rng(SEED + 4100)
    return _bright(g, [("G6", 0.0, 0.5), ("D7", 0.05, 0.45), ("A6", 0.1, 0.4)], SEED + 4110, decay=0.7,
                   hardness=0.5)


def swell_toma():
    """Return Tide's counter: a firm, bright strike, a small gong and a fifth over it (D5, A5)."""
    g = rng(SEED + 4200)
    gong = 0.5 * kettle_gong(n("D5"), 0.6, seed=SEED + 4201, t60=0.9)
    knock = np.zeros(_n(0.9))
    _place(knock, 0.5 * _thump(180, 120, 0.03, _n(0.3), g, click=0.6), 0.0)
    _place(knock, gong, 0.0)
    return _bright(g, [("A5", 0.0, 0.55), ("E6", 0.0, 0.3)], SEED + 4210, decay=0.7, hardness=0.7, extra=knock)


def swell_ysolde():
    """Written Light's last stroke: a rising glint, a fifth (C7 to G7), the page's flick before it."""
    g = rng(SEED + 4300)
    N = _n(0.9)
    flick = np.zeros(N)
    _place(flick, 0.25 * _grains(g, _n(0.1), 3000, 5000, 0.8, tau=0.02), 0.0)
    _place(flick, 0.3 * _glint(2093.0, 0.6, g, t60=0.5), 0.0)
    _place(flick, 0.28 * _glint(3136.0, 0.6, g, t60=0.5), 0.07)
    return _bright(g, [("C7", 0.0, 0.4), ("G7", 0.07, 0.35)], SEED + 4310, decay=0.6, hardness=0.45, extra=flick)


# --------------------------------------------------------------------------- the Drownbell's set piece


def toll_wave():
    """The toll's ring passing the party: a pressure front of air and spray rising, crossing, falling away."""
    g = rng(SEED + 5000)
    N = _n(1.5)
    t = _t(N)
    front = _sweep_band(_noise(g, N), 260, 2400, q=1.4, steps=20,
                        shape=lambda u: np.clip(np.sin(np.pi * np.clip(u / 0.7, 0, 1)), 0, 1))
    env = _crest(N, 0.38, 1.6, 0.32)
    buf = 0.9 * front * env
    hum = np.sin(2 * np.pi * np.cumsum(110.0 * (1.0 - 0.06 * np.clip((t - 0.3) / 0.4, 0, 1))) / SR)
    buf += 0.25 * hum * env
    buf += 0.5 * filt(_noise(g, N), [bq_lowpass(140, 0.7)]) * _crest(N, 0.34, 2.0, 0.2)
    buf += 0.25 * _grains(g, N, 1500, 3500, 0.8) * _crest(N, 0.45, 1.5, 0.25)
    return _tail_fade(_room(buf, 1.4, 0.22, SEED + 5001), 0.3)


def flood_surge():
    """A surge attack: the sea rises and crashes over the road, bubbles growing as it goes."""
    g = rng(SEED + 5100)
    N = _n(1.3)
    rush = _sweep_band(_noise(g, N), 300, 1400, q=1.0, steps=16) * _crest(N, 0.45, 1.6, 0.3)
    buf = 0.8 * rush
    buf += 0.5 * filt(_noise(g, N), [bq_lowpass(180, 0.7)]) * _crest(N, 0.42, 2.0, 0.3)
    k = N - _n(0.42)
    crash = _burst(g, k, 500, 6500, 0.16, 0.006) * (0.7 + 0.3 * smooth_noise(k, 60, g))
    _place(buf, 0.6 * crash, 0.42)
    buf += 0.7 * _bubbles(g, N, 40, 1.0, 2.5, 0.3, 1.0, amp=0.2, grow=1.0)
    return _tail_fade(_room(buf, 1.0, 0.18, SEED + 5101), 0.25)


def flood_brace(v):
    """The water against one member's legs as they brace: a swash up the shins and back."""
    g = rng(SEED + 5200 + v)
    N = _n(0.6)
    sw = filt(_noise(g, N), [bq_bandpass(g.uniform(700, 850), 1.1)]) * _crest(N, 0.12, 1.4, 0.15)
    buf = 0.8 * sw + 0.6 * _bubbles(g, N, 12, 1.0, 2.2, 0.05, 0.4, amp=0.25)
    buf += 0.2 * filt(_noise(g, N), [bq_lowpass(220, 0.7)]) * _crest(N, 0.1, 1.5, 0.12)
    return _tail_fade(_room(buf, 0.6, 0.12, SEED + 5201 + v), 0.12)


# --------------------------------------------------------------------------- the Vowbound


def vowbound_beckon():
    """The caller's call: a breath rising a fifth (D5 to A5), and a ring of water answering at the slot."""
    g = rng(SEED + 6000)
    N = _n(1.1)
    buf = np.zeros(N)
    _place(buf, breath_flute(n("D5"), 0.32, 0.45, seed=SEED + 6001, breath=0.5, attack=0.06, release=0.12), 0.0)
    _place(buf, breath_flute(n("A5"), 0.5, 0.5, seed=SEED + 6002, breath=0.45, attack=0.05, release=0.3), 0.24)
    ring = np.zeros(N)
    for i in range(3):
        _place(ring, bubble(3.4 - 0.6 * i, 0.4 - 0.08 * i, rise=0.06), 0.3 + 0.08 * i)
    buf += 0.6 * ring
    buf = filt(buf, [bq_highpass(180, 0.7)])
    return _tail_fade(_room(buf, 1.4, 0.26, SEED + 6003, high=7000), 0.25)


def _rise(g, sec, seed):
    """Water parting upward: a stream rising in pitch, droplets falling off the shape, a low swell under it."""
    N = _n(sec + 0.4)
    t = _t(N)
    env = np.clip(t / (sec * 0.25), 0, 1) ** 1.5 * np.where(t > sec, np.exp(-(t - sec) / 0.18), 1.0)
    stream = _sweep_band(_noise(g, N), 260, 1900, q=1.6, steps=22, shape=lambda u: np.clip(u * (sec + 0.4) / sec,
                                                                                           0, 1) ** 0.8)
    buf = 0.7 * stream * env * (0.8 + 0.2 * smooth_noise(N, 18, g))
    buf += 0.4 * filt(_noise(g, N), [bq_lowpass(160, 0.7)]) * env
    count = int(10 * sec)
    for i in range(count):
        at = g.uniform(sec * 0.3, sec + 0.2)
        _place(buf, 0.5 * drip(g.uniform(0.3, 0.6), g.uniform(1.8, 3.4), seed=seed + i), at)
    return _tail_fade(_room(buf, 1.4, 0.2, seed - 1), 0.25)


def vowbound_rise():
    """Ilun rises at his slot (the call's 1.3 s entry)."""
    return _rise(rng(SEED + 6100), 1.3, SEED + 6110)


def vowbound_rise_long():
    """Ilun's first rise (the C10 summon entry, 2.6 s): slower, the water stilled first."""
    return _rise(rng(SEED + 6200), 2.6, SEED + 6210)


def vowbound_sink():
    """The dismissal: he sinks back, the water folding over, a soft gurgle."""
    g = rng(SEED + 6300)
    N = _n(1.2)
    fold = _sweep_band(_noise(g, N), 1500, 280, q=1.4, steps=18) * _crest(N, 0.25, 1.2, 0.35)
    buf = 0.7 * fold + 0.6 * _bubbles(g, N, 22, 1.5, 4.0, 0.2, 0.9, amp=0.22, grow=0.6)
    buf = filt(buf, [bq_lowpass(3500, 0.7)])
    return _tail_fade(_room(buf, 1.2, 0.2, SEED + 6301), 0.25)


def vowbound_fall():
    """The fall: struck down, he tips back into the water and is drawn under, slower and heavier than a sink."""
    g = rng(SEED + 6400)
    N = _n(1.8)
    buf = np.zeros(N)
    S = _n(0.8)
    sp = 0.9 * _thump(80, 40, 0.14, S, g, click=0.5) + 0.5 * _burst(g, S, 300, 4500, 0.15, 0.005)
    _place(buf, sp, 0.0)
    D = N - _n(0.2)
    draw = _sweep_band(_noise(g, D), 900, 160, q=1.2, steps=18) * _crest(D, 0.4, 1.2, 0.5)
    _place(buf, 0.8 * draw, 0.2)
    buf += 0.7 * _bubbles(g, N, 30, 2.5, 6.0, 0.15, 1.3, amp=0.25, grow=0.5)
    buf = filt(buf, [bq_lowpass(2800, 0.7), bq_peak(140, 3.0, 0.8)])
    return _tail_fade(_room(buf, 1.6, 0.22, SEED + 6401), 0.3)


# --------------------------------------------------------------------------- the set


def _variants(name, fn, count, target):
    return {f"{SUB}/{name}_{i + 1}": ((lambda i=i: fn(i)), target) for i in range(count)}


SFX: dict = {}
SFX.update(_variants("whoosh_melee", whoosh_melee, 3, WHOOSH))
SFX.update(_variants("whoosh_heavy", whoosh_heavy, 2, WHOOSH))
SFX.update(_variants("whoosh_cast", whoosh_cast, 2, WHOOSH))
SFX.update(_variants("whoosh_throw", whoosh_throw, 2, WHOOSH))
SFX.update(_variants("whoosh_guard", whoosh_guard, 2, WHOOSH))
SFX.update(_variants("accent_hooks", accent_hooks, 3, LAYER))
SFX.update(_variants("accent_staff", accent_staff, 2, LAYER))
SFX.update(_variants("accent_spear", accent_spear, 3, LAYER))
SFX.update(_variants("accent_shield", accent_shield, 2, LAYER))
SFX.update(_variants("accent_book", accent_book, 2, LAYER))
SFX.update(_variants("accent_focus", accent_focus, 2, LAYER))
SFX.update(_variants("accent_cleaver", accent_cleaver, 2, LAYER))
SFX.update(_variants("accent_claw", accent_claw, 3, LAYER))
SFX.update(_variants("accent_teeth", accent_teeth, 2, LAYER))
SFX.update(_variants("accent_bell_hood", accent_bell_hood, 2, LAYER))
SFX.update(_variants("accent_guard", accent_guard, 2, LAYER))
SFX.update(_variants("step_sand", step_sand, 4, LAYER))
SFX.update(_variants("ko_collapse", ko_collapse, 2, BODY))
SFX.update({
    f"{SUB}/swell_rhen": (swell_rhen, BRIGHT),
    f"{SUB}/swell_asha": (swell_asha, BRIGHT),
    f"{SUB}/swell_toma": (swell_toma, BRIGHT),
    f"{SUB}/swell_ysolde": (swell_ysolde, BRIGHT),
    f"{SUB}/toll_wave": (toll_wave, BODY),
    f"{SUB}/flood_surge": (flood_surge, BODY),
})
SFX.update(_variants("flood_brace", flood_brace, 2, LAYER))
SFX.update({
    f"{SUB}/vowbound_beckon": (vowbound_beckon, BRIGHT),
    f"{SUB}/vowbound_rise": (vowbound_rise, BODY),
    f"{SUB}/vowbound_rise_long": (vowbound_rise_long, BODY),
    f"{SUB}/vowbound_sink": (vowbound_sink, -20.0),
    f"{SUB}/vowbound_fall": (vowbound_fall, BODY),
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
