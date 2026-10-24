class_name DrownbellProbe
extends Node
## The Drownbell's set piece on the GPU (M2-RND-04): key frames and its cost. Real GPU and window:
##   godot --path . --audio-driver Dummy --fixed-fps 60 --disable-vsync res://tools/gpu_bench/drownbell_probe.tscn -- \
##     --preset=high --res=1920x1080 --out=C:/abs/dir [--bench --frames=300 --reduced-motion]
## Starts the Drownbell on the battle sandbox, applies the preset (GraphicsSettings, then every system tier, as
## the game does on entry) and drives the engine's boss signals in story order, as BossMechanics would.
## - Default: saves <moment>.png at each moment's capture time (MOMENTS).
## - --bench: "DROWNBELL_BENCH <label>_<pass> median p99 max" GPU ms over --frames frames for each pass:
##   low_tide (the opening, the rig's water at -0.7 m), flood (the water up, two polyp lights), and set_piece
##   (the flood plus the toll ring, the floodnet and gather motes replayed every REPLAY_EVERY frames).

const SCENE := "res://game/battle/scene/battle_sandbox.tscn"
const PARTY: Array[StringName] = [&"rhen", &"asha", &"toma"]
const SEED := 20261023
const SETTLE_FRAMES := 90
const REPLAY_EVERY := 90
## [moment, seconds after it starts to capture]. Played in this order.
const MOMENTS := [
	["opening", 0.1],
	["telegraph", 1.4],
	["toll", 0.45],
	["rim_break", 0.25],
	["flood_rising", 4.0],
	["flood_full", 5.0],
	["mend", 0.9],
	["floodnet", 1.3],
	["bell_release", 1.6],
]

var _opts: Dictionary = {}
var _ctl: BattleController
var _vfx: BattleVfx


func _ready() -> void:
	_run.call_deferred()


func _run() -> void:
	_opts = _args()
	var out := str(_opts.get("out", ""))
	DirAccess.make_dir_recursive_absolute(out)
	var res := str(_opts.get("res", "1920x1080")).split("x")
	var win := get_window()
	win.borderless = true
	win.position = DisplayServer.screen_get_position(win.current_screen)
	win.size = Vector2i(int(res[0]), int(res[1]))
	var preset := str(_opts.get("preset", "high"))
	_ctl = (load(SCENE) as PackedScene).instantiate() as BattleController
	_ctl.auto_start = false
	_ctl.persist_progress = false
	add_child(_ctl)
	_ctl.start_battle(PARTY, [], &"drownbell", SEED)
	await get_tree().process_frame
	var gs := GraphicsSettings.new()
	gs.set_preset(preset)
	var envs := _ctl.find_children("*", "WorldEnvironment", true, false)
	gs.apply_current(get_viewport(), (envs[0] as WorldEnvironment).environment if envs.size() > 0 else null)
	GraphicsRuntime.apply_system_tiers(_ctl, preset)
	_vfx = _ctl.stage.get_node(^"BattleVfx") as BattleVfx
	_vfx.reduced_motion = _opts.has("reduced-motion")
	for i in SETTLE_FRAMES:
		await get_tree().process_frame
	if _opts.has("bench"):
		await _bench(preset)
	else:
		for m: Array in MOMENTS:
			_play(str(m[0]))
			await get_tree().create_timer(float(m[1])).timeout
			await RenderingServer.frame_post_draw
			var img := get_viewport().get_texture().get_image()
			img.convert(Image.FORMAT_RGB8)
			img.save_png(out.path_join("%s.png" % m[0]))
			print("DROWNBELL_FRAME ok %s water_y=%.2f" % [m[0], _vfx.boss.water_y()])
	get_tree().quit()


## Drives one moment through the engine's own signals (what BossMechanics emits).
func _play(moment: String) -> void:
	var engine := _ctl.engine
	var bell := engine.enemies[0]
	match moment:
		"telegraph":
			bell.charge_skill = &"toll"
			bell.charge_left = 2
			engine.charge_started.emit(bell, &"toll", 2)
			bell.charge_left = 1
			engine.turn_started.emit(bell)
		"toll":
			engine.action_resolved.emit(_result(bell.id, &"toll", []))
		"rim_break":
			bell.charge_left = 2
			engine.charge_started.emit(bell, &"toll", 2)
			engine.charge_broken.emit(bell, &"toll")
		"flood_rising":
			bell.hp = bell.max_hp * 40 / 100
			BossMechanics.check_phases(engine)
		"mend":
			var polyp := engine.enemies[1]
			engine.action_resolved.emit(_result(polyp.id, &"polyp_mend", [bell.id]))
		"floodnet":
			engine.field_cleared.emit(&"flood", engine.enemies.slice(1) as Array[BattleCombatant])
		"bell_release":
			_vfx.play(&"bell_release", bell.id)


func _result(actor: StringName, skill: StringName, targets: Array) -> ActionResult:
	var r := ActionResult.new()
	r.actor_id = actor
	r.skill_id = skill
	for t: StringName in targets:
		r.hits.append({"target_id": t, "hit": true, "crit": false, "amount": 0})
	return r


func _bench(preset: String) -> void:
	var rid := get_viewport().get_viewport_rid()
	RenderingServer.viewport_set_measure_render_time(rid, true)
	var frames := int(_opts.get("frames", 300))
	var label := "%s%s" % [preset, "_reduced" if _vfx.reduced_motion else ""]
	for pass_name in ["low_tide", "flood", "set_piece"]:
		if pass_name == "flood":
			_play("flood_rising")
			_vfx.boss.water.global_position.y = float(_vfx.boss.flood_target_m)
			for i in 30:
				await get_tree().process_frame
		var times: Array[float] = []
		for i in frames:
			if pass_name == "set_piece" and i % REPLAY_EVERY == 0:
				_play("telegraph")
				_play("toll")
				_vfx.boss._floodnet()
			await get_tree().process_frame
			times.append(RenderingServer.viewport_get_measured_render_time_gpu(rid))
		times.sort()
		print(
			(
				"DROWNBELL_BENCH %s_%s %.3f %.3f %.3f"
				% [label, pass_name, times[times.size() / 2], times[int(times.size() * 0.99)], times[-1]]
			)
		)


func _args() -> Dictionary:
	var out := {}
	for a in OS.get_cmdline_user_args():
		var kv := a.trim_prefix("--").split("=", true, 1)
		out[kv[0]] = kv[1] if kv.size() > 1 else true
	return out
