class_name WaterBench
extends Node
## Water cost benchmark and look-debug harness (M1-RND-01). Needs a real renderer (ADR 0009):
##   godot-render --path . --audio-driver Dummy --fixed-fps 60 --disable-vsync \
##     res://game/levels/_tests/water/water_bench.tscn -- [options]
## Options:
##   --camera=Cameras/Lagoon      shot camera (path under the test scene root)
##   --cost                       run every configuration in CONFIGS and print a cost table
##   --set=name=value,...         one look-debug configuration (shader params; bools as true/false)
##   --quality=low|medium|high|ultra   tier for --set
##   --png=/abs/file.png          save the last frame of --set
## Timing (--cost): COST_ROUNDS interleaved rounds. Per round, after WARMUP_FRAMES, the CPU time
## this process spends per frame over MEASURE_FRAMES (lavapipe rasterises in its own threads, so
## other load on the machine does not inflate it); the minimum round is reported. The numbers
## rank features relative to each other; they are not GPU milliseconds (docs/kb/tech/water.md).

const SCENE := "res://game/levels/_tests/water/water_test.tscn"
const WARMUP_FRAMES := 6
const MEASURE_FRAMES := 8
const COST_ROUNDS := 2
## /proc/self/stat: utime and stime are fields 14 and 15, i.e. indices 11 and 12 after the
## ")" that ends the command name; Linux clock ticks are 100 Hz (USER_HZ).
const STAT_UTIME := 11
const STAT_STIME := 12
const MS_PER_TICK := 10.0
const US_PER_MS := 1000.0
const QUALITY_NAMES := {
	"low": WaterSurface.Quality.LOW,
	"medium": WaterSurface.Quality.MEDIUM,
	"high": WaterSurface.Quality.HIGH,
	"ultra": WaterSurface.Quality.ULTRA,
}
## name, tier, water visible, shader overrides.
const CONFIGS: Array[Dictionary] = [
	{"name": "no water", "quality": "high", "water": false, "set": {}},
	{"name": "low", "quality": "low", "water": true, "set": {}},
	{"name": "medium", "quality": "medium", "water": true, "set": {}},
	{"name": "high", "quality": "high", "water": true, "set": {}},
	{"name": "ultra", "quality": "ultra", "water": true, "set": {}},
	{"name": "high - ssr", "quality": "high", "water": true, "set": {"use_ssr": false}},
	{"name": "high - caustics", "quality": "high", "water": true, "set": {"use_caustics": false}},
	{"name": "high - foam", "quality": "high", "water": true, "set": {"use_foam": false}},
	{"name": "high - refraction", "quality": "high", "water": true, "set": {"use_refraction": false}},
	{"name": "high - detail normals", "quality": "high", "water": true, "set": {"use_detail_normals": false}},
	{"name": "high - sss", "quality": "high", "water": true, "set": {"use_sss": false}},
	{
		"name": "high - all optional",
		"quality": "high",
		"water": true,
		"set":
		{
			"use_ssr": false,
			"use_caustics": false,
			"use_foam": false,
			"use_refraction": false,
			"use_detail_normals": false,
			"use_sss": false,
		},
	},
]

var _scene: WaterTestRig


func _ready() -> void:
	_run.call_deferred()


func _run() -> void:
	var opts := _args()
	_scene = (load(SCENE) as PackedScene).instantiate() as WaterTestRig
	add_child(_scene)
	var cam := _scene.get_node_or_null(NodePath(str(opts.get("camera", "Cameras/Lagoon")))) as Camera3D
	if cam != null:
		cam.make_current()
	if opts.has("no-sun-shadow"):
		_scene.sun.shadow_enabled = false
	RenderingServer.viewport_set_measure_render_time(get_viewport().get_viewport_rid(), true)
	if opts.has("cost"):
		print("BENCH %s, %s" % [opts.get("camera", "Cameras/Lagoon"), RenderingServer.get_video_adapter_name()])
		# Interleaved rounds, keeping each configuration's fastest round: other processes on a
		# shared machine only ever add time, so the minimum is the least-contended estimate.
		var best: Array[float] = []
		best.resize(CONFIGS.size())
		best.fill(INF)
		for round_i in COST_ROUNDS:
			for i in CONFIGS.size():
				var c := CONFIGS[i]
				var r := await _measure(str(c["quality"]), bool(c["water"]), c["set"] as Dictionary)
				best[i] = minf(best[i], r.z)
		for i in CONFIGS.size():
			print(
				(
					"BENCH %-24s cpu(min of %d) %7.1f ms/frame  water %+7.1f ms"
					% [CONFIGS[i]["name"], COST_ROUNDS, best[i], best[i] - best[0]]
				)
			)
	else:
		var overrides := _parse_set(str(opts.get("set", "")))
		var r := await _measure(str(opts.get("quality", "high")), not opts.has("hide-water"), overrides)
		print("BENCH wall %.1f ms gpu %.1f ms cpu %.1f ms" % [r.x, r.y, r.z])
		if opts.has("png"):
			var img := get_viewport().get_texture().get_image()
			img.convert(Image.FORMAT_RGB8)
			img.save_png(str(opts["png"]))
	get_tree().quit()


# Returns Vector2(mean wall ms, mean measured GPU ms).
func _measure(quality: String, water_visible: bool, overrides: Dictionary) -> Vector3:
	var water := _scene.water
	water.quality = QUALITY_NAMES.get(quality, WaterSurface.Quality.HIGH)
	water.visible = water_visible
	for key in ["use_ssr", "use_caustics", "use_foam", "use_refraction", "use_detail_normals", "use_sss"]:
		water.material.set_shader_parameter(key, true)
	for key: String in overrides:
		water.material.set_shader_parameter(key, overrides[key])
	for i in WARMUP_FRAMES:
		await RenderingServer.frame_post_draw
	var rid := get_viewport().get_viewport_rid()
	var gpu := 0.0
	var start := Time.get_ticks_usec()
	var cpu0 := _cpu_ticks()
	for i in MEASURE_FRAMES:
		await RenderingServer.frame_post_draw
		gpu += RenderingServer.viewport_get_measured_render_time_gpu(rid)
	var wall := float(Time.get_ticks_usec() - start) / US_PER_MS / MEASURE_FRAMES
	var cpu := float(_cpu_ticks() - cpu0) * MS_PER_TICK / MEASURE_FRAMES
	return Vector3(wall, gpu / MEASURE_FRAMES, cpu)


# User + system CPU time of this process in clock ticks (Linux /proc/self/stat fields 14 and 15).
# lavapipe rasterises in this process's threads, so this is the work done, whatever else runs.
func _cpu_ticks() -> int:
	# procfs reports length 0, so read line-wise rather than with get_file_as_string().
	var f := FileAccess.open("/proc/self/stat", FileAccess.READ)
	if f == null:
		return 0
	var stat := f.get_line()
	var fields := stat.substr(stat.rfind(")") + 2).split(" ")
	if fields.size() < STAT_STIME + 1:
		return 0
	return int(fields[STAT_UTIME]) + int(fields[STAT_STIME])


func _args() -> Dictionary:
	var out := {}
	for a in OS.get_cmdline_user_args():
		var kv := a.trim_prefix("--").split("=", true, 1)
		out[kv[0]] = kv[1] if kv.size() > 1 else true
	return out


func _parse_set(text: String) -> Dictionary:
	var out := {}
	for pair in text.split(",", false):
		var kv := pair.split("=", true, 1)
		if kv.size() != 2:
			continue
		var v: Variant = str_to_var(kv[1])
		out[kv[0]] = v if v != null else kv[1]
	return out
