class_name AaShimmerBench
extends Node
## Alpha-tested foliage shimmer under each anti-aliasing mode (M1-RND-07). Real GPU, real window:
##   godot --path . --audio-driver Dummy --disable-vsync res://tools/gpu_bench/aa_shimmer.tscn -- \
##     --aa=fxaa --out=C:/abs/dir [--preset=low --camera=Cameras/Wide --res=1920x1080]
## vegetation_test.tscn with its wind frozen (the scene default), the --preset applied with only
## "aa" overridden, and the camera yawing by --pan-deg per frame (default 0.01 deg, about 0.2 px at
## 1080p): any frame-to-frame change is temporal aliasing, not motion. After --warmup frames it saves
## --frames consecutive frames (f00.png ...) and prints the GPU median; tools/gpu_bench/aa_shimmer.py
## turns them into a flicker index.
## Ghosting with the wind on (M1-RND-15): --wind sets the scene's `animate_wind` (the vegetation test;
## Haluna's mood rig always runs its weather clock) and --scene/--camera pick another scene. Run under
## --fixed-fps 30 with --pan-deg=0, once with --aa=taa and once with --aa=none: the frames then show
## the same wind instants, and `aa_shimmer.py --ghost <taa_dir> <ref_dir>` measures the trail.

const SCENE := "res://game/levels/_tests/vegetation/vegetation_test.tscn"

var _opts: Dictionary = {}


func _ready() -> void:
	_run.call_deferred()


func _run() -> void:
	_opts = _args()
	var out := str(_opts.get("out", ""))
	DirAccess.make_dir_recursive_absolute(out)
	DisplayServer.window_set_vsync_mode(DisplayServer.VSYNC_DISABLED)
	var win := get_window()
	win.borderless = true
	win.position = DisplayServer.screen_get_position(win.current_screen)
	var wh := str(_opts.get("res", "1920x1080")).split("x")
	win.size = Vector2i(int(wh[0]), int(wh[1]))
	var scene := (load(str(_opts.get("scene", SCENE))) as PackedScene).instantiate()
	if _opts.has("wind") and "animate_wind" in scene:
		scene.set("animate_wind", true)
	add_child(scene)
	if _opts.has("undertow-half"):
		for st in scene.find_children("*", "", true, false):
			if st is UndertowStorm:
				(st as UndertowStorm).half_res_body_scale = float(_opts["undertow-half"])
	var cam := scene.get_node(NodePath(str(_opts.get("camera", "Cameras/Wide")))) as Camera3D
	cam.make_current()
	await get_tree().process_frame
	var gs := GraphicsSettings.new()
	gs.set_preset(str(_opts.get("preset", "low")))
	gs.set_override("aa", str(_opts.get("aa", "fxaa")))
	var envs := scene.find_children("*", "WorldEnvironment", true, false)
	gs.apply_current(get_viewport(), (envs[0] as WorldEnvironment).environment if envs.size() > 0 else null)
	var rid := get_viewport().get_viewport_rid()
	RenderingServer.viewport_set_measure_render_time(rid, true)
	var step := deg_to_rad(float(_opts.get("pan-deg", 0.01)))
	for i in int(_opts.get("warmup", 120)):
		cam.rotate_y(step)
		await RenderingServer.frame_post_draw
	var gpu := PackedFloat64Array()
	for i in int(_opts.get("frames", 30)):
		cam.rotate_y(step)
		await RenderingServer.frame_post_draw
		gpu.append(RenderingServer.viewport_get_measured_render_time_gpu(rid))
		var img := get_viewport().get_texture().get_image()
		img.convert(Image.FORMAT_RGB8)
		img.save_png(out.path_join("f%02d.png" % i))
	gpu.sort()
	print(
		(
			"AA_SHIMMER aa %s preset %s gpu median %.3f ms"
			% [_opts.get("aa", "fxaa"), _opts.get("preset", "low"), gpu[gpu.size() / 2]]
		)
	)
	get_tree().quit()


func _args() -> Dictionary:
	var out := {}
	for a in OS.get_cmdline_user_args():
		var kv := a.trim_prefix("--").split("=", true, 1)
		out[kv[0]] = kv[1] if kv.size() > 1 else true
	return out
