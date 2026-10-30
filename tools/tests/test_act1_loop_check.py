"""The Act I loop check runs over the shipped files and finds every seam clean and every level in budget (M3-AUD-861).
It decodes audio, so it skips when a file is a Git LFS pointer (run `git lfs pull`) or ffmpeg is missing.
Run: python3 -m unittest discover -s tools/tests"""
import importlib.util
import shutil
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
_spec = importlib.util.spec_from_file_location("act1_loop_check", ROOT / "tools/audio/act1_loop_check.py")
check = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(check)


def _is_pointer(p: Path) -> bool:
    return p.stat().st_size < 400 and p.read_bytes().startswith(b"version https://git-lfs")


class Act1LoopCheckTest(unittest.TestCase):
    def test_every_act1_zone_has_its_music_and_beds_listed(self) -> None:
        files = check.zone_files()
        zones = {z for z, _, _ in files}
        self.assertIn("prologue", zones)
        self.assertTrue(any(k.startswith("bed ") for _, k, _ in files))
        self.assertTrue(any(k.startswith("music ") for _, k, _ in files))

    @unittest.skipUnless(shutil.which("ffmpeg"), "needs ffmpeg to decode")
    def test_the_check_passes(self) -> None:
        for _, _, res in check.zone_files():
            if _is_pointer(ROOT / res.removeprefix("res://")):
                self.skipTest("LFS pointers: run git lfs pull")
        self.assertEqual(_run(), 0, "every Act I seam clean and every level in budget")


def _run() -> int:
    import contextlib
    import io
    import sys
    argv, sys.argv = sys.argv, ["act1_loop_check.py"]
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            return check.main()
    finally:
        sys.argv = argv


if __name__ == "__main__":
    unittest.main()
