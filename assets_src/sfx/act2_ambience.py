"""Act II's ambience beds (M4-A2P-093, ADR 0205; plain git under assets/audio/act2/ambience/, ADR 0175).

Each bed is a seamless loop built as act1_final_ambience.py builds Act I's (LoopMixer, field_ambience's sources,
-26 LUFS integrated with peaks well down, about 10 LU under its zone's music; mix.md), from its environment sheet and
the cue sheet (docs/kb/plan/act2/audio/act2_cue_sheet.md §4). New beds go at the end of BEDS: each bed's seed is its
index, so appending keeps every earlier bed byte-identical.

    fen_dusk           Ch10, Ossa Fen (art/environments/ossa_fen.md): mangrove channels at dusk, root-walks over tannin
                       water. The dusk insect chorus, frogs in the roots, drips into still brown water, the roots
                       creaking, water lapping under the walks, and a fen bird far off. Fireflies are seen, not heard.
    reedhollow_roost   Ch10, Reedhollow, the Kirru roost-village: woven reed lodges on mangrove roots round a lagoon.
                       Reed wind through the screens, the lagoon under the platforms, lodges creaking, a cook-fire, and
                       the clutch's wordless hum far across the water (a line in the Kirru mode on A, A B C# D# F#
                       with no E, written for this bed: the Kirru sing without words; they are a people, act2_roster).
    vey_galleries      Ch11, Sunken Vey (art/environments/lowlight.md): drowned Lit Age galleries, salt-glass floors, the
                       conduits' bound light still lit. Drips into deep still water in a big stone hollow, the conduits'
                       steady low hum (it does not pulse), salt-glass ticking as it settles, and fig roots creaking.
    lowlight_temple    Ch11, Lowlight: the temple half under water. Water lapping on the atrium steps and the hall's
                       hollow, a slow far throb in the conduits under the floor (the Lamp Engine's, felt not heard),
                       drips, and the glass answering now and then.
    keth_pass_wind     Ch12, Keth Pass (art/environments/keth_pass.md): three switchbacks up a cliff in the cold. High
                       wind in gusts, the pass-cords whistling and knocking on their posts, fine snow hissing over the
                       slate, and scree trickling off the drop side. (ADR 0015: snow is weather; nothing freezes.)
    quellan_town       Ch12, Quellan, the Ullari highland town: a lighter wind, red banners flapping, the town's murmur,
                       a loom clacking in a house, a goat-bell far up the slope, and a door now and then.
    cloudloom_hall     Ch12, Cloudloom, the open-roofed weaving-hall: looms and shuttles working, thousands of keth
                       cords stirring in the wind through the open roof, and a few women's voices low between them.
    ansedra_still      Ch13, Ansedra, the holy city of perfect stillness (art/environments/ansedra.md): almost nothing. No
                       wildlife at all (ADR 0204 §1: no seabirds). Very low air over still water, a moored barge's
                       lacquered hull ticking, pilgrims murmuring far off, and one far bell in the loop.
    lacquer_court      Ch14, the Lacquer Court at dusk: a gathered crowd's low murmur under a colonnade, silk moving, the
                       water-steps' faint lap, and a far gong.
    archive_room       Ch13, the Lamp Archive's reading room: a still room, a lamp's flame fluttering, paper shifting
                       somewhere in the stacks, and now and then a page turned.
    sanctum_basin      Ch13, the Sanctum of the Level: the still basin's air and nothing else, just above silence (its
                       music, sanctum_of_the_level, carries the light).
    open_sea_night     Ch15, the unlamped bridal barge at night: the sea against the hull, the barge's timbers, Merel's
                       bridal cloth over the bier stirring, and a light wind.
    pale_rim_shallows  Ch16, the Pale Rim: white shallows under a white sky. A soft wind, a thin wash over the flats,
                       far ripples, and a cairn stone settling.
    choir_bowl         Ch16, the Drowned Choir's bowl at moonrise: wind moaning through the colossal stone mouths (a few
                       slow resonant tones that never make a tune) and water moving in the bowl.

The battle arenas' beds (the Lead's 10-30 13:08 item; ambience.json `arenas`, played by BattleAudio for the
encounter's arena in place of the field's beds). Thinner than a zone bed, they sit under the battle cue: the place
holding its breath, no wildlife chorus, nothing on a beat. An arena that is the same place as a zone bed uses that
bed (the bridal barge at night: open_sea_night; the Drowned Choir's ring: choir_bowl).

    arena_fen_roots    Ch10, the dead mangrove's mudbank (the Mangrove Drowner): the fen gone quiet. Still tannin air,
                       mud sucking and settling, slow bubbles rising through the silt, the dead roots creaking, drips.
    arena_engine_hall  Ch11, the flooded hall under Lowlight's sanctum (the Lamp Engine): the engine near now, its
                       throb under the dais you can hear, the conduits' hum close, water lapping at the dais's edge.
    arena_seep_terrace Ch12, Keth Pass's seeping terrace (the Avalanche Ram): water seeping down the cut rock and
                       trickling over the old road's kerb, wind across the terrace, now and then a stone loosed above.
    arena_lagoon_dusk  Ch14, Ansedra's lagoon at the wedding's dusk (Warden Malcor Venn, from the bridal barge): the
                       still lagoon broken, water rippling against the hull, the barge's lacquered timbers, a far bell
                       still tolling the wedding, the city's voices far off and raised.
    arena_court_steps  Ch14, the Lacquer Court's water-steps: the crowd drawn back, murmuring low and far, silk
                       banners stirring, water on the steps, a far gong.

Ch15 and Ch16's remaining beds (the Lead's 10-30 13:48 item; beats act2_ch15.md §6, act2_ch16.md):

    hollowmere_flotilla Ch15 B10-B12, Hollowmere's first visit (`ch17/hollowmere`): "ambience only, no zone loop"; the
                        first visit is grief. The Saltwright flotilla's own sound: water among the moored hulls, the
                        tide-wheels turning slowly, a pump's steady hum, gulls, hammers far off and few, low voices.
                        No laughter, no song (Act III's `hollowmere` cue brings the warmth back in Ch17).
    open_sea_fog        Ch15 B09, the bow at dawn in fog (`ch15/open_sea` once `ch15_pell_said_he_knew` is set): flat
                        calm under a white wall, a low swell, fog-damp dripping off the canopy and the empty lamp hook,
                        the barge barely creaking. Nothing beyond the fog yet (hollowmere_answers brings the answer).
    choir_storm         Ch16, the storm waking early at the Drowned Choir (`ch16_holding_the_line`, by encounter):
                        the stone mouths roaring in a rising gale, surge pounding the ring channel, spray, the sea's
                        low roar under it all. It is weather, not the Undertow's voice (storm_wall carries that).

assets/audio/act2/ambience/<bed>.ogg + .loop.json (stereo, Vorbis q1 like the Act I beds; the rule
`act2/ambience/*.ogg`: -26 LUFS integrated +- 0.5, true peak under -5 dBTP). Synthesized here and in tools/audio/synth/
(SPEC §2, §9): no samples, no recordings, no generated audio.

Render:  python3 tools/audio/render_all.py --only act2_ambience
"""
from __future__ import annotations

import importlib.util
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools", "audio"))
sys.path.insert(0, HERE)

import numpy as np  # noqa: E402

from synth.dsp import SR, bq_bandpass, bq_highpass, bq_lowpass, filt, rng  # noqa: E402
from synth.looping import LoopMixer, master_loop, write_loop_sidecar  # noqa: E402
from synth.mixer import measure, write_ogg  # noqa: E402
from synth.reverb import ModFDNReverb  # noqa: E402
from synth.voice import hum_ensemble  # noqa: E402
from synth.water import drip  # noqa: E402

_spec = importlib.util.spec_from_file_location("field_ambience", os.path.join(HERE, "field_ambience.py"))
FA = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(FA)

