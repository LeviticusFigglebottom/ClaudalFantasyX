class_name ScreenshotCapture
extends Node
## Screenshot capture (SPEC §5.5, M1-QA-01, ADR 0009).
## Renders every shot in tests/screenshots/shots.json to tests/screenshots/out/<id>.png and writes
## out/capture_report.json, then quits with exit code 1 if any shot failed.
## Needs a real renderer: run it through `godot-render` (tools/dev/fetch_render_deps.py), never --headless:
##   godot-render --path . --audio-driver Dummy --fixed-fps 60 res://tests/screenshots/capture.tscn
## User args (after `--`): --shots=id1,id2   --out=<absolute dir>   --manifest=<res:// path>
## Shot keys: id, scene, camera ("default" or a Camera3D/Camera2D path relative to the scene root),
## resolution [w, h], settle_frames, seed, threshold_rmse, warm_shader_groups (M2-QA-01: non-TAA shots with
## VoxelGI, SSS or a lightmap; see _warm_shader_groups), and an optional setup block (globals, node
## properties, viewport properties, time_scale: see CaptureSetup). Missing keys come from "defaults".

const MANIFEST_PATH := "res://tests/screenshots/shots.json"
const OUT_DIR := "res://tests/screenshots/out"
const REPORT_NAME := "capture_report.json"
## Process after every node of the shot's scene (lower priorities run first), so the setup's held
## values are the last write before each frame is drawn.
const HOLD_PRIORITY := 1 << 20
## The warm-up viewport's side (px) for "warm_shader_groups" (M2-QA-01): it only has to render once.
const WARM_VIEWPORT_SIZE := 8

## The running shot's setup (null between shots and for shots without one).
var _setup: CaptureSetup = null


func _ready() -> void:
	process_priority = HOLD_PRIORITY
	# M2-ARC-02: the game's weather clock writes nothing for the whole run, so a shot's pinned globals and a
	# rig's own writes win, and no shot sees a clock or zone wind that moved between shots.
	var clock := WeatherClock.current()
	if clock != null:
		clock.hold(self)
	_run.call_deferred()


func _process(_delta: float) -> void:
	if _setup != null:
		_setup.hold()


func _run() -> void:
	var opts := _parse_args()
	var out_dir: String = opts.get("out", ProjectSettings.globalize_path(OUT_DIR))
	if DisplayServer.get_name() == "headless":
		printerr("CAPTURE needs a real renderer: run through godot-render, not --headless (ADR 0009)")
		get_tree().quit(2)
		return
	var manifest := _load_manifest(opts.get("manifest", MANIFEST_PATH))
	if manifest.is_empty():
		get_tree().quit(2)
		return
	DirAccess.make_dir_recursive_absolute(out_dir)
	# Keep Godot from importing the captured PNGs as project resources.
	FileAccess.open(out_dir.path_join(".gdignore"), FileAccess.WRITE).store_string("")
	var defaults: Dictionary = manifest.get("defaults", {})
	var wanted: PackedStringArray = opts.get("shots", PackedStringArray())
	var results: Array[Dictionary] = []
	var failed := 0
	for shot_v: Variant in manifest.get("shots", []):
		var shot: Dictionary = defaults.merged(shot_v as Dictionary, true)
		if not wanted.is_empty() and not wanted.has(String(shot.get("id", ""))):
			continue
		var result := await _capture(shot, out_dir)
		results.append(result)
		if not bool(result["ok"]):
			failed += 1
			printerr("CAPTURE FAIL %s: %s" % [result["id"], result["error"]])
		else:
			print("CAPTURE ok   %s  %d ms (%d frames)" % [result["id"], result["ms"], result["frames"]])
	_write_report(out_dir, results)
	print("Capture: %d shot(s), %d failed, renderer %s" % [results.size(), failed, _renderer_line()])
	get_tree().quit(1 if failed > 0 or results.is_empty() else 0)


