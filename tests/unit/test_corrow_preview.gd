extends TestCase
## M3-ENV-04: the Corrow seawall kit preview (game/levels/_tests/corrow_kit/). Its rig puts the two
## lighting phases of corrow.md §0 on the scene (the colour script's `ch08` frame and `ch08_surge`), lights
## the Coilspire beacon from the layout and raises the sea in the surge; the layout names only kit pieces
## whose materials load on their shaders.

const LAYOUT := "res://game/levels/_tests/corrow_kit/corrow_layout.json"
const SCENE := "res://game/levels/_tests/corrow_kit/corrow_preview.tscn"
const MATERIALS := "res://assets/environments/kits/corrow/materials"
const WEATHERING := "res://game/shaders/environment/env_weathering.gdshader"


func test_beacon_follows_the_layout() -> void:
	var layout := HalunaDresser._load_json(LAYOUT)
	var beacon := CorrowPreview.build_beacon_lights(layout)
	var entries: Array = layout["fire_lights"]
	assert_eq(beacon.get_child_count(), entries.size(), "one light per beacon entry")
	assert_eq(entries.size(), 1, "the Coilspire beacon")
	var light := beacon.get_child(0) as OmniLight3D
	assert_true(light != null, "an OmniLight3D")
	assert_false(light.shadow_enabled, "the beacon is an accent, not a key: no shadows")
	assert_eq(light.light_color, Color("#E0702E"), "ember_orange")
	assert_true(light.position.y > 60.0, "at the top of the spire on its headland")
	beacon.free()


func test_phases_are_the_colour_script_frames() -> void:
	var front: Array = CorrowPreview.PHASES[CorrowPreview.PHASE_FRONT]
	assert_eq(front[0], 30.0, "ch08 sun elevation")
	assert_eq(front[1], 250.0, "ch08 sun azimuth")
	assert_eq(front[2], Color("#FFE4CE"), "ch08 key")
	assert_eq(front[3], 2.0, "ch08 key energy")
	assert_eq(front[5], 0.03, "ch08 volumetric spray haze")
	var surge: Array = CorrowPreview.PHASES[CorrowPreview.PHASE_SURGE]
	assert_true(float(surge[3]) < float(front[3]), "the sun is behind the front in the surge")
	assert_true(float(surge[6]) > 1.0, "the surge floods the low town (+1.0 m)")
	assert_true(float(front[6]) < 1.0, "under the front the low town is still dry")


func test_phase_switch_relights_and_raises_the_sea() -> void:
	var root := (Engine.get_main_loop() as SceneTree).current_scene
	var rig := CorrowPreview.new()
	var sun := DirectionalLight3D.new()
	rig.add_child(sun)
	rig.sun = sun
	var we := WorldEnvironment.new()
	we.environment = Environment.new()
	rig.add_child(we)
	rig.world_environment = we
	var tide := WeatheringTide.new()
	rig.add_child(tide)
	rig.tide = tide
	root.add_child(rig)
	assert_between(sun.light_energy, 1.99, 2.01, "front key")
	assert_between(tide.water_height_y, 0.49, 0.51, "the sea under the front")
	rig.phase = CorrowPreview.PHASE_SURGE
	assert_between(sun.light_energy, 0.34, 0.36, "the sun behind the front")
	assert_between(we.environment.volumetric_fog_density, 0.059, 0.061, "the spray thickens")
	assert_between(tide.water_height_y, 1.79, 1.81, "the surge")
	var toward := sun.global_basis.z  # the light shines along -Z: +Z points at the sun
	assert_between(toward.y, sin(deg_to_rad(21.0)), sin(deg_to_rad(23.0)), "sun at 22 deg")
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
	for piece: String in ["seawall_curve", "watcher_head", "watcher_relief", "fisher_stair", "liss_hoist"]:
		assert_true(seen.has(piece), "the preview places %s" % piece)
	var count := 0
	for f in DirAccess.get_files_at(MATERIALS):
		if not f.ends_with(".tres"):
			continue
		var mat := load(MATERIALS.path_join(f)) as Material
		assert_true(mat != null, "%s loads" % f)
		if mat is ShaderMaterial:
			assert_eq((mat as ShaderMaterial).shader.resource_path, WEATHERING, "%s draws with env_weathering" % f)
		count += 1
	assert_true(count >= 16, "kit materials present (%d)" % count)


func test_preview_cameras_are_camera_shots() -> void:
	var scene := (load(SCENE) as PackedScene).instantiate()
	var cams := scene.get_node("Cameras").get_children()
	assert_eq(cams.size(), 7, "the design notes' preview shots (corrow.md §4 ◆)")
	for c: Node in cams:
		var sc := c as HalunaShotCamera
		assert_true(sc != null and sc.shot != null, "%s is driven by a CameraShot" % c.name)
	scene.free()