OUT_DIR = os.path.join(ROOT, "assets", "audio", "act2", "ambience")
SEED = 20261900
TARGET_LUFS = -26.0
CEILING_DB = -6.0
QUALITY = 1.0
LOOPS = {"fen_dusk": 48.0, "reedhollow_roost": 46.0, "vey_galleries": 50.0, "lowlight_temple": 48.0,
         "keth_pass_wind": 44.0, "quellan_town": 46.0, "cloudloom_hall": 44.0, "ansedra_still": 50.0,
         "lacquer_court": 46.0, "archive_room": 44.0, "sanctum_basin": 40.0, "open_sea_night": 48.0,
         "pale_rim_shallows": 50.0, "choir_bowl": 52.0, "arena_fen_roots": 40.0, "arena_engine_hall": 36.0,
         "arena_seep_terrace": 40.0, "arena_lagoon_dusk": 42.0, "arena_court_steps": 40.0,
         "hollowmere_flotilla": 48.0, "open_sea_fog": 44.0, "choir_storm": 36.0}
# The Kirru mode on A (reedhollow.py): A B C# D# F#, G# only as the top of a rise; never E.
KIRRU = {"A3": 57, "B3": 59, "C#4": 61, "D#4": 63, "F#4": 66, "F#3": 54, "G#4": 68}


def _mixer(name: str) -> tuple[LoopMixer, int]:
    mx = LoopMixer(intro_s=0.0, loop_s=LOOPS[name], preroll_s=6.0)
    return mx, mx.L


def _room(seed: int, rt60: float, size: float, highcut: float = 7000.0) -> ModFDNReverb:
    return ModFDNReverb(rt60=rt60, rt60_high=rt60 * 0.45, predelay=0.03, size=size, mod_depth=6.0, mod_rate=0.3,
                        early_level=0.3, lowcut=120.0, highcut=highcut, seed=seed)


# --------------------------------------------------------------------------- sources


def creak(g, dur: float, lo: float, hi: float) -> np.ndarray:
    """Wet wood working: a mangrove root or a lodge's lashing under weight."""
    return FA.stick_slip(g, dur, lo, hi, [(240.0, 1.0), (610.0, 0.55), (1300.0, 0.2)])


def croak(g) -> np.ndarray:
    """A fen frog: a short rattle of throat pulses through a low formant, two or three times."""
    rate = float(g.uniform(16, 26))
    f = float(g.uniform(420, 820))
    out = np.zeros(int(1.4 * SR))
    for k in range(int(g.integers(1, 4))):
        n = int(float(g.uniform(0.18, 0.32)) * SR)
        t = np.arange(n) / SR
        pulses = (np.sin(np.pi * rate * t) ** 8) * np.sin(np.pi * t / t[-1])
        body = filt(g.standard_normal(n), [bq_bandpass(f, 3.0), bq_bandpass(f * 2.1, 2.0)])
        y = pulses * body / (np.abs(body).max() + 1e-9)
        s = int((k * float(g.uniform(0.36, 0.5))) * SR)
        out[s: s + n] += y[: len(out) - s]
    return out


def dusk_buzz(L: int, g, carrier: float, am_hz: float) -> np.ndarray:
    """A dusk insect's continuous buzz: a narrow noise band pulsing fast, swelling and resting slowly (stereo)."""
    t = np.arange(L) / SR
    am = 0.55 + 0.45 * np.sin(2 * np.pi * FA.snap(am_hz, L) * t) ** 2
    swell = 0.5 + 0.5 * FA.plfo(L, 0.03, g)
    band = FA.stereo_noise(L, g, [bq_bandpass(carrier, 6.0), bq_lowpass(carrier * 1.4, 0.7)], 0.3)
    return band * (am * swell)[:, None]


def fen_bird(g) -> np.ndarray:
    """A fen bird far off at dusk: two falling whistled notes, the second lower and longer."""
    out = np.zeros(int(1.6 * SR))
    f0 = float(g.uniform(2100, 2700))
    for k, (ratio, dur) in enumerate(((1.0, 0.22), (0.78, 0.42))):
        n = int(dur * SR)
        t = np.arange(n) / SR
        f = f0 * ratio * (1.0 - 0.06 * t / dur)
        ph = 2 * np.pi * np.cumsum(f * (1 + 0.004 * np.sin(2 * np.pi * 22 * t))) / SR
        y = np.sin(ph) * np.sin(np.pi * t / dur) ** 1.5
        s = int((0.0 if k == 0 else 0.3) * SR)
        out[s: s + n] += y
    return out


def reed_rustle(g, sec: float) -> np.ndarray:
    """Reeds and woven screens moving in a gust: a dry, fibrous rustle swelling and falling."""
    n = int(sec * SR)
    t = np.arange(n) / n
    y = filt(g.standard_normal(n), [bq_bandpass(float(g.uniform(1800, 3200)), 0.9)])
    grain = 0.55 + 0.45 * np.abs(np.sin(2 * np.pi * float(g.uniform(25, 45)) * np.arange(n) / SR))
    return y * grain * np.sin(np.pi * t) ** 1.2


def fire(g, sec: float) -> np.ndarray:
    """A small cook-fire on a clay hearth: a low breathing flame with a few pops."""
    n = int(sec * SR)
    t = np.arange(n) / SR
    y = 0.4 * filt(g.standard_normal(n), [bq_lowpass(700, 0.7), bq_highpass(90, 0.7)])
    y = y / (np.abs(y).max() + 1e-9) * 0.5
    for _ in range(int(sec * 3)):
        s = int(float(g.uniform(0, sec - 0.01)) * SR)
        k = int(0.004 * SR)
        y[s: s + k] += filt(g.standard_normal(k), [bq_highpass(1500, 0.7)]) * np.linspace(1, 0, k) * float(g.uniform(0.2, 0.7))
    return y * np.clip(t / 0.5, 0, 1) * np.clip((sec - t) / 0.5, 0, 1)


def clutch_line(loop_s: float) -> list[tuple[float, float]]:
    """The clutch's wordless hum, one loop long: slow phrases in the Kirru mode with breaths of silence (midi 0)."""
    phrases = [
        [("A3", 3.0), ("C#4", 2.0), ("B3", 2.5), ("A3", 3.5)],
        [("F#3", 2.5), ("A3", 2.0), ("B3", 4.0)],
        [("C#4", 2.0), ("D#4", 2.0), ("F#4", 3.0), ("D#4", 1.5), ("C#4", 2.0), ("B3", 4.0)],
    ]
    line: list[tuple[float, float]] = []
    for ph in phrases:
        line += [(float(KIRRU[n]), d) for n, d in ph]
        line.append((0.0, 2.5))
    used = sum(d for _, d in line)
    line[-1] = (0.0, line[-1][1] + (loop_s - used))  # the last breath fills the loop exactly
    return line


# --------------------------------------------------------------------------- the beds


