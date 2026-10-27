"""Act I's cutscene sounds (M3-AUD-818): the 68 `@sfx` cues the chapters' cutscenes name.

The Act I cutscenes (Ch1, Ch4-Ch9) ask for a sound with `@sfx <id>`, and the CutsceneSequencer plays
assets/audio/sfx/<id>.ogg flat (game/data/cutscene/sequencer.json sfx_dir; the director routes its players to a
bus). None of the 68 existed, so every one of those beats was silent. Each sound is written for its scene (the cue's
dialogue is quoted in the comment), from shared builders: water, wood and rope creaks, struck metal, bells, fire,
crowds, wind and rain, and the synth voice for the four sung or hummed cues.

All synthesized here and in tools/audio/synth/ (SPEC §2, §9: no samples, no recordings, no generated audio). The
hummed and sung figures (neme_humming, asha_hum_lullaby, pell_storm_note, current_song) are short phrases written
for this file in a five-note mode; none quotes or derives from an existing melody. Mono, 44.1 kHz, Ogg Vorbis q4
(mix.md §5). Each file is normalised to its own momentary max (CUES' target, LUFS): a sharp one-shot about -18,
foley about -22, the long beds a cue sets under a line about -24. Sample peaks <= -2 dBFS, so decoded true peaks
stay at or under -1 dBTP.

Render:  python3 assets_src/sfx/act1_cutscene_sfx.py   (or tools/audio/render_all.py --only act1_cutscene_sfx)
"""
from __future__ import annotations

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools", "audio"))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "assets_src", "music"))

import numpy as np  # noqa: E402

from field_ambience import gull_call, lap, modal, murmur_phrase, stick_slip  # noqa: E402
from field_sfx import _env, _noise, _place, _room, _tail_fade  # noqa: E402
from motifs import order_hum_in_seconds, phrases_in_seconds  # noqa: E402
from synth.bells import tower_bell  # noqa: E402
from synth.dsp import SR, bq_bandpass, bq_highpass, bq_lowpass, filt, rng  # noqa: E402
from synth.mixer import measure, normalize_momentary, write_ogg  # noqa: E402
from synth.voice import sing  # noqa: E402
from synth.water import bubble, drip  # noqa: E402

OUT_DIR = os.path.join(ROOT, "assets", "audio", "sfx")
SEED = 81800
CEILING = -2.0


# --------------------------------------------------------------------------- builders


def _g(name: str) -> np.random.Generator:
    return rng(SEED + sum((i + 1) * ord(c) for i, c in enumerate(name)) % 100003)


def _buf(sec: float) -> np.ndarray:
    return np.zeros(int(sec * SR))


def _shape(n: int, attack: float, release: float) -> np.ndarray:
    """A flat envelope with a linear rise over `attack` and a fall over `release` (both in seconds)."""
    t = np.arange(n) / SR
    up = np.clip(t / max(attack, 1e-3), 0, 1)
    down = np.clip((n / SR - t) / max(release, 1e-3), 0, 1)
    return up * down


def _band(g, sec: float, lo: float, hi: float) -> np.ndarray:
    n = int(sec * SR)
    return filt(g.standard_normal(n), [bq_highpass(lo, 0.7), bq_lowpass(hi, 0.7)])


def _slow(g, n: int, hz: float) -> np.ndarray:
    """A slow random level, 0..1, wandering at about `hz`."""
    k = max(2, int(n / SR * hz) + 2)
    pts = g.uniform(0, 1, k)
    return np.interp(np.linspace(0, k - 1, n), np.arange(k), pts)


def _thump(g, f0: float, sec: float, decay: float, drop: float = 0.3) -> np.ndarray:
    n = int(sec * SR)
    t = np.arange(n) / SR
    f = f0 * (1 - drop * np.clip(t / sec, 0, 1))
    y = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / decay)
    y += 0.6 * filt(g.standard_normal(n), [bq_lowpass(f0 * 4, 0.8)]) * np.exp(-t / (decay * 0.5))
    return y * np.clip(t / 0.002, 0, 1)


def _wood(g, f0: float = 220.0, sec: float = 0.4) -> np.ndarray:
    b = float(g.uniform(0.9, 1.1)) * f0
    return modal([b, b * 2.3, b * 4.1, b * 6.9], [0.06, 0.035, 0.02, 0.01], [1.0, 0.5, 0.25, 0.1], sec, g, click=0.6)


def _iron(g, f0: float = 420.0, sec: float = 1.2, ring: float = 0.5) -> np.ndarray:
    b = float(g.uniform(0.95, 1.05)) * f0
    return modal([b, b * 2.71, b * 5.15, b * 8.2], [ring, ring * 0.6, ring * 0.35, ring * 0.2], [1.0, 0.6, 0.35, 0.2],
                 sec, g, click=0.5)


def _creak(g, dur: float, lo: float, hi: float, body=((350.0, 1.0), (900.0, 0.6), (1900.0, 0.3))) -> np.ndarray:
    return stick_slip(g, dur, lo, hi, list(body))


def _splash(g, size: float, sec: float = 1.8) -> np.ndarray:
    """A body entering water: the slap, the cavity's low plunge, bubbles, and the spray falling back."""
    buf = _buf(sec)
    _place(buf, _noise(g, 0.08, [bq_bandpass(1800, 0.7)], 0.001, 0.03) * size, 0.0)
    _place(buf, _thump(g, 90.0 / size ** 0.3, 0.4, 0.12) * 0.7 * size, 0.01)
    for _ in range(int(14 * size)):
        _place(buf, bubble(float(g.uniform(1.5, 7.0)), amp=float(g.uniform(0.2, 0.7))), float(g.uniform(0.02, 0.6)))
    for _ in range(int(20 * size)):
        _place(buf, drip(vel=float(g.uniform(0.3, 0.7)), radius_mm=float(g.uniform(1.5, 3.5)),
                         seed=int(g.integers(1 << 30))) * 0.4, float(g.uniform(0.25, sec - 0.4)))
    return buf


def _laps(g, sec: float, every: float, size: float = 1.0) -> np.ndarray:
    buf = _buf(sec)
    t = float(g.uniform(0, every))
    while t < sec - 1.0:
        _place(buf, lap(g, float(g.uniform(0.6, 1.2)) * size) * float(g.uniform(0.5, 1.0)), t)
        t += every * float(g.uniform(0.6, 1.4))
    return buf


def _roar(g, sec: float, lo: float, hi: float, attack: float, release: float, wobble: float = 0.4) -> np.ndarray:
    n = int(sec * SR)
    y = _band(g, sec, lo, hi) + 0.5 * _band(g, sec, lo * 0.5, lo * 2.0)
    return y * _shape(n, attack, release) * (1 - wobble + wobble * _slow(g, n, 3.0))


