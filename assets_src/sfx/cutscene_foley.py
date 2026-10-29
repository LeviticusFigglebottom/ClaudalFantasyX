"""Cutscene foley (M3-AUD-817): the small sounds of people moving in the slice's cutscenes.

The human's playtest said the slice's parts "look primitive", and its cutscenes ran on silence between the lines:
a book shut, a lantern catching, a hero turning or kneeling, a glimmer rising made no sound. CutsceneAudio
(game/audio/cutscene_audio.gd) plays these at the actor, the light or the effect when the CutsceneSequencer runs
the `@anim`, `@light` or `@vfx` cue that game/data/audio/cutscene_foley.json maps to them. Steps come from the
heroes' own foot contacts (FootstepAudio), not from here. All synthesized here and in tools/audio/synth/ (SPEC §2,
§9: no samples, no recordings, no generated audio), on field_sfx.py's palette. Mono, 44.1 kHz, Ogg Vorbis q4
(mix.md §5), under assets/audio/sfx/cutscene/, on the World bus.

Two variants each unless noted (momentary max; peaks <= -3 dBFS):
    cs_book_shut          a heavy bound book closed: the last pages fluttering down, the boards' soft thump (-22)
    cs_lantern_catch      the lantern's oil burner catching: the glass door's tick, a breathy flare, then a small
                          steady flutter of flame settling (-21)
    cs_lantern_snuff      the burner turned down: a puff and the door's tick (-24)
    cs_glimmer_lift       glimmer rising: a scatter of tiny inharmonic chimes, each drifting upward, never a tune (-25)
    cs_glimmer_held       glimmer held in a hand: a faint shimmer of slowly beating partials (-27)
    cs_glimmer_bound      glimmer bound: the shimmer drawn in to one soft low chime (-25)
    cs_cloth_turn  (x4)   a tunic and sleeve shifting as someone turns to look (-27)
    cs_cloth_kneel        cloth gathering and a knee set down (-24)
    cs_cloth_rise         rising to stand: cloth drawn up and the weight on the feet (-24)
    cs_cloth_sit          sitting down: cloth settling, a soft seat on stone (-25)
    cs_shield_up          a strapped wooden shield raised: leather creak, a knock and the rim's dull ring (-22)
    cs_unsling            a heavy blade unslung: the strap drawn through its buckle and the iron's low ring (-22)
    cs_untie              a cloth band untied: two tugs and the band slipping free (-25)
    cs_feed_fire          sticks laid on a fire: wooden knocks and the embers flaring in a crackle (-23)
    cs_trim_wicks         wicks trimmed: two small snips and the cut ends ticking down (-26)
    cs_pole_water         a pole set into water and pushed: the plunge, the drag and a swirl (-23)

Render:  python3 assets_src/sfx/cutscene_foley.py   (or tools/audio/render_all.py --only cutscene_foley)
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
from field_sfx import _env, _noise, _place, _tail_fade  # noqa: E402
from synth.dsp import SR, bq_bandpass, bq_highpass, bq_lowpass, filt, rng  # noqa: E402
from synth.mixer import measure, normalize_momentary, write_ogg  # noqa: E402
from synth.water import bubble  # noqa: E402

OUT_DIR = os.path.join(ROOT, "assets", "audio", "sfx", "cutscene")
SEED = 81700
CEILING = -3.0


def _g(kind: str, v: int) -> np.random.Generator:
    return rng(SEED + 100 * (sum(map(ord, kind)) % 211) + v)


def _rustle(g, sec: float, lo: float = 1400.0, hi: float = 4200.0, grain_hz: float = 40.0) -> np.ndarray:
    """Cloth moving: band-passed noise with a fibrous grain, swelling and falling over `sec`."""
    n = int(sec * SR)
    t = np.arange(n) / n
    y = np.zeros(n)
    for fc, w in ((lo, 0.6), ((lo * hi) ** 0.5, 0.9), (hi, 0.5)):
        y += w * filt(g.standard_normal(n), [bq_bandpass(fc, 1.1)])
    grain = 0.6 + 0.4 * np.abs(np.sin(2 * np.pi * grain_hz * np.arange(n) / SR + g.uniform(0, 6.28)))
    return y * grain * np.sin(np.pi * t) ** 1.3


def _thump(g, f0: float, sec: float, decay: float) -> np.ndarray:
    n = int(sec * SR)
    t = np.arange(n) / SR
    y = np.sin(2 * np.pi * f0 * t * (1 - 0.15 * t / sec)) * np.exp(-t / decay)
    y += 0.6 * filt(g.standard_normal(n), [bq_lowpass(f0 * 4, 0.8)]) * np.exp(-t / (decay * 0.5))
    return y * np.clip(t / 0.002, 0, 1)


def book_shut(v: int) -> np.ndarray:
    g = _g("book", v)
    buf = np.zeros(int(0.9 * SR))
    for k in range(int(g.integers(5, 9))):  # the last pages
        at = 0.02 + k * float(g.uniform(0.025, 0.04))
        _place(buf, _noise(g, 0.05, [bq_bandpass(float(g.uniform(2500, 4500)), 1.2)], 0.004, 0.015) * 0.35, at)
    shut = 0.3 + float(g.uniform(-0.03, 0.03))
    _place(buf, _thump(g, float(g.uniform(130, 160)), 0.35, 0.06), shut)
    _place(buf, modal([340.0, 780.0], [0.04, 0.02], [0.5, 0.2], 0.2, g, click=0.4) * 0.6, shut)
    _place(buf, _noise(g, 0.2, [bq_bandpass(900, 0.8)], 0.002, 0.05) * 0.4, shut)  # the air pushed out
    return _tail_fade(buf)


def lantern_catch(v: int) -> np.ndarray:
    g = _g("lantern", v)
    sec = 2.2
    n = int(sec * SR)
    buf = np.zeros(n)
    _place(buf, modal([2900.0, 6100.0], [0.05, 0.02], [1.0, 0.3], 0.12, g, click=0.2) * 0.3, 0.02)  # glass door
    # the flare: a breath of noise whose band opens upward, with a low whoomph under it
    fl = int(0.5 * SR)
    t = np.arange(fl) / fl
    flare = np.zeros(fl)
    for k in range(0, fl, 256):
        fc = 600.0 + 2200.0 * (k / fl)
        seg = filt(g.standard_normal(min(1024, fl - k)), [bq_bandpass(fc, 0.9)])
        flare[k: k + 256] += seg[: min(256, fl - k)]
    flare *= np.sin(np.pi * np.clip(t * 1.3, 0, 1)) * np.exp(-t * 1.2)
    _place(buf, flare * 0.8, 0.2)
    _place(buf, _thump(g, 70.0, 0.4, 0.12) * 0.4, 0.22)
    # the flame settling: low noise fluttering at a few Hz, fading
    m = n - int(0.55 * SR)
    tt = np.arange(m) / SR
    flutter = filt(g.standard_normal(m), [bq_lowpass(900, 0.7), bq_highpass(150, 0.7)])
    flutter *= (0.6 + 0.4 * np.sin(2 * np.pi * float(g.uniform(5, 8)) * tt) ** 2) * np.exp(-tt / 0.7)
    _place(buf, flutter * 0.35, 0.55)
    return _tail_fade(buf, 0.2)


def lantern_snuff(v: int) -> np.ndarray:
    g = _g("snuff", v)
    buf = np.zeros(int(0.6 * SR))
    _place(buf, _noise(g, 0.25, [bq_bandpass(700, 0.8)], 0.01, 0.07), 0.02)
    _place(buf, modal([2900.0, 6100.0], [0.05, 0.02], [1.0, 0.3], 0.12, g, click=0.2) * 0.4, 0.3)
    return _tail_fade(buf)


def _chime(g, f: float, sec: float, rise: float) -> np.ndarray:
    """A tiny inharmonic chime whose pitch drifts up by `rise` (a ratio) over its life."""
    n = int(sec * SR)
    t = np.arange(n) / SR
    drift = 1.0 + (rise - 1.0) * t / sec
    y = np.zeros(n)
    for ratio, amp, dec in ((1.0, 1.0, sec * 0.5), (2.76, 0.35, sec * 0.25), (5.4, 0.12, sec * 0.12)):
        y += amp * np.sin(2 * np.pi * np.cumsum(f * ratio * drift) / SR) * np.exp(-t / dec)
    return y * np.clip(t / 0.03, 0, 1)


def glimmer_lift(v: int) -> np.ndarray:
    g = _g("lift", v)
    buf = np.zeros(int(3.0 * SR))
    for _ in range(int(g.integers(10, 15))):
        f = float(g.uniform(2200, 4800))
        _place(buf, _chime(g, f, float(g.uniform(0.6, 1.1)), float(g.uniform(1.03, 1.08))) * float(g.uniform(0.3, 1.0)),
               float(g.uniform(0.0, 1.8)))
    air = _noise(g, 2.5, [bq_bandpass(6000, 0.7)], 0.8, 0.9) * 0.05
    _place(buf, air, 0.0)
    return _tail_fade(filt(buf, [bq_highpass(900, 0.7)]), 0.3)


def glimmer_held(v: int) -> np.ndarray:
    g = _g("held", v)
    sec = 2.6
    n = int(sec * SR)
    t = np.arange(n) / SR
    y = np.zeros(n)
    for _ in range(6):
        f = float(g.uniform(1800, 3200))
        y += np.sin(2 * np.pi * f * t + g.uniform(0, 6.28)) * (0.5 + 0.5 * np.sin(2 * np.pi * float(g.uniform(0.6, 1.8)) * t))
    return _tail_fade(y * np.sin(np.pi * t / sec) ** 1.5, 0.2)


def glimmer_bound(v: int) -> np.ndarray:
    g = _g("bound", v)
    buf = np.zeros(int(2.2 * SR))
    for k in range(7):  # drawn in: chimes falling together toward the bound note
        f = float(g.uniform(1800, 3600))
        _place(buf, _chime(g, f, 0.5, float(g.uniform(0.9, 0.95))) * (0.3 + 0.08 * k), 0.08 * k)
    _place(buf, modal([880.0, 1760.0 * 1.01, 2640.0], [0.9, 0.4, 0.2], [1.0, 0.3, 0.12], 1.5, g) * 0.9, 0.6)
    _place(buf, _thump(g, 90.0, 0.3, 0.06) * 0.25, 0.6)
    return _tail_fade(buf, 0.3)


def cloth_turn(v: int) -> np.ndarray:
    g = _g("turn", v)
    return _tail_fade(_rustle(g, float(g.uniform(0.25, 0.4))))


def cloth_kneel(v: int) -> np.ndarray:
    g = _g("kneel", v)
    buf = np.zeros(int(1.0 * SR))
    _place(buf, _rustle(g, 0.55), 0.0)
    _place(buf, _thump(g, float(g.uniform(95, 120)), 0.3, 0.05) * 0.8, 0.42)
    _place(buf, _noise(g, 0.12, [bq_bandpass(2200, 1.0)], 0.005, 0.04) * 0.3, 0.44)  # grit under the knee
    return _tail_fade(buf)


def cloth_rise(v: int) -> np.ndarray:
    g = _g("rise", v)
    buf = np.zeros(int(1.0 * SR))
    _place(buf, _rustle(g, 0.6, 1200.0, 3800.0), 0.0)
    _place(buf, _thump(g, 110.0, 0.2, 0.04) * 0.5, 0.5)
    _place(buf, _noise(g, 0.15, [bq_bandpass(1800, 1.0)], 0.01, 0.05) * 0.35, 0.52)  # the feet taking the weight
    return _tail_fade(buf)


def cloth_sit(v: int) -> np.ndarray:
    g = _g("sit", v)
    buf = np.zeros(int(1.0 * SR))
    _place(buf, _rustle(g, 0.5), 0.0)
    _place(buf, _thump(g, 85.0, 0.35, 0.07) * 0.7, 0.38)
    _place(buf, _rustle(g, 0.3) * 0.4, 0.45)
    return _tail_fade(buf)


def shield_up(v: int) -> np.ndarray:
    g = _g("shield", v)
    buf = np.zeros(int(1.0 * SR))
    _place(buf, stick_slip(g, 0.16, 140.0, 380.0, [(520.0, 1.0), (1300.0, 0.6)]) * 0.5, 0.0)  # the strap's creak
    _place(buf, modal([180.0, 430.0, 910.0], [0.06, 0.035, 0.02], [1.0, 0.5, 0.25], 0.4, g, click=0.6), 0.2)
    _place(buf, modal([620.0, 1490.0, 2710.0], [0.3, 0.15, 0.08], [1.0, 0.4, 0.2], 0.6, g) * 0.25, 0.2)  # rim
    return _tail_fade(buf)


def unsling(v: int) -> np.ndarray:
    g = _g("unsling", v)
    buf = np.zeros(int(1.3 * SR))
    n = int(0.35 * SR)
    rasp = filt(g.standard_normal(n), [bq_bandpass(1600, 1.2)]) * np.sin(np.pi * np.arange(n) / n)
    _place(buf, rasp * 0.6, 0.0)
    _place(buf, modal([140.0, 380.0, 690.0, 1220.0], [0.4, 0.25, 0.15, 0.08], [1.0, 0.6, 0.35, 0.2], 1.0, g, click=0.3)
           * 0.8, 0.32)
    return _tail_fade(buf, 0.15)


def untie(v: int) -> np.ndarray:
    g = _g("untie", v)
    buf = np.zeros(int(0.9 * SR))
    for k in range(2):
        n = int(0.12 * SR)
        tug = filt(g.standard_normal(n), [bq_bandpass(float(g.uniform(2200, 3000)), 1.4)]) * _env(n, 0.01, 0.05)
        _place(buf, tug, 0.05 + 0.22 * k)
    _place(buf, _rustle(g, 0.3, 1800.0, 5000.0) * 0.6, 0.5)
    return _tail_fade(buf)


def feed_fire(v: int) -> np.ndarray:
    g = _g("fire", v)
    buf = np.zeros(int(1.6 * SR))
    for k in range(int(g.integers(2, 4))):
        base = float(g.uniform(0.9, 1.2))
        _place(buf, modal([320 * base, 760 * base, 1400 * base], [0.04, 0.025, 0.015], [1.0, 0.5, 0.25], 0.2, g, click=0.5)
               * 0.7, 0.05 + 0.2 * k)
    for _ in range(int(g.integers(14, 24))):  # the embers flaring
        k = int(0.004 * SR)
        pop = g.standard_normal(k) * np.linspace(1, 0, k)
        _place(buf, filt(pop, [bq_highpass(1500, 0.7)]) * float(g.uniform(0.2, 0.6)), float(g.uniform(0.35, 1.4)))
    whoosh = _noise(g, 0.8, [bq_lowpass(800, 0.7)], 0.2, 0.35) * 0.3
    _place(buf, whoosh, 0.4)
    return _tail_fade(buf, 0.2)


def trim_wicks(v: int) -> np.ndarray:
    g = _g("wicks", v)
    buf = np.zeros(int(0.9 * SR))
    for k in range(2):
        snip = modal([3400.0, 5200.0, 7900.0], [0.012, 0.008, 0.005], [1.0, 0.6, 0.3], 0.05, g, click=0.6)
        _place(buf, snip, 0.05 + k * float(g.uniform(0.28, 0.36)))
        _place(buf, modal([1900.0], [0.01], [0.4], 0.03, g, click=0.2), 0.18 + k * 0.32)
    return _tail_fade(buf)


def pole_water(v: int) -> np.ndarray:
    g = _g("pole", v)
    buf = np.zeros(int(1.6 * SR))
    _place(buf, _noise(g, 0.15, [bq_lowpass(1200, 0.7)], 0.003, 0.05) * 0.7, 0.0)  # the plunge
    for _ in range(int(g.integers(8, 14))):
        _place(buf, bubble(float(g.uniform(2.5, 6.0)), amp=float(g.uniform(0.2, 0.6))), float(g.uniform(0.0, 0.25)))
    n = int(0.9 * SR)
    tt = np.arange(n) / n
    drag = filt(g.standard_normal(n), [bq_bandpass(500, 0.8)]) * np.sin(np.pi * tt) * (0.7 + 0.3 * np.sin(14 * tt))
    _place(buf, drag * 0.5, 0.3)
    for _ in range(int(g.integers(4, 8))):  # the swirl behind the pole
        _place(buf, bubble(float(g.uniform(1.5, 3.0)), amp=0.3), float(g.uniform(0.6, 1.2)))
    return _tail_fade(buf, 0.15)


def lamp_crackle(v: int) -> np.ndarray:
    """An oil wick burning (M3-AUD-847: Rhen's lamp at the Iskarra vigil): a few tiny spits of the wick and a breath
    of the flame between them. Played at the lamp at random gaps while it is lit (cutscene_foley.json `lamps`)."""
    g = _g("lamp_crackle", v)
    buf = np.zeros(int(0.7 * SR))
    for _ in range(int(g.integers(2, 6))):
        k = int(0.004 * SR)
        spit = filt(g.standard_normal(k), [bq_bandpass(float(g.uniform(2500, 5500)), 1.2)])
        spit *= np.exp(-np.arange(k) / (0.0012 * SR))
        _place(buf, spit * float(g.uniform(0.3, 1.0)), float(g.uniform(0.0, 0.45)))
    _place(buf, _noise(g, 0.5, [bq_lowpass(600, 0.7), bq_highpass(120, 0.7)], 0.05, 0.2) * 0.15, 0.0)
    return _tail_fade(buf, 0.08)


KINDS = {
    "cs_book_shut": (book_shut, 2, -22.0),
    "cs_lantern_catch": (lantern_catch, 2, -21.0),
    "cs_lantern_snuff": (lantern_snuff, 2, -24.0),
    "cs_glimmer_lift": (glimmer_lift, 2, -25.0),
    "cs_glimmer_held": (glimmer_held, 2, -27.0),
    "cs_glimmer_bound": (glimmer_bound, 2, -25.0),
    "cs_cloth_turn": (cloth_turn, 4, -27.0),
    "cs_cloth_kneel": (cloth_kneel, 2, -24.0),
    "cs_cloth_rise": (cloth_rise, 2, -24.0),
    "cs_cloth_sit": (cloth_sit, 2, -25.0),
    "cs_shield_up": (shield_up, 2, -22.0),
    "cs_unsling": (unsling, 2, -22.0),
    "cs_untie": (untie, 2, -25.0),
    "cs_feed_fire": (feed_fire, 2, -23.0),
    "cs_trim_wicks": (trim_wicks, 2, -26.0),
    "cs_pole_water": (pole_water, 2, -23.0),
    "cs_lamp_crackle": (lamp_crackle, 4, -30.0),
}


def _todo() -> list[tuple]:
    out = []
    for name, (fn, count, target) in KINDS.items():
        for v in range(count):
            out.append((f"{name}_{v + 1}", (lambda f=fn, i=v: f(i)), target))
    return out


FILES = [f"{name}.ogg" for name, *_ in _todo()]


def render(out_dir: str = OUT_DIR, verbose: bool = True) -> dict:
    os.makedirs(out_dir, exist_ok=True)
    res = {}
    for name, fn, target in _todo():
        x = normalize_momentary(fn(), target, ceiling_db=CEILING)
        write_ogg(os.path.join(out_dir, name + ".ogg"), x, quality=4.0)
        m = measure(x)
        res[name] = m
        if verbose:
            print(f"{name}: {m['seconds']:.3f}s  momentary max {m['momentary_max_lufs']:.2f} LUFS  "
                  f"peak {m['sample_peak_dbfs']:.2f} dBFS")
    return res


if __name__ == "__main__":
    render()
