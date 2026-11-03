extends TestCase
## The storm fights' arenas (the human's FAST-TRACK 11-03; env-art-b, M3-ENV-1334; tools/act1/storm_arenas.py). Each
## storm arena carries the Undertow (with its far plane), a storm rim and the rain on the camera, and ArenaRainWet soaks
## its own copies of the kit's weathering materials: the sources the zones share stay dry.

const STORMS: Array[StringName] = [
	&"oruvel_raft_storm",
	&"seawall_stairhead_storm",
	&"seawall_stairhead_hoist",
	&"seawall_stairhead_surge",
	&"coilspire_headland_path",
	&"drowned_choir_storm",
]

var arena: BattleArenaRoot


func after_each() -> void:
	_close()


func _close() -> void:
	if arena != null and is_instance_valid(arena):
		arena.get_parent().remove_child(arena)
		arena.free()
	arena = null


func _open(id: StringName) -> BattleArenaRoot:
	_close()
	arena = (load(BattleArenaRoot.path_for(id)) as PackedScene).instantiate() as BattleArenaRoot
	(Engine.get_main_loop() as SceneTree).current_scene.add_child(arena)
	return arena


func test_every_storm_arena_has_the_undertow_rain_and_a_rim() -> void:
	for id in STORMS:
		var a := _open(id)
		var storm := a.get_node_or_null(^"Undertow") as UndertowStorm
		assert_true(storm != null, "%s has the Undertow" % id)
		assert_true(storm.get_node_or_null(^"FarPlane") is StormFarPlane, "%s: its far plane follows it" % id)
		assert_between(storm.rain_amount, 0.05, 1.0, "%s rains on the camera" % id)
		var rim := a.get_node_or_null(^"StormRim") as DirectionalLight3D
		assert_true(rim != null and not rim.shadow_enabled, "%s has a shadowless storm rim" % id)
		assert_true(a.get_node_or_null(^"RainWet") is ArenaRainWet, "%s is soaked" % id)
		var sun_sky := a.world_environment().environment.sky.sky_material as ShaderMaterial
		assert_eq(float(sun_sky.get_shader_parameter(&"sun_disc_energy")), 0.0, "%s shows no sun disc" % id)
	_close()


func test_rain_wet_soaks_copies_and_leaves_the_sources_dry() -> void:
	var weathering := 0
	for id in STORMS:
		var a := _open(id)
		var wet := a.get_node(^"RainWet") as ArenaRainWet
		assert_true(wet.wetted_count() > 0, "%s: some of its materials were wetted" % id)
		var pairs := wet.wet_pairs()
		for src: Material in pairs:
			var copy := pairs[src] as ShaderMaterial
			if copy == null:
				continue
			weathering += 1
			assert_between(float(copy.get_shader_parameter(&"rain_wet")), 0.01, 1.0, "%s: the copy is wet" % id)
			var dry: Variant = (src as ShaderMaterial).get_shader_parameter(&"rain_wet")
			assert_true(dry == null or float(dry) == 0.0, "%s: the kit's own material stays dry" % id)
		var used := 0
		for mi: MeshInstance3D in a.find_children("*", "MeshInstance3D", true, false):
			if mi.mesh != null:
				for i in mi.mesh.get_surface_count():
					if mi.get_active_material(i) in pairs.values():
						used += 1
		assert_true(used > 0, "%s: its surfaces wear the wet copies" % id)
	assert_true(weathering > 0, "weathering surfaces took wet copies")
	_close()
