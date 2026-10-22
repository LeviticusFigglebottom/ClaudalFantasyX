class_name ScreenshotCapture
extends Node
## Screenshot capture (SPEC §5.5, M1-QA-01, ADR 0009).
## Renders every shot in tests/screenshots/shots.json to tests/screenshots/out/<id>.png and writes
## out/capture_report.json, then quits with exit code 1 if any shot failed.
## Needs a real renderer: run it through `godot-render` (tools/dev/fetch_render_deps.py), never --headless:
##   godot-render --path . --audio-driver Dummy --fixed-fps 60 res://tests/screenshots/capture.tscn
## User args (after `--`): --shots=id1,id2   --out=<absolute dir>   --manifest=<res:// path>
## Shot keys: id, scene, camera ("default" or a Camera3D/Camera2D path relative to the scene root),
## resolution [w, h], settle_frames, seed, threshold_rmse. Missing keys come from the manifest "defaults".

const MANIFEST_PATH := "res://tests/screenshots/shots.json"
const OUT_DIR := "res://tests/screenshots/out"
const REPORT_NAME := "capture_report.json"


func _ready() -> void:
	_run.call_deferred()


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
	var packed := load(String(shot["scene"])) as PackedScene
	if packed == null:
		result["error"] = "cannot load scene %s" % shot["scene"]
		return result
	var instance := packed.instantiate()
	add_child(instance)
	var cam_error := _use_camera(instance, String(shot.get("camera", "default")))
	if cam_error != "":
		instance.queue_free()
		result["error"] = cam_error
		return result
	for i in frames:
		await get_tree().process_frame
	await RenderingServer.frame_post_draw
	var image := get_viewport().get_texture().get_image()
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
