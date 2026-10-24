extends TestCase
## M3-ENV-10: the Coilspire temple kit preview (game/levels/_tests/coilspire_kit/). Its rig puts the two lighting
## phases of coilspire.md §0 on the scene (the colour script's `ch08` frame outside, the kit's
## `ch08_coilspire_int` inside), lights the beacon, the braziers, the keeping flame and the crown's grate from the
## layout (none of them lighting the volumetric fog: the Lead's fog-lamp rule); the layout names only kit pieces
## whose materials load on their shaders.

const LAYOUT := "res://game/levels/_tests/coilspire_kit/coilspire_layout.json"
const SCENE := "res://game/levels/_tests/coilspire_kit/coilspire_preview.tscn"
const INTERIOR := "res://game/levels/_tests/coilspire_kit/coilspire_int_environment.tres"
const MATERIALS := "res://assets/environments/kits/coilspire/materials"
const WEATHERING := "res://game/shaders/environment/env_weathering.gdshader"
const BRONZE := "res://game/shaders/environment/env_bronze.gdshader"


func test_fires_follow_the_layout_and_never_light_the_fog() -> void:
	var layout := HalunaDresser._load_json(LAYOUT)
	var beacon := CoilspirePreview.build_lights(layout, "fire_lights", "fire_light_color", CoilspirePreview.BEACON)
	assert_eq(beacon.get_child_count(), 1, "the beacon")
	var light := beacon.get_child(0) as OmniLight3D
	assert_eq(light.light_color, Color("#E0702E"), "ember_orange, as Corrow's beacon")
	assert_true(light.position.y > 80.0, "on top of the spire on its headland")
	var hearths := CoilspirePreview.build_lights(
		layout, "hearth_lights", "hearth_light_color", CoilspirePreview.HEARTHS
	)
	assert_eq(hearths.get_child_count(), (layout["hearth_lights"] as Array).size(), "one light per entry")
	assert_true(hearths.get_child_count() >= 6, "four braziers, the keeping flame and the crown's grate")
	for group: Node3D in [beacon, hearths]:
		for l: OmniLight3D in group.get_children():
			assert_false(l.shadow_enabled, "accents, not keys: no shadows")
			assert_eq(l.light_volumetric_fog_energy, 0.0, "no lamp lights the fog")
	beacon.free()
	hearths.free()


func test_storm_phase_is_the_colour_script_frame() -> void:
	var storm: Array = CoilspirePreview.PHASES[CoilspirePreview.PHASE_STORM]
	assert_eq(storm[0], 30.0, "ch08 sun elevation")
	assert_eq(storm[1], 250.0, "ch08 sun azimuth")
	assert_eq(storm[2], Color("#FFE4CE"), "ch08 key")
	assert_eq(storm[3], 2.0, "ch08 key energy")
	assert_eq(storm[5], 0.03, "ch08 volumetric haze")
	var interior := load(INTERIOR) as Environment
	assert_between(interior.tonemap_exposure, 1.0, 2.0, "the interior is exposed for a dark well")
	var amb := interior.ambient_light_color
	assert_true(amb.g > amb.r and amb.b > amb.r, "the copper green-cyan fill")


func test_phase_switch_swaps_the_environment() -> void:
	var root := (Engine.get_main_loop() as SceneTree).current_scene
	var rig := CoilspirePreview.new()
	var sun := DirectionalLight3D.new()
	rig.add_child(sun)
	rig.sun = sun
	var we := WorldEnvironment.new()
	var outside := Environment.new()
	outside.tonemap_exposure = 0.8
	we.environment = outside
	rig.add_child(we)
	rig.world_environment = we
	rig.interior_environment = load(INTERIOR) as Environment
	root.add_child(rig)
	assert_between(we.environment.tonemap_exposure, 0.79, 0.81, "storm: the exterior frame")
	assert_between(sun.light_energy, 1.99, 2.01, "the ch08 key")
	rig.phase = CoilspirePreview.PHASE_INTERIOR
	assert_between(we.environment.tonemap_exposure, 1.0, 2.0, "interior: the copper frame")
	assert_between(sun.light_energy, 1.99, 2.01, "the same sun, through the slits")
	rig.phase = CoilspirePreview.PHASE_STORM
	assert_between(we.environment.tonemap_exposure, 0.79, 0.81, "and back")
	var toward := sun.global_basis.z
	assert_between(toward.y, sin(deg_to_rad(29.0)), sin(deg_to_rad(31.0)), "sun at 30 deg")
	rig.free()


func test_layout_pieces_exist_and_materials_load() -> void:
	var layout := HalunaDresser._load_json(LAYOUT)
	assert_false(layout.is_empty(), "layout parses")
	var kit_dir := String(layout["kit_dir"])
	var seen := {}
	for spec: Dictionary in layout["pieces"]:
		seen[String(spec["piece"])] = true
	for piece: String in seen:
		assert_true(ResourceLoader.exists(kit_dir + piece + ".glb"), "piece %s exists" % piece)
	for piece: String in ["coilspire_shell", "coilspire_flues", "coilspire_tiers", "beacon_basket", "flue_key_wheel"]:
		assert_true(seen.has(piece), "the preview places %s" % piece)
	var count := 0
	for f in DirAccess.get_files_at(MATERIALS):
		if not f.ends_with(".tres"):
			continue
		var mat := load(MATERIALS.path_join(f)) as Material
		assert_true(mat != null, "%s loads" % f)
		if mat is ShaderMaterial:
			var path := (mat as ShaderMaterial).shader.resource_path
			assert_true(path == WEATHERING or path == BRONZE, "%s draws with a kit shader" % f)
		count += 1
	assert_true(count >= 16, "kit materials present (%d)" % count)


func test_preview_cameras_are_camera_shots() -> void:
	var scene := (load(SCENE) as PackedScene).instantiate()
	var cams := scene.get_node("Cameras").get_children()
	assert_eq(cams.size(), 8, "the design notes' preview views (coilspire.md §4)")
	for c: Node in cams:
		var sc := c as HalunaShotCamera
		assert_true(sc != null and sc.shot != null, "%s is driven by a CameraShot" % c.name)
	scene.free()
