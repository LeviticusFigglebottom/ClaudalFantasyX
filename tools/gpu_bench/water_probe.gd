class_name WaterProbe
extends Node
## Water look probe for sun-relative artefacts (M1-RND-08). Needs a real GPU and window:
##   godot --path . --audio-driver Dummy --disable-vsync res://tools/gpu_bench/water_probe.tscn -- \
##     --camera=Cameras/Horizon --sun-elev=5 --sun-rel-az=180 --png=C:/abs/out.png
## Loads water_test.tscn, places the sun --sun-elev degrees up at --sun-rel-az degrees (clockwise) from
## the camera's heading (180 = straight behind the camera, so the anti-solar point lies on the sea),
## applies the --preset (default high) at --res (default 2560x1440), renders --frames frames and saves
## the last. Prints the anti-solar pixel and the peak and mean luminance in a --radius px disc around
## it: a NaN there blooms into a white disc, a healthy sea stays dark.
##   --set=name=value,...   shader parameters on the water material (bools true/false)
##   --scene=water|undertow  water_test.tscn (default) or undertow_test.tscn (dusk mood, its storm ocean)

const SCENE := "res://game/levels/_tests/water/water_test.tscn"
const UNDERTOW_SCENE := "res://game/levels/_tests/undertow/undertow_test.tscn"
const DEFAULT_RES := "2560x1440"
const ANTI_SOLAR_PROBE_M := 2000.0

var _opts: Dictionary = {}


func _ready() -> void:
	_run.call_deferred()


func _run() -> void:
	_opts = _args()
	DisplayServer.window_set_vsync_mode(DisplayServer.VSYNC_DISABLED)
	var win := get_window()
	win.borderless = true
	win.position = DisplayServer.screen_get_position(win.current_screen)
	var wh := str(_opts.get("res", DEFAULT_RES)).split("x")
	win.size = Vector2i(int(wh[0]), int(wh[1]))
	var undertow := str(_opts.get("scene", "water")) == "undertow"
	var rig := (load(UNDERTOW_SCENE if undertow else SCENE) as PackedScene).instantiate()
	add_child(rig)
	var cam := rig.get_node(NodePath(str(_opts.get("camera", "Cameras/Horizon")))) as Camera3D
	cam.make_current()
	for i in 3:
		await get_tree().process_frame
	# Camera heading as an azimuth clockwise from north (-Z), east = +X (WaterTestRig convention).
	var fwd := -cam.global_transform.basis.z
	var heading := rad_to_deg(atan2(fwd.x, -fwd.z))
	var elev := float(_opts.get("sun-elev", 5.0))
	var az := fposmod(heading + float(_opts.get("sun-rel-az", 180.0)), 360.0)
	var water: WaterSurface
	if undertow:
		var ut := rig as UndertowTestRig
		var dusk := ut.moods[UndertowTestRig.MOOD_DUSK] as Dictionary
		dusk["elevation"] = elev
		dusk["azimuth"] = az
		ut.call("_apply_mood", UndertowTestRig.MOOD_DUSK)
		water = ut.water
	else:
		var wt := rig as WaterTestRig
		wt.sun_elevation_deg = elev
		wt.sun_azimuth_deg = az
		wt.call("_apply_mood", false)
		water = wt.water
	for pair in str(_opts.get("set", "")).split(",", false):
		var kv := pair.split("=", true, 1)
		var v: Variant = str_to_var(kv[1])
		water.material.set_shader_parameter(kv[0], v if v != null else kv[1])
	var gs := GraphicsSettings.new()
	gs.set_preset(str(_opts.get("preset", "high")))
	var env_node := rig.find_children("*", "WorldEnvironment", true, false)
	gs.apply_current(get_viewport(), (env_node[0] as WorldEnvironment).environment if env_node.size() > 0 else null)
	for i in int(_opts.get("frames", 90)):
		await RenderingServer.frame_post_draw
	var img := get_viewport().get_texture().get_image()
	img.convert(Image.FORMAT_RGB8)
	var sun_dir := WaterTestRig.direction_from_angles(elev, az)
	# The anti-solar point on screen: the view direction pointing away from the sun.
	var p := cam.unproject_position(cam.global_position - sun_dir * ANTI_SOLAR_PROBE_M)
	p *= Vector2(img.get_size()) / get_viewport().get_visible_rect().size
	var stats := _disc_stats(img, Vector2i(p), int(_opts.get("radius", 24)))
	print(
		(
			"WATER_PROBE heading %.1f sun elev %.1f az %.1f anti-solar px (%d, %d) peak %.3f mean %.3f"
			% [heading, elev, az, int(p.x), int(p.y), stats.x, stats.y]
		)
	)
	if _opts.has("png"):
		img.save_png(str(_opts["png"]))
	get_tree().quit()


## Peak and mean luminance (0..1, sRGB-encoded) in a disc of `radius` px around `c`.
static func _disc_stats(img: Image, c: Vector2i, radius: int) -> Vector2:
	var peak := 0.0
	var total := 0.0
	var n := 0
	for y in range(c.y - radius, c.y + radius + 1):
		for x in range(c.x - radius, c.x + radius + 1):
			if x < 0 or y < 0 or x >= img.get_width() or y >= img.get_height():
				continue
			if Vector2(x - c.x, y - c.y).length() > radius:
				continue
			var l := img.get_pixel(x, y).get_luminance()
			peak = maxf(peak, l)
			total += l
			n += 1
	return Vector2(peak, total / maxf(1.0, n))


func _args() -> Dictionary:
	var out := {}
	for a in OS.get_cmdline_user_args():
		var kv := a.trim_prefix("--").split("=", true, 1)
		out[kv[0]] = kv[1] if kv.size() > 1 else true
	return out
