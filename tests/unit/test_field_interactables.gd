extends TestCase
## M1-ARC-01: Interactables and touch triggers emit on the EventBus (FieldEvents) and use story
## flags only through Game.get_flag / Game.set_flag; every flag any scene names is declared.

const ZONE := "res://game/levels/_tests/field/field_test.tscn"
const SCENE_ROOT := "res://game"
const FLAG_FIELD_RE := '(requires_flag|blocked_by_flag|sets_flag) = &"([A-Za-z0-9_]+)"'
const DT := 1.0 / 60.0

var zone: Node3D
var player: FieldController
var lever: Interactable
var gate: Interactable
var saved_flags: Dictionary
var interactions: Array[Array] = []
var triggers: Array[Array] = []


func before_each() -> void:
	saved_flags = Game.state.flags.duplicate(true)
	zone = (load(ZONE) as PackedScene).instantiate() as Node3D
	_host().add_child(zone)
	(zone.get_node("CameraDirector") as FieldCameraDirector).auto_update = false
	player = zone.get_node("Player") as FieldController
	player.set_physics_process(false)
	player.set_process_unhandled_input(false)
	lever = zone.get_node("Interactables/Lever") as Interactable
	gate = zone.get_node("Interactables/CausewayGate") as Interactable
	FieldEvents.connect_interacted(_on_interacted)
	FieldEvents.connect_trigger(_on_trigger)


func _on_interacted(id: StringName, kind: StringName, payload: Dictionary) -> void:
	interactions.append([id, kind, payload])


func _on_trigger(id: StringName, payload: Dictionary) -> void:
	triggers.append([id, payload])


func test_lever_emits_on_the_bus_sets_its_flag_and_is_used_once() -> void:
	Game.set_flag(&"field_test_lever_pulled", false)
	player.global_position = lever.global_position + Vector3(0.3, -0.75, 0.3)
	assert_eq(player.nearest_interactable(), lever)
	assert_eq(player.interact(), lever)
	assert_eq(interactions.size(), 1)
	assert_eq(interactions[0][0], &"field_test_lever")
	assert_eq(interactions[0][1], Interactable.KIND_INTERACT)
	assert_eq((interactions[0][2] as Dictionary).get("note"), "test lever")
	assert_true(bool(Game.get_flag(&"field_test_lever_pulled")), "set through Game.set_flag")
	assert_eq(player.interact(), null, "once: nothing left to use")
	assert_eq(interactions.size(), 1)
	_done()


func test_once_interactable_stays_used_after_a_reload() -> void:
	Game.set_flag(&"field_test_lever_pulled", true)
	assert_false(lever.is_available(), "its flag says it was already used")
	_done()


func test_out_of_reach_does_nothing() -> void:
	player.global_position = lever.global_position + Vector3(6, -0.75, 0)
	assert_eq(player.nearest_interactable(), null)
	assert_eq(player.interact(), null)
	assert_eq(interactions.size(), 0)
	_done()


func test_required_and_blocking_flags_gate_use() -> void:
	Game.set_flag(&"field_test_lever_pulled", false)
	lever.requires_flag = &"test_flag"
	Game.set_flag(&"test_flag", false)
	assert_false(lever.is_available(), "required flag unset")
	Game.set_flag(&"test_flag", true)
	assert_true(lever.is_available())
	lever.requires_flag = &""
	lever.blocked_by_flag = &"test_flag"
	assert_false(lever.is_available(), "blocking flag set")
	_done()


func test_walking_through_the_gate_fires_the_touch_trigger_once() -> void:
	Game.set_flag(&"field_test_causeway_reached", false)
	player.global_position = gate.global_position + Vector3(0, -1.0, 3.0)
	player.input_override = Vector2(0, -1)
	for i in 240:
		player.step(DT)
	assert_true(player.global_position.z < gate.global_position.z - 1.0, "walked past the gate")
	assert_eq(triggers.size(), 1, "fired exactly once")
	assert_eq(triggers[0][0], &"field_test_causeway_gate")
	assert_true(bool(Game.get_flag(&"field_test_causeway_reached")))
	assert_false(gate.try_interact(), "a touch trigger cannot be 'used'")
	_done()


func test_every_flag_named_by_a_scene_is_declared() -> void:
	var re := RegEx.create_from_string(FLAG_FIELD_RE)
	var checked := 0
	for path in _scenes(SCENE_ROOT):
		for m in re.search_all(FileAccess.get_file_as_string(path)):
			checked += 1
			assert_true(Game.registry.is_declared(StringName(m.get_string(2))), "%s: %s" % [path, m.get_string(2)])
	assert_true(checked >= 2, "the field test zone's flags were found")
	for it: Interactable in [lever, gate]:
		for f in it.declared_flag_names():
			assert_true(Game.registry.is_declared(f), "%s uses %s" % [it.id, f])
	_done()


func test_bus_signals_are_declared_once() -> void:
	FieldEvents.ensure_signals()
	FieldEvents.ensure_signals()
	assert_true(EventBus.has_signal(FieldEvents.INTERACTED))
	assert_true(EventBus.has_signal(FieldEvents.TRIGGER_ENTERED))
	_done()


func _done() -> void:
	EventBus.disconnect(FieldEvents.INTERACTED, _on_interacted)
	EventBus.disconnect(FieldEvents.TRIGGER_ENTERED, _on_trigger)
	zone.free()
	Game.state.flags = saved_flags


func _scenes(dir_path: String) -> PackedStringArray:
	var out := PackedStringArray()
	var dir := DirAccess.open(dir_path)
	if dir == null:
		return out
	for f in dir.get_files():
		if f.ends_with(".tscn"):
			out.append(dir_path.path_join(f))
	for d in dir.get_directories():
		out.append_array(_scenes(dir_path.path_join(d)))
	return out


func _host() -> Node:
	return (Engine.get_main_loop() as SceneTree).current_scene
