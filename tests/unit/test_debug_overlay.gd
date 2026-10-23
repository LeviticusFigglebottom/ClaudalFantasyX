extends TestCase
## M1-ARC-02: debug overlay logic (DebugHooks registration, DebugReadouts pages) and the overlay
## node's input routing. Nothing here changes scene: teleport and sandbox launching go through
## SceneRouter and would replace the test runner, so those are checked by their bindings and data.

const DEBUG_DIR := "res://game/core/debug"
const GAME_DIR := "res://game"
const DEBUG_CLASSES: Array[String] = ["DebugOverlay", "DebugHooks", "DebugReadouts", "SceneSwapProbe"]
const FIELD_ZONE := "res://game/levels/_tests/field/field_test.tscn"
const SEED := 7
const BOOT_SCRIPT := "res://game/core/boot.gd"


class FakeEncounters:
	extends RefCounted

	func debug_encounter_state() -> Dictionary:
		return {"zone_id": &"test_flats", "danger": 30, "threshold": 120, "steps": 14, "bogus": 1}


class FakeLatticeScreen:
	extends RefCounted
	var progress: LatticeProgress
	var inventory := FacetInventory.new({})

	func debug_lattice() -> LatticeProgress:
		return progress

	func debug_facets() -> FacetInventory:
		return inventory


class FakeBattleScene:
	extends Node
	var engine: BattleEngine


var saved_flags: Dictionary
var saved_lattice: Dictionary
var saved_inventory: Dictionary
var saved_party: Array[StringName]


func before_each() -> void:
	saved_flags = Game.state.flags.duplicate(true)
	saved_lattice = Game.state.lattice.duplicate(true)
	saved_inventory = Game.state.inventory.duplicate(true)
	saved_party = Game.state.party_ids.duplicate()
	DebugHooks.clear()


func _restore() -> void:
	Game.state.flags = saved_flags
	Game.state.lattice = saved_lattice
	Game.state.inventory = saved_inventory
	Game.state.party_ids = saved_party
	DebugHooks.clear()


# --- F2 turn order -------------------------------------------------------------------------------


func test_turn_order_reads_the_registered_engine() -> void:
	var engine := _engine()
	assert_eq(DebugHooks.battle_engine(), null, "nothing registered, nothing in the runner scene")
	DebugHooks.register_battle_engine(engine)
	assert_eq(DebugHooks.battle_engine(), engine)
	var d := DebugReadouts.turn_order(engine, CtbTimeline.PREVIEW_LENGTH)
	var fighters := d["fighters"] as Array
	assert_eq(fighters.size(), engine.party_active.size() + engine.enemies.size() + engine.party_reserve.size())
	for i in range(1, fighters.size()):
		var prev: Dictionary = fighters[i - 1]
		var cur: Dictionary = fighters[i]
		assert_false(cur["active"] and not prev["active"], "reserves (off the timeline) come last")
		if cur["active"] == prev["active"]:
			assert_true(int(cur["next_time"]) >= int(prev["next_time"]), "sorted by next turn")
	for f: Dictionary in fighters:
		var expected := int(f["next_time"]) - engine.now if f["active"] else DebugReadouts.RESERVE_TICKS
		assert_eq(int(f["ticks_until"]), expected)
		assert_eq(int(f["base_delay"]), Formulas.base_delay(int(f["agility"])))
	var predicted := d["predicted"] as Array
	var truth := engine.timeline.predict(CtbTimeline.PREVIEW_LENGTH)
	assert_eq(predicted.size(), truth.size())
	assert_eq(predicted[0]["id"], truth[0].combatant_id, "same prediction as the HUD timeline")
	assert_eq(d["current"], engine.current.id)
	var lines := DebugReadouts.turn_order_lines(engine, CtbTimeline.PREVIEW_LENGTH)
	assert_true(lines[0].contains(String(engine.current.id)))
	_restore()


func test_battle_engine_is_discovered_without_registration() -> void:
	var scene := FakeBattleScene.new()
	var child := FakeBattleScene.new()
	scene.add_child(child)
	child.engine = _engine()
	assert_eq(DebugHooks.discover_battle_engine(scene), child.engine, "finds a node exposing `engine`")
	assert_eq(DebugReadouts.turn_order_lines(null, 1)[0], DebugReadouts.NO_BATTLE)
	scene.free()
	_restore()


# --- F3 encounters -------------------------------------------------------------------------------


