"""Act I cutscene foley, the rest of it (M3-AUD-864, ADR 0041).

M3-AUD-817 (cutscene_foley.py) gave the slice's cutscenes their small sounds. The Act I audit on lead/gate-big18
found 91 `@anim` clips across the prologue and Ch1-Ch9 that still played nothing: no foley row and no `@sfx` beside
them. Most of them are hands handling things: the Tender opening Kahre's chamber, Rhen throwing a sail over the
hatch, Toma straining at a seized key, Liss setting her lamp in the sand. Each of those gets a sound here, made
from what the clip does and what the thing is made of. The pure gestures (a nod, a look out to sea, walking, whose
steps are FootstepAudio's) stay silent on purpose: cutscene_foley.json maps them to '', so the audit can tell a
choice from a gap.

Synthesized here and in tools/audio/synth/ (SPEC §2, §9): no samples, no recordings, no generated audio. Built on
field_sfx.py's and cutscene_foley.py's palette. Mono, 44.1 kHz, Ogg Vorbis q4 (mix.md §5), under
assets/audio/sfx/cutscene/ (plain git: small files, ADR 0039 keeps LFS for binaries over 5 MB), on the World bus. Two variants each (momentary max; peaks <= -3 dBFS):

    cs_door_heavy     a heavy door swung on its pivot: the bar lifted, the stone sill grinding, the door settling (-22)
    cs_paper          paper handled: a letter opened, papers held out, a page turned (-27)
    cs_scratch        a dry mark on a hard face: charcoal rubbed over a stamp, chalk on slate (-28)
    cs_ink_cap        a small ink pot capped: the cork's squeak and the pot's tick on wood (-29)
    cs_leather_roll   a tool roll unrolled: leather flaps falling open and the small tools inside clinking (-26)
    cs_brush          a fine brush laying gilt: soft bristle strokes (-31)
    cs_crockery       clay bowls and plates set down, handed over or stacked (-24)
    cs_housing        a brass lamp housing lifted or set down: the brass knock, its cracked panes rattling (-23)
    cs_timber         timber shouldered or handed over: a wooden knock and the grain's creak (-24)
    cs_rope_haul      rope through hands: hauled hand over hand or coiled, the fibre creaking (-23)
    cs_clip           a tether clip snapped onto a ring (-25)
    cs_key            an iron key handed over: its ring's small jangle (-26)
    cs_key_strain     a seized key strained in its lock: iron grinding against rust, and no give (-22)
    cs_spear          a spear levelled or lowered: the ash shaft sliding in the hand, the iron head's faint ring (-25)
    cs_beacon         an oil beacon put to the flame: the whoomph, the roar settling into a big steady burn (-19)
    cs_brand_heat     an iron pushed into a brazier: the coals crunching and the hiss of it heating (-23)
    cs_sail_throw     a wet sail thrown down over a hatch: the canvas cracking open and the heavy slap (-21)
    cs_sand_press     a thing set into sand and the sand pressed flat over it by hand (-28)
    cs_tin            a small tin box pocketed or reached for: its lid's click, a rattle inside (-27)
    cs_scissors       shears taken up: the blades' small scrape and click (-28)
    cs_leaf_water     a leaf boat set on the water: a tiny touch and a ring of ripples (-30)
    cs_cloth_grab     a hand closing on cloth: a quick snatch of fabric and its pull (-24)
    cs_collide        two people colliding: bodies and gear, a breath of cloth (-21)
    cs_slip           a foot going out on wet stone: the scrape, the cloth flung, the catch (-23)
    cs_crawl          a child crawling out from under timber: knees and hands on sand and wood (-27)
    cs_shallows       a body shifting in the shallows: the water moving round it (-25)
    cs_slag_unfold    the Cinder Matron unfolding: slag plates grinding apart, cooling crackle along the seams (-20)
    cs_shell_tap      a fingertip on a set shell: one small bright click (-30)

Render:  python3 tools/audio/render_all.py --only act1_cutscene_foley
"""
from __future__ import annotations

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools", "audio"))
sys.path.insert(0, HERE)

import numpy as np  # noqa: E402

