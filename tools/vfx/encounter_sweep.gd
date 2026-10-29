extends Node
## The Act I encounter sweep (the Lead, 10-29): every Act I encounter played on the real battle stage, at real pacing,
## with freeze-frame stills and automatic checks. Per encounter it saves <out>/<encounter>/<nn>_<tag>.png at:
##   the opening (once the intro and the banner are over), each party action type (attack, skill, item, Swell,
##   Vowbound call), each enemy action (once per skill), and the victory.
## and writes <out>/<encounter>/checks.json:
##   arena      the arena shown (BattleArena META) against encounters.json's (a missing or fallen-back arena fails);
##   impacts    every landed hit with an effect on its target, every added status with a status effect;
##   framing    at each contact: the actor and its first target on screen, in front of the camera, and not under
##              the command menu, the party panel, the timeline or the help line;
##   dead       the longest run of frames with nothing animating while the battle waits on no one.
## The party plays by a sweep policy: an unused action type first (a Swell is filled when the turn comes, a Vowbound
## is made known when the encounter's chapter has bound it), else role_answer. After max_actions (default 18) the
## fight finishes at fast pacing (the role_answer policy, every sequence finished) and the victory is shot.
## Run it like a capture:
##   godot-render --path . --audio-driver Dummy --fixed-fps 60 --disable-vsync --rendering-driver vulkan \
##     res://tools/vfx/encounter_sweep.tscn -- --out=<abs dir> [--only=<id>,<id>] [--max_actions=18]

const SCENE := "res://game/battle/scene/battle_sandbox.tscn"
const TARGETS := "res://tools/balance/targets.json"
const DEFAULT_ACTIVE: Array[StringName] = [&"rhen", &"asha", &"toma"]
const SEED := 20261029
## The bag the party fights with (the field's inventory is the save's; a fresh one is empty).
const BAG := {"ember_pot": 2, "salt_tonic": 3}
const ITEM := &"ember_pot"
const FAST_STEP_SEC := 30.0
const MAX_FAST_STEPS := 4000
const MAX_FRAMES := 60 * 240  # a fight that has not ended in 4 minutes of real pacing goes fast
const DEAD_MIN_SEC := 0.6
const SCREEN_MARGIN := 0.02
## The chapter from which each Act I Vowbound is bound (its call is shot from then on).
const BOUND_FROM := {&"ilun": 4, &"kahre": 6, &"virel": 9}

var _opts: Dictionary = {}
var _ctl: BattleController
var _dir := ""
var _shot := 0
var _pending: Array[String] = []
var _checks: Dictionary = {}
var _done_types: Dictionary = {}
var _foe_skills: Dictionary = {}
var _cam: Camera3D


func _ready() -> void:
	_run.call_deferred()


func _run() -> void:
	_opts = _args()
	var out := str(_opts.get("out", ""))
	DirAccess.make_dir_recursive_absolute(out)
	get_window().size = Vector2i(1280, 720)
	var only := str(_opts.get("only", "")).split(",", false)
	var summary: Array = []
	for enc: StringName in act_one_encounters():
		if not only.is_empty() and not only.has(String(enc)):
			continue
		summary.append(await _sweep(enc, out))
	var f := FileAccess.open(out.path_join("summary.json"), FileAccess.WRITE)
	f.store_string(JSON.stringify(summary, "  "))
	f.close()
	get_tree().quit()


## Every encounter a player meets from the title to the end of Ch9 (ADR 0041): ch01..ch09, the slice's drownbell and
## the Reach. Not the sandbox's own.
static func act_one_encounters() -> Array[StringName]:
	var out: Array[StringName] = []
	for id: StringName in BattleDB.load_default().encounters:
		var s := String(id)
		if s == "sandbox_reef":
			continue
		if s.begins_with("ch") and s.substr(2, 2).is_valid_int() and int(s.substr(2, 2)) > 9:
			continue
		out.append(id)
	return out


