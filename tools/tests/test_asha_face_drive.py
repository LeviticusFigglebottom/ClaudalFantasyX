"""M1-CHR-07: do Asha's emotion tags actually drive her face?

Loads the committed `assets/characters/asha/asha.glb` and the emotion table AshaStage reads
(`game/levels/_tests/characters/asha/asha_face_poses.json`, asha.md §6.3). For every tag and
every shape it maps:
* the shape exists on the Head mesh, under the name AshaStage resolves (a pair or a scalar on a
  paired shape is applied to `<shape>_L` and `<shape>_R`);
* the shape moves skin in its expected region (brows above the eye, lids round the eye, cheek
  under it, mouth shapes round the mouth, ...). Most of its motion falls inside that region, its
  full-weight peak there is at least a FACS-scale floor, and at the tag's own weight the peak is
  still at least a third of a millimetre (about a pixel at dialogue framing);
* the expression shapes carry morph-target normals that change in the same region. Without them a
  cheek raise shades as at rest and does not read (the review-sweep-J "smile driver gap").

Plus the smile itself: the cheek raise and lid squint must lift the lower lid and the cheek by a
visible amount, and the neutral rest face must not.

Run: python3 -m unittest tools/tests/test_asha_face_drive.py
"""
import json
import struct
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "assets_src" / "characters" / "asha"))

import asha_glb  # noqa: E402

GLB = ROOT / "assets" / "characters" / "asha" / "asha.glb"
POSES = ROOT / "game" / "levels" / "_tests" / "characters" / "asha" / "asha_face_poses.json"
MM = 0.001

# shape family -> (region name, full-weight peak floor in mm inside the region)
FAMILY = {
    "brow_inner_up": ("brow", 3.0), "brow_down": ("brow", 3.0), "brow_outer_up": ("brow", 3.0),
    "lid_close": ("lid", 3.0), "lid_wide": ("lid", 3.0), "lid_squint": ("lid", 3.0),
    "cheek_raise": ("cheek", 4.0), "nose_sneer": ("nose", 3.0),
    "mouth_smile": ("mouth", 4.0), "mouth_frown": ("mouth", 3.0), "mouth_stretch": ("mouth", 3.0),
    "mouth_dimple": ("mouth", 1.5), "mouth_press": ("mouth", 2.0), "mouth_pucker": ("mouth", 4.0),
    "lip_upper_up": ("mouth", 3.0), "lip_lower_down": ("mouth", 3.0),
    "jaw_open": ("jaw", 20.0), "jaw_clench": ("clench", 1.0),  # masseter bulge + lip press
}
TAG_WEIGHT_FLOOR_MM = 0.33  # at the tag's own weight, the region's peak must reach about a pixel
IN_REGION_SHARE = 0.6  # of the shape's total displacement


class FaceDrive:
    """The committed head's skin targets plus the landmarks the regions are written against."""

    def __init__(self) -> None:
        js, bin_ = asha_glb.read_glb(GLB)
        self.h = asha_glb.head_targets(js, bin_)
        eyes = asha_glb.joint_positions(js, bin_, ["DEF-eye.L", "DEF-eye.R"])
        self.eye = {"L": eyes["DEF-eye.L"], "R": eyes["DEF-eye.R"]}
        mouth = asha_glb.head_targets(js, bin_, material="mouth")["P"]
        self.mouth_y = float(mouth[:, 1].mean())
        self.P = self.h["P"]

    def region(self, name: str, side: str | None) -> np.ndarray:
        P = self.P
        x, y = P[:, 0], P[:, 1]
        sg = {"L": 1.0, "R": -1.0, None: 0.0}[side]
        E = self.eye[side or "L"]
        ey = float(E[1])
        same = (sg * x > -0.004) if side else np.ones(len(P), bool)
        if name == "brow":
            return same & (y > ey + 0.004) & (y < ey + 0.040) & (np.abs(x) < 0.065)
        if name == "lid":
            return np.hypot(x - E[0], y - ey) < 0.018
        if name == "cheek":
            return same & (y < ey - 0.002) & (y > ey - 0.045) & (np.abs(x) > 0.008) & (np.abs(x) < 0.065)
        if name == "nose":
            return (np.abs(x) < 0.026) & (y > self.mouth_y + 0.004) & (y < ey)
        if name == "mouth":
            return (np.abs(x) < 0.045) & (np.abs(y - self.mouth_y) < 0.026)
        if name == "jaw":
            return y < self.mouth_y + 0.012
        if name == "clench":  # the masseter bulge at the jaw angle and the lips pressing
            return ((np.abs(x) > 0.035) & (y < ey - 0.020)) | self.region("mouth", None)
        raise KeyError(name)

    @staticmethod
    def targets(shape: str, value, names: list[str]) -> list[tuple[str, float, str | None]]:
        """(target, weight, side) as AshaStage._put_weight resolves a pose entry."""
        if isinstance(value, list):
            return [(f"{shape}_L", float(value[0]), "L"), (f"{shape}_R", float(value[1]), "R")]
        if f"{shape}_L" in names:
            return [(f"{shape}_L", float(value), "L"), (f"{shape}_R", float(value), "R")]
        return [(shape, float(value), None)]


