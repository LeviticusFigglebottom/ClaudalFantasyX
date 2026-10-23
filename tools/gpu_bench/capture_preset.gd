class_name CapturePreset
extends Node
## Screenshot shots rendered under a graphics preset (M1-QA-05). Real GPU and window:
##   godot --path . --audio-driver Dummy --fixed-fps 60 res://tools/gpu_bench/capture_preset.tscn -- \
##     --shots=asha_front,asha_q34 --preset=high --out=C:/abs/dir [--scale=2 --settle=60]
## For each shot in tests/screenshots/shots.json: instances its scene, makes its camera current,
## sizes the window to its resolution x --scale, applies the preset through GraphicsSettings (the
## viewport and the scene's Environment) and the matching character shader tier
## (CharacterShaderTiers), renders max(shot settle_frames, --settle) frames and saves <id>.png.
## The capture rig (tests/screenshots/capture.tscn) renders scene defaults; this shows what the
## player's preset does to the same shot. Never writes baselines.
## Diagnosis (M1-QA-05): --light-set=prop=value,... on every DirectionalLight3D (e.g.
## shadow_enabled=false, shadow_normal_bias=2.0, directional_shadow_max_distance=2.0);
## --mat-set=uniform=value,... on every ShaderMaterial that declares the uniform.

const MANIFEST := "res://tests/screenshots/shots.json"

var _opts: Dictionary = {}


func _ready() -> void:
	_run.call_deferred()


func _run() -> void:
	_opts = _args()
	var out := str(_opts.get("out", ""))
	DirAccess.make_dir_recursive_absolute(out)
	var manifest := JSON.parse_string(FileAccess.get_file_as_string(MANIFEST)) as Dictionary
	var defaults := manifest.get("defaults", {}) as Dictionary
	var wanted := str(_opts.get("shots", "")).split(",", false)
	var preset := str(_opts.get("preset", "high"))
	var scale := float(_opts.get("scale", 1.0))
	var win := get_window()
	win.borderless = true
	win.position = DisplayServer.screen_get_position(win.current_screen)
	for shot_v: Variant in manifest.get("shots", []):
		var shot := defaults.merged(shot_v as Dictionary, true)
		if not wanted.is_empty() and not wanted.has(str(shot["id"])):
			continue
		var res := shot["resolution"] as Array
		win.size = Vector2i(roundi(float(res[0]) * scale), roundi(float(res[1]) * scale))
		seed(int(shot.get("seed", 0)))
		var scene := (load(str(shot["scene"])) as PackedScene).instantiate()
		add_child(scene)
		var cam_path := str(shot.get("camera", "default"))
		if cam_path != "default":
			(scene.get_node(NodePath(cam_path)) as Camera3D).make_current()
		await get_tree().process_frame
		var gs := GraphicsSettings.new()
		gs.set_preset(preset)
		var envs := scene.find_children("*", "WorldEnvironment", true, false)
		gs.apply_current(get_viewport(), (envs[0] as WorldEnvironment).environment if envs.size() > 0 else null)
		CharacterShaderTiers.apply_to_tree(scene, CharacterShaderTiers.tier_for_preset(preset))
		_tweak(scene)
		for i in maxi(int(shot.get("settle_frames", 1)), int(_opts.get("settle", 60))):
			await get_tree().process_frame
		await RenderingServer.frame_post_draw
		var img := get_viewport().get_texture().get_image()
		img.convert(Image.FORMAT_RGB8)
		img.save_png(out.path_join("%s.png" % shot["id"]))
		print("CAPTURE_PRESET ok %s %s %dx%d" % [shot["id"], preset, win.size.x, win.size.y])
		scene.queue_free()
		await get_tree().process_frame
	get_tree().quit()


func _tweak(scene: Node) -> void:
	for pair in str(_opts.get("light-set", "")).split(",", false):
		var kv := pair.split("=", true, 1)
		for n in scene.find_children("*", "DirectionalLight3D", true, false):
			n.set(kv[0], str_to_var(kv[1]))
	var mats := {}
	for n in scene.find_children("*", "GeometryInstance3D", true, false):
		var g := n as GeometryInstance3D
		var list: Array[Material] = [g.material_override]
		if g is MeshInstance3D and (g as MeshInstance3D).mesh != null:
			for i in (g as MeshInstance3D).mesh.get_surface_count():
				list.append((g as MeshInstance3D).get_active_material(i))
		for m in list:
			if m is ShaderMaterial:
				mats[m] = true
	for pair in str(_opts.get("mat-set", "")).split(",", false):
		var kv := pair.split("=", true, 1)
		for m: ShaderMaterial in mats:
			var names := m.shader.get_shader_uniform_list().map(func(u: Dictionary) -> String: return str(u["name"]))
			if names.has(kv[0]):
				m.set_shader_parameter(kv[0], str_to_var(kv[1]))


func _args() -> Dictionary:
	var out := {}
	for a in OS.get_cmdline_user_args():
		var kv := a.trim_prefix("--").split("=", true, 1)
		out[kv[0]] = kv[1] if kv.size() > 1 else true
	return out