def _crackle(g, sec: float, rate: float, lo: float = 1500.0) -> np.ndarray:
    buf = _buf(sec)
    for _ in range(int(sec * rate)):
        k = int(float(g.uniform(0.002, 0.006)) * SR)
        pop = g.standard_normal(k) * np.linspace(1, 0, k) * float(g.uniform(0.2, 1.0))
        _place(buf, pop, float(g.uniform(0, sec - 0.01)))
    return filt(buf, [bq_highpass(lo, 0.7)])


def _fire(g, sec: float, size: float = 1.0) -> np.ndarray:
    n = int(sec * SR)
    body = _band(g, sec, 80, 900) * (0.6 + 0.4 * _slow(g, n, 4.0)) * 0.6 * size
    return body + _crackle(g, sec, 18 * size)


def _crowd(g, sec: float, voices: int, warm: bool = True) -> np.ndarray:
    buf = _buf(sec)
    for _ in range(voices):
        p = murmur_phrase(g, bool(g.random() < 0.5))
        _place(buf, p * float(g.uniform(0.3, 1.0)), float(g.uniform(0.0, sec - 1.0)) if sec > 2 else 0.0)
    bed = _band(g, sec, 200, 1400 if warm else 2000) * 0.15
    return buf + bed


def _wind(g, sec: float, strength: float, attack: float, release: float) -> np.ndarray:
    n = int(sec * SR)
    gust = _slow(g, n, 0.6)
    y = np.zeros(n)
    for f, q, w in ((200, 0.9, 1.0), (450, 1.0, 0.8), (900, 1.1, 0.5 * strength), (1800, 1.2, 0.3 * strength)):
        y += w * filt(g.standard_normal(n), [bq_bandpass(f, q)]) * (0.4 + 0.6 * gust ** (1 + strength))
    return y * _shape(n, attack, release)


def _rain(g, sec: float, density_from: float, density_to: float) -> np.ndarray:
    n = int(sec * SR)
    hiss = _band(g, sec, 1500, 9000)
    dens = np.linspace(density_from, density_to, n)
    buf = _buf(sec)
    for i in range(int(sec * 60 * max(density_from, density_to))):
        at = float(g.uniform(0, sec - 0.05))
        if g.random() < dens[int(at * SR)]:
            _place(buf, drip(vel=float(g.uniform(0.2, 0.5)), radius_mm=float(g.uniform(1.0, 2.0)),
                             seed=int(g.integers(1 << 30))) * 0.25, at)
    return hiss * dens * 0.4 + buf


def _hum(g, notes: list[tuple[float, float]], vowel: str, scale: float, seed: int, vib: float = 14.0) -> np.ndarray:
    """A hummed or sung line: `notes` are (midi, seconds); `vowel` 'm' hums, any vowel sings."""
    phon = [(vowel, d) for _, d in notes]
    return sing(phon, notes, vel=0.5, seed=seed, scale=scale, tilt=1.8, breath=0.08, vib_cents=vib, vib_rate=4.8,
                jitter_cents=6.0, release=0.4)


def _room_tail(g, x: np.ndarray, rt60: float, mix: float) -> np.ndarray:
    pad = np.concatenate([x, np.zeros(int(rt60 * SR))])
    return _room(pad, rt60, mix, int(g.integers(1 << 30)))


# --------------------------------------------------------------------------- Ch1: Oruvel


def splash(g):  # "Fine. Fine. Watch how it's done." Rhen dives off a roof into the canal.
    return _splash(g, 1.4, 2.2)


def bell_room_drip(g):  # dawn in the drowned bell room: slow drips into still water, a long stone room
    buf = _buf(6.0)
    for t in (0.2, 1.4, 2.1, 3.3, 4.6):
        _place(buf, drip(vel=float(g.uniform(0.4, 0.7)), radius_mm=float(g.uniform(2.5, 4.0)),
                         seed=int(g.integers(1 << 30))), t + float(g.uniform(-0.1, 0.1)))
    return _room_tail(g, buf, 2.8, 0.45)


def raft_lashing_snap(g):  # "Kell, the bridge!" the raft-bridge's lashing parts under the strain
    buf = _buf(2.2)
    _place(buf, _creak(g, 0.35, 120, 520, ((260.0, 1.0), (700.0, 0.6))) * 0.6, 0.0)
    n = int(0.06 * SR)
    snap = filt(g.standard_normal(n), [bq_bandpass(2400, 0.8)]) * _env(n, 0.0005, 0.012)
    _place(buf, snap * 1.2, 0.36)
    _place(buf, _wood(g, 160, 0.5) * 0.8, 0.42)
    _place(buf, _splash(g, 0.7, 1.4) * 0.6, 0.7)
    return buf


def salvage_cut(g):  # "Two metres of Lit Age brass": a saw biting old brass, three strokes and a clink
    buf = _buf(2.0)
    for k in range(3):
        sec = float(g.uniform(0.28, 0.36))
        n = int(sec * SR)
        tt = np.arange(n) / SR
        teeth = 1 + 0.8 * np.sin(2 * np.pi * float(g.uniform(55, 70)) * tt) ** 2
        stroke = filt(g.standard_normal(n), [bq_bandpass(float(g.uniform(3200, 4200)), 2.0)]) * teeth
        _place(buf, stroke * np.sin(np.pi * tt / sec), 0.05 + k * 0.45)
        _place(buf, _iron(g, 1250, 0.4, 0.15) * 0.15, 0.05 + k * 0.45)
    _place(buf, _iron(g, 900, 0.8, 0.3) * 0.6, 1.45)
    return buf


def undertow_wall_roar(g):  # "Go! Don't look back, go!" a wall of the sea coming in, swelling to fill everything
    y = _roar(g, 6.5, 40, 700, 2.5, 1.5, 0.5)
    y += _band(g, 6.5, 1500, 5000) * _shape(int(6.5 * SR), 3.5, 1.2) * 0.25  # the spray at its face
    t = np.arange(len(y)) / SR
    return y + 0.8 * np.sin(2 * np.pi * 32 * t) * _shape(len(y), 3.0, 1.5)


def beacon_lamp_gutter(g):  # the beacon's lamp guttering as the water reaches it, then out
    sec = 2.4
    n = int(sec * SR)
    flame = _band(g, sec, 120, 1100) * (0.5 + 0.5 * np.abs(np.sin(2 * np.pi * np.cumsum(np.linspace(6, 18, n)) / SR)))
    flame *= _shape(n, 0.05, 1.4)
    buf = flame * 0.6 + _crackle(g, sec, 10) * _shape(n, 0.05, 1.6)
    _place(buf, _noise(g, 0.6, [bq_bandpass(3500, 0.8)], 0.02, 0.25) * 0.5, 1.5)  # the hiss as it drowns
    return buf


