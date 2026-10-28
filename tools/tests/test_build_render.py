"""ADR 0172's prototype (tools/audio/build_render.py): a job's input key follows its import closure, and --ensure keeps
a file that matches the manifest and redoes one that doesn't. Nothing here renders audio.
Run: python3 -m unittest discover -s tools/tests"""
import hashlib
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools" / "audio"))
import build_render  # noqa: E402


class BuildRenderTest(unittest.TestCase):
    def test_a_jobs_inputs_are_its_source_and_every_local_module_it_imports(self) -> None:
        inputs = build_render.closure("assets_src/sfx/act2_creature_sfx.py")
        for rel in ("assets_src/sfx/act2_creature_sfx.py", "assets_src/sfx/creature_sfx.py",
                    "assets_src/sfx/underwater_sfx.py", "tools/audio/synth/dsp.py", "tools/audio/synth/mixer.py"):
            self.assertIn(rel, inputs)
        self.assertFalse(any("numpy" in p for p in inputs), "only the repo's own modules")
        self.assertNotIn("assets_src/sfx/screen_sfx.py", inputs, "not a module it never imports")

    def test_the_key_names_the_toolchain(self) -> None:
        a = build_render.input_key("assets_src/sfx/screen_sfx.py", "numpy 1; ffmpeg 1")
        b = build_render.input_key("assets_src/sfx/screen_sfx.py", "numpy 2; ffmpeg 1")
        self.assertNotEqual(a, b, "another numpy is another key")
        self.assertEqual(a, build_render.input_key("assets_src/sfx/screen_sfx.py", "numpy 1; ffmpeg 1"))

    def test_needs_lists_only_missing_or_changed_files(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            ok = Path(td, "a.ogg")
            ok.write_bytes(b"same")
            Path(td, "b.ogg").write_bytes(b"old")
            row = {"files": {"a.ogg": hashlib.sha256(b"same").hexdigest(),
                             "b.ogg": hashlib.sha256(b"new").hexdigest(),
                             "c.ogg": hashlib.sha256(b"x").hexdigest()}}
            self.assertEqual(build_render._needs(row, td), ["b.ogg", "c.ogg"])

    def test_every_render_job_is_covered(self) -> None:
        import render_all
        for src, *_ in render_all.JOBS:
            self.assertTrue(build_render.closure(src), src)


if __name__ == "__main__":
    unittest.main()
