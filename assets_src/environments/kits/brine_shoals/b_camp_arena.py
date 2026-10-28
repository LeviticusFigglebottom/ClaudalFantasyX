"""Ch6's salvage_camp_burning arena with its fires (env-art-b, M3-ENV-1313; act1_ch06.md B04 "by the burning hulk").
env-art's table (`CAMP` in `assets_src/environments/kits/haluna/arena_scenes.py`, read-only) lit the camp's fires
(FireLight rows at the tide-wheel's foot, the burned tent, the salvage pile) but drew no flame, so every angle showed
a grey, smoking, unburning camp. This writes the table through the same `write_arena` with b_fire.py's flames at those
lights and on the hulk beyond, and its smoke as Rendering's volumetric columns (b_smoke_columns.py, M3-RND-21). Re-run
after the table or the pieces change, instead of `arena_scenes.py`'s own write of this arena:

    python3 assets_src/environments/kits/brine_shoals/b_camp_arena.py
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
BS = "res://assets/environments/kits/brine_shoals/"
# (piece, x, z, yaw): the table's fire lights, plus the hulk the camp was built against (its wreck_hull_section at
# (2, -26)) burning along its gunwale, and a third where the tent still catching meets the vats
FIRES = (("camp_fire_large", -3.0, -14.2, 20.0), ("camp_fire_small", -12.0, -9.0, 70.0),
         ("camp_fire_small", -9.5, -14.6, 140.0), ("camp_fire_large", 0.5, -24.5, 175.0),
         ("camp_fire_large", 4.0, -25.5, 10.0), ("camp_fire_small", 11.0, -10.0, 300.0))
HULK_FIRE_LIGHT = {"at": (2.0, 1.6, -24.0), "flame": False, "energy": 4.0, "range": 16.0}


def _arena_scenes():
    path = HERE.parent / "haluna" / "arena_scenes.py"
    sys.path.insert(0, str(path.parent))
    spec = importlib.util.spec_from_file_location("arena_scenes_camp", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def arena(AS) -> dict:
    table = AS.CAMP
    pieces = list(table["pieces"]) + [{"glb": BS + p + ".glb", "at": (x, 0.0, z), "yaw": yaw} for p, x, z, yaw in FIRES]
    return {**table, "pieces": pieces, "lamps": list(table["lamps"]) + [HULK_FIRE_LIGHT]}


def main(out_dir: Path | None = None) -> int:
    sys.path.insert(0, str(HERE))
    import b_smoke_columns

    AS = _arena_scenes()
    if out_dir is not None:  # tools/tests/test_b_arenas.py writes to a scratch dir
        AS.OUT_DIR = out_dir
    out = AS.write_arena(arena(AS))
    print(f"ARENA {out.name} ({b_smoke_columns.swap(out)} smoke columns)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