_DRIVE: FaceDrive | None = None


def drive() -> FaceDrive:
    global _DRIVE
    if _DRIVE is None:
        _DRIVE = FaceDrive()
    return _DRIVE


class TestEmotionsDriveTheFace(unittest.TestCase):
    def test_every_mapped_shape_exists_and_moves_its_region(self):
        d = drive()
        poses = json.loads(POSES.read_text(encoding="utf-8"))["emotions"]
        names = d.h["names"]
        for tag, pose in poses.items():
            for shape, value in pose.items():
                self.assertIn(shape, FAMILY, f"{tag}: {shape} has no expected region in this test")
                region_name, floor = FAMILY[shape]
                for target, weight, side in d.targets(shape, value, names):
                    with self.subTest(tag=tag, target=target):
                        self.assertIn(target, names, "AshaStage would silently skip this weight")
                        D = d.h["D"][target]
                        mag = np.linalg.norm(D, axis=1)
                        reg = d.region(region_name, side)
                        self.assertGreater(mag.sum(), 0.0, "the shape moves nothing")
                        share = mag[reg].sum() / mag.sum()
                        self.assertGreaterEqual(share, IN_REGION_SHARE,
                                                f"only {share:.0%} of its motion is in the {region_name} region")
                        peak = float(mag[reg].max())
                        self.assertGreaterEqual(peak, floor * MM,
                                                f"full-weight peak {peak / MM:.2f} mm in the {region_name} region")
                        self.assertGreaterEqual(weight * peak, TAG_WEIGHT_FLOOR_MM * MM,
                                                f"at {weight} it moves {weight * peak / MM:.2f} mm: invisible")

    def test_expression_shapes_carry_morph_normals_in_their_region(self):
        d = drive()
        for shape, (region_name, _floor) in FAMILY.items():
            for target, _w, side in d.targets(shape, 1.0, d.h["names"]):
                with self.subTest(target=target):
                    dn = d.h["DN"].get(target)
                    self.assertIsNotNone(dn, "no NORMAL target: the shape would shade as at rest")
                    changed = np.linalg.norm(dn, axis=1) > 0
                    self.assertTrue((changed & d.region(region_name, side)).any())

    def test_visemes_carry_no_normals(self):
        # the GLB cap (ADR 0005): only the 30 expression shapes get them
        d = drive()
        for name in d.h["names"]:
            if name.startswith("vis_"):
                self.assertIsNone(d.h["DN"][name], name)

    def test_mouth_primitive_carries_normals_where_a_shape_moves_it(self):
        # M1-CHR-10: the inner lips and corners (the `mouth` primitive) shaded at rest under the
        # smile; every expression shape that moves it now changes its normals too, visemes still none
        js, bin_ = asha_glb.read_glb(GLB)
        m = asha_glb.head_targets(js, bin_, material="mouth")
        for name in m["names"]:
            moved = np.linalg.norm(m["D"][name], axis=1) > 1e-5
            with self.subTest(target=name):
                if name.startswith("vis_"):
                    self.assertIsNone(m["DN"][name])
                elif moved.sum() >= 8:
                    self.assertIsNotNone(m["DN"][name], f"{name} moves {moved.sum()} mouth vertices at rest normals")
        for side in ("L", "R"):
            dn = m["DN"][f"mouth_smile_{side}"]
            self.assertGreater(int((np.linalg.norm(dn, axis=1) > 0).sum()), 20)

    def test_smile_lifts_the_lower_lid_and_the_cheek(self):
        d = drive()
        poses = json.loads(POSES.read_text(encoding="utf-8"))["emotions"]

        def lift(tag: str) -> tuple[float, float]:
            tot = np.zeros_like(d.P)
            for shape, value in poses[tag].items():
                for target, w, _side in d.targets(shape, value, d.h["names"]):
                    tot += w * d.h["D"][target]
            out = []
            for side in ("L", "R"):
                E = d.eye[side]
                sg = 1.0 if side == "L" else -1.0
                rel = d.P - E
                lid = (rel[:, 1] < -0.002) & (rel[:, 1] > -0.010) & (np.abs(rel[:, 0]) < 0.013) & (rel[:, 2] > 0)
                cheek = (rel[:, 1] < -0.012) & (rel[:, 1] > -0.040) & (sg * rel[:, 0] > -0.005) & (sg * rel[:, 0] < 0.030)
                out.append((tot[lid, 1].max(), tot[cheek, 1].max()))
            return min(o[0] for o in out), min(o[1] for o in out)

        lid, cheek = lift("smile")
        self.assertGreaterEqual(lid, 2.5 * MM, f"smile lifts the lower lid {lid / MM:.2f} mm")
        self.assertGreaterEqual(cheek, 2.5 * MM, f"smile lifts the cheek {cheek / MM:.2f} mm")
        lid, cheek = lift("neutral")
        self.assertLess(max(lid, cheek), 0.2 * MM, "the rest face must not squint")


