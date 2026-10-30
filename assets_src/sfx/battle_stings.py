"""Stings for the battle presentation's announcements (M3-AUD-18; score-as-code for SFX).

battle-presentation's stinger and boss intro announce themselves on EventBus.dialogue_event; the Audio autoload
plays these on them (game/audio/sting_audio.gd, game/data/audio/battle_stings.json):
    battle/sting_tideline.ogg      "battle_stinger": the tide line rising before the field -> battle fade
    battle/sting_bark.ogg          "battle_bark": a low breath of water under the lead-in line
    battle/sting_boss.ogg          "boss_intro": the camera finds a boss and its title card shows (3-4 s)
    battle/sting_boss_bell.ogg     "boss_intro" for the Drownbell: a drawn-in swell into a dry, near toll
    battle/sting_boss_soft.ogg, sting_boss_bell_soft.ogg   the same without sub-bass (reduced audio)

Synthesized from the tools/audio/synth library and battle_sfx.py's helpers: no samples, no sample packs, no CC0
audio, no AI generation (SPEC section 2). The boss sting's only pitched material is an open fifth on a low gong and
a struck metallophone fifth above it, written for this file; nothing quotes an existing melody.

Loudness (mix.md section 2, measured on the decoded file by render_all.py): the boss stings -16 LUFS momentary max
(the stinger level), the tide line -18 (a combat SFX), the bark -22 (a texture under a line). Mono, 44.1 kHz, q4.

Render:  python3 assets_src/sfx/battle_stings.py   (or tools/audio/render_all.py --only battle_stings)
"""
from __future__ import annotations

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import battle_sfx as B  # noqa: E402
import numpy as np  # noqa: E402

from synth.dsp import bq_bandpass, bq_highpass, bq_lowpass, filt, midi_to_hz, rng, smooth_noise  # noqa: E402
from synth.gongs import kettle_gong, large_gong  # noqa: E402
from synth.metallophone import metallophone_note  # noqa: E402
from synth.mixer import measure, normalize_momentary, write_ogg  # noqa: E402
from synth.score import n  # noqa: E402

SEED = 9180
STING = -16.0
COMBAT = -18.0
TEXTURE = -22.0


def tideline():
    """The tide line rises: a band of surf noise climbing, bubbles thickening, a low swell that crests and spills.

    Timed to the stinger (battle_transition.json, BattleStinger): the line rises over rise_sec 0.5 and holds 0.25,
    then SceneRouter fades to black over 0.35 s and the battle cue comes in (battle_in_sec) once the battle scene is
    in. So the swell crests and spills with the line (CREST), its tail falls through the hold and the fade, and it is
    all but gone (about -14 dB) at black, never cresting over the battle cue's first bars (M3-AUD-864, the encounter
    pass; it crested at 1.55 s before, after the cut).
    """
    g = rng(SEED + 100)
    crest = 0.55
    N = B._n(1.8)
    t = B._t(N)
    rise = np.clip(t / crest, 0, 1) ** 1.3 * np.where(t > crest, np.exp(-(t - crest) / 0.3), 1.0)
    surf = B._sweep_band(B._noise(g, N), 300.0, 2600.0, q=1.1, steps=20) * rise
    body = filt(B._noise(g, N), [bq_lowpass(380, 0.7)]) * rise * (1 + 0.25 * smooth_noise(N, 3.0, g))
    under = B._sine_glide(N, 48.0, 62.0, 1.4) * B._swell(N, crest - 0.05, 1.5, 0.35)
    buf = 0.55 * surf + 0.35 * body + 0.22 * under
    buf += B._bubbles(g, N, 30, 1.2, 4.0, 0.1, crest + 0.05, amp=0.16, grow=0.8)
    M = B._n(0.7)
    spill = filt(B._noise(g, M), [bq_bandpass(1400, 0.8)]) * B._decay(M, 0.18, attack=0.03)
    B._place(buf, 0.45 * spill, crest - 0.05)
    B._place(buf, B._bubbles(g, B._n(0.7), 14, 2.0, 5.0, 0.0, 0.4, amp=0.18), crest)
    buf = filt(buf, [bq_highpass(32, 0.7)])
    return B._tail_fade(B._room(buf, 1.1, 0.2, SEED + 101, high=6000), 0.3)


def bark():
    """A low breath of water under a spoken line: a slow, dark swell with a few deep bubbles."""
    g = rng(SEED + 200)
    N = B._n(1.8)
    breath = filt(B._noise(g, N), [bq_bandpass(520, 0.9), bq_lowpass(1200, 0.7)]) * B._swell(N, 0.7, 1.6, 0.5)
    buf = 0.6 * breath + 0.12 * B._sine_glide(N, 70.0, 58.0, 1.0) * B._swell(N, 0.6, 2.0, 0.5)
    buf += B._bubbles(g, N, 6, 4.0, 7.0, 0.3, 1.1, amp=0.1)
    buf = filt(buf, [bq_highpass(40, 0.7)])
    return B._tail_fade(B._room(buf, 1.2, 0.2, SEED + 201, high=3000), 0.3)


