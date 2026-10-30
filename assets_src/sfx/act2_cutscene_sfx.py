"""Act II cutscene sounds: every `@sfx` the Act II scripts name (M4-A2P-093; the Act II audit's "Cutscenes",
tools/audio/act1_audio_audit.py --act 2; plain git, ADR 0175).

Each is made from what its line in the script shows (game/data/dialogue/ch1x/*.dlg):

    egret_lift          ch10_dead_channel: a fen egret lifts off the dead channel: wingbeats, drips falling, a croak
    lamp_seat           ch11_lamp_bench: Liss seats the burner and lights the housing: a twist, the click home, the
                        flame catching, the glass warming to a ring
    engine_tick         ch11_the_engine: the Lamp Engine in the silence before it wakes: a slow ratchet and its hum
    pole_no_wake        ch13_still_city: a pole stroke on Ansedra's held water that makes no wake: the wood's knock,
                        and none of the water's answer (a short, dead dip; no drips, no lapping)
    pole_stroke         ch14_first_ripple: Merel's stroke, the first ripple in four hundred years: the plunge, the
                        swirl, and the ring spreading out as lapping that widens
    stirring_bells      ch14_first_ripple: the city's bells waking one by one across the water (they sit in space as
                        SFX; lagoon_escape carries the music), shutters opening along the canal
    water_gate_drop     ch14_first_ripple: Merel pulls the pin: iron gives, the chain runs, the gate falls into water
    level_pin_ring      ch14_the_vows: Ysolde takes the level pin out: one fine, bright ring that will not stop
    pyre_crackle        ch15_pyre_raft: the raft pushed off: its fire crackling over water, the raft's wood grating
    lamp_housing_close  ch15_pyre_raft: the housing shut on the motes: the brass hinge, the latch, the bound hum
    lamp_crack          ch15_pyre_raft: the lamp's glass cracks and one mote is let out: the crack, its ring, a breath
    kerrid_sits         ch15_the_shoal: Kerrid sits down on the deck, heavily: cloth, the planking taking him, a breath
    storm_wall          ch16_swept_away: the sea standing up: a roar growing into a wall (the Undertow's family, larger)
    current_song_hum    ch16_swept_away: Liss humming the current-song under the storm (CURRENT_SONG, motifs.py),
                        one voice, the first phrase; the script plays it at vol=0.3
    kesh_rise           ch16_the_choir: Kesh rising in the memory: the stones' low groan lifting, and six colours chained
                        (fire, water, lightning, glimmer, holy and a cold glass), as kesh_bound's
    barge_no_wake       ch16_the_choir: the High Warden's barge gliding on flattened water: a low hull creak, a pressure
                        hum, no water at all

    fin_cut             ch15_the_fin: the Wakefin's first pass in the dark (act2_skill_sfx.py's fin_cut, at the
                        cutscene's level)

Synthesized here and in tools/audio/synth/ (SPEC §2, §9). Files are assets/audio/sfx/<id>.ogg (mono, q4; plain git), where
the CutsceneSequencer looks for an `@sfx` (sequencer.json sfx_dir) as Act I's are (act1_cutscene_sfx.py), so a cue
plays with or without Audio's rows; each at its own momentary max (the cutscene foley's levels, -19 to -30).

Render:  python3 tools/audio/render_all.py --only act2_cutscene_sfx
"""
from __future__ import annotations

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools", "audio"))
sys.path.insert(0, os.path.join(ROOT, "assets_src", "music"))
sys.path.insert(0, HERE)

import numpy as np  # noqa: E402

import act2_creature_sfx as A2  # noqa: E402
import act2_skill_sfx as SK  # noqa: E402
from act2_creature_sfx import Engine, splash, whoosh  # noqa: E402
from creature_sfx import (WOOD, beats, buf, burst, crackle, creak, finish, glass_ring, gurgle, room, slosh,  # noqa: E402
                          tap, thump)
from motifs import CURRENT_SONG, CURRENT_SONG_BPM  # noqa: E402
from synth.bells import tower_bell  # noqa: E402
from synth.dsp import SR, bq_bandpass, bq_highpass, bq_lowpass, filt, rng  # noqa: E402
from synth.mixer import measure, write_ogg  # noqa: E402
from synth.voice import hum_ensemble  # noqa: E402
from synth.water import drip  # noqa: E402
from underwater_sfx import _n, _t, noise, place  # noqa: E402

OUT_DIR = os.path.join(ROOT, "assets", "audio", "sfx")
SEED = 20262500
QUALITY = 4.0
DECK = [(f * 0.8, a) for f, a in WOOD]                       # a barge's planking


