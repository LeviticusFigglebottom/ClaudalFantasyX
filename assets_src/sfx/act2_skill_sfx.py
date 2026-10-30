"""Act II's skills that make no hit, heal or status, given their own sound (M4-A2P-093; the cue sheet §4; plain git,
ADR 0175).

The Act II audit (tools/audio/act1_audio_audit.py --act 2, "Skills") lists every skill whose effect would be silent
but for the choreography's accents. Each gets its own sound here, made from what the skill does:

    unravel   Ch12, the cord moth's buff-strip (skills.json: it strips the woven buffs, haste, protect, shell and
              regen, from its target). A weave pulled apart: the threads drawn taut and snapping one after another,
              and a ward's glassy ring dying as it goes.

Synthesized here and in tools/audio/synth/ (SPEC §2, §9). Files are assets/audio/act2/sfx/battle/skill_<id>.ogg (mono,
q4), at -19 LUFS momentary max (the combat rule).

Render:  python3 tools/audio/render_all.py --only act2_skill_sfx
"""
from __future__ import annotations

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools", "audio"))
sys.path.insert(0, HERE)

import numpy as np  # noqa: E402

from creature_sfx import buf, finish, glass_ring, room, tap  # noqa: E402
from field_ambience import stick_slip  # noqa: E402
from synth.dsp import rng  # noqa: E402
from synth.mixer import measure, write_ogg  # noqa: E402
from underwater_sfx import place  # noqa: E402

OUT_DIR = os.path.join(ROOT, "assets", "audio", "act2", "sfx", "battle")
SEED = 20262200
QUALITY = 4.0
CAST = -19.0


def unravel(g) -> np.ndarray:
    x = buf(1.6)
    for k in range(5):                                           # threads drawn taut, each snapping
        at = 0.05 + 0.16 * k + float(g.uniform(-0.02, 0.02))
        place(x, stick_slip(g, 0.1, 400.0 + 120 * k, 1400.0, [(2200.0 + 300 * k, 1.0), (4100.0, 0.4)], q=6.0), at, 0.5)
        place(x, tap(g, [3200.0 + 250 * k, 5200.0], [0.01, 0.006], 0.8, click=0.9), at + 0.1)
    ring = glass_ring(g, 1568.0, 1.2, 0.6)                       # the ward's ring, dying as it goes
    ring *= np.linspace(1, 0, len(ring)) ** 1.5
    place(x, ring, 0.0, 0.5)
    return x


SKILLS: list[tuple[str, object, float]] = [("unravel", unravel, CAST)]
FILES = [f"skill_{name}.ogg" for name, _, _ in SKILLS]


def render(out_dir: str = OUT_DIR, verbose: bool = True) -> dict:
    os.makedirs(out_dir, exist_ok=True)
    res = {}
    for i, (name, fn, tgt) in enumerate(SKILLS):
        seed = SEED + 100 * i
        x = finish(room(fn(rng(seed)), seed + 7, mix=0.12, tail=0.4, rt60=0.9), tgt)
        write_ogg(os.path.join(out_dir, f"skill_{name}.ogg"), x, quality=QUALITY)
        res[name] = measure(x)
        if verbose:
            print(f"skill_{name}: {res[name]['seconds']:.2f}s  Mmax {res[name]['momentary_max_lufs']:.2f}", flush=True)
    return res


if __name__ == "__main__":
    render()
