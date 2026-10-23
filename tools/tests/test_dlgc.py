"""Unit tests for tools/dlgc.py. Run: python3 -m unittest discover -s tools/tests"""
import contextlib
import io
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
        for name in ("speakers.json", "emotions.json", "cues.json", "events.json"):
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
        op = self.ops('@fade out 1.5 "deep blue"')[0]
        self.assertEqual(op, {"op": "cue", "cue": "fade", "args": ["out", 1.5, "deep blue"], "kwargs": {}, "src": 3})
        op = self.ops("@anim asha wave rhen loop=true")[0]
        self.assertEqual(op["kwargs"], {"loop": True})
        op = self.ops("@vfx glimmer_held at=rhen count=2 drift=down_seaward")[0]
        self.assertEqual(op["kwargs"], {"at": "rhen", "count": 2, "drift": "down_seaward"})

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
        ops = self.ops("<<event zone_unlock haluna>>\n<<stop>>")
        self.assertEqual(ops[0], {"op": "event", "name": "zone_unlock", "args": ["haluna"], "src": 3})
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


class SpeakerSyntaxTests(DlgcTestBase):
    """M1-NAR-04: `Speaker as "Alias"` and `Narrator(identity) [emotion]`."""

    def rows(self) -> list[tuple[str, str]]:
        return dlgc.compile_project(self.tmp).loc_rows

    def test_alias_adds_name_key_and_one_loc_row(self) -> None:
        ops = self.ops('Asha as "The girl" [smile]: Hi. #line:t_001\n'
                       'Asha as "The girl": Again. #line:t_002\nAsha: Named. #line:t_003')
        self.assertEqual(ops[0], {"op": "line", "id": "t_001", "key": "DLG_T_001", "speaker": "asha",
                                  "emotion": "smile", "voice": "", "src": 3, "name_key": "DLG_NAME_ASHA_THE_GIRL"})
        self.assertEqual(ops[1]["name_key"], "DLG_NAME_ASHA_THE_GIRL")
        self.assertNotIn("name_key", ops[2])
        self.assertEqual(self.rows(), [("DLG_T_001", "Hi."), ("DLG_NAME_ASHA_THE_GIRL", "The girl"),
                                       ("DLG_T_002", "Again."), ("DLG_T_003", "Named.")])

    def test_alias_without_letters_gets_a_hash_key(self) -> None:
        op = self.ops('Toma as "???": Who goes. #line:t_001')[0]
        self.assertRegex(op["name_key"], r"^DLG_NAME_TOMA_X[0-9A-F]{6}$")
        self.assertIn((op["name_key"], "???"), self.rows())

    def test_alias_with_escaped_quote(self) -> None:
        op = self.ops('Asha as "The \\"girl\\"": Hi. #line:t_001')[0]
        self.assertIn((op["name_key"], 'The "girl"'), self.rows())

    def test_aliases_that_collide_are_rejected(self) -> None:
        self.assert_error('Asha as "The girl": A. #line:t_001\nAsha as "The girl!": B. #line:t_002',
                          "both map to DLG_NAME_ASHA_THE_GIRL", 4)

    def test_alias_key_cannot_shadow_a_line_key(self) -> None:
        self.assert_error('Rhen: A. #line:name_asha_girl\nAsha as "Girl": B. #line:t_002',
                          "already defined at", 4)

    def test_empty_alias(self) -> None:
        self.assert_error('Asha as "": Hi. #line:t_001', "empty alias", 3)

    def test_narrator_with_identity_and_emotion(self) -> None:
        op = self.ops("Narrator(rhen) [tender]: Long ago. #line:t_001 #vo")[0]
        self.assertEqual(op, {"op": "line", "id": "t_001", "key": "DLG_T_001", "speaker": "", "emotion": "tender",
                              "voice": "", "src": 3, "narrator": "rhen", "tags": ["vo"]})

    def test_narrator_with_emotion_only(self) -> None:
        op = self.ops("Narrator [sad]: Long ago. #line:t_001")[0]
        self.assertEqual((op["speaker"], op["emotion"]), ("", "sad"))
        self.assertNotIn("narrator", op)

    def test_plain_narration_is_unchanged(self) -> None:
        op = self.ops("The tide went out. #line:t_001")[0]
        self.assertNotIn("narrator", op)
        self.assertNotIn("name_key", op)

    def test_narrator_errors(self) -> None:
        self.assert_error("Narrator(nobody): Hi. #line:t_001", "unknown narrator identity 'nobody'", 3)
        self.assert_error('Narrator as "X": Hi. #line:t_001', "takes no 'as", 3)
        self.assert_error("Asha(rhen): Hi. #line:t_001", "only Narrator takes a voice identity", 3)
        self.assert_error("Narrator [smug]: Hi. #line:t_001", "unknown emotion '[smug]'", 3)


