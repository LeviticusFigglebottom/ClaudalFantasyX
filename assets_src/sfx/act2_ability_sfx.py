"""Act II's enemy abilities, each with its own sound (M4-A2P-093; the Act II audit's "Abilities", tools/audio/
act1_audio_audit.py --act 2; plain git, ADR 0175).

Every Act II ability effect (effects.json map.skills) borrowed a generic hit row when battle-presentation gave it a
VFX. Each gets its own sound here, made from the creature's own materials (act2_creature_sfx.py: the Drowner's roots
and tannin water, the Engine's brass and salt-glass lamps, the woolback's wet wool and hooves, the urchin's salt-glass,
the skate's sand). The creature's voice plays on its clip (creature_voices.json), so these are the effect itself: the
blow, the water, the light. No ice anywhere (ADR 0204 §2): scree_slide is snow and grit, rime_spine is salt-glass.

    core_pulse         the Lamp Engine's bared core pulsing (all foes): a hum swelling into a bright glass bloom
    drowner_drag       two roots haul a hero along the water: creak, drag, the roots knocking shut
    glide_lash         the gallery ray's tail: the broad wing, a whip of air, the lash
    horn_toss          the ram's head-toss: a hoof, the wet locks swinging, the heavy blow, water shed
    lamp_flare         the lamps loosed together (darkness): salt-glass rings rising to a flash, then dimming
    lamp_gather        every lamp swings to face the party: ratchets, a rising hum, the lamps chiming in turn
    lamp_trim          the shear arm snips: the blade, the brass ring of the arm
    leech_bite         the fen leech's draining bite: a wet catch and the pull drawn back up to it
    ram_bellow         the bellow and the snow sliding off the terrace (slow)
    ram_charge         the stamp, three strides gathering, the drive through
    ram_charge_gather  the head drops and it paws the terrace: two slow hooves, a snort, a held breath
    rime_spine         a salt-glass spine breaking in a striker (slow): the crack, the shards, the ring
    rising_water       the Drowner's roots spread and the tannin water rises over the party
    root_drag          the root crab drags its target into the roots (delay): a smaller creak and drag, a knock
    root_stamp         the risen Drowner stamps on its root-feet: a heavy wet blow, the roots knocking
    scree_slide        the scree crawler sheds split scree: grit and stones sliding, snow hiss behind (no ice)
    skate_sting        the glass skate's tail from the sand (poison): sand, the whip, the sting's sharp tick
    tannin_jet         the archer's jet, which knocks its target back: the pressured hiss, the splash, the shove
    tide_gather        the risen Drowner draws its roots in (a charge): slow creaks, the water drawn off, a low moan

Synthesized here and in tools/audio/synth/ (SPEC §2, §9). Files are assets/audio/act2/sfx/battle/abl_<id>.ogg (mono,
q4), at -19 LUFS momentary max (the combat rule).

Render:  python3 tools/audio/render_all.py --only act2_ability_sfx
"""
from __future__ import annotations

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools", "audio"))
sys.path.insert(0, HERE)

import numpy as np  # noqa: E402

import act2_creature_sfx as A2  # noqa: E402
from act2_creature_sfx import (SALT_GLASS, SALT_GLASS_DECAY, Archer, Drowner, Engine, Ray, Skate, Urchin,  # noqa: E402
                               Woolback, splash, whoosh)
from creature_sfx import buf, burst, crackle, creak, finish, glass_ring, gurgle, room, slosh, tap, thump  # noqa: E402
from synth.dsp import bq_bandpass, bq_highpass, bq_lowpass, bq_peak, filt, rng  # noqa: E402
from synth.mixer import measure, write_ogg  # noqa: E402
from underwater_sfx import _n, _t, noise, place  # noqa: E402

OUT_DIR = os.path.join(ROOT, "assets", "audio", "act2", "sfx", "battle")
SEED = 20262400
QUALITY = 4.0
CAST = -19.0
CRAB_ROOT = [(f * 1.6, a) for f, a in Drowner.ROOT]          # the root crab's roots: smaller, higher