from cutscene_foley import _rustle, _thump  # noqa: E402
from field_ambience import modal, stick_slip  # noqa: E402
from field_sfx import _env, _noise, _place, _tail_fade  # noqa: E402
from synth.dsp import SR, bq_bandpass, bq_highpass, bq_lowpass, filt, rng  # noqa: E402
from synth.mixer import measure, normalize_momentary, write_ogg  # noqa: E402
from synth.water import bubble  # noqa: E402

OUT_DIR = os.path.join(ROOT, "assets", "audio", "sfx", "cutscene")
SEED = 86400
CEILING = -3.0
WOOD = [(520.0, 1.0), (1300.0, 0.6), (2600.0, 0.25)]
FIBRE = [(900.0, 1.0), (2100.0, 0.5), (3800.0, 0.2)]
IRON = [180.0, 470.0, 930.0, 1610.0]
IRON_DECAY = [0.25, 0.15, 0.09, 0.05]
BRASS = [420.0, 1130.0, 2050.0, 3300.0]
CLAY = [880.0, 2010.0, 3350.0]


def _g(kind: str, v: int) -> np.random.Generator:
    return rng(SEED + 100 * (sum(map(ord, kind)) % 251) + v)


def _buf(sec: float) -> np.ndarray:
    return np.zeros(int(sec * SR))


def _crinkle(g, sec: float, rate: float, lo: float = 2500.0, hi: float = 7000.0) -> np.ndarray:
    """Paper or dry leaf: a dense run of tiny bright crackles, swelling and falling over `sec`."""
    n = int(sec * SR)
    y = np.zeros(n)
    for _ in range(int(rate * sec)):
        k = int(float(g.uniform(0.002, 0.008)) * SR)
        at = int(g.uniform(0, max(1, n - k)))
        y[at: at + k] += filt(g.standard_normal(k), [bq_bandpass(float(g.uniform(lo, hi)), 1.5)]) * np.linspace(1, 0, k) \
            * float(g.uniform(0.2, 1.0))
    return y * np.sin(np.pi * np.arange(n) / n) ** 0.7


def _grind(g, sec: float, fc: float, q: float = 1.0, rough_hz: float = 30.0) -> np.ndarray:
    """Two hard faces sliding: band noise roughened by an irregular stick-slip amplitude."""
    n = int(sec * SR)
    t = np.arange(n) / SR
    rough = 0.5 + 0.5 * np.abs(np.sin(2 * np.pi * rough_hz * t + np.cumsum(g.standard_normal(n)) * 0.002))
    return filt(g.standard_normal(n), [bq_bandpass(fc, q)]) * rough * np.sin(np.pi * t / sec) ** 0.8


def _sizzle(g, sec: float, decay: float) -> np.ndarray:
    n = int(sec * SR)
    t = np.arange(n) / SR
    y = filt(g.standard_normal(n), [bq_highpass(3500, 0.7), bq_lowpass(9000, 0.7)])
    y *= (0.6 + 0.4 * filt(g.standard_normal(n), [bq_lowpass(25, 0.7)]) * 8) * np.exp(-t / decay)
    return y * np.clip(t / 0.04, 0, 1)


def door_heavy(v: int) -> np.ndarray:
    g = _g("door", v)
    buf = _buf(2.6)
    _place(buf, modal(IRON, IRON_DECAY, [1.0, 0.5, 0.3, 0.15], 0.6, g, click=0.5) * 0.5, 0.02)  # the bar lifted
    _place(buf, modal(IRON, [d * 0.6 for d in IRON_DECAY], [0.8, 0.4, 0.2, 0.1], 0.4, g, click=0.3) * 0.35, 0.3)
    _place(buf, stick_slip(g, 0.9, 40.0, 160.0, WOOD, q=5.0) * 0.6, 0.55)  # the pivot's creak
    _place(buf, filt(_grind(g, 1.3, 260.0, 0.8, 18.0), [bq_lowpass(900, 0.7)]) * 0.9, 0.5)  # the sill
    _place(buf, _thump(g, 70.0, 0.5, 0.12) * 0.9, 1.85)  # the door settling open
    _place(buf, _noise(g, 0.35, [bq_bandpass(1400, 0.8)], 0.005, 0.08) * 0.2, 1.86)
    return _tail_fade(buf, 0.2)


