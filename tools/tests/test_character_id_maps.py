"""Tests for the character id maps (M1-CHR-08). Run: python3 -m unittest discover -s tools/tests

An id map's values are labels (the sleeve band-id: 0 blank gauze, n/7 for verse band n), not
colours. The cloth shader samples it with filter_nearest and no mipmaps, so the contract in
docs/kb/tech/character_shading.md ("Every map", and the band-id row) asks for:

* the import with mipmaps off (`mipmaps/generate=false`), while every other character map keeps
  them on;
* each label's region at least 2 texels wide along both axes, checked both by the build scripts
  (`check_id_map`) and here on the committed PNGs;
* only whole labels: every value decodes to one of 0..7 with no in-between greys.
"""
import importlib.util
import unittest
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
CHARACTERS = ROOT / "assets" / "characters"
BUILDERS = {
    "asha": ROOT / "assets_src" / "characters" / "asha" / "asha_textures.py",
    "shader_test": ROOT / "assets_src" / "characters" / "shader_test" / "build_shader_test_textures.py",
}
ID_MAP_SUFFIX = "_bandid.png"
BANDS = 7
MIN_RUN = 2


def load_builder(name: str):
    spec = importlib.util.spec_from_file_location(f"chr08_{name}", BUILDERS[name])
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def id_maps() -> list:
    return sorted(CHARACTERS.rglob("*" + ID_MAP_SUFFIX))


class TestIdMapImports(unittest.TestCase):
    def test_id_maps_exist(self):
        names = {p.name for p in id_maps()}
        self.assertIn("sleeve_bandid.png", names)
        self.assertIn("asha_sleeve_bandid.png", names)

    def test_id_maps_import_without_mipmaps(self):
        for p in id_maps():
            text = p.with_name(p.name + ".import").read_text()
            self.assertIn("mipmaps/generate=false", text, p.name)
            self.assertIn("compress/mode=0", text, p.name)  # lossless: a block-compressed id bleeds too

    def test_other_character_maps_keep_mipmaps(self):
        for folder in (CHARACTERS / "asha" / "textures", CHARACTERS / "shader_test"):
            for p in sorted(folder.glob("*.png")):
                if p.name.endswith(ID_MAP_SUFFIX):
                    continue
                self.assertIn("mipmaps/generate=true", p.with_name(p.name + ".import").read_text(), p.name)


class TestIdMapContents(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.builders = {k: load_builder(k) for k in BUILDERS}

    def test_whole_labels_only(self):
        for p in id_maps():
            with Image.open(p) as im:
                self.assertEqual(im.mode, "L", p.name)
                a = np.asarray(im).astype(float) / 255.0
            labels = np.round(a * BANDS)
            # every value sits within a twentieth of a band of its label (no filtered in-betweens)
            self.assertLess(float(np.abs(a * BANDS - labels).max()), 0.05, p.name)
            self.assertEqual(sorted(set(labels.ravel().astype(int).tolist())), list(range(BANDS + 1)), p.name)

    def test_regions_at_least_two_texels_wide(self):
        for p in id_maps():
            with Image.open(p) as im:
                a = np.asarray(im)
            for name, mod in self.builders.items():
                self.assertEqual(mod.ID_MAP_MIN_RUN, MIN_RUN, name)
                self.assertGreaterEqual(mod.id_map_min_run(a), MIN_RUN, f"{p.name} ({name} helper)")

    def test_check_rejects_a_one_texel_region(self):
        a = np.zeros((8, 8), np.uint8)
        a[3:5, 2:6] = 36
        for name, mod in self.builders.items():
            self.assertEqual(mod.id_map_min_run(a), 2, name)
            mod.check_id_map("ok", a)
            a1 = a.copy()
            a1[6, 6] = 255  # a single texel: 1 wide in both directions
            self.assertEqual(mod.id_map_min_run(a1), 1, name)
            with self.assertRaises(SystemExit):
                mod.check_id_map("bad", a1)


if __name__ == "__main__":
    unittest.main()