def _sweep(g, sec: float, f_from: float, f_to: float, q: float = 2.0) -> np.ndarray:
    """Noise in a narrow band sliding f_from -> f_to (block by block), unit peak."""
    n = _n(sec)
    f = f_from * (f_to / f_from) ** (_t(n) / sec)
    y = np.zeros(n)
    for k in range(0, n, 512):
        seg = noise(g, min(512, n - k) + 1024, [bq_bandpass(float(f[k]), q)])[1024:]
        y[k: k + len(seg)] = seg
    return y / (np.abs(y).max() + 1e-9)


def _swell(n: int, sec: float, shape: float = 1.5) -> np.ndarray:
    return np.clip(_t(n) / sec, 0, 1) ** shape


def core_pulse(g):
    x = buf(2.0)
    place(x, A2.hum(g, 1.1, 98.0, 0.5) * _swell(_n(1.1), 0.9), 0.0)
    for i, f in enumerate((1568.0, 2349.0, 3136.0)):           # the bloom: the bound light at once
        place(x, glass_ring(g, f, 1.0, 0.5), 0.75 + 0.01 * i)
    place(x, thump(g, 110, 50, 0.12, 0.3, 0.6), 0.75, 0.6)     # the pulse's wave
    place(x, A2.tinkle(g, 0.6, 5, 2400, 4200, 0.3), 0.8)
    return x


def drowner_drag(g):
    x = buf(1.8)
    place(x, creak(g, 0.5, 25, 110, Drowner.ROOT, 0.7), 0.0)
    drag = A2.roar(g, 0.7, 650) * np.sin(np.pi * _t(_n(0.7)) / 0.7) ** 1.5
    place(x, drag, 0.1, 0.7)
    place(x, slosh(g, 1.0, 0.9, 1.6), 0.25)
    place(x, Drowner.knock(g, 0.9), 0.55)
    place(x, Drowner.knock(g, 0.6), 0.62)
    return x


def glide_lash(g):
    x = buf(1.2)
    place(x, Ray.wing(g, 2, 3.5, 0.6), 0.0)
    place(x, whoosh(g, 0.22, 900, 3000, 0.8), 0.18)
    place(x, Ray.thwack(g, 1.0), 0.38)
    place(x, burst(g, 0.05, [bq_bandpass(2600, 1.2)], 0.001, 0.012), 0.38, 0.5)
    return x


def horn_toss(g):
    x = buf(1.6)
    place(x, Woolback.hoof(g, 0.8), 0.0)
    place(x, Woolback.locks(g, 0.35, 0.7), 0.15)
    place(x, thump(g, 150, 60, 0.09, 0.7, 0.5), 0.42, 1.0)     # the blow
    place(x, A2.burst(g, 0.06, [bq_bandpass(800, 0.9)], 0.002, 0.02), 0.42, 0.6)
    place(x, Woolback.wet(g, 0.5, 0.6), 0.45)
    return x


def lamp_flare(g):
    x = buf(2.0)
    for i, f in enumerate((1175.0, 1568.0, 2093.0, 2637.0)):    # the lamps swinging up, one by one
        place(x, glass_ring(g, f, 0.6, 0.3) * _swell(_n(0.6), 0.3), 0.08 * i)
    flash = noise(g, _n(0.25), [bq_highpass(3000, 0.7), bq_lowpass(9000, 0.7)])
    flash *= np.exp(-_t(len(flash)) / 0.06)
    place(x, flash / (np.abs(flash).max() + 1e-9), 0.45, 0.6)  # loosed together
    for i, f in enumerate((2349.0, 3136.0, 3951.0)):
        place(x, glass_ring(g, f, 1.2, 0.45), 0.45 + 0.004 * i)
    dim = A2.hum(g, 1.0, 196.0, 0.3, bend=(1.0, 0.7))           # and the light dimming in the eyes
    place(x, dim, 0.8)
    return x


