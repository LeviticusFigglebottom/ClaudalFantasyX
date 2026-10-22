"""Unit tests for tools/dlgc.py. Run: python3 -m unittest discover -s tools/tests"""
import json
import shutil
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
import dlgc  # noqa: E402


class DlgcTestBase(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp())
        d = self.tmp / "game" / "data" / "dialogue"
        d.mkdir(parents=True)
        (self.tmp / "game" / "data" / "loc").mkdir(parents=True)
        for name in ("speakers.json", "emotions.json"):
            shutil.copy(ROOT / "game" / "data" / "dialogue" / name, d / name)

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp)

    def write(self, name: str, body: str) -> Path:
        p = self.tmp / "game" / "data" / "dialogue" / "ch99" / f"{name}.dlg"
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(textwrap.dedent(body).lstrip("\n"), encoding="utf-8")
        return p

    def scene(self, body: str, name: str = "t_scene") -> list[str]:
        """Writes a one-node scene and returns compile errors."""
        self.write(name, f"title: {name}\n---\n" + textwrap.dedent(body).strip("\n") + "\n===\n")
        return dlgc.compile_project(self.tmp).errors

    def ops(self, body: str, node: str = "t_scene") -> list[dict]:
        errors = self.scene(body)
        self.assertEqual(errors, [])
        res = dlgc.compile_project(self.tmp)
        data = json.loads(res.outputs["game/data/dialogue/compiled/t_scene.json"])
        return data["nodes"][node]["ops"]

    def assert_error(self, body: str, fragment: str, line: int) -> None:
        errors = self.scene(body)
        want = f"game/data/dialogue/ch99/t_scene.dlg:{line}: "
        self.assertTrue(any(e.startswith(want) and fragment in e for e in errors),
                        f"expected '{want}...{fragment}' in {errors}")