def _unit(x: np.ndarray) -> np.ndarray:
    return x / (np.abs(x).max() + 1e-9)


def _band(g, sec: float, sections, env) -> np.ndarray:
    n = _n(sec)
    return _unit(noise(g, n, sections)) * env(_t(n), sec)


def _drips(g, x, n: int, t0: float, t1: float, amp: float = 0.4) -> None:
    for _ in range(n):
        place(x, drip(0.3, float(g.uniform(1.4, 2.6)), seed=int(g.integers(1 << 30))), float(g.uniform(t0, t1)),
              float(g.uniform(0.4, 1.0)) * amp)


def egret_lift(g):
    x = buf(2.6)
    place(x, slosh(g, 0.4, 0.5, 3.0), 0.0)                      # feet leaving the water
    place(x, beats(g, 7, 3.2, 900, 0.8, 0.6, 0.2, decay=0.85, rate_end=2.4), 0.05)
    _drips(g, x, 9, 0.15, 1.3, 0.5)
    croak = A2.throat(g, 0.25, A2.contour(380, 420, 300, 0.4), [(900, 200, 1.0), (2100, 400, 0.4)], rough=0.6, sub=0.0,
                      breath=0.3, jitter=0.04, attack=0.01, release=0.08, tilt=1.0)
    place(x, croak, 0.55, 0.5)
    return x


def lamp_seat(g):
    x = buf(2.4)
    place(x, A2.burst(g, 0.18, [bq_bandpass(2400, 1.2)], 0.03, 0.04), 0.0, 0.4)    # the twist
    place(x, tap(g, [2200.0, 3600.0, 5100.0], [0.03, 0.02, 0.012], 0.9, 0.9), 0.2)   # home
    flame = _band(g, 0.9, [bq_bandpass(700, 0.6), bq_lowpass(2500, 0.7)],
                  lambda t, s: np.clip(t / 0.08, 0, 1) * np.exp(-t / 0.35))
    place(x, flame, 0.55, 0.6)                                   # catching
    place(x, glass_ring(g, 1568.0, 1.6, 0.35) * np.clip(_t(_n(1.6)) / 0.6, 0, 1), 0.7)
    return x


def engine_tick(g):
    x = buf(3.4)
    place(x, A2.hum(g, 3.2, 98.0, 0.35), 0.0)
    for k in range(6):                                          # slow, regular, waiting
        place(x, Engine.ratchet(g, 0.12, 6, 6, 0.6), 0.2 + 0.5 * k)
    return x


def pole_no_wake(g):
    x = buf(1.8)
    place(x, tap(g, [f for f, _ in DECK], [0.04, 0.03, 0.02, 0.01], 0.6, 0.5), 0.0)  # the pole's wood
    dip = _band(g, 0.18, [bq_lowpass(900, 0.7)], lambda t, s: np.sin(np.pi * t / s) ** 2)
    place(x, dip, 0.3, 0.25)                                    # a dull dip, and then nothing
    return x


def pole_stroke(g):
    x = buf(5.6)
    place(x, tap(g, [f for f, _ in DECK], [0.04, 0.03, 0.02, 0.01], 0.5, 0.5), 0.0)
    place(x, splash(g, 0.6, 0.6, 1400), 0.25)                   # the plunge
    place(x, gurgle(g, 0.8, 12, 0.008, 0.02, 0.5), 0.4)         # the swirl off the blade
    for k in range(6):                                          # the ring going out: lapping that widens and slows
        place(x, slosh(g, 0.7 + 0.15 * k, 0.6 - 0.07 * k, 2.4 - 0.25 * k), 1.0 + 0.7 * k)
    _drips(g, x, 6, 0.6, 1.6, 0.4)
    return x


def stirring_bells(g):
    x = buf(9.0)
    for k, (m, at) in enumerate(((55, 0.0), (60, 1.1), (52, 2.0), (64, 2.8), (57, 3.7))):   # one by one, far
        b = tower_bell(m, 0.6 - 0.04 * k, seed=SEED + 600 + k, t60=6.0, dark=0.6)
        place(x, _unit(filt(b, [bq_lowpass(3200, 0.7)])) * (0.8 - 0.08 * k), at)
    for at in (1.6, 3.2, 4.4):                                  # shutters opening along the canal
        place(x, creak(g, 0.35, 60, 200, DECK, 0.3), at)
        place(x, tap(g, [f * 1.4 for f, _ in DECK], [0.03, 0.02, 0.015, 0.01], 0.3, 0.6), at + 0.33)
    return x


