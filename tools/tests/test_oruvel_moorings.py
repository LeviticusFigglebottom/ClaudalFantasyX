"""No hull in Oruvel's dressing rises through another piece's planks (the human's playtest, 2026-10-30: "docked boats
clip through the docks at several points").

Each piece is rebuilt from the Oruvel kit (pure numpy) and placed as the dressing places it. A deck is a raft, bridge,
dive raft or net-pen piece: the box round its walking planks, from 0.3 m under them to 0.05 m over. A hull is any
vertex in a hull material (tar or paint). A hull vertex of one piece inside another piece's deck box is a clip.
Allowed by design: the run's low hull, which lies across its bridge's planks (C1-12); the scale booth's hull, whose
counter overhangs the scale-hull's deck edge with the scaleman at it; and the dive raft, whose gunwale the dive bridge
(and the storm's broken bridge) lands on.
"""

from __future__ import annotations

import json
import math
import sys
import unittest
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
KIT = ROOT / "assets_src" / "environments" / "kits"
sys.path.insert(0, str(KIT / "haluna"))
sys.path.insert(0, str(KIT / "oruvel"))

import ov_cabins  # noqa: E402
import ov_common as oc  # noqa: E402
import ov_heroes  # noqa: E402
import ov_hulls  # noqa: E402
import ov_props  # noqa: E402
import ov_rebuilt  # noqa: E402
import ov_storm  # noqa: E402

DRESSING = ROOT / "assets" / "environments" / "zones" / "ch01" / "oruvel_dressing.json"
DECKS = ("raft_deck", "raft_deck_tucked", "raft_deck_small", "raft_deck_small_tucked", "plank_bridge",
         "plank_bridge_broken", "dive_raft", "net_pen")
HULL_MATS = {oc.M_TAR, oc.M_PAINT, oc.M_PAINT_RED, oc.M_PAINT_OCHRE, oc.M_PAINT_TEAL, oc.M_PAINT_WHITE}
# Pieces whose painted walls stand on a deck (not hulls), and the clips the story places on purpose.
NOT_HULLS = {"cabin_keelroof", "keel_hull", "chandlery", "storm_debris"}
ALLOWED = {("scale_hull", "")}
ALLOWED_ON = {("dive_raft", "plank_bridge"), ("dive_raft", "plank_bridge_broken")}  # (hull piece, deck piece)
UNDER_M = 0.3
OVER_M = 0.05
EDGE_M = 0.05


def _targets() -> dict:
    t = {}
    for m in (ov_hulls, ov_cabins, ov_heroes, ov_props, ov_storm, ov_rebuilt):
        t.update(m.TARGETS)
    return t


def _to_world(p: dict, pts: np.ndarray) -> np.ndarray:
    a, s = math.radians(p.get("yaw_deg", 0.0)), p.get("scale", 1.0)
    c, sn = math.cos(a), math.sin(a)
    x, y, z = pts[:, 0] * s, pts[:, 1] * s, pts[:, 2] * s
    return np.stack([x * c + z * sn + p["at"][0], y + p.get("y", 0.0), -x * sn + z * c + p["at"][1]], 1)


def _to_local(p: dict, pts: np.ndarray) -> np.ndarray:
    a, s = math.radians(p.get("yaw_deg", 0.0)), p.get("scale", 1.0)
    c, sn = math.cos(a), math.sin(a)
    x, y, z = pts[:, 0] - p["at"][0], pts[:, 1] - p.get("y", 0.0), pts[:, 2] - p["at"][1]
    return np.stack([(x * c - z * sn) / s, y / s, (x * sn + z * c) / s], 1)


class OruvelMooringTests(unittest.TestCase):
    def test_no_hull_rises_through_a_deck(self) -> None:
        targets, cache = _targets(), {}

        def mesh(name):
            if name not in cache:
                cache[name] = targets[name]()[0]
            return cache[name]

        pieces = json.loads(DRESSING.read_text(encoding="utf-8"))["pieces"]
        decks = []
        for i, p in enumerate(pieces):
            if p["piece"] not in DECKS:
                continue
            mb = mesh(p["piece"])
            pos, tris, mats = np.asarray(mb.pos), np.asarray(mb.tris), np.asarray(mb.tri_mat)
            v = np.unique(tris[mats == mb.materials.index(oc.M_TIMBER)].ravel())
            top = pos[v, 1].max()
            v = v[pos[v, 1] > top - 0.25]
            decks.append((i, p, pos[v].min(0), pos[v].max(0), top))
        for j, q in enumerate(pieces):
            if q["piece"] not in targets or q["piece"] in NOT_HULLS:
                continue
            if (q["piece"], q.get("block", "")) in ALLOWED:
                continue
            mb = mesh(q["piece"])
            hull = [k for k, n in enumerate(mb.materials) if n in HULL_MATS]
            if not hull:
                continue
            tris, mats = np.asarray(mb.tris), np.asarray(mb.tri_mat)
            world = _to_world(q, np.asarray(mb.pos)[np.unique(tris[np.isin(mats, hull)].ravel())])
            for i, p, lo, hi, top in decks:
                if i == j or (q["piece"], p["piece"]) in ALLOWED_ON:
                    continue
                loc = _to_local(p, world)
                inside = ((loc[:, 0] > lo[0] + EDGE_M) & (loc[:, 0] < hi[0] - EDGE_M) & (loc[:, 2] > lo[2] + EDGE_M)
                          & (loc[:, 2] < hi[2] - EDGE_M) & (loc[:, 1] > top - UNDER_M) & (loc[:, 1] < top + OVER_M))
                with self.subTest(hull=(q["piece"], q["at"]), deck=(p["piece"], p["at"])):
                    self.assertFalse(bool(inside.any()), f"{int(inside.sum())} hull points in the planks")


if __name__ == "__main__":
    unittest.main()
