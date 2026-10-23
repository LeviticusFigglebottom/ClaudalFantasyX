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
##   party_vitals     {String: {hp, mp: whole numbers >= 0, statuses: [String],
##                              swell: whole number >= 0, swell_mode: String}}   (swell: v6)
##   respawn          {location_id: String, spawn: String}
##   bestiary         {String: {read: bool, defeated: whole number >= 0}}   (v5, M1-CMB-03)
##   swell            {unlocked: [String], progress: {String: whole number >= 0}}   (v6, M2-ARC-01)
## JSON loads every number as a float, so "whole number" means an int, or a finite float with no
## fractional part, and at most MAX_WHOLE in size: above 2^53 a float no longer holds every whole
## number, and int() of a float past the int64 range wraps to a negative number (QA review-sweep-E
## S1: `currency: 1e300` loaded as -9223372036854775808). Game caps (currency_cap, stack_cap) are
## applied by the domain objects; this bound only keeps int() honest.
## Equipment is also checked as a whole (review-sweep-E S2), because EquipmentBag trusts it:
## every owned key is a canonical uid ("5", never "05" or "+5", which str(uid) lookups never
## reach), next_uid is present and greater than every owned uid (add_piece would otherwise
## overwrite a piece), and every loadout uid is NO_PIECE (0) or an owned piece, worn in one
## loadout slot at most (M1-ARC-11). Whether a piece fits its wearer and slot needs the item
## tables, which a later build may change, so it is never a shape problem: SaveSystem repairs a
## misfit after loading (EquipmentBag.repair_loadout; review-sweep-G B1).

const OK_SHAPE := ""
## The largest whole number a save may hold: 2^53, the last float that every smaller whole number
## also fits in exactly.
const MAX_WHOLE := 9007199254740992
## EquipmentBag.NO_PIECE: an empty loadout slot.
const NO_PIECE := 0


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
		_opt(d, "bestiary", _bestiary),
		_opt(d, "swell", _swell),
	]
	for c in checks:
		if c != OK_SHAPE:
			return c
	return OK_SHAPE


## A whole number: an int, or a finite float without a fractional part (JSON numbers), no larger
## than MAX_WHOLE either way, so int() of it is exact.
static func is_whole(v: Variant) -> bool:
	if typeof(v) == TYPE_INT:
		return absi(int(v)) <= MAX_WHOLE
	if typeof(v) != TYPE_FLOAT:
		return false
	var f := float(v)
	return is_finite(f) and f == floorf(f) and absf(f) <= float(MAX_WHOLE)


# --- Checkers: each takes (value, path) and returns "" or the problem ----------------------------


static func _opt(d: Dictionary, key: String, check: Callable) -> String:
	if not d.has(key):
		return OK_SHAPE
	return check.call(d[key], key)


static func _string(v: Variant, path: String) -> String:
	return OK_SHAPE if typeof(v) == TYPE_STRING else "%s: expected a String" % path


static func _count(v: Variant, path: String) -> String:
	if not is_whole(v) or float(v) < 0.0:
		return "%s: expected a whole number in 0..%d" % [path, MAX_WHOLE]
	return OK_SHAPE


static func _uid(v: Variant, path: String) -> String:
	if not is_whole(v) or float(v) < 1.0:
		return "%s: expected a whole number in 1..%d" % [path, MAX_WHOLE]
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
		var key := String(k)
		if not key.is_valid_int() or _uid(int(key), path) != OK_SHAPE or str(int(key)) != key:
			return "%s: key '%s' is not a piece uid (a whole number >= 1, written plainly)" % [path, k]
	return OK_SHAPE


static func _slots(v: Variant, path: String) -> String:
	return _map_of(v, path, _count)


static func _loadout(v: Variant, path: String) -> String:
	return _map_of(v, path, _slots)


static func _equipment(v: Variant, path: String) -> String:
	var p := _record(v, path, {"next_uid": _uid, "owned": _owned, "loadout": _loadout})
	if p != OK_SHAPE:
		return p
	var d := v as Dictionary
	var owned := d.get("owned", {}) as Dictionary
	var top := 0
	for k: Variant in owned:
		top = maxi(top, int(String(k)))
	if top > 0 and (not d.has("next_uid") or int(d["next_uid"]) <= top):
		return "%s.next_uid: expected a whole number > %d (the highest owned uid)" % [path, top]
	var loadout := d.get("loadout", {}) as Dictionary
	var worn: Dictionary = {}
	for cid: Variant in loadout:
		var slots := loadout[cid] as Dictionary
		for slot: Variant in slots:
			var uid := int(slots[slot])
			if uid == NO_PIECE:
				continue
			if not owned.has(str(uid)):
				return "%s.loadout.%s.%s: piece %d is not owned" % [path, cid, slot, uid]
			if worn.has(uid):
				return "%s.loadout.%s.%s: piece %d is already worn at %s" % [path, cid, slot, uid, worn[uid]]
			worn[uid] = "%s.%s" % [cid, slot]
	return OK_SHAPE


static func _vital(v: Variant, path: String) -> String:
	return _record(
		v, path, {"hp": _count, "mp": _count, "statuses": _string_array, "swell": _count, "swell_mode": _string}
	)


static func _vitals(v: Variant, path: String) -> String:
	return _map_of(v, path, _vital)


static func _respawn(v: Variant, path: String) -> String:
	return _record(v, path, {"location_id": _string, "spawn": _string})


static func _bool(v: Variant, path: String) -> String:
	return OK_SHAPE if typeof(v) == TYPE_BOOL else "%s: expected true or false" % path


static func _beast(v: Variant, path: String) -> String:
	return _record(v, path, {"read": _bool, "defeated": _count})


static func _bestiary(v: Variant, path: String) -> String:
	return _map_of(v, path, _beast)


static func _counts(v: Variant, path: String) -> String:
	return _map_of(v, path, _count)


static func _swell(v: Variant, path: String) -> String:
	return _record(v, path, {"unlocked": _string_array, "progress": _counts})