static func chapter_of(enc: StringName) -> int:
	var s := String(enc)
	if s.begins_with("ch") and s.substr(2, 2).is_valid_int():
		return int(s.substr(2, 2))
	return 8 if s == "undertows_reach" else 3  # the Reach is Ch8's; the Drownbell ends the slice (Ch3)


## The sim suite's party for `enc` (targets.json), else the default three.
static func party_for(enc: StringName) -> Array:
	var t := JSON.parse_string(FileAccess.get_file_as_string(TARGETS)) as Dictionary
	for s: Dictionary in t.get("suites", []):
		if StringName(str(s.get("encounter", ""))) == enc:
			var a: Array[StringName] = []
			var r: Array[StringName] = []
			a.assign((s.get("active", []) as Array).map(func(x: Variant) -> StringName: return StringName(str(x))))
			r.assign((s.get("reserve", []) as Array).map(func(x: Variant) -> StringName: return StringName(str(x))))
			return [a, r]
	return [DEFAULT_ACTIVE.duplicate(), [] as Array[StringName]]


func _sweep(enc: StringName, out: String) -> Dictionary:
	_dir = out.path_join(String(enc))
	DirAccess.make_dir_recursive_absolute(_dir)
	_shot = 0
	_pending.clear()
	_done_types = {}
	_foe_skills = {}
	_checks = {"encounter": String(enc), "arena": {}, "impacts": [], "framing": [], "dead_max_sec": 0.0, "shots": []}
	var party := party_for(enc)
	_ctl = (load(SCENE) as PackedScene).instantiate() as BattleController
	_ctl.auto_start = false
	_ctl.persist_progress = false
	_ctl.show_damage_numbers = true
	add_child(_ctl)
	_ctl.pacing_scale = 1.0
	var item_db := ItemDB.load_default()
	_ctl.items = InventoryItemSource.new(item_db, Inventory.new(item_db, BAG.duplicate()))
	_ctl.start_battle(party[0], party[1], enc, SEED)
	var engine := _ctl.engine
	var chapter := chapter_of(enc)
	for vid: StringName in BOUND_FROM:
		if chapter >= int(BOUND_FROM[vid]) and engine.vowbound.rows.has(vid) and not engine.vowbound.known.has(vid):
			engine.vowbound.known.append(vid)
	_check_arena(enc)
	var choreo := _ctl.stage.choreo
	choreo.contact.connect(_on_contact)
	engine.action_resolved.connect(_on_resolved)
	_cam = get_viewport().get_camera_3d()
	var policy := SimPolicyRoleAnswer.new()
	policy.config = {"guard_ward": true, "call_vowbound": "at_once"}
	policy.swell = _ctl.swell
	policy.swell_quality = SwellInput.QUALITY_GOOD
	var opened := false
	var actions := 0
	var frames := 0
	var dead := 0.0
	var max_actions := int(_opts.get("max_actions", 18))
	while engine.outcome == &"" and frames < MAX_FRAMES and actions < max_actions:
		frames += 1
		await get_tree().process_frame
		await _flush()
		var intro := BattleBossIntro.of(_ctl.stage)
		var animating := (
			choreo.playing()
			or (choreo.camera != null and choreo.camera.moment_left() > 0.0)
			or (intro != null and intro.playing())
			or _ctl.is_waiting()
		)
		var ready := _ctl.state == BattleController.STATE_COMMAND and engine.is_party_turn() and not choreo.playing()
		if not opened and ready:
			opened = true
			await _capture("opening")
		if ready:
			dead = 0.0
			actions += 1
			var who := engine.current
			var now := engine.now
			_party_turn(policy)
			if engine.outcome == &"" and engine.current == who and engine.now == now and engine.is_party_turn():
				policy.take_turn(engine)  # the sweep's pick was refused: the turn must still end
				_ctl.after_action(who.id)
		elif animating or _ctl.state == BattleController.STATE_SWELL_INPUT:
			dead = 0.0
		else:
			dead += get_process_delta_time()
			_checks["dead_max_sec"] = maxf(float(_checks["dead_max_sec"]), dead)
	# The rest at fast pacing, the stills taken; then the victory on the real stage.
	var steps := 0
	while engine.outcome == &"" and steps < MAX_FAST_STEPS:
		steps += 1
		if _ctl.state == BattleController.STATE_COMMAND and engine.is_party_turn():
			var actor := engine.current.id
			policy.take_turn(engine)
			_ctl.after_action(actor)
		if choreo.playing():
			choreo.finish()
		var intro2 := BattleBossIntro.of(_ctl.stage)
		if intro2 != null and intro2.playing():
			intro2.skip()
		_ctl.tick(FAST_STEP_SEC)
	_pending.clear()
	for i in 150:  # the victory beat (BattleOutro's poses), before the result panel
		await get_tree().process_frame
	await _capture("end_" + String(engine.outcome))
	_checks["outcome"] = String(engine.outcome)
	_checks["actions"] = actions
	var f := FileAccess.open(_dir.path_join("checks.json"), FileAccess.WRITE)
	f.store_string(JSON.stringify(_checks, "  "))
	f.close()
	remove_child(_ctl)
	_ctl.queue_free()
	await get_tree().process_frame
	print("ENCOUNTER_SWEEP %s outcome=%s actions=%d shots=%d" % [enc, engine.outcome, actions, _shot])
	return _checks


