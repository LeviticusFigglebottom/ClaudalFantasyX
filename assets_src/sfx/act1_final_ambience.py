"""Act I's last unbedded zones, each given its own ambience bed (M3-AUD-861, ADR 0041; Git LFS, ADR 0173).

The audit (tools/audio/act1_audio_audit.py, "Zones") found three Act I zones with music but no bed under it. Each
bed is a seamless loop built as act1_ambience.py builds its beds (LoopMixer, field_ambience's sources, -26 LUFS
integrated with peaks well down, mix.md), from its environment sheet:

    oruvel_raft          Ch1, Oruvel (docs/kb/art/environments/oruvel.md): "the brightest morning in the game on a
                         poor, loud, patched-together town that floats". Lashed hulls knocking and creaking against
                         each other on the swell, water slapping in the gaps between them, the cook-boats' stoves
                         crackling, the market's voices, rope, and the gulls over it all.
    brightwater_deck     Ch4, the Brightwater ferry at sea (brightwater_ferry.md): a broad-beamed plank ship running up
                         the strait with the trade wind on her beam. The bow wash, never stopping; the sails bellied
                         and the rigging working; her timbers; the caged oil lamp swinging on its hook; the reef's surf
                         far off to the east.
    coilspire_flues      Ch8, Coilspire (coilspire.md): a hollow stone spire on the headland where storms break,
                         "a chimney you climb": the keeping fire drawn up through three copper flues coiled in its
                         walls. The flues' low roar, copper ticking as it heats, the storm's wind outside the stone,
                         and the hollow of the spire itself.

assets/lfs/audio/ambience/<bed>.ogg + .loop.json (stereo, Vorbis q1 like the Act I beds; the ambience rule
`ambience/*.ogg`: -26 LUFS integrated +- 0.5, true peak under -5 dBTP). Synthesized (SPEC §2, §9).

Render:  python3 tools/audio/render_all.py --only act1_final_ambience
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

_spec = importlib.util.spec_from_file_location("field_ambience", os.path.join(HERE, "field_ambience.py"))
FA = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(FA)

OUT_DIR = os.path.join(ROOT, "assets", "lfs", "audio", "ambience")
SEED = 20261863
TARGET_LUFS = -26.0
CEILING_DB = -6.0
QUALITY = 1.0
LOOPS = {"oruvel_raft": 44.0, "brightwater_deck": 42.0, "coilspire_flues": 40.0}


def _mixer(name: str) -> tuple[LoopMixer, int]:
    mx = LoopMixer(intro_s=0.0, loop_s=LOOPS[name], preroll_s=6.0)
    return mx, mx.L


def _room(seed: int, rt60: float, size: float, highcut: float = 7000.0) -> ModFDNReverb:
    return ModFDNReverb(rt60=rt60, rt60_high=rt60 * 0.45, predelay=0.03, size=size, mod_depth=6.0, mod_rate=0.3,
                        early_level=0.3, lowcut=120.0, highcut=highcut, seed=seed)


def hull_knock(g) -> np.ndarray:
    """Two lashed hulls bumping on the swell: a hollow wooden knock through the planks."""
    b = float(g.uniform(110, 190))
    return FA.modal([b, b * 2.3, b * 4.1, b * 6.9], [0.09, 0.05, 0.025, 0.012], [1.0, 0.5, 0.25, 0.1], 0.6, g, click=0.4)


def creak(g, dur: float, lo: float, hi: float) -> np.ndarray:
    return FA.stick_slip(g, dur, lo, hi, [(280.0, 1.0), (690.0, 0.6), (1500.0, 0.25)])


def rope(g, dur: float) -> np.ndarray:
    return FA.stick_slip(g, dur, 140, 520, [(900.0, 1.0), (2100.0, 0.5), (3800.0, 0.2)], q=4.0)


def stove(g, sec: float) -> np.ndarray:
    """A cook-boat's clay stove: a soft charcoal hiss with small pops in it."""
    n = int(sec * SR)
    t = np.arange(n) / SR
    hiss = filt(g.standard_normal(n), [bq_bandpass(2600, 0.6), bq_highpass(900, 0.7)])
    y = 0.35 * hiss / (np.abs(hiss).max() + 1e-9)
    for _ in range(int(sec * 6)):
        s = int(float(g.uniform(0, sec - 0.01)) * SR)
        k = int(0.003 * SR)
        y[s: s + k] += g.standard_normal(k) * np.linspace(1, 0, k) * float(g.uniform(0.2, 0.8))
    return y * np.clip(t / 0.3, 0, 1) * np.clip((sec - t) / 0.3, 0, 1)