func test_encounter_readout_uses_the_provider_interface() -> void:
	assert_eq(DebugReadouts.encounter_lines(DebugHooks.encounter_provider())[0], DebugReadouts.NO_ENCOUNTERS)
	var p := FakeEncounters.new()
	DebugHooks.register_encounter_provider(p)
	assert_eq(DebugHooks.encounter_provider(), p)
	var s := DebugReadouts.encounter_state(p)
	assert_false(s.has("bogus"), "unknown keys dropped")
	assert_eq(s["danger"], 30)
	var text := "\n".join(DebugReadouts.encounter_lines(p))
	assert_true(text.contains("test_flats") and text.contains("25%"), text)
	var plain := RefCounted.new()
	DebugHooks.register_encounter_provider(plain)
	assert_eq(DebugHooks.encounter_provider(), p, "an object without the method is refused")
	_restore()


# --- F4 flags ------------------------------------------------------------------------------------


func test_flag_inspector_lists_declared_flags_and_toggles_bools() -> void:
	var rows := DebugReadouts.flag_rows()
	assert_eq(rows.size(), Game.registry.flags.size())
	var names: Array[String] = []
	for r in rows:
		names.append(String(r["name"]))
	var sorted := names.duplicate()
	sorted.sort()
	assert_eq(names, sorted)
	Game.set_flag(&"test_flag", false)
	assert_true(DebugReadouts.toggle_flag(&"test_flag"))
	assert_eq(Game.get_flag(&"test_flag"), true)
	assert_true(DebugReadouts.toggle_flag(&"test_flag"))
	assert_eq(Game.get_flag(&"test_flag"), false)
	Game.set_flag(&"test_counter", 3)
	assert_false(DebugReadouts.toggle_flag(&"test_counter"), "numbers are not toggled")
	assert_eq(Game.get_flag(&"test_counter"), 3)
	assert_false(DebugReadouts.toggle_flag(&"not_a_declared_flag"))
	_restore()


# --- F5 teleports --------------------------------------------------------------------------------


func test_teleports_resolve_and_spawns_exist() -> void:
	var cfg := DebugReadouts.config()
	var raw := (FieldInput.load_json(str(cfg["teleports_path"]))["teleports"] as Array).size()
	var list := DebugReadouts.teleports(str(cfg["teleports_path"]))
	assert_eq(list.size(), raw, "every registered scene exists")
	var ids := {}
	var zone := (load(FIELD_ZONE) as PackedScene).instantiate()
	for t in list:
		assert_false(ids.has(t["id"]), "unique id %s" % t["id"])
		ids[t["id"]] = true
		if t["scene"] == FIELD_ZONE:
			assert_true(zone.has_node(NodePath("Spawns/%s" % t["spawn"])), "spawn %s exists" % t["spawn"])
	assert_true(zone.has_method(&"place_at"), "teleport spawns reach place_at()")
	zone.free()


# --- F6 Lattice ----------------------------------------------------------------------------------


func test_lattice_cheat_grants_movement_and_facets_into_game_state() -> void:
	var cfg := DebugReadouts.config()["lattice_cheat"] as Dictionary
	Game.state.lattice = {}
	Game.state.inventory = {}
	Game.state.party_ids = [&"rhen", &"asha"] as Array[StringName]
	var r := DebugReadouts.apply_lattice_cheat(null, cfg)
	var points := int(cfg["movement_points"])
	assert_eq((r["characters"] as Dictionary).keys().size(), 2)
	var progress := LatticeProgress.from_dict(Game.state.lattice, LatticeBoard.load_board(), LatticeRules.load_file())
	assert_eq(progress.traveler(&"rhen").movement_points, points, "persisted through to_dict")
	var rules := LatticeRules.load_file()
	var inv := FacetInventory.new(Game.state.inventory)
	for fid: StringName in rules.facets:
		assert_eq(inv.count(fid), int(cfg["facets_each"]), "%s granted" % fid)
	DebugReadouts.apply_lattice_cheat(null, cfg)
	progress = LatticeProgress.from_dict(Game.state.lattice, LatticeBoard.load_board(), LatticeRules.load_file())
	assert_eq(progress.traveler(&"asha").movement_points, 2 * points, "stacks")
	assert_true("\n".join(DebugReadouts.lattice_lines(null, cfg)).contains("rhen"))
	_restore()


func test_lattice_cheat_on_a_live_screen_leaves_the_save_alone() -> void:
	var cfg := DebugReadouts.config()["lattice_cheat"] as Dictionary
	Game.state.lattice = {}
	var screen := FakeLatticeScreen.new()
	screen.progress = LatticeProgress.new(LatticeBoard.load_board(), LatticeRules.load_file())
	DebugHooks.register_lattice_source(screen)
	DebugReadouts.apply_lattice_cheat(DebugHooks.lattice_source(), cfg)
	assert_true(Game.state.lattice.is_empty(), "the live screen owns persistence")
	assert_true(screen.progress.traveler(&"rhen").movement_points > 0)
	assert_true(screen.inventory.count(&"facet_power") > 0)
	assert_eq(DebugReadouts.grant_movement(screen.progress, &"nobody", 5), -1, "no start, no grant")
	_restore()