def water_gate_drop(g):
    x = buf(4.0)
    place(x, tap(g, [820.0, 2100.0, 3900.0], [0.12, 0.06, 0.03], 0.9, 0.9), 0.0)     # the pin out
    chain = A2.train(g, 0.8, 16, 28, [700, 1500, 3100], [0.02, 0.012, 0.008], 0.9, 0.06, 0.7)
    place(x, chain, 0.25, 0.7)                                  # the chain running
    place(x, thump(g, 70, 30, 0.35, 0.6, 1.2), 1.05, 1.0)       # the gate into the water
    place(x, splash(g, 1.6, 1.0, 1800), 1.05)
    place(x, slosh(g, 2.0, 0.8, 1.2), 1.4)
    return x


def level_pin_ring(g):
    x = buf(3.2)
    place(x, tap(g, [1200.0, 2600.0], [0.02, 0.01], 0.4, 0.8), 0.0)
    place(x, glass_ring(g, 3520.0, 3.0, 0.8), 0.02)              # fine and long
    place(x, glass_ring(g, 3520.0 * 2.76, 1.2, 0.5), 0.02, 0.4)
    return x


def pyre_crackle(g):
    x = buf(4.4)
    fire = crackle(g, 4.0, 18, 3400, 0.8, 0.2)
    roar = _band(g, 4.0, [bq_bandpass(500, 0.6), bq_lowpass(1500, 0.7)],
                 lambda t, s: 0.6 + 0.4 * np.sin(np.pi * np.clip(t / s, 0, 1)))
    place(x, 0.7 * fire + 0.5 * roar, 0.2)
    place(x, creak(g, 0.8, 30, 100, DECK, 0.6), 0.0)            # the raft grating off
    place(x, slosh(g, 3.0, 0.5, 1.0), 0.4)
    for _ in range(5):                                          # embers hissing on the sea
        at = float(g.uniform(1.0, 3.6))
        place(x, _band(g, 0.25, [bq_bandpass(3600, 1.5)], lambda t, s: np.exp(-t / 0.07)), at, 0.25)
    return x


def lamp_housing_close(g):
    x = buf(2.4)
    place(x, creak(g, 0.3, 90, 260, [(1100.0, 1.0), (2400.0, 0.5)], 0.5), 0.0)       # the brass hinge
    place(x, A2.clang(g, 0.7, 0.5, 0.4), 0.3)                   # shut
    place(x, tap(g, [2600.0, 4100.0], [0.02, 0.012], 0.7, 0.9), 0.36)                # the latch
    place(x, A2.hum(g, 1.8, 196.0, 0.3) * np.clip(_t(_n(1.8)) / 0.4, 0, 1), 0.4)     # bound: a steady hum
    return x


def lamp_crack(g):
    x = buf(2.8)
    place(x, crackle(g, 0.12, 1800, 4200, 0.9, 0.03), 0.0)
    place(x, glass_ring(g, 2350.0, 1.4, 0.6), 0.01)
    breath = _band(g, 1.6, [bq_bandpass(1200, 0.8), bq_lowpass(4000, 0.7)],
                   lambda t, s: np.sin(np.pi * np.clip(t / s, 0, 1)) ** 2)
    place(x, breath, 0.15, 0.25)                                # one mote let out: a held breath leaving
    return x


def kerrid_sits(g):
    x = buf(2.4)
    place(x, A2.whoosh(g, 0.5, 400, 1400, 0.4), 0.0)             # cloth
    place(x, thump(g, 110, 60, 0.08, 0.3, 0.4), 0.45, 0.8)      # down
    place(x, creak(g, 0.7, 30, 110, DECK, 0.6), 0.48)           # the planking takes him
    sigh = _band(g, 0.9, [bq_bandpass(600, 0.7), bq_lowpass(2000, 0.7)],
                 lambda t, s: np.sin(np.pi * np.clip(t / s, 0, 1)) ** 1.5)
    place(x, sigh, 1.1, 0.3)
    return x


def storm_wall(g):
    x = buf(4.6)
    n = _n(4.2)
    t = _t(n)
    grow = np.clip(t / 3.0, 0, 1) ** 1.6
    low = _unit(noise(g, n, [bq_lowpass(380, 0.7), bq_highpass(30, 0.7)]))
    mid = _unit(noise(g, n, [bq_bandpass(900, 0.5)])) * A2.smooth_noise(n, 3.0, g) ** 2
    hiss = _unit(noise(g, n, [bq_highpass(2500, 0.7), bq_lowpass(7000, 0.7)]))
    place(x, (1.0 * low + 0.6 * mid + 0.35 * hiss) * grow, 0.0)
    place(x, thump(g, 45, 28, 0.9, 0.2, 2.0), 2.6, 0.8)          # it stands up
    return x


