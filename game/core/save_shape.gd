class_name SaveShape
extends RefCounted
## Deep shape check of a migrated save "state" (M1-ARC-08). SaveSystem runs it before
## GameStateData.from_dict on every load and listing: a save that fails it reads as corrupt, so
## no wrongly typed value reaches the live state, LatticeProgress, EquipmentBag or battle setup.
##
## problem(state) returns "" for a well-formed state, otherwise a short path to the first bad
## value ("party_ids[1]: expected a String"), for logs and tests. Every key is optional (older
## saves and migrations fill gaps), but a key that is present must have the right shape:
##   flags            {String: bool | number | String}       (flags are scalars, flags.tres)
##   party_ids, reserve_ids, attuned_shrines                  [String]
##   inventory        {String: whole number >= 0}
##   currency         whole number >= 0
##   chapter          whole number >= 0
##   play_time_sec    finite number >= 0
##   location_id      String
##   lattice          {board: String, opened_gates: [String],
##                     characters: {String: {position: String, activated: [String],
##                                           movement_points, lattice_points, movement_earned:
##                                           whole numbers >= 0}}}
##   equipment        {next_uid: whole number >= 1,
##                     owned: {"<whole number>": {base: String, abilities: [String]}},
##                     loadout: {String: {String: whole number >= 0}}}
##   party_vitals     {String: {hp, mp: whole numbers >= 0, statuses: [String]}}
##   respawn          {location_id: String, spawn: String}
## JSON loads every number as a float, so "whole number" means an int, or a finite float with no
## fractional part.

const OK_SHAPE := ""


static func is_ok(st: Variant) -> bool:
	return problem(st) == OK_SHAPE


static func problem(st: Variant) -> String:
	if typeof(st) != TYPE_DICTIONARY:
		return "state: expected a Dictionary"
	var d := st as Dictionary
	var checks: Array[String] = [
		_opt(d, "flags", _flags),
		_opt(d, "party_ids", _string_array),
		_opt(d, "reserve_ids", _string_array),
		_opt(d, "attuned_shrines", _string_array),
		_opt(d, "inventory", _inventory),
		_opt(d, "currency", _count),
		_opt(d, "chapter", _count),
		_opt(d, "play_time_sec", _duration),
		_opt(d, "location_id", _string),
		_opt(d, "lattice", _lattice),
		_opt(d, "equipment", _equipment),
		_opt(d, "party_vitals", _vitals),
		_opt(d, "respawn", _respawn),
	]
	for c in checks:
		if c != OK_SHAPE:
			return c
	return OK_SHAPE


## A whole number: an int, or a finite float without a fractional part (JSON numbers).
static func is_whole(v: Variant) -> bool:
	if typeof(v) == TYPE_INT:
		return true
	if typeof(v) != TYPE_FLOAT:
		return false
	var f := float(v)
	return is_finite(f) and f == floorf(f)


# --- Checkers: each takes (value, path) and returns "" or the problem ----------------------------


static func _opt(d: Dictionary, key: String, check: Callable) -> String:
	if not d.has(key):
		return OK_SHAPE
	return check.call(d[key], key)


static func _string(v: Variant, path: String) -> String:
	return OK_SHAPE if typeof(v) == TYPE_STRING else "%s: expected a String" % path


static func _count(v: Variant, path: String) -> String:
	if not is_whole(v) or float(v) < 0.0:
		return "%s: expected a whole number >= 0" % path
	return OK_SHAPE


static func _uid(v: Variant, path: String) -> String:
	if not is_whole(v) or float(v) < 1.0:
		return "%s: expected a whole number >= 1" % path
	return OK_SHAPE


static func _duration(v: Variant, path: String) -> String:
	var numeric := typeof(v) == TYPE_INT or typeof(v) == TYPE_FLOAT
	if not numeric or not is_finite(float(v)) or float(v) < 0.0:
		return "%s: expected a finite number >= 0" % path
	return OK_SHAPE


static func _string_array(v: Variant, path: String) -> String:
	if typeof(v) != TYPE_ARRAY:
		return "%s: expected an Array" % path
	var a := v as Array
	for i in a.size():
		if typeof(a[i]) != TYPE_STRING:
			return "%s[%d]: expected a String" % [path, i]
	return OK_SHAPE


## A Dictionary whose keys are Strings and whose values all pass `value_check`.
static func _map_of(v: Variant, path: String, value_check: Callable) -> String:
	if typeof(v) != TYPE_DICTIONARY:
		return "%s: expected a Dictionary" % path
	var d := v as Dictionary
	for k: Variant in d:
		if typeof(k) != TYPE_STRING:
			return "%s: expected String keys" % path
		var p: String = value_check.call(d[k], "%s.%s" % [path, k])
		if p != OK_SHAPE:
			return p
	return OK_SHAPE


## A Dictionary whose listed keys, when present, pass their checks. Other keys are ignored.
static func _record(v: Variant, path: String, fields: Dictionary) -> String:
	if typeof(v) != TYPE_DICTIONARY:
		return "%s: expected a Dictionary" % path
	var d := v as Dictionary
	for key: String in fields:
		if d.has(key):
			var p: String = (fields[key] as Callable).call(d[key], "%s.%s" % [path, key])
			if p != OK_SHAPE:
				return p
	return OK_SHAPE


static func _flag_value(v: Variant, path: String) -> String:
	match typeof(v):
		TYPE_BOOL, TYPE_INT, TYPE_FLOAT, TYPE_STRING:
			return OK_SHAPE
	return "%s: expected a bool, number or String" % path


static func _flags(v: Variant, path: String) -> String:
	return _map_of(v, path, _flag_value)


static func _inventory(v: Variant, path: String) -> String:
	return _map_of(v, path, _count)


static func _traveler(v: Variant, path: String) -> String:
	return _record(
		v,
		path,
		{
			"position": _string,
			"activated": _string_array,
			"movement_points": _count,
			"lattice_points": _count,
			"movement_earned": _count,
		}
	)


static func _travelers(v: Variant, path: String) -> String:
	return _map_of(v, path, _traveler)


static func _lattice(v: Variant, path: String) -> String:
	return _record(v, path, {"board": _string, "opened_gates": _string_array, "characters": _travelers})


static func _piece(v: Variant, path: String) -> String:
	return _record(v, path, {"base": _string, "abilities": _string_array})


static func _owned(v: Variant, path: String) -> String:
	var p := _map_of(v, path, _piece)
	if p != OK_SHAPE:
		return p
	for k: Variant in v as Dictionary:
		if not String(k).is_valid_int() or int(String(k)) < 1:
			return "%s: key '%s' is not a piece uid" % [path, k]
	return OK_SHAPE


static func _slots(v: Variant, path: String) -> String:
	return _map_of(v, path, _count)


static func _loadout(v: Variant, path: String) -> String:
	return _map_of(v, path, _slots)


static func _equipment(v: Variant, path: String) -> String:
	return _record(v, path, {"next_uid": _uid, "owned": _owned, "loadout": _loadout})


static func _vital(v: Variant, path: String) -> String:
	return _record(v, path, {"hp": _count, "mp": _count, "statuses": _string_array})


static func _vitals(v: Variant, path: String) -> String:
	return _map_of(v, path, _vital)


static func _respawn(v: Variant, path: String) -> String:
	return _record(v, path, {"location_id": _string, "spawn": _string})
