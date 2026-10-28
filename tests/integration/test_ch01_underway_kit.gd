extends TestCase
## M3-C01-101: Ch1's Underway wears env-art's drowned-tower kit (ZoneKitDressing, ADR 0200) over its greybox rooms,
## under a sea with the UnderwaterRig. The kit sits on the rooms' 6 m grid (slabs on the floors, bays and piers on the
## wall lines), each room is lit as at its depth in the tower, and the cut gauge wheel swaps in on its flag.

const ZONE := "res://game/levels/ch01/oruvel_underway/oruvel_underway.tscn"
const DRESSING := "res://game/levels/ch01/oruvel_underway/oruvel_underway_dressing.json"
const MIN_PIECES := 100
const SEA_Y := 10.0
const ON_LINE_M := 0.5
const FLOORS: Array[String] = ["CrownFloor", "BellFloor", "GalleryFloor", "GaugeFloor", "TinAlcove"]
const WALL_PIECES: Array[String] = ["tower_bay", "tower_bay_broken", "tower_bay_solid", "tower_pier", "hinge_door"]
const CUT_FLAG := &"ch01_cut_gauge_wheel"

var zone: Ch01UnderwayZone
var saved_flags: Dictionary


func before_each() -> void:
	saved_flags = Game.state.flags.duplicate(true)


func _load() -> void:
	zone = (load(ZONE) as PackedScene).instantiate() as Ch01UnderwayZone
	_host().add_child(zone)
	zone.director.auto_update = false
	zone.player.set_physics_process(false)


func _host() -> Node:
	var tree := Engine.get_main_loop() as SceneTree
	return tree.current_scene if tree.current_scene != null else tree.root


func _done() -> void:
	_host().remove_child(zone)
	zone.free()  # a publishing WaterSurface must go before the test returns
	Game.state.flags = saved_flags


func _blocks() -> Dictionary:
	var out := {}
	for b: Dictionary in zone.layout["blocks"]:
		out[str(b["id"])] = b
	return out


## The block's footprint [x0, z0, x1, z1], grown by `pad` metres.
func _rect(b: Dictionary, pad: float = 0.0) -> Rect2:
	var p: Array = b["pos"]
	var s: Array = b["size"]
	var r := Rect2(float(p[0]) - float(s[0]) * 0.5, float(p[2]) - float(s[2]) * 0.5, float(s[0]), float(s[2]))
	return r.grow(pad)


func test_the_tower_is_dressed_over_the_greybox_rooms() -> void:
	_load()
	var dressing := zone.get_node(^"Dressing") as ZoneKitDressing
	assert_true(dressing.get_child_count() >= MIN_PIECES, "the kit is placed")
	for block: Node in zone.get_node(^"Greybox").get_children():
		var mesh := block.get_node_or_null(^"Mesh") as Node3D
		assert_true(mesh == null or not mesh.visible, "%s's greybox mesh hides under the kit" % block.name)
	assert_eq(zone.get_node(^"Tide").get(&"water_height_y"), SEA_Y, "the sea over the crown")
	assert_true(
		(zone.get_node(^"Underwater") as UnderwaterRig).lantern == zone.lantern, "the rig's halo is Rhen's lamp"
	)
	_done()


func test_the_kit_sits_on_the_rooms_grid() -> void:
	_load()
	var blocks := _blocks()
	var walls: Array[Rect2] = []
	for id: String in blocks:
		var b: Dictionary = blocks[id]
		if id.contains("Wall"):
			walls.append(_rect(b, ON_LINE_M))
	for spec: Dictionary in HalunaDresser._load_json(DRESSING)["pieces"]:
		var at := Vector2(float(spec["at"][0]), float(spec["at"][1]))
		var name := str(spec["piece"])
		if name.begins_with("floor_slab"):
			var on_floor := false
			for id in FLOORS:
				on_floor = on_floor or _rect(blocks[id]).has_point(at)
			assert_true(on_floor, "the %s at %s lies on a greybox floor" % [name, at])
		elif name in WALL_PIECES:
			var on_wall := false
			for r in walls:
				on_wall = on_wall or r.has_point(at)
			assert_true(on_wall, "the %s at %s stands on a wall line" % [name, at])
	_done()


func test_each_room_is_lit_at_its_depth() -> void:
	_load()
	var env := (zone.get_node(^"WorldEnvironment") as WorldEnvironment).environment
	zone.player.position = Vector3(0.0, 0.0, 15.0)  # Drop, on the crown
	zone.update_room()
	assert_eq(zone.room, &"crown")
	var crown_sun := zone.sun.light_color
	var crown_ambient := env.ambient_light_energy
	zone.player.position = Vector3(80.0, 0.0, 0.0)  # GalleryAfter
	zone.update_room()
	assert_eq(zone.room, &"gallery")
	assert_true(env.ambient_light_energy < crown_ambient, "the gallery is an interior")
	assert_true(zone.sun.light_color.r < crown_sun.r, "and 22 m down the red is gone")
	for id: StringName in zone.spawn_names():
		assert_false(zone.room_at(zone.spawn_marker(id).position).is_empty(), "spawn %s is in a lit room" % id)
	_done()


func test_the_cut_gauge_wheel_swaps_in() -> void:
	Game.state.flags.erase(CUT_FLAG)
	_load()
	var dressing := zone.get_node(^"Dressing") as ZoneKitDressing
	assert_true(zone.block_shown("GaugeWheel") and not zone.block_shown("GaugeWheelCut"))
	assert_false(dressing.followers("GaugeWheelCut")[0].visible, "the cut wheel's piece waits")
	Game.set_flag(CUT_FLAG)
	assert_false(zone.block_shown("GaugeWheel"), "the cut takes the wheel")
	assert_true(dressing.followers("GaugeWheelCut")[0].visible, "and leaves its hub")
	assert_false(dressing.followers("GaugeWheel")[0].visible)
	_done()