def paper(v: int) -> np.ndarray:
    g = _g("paper", v)
    buf = _buf(0.9)
    _place(buf, _crinkle(g, 0.35, 160.0), 0.0)
    _place(buf, _noise(g, 0.25, [bq_bandpass(1800, 0.7)], 0.03, 0.08) * 0.35, 0.05)  # the sheet's swish
    _place(buf, _crinkle(g, 0.2, 120.0, 2000.0, 5500.0) * 0.6, 0.45)
    return _tail_fade(buf)


def scratch(v: int) -> np.ndarray:
    g = _g("scratch", v)
    buf = _buf(1.4)
    for k in range(int(g.integers(3, 5))):
        sec = float(g.uniform(0.18, 0.3))
        stroke = _grind(g, sec, float(g.uniform(2400, 3600)), 1.6, float(g.uniform(60, 110)))
        _place(buf, stroke * float(g.uniform(0.6, 1.0)), 0.05 + k * float(g.uniform(0.26, 0.32)))
    return _tail_fade(buf)


def ink_cap(v: int) -> np.ndarray:
    g = _g("ink", v)
    buf = _buf(0.7)
    _place(buf, stick_slip(g, 0.12, 300.0, 900.0, [(1700.0, 1.0), (3100.0, 0.4)], q=7.0) * 0.4, 0.0)  # the cork
    _place(buf, modal(CLAY, [0.03, 0.018, 0.01], [1.0, 0.4, 0.2], 0.15, g, click=0.4) * 0.6, 0.22)
    _place(buf, _thump(g, 210.0, 0.12, 0.02) * 0.4, 0.22)
    return _tail_fade(buf)


def leather_roll(v: int) -> np.ndarray:
    g = _g("roll", v)
    buf = _buf(1.4)
    for k in range(3):  # the flaps falling open
        _place(buf, _rustle(g, 0.18, 700.0, 2200.0, 25.0) * 0.8, 0.05 + 0.2 * k)
        _place(buf, _thump(g, float(g.uniform(150, 190)), 0.15, 0.025) * 0.35, 0.18 + 0.2 * k)
    for _ in range(int(g.integers(3, 6))):  # pens and the knife inside
        f = float(g.uniform(2600, 4200))
        _place(buf, modal([f, f * 2.3], [0.03, 0.015], [1.0, 0.3], 0.1, g, click=0.3) * float(g.uniform(0.15, 0.35)),
               float(g.uniform(0.35, 0.9)))
    return _tail_fade(buf)


def brush(v: int) -> np.ndarray:
    g = _g("brush", v)
    buf = _buf(1.4)
    for k in range(3):
        sec = float(g.uniform(0.25, 0.35))
        n = int(sec * SR)
        s = filt(g.standard_normal(n), [bq_bandpass(float(g.uniform(4500, 6500)), 0.8)]) * np.sin(np.pi * np.arange(n) / n)
        _place(buf, s, 0.05 + k * 0.4)
    return _tail_fade(buf)


def crockery(v: int) -> np.ndarray:
    g = _g("bowl", v)
    buf = _buf(1.2)
    for k in range(int(g.integers(2, 4))):
        r = float(g.uniform(0.92, 1.1))
        at = 0.04 + k * float(g.uniform(0.18, 0.3))
        _place(buf, modal([f * r for f in CLAY], [0.09, 0.05, 0.025], [1.0, 0.5, 0.25], 0.35, g, click=0.5)
               * float(g.uniform(0.5, 1.0)), at)
        _place(buf, _thump(g, float(g.uniform(160, 220)), 0.2, 0.03) * 0.6, at)  # on the wood
    _place(buf, _noise(g, 0.2, [bq_bandpass(2500, 1.0)], 0.01, 0.05) * 0.15, 0.0)  # the hand on the rim
    return _tail_fade(buf, 0.1)


def housing(v: int) -> np.ndarray:
    g = _g("housing", v)
    buf = _buf(1.3)
    _place(buf, modal(BRASS, [0.35, 0.2, 0.12, 0.07], [1.0, 0.5, 0.3, 0.15], 0.8, g, click=0.4) * 0.7, 0.05)
    _place(buf, _thump(g, 120.0, 0.3, 0.05) * 0.6, 0.05)
    for _ in range(int(g.integers(5, 9))):  # the crazed panes in their frame
        f = float(g.uniform(2600, 5200))
        _place(buf, modal([f], [float(g.uniform(0.03, 0.08))], [1.0], 0.15, g, click=0.1) * float(g.uniform(0.1, 0.3)),
               float(g.uniform(0.07, 0.45)))
    return _tail_fade(buf, 0.15)