## The sweep's party turn: an action type not yet shot, else role_answer.
func _party_turn(policy: SimPolicy) -> void:
	var engine := _ctl.engine
	var actor := engine.current
	if not _done_types.has("swell") and _ctl.swell != null and not _ctl.swell.techniques(actor).is_empty():
		actor.swell = Formulas.SWELL_MAX
		if policy.unleash_swell(engine):
			_mark("swell")
			_ctl.after_action(actor.id)
			return
	if not _done_types.has("vowbound") and not engine.vowbound.callable_ids(engine).is_empty():
		if engine.summon(engine.vowbound.callable_ids(engine)[0]):
			_mark("vowbound")
			_ctl.after_action(actor.id)
			return
	if not _done_types.has("item"):  # a thrown item on a foe (the item style, its effect on the foe)
		var foes0 := _ctl.default_targets(&"attack")
		if not foes0.is_empty():
			var res := _ctl.use_item_on(ITEM, [foes0[0].id] as Array[StringName])
			if res != null and res.ok:
				_mark("item")
				return
	if not _done_types.has("skill"):
		for sid: StringName in SimPolicy.usable_skills(engine, actor):
			if sid == &"attack" or bool(engine.db.skill(sid).get("swell", false)):
				continue
			var targets := _ctl.default_targets(sid)
			if targets.is_empty():
				continue
			var ids: Array[StringName] = []
			for t in targets:
				ids.append(t.id)
			var res2 := _ctl.act(sid, ids)
			if res2 != null and res2.ok:
				_mark("skill")
				return
	if not _done_types.has("attack"):
		var foes := _ctl.default_targets(&"attack")
		if not foes.is_empty():
			var res3 := _ctl.act(&"attack", [foes[0].id] as Array[StringName])
			if res3 != null and res3.ok:
				_mark("attack")
				return
	policy.take_turn(engine)
	_ctl.after_action(actor.id)


## The type the next party contact is shot as.
func _mark(kind: String) -> void:
	_done_types[kind] = "next"


func _on_resolved(result: ActionResult) -> void:
	if not result.ok:
		return
	var vfx := _ctl.stage.get_node_or_null(^"BattleVfx") as BattleVfx
	if vfx == null:
		return
	var effects := vfx.effects_for(result)
	for h: Dictionary in result.hits:
		var tid := StringName(str(h.get("target_id", "")))
		var landed := bool(h.get("hit", false)) and int(h.get("amount", 0)) != 0
		var statuses := (h.get("statuses_added", []) as Array).size() > 0
		if not landed and not statuses:
			continue
		var on_target := effects.filter(func(e: Dictionary) -> bool: return e["target"] == tid)
		if on_target.is_empty():
			_checks["impacts"].append(
				{"actor": String(result.actor_id), "skill": String(result.skill_id), "target": String(tid)}
			)


