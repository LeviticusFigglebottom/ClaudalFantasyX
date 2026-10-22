extends TestCase
## LatticeProgress: movement cost, activation, gates, MP awards, and apply_to.

var p: LatticeProgress
var inv: FacetInventory


func before_each() -> void:
	p = LatticeFixture.progress()
	inv = FacetInventory.new({})


func test_characters_start_on_their_start_node() -> void:
	assert_eq(p.traveler(&"rhen").position, &"rhen_start")
	assert_true(p.is_activated_by(&"rhen", &"rhen_start"))
	assert_false(p.add_character(&"ysolde"), "no start on this board")
	assert_true(p.traveler(&"ysolde") == null)


func test_move_costs_one_point_onto_fresh_node() -> void:
	var t := p.traveler(&"rhen")
	t.movement_points = 2
	assert_eq(p.move_cost(&"rhen", &"s_str"), p.rules.move_cost)
	assert_eq(p.move(&"rhen", &"s_str"), LatticeProgress.RESULT_OK)
	assert_eq(t.position, &"s_str")
	assert_eq(t.movement_points, 2 - p.rules.move_cost)


func test_move_is_free_onto_node_anyone_activated() -> void:
	inv.add(&"facet_power", 1)
	var rhen := p.traveler(&"rhen")
	rhen.movement_points = 1
	p.move(&"rhen", &"s_str")
	assert_eq(p.activate(&"rhen", inv), LatticeProgress.RESULT_OK)
	# Asha walks over Rhen's activated node at the activated rate.
	var asha := p.traveler(&"asha")
	asha.movement_points = 1
	assert_eq(p.move(&"asha", &"empty"), LatticeProgress.RESULT_OK)
	assert_eq(asha.movement_points, 0)
	assert_eq(p.move_cost(&"asha", &"s_str"), p.rules.move_cost_activated)
	assert_eq(p.move(&"asha", &"s_str"), LatticeProgress.RESULT_OK, "free even with 0 points")
	assert_eq(p.move_cost(&"asha", &"rhen_start"), p.rules.move_cost_activated, "starts count as activated")


func test_illegal_moves() -> void:
	var t := p.traveler(&"rhen")
	assert_eq(p.move(&"rhen", &"s_str"), LatticeProgress.ERR_NO_MOVEMENT)
	t.movement_points = 5
	assert_eq(p.move(&"rhen", &"s_hp"), LatticeProgress.ERR_NOT_ADJACENT)
	assert_eq(p.move_cost(&"rhen", &"s_hp"), LatticeProgress.MOVE_ILLEGAL)
	assert_eq(p.move(&"rhen", &"nowhere"), LatticeProgress.ERR_UNKNOWN_NODE)
	assert_eq(p.move(&"ghost", &"s_str"), LatticeProgress.ERR_UNKNOWN_CHARACTER)
	assert_eq(t.movement_points, 5, "failed moves cost nothing")
	assert_eq(t.position, &"rhen_start")


func test_activation_consumes_matching_facet() -> void:
	var t := p.traveler(&"rhen")
	t.movement_points = 3
	p.move(&"rhen", &"s_str")
	assert_eq(p.activation_facet(&"rhen"), &"facet_power", "strength is a Power stat")
	inv.add(&"facet_mind", 1)
	assert_eq(p.activate(&"rhen", inv), LatticeProgress.ERR_NO_FACET, "wrong facet type")
	inv.add(&"facet_power", 2)
	assert_eq(p.activate(&"rhen", inv), LatticeProgress.RESULT_OK)
	assert_eq(inv.count(&"facet_power"), 2 - p.rules.facets_per_activation)
	assert_eq(inv.count(&"facet_mind"), 1, "other facets untouched")
	assert_eq(p.activate(&"rhen", inv), LatticeProgress.ERR_ALREADY_ACTIVATED)
	assert_eq(inv.count(&"facet_power"), 2 - p.rules.facets_per_activation, "no double charge")