def timber(v: int) -> np.ndarray:
    g = _g("timber", v)
    buf = _buf(1.1)
    _place(buf, modal([210.0, 560.0, 1120.0], [0.07, 0.04, 0.02], [1.0, 0.5, 0.2], 0.3, g, click=0.6) * 0.8, 0.05)
    _place(buf, _thump(g, 110.0, 0.3, 0.05) * 0.6, 0.05)
    _place(buf, stick_slip(g, 0.45, 60.0, 220.0, WOOD, q=5.0) * 0.4, 0.3)
    return _tail_fade(buf)


def rope_haul(v: int) -> np.ndarray:
    g = _g("haul", v)
    buf = _buf(1.8)
    for k in range(3):  # hand over hand
        _place(buf, stick_slip(g, 0.35, 120.0, 520.0, FIBRE, q=4.0) * 0.8, 0.02 + k * 0.5)
        _place(buf, _noise(g, 0.3, [bq_bandpass(1600, 0.9)], 0.04, 0.08) * 0.35, 0.02 + k * 0.5)
        _place(buf, _thump(g, 140.0, 0.12, 0.02) * 0.25, 0.32 + k * 0.5)
    return _tail_fade(buf, 0.15)


def clip(v: int) -> np.ndarray:
    g = _g("clip", v)
    buf = _buf(0.6)
    _place(buf, modal([2400.0, 4100.0, 6300.0], [0.04, 0.02, 0.012], [1.0, 0.6, 0.3], 0.15, g, click=0.6) * 0.6, 0.02)
    _place(buf, modal([1900.0, 3500.0, 5600.0], [0.07, 0.04, 0.02], [1.0, 0.5, 0.25], 0.25, g, click=0.8), 0.12)
    _place(buf, _rustle(g, 0.2, 1500.0, 3500.0) * 0.25, 0.15)
    return _tail_fade(buf)


def key(v: int) -> np.ndarray:
    g = _g("key", v)
    buf = _buf(0.9)
    for _ in range(int(g.integers(4, 7))):
        f = float(g.uniform(1900, 3600))
        _place(buf, modal([f, f * 2.6], [0.06, 0.03], [1.0, 0.35], 0.2, g, click=0.3) * float(g.uniform(0.3, 0.9)),
               float(g.uniform(0.0, 0.35)))
    return _tail_fade(buf)


def key_strain(v: int) -> np.ndarray:
    g = _g("strain", v)
    buf = _buf(1.9)
    for k in range(2):  # two hard turns against the rust, and neither gives
        at = 0.05 + k * 0.85
        _place(buf, filt(_grind(g, 0.55, 900.0, 1.2, 45.0), [bq_highpass(300, 0.7)]) * 0.9, at)
        _place(buf, stick_slip(g, 0.5, 30.0, 90.0, [(1150.0, 1.0), (2700.0, 0.4)], q=8.0) * 0.5, at)
        _place(buf, modal(IRON, IRON_DECAY, [0.6, 0.4, 0.3, 0.2], 0.4, g, click=0.6) * 0.45, at + 0.55)  # the jolt
    return _tail_fade(buf, 0.15)


def spear(v: int) -> np.ndarray:
    g = _g("spear", v)
    buf = _buf(1.2)
    n = int(0.4 * SR)
    slide = filt(g.standard_normal(n), [bq_bandpass(1100, 0.9)]) * np.sin(np.pi * np.arange(n) / n)
    _place(buf, slide * 0.6, 0.0)
    _place(buf, _rustle(g, 0.35) * 0.4, 0.0)
    _place(buf, modal([1240.0, 2900.0, 4700.0], [0.3, 0.15, 0.08], [1.0, 0.4, 0.2], 0.8, g, click=0.2) * 0.25, 0.38)
    _place(buf, _thump(g, 150.0, 0.15, 0.025) * 0.3, 0.38)  # the grip set
    return _tail_fade(buf, 0.15)


