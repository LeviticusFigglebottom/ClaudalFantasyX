extends Node
## M3-BPR-420 (ADR 0041): renders each Act I boss's big moves (camera.enemy_by_skill) in its own fight and arena, so
## the shots are viewed: the move is built as the engine reports it (ActionResult) and played by the real choreography,
## frozen at the lead shot (`lead` of the way to contact, default 0.7) and at the contact. Saves
## <out>/<encounter>_<skill>_{lead,contact}.png. Run it like a capture:
##   godot-render --path . --audio-driver Dummy --fixed-fps 60 --disable-vsync --rendering-driver vulkan \
##     res://tools/vfx/boss_camera_sheet.tscn -- --out=<abs dir> [--lead=0.7] [--only=<encounter>]
##     [--moment=phase|fall]   (M3-BPR-426: each fight's camera moment instead, mid-hold)
##     [--entry]               (M3-BPR-1325: the Climb's camera cut and its stair effects; M3-BPR-406: the Kirru's)

const SCENE := "res://game/battle/scene/battle_sandbox.tscn"
const PARTY: Array[StringName] = [&"rhen", &"asha", &"toma"]
const SETTLE_FRAMES := 30
const SETTLE_SEC := 2.0
const FIGHTS := {
	&"ch01_hullgnaw": [&"hullgnaw", [&"gnaw", &"thrash"]],
	&"ch04_spar_wraith": [&"spar_wraith", [&"haul", &"sea_lash", &"shroud_sweep"]],
	&"ch05_cinder_matron": [&"cinder_matron", [&"ladle_swing", &"slag_pour"]],
	&"ch06_inquisitor": [&"stillguard_inquisitor", [&"brine_iron", &"torch_hulk"]],
	&"drownbell": [&"drownbell", [&"hood_slam"]],
	&"ch04_bottle_hermit": [&"bottle_hermit", []],  # moments only (no big move)
	&"undertows_reach": [&"undertows_reach", []],  # moments only (its moves keep the default frame)
	# ADR 0205: the Act II creature bosses (PROVISIONAL rows), each move with its own effect
	&"ch10_mangrove_drowner": [&"mangrove_drowner", [&"drowner_drag", &"rising_water", &"root_stamp"]],
	&"ch11_lamp_engine": [&"lamp_engine", [&"lamp_trim", &"lamp_flare", &"core_pulse"]],
	&"ch12_avalanche_ram": [&"avalanche_ram", [&"horn_toss", &"ram_charge", &"ram_bellow"]],
	&"ch15_wakefin": [&"wakefin", [&"fin_cut", &"sound_dive", &"wake_breach", &"wake_wheel"]],
}

var _opts: Dictionary = {}


func _ready() -> void:
	_run.call_deferred()


func _run() -> void:
	_opts = _args()
	var out := str(_opts.get("out", ""))
	DirAccess.make_dir_recursive_absolute(out)
	get_window().size = Vector2i(1280, 720)
	if _opts.has("entry"):  # M3-BPR-1325: the Climb's turn on the stair head, its effects on the mark
		await _entry(out)
		get_tree().quit()
		return
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
		if _opts.has("moment"):  # M3-BPR-426: the phase change's or the fall's camera moment, mid-hold
			await _moment(ctl, boss, out, enc)
			remove_child(ctl)
			ctl.queue_free()
			continue
		for sid: StringName in FIGHTS[enc][1]:
			var r := ActionResult.new()
			r.actor_id = boss.id
			r.skill_id = sid
			var hits: Array[Dictionary] = []
			var row := ctl.engine.db.skill(sid)
			var charge := row.get("charge", {}) as Dictionary
			if str(row.get("target", "")) == "self":  # a telegraph (the Wakefin's Sound Dive): on itself
				hits.append({"target_id": boss.id, "hit": true, "crit": false, "amount": 0, "statuses_added": []})
			for h in ctl.engine.party_active if hits.is_empty() else []:
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
			if not charge.is_empty():  # as BossMechanics: the charge's own staging (M3-BPR-418's blade under)
				var next := StringName(str(charge.get("skill", "")))
				ctl.engine.charge_started.emit(boss, next, maxi(int(charge.get("turns", 1)), 1))
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
			# the last move's particles die out first (Rising Water's teal had hung over Root Stamp's frames)
			await get_tree().create_timer(SETTLE_SEC).timeout
		remove_child(ctl)
		ctl.queue_free()
	get_tree().quit()


