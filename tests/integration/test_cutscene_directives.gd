extends TestCase
## M2-FP-120 (the Lead's 10-29 item: ui-menus' sweep found cutscene directives parsed but never performed): every
## directive and argument the Act I scenes (the prologue and Ch1-Ch9) use is one the sequencer performs.
## - No cue uses a key the sequencer lists as unsupported (CutsceneSequencer.UNSUPPORTED_KWARGS).
## - Every key cues.json allows is read by the cutscene code (a new key with no code behind it fails here).
## - Every grade (a node's `grade:` header, `@camera grade=`) has a row in the zones' grade tables (CutsceneGrade),
##   bar the ones cutscene_directives_known.json lists as waiting on Rendering.
## - Every `@vfx form=` has a form in glimmer_forms.json.

const COMPILED_DIR := "res://game/data/dialogue/compiled"
const ACT1_DIRS: Array[String] = [
	"game/data/dialogue/prologue/",
	"game/data/dialogue/ch01/",
	"game/data/dialogue/ch02/",
	"game/data/dialogue/ch03/",
	"game/data/dialogue/ch04/",
	"game/data/dialogue/ch05/",
	"game/data/dialogue/ch06/",
	"game/data/dialogue/ch07/",
	"game/data/dialogue/ch08/",
	"game/data/dialogue/ch09/",
]
const CUES_PATH := "res://game/data/dialogue/cues.json"
const KNOWN_PATH := "res://tests/integration/cutscene_directives_known.json"
## Where the code that performs a cue's keys lives.
const CODE_DIRS: Array[String] = ["res://game/cutscene", "res://game/vfx/glimmer"]
const FORMS_PATH := "res://game/data/cutscene/glimmer_forms.json"


func test_act1_scenes_use_only_performed_directives() -> void:
	var grades: Dictionary = {}  # grade id -> first "scene:node" that names it
	var forms: Dictionary = {}
	var scenes := 0
	for f in DirAccess.get_files_at(COMPILED_DIR):
		var data: Dictionary = GreyboxZone.read_json("%s/%s" % [COMPILED_DIR, f])
		if not _act1(str(data.get("source", ""))):
			continue
		scenes += 1
		var nodes: Dictionary = data.get("nodes", {})
		for node: String in nodes:
			var where := "%s:%s" % [data.get("scene", f), node]
			var header := str((nodes[node] as Dictionary).get("headers", {}).get("grade", ""))
			if header != "" and not grades.has(header):
				grades[header] = where
			for op: Dictionary in (nodes[node] as Dictionary).get("ops", []):
				if str(op.get("op", "")) != "cue":
					continue
				var cue := StringName(str(op["cue"]))
				var kwargs: Dictionary = op.get("kwargs", {})
				for k: String in kwargs:
					var unsupported: Array = CutsceneSequencer.UNSUPPORTED_KWARGS.get(cue, [])
					assert_false(unsupported.has(k), "%s: @%s %s= is not performed" % [where, cue, k])
				if cue == &"camera" and kwargs.has("grade") and not grades.has(str(kwargs["grade"])):
					grades[str(kwargs["grade"])] = where
				if cue == &"vfx" and kwargs.has("form"):
					forms[str(kwargs["form"])] = where
	assert_true(scenes > 100, "found the Act I scenes (%d)" % scenes)
	var known: Array = GreyboxZone.read_json(KNOWN_PATH).get("grades", [])
	for id: String in grades:
		if not CutsceneGrade.has_grade(StringName(id)):
			assert_true(known.has(id), "%s: grade '%s' has no row in a zone grade table" % [grades[id], id])
	for id: String in known:
		assert_false(
			CutsceneGrade.has_grade(StringName(id)), "grade '%s' has a row now: take it off %s" % [id, KNOWN_PATH]
		)
		assert_true(grades.has(id), "no Act I scene names grade '%s' any more: take it off %s" % [id, KNOWN_PATH])
	var form_rows: Dictionary = GreyboxZone.read_json(FORMS_PATH).get("forms", {})
	for id: String in forms:
		assert_true(form_rows.has(id), "%s: @vfx form=%s has no form in glimmer_forms.json" % [forms[id], id])


func test_every_cue_key_has_code_behind_it() -> void:
	var code := ""
	for dir in CODE_DIRS:
		for f in DirAccess.get_files_at(dir):
			if f.ends_with(".gd"):
				code += FileAccess.get_file_as_string("%s/%s" % [dir, f])
	var cues: Dictionary = GreyboxZone.read_json(CUES_PATH).get("cues", {})
	for cue: String in cues:
		var unsupported: Array = CutsceneSequencer.UNSUPPORTED_KWARGS.get(StringName(cue), [])
		for k: String in (cues[cue] as Dictionary).get("kwargs", {}):
			if unsupported.has(k):
				continue
			assert_true(code.contains('"%s"' % k), "@%s %s= is in cues.json but no cutscene code reads it" % [cue, k])


func _act1(source: String) -> bool:
	for d in ACT1_DIRS:
		if source.begins_with(d):
			return true
	return false