class TagTests(DlgcTestBase):
    """M1-NAR-04: #sung, #notr, #tn:"...", the notes file, and interior spacing."""

    def notes(self) -> str:
        return dlgc.compile_project(self.tmp).outputs["game/data/dialogue/compiled/translator_notes.tsv"]

    def test_sung_is_a_plain_tag(self) -> None:
        self.assertEqual(self.ops("Asha: La. #line:t_001 #sung")[0]["tags"], ["sung"])

    def test_notr_and_note_go_to_the_notes_file_not_the_tags(self) -> None:
        op = self.ops('Asha: Vey ennu. #line:t_001 #sung #notr #tn:"Lamptongue: keep it."')[0]
        self.assertEqual(op["tags"], ["sung", "notr"])
        self.assertEqual(self.notes(), "keys\tscene\tdo_not_translate\tnote\ten\n"
                                       "DLG_T_001\tt_scene\tyes\tLamptongue: keep it.\tVey ennu.\n")
        self.assertEqual(dlgc.compile_project(self.tmp).loc_rows, [("DLG_T_001", "Vey ennu.")])

    def test_note_without_notr_and_on_an_option(self) -> None:
        self.ops('-> Go. #tn:"A verb, not a board game." #line:t_001\n'
                 '-> Stay. #line:t_002 #tn:"Say \\"stay\\"." <<if $a>>')
        rows = self.notes().splitlines()[1:]
        self.assertEqual(rows, ["DLG_T_001\tt_scene\t\tA verb, not a board game.\tGo.",
                                'DLG_T_002\tt_scene\t\t"Say ""stay""."\tStay.'])

    def test_notes_file_has_only_a_header_without_notes(self) -> None:
        self.ops("Rhen: Hi. #line:t_001")
        self.assertEqual(self.notes(), "keys\tscene\tdo_not_translate\tnote\ten\n")

    def test_notr_needs_a_note(self) -> None:
        self.assert_error("Asha: Vey. #line:t_001 #notr", "#notr needs a translator note", 3)

    def test_bad_notes(self) -> None:
        self.assert_error("Asha: Vey. #line:t_001 #tn:'single'", "double quotes", 3)
        self.assert_error('Asha: Vey. #line:t_001 #tn:"a" #tn:"b"', "more than one", 3)
        self.assert_error('Asha: Vey. #line:t_001 #tn:" "', "is empty", 3)

    def test_interior_spacing_is_kept(self) -> None:
        self.ops("Rhen: Wait.  Listen. #line:t_001  #whisper")
        self.assertEqual(dlgc.compile_project(self.tmp).loc_rows, [("DLG_T_001", "Wait.  Listen.")])