class CompileTests(DlgcTestBase):
    def test_line_with_speaker_and_emotion(self) -> None:
        ops = self.ops("Asha [soft_smile]: Then we walk. #line:t_001")
        self.assertEqual(ops, [{"op": "line", "id": "t_001", "key": "DLG_T_001", "speaker": "asha",
                                "emotion": "soft_smile", "voice": "", "src": 3}])

    def test_narration_has_no_speaker(self) -> None:
        op = self.ops("The tide went out. #line:t_001")[0]
        self.assertEqual((op["speaker"], op["emotion"]), ("", ""))

    def test_escaped_colon_in_narration(self) -> None:
        self.ops("Dawn\\: grey and long. #line:t_001")
        rows = dlgc.compile_project(self.tmp).loc_rows
        self.assertEqual(rows, [("DLG_T_001", "Dawn: grey and long.")])

    def test_extra_tags_are_kept(self) -> None:
        op = self.ops("Rhen: Hey. #line:t_001 #whisper")[0]
        self.assertEqual(op["tags"], ["whisper"])

    def test_cue_args_and_kwargs_are_typed(self) -> None:
        op = self.ops('@camera dock_wide "two words" blend=1.5 hold=true count=2')[0]
        self.assertEqual(op, {"op": "cue", "cue": "camera", "args": ["dock_wide", "two words"],
                              "kwargs": {"blend": 1.5, "hold": True, "count": 2}, "src": 3})

    def test_comments_are_ignored(self) -> None:
        ops = self.ops("@anim asha look_at rhen   // turn her head\n// whole-line comment")
        self.assertEqual(ops[0]["args"], ["asha", "look_at", "rhen"])
        self.assertEqual(len(ops), 1)

    def test_if_elseif_else_codegen(self) -> None:
        ops = self.ops("""
            <<if $a>>
            Rhen: A. #line:t_001
            <<elseif not $b and $n >= 2>>
            Rhen: B. #line:t_002
            <<else>>
            Rhen: C. #line:t_003
            <<endif>>
        """)
        self.assertEqual([o["op"] for o in ops], ["if_not", "line", "goto", "if_not", "line", "goto", "line", "goto"])
        self.assertEqual(ops[0]["to"], 3)
        self.assertEqual(ops[3]["cond"], ["and", ["not", ["flag", "b"]], [">=", ["flag", "n"], ["lit", 2]]])
        self.assertEqual(ops[3]["to"], 6)
        self.assertTrue(all(ops[i]["to"] == 8 for i in (2, 5, 7)))

    def test_indented_if_body(self) -> None:
        ops = self.ops("""
            <<if $a>>
                Rhen: A. #line:t_001
            <<endif>>
        """)
        self.assertEqual(ops[1]["id"], "t_001")

    def test_expression_precedence_and_literals(self) -> None:
        ops = self.ops('<<set $x = $a or $b and not ($c == "x y")>>\n<<set $y = -1.5>>\n<<set $z = false>>')
        self.assertEqual(ops[0]["value"],
                         ["or", ["flag", "a"], ["and", ["flag", "b"], ["not", ["==", ["flag", "c"], ["lit", "x y"]]]]])
        self.assertEqual(ops[1]["value"], ["lit", -1.5])
        self.assertEqual(ops[2]["value"], ["lit", False])

    def test_all_comparison_operators(self) -> None:
        for op in ("==", "!=", "<", ">", "<=", ">="):
            ops = self.ops(f"<<set $x = $n {op} 3>>")
            self.assertEqual(ops[0]["value"], [op, ["flag", "n"], ["lit", 3]])

    def test_options_with_nested_bodies(self) -> None:
        ops = self.ops("""
            -> Wait. #line:t_001
                <<jump other>>
            -> Walk. #line:t_002 <<if $ready>>
                <<set $walked = true>>
                -> Inner. #line:t_003
                    Rhen: Deep. #line:t_004
            Rhen: After. #line:t_005
            ===
            title: other
            ---
            Rhen: Other. #line:t_006
        """)
        menu = ops[0]
        self.assertEqual(menu["op"], "options")
        self.assertEqual([c["id"] for c in menu["choices"]], ["t_001", "t_002"])
        self.assertEqual(menu["choices"][1]["cond"], ["flag", "ready"])
        self.assertEqual(ops[menu["choices"][0]["to"]], {"op": "jump", "node": "other", "src": 4})
        self.assertEqual(ops[menu["choices"][1]["to"]]["op"], "set")
        self.assertEqual(ops[menu["next"]]["id"], "t_005")
        inner = next(o for o in ops[1:] if o["op"] == "options")
        self.assertEqual(ops[inner["choices"][0]["to"]]["id"], "t_004")

    def test_option_condition_before_line_tag(self) -> None:
        ops = self.ops("-> Go. <<if $a>> #line:t_001")
        self.assertEqual(ops[0]["choices"][0]["cond"], ["flag", "a"])

    def test_event_and_stop(self) -> None:
        ops = self.ops("<<event zone_unlock haluna 2>>\n<<stop>>")
        self.assertEqual(ops[0], {"op": "event", "name": "zone_unlock", "args": ["haluna", 2], "src": 3})
        self.assertEqual(ops[1]["op"], "stop")

    def test_loc_csv_format(self) -> None:
        self.scene('Asha: Hello, "friend". #line:t_001\n-> Yes. #line:t_002')
        csv_text = dlgc.compile_project(self.tmp).outputs["game/data/loc/dialogue.csv"]
        self.assertEqual(csv_text, 'keys,en\nDLG_T_001,"Hello, ""friend""."\nDLG_T_002,Yes.\n')

    def test_headers_are_kept(self) -> None:
        self.write("t_scene", "title: t_scene\nlocation: ch99/x\n---\nRhen: Hi. #line:t_001\n===\n")
        res = dlgc.compile_project(self.tmp)
        data = json.loads(res.outputs["game/data/dialogue/compiled/t_scene.json"])
        self.assertEqual(data["nodes"]["t_scene"]["headers"], {"location": "ch99/x"})
        self.assertEqual(data["start"], "t_scene")


