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
                script = vbb.run_script(run)
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

    def test_known_failures_must_carry_a_signature(self) -> None:  # M1-QA-06
        job = {"id": "x", "sources": ["a/**"], "outputs": ["b/*.glb"], "runs": [["{blender}", "--python", "s.py"]]}
        cases = [
            ({"task": "T", "why": "w"}, "kind"),
            ({"task": "T", "why": "w", "kind": "flaky"}, "kind"),
            ({"task": "T", "why": "w", "kind": "build_error"}, "log_contains"),
            ({"task": "T", "why": "w", "kind": "build_error", "log_contains": "  "}, "log_contains"),
            ({"task": "T", "why": "w", "kind": "mismatch"}, "differs"),
            ({"task": "T", "why": "w", "kind": "mismatch", "differs": {"b/x.glb": []}}, "differs"),
            ({"task": "T", "why": "w", "kind": "mismatch", "differs": {"c/x.glb": ["m.POSITION"]}}, "outside its outputs"),
        ]
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "m.json"
            for known, want in cases:
                path.write_text(json.dumps({"jobs": [dict(job, expected_failure=known)]}))
                with self.assertRaises(ValueError) as cm:
                    vbb.load_manifest(path)
                self.assertIn(want, str(cm.exception), known)
            ok = {"task": "T", "why": "w", "kind": "mismatch", "differs": {"b/x.glb": ["m.POSITION"]}}
            path.write_text(json.dumps({"jobs": [dict(job, expected_failure=ok)]}))
            vbb.load_manifest(path)
            path.write_text(json.dumps({"jobs": [dict(job, runs=[["{python}", "t.py"]])]}))
            with self.assertRaises(ValueError):
                vbb.load_manifest(path)  # a job opens with its Blender run
            path.write_text(json.dumps({"jobs": [job], "coverage_exempt": [{"path": "assets/x.glb"}]}))
            with self.assertRaises(ValueError):
                vbb.load_manifest(path)  # an exemption needs a why

    def test_repo_known_failures_are_pinned(self) -> None:
        kinds = {j["id"]: j["expected_failure"]["kind"] for j in self.manifest["jobs"] if "expected_failure" in j}
        self.assertEqual(kinds, {"base_body": "mismatch"})  # M1-RND-14 fixed


    def test_owner_build_scripts_use_the_gate_thread_count(self) -> None:  # M1-CHR-06
        """A hand rebuild must commit what the gate rebuilds: base_body's build_all.sh passes the job's
        --threads (Asha's build.sh is folded in by the Asha line, M1-CHR-06 notes)."""
        bb = next(j for j in self.manifest["jobs"] if j["id"] == "base_body")
        sh = (ROOT / "assets_src/characters/base_body/build_all.sh").read_text(encoding="utf-8")
        self.assertIn(f'"$blender" --threads {vbb.job_threads(bb, self.manifest)} ', sh)
    def test_python_runs_use_this_interpreter(self) -> None:
        run = ["{python}", "assets_src/x/t.py", "--bake-dir", "{scratch}/b"]
        self.assertEqual(vbb.expand(run, "/bin/blender", Path("/s")), [sys.executable, "assets_src/x/t.py", "--bake-dir", "/s/b"])
        self.assertEqual(vbb.run_script(run), "assets_src/x/t.py")
        self.assertEqual(vbb.expand(["{blender}", "--python", "a.py"], "/bin/blender", Path("/s"))[:2],
                         ["/bin/blender", "--background"])

    def test_blender_runs_with_a_pinned_thread_count(self) -> None:  # M1-QA-06 (Lead addition 1)
        self.assertEqual(self.manifest["default_threads"], 4, "the count the committed files were built with")
        cmd = vbb.expand(["{blender}", "--python", "a.py"], "/bin/blender", Path("/s"), 1)
        self.assertEqual(cmd[:3], ["/bin/blender", "--threads", "1"])
        self.assertNotIn("--threads", vbb.expand(["{python}", "t.py"], "/bin/blender", Path("/s"), 4))
        for job in self.manifest["jobs"]:
            self.assertGreater(vbb.job_threads(job, self.manifest), 0, f"{job['id']}: never the host's CPU count")

    def test_jobs_that_export_tangents_run_single_threaded(self) -> None:
        """Blender's threaded tangent export races: base_body differed run to run at 4 threads and was
        byte-stable at 1 (2026-10-23). A new tangent-exporting build must not join a threaded job."""
        for job in self.manifest["jobs"]:
            # The scripts a job runs and the modules beside them (asha lists base_body/** as a source
            # for its shared bb_* modules, but never runs base_body's build.py).
            dirs = {str(Path(vbb.run_script(r)).parent) for r in job["runs"]}
            scripts = [p for p in vbb._tracked(ROOT, "assets_src", ".py") if str(Path(p).parent) in dirs]
            exports = [p for p in scripts if "export_tangents=True" in (ROOT / p).read_text(encoding="utf-8")]
            if exports:
                self.assertEqual(vbb.job_threads(job, self.manifest), 1, f"{job['id']}: {exports} export tangents")
            self.assertNotIn("tolerance", job, f"{job['id']}: deterministic now; a tolerance is the last resort")

    def test_rejects_a_bad_thread_count(self) -> None:
        job = {"id": "x", "sources": ["a/**"], "outputs": ["b/*.glb"], "runs": [["{blender}", "--python", "s.py"]]}
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "m.json"
            for bad in (-1, "4", True, 1.5):
                path.write_text(json.dumps({"jobs": [dict(job, threads=bad)]}))
                with self.assertRaises(ValueError, msg=bad):
                    vbb.load_manifest(path)

    def test_asha_textures_and_materials_are_verified(self) -> None:  # sweep I, S3 on M1-QA-02
        asha = next(j for j in self.manifest["jobs"] if j["id"] == "asha")
        self.assertTrue(vbb.matches("assets/characters/asha/textures/asha_head_albedo.png", asha["outputs"]))
        self.assertTrue(vbb.matches("assets/characters/asha/materials/skin_head.tres", asha["outputs"]))
        self.assertFalse(vbb.matches("assets/characters/asha/textures/asha_head_albedo.png.import", asha["outputs"]))
        scripts = [vbb.run_script(r) for r in asha["runs"]]
        self.assertIn("assets_src/characters/asha/asha_textures.py", scripts)
        self.assertIn("{scratch}/asha_bake", asha["runs"][0], "the texture step reads the Blender run's dump")