def beacon(v: int) -> np.ndarray:
    g = _g("beacon", v)
    sec = 3.2
    n = int(sec * SR)
    buf = np.zeros(n)
    fl = int(0.9 * SR)
    t = np.arange(fl) / fl
    flare = np.zeros(fl)
    for k in range(0, fl, 512):  # the flare climbing
        seg = filt(g.standard_normal(min(2048, fl - k)), [bq_bandpass(300.0 + 1500.0 * (k / fl), 0.7)])
        flare[k: k + 512] += seg[: min(512, fl - k)]
    flare *= np.sin(np.pi * np.clip(t * 1.6, 0, 1)) ** 0.6 * np.exp(-t * 0.6)
    _place(buf, flare, 0.05)
    _place(buf, _thump(g, 55.0, 0.8, 0.25) * 1.2, 0.08)  # the whoomph
    m = n - int(0.5 * SR)
    tt = np.arange(m) / SR
    roar = filt(g.standard_normal(m), [bq_lowpass(1100, 0.7), bq_highpass(80, 0.7)])
    roar *= (0.7 + 0.3 * filt(g.standard_normal(m), [bq_lowpass(6, 0.7)]) * 10) * np.clip(tt / 0.3, 0, 1)
    _place(buf, roar * 0.5 * np.exp(-tt / 2.5), 0.5)
    for _ in range(int(g.integers(20, 32))):  # the oil spitting
        k = int(0.004 * SR)
        _place(buf, filt(g.standard_normal(k), [bq_highpass(2000, 0.7)]) * np.linspace(1, 0, k) * float(g.uniform(0.2, 0.6)),
               float(g.uniform(0.4, 2.8)))
    return _tail_fade(buf, 0.6)


def brand_heat(v: int) -> np.ndarray:
    g = _g("brand", v)
    buf = _buf(2.2)
    for _ in range(int(g.integers(6, 10))):  # the coals crunching
        f = float(g.uniform(900, 2200))
        _place(buf, modal([f, f * 1.7], [0.02, 0.012], [1.0, 0.4], 0.08, g, click=0.6) * float(g.uniform(0.3, 0.8)),
               float(g.uniform(0.0, 0.3)))
    _place(buf, modal(IRON, IRON_DECAY, [0.5, 0.3, 0.2, 0.1], 0.5, g, click=0.4) * 0.35, 0.02)
    _place(buf, _sizzle(g, 1.8, 0.8) * 0.6, 0.25)
    _place(buf, _noise(g, 1.5, [bq_lowpass(600, 0.7)], 0.2, 0.6) * 0.25, 0.2)  # the draught
    return _tail_fade(buf, 0.2)


def sail_throw(v: int) -> np.ndarray:
    g = _g("sail", v)
    buf = _buf(1.5)
    _place(buf, _rustle(g, 0.45, 500.0, 1800.0, 18.0) * 0.8, 0.0)  # the canvas opening in the air
    _place(buf, _noise(g, 0.12, [bq_bandpass(900, 0.8)], 0.002, 0.03) * 0.6, 0.28)  # its crack
    _place(buf, _thump(g, 75.0, 0.6, 0.12) * 1.0, 0.5)  # the wet weight landing
    _place(buf, _noise(g, 0.35, [bq_lowpass(1200, 0.7)], 0.003, 0.08) * 0.6, 0.5)
    for _ in range(int(g.integers(5, 9))):
        _place(buf, bubble(float(g.uniform(2.0, 5.0)), amp=float(g.uniform(0.1, 0.3))), float(g.uniform(0.5, 0.8)))
    return _tail_fade(buf, 0.15)


def sand_press(v: int) -> np.ndarray:
    g = _g("sand", v)
    buf = _buf(1.4)
    for k in range(3):
        n = int(0.3 * SR)
        s = filt(g.standard_normal(n), [bq_bandpass(float(g.uniform(1200, 2000)), 0.8)]) * np.sin(np.pi * np.arange(n) / n)
        _place(buf, s * (1.0 - 0.2 * k), 0.05 + k * 0.38)
        _place(buf, _thump(g, 120.0, 0.12, 0.02) * 0.2, 0.15 + k * 0.38)
    return _tail_fade(buf)


