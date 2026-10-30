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
const KEY_PLAYABLE := "playable"
const KEY_ORDER := "order"
## resolve()'s "reason" when it falls back: the id is empty, not listed, or not playable.
const REASON_EMPTY := &"empty"
const REASON_UNKNOWN := &"unknown"
const REASON_NOT_PLAYABLE := &"not_playable"

var default_location: StringName = &""
var new_game_location: StringName = &""
var new_game_spawn: StringName = &""
## Why the file could not be read ("" when it was); the registry is then empty (M1-ARC-13).
var load_error: String = ""
var _locations: Dictionary = {}
var _shrines: Dictionary = {}


static func load_default() -> LocationRegistry:
	return load_path(DATA_PATH)


## Reads a locations file. A missing or unparseable one gives an empty registry that says why in
## load_error, with a push_error. Tests point it at a broken file.
static func load_path(path: String) -> LocationRegistry:
	var parsed: Variant = null
	if FileAccess.file_exists(path):
		parsed = JSON.parse_string(FileAccess.get_file_as_string(path))
	if typeof(parsed) != TYPE_DICTIONARY:
		push_error("LocationRegistry: could not read %s" % path)
		var empty := LocationRegistry.new()
		empty.load_error = "%s is missing or could not be parsed" % path
		return empty
	return from_dict(parsed as Dictionary)


## Why this registry must not judge a saved location ("" when it can): the file was missing or
## failed to parse, it lists no locations, or its default_location is not listed. A save made
## meanwhile could record a stand-in place, so SaveSystem's data-tables gate refuses to save
## while this is non-empty (M1-ARC-13).
func integrity_problem() -> String:
	if load_error != "":
		return load_error
	if _locations.is_empty() or not has_location(default_location):
		return "the location registry lists no locations, or not its default_location"
	return ""


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


## False for a location row marked `"playable": false`: its scene stages the place (a mood or
## art stand-in) but has no player to put there (M1-ARC-11, after review-sweep-G on M1-ENV-04).
## The validator requires the mark on every location whose scene has no player.
func is_playable(id: StringName) -> bool:
	return has_location(id) and bool((_locations[id] as Dictionary).get(KEY_PLAYABLE, true))


## True when the party can be sent to `id`: it is listed and playable.
func can_enter(id: StringName) -> bool:
	return is_playable(id)


func scene_of(id: StringName) -> String:
	return str((_locations.get(id, {}) as Dictionary).get(KEY_SCENE, ""))


## The location's own spawn marker name (used when a respawn names none).
func spawn_of(id: StringName) -> StringName:
	return StringName(str((_locations.get(id, {}) as Dictionary).get(KEY_SPAWN, "")))


func name_key_of(id: StringName) -> String:
	return str((_locations.get(id, {}) as Dictionary).get("name_key", ""))


func has_shrine(network_id: StringName) -> bool:
	return _shrines.has(network_id)


## True for a shrine row marked "order": true (one of the Order's; dark once the party are heretics, ShrineNetwork).
func shrine_is_order(network_id: StringName) -> bool:
	return bool((_shrines.get(network_id, {}) as Dictionary).get(KEY_ORDER, false))


## {location_id, spawn} for a shrine network id, or {} when the registry does not list it.
## An empty spawn on the row falls back to the location's own spawn.
func shrine_point(network_id: StringName) -> Dictionary:
	if not _shrines.has(network_id):
		return {}
	var row: Dictionary = _shrines[network_id]
	var loc := StringName(str(row.get(KEY_LOCATION, "")))
	var spawn := StringName(str(row.get(KEY_SPAWN, "")))
	return {KEY_LOCATION: loc, KEY_SPAWN: spawn if spawn != &"" else spawn_of(loc)}


## Where to put the party for (location_id, spawn): {location_id, scene, spawn, fallback, reason}.
## An empty, unknown or not playable location falls back to default_location (fallback = true,
## reason REASON_*; &"" when it resolved as asked); an empty spawn becomes the location's own
## spawn. Returns {} when not even the default resolves.
func resolve(location_id: StringName, spawn: StringName = &"") -> Dictionary:
	var loc := location_id
	var reason: StringName = &""
	if not can_enter(loc):
		if loc == &"":
			reason = REASON_EMPTY
		elif has_location(loc):
			reason = REASON_NOT_PLAYABLE
		else:
			reason = REASON_UNKNOWN
		loc = default_location
		spawn = &""
	if not has_location(loc):
		return {}
	return {
		KEY_LOCATION: loc,
		KEY_SCENE: scene_of(loc),
		KEY_SPAWN: spawn if spawn != &"" else spawn_of(loc),
		"fallback": reason != &"",
		"reason": reason,
	}
