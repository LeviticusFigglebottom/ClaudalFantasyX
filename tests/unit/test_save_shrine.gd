extends TestCase
## M1-ARC-03: the save shrine in the save-shrine copy of the field test zone. The player uses it
## through FieldController.interact(): the party is restored (bus request), flags and location
## are set, the save menu opens over a paused field, and the teleport hook is a stub.

const ZONE := "res://game/levels/_tests/save_shrine/save_shrine_test.tscn"
const TEST_DIR := "user://test_save_shrine"
const GLIMMER_CONFIG := "res://game/data/vfx/glimmer.json"

## The kit stores colours to four places: within one 8-bit step.
const COLOR_STEP := 1.0 / 255.0

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


## Act II's heresy (M4-A2P-082): an Order shrine works until the party are heretics, then goes dark: its light out, its
## prompt and its use only the dark-shrine bark, no rest. A shrine that isn't the Order's never goes dark.
func test_an_order_shrine_goes_dark_for_heretics() -> void:
	shrine.opens_menu = false
	shrine.order = true
	assert_false(shrine.is_dark(), "before the trap the Order's shrine still answers")
	Game.set_flag(SaveShrine.HERETIC_FLAG, true)
	assert_true(shrine.is_dark())
	assert_eq(shrine.prompt_key, SaveShrine.DARK_PROMPT_KEY, "the prompt says it is dark")
	assert_eq(shrine.payload.get("dialogue", ""), SaveShrine.DARK_SCENE, "using it plays the bark")
	assert_false((shrine.get_node(^"Visual/Core") as Node3D).visible, "its bound light is out")
	assert_true(shrine.try_interact())
	assert_true(heals.is_empty(), "a dark shrine heals nothing")
	assert_true(uses.is_empty(), "and records nothing")
	assert_ne(tr(SaveShrine.DARK_PROMPT_KEY), SaveShrine.DARK_PROMPT_KEY, "the dark prompt is localized")
	assert_true(FileAccess.file_exists("res://game/data/dialogue/compiled/%s.json" % SaveShrine.DARK_SCENE))
	shrine.order = false
	Game.set_flag(SaveShrine.HERETIC_FLAG, false)
	Game.set_flag(SaveShrine.HERETIC_FLAG, true)
	assert_false(shrine.is_dark(), "a Kirru or Saltwright shrine keeps working")
	assert_eq(shrine.prompt_key, SaveShrine.DEFAULT_PROMPT_KEY)
	assert_true((shrine.get_node(^"Visual/Core") as Node3D).visible)
	Game.set_flag(SaveShrine.HERETIC_FLAG, false)
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
	# M3-ENV-101: the core is the Haluna kit's save_shrine_core piece (kit_bound_core).
	var cores := shrine.get_node("Visual/Core").find_children("*", "MeshInstance3D", true, false)
	assert_false(cores.is_empty(), "the salt-glass core is modelled")
	var core := cores[0] as MeshInstance3D
	var mat := core.get_active_material(0) as StandardMaterial3D  # the kit's surface override (AssetImportRules)
	assert_true(mat.emission_enabled)
	var off := Vector3(mat.emission.r - bound.r, mat.emission.g - bound.g, mat.emission.b - bound.b)
	assert_true(off.length() < COLOR_STEP, "the salt-glass core glows glimmer_bound")
	_done()


func test_the_shrine_joins_the_teleport_network_when_used() -> void:
	assert_eq(shrine.network_id, &"save_shrine_test")
	assert_eq(ShrineNetwork.loaded_shrines().get(&"save_shrine_test"), shrine, "registered while loaded")
	assert_false(ShrineNetwork.is_attuned(&"save_shrine_test"))
	assert_eq(shrine.teleport_destinations(), [] as Array[StringName], "the only shrine: nowhere to go")
	assert_false(shrine.request_teleport(&"anywhere"))
	shrine.opens_menu = false
	shrine.rest()
	assert_true(ShrineNetwork.is_attuned(&"save_shrine_test"), "attuned by resting (M1-ARC-06)")
	assert_eq(Game.state.attuned_shrines, [&"save_shrine_test"] as Array[StringName])
	_done()
	assert_false(ShrineNetwork.loaded_shrines().has(&"save_shrine_test"), "unregistered on exit")


func test_resting_heals_the_saved_party_and_sets_the_respawn_point() -> void:
	Game.state.party_vitals = {"rhen": {"hp": 3, "mp": 0, "statuses": ["poison", "petrify"]}, "asha": {"hp": 0}}
	shrine.opens_menu = false
	shrine.rest()
	assert_eq(Game.state.party_vitals, {}, "full HP/MP and every shrine cure (party_rest.json)")
	assert_eq(Game.state.respawn_location_id, &"field_test")
	assert_eq(Game.state.respawn_spawn, &"Shrine", "the shrine's row in locations.json")
	_done()


func test_the_save_made_at_the_shrine_continues_at_the_shrine() -> void:
	Game.state.party_vitals = {"toma": {"hp": 1}}
	player.interact()
	shrine.menu.handle_input(_action(&"ui_accept"))
	var back := SaveSystem.load_from_slot(1)
	assert_eq(back.party_vitals, {}, "the save holds the healed party")
	assert_eq(back.attuned_shrines, [&"save_shrine_test"] as Array[StringName])
	var wr := WorldReturn.new()
	var to := wr.resolve(back)
	assert_eq(to["scene"], ZONE)
	assert_eq(to["spawn"], &"Shrine")
	wr.free()
	_done()


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
