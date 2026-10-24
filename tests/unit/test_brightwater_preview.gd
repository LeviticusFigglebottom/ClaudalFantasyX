extends TestCase
## M3-ENV-08: the Brightwater ferry kit preview (game/levels/_tests/brightwater_ferry_kit/). Its rig is HalunaMood's
## night mood with the colour script's `ch04` values (the Moon, sea-glow 0.12, the ch04 Environment with the kit's
## `lut_ch04_crossing`) and the deck lanterns' lights from the layout; every lantern light keeps the volumetric fog
## dark (the Lead's fog-lamp rule); the layout names only kit pieces whose materials load.

const LAYOUT := "res://game/levels/_tests/brightwater_ferry_kit/brightwater_ferry_layout.json"
const SCENE := "res://game/levels/_tests/brightwater_ferry_kit/brightwater_ferry_preview.tscn"
const ENVIRONMENT := "res://game/levels/_tests/brightwater_ferry_kit/brightwater_ferry_ch04_environment.tres"
const LUT := "res://assets/environments/kits/brightwater_ferry/lut_ch04_crossing.png"
const MATERIALS := "res://assets/environments/kits/brightwater_ferry/materials"
const WEATHERING := "res://game/shaders/environment/env_weathering.gdshader"


func test_lamps_follow_the_layout_and_never_light_the_fog() -> void:
	var layout := HalunaDresser._load_json(LAYOUT)
	var lamps := BrightwaterFerryPreview.build_lamps(layout)
	var entries: Array = layout["lamps"]
	assert_eq(lamps.get_child_count(), entries.size(), "one light per lamp entry")
	assert_true(entries.size() >= 8, "the deck's lanterns (%d)" % entries.size())
	var shadows := 0
	for i in lamps.get_child_count():
		var light := lamps.get_child(i) as OmniLight3D
		assert_true(light != null, "an OmniLight3D")
		assert_eq(light.light_volumetric_fog_energy, 0.0, "lamp %d keeps the volumetric fog dark" % i)
		assert_eq(light.light_color, Color("#FFB16E"), "oil_lamp")
		assert_between(light.light_energy, 0.5, 1.21, "around the ch04 lamp key 1.2")
		var entry: Array = entries[i]
		assert_true(light.position.is_equal_approx(Vector3(entry[0], entry[1], entry[2])), "at its flame")
		if light.shadow_enabled:
			shadows += 1
	assert_between(shadows, 1, 3, "only a couple of lanterns cast shadows (%d)" % shadows)
	lamps.free()


func test_scene_is_the_ch04_night() -> void:
	var scene := (load(SCENE) as PackedScene).instantiate() as BrightwaterFerryPreview
	assert_true(scene != null, "the preview's root is the rig")
	assert_eq(scene.mood, HalunaMood.MOOD_NIGHT, "the night mood")
	assert_between(scene.night_sea_glow, 0.119, 0.121, "ch04 sea-glow 0.12")
	var moon := scene.get_node("Moon") as DirectionalLight3D
	assert_eq(moon.light_color, Color(0.6157, 0.7059, 0.851, 1), "the moon #9DB4D9")
	assert_true(moon.light_energy <= 2.5 * 0.12, "rule 3: the moon at most 2.5x the sea-glow")
	var env := load(ENVIRONMENT) as Environment
	assert_between(env.tonemap_exposure, 1.09, 1.11, "ch04 exposure 1.10")
	assert_true(env.adjustment_enabled, "graded")
	assert_eq(env.adjustment_color_correction.resource_path, LUT, "by the crossing's LUT")
	assert_true(load(LUT) is Texture3D, "the LUT imports as a Texture3D")
	scene.free()


func test_preview_cameras_are_camera_shots() -> void:
	var scene := (load(SCENE) as PackedScene).instantiate()
	var cams := scene.get_node("Cameras").get_children()
	assert_eq(cams.size(), 7, "the design notes' preview shots (brightwater_ferry.md §4)")
	for c: Node in cams:
		var sc := c as HalunaShotCamera
		assert_true(sc != null and sc.shot != null, "%s is driven by a CameraShot" % c.name)
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
	for piece: String in [
		"ferry_hull", "ferry_rig", "ferry_deckhouse", "ferry_awning", "ferry_cargo", "ferry_lantern", "derelict_hulk_a"
	]:
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
	assert_true(count >= 20, "kit materials present (%d)" % count)


func test_lantern_glass_glows_oil_lamp() -> void:
	var glass := load(MATERIALS.path_join("bf_lamp_glass.tres")) as StandardMaterial3D
	assert_true(glass != null and glass.emission_enabled, "the lit chimney emits")
	assert_eq(glass.emission.to_html(false), "ffb16e", "oil_lamp")