func _capture(shot: Dictionary, out_dir: String) -> Dictionary:
	var id := String(shot.get("id", ""))
	var result := {"id": id, "ok": false, "error": "", "ms": 0, "frames": 0}
	var res: Array = shot.get("resolution", [])
	if id == "" or res.size() != 2 or not shot.has("scene"):
		result["error"] = "shot needs id, scene and resolution [w, h]"
		return result
	var size := Vector2i(int(res[0]), int(res[1]))
	var frames := int(shot.get("settle_frames", 1))
	var started := Time.get_ticks_msec()
	seed(int(shot.get("seed", 0)))
	get_window().size = size
	if bool(shot.get("warm_shader_groups", false)):
		_warm_shader_groups()
	var packed := load(String(shot["scene"])) as PackedScene
	if packed == null:
		result["error"] = "cannot load scene %s" % shot["scene"]
		return result
	# An absent setup is empty: begin/attach/hold/end then change nothing (baselines stay byte-stable).
	_setup = CaptureSetup.new(shot.get("setup", {}))
	var instance: Node = null
	var error := _setup.begin(get_viewport())
	if error == "":
		instance = packed.instantiate()
		add_child(instance)
		error = _setup.attach(instance)
	if error == "":
		error = _use_camera(instance, String(shot.get("camera", "default")))
	if error != "":
		_end_setup()
		if instance != null:
			instance.queue_free()
		result["error"] = error
		return result
	for i in frames:
		await get_tree().process_frame
	await RenderingServer.frame_post_draw
	var image := get_viewport().get_texture().get_image()
	_end_setup()
	instance.queue_free()
	await get_tree().process_frame
	if image == null or image.get_size() != size:
		result["error"] = (
			"captured %s, wanted %s (enlarge HYMN_XVFB_SCREEN)" % [image.get_size() if image else Vector2i.ZERO, size]
		)
		return result
	image.convert(Image.FORMAT_RGB8)
	var err := image.save_png(out_dir.path_join("%s.png" % id))
	if err != OK:
		result["error"] = "save_png failed: %s" % error_string(err)
		return result
	result["ok"] = true
	result["frames"] = frames
	result["ms"] = Time.get_ticks_msec() - started
	return result


## M2-QA-01: turns on Forward+'s "advanced" scene-shader group (motion vectors, VoxelGI, SSS, lightmap
## variants) before the shot's scene loads a single shader. Godot 4.6.3 enables that group lazily, on
## the first frame that needs it, and then queues its compile for every shader already loaded behind the
## pipeline compiles already queued. The render thread waits for it holding the shader's version mutex
## while those pipeline compiles (on every pool worker) block on the same mutex: a deadlock
## (docs/kb/qa/screenshots.md, "Engine deadlock"). With the group on first, each shader's groups are
## queued when it is created, ahead of any of its pipelines. One TAA (motion-vector) render of an
## empty 8 px world through force_draw with frame_step 0, so TIME does not advance. It does add one to
## the frame count, so only non-TAA shots may set the key (TAA jitter follows the frame count).
func _warm_shader_groups() -> void:
	var vp := SubViewport.new()
	vp.size = Vector2i(WARM_VIEWPORT_SIZE, WARM_VIEWPORT_SIZE)
	vp.own_world_3d = true
	vp.use_taa = true
	vp.render_target_update_mode = SubViewport.UPDATE_ONCE
	var cam := Camera3D.new()
	vp.add_child(cam)
	add_child(vp)
	cam.make_current()
	RenderingServer.force_draw(false, 0.0)
	remove_child(vp)
	vp.free()


func _end_setup() -> void:
	if _setup != null:
		_setup.end()
		_setup = null


func _use_camera(instance: Node, camera: String) -> String:
	if camera == "default":
		return ""
	var node := instance.get_node_or_null(NodePath(camera))
	if node is Camera3D:
		(node as Camera3D).make_current()
	elif node is Camera2D:
		(node as Camera2D).make_current()
	else:
		return "camera '%s' is not a Camera3D/Camera2D under the scene root" % camera
	return ""


func _parse_args() -> Dictionary:
	var opts := {}
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--shots="):
			opts["shots"] = arg.trim_prefix("--shots=").split(",", false)
		elif arg.begins_with("--out="):
			opts["out"] = arg.trim_prefix("--out=")
		elif arg.begins_with("--manifest="):
			opts["manifest"] = arg.trim_prefix("--manifest=")
	return opts


func _load_manifest(path: String) -> Dictionary:
	var text := FileAccess.get_file_as_string(path)
	var parsed: Variant = JSON.parse_string(text)
	if not parsed is Dictionary:
		printerr("CAPTURE cannot parse manifest %s" % path)
		return {}
	return parsed as Dictionary


func _renderer_line() -> String:
	return (
		"%s/%s on %s"
		% [
			RenderingServer.get_current_rendering_method(),
			RenderingServer.get_current_rendering_driver_name(),
			RenderingServer.get_video_adapter_name(),
		]
	)


func _write_report(out_dir: String, results: Array[Dictionary]) -> void:
	var report := {
		"godot": Engine.get_version_info()["string"],
		"rendering_method": RenderingServer.get_current_rendering_method(),
		"rendering_driver": RenderingServer.get_current_rendering_driver_name(),
		"adapter": RenderingServer.get_video_adapter_name(),
		"adapter_vendor": RenderingServer.get_video_adapter_vendor(),
		"shots": results,
	}
	var f := FileAccess.open(out_dir.path_join(REPORT_NAME), FileAccess.WRITE)
	f.store_string(JSON.stringify(report, "  ") + "\n")