def tin(v: int) -> np.ndarray:
    g = _g("tin", v)
    buf = _buf(0.8)
    _place(buf, modal([1650.0, 3900.0, 6100.0], [0.05, 0.03, 0.015], [1.0, 0.5, 0.25], 0.15, g, click=0.5) * 0.7, 0.02)
    for _ in range(int(g.integers(3, 6))):  # what is inside
        _place(buf, modal([float(g.uniform(2500, 4500))], [0.02], [1.0], 0.06, g, click=0.3) * float(g.uniform(0.15, 0.35)),
               float(g.uniform(0.05, 0.3)))
    _place(buf, _rustle(g, 0.25) * 0.35, 0.3)  # into the pocket
    return _tail_fade(buf)


def scissors(v: int) -> np.ndarray:
    g = _g("shears", v)
    buf = _buf(0.8)
    _place(buf, modal([1500.0, 3300.0], [0.06, 0.03], [1.0, 0.4], 0.15, g, click=0.3) * 0.4, 0.02)  # off the board
    _place(buf, filt(_grind(g, 0.12, 4200.0, 2.0, 120.0), [bq_highpass(2000, 0.7)]) * 0.5, 0.25)
    _place(buf, modal([3600.0, 5900.0, 8100.0], [0.015, 0.01, 0.006], [1.0, 0.6, 0.3], 0.06, g, click=0.6), 0.37)
    return _tail_fade(buf)


def leaf_water(v: int) -> np.ndarray:
    g = _g("leaf", v)
    buf = _buf(1.2)
    _place(buf, _crinkle(g, 0.15, 60.0, 1800.0, 4000.0) * 0.4, 0.0)
    for k in range(int(g.integers(3, 5))):
        _place(buf, bubble(float(g.uniform(1.2, 2.2)), amp=float(g.uniform(0.2, 0.4))), 0.15 + 0.12 * k)
    _place(buf, _noise(g, 0.6, [bq_bandpass(700, 0.8)], 0.05, 0.25) * 0.12, 0.15)  # the ripples
    return _tail_fade(buf)


def cloth_grab(v: int) -> np.ndarray:
    g = _g("grab", v)
    buf = _buf(0.8)
    _place(buf, _rustle(g, 0.15, 1200.0, 4000.0, 60.0) * 1.0, 0.0)
    _place(buf, _thump(g, 140.0, 0.12, 0.02) * 0.4, 0.06)
    _place(buf, _rustle(g, 0.3, 900.0, 2800.0) * 0.5, 0.12)  # the pull
    return _tail_fade(buf)


def collide(v: int) -> np.ndarray:
    g = _g("collide", v)
    buf = _buf(1.0)
    _place(buf, _thump(g, 95.0, 0.4, 0.08) * 1.0, 0.03)
    _place(buf, _thump(g, 130.0, 0.25, 0.04) * 0.5, 0.06)
    _place(buf, modal(BRASS, [0.08, 0.05, 0.03, 0.02], [0.6, 0.4, 0.2, 0.1], 0.2, g, click=0.3) * 0.25, 0.05)  # gear
    _place(buf, _rustle(g, 0.4, 900.0, 3000.0) * 0.6, 0.0)
    return _tail_fade(buf)


def slip(v: int) -> np.ndarray:
    g = _g("slip", v)
    buf = _buf(1.1)
    n = int(0.22 * SR)
    scrape = filt(g.standard_normal(n), [bq_bandpass(1600, 1.0)]) * np.linspace(0.3, 1, n) * np.linspace(1, 0, n) ** 0.5
    _place(buf, scrape * 0.9, 0.02)
    for _ in range(int(g.integers(3, 6))):  # wet under the sole
        _place(buf, bubble(float(g.uniform(2.0, 4.0)), amp=float(g.uniform(0.1, 0.25))), float(g.uniform(0.04, 0.2)))
    _place(buf, _rustle(g, 0.35, 1100.0, 3500.0, 70.0) * 0.8, 0.15)  # the arms flung
    _place(buf, _thump(g, 120.0, 0.2, 0.03) * 0.6, 0.45)  # the foot caught
    return _tail_fade(buf)


