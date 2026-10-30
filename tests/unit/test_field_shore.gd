extends TestCase
## FieldShore's safety catch (big24's red: Lowlight's drowned Sanctum spawn, 6 m under its hall's water plane, was
## snapped back to the zone's previous spawn): grounded deeper than deep_water_m, the hero goes back to his last safe
## spot only when that is within teleport_m; a spawn or a teleport forgets it, and more than underwater_m under the
## surface (a seabed walk) there is no catch at all.

const ZONE := "res://game/levels/_tests/field/field_test.tscn"

var zone: Node3D
var player: FieldController
var water: WaterSurface


func before_each() -> void:
	zone = (load(ZONE) as PackedScene).instantiate() as Node3D
	_host().add_child(zone)
	player = zone.get_node("Player") as FieldController
	player.set_physics_process(false)
	water = WaterSurface.new()
	zone.add_child(water)


func test_deep_water_near_the_last_safe_spot_puts_him_back() -> void:
	var cfg := player.shore.cfg
	water.global_position = Vector3(0, float(cfg["deep_water_m"]) + 0.5, 0)  # deep, but not a seabed walk
	player.global_position = Vector3(0, 0, -5)
	player.shore.last_safe = Vector3(0.5, 0, -5)
	assert_true(player.shore.settle(player, true), "a step into deep water is undone")
	assert_eq(player.global_position, Vector3(0.5, 0, -5))
	_free()


func test_a_teleport_forgets_the_old_safe_spot() -> void:
	var cfg := player.shore.cfg
	water.global_position = Vector3(0, float(cfg["deep_water_m"]) + 0.5, 0)
	player.global_position = Vector3(0, 0, -5)
	player.shore.last_safe = Vector3(0, 0, -5 + float(cfg["teleport_m"]) + 3.0)  # the previous spawn's
	assert_false(player.shore.settle(player, true), "placed here: not snapped across the zone")
	assert_eq(player.global_position, Vector3(0, 0, -5))
	assert_true(is_nan(player.shore.last_safe.x), "the old spot is forgotten")
	_free()


func test_under_a_surface_there_is_no_catch() -> void:
	var cfg := player.shore.cfg
	water.global_position = Vector3(0, float(cfg["underwater_m"]) + 3.0, 0)  # Lowlight's Sanctum: 6 m under
	player.global_position = Vector3(0, 0, -5)
	player.shore.last_safe = Vector3(0.5, 0, -5)
	assert_false(player.shore.settle(player, true), "a seabed walk keeps its place")
	assert_eq(player.global_position, Vector3(0, 0, -5))
	_free()


func _free() -> void:
	zone.free()


func _host() -> Node:
	return (Engine.get_main_loop() as SceneTree).current_scene
