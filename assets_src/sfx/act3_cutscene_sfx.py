"""Act III cutscene sounds: every `@sfx` the Act III drafts name that no row plays yet (M5-A3P-1953;
docs/kb/story/act3/drafts/; plain git, ADR 0208). Four more of the drafts' ids are the Kite's own foley
(kite_foley.py, M3-AUD-859) and have alias rows in sfx_act3.json instead: kite_engines_stop, sails_fill,
rope_creak, hull_meets_water.

Each is made from what its line in the draft shows:

    sea_flat_lap        ch17_pulled_from_the_sea: after the storm, the sea gone flat: slow, small laps on a hull, and
                        nothing else (no wind, no gulls; the first quiet after Ch16)
    names_murmured      ch18_backs_to_the_water: Haluna with its backs to the water, saying its dead's names under
                        its breath: many low voices, wordless and overlapping, never a word clear
    clutch_hum          ch18_farewell_tide_taught: the Kirru clutch humming as Asha learns the tune: the clutch's own
                        wordless line (act2_ambience.py `clutch_line`, the Kirru mode), a few voices, close
    velamir_lullaby_hum ch18_farewell_tide_taught (Asha) and ending_imra (Imra): the Velamir lullaby hummed, the first
                        verse's first two lines (hush_first_verse.py VERSE) on a closed-mouth "m", one woman's voice,
                        close, no words (N-11: the women of the line hum it without the words)
    sails_fill          (alias, kite_sail_fill)
    shell_into_water    ch18_through_the_gate: Pell throws the old shell into the lagoon: a small plunk, a ring of
                        lapping, and the shell's clack against a stone going down
    engine_hum_stops    ch19_the_engine_stops: Iskarra's spire engine stopping on Liss's last lever: its deep bound
                        hum sinking and slowing to nothing, a ratchet running down, the last knock
    rope_slips          ch19_the_hitch: Kerrid's hitch: "one pull, and it lets go": the knot spilling with a soft
                        rip of fibre, the tail running through and dropping slack on the planks
    kite_settles        ch19_the_kite_comes_down: the Kite settling on the drowned plaza: its engines idling down
                        to a hum, the hull taking the stone with a long creak, the rigging slackening
    kite_engine_strains ch20_down_the_eye: the Kite going down the maelstrom's throat: both engines labouring a fifth
                        over their idle, the vanes beating unevenly, the hull complaining
    kite_touches_floor  ch20_down_the_eye: the Kite touching the Undertow's first floor: a soft, deep contact, the
                        keel grinding on held light (glassy, not stone), then stillness
    pell_farewell_tide  ch20_nhoa_release: Pell sings the farewell-tide for Nhoa: one low man's voice on the clutch's
                        rising line (reedhollow.py CLUTCH), open "a", over farewell_tide's music
    match_struck        ending_first_lamp: someone lights the first oil lamp with Mother Kell's wick: the scratch,
                        the flare, the small steady flame catching (Ch1's warmth, the only warm sound)
    wind_in_sails       ending_the_kite_comes_down: the Kite gliding dark on sail alone: wind in the canvas, the
                        sheets humming, no engines

Render:  python3 tools/audio/render_all.py --only act3_cutscene_sfx
"""
from __future__ import annotations

import importlib.util
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools", "audio"))
sys.path.insert(0, os.path.join(ROOT, "assets_src", "music"))
sys.path.insert(0, HERE)

import numpy as np  # noqa: E402

import act2_creature_sfx as A2  # noqa: E402
from act2_creature_sfx import Engine, hum, splash, whoosh  # noqa: E402
from creature_sfx import WOOD, buf, burst, crackle, creak, finish, glass_ring, room, slosh, tap, thump  # noqa: E402
from synth.dsp import SR, bq_bandpass, bq_highpass, bq_lowpass, filt, rng  # noqa: E402
from synth.mixer import measure, write_ogg  # noqa: E402
from synth.score import n as midi  # noqa: E402
from synth.voice import hum_ensemble, sing  # noqa: E402
from underwater_sfx import _n, _t, noise, place  # noqa: E402
from vowbound_sfx import luff  # noqa: E402