def lintel_gull_cry(g):  # "...That's the gulls." the lintel gulls crying alarm, close and many
    buf = _buf(3.5)
    for k in range(5):
        _place(buf, gull_call(g) * float(g.uniform(0.5, 1.0)), float(g.uniform(0.0, 1.8)))
    return filt(buf, [bq_highpass(600, 0.7)])


def hullgnaw_ribs_creak(g):  # the Hullgnaw rising: its ribs of old hull timber groaning under their own weight
    buf = _buf(3.5)
    _place(buf, _creak(g, 1.6, 30, 140, ((110.0, 1.0), (260.0, 0.7), (520.0, 0.3))), 0.0)
    _place(buf, _creak(g, 1.1, 40, 180, ((150.0, 1.0), (330.0, 0.6))) * 0.7, 1.4)
    _place(buf, _roar(g, 3.5, 30, 250, 0.6, 1.0) * 0.4, 0.0)
    return buf


def scale_weigh(g):  # the scale-man weighs the brass: chains clink, the pan dips and settles, a weight set down
    buf = _buf(1.8)
    for k in range(6):
        _place(buf, _iron(g, float(g.uniform(1800, 2600)), 0.25, 0.05) * float(g.uniform(0.3, 0.6)),
               float(g.uniform(0.0, 0.5)))
    _place(buf, _thump(g, 140, 0.4, 0.08) * 0.8, 0.15)
    _place(buf, _iron(g, 700, 1.0, 0.4) * 0.5, 0.9)
    return buf


def chit_stamp(g):  # "There's your chit": a wooden stamp on a paper chit, on a counter
    buf = _buf(0.6)
    _place(buf, _noise(g, 0.05, [bq_bandpass(3000, 0.9)], 0.002, 0.02) * 0.3, 0.0)
    _place(buf, _wood(g, 300, 0.3), 0.04)
    _place(buf, _thump(g, 120, 0.25, 0.05) * 0.6, 0.04)
    return buf


def tether_run(g):  # "One month earlier." a diver's tether line running out fast through its ring
    sec = 2.8
    n = int(sec * SR)
    rate = np.linspace(30, 120, n)
    tt = np.cumsum(rate) / SR
    whir = filt(g.standard_normal(n), [bq_bandpass(1600, 1.0)]) * (0.6 + 0.4 * np.sin(2 * np.pi * tt) ** 2)
    whir *= _shape(n, 0.3, 0.5)
    buf = whir + _creak(g, sec, 80, 300, ((900.0, 1.0), (2100.0, 0.5))) * 0.25
    _place(buf, _iron(g, 600, 0.6, 0.2) * 0.5, sec - 0.5)
    return buf


# --------------------------------------------------------------------------- Ch4: Haluna's wake, the ferry


def gangplank(g):  # a gangplank run out and dropped onto a deck: a slide, a heavy plank landing, a rattle
    buf = _buf(1.4)
    _place(buf, _creak(g, 0.3, 200, 600, ((420.0, 1.0), (980.0, 0.5))) * 0.4, 0.0)
    _place(buf, _wood(g, 140, 0.6) * 1.0, 0.32)
    _place(buf, _thump(g, 95, 0.4, 0.1) * 0.8, 0.32)
    _place(buf, _wood(g, 210, 0.3) * 0.4, 0.46)
    return buf


def wake_lamps_out(g):  # the wake: the lamps carried to the wall and put out one by one, the sea beyond
    buf = _laps(g, 6.0, 1.6, 0.8) * 0.5
    for k in range(5):
        _place(buf, _noise(g, 0.3, [bq_bandpass(700, 0.8)], 0.01, 0.08) * 0.8, 0.6 + k * float(g.uniform(0.9, 1.1)))
    return buf


def name_board_prise(g):  # "prise_name_board": a bar under the old name board, nails squealing out, wood giving
    buf = _buf(2.8)
    _place(buf, _iron(g, 520, 0.4, 0.1) * 0.5, 0.0)  # the bar set
    for k in range(3):
        n = int(0.35 * SR)
        f = np.linspace(900, 2400, n)
        squeal = np.sin(2 * np.pi * np.cumsum(f) / SR) * _shape(n, 0.05, 0.1) * 0.25
        _place(buf, squeal + _creak(g, 0.35, 150, 600)[:n] * 0.5, 0.25 + k * 0.6)
    _place(buf, _wood(g, 180, 0.6), 2.1)
    return buf


def sails_luff_and_fall(g):  # the derelict's sails shivering in the wind, then coming down
    sec = 4.0
    n = int(sec * SR)
    t = np.arange(n) / SR
    flap = 0.5 + 0.5 * np.sin(2 * np.pi * np.cumsum(5 + 3 * _slow(g, n, 1.5)) / SR)
    luff = _band(g, sec, 120, 2500) * flap ** 3 * _shape(n, 0.2, 1.2) * np.clip((3.0 - t) / 0.6, 0, 1)
    buf = luff
    _place(buf, _roar(g, 1.4, 80, 900, 0.05, 0.9) * 0.9, 2.6)  # the canvas falling
    return buf


def lookout_call(g):  # "Sail! Sail off the bow": the ferry's hand bell rung fast for all hands
    buf = _buf(2.5)
    for k in range(7):
        _place(buf, _iron(g, 1350, 1.0, 0.35) * float(g.uniform(0.6, 1.0)), 0.02 + k * float(g.uniform(0.16, 0.2)))
    return buf


def derelict_wheel_turning(g):  # the derelict's wheel turning by itself, the rudder knocking below
    buf = _buf(3.5)
    for k in range(4):
        _place(buf, _creak(g, 0.55, 60, 260, ((240.0, 1.0), (610.0, 0.5))) * 0.8, k * 0.8)
        _place(buf, _wood(g, 120, 0.4) * 0.4, k * 0.8 + 0.5)
    return buf


def shell_set(g):  # "It's time." the shell set into the wall's gap: ceramic on stone, a small settling
    buf = _buf(1.2)
    _place(buf, _noise(g, 0.15, [bq_bandpass(2500, 1.0)], 0.01, 0.05) * 0.3, 0.0)
    _place(buf, modal([1900.0, 4300.0, 6900.0], [0.12, 0.06, 0.03], [1.0, 0.4, 0.15], 0.6, g, click=0.4) * 0.7, 0.12)
    _place(buf, _thump(g, 160, 0.2, 0.04) * 0.5, 0.12)
    return buf


