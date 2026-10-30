"""The Act I as-played pass (2026-10-30): the Spar-Wraith's KO from the deck (`ko_deck`, which `hauled_down` maps `ko`
to) keeps the body on the planks. Its face had pitched 40° down into the deck, more than grounding's head turn takes
back, so grounding lifted the whole body half a metre as it died and it read as rising back into the web.
"""

from __future__ import annotations

import json
import struct
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GLB = ROOT / "assets/creatures/spar_wraith/spar_wraith.glb"
# The deck idle breathes (its body0 rises and falls); the KO may not go higher than its highest point.
SLACK_M = 0.02


def _track_y(clip: str, bone: str) -> list[float]:
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
            return list(vals[1::3])
    raise AssertionError("%s has no %s translation track" % (clip, bone))


class SparWraithDeckKoTest(unittest.TestCase):
    def test_the_deck_ko_never_lifts_the_body_above_the_deck_idle(self) -> None:
        idle = _track_y("idle_deck", "body0")
        ko = _track_y("ko_deck", "body0")
        msg = "ko_deck body0 peaks %.3f, idle_deck %.3f" % (max(ko), max(idle))
        self.assertLessEqual(max(ko), max(idle) + SLACK_M, msg)


if __name__ == "__main__":
    unittest.main()
