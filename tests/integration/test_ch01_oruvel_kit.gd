extends TestCase
## Ch1's Oruvel wears env-art's zone dressing (M3-ENV-738, mounted by M3-ENV-740; ZoneKitDressing, ADR 0200) over
## its greybox gameplay: the greybox meshes hide, the kit's ch01 frame lights it, and the storm swaps in env-art's
## storm frame and back. The Seventh Terrace is the Brightwater kit's own ship (her name-board is O07's insert and
## Ch4's derelict), and the storm takes her; the storm set and the real Undertow come up with StormWall (M3-ENV-751,
## M3-C01-100).

const ZONE := "res://game/levels/ch01/oruvel/oruvel.tscn"
const MIN_PIECES := 30
const KEPT: Array[StringName] = []
## The keel-hull's and the dive raft's (O10 frames the dive raft's).
const MIN_GULLS := 2
## O07's aim: the name-board stands within NAME_BOARD_M of it (env-art places her from the SeventhTerrace block).
const NAME_BOARD := Vector3(-36.6, 1.65, -5.8)
const NAME_BOARD_M := 1.0
const SEA_Y := -0.8
const TOLERANCE := 0.01

var zone: Ch01OruvelZone
var saved_flags: Dictionary


func before_each() -> void:
	saved_flags = Game.state.flags.duplicate(true)
	Game.state.flags.erase(&"ch01_gulls_cried")  # an earlier test's storm would bring the zone up in it


func _load() -> void:
	zone = (load(ZONE) as PackedScene).instantiate() as Ch01OruvelZone
	_host().add_child(zone)
	zone.director.auto_update = false
	zone.player.set_physics_process(false)


func _host() -> Node:
	var tree := Engine.get_main_loop() as SceneTree
	return tree.current_scene if tree.current_scene != null else tree.root


func _done() -> void:
	_host().remove_child(zone)
	zone.free()
	Game.state.flags = saved_flags


func test_the_town_is_dressed_over_the_greybox() -> void:
	_load()
	var dressing := zone.get_node(^"Dressing")
	assert_true(dressing.find_children("*", "MeshInstance3D", true, false).size() >= MIN_PIECES, "the kit is placed")
	var greybox := zone.get_node(^"Greybox")
	for block: Node in greybox.get_children():
		var mesh := block.get_node_or_null(^"Mesh") as Node3D
		if mesh == null:
			continue
		var kept := StringName(block.name) in KEPT
		if kept:
			assert_true(
				mesh.visible or not (block as Node3D).visible,
				"%s (a story block) is not hidden by the kit" % block.name
			)
		elif block.name in [&"Commons", &"ScaleHull", &"NetPen", &"LowHull"]:
			assert_false(mesh.visible, "%s's greybox mesh hides under the kit" % block.name)
	# The low hull C1-13 cuts loose is the kit's outrigger, drifting clear with its block.
	assert_true((dressing as ZoneKitDressing).followers("LowHull").size() >= 1, "the low hull follows its block")
	var water := zone.get_node(^"Water") as Node3D
	assert_between(zone.get_node(^"Tide").get(&"water_height_y"), SEA_Y - TOLERANCE, SEA_Y + TOLERANCE, "the waterline")
	assert_true(water != null)
	_done()


func test_the_seventh_terrace_and_the_gulls() -> void:
	_load()
	var terrace := zone.get_node(^"Dressing") as ZoneKitDressing
	assert_true(terrace.followers("SeventhTerrace").size() >= 6, "the ship's hull, rig and sails follow her block")
	var board := terrace.followers("NameBoard")
	assert_eq(board.size(), 1, "her name-board follows its block")
	assert_true(board[0].global_position.distance_to(NAME_BOARD) < NAME_BOARD_M, "where O07 looks")
	var placed: Dictionary = (zone.get_node(^"Dressing") as ZoneKitDressing).placed
	assert_true(int(placed.get("lintel_gull_open", 0)) >= MIN_GULLS, "a lintel-gull on every ridge")
	zone.set_storm(true)
	assert_false(board[0].visible or terrace.followers("SeventhTerrace")[0].visible, "the storm takes her")
	var undertow := zone.get_node_or_null(^"Undertow") as UndertowStorm
	assert_true(undertow != null and undertow.visible, "the real Undertow stands up on the horizon")
	var wall := zone.get_node(^"Greybox/StormWall/Mesh") as Node3D
	assert_false(wall.is_visible_in_tree(), "in place of its greybox wall (the slab is never drawn)")
	var storm_set := (zone.get_node(^"Dressing") as ZoneKitDressing).followers("StormWall")
	assert_true(storm_set.size() >= 6 and storm_set[0].is_visible_in_tree(), "the storm set is up with it (M3-ENV-751)")
	var reach := undertow.storm_center().distance_to(zone.field_camera.global_position)
	assert_true(zone.field_camera.far > reach, "and the camera reaches it (%.0f m)" % reach)
	zone.set_storm(false)
	_done()


func test_the_storm_swaps_the_environment_and_back() -> void:
	_load()
	var we := zone.get_node(^"WorldEnvironment") as WorldEnvironment
	var day := we.environment
	assert_true(day.background_mode == Environment.BG_SKY, "the day is the kit's sky, not the greybox colour")
	zone.set_storm(true)
	assert_ne(we.environment, day, "the storm brings env-art's storm frame")
	zone.set_storm(false)
	assert_eq(we.environment, day, "and the day comes back")
	_done()
