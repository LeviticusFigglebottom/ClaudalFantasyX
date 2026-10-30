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


## Each Act I zone has its runtime loads listed (tools/loading/scene_loads.gd), and they are real files.
func test_every_act1_zone_lists_its_runtime_loads() -> void:
	var scenes := (_json(ResidentLoads.SCENE_LOADS_PATH)["scene_loads"] as Dictionary)["scenes"] as Dictionary
	var reg := LocationRegistry.load_default()
	var zones := 0
	for id: StringName in reg.location_ids():
		var s := String(id)
		if s.begins_with("prologue") or (s.begins_with("ch0") and s.substr(2, 1).is_valid_int()):
			var path := reg.scene_of(id)
			if path != "" and ResourceLoader.exists(path):
				zones += 1
				assert_true(scenes.has(path), "%s has its loads listed (rerun tools/loading/scene_loads.gd)" % id)
	assert_true(zones > 10, "the Act I zones were read")
	for path: String in scenes:
		for p: Variant in scenes[path]:
			assert_true(ResourceLoader.exists(str(p)), "%s: %s exists" % [path.get_file(), p])


## ADR 0042 §4: a VillagerLayer builds after its zone's own set-up, so its villagers' actors were missing from the
## lists until the generator let each zone settle. Each villager a zone's npc table dresses (its `actor`, else its
## npc_id, as VillagerLayer._make reads it) is in that zone's list, or it loads in the swap frame.
func test_each_zone_s_villager_actors_are_listed() -> void:
	var scenes := (_json(ResidentLoads.SCENE_LOADS_PATH)["scene_loads"] as Dictionary)["scenes"] as Dictionary
	var reg := LocationRegistry.load_default()
	var checked := 0
	for f in DirAccess.get_files_at(VillagerLayer.DATA_DIR):
		if not f.ends_with(".json"):
			continue
		var data := VillagerLayer.load_data(VillagerLayer.DATA_DIR + f)
		var path := reg.scene_of(StringName(str(data.get("zone", ""))))
		if not scenes.has(path):
			continue
		for row: Dictionary in data.get("villagers", []):
			var actor := str(row.get("actor", row.get("npc_id", "")))
			var actor_path := VillagerLayer.ACTOR_PATH % [actor, actor]
			if ResourceLoader.exists(actor_path):
				checked += 1
				assert_true(
					(scenes[path] as Array).has(actor_path),
					"%s lists %s (rerun tools/loading/scene_loads.gd)" % [path.get_file(), actor_path]
				)
	assert_true(checked > 5, "the villager tables were read")


## A change loads the zone's own list behind the same hold, and the next change drops it.
func test_a_change_loads_the_zone_s_list_and_drops_the_last() -> void:
	var router := Node.new()
	router.set_script(load("res://tests/fixtures/resident/hold_router.gd"))
	_add(router)
	ResidentLoads.run_headless = true
	var r := ResidentLoads.install(router)
	var ch1 := "res://game/levels/ch01/oruvel_underway/oruvel_underway.tscn"
	r.load_scene(ch1)
	r.hold()
	assert_true(r.holding, "held while the zone's loads run")
	while not r.is_ready():
		r.poll()
		OS.delay_msec(5)
	assert_false(r.scene.is_empty(), "the zone's resources are in")
	assert_true(
		r.swap_wait_progress() >= r.scene.size() * ResidentLoads.PROGRESS_SCALE,
		"its progress counts every finished load"
	)
	assert_false(r.holding, "released")
	var one := r.scene.keys()[0] as String
	r.load_scene("res://game/levels/ch08/coilspire/coilspire.tscn")
	var lists := (_json(ResidentLoads.SCENE_LOADS_PATH)["scene_loads"] as Dictionary)["scenes"] as Dictionary
	if not (lists["res://game/levels/ch08/coilspire/coilspire.tscn"] as Array).has(one):
		assert_false(r.scene.has(one), "the last zone's own resources are dropped")
	while not r.is_ready():
		r.poll()
		OS.delay_msec(5)
	_done()


## A field battle keeps the zone's loads, so the change back to the field reads nothing again (the human playtest's
## seconds of black after a won fight, 2026-10-30).
func test_a_field_battle_keeps_the_zone_s_loads_for_the_return() -> void:
	ResidentLoads.run_headless = true
	var router := Node.new()
	router.set_script(load("res://tests/fixtures/resident/hold_router.gd"))
	_add(router)
	var r := ResidentLoads.install(router)
	var ch1 := "res://game/levels/ch01/oruvel_underway/oruvel_underway.tscn"
	r.load_scene(ch1)
	while not r.is_ready():
		r.poll()
		OS.delay_msec(5)
	var zone := r.scene.keys()
	assert_false(zone.is_empty(), "the zone's resources are in")
	r.load_scene(SceneSwapProbe._queue_battle(&"ch02_tideline"))
	for path: String in zone:
		assert_true(r.scene.has(path), "kept through the battle: %s" % path)
	while not r.is_ready():
		r.poll()
		OS.delay_msec(5)
	BattleRequest.clear()
	r.load_scene(ch1)
	assert_true(r.is_ready(), "the return has nothing to load")
	assert_false(r.prewarm_pending(), "nor anything to prewarm again")
	_done()


## A field battle loads its arena and its enemies' actors behind the fade (the PC's ~2 s battle entries).
func test_a_battle_lists_its_arena_and_its_enemies() -> void:
	var paths := ResidentLoads.battle_paths(&"ch02_tideline")
	assert_true(paths.has(BattleArena.scene_of("tideline_dawn")), "the encounter's arena")
	for e: StringName in [&"reef_crab", &"lantern_eel"]:
		var s := str(BattleStage.stand_in_spec(e).get("scene", ""))
		if s != "":
			assert_true(paths.has(s), "%s's actor" % e)
	assert_true(ResidentLoads.battle_paths(&"no_such_fight").is_empty())


func test_the_router_starts_them_when_a_change_begins() -> void:
	assert_true(SceneRouter.has_signal(&"change_started"), "SceneRouter.change_started")
	assert_true(SceneRouter.get_node_or_null(NodePath(String(ResidentLoads.NAME))) is ResidentLoads, "installed")
	assert_eq(ResidentLoads.shared(), SceneRouter.get_node(NodePath(String(ResidentLoads.NAME))))


func _json(path: String) -> Dictionary:
	return JSON.parse_string(FileAccess.get_file_as_string(path)) as Dictionary


func _add(n: Node) -> void:
	var tree := Engine.get_main_loop() as SceneTree
	(tree.current_scene if tree.current_scene != null else tree.root).add_child(n)
	_made.append(n)


func _done() -> void:
	for n in _made:
		if is_instance_valid(n) and n.get_parent() != null:
			n.get_parent().remove_child(n)
			n.free()
	_made.clear()
	ResidentLoads.run_headless = false