def fen_dusk(g):
    mx, L = _mixer("fen_dusk")
    mx.bus("air", 0.0, send=0.05)
    mx.bus("insects", 0.0, send=0.25, process=lambda x: filt(x, [bq_lowpass(6500, 0.7)]))
    mx.bus("frogs", 0.0, send=0.3)
    mx.bus("water", 0.0, send=0.15)
    mx.bus("roots", 0.0, send=0.25)
    mx.bus("far", 0.0, send=0.5, process=lambda x: filt(x, [bq_lowpass(3500, 0.7)]))
    mx.add("air", FA.stereo_noise(L, g, [bq_lowpass(300, 0.6), bq_highpass(40, 0.7)], 0.6) * 0.14, 0.0)  # humid air
    mx.add("insects", dusk_buzz(L, g, 4300.0, 31.0) * 0.05, 0.0)
    mx.add("insects", dusk_buzz(L, g, 5200.0, 43.0) * 0.03, 0.0)
    for _ in range(3):                                                     # crickets in the roots, each its own
        carrier = float(g.uniform(3600, 4600))
        period = float(g.uniform(0.6, 1.1))
        pan = float(g.uniform(-0.9, 0.9))
        for t in FA.schedule(L, period, g, 0.08):
            mx.add("insects", FA.cricket_chirp(g, carrier, int(g.integers(2, 4)), float(g.uniform(24, 32))), t,
                   pan=pan, gain=float(g.uniform(0.15, 0.35)))
    for t in FA.schedule(L, 3.1, g, 0.6):                                  # frogs, near and far
        mx.add("frogs", croak(g), t, pan=float(g.uniform(-0.9, 0.9)), gain=float(g.uniform(0.15, 0.5)))
    for t in FA.schedule(L, 0.9, g, 0.6):                                  # drips into the tannin water
        mx.add("water", drip(float(g.uniform(0.15, 0.5)), float(g.uniform(1.4, 3.0)), seed=int(g.integers(1 << 30))),
               t, pan=float(g.uniform(-0.8, 0.8)), gain=float(g.uniform(0.15, 0.4)))
    for t in FA.schedule(L, 2.2, g, 0.5):                                  # water lapping under the root-walks
        mx.add("water", FA.lap(g, float(g.uniform(0.5, 0.9))), t, pan=float(g.uniform(-0.6, 0.6)),
               gain=float(g.uniform(0.25, 0.6)))
    for t in FA.schedule(L, 5.5, g, 0.5):                                  # the roots creaking
        mx.add("roots", creak(g, float(g.uniform(0.6, 1.4)), 40, 180), t, pan=float(g.uniform(-0.7, 0.7)),
               gain=float(g.uniform(0.2, 0.4)))
    for t in FA.schedule(L, 14.0, g, 0.4):                                 # a fen bird far off
        mx.add("far", fen_bird(g), t, pan=float(g.uniform(-0.8, 0.8)), gain=float(g.uniform(0.15, 0.3)))
    return mx, _room(SEED % 9973 + 1, 1.1, 1.6, highcut=6000.0)


def reedhollow_roost(g):
    mx, L = _mixer("reedhollow_roost")
    mx.bus("wind", 0.0, send=0.1)
    mx.bus("reeds", 0.0, send=0.2)
    mx.bus("water", 0.0, send=0.15)
    mx.bus("lodges", 0.0, send=0.3)
    mx.bus("clutch", 0.0, send=0.55, process=lambda x: filt(x, [bq_lowpass(2600, 0.7)]))
    gust = 0.5 + 0.5 * FA.plfo(L, 0.07, g)
    mx.add("wind", FA.stereo_noise(L, g, [bq_bandpass(1400, 0.5), bq_highpass(250, 0.7)], 0.4)
           * (0.35 + 0.65 * gust ** 1.3)[:, None] * 0.1, 0.0)
    for t in FA.schedule(L, 1.6, g, 0.6):                                  # reeds and woven screens in the gusts
        mx.add("reeds", reed_rustle(g, float(g.uniform(0.8, 1.8))), t, pan=float(g.uniform(-0.9, 0.9)),
               gain=float(g.uniform(0.1, 0.3)))
    for t in FA.schedule(L, 1.5, g, 0.5):                                  # the lagoon under the platforms
        mx.add("water", FA.slap(g) if g.random() < 0.4 else FA.lap(g, 0.8), t, pan=float(g.uniform(-0.8, 0.8)),
               gain=float(g.uniform(0.25, 0.6)))
    for t in FA.schedule(L, 4.0, g, 0.5):                                  # the lodges on their roots
        mx.add("lodges", creak(g, float(g.uniform(0.6, 1.2)), 60, 260), t, pan=float(g.uniform(-0.7, 0.7)),
               gain=float(g.uniform(0.15, 0.35)))
    mx.add("lodges", fire(g, LOOPS["reedhollow_roost"] - 1.0), 0.5, pan=-0.45, gain=0.12)  # a cook-fire
    hum = hum_ensemble(clutch_line(LOOPS["reedhollow_roost"]), voices=9, seed=int(g.integers(1 << 30)),
                       register="high", spread=0.9, loop=True)
    mx.add("clutch", hum[:L] * 0.25, 0.0)                                  # the clutch, far across the water
    return mx, _room(SEED % 9973 + 2, 1.4, 1.8, highcut=6000.0)


def conduit_hum(L: int, g, f0: float) -> np.ndarray:
    """A Lit Age conduit's bound light: a steady low harmonic hum with two near partials beating slowly (stereo,
    snapped to the loop). It does not pulse (bible: bound glimmer is steady)."""
    t = np.arange(L) / SR
    y = np.zeros((L, 2))
    for k, a in ((1, 1.0), (2, 0.5), (3, 0.22), (5, 0.08)):
        for ch, det in ((0, 1.0), (1, 1.0015)):
            f = FA.snap(f0 * k * det, L)
            y[:, ch] += a * np.sin(2 * np.pi * f * t + float(g.uniform(0, 6.28)))
    return y / np.abs(y).max()


def glass_tick(g) -> np.ndarray:
    """Salt-glass settling: a small, bright, brittle tick with a short ring."""
    f = float(g.uniform(2800, 4600))
    return FA.modal([f, f * 1.47, f * 2.3], [0.04, 0.025, 0.012], [1.0, 0.5, 0.2], 0.2, g, click=0.3)


def throb(L: int, g, hz: float, f0: float) -> np.ndarray:
    """A far, slow pulse under the floor: a low tone swelling at `hz` (snapped to the loop). Stereo."""
    t = np.arange(L) / SR
    env = np.sin(np.pi * FA.snap(hz, L) * t) ** 6
    y = np.sin(2 * np.pi * FA.snap(f0, L) * t) * env
    return np.stack([y, y], axis=1)


def cord_whistle(g, sec: float) -> np.ndarray:
    """A pass-cord singing in a gust: a thin, fluttering whistle rising and falling with the wind."""
    n = int(sec * SR)
    t = np.arange(n) / SR
    f0 = float(g.uniform(900, 1700))
    f = f0 * (1.0 + 0.08 * np.sin(np.pi * t / sec)) * (1.0 + 0.01 * np.sin(2 * np.pi * float(g.uniform(5, 9)) * t))
    y = np.sin(2 * np.pi * np.cumsum(f) / SR) * (0.6 + 0.4 * np.sin(2 * np.pi * float(g.uniform(11, 17)) * t) ** 2)
    return y * np.sin(np.pi * t / sec) ** 2


def cord_knock(g) -> np.ndarray:
    """A cord's knot knocking on its wooden post."""
    b = float(g.uniform(380, 520))
    return FA.modal([b, b * 2.6, b * 5.1], [0.03, 0.015, 0.008], [1.0, 0.4, 0.15], 0.15, g, click=0.4)


def flap(g) -> np.ndarray:
    """A woollen banner snapping in the wind: a few quick cloth slaps and a flutter."""
    out = np.zeros(int(0.8 * SR))
    for k in range(int(g.integers(2, 5))):
        m = int(0.05 * SR)
        x = filt(g.standard_normal(m), [bq_bandpass(float(g.uniform(500, 900)), 0.9)]) * np.exp(-np.arange(m) / (0.012 * SR))
        s = int((k * float(g.uniform(0.09, 0.16))) * SR)
        out[s: s + m] += x * float(g.uniform(0.5, 1.0))
    return out