def _load(name: str, path: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


FV = _load("hush_first_verse", os.path.join(ROOT, "assets_src", "music", "hush_first_verse.py"))
RH = _load("reedhollow_sketch", os.path.join(ROOT, "assets_src", "music", "reedhollow.py"))
AMB = _load("act2_ambience", os.path.join(HERE, "act2_ambience.py"))
OUT_DIR = os.path.join(ROOT, "assets", "audio", "act3", "sfx")
SEED = 20263500
QUALITY = 4.0
DECK = [(f * 0.8, a) for f, a in WOOD]
ENGINE_HZ = 55.0                     # the Kite's engines, as kite_foley.py's ENGINE_HZ


def _unit(x: np.ndarray) -> np.ndarray:
    return x / (np.abs(x).max() + 1e-9)


def sea_flat_lap(g):
    x = buf(6.0)
    for k in range(5):                                  # slow, small, unhurried: nothing pushing the water
        place(x, slosh(g, 0.9, 0.35 - 0.03 * k, 1.6), 0.3 + 1.1 * k + float(g.uniform(-0.1, 0.1)))
    return x


def names_murmured(g):
    sec = 6.0
    x = buf(sec + 0.6)
    for v in range(10):                                 # many low voices, overlapping, no word clear
        at = float(g.uniform(0.0, 1.5))
        d = float(g.uniform(2.5, 4.2))
        syl = []
        left = d
        while left > 0.05:
            s = min(left, float(g.uniform(0.18, 0.4)))
            syl.append((str(g.choice(["a", "e", "o", "u", "m", "n"])), s))
            left -= s
        pitches = [(float(g.uniform(47, 55)) if v % 3 else float(g.uniform(55, 60)), d)]
        y = sing(syl, pitches, vel=0.45, seed=int(g.integers(1 << 30)), scale=1.0 if v % 3 else 1.15, tilt=2.2,
                 breath=0.25, vib_cents=4.0, jitter_cents=30.0, release=0.2)
        y = filt(y, [bq_lowpass(1800, 0.7), bq_highpass(120, 0.7)])
        place(x, y * 0.6, at)
    return x


def clutch_hum(g):
    line = [(m, d) for m, d in AMB.clutch_line(14.0) if m > 0][:4]
    h = hum_ensemble(line, voices=5, seed=SEED + 300, register="low", spread=0.6, breath_every=(20.0, 30.0))
    return filt(h.mean(axis=1), [bq_highpass(90, 0.7), bq_lowpass(3000, 0.7)])


def velamir_lullaby_hum(g):
    beat = 60.0 / 62.0                                  # about 11.5 s for the two lines: the scenes' 10-12 s waits
    notes, phon = [], []
    for line in FV.VERSE[:2]:
        for p, beats in line:
            notes.append((float(midi(p)), beats * beat))
            phon.append(("m", beats * beat))
    y = sing(phon, notes, vel=0.5, seed=SEED + 400, scale=1.17, tilt=2.0, breath=0.08, vib_cents=8.0, vib_rate=4.8,
             jitter_cents=5.0, release=0.6)
    return filt(y, [bq_highpass(140, 0.7), bq_lowpass(3600, 0.7)])


def shell_into_water(g):
    x = buf(4.2)
    place(x, splash(g, 0.25, 0.45, 2200), 0.0)          # a small plunk
    for k in range(4):                                  # the ring of lapping going out
        place(x, slosh(g, 0.6, 0.3 - 0.05 * k, 2.6 - 0.3 * k), 0.4 + 0.55 * k)
    place(x, tap(g, [1900.0, 3100.0], [0.02, 0.012], 0.5, 0.25), 2.6)   # the shell on a stone, going down
    return x


def engine_hum_stops(g):
    x = buf(6.0)
    place(x, hum(g, 4.6, 98.0, 1.0, bend=(1.0, 0.3)), 0.0)            # the Iskarra engine's bound hum sinking
    place(x, hum(g, 4.2, 196.0 * 1.01, 0.4, bend=(1.0, 0.28)), 0.05)
    for k in range(8):                                  # the ratchet running down, each tick further apart
        place(x, Engine.ratchet(g, 0.1, 5, 5, 0.5 - 0.04 * k), 0.2 + 0.35 * k * (1 + 0.25 * k))
    place(x, thump(g, 70, 35, 0.3, 0.4, 1.0), 4.6)     # the last knock
    return x


def rope_slips(g):
    x = buf(2.6)
    rip = filt(g.standard_normal(_n(0.35)), [bq_bandpass(1800, 0.9)]) * np.exp(-_t(_n(0.35)) / 0.12)
    place(x, rip, 0.0, 0.6)                             # the knot spilling: a soft rip of fibre
    run = filt(g.standard_normal(_n(0.6)), [bq_bandpass(1100, 0.7)]) * np.linspace(1.0, 0.2, _n(0.6))
    place(x, run, 0.25, 0.45)                           # the tail running through
    place(x, thump(g, 180, 120, 0.04, 0.3, 0.25), 0.95, 0.6)   # slack on the planks
    place(x, tap(g, [f for f, _ in DECK], [0.03, 0.02, 0.015, 0.01], 0.35, 0.3), 1.05)
    return x


def kite_settles(g):
    x = buf(6.0)
    place(x, hum(g, 4.5, ENGINE_HZ * 2, 0.8, bend=(1.0, 0.6)), 0.0)  # engines idling down, not out
    place(x, creak(g, 1.8, 30, 110, DECK, 0.7), 0.9)    # the hull taking the stone
    place(x, thump(g, 70, 40, 0.4, 0.4, 0.9), 0.9, 0.7)
    place(x, luff(g, 2.2, 6.0, 0.35), 2.4)              # the rigging slackening
    return x


def kite_engine_strains(g):
    sec = 5.0
    x = buf(sec + 0.5)
    t = _t(_n(sec))
    place(x, hum(g, sec, ENGINE_HZ * 3.0, 0.9), 0.0)    # a fifth over the idle: labouring
    whirr = filt(g.standard_normal(_n(sec)), [bq_bandpass(1100, 0.8)])
    beat = (0.6 + 0.4 * np.sin(2 * np.pi * (13.0 + 2.5 * np.sin(2 * np.pi * 0.7 * t)) * t)) ** 2   # vanes, uneven
    place(x, 0.35 * _unit(whirr) * beat, 0.0)
    for at in (0.8, 2.3, 3.9):
        place(x, creak(g, 0.7, 25, 90, DECK, 0.5), at)  # the hull complaining
    return x


def kite_touches_floor(g):
    x = buf(4.0)
    place(x, thump(g, 55, 30, 0.6, 0.5, 1.4), 0.0)      # soft, deep contact
    grind = filt(g.standard_normal(_n(1.2)), [bq_bandpass(2600, 2.0)]) * np.exp(-_t(_n(1.2)) / 0.4)
    place(x, grind, 0.05, 0.3)                          # the keel on held light: glassy, not stone
    place(x, glass_ring(g, 1760.0, 1.4, 0.3), 0.1)
    place(x, glass_ring(g, 2349.0, 1.0, 0.2), 0.2)
    return x


def pell_farewell_tide(g):
    beat = 60.0 / 60.0
    line = [(float(midi(p)) - 12, b * beat * 0.8) for p, b in RH.CLUTCH]
    ph = [("a", d) for _, d in line]
    y = sing(ph, line, vel=0.6, seed=SEED + 900, scale=0.95, tilt=1.7, breath=0.1, vib_cents=16.0, vib_rate=4.6,
             jitter_cents=8.0, release=0.8)
    return filt(y, [bq_highpass(80, 0.7), bq_lowpass(4200, 0.7)])


def match_struck(g):
    x = buf(3.0)
    scratch = filt(g.standard_normal(_n(0.22)), [bq_bandpass(3200, 1.2)]) * np.sin(np.pi * _t(_n(0.22)) / 0.22)
    place(x, scratch, 0.0, 0.7)                         # the scratch
    place(x, burst(g, 0.3, [bq_bandpass(1400, 0.7)], 0.005, 0.12), 0.2, 0.8)   # the flare
    place(x, crackle(g, 2.2, 6, 2400, 0.25, 0.05), 0.45)                      # the flame catching, small and steady
    flame = filt(g.standard_normal(_n(2.4)), [bq_lowpass(600, 0.7), bq_highpass(120, 0.7)])
    place(x, 0.25 * _unit(flame) * np.clip(_t(_n(2.4)) / 0.4, 0, 1), 0.4)
    return x


def wind_in_sails(g):
    sec = 5.5
    x = buf(sec + 0.5)
    t = _t(_n(sec))
    gust = A2.smooth_noise(_n(sec), 0.6, g)
    wind = filt(g.standard_normal(_n(sec)), [bq_bandpass(500, 0.6)]) * (0.5 + 0.5 * gust) * np.clip(t / 1.0, 0, 1)
    place(x, 0.6 * _unit(wind), 0.0)
    place(x, luff(g, sec - 0.5, 5.0, 0.4, fc=700.0), 0.3)       # the canvas
    for f in (196.0, 293.7):                                    # the sheets humming
        place(x, 0.12 * np.sin(2 * np.pi * f * t) * (0.4 + 0.6 * gust), 0.0)
    return x


# name -> (fn, momentary max): the cutscene foley's levels (act2_cutscene_sfx.py's), the voices under a line
SFX: list[tuple[str, object, float]] = [
    ("sea_flat_lap", sea_flat_lap, -28.0), ("names_murmured", names_murmured, -26.0),
    ("clutch_hum", clutch_hum, -24.0), ("velamir_lullaby_hum", velamir_lullaby_hum, -22.0),
    ("shell_into_water", shell_into_water, -25.0), ("engine_hum_stops", engine_hum_stops, -21.0),
    ("rope_slips", rope_slips, -25.0), ("kite_settles", kite_settles, -22.0),
    ("kite_engine_strains", kite_engine_strains, -21.0), ("kite_touches_floor", kite_touches_floor, -22.0),
    ("pell_farewell_tide", pell_farewell_tide, -21.0), ("match_struck", match_struck, -26.0),
    ("wind_in_sails", wind_in_sails, -25.0),
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
