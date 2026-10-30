class_name GpuBench
extends Node
## GPU frame-time benchmark (M1-QA-01 follow-up). Needs a real GPU and a real window, never --headless:
##   godot --path . --audio-driver Dummy --disable-vsync res://tools/gpu_bench/gpu_bench.tscn -- \
##     --scene=res://game/levels/_tests/water/water_test.tscn --camera=Cameras/Lagoon \
##     --presets=low,medium,high,ultra --res=1920x1080,2560x1440 --csv=C:/abs/results.csv
## Options (after `--`):
##   --scene=res://...            scene to instance (required)
##   --camera=default|<path>      Camera3D path relative to the scene root
##   --presets=low,...            GraphicsSettings presets (game/data/settings/graphics_presets.json)
##   --res=WxH,...                window sizes; the window is borderless at the screen origin
##   --variants=scene|undertow|water|sky   undertow/water run UndertowBench/WaterBench CONFIGS per preset;
##                                sky runs SKY_CONFIGS on the Environment's sky material (M1-RND-12)
##   --sky-set=uniform=value,...  extra sky-material uniforms on top of every sky variant
##   --warmup=120 --frames=300    frames skipped after each change, then frames sampled
##   --warmup-s=3.0               the warm-up also lasts at least this long (async pipeline compiles)
##   --csv=<abs path>             append one row per measurement (header written for a new file)
##   --label=<name>               scene label in the CSV (default: scene file name + camera)
##   --png-dir=<abs dir>          save the last sampled frame of each measurement as a PNG
##   --override=key=value,...     GraphicsSettings overrides on top of each preset (e.g. vegetation_detail=low)
##   --undertow-half=<scale>     render every UndertowStorm's body at this resolution fraction (M2-RND-01)
##   --node-set=Path:prop=value,...   set a property on a node of the scene (e.g. Underwater:active=false)
##   --hide=<glob>[;<glob>...]    after the settle, hide every Node3D whose name matches (e.g. camp_fire*;smoke_*):
##                                an element's cost by difference, runtime-built dressing included
##   --hide-storms                hide every UndertowStorm (the frame without the storm: its own cost by difference)
##   --debug-draw=overdraw      render Viewport.DEBUG_DRAW_OVERDRAW (pair with --png-dir; M1-ENV-03 budget)
##   --tag-vegetation             tag MultiMeshes (vegetation_multimesh, small_foliage) and range-limited
##                                meshes (vegetation_lod) before measuring, as a zone would (M1-RND-07)
##   --spin-sun=<deg>             turn every DirectionalLight3D this many degrees about Y each frame
##                                (a moving sun: measures the sky's radiance re-render, M1-RND-12)
##   --drift-sky=<m>              move the sky material's cloud_offset_m this far each frame (drifting clouds)
##   --sky-process=<0-3>          Sky.process_mode for the run (0 automatic, 2 incremental, 3 realtime)
##   --hold-storm                 freeze every UndertowStorm clock (deterministic frames for look diffs)
##                                while its temporal jitter keeps advancing; pair with --warmup-s=0
## Per configuration: apply the preset through GraphicsSettings (viewport + the scene's Environment),
## then the matching tier of every WaterSurface, UndertowStorm, GlimmerField and character material,
## skip `warmup` frames, then read RenderingServer.viewport_get_measured_render_time_gpu/_cpu after
## each of `frames` frames. Reports median, p99 and mean. Frame wall time is reported too.
## These are steady-state frames after the warm-up, neither of ADR 0029's transition windows (the hidden frames
## under a fade, the first 60 after it lifts): SceneRouter's last_swap_stats measures those (M1-ARC-16).

