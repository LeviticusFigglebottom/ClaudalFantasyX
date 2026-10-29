"""Unit tests for tools/screenshots/{pngio,compare}.py. Run: python3 -m unittest discover -s tools/tests"""
import json
import shutil
import struct
import sys
import tempfile
import unittest
import zlib
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools" / "screenshots"))
import compare  # noqa: E402
import pngio  # noqa: E402


def _filter_row(ftype: int, row: np.ndarray, prev: np.ndarray, bpp: int) -> bytes:
    """Reference PNG filter encoder (the inverse of what pngio must undo)."""
    r, p = row.astype(np.int32), prev.astype(np.int32)
    left = np.concatenate([np.zeros(bpp, np.int32), r[:-bpp]])
    upleft = np.concatenate([np.zeros(bpp, np.int32), p[:-bpp]])
    if ftype == 0:
        pred = np.zeros_like(r)
    elif ftype == 1:
        pred = left
    elif ftype == 2:
        pred = p
    elif ftype == 3:
        pred = (left + p) // 2
    else:
        est = left + p - upleft
        pa, pb, pc = np.abs(est - left), np.abs(est - p), np.abs(est - upleft)
        pred = np.where((pa <= pb) & (pa <= pc), left, np.where(pb <= pc, p, upleft))
    return bytes([ftype]) + ((r - pred) & 0xFF).astype(np.uint8).tobytes()


def _encode_filtered(img: np.ndarray, ctype: int, depth: int = 8) -> bytes:
    h, w, c = img.shape
    if depth == 16:
        rows = img.astype(">u2").view(np.uint8).reshape(h, w * c * 2)
    else:
        rows = img.astype(np.uint8).reshape(h, w * c)
    bpp = c * depth // 8
    prev = np.zeros(rows.shape[1], np.uint8)
    raw = b""
    for y in range(h):
        raw += _filter_row(y % 5, rows[y], prev, bpp)  # cycle through all five filter types
        prev = rows[y]

    def chunk(kind: bytes, body: bytes) -> bytes:
        return struct.pack(">I", len(body)) + kind + body + struct.pack(">I", zlib.crc32(kind + body))

    ihdr = struct.pack(">IIBBBBB", w, h, depth, ctype, 0, 0, 0)
    return pngio.SIGNATURE + chunk(b"IHDR", ihdr) + chunk(b"IDAT", zlib.compress(raw)) + chunk(b"IEND", b"")


class PngTests(unittest.TestCase):
    def setUp(self) -> None:
        self.rng = np.random.default_rng(7)

    def test_all_filters_rgb8(self) -> None:
        img = self.rng.integers(0, 256, (11, 13, 3), dtype=np.uint8)
        np.testing.assert_array_equal(pngio.decode(_encode_filtered(img, 2)), img)

    def test_all_filters_rgba8_and_grey(self) -> None:
        rgba = self.rng.integers(0, 256, (9, 7, 4), dtype=np.uint8)
        np.testing.assert_array_equal(pngio.decode(_encode_filtered(rgba, 6)), rgba)
        grey = self.rng.integers(0, 256, (6, 5, 1), dtype=np.uint8)
        np.testing.assert_array_equal(pngio.decode(_encode_filtered(grey, 0)), grey)

    def test_all_filters_rgb16(self) -> None:
        img = self.rng.integers(0, 65536, (5, 6, 3), dtype=np.uint16)
        out = pngio.decode(_encode_filtered(img, 2, depth=16))
        self.assertEqual(out.dtype, np.uint16)
        np.testing.assert_array_equal(out, img)

    def test_write_read_roundtrip(self) -> None:
        img = self.rng.integers(0, 256, (4, 8, 3), dtype=np.uint8)
        np.testing.assert_array_equal(pngio.decode(pngio.encode(img)), img)

    def test_rejects_non_png(self) -> None:
        with self.assertRaises(pngio.PngError):
            pngio.decode(b"GIF89a....")


class CompareTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp())
        self.out, self.base = self.tmp / "out", self.tmp / "baselines"
        self.out.mkdir()
        self.base.mkdir()
        self.shot = {"id": "s", "scene": "res://x.tscn", "camera": "default", "resolution": [8, 4],
                     "threshold_rmse": 0.01}
        self.grey = np.full((4, 8, 3), 128, np.uint8)

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp)

    def test_linear_conversion_endpoints(self) -> None:
        lin = compare.srgb_to_linear(np.array([[[0, 255, 188]]], np.uint8))
        self.assertAlmostEqual(lin[0, 0, 0], 0.0)
        self.assertAlmostEqual(lin[0, 0, 1], 1.0)
        self.assertAlmostEqual(lin[0, 0, 2], 0.5029, places=3)  # sRGB 188 is ~50% linear light

    def test_rmse_values(self) -> None:
        black, white = np.zeros((2, 2, 3), np.uint8), np.full((2, 2, 3), 255, np.uint8)
        self.assertEqual(compare.rmse_linear(black, black), 0.0)
        self.assertAlmostEqual(compare.rmse_linear(black, white), 1.0)
        with self.assertRaises(ValueError):
            compare.rmse_linear(black, np.zeros((3, 2, 3), np.uint8))

    def test_identical_passes_and_writes_diff(self) -> None:
        pngio.write(self.out / "s.png", self.grey)
        pngio.write(self.base / "s.png", self.grey)
        ok, msg = compare.compare_shot(self.shot, self.out, self.base)
        self.assertTrue(ok, msg)
        self.assertEqual(pngio.read(self.out / "diff" / "s.png").shape, (4, 8, 3))

    def test_drift_above_threshold_fails(self) -> None:
        changed = self.grey.copy()
        changed[:, :4] = 200
        pngio.write(self.out / "s.png", changed)
        pngio.write(self.base / "s.png", self.grey)
        ok, msg = compare.compare_shot(self.shot, self.out, self.base)
        self.assertFalse(ok, msg)
        diff = pngio.read(self.out / "diff" / "s.png")
        self.assertGreater(int(diff[0, 0, 0]), int(diff[0, 7, 0]))  # changed half glows red

    def test_missing_baseline_and_size_mismatch_fail(self) -> None:
        pngio.write(self.out / "s.png", self.grey)
        self.assertFalse(compare.compare_shot(self.shot, self.out, self.base)[0])
        pngio.write(self.base / "s.png", np.zeros((5, 8, 3), np.uint8))
        ok, msg = compare.compare_shot(self.shot, self.out, self.base)
        self.assertFalse(ok)
        self.assertIn("size", msg)

    def test_a_pending_shot_passes_until_it_has_a_baseline(self) -> None:
        pngio.write(self.out / "s.png", self.grey)
        pending = {**self.shot, compare.PENDING: True}
        ok, msg = compare.compare_shot(pending, self.out, self.base)
        self.assertTrue(ok, msg)
        self.assertIn("PENDING", msg)
        pngio.write(self.base / "s.png", np.zeros((4, 8, 3), np.uint8))
        self.assertFalse(compare.compare_shot(pending, self.out, self.base)[0], "with a baseline it is compared")

    def test_update_baselines_copies_and_records_renderer(self) -> None:
        pngio.write(self.out / "s.png", self.grey)
        (self.out / "capture_report.json").write_text(json.dumps({"rendering_method": "forward_plus"}))
        self.assertEqual(compare.update_baselines([self.shot], [], self.out, self.base), 0)
        np.testing.assert_array_equal(pngio.read(self.base / "s.png"), self.grey)
        meta = json.loads((self.base / compare.BASELINE_META).read_text())
        self.assertEqual(meta["s"]["rendering_method"], "forward_plus")
        self.assertEqual(compare.update_baselines([self.shot], ["nope"], self.out, self.base), 1)

    def test_manifest_defaults_and_validation(self) -> None:
        path = self.tmp / "shots.json"
        path.write_text(json.dumps({"defaults": {"camera": "default", "resolution": [8, 4], "threshold_rmse": 0.1},
                                    "shots": [{"id": "a", "scene": "res://a.tscn"}]}))
        self.assertEqual(compare.load_shots(path)[0]["camera"], "default")
        path.write_text(json.dumps({"shots": [{"id": "a", "scene": "res://a.tscn"}]}))
        with self.assertRaises(ValueError):
            compare.load_shots(path)

    def test_manifest_setup_keys(self) -> None:
        path = self.tmp / "shots.json"
        base = {"id": "a", "scene": "res://a.tscn", "camera": "default", "resolution": [8, 4], "threshold_rmse": 0.1}
        path.write_text(json.dumps({"shots": [{**base, "setup": {"globals": {"g": 1}, "time_scale": 0}}]}))
        self.assertEqual(compare.load_shots(path)[0]["setup"]["time_scale"], 0)
        for bad in ({"global": {}}, [1]):
            path.write_text(json.dumps({"shots": [{**base, "setup": bad}]}))
            with self.assertRaises(ValueError):
                compare.load_shots(path)

    def test_setup_keys_match_capture_setup(self) -> None:
        text = (ROOT / "tests" / "screenshots" / "capture_setup.gd").read_text()
        line = next(ln for ln in text.splitlines() if ln.startswith("const KEYS"))
        self.assertEqual(set(json.loads(line.split("=", 1)[1])), compare.SETUP_KEYS)

    def test_repo_manifest_is_valid_and_baselined(self) -> None:
        for shot in compare.load_shots(compare.SHOTS):
            has = (compare.BASELINES / f"{shot['id']}.png").exists()
            if shot.get(compare.PENDING, False):
                self.assertFalse(has, f"{shot['id']} is approved: drop its {compare.PENDING} key")
            else:
                self.assertTrue(has, shot["id"])
            scene = ROOT / shot["scene"].removeprefix("res://")
            self.assertTrue(scene.exists(), shot["scene"])


if __name__ == "__main__":
    unittest.main()
