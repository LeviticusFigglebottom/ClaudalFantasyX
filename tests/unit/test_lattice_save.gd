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


## M1-ARC-13: in play, unknown ids grant nothing and a lost position stands on the start; the
## saved data itself is kept (round trips: tests/unit/test_save_data_tables.gd).
func test_unknown_ids_grant_nothing_and_position_falls_back_to_start() -> void:
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
	assert_true(t.activated.has(&"deleted_node"), "kept, not dropped (M1-ARC-13)")
	assert_eq(t.movement_points, 2)
	assert_true(p.traveler(&"ysolde") == null, "no start for her on this board")
	assert_true(p.kept_characters.has("ysolde"), "but her saved progress is kept")
	assert_eq(p.opened_gates.keys(), [&"gate1"], "only real gates stay open")
	assert_eq(p.kept_gates, ["s_str", "gone"] as Array[String], "the others are kept as saved")
	var back := p.to_dict()
	assert_eq(back["characters"]["rhen"]["position"], "deleted_node", "the saved position until rhen moves")
	assert_eq(back["characters"]["ysolde"], d["characters"]["ysolde"])
	assert_eq(back["opened_gates"], ["gate1", "s_str", "gone"] as Array[String], "in saved order")


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


## M1-ARC-14 (review-sweep-J S1): a save naming another board is frozen, never re-homed.
func test_a_save_naming_another_board_is_frozen() -> void:
	var d := {
		"board": "elsewhere",
		"characters": {"rhen": {"position": "far_node", "activated": ["far_node", "x2"], "movement_points": 3}},
		"opened_gates": ["far_gate"],
	}
	var p := LatticeProgress.from_dict(d, LatticeFixture.board(), LatticeFixture.rules())
	assert_true(p.is_frozen(), "another board's save is frozen")
	assert_true(p.travelers.is_empty(), "nobody is placed on the wrong board")
	assert_false(p.add_character(&"rhen"), "and nobody is added")
	assert_eq(p.to_dict(), d, "the board field and positions are written back as saved")
	var st := GameStateData.new()
	assert_true(p.save_into(st))
	assert_eq(st.lattice, d, "a write-back changes nothing")


func test_a_save_naming_the_same_board_is_not_frozen() -> void:
	var p := LatticeProgress.from_dict({"board": "fixture"}, LatticeFixture.board(), LatticeFixture.rules())
	assert_false(p.is_frozen())
	assert_true(p.add_character(&"rhen"))


## Review-sweep-J nit: an empty save on a broken board is frozen too (is_frozen is a flag).
func test_an_empty_save_on_a_broken_board_is_frozen() -> void:
	var p := LatticeProgress.from_dict({}, LatticeBoard.new(), LatticeFixture.rules())
	assert_true(p.is_frozen())
	assert_false(p.add_character(&"rhen"))
	assert_eq(p.to_dict(), {})


## M1-ARC-14: writers load the board the save names; an id that is not a board id is refused.
func test_board_for_loads_the_board_the_save_names() -> void:
	assert_eq(LatticeProgress.board_for({}, LatticeBoard.DEFAULT_BOARD).id, LatticeBoard.DEFAULT_BOARD)
	var named := LatticeProgress.board_for({"board": "missing_board"}, LatticeBoard.DEFAULT_BOARD)
	assert_eq(named.id, &"missing_board", "the save's board, not the configured one")
	assert_ne(named.integrity_problem(), "", "a board that does not exist is broken, so the save freezes")
	var refused := LatticeProgress.board_for({"board": "../ui/x"}, LatticeBoard.DEFAULT_BOARD)
	assert_eq(refused.id, LatticeBoard.DEFAULT_BOARD, "no path is built from an invalid id")
	var p := LatticeProgress.from_dict({"board": "../ui/x"}, refused, LatticeFixture.rules())
	assert_true(p.is_frozen(), "and the save is frozen against the configured board")


func test_board_ids_are_checked() -> void:
	assert_true(LatticeBoard.is_valid_id("standard"))
	assert_true(LatticeBoard.is_valid_id("act_2_board"))
	for bad: String in ["", "../standard", "Standard", "a/b", "a.json", "a b"]:
		assert_false(LatticeBoard.is_valid_id(bad), "'%s' is not a board id" % bad)


## Review-sweep-J nit: the data gate builds no path from an invalid id and says why.
func test_the_data_gate_rejects_an_invalid_saved_board_id() -> void:
	var st := GameStateData.new()
	st.lattice = {"board": "../ui/x"}
	assert_ne(DataHealth.new().lattice_problem(st), "")
	st.lattice = {"board": "standard"}
	assert_eq(DataHealth.new().lattice_problem(st), "", "the shipped board is sound")


func test_battle_stage_restores_onto_the_saved_board() -> void:
	var saved := {"board": "../ui/x", "characters": {"rhen": {"position": "far_node"}}}
	var ids: Array[StringName] = [&"rhen"]
	var p := BattleStage.lattice_for(ids, saved)
	assert_true(p.is_frozen(), "an invalid board id is refused, not re-homed")
	assert_eq(p.to_dict(), saved)


## M1-ARC-14 (review-sweep-J S2): a lost position does not write the start into the save.
func test_a_lost_position_does_not_add_the_start_to_the_save() -> void:
	var d := {
		"board": "fixture",
		"characters":
		{
			"rhen":
			{
				"position": "far_node",
				"activated": ["far_node", "x2"],
				"movement_points": 1,
				"lattice_points": 0,
				"movement_earned": 0,
			}
		},
		"opened_gates": [],
	}
	var p := LatticeProgress.from_dict(d, LatticeFixture.board(), LatticeFixture.rules())
	var t := p.traveler(&"rhen")
	assert_eq(t.position, &"rhen_start")
	assert_true(p.is_activated_by(&"rhen", &"rhen_start"), "the start still counts as activated in play")
	assert_true(p.is_activated_by_anyone(&"rhen_start"))
	assert_false(t.activated.has(&"rhen_start"), "but it is not in the saved set")
	assert_eq(JSON.stringify(p.to_dict()), JSON.stringify(d), "an untouched save round-trips exactly")
	assert_eq(p.move(&"rhen", &"s_str"), LatticeProgress.RESULT_OK)
	var moved: Dictionary = p.to_dict()["characters"]["rhen"]
	assert_eq(moved["position"], "s_str")
	assert_eq(moved["activated"], ["far_node", "x2", "rhen_start"] as Array[String], "the first move adds it")
	assert_eq(t.implied_start, &"")
