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


## M2-ENV-03: the working parts are kit pieces; the water runs (and the nacre shimmers) only where it flows.
func test_the_room_is_built_from_the_shrine_kit() -> void:
	assert_eq(level.missing_pieces, [] as Array[String], "every kit piece loads (no primitive stands in)")
	for id in level.trial.basin_ids():
		var pivot := level.basin_pivots[id] as Node3D
		assert_true(pivot.get_node_or_null(^"shrine_basin_bowl") != null, "%s's bowl is the turning part" % id)
	assert_true(level.door.get_node_or_null(^"shrine_door_valve") != null, "the shell valve sinks with the door")
	assert_true(level.charm.get_node_or_null(^"shrine_charm_net_float") != null, "the salt-glass float")
	assert_true(level.pool_water is WaterSurface and (level.pool_water as WaterSurface).river, "flowmap water")
	for key: String in level.channels:
		var w := level.channel_water(key)
		assert_true(w != null and w.river, "%s has flowmap water" % key)
		assert_eq(w.visible, level.is_channel_lit(key), "%s's water shows only while it runs" % key)
	assert_eq(_shimmer(level.channels["b1>b4"] as Node3D), 1.0, "a running channel's nacre shimmers")
	assert_eq(_shimmer(level.channels["b3>inner_pool"] as Node3D), 0.0, "a dry one does not")
	var pour := (level.basin_pivots[&"b1"] as Node3D).get_node(^"Pour") as Node3D
	assert_true(pour.visible, "b1 pours off its lip")
	assert_false((level.basin_pivots[&"b2"] as Node3D).get_node(^"Pour").visible, "b2 is dry")
	assert_true(level.gi != null and level.gi.is_in_group(&"gi_voxel"), "the hall's VoxelGI follows the GI preset")
	assert_eq(level.gi_bake_ms, -1, "no bake without a rendering device")
	_done()


func test_spill_lips_face_their_layout_bearings() -> void:
	var b := deg_to_rad(122.0)
	assert_true(level.spill_dir(&"b1", 2).is_equal_approx(Vector3(sin(b), 0.0, -cos(b))), "b1's third lip")
	assert_true(level.spill_dir(&"b4", 0).is_equal_approx(Vector3.FORWARD), "north")
	assert_true(level.spill_dir(&"nowhere", 3).is_equal_approx(Vector3.LEFT), "the compass default")
	var fallback := level._piece("no_such_piece", BoxMesh.new())
	assert_true(fallback is MeshInstance3D and level.missing_pieces.has("no_such_piece"), "a primitive stands in")
	fallback.free()
	_done()


func test_turning_basins_routes_the_water_fills_the_pool_and_opens_the_door() -> void:
	var b4 := _interactable(&"basin_b4")
	assert_true(level.is_channel_lit("b1>b4"), "the water starts out round b1 and b4 (M2-FP-22)")
	assert_true(b4.try_interact(), "Rhen turns b4 away from b1")
	assert_eq(int(level.trial.rotations[&"b4"]), 0)
	assert_between(angle_difference(level.basin_yaw(&"b4"), _yaw_to_outlet(&"b4")), -0.01, 0.01, "the lip turned")
	assert_false(level.is_channel_lit("b4>b1"), "no longer back to b1")
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
	_solve(level.trial.drain())
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


func _solve(target: StringName = &"") -> void:
	if target == &"":
		target = level.trial.goal()
	var guard := 0
	while not level.trial.reaches(target) and guard < 16:
		guard += 1
		var best := &""
		var best_n := 1 << 20
		for b in level.trial.basin_ids():
			var probe := ShellShrineTrial.new(level.trial.data)
			probe.rotations = level.trial.rotations.duplicate()
			probe.rotate(b)
			var n := probe.min_turns_to(target)
			if n >= 0 and n < best_n:
				best_n = n
				best = b
		_interactable(StringName("basin_%s" % best)).try_interact()


## The nacre shimmer set on a channel's trough (the first geometry under it).
func _shimmer(node: Node3D) -> float:
	for g: Node in node.find_children("*", "GeometryInstance3D", true, false):
		return float((g as GeometryInstance3D).get_instance_shader_parameter(&"inst_shimmer"))
	return -1.0


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
