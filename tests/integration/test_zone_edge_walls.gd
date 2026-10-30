extends TestCase
## The human's playtest (2026-10-30): "you can easily fall off and start walking in the water". Oruvel's dressing
## stands invisible walls along its walkways over the water (ZoneKitDressing "edge_walls",
## assets_src/environments/zone_edges.py): every one collides, none draws, and the storm's lost bridge leaves no open
## edge (its walls collide only while the bridge is hidden).

const ZONE := "res://game/levels/ch01/oruvel/oruvel.tscn"
const MIN_WALLS := 40
const STORM_BRIDGE := "DiveBridge"
const WALL_H_M := 1.5

var zone: Ch01OruvelZone
var saved_flags: Dictionary


func before_each() -> void:
	saved_flags = Game.state.flags.duplicate(true)
	Game.state.flags.erase(&"ch01_gulls_cried")


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


func _walls() -> Array[Node]:
	var root := zone.get_node_or_null(^"Dressing/EdgeWalls")
	return root.get_children() if root != null else ([] as Array[Node])


func test_the_walkways_have_walls_and_nothing_draws() -> void:
	_load()
	var walls := _walls()
	assert_true(walls.size() >= MIN_WALLS, "%d edge walls" % walls.size())
	for w: Node in walls:
		assert_true(w is StaticBody3D, "%s is a static body" % w.name)
		assert_true(w.find_children("*", "MeshInstance3D", true, false).is_empty(), "%s draws nothing" % w.name)
		var shape := (w.get_child(0) as CollisionShape3D).shape as BoxShape3D
		assert_true(shape.size.y >= WALL_H_M, "%s stands taller than a step" % w.name)
	_done()


func test_the_storm_bridge_leaves_no_open_edge() -> void:
	_load()
	var gated: Array[CollisionShape3D] = []
	for w: Node in _walls():
		var cs := w.get_child(0) as CollisionShape3D
		var pos := (w as Node3D).position
		# The bridge's two ends: on the moorings' facing edges, across the bridge's 2 m.
		if absf(pos.z + 6.0) < 0.01 and (absf(pos.x - 35.06) < 0.01 or absf(pos.x - 40.94) < 0.01):
			gated.append(cs)
	assert_eq(gated.size(), 2, "a wall at each end of the bridge")
	for cs: CollisionShape3D in gated:
		assert_true(cs.disabled, "the bridge stands: its ends are open")
	zone.hide_block(STORM_BRIDGE)
	for cs: CollisionShape3D in gated:
		assert_false(cs.disabled, "the bridge is gone: its ends are walled")
	zone.show_block(STORM_BRIDGE)
	for cs: CollisionShape3D in gated:
		assert_true(cs.disabled, "back again: open")
	_done()
