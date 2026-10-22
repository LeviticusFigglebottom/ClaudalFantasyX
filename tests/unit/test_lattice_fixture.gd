class_name LatticeFixture
extends RefCounted
## Shared tiny board for the Lattice tests (no test_* methods: the runner skips it).
##
##   rhen_start - s_str - s_hp - ab_kick - gate1 - beyond
##                  |
##   asha_start - empty
##
## Rules come from the real facets.json so the tests follow the data.


static func board() -> LatticeBoard:
	var d := {
		"board": {"id": "fixture", "name_key": "LATTICE_STANDARD"},
		"nodes":
		[
			{"id": "rhen_start", "type": "start", "character": "rhen", "x": 0, "y": 0},
			{"id": "s_str", "type": "stat", "stat": "strength", "value": 3, "x": 1, "y": 0},
			{"id": "s_hp", "type": "stat", "stat": "hp", "value": 40, "x": 2, "y": 0},
			{"id": "ab_kick", "type": "ability", "skill": "kick_off", "x": 3, "y": 0},
			{"id": "gate1", "type": "gate", "gate_level": 1, "x": 4, "y": 0},
			{"id": "beyond", "type": "stat", "stat": "agility", "value": 2, "x": 5, "y": 0},
			{"id": "asha_start", "type": "start", "character": "asha", "x": 0, "y": 2},
			{"id": "empty", "type": "empty", "x": 1, "y": 2},
		],
		"edges":
		[
			["rhen_start", "s_str"],
			["s_str", "s_hp"],
			["s_hp", "ab_kick"],
			["ab_kick", "gate1"],
			["gate1", "beyond"],
			["asha_start", "empty"],
			["empty", "s_str"],
		],
	}
	return LatticeBoard.from_dict(d)


static func rules() -> LatticeRules:
	return LatticeRules.load_file()


static func progress() -> LatticeProgress:
	var p := LatticeProgress.new(board(), rules())
	p.add_character(&"rhen")
	p.add_character(&"asha")
	return p