def loom(g, sec: float, rate: float) -> np.ndarray:
    """A loom at work: the beater's wooden clack on each pick, the shuttle's swish between, at `rate` picks a second."""
    out = np.zeros(int(sec * SR))
    t = 0.0
    while t < sec - 0.4:
        b = float(g.uniform(260, 340))
        clack = FA.modal([b, b * 2.3, b * 4.4], [0.03, 0.018, 0.01], [1.0, 0.5, 0.2], 0.12, g, click=0.6)
        s = int(t * SR)
        out[s: s + len(clack)] += clack[: len(out) - s]
        m = int(0.18 * SR)
        sw = filt(g.standard_normal(m), [bq_bandpass(float(g.uniform(1500, 2500)), 0.8)]) * np.sin(np.pi * np.arange(m) / m)
        s2 = int((t + 0.35 / rate) * SR)
        out[s2: s2 + m] += 0.25 * sw[: max(0, len(out) - s2)]
        t += float(g.uniform(0.9, 1.1)) / rate
    return out


def goat_bell(g) -> np.ndarray:
    """A goat's iron bell far up the slope: two or three dull clanks."""
    out = np.zeros(int(1.2 * SR))
    b = float(g.uniform(700, 900))
    for k in range(int(g.integers(2, 4))):
        x = FA.modal([b, b * 1.6, b * 2.8], [0.25, 0.15, 0.06], [1.0, 0.5, 0.25], 0.5, g, click=0.2)
        s = int(k * float(g.uniform(0.25, 0.4)) * SR)
        out[s: s + len(x)] += x[: len(out) - s]
    return out


def vey_galleries(g):
    mx, L = _mixer("vey_galleries")
    mx.bus("hum", 0.0, send=0.3)
    mx.bus("water", 0.0, send=0.5)
    mx.bus("glass", 0.0, send=0.6, process=lambda x: filt(x, [bq_lowpass(7000, 0.7)]))
    mx.bus("roots", 0.0, send=0.5)
    mx.add("hum", conduit_hum(L, g, 98.0) * 0.08, 0.0)
    mx.add("water", FA.stereo_noise(L, g, [bq_lowpass(260, 0.6), bq_highpass(40, 0.7)], 0.7) * 0.1, 0.0)
    for t in FA.schedule(L, 1.3, g, 0.7):
        mx.add("water", drip(float(g.uniform(0.2, 0.6)), float(g.uniform(1.8, 3.6)), seed=int(g.integers(1 << 30))), t,
               pan=float(g.uniform(-0.9, 0.9)), gain=float(g.uniform(0.2, 0.5)))
    for t in FA.schedule(L, 3.3, g, 0.6):
        mx.add("glass", glass_tick(g), t, pan=float(g.uniform(-0.9, 0.9)), gain=float(g.uniform(0.08, 0.2)))
    for t in FA.schedule(L, 9.0, g, 0.5):
        mx.add("roots", creak(g, float(g.uniform(0.8, 1.5)), 30, 140), t, pan=float(g.uniform(-0.7, 0.7)), gain=0.25)
    return mx, _room(SEED % 9973 + 3, 3.2, 2.4, highcut=5000.0)


def lowlight_temple(g):
    mx, L = _mixer("lowlight_temple")
    mx.bus("water", 0.0, send=0.45)
    mx.bus("throb", 0.0, send=0.3, process=lambda x: filt(x, [bq_lowpass(300, 0.7)]))
    mx.bus("hum", 0.0, send=0.35)
    mx.bus("glass", 0.0, send=0.6, process=lambda x: filt(x, [bq_lowpass(6500, 0.7)]))
    mx.add("water", FA.stereo_noise(L, g, [bq_lowpass(400, 0.6), bq_highpass(50, 0.7)], 0.6) * 0.12, 0.0)
    for t in FA.schedule(L, 1.8, g, 0.5):
        mx.add("water", FA.lap(g, float(g.uniform(0.6, 1.1))), t, pan=float(g.uniform(-0.6, 0.6)),
               gain=float(g.uniform(0.3, 0.7)))
    for t in FA.schedule(L, 2.4, g, 0.7):
        mx.add("water", drip(float(g.uniform(0.2, 0.5)), float(g.uniform(2.0, 3.4)), seed=int(g.integers(1 << 30))), t,
               pan=float(g.uniform(-0.9, 0.9)), gain=float(g.uniform(0.15, 0.4)))
    mx.add("throb", throb(L, g, 0.4, 46.0) * 0.1, 0.0)        # felt more than heard
    mx.add("hum", conduit_hum(L, g, 130.0) * 0.04, 0.0)
    for t in FA.schedule(L, 6.0, g, 0.6):
        mx.add("glass", glass_tick(g), t, pan=float(g.uniform(-0.8, 0.8)), gain=float(g.uniform(0.06, 0.15)))
    return mx, _room(SEED % 9973 + 4, 3.6, 2.6, highcut=4800.0)


def keth_pass_wind(g):
    mx, L = _mixer("keth_pass_wind")
    mx.bus("wind", 0.0, send=0.1)
    mx.bus("cords", 0.0, send=0.25, process=lambda x: filt(x, [bq_lowpass(3500, 0.7)]))
    mx.bus("snow", 0.0, send=0.1)
    mx.bus("scree", 0.0, send=0.3)
    gust = 0.5 + 0.5 * FA.plfo(L, 0.08, g)
    mx.add("wind", FA.stereo_noise(L, g, [bq_lowpass(1400, 0.6), bq_highpass(120, 0.7)], 0.4)
           * (0.3 + 0.7 * gust ** 1.6)[:, None] * 0.2, 0.0)
    mx.add("snow", FA.stereo_noise(L, g, [bq_bandpass(4500, 0.8), bq_highpass(2500, 0.7)], 0.3)
           * (0.2 + 0.8 * gust ** 2)[:, None] * 0.04, 0.0)
    for t in FA.schedule(L, 2.6, g, 0.6):
        mx.add("cords", cord_whistle(g, float(g.uniform(1.0, 2.4))), t, pan=float(g.uniform(-0.9, 0.9)),
               gain=float(g.uniform(0.05, 0.14)))
    for t in FA.schedule(L, 3.0, g, 0.6):
        mx.add("cords", cord_knock(g), t, pan=float(g.uniform(-0.8, 0.8)), gain=float(g.uniform(0.15, 0.35)))
    for t in FA.schedule(L, 11.0, g, 0.5):                                 # scree off the drop side
        mx.add("scree", FA.burst(g, 1.2, [bq_bandpass(1800, 0.7)], 0.05, 0.4) * 0.5, t,
               pan=float(g.uniform(0.3, 0.9)), gain=float(g.uniform(0.15, 0.3)))
    return mx, _room(SEED % 9973 + 5, 0.9, 1.6, highcut=6000.0)


def quellan_town(g):
    mx, L = _mixer("quellan_town")
    mx.bus("wind", 0.0, send=0.1)
    mx.bus("town", 0.0, send=0.35, process=lambda x: filt(x, [bq_lowpass(2800, 0.7)]))
    mx.bus("work", 0.0, send=0.35)
    mx.bus("far", 0.0, send=0.5, process=lambda x: filt(x, [bq_lowpass(2500, 0.7)]))
    gust = 0.5 + 0.5 * FA.plfo(L, 0.06, g)
    mx.add("wind", FA.stereo_noise(L, g, [bq_lowpass(1000, 0.6), bq_highpass(100, 0.7)], 0.4)
           * (0.35 + 0.65 * gust ** 1.5)[:, None] * 0.12, 0.0)
    for t in FA.schedule(L, 3.5, g, 0.6):
        mx.add("work", flap(g), t, pan=float(g.uniform(-0.8, 0.8)), gain=float(g.uniform(0.15, 0.35)))
    t = 0.5
    while t < LOOPS["quellan_town"] - 2.0:
        mx.add("town", FA.murmur_phrase(g, bool(g.random() < 0.5)), t, pan=float(g.uniform(-0.7, 0.7)),
               gain=float(g.uniform(0.25, 0.6)))
        t += float(g.uniform(1.2, 3.5))
    mx.add("work", loom(g, 18.0, 1.1), 6.0, pan=0.55, gain=0.18)
    for t in FA.schedule(L, 13.0, g, 0.4):
        mx.add("far", goat_bell(g), t, pan=float(g.uniform(-0.8, 0.8)), gain=float(g.uniform(0.08, 0.16)))
    return mx, _room(SEED % 9973 + 6, 0.8, 1.4)


