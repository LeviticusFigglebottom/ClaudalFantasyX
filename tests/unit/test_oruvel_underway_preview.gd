extends TestCase
## M3-ENV-05: the Oruvel Underway kit preview (game/levels/_tests/oruvel_underway_kit/). Its rig lights each shot
## for the depth of its subject (the sun and the ambient through the rig's own water, red first) and for its area
## (open, interior, deep: oruvel_underway.md §0), hangs Rhen's lantern per shot, never writes the rig data cache
## that every UnderwaterRig shares, and the layout names only kit pieces whose materials load on their shaders.

const LAYOUT := "res://game/levels/_tests/oruvel_underway_kit/oruvel_underway_layout.json"
const SCENE := "res://game/levels/_tests/oruvel_underway_kit/oruvel_underway_preview.tscn"
const MATERIALS := "res://assets/environments/kits/oruvel_underway/materials"
const WEATHERING := "res://game/shaders/environment/env_weathering.gdshader"


func test_transmittance_drains_red_first() -> void:
	var rig := OruvelUnderwayPreview.new()
	var surface := rig.transmittance(0.0)
	assert_between(surface.x, 0.999, 1.001, "no water, no loss")
	var deep := rig.transmittance(22.0)
	assert_true(deep.x < deep.y and deep.x < deep.z, "red goes first")
	assert_between(deep.y, 0.4, 0.8, "green keeps about half at the terrace")
	rig.free()


func test_tinted_key_is_teal_at_the_terrace() -> void:
	var rig := OruvelUnderwayPreview.new()
	var key := Color("#FFEFE1")
	var at_depth := OruvelUnderwayPreview.tinted(key, rig.transmittance(21.0))
	assert_true(at_depth.r < at_depth.g, "the sun at 21 m is teal, not warm")
	assert_true(at_depth.b > at_depth.r, "blue outlasts red")
	rig.free()


func test_apply_shot_hangs_the_lantern_and_lights_the_area() -> void:
	var root := (Engine.get_main_loop() as SceneTree).current_scene
	var rig := OruvelUnderwayPreview.new()
	var sun := DirectionalLight3D.new()
	sun.light_color = Color("#FFEFE1")
	rig.add_child(sun)
	rig.sun = sun
	var we := WorldEnvironment.new()
	we.environment = Environment.new()
	rig.add_child(we)
	rig.world_environment = we
	var lamp := Node3D.new()
	rig.add_child(lamp)
	rig.lantern = lamp
	var dresser := HalunaDresser.new()  # not in the tree: only its layout is read
	dresser.layout = {
		"shots": {"U04": {"lantern": [1.0, -20.0, 2.0], "area": "interior", "depth_m": 21.0}},
	}
	rig.dresser = dresser
	root.add_child(rig)
	rig.apply_shot(&"U04")
	assert_eq(lamp.global_position, Vector3(1.0, -20.0, 2.0), "the lantern hangs where the layout says")
	assert_eq(rig.area, OruvelUnderwayPreview.AREA_INTERIOR)
	assert_between(we.environment.ambient_light_energy, 0.21, 0.23, "interior ambient")
	assert_true(sun.light_color.r < sun.light_color.g, "the key is tinted by 21 m of water")
	rig.apply_shot(&"U99")
	assert_eq(rig.area, OruvelUnderwayPreview.AREA_INTERIOR, "an unlisted camera changes nothing")
	rig.free()
	dresser.free()


func test_the_rig_data_cache_is_never_written() -> void:
	var before := float((UnderwaterRig.load_data()["optics"] as Dictionary)["light_reference"])
	var scene := (load(SCENE) as PackedScene).instantiate() as OruvelUnderwayPreview
	var root := (Engine.get_main_loop() as SceneTree).current_scene
	root.add_child(scene)
	scene.area = OruvelUnderwayPreview.AREA_DEEP
	var after := float((UnderwaterRig.load_data()["optics"] as Dictionary)["light_reference"])
	assert_eq(after, before, "the shared cache keeps its light reference")
	var own := float((scene.rig.data["optics"] as Dictionary)["light_reference"])
	assert_true(own > before, "the preview's private copy is scaled for the deep area")
	scene.free()


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
			assert_eq((mat as ShaderMaterial).shader.resource_path, WEATHERING, "%s: the weathering stack" % f)
		count += 1
	assert_true(count >= 25, "kit materials present (%d)" % count)


func test_preview_cameras_are_camera_shots() -> void:
	var scene := (load(SCENE) as PackedScene).instantiate()
	var cams := scene.get_node("Cameras").get_children()
	assert_eq(cams.size(), 7, "the design notes' preview shots (oruvel_underway.md §4 ◆)")
	for c: Node in cams:
		var sc := c as HalunaShotCamera
		assert_true(sc != null and sc.shot != null, "%s is driven by a CameraShot" % c.name)
	scene.free()