def lamp_swing(g) -> np.ndarray:
    """The caged oil lamp on its hook: iron squeaking as it swings, the cage's bars ticking."""
    y = FA.stick_slip(g, 0.5, 300, 900, [(1400.0, 1.0), (3100.0, 0.5)], q=8.0)
    f = float(g.uniform(2400, 3000))
    tick = FA.modal([f, f * 2.6], [0.04, 0.02], [1.0, 0.4], 0.2, g, click=0.2)
    out = np.zeros(max(len(y), len(tick)) + int(0.3 * SR))
    out[: len(y)] += y
    s = int(0.25 * SR)
    out[s: s + len(tick)] += 0.4 * tick
    return out


def copper_tick(g) -> np.ndarray:
    """A copper flue ticking as the fire heats it: a small, bright, dull-edged metal tick."""
    f = float(g.uniform(1500, 2400))
    return FA.modal([f, f * 2.4, f * 5.1], [0.03, 0.015, 0.008], [1.0, 0.4, 0.15], 0.25, g, click=0.5)


# --------------------------------------------------------------------------- the beds


def oruvel_raft(g):
    mx, L = _mixer("oruvel_raft")
    mx.bus("water", 0.0, send=0.1)
    mx.bus("hulls", 0.0, send=0.2)
    mx.bus("town", 0.0, send=0.35, process=lambda x: filt(x, [bq_lowpass(2800, 0.7)]))
    mx.bus("gulls", 0.0, send=0.35, process=lambda x: filt(x, [bq_lowpass(4200, 0.7)]))
    swell = 0.5 + 0.5 * FA.plfo(L, 0.11, g)
    mx.add("water", FA.stereo_noise(L, g, [bq_lowpass(550, 0.6), bq_highpass(60, 0.7)], 0.5)
           * (0.7 + 0.3 * swell)[:, None] * 0.18, 0.0)
    for t in FA.schedule(L, 0.9, g, 0.45):                                  # water slapping in the gaps between hulls
        mx.add("water", FA.slap(g) if g.random() < 0.6 else FA.lap(g, 0.7), t, pan=float(g.uniform(-0.9, 0.9)),
               gain=float(g.uniform(0.3, 0.9)))
    for t in FA.schedule(L, 1.7, g, 0.5):                                   # the hulls knocking on the swell
        mx.add("hulls", hull_knock(g), t, pan=float(g.uniform(-0.8, 0.8)), gain=float(g.uniform(0.3, 0.8)))
    for t in FA.schedule(L, 3.2, g, 0.5):
        mx.add("hulls", creak(g, float(g.uniform(0.6, 1.3)), 50, 240), t, pan=float(g.uniform(-0.7, 0.7)),
               gain=float(g.uniform(0.2, 0.45)))
    for t in FA.schedule(L, 7.0, g, 0.5):
        mx.add("hulls", rope(g, float(g.uniform(0.5, 1.0))), t, pan=float(g.uniform(-0.7, 0.7)), gain=0.25)
    for k, t in enumerate(FA.schedule(L, 14.0, g, 0.3)):                    # two cook-boat stoves, one each side
        mx.add("town", stove(g, 12.0), t, pan=-0.5 if k % 2 else 0.55, gain=0.18)
    t = 0.4
    while t < LOOPS["oruvel_raft"] - 2.0:                                   # the market's voices, loud and close
        mx.add("town", FA.murmur_phrase(g, bool(g.random() < 0.5)), t, pan=float(g.uniform(-0.7, 0.7)),
               gain=float(g.uniform(0.45, 1.0)))
        t += float(g.uniform(0.7, 2.2))
    for t in FA.schedule(L, 6.5, g, 0.35):                                  # the gulls over the bright water
        mx.add("gulls", FA.gull_call(g), t, pan=float(g.uniform(-0.9, 0.9)), gain=float(g.uniform(0.5, 1.0)))
    return mx, _room(SEED % 9973 + 1, 0.8, 1.4)


