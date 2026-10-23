extends TestCase
## M1-ARC-03: the save shrine in the save-shrine copy of the field test zone. The player uses it
## through FieldController.interact(): the party is restored (bus request), flags and location
## are set, the save menu opens over a paused field, and the teleport hook is a stub.

const ZONE := "res://game/levels/_tests/save_shrine/save_shrine_test.tscn"
const TEST_DIR := "user://test_save_shrine"
const GLIMMER_CONFIG := "res://game/data/vfx/glimmer.json"

var zone: Node3D
var player: FieldController
var shrine: SaveShrine
var heals: Array[StringName] = []
var uses: Array[Array] = []
var interactions: Array[StringName] = []
var _saved_dir := ""
var _saved_state: GameStateData


func before_each() -> void:
	_saved_dir = SaveSystem.save_dir
	_saved_state = Game.state
	SaveSystem.save_dir = TEST_DIR
	Game.state = GameStateData.new()
	zone = (load(ZONE) as PackedScene).instantiate() as Node3D
	_host().add_child(zone)
	(zone.get_node("CameraDirector") as FieldCameraDirector).auto_update = false
	player = zone.get_node("Player") as FieldController
	player.set_physics_process(false)
	player.set_process_unhandled_input(false)
	shrine = zone.get_node("Interactables/SaveShrine") as SaveShrine
	zone.call(&"place_at", &"Shrine", 0.0)
	EventBus.party_full_heal_requested.connect(_on_heal)
	EventBus.save_shrine_used.connect(_on_used)
	FieldEvents.connect_interacted(_on_interacted)


func _on_heal(source: StringName) -> void:
	heals.append(source)


func _on_used(shrine_id: StringName, location: StringName) -> void:
	uses.append([shrine_id, location])


func _on_interacted(id: StringName, _kind: StringName, _payload: Dictionary) -> void:
	interactions.append(id)


func test_using_the_shrine_heals_flags_and_opens_the_save_menu() -> void:
	assert_false(bool(Game.get_flag(&"save_shrine_used")))
	assert_eq(player.nearest_interactable(), shrine, "the spawn is within reach")
	assert_eq(player.interact(), shrine)
	assert_eq(heals, [&"save_shrine_test"] as Array[StringName], "one full-heal request from this shrine")
	assert_true(bool(Game.get_flag(&"save_shrine_used")), "set through Game.set_flag")
	assert_eq(Game.state.location_id, &"field_test")
	assert_eq(uses, [[&"save_shrine_test", &"field_test"]])
	assert_eq(interactions, [&"save_shrine_test"] as Array[StringName], "still a normal field interaction")
	assert_true(shrine.is_menu_open())
	assert_eq(shrine.menu.model.mode, SaveMenuModel.Mode.SAVE)
	assert_eq(shrine.menu.model.extra_meta, {"shrine_id": "save_shrine_test"})
	assert_eq(shrine.menu.subtitle_key, SaveShrine.RESTORED_KEY)
	assert_true(zone.get_tree().paused, "the field waits under the menu")
	_done()


func test_closing_the_menu_unpauses_and_the_shrine_can_be_used_again() -> void:
	var closed: Array[SaveMenuModel.Outcome] = []
	shrine.menu_closed.connect(func(o: SaveMenuModel.Outcome) -> void: closed.append(o))
	player.interact()
	var menu := shrine.menu
	menu.handle_input(_action(&"ui_cancel"))
	assert_eq(closed.size(), 1)
	assert_false(shrine.is_menu_open())
	assert_false(zone.get_tree().paused)
	assert_true(shrine.is_available(), "shrines are never used up")
	assert_eq(player.interact(), shrine)
	assert_eq(heals.size(), 2)
	assert_eq(shrine.uses, 2)
	_done()


func test_saving_at_the_shrine_records_the_shrine_and_its_location() -> void:
	Game.state.chapter = 2
	player.interact()
	shrine.menu.handle_input(_action(&"ui_accept"))
	var info := SaveSystem.slot_info(1)
	assert_eq(info["status"], SaveSystem.STATUS_OK)
	assert_eq(info["location_key"], "LOCATION_FIELD_TEST")
	var raw: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(SaveSystem.slot_path(1)))
	assert_eq((raw["meta"] as Dictionary)["shrine_id"], "save_shrine_test")
	assert_eq(SaveSystem.load_from_slot(1).flags.get("save_shrine_used"), true, "the flag is in the save")
	_done()