class CoverageTest(unittest.TestCase):  # M1-QA-06
    def test_repo_is_fully_covered(self) -> None:
        self.assertEqual(vbb.coverage_errors(vbb.load_manifest()), [])

    def test_uncovered_glb_and_bpy_script_fail_unless_exempt(self) -> None:
        manifest = {"jobs": [{"id": "a", "sources": ["assets_src/a/**"], "outputs": ["assets/a/*.glb"], "runs": []}]}
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            files = {
                "assets/a/ok.glb": "",
                "assets/b/new.glb": "",
                "assets_src/a/build.py": "import bpy\n",
                "assets_src/b/gen.py": "def f():\n    import bmesh\n",
                "assets_src/b/numpy_only.py": "import numpy\n# not bpy: 'import bpy' in a comment is not at line start\n",
                "assets_src/c/also.py": "from mathutils import Vector\n",
            }
            for rel, text in files.items():
                (root / rel).parent.mkdir(parents=True, exist_ok=True)
                (root / rel).write_text(text)
            errs = vbb.coverage_errors(manifest, root)
            self.assertEqual(len(errs), 3, errs)
            for want in ("assets/b/new.glb", "assets_src/b/gen.py", "assets_src/c/also.py"):
                self.assertTrue(any(e.startswith(want) for e in errs), want)
            manifest["coverage_exempt"] = [{"path": "assets/b/*.glb", "why": "t"}, {"path": "assets_src/**", "why": "t"}]
            self.assertEqual(vbb.coverage_errors(manifest, root), [])