def cloudloom_hall(g):
    mx, L = _mixer("cloudloom_hall")
    mx.bus("looms", 0.0, send=0.4)
    mx.bus("cords", 0.0, send=0.3, process=lambda x: filt(x, [bq_lowpass(4000, 0.7)]))
    mx.bus("voices", 0.0, send=0.5, process=lambda x: filt(x, [bq_lowpass(2600, 0.7)]))
    mx.bus("air", 0.0, send=0.1)
    gust = 0.5 + 0.5 * FA.plfo(L, 0.07, g)
    mx.add("air", FA.stereo_noise(L, g, [bq_lowpass(1200, 0.6), bq_highpass(150, 0.7)], 0.4)
           * (0.4 + 0.6 * gust)[:, None] * 0.08, 0.0)
    for k in range(4):                                                     # four looms across the hall
        mx.add("looms", loom(g, LOOPS["cloudloom_hall"] - 2.0, float(g.uniform(0.8, 1.3))), float(g.uniform(0.0, 1.5)),
               pan=-0.75 + 0.5 * k, gain=float(g.uniform(0.12, 0.22)))
    for t in FA.schedule(L, 0.5, g, 0.8):                                  # the keth stirring in the wind
        mx.add("cords", reed_rustle(g, float(g.uniform(0.6, 1.4))), t, pan=float(g.uniform(-0.9, 0.9)),
               gain=float(g.uniform(0.04, 0.1)) * float(0.5 + 0.5 * gust[min(L - 1, int(t * SR))]))
    t = 3.0
    while t < LOOPS["cloudloom_hall"] - 3.0:
        mx.add("voices", FA.murmur_phrase(g, True), t, pan=float(g.uniform(-0.6, 0.6)), gain=float(g.uniform(0.2, 0.4)))
        t += float(g.uniform(3.0, 7.0))
    return mx, _room(SEED % 9973 + 7, 1.8, 2.2, highcut=5500.0)


def hull_tick(g) -> np.ndarray:
    """A lacquered hull at its mooring: a small hard tick as it touches the post."""
    b = float(g.uniform(600, 900))
    return FA.modal([b, b * 2.1, b * 3.7], [0.02, 0.012, 0.006], [1.0, 0.4, 0.15], 0.1, g, click=0.4)


def far_bell(g) -> np.ndarray:
    from synth.bells import tower_bell
    return tower_bell(float(g.choice([50.0, 52.0, 55.0])), 0.5, seed=int(g.integers(1 << 30)), t60=7.0, dark=0.7)


def page(g) -> np.ndarray:
    """A page turned: a lift, a soft flutter and the paper settling."""
    n = int(0.6 * SR)
    t = np.arange(n) / n
    y = filt(g.standard_normal(n), [bq_bandpass(float(g.uniform(2500, 3800)), 1.0)])
    return y * (np.sin(np.pi * t) ** 2) * (0.6 + 0.4 * np.sin(2 * np.pi * 14 * t) ** 2)


def mouth_moan(L: int, g, f0: float) -> np.ndarray:
    """Wind through a colossal stone mouth: noise through two resonances near f0 and 2.7 f0, swelling slowly."""
    swell = 0.3 + 0.7 * (0.5 + 0.5 * FA.plfo(L, float(g.uniform(0.02, 0.05)), g)) ** 2
    y = FA.stereo_noise(L, g, [bq_bandpass(f0, 12.0)], 0.5) + 0.4 * FA.stereo_noise(L, g, [bq_bandpass(f0 * 2.7, 10.0)], 0.5)
    return y * swell[:, None]


def ansedra_still(g):
    mx, L = _mixer("ansedra_still")
    mx.bus("air", 0.0, send=0.1)
    mx.bus("hulls", 0.0, send=0.4)
    mx.bus("far", 0.0, send=0.6, process=lambda x: filt(x, [bq_lowpass(2200, 0.7)]))
    mx.add("air", FA.stereo_noise(L, g, [bq_lowpass(500, 0.6), bq_highpass(60, 0.7)], 0.6) * 0.1, 0.0)
    for t in FA.schedule(L, 4.5, g, 0.6):
        mx.add("hulls", hull_tick(g), t, pan=float(g.uniform(-0.8, 0.8)), gain=float(g.uniform(0.1, 0.3)))
    t = 2.0
    while t < LOOPS["ansedra_still"] - 3.0:
        mx.add("far", FA.murmur_phrase(g, bool(g.random() < 0.5)), t, pan=float(g.uniform(-0.6, 0.6)),
               gain=float(g.uniform(0.15, 0.3)))
        t += float(g.uniform(4.0, 9.0))
    mx.add("far", far_bell(g), 21.0, pan=0.4, gain=0.25)
    return mx, _room(SEED % 9973 + 8, 2.2, 2.0, highcut=5000.0)


def lacquer_court(g):
    mx, L = _mixer("lacquer_court")
    mx.bus("crowd", 0.0, send=0.35, process=lambda x: filt(x, [bq_lowpass(2600, 0.7)]))
    mx.bus("silk", 0.0, send=0.25)
    mx.bus("water", 0.0, send=0.2)
    mx.bus("far", 0.0, send=0.5, process=lambda x: filt(x, [bq_lowpass(1500, 0.7)]))
    mx.bus("floor", 0.0, send=0.3)
    mx.add("floor", FA.stereo_noise(L, g, [bq_bandpass(500, 0.6), bq_lowpass(1500, 0.7)], 0.5) * 0.12, 0.0)  # the crowd
    mx.add("floor", FA.stereo_noise(L, g, [bq_lowpass(300, 0.6), bq_highpass(50, 0.7)], 0.6) * 0.08, 0.0)    # the court
    t = 0.3
    while t < LOOPS["lacquer_court"] - 2.0:
        mx.add("crowd", FA.murmur_phrase(g, bool(g.random() < 0.5)), t, pan=float(g.uniform(-0.8, 0.8)),
               gain=float(g.uniform(0.2, 0.45)))
        t += float(g.uniform(0.3, 0.9))
    for t in FA.schedule(L, 2.8, g, 0.6):
        mx.add("silk", filt(reed_rustle(g, float(g.uniform(0.5, 1.0))), [bq_lowpass(4000, 0.7)]), t,
               pan=float(g.uniform(-0.8, 0.8)), gain=float(g.uniform(0.02, 0.05)))
    for t in FA.schedule(L, 3.0, g, 0.5):
        mx.add("water", FA.lap(g, float(g.uniform(0.4, 0.7))), t, pan=float(g.uniform(-0.5, 0.5)),
               gain=float(g.uniform(0.15, 0.3)))
    from synth.gongs import kettle_gong
    mx.add("far", kettle_gong(38.0, 0.5, seed=int(g.integers(1 << 30)), t60=3.0), 30.0, pan=-0.5, gain=0.4)
    return mx, _room(SEED % 9973 + 9, 1.6, 1.6)


def archive_room(g):
    mx, L = _mixer("archive_room")
    mx.bus("room", 0.0, send=0.2)
    mx.bus("lamp", 0.0, send=0.25)
    mx.bus("paper", 0.0, send=0.4)
    mx.add("room", FA.stereo_noise(L, g, [bq_lowpass(350, 0.6), bq_highpass(50, 0.7)], 0.7) * 0.08, 0.0)
    mx.add("lamp", fire(g, LOOPS["archive_room"] - 1.0) * 0.6, 0.5, pan=0.3, gain=0.2)
    for t in FA.schedule(L, 6.0, g, 0.6):
        mx.add("paper", page(g) if g.random() < 0.4 else reed_rustle(g, float(g.uniform(0.3, 0.6))) * 0.5, t,
               pan=float(g.uniform(-0.8, 0.8)), gain=float(g.uniform(0.08, 0.2)))
    return mx, _room(SEED % 9973 + 10, 1.1, 1.0, highcut=6000.0)


