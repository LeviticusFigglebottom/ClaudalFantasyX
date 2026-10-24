extends TestCase
## M3-ENV-07: the Oruvel raft-town kit preview (game/levels/_tests/oruvel_kit/). The rig is HalunaMood at the colour
## script's `ch01` frame (10:30, sun 58 deg / 120 deg, #FFEFE1 at 3.0, exposure 0.65, lut_ch01_raft); the sea is the
## validated `lagoon_clear` look at x2.0; both layouts name only kit pieces whose materials load on their shaders;
## every camera is a HalunaShotCamera driven by the layout's shot; nothing in the kit emits light (every lamp is out).

const LAYOUT := "res://game/levels/_tests/oruvel_kit/oruvel_layout.json"
const DROWNED := "res://game/levels/_tests/oruvel_kit/oruvel_drowned_layout.json"
const SCENE := "res://game/levels/_tests/oruvel_kit/oruvel_preview.tscn"
const WATER := "res://game/levels/_tests/oruvel_kit/oruvel_water_material.tres"
const ENVIRONMENT := "res://game/levels/_tests/oruvel_kit/oruvel_ch01_environment.tres"
const MATERIALS := "res://assets/environments/kits/oruvel/materials"
const WEATHERING := "res://game/shaders/environment/env_weathering.gdshader"
const LUT := "res://assets/environments/arenas/oruvel_raft_morning/lut_ch01_raft.png"


func _pieces_exist(path: String) -> int:
	var layout := HalunaDresser._load_json(path)
	assert_false(layout.is_empty(), "%s parses" % path)
	var kit_dir := String(layout["kit_dir"])
	var seen := {}
	for spec: Dictionary in layout["pieces"]:
		assert_true(spec.has("y"), "no terrain: every piece carries its height")
		seen[String(spec["piece"])] = true
	for piece: String in seen:
		assert_true(ResourceLoader.exists(kit_dir + piece + ".glb"), "piece %s exists" % piece)
	return seen.size()


func test_layouts_name_only_existing_pieces() -> void:
	assert_true(_pieces_exist(LAYOUT) >= 18, "every kit piece is in the preview")
	assert_true(_pieces_exist(DROWNED) >= 3, "the Underway's crown under the dive raft")


func test_kit_materials_load_and_none_emits() -> void:
	var count := 0
	for f in DirAccess.get_files_at(MATERIALS):
		if not f.ends_with(".tres"):
			continue
		var mat := load(MATERIALS.path_join(f)) as Material
		assert_true(mat != null, "%s loads" % f)
		if mat is ShaderMaterial:
			assert_eq((mat as ShaderMaterial).shader.resource_path, WEATHERING, "%s: the weathering stack" % f)
		elif mat is BaseMaterial3D:
			assert_false((mat as BaseMaterial3D).emission_enabled, "%s: every lamp in the town is out at 10:30" % f)
		count += 1
	assert_true(count >= 23, "kit materials present (%d)" % count)


func test_rig_is_the_colour_script_ch01_frame() -> void:
	var scene := (load(SCENE) as PackedScene).instantiate()
	var rig := scene as HalunaMood
	assert_true(rig != null, "the preview's root is the HalunaMood rig")
	assert_eq(rig.sun_elevation_deg, 58.0, "ch01 sun elevation")
	assert_eq(rig.sun_azimuth_deg, 120.0, "ch01 sun azimuth")
	assert_eq(rig.water_height_m, 0.0, "the sea at y 0 (the Underway's frame)")
	var sun := scene.get_node("Sun") as DirectionalLight3D
	assert_between(sun.light_energy, 2.99, 3.01, "ch01 key energy")
	assert_true(absf(sun.light_color.r - 1.0) < 0.01 and absf(sun.light_color.b - Color("#FFEFE1").b) < 0.01, "#FFEFE1")
	var env := (scene.get_node("WorldEnvironment") as WorldEnvironment).environment
	assert_between(env.tonemap_exposure, 0.649, 0.651, "exposure 0.65")
	assert_false(env.sdfgi_enabled, "SDFGI off (sky ambient + SSAO)")
	assert_eq(env.adjustment_color_correction.resource_path, LUT, "lut_ch01_raft")
	scene.free()


func test_sea_is_lagoon_clear_at_two() -> void:
	var water := load(WATER) as ShaderMaterial
	assert_between(float(water.get_shader_parameter(&"absorption_scale")), 1.99, 2.01, "colour script ch01: x2.0")
	assert_eq(water.get_shader_parameter(&"col_deep"), Color(0.0549, 0.2902, 0.3333, 1), "deep #0E4A55")


func test_cameras_follow_the_layout_shots() -> void:
	var layout := HalunaDresser._load_json(LAYOUT)
	var shots: Dictionary = layout["shots"]
	var scene := (load(SCENE) as PackedScene).instantiate()
	var cams := scene.get_node("Cameras").get_children()
	assert_eq(cams.size(), shots.size(), "one camera per layout shot (oruvel.md §4 ◆)")
	for c: Node in cams:
		var sc := c as HalunaShotCamera
		assert_true(sc != null and sc.shot != null, "%s is driven by a CameraShot" % c.name)
		var s: Dictionary = shots[String(c.name)]
		var eye: Array = s["eye"]
		assert_true(sc.shot.position.distance_to(Vector3(eye[0], eye[1], eye[2])) < 0.01, "%s eye" % c.name)
		assert_between(sc.shot.fov_deg, float(s["fov"]) - 0.01, float(s["fov"]) + 0.01, "%s lens" % c.name)
	scene.free()