func test_activation_is_per_character() -> void:
	inv.add(&"facet_power", 2)
	p.traveler(&"rhen").movement_points = 1
	p.move(&"rhen", &"s_str")
	p.activate(&"rhen", inv)
	var asha := p.traveler(&"asha")
	asha.movement_points = 1
	p.move(&"asha", &"empty")
	p.move(&"asha", &"s_str")
	assert_false(p.is_activated_by(&"asha", &"s_str"))
	assert_eq(p.activate_error(&"asha", inv), LatticeProgress.RESULT_OK, "Asha can activate it too")


func test_start_and_empty_nodes_cannot_be_activated() -> void:
	inv.add(&"facet_power", 1)
	assert_eq(p.activate(&"rhen", inv), LatticeProgress.ERR_NOT_ACTIVATABLE)
	p.traveler(&"asha").movement_points = 1
	p.move(&"asha", &"empty")
	assert_eq(p.activation_facet(&"asha"), &"")
	assert_eq(p.activate(&"asha", inv), LatticeProgress.ERR_NOT_ACTIVATABLE)


func test_ability_node_needs_ability_facet() -> void:
	_walk_rhen_to(&"ab_kick")
	assert_eq(p.activation_facet(&"rhen"), &"facet_ability")
	inv.add(&"facet_ability", 1)
	assert_eq(p.activate(&"rhen", inv), LatticeProgress.RESULT_OK)
	assert_eq(p.learned_skills(&"rhen"), [&"kick_off"] as Array[StringName])


func test_gate_blocks_until_opened_with_exact_key_level() -> void:
	_walk_rhen_to(&"ab_kick")
	p.traveler(&"rhen").movement_points = 5
	assert_eq(p.move(&"rhen", &"gate1"), LatticeProgress.ERR_GATE_CLOSED)
	assert_eq(p.move_cost(&"rhen", &"gate1"), LatticeProgress.MOVE_ILLEGAL)
	inv.add(&"facet_key_2", 1)
	assert_eq(p.open_gate(&"rhen", &"gate1", inv), LatticeProgress.ERR_NO_FACET, "level 2 key can't open level 1")
	inv.add(&"facet_key_1", 1)
	assert_eq(p.open_gate(&"rhen", &"gate1", inv), LatticeProgress.RESULT_OK)
	assert_eq(inv.count(&"facet_key_1"), 1 - p.rules.keys_per_gate)
	assert_eq(inv.count(&"facet_key_2"), 1)
	assert_true(p.is_gate_open(&"gate1"))
	assert_eq(p.open_gate(&"rhen", &"gate1", inv), LatticeProgress.ERR_GATE_OPEN)
	assert_eq(p.move_cost(&"rhen", &"gate1"), p.rules.move_cost_activated, "opened gates are activated for all")
	assert_eq(p.move(&"rhen", &"gate1"), LatticeProgress.RESULT_OK)
	assert_eq(p.move(&"rhen", &"beyond"), LatticeProgress.RESULT_OK)


func test_gate_must_be_adjacent_and_a_gate() -> void:
	inv.add(&"facet_key_1", 1)
	assert_eq(p.open_gate(&"rhen", &"gate1", inv), LatticeProgress.ERR_NOT_ADJACENT)
	assert_eq(p.open_gate(&"rhen", &"s_str", inv), LatticeProgress.ERR_NOT_A_GATE)
	assert_eq(p.open_gate(&"rhen", &"nowhere", inv), LatticeProgress.ERR_UNKNOWN_NODE)
	assert_eq(inv.count(&"facet_key_1"), 1)


func test_cheapest_path_prefers_activated_nodes_and_skips_closed_gates() -> void:
	assert_eq(p.cheapest_path(&"rhen", &"beyond"), [] as Array[StringName], "gate closed")
	var path := p.cheapest_path(&"asha", &"s_hp")
	assert_eq(path, [&"asha_start", &"empty", &"s_str", &"s_hp"] as Array[StringName])
	p.opened_gates[&"gate1"] = true
	assert_eq(p.cheapest_path(&"rhen", &"beyond").size(), 6)


