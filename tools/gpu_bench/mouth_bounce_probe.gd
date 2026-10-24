class_name MouthBounceProbe
extends Node
## GPU check of the unshadowed cavity-bounce pass (M1-RND-24 criterion 2). Real GPU and window:
##   godot --path . --audio-driver Dummy --fixed-fps 60 --disable-vsync res://tools/gpu_bench/mouth_bounce_probe.tscn \
##     -- --shots=asha_face_grief,asha_face_smile --preset=high --out=C:/abs/dir [--scale=1 --settle=60
##     --keys=dir,spot,omni --shadows=on,off --variants=pass,fallback,nobounce,mask --bench --frames=300]
## For each shot (tests/screenshots/shots.json), key, key shadow and variant: instances the shot's scene, applies
## the preset as capture_preset does, and saves <shot>_<preset>_<key>_<shadow>_<variant>.png.
## - Keys: `dir` is the stage's own DirectionalLight3D key. `spot` and `omni` replace it with a positional light
##   along the same direction, KEY_DISTANCE m from the mouth, its energy scaled so the mouth gets the
##   directional key's irradiance (distance falloff and range window), with the key's colour and shadow settings.
## - Shadows: `off` disables the key's shadow (the control: then the fallback equals the pass).
## - Variants: `pass` as shipped (CharacterShaderTiers attaches the bounce pass); `fallback` removes the pass and
##   clears cavity_bounce_pass (the pre-RND-24 bounce, shadow included); `nobounce` sets cavity_bounce 0 (the
##   pre-RND-21 interior); `mask` paints the mouth family unshaded green (the interior's pixels).
## - --push-override=key=value,... pushes a scoped GraphicsSettings override on top of the preset (as capture_preset).
## - --bench prints "MOUTH_BOUNCE_BENCH shot preset key shadow variant median_ms p99_ms" over --frames frames.

const MANIFEST := "res://tests/screenshots/shots.json"
const KEY_PATH := ^"KeyLight"
const KEY_DISTANCE := 2.0
const KEY_RANGE := 6.0
const SPOT_ANGLE := 20.0

var _opts: Dictionary = {}


func _ready() -> void:
	_run.call_deferred()


func _run() -> void:
	_opts = _args()
	var out := str(_opts.get("out", ""))
	DirAccess.make_dir_recursive_absolute(out)
	var manifest := JSON.parse_string(FileAccess.get_file_as_string(MANIFEST)) as Dictionary
	var defaults := manifest.get("defaults", {}) as Dictionary
	var wanted := str(_opts.get("shots", "asha_face_grief")).split(",", false)
	var preset := str(_opts.get("preset", "high"))
	var scale := float(_opts.get("scale", 1.0))
	var win := get_window()
	win.borderless = true
	win.position = DisplayServer.screen_get_position(win.current_screen)
	for shot_v: Variant in manifest.get("shots", []):
		var shot := defaults.merged(shot_v as Dictionary, true)
		if not wanted.has(str(shot["id"])):
			continue
		var res := shot["resolution"] as Array
		win.size = Vector2i(roundi(float(res[0]) * scale), roundi(float(res[1]) * scale))
		for key in str(_opts.get("keys", "dir,spot,omni")).split(",", false):
			for shadow in str(_opts.get("shadows", "on,off")).split(",", false):
				for variant in str(_opts.get("variants", "pass,fallback,nobounce,mask")).split(",", false):
					await _one(shot, preset, key, shadow == "on", variant, out)
	get_tree().quit()


func _one(shot: Dictionary, preset: String, key: String, shadow: bool, variant: String, out: String) -> void:
	var tag := "%s_%s_%s_%s_%s" % [shot["id"], preset, key, "on" if shadow else "off", variant]
	var scene := (load(str(shot["scene"])) as PackedScene).instantiate()
	add_child(scene)
	(scene.get_node(NodePath(str(shot["camera"]))) as Camera3D).make_current()
	await get_tree().process_frame
	var gs := GraphicsSettings.new()
	gs.set_preset(preset)
	var envs := scene.find_children("*", "WorldEnvironment", true, false)
	gs.apply_current(get_viewport(), (envs[0] as WorldEnvironment).environment if envs.size() > 0 else null)
	CharacterShaderTiers.apply_to_tree(scene, CharacterShaderTiers.tier_for_preset(preset))
	var handle := 0
	if _opts.has("push-override"):
		var values := {}
		for pair in str(_opts["push-override"]).split(",", false):
			var kv := pair.split("=", true, 1)
			var parsed: Variant = str_to_var(kv[1])
			values[kv[0]] = parsed if parsed is float or parsed is int or parsed is bool else kv[1]
		handle = GraphicsSettings.push_override(scene, values, get_viewport(), gs)
	var mouth := _mouth_surfaces(scene)
	if mouth.is_empty():
		push_error("MouthBounceProbe: no mouth-family surface in %s" % shot["id"])
	_set_key(scene, key, shadow, _centre(mouth))
	_set_variant(mouth, variant)
	for i in maxi(int(shot.get("settle_frames", 1)), int(_opts.get("settle", 60))):
		await get_tree().process_frame
	await RenderingServer.frame_post_draw
	var img := get_viewport().get_texture().get_image()
	img.convert(Image.FORMAT_RGB8)
	img.save_png(out.path_join("%s.png" % tag))
	print("MOUTH_BOUNCE_FRAME ok %s %dx%d" % [tag, img.get_width(), img.get_height()])
	if _opts.has("bench"):
		await _bench(tag)
	if handle != 0:
		GraphicsSettings.pop_override(handle)
	scene.queue_free()
	await get_tree().process_frame


