extends Node
## M3-BPR-420 (ADR 0041): renders each Act I boss's big moves (camera.enemy_by_skill) in its own fight and arena, so
## the shots are viewed: the move is built as the engine reports it (ActionResult) and played by the real choreography,
## frozen at the lead shot (`lead` of the way to contact, default 0.7) and at the contact. Saves
## <out>/<encounter>_<skill>_{lead,contact}.png. Run it like a capture:
##   godot-render --path . --audio-driver Dummy --fixed-fps 60 --disable-vsync --rendering-driver vulkan \
##     res://tools/vfx/boss_camera_sheet.tscn -- --out=<abs dir> [--lead=0.7] [--only=<encounter>]

const SCENE := "res://game/battle/scene/battle_sandbox.tscn"
const PARTY: Array[StringName] = [&"rhen", &"asha", &"toma"]
const SETTLE_FRAMES := 30
const FIGHTS := {
	&"ch01_hullgnaw": [&"hullgnaw", [&"gnaw", &"thrash"]],
	&"ch04_spar_wraith": [&"spar_wraith", [&"haul", &"sea_lash", &"shroud_sweep"]],
	&"ch05_cinder_matron": [&"cinder_matron", [&"ladle_swing", &"slag_pour"]],
	&"ch06_inquisitor": [&"stillguard_inquisitor", [&"brine_iron", &"torch_hulk"]],
	&"drownbell": [&"drownbell", [&"hood_slam"]],
	&"undertows_reach": [&"undertows_reach", [&"crust_slam", &"undertow_pull", &"breach"]],
}

var _opts: Dictionary = {}


func _ready() -> void:
	_run.call_deferred()


func _run() -> void:
	_opts = _args()
	var out := str(_opts.get("out", ""))
	DirAccess.make_dir_recursive_absolute(out)
	get_window().size = Vector2i(1280, 720)
	for enc: StringName in FIGHTS:
		if _opts.has("only") and str(_opts["only"]) != String(enc):
			continue
		var ctl := (load(SCENE) as PackedScene).instantiate() as BattleController
		ctl.auto_start = false
		ctl.persist_progress = false
		ctl.show_damage_numbers = false
		add_child(ctl)
		ctl.pacing_scale = 0.0
		ctl.set_meta(BattleBossIntro.META_PLAYED, String(enc))
		ctl.start_battle(PARTY, [], enc, 20261028)
		for i in SETTLE_FRAMES:
			await get_tree().process_frame
		var boss: BattleCombatant = null
		for e in ctl.engine.enemies:
			if String(e.id).get_slice("#", 0) == String(FIGHTS[enc][0]):
				boss = e
		var choreo := ctl.stage.choreo
		for sid: StringName in FIGHTS[enc][1]:
			var r := ActionResult.new()
			r.actor_id = boss.id
			r.skill_id = sid
			var hits: Array = []
			for h in ctl.engine.party_active:
				hits.append({"target_id": h.id, "hit": true, "crit": false, "amount": 10, "statuses_added": []})
				if not _sweeps(sid):
					break
			r.hits = hits
			ctl.pacing_scale = 1.0
			choreo.force_play = true
			choreo.live = false
			choreo.frozen = true
			choreo.reduced_motion = false
			choreo.skip = false
			choreo.speed = 1.0
			ctl.engine.action_resolved.emit(r)
			var c := float(choreo.current().get("contact", 0.5))
			for moment: String in ["lead", "contact"]:
				choreo.seek(c * float(_opts.get("lead", 0.7)) if moment == "lead" else c)
				for i in 3:
					await get_tree().process_frame
				await RenderingServer.frame_post_draw
				var img := get_viewport().get_texture().get_image()
				img.convert(Image.FORMAT_RGB8)
				img.save_png(out.path_join("%s_%s_%s.png" % [enc, sid, moment]))
				print("BOSS_CAMERA_SHEET %s %s %s %s" % [enc, sid, moment, choreo.camera.shot_ids])
			choreo.frozen = false
			choreo.seek(float(choreo.current().get("total", 0.0)) + 1.0)
			for i in 10:
				await get_tree().process_frame
		remove_child(ctl)
		ctl.queue_free()
	get_tree().quit()


## A move on the whole party (its enemy_by_skill lead is boss_sweep) hits every hero.
func _sweeps(sid: StringName) -> bool:
	var by_skill := BattleChoreo.load_data()["camera"]["enemy_by_skill"] as Dictionary
	return str((by_skill.get(String(sid), {}) as Dictionary).get("lead", "")) == "boss_sweep"


func _args() -> Dictionary:
	var out := {}
	for a in OS.get_cmdline_user_args():
		var kv := a.trim_prefix("--").split("=", true, 1)
		out[kv[0]] = kv[1] if kv.size() > 1 else true
	return out
