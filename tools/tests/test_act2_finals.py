"""Act II's final cues wait for Git LFS (ADR 0039, M3-AUD-839): every ACT2_FINALS job renders from assets_src/music/act2/
into assets/audio/music/act2/, and no file there is committed until .gitattributes routes that path to LFS (the Lead
adds it when LFS is live in the cloud). Run: python3 -m unittest discover -s tools/tests"""
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools" / "audio"))
import render_all  # noqa: E402


def lfs_routes(path: str) -> bool:
    attrs = ROOT / ".gitattributes"
    if not attrs.is_file():
        return False
    for line in attrs.read_text(encoding="utf-8").splitlines():
        if line.strip().startswith(path) and "filter=lfs" in line:
            return True
    return False


def lfs_routes_act2() -> bool:
    return lfs_routes("assets/audio/music/act2")


class Act2FinalsTest(unittest.TestCase):
    def test_every_final_renders_from_act2_into_act2(self) -> None:
        for src, rel_dir, files, kind in render_all.ACT2_FINALS:
            self.assertTrue(src.startswith("assets_src/music/act2/"), src)
            self.assertEqual(rel_dir, render_all.ACT2_DIR, src)
            self.assertTrue((ROOT / src).is_file(), src)
            self.assertIn(kind, ("music", "music_loop"), src)
        self.assertFalse(any(rel == render_all.ACT2_DIR for _, rel, _, _ in render_all.JOBS),
                         "Act II finals stay out of the default run")

    def test_every_act3_cue_renders_from_act3_into_act3(self) -> None:
        for src, rel_dir, files, kind in render_all.ACT3_FINALS:
            self.assertTrue(src.startswith("assets_src/music/act3/"), src)
            self.assertEqual(rel_dir, render_all.ACT3_DIR, src)
            self.assertTrue((ROOT / src).is_file(), src)
        self.assertFalse(any(rel == render_all.ACT3_DIR for _, rel, _, _ in render_all.JOBS))

    def test_every_act3_sfx_renders_from_act3_into_act3(self) -> None:
        for src, rel_dir, files, kind in render_all.ACT3_SFX:
            self.assertTrue(src.startswith("assets_src/sfx/act3/"), src)
            self.assertEqual(rel_dir, render_all.ACT3_SFX_DIR, src)
            self.assertTrue((ROOT / src).is_file(), src)
            self.assertIn(kind, ("sfx", "sfx_set"), src)
        self.assertFalse(any(rel == render_all.ACT3_SFX_DIR for _, rel, _, _ in render_all.JOBS))

    def test_nothing_under_act3_sfx_is_committed_before_lfs(self) -> None:
        if lfs_routes(render_all.ACT3_SFX_DIR):
            self.skipTest(".gitattributes routes act3 SFX to LFS (ADR 0039 is live)")
        tracked = subprocess.run(["git", "ls-files", render_all.ACT3_SFX_DIR], cwd=ROOT, capture_output=True,
                                 text=True).stdout.split()
        self.assertEqual([t for t in tracked if t.endswith((".ogg", ".loop.json", ".ogg.import"))], [],
                         "Act III SFX land with LFS too (M3-AUD-859)")

    def test_nothing_under_act3_is_committed_before_lfs(self) -> None:
        if lfs_routes(render_all.ACT3_DIR):
            self.skipTest(".gitattributes routes act3 to LFS (ADR 0039 is live)")
        tracked = subprocess.run(["git", "ls-files", render_all.ACT3_DIR], cwd=ROOT, capture_output=True,
                                 text=True).stdout.split()
        self.assertEqual([t for t in tracked if t.endswith((".ogg", ".loop.json", ".ogg.import"))], [],
                         "Act III cues land with LFS too")

    def test_nothing_under_act2_is_committed_before_lfs(self) -> None:
        if lfs_routes_act2():
            self.skipTest(".gitattributes routes act2 to LFS (ADR 0039 is live)")
        tracked = subprocess.run(["git", "ls-files", render_all.ACT2_DIR], cwd=ROOT, capture_output=True,
                                 text=True).stdout.split()
        audio = [t for t in tracked if t.endswith((".ogg", ".loop.json", ".ogg.import"))]
        self.assertEqual(audio, [], "Act II finals land with LFS: keep them uncommitted until the Lead says it's live")


if __name__ == "__main__":
    unittest.main()
