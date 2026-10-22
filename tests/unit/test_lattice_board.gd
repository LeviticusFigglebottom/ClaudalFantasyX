extends TestCase
## LatticeBoard: loading, adjacency, starts, and path queries.


func test_adjacency_is_undirected() -> void:
	var b := LatticeFixture.board()
	assert_true(b.are_adjacent(&"s_str", &"s_hp"))
	assert_true(b.are_adjacent(&"s_hp", &"s_str"), "edges work both ways")
	assert_false(b.are_adjacent(&"rhen_start", &"s_hp"))
	assert_eq(b.neighbors(&"s_str"), [&"rhen_start", &"s_hp", &"empty"] as Array[StringName], "edge order")
	assert_eq(b.neighbors(&"nope"), [] as Array[StringName])


func test_nodes_and_starts() -> void:
	var b := LatticeFixture.board()
	assert_eq(b.node_count(), 8)
	assert_eq(b.edge_count(), 7)
	assert_eq(b.start_of(&"rhen"), &"rhen_start")
	assert_eq(b.start_of(&"ysolde"), &"", "no start on this board")
	var n := b.lattice_node(&"gate1")
	assert_true(n.is_gate())
	assert_eq(n.gate_level, 1)
	assert_eq(n.position, Vector2i(4, 0))
	assert_true(b.lattice_node(&"s_hp").is_activatable())
	assert_false(b.lattice_node(&"empty").is_activatable())
	assert_true(b.lattice_node(&"missing") == null)


func test_shortest_path_and_blocking() -> void:
	var b := LatticeFixture.board()
	var path := b.shortest_path(&"asha_start", &"beyond")
	assert_eq(path, [&"asha_start", &"empty", &"s_str", &"s_hp", &"ab_kick", &"gate1", &"beyond"] as Array[StringName])
	assert_eq(b.shortest_path(&"rhen_start", &"beyond", {&"gate1": true}), [] as Array[StringName], "blocked")
	assert_eq(b.shortest_path(&"rhen_start", &"rhen_start"), [&"rhen_start"] as Array[StringName])


func test_reachable_respects_blocked() -> void:
	var b := LatticeFixture.board()
	assert_eq(b.reachable_from(&"rhen_start").size(), 8)
	var closed := b.reachable_from(&"rhen_start", {&"gate1": true})
	assert_eq(closed.size(), 6)
	assert_false(closed.has(&"beyond"))


func test_standard_board_loads_and_is_connected() -> void:
	var b := LatticeBoard.load_board()
	assert_eq(b.id, &"standard")
	assert_between(b.node_count(), 60, 90, "first section size")
	for cid: StringName in [&"rhen", &"asha", &"toma"]:
		var start := b.start_of(cid)
		assert_ne(start, &"", "%s has a start" % cid)
		assert_eq(b.reachable_from(start).size(), b.node_count(), "%s reaches every node" % cid)


func test_standard_board_skills_exist_in_battle_data() -> void:
	var b := LatticeBoard.load_board()
	var db := BattleDB.load_default()
	for n: LatticeNode in b.nodes.values():
		if n.kind == LatticeNode.KIND_ABILITY:
			assert_true(db.skills.has(n.skill), "skill %s exists" % n.skill)