const DEFAULT_PRESETS := "low,medium,high,ultra"
const DEFAULT_RES := "1920x1080"
const DEFAULT_WARMUP := 120
const DEFAULT_FRAMES := 300
const DEFAULT_WARMUP_S := 3.0
## Frames after instancing for rigs that react to the current camera (undertow mood, its env swap).
const SETTLE_FRAMES := 5
const US_PER_MS := 1000.0
const P99 := 0.99
const CSV_HEADER := (
	"scene,camera,variant,preset,res_w,res_h,internal_w,internal_h,frames,"
	+ "gpu_median_ms,gpu_p99_ms,gpu_mean_ms,cpu_median_ms,cpu_p99_ms,frame_median_ms,frame_p99_ms,adapter,driver"
)
const WATER_TOGGLES := ["use_ssr", "use_caustics", "use_foam", "use_refraction", "use_detail_normals", "use_sss"]
## Sky variants (M1-RND-12): the preset's sky tier as applied, and the same frame without clouds (a
## cloud_max_distance_m of 0 returns before the march), so the difference is the cloud march.
const SKY_CONFIGS: Array[Dictionary] = [
	{"name": "sky", "set": {}},
	{"name": "no_clouds", "set": {"cloud_max_distance_m": 0.0}},
]

var _scene: Node
var _opts: Dictionary = {}
var _held: Array[UndertowStorm] = []
## The sky material's uniforms before any sky variant touched them (restored between variants).
var _sky_authored: Dictionary = {}


func _ready() -> void:
	_run.call_deferred()


func _run() -> void:
	_opts = _args()
	if DisplayServer.get_name() == "headless":
		printerr("GPU_BENCH needs a real renderer and window, not --headless")
		get_tree().quit(2)
		return
	var scene_path := str(_opts.get("scene", ""))
	var packed := load(scene_path) as PackedScene if scene_path != "" else null
	if packed == null:
		printerr("GPU_BENCH cannot load --scene=%s" % scene_path)
		get_tree().quit(2)
		return
	Engine.max_fps = 0
	DisplayServer.window_set_vsync_mode(DisplayServer.VSYNC_DISABLED)
	var win := get_window()
	win.borderless = true
	win.position = DisplayServer.screen_get_position(win.current_screen)
	_scene = packed.instantiate()
	add_child(_scene)
	if _opts.has("undertow-half"):
		for n in _scene.find_children("*", "", true, false):
			if n is UndertowStorm:
				(n as UndertowStorm).half_res_body_scale = float(_opts["undertow-half"])
	for pair in str(_opts.get("node-set", "")).split(",", false):
		var kv := pair.split("=", true, 1)
		var at := kv[0].split(":", true, 1)
		var node := _scene.get_node_or_null(NodePath(at[0]))
		if node == null or at.size() < 2 or kv.size() < 2:
			push_error("--node-set: cannot apply '%s'" % pair)
			continue
		node.set(at[1], str_to_var(kv[1]))
	if _opts.has("hide-storms"):
		for n in _scene.find_children("*", "", true, false):
			if n is UndertowStorm:
				(n as UndertowStorm).visible = false
	if _opts.has("hold-storm"):
		for n in _scene.find_children("*", "", true, false):
			if n is UndertowStorm:
				(n as UndertowStorm).playing = false
				_held.append(n as UndertowStorm)
	var camera := str(_opts.get("camera", "default"))
	if camera != "default":
		var cam := _scene.get_node_or_null(NodePath(camera)) as Camera3D
		if cam == null:
			printerr("GPU_BENCH camera '%s' is not a Camera3D under the scene root" % camera)
			get_tree().quit(2)
			return
		cam.make_current()
	for i in SETTLE_FRAMES:
		await get_tree().process_frame
	# --hide runs after the settle so runtime-built dressing (ZoneKitDressing) is already in the tree.
	for pattern in str(_opts.get("hide", "")).split(";", false):
		var hidden := 0
		for n in _scene.find_children(pattern, "Node3D", true, false):
			(n as Node3D).visible = false
			hidden += 1
		print("GPU_BENCH hide '%s': %d node(s)" % [pattern, hidden])
	if _opts.has("tag-vegetation"):
		var groups := GraphicsSettings.new().data.get("vegetation_groups", {}) as Dictionary
		for n in _scene.find_children("*", "GeometryInstance3D", true, false):
			if n is MultiMeshInstance3D:
				n.add_to_group(str(groups.get("multimesh", "")))
				n.add_to_group(str(groups.get("small_shadows", "")))
			elif (n as GeometryInstance3D).visibility_range_end > 0.0:
				n.add_to_group(str(groups.get("lod", "")))
	var rid := get_viewport().get_viewport_rid()
	RenderingServer.viewport_set_measure_render_time(rid, true)
	var label := str(_opts.get("label", "%s:%s" % [scene_path.get_file().get_basename(), camera]))
	print(
		(
			"GPU_BENCH %s on %s (%s %s), Godot %s"
			% [
				label,
				RenderingServer.get_video_adapter_name(),
				RenderingServer.get_current_rendering_driver_name(),
				RenderingServer.get_video_adapter_api_version(),
				Engine.get_version_info()["string"],
			]
		)
	)
	var variants := _variants(str(_opts.get("variants", "scene")))
	for res_text in str(_opts.get("res", DEFAULT_RES)).split(",", false):
		var size := _parse_res(res_text)
		win.size = size
		for preset in str(_opts.get("presets", DEFAULT_PRESETS)).split(",", false):
			for v: Dictionary in variants:
				var row := await _measure(preset, v, camera, label)
				if win.size != size:
					push_warning("GPU_BENCH window is %s, wanted %s (screen too small?)" % [win.size, size])
				_emit(row)
	get_tree().quit()


