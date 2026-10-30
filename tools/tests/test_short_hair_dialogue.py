"""Tests for the short hair and beards at dialogue range (M2-CHR-524). Run: python3 -m unittest tools.tests.test_short_hair_dialogue

* Every texture a hero's hair or beard material samples imports with mipmaps (docs/kb/tech/character_shading.md,
  "Every map"). Toma's short-hair atlas, which Kerrid and Moll share, imported without them: a 128-texel column on a
  15-pixel card point-sampled single strands, and the cards rendered as dark blotches with pale specks.
* The beard region (toma_hair.beard_v, Kerrid's kerrid_hair.beard_v) is a distance in head heights everywhere round the
  mouth. The lip clearing was a box whose distance was divided by 0.02-0.04, so the cards and the skin's beard shadow
  stopped dead at it (Kerrid's rectangular notch over the lip).
"""
import re
import sys
import unittest
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
CHARS = ROOT / "assets_src" / "characters"
for sub in ("kerrid", "toma", "villagers", "rhen", "asha", "base_body"):
    sys.path.insert(0, str(CHARS / sub))

HEROES = ("toma", "kerrid", "moll")
HAIR_MATERIALS = ("hair", "hair_grey", "beard", "beard_grey")
TEXTURE = re.compile(r'path="res://([^"]+\.png)"')
# the steepest slope of beard_v (head heights per head height) allowed round the mouth; the old lip box reached 50
MAX_SLOPE = 5.0
GRID_U = (-0.20, 0.20, 161)  # head heights either side of the midline
GRID_V = (0.05, 0.40, 141)  # head heights above the chin


class TestHairAtlasMips(unittest.TestCase):
    def test_hair_textures_import_with_mipmaps(self):
        seen = 0
        for hero in HEROES:
            for mat in HAIR_MATERIALS:
                tres = ROOT / "assets" / "characters" / hero / "materials" / f"{mat}.tres"
                if not tres.exists():
                    continue
                for tex in TEXTURE.findall(tres.read_text(encoding="utf-8")):
                    imp = (ROOT / tex).with_name(Path(tex).name + ".import")
                    self.assertIn("mipmaps/generate=true", imp.read_text(encoding="utf-8"), f"{hero}/{mat}: {tex}")
                    seen += 1
        self.assertGreater(seen, 0)


class TestBeardEdgeIsSoft(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import bb_face
        import bb_params

        cls.fits = {}
        for hero in ("toma", "kerrid"):
            bb = bb_params.load_params(path=str(CHARS / hero / f"{hero}_params.json"))
            lm = bb_params.Landmarks(bb)
            cls.fits[hero] = (lm, bb_face.Face(lm))

    def _slopes(self, hero, fn):
        lm, face = self.fits[hero]
        us, vs = np.linspace(*GRID_U), np.linspace(*GRID_V)
        U, V = np.meshgrid(us, vs)
        yc, zc = lm.P("head_c")[1], lm.P("chin")[2]
        P = np.stack([U.ravel() * lm.h, np.full(U.size, yc - 0.1), zc + V.ravel() * lm.h], axis=1)
        b = fn(lm, face, P).reshape(V.shape)
        gv, gu = np.gradient(b, vs[1] - vs[0], us[1] - us[0])
        inside_mouth = (b < 0).any() and (b > 0).any()
        return float(np.abs(gv).max()), float(np.abs(gu).max()), inside_mouth

    def test_toma_lip_edge(self):
        import toma_hair

        sv, su, both = self._slopes("toma", toma_hair.beard_v)
        self.assertTrue(both)
        self.assertLess(max(sv, su), MAX_SLOPE)

    def test_kerrid_trimmed_lip_edge(self):
        import kerrid_hair

        sv, su, both = self._slopes("kerrid", kerrid_hair.beard_v)
        self.assertTrue(both)
        self.assertLess(max(sv, su), MAX_SLOPE)


if __name__ == "__main__":
    unittest.main()