def lamp_gather(g):
    x = buf(2.2)
    place(x, Engine.ratchet(g, 0.9, 8, 20, 0.6), 0.0)
    place(x, A2.hum(g, 1.6, 98.0, 0.5, bend=(0.85, 1.0)) * _swell(_n(1.6), 1.2), 0.1)
    for i, f in enumerate((1760.0, 2217.0, 2637.0, 3520.0)):    # each lamp coming to face the party
        place(x, glass_ring(g, f, 0.8, 0.35), 0.5 + 0.22 * i)
    return x


def lamp_trim(g):
    x = buf(1.0)
    place(x, whoosh(g, 0.2, 1800, 4200, 0.4), 0.0)
    place(x, Engine.snip(g, 1.0), 0.15)
    place(x, A2.clang(g, 1.05, 0.5, 0.6), 0.24)
    return x


def leech_bite(g):
    x = buf(1.3)
    place(x, burst(g, 0.08, [bq_bandpass(700, 0.8), bq_lowpass(2000, 0.7)], 0.002, 0.03), 0.0)   # the wet catch
    place(x, gurgle(g, 0.3, 24, 0.004, 0.01, 0.5), 0.02)
    pull = _sweep(g, 0.6, 400.0, 1400.0, 3.0) * np.sin(np.pi * _t(_n(0.6)) / 0.6)              # drawn back up
    place(x, pull, 0.2, 0.5)
    place(x, gurgle(g, 0.5, 14, 0.006, 0.016, 0.4), 0.35)
    return x


def ram_bellow(g):
    x = buf(2.4)
    place(x, Woolback.bellow(g, 1.2, A2.contour(62, 84, 58, 0.35), 0.5, 0.8), 0.0)
    n = _n(1.6)
    snow = noise(g, n, [bq_bandpass(2200, 0.6), bq_lowpass(5000, 0.7)]) * _swell(n, 0.6) * np.exp(-_t(n) / 1.0)
    place(x, snow / (np.abs(snow).max() + 1e-9), 0.5, 0.5)     # the snow sliding off the terrace
    place(x, thump(g, 60, 35, 0.6, 0.2, 1.6), 0.6, 0.5)                # the shelf letting go
    place(x, Woolback.wet(g, 0.6, 0.5), 0.3)
    return x


def ram_charge(g):
    x = buf(1.6)
    for i, at in enumerate((0.0, 0.22, 0.38)):                  # the stamp, then the strides gathering
        place(x, Woolback.hoof(g, 0.7 + 0.1 * i), at)
    place(x, Woolback.locks(g, 0.3, 0.6), 0.3)
    place(x, thump(g, 120, 45, 0.14, 0.8, 0.7), 0.55, 1.0)     # it drives through
    place(x, burst(g, 0.1, [bq_bandpass(600, 0.8)], 0.002, 0.04), 0.55, 0.6)
    place(x, Woolback.wet(g, 0.5, 0.5), 0.58)
    return x


def ram_charge_gather(g):
    x = buf(2.2)
    place(x, Woolback.hoof(g, 0.7), 0.0)
    place(x, Woolback.hoof(g, 0.6), 0.6)
    place(x, Woolback.snort(g, 0.8), 1.0)
    breath = noise(g, _n(0.9), [bq_bandpass(500, 0.7)]) * np.sin(np.pi * _t(_n(0.9)) / 0.9) ** 2
    place(x, breath / (np.abs(breath).max() + 1e-9), 1.2, 0.35)  # held
    return x


def rime_spine(g):
    x = buf(1.2)
    place(x, Urchin.crunch(g, 1.0), 0.0)
    place(x, tap(g, [880.0, 1450.0, 2150.0], [0.06, 0.04, 0.02], 0.9, 0.6), 0.0)   # the spine into the striker
    place(x, Urchin.field(g, 0.35, 40, 0.5, swell=False), 0.03)
    place(x, tap(g, SALT_GLASS, SALT_GLASS_DECAY, 0.5, 0.4, 0.1), 0.2)
    return x