func _measure(preset: String, variant: Dictionary, camera: String, label: String) -> Dictionary:
	var gs := GraphicsSettings.new()
	gs.set_preset(preset)
	for pair in str(_opts.get("override", "")).split(",", false):
		var kv := pair.split("=", true, 1)
		var v: Variant = str_to_var(kv[1])
		gs.set_override(kv[0], v if v != null else kv[1])
	gs.apply_current(get_viewport(), _environment())
	if str(_opts.get("debug-draw", "")) == "overdraw":
		get_viewport().debug_draw = Viewport.DEBUG_DRAW_OVERDRAW
	if _opts.has("sky-process") and _environment() != null and _environment().sky != null:
		_environment().sky.process_mode = int(_opts["sky-process"]) as Sky.ProcessMode
	_apply_tiers(preset)
	_apply_variant(variant)
	var warmup := int(_opts.get("warmup", DEFAULT_WARMUP))
	var frames := int(_opts.get("frames", DEFAULT_FRAMES))
	var rid := get_viewport().get_viewport_rid()
	var warmup_until := (
		Time.get_ticks_usec() + int(float(_opts.get("warmup-s", DEFAULT_WARMUP_S)) * US_PER_MS * US_PER_MS)
	)
	var skipped := 0
	while skipped < warmup or Time.get_ticks_usec() < warmup_until:
		await RenderingServer.frame_post_draw
		_tick_held()
		_tick_sun()
		skipped += 1
	var gpu := PackedFloat64Array()
	var cpu := PackedFloat64Array()
	var wall := PackedFloat64Array()
	var last := Time.get_ticks_usec()
	for i in frames:
		await RenderingServer.frame_post_draw
		_tick_held()
		_tick_sun()
		var now := Time.get_ticks_usec()
		wall.append(float(now - last) / US_PER_MS)
		last = now
		gpu.append(RenderingServer.viewport_get_measured_render_time_gpu(rid) + _sub_viewports_gpu())
		cpu.append(RenderingServer.viewport_get_measured_render_time_cpu(rid))
	var size := get_window().size
	var scale := get_viewport().scaling_3d_scale
	if _opts.has("png-dir"):
		var img := get_viewport().get_texture().get_image()
		img.convert(Image.FORMAT_RGB8)
		var png_name := "%s_%s_%s_%dx%d.png" % [label.validate_filename(), str(variant["name"]), preset, size.x, size.y]
		img.save_png(str(_opts["png-dir"]).path_join(png_name.replace(" ", "_")))
	return {
		"scene": label.get_slice(":", 0),
		"camera": camera,
		"variant": str(variant["name"]),
		"preset": preset,
		"res_w": size.x,
		"res_h": size.y,
		"internal_w": roundi(size.x * scale),
		"internal_h": roundi(size.y * scale),
		"frames": frames,
		"gpu_median_ms": _percentile(gpu, 0.5),
		"gpu_p99_ms": _percentile(gpu, P99),
		"gpu_mean_ms": _mean(gpu),
		"cpu_median_ms": _percentile(cpu, 0.5),
		"cpu_p99_ms": _percentile(cpu, P99),
		"frame_median_ms": _percentile(wall, 0.5),
		"frame_p99_ms": _percentile(wall, P99),
		"adapter": RenderingServer.get_video_adapter_name(),
		"driver": RenderingServer.get_video_adapter_api_version(),
	}


