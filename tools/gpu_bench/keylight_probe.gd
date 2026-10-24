class_name KeylightProbe
extends Node
## GPU check of the cutscene key light (M2-FP-10) on a zone's close shots. Real GPU and window:
##   godot --path . --audio-driver Dummy --fixed-fps 60 --disable-vsync res://tools/gpu_bench/keylight_probe.tscn -- \
##     --scene=res://game/levels/ch02/haluna/haluna.tscn --shots=H05,H06 --preset=high --out=C:/abs/dir \
##     [--res=1920x1080 --settle=90 --bench --frames=300 --key-shadow=false --no-cast=hair,lash
##     --key-pitch=<deg, as the shot's key_pitch_deg> --list-cast --shadow-32=4096
##     --key-set=light_angular_distance=0.0,shadow_blur=0.0]
## For each shot and key on/off: instances the zone, applies the preset (as capture_preset does), puts the
## stage's director on the shot (snapped), engages a CutsceneKeyLight from sequencer.json exactly as the
## sequencer's _key_for() does (or leaves the sun on the cast), renders --settle frames and saves
## <shot>_<preset>_key<on|off>.png. --bench then reads the GPU time for --frames frames and prints one
## "KEYLIGHT_BENCH shot preset key median_ms p99_ms" line. Also prints the zone sun's shadow_normal_bias.

const SEQUENCER := "res://game/data/cutscene/sequencer.json"

var _opts: Dictionary = {}
var _times: Array[float] = []
var _bench_tag := ""


func _ready() -> void:
	_run.call_deferred()


func _run() -> void:
	_opts = _args()
	var out := str(_opts.get("out", ""))
	DirAccess.make_dir_recursive_absolute(out)
	var preset := str(_opts.get("preset", "high"))
	var res := str(_opts.get("res", "1920x1080")).split("x")
	var win := get_window()
	win.borderless = true
	win.position = DisplayServer.screen_get_position(win.current_screen)
	win.size = Vector2i(int(res[0]), int(res[1]))
	var cfg := (
		(JSON.parse_string(FileAccess.get_file_as_string(SEQUENCER)) as Dictionary).get("key_light", {}) as Dictionary
	)
	for shot_id in str(_opts.get("shots", "H05")).split(",", false):
		for key_on: bool in [true, false]:
			var scene := (load(str(_opts["scene"])) as PackedScene).instantiate()
			add_child(scene)
			await get_tree().process_frame
			var gs := GraphicsSettings.new()
			gs.set_preset(preset)
			var envs := scene.find_children("*", "WorldEnvironment", true, false)
			gs.apply_current(get_viewport(), (envs[0] as WorldEnvironment).environment if envs.size() > 0 else null)
			CharacterShaderTiers.apply_to_tree(scene, CharacterShaderTiers.tier_for_preset(preset))
			if _opts.has("shadow-32"):  # diagnosis: --shadow-32=<atlas size>, the atlas at 32-bit depth (presets: 16)
				RenderingServer.directional_shadow_atlas_set_size(int(str(_opts["shadow-32"])), false)
			var stage := scene.find_children("*", "CutsceneStage", true, false)[0] as CutsceneStage
			var director := stage.director()
			director.play_shot(stage.shot(StringName(shot_id)), 0.0)
			director.snap()
			var sun := stage.sun()
			var to_sun := sun.global_basis.z.normalized()
			print(
				(
					"KEYLIGHT_SUN %s bias=%s normal_bias=%s elevation_deg=%.1f"
					% [sun.get_path(), sun.shadow_bias, sun.shadow_normal_bias, rad_to_deg(asin(to_sun.y))]
				)
			)
			if _opts.has("list-cast"):
				for root in stage.cast():
					print("KEYLIGHT_CAST %s at %s" % [root.get_path(), root.global_position])
			if key_on:
				var sn := stage.shot_node(StringName(shot_id))
				var key := CutsceneKeyLight.new(cfg)
				stage.add_child(key)
				var pitch := float(str(_opts["key-pitch"])) if _opts.has("key-pitch") else sn.key_pitch_deg
				key.engage(sun, stage.cast(), sn.key_yaw_deg, pitch, sn.key_energy_scale)
				if _opts.get("key-shadow", "true") == "false":
					key.shadow_enabled = false  # diagnosis: is a key-on artefact its shadow?
				for pair in str(_opts.get("key-set", "")).split(",", false):  # diagnosis: key light properties
					var kv := pair.split("=", true, 1)
					key.set(kv[0], str_to_var(kv[1]))
			# Diagnosis: --no-cast=hair,toma stops cast meshes whose node path contains one of these from casting.
			for sub in str(_opts.get("no-cast", "")).split(",", false):
				for root in stage.cast():
					for g: Node in root.find_children("*", "GeometryInstance3D", true, false):
						if str(g.get_path()).to_lower().contains(sub):
							(g as GeometryInstance3D).cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
							print("KEYLIGHT_NOCAST ", g.get_path())
			for i in int(_opts.get("settle", 90)):
				await get_tree().process_frame
			await RenderingServer.frame_post_draw
			var tag := "%s_%s_key%s" % [shot_id, preset, "on" if key_on else "off"]
			var img := get_viewport().get_texture().get_image()
			img.convert(Image.FORMAT_RGB8)
			img.save_png(out.path_join(tag + ".png"))
			print("KEYLIGHT_PROBE ok %s" % tag)
			if _opts.has("bench"):
				_bench(shot_id, preset, key_on)
				await _bench_frames()
			scene.queue_free()
			await get_tree().process_frame
	get_tree().quit()


func _bench(shot_id: String, preset: String, key_on: bool) -> void:
	_bench_tag = "%s %s %s" % [shot_id, preset, "on" if key_on else "off"]
	RenderingServer.viewport_set_measure_render_time(get_viewport().get_viewport_rid(), true)


func _bench_frames() -> void:
	var rid := get_viewport().get_viewport_rid()
	_times.clear()
	for i in int(_opts.get("warmup", 60)):
		await get_tree().process_frame
	for i in int(_opts.get("frames", 300)):
		await get_tree().process_frame
		_times.append(RenderingServer.viewport_get_measured_render_time_gpu(rid))
	_times.sort()
	var med := _times[_times.size() / 2]
	var p99 := _times[mini(_times.size() - 1, int(_times.size() * 0.99))]
	print("KEYLIGHT_BENCH %s %.3f %.3f" % [_bench_tag, med, p99])


func _args() -> Dictionary:
	var out := {}
	for a in OS.get_cmdline_user_args():
		var kv := a.trim_prefix("--").split("=", true, 1)
		out[kv[0]] = kv[1] if kv.size() > 1 else true
	return out
