"""Tests for the procedural vegetation (M1-ENV-02). Run: python3 -m unittest discover -s tools/tests

* Geometry (no Blender needed): every generator is deterministic, inside its triangle budget, and
  writes wind weights in the documented ranges.
* Export (needs Blender 5.0.1, skipped otherwise): one generator is built through Blender and the
  .glb is checked for size, triangle budget and the COLOR_0 / TEXCOORD_1 channels.
* Committed assets: every file under assets/environments/vegetation/ is < 5 MB (ADR 0005) and every
  committed .glb is inside the budgets of its generator.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import shutil
import struct
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "assets_src" / "environments" / "vegetation"
ASSETS = ROOT / "assets" / "environments" / "vegetation"
MAX_BYTES = 5 * 1024 * 1024
GLTF_TRIANGLES = 4  # glTF primitive mode

sys.path.insert(0, str(SRC))


def _load(name: str):
    spec = importlib.util.spec_from_file_location(f"veg_{name}", SRC / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod  # dataclasses look their module up while the class is created
    spec.loader.exec_module(mod)
    return mod


BUILD = _load("build")


def find_blender() -> str | None:
    for cand in (os.environ.get("HYMN_BLENDER"), str(Path.home() / ".cache/hymn/blender-5.0.1+dfsg-5/blender"),
                 shutil.which("blender")):
        if cand and Path(cand).is_file() and os.access(cand, os.X_OK):
            return cand
    return None


def read_glb(path: Path) -> tuple[dict, bytes]:
    data = path.read_bytes()
    magic, _version, _length = struct.unpack("<III", data[:12])
    assert magic == 0x46546C67, "not a glb"
    jlen = struct.unpack("<I", data[12:16])[0]
    gltf = json.loads(data[20:20 + jlen])
    blen = struct.unpack("<I", data[20 + jlen:24 + jlen])[0]
    return gltf, data[28 + jlen:28 + jlen + blen]


def glb_mesh_stats(path: Path) -> dict[str, dict]:
    gltf, _ = read_glb(path)
    out = {}
    for mesh in gltf["meshes"]:
        tris = 0
        attrs: set[str] = set()
        for prim in mesh["primitives"]:
            assert prim.get("mode", GLTF_TRIANGLES) == GLTF_TRIANGLES
            tris += gltf["accessors"][prim["indices"]]["count"] // 3
            attrs |= set(prim["attributes"])
        out[mesh["name"]] = {"triangles": tris, "attributes": attrs}
    return out


def budget_for(module, mesh_name: str) -> int:
    lod = int(mesh_name.rsplit("-lod", 1)[1]) if "-lod" in mesh_name else 0
    return module.TRI_BUDGET[min(lod, len(module.TRI_BUDGET) - 1)]


def digest(builders) -> str:
    h = hashlib.sha256()
    for mb in builders:
        for arr in (mb.pos, mb.nrm, mb.uv, mb.uv2, mb.col, mb.tris):
            h.update(np.asarray(arr, dtype=np.float64).round(9).tobytes())
    return h.hexdigest()


class GeneratorGeometryTest(unittest.TestCase):
    def test_every_target_is_deterministic_and_in_budget(self):
        for name, (module, fn) in BUILD.targets().items():
            with self.subTest(target=name):
                first = fn()
                self.assertEqual(digest(first), digest(fn()), "same seed must give the same mesh")
                self.assertEqual(BUILD.check_budget(module, first), [])
                lods = [mb.triangle_count for mb in first]
                self.assertTrue(all(t > 0 for t in lods))

    def test_lods_get_cheaper(self):
        for name, (_module, fn) in BUILD.targets().items():
            builders = fn()
            groups: dict[str, list[int]] = {}
            for mb in builders:
                groups.setdefault(mb.name.split("-lod")[0], []).append(mb.triangle_count)
            for base, counts in groups.items():
                with self.subTest(target=name, mesh=base):
                    self.assertEqual(counts, sorted(counts, reverse=True))

    def test_wind_channels_follow_the_convention(self):
        palm = _load("palm")
        mb = palm.build("a")[0]
        col = np.asarray(mb.col)
        uv2 = np.asarray(mb.uv2)
        self.assertTrue(((col >= 0) & (col <= 1)).all() and ((uv2 >= 0) & (uv2 <= 1)).all())
        tri_mat = np.asarray(mb.tri_mat)
        bark = mb.materials.index("palm_bark")
        bark_verts = np.unique(np.asarray(mb.tris)[tri_mat == bark])
        pos = np.asarray(mb.pos)[bark_verts]
        r = col[bark_verts, 0]
        self.assertLess(r[pos[:, 2].argmin()], 0.01, "trunk root must not sway (R = 0)")
        self.assertGreater(r[pos[:, 2].argmax()], 0.9, "trunk top sways fully (R ~ 1)")
        self.assertTrue((col[bark_verts, 3] == 0).all(), "bark has no flutter (A = 0)")
        frond = np.unique(np.asarray(mb.tris)[tri_mat == mb.materials.index("palm_frond")])
        self.assertGreater(col[frond, 3].max(), 0.9, "leaflet tips flutter (A ~ 1)")
        self.assertGreater(len(np.unique(col[frond, 2].round(4))), 20, "fronds carry distinct phases (B)")

    def test_seeds_change_the_plant(self):
        palm = _load("palm")
        a = palm.make_skeleton(dict(palm.VARIANTS["a"]))
        b = palm.make_skeleton(dict(palm.VARIANTS["a"], seed=999))
        self.assertFalse(np.allclose(a.trunk_p, b.trunk_p))


class CommittedAssetsTest(unittest.TestCase):
    def test_files_are_small(self):
        files = [p for p in ASSETS.rglob("*") if p.is_file() and p.suffix != ".import"]
        self.assertTrue(files, "no vegetation assets committed")
        for p in files:
            with self.subTest(file=p.name):
                self.assertLess(p.stat().st_size, MAX_BYTES)

    def test_textures_are_at_most_1k(self):
        for p in ASSETS.glob("*.png"):
            with self.subTest(file=p.name):
                w, h = struct.unpack(">II", p.read_bytes()[16:24])
                self.assertLessEqual(max(w, h), 1024)

    def test_glbs_match_budgets_and_channels(self):
        table = BUILD.targets()
        for path in sorted(ASSETS.glob("*.glb")):
            module = table[path.stem][0]
            with self.subTest(glb=path.name):
                for mesh, st in glb_mesh_stats(path).items():
                    self.assertLessEqual(st["triangles"], budget_for(module, mesh), mesh)
                    self.assertTrue({"COLOR_0", "TEXCOORD_0", "TEXCOORD_1", "NORMAL", "TANGENT"} <= st["attributes"])


@unittest.skipUnless(find_blender(), "Blender 5.0.1 not found (python3 tools/dev/fetch_blender.py)")
class BlenderExportTest(unittest.TestCase):
    def test_build_one_generator(self):
        blender = find_blender()
        target = "palm_coconut_c"
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / f"{target}.glb"
            stats = Path(tmp) / "stats.json"
            proc = subprocess.run(
                [blender, "--background", "--factory-startup", "--python", str(SRC / "build.py"), "--",
                 "--target", target, "--out", str(out), "--stats", str(stats)],
                capture_output=True, text=True, timeout=300, cwd=ROOT)
            self.assertEqual(proc.returncode, 0, proc.stdout[-2000:] + proc.stderr[-2000:])
            self.assertTrue(out.is_file())
            self.assertLess(out.stat().st_size, MAX_BYTES)
            module = BUILD.targets()[target][0]
            meshes = glb_mesh_stats(out)
            self.assertEqual(sorted(meshes), [target, f"{target}-lod1", f"{target}-lod2"])
            reported = json.loads(stats.read_text())[target]
            for mesh, st in meshes.items():
                self.assertLessEqual(st["triangles"], budget_for(module, mesh))
                self.assertEqual(st["triangles"], reported[mesh]["triangles"])
                self.assertIn("COLOR_0", st["attributes"])
                self.assertIn("TEXCOORD_1", st["attributes"])


@unittest.skipUnless(shutil.which(os.environ.get("GODOT", "godot")), "Godot not on PATH")
class ShaderCompileTest(unittest.TestCase):
    def test_vegetation_shaders_compile_headless(self):
        proc = subprocess.run(
            [shutil.which(os.environ.get("GODOT", "godot")), "--headless", "--path", str(ROOT), "--script",
             "res://game/levels/_tests/vegetation/vegetation_shader_check.gd"],
            capture_output=True, text=True, timeout=300, cwd=ROOT)
        out = proc.stdout + proc.stderr
        self.assertNotIn("SHADER ERROR", out)
        self.assertEqual(out.count("VEG_SHADER ok"), 3, out[-3000:])
        self.assertEqual(proc.returncode, 0, out[-3000:])


if __name__ == "__main__":
    unittest.main()