# --- Tiers and variants --------------------------------------------------------------------------


## The subsystems that carry their own preset -> tier map, exactly as the game sets them on scene entry
## (GraphicsRuntime.apply_system_tiers: water, weathering, the Undertow, glimmer, the underwater rig and
## character materials; M2-RND-02 replaced a hand list that had fallen behind).
func _apply_tiers(preset: String) -> void:
	GraphicsRuntime.apply_system_tiers(_scene, preset)


func _variants(kind: String) -> Array[Dictionary]:
	var out: Array[Dictionary] = []
	match kind:
		"undertow":
			for c in UndertowBench.CONFIGS:
				out.append(c.merged({"kind": "undertow"}))
		"water":
			for c in WaterBench.CONFIGS:
				out.append(c.merged({"kind": "water"}))
		"sky":
			for c in SKY_CONFIGS:
				out.append(c.merged({"kind": "sky"}))
		_:
			out.append({"name": "scene", "kind": "scene"})
	return out


## Same toggles as UndertowBench._measure / WaterBench._measure, on top of the preset's tiers.
func _apply_variant(v: Dictionary) -> void:
	match str(v["kind"]):
		"undertow":
			var storm := _scene.get("storm") as UndertowStorm
			storm.set_quality(str(v["quality"]))
			storm.visuals.visible = bool(v["storm"])
			for child in storm.visuals.get_children():
				(child as Node3D).visible = true
			storm.refresh()
			for child in storm.visuals.get_children():
				if (v["parts"] as Array).has(str(child.name)):
					(child as Node3D).visible = false
			var overrides := v["set"] as Dictionary
			for m in storm.materials():
				for key: String in overrides:
					m.set_shader_parameter(key, overrides[key])
			if overrides.has("wound_intensity"):
				storm.wound_intensity = float(overrides["wound_intensity"])
		"water":
			var water := _scene.get("water") as WaterSurface
			water.quality = WaterBench.QUALITY_NAMES.get(str(v["quality"]), WaterSurface.Quality.HIGH)
			water.visible = bool(v["water"])
			for key: String in WATER_TOGGLES:
				water.material.set_shader_parameter(key, true)
			var overrides := v["set"] as Dictionary
			for key: String in overrides:
				water.material.set_shader_parameter(key, overrides[key])
		"sky":
			var env := _environment()
			var m := env.sky.sky_material as ShaderMaterial if env != null and env.sky != null else null
			if m == null:
				push_warning("GPU_BENCH --variants=sky: the scene has no ShaderMaterial sky")
				return
			for key: String in _sky_authored:
				m.set_shader_parameter(key, _sky_authored[key])
			var uniforms := (v["set"] as Dictionary).duplicate()
			for pair in str(_opts.get("sky-set", "")).split(",", false):
				var kv := pair.split("=", true, 1)
				uniforms[kv[0]] = str_to_var(kv[1])
			for key: String in uniforms:
				if not _sky_authored.has(key):
					_sky_authored[key] = m.get_shader_parameter(key)
				m.set_shader_parameter(key, uniforms[key])