def ink_brush(g):  # Ysolde inking a shell: a fine brush drawing two strokes
    buf = _buf(1.0)
    for k in range(2):
        n = int(float(g.uniform(0.22, 0.32)) * SR)
        stroke = filt(g.standard_normal(n), [bq_bandpass(float(g.uniform(4500, 6000)), 1.2)])
        _place(buf, stroke * np.sin(np.pi * np.arange(n) / n) ** 1.5, 0.05 + 0.4 * k)
    return buf


def neme_humming(g):  # Neme clearing plates at the wake, humming to herself: an older voice, low and unhurried
    # an original phrase in a five-note mode (D F G A C): rising, a turn, and home
    notes = [(62, 0.55), (65, 0.45), (67, 0.8), (69, 0.4), (67, 0.4), (65, 0.9), (62, 1.2)]
    return _hum(g, notes, "m", 1.08, int(g.integers(1 << 30)), vib=10.0)


# --------------------------------------------------------------------------- Ch5: Pemakar, Ashcrown


def plume_crackle(g):  # "One... two... three." lightning crackling in the far plume of ash
    buf = _buf(3.0)
    for k in range(3):
        _place(buf, _crackle(g, 0.7, 140, 900) * float(g.uniform(0.5, 1.0)), 0.2 + k * 0.8)
    return filt(buf, [bq_lowpass(5000, 0.7)])


def plume_thunder(g):  # "Daro's at his anvil." the plume's thunder rolling down the mountain
    sec = 4.5
    n = int(sec * SR)
    t = np.arange(n) / SR
    y = _band(g, sec, 25, 400) * np.exp(-t / 1.4) * (0.5 + 0.5 * _slow(g, n, 5.0))
    return y * np.clip(t / 0.08, 0, 1)


def matron_bank(g):  # the Cinder Matron banking overhead: a vast wing turning the air, and her low breath
    sec = 3.0
    n = int(sec * SR)
    t = np.arange(n) / SR
    sweep = np.zeros(n)
    for k in range(0, n, 256):
        fc = 200 + 1200 * np.sin(np.pi * k / n)
        seg = filt(g.standard_normal(min(1024, n - k)), [bq_bandpass(fc, 0.8)])
        sweep[k: k + 256] += seg[: min(256, n - k)]
    sweep *= np.sin(np.pi * t / sec) ** 1.5
    breath = _band(g, sec, 40, 300) * np.sin(np.pi * t / sec) * 0.6
    return sweep + breath


def crown_bell(g):  # Lanternfall: the crown bell on the elder's boat, small and bright, once
    return tower_bell(79.0, 0.6, seed=int(g.integers(1 << 30)), t60=3.5, dark=0.2)


def weir_spill(g):  # the weir: terrace water spilling over the lip into the pool below
    sec = 5.0
    n = int(sec * SR)
    rush = _band(g, sec, 300, 6000) * (0.8 + 0.2 * _slow(g, n, 6.0)) * _shape(n, 0.8, 1.5)
    buf = rush * 0.6
    for _ in range(40):
        _place(buf, bubble(float(g.uniform(1.5, 5.0)), amp=0.3), float(g.uniform(0.2, sec - 0.5)))
    return buf


def anvil_crack(g):  # the Matron wakes: the great anvil-stone cracks, iron ringing in the split
    buf = _buf(3.0)
    _place(buf, _thump(g, 70, 0.8, 0.25) * 1.0, 0.0)
    n = int(0.08 * SR)
    _place(buf, filt(g.standard_normal(n), [bq_bandpass(1800, 0.7)]) * _env(n, 0.0005, 0.02), 0.0)
    _place(buf, _iron(g, 310, 2.8, 0.9) * 0.6, 0.02)
    return buf


# --------------------------------------------------------------------------- Ch6: the Brine Shoals


def barge_pole(g):  # the Reeds poling the barge through the smoke: wood creak and their footfalls, and NO water
    # (act1_ch06.md §6: the absence is the effect; brine_iron_hiss is B05's only water sound)
    buf = _buf(2.2)
    _place(buf, _creak(g, 0.7, 70, 260, ((280.0, 1.0), (690.0, 0.6), (1500.0, 0.25))) * 0.8, 0.1)  # the pole bending
    for k in range(3):  # bare feet stepping along the deck planks with the push
        at = 0.25 + 0.42 * k
        _place(buf, _thump(g, float(g.uniform(110, 140)), 0.15, 0.03) * 0.5, at)
        _place(buf, _wood(g, float(g.uniform(190, 240)), 0.2) * 0.25, at)
    _place(buf, _creak(g, 0.5, 90, 300, ((380.0, 1.0), (900.0, 0.5))) * 0.4, 1.3)  # the barge's planks settling
    return buf


def brine_iron_hiss(g):  # "Put the iron in the water, please." the branding iron quenched: a hiss and the steam
    sec = 3.0
    n = int(sec * SR)
    t = np.arange(n) / SR
    hiss = _band(g, sec, 2500, 9000) * np.exp(-t / 0.9) * np.clip(t / 0.02, 0, 1)
    steam = _band(g, sec, 400, 2500) * np.exp(-t / 1.4) * 0.4
    buf = hiss + steam
    for _ in range(30):
        _place(buf, bubble(float(g.uniform(0.8, 2.0)), amp=0.2), float(g.uniform(0.0, 1.2)))
    return buf


def tide_ambience(g):  # the burned lamp: the tide coming in over the mud flats, quiet, a long while
    sec = 9.0
    n = int(sec * SR)
    wash = _band(g, sec, 150, 2500) * (0.3 + 0.7 * _slow(g, n, 0.25)) * _shape(n, 1.5, 2.5) * 0.4
    return wash + _laps(g, sec, 1.8, 0.7) * _shape(n, 1.0, 2.5)


def stillguard_hum(g):  # the raid: the Stillguard humming the Order's congregational tune, calmly, a dozen men
    # (act1_ch06.md §6: the Order's existing hummed tune, so the player knows it: motifs.py ORDER_HUM)
    line = order_hum_in_seconds()
    voices = []
    for k in range(12):
        octave = -12.0 if k % 3 == 0 else 0.0
        notes = [(m + octave + float(g.normal(0, 0.06)), d * float(g.uniform(0.98, 1.02))) for m, d in line]
        voices.append(_hum(g, notes, "m", float(g.uniform(0.9, 1.0)), int(g.integers(1 << 30)), vib=5.0)
                      * float(g.uniform(0.5, 1.0)))
    n = min(len(v) for v in voices)
    y = sum(v[:n] for v in voices)
    return _room_tail(g, y * _shape(n, 0.6, 1.5), 1.6, 0.3)


