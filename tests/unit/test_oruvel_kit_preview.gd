extends TestCase
## M3-ENV-07: the Oruvel raft-town kit preview (game/levels/_tests/oruvel_kit/). The rig is HalunaMood at the colour
## script's `ch01` frame (10:30, sun 58 deg / 120 deg, #FFEFE1 at 3.0, exposure 0.65, lut_ch01_raft); the sea is the
## validated `lagoon_clear` look at x2.0; both layouts name only kit pieces whose materials load on their shaders;
## every camera is a HalunaShotCamera driven by the layout's shot; nothing in the kit emits light (every lamp is out).

const LAYOUT := "res://game/levels/_tests/oruvel_kit/oruvel_layout.json"
const DROWNED := "res://game/levels/_tests/oruvel_kit/oruvel_drowned_layout.json"
## M3-ENV-08B: the Seventh Terrace (the Brightwater ferry kit's pieces) moored and crewed at the outer mooring.
const TERRACE := "res://game/levels/_tests/oruvel_kit/oruvel_seventh_terrace_layout.json"
const SCENE := "res://game/levels/_tests/oruvel_kit/oruvel_preview.tscn"
const WATER := "res://game/levels/_tests/oruvel_kit/oruvel_water_material.tres"
const ENVIRONMENT := "res://game/levels/_tests/oruvel_kit/oruvel_ch01_environment.tres"
const MATERIALS := "res://assets/environments/kits/oruvel/materials"
const WEATHERING := "res://game/shaders/environment/env_weathering.gdshader"
const LUT := "res://assets/environments/arenas/oruvel_raft_morning/lut_ch01_raft.png"
## M3-ENV-07B: the storm frame.
const STORM_ENVIRONMENT := "res://game/levels/_tests/oruvel_kit/oruvel_storm_environment.tres"
const STORM_LUT := "res://assets/environments/kits/oruvel/lut_ch01_storm.png"


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
	assert_true(_pieces_exist(TERRACE) >= 8, "the Seventh Terrace at the outer mooring")


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


# ---- M3-ENV-07B: the storm --------------------------------------------------------------------


func test_storm_frame_is_the_stand_in() -> void:
	var env := load(STORM_ENVIRONMENT) as Environment
	assert_eq(env.adjustment_color_correction.resource_path, STORM_LUT, "lut_ch01_storm")
	assert_true(env.adjustment_color_correction is Texture3D, "the LUT imports as a 3D texture")
	var scene := (load(SCENE) as PackedScene).instantiate()
	var rig := scene as OruvelPreview
	assert_true(rig != null, "the preview's root is OruvelPreview")
	assert_eq(rig.phase, OruvelPreview.PHASE_DAY, "the scene is authored in the day (the baselines' frame)")
	assert_eq(rig.storm_environment.resource_path, STORM_ENVIRONMENT, "the storm frame")
	assert_true(rig.storm_waves != null and rig.storm_waves.components.size() >= 3, "the storm swell")
	assert_true((scene.get_node("Cameras/O17") as Camera3D).far > 18000.0, "O17 reaches the Undertow")
	assert_between((scene.get_node("Cameras/O01") as Camera3D).far, 5999.0, 6001.0, "the day views are untouched")
	scene.free()


func test_storm_state_swaps_pieces_and_lights_the_beacon() -> void:
	var root := (Engine.get_main_loop() as SceneTree).current_scene
	var dresser := HalunaDresser.new()  # never in the tree: it would dress the default layout
	dresser.layout = {
		"kit_dir": "res://assets/environments/kits/oruvel/",
		"materials_dir": "res://assets/environments/kits/oruvel/materials/",
		"states":
		{
			"storm":
			{
				"hide": [{"piece": "plank_bridge", "at": [1.0, 2.0], "y": 0.8}],
				"pieces": [{"piece": "plank_bridge_broken", "at": [1.0, 2.0], "y": 0.8, "yaw_deg": 0.0}],
			}
		},
		"storm_lights": [{"id": "kell_beacon", "at": [0.0, 5.0, 0.0], "color": "#FFB466", "energy": 3.0}],
	}
	var intact := dresser.instance_piece("plank_bridge")
	intact.position = Vector3(1.0, 0.8, 2.0)
	dresser.add_child(intact)
	var rig := OruvelPreview.new()
	rig.dresser = dresser
	rig.undertow_enabled = false
	root.add_child(rig)
	assert_true(rig.state_root() == null, "a day scene is never touched")
	rig.phase = OruvelPreview.PHASE_STORM
	var state := rig.state_root()
	assert_true(state != null and state.visible and state.get_child_count() == 1, "the broken bridge is placed")
	assert_false(intact.visible, "the bridge it replaces is hidden")
	var lamp := rig.get_node(NodePath(String(OruvelPreview.LIGHTS_ROOT) + "/kell_beacon")) as OmniLight3D
	assert_true(lamp != null and lamp.is_visible_in_tree(), "Kell's beacon is lit")
	assert_eq(lamp.light_volumetric_fog_energy, 0.0, "the fog-lamp rule")
	rig.phase = OruvelPreview.PHASE_DAY
	assert_false(state.visible, "back to the day: the storm hides")
	assert_true(intact.visible, "and the bridge stands again")
	assert_false(lamp.is_visible_in_tree(), "the beacon is out")
	rig.free()
	dresser.free()


func test_split_rig_composes_the_pen_at_rest_and_matches_the_state() -> void:
	var layout := HalunaDresser._load_json(LAYOUT)
	var rig := OruvelPreview.pen_rig(layout)
	var sections: Array = rig["sections"]
	assert_eq(sections.size(), 3, "three sections")
	var state: Array = layout["states"]["storm"]["pieces"]
	for s: Dictionary in sections:
		var hinge: Array = s["hinge"]
		var rest := OruvelPreview.section_transform(s, 0.0, 3.7)
		assert_true(
			rest.origin.is_equal_approx(Vector3(hinge[0], hinge[1], hinge[2])), "%s rests at its hinge" % s["piece"]
		)
		assert_true(rest.basis.is_equal_approx(Basis.IDENTITY), "%s: no turn at rest, whatever the swell" % s["piece"])
		var open := OruvelPreview.section_transform(s, 1.0, 0.0)
		var placed: Dictionary = {}
		for spec: Dictionary in state:
			if (
				spec["piece"] == s["piece"]
				and CorrowPreview.piece_transform(spec).origin.distance_to(rest.origin) < 3.0
			):
				placed = spec
		assert_false(placed.is_empty(), "%s is in the state at the pen" % s["piece"])
		var t := CorrowPreview.piece_transform(placed)
		assert_true(t.origin.distance_to(open.origin) < 0.002, "%s: the state's pose is the rig's at 1" % s["piece"])
		var turn := (t.basis.x - open.basis.x).length() + (t.basis.y - open.basis.y).length()
		assert_true(turn < 0.001, "%s: and its turn (the layout rounds to 0.001)" % s["piece"])
