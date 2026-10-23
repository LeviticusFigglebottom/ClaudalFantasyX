extends Node
## Water look probe (M1-ART-04): renders the M1-RND-01 water test scene with one look from water_looks.json
## (a zone's water material under a colour-script frame's light) and measures the water by seabed depth.
## Needs a real renderer (ADR 0009), not --headless:
##   ~/.cache/hymn/godot-4.6.3+ds-2/godot-render --path . --audio-driver Dummy --fixed-fps 60 \
##     res://game/levels/_tests/swatches/water_look_probe.tscn -- --look=lagoon_clear --out=/abs/dir
## Optional overrides: --camera=Cameras/Lagoon | survey  --sea_glow=0  --moon=0.25  --exposure=0.65  --scale=1.0
##   --deep=#0E4A55  --scatter=#1FA3A6  --tag=name (appended to the output stem). The validation in
##   docs/kb/art/color_script.md ("Water looks") measures the Lagoon and survey views (Night for night_sea).
## Writes <out>/<look>[_<camera>].png and .json: the median on-screen sRGB per depth band, plus dry sand.
## The water test scene itself is not modified; everything is applied to the instance at runtime.

const LOOKS_PATH := "res://game/levels/_tests/swatches/water_looks.json"
const WATER_TEST := "res://game/levels/_tests/water/water_test.tscn"
const SIZE := Vector2i(960, 540)
const SETTLE_FRAMES := 16
## Sample every Nth pixel when binning by depth.
const STRIDE := 3
## Pixels below the horizon line only; rays flatter than this never reach the seabed in view.
const MIN_RAY_DOWN := 0.02
const PARAM_ABSORPTION := &"absorption_per_m"
const PARAM_SCATTER := &"col_scatter_shallow"
const PARAM_SSS := &"col_sss"
## --camera=survey: a probe-made camera 40 m up, looking 39 deg down across all four depth bands.
const SURVEY_CAMERA := "survey"
const SURVEY_FROM := Vector3(0.0, 40.0, -10.0)
const SURVEY_AT := Vector3(0.0, 0.0, -60.0)
const SURVEY_FOV_DEG := 50.0
const SURVEY_FAR_M := 4000.0


func _ready() -> void:
	_run.call_deferred()