def brightwater_deck(g):
    mx, L = _mixer("brightwater_deck")
    mx.bus("sea", 0.0, send=0.08)
    mx.bus("wind", 0.0, send=0.1)
    mx.bus("ship", 0.0, send=0.25)
    mx.bus("far", 0.0, send=0.5, process=lambda x: filt(x, [bq_lowpass(1400, 0.7)]))
    surge = 0.5 + 0.5 * FA.plfo(L, 0.13, g)
    gust = 0.5 + 0.5 * FA.plfo(L, 0.07, g)
    mx.add("sea", FA.stereo_noise(L, g, [bq_bandpass(900, 0.5), bq_highpass(120, 0.7)], 0.3)   # the bow wash
           * (0.65 + 0.35 * surge)[:, None] * 0.22, 0.0)
    mx.add("sea", FA.stereo_noise(L, g, [bq_lowpass(280, 0.6), bq_highpass(40, 0.7)], 0.6)     # the hull's push
           * (0.6 + 0.4 * surge)[:, None] * 0.2, 0.0)
    mx.add("wind", FA.stereo_noise(L, g, [bq_lowpass(1600, 0.6), bq_highpass(200, 0.7)], 0.5)
           * (0.5 + 0.5 * gust)[:, None] * 0.12, 0.0)
    for t in FA.schedule(L, 2.6, g, 0.5):                                   # her timbers working
        mx.add("ship", creak(g, float(g.uniform(0.7, 1.5)), 40, 200), t, pan=float(g.uniform(-0.6, 0.6)),
               gain=float(g.uniform(0.25, 0.5)))
    for t in FA.schedule(L, 5.0, g, 0.5):                                   # sheets and halyards
        mx.add("ship", rope(g, float(g.uniform(0.5, 1.1))), t, pan=float(g.uniform(-0.8, 0.8)), gain=0.3)
    for t in FA.schedule(L, 3.5, g, 0.3):                                   # the lamp on its hook, with the roll
        mx.add("ship", lamp_swing(g), t, pan=0.3, gain=float(g.uniform(0.12, 0.22)))
    for t in FA.schedule(L, 4.0, g, 0.6):                                   # the reef's surf, far off to the east
        mx.add("far", FA.lap(g, 1.6), t, pan=0.85, gain=float(g.uniform(0.3, 0.6)))
    return mx, _room(SEED % 9973 + 2, 0.5, 0.9)


def coilspire_flues(g):
    mx, L = _mixer("coilspire_flues")
    mx.bus("flues", 0.0, send=0.35)
    mx.bus("copper", 0.0, send=0.5)
    mx.bus("storm", 0.0, send=0.25, process=lambda x: filt(x, [bq_lowpass(900, 0.7)]))  # heard through the stone
    draw = 0.5 + 0.5 * FA.plfo(L, 0.06, g)
    mx.add("flues", FA.stereo_noise(L, g, [bq_lowpass(220, 0.6), bq_highpass(35, 0.7)], 0.7)    # the draw's roar
           * (0.7 + 0.3 * draw)[:, None] * 0.32, 0.0)
    mx.add("flues", FA.stereo_noise(L, g, [bq_bandpass(520, 2.5), bq_bandpass(520, 2.5)], 0.5)  # the coil's hollow
           * (0.6 + 0.4 * draw)[:, None] * 0.12, 0.0)
    for t in FA.schedule(L, 1.4, g, 0.6):                                   # copper ticking as it heats
        mx.add("copper", copper_tick(g), t, pan=float(g.uniform(-0.9, 0.9)), gain=float(g.uniform(0.15, 0.5)))
    gust = 0.5 + 0.5 * FA.plfo(L, 0.09, g)
    mx.add("storm", FA.stereo_noise(L, g, [bq_lowpass(1200, 0.6), bq_highpass(120, 0.7)], 0.4)
           * (0.35 + 0.65 * gust ** 1.5)[:, None] * 0.3, 0.0)
    for t in FA.schedule(L, 9.0, g, 0.4):                                   # a sea breaking on the headland, felt
        mx.add("storm", FA.lap(g, 1.8), t, pan=float(g.uniform(-0.5, 0.5)), gain=float(g.uniform(0.4, 0.7)))
    return mx, _room(SEED % 9973 + 3, 2.4, 2.2, highcut=5000.0)              # the hollow spire


BEDS = {"oruvel_raft": oruvel_raft, "brightwater_deck": brightwater_deck, "coilspire_flues": coilspire_flues}
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