# --- Overlay node --------------------------------------------------------------------------------


func test_overlay_routes_function_keys_and_lists() -> void:
	var overlay := (load(DebugOverlay.SCENE_PATH) as PackedScene).instantiate() as DebugOverlay
	_host().add_child(overlay)
	var cfg := overlay.cfg
	for action: String in cfg["actions"]:
		assert_true(InputMap.has_action(StringName(action)), "%s bound at runtime" % action)
	assert_false(overlay.is_open())
	assert_true(overlay.handle_input(_key(KEY_F4)))
	assert_eq(overlay.page, DebugOverlay.PAGE_FLAGS)
	var rows := DebugReadouts.flag_rows()
	var target := -1
	for i in rows.size():
		if rows[i]["name"] == &"test_flag":
			target = i
	Game.set_flag(&"test_flag", false)
	for i in target:
		overlay.move_selection(1)
	overlay.activate()
	assert_eq(Game.get_flag(&"test_flag"), true, "Enter toggled the selected flag")
	overlay.move_selection(-rows.size())
	assert_eq(overlay.selection, target, "selection wraps")
	assert_true(overlay.handle_input(_key(KEY_F2)))
	assert_eq(overlay.page, DebugOverlay.PAGE_TURN_ORDER)
	assert_eq(overlay.render_page(DebugOverlay.PAGE_TURN_ORDER)[0], DebugReadouts.NO_BATTLE)
	assert_true(overlay.handle_input(_key(KEY_F2)), "same key again hides")
	assert_false(overlay.is_open())
	assert_false(overlay.handle_input(_key(KEY_UP)), "list keys pass through while closed")
	var help := "\n".join(overlay.render_page(DebugOverlay.PAGE_HELP))
	assert_true(help.contains("F9") and help.contains("F4"), help)
	assert_eq(overlay.teleport_entries().size(), DebugReadouts.teleports(str(cfg["teleports_path"])).size())
	overlay.free()
	_restore()


func test_install_is_idempotent() -> void:
	var host := Node.new()
	_host().add_child(host)
	var a := DebugOverlay.install(host)
	var b := DebugOverlay.install(host)
	assert_true(a != null and a == b, "one overlay per root (debug build)")
	host.free()
	_restore()


func test_f9_moved_out_of_boot_and_game_code_never_names_debug_classes() -> void:
	var boot := FileAccess.get_file_as_string(BOOT_SCRIPT)
	assert_false(boot.contains("KEY_F9"), "boot.gd no longer handles F9")
	assert_false(boot.contains("SceneRouter.change_scene"), "boot.gd no longer launches the sandbox")
	var events := InputMap.action_get_events(DebugOverlay.ACTION_SANDBOX)
	var has_f9 := false
	for ev in events:
		has_f9 = has_f9 or (ev is InputEventKey and (ev as InputEventKey).physical_keycode == KEY_F9)
	assert_true(has_f9, "F9 opens the sandbox from the overlay")
	for path in _scripts(GAME_DIR):
		if path.begins_with(DEBUG_DIR):
			continue
		var text := FileAccess.get_file_as_string(path)
		for cls in DEBUG_CLASSES:
			# A code reference (not a quoted node name or path) would fail to compile in release.
			var code_ref := RegEx.create_from_string('(?<!["\\w/])%s(?!["\\w])' % cls)
			assert_true(code_ref.search(text) == null, "%s names %s: release strips game/core/debug/" % [path, cls])


# --- helpers -------------------------------------------------------------------------------------


func _engine() -> BattleEngine:
	var e := BattleEngine.new()
	var active: Array[StringName] = [&"rhen", &"asha"]
	var reserve: Array[StringName] = [&"toma"]
	e.setup(BattleDB.load_default(), active, reserve, &"sandbox_reef", SEED)
	e.begin()
	return e


func _key(code: Key) -> InputEventKey:
	var k := InputEventKey.new()
	k.physical_keycode = code
	k.pressed = true
	return k


func _scripts(dir_path: String) -> PackedStringArray:
	var out := PackedStringArray()
	var dir := DirAccess.open(dir_path)
	if dir == null:
		return out
	for f in dir.get_files():
		if f.ends_with(".gd"):
			out.append(dir_path.path_join(f))
	for d in dir.get_directories():
		out.append_array(_scripts(dir_path.path_join(d)))
	return out


func _host() -> Node:
	return (Engine.get_main_loop() as SceneTree).current_scene
