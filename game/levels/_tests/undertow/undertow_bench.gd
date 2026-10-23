class_name UndertowBench
extends Node
## Undertow cost benchmark (M1-RND-03). Needs a real renderer (ADR 0009):
##   godot-render --path . --audio-driver Dummy --fixed-fps 60 --disable-vsync --resolution 960x540 \
##     res://game/levels/_tests/undertow/undertow_bench.tscn -- --camera=Cameras/Horizon
## Same method as water_bench.gd (docs/kb/tech/water.md "Cost"): per configuration, after
## WARMUP_FRAMES, the CPU time this process spends per frame over MEASURE_FRAMES, read from
## /proc/self/stat (lavapipe rasterises in this process's threads, so other load on the machine
## does not inflate it); COST_ROUNDS interleaved rounds, minimum kept. The numbers rank features
## against each other; they are not GPU milliseconds (docs/kb/tech/undertow.md).

const SCENE := "res://game/levels/_tests/undertow/undertow_test.tscn"
const WARMUP_FRAMES := 3
const MEASURE_FRAMES := 4
const COST_ROUNDS := 2
const STAT_UTIME := 11
const STAT_STIME := 12
const MS_PER_TICK := 10.0
## name, tier, which storm parts draw, and overrides (shader params on every storm material).
const CONFIGS: Array[Dictionary] = [
	{"name": "no storm", "quality": "high", "storm": false, "parts": [], "set": {}},
	{"name": "low (shells)", "quality": "low", "storm": true, "parts": [], "set": {}},
	{"name": "medium", "quality": "medium", "storm": true, "parts": [], "set": {}},
	{"name": "high", "quality": "high", "storm": true, "parts": [], "set": {}},
	{"name": "ultra", "quality": "ultra", "storm": true, "parts": [], "set": {}},
	{"name": "high - body", "quality": "high", "storm": true, "parts": ["Body"], "set": {}},
	{"name": "high - sea", "quality": "high", "storm": true, "parts": ["Sea", "SeaLid"], "set": {}},
	{"name": "high - spray", "quality": "high", "storm": true, "parts": ["Spray0", "Spray1"], "set": {}},
	{"name": "high - wounds", "quality": "high", "storm": true, "parts": [], "set": {"wound_intensity": 0.0}},
	{"name": "high, 22 steps", "quality": "high", "storm": true, "parts": [], "set": {"march_steps": 22}},
]

var _scene: UndertowTestRig


func _ready() -> void:
	_run.call_deferred()


func _run() -> void:
	var opts := _args()
	_scene = (load(SCENE) as PackedScene).instantiate() as UndertowTestRig
	add_child(_scene)
	var cam_path := str(opts.get("camera", "Cameras/Horizon"))
	var cam := _scene.get_node_or_null(NodePath(cam_path)) as Camera3D
	if cam != null:
		cam.make_current()
	_scene.storm.playing = false
	print("BENCH %s, %s" % [cam_path, RenderingServer.get_video_adapter_name()])
	var best: Array[float] = []
	best.resize(CONFIGS.size())
	best.fill(INF)
	for round_i in COST_ROUNDS:
		for i in CONFIGS.size():
			var ms := await _measure(CONFIGS[i])
			best[i] = minf(best[i], ms)
			print("BENCH round %d %-18s %8.1f ms" % [round_i, CONFIGS[i]["name"], ms])
	for i in CONFIGS.size():
		print(
			(
				"BENCH %-18s cpu(min of %d) %8.1f ms/frame  storm %+8.1f ms"
				% [CONFIGS[i]["name"], COST_ROUNDS, best[i], best[i] - best[0]]
			)
		)
	get_tree().quit()


func _measure(c: Dictionary) -> float:
	var storm := _scene.storm
	storm.set_quality(str(c["quality"]))
	storm.visuals.visible = bool(c["storm"])
	# Everything on, let the tier pick its parts, then hide what this configuration removes.
	for child in storm.visuals.get_children():
		(child as Node3D).visible = true
	storm.refresh()
	for child in storm.visuals.get_children():
		if (c["parts"] as Array).has(str(child.name)):
			(child as Node3D).visible = false
	var overrides := c["set"] as Dictionary
	for m in storm.materials():
		for key: String in overrides:
			m.set_shader_parameter(key, overrides[key])
	var wounds := storm.wound_intensity
	if overrides.has("wound_intensity"):
		storm.wound_intensity = float(overrides["wound_intensity"])
	for i in WARMUP_FRAMES:
		await RenderingServer.frame_post_draw
	var cpu0 := _cpu_ticks()
	for i in MEASURE_FRAMES:
		await RenderingServer.frame_post_draw
	var cpu := float(_cpu_ticks() - cpu0) * MS_PER_TICK / MEASURE_FRAMES
	if overrides.has("wound_intensity"):
		storm.wound_intensity = wounds
	storm.visuals.visible = true
	return cpu


func _cpu_ticks() -> int:
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
