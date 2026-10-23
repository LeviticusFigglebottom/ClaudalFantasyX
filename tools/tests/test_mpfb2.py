"""Tests for the vendored MPFB2 CC0 data and the donor-topology base body (M1-CHR-03, ADR 0021).

Run: python3 -m unittest discover -s tools/tests

* The vendored set matches MANIFEST.json and the pinned commit, holds the licence texts, stays
  under the 5 MB blob cap, and holds no program code.
* Nothing in the repository imports MPFB2's (GPL) code: no `import mpfb` / `from mpfb` anywhere
  under assets_src/ or tools/ (our own reader is `mpfb_data`).
* Our readers parse the donor (closed all-quad hm08 skin), and bb_donor fits it to the slender
  variant's landmarks (pure numpy, no Blender).
"""
import re
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
VENDOR = ROOT / "assets_src" / "third_party" / "mpfb2"
sys.path.insert(0, str(ROOT / "assets_src" / "characters" / "base_body"))
MAX_BYTES = 5 * 1024 * 1024


class TestVendoredData(unittest.TestCase):
    def test_check_passes(self):
        proc = subprocess.run([sys.executable, str(ROOT / "tools" / "fetch_mpfb2.py"), "--check"],
                              capture_output=True, text=True, cwd=ROOT)
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)

    def test_licences_present_and_files_small(self):
        for name in ("LICENSE.md", "LICENSE.ASSETS.md"):
            self.assertTrue((VENDOR / name).exists(), name)
        self.assertIn("CC0", (VENDOR / "LICENSE.ASSETS.md").read_text(encoding="utf-8"))
        for p in VENDOR.rglob("*"):
            if p.is_file():
                self.assertLess(p.stat().st_size, MAX_BYTES, p.name)
                self.assertNotIn(p.suffix, {".py", ".sh", ".pyc"}, p.name)

    def test_no_mpfb_code_is_imported(self):
        pat = re.compile(r"^\s*(import\s+mpfb\b|from\s+mpfb\b)", re.MULTILINE)
        for base in (ROOT / "assets_src", ROOT / "tools"):
            for p in base.rglob("*.py"):
                self.assertIsNone(pat.search(p.read_text(encoding="utf-8")), p)


class TestDonor(unittest.TestCase):
    def test_reader_and_fit(self):
        import numpy as np

        import bb_cage
        import bb_donor
        import bb_params
        import mpfb_data

        m = mpfb_data.load_obj()
        F, _T = m.body()
        self.assertEqual(F.shape, (13378, 4))
        self.assertEqual(bb_cage.check_manifold(F)["non_manifold"], 0)
        params = bb_params.load_params("slender")
        res = bb_donor.generate(params, log=lambda _m: None)
        V, lm = res["V"], res["lm"]
        self.assertAlmostEqual(float(V[:, 2].max()), params["height_m"], delta=0.005)  # crown on the canon
        self.assertGreaterEqual(float(V[:, 2].min()), 0.0)
        heads = float(V[:, 2].max()) / lm.h
        self.assertTrue(7.0 <= heads <= 7.5, heads)  # SPEC §7.3
        regions = set(res["reg"])
        for r in ("head", "torso", "arm_L", "hand_R", "leg_L", "foot_R"):
            self.assertIn(r, regions)
        # every skin vertex is weighted, onto our DEF-* bones only
        W = np.stack(list(res["weights"].values()), axis=1)
        self.assertTrue(np.all(W.sum(axis=1) > 0.5))
        self.assertTrue(all(b.startswith("DEF-") for b in res["weights"]))
        # the anatomy field is re-seated on the donor skin (costume and hair ray-cast onto it)
        d = res["body"].regions["torso"].sdf(V[np.array(res["reg"]) == "torso"])
        self.assertLess(float(np.percentile(np.abs(d), 95)), 0.004)


if __name__ == "__main__":
    unittest.main()
