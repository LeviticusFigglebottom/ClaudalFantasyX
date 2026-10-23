"""Tests for tools/dev/godot_log_check.py (M1-QA-06): the ci_local script-error check must catch real
GDScript errors and ignore Godot's "Parse Error" for a deliberately torn text resource.
The sample lines are Godot 4.6.3's own output, captured 2026-10-23.
Run: python3 -m unittest discover -s tools/tests"""
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools" / "dev"))
import godot_log_check as glc  # noqa: E402

TORN_TRES = """ERROR: user://saves/slot_1.tres:6 - Parse Error: Expected ','.
   at: _printerr (scene/resources/resource_format_text.cpp:40)
   GDScript backtrace (most recent call first):
       [0] test_a_torn_resource_reads_as_corrupt (res://tests/unit/test_save_recovery.gd:3)
ERROR: Failed loading resource: user://saves/slot_1.tres.
   at: _load (core/io/resource_loader.cpp:343)""".splitlines()

BROKEN_GD = """SCRIPT ERROR: Parse Error: Identifier "undeclared_name" not declared in the current scope.
          at: GDScript::reload (res://game/battle/broken.gd:3)
ERROR: Failed to load script "res://game/battle/broken.gd" with error "Parse error".
   at: load (modules/gdscript/gdscript.cpp:2907)""".splitlines()

CLEAN = ["Godot Engine v4.6.3.stable", "PASS test_x", "Tests: 944 run, 0 failed"]


class GodotLogCheckTest(unittest.TestCase):
    def test_a_torn_text_resource_in_a_test_is_not_a_script_error(self) -> None:
        self.assertEqual(glc.script_errors(CLEAN + TORN_TRES), [])

    def test_a_real_gdscript_parse_error_is_caught(self) -> None:
        bad = glc.script_errors(CLEAN + TORN_TRES + BROKEN_GD)
        self.assertEqual(len(bad), 2, bad)
        self.assertTrue(bad[0].startswith("SCRIPT ERROR: Parse Error"))
        self.assertIn("Failed to load script", bad[1])

    def test_a_parse_error_naming_a_gd_file_counts_even_without_script_error(self) -> None:
        line = "ERROR: res://tests/unit/test_x.gd:12 - Parse Error: Unexpected token."
        self.assertEqual(glc.script_errors([line]), [line])
        self.assertEqual(glc.script_errors(["ERROR: res://a/b.tscn:4 - Parse Error: Expected ']'."]), [])

    def test_runtime_script_errors_still_fail(self) -> None:
        line = "SCRIPT ERROR: Invalid call. Nonexistent function 'foo' in base 'Nil'."
        self.assertEqual(glc.script_errors([line]), [line])

    def test_the_import_log_stays_strict_about_resources(self) -> None:
        self.assertEqual(len(glc.import_errors(TORN_TRES)), 2, "a torn resource in the repo is an import error")
        self.assertEqual(glc.import_errors(CLEAN), [])

    def test_cli_exit_codes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            log = Path(tmp) / "t.log"
            log.write_text("\n".join(CLEAN + TORN_TRES) + "\n")
            self.assertEqual(glc.main(["tests", str(log)]), 0)
            self.assertEqual(glc.main(["import", str(log)]), 1)
            log.write_text("\n".join(BROKEN_GD) + "\n")
            self.assertEqual(glc.main(["tests", str(log)]), 1)
            self.assertEqual(glc.main(["nope", str(log)]), 2)

    def test_ci_local_uses_the_checker(self) -> None:
        text = (ROOT / "tools" / "ci_local.sh").read_text()
        self.assertIn("godot_log_check.py tests", text)
        self.assertIn("godot_log_check.py import", text)
        self.assertNotIn('grep -E "SCRIPT ERROR|Parse Error" $L/hymn_tests.log', text)


if __name__ == "__main__":
    unittest.main()
