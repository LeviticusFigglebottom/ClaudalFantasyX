"""The Act I boss feel pass (2026-10-30, pillar 4): the Undertow's Reach shows the party's blows land. Measured at its
fight's default camera, its `hit` moved its screen-filling body at 17 px per 0.05 s (its `ready` loop moves at 13): the
shudder ran along the view axis. The hand is now thrown up and aside off the wall-head (35 px per 0.05 s).
"""

from __future__ import annotations

import json
import math
import struct
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GLB = ROOT / "assets/creatures/undertows_reach/undertows_reach.glb"
# How far (metres, from its rest) the hit must throw the hand; the old hit moved it 0.38 m, the new one 0.67 m.
MIN_HAND_THROW_M = 0.55


def _track(clip: str, bone: str) -> list[tuple[float, float, float]]:
    raw = GLB.read_bytes()
    n = struct.unpack("<I", raw[12:16])[0]
    js = json.loads(raw[20 : 20 + n])
    off = 20 + n
    blob = raw[off + 8 : off + 8 + struct.unpack("<I", raw[off : off + 4])[0]]
    names = [nd.get("name") for nd in js["nodes"]]
    for an in js["animations"]:
        if an["name"] != clip:
            continue
        for ch in an["channels"]:
            if names[ch["target"]["node"]] != bone or ch["target"]["path"] != "translation":
                continue
            acc = js["accessors"][an["samplers"][ch["sampler"]]["output"]]
            view = js["bufferViews"][acc["bufferView"]]
            start = view.get("byteOffset", 0) + acc.get("byteOffset", 0)
            vals = struct.unpack("<%df" % (acc["count"] * 3), blob[start : start + acc["count"] * 12])
            return [tuple(vals[i : i + 3]) for i in range(0, len(vals), 3)]
    raise AssertionError("%s has no %s translation track" % (clip, bone))


class UndertowsReachHitTest(unittest.TestCase):
    def test_the_hit_throws_the_hand_clear_of_the_wall_head(self) -> None:
        track = _track("hit", "hand")
        throw = max(math.dist(p, track[0]) for p in track)
        self.assertGreaterEqual(throw, MIN_HAND_THROW_M, "the hand is thrown %.2f m" % throw)


if __name__ == "__main__":
    unittest.main()