def current_song_hum(g):
    beat = 60.0 / CURRENT_SONG_BPM
    line = [(float(m), d * beat) for m, d in CURRENT_SONG[0]]
    h = hum_ensemble(line, voices=1, seed=SEED + 1400, register="high", spread=0.0, breath_every=(30.0, 40.0))
    y = h.mean(axis=1)
    return filt(y, [bq_highpass(140, 0.7), bq_lowpass(3200, 0.7)])


def kesh_rise(g):
    x = buf(5.4)
    n = _n(4.6)
    t = _t(n)
    f = 38.0 * 2 ** (t / 4.6 * 1.0)                              # the stones' groan rising an octave
    ph = 2 * np.pi * np.cumsum(f) / SR
    groan = (np.sin(ph) + 0.5 * np.sin(2.01 * ph) + 0.25 * np.sin(3.02 * ph)) * np.sin(np.pi * t / 4.6) ** 1.2
    place(x, _unit(groan) * 0.8, 0.0)
    colours = [crackle(g, 0.3, 40, 2600, 0.9, 0.1),               # fire
               slosh(g, 0.4, 0.8, 3.0),                          # water
               _band(g, 0.2, [bq_highpass(3000, 0.7)], lambda t, s: (np.sin(2 * np.pi * 37 * t) > 0) * np.exp(-t / 0.06)),
               glass_ring(g, 2637.0, 0.6, 0.6),                  # glimmer
               _unit(tower_bell(76, 0.5, seed=SEED + 1500, t60=1.5, dark=0.3)[: _n(0.8)]) * 0.5,   # holy
               glass_ring(g, 3951.0, 0.5, 0.5)]                  # cold glass
    for k, c in enumerate(colours):
        place(x, c, 0.9 + 0.5 * k, 0.6)
    return x


def barge_no_wake(g):
    x = buf(4.4)
    place(x, A2.hum(g, 4.0, 49.0, 0.4) * np.sin(np.pi * np.clip(_t(_n(4.0)) / 4.0, 0, 1)), 0.0)   # the pressure
    for at in (0.6, 2.1, 3.2):
        place(x, creak(g, 0.6, 20, 70, DECK, 0.4), at)
    return x


# name -> (fn, momentary max): the cutscene foley's levels (act1_cutscene_foley.py), louder for the set pieces
SFX: list[tuple[str, object, float]] = [
    ("egret_lift", egret_lift, -24.0), ("lamp_seat", lamp_seat, -26.0), ("engine_tick", engine_tick, -25.0),
    ("pole_no_wake", pole_no_wake, -30.0), ("pole_stroke", pole_stroke, -24.0), ("stirring_bells", stirring_bells, -21.0),
    ("water_gate_drop", water_gate_drop, -19.0), ("level_pin_ring", level_pin_ring, -28.0),
    ("pyre_crackle", pyre_crackle, -23.0), ("lamp_housing_close", lamp_housing_close, -25.0),
    ("lamp_crack", lamp_crack, -26.0), ("kerrid_sits", kerrid_sits, -26.0), ("storm_wall", storm_wall, -19.0),
    ("current_song_hum", current_song_hum, -24.0), ("kesh_rise", kesh_rise, -21.0),
    ("barge_no_wake", barge_no_wake, -27.0), ("fin_cut", SK.fin_cut, -22.0),
]
FILES = [f"{name}.ogg" for name, _, _ in SFX]


def render(out_dir: str = OUT_DIR, verbose: bool = True) -> dict:
    os.makedirs(out_dir, exist_ok=True)
    res = {}
    for i, (name, fn, tgt) in enumerate(SFX):
        seed = SEED + 100 * i
        x = finish(room(fn(rng(seed)), seed + 7, mix=0.15, tail=0.6, rt60=1.2), tgt)
        write_ogg(os.path.join(out_dir, f"{name}.ogg"), x, quality=QUALITY)
        res[name] = m = measure(x)
        if verbose:
            print(f"{name}: {m['seconds']:.2f}s  Mmax {m['momentary_max_lufs']:.2f}  TP {m['true_peak_dbtp']:.2f}",
                  flush=True)
    return res


if __name__ == "__main__":
    render()