class KnownVerdictTest(unittest.TestCase):  # M1-QA-06
    BUILD = {"task": "T", "why": "w", "kind": "build_error", "log_contains": "ValueError: key"}
    MISMATCH = {"task": "T", "why": "w", "kind": "mismatch", "differs": {"o/a.glb": ["m.indices", "m.POSITION"]}}

    @staticmethod
    def res(error: str = "", diffs: dict | None = None) -> dict:
        files = [{"path": p, "status": "DIFF", "signature": sorted(s)} for p, s in (diffs or {}).items()]
        files.append({"path": "o/same.glb", "status": "identical"})
        return {"ok": False, "error": error, "files": files}

    def test_build_error_needs_its_log_line(self) -> None:
        self.assertTrue(vbb.known_verdict(self.BUILD, self.res("build exited 1"), "...\nValueError: key\n")[0])
        ok, why = vbb.known_verdict(self.BUILD, self.res("build exited 1"), "ImportError: no module\n")
        self.assertFalse(ok)
        self.assertIn("does not contain", why)
        self.assertFalse(vbb.known_verdict(self.BUILD, self.res("timed out after 900 s"), "ValueError: key")[0])
        self.assertFalse(vbb.known_verdict(self.BUILD, self.res(diffs={"o/a.glb": ["m.POSITION"]}), "")[0],
                         "a build that now runs but mismatches is a new failure")

    def test_mismatch_must_be_the_same_files_and_accessors(self) -> None:
        same = {"o/a.glb": ["m.POSITION", "m.indices"]}
        self.assertTrue(vbb.known_verdict(self.MISMATCH, self.res(diffs=same), "")[0])
        for diffs, want in (
            ({"o/a.glb": ["m.POSITION", "m.indices", "m.JOINTS_0"]}, "now also differs in m.JOINTS_0"),
            ({"o/a.glb": ["m.POSITION"]}, "no longer in m.indices"),
            ({"o/a.glb": ["m.POSITION", "m.indices"], "o/b.glb": ["<bytes>"]}, "o/b.glb differs too"),
            ({}, "o/a.glb no longer differs"),
        ):
            ok, why = vbb.known_verdict(self.MISMATCH, self.res(diffs=diffs), "")
            self.assertFalse(ok, diffs)
            self.assertIn(want, why)
        self.assertFalse(vbb.known_verdict(self.MISMATCH, self.res("build exited 1"), "")[0], "a crash is not the mismatch")

    def test_a_content_pin_sees_a_change_inside_the_same_accessors(self) -> None:  # M1-NIT-01
        pinned = dict(self.MISMATCH, rebuilt_sha256={"o/a.glb": "a" * 64})
        same = {"o/a.glb": ["m.POSITION", "m.indices"]}
        res = self.res(diffs=same)
        res["files"][0]["rebuilt_sha256"] = "a" * 64
        self.assertTrue(vbb.known_verdict(pinned, res, "")[0])
        res["files"][0]["rebuilt_sha256"] = "b" * 64
        ok, why = vbb.known_verdict(pinned, res, "")
        self.assertFalse(ok, "same accessors, different bytes: a regression inside POSITION")
        self.assertIn("rebuilt content changed", why)

    def test_a_single_threaded_mismatch_must_pin_content(self) -> None:  # M1-NIT-01
        job = {"id": "x", "sources": ["a/**"], "outputs": ["b/*.glb"], "runs": [["{blender}", "--python", "s.py"]]}
        known = {"task": "T", "why": "w", "kind": "mismatch", "differs": {"b/x.glb": ["m.POSITION"]}}
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "m.json"
            path.write_text(json.dumps({"jobs": [dict(job, threads=4, expected_failure=known)]}))
            vbb.load_manifest(path)  # a threaded build is not byte-stable: names only
            for hashes, want in ((None, "needs 'rebuilt_sha256'"), ({"b/x.glb": "ABC"}, "lowercase hex"),
                                 ({"b/y.glb": "a" * 64}, "per 'differs' path")):
                k = dict(known) if hashes is None else dict(known, rebuilt_sha256=hashes)
                path.write_text(json.dumps({"jobs": [dict(job, threads=1, expected_failure=k)]}))
                with self.assertRaises(ValueError, msg=hashes) as cm:
                    vbb.load_manifest(path)
                self.assertIn(want, str(cm.exception))
            ok = dict(known, rebuilt_sha256={"b/x.glb": "a" * 64})
            path.write_text(json.dumps({"jobs": [dict(job, threads=1, expected_failure=ok)]}))
            vbb.load_manifest(path)

    def test_repo_base_body_pins_its_rebuilt_content(self) -> None:  # M1-NIT-01
        manifest = vbb.load_manifest()
        bb = next(j for j in manifest["jobs"] if j["id"] == "base_body")
        self.assertEqual(vbb.job_threads(bb, manifest), 1)
        self.assertEqual(set(bb["expected_failure"]["rebuilt_sha256"]), set(bb["expected_failure"]["differs"]))


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

    def test_differences_name_every_accessor_not_only_the_first_kind(self) -> None:  # M1-QA-06
        pos = POS.copy()
        pos[2, 1] += 0.5  # changes POSITION data and its max
        tan = TAN.copy()
        tan[1, 0] -= 1e-4  # within tolerance: not a difference
        a, b = make_glb(POS, TAN, IDX), make_glb(pos, tan, IDX[::-1].copy())
        self.assertEqual(vbb.glb_differences(a, b, TOL), ["m.POSITION", "m.indices"])
        self.assertEqual(vbb.glb_differences(a, b, None), ["m.POSITION", "m.TANGENT", "m.indices"])
        self.assertEqual(vbb.glb_differences(a, a, TOL), [])
        with tempfile.TemporaryDirectory() as tmp:
            pa, pb = Path(tmp) / "a.glb", Path(tmp) / "b.glb"
            pa.write_bytes(a)
            pb.write_bytes(b)
            status, _detail, sig = vbb.compare_file(pa, pb, TOL)
            self.assertEqual((status, sig), ("DIFF", ["m.POSITION", "m.indices"]))
            pb.write_bytes(b"not a glb at all")
            self.assertEqual(vbb.compare_file(pa, pb, TOL)[2], [vbb.SIG_BYTES])

    def test_non_glb_needs_bytes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            a, b = Path(tmp) / "a.json", Path(tmp) / "b.json"
            a.write_text("{}\n")
            b.write_text("{ }\n")
            self.assertEqual(vbb.compare_file(a, b, TOL)[0], "DIFF")


if __name__ == "__main__":
    unittest.main()
