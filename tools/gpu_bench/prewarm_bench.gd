class_name PrewarmBench
extends Node
## Scene-entry hitch benchmark (M1-RND-07): how long the first frames of a scene take, with and
## without ShaderPrewarm, on a real GPU. Run it in a fresh process per measurement; clear the
## project's shader caches first for a cold start (user://shader_cache, user://vulkan):
##   godot --path . --audio-driver Dummy --disable-vsync res://tools/gpu_bench/prewarm_bench.tscn -- \
##     --scene=res://game/levels/_tests/water/water_test.tscn --prewarm --label=cold_prewarm --csv=C:/abs.csv
## The scene is loaded from disk first (file I/O is not counted). With --prewarm, ShaderPrewarm runs
## for the scene and the bench waits for it. Then the scene is added, the --preset (default high) is
## applied, and the wall time of each of --frames frames is recorded: max, count over the SPEC 4.2
## 50 ms budget, and the first frames.

const DEFAULT_FRAMES := 180
const HITCH_MS := 50.0
const FIRST_FRAMES := 5
const US_PER_MS := 1000.0
const CSV_HEADER := "label,scene,prewarm,preset,res,frames,max_ms,over_50ms,mean_ms,first_frames_ms,prewarm_max_ms"

var _opts: Dictionary = {}


func _ready() -> void:
	_run.call_deferred()


func _run() -> void:
	_opts = _args()
	DisplayServer.window_set_vsync_mode(DisplayServer.VSYNC_DISABLED)
	var win := get_window()
	win.borderless = true
	win.position = DisplayServer.screen_get_position(win.current_screen)
	var wh := str(_opts.get("res", "1920x1080")).split("x")
	win.size = Vector2i(int(wh[0]), int(wh[1]))
	var scene_path := str(_opts.get("scene", ""))
	var packed := load(scene_path) as PackedScene
	if packed == null:
		printerr("PREWARM_BENCH cannot load %s" % scene_path)
		get_tree().quit(2)
		return
	var gs := GraphicsSettings.new()
	gs.set_preset(str(_opts.get("preset", "high")))
	gs.apply_current(get_viewport(), null)
	for i in 3:
		await RenderingServer.frame_post_draw
	var prewarm_max := 0.0
	if _opts.has("prewarm"):
		var pw := ShaderPrewarm.spawn(scene_path, self)
		var stats: Dictionary = await pw.finished
		prewarm_max = float(stats.get("max_frame_ms", 0.0))
	var scene := packed.instantiate()
	add_child(scene)
	var envs := scene.find_children("*", "WorldEnvironment", true, false)
	gs.apply_current(get_viewport(), (envs[0] as WorldEnvironment).environment if envs.size() > 0 else null)
	var times := PackedFloat64Array()
	var last := Time.get_ticks_usec()
	for i in int(_opts.get("frames", DEFAULT_FRAMES)):
		await RenderingServer.frame_post_draw
		var now := Time.get_ticks_usec()
		times.append(float(now - last) / US_PER_MS)
		last = now
	var over := 0
	var total := 0.0
	var peak := 0.0
	for t in times:
		over += int(t > HITCH_MS)
		total += t
		peak = maxf(peak, t)
	var first := PackedStringArray()
	for i in mini(FIRST_FRAMES, times.size()):
		first.append("%.1f" % times[i])
	var row := [
		str(_opts.get("label", "")),
		scene_path.get_file().get_basename(),
		str(_opts.has("prewarm")),
		str(_opts.get("preset", "high")),
		str(_opts.get("res", "1920x1080")),
		str(times.size()),
		"%.1f" % peak,
		str(over),
		"%.2f" % (total / maxf(1.0, times.size())),
		" ".join(first),
		"%.1f" % prewarm_max,
	]
	print("PREWARM_BENCH " + " | ".join(row))
	if _opts.has("csv"):
		var path := str(_opts["csv"])
		var is_new := not FileAccess.file_exists(path)
		var f := FileAccess.open(path, FileAccess.READ_WRITE if not is_new else FileAccess.WRITE)
		f.seek_end()
		if is_new:
			f.store_line(CSV_HEADER)
		f.store_line(",".join(row))
	get_tree().quit()


func _args() -> Dictionary:
	var out := {}
	for a in OS.get_cmdline_user_args():
		var kv := a.trim_prefix("--").split("=", true, 1)
		out[kv[0]] = kv[1] if kv.size() > 1 else true
	return out
