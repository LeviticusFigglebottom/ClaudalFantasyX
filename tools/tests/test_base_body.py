"""Tests for the parametric base body (M1-CHR-01, assets_src/characters/base_body/).

Run: python3 -m unittest discover -s tools/tests

* Pure-Python checks (always run): parameter loading, landmark proportions, committed .glb budget.
* Blender build check (skipped when Blender is absent): builds the slender variant geometry-only
  (`--no-rig`) and checks the triangle budget and the bounding-box height / head-height ratio.
  Blender is found at $HYMN_BLENDER, `blender` on PATH, or the tools/dev/fetch_blender.py wrapper.
"""
import json
import os
import shutil
import struct
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "assets_src" / "characters" / "base_body"
OUT = ROOT / "assets" / "characters" / "base_body"
sys.path.insert(0, str(SRC))

VARIANTS = ("slender", "athletic", "heavy")
TRI_MIN, TRI_MAX = 15_000, 27_000  # body skin before costume; M1-CHR-02 head loop flow adds ~4.6k
MAX_BYTES = 5 * 1024 * 1024  # ADR 0005 plain-blob cap


def find_blender() -> str | None:
    for cand in (os.environ.get("HYMN_BLENDER"), shutil.which("blender"),
                 str(Path.home() / ".cache" / "hymn" / "blender-5.0.1+dfsg-5" / "blender")):
        if cand and Path(cand).exists():
            return cand
    return None


def glb_json(path: Path) -> dict:
    data = path.read_bytes()
    magic, _version, _total = struct.unpack("<III", data[:12])
    assert magic == 0x46546C67, "not a GLB"
    length, _kind = struct.unpack("<II", data[12:20])
    return json.loads(data[20:20 + length])


class TestParams(unittest.TestCase):
    def test_variants_load_and_reject_unknown_keys(self):
        import bb_params

        for v in VARIANTS:
            p = bb_params.load_params(v)
            self.assertEqual(p["name"], v)
        with self.assertRaises(KeyError):
            bb_params.load_params("slender", overrides={"no_such_slider": 1})

    def test_landmarks_follow_the_head_canon(self):
        import numpy as np
        import bb_params

        for v in VARIANTS:
            p = bb_params.load_params(v)
            lm = bb_params.Landmarks(p)
            heads = p["height_m"] / lm.h
            self.assertTrue(7.0 <= heads <= 7.5, (v, heads))  # SPEC §7.3
            # crotch near the middle of the body, eyes at mid-head, joints in anatomical order
            self.assertAlmostEqual(lm.P("crotch")[2] / p["height_m"], p["crotch_height_heads"] / heads, places=6)
            z = [lm.P(n)[2] for n in ("ankle", "knee", "hip", "navel", "nipple", "notch", "chin", "crown")]
            self.assertEqual(z, sorted(z), v)
            self.assertGreater(lm.P("eye")[2], lm.P("chin")[2] + 0.45 * lm.h)
            self.assertTrue(np.all(np.isfinite(lm.P("wrist"))))


class TestCommittedAssets(unittest.TestCase):
    def test_glbs_exist_are_small_and_tagged_placeholder(self):
        for v in VARIANTS:
            path = OUT / f"base_body_{v}.glb"
            self.assertTrue(path.exists(), path)
            self.assertLess(path.stat().st_size, MAX_BYTES, path)
            js = glb_json(path)
            self.assertEqual(js["scenes"][0].get("extras", {}).get("hymn_tag"), "PLACEHOLDER")
            self.assertTrue(all(m["name"].startswith("PLACEHOLDER_") for m in js["materials"]))
            joints = {js["nodes"][j]["name"] for j in js["skins"][0]["joints"]}
            for bone in ("DEF-spine", "DEF-spine.006", "DEF-upper_arm.L", "DEF-thigh.R", "DEF-eye.L",
                         "DEF-f_index.03.L", "DEF-thumb.01.R"):
                self.assertIn(bone, joints)
            self.assertTrue(all(n.startswith("DEF-") for n in joints))


@unittest.skipUnless(find_blender(), "Blender not available (python3 tools/dev/fetch_blender.py)")
class TestBlenderBuild(unittest.TestCase):
    def test_slender_geometry(self):
        blender = find_blender()
        with tempfile.TemporaryDirectory() as tmp:
            report = Path(tmp) / "report.json"
            proc = subprocess.run(
                [blender, "--background", "--factory-startup", "--python", str(SRC / "build.py"), "--",
                 "--variant", "slender", "--no-rig", "--report", str(report)],
                capture_output=True, text=True, timeout=600, cwd=ROOT,
            )
            self.assertTrue(report.exists(), proc.stdout[-3000:] + proc.stderr[-3000:])
            r = json.loads(report.read_text())
        self.assertTrue(TRI_MIN <= r["triangles_body"] <= TRI_MAX, r["triangles_body"])
        self.assertAlmostEqual(r["height_m"], 1.63, delta=0.005)
        self.assertTrue(7.0 <= r["heads_tall"] <= 7.5, r["heads_tall"])
        self.assertAlmostEqual(r["heads_tall"], 7.34, delta=0.03)
        self.assertIn("non-manifold edges 0", proc.stdout)
        self.assertTrue(r["placeholder"])


if __name__ == "__main__":
    unittest.main()