class TestRound6Expressions(unittest.TestCase):
    """M1-CHR-11: the Duchenne smile, grief's inner brows, and no notch at the nose bridge."""

    def total(self, tag: str) -> np.ndarray:
        d = drive()
        poses = json.loads(POSES.read_text(encoding="utf-8"))["emotions"]
        tot = np.zeros_like(d.P)
        for shape, value in poses[tag].items():
            for target, w, _side in d.targets(shape, value, d.h["names"]):
                tot += w * d.h["D"][target]
        return tot

    def test_smile_narrows_the_eye_and_draws_the_crows_feet(self):
        d = drive()
        tot = self.total("smile")
        for side in ("L", "R"):
            sg = 1.0 if side == "L" else -1.0
            rel = d.P - d.eye[side]
            lid = (rel[:, 1] < -0.002) & (rel[:, 1] > -0.010) & (np.abs(rel[:, 0]) < 0.013) & (rel[:, 2] > 0)
            with self.subTest(side=side):
                self.assertGreaterEqual(float(tot[lid, 1].max()), 4.0 * MM)  # CHR-10: 3.3 mm
                # crow's feet: lateral of the outer canthus, skin drawn toward the eye and folded
                crow = (sg * rel[:, 0] > 0.016) & (sg * rel[:, 0] < 0.030) & (np.abs(rel[:, 1]) < 0.008)
                self.assertLess(float((sg * tot[crow, 0]).min()), -0.5 * MM)
                # the brow tail comes down a little; the brow head does not
                tail = (sg * rel[:, 0] > 0.010) & (sg * rel[:, 0] < 0.022) & (rel[:, 1] > 0.008) & (rel[:, 1] < 0.022)
                self.assertLess(float(tot[tail & (rel[:, 2] > 0), 1].mean()), -0.4 * MM)

    def test_grief_lifts_the_inner_brows_obliquely(self):
        d = drive()
        tot = self.total("grief")
        for side in ("L", "R"):
            sg = 1.0 if side == "L" else -1.0
            rel = d.P - d.eye[side]
            band = (rel[:, 1] > 0.008) & (rel[:, 1] < 0.022) & (rel[:, 2] > 0)
            med = band & (sg * rel[:, 0] > -0.016) & (sg * rel[:, 0] < -0.006)
            lat = band & (sg * rel[:, 0] > 0.010) & (sg * rel[:, 0] < 0.022)
            with self.subTest(side=side):
                self.assertGreaterEqual(float(tot[med, 1].mean()), 2.5 * MM)  # CHR-10: 0.4 mm
                self.assertGreater(float(tot[med, 1].mean() - tot[lat, 1].mean()), 2.0 * MM)

    def test_lid_shapes_have_no_step_on_the_nose_bridge(self):
        # QA-05c fault 6: the squint's rotation stopped dead 5 mm off the midline (a hard 30 mm ball),
        # which drew a light/dark notch. Each vertex's delta must stay close to its neighbours' mean
        d = drive()
        P, F = d.P, d.h["F"]
        wid = asha_glb.weld(P)
        nw = int(wid.max()) + 1
        ed = np.concatenate([F[:, [0, 1]], F[:, [1, 2]], F[:, [2, 0]]])
        ew = np.unique(np.sort(wid[ed], axis=1), axis=0)
        ew = ew[ew[:, 0] != ew[:, 1]]
        cnt = np.maximum(np.bincount(ew.ravel(), minlength=nw), 1).astype(float)
        Pw = np.zeros((nw, 3))
        Pw[wid] = P
        bridge = (np.abs(Pw[:, 0]) < 0.010) & (np.abs(Pw[:, 1] - d.eye["L"][1]) < 0.015) & (Pw[:, 2] > 0.06)
        for name in ("lid_squint_L", "lid_squint_R", "lid_close_L", "lid_close_R", "cheek_raise_L", "cheek_raise_R"):
            Dw = np.zeros((nw, 3))
            Dw[wid] = d.h["D"][name]
            acc = np.zeros((nw, 3))
            np.add.at(acc, ew[:, 0], Dw[ew[:, 1]])
            np.add.at(acc, ew[:, 1], Dw[ew[:, 0]])
            lap = np.linalg.norm(Dw - acc / cnt[:, None], axis=1)
            with self.subTest(target=name):
                self.assertLess(float(lap[bridge].max()), 0.5 * MM)  # CHR-10 squint: 1.23 mm