def crawl(v: int) -> np.ndarray:
    g = _g("crawl", v)
    buf = _buf(1.6)
    for k in range(4):
        n = int(0.12 * SR)
        s = filt(g.standard_normal(n), [bq_bandpass(float(g.uniform(1300, 2200)), 0.9)]) * np.sin(np.pi * np.arange(n) / n)
        _place(buf, s * 0.7, 0.05 + k * float(g.uniform(0.28, 0.34)))
        _place(buf, _thump(g, float(g.uniform(130, 170)), 0.12, 0.02) * 0.35, 0.08 + k * 0.31)
    _place(buf, _rustle(g, 1.2, 1000.0, 3200.0) * 0.4, 0.05)
    return _tail_fade(buf, 0.1)


def shallows(v: int) -> np.ndarray:
    g = _g("shallows", v)
    buf = _buf(1.8)
    n = int(1.2 * SR)
    tt = np.arange(n) / n
    swash = filt(g.standard_normal(n), [bq_bandpass(600, 0.7)]) * np.sin(np.pi * tt) * (0.7 + 0.3 * np.sin(9 * tt))
    _place(buf, swash * 0.7, 0.0)
    for _ in range(int(g.integers(10, 16))):
        _place(buf, bubble(float(g.uniform(1.5, 5.0)), amp=float(g.uniform(0.15, 0.45))), float(g.uniform(0.05, 1.2)))
    _place(buf, _rustle(g, 0.5, 800.0, 2400.0) * 0.3, 0.2)
    return _tail_fade(buf, 0.2)


def slag_unfold(v: int) -> np.ndarray:
    g = _g("slag", v)
    buf = _buf(3.2)
    for k in range(4):  # plates grinding apart, each a little higher
        _place(buf, filt(_grind(g, 0.7, 160.0 + 60.0 * k, 0.9, 14.0), [bq_lowpass(1500, 0.7)]) * 0.9, 0.1 + 0.55 * k)
        _place(buf, _thump(g, 60.0 + 8.0 * k, 0.5, 0.1) * 0.6, 0.75 + 0.55 * k)
    for _ in range(int(g.integers(30, 45))):  # cooling crackle along the seams
        f = float(g.uniform(1800, 4200))
        _place(buf, modal([f], [0.012], [1.0], 0.04, g, click=0.4) * float(g.uniform(0.1, 0.35)), float(g.uniform(0.3, 2.9)))
    return _tail_fade(buf, 0.3)


def shell_tap(v: int) -> np.ndarray:
    g = _g("shelltap", v)
    buf = _buf(0.5)
    _place(buf, modal([3100.0, 5400.0, 7700.0], [0.025, 0.014, 0.008], [1.0, 0.45, 0.2], 0.1, g, click=0.4), 0.02)
    return _tail_fade(buf)


KINDS = {
    "cs_door_heavy": (door_heavy, 2, -22.0),
    "cs_paper": (paper, 2, -27.0),
    "cs_scratch": (scratch, 2, -28.0),
    "cs_ink_cap": (ink_cap, 2, -29.0),
    "cs_leather_roll": (leather_roll, 2, -26.0),
    "cs_brush": (brush, 2, -31.0),
    "cs_crockery": (crockery, 2, -24.0),
    "cs_housing": (housing, 2, -23.0),
    "cs_timber": (timber, 2, -24.0),
    "cs_rope_haul": (rope_haul, 2, -23.0),
    "cs_clip": (clip, 2, -25.0),
    "cs_key": (key, 2, -26.0),
    "cs_key_strain": (key_strain, 2, -22.0),
    "cs_spear": (spear, 2, -25.0),
    "cs_beacon": (beacon, 2, -19.0),
    "cs_brand_heat": (brand_heat, 2, -23.0),
    "cs_sail_throw": (sail_throw, 2, -21.0),
    "cs_sand_press": (sand_press, 2, -28.0),
    "cs_tin": (tin, 2, -27.0),
    "cs_scissors": (scissors, 2, -28.0),
    "cs_leaf_water": (leaf_water, 2, -30.0),
    "cs_cloth_grab": (cloth_grab, 2, -24.0),
    "cs_collide": (collide, 2, -21.0),
    "cs_slip": (slip, 2, -23.0),
    "cs_crawl": (crawl, 2, -27.0),
    "cs_shallows": (shallows, 2, -25.0),
    "cs_slag_unfold": (slag_unfold, 2, -20.0),
    "cs_shell_tap": (shell_tap, 2, -30.0),
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