## [MeshInstance3D, surface, material] for every mouth-family surface (after the tier walk).
func _mouth_surfaces(root: Node) -> Array:
	var found := []
	for n in root.find_children("*", "MeshInstance3D", true, false):
		var mi := n as MeshInstance3D
		if mi.mesh == null:
			continue
		for s in mi.mesh.get_surface_count():
			var sm := mi.get_active_material(s) as ShaderMaterial
			if sm != null and CharacterShaderTiers.family_of(sm.shader) == "mouth":
				found.append([mi, s, sm])
	return found


func _centre(mouth: Array) -> Vector3:
	var box := AABB()
	for i in mouth.size():
		var mi := mouth[i][0] as MeshInstance3D
		var b := mi.global_transform * mi.get_aabb()
		box = b if i == 0 else box.merge(b)
	return box.get_center()


func _set_key(scene: Node, key: String, shadow: bool, at: Vector3) -> void:
	var sun := scene.get_node(KEY_PATH) as DirectionalLight3D
	sun.shadow_enabled = shadow
	if key == "dir":
		return
	var light: Light3D
	var window := pow(clampf(1.0 - pow(KEY_DISTANCE / KEY_RANGE, 4.0), 0.0, 1.0), 2.0)
	if key == "spot":
		var spot := SpotLight3D.new()
		spot.spot_range = KEY_RANGE
		spot.spot_angle = SPOT_ANGLE
		spot.light_energy = sun.light_energy * pow(KEY_DISTANCE, spot.spot_attenuation) / window
		light = spot
	else:
		var omni := OmniLight3D.new()
		omni.omni_range = KEY_RANGE
		omni.light_energy = sun.light_energy * pow(KEY_DISTANCE, omni.omni_attenuation) / window
		light = omni
	light.name = &"ProbeKey"
	light.light_color = sun.light_color
	light.shadow_enabled = shadow
	light.shadow_blur = sun.shadow_blur
	scene.add_child(light)
	# A light shines down its -Z: put it KEY_DISTANCE back along the sun's direction from the mouth.
	light.global_transform = Transform3D(sun.global_basis, at + sun.global_basis.z * KEY_DISTANCE)
	sun.visible = false
	# M1-RND-26: the bounce pass draws only while a positional light reaches the mouth.
	CharacterShaderTiers.refresh_bounce_passes(scene)


func _set_variant(mouth: Array, variant: String) -> void:
	var green := StandardMaterial3D.new()
	green.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	green.albedo_color = Color(0, 1, 0)
	for m: Array in mouth:
		var mi := m[0] as MeshInstance3D
		var sm := m[2] as ShaderMaterial
		match variant:
			"fallback":
				sm.next_pass = null
				sm.set_shader_parameter(CharacterShaderTiers.PARAM_BOUNCE_PASS, false)
			"nobounce":
				sm.set_shader_parameter(&"cavity_bounce", 0.0)
				if sm.next_pass is ShaderMaterial:
					(sm.next_pass as ShaderMaterial).set_shader_parameter(&"cavity_bounce", 0.0)
			"mask":
				mi.set_surface_override_material(int(m[1]), green)


func _bench(tag: String) -> void:
	var rid := get_viewport().get_viewport_rid()
	RenderingServer.viewport_set_measure_render_time(rid, true)
	var times: Array[float] = []
	for i in int(_opts.get("frames", 300)):
		await get_tree().process_frame
		times.append(RenderingServer.viewport_get_measured_render_time_gpu(rid))
	times.sort()
	print(
		(
			"MOUTH_BOUNCE_BENCH %s %.4f %.4f"
			% [tag.replace("_", " "), times[times.size() / 2], times[int(times.size() * 0.99)]]
		)
	)


func _args() -> Dictionary:
	var out := {}
	for a in OS.get_cmdline_user_args():
		var kv := a.trim_prefix("--").split("=", true, 1)
		out[kv[0]] = kv[1] if kv.size() > 1 else true
	return out