class ErrorTests(DlgcTestBase):
    def test_missing_line_tag(self) -> None:
        self.assert_error("Rhen: No tag here.", "missing its #line", 3)

    def test_missing_line_tag_on_option(self) -> None:
        self.assert_error("Rhen: Hi. #line:t_001\n-> Untagged option", "option text is missing", 4)

    def test_duplicate_line_id_across_files(self) -> None:
        self.write("other_scene", "title: other_scene\n---\nRhen: One. #line:dup_1\n===\n")
        errors = self.scene("Rhen: Two. #line:dup_1")
        self.assertTrue(any("t_scene.dlg:3: duplicate line id 'dup_1'" in e and "other_scene.dlg:3" in e
                            for e in errors), errors)

    def test_unknown_jump_target(self) -> None:
        self.assert_error("<<jump nowhere>>", "unknown jump target 'nowhere'", 3)

    def test_missing_endif(self) -> None:
        self.assert_error("<<if $a>>\nRhen: Hi. #line:t_001", "unbalanced <<if>>", 3)

    def test_stray_endif(self) -> None:
        self.assert_error("Rhen: Hi. #line:t_001\n<<endif>>", "<<endif>> without a matching <<if>>", 4)

    def test_else_after_else(self) -> None:
        self.assert_error("<<if $a>>\n<<else>>\n<<else>>\n<<endif>>", "after <<else>>", 5)

    def test_misaligned_endif(self) -> None:
        self.assert_error("<<if $a>>\n    Rhen: Hi. #line:t_001\n    <<endif>>", "must align", 5)

    def test_unexpected_indent(self) -> None:
        self.assert_error("Rhen: Hi. #line:t_001\n    Rhen: Indented. #line:t_002", "bad indentation", 4)

    def test_dedent_to_unknown_column(self) -> None:
        self.assert_error("-> A. #line:t_001\n    Rhen: In. #line:t_002\n  Rhen: Odd. #line:t_003",
                          "bad indentation", 5)

    def test_tabs_rejected(self) -> None:
        self.assert_error("-> A. #line:t_001\n\tRhen: In. #line:t_002", "tabs", 4)

    def test_unknown_speaker(self) -> None:
        self.assert_error("Nobody: Hi. #line:t_001", "unknown speaker 'Nobody'", 3)

    def test_unknown_emotion(self) -> None:
        self.assert_error("Rhen [smug]: Hi. #line:t_001", "unknown emotion '[smug]'", 3)

    def test_unknown_command(self) -> None:
        self.assert_error("<<dance>>", "unknown command <<dance>>", 3)

    def test_bad_expression(self) -> None:
        self.assert_error("<<if $a ==>>\n<<endif>>", "ends too early", 3)
        self.assert_error("<<if flag>>\n<<endif>>", "unknown word 'flag'", 3)

    def test_missing_close(self) -> None:
        self.write("t_scene", "title: t_scene\n---\nRhen: Hi. #line:t_001\n")
        errors = dlgc.compile_project(self.tmp).errors
        self.assertTrue(any("missing its closing '==='" in e for e in errors), errors)

    def test_title_must_match_file(self) -> None:
        self.write("t_scene", "title: wrong_name\n---\nRhen: Hi. #line:t_001\n===\n")
        errors = dlgc.compile_project(self.tmp).errors
        self.assertTrue(any("t_scene.dlg:1:" in e and "must match the file name" in e for e in errors), errors)

    def test_errors_produce_no_scene_output(self) -> None:
        self.scene("<<jump nowhere>>")
        self.assertNotIn("game/data/dialogue/compiled/t_scene.json", dlgc.compile_project(self.tmp).outputs)


class CheckModeTests(DlgcTestBase):
    def test_write_then_check_is_clean(self) -> None:
        self.scene("Rhen: Hi. #line:t_001")
        self.assertEqual(dlgc.write(self.tmp).errors, [])
        self.assertEqual(dlgc.check(self.tmp), [])

    def test_check_flags_stale_outputs(self) -> None:
        self.scene("Rhen: Hi. #line:t_001")
        dlgc.write(self.tmp)
        self.scene("Rhen [sad]: Changed. #line:t_001")
        errors = dlgc.check(self.tmp)
        self.assertTrue(any("dialogue.csv: dialogue output is stale" in e for e in errors), errors)
        self.assertTrue(any("t_scene.json: dialogue output is stale" in e for e in errors), errors)

    def test_check_flags_orphaned_compiled_file(self) -> None:
        self.scene("Rhen: Hi. #line:t_001")
        dlgc.write(self.tmp)
        (self.tmp / "game" / "data" / "dialogue" / "compiled" / "gone.json").write_text("{}")
        self.assertTrue(any("gone.json" in e for e in dlgc.check(self.tmp)))
        dlgc.write(self.tmp)
        self.assertFalse((self.tmp / "game" / "data" / "dialogue" / "compiled" / "gone.json").exists())

    def test_check_does_not_write(self) -> None:
        self.scene("Rhen: Hi. #line:t_001")
        dlgc.check(self.tmp)
        self.assertFalse((self.tmp / "game" / "data" / "loc" / "dialogue.csv").exists())

    def test_repo_outputs_are_fresh(self) -> None:
        self.assertEqual(dlgc.check(ROOT), [])


if __name__ == "__main__":
    unittest.main()
