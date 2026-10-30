class_name FirstPlayableConfig
extends RefCounted
## Reads game/data/flow/first_playable.json (M2-FP-03): the field battle defaults, the prologue
## hand-off and the end card timings. See docs/kb/tech/first_playable_flow.md.

const DATA_PATH := "res://game/data/flow/first_playable.json"
const ROOT_KEY := "first_playable"
const SECTION_FIELD_BATTLE := &"field_battle"
const SECTION_PROLOGUE := &"prologue"
const SECTION_END_CARD := &"end_card"
const SECTION_HALUNA := &"haluna"
const SECTION_FIRST_VERSE := &"first_verse"
const SECTION_SHELL_SHRINE := &"shell_shrine"
const SECTION_PARTY := &"party"
const SECTION_CHAPTER_CARD := &"chapter_card"


## One block of the file ({} with an error when the file or the block is missing).
static func section(name: StringName) -> Dictionary:
	var parsed: Variant = null
	if FileAccess.file_exists(DATA_PATH):
		parsed = JSON.parse_string(FileAccess.get_file_as_string(DATA_PATH))
	if typeof(parsed) != TYPE_DICTIONARY or typeof((parsed as Dictionary).get(ROOT_KEY)) != TYPE_DICTIONARY:
		push_error("FirstPlayableConfig: could not read '%s' from %s" % [ROOT_KEY, DATA_PATH])
		return {}
	var block: Variant = ((parsed as Dictionary)[ROOT_KEY] as Dictionary).get(String(name))
	if typeof(block) != TYPE_DICTIONARY:
		push_error("FirstPlayableConfig: no '%s' block in %s" % [name, DATA_PATH])
		return {}
	return block as Dictionary


## A JSON list as typed ids.
static func ids(raw: Variant) -> Array[StringName]:
	var out: Array[StringName] = []
	if typeof(raw) == TYPE_ARRAY:
		for v: Variant in raw as Array:
			out.append(StringName(str(v)))
	return out