func _tick_sun() -> void:
	if _opts.has("spin-sun"):
		for n in _scene.find_children("*", "DirectionalLight3D", true, false):
			(n as Node3D).rotate_y(deg_to_rad(float(_opts["spin-sun"])))
	var env := _environment()
	if _opts.has("drift-sky") and env != null and env.sky != null and env.sky.sky_material is ShaderMaterial:
		var m := env.sky.sky_material as ShaderMaterial
		var off: Variant = m.get_shader_parameter("cloud_offset_m")
		var v := off as Vector2 if off is Vector2 else Vector2(900.0, -1400.0)
		m.set_shader_parameter("cloud_offset_m", v + Vector2(float(_opts["drift-sky"]), 0.0))


## GPU ms of the SubViewports the scene renders (an off-screen storm body, M2-RND-01): the main
## viewport's own measurement does not include them.
func _sub_viewports_gpu() -> float:
	var ms := 0.0
	for n in find_children("*", "SubViewport", true, false):
		var vp_rid := (n as SubViewport).get_viewport_rid()
		RenderingServer.viewport_set_measure_render_time(vp_rid, true)
		ms += RenderingServer.viewport_get_measured_render_time_gpu(vp_rid)
	return ms


## A held storm's clock stays put, but its temporal jitter (UndertowState.frame) still advances.
func _tick_held() -> void:
	for storm in _held:
		if "frame" in storm.state:
			storm.state.frame += 1


func _environment() -> Environment:
	var cam := get_viewport().get_camera_3d()
	if cam != null and cam.environment != null:
		return cam.environment
	for n in _scene.find_children("*", "WorldEnvironment", true, false):
		return (n as WorldEnvironment).environment
	return null


# --- Output --------------------------------------------------------------------------------------


func _emit(row: Dictionary) -> void:
	print(
		(
			"GPU_BENCH %-22s %-20s %-6s %4dx%-4d gpu med %6.2f p99 %6.2f | cpu med %5.2f p99 %5.2f | frame med %6.2f ms"
			% [
				row["scene"],
				row["variant"],
				row["preset"],
				row["res_w"],
				row["res_h"],
				row["gpu_median_ms"],
				row["gpu_p99_ms"],
				row["cpu_median_ms"],
				row["cpu_p99_ms"],
				row["frame_median_ms"],
			]
		)
	)
	var path := str(_opts.get("csv", ""))
	if path == "":
		return
	var is_new := not FileAccess.file_exists(path)
	var f := FileAccess.open(path, FileAccess.READ_WRITE if not is_new else FileAccess.WRITE)
	if f == null:
		printerr("GPU_BENCH cannot write %s" % path)
		return
	f.seek_end()
	if is_new:
		f.store_line(CSV_HEADER)
	var cells := PackedStringArray()
	for key in CSV_HEADER.split(","):
		var v: Variant = row[key]
		cells.append("%.3f" % v if v is float else str(v).replace(",", ";"))
	f.store_line(",".join(cells))


static func _percentile(values: PackedFloat64Array, q: float) -> float:
	if values.is_empty():
		return 0.0
	var sorted := values.duplicate()
	sorted.sort()
	return sorted[clampi(ceili(q * sorted.size()) - 1, 0, sorted.size() - 1)]


static func _mean(values: PackedFloat64Array) -> float:
	var total := 0.0
	for v in values:
		total += v
	return total / maxf(1.0, values.size())


static func _parse_res(text: String) -> Vector2i:
	var wh := text.split("x")
	return Vector2i(int(wh[0]), int(wh[1]))


func _args() -> Dictionary:
	var out := {}
	for a in OS.get_cmdline_user_args():
		var kv := a.trim_prefix("--").split("=", true, 1)
		out[kv[0]] = kv[1] if kv.size() > 1 else true
	return out