func _run() -> void:
	var opts := _parse_args()
	var data: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(LOOKS_PATH))
	var look_id := str(opts.get("look", "lagoon_clear"))
	var look: Dictionary = (data["looks"] as Dictionary)[look_id]
	var night := bool(look.get("night", false))
	var cam_path := str(opts.get("camera", look["camera"]))
	get_window().size = SIZE

	var rig := (load(WATER_TEST) as PackedScene).instantiate() as WaterTestRig
	rig.frame_step_s = 0.0  # hold the sea still (deterministic)
	if night:
		var moon: Dictionary = look["moon"]
		rig.moon_elevation_deg = float(moon["elevation_deg"])
		rig.moon_azimuth_deg = float(moon["azimuth_deg"])
		rig.night_deep_color = Color(str(opts.get("deep", look["deep"])))
		rig.night_sea_glow = float(opts.get("sea_glow", look.get("sea_glow", 0.0)))
	else:
		var sun: Dictionary = look["sun"]
		rig.sun_elevation_deg = float(sun["elevation_deg"])
		rig.sun_azimuth_deg = float(sun["azimuth_deg"])
		rig.day_deep_color = Color(str(opts.get("deep", look["deep"])))
		rig.day_caustic_strength = float(look.get("caustics", rig.day_caustic_strength))
	var water := rig.get_node("Water") as WaterSurface
	var mat := (water.material as ShaderMaterial).duplicate() as ShaderMaterial
	var base: Array = data["base_absorption_per_m"]
	var tint: Array = look.get("absorption_tint", [1.0, 1.0, 1.0])
	var scale := float(opts.get("scale", look.get("absorption_scale", 1.0)))
	var sigma := Vector3(
		float(base[0]) * float(tint[0]), float(base[1]) * float(tint[1]), float(base[2]) * float(tint[2])
	)
	mat.set_shader_parameter(PARAM_ABSORPTION, sigma * scale)
	mat.set_shader_parameter(PARAM_SCATTER, Color(str(opts.get("scatter", look["scatter_shallow"]))))
	if look.has("sss"):
		mat.set_shader_parameter(PARAM_SSS, Color(str(look["sss"])))
	water.material = mat
	add_child(rig)

	var cam: Camera3D
	if cam_path == SURVEY_CAMERA:
		# A steep view over the lagoon, reef lip and open sea: little Fresnel sky, so every band is visible.
		cam = Camera3D.new()
		cam.fov = SURVEY_FOV_DEG
		cam.far = SURVEY_FAR_M
		rig.add_child(cam)
		cam.look_at_from_position(SURVEY_FROM, SURVEY_AT)
	else:
		cam = rig.get_node(NodePath(cam_path)) as Camera3D
	cam.make_current()
	var vp := get_viewport()
	vp.use_taa = false
	vp.screen_space_aa = Viewport.SCREEN_SPACE_AA_FXAA
	if night:
		var moon_light := rig.get_node("Moon") as DirectionalLight3D
		var moon: Dictionary = look["moon"]
		moon_light.light_color = Color(str(moon["hex"]))
		moon_light.light_energy = float(opts.get("moon", moon["energy"]))
		var env_n := (cam.environment if cam.environment != null else _world_env(rig)).duplicate() as Environment
		env_n.tonemap_exposure = float(opts.get("exposure", look["exposure"]))
		cam.environment = env_n
	else:
		var sun_light := rig.get_node("Sun") as DirectionalLight3D
		var sun: Dictionary = look["sun"]
		sun_light.light_color = Color(str(sun["hex"]))
		sun_light.light_energy = float(sun["energy"])
		var we := rig.get_node("WorldEnvironment") as WorldEnvironment
		var env := we.environment.duplicate(true) as Environment
		env.tonemap_exposure = float(opts.get("exposure", look["exposure"]))
		env.adjustment_enabled = true
		env.adjustment_saturation = float(look["saturation"])
		env.ambient_light_energy = float(look["ambient_energy"])
		var sky_mat := env.sky.sky_material as ProceduralSkyMaterial
		var sky: Dictionary = look["sky"]
		sky_mat.sky_top_color = Color(str(sky["top"]))
		sky_mat.sky_horizon_color = Color(str(sky["horizon"]))
		sky_mat.ground_horizon_color = Color(str(sky["horizon"]))
		sky_mat.ground_bottom_color = Color(str(sky["horizon"])).lerp(Color(str(sky["top"])), 0.5)
		env.fog_light_color = Color(str(sky["horizon"]))
		we.environment = env

	for i in SETTLE_FRAMES:
		await get_tree().process_frame
	await RenderingServer.frame_post_draw
	var image := vp.get_texture().get_image()
	image.convert(Image.FORMAT_RGB8)
	var out_dir := str(opts.get("out", OS.get_user_data_dir()))
	var stem := look_id if not opts.has("camera") else "%s_%s" % [look_id, cam_path.get_file().to_lower()]
	if opts.has("sea_glow"):
		stem += "_glow%s" % str(opts["sea_glow"])
	if opts.has("moon"):
		stem += "_moon%s" % str(opts["moon"])
	if opts.has("tag"):
		stem += "_" + str(opts["tag"])
	image.save_png(out_dir.path_join(stem + ".png"))
	var seabed := rig.get_node("Seabed") as LagoonSeabed
	var result := {
		"look": look_id,
		"camera": cam_path,
		"absorption_per_m": [sigma.x * scale, sigma.y * scale, sigma.z * scale],
		"bands": _bands(image, cam, seabed, data["bands_m"] as Array),
	}
	FileAccess.open(out_dir.path_join(stem + ".json"), FileAccess.WRITE).store_string(
		JSON.stringify(result, " ", false)
	)
	print("WATER PROBE %s -> %s" % [look_id, out_dir.path_join(stem + ".png")])
	get_tree().quit(0)


## Median on-screen colour per seabed depth band (depth at the point where the view ray meets the rest
## plane y = 0), plus "dry" (seabed above water). Medians keep ruins and glints from skewing a band.
func _bands(image: Image, cam: Camera3D, seabed: LagoonSeabed, bands: Array) -> Dictionary:
	var bins := {}
	for b: Array in bands:
		bins["%s-%s" % [b[0], b[1]]] = [[], [], []]
	bins["dry"] = [[], [], []]
	for y in range(0, image.get_height(), STRIDE):
		for x in range(0, image.get_width(), STRIDE):
			var o := cam.project_ray_origin(Vector2(x, y))
			var d := cam.project_ray_normal(Vector2(x, y))
			if d.y > -MIN_RAY_DOWN:
				continue
			var hit := o + d * (-o.y / d.y)
			var depth := -seabed.height_at(hit.x, hit.z)
			var key := ""
			if depth < 0.0:
				key = "dry"
			else:
				for b: Array in bands:
					if depth >= float(b[0]) and depth < float(b[1]):
						key = "%s-%s" % [b[0], b[1]]
			if key == "":
				continue
			var c := image.get_pixel(x, y)
			var arr: Array = bins[key]
			(arr[0] as Array).append(c.r)
			(arr[1] as Array).append(c.g)
			(arr[2] as Array).append(c.b)
	var out := {}
	for key: String in bins:
		var arr: Array = bins[key]
		var n := (arr[0] as Array).size()
		if n == 0:
			continue
		var med := Color(_median(arr[0]), _median(arr[1]), _median(arr[2]))
		out[key] = {"hex": "#" + med.to_html(false).to_upper(), "n": n}
	return out


func _median(values: Array) -> float:
	var v := values.duplicate()
	v.sort()
	return v[v.size() / 2]


func _world_env(rig: Node) -> Environment:
	return (rig.get_node("WorldEnvironment") as WorldEnvironment).environment


func _parse_args() -> Dictionary:
	var opts := {}
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--") and arg.contains("="):
			var kv := arg.trim_prefix("--").split("=", true, 1)
			opts[kv[0]] = kv[1]
	return opts
