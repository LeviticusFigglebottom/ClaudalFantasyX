class_name ChapterRegistry
extends RefCounted
## Act I chapter data (M3-ARC-01; docs/kb/tech/chapter_flow.md). game/data/flow/chapters.json lists
## the chapter files; each file has a "zones" block keyed by location id, which ZoneStory plays.

const DATA_PATH := "res://game/data/flow/chapters.json"
const ROOT_KEY := "chapters"
const KEY_FILES := "files"
const KEY_ZONES := "zones"


## The chapter files listed in chapters.json.
static func files() -> PackedStringArray:
	var out := PackedStringArray()
	var root: Dictionary = GreyboxZone.read_json(DATA_PATH).get(ROOT_KEY, {}) as Dictionary
	for f: Variant in root.get(KEY_FILES, []):
		out.append(str(f))
	return out


## The story block for `location_id`: from `chapter_path` when given, else from the first listed
## chapter file that has it. {} when none does.
static func zone(location_id: StringName, chapter_path: String = "") -> Dictionary:
	var paths := PackedStringArray([chapter_path]) if chapter_path != "" else files()
	for p in paths:
		var zones: Dictionary = GreyboxZone.read_json(p).get(KEY_ZONES, {})
		if zones.has(String(location_id)):
			return zones[String(location_id)]
	return {}
