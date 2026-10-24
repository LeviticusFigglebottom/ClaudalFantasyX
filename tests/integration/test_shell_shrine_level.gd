extends TestCase
## M2-FP-16: the Shell Shrine trial level (ShellShrineLevel) on the real data. Turning basins
## through their interactables, the channels lighting the water's path, the pool filling and the
## door opening, the side pool and the charm, the hint, and the exit to Cutscene B.

const SCENE := "res://game/levels/ch03/shell_shrine/shell_shrine.tscn"
const FIRST_VERSE := "res://game/levels/ch03/first_verse/first_verse.tscn"

var level: ShellShrineLevel
var saved_state: GameStateData
var exits: Array[String] = []


func before_each() -> void:
	saved_state = Game.state
	Game.state = GameStateData.new()
	level = (load(SCENE) as PackedScene).instantiate() as ShellShrineLevel
	level.autostart = false
	level.hand_off = func(target: String) -> void: exits.append(target)
	_host().add_child(level)
	level.set_process(false)  # time passes only through advance(); turns and the door snap
	level.director.auto_update = false
	level.player.set_physics_process(false)
	level.hint.instant = true


func test_the_room_has_its_basins_channels_pools_and_door() -> void:
	for id in level.trial.basin_ids():
		assert_true(level.basin_pivots.has(id), "basin %s" % id)
		assert_true(_interactable(StringName("basin_%s" % id)) != null, "basin %s can be turned" % id)
		assert_between(angle_difference(level.basin_yaw(id), _yaw_to_outlet(id)), -0.01, 0.01, "%s's lip" % id)
	assert_true(level.channels.size() >= level.trial.basin_ids().size(), "channels")
	assert_true(level.is_channel_lit("source>b1"), "the spring runs into the first basin")
	assert_true(level.pool_water != null and level.side_water != null and level.door != null)
	assert_false(level.pool_water.visible, "the inner pool starts empty")
	assert_true(level.side_water.visible, "the side pool starts full")
	assert_false(level.charm.visible, "the charm is hidden under the side pool")
	assert_false(_interactable(&"shrine_exit").is_available(), "the way on waits for the door")
	assert_true(level.get_viewport().get_camera_3d() == level.field_camera)
	_done()


func test_turning_basins_routes_the_water_fills_the_pool_and_opens_the_door() -> void:
	var b1 := _interactable(&"basin_b1")
	assert_true(b1.try_interact(), "Rhen turns the first basin")
	assert_eq(int(level.trial.rotations[&"b1"]), 1)
	assert_between(angle_difference(level.basin_yaw(&"b1"), _yaw_to_outlet(&"b1")), -0.01, 0.01, "the lip turned")
	assert_true(level.is_channel_lit("b1>b2"), "the water now runs to the second basin")
	_solve()
	assert_true(level.trial.reaches(level.trial.goal()))
	assert_true(level.is_channel_lit("b3>inner_pool"), "and on into the inner pool")
	assert_true(level.is_inserting(), "the water's first arrival cuts to S04")
	assert_false(level.player.accepts_input, "Rhen waits out the insert")
	var low := level.pool_water.position.y
	level.advance(float(level.trial.data["insert_sec"]) + 0.1)
	assert_false(level.is_inserting())
	assert_true(level.player.accepts_input)
	assert_true(level.pool_water.position.y > low, "the pool rises")
	level.advance(float(level.trial.data["fill_sec"]))
	assert_true(level.trial.door_open)
	assert_true(bool(Game.get_flag(&"ch03_shrine_door_open")))
	assert_true((level.door.get_node(^"Shape") as CollisionShape3D).disabled, "the door no longer blocks")
	var exit := _interactable(&"shrine_exit")
	assert_true(exit.on_touched(), "through the flooded door")
	assert_eq(exits, [FIRST_VERSE] as Array[String], "the way on is Cutscene B")
	assert_false(exit.on_touched() and exits.size() > 1, "once")
	_done()


func test_the_side_pool_drains_and_gives_the_charm() -> void:
	var take := _interactable(&"net_float_charm")
	assert_false(take.is_available(), "nothing to take while the pool is full")
	_interactable(&"basin_b1").try_interact()
	_interactable(&"basin_b2").try_interact()
	_interactable(&"basin_b2").try_interact()
	assert_true(level.trial.reaches(level.trial.drain()))
	level.advance(0.1)
	assert_true(level.trial.side_drained)
	assert_true(level.charm.visible, "the charm glints in the silt")
	assert_true(level.is_inserting(), "S05 shows it")
	level.advance(float(level.trial.data["insert_sec"]) + 0.1)
	assert_true(take.try_interact())
	assert_true(bool(Game.get_flag(&"ch03_found_net_float")), "Cutscene B's branch flag")
	assert_eq(int(Game.state.inventory.get("net_float_charm", 0)), 1, "the key item")
	assert_false(level.charm.visible)
	assert_false(take.is_available(), "once")
	_done()


func test_the_hint_plays_once_after_idling() -> void:
	var lines: Array[StringName] = []
	level.hint.line_shown.connect(func(s: DialogueStep) -> void: lines.append(s.speaker))
	level.advance(float(level.trial.data["hint_idle_sec"]) + 1.0)
	assert_eq(lines, [&"toma"] as Array[StringName], "Toma's one hint")
	level.advance(float(level.trial.data["hint_idle_sec"]) * 2.0)
	assert_eq(lines.size(), 1, "only once")
	_done()


func test_a_reload_keeps_an_open_door_and_a_drained_pool() -> void:
	_done()
	Game.state = GameStateData.new()
	Game.set_flag(&"ch03_shrine_door_open", true)
	Game.set_flag(&"ch03_side_pool_drained", true)
	before_each_keep_state()
	assert_true(level.trial.door_open)
	assert_true((level.door.get_node(^"Shape") as CollisionShape3D).disabled)
	assert_true(level.charm.visible)
	assert_true(_interactable(&"shrine_exit").is_available())
	_done()


## before_each without replacing Game.state (the reload test sets its own flags first).
func before_each_keep_state() -> void:
	level = (load(SCENE) as PackedScene).instantiate() as ShellShrineLevel
	level.autostart = false
	level.hand_off = func(target: String) -> void: exits.append(target)
	_host().add_child(level)
	level.set_process(false)
	level.director.auto_update = false
	level.player.set_physics_process(false)


func _solve() -> void:
	var guard := 0
	while not level.trial.reaches(level.trial.goal()) and guard < 16:
		guard += 1
		var best := &""
		var best_n := 1 << 20
		for b in level.trial.basin_ids():
			var probe := ShellShrineTrial.new(level.trial.data)
			probe.rotations = level.trial.rotations.duplicate()
			probe.rotate(b)
			var n := probe.min_turns_to(probe.goal())
			if n >= 0 and n < best_n:
				best_n = n
				best = b
		_interactable(StringName("basin_%s" % best)).try_interact()


func _yaw_to_outlet(id: StringName) -> float:
	var from := (level.basin_pivots[id] as Node3D).global_position
	var to := level.outlet_point(id)
	return atan2(-(to.x - from.x), -(to.z - from.z))


func _interactable(id: StringName) -> Interactable:
	for n in level.find_children("*", "Interactable", true, false):
		if (n as Interactable).id == id:
			return n as Interactable
	return null


func _done() -> void:
	if level != null and is_instance_valid(level):
		_host().remove_child(level)
		level.free()
	level = null
	Game.state = saved_state


func _host() -> Node:
	return (Engine.get_main_loop() as SceneTree).current_scene