func test_shrine_without_its_menu_still_restores_the_party() -> void:
	shrine.opens_menu = false
	assert_eq(shrine.rest(), null)
	assert_eq(heals.size(), 1)
	assert_false(shrine.is_menu_open())
	assert_false(zone.get_tree().paused)
	_done()


func test_instance_flag_is_set_too() -> void:
	shrine.sets_flag = &"test_flag"
	Game.set_flag(&"test_flag", false)
	shrine.opens_menu = false
	assert_true(shrine.try_interact())
	assert_true(bool(Game.get_flag(&"test_flag")), "a story shrine's own flag (e.g. ch02_saved_once)")
	assert_true(bool(Game.get_flag(&"save_shrine_used")))
	_done()


func test_prompt_and_flags_are_localized_and_declared() -> void:
	assert_eq(shrine.prompt_key, SaveShrine.DEFAULT_PROMPT_KEY)
	assert_ne(tr(shrine.prompt_key), shrine.prompt_key, "prompt has a loc entry")
	assert_ne(tr(SaveShrine.RESTORED_KEY), SaveShrine.RESTORED_KEY)
	assert_true(Game.registry.is_declared(&"save_shrine_used"))
	assert_true(Game.registry.is_declared(&"ch02_saved_once"), "Haluna's shrine flag")
	_done()


func test_shrine_light_is_bound_and_still() -> void:
	var field := shrine.get_node("Visual/BoundGlimmer") as GlimmerField
	assert_eq(field.get_mode(), GlimmerState.Mode.MACHINE, "shrines are bound light")
	assert_false(field.follow_scene_intensity, "visible in daylight zones (hymn_glimmer.a = 0)")
	assert_false(field.follow_global_focus, "bound motes never gather")
	var cfg: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(GLIMMER_CONFIG))
	var bound := Color(str((cfg["colors"] as Dictionary)["machine"]))
	assert_true(field.current_color().is_equal_approx(bound), "glimmer_bound teal")
	var mesh := (shrine.get_node("Visual/Core") as MeshInstance3D).mesh as PrimitiveMesh
	var mat := mesh.material as StandardMaterial3D
	assert_true(mat.emission_enabled)
	assert_true(mat.emission.is_equal_approx(bound), "the salt-glass core glows glimmer_bound")
	_done()


func test_teleport_network_is_a_stub() -> void:
	assert_eq(shrine.network_id, &"save_shrine_test")
	assert_eq(ShrineNetwork.loaded_shrines().get(&"save_shrine_test"), shrine, "registered while loaded")
	assert_eq(shrine.teleport_destinations(), [] as Array[StringName])
	assert_false(shrine.request_teleport(&"anywhere"))
	assert_false(ShrineNetwork.is_attuned(&"save_shrine_test"))
	_done()
	assert_false(ShrineNetwork.loaded_shrines().has(&"save_shrine_test"), "unregistered on exit")


func _action(action: StringName) -> InputEventAction:
	var e := InputEventAction.new()
	e.action = action
	e.pressed = true
	return e


func _done() -> void:
	EventBus.party_full_heal_requested.disconnect(_on_heal)
	EventBus.save_shrine_used.disconnect(_on_used)
	EventBus.disconnect(FieldEvents.INTERACTED, _on_interacted)
	_host().remove_child(zone)
	zone.free()
	assert_false((Engine.get_main_loop() as SceneTree).paused, "freeing an open menu unpauses")
	var dir := DirAccess.open(TEST_DIR)
	if dir != null:
		for f in dir.get_files():
			DirAccess.remove_absolute(TEST_DIR.path_join(f))
		DirAccess.remove_absolute(TEST_DIR)
	SaveSystem.save_dir = _saved_dir
	Game.state = _saved_state


func _host() -> Node:
	return (Engine.get_main_loop() as SceneTree).current_scene
