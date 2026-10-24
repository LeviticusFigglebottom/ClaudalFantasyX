"""Tests for the hero banyan and the windbreak tree (M2-ENV-07). Run: python3 -m unittest discover -s tools/tests

No Blender needed: the generators are deterministic and inside their budgets, the LODs get cheaper,
the wind channels follow vegetation.md, leaf faces wind the way their shading normals point (Godot
flips back-face normals on the two-sided foliage), the banyan keeps the chapel walk clear, and the
Haluna kit export keeps the piece names, maps every slot to a kit material and gives bark and leaves
of one tree the same wind uniforms.
"""

from __future__ import annotations

import hashlib
import importlib.util
import sys
import unittest
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
VEG = ROOT / "assets_src" / "environments" / "vegetation"
KIT = ROOT / "assets_src" / "environments" / "kits" / "haluna"
for d in (VEG, KIT):
    if str(d) not in sys.path:
        sys.path.append(str(d))

import banyan  # noqa: E402
import windbreak  # noqa: E402

WIND_KEYS = ("wind_response", "plant_height_m", "sway_lean", "sway_amplitude", "sway_frequency_hz", "gust_contrast",
             "secondary_amplitude_m", "secondary_frequency_hz")


def _load_kit(name: str):
    spec = importlib.util.spec_from_file_location(f"broadleaf_kit_{name}", KIT / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


def digest(builders) -> str:
    h = hashlib.sha256()
    for mb in builders:
        for arr in (mb.pos, mb.nrm, mb.uv, mb.uv2, mb.col, mb.tris):
            h.update(np.asarray(arr, dtype=np.float64).round(9).tobytes())
    return h.hexdigest()


SPECIES = {"banyan": (banyan, "hero"), "windbreak": (windbreak, "a")}


class BroadleafGeometryTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.built = {k: m.build(v) for k, (m, v) in SPECIES.items()}

    def test_deterministic_in_budget_and_lods_get_cheaper(self) -> None:
        for name, (mod, variant) in SPECIES.items():
            with self.subTest(species=name):
                first = self.built[name]
                self.assertEqual(digest(first), digest(mod.build(variant)))
                counts = [mb.triangle_count for mb in first]
                self.assertEqual(len(counts), 2, "kit pieces carry exactly LOD0 + LOD1")
                for c, budget in zip(counts, mod.TRI_BUDGET):
                    self.assertLessEqual(c, budget)
                self.assertEqual(counts, sorted(counts, reverse=True))
                self.assertEqual(first[1].name, first[0].name + "-lod1")

    def test_wind_channels(self) -> None:
        for name, builders in self.built.items():
            for mb in builders:
                with self.subTest(mesh=mb.name):
                    col, uv2 = np.asarray(mb.col), np.asarray(mb.uv2)
                    pos = np.asarray(mb.pos)
                    self.assertTrue(((col >= 0) & (col <= 1)).all() and ((uv2 >= 0) & (uv2 <= 1)).all())
                    self.assertLess(col[pos[:, 2] < 0.3, 0].max(), 0.01, "primary sway ~0 at the root")
                    tris = np.asarray(mb.tris)
                    tm = np.asarray(mb.tri_mat)
                    leaf = [i for i, m in enumerate(mb.materials) if m.endswith("_leaf")][0]
                    bark_v = np.unique(tris[tm != leaf])
                    leaf_v = np.unique(tris[tm == leaf])
                    self.assertEqual(col[bark_v, 3].max(), 0.0, "bark has no flutter")
                    self.assertGreater(col[leaf_v, 3].max(), 0.5, "spray tips flutter")

    def test_leaf_winding_matches_shading_normal(self) -> None:
        for name, builders in self.built.items():
            mb = builders[0]
            pos, nrm = np.asarray(mb.pos), np.asarray(mb.nrm)
            tris = np.asarray(mb.tris)
            leaf = [i for i, m in enumerate(mb.materials) if m.endswith("_leaf")][0]
            t = tris[np.asarray(mb.tri_mat) == leaf]
            geo = np.cross(pos[t[:, 1]] - pos[t[:, 0]], pos[t[:, 2]] - pos[t[:, 0]])
            agree = np.einsum("ij,ij->i", geo, nrm[t].mean(axis=1)) > 0
            with self.subTest(species=name):
                self.assertGreater(agree.mean(), 0.97)

    def test_banyan_shape_roots_and_clear_walk(self) -> None:
        p = banyan.VARIANTS["hero"]
        tree = banyan.make_tree(p)
        pos = np.asarray(self.built["banyan"][0].pos)
        lo, hi = pos.min(axis=0), pos.max(axis=0)
        self.assertLessEqual(hi[2], p["height"] + 0.5)
        self.assertGreater(min(hi[0] - lo[0], hi[1] - lo[1]), 18.0, "a broad crown")
        self.assertGreater(len(tree.roots), 150, "hanging aerial roots")
        self.assertGreaterEqual(len({id(lb) for lb in tree.props if lb.keep == 0}), 8, "prop roots")
        for lb in tree.props:
            self.assertLess(lb.pts[-1, 2], 0.0, "prop roots stand in the ground")
            self.assertGreater(banyan.path_distance(lb.pts[-1], p["path"]), 0.0, "no prop root on the walk")
        for lb in tree.roots:
            if min(banyan.path_distance(q, p["path"]) for q in lb.pts) < 0.0:  # hangs over the walk
                self.assertGreaterEqual(lb.pts[-1, 2], p["path_cut_m"] - 1e-6, "roots over the walk cut at head height")

    def test_windbreak_is_an_upright_oval(self) -> None:
        pos = np.asarray(self.built["windbreak"][0].pos)
        lo, hi = pos.min(axis=0), pos.max(axis=0)
        self.assertGreater((hi[2] - lo[2]) / max(hi[0] - lo[0], hi[1] - lo[1]), 1.5)


class HalunaKitExportTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.trees = _load_kit("trees")
        cls.materials = _load_kit("materials")

    def test_piece_names_axes_and_slots(self) -> None:
        for piece, fn in self.trees.TARGETS.items():
            builders = fn()
            with self.subTest(piece=piece):
                self.assertEqual([b.name for b in builders], [piece, f"{piece}-lod1"])
                pos = np.asarray(builders[0].pos)
                self.assertGreater(pos[:, 1].max(), 7.0, "kit frame is +Y up")
                for slot in builders[0].materials:
                    self.assertIn(slot, self.materials.MATERIALS, slot)

    def test_one_tree_shares_its_wind(self) -> None:
        groups = {"banyan": ("kit_banyan_bark", "kit_banyan_root", "kit_banyan_leaf"),
                  "windbreak": ("kit_windbreak_bark", "kit_windbreak_leaf")}
        for tree, names in groups.items():
            with self.subTest(tree=tree):
                ref = self.materials.MATERIALS[names[0]]["params"]
                for n in names[1:]:
                    other = self.materials.MATERIALS[n]["params"]
                    self.assertEqual({k: ref[k] for k in WIND_KEYS}, {k: other[k] for k in WIND_KEYS}, n)


if __name__ == "__main__":
    unittest.main()
