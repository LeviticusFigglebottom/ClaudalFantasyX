extends Node
## M3-C05-06 / M3-C06-05: Kerrid's and Liss's Swell techniques played for real in their own fights, so each finisher is
## viewed. The hero's gauge is filled and the turn is theirs; BattleSwell.perform resolves the technique (played at
## good) through the engine, and the real choreography plays it, frozen at the lead shot (`lead` of the way to contact,
## default 0.7), at the contact, and held there `after` seconds on (default 0.25) while the effects play out. Saves
## <out>/<hero>_<technique>_{lead,contact,after}.png. Run it like a capture:
##   godot-render --path . --audio-driver Dummy --fixed-fps 60 --disable-vsync --rendering-driver vulkan \
##     res://tools/vfx/swell_finisher_sheet.tscn -- --out=<abs dir> [--lead=0.7] [--after=0.25] [--only=<hero>]

const SCENE := "res://game/battle/scene/battle_sandbox.tscn"
const SETTLE_FRAMES := 30
## hero -> [encounter, party (the hero first), technique]
const FIGHTS := {
	&"kerrid": [&"ch05_cinder_matron", [&"kerrid", &"toma", &"asha"], &"long_hold"],
	&"liss": [&"ch08_stair_hold_3", [&"liss", &"toma", &"rhen"], &"three_reel_charge"],
}

var _opts: Dictionary = {}


func _ready() -> void:
	_run.call_deferred()


func _run() -> void:
	_opts = _args()
	var out := str(_opts.get("out", ""))
	DirAccess.make_dir_recursive_absolute(out)
	get_window().size = Vector2i(1280, 720)
	for hero: StringName in FIGHTS:
		if _opts.has("only") and str(_opts["only"]) != String(hero):
			continue
		await _play(hero, out)
	get_tree().quit()


func _play(hero: StringName, out: String) -> void:
	var enc: StringName = FIGHTS[hero][0]
	var party: Array[StringName] = []
	party.assign(FIGHTS[hero][1])
	var tech: StringName = FIGHTS[hero][2]
	var ctl := (load(SCENE) as PackedScene).instantiate() as BattleController
	ctl.auto_start = false
	ctl.persist_progress = false
	ctl.show_damage_numbers = false
	add_child(ctl)
	ctl.pacing_scale = 0.0
	ctl.set_meta(BattleBossIntro.META_PLAYED, String(enc))
	ctl.start_battle(party, [], enc, 20261029)
	for i in SETTLE_FRAMES:
		await get_tree().process_frame
	var actor := ctl.engine.find(hero)
	actor.swell = Formulas.SWELL_MAX
	ctl.engine.current = actor
	var targets: Array[BattleCombatant] = []
	for e in ctl.engine.enemies:
		if e.is_alive() and (targets.is_empty() or str(ctl.engine.db.skill(tech).get("target", "")) == "all_foes"):
			targets.append(e)
	var choreo := ctl.stage.choreo
	ctl.pacing_scale = 1.0
	choreo.force_play = true
	choreo.live = false
	choreo.frozen = true
	choreo.reduced_motion = false
	choreo.skip = false
	choreo.speed = 1.0
	var input := ctl.swell.input_for(actor)
	var r := ctl.swell.perform(tech, targets, SwellInput.scripted_result(input, SwellInput.QUALITY_GOOD))
	print("SWELL_FINISHER_SHEET %s %s ok=%s bonus=%d hits=%d" % [hero, tech, r.ok, r.swell_bonus_pct, r.hits.size()])
	var c := float(choreo.current().get("contact", 0.5))
	for moment: String in ["lead", "contact", "after"]:
		if moment == "after":  # the choreography stays held at the contact; the effects run on in real time
			await get_tree().create_timer(float(_opts.get("after", 0.25))).timeout
		else:
			choreo.seek(c * float(_opts.get("lead", 0.7)) if moment == "lead" else c)
			for i in 3:
				await get_tree().process_frame
		await RenderingServer.frame_post_draw
		var img := get_viewport().get_texture().get_image()
		img.convert(Image.FORMAT_RGB8)
		img.save_png(out.path_join("%s_%s_%s.png" % [hero, tech, moment]))
		print("SWELL_FINISHER_SHEET %s %s %s %s" % [hero, tech, moment, choreo.camera.shot_ids])
	print("SWELL_FINISHER_SHEET %s effects %s" % [hero, (ctl.stage.get_node(^"BattleVfx") as BattleVfx).played])
	choreo.frozen = false
	remove_child(ctl)
	ctl.queue_free()


func _args() -> Dictionary:
	var out := {}
	for a in OS.get_cmdline_user_args():
		var kv := a.trim_prefix("--").split("=", true, 1)
		out[kv[0]] = kv[1] if kv.size() > 1 else true
	return out
