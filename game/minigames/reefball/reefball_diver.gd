class_name ReefballDiver
extends RefCounted
## Runtime state of one Reefball diver (M3-RBL-01): side, role, stats, breath and depth band.
## Depth 0 is the ring at the top of the drop; larger is deeper. Node-free.

const STATS: Array[String] = ["breath", "stroke", "reach", "grip", "strip", "loft", "ward"]

var id: StringName = &""
var name_key := ""
var side := 0
## Index in ReefballMatch.divers (both sides, side 0 first): every tie breaks by it.
var order := 0
var role: StringName = &""
var stats: Dictionary = {}
var breath := 0
var depth := 0
## True while the diver is going up to (or waiting at) the ring to get breath back.
var resting := false


static func from_row(row: Dictionary, side_index: int) -> ReefballDiver:
	var d := ReefballDiver.new()
	d.id = StringName(str(row.get("id", "")))
	d.name_key = str(row.get("name_key", ""))
	d.side = side_index
	d.role = StringName(str(row.get("role", "")))
	for s in STATS:
		d.stats[s] = int((row.get("stats", {}) as Dictionary).get(s, 0))
	d.breath = d.max_breath()
	return d


func stat(stat_name: String) -> int:
	return int(stats.get(stat_name, 0))


func max_breath() -> int:
	return stat("breath")


func breath_frac() -> float:
	return float(breath) / float(maxi(1, max_breath()))


func snapshot() -> Dictionary:
	return {
		"id": id,
		"name_key": name_key,
		"side": side,
		"role": role,
		"stats": stats.duplicate(),
		"breath": breath,
		"max_breath": max_breath(),
		"depth": depth,
		"resting": resting,
	}
