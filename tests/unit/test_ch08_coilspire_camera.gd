extends TestCase
## M3-C04-1226 (act1-chapters' playthrough, field POI stills): inside the Coilspire the hub orbit sits in the spire's
## wall, in the keeper's hut it sits in the spire, and on the gallery the beacon stands between it and the ring. The
## layout's camera volumes take each of those places: the hut, one per tier on the spire's axis (its open well) from
## the tier's floor to the next one's, and the gallery's south and north halves (the great key is on the north).

const COILSPIRE := "res://game/levels/ch08/coilspire/coilspire.tscn"

var zone: GreyboxZone


func test_each_place_inside_the_spire_has_its_volume() -> void:
	_open()
	_assert_in(&"Tier1", zone.spawn_marker(&"SpireBase").position, "the hall")
	_assert_in(&"Tier2", zone.spawn_marker(&"Tier2").position, "tier 2's landing")
	_assert_in(&"Tier3", _trigger(&"key_t3_seized"), "tier 3's seized key")
	_assert_in(&"Tier4", zone.spawn_marker(&"Tier4").position, "tier 4's landing")
	_assert_in(&"Tier4", _trigger(&"crown"), "the climb to the crown")
	_assert_in(&"KeepersHut", _trigger(&"hearth"), "the hearth")
	_assert_in(&"GallerySouth", zone.spawn_marker(&"Gallery").position, "the gallery door")
	_assert_in(&"GalleryNorth", _trigger(&"great_key"), "the great key")
	_done()


func test_the_headland_keeps_the_orbit() -> void:
	_open()
	for spawn: StringName in [&"PathFoot", &"PathMid"]:
		var p := zone.spawn_marker(spawn).position
		for v in zone.get_node(^"CameraVolumes").get_children():
			assert_false((v as CameraVolume).contains_point(p), "%s is in no volume (%s)" % [spawn, v.name])
	_done()


func _assert_in(volume: StringName, p: Vector3, what: String) -> void:
	var v := zone.get_node(NodePath("CameraVolumes/%s" % volume)) as CameraVolume
	assert_true(v != null and v.contains_point(p), "%s is in %s" % [what, volume])


func _trigger(id: StringName) -> Vector3:
	return (zone.get_node(NodePath("Triggers/%s" % id)) as Node3D).position


func _open() -> void:
	zone = (load(COILSPIRE) as PackedScene).instantiate() as GreyboxZone
	zone.story.autostart = false
	_host().add_child(zone)
	zone.set_process(false)
	zone.director.auto_update = false
	zone.player.set_physics_process(false)
	if zone.encounters != null:
		zone.encounters.set_physics_process(false)


func _done() -> void:
	if zone != null and is_instance_valid(zone):
		_host().remove_child(zone)
		zone.free()
	zone = null


func _host() -> Node:
	return (Engine.get_main_loop() as SceneTree).current_scene