class TestMorphNormalPass(unittest.TestCase):
    """asha_glb.add_morph_normals on a tiny hand-made GLB: a 3x3 vertex grid with one target that
    lifts the centre vertex."""

    @staticmethod
    def grid_glb(path: Path) -> None:
        P = np.array([[x, 0.0, z] for z in (0, 1, 2) for x in (0, 1, 2)], np.float32) * 0.01
        N = np.tile(np.array([0, 1, 0], np.float32), (9, 1))
        F = []
        for r in range(2):
            for c in range(2):
                a = r * 3 + c
                F += [a, a + 3, a + 1, a + 1, a + 3, a + 4]
        F = np.array(F, np.uint16)
        D = np.zeros((9, 3), np.float32)
        D[4, 1] = 0.004
        blobs = [P.tobytes(), N.tobytes(), F.tobytes() + b"\0\0", D.tobytes()]
        views, off = [], 0
        for bl in blobs:
            views.append({"buffer": 0, "byteOffset": off, "byteLength": len(bl)})
            off += len(bl)
        js = {
            "asset": {"version": "2.0"}, "buffers": [{"byteLength": off}], "bufferViews": views,
            "accessors": [
                {"bufferView": 0, "componentType": 5126, "count": 9, "type": "VEC3",
                 "min": P.min(0).tolist(), "max": P.max(0).tolist()},
                {"bufferView": 1, "componentType": 5126, "count": 9, "type": "VEC3"},
                {"bufferView": 2, "componentType": 5123, "count": len(F), "type": "SCALAR"},
                {"bufferView": 3, "componentType": 5126, "count": 9, "type": "VEC3",
                 "min": D.min(0).tolist(), "max": D.max(0).tolist()},
            ],
            "materials": [{"name": "skin_head"}],
            "meshes": [{"name": "Head", "extras": {"targetNames": ["bump"]}, "primitives": [
                {"attributes": {"POSITION": 0, "NORMAL": 1}, "indices": 2, "material": 0,
                 "targets": [{"POSITION": 3}]}]}],
        }
        asha_glb.write_glb(path, js, b"".join(blobs))

    def test_bump_gets_tilted_normals_and_the_file_rereads(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "grid.glb"
            self.grid_glb(path)
            r = asha_glb.add_morph_normals(path, ["bump"])
            self.assertEqual(r["shapes"], 1)
            js, bin_ = asha_glb.read_glb(path)
            total = struct.unpack("<I", path.read_bytes()[8:12])[0]
            self.assertEqual(total, path.stat().st_size)
            h = asha_glb.head_targets(js, bin_)
            dn = h["DN"]["bump"]
            self.assertIsNotNone(dn)
            self.assertAlmostEqual(float(np.abs(dn[4]).max()), 0.0, places=6)  # the apex stays up
            self.assertGreater(float(np.linalg.norm(dn[1])), 0.1)  # its neighbours tilt away
            self.assertLess(dn[1][2], 0.0)  # vertex 1 is at z = 0, so it tilts toward -z
            np.testing.assert_allclose(np.linalg.norm(h["N"] + dn, axis=1), 1.0, atol=1e-5)
            # deterministic: the same input gives the same bytes
            again = Path(tmp) / "again.glb"
            self.grid_glb(again)
            asha_glb.add_morph_normals(again, ["bump"])
            self.assertEqual(path.read_bytes(), again.read_bytes())


if __name__ == "__main__":
    unittest.main()
