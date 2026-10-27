extends TestCase
## M3-ENV-09: the Ashcrown temple kit preview (game/levels/_tests/ashcrown_kit/). Its rig places the Pemakar
## pieces the layout borrows (the plume with this kit's noon material, the open-hand gate, the lamp pillars),
## lights the hall from the layout with lamps that never light a FogVolume, and opens the exposure for the
## hall's sub-frame (`ch05_temple_int`); the layout names only kit pieces whose materials load.

const LAYOUT := "res://game/levels/_tests/ashcrown_kit/ashcrown_layout.json"
const SCENE := "res://game/levels/_tests/ashcrown_kit/ashcrown_preview.tscn"
const MATERIALS := "res://assets/environments/kits/ashcrown/materials"
const WEATHERING := "res://game/shaders/environment/env_weathering.gdshader"
const PLUME_SHADER := "res://game/shaders/environment/env_ash_plume.gdshader"
const PLUME_DAY := "res://assets/environments/kits/ashcrown/materials/ac_plume_day.tres"


func test_lights_follow_the_layout_and_never_light_fog() -> void:
	var layout := HalunaDresser._load_json(LAYOUT)
	var lights := AshcrownPreview.build_lights(layout)
	var entries: Array = layout["lights"]
	assert_eq(lights.get_child_count(), entries.size(), "one light per layout entry")
	for child: Node in lights.get_children():
		var light := child as OmniLight3D
		assert_true(light != null, "an OmniLight3D")
		assert_false(light.shadow_enabled, "the hall's lamps are shadowless")
		assert_eq(light.light_volumetric_fog_energy, 0.0, "the fog-lamp rule")
	lights.free()


func test_borrowed_pieces_are_pemakars_with_the_noon_plume() -> void:
	var layout := HalunaDresser._load_json(LAYOUT)
	var root := AshcrownPreview.build_borrowed(layout)
	assert_eq(root.get_child_count(), (layout["borrowed"] as Array).size(), "every borrowed piece loads")
	var plume := root.get_node_or_null("ash_plume") as Node3D
	assert_true(plume != null, "the plume")
	var found_day := false
	for child: Node in plume.find_children("*", "MeshInstance3D", true, false):
		var mi := child as MeshInstance3D
		var mat := mi.get_surface_override_material(0)
		if mat != null and mat.resource_path == PLUME_DAY:
			found_day = true
		assert_true(mi.visibility_range_end > 2000.0 or mi.visibility_range_begin > 2000.0, "LOD0 drawn up close")
	assert_true(found_day, "the plume wears ac_plume_day")
	assert_true(plume.position.z < -70.0, "in the crater, north of the temple")
	var gate := root.get_node_or_null("open_hand_gate") as Node3D
	assert_true(gate != null, "the open-hand gate")
	assert_between(gate.basis.get_scale().y, 1.59, 1.61, "at 1.6x")
	root.free()


func test_interior_opens_the_exposure() -> void:
	var root := (Engine.get_main_loop() as SceneTree).current_scene
	var rig := AshcrownPreview.new()
	var sun := DirectionalLight3D.new()
	rig.add_child(sun)
	rig.sun = sun
	var we := WorldEnvironment.new()
	var env := Environment.new()
	env.tonemap_exposure = 0.72
	we.environment = env
	rig.add_child(we)
	rig.world_environment = we
	root.add_child(rig)
	assert_between(we.environment.tonemap_exposure, 0.719, 0.721, "ch05_temple")
	rig.interior = true
	assert_between(we.environment.tonemap_exposure, 1.049, 1.051, "ch05_temple_int")
	rig.interior = false
	assert_between(we.environment.tonemap_exposure, 0.719, 0.721, "back to the day")
	assert_between(env.tonemap_exposure, 0.719, 0.721, "the shared resource is untouched")
	rig.free()


func test_layout_pieces_exist_and_materials_load() -> void:
	var layout := HalunaDresser._load_json(LAYOUT)
	assert_false(layout.is_empty(), "layout parses")
	var kit_dir := String(layout["kit_dir"])
	for spec: Dictionary in layout["pieces"]:
		assert_true(ResourceLoader.exists(kit_dir + String(spec["piece"]) + ".glb"), "piece %s exists" % spec["piece"])
	var count := 0
	for f in DirAccess.get_files_at(MATERIALS):
		if not f.ends_with(".tres"):
			continue
		var mat := load(MATERIALS.path_join(f)) as Material
		assert_true(mat != null, "%s loads" % f)
		if mat is ShaderMaterial:
			var path := (mat as ShaderMaterial).shader.resource_path
			assert_true(path == WEATHERING or path == PLUME_SHADER, "%s draws with a kit shader" % f)
		count += 1
	assert_true(count >= 24, "kit materials present (%d)" % count)


func test_preview_cameras_are_camera_shots() -> void:
	var scene := (load(SCENE) as PackedScene).instantiate()
	var cams := scene.get_node("Cameras").get_children()
	assert_true(cams.size() >= 7, "the design notes' preview shots (ashcrown.md §5 ◆)")
	for c: Node in cams:
		var sc := c as HalunaShotCamera
		assert_true(sc != null and sc.shot != null, "%s is driven by a CameraShot" % c.name)
	assert_true(scene.get_node_or_null("HallProbe") is ReflectionProbe, "the hall's interior ambient")
	scene.free()
