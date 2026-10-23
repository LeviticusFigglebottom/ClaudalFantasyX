class_name LocationRegistry
extends RefCounted
## The location registry (M1-ARC-06): game/data/world/locations.json read into lookups.
##   location id -> {scene (res:// path), spawn (marker under Spawns/), name_key}
##   shrine network id -> {location_id, spawn}
## plus default_location (where an unresolvable respawn goes) and new_game (where New Game
## starts). WorldReturn, ShrineNetwork and the title screen use it; tools/validate_data.py
## checks the file (check_locations). Tests build one from a dictionary with from_dict().

const DATA_PATH := "res://game/data/world/locations.json"
const KEY_LOCATION := "location_id"
const KEY_SPAWN := "spawn"
const KEY_SCENE := "scene"

var default_location: StringName = &""
var new_game_location: StringName = &""
var new_game_spawn: StringName = &""
var _locations: Dictionary = {}
var _shrines: Dictionary = {}


static func load_default() -> LocationRegistry:
	var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(DATA_PATH))
	if typeof(parsed) != TYPE_DICTIONARY:
		push_error("LocationRegistry: could not read %s" % DATA_PATH)
		return LocationRegistry.new()
	return from_dict(parsed as Dictionary)


static func from_dict(d: Dictionary) -> LocationRegistry:
	var r := LocationRegistry.new()
	r.default_location = StringName(str(d.get("default_location", "")))
	var ng: Variant = d.get("new_game", {})
	if typeof(ng) == TYPE_DICTIONARY:
		r.new_game_location = StringName(str((ng as Dictionary).get(KEY_LOCATION, "")))
		r.new_game_spawn = StringName(str((ng as Dictionary).get(KEY_SPAWN, "")))
	for row: Variant in d.get("locations", []):
		if typeof(row) == TYPE_DICTIONARY and (row as Dictionary).has("id"):
			r._locations[StringName(str(row["id"]))] = (row as Dictionary).duplicate(true)
	for row: Variant in d.get("shrines", []):
		if typeof(row) == TYPE_DICTIONARY and (row as Dictionary).has("id"):
			r._shrines[StringName(str(row["id"]))] = (row as Dictionary).duplicate(true)
	return r


func has_location(id: StringName) -> bool:
	return _locations.has(id)


func location_ids() -> Array[StringName]:
	var out: Array[StringName] = []
	for k: StringName in _locations:
		out.append(k)
	out.sort_custom(func(a: StringName, b: StringName) -> bool: return String(a) < String(b))
	return out


func scene_of(id: StringName) -> String:
	return str((_locations.get(id, {}) as Dictionary).get(KEY_SCENE, ""))


## The location's own spawn marker name (used when a respawn names none).
func spawn_of(id: StringName) -> StringName:
	return StringName(str((_locations.get(id, {}) as Dictionary).get(KEY_SPAWN, "")))


func name_key_of(id: StringName) -> String:
	return str((_locations.get(id, {}) as Dictionary).get("name_key", ""))


func has_shrine(network_id: StringName) -> bool:
	return _shrines.has(network_id)


## {location_id, spawn} for a shrine network id, or {} when the registry does not list it.
## An empty spawn on the row falls back to the location's own spawn.
func shrine_point(network_id: StringName) -> Dictionary:
	if not _shrines.has(network_id):
		return {}
	var row: Dictionary = _shrines[network_id]
	var loc := StringName(str(row.get(KEY_LOCATION, "")))
	var spawn := StringName(str(row.get(KEY_SPAWN, "")))
	return {KEY_LOCATION: loc, KEY_SPAWN: spawn if spawn != &"" else spawn_of(loc)}


## Where to put the party for (location_id, spawn): {location_id, scene, spawn, fallback}.
## An unknown or empty location falls back to default_location (fallback = true); an empty spawn
## becomes the location's own spawn. Returns {} when not even the default resolves.
func resolve(location_id: StringName, spawn: StringName = &"") -> Dictionary:
	var loc := location_id
	var fallback := false
	if not has_location(loc):
		loc = default_location
		fallback = true
		spawn = &""
	if not has_location(loc):
		return {}
	return {
		KEY_LOCATION: loc,
		KEY_SCENE: scene_of(loc),
		KEY_SPAWN: spawn if spawn != &"" else spawn_of(loc),
		"fallback": fallback,
	}