## The stair hold's Climb: the entry camera's stair hint held, the stair-aimed effects playing on the Climb's mark.
## Saves <out>/ch08_stair_hold_1_entry.png. M3-BPR-406: then wave 3's Kirru sounding Storm-Call, the cut out to the
## storm held: <out>/ch08_stair_hold_3_kirru.png.
func _entry(out: String) -> void:
	await _entry_cut(out, &"ch08_stair_hold_1", &"ward", &"climb_up", [&"climb_up", &"grip_the_stair", &"hand_closes"])
	await _entry_cut(out, &"ch08_stair_hold_3", &"guest", &"storm_call_sound", [], "kirru")


func _entry_cut(
	out: String, enc: StringName, role: StringName, skill: StringName, effects: Array, tag: String = "entry"
) -> void:
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
	var choreo := ctl.stage.choreo
	choreo.force_play = true
	choreo.reduced_motion = false
	choreo.skip = false
	var who: BattleCombatant = null
	for c in ctl.engine.entries:
		if c.entry_role == role:
			who = c
	var cam := choreo.get_node(^"BattleEntryCamera") as BattleEntryCamera
	var vfx := ctl.stage.get_node(^"BattleVfx") as BattleVfx
	var r := ActionResult.new()
	r.actor_id = who.id
	r.skill_id = skill
	choreo.contact.emit(r)
	choreo.advance(float(cam.cfg.get("in_sec", 0.0)) + 0.2)
	for eid: StringName in effects:
		vfx.play(eid, who.id)
	await get_tree().create_timer(0.3).timeout
	await RenderingServer.frame_post_draw
	var img := get_viewport().get_texture().get_image()
	img.convert(Image.FORMAT_RGB8)
	img.save_png(out.path_join("%s_%s.png" % [enc, tag]))
	print("BOSS_CAMERA_SHEET %s %s %s" % [tag, enc, cam.cut_for])
	remove_child(ctl)
	ctl.queue_free()


## Plays the boss's --moment (phase or fall) and saves <out>/<encounter>_<moment>.png once it is in and held.
func _moment(ctl: BattleController, boss: BattleCombatant, out: String, enc: StringName) -> void:
	var choreo := ctl.stage.choreo
	choreo.reduced_motion = false
	choreo.skip = false
	choreo.speed = 1.0
	var which := str(_opts["moment"])
	if which == "fall":
		boss.hp = 0
		choreo.contact.emit(ActionResult.new())
	else:
		ctl.engine.phase_changed.emit(boss, &"_sheet")
	var row := (choreo.data["camera"]["moments"] as Dictionary).get(which, {}) as Dictionary
	choreo.advance(float(row.get("in_sec", 0.0)) + float(row.get("hold_sec", 0.0)) * 0.5)
	for i in 3:
		await get_tree().process_frame
	await RenderingServer.frame_post_draw
	var img := get_viewport().get_texture().get_image()
	img.convert(Image.FORMAT_RGB8)
	img.save_png(out.path_join("%s_%s.png" % [enc, which]))
	print("BOSS_CAMERA_SHEET %s %s %s" % [enc, which, choreo.camera.moments_played])


## A move on the whole party (its enemy_by_skill lead is boss_sweep, or it targets all foes) hits every hero.
func _sweeps(sid: StringName) -> bool:
	var by_skill := BattleChoreo.load_data()["camera"]["enemy_by_skill"] as Dictionary
	if str((by_skill.get(String(sid), {}) as Dictionary).get("lead", "")) == "boss_sweep":
		return true
	return str(BattleDB.load_default().skill(sid).get("target", "")) == "all_foes"


func _args() -> Dictionary:
	var out := {}
	for a in OS.get_cmdline_user_args():
		var kv := a.trim_prefix("--").split("=", true, 1)
		out[kv[0]] = kv[1] if kv.size() > 1 else true
	return out