def hatch_burst(g):  # a hatch kicked open from below: the bar splinters, the lid slams back
    buf = _buf(1.4)
    n = int(0.05 * SR)
    _place(buf, filt(g.standard_normal(n), [bq_bandpass(2200, 0.8)]) * _env(n, 0.0005, 0.015), 0.0)
    _place(buf, _wood(g, 150, 0.6) * 1.0, 0.0)
    _place(buf, _wood(g, 110, 0.7) * 1.0, 0.18)
    _place(buf, _thump(g, 80, 0.5, 0.12) * 0.8, 0.18)
    return buf


def raid_hound_bay(g):  # a raid hound baying: a deep, open-throated call that breaks at the end
    notes = [(50.0, 0.25), (57.0, 0.7), (55.0, 0.5), (48.0, 0.4)]
    y = sing([("o", 0.25), ("u", 0.7), ("o", 0.5), ("a", 0.4)], notes, vel=0.8, seed=int(g.integers(1 << 30)),
             scale=0.85, tilt=1.4, breath=0.25, vib_cents=40.0, vib_rate=6.5, jitter_cents=30.0, release=0.2)
    rough = 1 + 0.4 * np.sin(2 * np.pi * 34 * np.arange(len(y)) / SR)
    return _room_tail(g, y * rough, 1.2, 0.3)


def sail_pulled(g):  # "Not now." a sail pulled over Liss to hide her: heavy canvas dragged and settling
    buf = _buf(1.4)
    n = int(0.7 * SR)
    drag = _band(g, 0.7, 300, 3000) * np.sin(np.pi * np.arange(n) / n) ** 1.2
    _place(buf, drag * 0.8, 0.0)
    _place(buf, _thump(g, 100, 0.3, 0.06) * 0.4, 0.65)
    return buf


def camp_burn(g):  # "Somebody's cookfire." the salvage camp burning beyond the smoke, roaring and cracking
    sec = 7.0
    n = int(sec * SR)
    y = _fire(g, sec, 1.6) * _shape(n, 1.2, 2.0)
    _place(y, _wood(g, 120, 0.6) * 0.4, 3.1)  # a timber giving way in it
    return filt(y, [bq_lowpass(4500, 0.7)])


# --------------------------------------------------------------------------- Ch7: Tamsule


def crowd_warm(g):  # after the Bell: the crowd breathing out, warm talk, scattered clapping
    sec = 7.0
    n = int(sec * SR)
    buf = _crowd(g, sec, 22)
    for _ in range(60):
        k = int(0.012 * SR)
        clap = filt(g.standard_normal(k), [bq_bandpass(float(g.uniform(1200, 2500)), 1.2)]) * _env(k, 0.0005, 0.005)
        _place(buf, clap * float(g.uniform(0.1, 0.4)), float(g.uniform(0.2, 2.8)))
    return buf * _shape(n, 0.5, 2.0)


def mooring_ring(g):  # the empty moorings: an iron mooring ring lifted and let fall on the stone
    buf = _buf(2.2)
    _place(buf, _iron(g, 690, 2.0, 0.55) * 0.8, 0.0)
    _place(buf, _thump(g, 180, 0.2, 0.04) * 0.4, 0.0)
    return buf


def bell_hum_rise(g):  # the galleries: the Tamsule Bell's hum rising in its bowl, prime and tierce
    sec = 6.0
    n = int(sec * SR)
    t = np.arange(n) / SR
    y = np.zeros(n)
    for ratio, a in ((1.0, 1.0), (2.0, 0.4), (2.4, 0.3), (3.0, 0.15)):
        y += a * np.sin(2 * np.pi * 110.0 * ratio * t + float(g.uniform(0, 6.28)))
    return y * np.clip(t / 4.0, 0, 1) ** 2 * _shape(n, 0.1, 1.0) * (0.85 + 0.15 * np.sin(2 * np.pi * 0.7 * t))


def bell_crowd_roar(g):  # leaving Tamsule: the far crowd roaring the cup home, and the Bell under it
    sec = 7.0
    n = int(sec * SR)
    roar = _band(g, sec, 250, 2200) * (0.5 + 0.5 * _slow(g, n, 1.5)) * _shape(n, 1.0, 2.5)
    buf = filt(_crowd(g, sec, 30, False) + roar, [bq_lowpass(1800, 0.7)])
    _place(buf, tower_bell(45.0, 0.5, seed=int(g.integers(1 << 30)), t60=6.0, dark=0.6)[: n] * 0.5, 0.8)
    return buf


def column_weep(g):  # the naming: water weeping down the old column, thin trickles over stone
    sec = 6.0
    n = int(sec * SR)
    trickle = _band(g, sec, 1200, 6000) * (0.4 + 0.6 * _slow(g, n, 8.0)) * _shape(n, 1.0, 2.0) * 0.3
    buf = trickle
    for _ in range(25):
        _place(buf, drip(vel=0.3, radius_mm=float(g.uniform(1.0, 2.0)), seed=int(g.integers(1 << 30))) * 0.4,
               float(g.uniform(0.5, sec - 1.0)))
    return buf


def crowd_up(g):  # "Up." ten thousand people say the one word to a diver who should be surfacing
    buf = _buf(2.6)
    for k in range(40):
        y = sing([("u", 0.22), ("m", 0.08)], [(float(g.uniform(43, 55)), 0.22), (float(g.uniform(43, 55)), 0.08)],
                 vel=0.5, seed=int(g.integers(1 << 30)), scale=float(g.uniform(0.95, 1.2)), tilt=1.7, breath=0.15,
                 vib_cents=0.0, jitter_cents=15.0, release=0.1)
        _place(buf, y * float(g.uniform(0.3, 1.0)), float(g.normal(0.15, 0.05)) % 0.4)
    return _room_tail(g, filt(buf, [bq_lowpass(2200, 0.7)]), 2.5, 0.5)


# --------------------------------------------------------------------------- Ch8: Corrow


def beacon_roar(g):  # "turn_great_key": the great beacon catching, its flame roaring up the tower
    sec = 5.0
    n = int(sec * SR)
    t = np.arange(n) / SR
    whoomph = _thump(g, 55, 1.0, 0.3)
    y = _fire(g, sec, 2.0) * np.clip(t / 1.2, 0, 1) * _shape(n, 0.01, 1.5)
    _place(y, whoomph * 1.2, 0.0)
    return filt(y, [bq_lowpass(6000, 0.7)])  # the crackle's broadband pops overshoot between samples otherwise


