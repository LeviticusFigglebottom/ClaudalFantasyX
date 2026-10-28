extends TestCase
## ADR 0111 (the PC's 1.3-3 s hidden swap frames): the hero bodies load on worker threads as a change starts,
## the router's swap waits for them, and they stay cached, so HeroFieldActor and the battle stand-ins never read
## a hero scene from disk inside the swap frame.

var _made: Array[Node] = []


func test_the_paths_are_every_field_body_and_the_party_s_battle_actors() -> void:
	var data := ResidentLoads.load_data()
	var field := HeroFieldActor.field_data().get("heroes", {}) as Dictionary
	var paths := ResidentLoads.paths_for(data, [&"asha"] as Array[StringName])
	for id: String in field:
		var p := HeroFieldActor.scene_path(StringName(id))
		if p != "":
			assert_true(paths.has(p), "%s's field body" % id)
	var stand := (
		(_json("res://game/data/ui/battle_sandbox.json")["battle_sandbox"] as Dictionary)["stand_ins"] as Dictionary
	)
	assert_true(paths.has(str((stand["asha"] as Dictionary)["scene"])), "a party hero's battle actor")
	assert_true(paths.has(str((stand[str(data["leader_default"])] as Dictionary)["scene"])), "the leader's, always")
	assert_false(paths.has(str((stand["kerrid"] as Dictionary)["scene"])), "not a hero outside the party")


func test_a_change_holds_the_swap_until_the_loads_are_in_then_keeps_them() -> void:
	var router := Node.new()
	router.set_script(load("res://tests/fixtures/resident/hold_router.gd"))
	_add(router)
	ResidentLoads.run_headless = true
	var r := ResidentLoads.install(router)
	assert_eq(ResidentLoads.install(router), r, "idempotent")
	r.resident.clear()
	router.emit_signal(&"change_started", "res://game/levels/ch02/haluna/haluna.tscn")
	assert_false(r.pending.is_empty(), "the loads started")
	assert_true(r.holding and router.call(&"holders").has(r), "the swap is held")
	var frames := 0
	while not r.is_ready() and frames < 100000:
		r.poll()
		OS.delay_msec(5)
		frames += 1
	assert_true(r.is_ready(), "every load came in")
	assert_false(r.holding, "the hold is released")
	assert_false(router.call(&"holders").has(r), "the router's swap is free")
	var first := r.resident.keys()[0] as String
	assert_true(ResourceLoader.has_cached(first), "kept in the cache for the next load()")
	router.emit_signal(&"change_started", "res://game/levels/ch02/haluna/haluna.tscn")
	assert_true(r.pending.is_empty() and not r.holding, "a later change waits for nothing")
	_done()


func test_the_title_scene_starts_them_without_a_hold() -> void:
	var router := Node.new()
	router.set_script(load("res://tests/fixtures/resident/hold_router.gd"))
	_add(router)
	ResidentLoads.run_headless = true
	var r := ResidentLoads.install(router)
	r.resident.clear()
	router.emit_signal(&"change_started", "res://game/core/boot.tscn")
	assert_false(r.holding, "the title never waits for the heroes")
	while not r.is_ready():
		r.poll()
		OS.delay_msec(5)
	_done()


func test_the_router_starts_them_when_a_change_begins() -> void:
	assert_true(SceneRouter.has_signal(&"change_started"), "SceneRouter.change_started")
	assert_true(SceneRouter.get_node_or_null(NodePath(String(ResidentLoads.NAME))) is ResidentLoads, "installed")
	assert_eq(ResidentLoads.shared(), SceneRouter.get_node(NodePath(String(ResidentLoads.NAME))))


func _json(path: String) -> Dictionary:
	return JSON.parse_string(FileAccess.get_file_as_string(path)) as Dictionary


func _add(n: Node) -> void:
	(Engine.get_main_loop() as SceneTree).root.add_child(n)
	_made.append(n)


func _done() -> void:
	for n in _made:
		if is_instance_valid(n) and n.get_parent() != null:
			n.get_parent().remove_child(n)
			n.free()
	_made.clear()
	ResidentLoads.run_headless = false