class CueVocabularyTests(DlgcTestBase):
    """M1-NAR-04: cues.json (names, args, keys, option sets) and header grades."""

    def test_new_cues_compile(self) -> None:
        ops = self.ops("@sfx drownbell_toll vol=0.5 at=causeway\n@music silence fade=1.2\n"
                       "@wait music=verse_end max=8\n@wait 1.5\n@camera H01 blend=3.0 grade=ch02\n"
                       "@vfx glimmer_lift at=asha motion=spiral_up rate=slow\n@face asha soft_smile 0.6\n"
                       "@mark asha path run\n@letterbox on")
        self.assertEqual(ops[0]["kwargs"], {"vol": 0.5, "at": "causeway"})
        self.assertEqual(ops[1]["args"], ["silence"])
        self.assertEqual(ops[2]["kwargs"], {"music": "verse_end", "max": 8})

    def test_unknown_cue(self) -> None:
        self.assert_error("@dance asha", "unknown cue '@dance'", 3)

    def test_unknown_key(self) -> None:
        self.assert_error("@camera H01 hold=true", "unknown key 'hold='", 3)

    def test_option_sets(self) -> None:
        self.assert_error("@vfx glimmer_held drift=up", "'up' is not one of down_seaward", 3)
        self.assert_error("@vfx sparkles", "set 'vfx_effects'", 3)
        self.assert_error("@camera H01 grade=ch99", "'ch99' is not one of", 3)
        self.assert_error("@mark asha path skip", "'skip' is not one of walk, run", 3)

    def test_arg_types_and_ranges(self) -> None:
        self.assert_error("@sfx toll vol=1.5", "above the maximum 1", 3)
        self.assert_error("@vfx glimmer_held count=1.5", "not an integer", 3)
        self.assert_error("@camera H01 blend=fast", "not a number", 3)
        self.assert_error("@face asha smug", "not an emotion", 3)
        self.assert_error('@music "two words"', "not an id", 3)
        self.assert_error("@anim asha", "takes actor clip [target]; got 1", 3)
        self.assert_error("@letterbox on off", "got 2", 3)

    def test_wait_needs_exactly_one_form(self) -> None:
        self.assert_error("@wait", "exactly one of: sec, music", 3)
        self.assert_error("@wait 1.0 music=m", "exactly one of: sec, music", 3)
        self.assert_error("@wait 1.0 max=3", "max= only works together with music", 3)

    def test_header_grade_is_checked(self) -> None:
        self.write("t_scene", "title: t_scene\ngrade: ch99\n---\nRhen: Hi. #line:t_001\n===\n")
        errors = dlgc.compile_project(self.tmp).errors
        self.assertTrue(any("t_scene.dlg:1: unknown grade 'ch99'" in e for e in errors), errors)

    def test_repo_cues_json_covers_its_sets(self) -> None:
        cues = json.loads((ROOT / "game/data/dialogue/cues.json").read_text(encoding="utf-8"))
        for name, spec in cues["cues"].items():
            for arg in spec.get("args", []) + list(spec.get("kwargs", {}).values()):
                self.assertIn(arg["type"], dlgc.ARG_TYPES, name)
                if "set" in arg:
                    self.assertIn(arg["set"], cues["sets"], name)


class VocabShapeTests(unittest.TestCase):
    """validate_data.dialogue_vocab_errors over cues.json / events.json."""

    def setUp(self) -> None:
        import validate_data
        self.check = validate_data.dialogue_vocab_errors
        base = ROOT / "game/data/dialogue"
        self.cues = json.loads((base / "cues.json").read_text(encoding="utf-8"))
        self.events = json.loads((base / "events.json").read_text(encoding="utf-8"))

    def test_repo_tables_are_clean(self) -> None:
        self.assertEqual(self.check(self.cues, self.events), [])

    def test_bad_shapes_are_reported(self) -> None:
        self.cues["cues"]["vfx"]["kwargs"]["drift"] = {"type": "enum", "set": "nope"}
        self.cues["cues"]["mark"]["args"].append({"name": "late", "type": "id"})
        self.cues["cues"]["wait"]["one_of"] = ["sec", "beat"]
        self.events["events"].append({"id": "zone_unlock", "doc": "dup", "args": []})
        errs = "\n".join(self.check(self.cues, self.events))
        for want in ("unknown set 'nope'", "a required arg after an optional one", "'beat' is not an arg",
                     "duplicate event 'zone_unlock'"):
            self.assertIn(want, errs)
        self.assertTrue(self.check({}, {}))


class EventTests(DlgcTestBase):
    def test_unknown_event(self) -> None:
        self.assert_error("<<event zone_unlok haluna>>", "unknown event 'zone_unlok'", 3)

    def test_event_args_are_checked(self) -> None:
        self.assert_error("<<event start_battle>>", "takes encounter; got 0", 3)
        self.assert_error("<<event start_battle 3>>", "encounter: 3 is not an id", 3)

    def test_test_only_event_only_in_test_dir(self) -> None:
        self.assert_error("<<event fixture_event a 1 true>>", "unknown event 'fixture_event'", 3)
        (self.tmp / "game/data/dialogue/ch99/t_scene.dlg").unlink()
        p = self.tmp / "game/data/dialogue/test/t_fix.dlg"
        p.parent.mkdir(parents=True)
        p.write_text("title: t_fix\n---\n<<event fixture_event a 1 true>>\n===\n", encoding="utf-8")
        self.assertEqual(dlgc.compile_project(self.tmp).errors, [])