def coast_bells(g):  # the beacon answered: bells along the coast, far and near, taking up the alarm
    buf = _buf(7.0)
    for k, (m, at, dark) in enumerate(((52.0, 0.6, 0.6), (57.0, 1.4, 0.5), (49.0, 2.3, 0.7), (60.0, 3.0, 0.6),
                                        (55.0, 3.9, 0.8))):
        b = tower_bell(m, 0.55, seed=int(g.integers(1 << 30)), t60=5.0, dark=dark)
        _place(buf, b * (0.9 - 0.12 * k), at)
    return buf


def surf_storm(g):  # Kerrid on the stair: the storm surf booming in against the seawall
    sec = 7.0
    n = int(sec * SR)
    buf = _band(g, sec, 80, 3000) * (0.4 + 0.6 * _slow(g, n, 0.5)) * _shape(n, 1.0, 2.0) * 0.5
    for at in (0.8, 3.4, 5.6):
        _place(buf, _thump(g, 45, 1.2, 0.4) * 0.9, at)
        _place(buf, _band(g, 1.5, 1500, 6000) * np.exp(-np.arange(int(1.5 * SR)) / SR / 0.5) * 0.3, at + 0.25)
    return buf


def rain_easing(g):  # after the rope: the rain easing off over Corrow, heavy to a few last drops
    sec = 8.0
    n = int(sec * SR)
    return _rain(g, sec, 1.0, 0.08) * _shape(n, 0.6, 1.5)


def hatchet_rope(g):  # "Cut it down." two hatchet blows on the hoist rope and the rope parting
    buf = _buf(2.0)
    for k in range(2):
        _place(buf, _wood(g, 260, 0.3) * 0.8, 0.1 + 0.55 * k)
        n = int(0.04 * SR)
        _place(buf, filt(g.standard_normal(n), [bq_bandpass(1800, 1.0)]) * _env(n, 0.0005, 0.01) * 0.6, 0.1 + 0.55 * k)
    n = int(0.15 * SR)
    twang = np.sin(2 * np.pi * np.cumsum(np.linspace(380, 120, n)) / SR) * _env(n, 0.001, 0.05)
    _place(buf, twang * 0.6 + _noise(g, 0.15, [bq_bandpass(2600, 0.8)], 0.001, 0.03)[:n] * 0.6, 1.22)
    return buf


def crowd_on_stair(g):  # "First down!" the stair-watch and the town running down the Fisher Stair
    sec = 5.0
    buf = _buf(sec)
    for _ in range(90):
        at = float(g.uniform(0.0, sec - 0.5))
        lvl = float(g.uniform(0.2, 0.7))
        _place(buf, _noise(g, 0.06, [bq_bandpass(float(g.uniform(1500, 3500)), 1.0)], 0.002, 0.02) * lvl, at)
        _place(buf, _thump(g, float(g.uniform(90, 140)), 0.1, 0.02) * 0.5 * lvl, at)
    buf += _crowd(g, sec, 14, False) * 0.6
    return buf * _shape(len(buf), 0.4, 1.2)


def watchers_pin(g):  # "Seat the pin." an iron pin hammered into the Watchers' stone mouths
    buf = _buf(1.2)
    _place(buf, _iron(g, 1150, 1.0, 0.35) * 1.0, 0.0)
    _place(buf, _thump(g, 210, 0.2, 0.03) * 0.5, 0.0)
    return buf


def hoist_block(g):  # the hoist's block taking the load: rope through the sheave, the block creaking
    buf = _buf(2.4)
    _place(buf, _creak(g, 1.6, 50, 240, ((320.0, 1.0), (840.0, 0.6), (1600.0, 0.3))), 0.0)
    n = int(1.8 * SR)
    _place(buf, _band(g, 1.8, 700, 2600) * np.sin(np.pi * np.arange(n) / n) * 0.25, 0.1)
    _place(buf, _wood(g, 230, 0.4) * 0.5, 1.7)
    return buf


def hearth_crackle(g):  # Fenn's hearth: a small fire crackling in a stone room
    sec = 5.0
    return _fire(g, sec, 0.7) * _shape(int(sec * SR), 0.8, 1.5)


def hearth_settle(g):  # "Not a log on a fire." the driftwood laid on, the embers settling under it
    buf = _buf(2.0)
    _place(buf, _wood(g, 280, 0.3) * 0.6, 0.0)
    _place(buf, _noise(g, 0.5, [bq_lowpass(700, 0.7)], 0.05, 0.2) * 0.5, 0.15)
    _place(buf, _crackle(g, 1.5, 25) * 0.8, 0.3)
    return buf


def gulls_far(g):  # landfall at Corrow: gulls far off over the harbour
    buf = _buf(5.0)
    for _ in range(4):
        _place(buf, gull_call(g) * float(g.uniform(0.4, 1.0)), float(g.uniform(0.0, 3.0)))
    return _room_tail(g, filt(buf, [bq_lowpass(2500, 0.7), bq_highpass(400, 0.7)]), 1.5, 0.4)


def shield_dropped(g):  # Ivo runs to Toma: the shield let go, clattering on the stone
    buf = _buf(1.6)
    _place(buf, _wood(g, 170, 0.5) * 1.0, 0.0)
    _place(buf, _iron(g, 620, 1.0, 0.3) * 0.4, 0.0)
    _place(buf, _wood(g, 200, 0.3) * 0.5, 0.22)
    _place(buf, _wood(g, 240, 0.25) * 0.3, 0.36)
    return buf


def wind_landward(g):  # the run back: the storm wind turning landward, a hard rising gust
    sec = 6.0
    return _wind(g, sec, 1.0, 1.5, 2.0)


def kite_torn(g):  # a child's kite torn away: the paper ripping, a flutter going up and away
    buf = _buf(1.8)
    n = int(0.25 * SR)
    rip = filt(g.standard_normal(n), [bq_bandpass(3500, 0.9)]) * (0.5 + 0.5 * (g.random(n) < 0.3)) * _env(n, 0.01, 0.1)
    _place(buf, rip, 0.0)
    m = int(1.3 * SR)
    flutter = _band(g, 1.3, 400, 2500) * np.abs(np.sin(2 * np.pi * 14 * np.arange(m) / SR)) * np.linspace(1, 0, m)
    _place(buf, flutter * 0.6, 0.2)
    return buf


def spire_door(g):  # "The Lady Cantor's guardians may attend her." the spire's heavy door: latch, a long creak
    buf = _buf(3.5)
    _place(buf, _iron(g, 820, 0.5, 0.15) * 0.6, 0.0)
    _place(buf, _creak(g, 2.0, 25, 120, ((140.0, 1.0), (360.0, 0.6), (800.0, 0.2))) * 0.9, 0.3)
    _place(buf, _thump(g, 70, 0.6, 0.18) * 0.6, 2.3)
    return _room_tail(g, buf, 1.8, 0.35)


