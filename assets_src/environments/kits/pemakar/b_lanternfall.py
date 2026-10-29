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
# The terrace's own tier and the paddy tier below it, past the arena tread's ends (M3-ENV-1312): the table keeps only
# the town above arena y 2, so in the side angles (party_side, foe_side) the floor ran out into black at x +-16.
# These pieces carry the tier on round the mountain (its treads, walls, channels and graves) and the paddies below.
TIER_Y_RANGE = (-3.5, 2.0)
TIER_X_FROM_M = 15.0
TIER_X_TO_M = 90.0
# The party's key (M3-ENV-1322, the PC's QA row 16: the party barely lit at High): the festival lamps on the tread
# behind the camera, one warm shadowless pool over the party's slots
PARTY_KEY = {"at": (3.2, 2.6, 3.8), "energy": 2.4, "range": 8.0, "own": True}
TIER_LIGHT_X_TO_M = 32.0  # the tier's own lamps (shrine boxes, lamp pillars) out to here, so its run reads at night


def _arena_scenes():
    path = HERE.parent / "haluna" / "arena_scenes.py"
    sys.path.insert(0, str(path.parent))
    sys.path.insert(0, str(HERE))
    spec = importlib.util.spec_from_file_location("arena_scenes_lanternfall", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def tier_lamps(AS) -> list[dict]:
    import pemakar_arena as pa
    import pemakar_layout as pl

    out = []
    for lt in pl.build()["lights"]:
        at = pa.town_to_arena(lt["at"])
        if -0.5 < at[1] < AS.PEM_TOWN_Y_MIN_M and TIER_X_FROM_M < abs(at[0]) < TIER_LIGHT_X_TO_M:
            row = {"at": tuple(round(float(v), 3) for v in at), "energy": lt["energy"], "range": lt["range"]}
            if lt["color"] != AS.TERRACE_LAMP:
                row["color"] = lt["color"]
            out.append(row)
    return out


def tier_continuation(AS) -> list[dict]:
    import math

    import pemakar_arena as pa
    import pemakar_layout as pl

    turn = math.degrees(pa.axis_angle())
    out = []
    for p in pl.build()["pieces"]:
        at = pa.town_to_arena(p["at"])
        if TIER_Y_RANGE[0] < at[1] < TIER_Y_RANGE[1] and TIER_X_FROM_M < abs(at[0]) < TIER_X_TO_M:
            out.append({"glb": p.get("kit_dir", AS.PEM) + p["piece"] + ".glb",
                        "at": tuple(round(float(v), 3) for v in at), "yaw": round(p["yaw_deg"] - turn, 3)})
    return out


def arena(AS) -> dict:
    table = AS._terrace_arena()
    votives = {tuple(v["at"]) for v in AS._terrace_votives()}
    rng = np.random.default_rng(np.random.SeedSequence([6006, 51]))
    lamps, pieces = [], list(table["pieces"]) + tier_continuation(AS)
    for lp in table["lamps"]:
        if tuple(lp["at"]) in votives:
            lp = {**lp, "flame": False}
            x, _, z = lp["at"]
            yaw = round(float(rng.uniform(-VOTIVE_YAW_SPREAD_DEG, VOTIVE_YAW_SPREAD_DEG)), 2)
            pieces.append({"glb": VOTIVE, "at": (x, 0.0, z), "yaw": yaw})
        lamps.append(lp)
    return {**table, "lamps": lamps + tier_lamps(AS) + [PARTY_KEY], "pieces": pieces}


def main(out_dir: Path | None = None) -> int:
    AS = _arena_scenes()
    if out_dir is not None:  # tools/tests/test_b_arenas.py writes to a scratch dir
        AS.OUT_DIR = out_dir
    print(f"ARENA {AS.write_arena(arena(AS)).name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
