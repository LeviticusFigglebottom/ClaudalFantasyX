class_name ObjectiveTracker
extends RefCounted
## The current objective (M2-UI-16), node-free: the rows of game/data/flow/objectives.json read
## against story flags. A row applies when every flag in `requires` is set and its `until` flag is
## not, and its `zone` (if any) is the zone asked about (a zoned row never applies in a scene with
## no map, so test zones and shot scenes show nothing). The main objective is the first main row
## that applies, in story order; side rows are optional errands. Flags come through `is_set`
## (Game.get_flag in play; tests pass their own), never by touching Game directly.
## The zones and their points of interest are game/data/ui/zone_maps.json (ZoneMaps).

const DATA_PATH := "res://game/data/flow/objectives.json"

var rows: Array[Dictionary] = []
## Zone id -> the loc key of its own line for when nothing calls (objectives.json idle_keys).
var idle_keys: Dictionary = {}
## Callable(flag: StringName) -> bool.
var is_set: Callable


func _init(flag_check: Callable = Callable(), path: String = DATA_PATH) -> void:
	is_set = flag_check if flag_check.is_valid() else func(f: StringName) -> bool: return bool(Game.get_flag(f))
	for r: Variant in load_rows(path):
		rows.append(r as Dictionary)
	var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(path))
	if typeof(parsed) == TYPE_DICTIONARY and typeof((parsed as Dictionary).get("objectives")) == TYPE_DICTIONARY:
		idle_keys = ((parsed as Dictionary)["objectives"] as Dictionary).get("idle_keys", {}) as Dictionary


static func load_rows(path: String = DATA_PATH) -> Array:
	var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(path))
	if typeof(parsed) != TYPE_DICTIONARY or typeof((parsed as Dictionary).get("objectives")) != TYPE_DICTIONARY:
		push_error("ObjectiveTracker: could not read 'objectives' from %s" % path)
		return []
	return ((parsed as Dictionary)["objectives"] as Dictionary).get("rows", []) as Array


## True when row `row` applies in zone `zone` (&"": a scene with no map; only unzoned rows).
func applies(row: Dictionary, zone: StringName) -> bool:
	var row_zone := StringName(str(row.get("zone", "")))
	if row_zone != &"" and row_zone != zone:
		return false  # a zoned row never applies elsewhere, nor in a scene with no map (&"")
	for f: Variant in row.get("requires", []):
		if not bool(is_set.call(StringName(str(f)))):
			return false
	var until := StringName(str(row.get("until", "")))
	return until == &"" or not bool(is_set.call(until))


## The main objective row for zone `zone`, or {} when nothing calls.
func current(zone: StringName) -> Dictionary:
	for row in rows:
		if not bool(row.get("side", false)) and applies(row, zone):
			return row
	return {}


## The side rows that apply in `zone`, in story order.
func side(zone: StringName) -> Array[Dictionary]:
	var out: Array[Dictionary] = []
	for row in rows:
		if bool(row.get("side", false)) and applies(row, zone):
			out.append(row)
	return out


## The current objective's line in words; when nothing calls, the zone's own idle line (idle_keys), else
## OBJ_NONE.
func line(zone: StringName) -> String:
	var row := current(zone)
	var idle := str(idle_keys.get(String(zone), "OBJ_NONE"))
	return TranslationServer.translate(str(row.get("line_key", idle)))


## The current objective's target {zone, poi}, or {} when it has none.
func target(zone: StringName) -> Dictionary:
	return current(zone).get("target", {}) as Dictionary
