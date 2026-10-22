class_name DialogueSpeakers
extends RefCounted
## Speaker table (game/data/dialogue/speakers.json): id -> name_key, blip_pitch, portrait_id.

const DATA_PATH := "res://game/data/dialogue/speakers.json"
## Pitch scale for unknown speakers and narration: the blip as recorded.
const UNPITCHED := 1.0

var rows: Dictionary = {}


static func load_default() -> DialogueSpeakers:
	var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(DATA_PATH))
	if typeof(parsed) != TYPE_DICTIONARY:
		push_error("DialogueSpeakers: could not parse %s" % DATA_PATH)
		return DialogueSpeakers.new()
	return from_rows((parsed as Dictionary).get("speakers", []))


static func from_rows(table: Array) -> DialogueSpeakers:
	var s := DialogueSpeakers.new()
	for row: Variant in table:
		if row is Dictionary and (row as Dictionary).has("id"):
			s.rows[StringName(str(row["id"]))] = row
	return s


func has(speaker: StringName) -> bool:
	return rows.has(speaker)


func name_key(speaker: StringName) -> StringName:
	return StringName(str((rows.get(speaker, {}) as Dictionary).get("name_key", "")))


func blip_pitch(speaker: StringName) -> float:
	return float((rows.get(speaker, {}) as Dictionary).get("blip_pitch", UNPITCHED))


func portrait_id(speaker: StringName) -> StringName:
	return StringName(str((rows.get(speaker, {}) as Dictionary).get("portrait_id", "")))
