class_name CapturePreset
extends Node
## Screenshot shots rendered under a graphics preset (M1-QA-05). Real GPU and window:
##   godot --path . --audio-driver Dummy --fixed-fps 60 res://tools/gpu_bench/capture_preset.tscn -- \
##     --shots=asha_front,asha_q34 --preset=high --out=C:/abs/dir [--scale=2 --settle=60]
## For each shot in tests/screenshots/shots.json: instances its scene, makes its camera current,
## sizes the window to its resolution x --scale, applies the preset through GraphicsSettings (the
## viewport and the scene's Environment) and every system tier the game would set
## (GraphicsRuntime.apply_system_tiers), renders max(shot settle_frames, --settle) frames and saves <id>.png.
## The capture rig (tests/screenshots/capture.tscn) renders scene defaults; this shows what the
## player's preset does to the same shot. Never writes baselines.
## Diagnosis (M1-QA-05): --light-set=prop=value,... on every DirectionalLight3D (e.g.
## shadow_enabled=false, shadow_normal_bias=2.0, directional_shadow_max_distance=2.0);
## --mat-set=uniform=value,... on every ShaderMaterial that declares the uniform (#rrggbb for colours).
## --push-override=key=value,... pushes a scoped GraphicsSettings override (M1-RND-16, e.g.
## aa=taa,scaling_mode=fsr) on top of the preset for the shot, through the real API, and pops it after.
## --manifest=res://...json reads another manifest (e.g. a pending-shots file); --hold-storm freezes
## every UndertowStorm clock while its temporal jitter keeps advancing (deterministic, TAA integrates);
## add --freeze-jitter to hold the jitter too (a static pattern, the control).
## --node-set=Path:prop=value,... sets a property on a node of the shot's scene (e.g.
## Storm:half_res_compute=false, M2-RND-01).
## --add-box=x,y,z,sx,sy,sz adds an opaque grey box (world centre and size, metres) to the scene, e.g. a
## pillar inside the Undertow's wall foot to check its occlusion (M2-RND-01).
## --setup applies each shot's setup block (globals, nodes, time_scale; not viewport) as capture.tscn does, held every
## frame after the scene's own _process (Act I real-GPU QA: moods, the slice cutscene shots).

const MANIFEST := "res://tests/screenshots/shots.json"

var _opts: Dictionary = {}
var _setup: CaptureSetup = null


func _ready() -> void:
	process_priority = ScreenshotCapture.HOLD_PRIORITY
	_run.call_deferred()


func _process(_delta: float) -> void:
	if _setup != null:
		_setup.hold()


func _run() -> void:
	_opts = _args()
	var out := str(_opts.get("out", ""))
	DirAccess.make_dir_recursive_absolute(out)
	var manifest := JSON.parse_string(FileAccess.get_file_as_string(str(_opts.get("manifest", MANIFEST)))) as Dictionary
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
		# --setup (Act I real-GPU QA): the shot's setup block as capture.tscn applies it (globals, nodes, time_scale),
		# so a scene that needs it (a mood, a cutscene shot's level) is the shot. Its "viewport" key is left out:
		# the preset decides AA here.
		if _opts.has("setup"):
			var spec := (shot.get("setup", {}) as Dictionary).duplicate()
			spec.erase("viewport")
			_setup = CaptureSetup.new(spec)
			var err := _setup.begin(get_viewport())
			if err != "":
				push_error("CAPTURE_PRESET setup %s: %s" % [shot["id"], err])
		var scene := (load(str(shot["scene"])) as PackedScene).instantiate()
		add_child(scene)
		if _setup != null:
			var err := _setup.attach(scene)
			if err != "":
				push_error("CAPTURE_PRESET setup %s: %s" % [shot["id"], err])
		var cam_path := str(shot.get("camera", "default"))
		if cam_path != "default":
			(scene.get_node(NodePath(cam_path)) as Camera3D).make_current()
		await get_tree().process_frame
		var gs := GraphicsSettings.new()
		gs.set_preset(preset)
		var envs := scene.find_children("*", "WorldEnvironment", true, false)
		gs.apply_current(get_viewport(), (envs[0] as WorldEnvironment).environment if envs.size() > 0 else null)
		# Every system tier the game sets on scene entry (M2-RND-02; it was character materials only).
		GraphicsRuntime.apply_system_tiers(scene, preset)
		var handle := 0
		if _opts.has("push-override"):
			var values := {}
			for pair in str(_opts["push-override"]).split(",", false):
				var kv := pair.split("=", true, 1)
				var parsed: Variant = str_to_var(kv[1])
				values[kv[0]] = parsed if parsed is float or parsed is int else kv[1]
			handle = GraphicsSettings.push_override(scene, values, get_viewport(), gs)
		_tweak(scene)
		if _opts.has("add-box"):
			_add_box(scene, str(_opts["add-box"]))
		var held: Array[UndertowStorm] = []
		if _opts.has("hold-storm"):
			for n in scene.find_children("*", "", true, false):
				if n is UndertowStorm:
					(n as UndertowStorm).playing = false
					held.append(n as UndertowStorm)
		for i in maxi(int(shot.get("settle_frames", 1)), int(_opts.get("settle", 60))):
			await get_tree().process_frame
			if not _opts.has("freeze-jitter"):
				for storm in held:
					storm.state.frame += 1
		await RenderingServer.frame_post_draw
		var img := get_viewport().get_texture().get_image()
		img.convert(Image.FORMAT_RGB8)
		img.save_png(out.path_join("%s.png" % shot["id"]))
		print("CAPTURE_PRESET ok %s %s %dx%d" % [shot["id"], preset, win.size.x, win.size.y])
		if handle != 0:
			GraphicsSettings.pop_override(handle)
		if _setup != null:
			_setup.end()
			_setup = null
		scene.queue_free()
		await get_tree().process_frame
	get_tree().quit()


func _tweak(scene: Node) -> void:
	for pair in str(_opts.get("node-set", "")).split(",", false):
		var kv := pair.split("=", true, 1)
		var at := kv[0].split(":", true, 1)
		var node := scene.get_node_or_null(NodePath(at[0]))
		if node == null or at.size() < 2 or kv.size() < 2:
			push_error("--node-set: cannot apply '%s'" % pair)
			continue
		node.set(at[1], str_to_var(kv[1]))
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
				m.set_shader_parameter(kv[0], _value(kv[1]))


## A --mat-set value: a Godot literal (1.5, true, Vector3(...)), or a #rrggbb colour (the list is
## comma-separated, so Color(r, g, b) cannot be passed).
static func _value(text: String) -> Variant:
	if text.begins_with("#") and Color.html_is_valid(text):
		return Color.html(text)
	return str_to_var(text)


func _args() -> Dictionary:
	var out := {}
	for a in OS.get_cmdline_user_args():
		var kv := a.trim_prefix("--").split("=", true, 1)
		out[kv[0]] = kv[1] if kv.size() > 1 else true
	return out


func _add_box(scene: Node, spec: String) -> void:
	var v := spec.split_floats(",", false)
	if v.size() != 6:
		push_error("--add-box wants x,y,z,sx,sy,sz")
		return
	var box := MeshInstance3D.new()
	var mesh := BoxMesh.new()
	mesh.size = Vector3(v[3], v[4], v[5])
	var mat := StandardMaterial3D.new()
	mat.albedo_color = Color(0.5, 0.5, 0.5)
	mesh.material = mat
	box.mesh = mesh
	scene.add_child(box)
	box.global_position = Vector3(v[0], v[1], v[2])
