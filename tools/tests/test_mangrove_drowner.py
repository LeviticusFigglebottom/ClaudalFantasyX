"""The Act II boss feel pass (2026-10-30, pillar 4): the Mangrove Drowner's `rising_water`, its party-wide call every
third turn, is its own tell (no charge). At the battle camera the rooted clip had moved the body 30 px on a 378 px body
(the mass heaving 0.26 m); the heave is doubled (65 px).
"""

from __future__ import annotations

import json
import math
import struct
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GLB = ROOT / "assets/creatures/mangrove_drowner/mangrove_drowner.glb"
# How far (metres) the dark mass (core0) heaves in the rooted rising_water; the old clip moved it 0.27 m.
MIN_HEAVE_M = 0.45


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


class MangroveDrownerTellTest(unittest.TestCase):
    def test_rising_water_heaves_the_mass_enough_to_read(self) -> None:
        track = _track("rising_water", "core0")
        heave = max(math.dist(p, track[0]) for p in track)
        self.assertGreaterEqual(heave, MIN_HEAVE_M, "the mass heaves %.2f m" % heave)


if __name__ == "__main__":
    unittest.main()