class LongLineTests(DlgcTestBase):
    LONG = " ".join(["word"] * 26)

    def test_long_line_warns_but_compiles(self) -> None:
        self.scene(f"Rhen: {self.LONG}. #line:t_001\n-> {self.LONG} #line:t_002")
        res = dlgc.compile_project(self.tmp)
        self.assertEqual(res.errors, [])
        self.assertEqual(len(res.warnings), 2, res.warnings)
        self.assertTrue(res.warnings[0].startswith("game/data/dialogue/ch99/t_scene.dlg:3: 't_001' has 26 words"))
        dlgc.write(self.tmp)
        self.assertEqual(dlgc.check_report(self.tmp), ([], res.warnings))

    def test_25_words_and_long_tag_do_not_warn(self) -> None:
        words = " ".join(["word"] * 25)
        self.scene(f"Rhen: {words}. #line:t_001\nNarrator(rhen): {self.LONG} #line:t_002 #long")
        self.assertEqual(dlgc.compile_project(self.tmp).warnings, [])

    def test_count_words(self) -> None:
        self.assertEqual(dlgc.count_words("Don't look—it's the raft-town, 2 hulls."), 7)


class AssignIdsTests(DlgcTestBase):
    def assign(self, body: str, prefix: str | None = None) -> tuple[dlgc.AssignResult, Path]:
        p = self.write("t_scene", "title: t_scene\n---\n" + textwrap.dedent(body).strip("\n") + "\n===\n")
        return dlgc.assign_ids(self.tmp, p, prefix), p

    def test_fills_gaps_after_the_highest_number_without_renumbering(self) -> None:
        res, _ = self.assign("""
            Rhen: One. #line:t_beach_007
            Rhen: Two.
            -> Go. <<if $a>>   // a comment
                Asha [smile]: In. #whisper
            Rhen: Three. #line:t_beach_002
        """)
        self.assertEqual(res.errors, [])
        self.assertEqual(res.assigned, [(4, "t_beach_008"), (5, "t_beach_009"), (6, "t_beach_010")])
        self.assertEqual(res.text.splitlines()[2:7], [
            "Rhen: One. #line:t_beach_007",
            "Rhen: Two. #line:t_beach_008",
            "-> Go. <<if $a>> #line:t_beach_009   // a comment",
            "    Asha [smile]: In. #whisper #line:t_beach_010",
            "Rhen: Three. #line:t_beach_002",
        ])

    def test_output_compiles_and_a_second_run_assigns_nothing(self) -> None:
        res, p = self.assign("Rhen: One.\nRhen: Two. #line:t_x_001")
        p.write_text(res.text, encoding="utf-8")
        self.assertEqual(dlgc.compile_project(self.tmp).errors, [])
        again = dlgc.assign_ids(self.tmp, p)
        self.assertEqual((again.assigned, again.text), ([], res.text))

    def test_prefix_defaults_to_scene_name_and_can_be_given(self) -> None:
        res, _ = self.assign("Rhen: One.")
        self.assertEqual(res.assigned, [(3, "t_scene_001")])
        res, _ = self.assign("Rhen: One. #line:t_x_001\nRhen: Two.", prefix="ch99_new")
        self.assertEqual(res.assigned, [(4, "ch99_new_001")])
        res, _ = self.assign("Rhen: One.", prefix="Bad-Prefix")
        self.assertIsNone(res.text)

    def test_skips_ids_used_in_other_files_and_keeps_width(self) -> None:
        self.write("other", "title: other\n---\nRhen: Elsewhere. #line:t_x_0012\n===\n")
        res, _ = self.assign("Rhen: One. #line:t_x_0003\nRhen: Two.")
        self.assertEqual(res.assigned, [(4, "t_x_0013")])

    def test_other_errors_abort_without_text(self) -> None:
        res, p = self.assign("Nobody: One.")
        self.assertIsNone(res.text)
        self.assertTrue(any("unknown speaker" in e for e in res.errors), res.errors)
        self.assertNotIn("#line:", p.read_text(encoding="utf-8"))

    def test_cli_rewrites_in_place(self) -> None:
        p = self.write("t_scene", "title: t_scene\n---\nRhen: One.\n===\n")
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = dlgc.main(["--root", str(self.tmp), "--assign-ids", str(p)])
        self.assertEqual(code, 0)
        self.assertIn("Rhen: One. #line:t_scene_001\n", p.read_text(encoding="utf-8"))
        self.assertIn("1 id(s) assigned", out.getvalue())


if __name__ == "__main__":
    unittest.main()