def asha_hum_lullaby(g):  # Asha kneels by the boy on the wall and hums: soft, close, a lullaby's rocking
    # an original rocking figure in a five-note mode (G A B D E): two rocking phrases and a falling close
    notes = [(67, 0.6), (69, 0.4), (71, 0.9), (69, 0.5), (67, 0.9),
             (71, 0.6), (74, 0.4), (71, 0.6), (69, 0.6), (67, 1.4)]
    return _hum(g, notes, "m", 1.2, int(g.integers(1 << 30)), vib=8.0)


def pell_storm_note(g):  # Pell's Storm-Call: one huge low note from a throat, rising and falling: a voice doing a storm
    # (act1_ch08.md §6: clearly a voice, never the weather; built from the synth voice, a growl under it)
    notes = [(38.0, 0.6), (47.0, 1.6), (50.0, 0.8), (41.0, 1.6)]
    phon = [("u", 0.6), ("o", 1.6), ("a", 0.8), ("u", 1.6)]
    y = sing(phon, notes, vel=0.9, seed=int(g.integers(1 << 30)), scale=0.82, tilt=1.3, breath=0.35, vib_cents=55.0,
             vib_rate=3.2, jitter_cents=35.0, release=0.5)
    t_ = np.arange(len(y)) / SR
    rough = 1 + 0.5 * np.sin(2 * np.pi * 27 * t_) * (0.5 + 0.5 * np.sin(2 * np.pi * 0.4 * t_))  # the throat's rasp
    breath = _band(g, len(y) / SR, 300, 2500) * np.abs(y).max() * 0.08 * _shape(len(y), 0.8, 1.0)
    return _room_tail(g, y * rough + breath, 2.2, 0.3)


def flue_key_free(g):  # "She wants oil, not muscle." the seized flue key easing, then turning free with a clunk
    buf = _buf(2.2)
    _place(buf, _creak(g, 1.1, 18, 70, ((180.0, 1.0), (460.0, 0.6), (1100.0, 0.3))) * 0.8, 0.0)
    _place(buf, _iron(g, 380, 1.0, 0.3) * 0.8, 1.15)
    _place(buf, _thump(g, 100, 0.3, 0.05) * 0.6, 1.15)
    return buf


def reach_rises(g):  # Undertow's Reach rising out of the sea at the wall: the water heaved up and pouring off
    sec = 5.5
    n = int(sec * SR)
    heave = _roar(g, sec, 30, 500, 1.6, 2.0, 0.3)
    pour = _band(g, sec, 800, 5000) * np.clip((np.arange(n) / SR - 1.4) / 1.0, 0, 1) * _shape(n, 0.01, 2.0) * 0.4
    return heave + pour


def reach_grips(g):  # "Hold." the Reach takes hold of the seawall: stone grinding under it, a wet slap
    buf = _buf(2.6)
    _place(buf, _splash(g, 1.2, 1.6) * 0.6, 0.0)
    _place(buf, _creak(g, 1.6, 15, 60, ((90.0, 1.0), (240.0, 0.6), (520.0, 0.3))) * 0.9, 0.2)
    return buf


def wall_breach(g):  # the seawall breaks: the stone going, and the sea through the gap
    buf = _buf(6.0)
    _place(buf, _thump(g, 40, 1.5, 0.5) * 1.0, 0.0)
    for _ in range(8):
        _place(buf, _wood(g, float(g.uniform(70, 120)), 0.5) * float(g.uniform(0.3, 0.7)), float(g.uniform(0.1, 1.2)))
    _place(buf, _roar(g, 5.0, 40, 1200, 0.6, 1.8, 0.4) * 0.8, 0.8)
    return buf


def current_song(g):  # B17, from Rhen's position only: Dace's current-song, one unaccompanied low voice in the storm
    # The whole tune, the same notes as Ch1's statement (assets_src/music/motifs.py CURRENT_SONG), an octave down.
    vowels = ("o", "a", "o", "u", "a", "o", "u")
    out = []
    for phrase in phrases_in_seconds():
        notes = [(m - 12.0, d) for m, d in phrase]
        phon = [(vowels[i % len(vowels)], d) for i, (_, d) in enumerate(notes)]
        out.append(sing(phon, notes, vel=0.55, seed=int(g.integers(1 << 30)), scale=0.9, tilt=1.8, breath=0.12,
                        vib_cents=16.0, vib_rate=4.6, jitter_cents=6.0, release=0.4))
        out.append(np.zeros(int(0.45 * SR)))  # his breath
    y = np.concatenate(out)
    return _room_tail(g, filt(y, [bq_lowpass(1800, 0.7)]), 3.0, 0.5)


def stone_falls(g):  # Kerrid catches Rhen's collar as the stone goes: blocks breaking away and falling
    buf = _buf(3.5)
    for k in range(5):
        at = 0.1 + k * float(g.uniform(0.25, 0.45))
        _place(buf, _thump(g, float(g.uniform(60, 110)), 0.6, 0.15) * float(g.uniform(0.6, 1.0)), at)
        _place(buf, _noise(g, 0.2, [bq_bandpass(1500, 0.8)], 0.001, 0.06) * 0.4, at)
    for _ in range(40):
        _place(buf, _noise(g, 0.02, [bq_bandpass(float(g.uniform(2000, 5000)), 1.5)], 0.0005, 0.006)
               * float(g.uniform(0.1, 0.4)), float(g.uniform(0.2, 2.5)))
    return buf


def gate_bar(g):  # the gatekeeper opens the wall gate: the bar drawn back through its brackets, a thunk
    buf = _buf(1.8)
    n = int(0.8 * SR)
    _place(buf, _band(g, 0.8, 300, 2200) * np.sin(np.pi * np.arange(n) / n) * 0.5, 0.0)
    _place(buf, _creak(g, 0.8, 60, 200, ((260.0, 1.0), (640.0, 0.5))) * 0.4, 0.0)
    _place(buf, _wood(g, 130, 0.6) * 0.9, 0.85)
    return buf


# --------------------------------------------------------------------------- Ch9: the Ebbing


def shingle_kneel(g):  # Rhen kneels on the shingle: pebbles shifting and crunching under the knee
    buf = _buf(1.2)
    for _ in range(28):
        _place(buf, modal([float(g.uniform(1800, 4200))], [0.01], [1.0], 0.03, g, click=0.4) * float(g.uniform(0.2, 0.7)),
               float(g.uniform(0.0, 0.5)))
    _place(buf, _thump(g, 110, 0.2, 0.04) * 0.4, 0.25)
    return buf