def rising_water(g):
    x = buf(2.4)
    place(x, creak(g, 0.6, 20, 80, Drowner.ROOT, 0.5), 0.0)
    n = _n(1.6)
    rise = noise(g, n, [bq_lowpass(900, 0.7), bq_highpass(60, 0.7)]) * _swell(n, 1.3, 2.0)
    place(x, rise / (np.abs(rise).max() + 1e-9), 0.2, 0.7)       # the tannin water rising
    place(x, slosh(g, 1.4, 0.8, 1.1), 0.6)
    place(x, gurgle(g, 0.8, 16, 0.006, 0.016, 0.5), 0.9)
    place(x, splash(g, 0.8, 0.6, 1600), 1.5)
    return x


def root_drag(g):
    x = buf(1.4)
    place(x, creak(g, 0.4, 40, 160, CRAB_ROOT, 0.6), 0.0)
    drag = noise(g, _n(0.5), [bq_bandpass(1100, 0.8)]) * np.sin(np.pi * _t(_n(0.5)) / 0.5) ** 1.5
    place(x, drag / (np.abs(drag).max() + 1e-9), 0.15, 0.6)
    place(x, slosh(g, 0.6, 0.5, 2.0), 0.25)
    place(x, tap(g, [f for f, _ in CRAB_ROOT], [0.04, 0.03, 0.02, 0.012], 0.8, 0.7), 0.6)
    return x


def root_stamp(g):
    x = buf(1.6)
    place(x, creak(g, 0.35, 25, 90, Drowner.ROOT, 0.5), 0.0)
    place(x, thump(g, 95, 38, 0.2, 0.6, 0.8), 0.32, 1.0)
    place(x, splash(g, 1.0, 0.8, 1800), 0.33)
    place(x, Drowner.knock(g, 0.8), 0.34)
    place(x, Drowner.knock(g, 0.5), 0.42)
    return x


def scree_slide(g):
    x = buf(1.8)
    n = _n(1.0)
    grit = crackle(g, 1.0, 120, 2400, 0.7, 0.6) * np.sin(np.pi * _t(n) / 1.0)
    place(x, grit, 0.0)
    for i in range(6):                                          # stones knocking down the slope
        at = 0.1 + 0.13 * i + float(g.uniform(-0.03, 0.03))
        place(x, tap(g, [620.0 * (1 + 0.1 * i), 1400.0, 2900.0], [0.03, 0.02, 0.01], 0.6, 0.8), at)
    hiss = noise(g, _n(1.2), [bq_bandpass(3000, 0.7), bq_lowpass(6000, 0.7)]) * np.exp(-_t(_n(1.2)) / 0.5)
    place(x, hiss / (np.abs(hiss).max() + 1e-9), 0.25, 0.25)   # the snow behind it
    place(x, thump(g, 160, 80, 0.05, 0.6, 0.3), 0.7, 0.6)
    return x


def skate_sting(g):
    x = buf(1.1)
    place(x, Skate.sand(g, 0.25, 0.6), 0.0)
    place(x, whoosh(g, 0.16, 1400, 4200, 0.7), 0.15)
    place(x, tap(g, [2900.0, 4600.0, 6800.0], [0.02, 0.012, 0.008], 0.9, 0.9), 0.3)   # the sting
    place(x, Ray.thwack(g, 0.6), 0.3)
    hiss = noise(g, _n(0.35), [bq_bandpass(2200, 2.0)]) * np.exp(-_t(_n(0.35)) / 0.12)
    place(x, hiss / (np.abs(hiss).max() + 1e-9), 0.34, 0.25)    # the venom going in
    return x


