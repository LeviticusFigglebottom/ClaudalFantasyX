extends TestCase
## M3-C01-100: Ch1's Oruvel wears env-art's raft-town kit (ZoneKitDressing, ADR 0200) over its greybox gameplay:
## the pieces are placed and sunk so their decks sit at the walk height, the greybox meshes hide (the story blocks
## stay), the kit's ch01 frame lights it, and the storm swaps in env-art's storm stand-in and back.

const ZONE := "res://game/levels/ch01/oruvel/oruvel.tscn"
const MIN_PIECES := 30
const KEPT: Array[StringName] = [&"SeventhTerrace", &"KellBeacon", &"LowHull"]
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
		elif block.name in [&"Commons", &"ScaleHull", &"NetPen"]:
			assert_false(mesh.visible, "%s's greybox mesh hides under the kit" % block.name)
	var water := zone.get_node(^"Water") as Node3D
	assert_between(zone.get_node(^"Tide").get(&"water_height_y"), SEA_Y - TOLERANCE, SEA_Y + TOLERANCE, "the waterline")
	assert_true(water != null)
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
