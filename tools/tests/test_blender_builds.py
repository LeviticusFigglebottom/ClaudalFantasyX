"""Unit tests for tools/dev/verify_blender_builds.py (M1-QA-02). No Blender needed.
Run: python3 -m unittest discover -s tools/tests"""
import json
import struct
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools" / "dev"))
import verify_blender_builds as vbb  # noqa: E402


def make_glb(positions: np.ndarray, tangents: np.ndarray, indices: np.ndarray) -> bytes:
    """A minimal one-primitive .glb: POSITION, TANGENT (float) and uint16 indices."""
    blobs = [positions.astype("<f4").tobytes(), tangents.astype("<f4").tobytes(), indices.astype("<u2").tobytes()]
    views, off = [], 0
    for b in blobs:
        views.append({"buffer": 0, "byteOffset": off, "byteLength": len(b)})
        off += (len(b) + 3) // 4 * 4
    binc = b"".join(b + b"\0" * ((4 - len(b) % 4) % 4) for b in blobs)
    js = {
        "asset": {"version": "2.0"},
        "buffers": [{"byteLength": len(binc)}],
        "bufferViews": views,
        "accessors": [
            {"bufferView": 0, "componentType": 5126, "count": len(positions), "type": "VEC3",
             "min": positions.min(0).tolist(), "max": positions.max(0).tolist()},
            {"bufferView": 1, "componentType": 5126, "count": len(tangents), "type": "VEC4"},
            {"bufferView": 2, "componentType": 5123, "count": len(indices), "type": "SCALAR"},
        ],
        "meshes": [{"name": "m", "primitives": [{"attributes": {"POSITION": 0, "TANGENT": 1}, "indices": 2}]}],
    }
    jbytes = json.dumps(js).encode()
    jbytes += b" " * ((4 - len(jbytes) % 4) % 4)
    body = struct.pack("<II", len(jbytes), vbb.GLB_JSON_CHUNK) + jbytes + struct.pack("<II", len(binc), vbb.GLB_BIN_CHUNK) + binc
    return struct.pack("<III", vbb.GLB_MAGIC, 2, 12 + len(body)) + body


POS = np.array([[0, 0, 0], [1, 0, 0], [0, 1, 0]], dtype=np.float32)
TAN = np.array([[1, 0, 0, 1]] * 3, dtype=np.float32)
IDX = np.array([0, 1, 2], dtype=np.uint16)
TOL = {"abs": 1e-3, "attributes": ["TANGENT"], "why": "test"}


class ManifestTest(unittest.TestCase):
    def setUp(self) -> None:
        self.manifest = vbb.load_manifest()

    def test_pinned_version_matches_fetch_script(self) -> None:
        text = (ROOT / "tools" / "dev" / "fetch_blender.py").read_text()
        self.assertIn(f'PINNED_DEB = "{self.manifest["blender_deb"]}"', text)
        self.assertTrue(self.manifest["blender_deb"].startswith(self.manifest["blender_version"] + "+"))

    def test_every_job_points_at_real_scripts_and_committed_outputs(self) -> None:
        for job in self.manifest["jobs"]:
            for run in job["runs"]:
                script = run[run.index("--python") + 1]
                self.assertTrue((ROOT / script).is_file(), f"{job['id']}: {script}")
                self.assertTrue(vbb.matches(script, job["sources"]), f"{job['id']}: {script} not in its sources")
            self.assertTrue(vbb.committed_outputs(job, ROOT), f"{job['id']}: no committed output")

    def test_every_blender_glb_in_provenance_is_covered(self) -> None:
        rows = (ROOT / "assets" / "PROVENANCE.md").read_text().splitlines()
        outputs = [o for j in self.manifest["jobs"] for o in j["outputs"]]
        for row in rows:
            cells = [c.strip() for c in row.split("|")]
            if len(cells) > 3 and cells[1].endswith(".glb") and "blender" in row.lower():
                self.assertTrue(vbb.matches(cells[1], outputs), f"{cells[1]} has no job in blender_builds.json")

    def test_rejects_bad_jobs(self) -> None:
        bad = {"jobs": [{"id": "x", "sources": ["a/**"], "outputs": ["b/*.glb"], "runs": [["blender", "--python", "s.py"]]}]}
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "m.json"
            path.write_text(json.dumps(bad))
            with self.assertRaises(ValueError):
                vbb.load_manifest(path)
            bad["jobs"][0]["runs"] = [["{blender}", "--python", "s.py"]]
            bad["jobs"][0]["expected_failure"] = {"task": "M1-X-01"}
            path.write_text(json.dumps(bad))
            with self.assertRaises(ValueError):
                vbb.load_manifest(path)


