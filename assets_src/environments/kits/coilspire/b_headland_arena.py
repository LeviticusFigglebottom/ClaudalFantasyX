"""Ch8's coilspire_headland_path arena with its slopes clothed (env-art-b, M3-ENV-1314). env-art's table
(`_headland_arena` in `assets_src/environments/kits/haluna/arena_scenes.py`, read-only) stands the fight on the
landing with the headland's ground rising round it; at battle-camera distance that ground's broad facets read as flat
grey-brown triangles behind every angle (`battle`, `party_side`, `to_the_spire`). This writes the table through the
same `write_arena` with the kit's scrub clumps scattered over the slopes in view, each set on the ground's own height
(the table's `_headland_ground_y`), clear of the fight and of the path up to the spire. Re-run after the table
changes, instead of `arena_scenes.py`'s own write of this arena:

    python3 assets_src/environments/kits/coilspire/b_headland_arena.py
"""

from __future__ import annotations

import importlib.util
import math
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
CS = "res://assets/environments/kits/coilspire/"
RING_M = (10.0, 45.0)  # the slopes in view, from the landing's edge out: the table's ground height holds only so far
# (past it the far hill is other ground, and a clump set by this height floats), so the far facets stay env-art's
STEP_M = 4.0  # the grid the clumps are jittered on
PATH_CLEAR_M = 4.0  # off the path's line (the `to_the_spire` hint's bearing, both ways)
SCALE = (1.2, 2.4)


def _arena_scenes():
    path = HERE.parent / "haluna" / "arena_scenes.py"
    sys.path.insert(0, str(path.parent))
    spec = importlib.util.spec_from_file_location("arena_scenes_headland", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def world_from_arena(AS, x: float, z: float) -> tuple[float, float]:
    """The inverse of the table's `headland_from_world` on the ground plane."""
    (x0, _y0, z0), psi = AS.headland_pose()
    a = math.radians(psi)
    ry = -z
    bx = x * math.cos(a) - ry * math.sin(a)
    by = x * math.sin(a) + ry * math.cos(a)
    return x0 + bx, z0 - by


def scrub(AS, table: dict) -> list[dict]:
    (_x0, y0, _z0), _psi = AS.headland_pose()
    (px, _py, pz), (lx, _ly, lz) = table["hints"]["to_the_spire"]
    d = np.array([lx - px, lz - pz])
    d /= np.linalg.norm(d)
    rng = np.random.default_rng(np.random.SeedSequence([8008, 14]))
    out = []
    n = int(RING_M[1] // STEP_M)
    for i in range(-n, n + 1):
        for j in range(-n, n + 1):
            x = i * STEP_M + rng.uniform(-1.2, 1.2)
            z = j * STEP_M + rng.uniform(-1.2, 1.2)
            r = math.hypot(x, z)
            if not RING_M[0] < r < RING_M[1] or abs(x * d[1] - z * d[0]) < PATH_CLEAR_M:
                continue
            if rng.uniform() > 0.3:  # broken cover, not a lawn (and few nodes: one instance each)
                continue
            wx, wz = world_from_arena(AS, x, z)
            y = AS._headland_ground_y(wx, wz) - y0
            out.append({"glb": CS + ("scrub_clump_a" if rng.uniform() < 0.5 else "scrub_clump_b") + ".glb",
                        "at": (round(x, 3), round(float(y), 3), round(z, 3)), "yaw": round(rng.uniform(0, 360), 1),
                        "scale": round(rng.uniform(*SCALE), 2)})
    return out


def main(out_dir: Path | None = None) -> int:
    AS = _arena_scenes()
    if out_dir is not None:  # tools/tests/test_b_arenas.py writes to a scratch dir
        AS.OUT_DIR = out_dir
    table = AS.HEADLAND
    extra = scrub(AS, table)
    path = AS.write_arena({**table, "pieces": list(table["pieces"]) + extra})
    print(f"ARENA {path.name} (+{len(extra)} scrub clumps)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
