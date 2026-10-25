extends TestCase
## M3-ENV-03: the Pemakar kit preview (game/levels/_tests/pemakar_kit/). It dresses the town from the
## generated layout (kit pieces with their slot materials and LOD chains, the Lanternfall boats, lamps,
## far lights and the boats on the sea) and lights it in the two sub-frames of pemakar.md §0: `dusk`
## (ch05_dusk) and `night` (the colour script's ch05 festival frame).

const SCENE := "res://game/levels/_tests/pemakar_kit/pemakar_kit_preview.tscn"
const LAYOUT := "res://game/levels/_tests/pemakar_kit/pemakar_preview_layout.json"
const MOODS := "res://game/levels/_tests/pemakar_kit/pemakar_preview_moods.json"
const MATERIALS := "res://assets/environments/kits/pemakar/materials"
const PLUME := "res://game/shaders/environment/env_ash_plume.gdshader"


func test_night_mood_is_the_colour_script_frame() -> void:
	var moods: Dictionary = PemakarKitPreview.load_json(MOODS)["moods"]
	var night: Dictionary = moods["night"]
	assert_eq(float(night["time_of_day_h"]), 20.0, "ch05 festival night 20:00")
	assert_eq(float(night["sun"]["elevation_deg"]), -18.0, "ch05 sun elevation")
	assert_eq(float(night["sea_glow"]), 0.08, "ch05 sea-glow")
	assert_eq(String(night["lights"]["SkyFill"]["color"]), "#3A4A6A", "ch05 fill")
	assert_eq(float(night["lights"]["SkyFill"]["energy"]), 0.25, "ch05 fill energy")
	assert_false(bool(night["lights"]["Afterglow"]["visible"]), "no afterglow at 20:00")
	var dusk: Dictionary = moods["dusk"]
	assert_true(float(dusk["time_of_day_h"]) < 20.0, "the arrival comes first: the light declines")
	assert_true(float(dusk["sea_glow"]) < float(night["sea_glow"]), "the sea-glow grows into the night")


func test_direction_from_angles_uses_compass_bearings() -> void:
	var north := PemakarKitPreview.direction_from_angles(0.0, 0.0)
	assert_between(north.z, -1.0001, -0.9999, "azimuth 0 is north (-Z)")
	var east := PemakarKitPreview.direction_from_angles(0.0, 90.0)
	assert_between(east.x, 0.9999, 1.0001, "azimuth 90 is east (+X)")
	var below := PemakarKitPreview.direction_from_angles(-18.0, 0.0)
	assert_between(below.y, sin(deg_to_rad(-18.0)) - 1e-4, sin(deg_to_rad(-18.0)) + 1e-4, "below the horizon")


func test_preview_dresses_the_layout_and_switches_mood() -> void:
	var layout := PemakarKitPreview.load_json(LAYOUT)
	var root := (Engine.get_main_loop() as SceneTree).current_scene
	var preview := (load(SCENE) as PackedScene).instantiate() as PemakarKitPreview
	root.add_child(preview)
	assert_eq(preview.lamps.size(), (layout["lights"] as Array).size(), "one OmniLight3D per layout light")
	assert_eq(preview.boats.multimesh.instance_count, (layout["boats"]["transforms"] as Array).size(), "boats")
	assert_eq(preview.far_lights.multimesh.instance_count, (layout["far_lights"]["points"] as Array).size())
	assert_eq(preview.sea_lights.multimesh.instance_count, (layout["sea_lights"]["points"] as Array).size())
	var pieces := 0
	for n: String in preview.placed:
		if not n.begins_with("frangipani"):
			pieces += int(preview.placed[n])
	assert_eq(pieces, (layout["pieces"] as Array).size(), "every layout piece placed")
	assert_eq(preview.applied_mood(), &"night")
	var night_env := preview.world_environment.environment
	preview.mood = &"dusk"
	assert_eq(preview.applied_mood(), &"dusk")
	assert_true(preview.world_environment.environment != night_env, "dusk has its own environment")
	var afterglow := preview.get_node("Lights/Afterglow") as DirectionalLight3D
	assert_true(afterglow.visible, "the afterglow is up at dusk")
	assert_between(float(ShaderGlobals.get_value(&"hymn_time_of_day")), 19.0, 19.2, "19:05")
	root.remove_child(preview)  # _exit_tree puts the globals back
	preview.free()


func test_kit_materials_load_on_their_shaders() -> void:
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
	var plume := load(MATERIALS.path_join("kit_plume.tres")) as ShaderMaterial
	assert_eq(plume.shader.resource_path, PLUME, "the plume draws with the in-repo ash-plume shader")


func test_preview_cameras_are_camera_shots() -> void:
	var scene := (load(SCENE) as PackedScene).instantiate()
	var cams := scene.get_node("Cameras").get_children()
	assert_eq(cams.size(), 7, "the design notes' preview shots (pemakar.md §5 ◆)")
	for c: Node in cams:
		var sc := c as HalunaShotCamera
		assert_true(sc != null and sc.shot != null, "%s is driven by a CameraShot" % c.name)
	scene.free()