class SelectionTest(unittest.TestCase):
    def test_matches(self) -> None:
        self.assertTrue(vbb.matches("assets_src/a/b/c.py", ["assets_src/a/**"]))
        self.assertTrue(vbb.matches("assets/x/y.glb", ["assets/x/*.glb"]))
        self.assertFalse(vbb.matches("assets/x/sub/y.glb", ["assets/x/*.glb"]))
        self.assertFalse(vbb.matches("assets/x/y.png", ["assets/x/*.glb"]))
        self.assertFalse(vbb.matches("assets_src/ab/c.py", ["assets_src/a/**"]))

    def test_select_jobs(self) -> None:
        jobs = [{"id": "a", "sources": ["src/a/**"], "outputs": ["out/a/*.glb"]},
                {"id": "b", "sources": ["src/b/*.py"], "outputs": ["out/b/*.glb"]}]
        self.assertEqual([j["id"] for j in vbb.select_jobs(jobs, None)], ["a", "b"])
        self.assertEqual(vbb.select_jobs(jobs, ["docs/x.md"]), [])
        self.assertEqual([j["id"] for j in vbb.select_jobs(jobs, ["src/a/deep/m.py"])], ["a"])
        self.assertEqual([j["id"] for j in vbb.select_jobs(jobs, ["out/b/t.glb"])], ["b"])


class CompareTest(unittest.TestCase):
    def test_identical(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            a, b = Path(tmp) / "a.glb", Path(tmp) / "b.glb"
            a.write_bytes(make_glb(POS, TAN, IDX))
            b.write_bytes(make_glb(POS, TAN, IDX))
            self.assertEqual(vbb.compare_file(a, b, None)[0], "identical")

    def test_tangent_wobble_within_tolerance_only_when_declared(self) -> None:
        tan = TAN.copy()
        tan[1, 0] -= 1e-4
        a, b = make_glb(POS, TAN, IDX), make_glb(POS, tan, IDX)
        ok, why = vbb.compare_glb(a, b, TOL)
        self.assertTrue(ok, why)
        self.assertIn("m.TANGENT", why)
        self.assertFalse(vbb.compare_glb(a, b, None)[0])

    def test_tangent_beyond_tolerance_fails(self) -> None:
        tan = TAN.copy()
        tan[1, 0] = 0.5
        ok, why = vbb.compare_glb(make_glb(POS, TAN, IDX), make_glb(POS, tan, IDX), TOL)
        self.assertFalse(ok)
        self.assertIn("> tolerance", why)

    def test_position_change_is_never_tolerated(self) -> None:
        pos = POS.copy()
        pos[2, 1] += 1e-5
        ok, why = vbb.compare_glb(make_glb(POS, TAN, IDX), make_glb(pos, TAN, IDX), TOL)
        self.assertFalse(ok)
        self.assertIn("POSITION", why)

    def test_index_change_fails(self) -> None:
        ok, why = vbb.compare_glb(make_glb(POS, TAN, IDX), make_glb(POS, TAN, IDX[::-1].copy()), TOL)
        self.assertFalse(ok)
        self.assertIn("m.indices", why)

    def test_non_glb_needs_bytes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            a, b = Path(tmp) / "a.json", Path(tmp) / "b.json"
            a.write_text("{}\n")
            b.write_text("{ }\n")
            self.assertEqual(vbb.compare_file(a, b, TOL)[0], "DIFF")


if __name__ == "__main__":
    unittest.main()
