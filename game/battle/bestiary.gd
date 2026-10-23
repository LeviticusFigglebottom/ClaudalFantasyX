class_name Bestiary
extends RefCounted
## The bestiary log (SPEC §6.1, §6.11; M1-CMB-03): which foes the party has Read and how many of
## each it has defeated. It wraps GameStateData.bestiary in place, as EquipmentBag wraps the
## equipment, so a write is in the next save. Node-free.
##
## Saved shape (save v5, SaveShape checks it): {"<enemy id>": {"read": bool, "defeated": whole}}.
## Only the facts are saved; what an entry shows (stats, weaknesses, lore) comes from enemies.json
## at display time, so a rebalance never leaves a stale page. An entry is created by the first
## Read or defeat. An id enemies.json no longer lists is kept as saved, never pruned.

const KEY_READ := "read"
const KEY_DEFEATED := "defeated"

## The live dictionary this log writes into (GameStateData.bestiary, or a scratch one).
var entries: Dictionary


func _init(backing: Dictionary = {}) -> void:
	entries = backing


## Logs a Read of `enemy_id`. True when it was not Read before. An empty id logs nothing.
func record_read(enemy_id: StringName) -> bool:
	if enemy_id == &"" or is_read(enemy_id):
		return false
	_entry(enemy_id)[KEY_READ] = true
	return true


## Adds `count` defeats of `enemy_id` (count <= 0 or an empty id logs nothing).
func record_defeated(enemy_id: StringName, count: int = 1) -> void:
	if enemy_id == &"" or count <= 0:
		return
	var e := _entry(enemy_id)
	e[KEY_DEFEATED] = defeated(enemy_id) + count


func is_read(enemy_id: StringName) -> bool:
	return bool(entry(enemy_id).get(KEY_READ, false))


func defeated(enemy_id: StringName) -> int:
	return int(entry(enemy_id).get(KEY_DEFEATED, 0))


## A copy of the entry for `enemy_id` ({} when it has none).
func entry(enemy_id: StringName) -> Dictionary:
	var e: Variant = entries.get(String(enemy_id), {})
	return (e as Dictionary).duplicate() if typeof(e) == TYPE_DICTIONARY else {}


## Every logged enemy id, sorted.
func known_ids() -> Array[StringName]:
	var out: Array[StringName] = []
	for k: Variant in entries:
		out.append(StringName(str(k)))
	out.sort_custom(func(a: StringName, b: StringName) -> bool: return String(a) < String(b))
	return out


## The saved bestiary as live state: JSON's float counts become ints and every entry is copied.
## Called by GameStateData.from_dict after SaveShape has checked the save, so an entry that is
## not a Dictionary (only possible from code, not from a checked save) is skipped.
static func from_saved(raw: Variant) -> Dictionary:
	var out: Dictionary = {}
	if typeof(raw) != TYPE_DICTIONARY:
		return out
	for k: Variant in raw:
		var e: Variant = (raw as Dictionary)[k]
		if typeof(e) != TYPE_DICTIONARY:
			continue
		var copy := (e as Dictionary).duplicate(true)
		if copy.has(KEY_DEFEATED):
			copy[KEY_DEFEATED] = int(copy[KEY_DEFEATED])
		out[str(k)] = copy
	return out


func _entry(enemy_id: StringName) -> Dictionary:
	var key := String(enemy_id)
	if typeof(entries.get(key)) != TYPE_DICTIONARY:
		entries[key] = {}
	return entries[key] as Dictionary
