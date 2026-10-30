extends TestCase
## M3-RND-21: the volumetric smoke column. Its data has a row for every preset, its shader declares what the node sets
## and runs on the held clock, its box bounds the column, and the Ch6 camp's smoke follows the Smoke block.

const SHADER := "res://game/vfx/smoke/smoke_column.gdshader"
const CH06_DRESSING := "res://game/levels/ch06/brine_shoals/brine_shoals_dressing.json"


func test_data_has_every_preset_and_the_shader_declares_the_columns_keys() -> void:
	var data := SmokeColumn.load_data()
	var quality := data["quality"] as Dictionary
	for preset in GraphicsSettings.new().preset_ids():
		assert_true(quality.has(preset), "%s has a smoke row" % preset)
		assert_true(int((quality[preset] as Dictionary)["steps"]) >= 8, "%s still reads as a column" % preset)
	var sh := load(SHADER) as Shader
	var names := sh.get_shader_uniform_list().map(func(u: Dictionary) -> String: return str(u["name"]))
	for key in SmokeColumn.FLOAT_KEYS + SmokeColumn.COLOR_KEYS + ["steps", "seed", "box_min", "box_max", "box_offset"]:
		assert_true(names.has(key), "the shader declares %s" % key)
	var code := FileAccess.get_file_as_string(SHADER)
	assert_true(code.contains("hymn_wind_time"), "the held clock drives the billows")
	assert_false(code.substr(code.find("void vertex()")).contains("TIME"), "never TIME")


func test_the_column_builds_its_box_and_follows_the_tier() -> void:
	var smoke := SmokeColumn.new()
	(Engine.get_main_loop() as SceneTree).current_scene.add_child(smoke)
	var col := smoke.column
	assert_false(col.is_empty(), "the camp profile")
	var lo := smoke.bounds_min()
	var hi := smoke.bounds_max()
	var r := float(col["top_radius_m"])
	assert_true(hi.x >= float(col["lean_m"]) + r and lo.x <= -r, "the box spans the lean and the widest radius")
	assert_eq(hi.y, float(col["height_m"]))
	assert_true((smoke.box.mesh as BoxMesh).size.is_equal_approx(hi - lo))
	assert_true(smoke.set_quality("low"))
	assert_eq(int(smoke.material.get_shader_parameter(&"steps")), 12)
	assert_true(smoke.set_quality("ultra"))
	assert_true(int(smoke.material.get_shader_parameter(&"steps")) > 12, "more steps on Ultra")
	assert_false(smoke.set_quality("nonsense"))
	smoke.free()


func test_the_camp_smoke_follows_the_smoke_block() -> void:
	var d := JSON.parse_string(FileAccess.get_file_as_string(CH06_DRESSING)) as Dictionary
	var rows := d.get("smokes", []) as Array
	assert_eq(rows.size(), 3, "the hulk and the two burned tents")
	for row: Dictionary in rows:
		assert_eq(str(row["block"]), "Smoke", "%s goes out with the evening camp" % row["name"])
	for p: Dictionary in d["pieces"]:
		assert_ne(str(p["piece"]), "smoke_plume", "no shell plume left")
