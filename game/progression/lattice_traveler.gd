class_name LatticeTraveler
extends RefCounted
## One character's state on the Lattice: where they stand, what they activated, and their
## movement-point and LP balances. Owned by LatticeProgress.

var character_id: StringName = &""
var position: StringName = &""
## Set of node ids this character activated (id -> true), in activation order.
var activated: Dictionary = {}
## Banked movement points (spent to walk the board). Not the battle "mp" stat.
var movement_points: int = 0
## Lattice points pooled toward the next movement point.
var lattice_points: int = 0
## Movement points earned over the whole game (drives ProgressionFormulas.lp_threshold).
var movement_earned: int = 0
## M1-ARC-13: the saved position when this board has no such node ("" otherwise). The traveler
## stands on their start meanwhile, but to_dict writes this back until they move, so a node that a
## later board restores (or a board that failed to load) never costs them their place.
var saved_position: StringName = &""
## M1-ARC-14 (review-sweep-J S2): the start a lost position put the traveler on, when the save did
## not already list it as activated ("" otherwise). It counts as activated in memory (as every start
## does) but is not written back, so an untouched save round-trips exactly; the first move adds it
## to `activated` (LatticeProgress.move), as add_character would have.
var implied_start: StringName = &""


## True when this traveler activated `node_id`, counting an implied start.
func has_activated(node_id: StringName) -> bool:
	return activated.has(node_id) or (implied_start != &"" and implied_start == node_id)


func to_dict() -> Dictionary:
	var ids: Array[String] = []
	for nid: StringName in activated:
		ids.append(String(nid))
	return {
		"position": String(saved_position if saved_position != &"" else position),
		"activated": ids,
		"movement_points": movement_points,
		"lattice_points": lattice_points,
		"movement_earned": movement_earned,
	}


static func from_dict(cid: StringName, d: Dictionary) -> LatticeTraveler:
	var t := LatticeTraveler.new()
	t.character_id = cid
	t.position = StringName(str(d.get("position", "")))
	for nid: Variant in d.get("activated", []):
		t.activated[StringName(str(nid))] = true
	t.movement_points = int(d.get("movement_points", 0))
	t.lattice_points = int(d.get("lattice_points", 0))
	t.movement_earned = int(d.get("movement_earned", 0))
	return t