def boss(soft=False):
    """A boss is named: a low gong and drum together, an open fifth struck high above, a held, darkening wash."""
    g = rng(SEED + 300)
    N = B._n(4.0)
    t = B._t(N)
    buf = np.zeros(N)
    B._place(buf, 0.85 * large_gong(n("D2"), 0.95, seed=SEED + 310, t60=4.0)[:N], 0.0)
    buf += 0.75 * B._thump(78, 36, 0.32, N, g, click=0.5)
    for i, (note, at) in enumerate((("D5", 0.02), ("A5", 0.05))):
        B._place(buf, 0.35 * metallophone_note(n(note), 0.75, seed=SEED + 320 + i, decay=2.6, hardness=0.6,
                                               ombak_hz=4.5), at)
    B._place(buf, 0.4 * kettle_gong(n("A3"), 0.6, seed=SEED + 330, t60=2.4), 0.05)
    drone = np.zeros(N)
    for m in (n("D3"), n("A3")):
        f = midi_to_hz(m)
        drone += np.sin(2 * np.pi * f * t) + 0.25 * np.sin(4 * np.pi * f * t + 0.7)
    drone = filt(drone, [bq_lowpass(900, 0.7)]) * B._swell(N, 1.2, 1.4, 1.4)
    buf += 0.08 * drone
    wash = filt(B._noise(g, N), [bq_bandpass(900, 0.7)]) * B._swell(N, 0.9, 1.2, 1.1)
    buf += 0.05 * wash
    if soft:
        buf = filt(buf, [bq_highpass(140, 0.9), bq_highpass(140, 0.9)])
    buf = filt(buf, [bq_highpass(28, 0.7)])
    return B._tail_fade(B._room(buf, 2.4, 0.26, SEED + 301, predelay=0.03, size=0.9, high=5000), 0.5)


def boss_bell(soft=False):
    """The Drownbell is named: water drawn in toward it (a reversed-feeling swell), then its toll, dry and near."""
    g = rng(SEED + 400)
    lead = 1.1
    N = B._n(lead + 4.2)
    t = B._t(N)
    draw = np.clip(t / lead, 0, 1) ** 3 * np.where(t > lead, 0.0, 1.0)
    pull = B._sweep_band(B._noise(g, N), 2400.0, 260.0, q=1.2, steps=16) * draw
    buf = 0.5 * pull + 0.2 * filt(B._noise(g, N), [bq_lowpass(300, 0.7)]) * draw
    B._place(buf, 0.9 * B._toll_dry(g, 4.2), lead)
    B._place(buf, 0.6 * B._thump(60, 32, 0.4, B._n(1.2), g, click=0.2), lead)
    if soft:
        buf = filt(buf, [bq_highpass(140, 0.9), bq_highpass(140, 0.9)])
    buf = filt(buf, [bq_highpass(28, 0.7)])
    return B._tail_fade(B._room(buf, 3.2, 0.3, SEED + 401, predelay=0.04, size=1.0, high=4500), 0.5)


SFX: dict = {
    f"{B.SUB}/sting_tideline": (tideline, COMBAT),
    f"{B.SUB}/sting_bark": (bark, TEXTURE),
    f"{B.SUB}/sting_boss": (boss, STING),
    f"{B.SUB}/sting_boss_soft": ((lambda: boss(True)), -17.0),
    f"{B.SUB}/sting_boss_bell": (boss_bell, STING),
    f"{B.SUB}/sting_boss_bell_soft": ((lambda: boss_bell(True)), -17.0),
}

# render_all.py's JOBS entry lists these (relative to assets/audio/sfx).
FILES = [name + ".ogg" for name in SFX]


def render(out_dir: str = B.OUT_DIR, verbose: bool = True, only: str = "") -> dict:
    res = {}
    for name, (fn, target) in SFX.items():
        if only and only not in name:
            continue
        x = normalize_momentary(fn(), target, ceiling_db=B.CEILING)
        write_ogg(os.path.join(out_dir, name + ".ogg"), x, quality=B.QUALITY)
        m = measure(x)
        res[name] = m
        if verbose:
            print(f"{name}: {m['seconds']:.3f}s  momentary max {m['momentary_max_lufs']:.2f} LUFS  "
                  f"peak {m['sample_peak_dbfs']:.2f} dBFS", flush=True)
    return res


if __name__ == "__main__":
    render(only=sys.argv[1] if len(sys.argv) > 1 else "")