func test_award_battle_converts_lp_to_movement_points() -> void:
	var t := p.traveler(&"rhen")
	var gained := p.award_battle(&"rhen", 105)
	assert_eq(gained, 3, "105 LP at 30 per point")
	assert_eq(t.movement_points, 3)
	assert_eq(t.lattice_points, 15)
	assert_eq(t.movement_earned, 3)
	assert_eq(p.award_battle(&"rhen", 15), 1, "the pool carries over")
	assert_eq(t.lattice_points, 0)
	assert_eq(p.award_battle(&"ghost", 100), 0)


func test_award_battle_respects_cap() -> void:
	var t := p.traveler(&"rhen")
	t.movement_points = ProgressionFormulas.MOVEMENT_POINT_CAP - 1
	assert_eq(p.award_battle(&"rhen", 90), 1)
	assert_eq(t.movement_points, ProgressionFormulas.MOVEMENT_POINT_CAP)
	assert_eq(t.lattice_points, 60, "LP keeps pooling at the cap")


func test_apply_to_adds_stats_and_skills_on_base() -> void:
	inv.add(&"facet_power", 2)
	inv.add(&"facet_ability", 1)
	p.traveler(&"rhen").movement_points = 3
	p.move(&"rhen", &"s_str")
	p.activate(&"rhen", inv)
	p.move(&"rhen", &"s_hp")
	p.activate(&"rhen", inv)
	p.move(&"rhen", &"ab_kick")
	p.activate(&"rhen", inv)
	var db := BattleDB.load_default()
	var base := BattleCombatant.from_dict(&"rhen", BattleCombatant.TEAM_PARTY, db.characters[&"rhen"])
	var c := BattleCombatant.from_dict(&"rhen", BattleCombatant.TEAM_PARTY, db.characters[&"rhen"])
	p.apply_to(c)
	assert_eq(c.strength, base.strength + 3)
	assert_eq(c.max_hp, base.max_hp + 40)
	assert_eq(c.hp, c.max_hp, "starts at full HP")
	assert_eq(c.agility, base.agility, "unactivated nodes add nothing")
	assert_eq(c.magic, base.magic)
	assert_true(c.skills.has(&"kick_off"))
	assert_eq(c.skills.size(), base.skills.size() + 1)
	assert_eq(p.stat_bonuses(&"rhen"), {&"strength": 3, &"hp": 40})


func test_apply_to_does_not_duplicate_known_skills_or_leak_between_characters() -> void:
	var nodes := [
		{"id": "s", "type": "start", "character": "rhen", "x": 0, "y": 0},
		{"id": "q", "type": "ability", "skill": "quick_hit", "x": 1, "y": 0},
		{"id": "m", "type": "stat", "stat": "mp", "value": 10, "x": 2, "y": 0},
	]
	var b := LatticeBoard.from_dict({"board": {"id": "dup"}, "nodes": nodes, "edges": [["s", "q"], ["q", "m"]]})
	var prog := LatticeProgress.new(b, LatticeFixture.rules())
	prog.add_character(&"rhen")
	inv.add(&"facet_ability", 1)
	inv.add(&"facet_mind", 1)
	prog.traveler(&"rhen").movement_points = 2
	prog.move(&"rhen", &"q")
	prog.activate(&"rhen", inv)
	prog.move(&"rhen", &"m")
	prog.activate(&"rhen", inv)
	var db := BattleDB.load_default()
	var c := BattleCombatant.from_dict(&"rhen", BattleCombatant.TEAM_PARTY, db.characters[&"rhen"])
	var before := c.skills.size()
	var mp_before := c.max_mp
	prog.apply_to(c)
	assert_eq(c.skills.size(), before, "quick_hit already known")
	assert_eq(c.max_mp, mp_before + 10)
	assert_eq(c.mp, c.max_mp)
	var asha := BattleCombatant.from_dict(&"asha", BattleCombatant.TEAM_PARTY, db.characters[&"asha"])
	var asha_mp := asha.max_mp
	prog.apply_to(asha)
	assert_eq(asha.max_mp, asha_mp, "Rhen's nodes don't apply to Asha")


func _walk_rhen_to(target: StringName) -> void:
	var t := p.traveler(&"rhen")
	t.movement_points = 10
	for step in p.cheapest_path(&"rhen", target).slice(1):
		p.move(&"rhen", step)
	t.movement_points = 0
