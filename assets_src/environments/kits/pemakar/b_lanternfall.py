"""Ch5's Lanternfall arena with the mourners' votive lamps as kit pieces (env-art-b, M3-ENV-1305; the Act I
inventory's `ash_terrace_lanternfall` row, M3-HER-1141). The arena's table stays env-art's (`_terrace_arena` in
`assets_src/environments/kits/haluna/arena_scenes.py`, read-only); this writes it through the same `write_arena` with
one change: each votive row (`_terrace_votives`) keeps its light but draws no writer sphere flame, and a
`votive_lamp` piece (b_votive.py) stands under it, its own flame where the sphere was. Re-run after the table or the
piece changes, instead of `arena_scenes.py`'s own write of this arena:

    python3 assets_src/environments/kits/pemakar/b_lanternfall.py
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
VOTIVE = "res://assets/environments/kits/pemakar/votive_lamp.glb"
VOTIVE_YAW_SPREAD_DEG = 25.0  # the spouts face the fight, each set down by hand


def _arena_scenes():
    path = HERE.parent / "haluna" / "arena_scenes.py"
    sys.path.insert(0, str(path.parent))
    sys.path.insert(0, str(HERE))
    spec = importlib.util.spec_from_file_location("arena_scenes_lanternfall", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def arena(AS) -> dict:
    table = AS._terrace_arena()
    votives = {tuple(v["at"]) for v in AS._terrace_votives()}
    rng = np.random.default_rng(np.random.SeedSequence([6006, 51]))
    lamps, pieces = [], list(table["pieces"])
    for lp in table["lamps"]:
        if tuple(lp["at"]) in votives:
            lp = {**lp, "flame": False}
            x, _, z = lp["at"]
            yaw = round(float(rng.uniform(-VOTIVE_YAW_SPREAD_DEG, VOTIVE_YAW_SPREAD_DEG)), 2)
            pieces.append({"glb": VOTIVE, "at": (x, 0.0, z), "yaw": yaw})
        lamps.append(lp)
    return {**table, "lamps": lamps, "pieces": pieces}


def main() -> int:
    AS = _arena_scenes()
    print(f"ARENA {AS.write_arena(arena(AS)).relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
