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
const CSV_HEADER := (
	"label,scene,prewarm,preset,res,frames,max_ms,over_50ms,mean_ms,first_frames_ms,prewarm_max_ms,"
	+ "prewarm_frames,prewarm_wall_max_ms,prewarm_trace_ms"
)
## Prewarm frames listed in the trace column (M1-RND-15).
## --resident: load the registry's resident entries first, as boot does (M1-RND-22).
## Prints PREWARM_START_MS: the synchronous ShaderPrewarm.start() (in the spawn frame), M1-RND-22.
const TRACE_FRAMES := 16
## Frames the --pre-scene (a field played before the transition, M1-RND-15) runs first.
const PRE_FRAMES := 120

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
	GraphicsRuntime.set_settings(gs)  # the prewarm warms this preset's tier variants (M1-RND-22)
	gs.apply_current(get_viewport(), null)
	for i in 3:
		await RenderingServer.frame_post_draw
	# --pre-scene: play a field scene first (M1-RND-15), as a battle transition always follows one.
	# The game viewport has then already run its AA and upscaler, so what the prewarm costs is the
	# incoming scene's pipelines, not the engine's first use of TAA in this process.
	if _opts.has("resident"):  # M1-RND-22: what boot loads and holds, before the field
		var t_res := Time.get_ticks_usec()
		var boot := ShaderPrewarm.spawn_resident(self, gs.preset_id)
		var boot_max := 0.0
		var prev_res := Time.get_ticks_usec()
		while is_instance_valid(boot) and boot.is_running():
			await RenderingServer.frame_post_draw
			var now_res := Time.get_ticks_usec()
			boot_max = maxf(boot_max, float(now_res - prev_res) / US_PER_MS)
			prev_res = now_res
		print(
			(
				"PREWARM_RESIDENT %d held; boot warm-up %.1f ms, worst frame %.1f ms"
				% [ShaderPrewarm.resident_count(), float(Time.get_ticks_usec() - t_res) / US_PER_MS, boot_max]
			)
		)
	if _opts.has("pre-scene"):
		var field := (load(str(_opts["pre-scene"])) as PackedScene).instantiate()
		add_child(field)
		var fenvs := field.find_children("*", "WorldEnvironment", true, false)
		gs.apply_current(get_viewport(), (fenvs[0] as WorldEnvironment).environment if fenvs.size() > 0 else null)
		for i in int(_opts.get("pre-frames", PRE_FRAMES)):
			await RenderingServer.frame_post_draw
		field.queue_free()
		await RenderingServer.frame_post_draw
	var prewarm_max := 0.0
	var trace := PackedFloat64Array()
	if _opts.has("prewarm"):
		# Wall time of every frame while the prewarm runs, the spawn frame included (M1-RND-15): what a
		# player would see under the transition fade.
		var t0 := Time.get_ticks_usec()
		var t_start := Time.get_ticks_usec()
		var pw := ShaderPrewarm.spawn(scene_path, self)
		print("PREWARM_START_MS %.1f" % (float(Time.get_ticks_usec() - t_start) / US_PER_MS))
		var done := {"stats": {}}
		pw.finished.connect(func(st: Dictionary) -> void: done["stats"] = st, CONNECT_ONE_SHOT)
		var prev := t0
		while (done["stats"] as Dictionary).is_empty():
			await RenderingServer.frame_post_draw
			var now_us := Time.get_ticks_usec()
			trace.append(float(now_us - prev) / US_PER_MS)
			prev = now_us
		prewarm_max = float((done["stats"] as Dictionary).get("max_frame_ms", 0.0))
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
		str(trace.size()),
		"%.1f" % _max(trace),
		" ".join(_fmt(trace.slice(0, TRACE_FRAMES))),
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


static func _max(a: PackedFloat64Array) -> float:
	var m := 0.0
	for v in a:
		m = maxf(m, v)
	return m


static func _fmt(a: PackedFloat64Array) -> PackedStringArray:
	var out := PackedStringArray()
	for v in a:
		out.append("%.1f" % v)
	return out


func _args() -> Dictionary:
	var out := {}
	for a in OS.get_cmdline_user_args():
		var kv := a.trim_prefix("--").split("=", true, 1)
		out[kv[0]] = kv[1] if kv.size() > 1 else true
	return out