def sanctum_basin(g):
    mx, L = _mixer("sanctum_basin")
    mx.bus("air", 0.0, send=0.4)
    mx.add("air", FA.stereo_noise(L, g, [bq_lowpass(260, 0.6), bq_highpass(40, 0.7)], 0.8) * 0.12, 0.0)
    mx.add("air", FA.stereo_noise(L, g, [bq_bandpass(900, 0.6)], 0.8) * 0.015, 0.0)
    return mx, _room(SEED % 9973 + 11, 4.0, 2.4, highcut=4000.0)


def open_sea_night(g):
    mx, L = _mixer("open_sea_night")
    mx.bus("sea", 0.0, send=0.1)
    mx.bus("barge", 0.0, send=0.25)
    mx.bus("cloth", 0.0, send=0.2)
    swell = 0.5 + 0.5 * FA.plfo(L, 0.09, g)
    mx.add("sea", FA.stereo_noise(L, g, [bq_lowpass(450, 0.6), bq_highpass(40, 0.7)], 0.5)
           * (0.6 + 0.4 * swell)[:, None] * 0.16, 0.0)
    for t in FA.schedule(L, 1.6, g, 0.5):
        mx.add("sea", FA.slap(g) if g.random() < 0.5 else FA.lap(g, 0.9), t, pan=float(g.uniform(-0.8, 0.8)),
               gain=float(g.uniform(0.25, 0.6)))
    for t in FA.schedule(L, 3.4, g, 0.5):
        mx.add("barge", creak(g, float(g.uniform(0.7, 1.4)), 35, 170), t, pan=float(g.uniform(-0.6, 0.6)),
               gain=float(g.uniform(0.2, 0.4)))
    for t in FA.schedule(L, 5.0, g, 0.5):
        mx.add("cloth", reed_rustle(g, float(g.uniform(0.8, 1.6))) * 0.7, t, pan=-0.3, gain=float(g.uniform(0.06, 0.12)))
    return mx, _room(SEED % 9973 + 12, 0.6, 1.2, highcut=5500.0)


def pale_rim_shallows(g):
    mx, L = _mixer("pale_rim_shallows")
    mx.bus("wind", 0.0, send=0.1)
    mx.bus("wash", 0.0, send=0.15)
    mx.bus("far", 0.0, send=0.5, process=lambda x: filt(x, [bq_lowpass(2500, 0.7)]))
    gust = 0.5 + 0.5 * FA.plfo(L, 0.05, g)
    mx.add("wind", FA.stereo_noise(L, g, [bq_lowpass(900, 0.6), bq_highpass(150, 0.7)], 0.4)
           * (0.4 + 0.6 * gust)[:, None] * 0.1, 0.0)
    mx.add("wash", FA.stereo_noise(L, g, [bq_bandpass(1800, 0.5), bq_highpass(600, 0.7)], 0.3)
           * (0.5 + 0.5 * FA.plfo(L, 0.12, g))[:, None] * 0.05, 0.0)
    for t in FA.schedule(L, 4.0, g, 0.6):
        mx.add("far", FA.lap(g, float(g.uniform(0.3, 0.6))), t, pan=float(g.uniform(-0.9, 0.9)),
               gain=float(g.uniform(0.15, 0.3)))
    for t in FA.schedule(L, 17.0, g, 0.4):
        b = float(g.uniform(200, 320))
        mx.add("far", FA.modal([b, b * 2.4], [0.05, 0.03], [1.0, 0.4], 0.2, g, click=0.4), t,
               pan=float(g.uniform(-0.7, 0.7)), gain=0.2)
    return mx, _room(SEED % 9973 + 13, 0.4, 0.8)


def choir_bowl(g):
    mx, L = _mixer("choir_bowl")
    mx.bus("mouths", 0.0, send=0.5)
    mx.bus("water", 0.0, send=0.3)
    for k, f0 in enumerate((92.0, 123.0, 155.0, 207.0)):       # four mouths, never a chord that resolves
        mx.add("mouths", mouth_moan(L, g, f0) * (0.08 if k else 0.1), 0.0)
    for t in FA.schedule(L, 2.4, g, 0.6):
        mx.add("water", FA.lap(g, float(g.uniform(0.6, 1.2))), t, pan=float(g.uniform(-0.7, 0.7)),
               gain=float(g.uniform(0.2, 0.45)))
    return mx, _room(SEED % 9973 + 14, 3.0, 2.6, highcut=4500.0)


def mud_suck(g) -> np.ndarray:
    """Mud letting go: a short wet, low suck with a soft pop as the silt settles."""
    n = int(float(g.uniform(0.2, 0.4)) * SR)
    t = np.arange(n) / n
    y = filt(g.standard_normal(n), [bq_bandpass(float(g.uniform(180, 320)), 2.0), bq_lowpass(900, 0.7)])
    y = y / (np.abs(y).max() + 1e-9) * np.sin(np.pi * t) ** 2
    pop = FA.modal([float(g.uniform(300, 500))], [0.02], [1.0], 0.06, g, click=0.2)
    y[-len(pop):] += 0.4 * pop[: len(y)]
    return y


def silt_bubble(g) -> np.ndarray:
    """A bubble of fen gas rising through the silt and breaking: a low, rounded blip."""
    n = int(0.12 * SR)
    t = np.arange(n) / SR
    f = float(g.uniform(160, 300)) * (1 + 1.5 * t / t[-1])
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.03)


def trickle(L: int, g, centre: float) -> np.ndarray:
    """Water running thinly down rock: a narrow, bubbling band, steady, stereo."""
    y = FA.stereo_noise(L, g, [bq_bandpass(centre, 2.5), bq_bandpass(centre * 1.6, 1.5)], 0.4)
    return y * (0.7 + 0.3 * FA.plfo(L, 0.4, g))[:, None]


def arena_fen_roots(g):
    mx, L = _mixer("arena_fen_roots")
    mx.bus("air", 0.0, send=0.1)
    mx.bus("mud", 0.0, send=0.2)
    mx.bus("roots", 0.0, send=0.3)
    mx.add("air", FA.stereo_noise(L, g, [bq_lowpass(260, 0.6), bq_highpass(40, 0.7)], 0.6) * 0.14, 0.0)
    for t in FA.schedule(L, 2.2, g, 0.6):
        mx.add("mud", mud_suck(g), t, pan=float(g.uniform(-0.7, 0.7)), gain=float(g.uniform(0.15, 0.35)))
    for t in FA.schedule(L, 1.7, g, 0.7):
        mx.add("mud", silt_bubble(g), t, pan=float(g.uniform(-0.8, 0.8)), gain=float(g.uniform(0.1, 0.25)))
    for t in FA.schedule(L, 2.0, g, 0.6):
        mx.add("mud", drip(float(g.uniform(0.15, 0.4)), float(g.uniform(1.4, 2.8)), seed=int(g.integers(1 << 30))), t,
               pan=float(g.uniform(-0.8, 0.8)), gain=float(g.uniform(0.1, 0.25)))
    for t in FA.schedule(L, 6.0, g, 0.5):
        mx.add("roots", creak(g, float(g.uniform(0.8, 1.6)), 30, 120), t, pan=float(g.uniform(-0.7, 0.7)),
               gain=float(g.uniform(0.2, 0.4)))
    return mx, _room(SEED % 9973 + 15, 1.0, 1.4, highcut=5000.0)


