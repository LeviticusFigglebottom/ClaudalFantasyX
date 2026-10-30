class_name ChapterRegistry
extends RefCounted
## Act I chapter data (M3-ARC-01; docs/kb/tech/chapter_flow.md). game/data/flow/chapters.json lists
## the chapter files; each file has a "zones" block keyed by location id, which ZoneStory plays.

const DATA_PATH := "res://game/data/flow/chapters.json"
const ROOT_KEY := "chapters"
const KEY_FILES := "files"
const KEY_ZONES := "zones"
const KEY_CHAPTER := "chapter"


## The chapter files listed in chapters.json.
static func files() -> PackedStringArray:
	var out := PackedStringArray()
	var root: Dictionary = GreyboxZone.read_json(DATA_PATH).get(ROOT_KEY, {}) as Dictionary
	for f: Variant in root.get(KEY_FILES, []):
		out.append(str(f))
	return out


## The story block for `location_id`: from `chapter_path` when given; else, of the listed chapter files (in
## story order) that have the zone, the first whose chapter is the story's current `chapter` or later, else the
## first. Act III comes back to earlier zones (Ch17's Hollowmere is Ch15's; Ch18 revisits Act I; M5-A3P-1001),
## and a zone reached on the way out of one chapter (still chapter 16 at Hollowmere) belongs to the next. With
## every zone in one file this is the first file that has it. {} when none does.
static func zone(location_id: StringName, chapter_path: String = "", chapter: int = 0) -> Dictionary:
	if chapter_path != "":
		return zone_in(PackedStringArray([chapter_path]), location_id)
	return zone_in(files(), location_id, chapter)


## zone() over the given chapter files, in order. A file's "chapter" key ("ch17") names its chapter.
static func zone_in(paths: PackedStringArray, location_id: StringName, chapter: int = 0) -> Dictionary:
	var first := {}
	for p in paths:
		var data: Dictionary = GreyboxZone.read_json(p)
		var zones: Dictionary = data.get(KEY_ZONES, {})
		if not zones.has(String(location_id)):
			continue
		if chapter_number(str(data.get(KEY_CHAPTER, ""))) >= chapter:
			return zones[String(location_id)]
		if first.is_empty():
			first = zones[String(location_id)]
	return first


## "ch17" -> 17; 0 for anything else.
static func chapter_number(key: String) -> int:
	return key.trim_prefix("ch").to_int() if key.begins_with("ch") and key.trim_prefix("ch").is_valid_int() else 0