def raft_pole(g):  # Asha poling the raft out across the harbour, slow and level: the plunge, the push, the drag
    buf = _buf(1.8)
    _place(buf, _noise(g, 0.12, [bq_lowpass(1100, 0.7)], 0.003, 0.05) * 0.7, 0.0)
    for _ in range(10):
        _place(buf, bubble(float(g.uniform(2.5, 6.0)), amp=float(g.uniform(0.2, 0.6))), float(g.uniform(0.0, 0.3)))
    _place(buf, _band(g, 1.0, 250, 900) * np.sin(np.linspace(0, np.pi, int(1.0 * SR))) * 0.4, 0.3)
    _place(buf, _creak(g, 0.4, 100, 320, ((300.0, 1.0), (720.0, 0.5))) * 0.3, 0.5)
    return buf


def staff_bell_shells(g):  # the Ebbing: Asha's staff raised, its bell-shells shivering together
    # pitched in the cue's key (the_ebbing.py: A minor, its pentatonic A C D E G): every shell and both bells on it
    penta = [1760.0, 2093.0, 2349.3, 2637.0, 3136.0, 3520.0]  # A6 C7 D7 E7 G7 A7
    buf = _buf(2.6)
    for _ in range(int(g.integers(9, 14))):
        f = penta[int(g.integers(0, len(penta)))] * float(g.uniform(0.998, 1.002))
        _place(buf, modal([f, f * 2.0, f * 3.0], [0.08, 0.035, 0.015], [1.0, 0.3, 0.1], 0.3, g, click=0.2)
               * float(g.uniform(0.2, 0.7)), float(g.uniform(0.0, 0.9)))
    for m, at in ((81.0, 0.1), (88.0, 0.35)):  # A5 and E6
        _place(buf, tower_bell(m, 0.3, seed=int(g.integers(1 << 30)), t60=1.8, dark=0.3)[: int(2.0 * SR)] * 0.25, at)
    return buf


def harbour_lap(g):  # the harbour after the Ebbing: water lapping at the moorings, nothing else
    sec = 8.0
    n = int(sec * SR)
    return _laps(g, sec, 1.4, 0.9) * _shape(n, 1.0, 2.5)


# (id, builder, momentary-max target LUFS)
CUES = [
    ("splash", splash, -18.0), ("bell_room_drip", bell_room_drip, -26.0), ("raft_lashing_snap", raft_lashing_snap, -18.0),
    ("salvage_cut", salvage_cut, -21.0), ("undertow_wall_roar", undertow_wall_roar, -16.0),
    ("beacon_lamp_gutter", beacon_lamp_gutter, -22.0), ("lintel_gull_cry", lintel_gull_cry, -19.0),
    ("hullgnaw_ribs_creak", hullgnaw_ribs_creak, -18.0), ("scale_weigh", scale_weigh, -22.0),
    ("chit_stamp", chit_stamp, -21.0), ("tether_run", tether_run, -20.0),
    ("gangplank", gangplank, -19.0), ("wake_lamps_out", wake_lamps_out, -25.0),
    ("name_board_prise", name_board_prise, -20.0), ("sails_luff_and_fall", sails_luff_and_fall, -19.0),
    ("lookout_call", lookout_call, -19.0), ("derelict_wheel_turning", derelict_wheel_turning, -20.0),
    ("shell_set", shell_set, -23.0), ("ink_brush", ink_brush, -27.0), ("neme_humming", neme_humming, -24.0),
    ("plume_crackle", plume_crackle, -22.0), ("plume_thunder", plume_thunder, -18.0),
    ("matron_bank", matron_bank, -17.0), ("crown_bell", crown_bell, -20.0), ("weir_spill", weir_spill, -23.0),
    ("anvil_crack", anvil_crack, -16.0),
    ("barge_pole", barge_pole, -22.0), ("brine_iron_hiss", brine_iron_hiss, -20.0),
    ("tide_ambience", tide_ambience, -25.0), ("stillguard_hum", stillguard_hum, -21.0),
    ("hatch_burst", hatch_burst, -17.0), ("raid_hound_bay", raid_hound_bay, -17.0), ("sail_pulled", sail_pulled, -22.0),
    ("camp_burn", camp_burn, -22.0),
    ("crowd_warm", crowd_warm, -22.0), ("mooring_ring", mooring_ring, -22.0), ("bell_hum_rise", bell_hum_rise, -20.0),
    ("bell_crowd_roar", bell_crowd_roar, -21.0), ("column_weep", column_weep, -26.0), ("crowd_up", crowd_up, -19.0),
    ("beacon_roar", beacon_roar, -18.0), ("coast_bells", coast_bells, -19.0), ("surf_storm", surf_storm, -19.0),
    ("rain_easing", rain_easing, -23.0), ("hatchet_rope", hatchet_rope, -19.0), ("crowd_on_stair", crowd_on_stair, -20.0),
    ("watchers_pin", watchers_pin, -18.0), ("hoist_block", hoist_block, -21.0), ("hearth_crackle", hearth_crackle, -25.0),
    ("hearth_settle", hearth_settle, -24.0), ("gulls_far", gulls_far, -25.0), ("shield_dropped", shield_dropped, -18.0),
    ("wind_landward", wind_landward, -19.0), ("kite_torn", kite_torn, -21.0), ("spire_door", spire_door, -19.0),
    ("asha_hum_lullaby", asha_hum_lullaby, -24.0), ("pell_storm_note", pell_storm_note, -19.0),
    ("flue_key_free", flue_key_free, -20.0), ("reach_rises", reach_rises, -16.0), ("reach_grips", reach_grips, -17.0),
    ("wall_breach", wall_breach, -15.0), ("current_song", current_song, -22.0), ("stone_falls", stone_falls, -17.0),
    ("gate_bar", gate_bar, -20.0),
    ("shingle_kneel", shingle_kneel, -23.0), ("raft_pole", raft_pole, -22.0),
    ("staff_bell_shells", staff_bell_shells, -21.0), ("harbour_lap", harbour_lap, -25.0),
]
FILES = [f"{name}.ogg" for name, _, _ in CUES]


def render(out_dir: str = OUT_DIR, verbose: bool = True) -> dict:
    os.makedirs(out_dir, exist_ok=True)
    res = {}
    for name, fn, target in CUES:
        x = _tail_fade(np.asarray(fn(_g(name)), dtype=np.float64), 0.05)
        x = normalize_momentary(x, target, ceiling_db=CEILING)
        write_ogg(os.path.join(out_dir, name + ".ogg"), x, quality=4.0)
        m = measure(x)
        res[name] = m
        if verbose:
            print(f"{name}: {m['seconds']:.2f}s  momentary max {m['momentary_max_lufs']:.2f} LUFS  "
                  f"peak {m['sample_peak_dbfs']:.2f} dBFS")
    return res


if __name__ == "__main__":
    render()