def arena_engine_hall(g):
    mx, L = _mixer("arena_engine_hall")
    mx.bus("throb", 0.0, send=0.35, process=lambda x: filt(x, [bq_lowpass(500, 0.7)]))
    mx.bus("hum", 0.0, send=0.35)
    mx.bus("water", 0.0, send=0.45)
    mx.add("throb", throb(L, g, 0.5, 55.0) * 0.16, 0.0)                    # the engine, near now
    mx.add("throb", throb(L, g, 0.5, 110.0) * 0.04, 0.0)
    mx.add("hum", conduit_hum(L, g, 130.0) * 0.06, 0.0)
    mx.add("water", FA.stereo_noise(L, g, [bq_lowpass(380, 0.6), bq_highpass(50, 0.7)], 0.6) * 0.1, 0.0)
    for t in FA.schedule(L, 2.2, g, 0.5):
        mx.add("water", FA.lap(g, float(g.uniform(0.5, 0.9))), t, pan=float(g.uniform(-0.7, 0.7)),
               gain=float(g.uniform(0.2, 0.45)))
    for t in FA.schedule(L, 3.0, g, 0.7):
        mx.add("water", drip(float(g.uniform(0.2, 0.5)), float(g.uniform(2.0, 3.4)), seed=int(g.integers(1 << 30))), t,
               pan=float(g.uniform(-0.9, 0.9)), gain=float(g.uniform(0.1, 0.3)))
    return mx, _room(SEED % 9973 + 16, 3.4, 2.6, highcut=4800.0)


def arena_seep_terrace(g):
    mx, L = _mixer("arena_seep_terrace")
    mx.bus("wind", 0.0, send=0.1)
    mx.bus("seep", 0.0, send=0.25)
    mx.bus("stone", 0.0, send=0.35)
    gust = 0.5 + 0.5 * FA.plfo(L, 0.06, g)
    mx.add("wind", FA.stereo_noise(L, g, [bq_lowpass(1100, 0.6), bq_highpass(110, 0.7)], 0.4)
           * (0.35 + 0.65 * gust ** 1.4)[:, None] * 0.13, 0.0)
    mx.add("seep", trickle(L, g, 1900.0) * 0.025, 0.0)                   # the wall seeping
    mx.add("seep", trickle(L, g, 3100.0) * 0.012, 0.0)
    for t in FA.schedule(L, 1.4, g, 0.7):                                  # over the kerb
        mx.add("seep", drip(float(g.uniform(0.15, 0.4)), float(g.uniform(1.6, 3.0)), seed=int(g.integers(1 << 30))), t,
               pan=float(g.uniform(-0.8, 0.8)), gain=float(g.uniform(0.1, 0.25)))
    for t in FA.schedule(L, 13.0, g, 0.4):                                 # a stone loosed above
        mx.add("stone", FA.burst(g, 0.9, [bq_bandpass(1500, 0.7)], 0.03, 0.3) * 0.5, t,
               pan=float(g.uniform(-0.8, 0.8)), gain=float(g.uniform(0.12, 0.25)))
    return mx, _room(SEED % 9973 + 17, 0.9, 1.5, highcut=6000.0)


def arena_lagoon_dusk(g):
    mx, L = _mixer("arena_lagoon_dusk")
    mx.bus("water", 0.0, send=0.15)
    mx.bus("barge", 0.0, send=0.3)
    mx.bus("far", 0.0, send=0.6, process=lambda x: filt(x, [bq_lowpass(2000, 0.7)]))
    mx.add("water", FA.stereo_noise(L, g, [bq_lowpass(500, 0.6), bq_highpass(50, 0.7)], 0.6) * 0.1, 0.0)
    for t in FA.schedule(L, 1.3, g, 0.5):                                  # the stillness broken
        mx.add("water", FA.lap(g, float(g.uniform(0.4, 0.8))), t, pan=float(g.uniform(-0.8, 0.8)),
               gain=float(g.uniform(0.2, 0.5)))
    for t in FA.schedule(L, 4.0, g, 0.5):
        mx.add("barge", hull_tick(g) if g.random() < 0.5 else creak(g, float(g.uniform(0.6, 1.1)), 40, 190), t,
               pan=float(g.uniform(-0.6, 0.6)), gain=float(g.uniform(0.15, 0.35)))
    t = 1.5
    while t < LOOPS["arena_lagoon_dusk"] - 3.0:                            # the city's voices, far and raised
        mx.add("far", FA.murmur_phrase(g, bool(g.random() < 0.6)), t, pan=float(g.uniform(-0.8, 0.8)),
               gain=float(g.uniform(0.15, 0.3)))
        t += float(g.uniform(1.5, 4.0))
    for at in (8.0, 29.0):
        mx.add("far", far_bell(g), at, pan=float(g.uniform(-0.5, 0.5)), gain=0.22)
    return mx, _room(SEED % 9973 + 18, 2.0, 2.0, highcut=5000.0)


def arena_court_steps(g):
    mx, L = _mixer("arena_court_steps")
    mx.bus("crowd", 0.0, send=0.5, process=lambda x: filt(x, [bq_lowpass(1800, 0.7)]))
    mx.bus("silk", 0.0, send=0.25)
    mx.bus("water", 0.0, send=0.2)
    mx.bus("far", 0.0, send=0.5, process=lambda x: filt(x, [bq_lowpass(1500, 0.7)]))
    mx.add("crowd", FA.stereo_noise(L, g, [bq_bandpass(450, 0.6), bq_lowpass(1200, 0.7)], 0.5) * 0.06, 0.0)
    t = 1.0
    while t < LOOPS["arena_court_steps"] - 2.0:                            # drawn back, low and far
        mx.add("crowd", FA.murmur_phrase(g, bool(g.random() < 0.5)), t, pan=float(g.uniform(-0.9, 0.9)),
               gain=float(g.uniform(0.12, 0.28)))
        t += float(g.uniform(1.0, 2.6))
    for t in FA.schedule(L, 2.4, g, 0.6):
        mx.add("silk", filt(reed_rustle(g, float(g.uniform(0.6, 1.2))), [bq_lowpass(4000, 0.7)]), t,
               pan=float(g.uniform(-0.8, 0.8)), gain=float(g.uniform(0.03, 0.06)))
    for t in FA.schedule(L, 2.6, g, 0.5):
        mx.add("water", FA.lap(g, float(g.uniform(0.4, 0.7))), t, pan=float(g.uniform(-0.5, 0.5)),
               gain=float(g.uniform(0.15, 0.3)))
    from synth.gongs import kettle_gong
    mx.add("far", kettle_gong(36.0, 0.5, seed=int(g.integers(1 << 30)), t60=3.0), 22.0, pan=0.5, gain=0.35)
    return mx, _room(SEED % 9973 + 19, 1.6, 1.6)


def wheel(g, sec: float, period: float) -> np.ndarray:
    """A tide-wheel turning slowly: a paddle's wet slap and a wooden axle knock, once every `period` s."""
    out = np.zeros(int(sec * SR))
    t = float(g.uniform(0, period))
    while t < sec - 0.6:
        s = int(t * SR)
        x = 0.6 * FA.slap(g)
        out[s: s + len(x)] += x[: len(out) - s]
        b = float(g.uniform(140, 190))
        k = FA.modal([b, b * 2.5], [0.06, 0.03], [1.0, 0.3], 0.3, g, click=0.3) * 0.5
        s2 = int((t + 0.25) * SR)
        out[s2: s2 + len(k)] += k[: max(0, len(out) - s2)]
        t += period * float(g.uniform(0.95, 1.05))
    return out