def tannin_jet(g):
    x = buf(1.4)
    place(x, Archer.spit(g, 0.16, 1.0), 0.0)
    place(x, splash(g, 0.7, 0.6, 2200), 0.22)
    place(x, whoosh(g, 0.35, 1600, 500, 0.6), 0.25)              # knocked back
    place(x, thump(g, 140, 70, 0.06, 0.4, 0.3), 0.3, 0.5)
    return x


def tide_gather(g):
    x = buf(2.6)
    for i in range(3):                                          # the roots drawn in, one after another
        place(x, creak(g, 0.5, 18 + 4 * i, 70, Drowner.ROOT, 0.5), 0.2 + 0.55 * i)
    n = _n(2.0)
    draw = noise(g, n, [bq_lowpass(700, 0.7), bq_highpass(50, 0.7)]) * _swell(n, 1.8, 1.0)
    place(x, draw / (np.abs(draw).max() + 1e-9), 0.0, 0.5)      # the water drawn off
    place(x, gurgle(g, 1.2, 10, 0.008, 0.02, 0.4), 0.6)
    place(x, A2.moan(g, 1.6, A2.contour(48, 60, 50, 0.6), 0.5), 0.5)
    return x


ABILITIES: list[tuple[str, object]] = [
    ("core_pulse", core_pulse), ("drowner_drag", drowner_drag), ("glide_lash", glide_lash), ("horn_toss", horn_toss),
    ("lamp_flare", lamp_flare), ("lamp_gather", lamp_gather), ("lamp_trim", lamp_trim), ("leech_bite", leech_bite),
    ("ram_bellow", ram_bellow), ("ram_charge", ram_charge), ("ram_charge_gather", ram_charge_gather),
    ("rime_spine", rime_spine), ("rising_water", rising_water), ("root_drag", root_drag), ("root_stamp", root_stamp),
    ("scree_slide", scree_slide), ("skate_sting", skate_sting), ("tannin_jet", tannin_jet), ("tide_gather", tide_gather),
]
FILES = [f"abl_{name}.ogg" for name, _ in ABILITIES]
# Tone, set from the Act I ability set's spectra (act1_listening_report's harsh and mud measures): the glass, brass and
# spray pulled under 5-6 kHz and their presence dipped, the roots and water cleared of low-mid weight. The material
# stays (the shears and spines are still the brightest), but none sits more than 4 dB past the set's median.
DARKEN = [bq_lowpass(5200, 0.7), bq_peak(3800, -4.0, 0.8)]
CLEAR = [bq_highpass(110, 0.7), bq_peak(420, -5.0, 0.9)]
TONE = {"core_pulse": DARKEN, "glide_lash": DARKEN, "lamp_gather": DARKEN, "rime_spine": DARKEN,
        "skate_sting": DARKEN, "tannin_jet": DARKEN, "root_stamp": DARKEN + CLEAR,
        "lamp_trim": [bq_lowpass(4600, 0.7), bq_peak(3800, -6.0, 0.8)], "ram_bellow": DARKEN + CLEAR,
        "drowner_drag": CLEAR + [bq_peak(280, -3.0, 1.0)], "rising_water": CLEAR,
        "tide_gather": CLEAR + [bq_peak(280, -3.0, 1.0)]}


def render(out_dir: str = OUT_DIR, verbose: bool = True) -> dict:
    os.makedirs(out_dir, exist_ok=True)
    res = {}
    for i, (name, fn) in enumerate(ABILITIES):
        seed = SEED + 100 * i
        x = fn(rng(seed))
        if name in TONE:
            x = filt(x, TONE[name])
        x = finish(room(x, seed + 7, mix=0.12, tail=0.4, rt60=0.9), CAST)
        write_ogg(os.path.join(out_dir, f"abl_{name}.ogg"), x, quality=QUALITY)
        res[name] = m = measure(x)
        if verbose:
            print(f"abl_{name}: {m['seconds']:.2f}s  Mmax {m['momentary_max_lufs']:.2f}  TP {m['true_peak_dbtp']:.2f}",
                  flush=True)
    return res


if __name__ == "__main__":
    render()
