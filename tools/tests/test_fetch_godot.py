"""tools/dev/fetch_godot.py: the official-build path's SHA-512 check (the 4.7.2 port prep)."""
import hashlib
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "dev"))
import fetch_godot  # noqa: E402

GOOD = b"godot editor bytes"


class OfficialChecksumTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def test_parses_sha512sum_lines_and_skips_noise(self) -> None:
        h = "ab" * 64
        sums = fetch_godot.parse_sums(f"{h}  Godot_v4.7.2-stable_linux.x86_64.zip\nnot a line\n{'cd' * 64} *b.tpz\n")
        self.assertEqual(sums, {"Godot_v4.7.2-stable_linux.x86_64.zip": h, "b.tpz": "cd" * 64})

    def test_a_matching_file_passes_and_a_changed_or_unlisted_one_is_refused(self) -> None:
        f = self.dir / "Godot_v4.7.2-stable_linux.x86_64.zip"
        f.write_bytes(GOOD)
        sums = {f.name: hashlib.sha512(GOOD).hexdigest()}
        fetch_godot.verify(f, sums)
        f.write_bytes(GOOD + b"!")
        with self.assertRaises(ValueError):
            fetch_godot.verify(f, sums)
        with self.assertRaises(ValueError):
            fetch_godot.verify(f, {})

    def test_official_names_are_the_release_files(self) -> None:
        self.assertEqual(
            fetch_godot.official_names("4.7.2"),
            ("Godot_v4.7.2-stable_linux.x86_64.zip", "Godot_v4.7.2-stable_export_templates.tpz"),
        )


if __name__ == "__main__":
    unittest.main()