def hollowmere_flotilla(g):
    mx, L = _mixer("hollowmere_flotilla")
    mx.bus("water", 0.0, send=0.15)
    mx.bus("wheels", 0.0, send=0.3)
    mx.bus("pump", 0.0, send=0.25, process=lambda x: filt(x, [bq_lowpass(900, 0.7)]))
    mx.bus("far", 0.0, send=0.5, process=lambda x: filt(x, [bq_lowpass(3000, 0.7)]))
    mx.add("water", FA.stereo_noise(L, g, [bq_lowpass(500, 0.6), bq_highpass(50, 0.7)], 0.5) * 0.1, 0.0)
    for t in FA.schedule(L, 1.4, g, 0.5):                                  # water among the hulls
        mx.add("water", FA.slap(g) if g.random() < 0.4 else FA.lap(g, 0.8), t, pan=float(g.uniform(-0.9, 0.9)),
               gain=float(g.uniform(0.2, 0.5)))
    for k, (pan, period) in enumerate(((-0.6, 4.2), (0.5, 5.6))):          # two tide-wheels, out of step
        mx.add("wheels", wheel(g, LOOPS["hollowmere_flotilla"] - 1.0, period), 0.3 + k, pan=pan, gain=0.3 - 0.1 * k)
    mx.add("pump", throb(L, g, 1.2, 98.0) * 0.06, 0.0)                     # a pump's steady stroke
    mx.add("pump", conduit_hum(L, g, 98.0) * 0.015, 0.0)
    for t in FA.schedule(L, 9.0, g, 0.5):                                  # gulls
        mx.add("far", FA.gull_call(g), t, pan=float(g.uniform(-0.9, 0.9)), gain=float(g.uniform(0.1, 0.22)))
    for t in FA.schedule(L, 12.0, g, 0.5):                                 # hammers, far off and few
        mx.add("far", FA.mallet_cluster(g), t, pan=float(g.uniform(-0.8, 0.8)), gain=float(g.uniform(0.1, 0.2)))
    t = 3.0
    while t < LOOPS["hollowmere_flotilla"] - 3.0:                          # low voices, a people grieving at work
        mx.add("far", FA.murmur_phrase(g, bool(g.random() < 0.4)), t, pan=float(g.uniform(-0.7, 0.7)),
               gain=float(g.uniform(0.12, 0.25)))
        t += float(g.uniform(3.0, 7.0))
    return mx, _room(SEED % 9973 + 20, 0.9, 1.6, highcut=6000.0)


def open_sea_fog(g):
    mx, L = _mixer("open_sea_fog")
    mx.bus("sea", 0.0, send=0.2)
    mx.bus("barge", 0.0, send=0.3)
    mx.bus("drip", 0.0, send=0.4)
    swell = 0.5 + 0.5 * FA.plfo(L, 0.07, g)
    mx.add("sea", FA.stereo_noise(L, g, [bq_lowpass(300, 0.6), bq_highpass(40, 0.7)], 0.6)
           * (0.6 + 0.4 * swell)[:, None] * 0.12, 0.0)
    for t in FA.schedule(L, 3.2, g, 0.5):                                  # a low swell lapping the hull
        mx.add("sea", FA.lap(g, float(g.uniform(0.6, 1.0))), t, pan=float(g.uniform(-0.6, 0.6)),
               gain=float(g.uniform(0.15, 0.35)))
    for t in FA.schedule(L, 1.6, g, 0.7):                                  # fog-damp off the canopy and the hook
        mx.add("drip", drip(float(g.uniform(0.1, 0.3)), float(g.uniform(2.6, 4.2)), seed=int(g.integers(1 << 30))), t,
               pan=float(g.uniform(-0.8, 0.8)), gain=float(g.uniform(0.06, 0.16)))
    for t in FA.schedule(L, 8.0, g, 0.5):                                  # the barge barely creaking
        mx.add("barge", creak(g, float(g.uniform(0.8, 1.4)), 30, 140), t, pan=float(g.uniform(-0.5, 0.5)),
               gain=float(g.uniform(0.12, 0.22)))
    return mx, _room(SEED % 9973 + 21, 1.6, 2.2, highcut=3500.0)     # fog: a close, dull, swallowing room


def choir_storm(g):
    mx, L = _mixer("choir_storm")
    mx.bus("gale", 0.0, send=0.1)
    mx.bus("mouths", 0.0, send=0.4)
    mx.bus("surge", 0.0, send=0.25)
    mx.bus("roar", 0.0, send=0.2, process=lambda x: filt(x, [bq_lowpass(220, 0.7)]))
    gust = 0.5 + 0.5 * FA.plfo(L, 0.11, g)
    mx.add("gale", FA.stereo_noise(L, g, [bq_lowpass(2400, 0.6), bq_highpass(150, 0.7)], 0.3)
           * (0.45 + 0.55 * gust ** 1.3)[:, None] * 0.2, 0.0)
    for k, f0 in enumerate((92.0, 123.0, 155.0, 207.0)):                  # the same mouths, roaring now
        mx.add("mouths", mouth_moan(L, g, f0) * (0.1 + 0.02 * k) * (0.5 + 0.5 * gust)[:, None], 0.0)
    for t in FA.schedule(L, 2.2, g, 0.4):                                  # surge in the ring channel, and spray
        mx.add("surge", FA.burst(g, 1.4, [bq_lowpass(1600, 0.7), bq_highpass(120, 0.7)], 0.15, 0.6), t,
               pan=float(g.uniform(-0.9, 0.9)), gain=float(g.uniform(0.25, 0.5)))
        mx.add("surge", FA.burst(g, 0.8, [bq_bandpass(3500, 0.7)], 0.02, 0.3), t + 0.25,
               pan=float(g.uniform(-0.9, 0.9)), gain=float(g.uniform(0.06, 0.12)))
    mx.add("roar", FA.stereo_noise(L, g, [bq_lowpass(160, 0.6), bq_highpass(30, 0.7)], 0.7) * 0.25, 0.0)
    return mx, _room(SEED % 9973 + 22, 2.4, 2.6, highcut=5000.0)


BEDS = {"fen_dusk": fen_dusk, "reedhollow_roost": reedhollow_roost, "vey_galleries": vey_galleries,
        "lowlight_temple": lowlight_temple, "keth_pass_wind": keth_pass_wind, "quellan_town": quellan_town,
        "cloudloom_hall": cloudloom_hall, "ansedra_still": ansedra_still, "lacquer_court": lacquer_court,
        "archive_room": archive_room, "sanctum_basin": sanctum_basin, "open_sea_night": open_sea_night,
        "pale_rim_shallows": pale_rim_shallows, "choir_bowl": choir_bowl, "arena_fen_roots": arena_fen_roots,
        "arena_engine_hall": arena_engine_hall, "arena_seep_terrace": arena_seep_terrace,
        "arena_lagoon_dusk": arena_lagoon_dusk, "arena_court_steps": arena_court_steps,
        "hollowmere_flotilla": hollowmere_flotilla, "open_sea_fog": open_sea_fog, "choir_storm": choir_storm}
FILES = [f"{b}{ext}" for b in BEDS for ext in (".ogg", ".loop.json")]


def render_bed(name: str, out_dir: str = OUT_DIR, verbose: bool = True) -> dict:
    g = rng(SEED + 101 * (list(BEDS).index(name) + 1))
    mx, verb = BEDS[name](g)
    _, loop = mx.render(reverb=verb, reverb_return_db=-4.0, hp_hz=30.0)
    _, loop = master_loop(np.zeros((0, 2)), loop, TARGET_LUFS, ceiling_db=CEILING_DB, report={})
    n_ = len(loop)
    write_ogg(os.path.join(out_dir, name + ".ogg"), loop, quality=QUALITY, tags={"LOOPSTART": "0", "LOOPLENGTH": str(n_)})
    write_loop_sidecar(os.path.join(out_dir, name + ".loop.json"), SR, 0, n_, None, None)
    m = measure(loop)
    if verbose:
        print(f"{name}: {m['seconds']:.2f}s  {m['integrated_lufs']:.2f} LUFS  peak {m['sample_peak_dbfs']:.2f} dBFS")
    return m


def render(out_dir: str = OUT_DIR, verbose: bool = True) -> dict:
    os.makedirs(out_dir, exist_ok=True)
    return {name: render_bed(name, out_dir, verbose) for name in BEDS}


if __name__ == "__main__":
    render()