func _on_contact(result: ActionResult) -> void:
	var c := _ctl.engine.find(result.actor_id)
	if c == null:
		return
	var tag := ""
	if c.team == BattleCombatant.TEAM_ENEMY or c.entry_role != &"":  # a foe, or a set piece's entry (the Climb)
		var sid := String(result.skill_id)
		if not _foe_skills.has(sid):
			_foe_skills[sid] = true
			var kind := "entry" if c.entry_role != &"" else "foe"
			tag = "%s_%s_%s" % [kind, BattleVfx.base_id(c.id), sid]
	else:
		for kind: String in _done_types:
			if str(_done_types[kind]) == "next":
				_done_types[kind] = "shot"
				tag = "party_%s_%s" % [kind, String(result.skill_id if result.skill_id != &"" else result.item_id)]
	if tag != "":
		_pending.append(tag)
		_check_framing(result, tag)


func _flush() -> void:
	while not _pending.is_empty():
		await _capture(_pending.pop_front())


func _capture(tag: String) -> void:
	await RenderingServer.frame_post_draw
	var img := get_viewport().get_texture().get_image()
	img.convert(Image.FORMAT_RGB8)
	var name := "%02d_%s.png" % [_shot, tag]
	img.save_png(_dir.path_join(name))
	(_checks["shots"] as Array).append(name)
	_shot += 1


func _check_arena(enc: StringName) -> void:
	var want := BattleArena.scene_for(_ctl.engine.db, enc)
	var shown := str(_ctl.get_meta(BattleArena.META_ARENA, ""))
	_checks["arena"] = {"want": want, "shown": shown, "ok": want != "" and shown == want}


## The actor and its first target on screen, in front of the camera, and clear of the HUD's panels.
func _check_framing(result: ActionResult, tag: String) -> void:
	var vfx := _ctl.stage.get_node_or_null(^"BattleVfx") as BattleVfx
	if vfx == null or _cam == null:
		return
	var ids: Array[StringName] = [result.actor_id]
	if not result.hits.is_empty():
		ids.append(StringName(str(result.hits[0].get("target_id", ""))))
	var size := get_viewport().get_visible_rect().size
	var panels: Array[Control] = [_ctl.hud.commands, _ctl.hud.party, _ctl.hud.timeline]
	for cid in ids:
		if not _ctl.stage.has_fighter(cid):
			continue
		var p := vfx.anchor(cid, "chest")
		var issue := ""
		if _cam.is_position_behind(p):
			issue = "behind the camera"
		else:
			var s := _cam.unproject_position(p)
			var inner := Rect2(size * SCREEN_MARGIN, size * (1.0 - 2.0 * SCREEN_MARGIN))
			if not inner.has_point(s):
				issue = "off screen at %s" % s
			else:
				for panel in panels:
					if panel != null and panel.is_visible_in_tree() and panel.get_global_rect().has_point(s):
						issue = "under %s" % panel.name
		if issue != "":
			_checks["framing"].append({"shot": tag, "fighter": String(cid), "issue": issue})
	# Hidden behind someone: another fighter across the lens's sight line to a target's middle (the director's test).
	var dir := _ctl.stage.choreo.camera
	var plan := _ctl.stage.choreo.current()
	if dir != null and not plan.is_empty():
		var pose := {"pos": _cam.transform.origin}
		var mids := dir._target_mids(plan, result.actor_id)
		for b: AABB in dir._bystander_boxes(result.actor_id, plan["targets"]):
			if BattleCameraDirector._blocked(pose, b, mids):
				_checks["framing"].append({"shot": tag, "issue": "a target hidden behind a bystander"})
				break


func _args() -> Dictionary:
	var out := {}
	for a in OS.get_cmdline_user_args():
		var kv := a.trim_prefix("--").split("=", true, 1)
		out[kv[0]] = kv[1] if kv.size() > 1 else true
	return out
