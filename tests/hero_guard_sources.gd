class_name HeroGuardSources
extends RefCounted
## Where the no-snapping guards (M2-HER-1110, ADR 0192) find what to check, read from the game's own data so a new
## zone or scene is covered the day it lands (no list in the tests to forget):
##   field_zones()  every chapter location's scene in game/data/world/locations.json (game/levels/ch*);
##   cutscenes()    scene path -> the in-engine scenes played there: the prologue (first_playable.json
##                  prologue.scene_id), Haluna's HalunaStory scenes (first_playable.json haluna.*_scene_id), and every
##                  "play" step in the chapter files (game/data/flow/chapters/*.json zones.<location>).

const LOCATIONS := "res://game/data/world/locations.json"
const FIRST_PLAYABLE := "res://game/data/flow/first_playable.json"
const CHAPTERS_DIR := "res://game/data/flow/chapters"
const LEVELS_PREFIX := "res://game/levels/ch"
const PROLOGUE_ID := "prologue"
const HALUNA_ID := "ch02/haluna"
const PLAY_KEY := "play"
const SCENE_ID_SUFFIX := "scene_id"


## Location id -> its scene path.
static func scenes_by_location() -> Dictionary:
	var out := {}
	for row: Variant in _json(LOCATIONS).get("locations", []):
		var r := row as Dictionary
		out[str(r.get("id", ""))] = str(r.get("scene", ""))
	return out


static func field_zones() -> Array[String]:
	var out: Array[String] = []
	for path: String in scenes_by_location().values():
		if path.begins_with(LEVELS_PREFIX) and not out.has(path) and ResourceLoader.exists(path):
			out.append(path)
	out.sort()
	return out


static func cutscenes() -> Dictionary:
	var by_loc := scenes_by_location()
	var out := {}
	var fp := _json(FIRST_PLAYABLE).get("first_playable", {}) as Dictionary
	_add(out, by_loc.get(PROLOGUE_ID, ""), str((fp.get("prologue", {}) as Dictionary).get(SCENE_ID_SUFFIX, "")))
	var haluna := fp.get("haluna", {}) as Dictionary
	for key: String in haluna:
		if key.ends_with(SCENE_ID_SUFFIX):
			_add(out, by_loc.get(HALUNA_ID, ""), str(haluna[key]))
	for file in DirAccess.get_files_at(CHAPTERS_DIR):
		if not file.ends_with(".json"):
			continue
		var zones := _json(CHAPTERS_DIR.path_join(file)).get("zones", {}) as Dictionary
		for loc: String in zones:
			var found: Array[String] = []
			_plays(zones[loc], found)
			for scene_id in found:
				_add(out, by_loc.get(loc, ""), scene_id)
	return out


static func _add(out: Dictionary, path: String, scene_id: String) -> void:
	if path == "" or scene_id == "" or not ResourceLoader.exists(path):
		return
	if not out.has(path):
		out[path] = [] as Array[String]
	if not (out[path] as Array[String]).has(scene_id):
		(out[path] as Array[String]).append(scene_id)


## Every value of a "play" key anywhere under `v`.
static func _plays(v: Variant, found: Array[String]) -> void:
	if v is Dictionary:
		for k: Variant in v:
			if str(k) == PLAY_KEY and v[k] is String:
				if not found.has(str(v[k])):
					found.append(str(v[k]))
			else:
				_plays(v[k], found)
	elif v is Array:
		for x: Variant in v:
			_plays(x, found)


static func _json(path: String) -> Dictionary:
	var f := FileAccess.open(path, FileAccess.READ)
	if f == null:
		return {}
	var parsed: Variant = JSON.parse_string(f.get_as_text())
	return parsed if parsed is Dictionary else {}
