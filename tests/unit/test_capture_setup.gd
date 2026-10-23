extends TestCase
## M1-QA-04: the per-shot setup block of the screenshot capture (tests/screenshots/capture_setup.gd).
## Headless, so global shader parameters are only checked for their error path (the dummy renderer
## keeps no globals); the real capture run exercises them.


func _host() -> Node:
	return (Engine.get_main_loop() as SceneTree).current_scene


func _scene() -> Node3D:
	var root := Node3D.new()
	root.name = "ShotRoot"
	var light := OmniLight3D.new()
	light.name = "Lamp"
	root.add_child(light)
	var cam := Camera3D.new()
	cam.name = "Cam"
	root.add_child(cam)
	_host().add_child(root)
	return root


func test_validate_accepts_known_keys_and_rejects_typos() -> void:
	var ok := CaptureSetup.new({"globals": {}, "nodes": {"Lamp": {"visible": false}}, "viewport": {}, "time_scale": 0})
	assert_eq(ok.validate(), "")
	assert_true(CaptureSetup.new({}).is_empty())
	assert_ne(CaptureSetup.new({"global": {}}).validate(), "", "unknown key")
	assert_ne(CaptureSetup.new({"nodes": {"Lamp": 1}}).validate(), "", "node entry must be an object")
	assert_ne(CaptureSetup.new({"time_scale": "0"}).validate(), "", "time_scale must be a number")
	assert_ne(CaptureSetup.new({"time_scale": -1.0}).validate(), "", "negative time_scale")


func test_coerce_converts_json_to_the_target_type() -> void:
	assert_eq(CaptureSetup.coerce(1.0, 2), 2.0)
	assert_eq(typeof(CaptureSetup.coerce(1.0, 2)), TYPE_FLOAT)
	assert_eq(CaptureSetup.coerce(3, 4.0), 4)
	assert_eq(typeof(CaptureSetup.coerce(3, 4.0)), TYPE_INT)
	assert_eq(CaptureSetup.coerce(true, 0), false)
	assert_eq(CaptureSetup.coerce(Vector3.ZERO, [1, 2, 3]), Vector3(1, 2, 3))
	assert_eq(CaptureSetup.coerce(Vector2i.ZERO, [4.0, 5.0]), Vector2i(4, 5))
	assert_eq(CaptureSetup.coerce(Vector4.ZERO, [1, 0, 0, 0.5]), Vector4(1, 0, 0, 0.5))
	assert_eq(CaptureSetup.coerce(Color.BLACK, "#7FC6D9"), Color("#7FC6D9"))
	assert_eq(CaptureSetup.coerce(Color.BLACK, [0.5, 0.25, 1.0]), Color(0.5, 0.25, 1.0))
	assert_eq(CaptureSetup.coerce(&"a", "b"), &"b")
	assert_eq(typeof(CaptureSetup.coerce(&"a", "b")), TYPE_STRING_NAME)


func test_nodes_are_set_held_against_the_scene_and_restored() -> void:
	var root := _scene()
	var lamp := root.get_node("Lamp") as OmniLight3D
	var setup := CaptureSetup.new(
		{"nodes": {"Lamp": {"light_energy": 3, "light_color": "#ff8000"}, ".": {"visible": false}}}
	)
	assert_eq(setup.attach(root), "")
	assert_eq(lamp.light_energy, 3.0)
	assert_eq(lamp.light_color, Color("#ff8000"))
	assert_false(root.visible)
	lamp.light_energy = 0.5  # a rig writing its own value during _process
	setup.hold()
	assert_eq(lamp.light_energy, 3.0, "hold re-applies the manifest value")
	setup.end()
	assert_eq(lamp.light_energy, 1.0, "restored to the scene's value")
	assert_true(root.visible)
	root.free()


func test_viewport_and_time_scale_are_restored() -> void:
	var vp := _host().get_viewport()
	var taa := vp.use_taa
	var aa := vp.screen_space_aa
	var scale := Engine.time_scale
	var setup := CaptureSetup.new({"viewport": {"use_taa": false, "screen_space_aa": 1}, "time_scale": 0})
	assert_eq(setup.begin(vp), "")
	assert_false(vp.use_taa)
	assert_eq(vp.screen_space_aa, Viewport.SCREEN_SPACE_AA_FXAA)
	assert_eq(Engine.time_scale, 0.0)
	setup.end()
	assert_eq(vp.use_taa, taa)
	assert_eq(vp.screen_space_aa, aa)
	assert_eq(Engine.time_scale, scale)


func test_unknown_node_property_or_global_fails_loudly() -> void:
	var root := _scene()
	var no_node := CaptureSetup.new({"nodes": {"Nope": {"visible": false}}})
	assert_ne(no_node.attach(root), "", "missing node")
	no_node.end()
	var no_prop := CaptureSetup.new({"nodes": {"Lamp": {"light_energi": 1}}})
	assert_ne(no_prop.attach(root), "", "misspelt property")
	no_prop.end()
	var bad_type := CaptureSetup.new({"nodes": {"Lamp": {"light_color": [1, 2]}}})
	assert_ne(bad_type.attach(root), "", "two numbers are not a Color")
	bad_type.end()
	var no_global := CaptureSetup.new({"globals": {"hymn_no_such_global": 1.0}})
	assert_ne(no_global.begin(_host().get_viewport()), "", "missing global")
	no_global.end()
	var bad_global := CaptureSetup.new({"globals": {"hymn_sun_direction": [0, 1]}})
	assert_ne(bad_global.begin(_host().get_viewport()), "", "two numbers are not a vec3")
	bad_global.end()
	assert_eq(Engine.time_scale, 1.0)
	root.free()


func test_declared_globals_are_accepted() -> void:
	var setup := CaptureSetup.new({"globals": {"hymn_wind_time": 40, "hymn_sun_direction": [0, 1, 0]}})
	assert_eq(setup.begin(_host().get_viewport()), "")
	setup.hold()
	setup.end()


func test_shots_manifest_setups_are_valid() -> void:
	var manifest: Variant = JSON.parse_string(FileAccess.get_file_as_string("res://tests/screenshots/shots.json"))
	assert_true(manifest is Dictionary)
	for shot: Variant in (manifest as Dictionary).get("shots", []):
		var spec: Variant = (shot as Dictionary).get("setup", {})
		assert_true(spec is Dictionary, "%s: setup must be an object" % shot["id"])
		if spec is Dictionary:
			assert_eq(CaptureSetup.new(spec as Dictionary).validate(), "", String(shot["id"]))
