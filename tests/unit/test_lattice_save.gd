extends TestCase
## LatticeProgress persistence: to_dict/from_dict round trip and tolerance of board changes.


func test_round_trip_preserves_progress() -> void:
	var p := LatticeFixture.progress()
	var inv := FacetInventory.new({"facet_power": 1, "facet_key_1": 1})
	var t := p.traveler(&"rhen")
	t.movement_points = 4
	p.move(&"rhen", &"s_str")
	p.activate(&"rhen", inv)
	p.award_battle(&"rhen", 50)
	p.opened_gates[&"gate1"] = true
	var json_text := JSON.stringify(p.to_dict())
	var back := LatticeProgress.from_dict(
		JSON.parse_string(json_text) as Dictionary, LatticeFixture.board(), LatticeFixture.rules()
	)
	var bt := back.traveler(&"rhen")
	assert_eq(bt.position, &"s_str")
	assert_eq(bt.movement_points, t.movement_points)
	assert_eq(bt.lattice_points, t.lattice_points)
	assert_eq(bt.movement_earned, t.movement_earned)
	assert_true(back.is_activated_by(&"rhen", &"s_str"))
	assert_true(back.is_activated_by(&"rhen", &"rhen_start"))
	assert_true(back.is_gate_open(&"gate1"))
	assert_eq(back.traveler(&"asha").position, &"asha_start")
	assert_eq(back.stat_bonuses(&"rhen"), p.stat_bonuses(&"rhen"))
	assert_eq(back.to_dict(), p.to_dict(), "stable")


func test_empty_dict_is_fresh_progress() -> void:
	var p := LatticeProgress.from_dict({}, LatticeFixture.board(), LatticeFixture.rules())
	assert_true(p.travelers.is_empty())
	assert_true(p.add_character(&"rhen"))


func test_unknown_ids_are_dropped_and_position_falls_back_to_start() -> void:
	var d := {
		"board": "fixture",
		"characters":
		{
			"rhen": {"position": "deleted_node", "activated": ["s_str", "deleted_node"], "movement_points": 2},
			"ysolde": {"position": "also_gone", "activated": []},
		},
		"opened_gates": ["gate1", "s_str", "gone"],
	}
	var p := LatticeProgress.from_dict(d, LatticeFixture.board(), LatticeFixture.rules())
	var t := p.traveler(&"rhen")
	assert_eq(t.position, &"rhen_start")
	assert_true(t.activated.has(&"s_str"))
	assert_false(t.activated.has(&"deleted_node"))
	assert_eq(t.movement_points, 2)
	assert_true(p.traveler(&"ysolde") == null, "no start for her on this board")
	assert_eq(p.opened_gates.keys(), [&"gate1"], "only real gates stay open")


func test_progress_survives_a_full_save_round_trip() -> void:
	var saves: Node = (load("res://game/core/save_system.gd") as GDScript).new()
	var p := LatticeFixture.progress()
	p.traveler(&"asha").movement_points = 7
	var s := GameStateData.new()
	s.lattice = p.to_dict()
	var back: GameStateData = saves.deserialize(JSON.parse_string(JSON.stringify(saves.serialize(s))))
	var restored := LatticeProgress.from_dict(back.lattice, LatticeFixture.board(), LatticeFixture.rules())
	assert_eq(restored.traveler(&"asha").movement_points, 7)
	assert_eq(restored.to_dict(), p.to_dict())
	saves.free()
