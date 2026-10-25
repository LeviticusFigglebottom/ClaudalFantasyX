extends TestCase
## M3-ENV-02: the Brine Shoals kit preview (game/levels/_tests/brine_shoals_kit/). Its rig puts the two
## lighting phases of brine_shoals.md §0 on the scene (the colour script's `ch06` frame and the side
## scene's `ch06_after`), lights the fires from the layout, and the layout names only kit pieces whose
## materials load on their shaders.

const LAYOUT := "res://game/levels/_tests/brine_shoals_kit/brine_shoals_layout.json"
const SCENE := "res://game/levels/_tests/brine_shoals_kit/brine_shoals_preview.tscn"
const MATERIALS := "res://assets/environments/kits/brine_shoals/materials"
const SMOKE := "res://game/shaders/environment/env_smoke_plume.gdshader"


func test_fire_lights_follow_the_layout() -> void:
	var layout := HalunaDresser._load_json(LAYOUT)
	var fires := BrineShoalsPreview.build_fire_lights(layout)
	var entries: Array = layout["fire_lights"]
	assert_eq(fires.get_child_count(), entries.size(), "one light per fire")
	assert_true(entries.size() >= 3, "the three fires and the brazier")
	for i in fires.get_child_count():
		var light := fires.get_child(i) as OmniLight3D
		var e: Array = entries[i]
		assert_true(light != null, "an OmniLight3D")
		assert_false(light.shadow_enabled, "fire lights are fill, not key: no shadows")
		assert_eq(light.light_color, Color("#E0702E"), "ember_orange")
		assert_eq(light.omni_range, float(e[4]))
	fires.free()


func test_phases_are_the_colour_script_frames() -> void:
	var raid: Array = BrineShoalsPreview.PHASES[BrineShoalsPreview.PHASE_RAID]
	assert_eq(raid[0], 35.0, "ch06 sun elevation")
	assert_eq(raid[1], 240.0, "ch06 sun azimuth")
	assert_eq(raid[2], Color("#FFD5B3"), "ch06 key")
	assert_eq(raid[3], 2.4, "ch06 key energy")
	assert_eq(raid[5], 0.02, "ch06 volumetric haze")
	var after: Array = BrineShoalsPreview.PHASES[BrineShoalsPreview.PHASE_AFTER]
	assert_true(float(after[0]) < float(raid[0]), "the side scene comes later: the sun is lower")
	assert_false(bool(after[7]), "the fires are out")


func test_phase_switch_relights_a_rig_in_the_tree() -> void:
	var root := (Engine.get_main_loop() as SceneTree).current_scene
	var rig := BrineShoalsPreview.new()
	var sun := DirectionalLight3D.new()
	rig.add_child(sun)
	rig.sun = sun
	var we := WorldEnvironment.new()
	we.environment = Environment.new()
	rig.add_child(we)
	rig.world_environment = we
	root.add_child(rig)
	assert_between(sun.light_energy, 2.39, 2.41, "raid key")
	rig.phase = BrineShoalsPreview.PHASE_AFTER
	assert_eq(sun.light_color, Color("#FFC79A"), "after key")
	assert_between(we.environment.volumetric_fog_density, 0.0119, 0.0121, "the haze thins")
	var toward := sun.global_basis.z  # the light shines along -Z: +Z points at the sun
	assert_between(toward.y, sin(deg_to_rad(23.0)), sin(deg_to_rad(25.0)), "sun at 24 deg")
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
	var count := 0
	for f in DirAccess.get_files_at(MATERIALS):
		if not f.ends_with(".tres"):
			continue
		var mat := load(MATERIALS.path_join(f)) as Material
		assert_true(mat != null, "%s loads" % f)
		if mat is ShaderMaterial:
			assert_true((mat as ShaderMaterial).shader != null, "%s has its shader" % f)
		count += 1
	assert_true(count >= 25, "kit materials present (%d)" % count)
	var smoke := load(MATERIALS.path_join("bs_smoke.tres")) as ShaderMaterial
	assert_eq(smoke.shader.resource_path, SMOKE, "the smoke draws with the in-repo plume shader")


func test_preview_cameras_are_camera_shots() -> void:
	var scene := (load(SCENE) as PackedScene).instantiate()
	var cams := scene.get_node("Cameras").get_children()
	assert_eq(cams.size(), 8, "the design notes' preview shots (brine_shoals.md §4 ◆)")
	for c: Node in cams:
		var sc := c as HalunaShotCamera
		assert_true(sc != null and sc.shot != null, "%s is driven by a CameraShot" % c.name)
	scene.free()
