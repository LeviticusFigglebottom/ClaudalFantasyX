"""The Tide Matron (M5-A3P-1852, docs/kb/art/creatures/act3/tide_matron.md): her sister's rig and mesh, built by
build_cinder_matron.py --tide. Her fire is out (no vertex is lit but the heart and the weak point), the slag is a
`Reef` and kelp hangs off her, her clips play 1.25x slower, and her KO is `bank`, never a break.
"""

from __future__ import annotations

import json
import struct
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TIDE = ROOT / "assets/creatures/tide_matron/tide_matron.glb"
CINDER = ROOT / "assets/creatures/cinder_matron/cinder_matron.glb"
SLOW = 1.25
RENAMED = {"bank_the_fire": "bank_the_tide", "slag_pour": "tide_pour", "recrust_gather": "regrow_gather",
           "recrust": "regrow"}
LIT_SLOTS = {"heart", "wound"}


def _glb(path: Path) -> tuple[dict, bytes]:
    raw = path.read_bytes()
    n = struct.unpack("<I", raw[12:16])[0]
    js = json.loads(raw[20 : 20 + n])
    off = 20 + n
    return js, raw[off + 8 : off + 8 + struct.unpack("<I", raw[off : off + 4])[0]]


def _lengths(js: dict) -> dict[str, float]:
    out = {}
    for an in js["animations"]:
        out[an["name"]] = max(js["accessors"][s["input"]]["max"][0] for s in an["samplers"])
    return out


def _floats(js: dict, blob: bytes, acc_i: int) -> list[tuple[float, ...]]:
    acc = js["accessors"][acc_i]
    view = js["bufferViews"][acc["bufferView"]]
    width = {"VEC2": 2, "VEC3": 3, "VEC4": 4}[acc["type"]]
    start = view.get("byteOffset", 0) + acc.get("byteOffset", 0)
    stride = view.get("byteStride", 4 * width)
    return [struct.unpack_from(f"<{width}f", blob, start + i * stride) for i in range(acc["count"])]


class TideMatronTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.js, cls.blob = _glb(TIDE)
        cls.sister, _ = _glb(CINDER)

    def test_her_meshes_are_the_reef_and_the_kelp_not_the_crust(self) -> None:
        names = {m["name"] for m in self.js["meshes"]}
        self.assertIn("Reef", names)
        self.assertIn("Kelp", names)
        self.assertNotIn("Crust", names)
        mats = {m["name"] for m in self.js["materials"]}
        self.assertNotIn("crust", mats)
        self.assertTrue({"reef", "kelp", "heart", "metal"} <= mats, mats)

    def test_her_fire_is_out(self) -> None:
        lit = []
        for mesh in self.js["meshes"]:
            for prim in mesh["primitives"]:
                slot = self.js["materials"][prim["material"]]["name"]
                if slot in LIT_SLOTS or "TEXCOORD_1" not in prim["attributes"]:
                    continue
                if any(v[1] > 0.0 for v in _floats(self.js, self.blob, prim["attributes"]["TEXCOORD_1"])):
                    lit.append(f"{mesh['name']}/{slot}")
        self.assertEqual(lit, [], "only her heart and her weak point give light")

    def test_her_clips_are_her_sisters_slower(self) -> None:
        mine, hers = _lengths(self.js), _lengths(self.sister)
        for name, sec in hers.items():
            if name in ("ko", "phase_change"):
                continue
            ours = RENAMED.get(name, name)
            self.assertIn(ours, mine)
            self.assertAlmostEqual(mine[ours], sec * SLOW, delta=0.05, msg=ours)
        for gone in ("ko", *RENAMED):
            self.assertNotIn(gone, mine)

    def test_her_ko_is_the_bank_and_the_row_plays_it(self) -> None:
        self.assertIn("bank", _lengths(self.js))
        rows = json.loads((ROOT / "game/data/creatures/creatures.json").read_text(encoding="utf-8"))["creatures"]
        self.assertEqual(rows["tide_matron"]["ko"], "bank")
        for clip in rows["tide_matron"]["contact"]:
            self.assertIn(clip, _lengths(self.js))

    def test_the_kelp_sways_in_the_idle(self) -> None:
        names = [nd.get("name") for nd in self.js["nodes"]]
        idle = next(an for an in self.js["animations"] if an["name"] == "idle")
        moving = set()
        for ch in idle["channels"]:
            bone = names[ch["target"]["node"]]
            if not bone.startswith("kelp_") or ch["target"]["path"] != "rotation":
                continue
            rows = _floats(self.js, self.blob, idle["samplers"][ch["sampler"]]["output"])
            if max(abs(a - b) for r in rows for a, b in zip(r, rows[0])) > 0.01:
                moving.add(bone)
        self.assertGreaterEqual(len(moving), 8, moving)


if __name__ == "__main__":
    unittest.main()
