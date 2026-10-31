class_name BattleChoreo
extends Node
## Battle choreography sequencer (M2-BPR-01). Docs: docs/kb/tech/battle_presentation.md.
## - **Listens only.** BattleController._build_engine attaches it with one line, `BattleChoreo.attached(self,
##   engine)`, in the place BattleFloats used to connect. It hooks `engine.action_resolved` and never writes
##   combat state: the engine has already resolved the action when the choreography starts.
## - **Beats.** plan_for() turns an ActionResult into a timed plan with no nodes (tests call it): approach (the
##   actor travels to its strike point), strike (the action's clip, or its procedural motion), contact (the
##   targets react; damage floats and hit VFX land), recover, return. A KO collapses after contact. All times
##   and distances are in game/data/battle/choreo.json.
## - **Turn hand-off.** BattleController.after_action waits BattleStage.hold_after(), which is the choreography's
##   remaining time plus a settle when one plays, so the next turn starts once everyone is back on their mark.
## - **Clips.** A model with the clip plays it (BattleClips, the clip contract); a primitive stand-in moves its
##   root procedurally (lunge, recoil, collapse). Its inner mesh stays the stand-in's own (flinch, KO sink).
## - **Instant.** With the controller's pacing at 0 (tests, captures) or "skip animations", every action lands
##   at once exactly as before this sequencer existed. force_play (freeze-frame captures) overrides that.
## - **Specials (M2-BPR-04).** Generic shape fields (arc_m, windup_m, trace_m, stagger_sec, wave_m_s, react_scale)
##   give the Swell finishers and the Drownbell's toll their own rows; accent() lays a short overlay on a fighter
##   (BattleBossChoreo: the bell's gather sway, rim stagger, the party's flood brace); leave() and enter() play a
##   Vowbound's call, entry, dismissal and fall (BattleVowboundChoreo). All of it moves fighters' roots only.

signal contact(result: ActionResult)
signal beat(kind: StringName, actor_id: StringName)
signal sequence_finished(actor_id: StringName)
## After every pose of a sequence, with its time (the camera director frames from it; M2-BPR-03).
signal posed(t: float)

const DATA_PATH := "res://game/data/battle/choreo.json"
const NODE_NAME := "BattleChoreo"
const TRAVEL_TARGET := "target"
const TRAVEL_STEP := "step"
const BEAT_APPROACH := &"approach"
const BEAT_STRIKE := &"strike"
const BEAT_CONTACT := &"contact"
const BEAT_RECOVER := &"recover"
const BEAT_RETURN := &"return"
const BEAT_KO := &"ko"
const REACT_DAMAGE := "damage"
const REACT_HEAL := "heal"
const REACT_MISS := "miss"
const REACT_IMMUNE := "immune"  # M3-BPR-406: a blow on a damage-immune foe: a hard stop, no recoil
const REACT_PUSH := "push"  # M3-BPR-411: a landed push down the timeline with no damage (the ward shoved back)
const FALLBACK_STYLE := "melee"
const SETTING_SPEED := &"battle_speed"
const SETTING_ANIMATIONS := &"battle_animations"
const ANIMATIONS_SKIP := "skip"

static var _data_cache: Dictionary = {}

var data: Dictionary = {}
## Battle speed (UiSettings battle_speed), clamped to choreo.json speeds.
var speed := 1.0
var reduced_motion := false
## Skip animations (UiSettings battle_animations = skip): every action lands at once.
var skip := false
## Plays even when the controller's pacing is instant (freeze-frame captures).
var force_play := false
## False holds a sequence where it stands (captures); advance() still moves it.
var live := true
## The arena's staging (arenas.json staging): runs and walks scale by arena_travel; arena_tempo scales the speed.
var arena_travel := 1.0
var arena_tempo := 1.0
## A freeze-frame capture: the sequence never ends, so the controller's hand-off holds forever.
var frozen := false
## Every plan started, in order (tests and tools).
var played: Array[Dictionary] = []
## The victory pose and the escape (M2-BPR-05).
var outro: BattleOutro
## The battle camera director following this sequencer (M2-BPR-03).
var camera: BattleCameraDirector
## The Vowbound's call, entry, dismissal and fall (attached() builds it; M2-BPR-04).
var vow: BattleVowboundChoreo
## A Vowbound's first-call cinematic (C10; M2-BPR-08).
var summon: BattleSummonCinematic
## A boss's set-piece motion (null without a boss row in choreo.json bosses; M2-BPR-04).
var boss: BattleBossChoreo
## M3-BPR-401: hit-stop, shake, flash and KO slow-mo on the contact (BattleImpact).
var impact: BattleImpact
## Every foe's gathering charge on stage (M3-BPR-413).
var telegraph: BattleTelegraph

var _ctl: BattleController
var _engine: BattleEngine
var _plan: Dictionary = {}
var _result: ActionResult
var _t := 0.0
var _fired: Dictionary = {}
## Fighter instance id -> the transform the stage placed it at.
var _homes: Dictionary = {}
## Combatant ids whose KO the stage holds back until their collapse beat.
var _held_ko: Dictionary = {}
## Combatant id -> the collapsed transform a procedural KO left it in (cleared on revive).
var _ko_pose: Dictionary = {}
var _after: Array[Callable] = []
## The HUD says an action is playing (help line, the timeline head reads "Next"); undone on finish.
var _announced := false
## Fighters walking (or rising) onto their mark: combatant id -> {t (seconds; < 0 still waiting), spec, fwd}.
var _entering: Dictionary = {}
## Fighters the stage took off the field that still play their exit: [{cid, node, t, spec, fwd, clip}].
var _leaving: Array[Dictionary] = []
## Accents on fighters' roots: combatant id -> {t, spec, back, clip}.
var _accents: Dictionary = {}
var _radii: Dictionary = {}  # combatant id -> footprint radius (M3-BPR-402)


static func load_data() -> Dictionary:
	if _data_cache.is_empty():
		var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(DATA_PATH))
		if typeof(parsed) == TYPE_DICTIONARY:
			_data_cache = (parsed as Dictionary).get("choreo", {}) as Dictionary
		else:
			push_warning("BattleChoreo: cannot read %s" % DATA_PATH)
	return _data_cache


## Builds the sequencer under the controller's stage and connects it to `engine` (a retry replaces it).
static func attached(controller: BattleController, engine: BattleEngine) -> BattleChoreo:
	var old := controller.stage.get_node_or_null(NodePath(NODE_NAME))
	if old != null:
		controller.stage.remove_child(old)
		old.queue_free()
	BattleArena.apply(controller, engine.db, engine.encounter_id)  # M2-BPR-07: before the VFX (the flood rig)
	var c := BattleChoreo.new()
	c.name = NODE_NAME
	controller.stage.add_child(c)
	controller.stage.choreo = c
	c.attach(controller, engine)
	c.outro = BattleOutro.attached(c, engine)
	c.camera = BattleCameraDirector.attached(controller, c)
	c.vow = BattleVowboundChoreo.new(c, engine)  # M2-BPR-04: listen-only, like the sequencer
	c.boss = BattleBossChoreo.attached_if_boss(c, engine)
	c.telegraph = BattleTelegraph.new(c, engine)  # M3-BPR-413: any foe's gathering charge reads on stage
	c.summon = BattleSummonCinematic.attached(c, controller, engine)  # M2-BPR-08: C10
	c.impact = BattleImpact.attached(c, controller, engine)  # M3-BPR-401: battle feel
	BattleBossIntro.attached(c, controller, engine)  # M3-BPR-02: a boss's intro at the first turn
	BattlePhaseLooks.attached(c, controller, engine)  # M3-BPR-406: an untargetable phase shows it
	BattleBossCamera.attached(c, engine)  # M3-BPR-426: a boss's phase change and fall get a shot
	BattleEntryCamera.attached(c, engine)  # M3-BPR-1325: the Climb's turn shows the stair
	return c


func _init() -> void:
	data = load_data()


func attach(controller: BattleController, engine: BattleEngine) -> void:
	_ctl = controller
	_engine = engine
	var staging := BattleArena.staging_for(engine.db, engine.encounter_id)  # M3-BPR-01: per-arena choreography
	arena_travel = float(staging.get("travel_scale", 1.0))
	arena_tempo = float(staging.get("tempo", 1.0))
	set_speed(1.0)
	engine.action_resolved.connect(_on_action_resolved)
	var settings := UiSettings.shared()
	if settings != null:
		_read_settings(settings)
		settings.changed.connect(func(_key: StringName) -> void: _read_settings(settings))


func _read_settings(settings: UiSettings) -> void:
	reduced_motion = settings.reduced_motion()
	var keys := settings.settings()
	if keys.has(SETTING_SPEED):
		set_speed(settings.battle_speed())  # one reader: UiSettings.battle_speed (M2-UI-23)
	if keys.has(SETTING_ANIMATIONS):
		skip = str(settings.get_value(SETTING_ANIMATIONS)) == ANIMATIONS_SKIP


func set_speed(v: float) -> void:
	var s := data.get("speeds", {}) as Dictionary
	speed = clampf(v, float(s.get("min", 1.0)), float(s.get("max", 1.0))) * arena_tempo


func _process(delta: float) -> void:
	if live:
		advance(delta)


## [[home position, radius], ...] of every fighter on the field but `skip` (melee spacing, M3-BPR-402).
func _bodies(skip: StringName) -> Array:
	var out: Array = []
	for c: BattleCombatant in _engine.party_active + _engine.enemies:
		if c.id != skip and c.is_alive() and _ctl.stage.stand_in(c.id) != null:
			out.append([_home_of(c.id).origin, _radius(c.id)])
	return out


func _target_bodies(ids: Array[StringName]) -> Array:
	var out: Array = []
	for cid in ids:
		if _ctl.stage.stand_in(cid) != null:
			out.append([_home_of(cid).origin, _radius(cid)])
	return out


## A fighter's footprint: its model's (BattleChoreoPlan.footprint, cached), else its stand-in spec radius.
func _radius(cid: StringName) -> float:
	if not _radii.has(cid):
		var r := BattleChoreoPlan.footprint(_ctl.stage.stand_in(cid), data)
		_radii[cid] = r if r > 0.0 else float(BattleStage.stand_in_spec(cid).get("radius", 0.0))
	return float(_radii[cid])


## True when actions play as choreography (not instant).
func animating() -> bool:
	return force_play or (not skip and _ctl != null and _ctl.pacing_scale > 0.0)


func playing() -> bool:
	return not _plan.is_empty()


## The plan playing now ({} when none).
func current() -> Dictionary:
	return _plan


## Seconds into the current sequence, in plan time (0 when none plays).
func time() -> float:
	return _t if not _plan.is_empty() else 0.0


## Seconds into the current plan (plan time, at battle speed 1).
func plan_time() -> float:
	return _t


## Seconds of the current sequence still to play, at the battle speed (0 when none plays).
func remaining_sec() -> float:
	if _plan.is_empty():
		return 0.0
	var extra := impact.extra_sec(_plan, _t) if impact != null else 0.0  # hit-stop and slow-mo time
	return maxf(float(_plan["total"]) - _t, 0.0) / speed + extra


## How long the controller holds after an action: `base`, or the choreography's rest plus a settle (an entrance,
## an exit or an accent in progress counts too: a Vowbound's call plays without an action plan).
func hold_after(base: float) -> float:
	var busy := busy_sec()
	if not _plan.is_empty():
		_announce()
		if frozen:
			return INF
	elif busy <= 0.0:
		return base
	return maxf(base, maxf(remaining_sec(), busy) + float(data.get("settle_sec", 0.0)) / speed)


## Seconds (at the battle speed) until every entrance, exit and accent in progress has finished.
func busy_sec() -> float:
	var left := 0.0
	for e: Dictionary in _entering.values() + _leaving + _accents.values():
		left = maxf(left, float((e["spec"] as Dictionary).get("sec", 0.0)) - float(e["t"]))
	left = maxf(left, camera.moment_left() if camera != null else 0.0)  # M3-BPR-426: a boss's camera moment
	return maxf(left / speed, summon.remaining_sec() if summon != null else 0.0)


## M3-CRE-639: an entrance's or exit's clip: its `clip_own` when the fighter's model has that clip (Ilun's `rise`,
## `dismiss`), else its contract `clip`.
static func spec_clip(f: Node, spec: Dictionary) -> StringName:
	var own := StringName(str(spec.get("clip_own", "")))
	if own != &"" and BattleClips.has_clip(f, own):
		return own
	return StringName(str(spec.get("clip", "")))


## Runs `cb` once the current sequence has finished (at once when none plays).
func after_sequence(cb: Callable) -> void:
	if _plan.is_empty():
		cb.call()
	else:
		_after.append(cb)


## True while the stage should hold `cid`'s KO look back (its collapse beat has not come yet).
func holds_ko(cid: StringName) -> bool:
	return _held_ko.has(cid)


## Pillar 4 while an action plays: the controller has already moved the order on, so the timeline head is who acts
## next ("Next", not "Acting now"), and the help line names the action being played (the enemy and automatic turns,
## and a Swell's input grade, already say it). hold_after calls it, right after the hand-off has redrawn the order.
func _announce() -> void:
	if _announced or _result == null:
		return
	_announced = true
	_ctl.hud.timeline.set_head_caption(tr("HUD_TL_NEXT"))
	var actor := _engine.find(_result.actor_id)
	if actor == null or actor.team != BattleCombatant.TEAM_PARTY or _result.auto_reason != &"":
		return
	if _ctl.swell != null and _ctl.swell.is_technique(actor, _result.skill_id):
		return
	var what := (
		_ctl.menus.item_name(_ctl.items, _result.item_id)
		if _result.item_id != &""
		else _ctl.menus.skill_name(_engine, _result.skill_id)
	)
	_ctl.hud.set_help(tr("HUD_ENEMY_ACTS_FMT").format({"name": _ctl.menus.display_name(actor), "skill": what}))


# --- the plan (pure data) -----------------------------------------------------------------


## The style an action plays (BattleChoreoPlan.style_id_for: item, skill, target, kind).
func style_id_for(result: ActionResult) -> String:
	return BattleChoreoPlan.style_id_for(data, _engine, result)


func style(id: String) -> Dictionary:
	return BattleChoreoPlan.style(data, id)


## What an action plays, with no nodes (BattleChoreoPlan.plan_for). {} for a failed action.
func plan_for(result: ActionResult) -> Dictionary:
	return BattleChoreoPlan.plan_for(data, _engine, result)


func _retime(plan: Dictionary) -> void:
	BattleChoreoPlan.retime(data, plan)


# --- playback -----------------------------------------------------------------------------


func _on_action_resolved(result: ActionResult) -> void:
	_ctl.floats.snapshot(result)
	if playing():
		finish()
	var plan := plan_for(result)
	if plan.is_empty() or not animating():
		_ctl.floats.show_hits(result, true)
		contact.emit(result)
		return
	_start(result, plan)


func _start(result: ActionResult, plan: Dictionary) -> void:
	_result = result
	_plan = plan
	_t = 0.0
	_fired = {}
	if impact != null:
		impact.on_plan(plan)
	var actor_id := StringName(str(plan["actor"]))
	var from := _home_of(actor_id).origin
	var targets: Array[StringName] = []
	targets.assign(plan["targets"])
	var aim := _centroid(targets, actor_id)
	var dir := _flat(aim - from)
	if dir == Vector3.ZERO:
		dir = _facing(actor_id)
	var st := style(str(plan["style"]))
	var to := from
	match str(st.get("travel", "")):
		TRAVEL_TARGET:
			var run := BattleChoreoPlan.melee_approach(
				data, st, from, aim, _bodies(actor_id), _target_bodies(targets), _radius(actor_id)
			)
			if run["dir"] != Vector3.ZERO:
				dir = run["dir"]  # M3-BPR-402: it may come at the target from a little to one side
			to = from + dir * float(run["gap"])
		TRAVEL_STEP:
			to = from + dir * float(st.get("step_m", 0.0))
	to = from + (to - from) * (_rm("travel_scale") if reduced_motion else 1.0) * arena_travel
	plan["from"] = from
	plan["to"] = to
	plan["dir"] = dir
	plan["aim"] = aim
	var actor_f := _ctl.stage.stand_in(actor_id)
	var cr_clip := BattleClips.action_clip(actor_f, _result.skill_id, _kind())
	plan["actor_clip"] = cr_clip != &"" or BattleClips.has_clip(actor_f, StringName(str(st.get("clip", ""))))
	var strike_clip := cr_clip if cr_clip != &"" else StringName(str(st.get("clip", "")))
	if bool(plan["actor_clip"]) and BattleClips.contact_sec(actor_f, strike_clip) >= 0.0:  # the clip's own blow
		_move_contact(plan, float(plan["approach_end"]) + BattleClips.contact_sec(actor_f, strike_clip))
	for r: Dictionary in plan["reactions"]:
		var tid := StringName(str(r["target"]))
		var away := _flat(_home_of(tid).origin - from)
		r["dir"] = away if away != Vector3.ZERO else dir
		var clip := StringName(
			str(((data.get("reaction", {}) as Dictionary).get(r["kind"], {}) as Dictionary).get("clip", ""))
		)
		r["clip"] = BattleClips.has_clip(_ctl.stage.stand_in(tid), clip)
		if str(r["counter_by"]) != "":  # the riposte's own blow lands the reaction (M3-BPR-406)
			r["strike_at"] = r["at"]
			r["at"] = float(r["at"]) + maxf(BattleClips.contact_sec(_node_of(r["counter_by"]), BattleClips.ATTACK), 0.0)
			_retime(plan)
	var wave := float(st.get("wave_m_s", 0.0))
	if wave > 0.0:  # a shockwave (the toll): each target reacts as the wave reaches it
		for r: Dictionary in plan["reactions"]:
			r["at"] = float(r["at"]) + _flat_len(_home_of(StringName(str(r["target"]))).origin - from) / wave
		_retime(plan)
	for k: StringName in plan["kos"]:
		_held_ko[k] = true
	played.append(plan)
	_step_beats()
	_apply()


## Moves the current sequence (and any accent, exit or entrance) on by `delta` real seconds.
func advance(delta: float) -> void:
	_advance_accents(delta)
	if _plan.is_empty() and camera != null:
		camera.advance_moment(delta * speed)
	_advance_leaving(delta)
	_advance_entering(delta)
	if _plan.is_empty():
		return
	_t += (impact.warp(delta, _t) if impact != null else delta) * speed
	_step_beats()
	if _plan.is_empty():
		return
	_apply()
	if _t >= float(_plan["total"]):
		finish()


## Jumps the current sequence to `t` seconds into its plan (freeze-frame captures; live = false holds it).
func seek(t: float) -> void:
	if _plan.is_empty():
		return
	_t = clampf(t, 0.0, float(_plan["total"]))
	_apply()  # everyone where they stand at `t` first: a beat's VFX lands there, not on a mark left long ago
	_step_beats()
	if impact != null:
		impact.finish()  # a freeze-frame jump carries no hit-stop
	_apply()


## Ends the current sequence at once: anything it has not landed lands, and everyone stands on their mark.
func finish() -> void:
	if _plan.is_empty() or frozen:
		return
	_t = float(_plan["total"])
	_step_beats()
	var actor_id := StringName(str(_plan["actor"]))
	_rest(actor_id)
	for tid: StringName in _plan["targets"]:
		if not _ko_pose.has(tid):
			_rest(tid)
	if _announced:
		_announced = false
		_ctl.hud.timeline.set_head_caption("")
	_plan = {}
	_result = null
	if impact != null:
		impact.finish()
	sequence_finished.emit(actor_id)
	var pending := _after
	_after = []
	for cb in pending:
		cb.call()


func _step_beats() -> void:
	var p := _plan
	_fire(BEAT_APPROACH, 0.0, _beat_approach)
	_fire(BEAT_STRIKE, float(p["approach_end"]), _beat_strike)
	_fire(BEAT_CONTACT, float(p["contact"]), _beat_contact)
	_fire(BEAT_RECOVER, float(p["strike_end"]), Callable())
	_fire(BEAT_RETURN, float(p["recover_end"]), Callable())
	var reactions: Array = p["reactions"]
	for i in reactions.size():
		if reactions[i].has("strike_at"):
			_fire(StringName("riposte_%d" % i), float(reactions[i]["strike_at"]), _riposte.bind(reactions[i]))
		_fire(StringName("react_%d" % i), float(reactions[i]["at"]), _react.bind(reactions[i]), false)
	if not (p["kos"] as Array).is_empty():
		_fire(BEAT_KO, float(p["ko_at"]), _beat_ko)
		_fire(
			&"ko_end",
			float(p["ko_at"]) + float((data.get("ko", {}) as Dictionary).get("collapse_sec", 0.0)),
			_release_kos,
			false
		)


func _fire(id: StringName, at: float, cb: Callable, announce := true) -> void:
	if _fired.has(id) or _t < at or _plan.is_empty():
		return
	if cb.is_valid():
		cb.call()
	_fired[id] = true
	if announce:
		beat.emit(id, StringName(str(_plan.get("actor", ""))))


func _beat_approach() -> void:
	BattleClips.play(_ctl.stage.stand_in(StringName(str(_plan["actor"]))), BattleClips.READY, speed)


func _beat_strike() -> void:
	var clip := StringName(str(style(str(_plan["style"])).get("clip", "")))
	BattleClips.play_action(
		_ctl.stage.stand_in(StringName(str(_plan["actor"]))), _result.skill_id, _kind(), clip, speed
	)


## The action's skill kind ("" for an item).
func _kind() -> StringName:
	if _result == null or _result.skill_id == &"" or _engine == null:
		return &""
	return StringName(str(_engine.db.skill(_result.skill_id).get("kind", "")))


## Moves the contact beat to `contact` (a creature clip's own contact second): every reaction starts as much later
## (or earlier), the strike's later beats move by as much as the contact passed the strike's end, and _retime puts
## the KO and the total after them, so the blow lands on the clip's frame.
func _move_contact(plan: Dictionary, contact: float) -> void:
	var new_contact := maxf(contact, float(plan["approach_end"]))
	var shift := new_contact - float(plan["contact"])
	var late := maxf(new_contact - float(plan["strike_end"]), 0.0)
	plan["contact"] = new_contact
	for key in ["strike_end", "recover_end", "return_end"]:
		plan[key] = float(plan[key]) + late
	for r: Dictionary in plan["reactions"]:
		r["at"] = float(r["at"]) + shift
	_retime(plan)


func _beat_contact() -> void:
	_ctl.floats.show_hits(_result, false)
	contact.emit(_result)


## A target's reaction starts (on the contact, or later when staggered or reached by a wave): its clip, if any.
func _react(r: Dictionary) -> void:
	if bool(r["clip"]):
		var def := (data.get("reaction", {}) as Dictionary).get(r["kind"], {}) as Dictionary
		BattleClips.play(_ctl.stage.stand_in(StringName(str(r["target"]))), StringName(str(def["clip"])), speed)


func _riposte(r: Dictionary) -> void:
	BattleClips.play(_node_of(StringName(str(r["counter_by"]))), BattleClips.ATTACK, speed)


## A KO with a clip on the model plays it (BattleClips.play_ko) and lets the stage apply it; a stand-in
## collapses procedurally in _apply until ko_end.
func _beat_ko() -> void:
	for k: StringName in _plan["kos"]:
		if BattleClips.play_ko(_ctl.stage.stand_in(k), speed):
			_held_ko.erase(k)
	_ctl.stage.refresh_ko(_engine)


func _release_kos() -> void:
	_apply()  # the collapse at its end pose (ko_end is not marked fired yet)
	for k: StringName in _plan["kos"]:
		if _held_ko.has(k):
			_held_ko.erase(k)
			var f := _ctl.stage.stand_in(k)
			if f != null:
				_ko_pose[k] = f.transform
	_ctl.stage.refresh_ko(_engine)


## A revive: a fighter left collapsed by a procedural KO stands up on its mark again.
func on_ko_state(cid: StringName, ko: bool) -> void:
	BattleClips.ko_changed(_ctl.stage.stand_in(cid), ko)
	if not ko and _ko_pose.has(cid) and not _held_ko.has(cid):
		_ko_pose.erase(cid)
		_rest(cid)


# --- poses --------------------------------------------------------------------------------


func _apply() -> void:
	var p := _plan
	var actor_id := StringName(str(p["actor"]))
	var st := style(str(p["style"]))
	var from: Vector3 = p["from"]
	var to: Vector3 = p["to"]
	var dir: Vector3 = p["dir"]
	var a := float(p["approach_end"])
	var s_end := float(p["strike_end"])
	var rec := float(p["recover_end"])
	var ret := float(p["return_end"])
	var lean_max := float(st.get("lean_deg", 0.0)) * (_rm("lean_scale") if reduced_motion else 1.0)
	var arc := float(st.get("arc_m", 0.0)) * (_rm("travel_scale") if reduced_motion else 1.0)
	var c := float(p["contact"])
	var pos := from
	var lean := 0.0
	if _t < a:
		var u := _ease(_t / a)
		pos = from.lerp(to, u) + Vector3.UP * arc * sin(clampf(_t / a, 0.0, 1.0) * PI * 0.5)  # the leap rises
		lean = lean_max * 0.5 * u
	elif _t < s_end:
		var u := (_t - a) / (s_end - a)
		var cu := (c - a) / (s_end - a)
		var peak := _peak(u, cu)
		pos = to
		if _t < c:  # the plunge: the leap's height falls away, faster and faster, onto the contact
			pos += Vector3.UP * arc * (1.0 - pow((_t - a) / (c - a), 2.0))
		var windup := float(st.get("windup_m", 0.0))
		var wind := 0.0
		var thrust := peak
		if windup != 0.0 and u < cu:  # a planted brace (or a rear-back), and the blow only once it has held
			var at := float(st.get("windup_at", 0.5))
			wind = _peak(u / cu, at)
			thrust = _ease((u / cu - at) / (1.0 - at))
		lean = lean_max * (0.5 + 0.5 * peak - wind)
		if not bool(p["actor_clip"]):
			pos += dir * (float(st.get("lunge_m", 0.0)) * thrust - windup * wind)
			pos += (
				Vector3.UP * (float(st.get("lift_m", 0.0)) * peak - float(st.get("crouch_m", 0.0)) * maxf(peak, wind))
			)
			var trace := float(st.get("trace_m", 0.0))
			if trace != 0.0 and u < cu:  # a glyph written in the air, stroke by stroke, finished on the contact
				var strokes := float(st.get("trace_strokes", 1.0))
				pos += Vector3.UP.cross(dir).normalized() * trace * sin(PI * strokes * u / cu)
	elif _t < rec:
		pos = to
		lean = lean_max * 0.5 * (1.0 - (_t - s_end) / maxf(rec - s_end, 0.0001))
	elif _t < ret:
		pos = to.lerp(from, _ease((_t - rec) / (ret - rec)))
	_pose(actor_id, pos - from, dir, 0.0 if bool(p["actor_clip"]) else lean)
	var poses: Dictionary = {}
	for r: Dictionary in p["reactions"]:
		var tid := StringName(str(r["target"]))
		if not _ko_pose.has(tid) and tid != actor_id:  # an answered actor keeps its run (a counter: clip only)
			var react_k := float(style(str(p["style"])).get("react_scale", 1.0))
			poses[tid] = BattleChoreoPlan.reaction_pose(
				data, r, _t, float(p["contact"]), react_k, _rm("tilt_scale") if reduced_motion else 1.0
			)
	if _fired.has(BEAT_KO) and not _fired.has(&"ko_end"):
		_add_collapse(poses)
	for tid: StringName in poses:
		var q: Array = poses[tid]
		_pose(tid, q[0] as Vector3, q[1] as Vector3, float(q[2]))
	posed.emit(_t)


## A held KO (a stand-in with no KO clip) drops and tips away from the actor on top of its reaction.
func _add_collapse(poses: Dictionary) -> void:
	var ko := data.get("ko", {}) as Dictionary
	var sec := float(ko.get("collapse_sec", 0.0))
	var u := _ease(clampf((_t - float(_plan["ko_at"])) / maxf(sec, 0.0001), 0.0, 1.0))
	for k: StringName in _plan["kos"]:
		if not _held_ko.has(k):
			continue
		var away := _flat(_home_of(k).origin - (_plan["from"] as Vector3))
		if away == Vector3.ZERO:
			away = -_facing(k)
		var q: Array = poses.get(k, [Vector3.ZERO, away, 0.0])
		q[0] = (q[0] as Vector3) + Vector3.DOWN * float(ko.get("drop_m", 0.0)) * u
		q[1] = away
		q[2] = float(q[2]) + float(ko.get("tilt_deg", 0.0)) * u
		poses[k] = q


## Places fighter `cid` at its home moved by `offset`, tipped `lean_deg` toward `toward` (about its feet).
func _pose(cid: StringName, offset: Vector3, toward: Vector3, lean_deg: float) -> void:
	var f := _node_of(cid)
	if f != null:
		_pose_node(f, offset, toward, lean_deg)


## Places `f` at its home moved by `offset`, tipped `lean_deg` toward `toward`, with its accent (if any) on top.
func _pose_node(f: FighterStandIn, offset: Vector3, toward: Vector3, lean_deg: float) -> void:
	var home := _home(f)
	var acc := _accent_now(f.combatant_id)
	var basis := (acc[1] as Basis) * _tipped(home.basis, toward, lean_deg)
	f.transform = Transform3D(basis, home.origin + offset + (acc[0] as Vector3))


static func _tipped(basis: Basis, toward: Vector3, lean_deg: float) -> Basis:
	var axis := Vector3.UP.cross(toward)
	if absf(lean_deg) > 0.0 and axis.length() > 0.0:
		return Basis(axis.normalized(), deg_to_rad(lean_deg)) * basis
	return basis


## Public for BattleOutro: the stand-in, its pose, its rest, its facing, a reduced-motion scale, the ease.
func stand_in(cid: StringName) -> FighterStandIn:
	return _ctl.stage.stand_in(cid) if _ctl != null else null


func pose(cid: StringName, offset: Vector3, toward: Vector3, lean_deg: float) -> void:
	_pose(cid, offset, toward, lean_deg)


func rest(cid: StringName) -> void:
	_rest(cid)


func facing(cid: StringName) -> Vector3:
	return _facing(cid)


func rm(key: String) -> float:
	return _rm(key)


static func ease01(u: float) -> float:
	return _ease(u)


func _rest(cid: StringName) -> void:
	var f := _node_of(cid)
	if f != null:
		f.transform = _home(f)


## The fighter node for `cid`: the stage's, or one the stage took off that has not started its exit yet (a
## Vowbound struck down still takes the blow before it falls; a caller still makes its call).
func _node_of(cid: StringName) -> FighterStandIn:
	var f := _ctl.stage.stand_in(cid) if _ctl != null else null
	if f != null:
		return f
	for e: Dictionary in _leaving:
		if e["cid"] == cid and float(e["t"]) < 0.0 and is_instance_valid(e["node"]):
			return e["node"] as FighterStandIn
	return null


# --- entering, leaving (swap, a Vowbound's call and departure) ------------------------------


## A fighter the stage just placed walks onto its mark from behind it (a swap: choreo.json enter), or plays the
## entrance BattleVowboundChoreo gives it (a Vowbound rising at its slot, the party walking back in after it).
func enter(cid: StringName) -> void:
	var f := _ctl.stage.stand_in(cid) if _ctl != null else null
	if f == null:
		return
	_home(f)
	if not animating():
		return
	var spec: Dictionary = vow.enter_spec(cid) if vow != null else {}
	if spec.is_empty():
		spec = data.get("enter", {}) as Dictionary
	_entering[cid] = {"t": -float(spec.get("delay_sec", 0.0)), "spec": spec, "fwd": _facing(cid), "clip": false}
	_advance_entering(0.0)


## Ends `cid`'s entrance now: it stands on its mark (a skipped cinematic).
func skip_entering(cid: StringName) -> void:
	if _entering.has(cid):
		var e: Dictionary = _entering[cid]
		e["t"] = float((e["spec"] as Dictionary).get("sec", 0.0))
		_advance_entering(0.0)


## Where `cid` stands when the stage placed it, in its parent's space.
func home_origin(cid: StringName) -> Vector3:
	return _home_of(cid).origin


func is_entering(cid: StringName) -> bool:
	return _entering.has(cid)


## The entrance `cid` is playing ({} when none): {t, spec, fwd}.
func entering(cid: StringName) -> Dictionary:
	return _entering.get(cid, {}) as Dictionary


## From back_m behind the mark and depth_m under it, tipped lean_deg forward, onto the mark over sec (eased),
## after delay_sec unseen. Reduced motion shortens the walk (travel_scale) and the tip, never the rise.
func _advance_entering(delta: float) -> void:
	if _entering.is_empty():
		return
	var travel := (_rm("travel_scale") if reduced_motion else 1.0) * arena_travel
	var lean_k := _rm("lean_scale") if reduced_motion else 1.0
	for cid: StringName in _entering.keys():
		var e: Dictionary = _entering[cid]
		var spec: Dictionary = e["spec"]
		var sec := float(spec.get("sec", 0.0))
		var t := float(e["t"]) + delta * speed
		var f := _ctl.stage.stand_in(cid)
		if f == null or t >= sec:  # a zero-length entrance (summon_cinematic "off") is there at once
			_entering.erase(cid)
			if f != null:
				f.visible = true
				_rest(cid)
			continue
		e["t"] = t
		f.visible = t >= 0.0
		if t >= 0.0 and not bool(e["clip"]):
			e["clip"] = true
			BattleClips.play(f, spec_clip(f, spec), speed)
		var k := 1.0 - _ease(maxf(t, 0.0) / maxf(sec, 0.0001))
		var fwd: Vector3 = e["fwd"]
		var off := -fwd * float(spec.get("back_m", 0.0)) * travel + Vector3.DOWN * float(spec.get("depth_m", 0.0))
		_pose_node(f, off * k, fwd, float(spec.get("lean_deg", 0.0)) * lean_k * k)


## The stage takes `f` (combatant `cid`) off the field (BattleStage.sync_party). A swap's leaver goes at once, as
## before; BattleVowboundChoreo gives the party's step-off at a call and a Vowbound's departure or fall, which
## play out (the node no longer belongs to the stage) and then free it.
func leave(cid: StringName, f: FighterStandIn) -> void:
	var spec: Dictionary = vow.leave_spec(cid) if vow != null else {}
	if spec.is_empty() or not animating():
		f.queue_free()
		return
	var home := _home(f)
	var e := {"cid": cid, "node": f, "t": -float(spec.get("delay_sec", 0.0)), "spec": spec, "clip": false}
	e["fwd"] = _facing_from(home.origin, BattleCombatant.TEAM_PARTY)
	_leaving.append(e)
	if spec.has("accent"):  # played while it still stands (a Vowbound's caller makes its call)
		accent(cid, spec["accent"] as Dictionary)


## The exit `cid` is playing ({} when none): {cid, node, t, spec, fwd}.
func leaving(cid: StringName) -> Dictionary:
	for e: Dictionary in _leaving:
		if e["cid"] == cid:
			return e
	return {}


## Holds on the mark through delay_sec, then back_m back and depth_m down, tipped tilt_deg back, over sec.
func _advance_leaving(delta: float) -> void:
	var travel := (_rm("travel_scale") if reduced_motion else 1.0) * arena_travel
	var lean_k := _rm("lean_scale") if reduced_motion else 1.0
	for e: Dictionary in _leaving.duplicate():
		var spec: Dictionary = e["spec"]
		var sec := maxf(float(spec.get("sec", 0.0)), 0.0001)
		e["t"] = float(e["t"]) + delta * speed
		if not is_instance_valid(e["node"]):  # freed under us (M3-HER-1153): check before the cast, drop the row
			_leaving.erase(e)
			continue
		var f := e["node"] as FighterStandIn
		if float(e["t"]) >= sec:
			_leaving.erase(e)
			f.queue_free()
			continue
		if float(e["t"]) < 0.0:
			continue  # still on the field: the sequence (and an accent) pose it
		if not bool(e["clip"]):
			e["clip"] = true
			BattleClips.play(f, spec_clip(f, spec), speed)
		var u := _ease(float(e["t"]) / sec)
		var back := -(e["fwd"] as Vector3)
		var off := back * float(spec.get("back_m", 0.0)) * travel + Vector3.DOWN * float(spec.get("depth_m", 0.0))
		_pose_node(f, off * u, back, float(spec.get("tilt_deg", 0.0)) * lean_k * u)


func _exit_tree() -> void:
	for e: Dictionary in _leaving:
		if is_instance_valid(e["node"]):
			(e["node"] as Node).queue_free()
	_leaving.clear()
	for cid: StringName in _entering:
		var f := _ctl.stage.stand_in(cid) if _ctl != null else null
		if f != null:
			f.visible = true
	_entering.clear()


# --- accents (a boss's set piece, a Vowbound's caller) ----------------------------------------


## A short overlay on `cid`'s root after `delay` seconds, on top of whatever else moves it (its own action, a
## reaction, an entrance). `spec` (choreo.json): sec; lift_m and crouch_m (up, down); recoil_m and tilt_deg (back,
## away from the other side; negative leans in); sway_deg and sways (side to side, that many times); clip. Out and
## back over sec. A fallen fighter takes none. Nothing when actions land instantly.
func accent(cid: StringName, spec: Dictionary, delay := 0.0) -> void:
	var f := _node_of(cid)
	var c := _engine.find(cid) if _engine != null else null
	if f == null or not animating() or float(spec.get("sec", 0.0)) <= 0.0 or (c != null and c.hp <= 0):
		return
	if _ko_pose.has(cid) or _held_ko.has(cid):
		return
	_home(f)
	_accents[cid] = {"t": -delay, "spec": spec, "back": -_facing(cid), "clip": false}
	_advance_accents(0.0)


func has_accent(cid: StringName) -> bool:
	return _accents.has(cid)


func _advance_accents(delta: float) -> void:
	for cid: StringName in _accents.keys():
		var e: Dictionary = _accents[cid]
		var spec: Dictionary = e["spec"]
		e["t"] = float(e["t"]) + delta * speed
		var f := _node_of(cid)
		if f == null or float(e["t"]) >= float(spec.get("sec", 0.0)):
			_accents.erase(cid)
			if f != null and not _moved_elsewhere(cid):
				_rest(cid)
			continue
		if float(e["t"]) >= 0.0 and not bool(e["clip"]):
			e["clip"] = true
			BattleClips.play(f, StringName(str(spec.get("clip", ""))), speed)
		if not _moved_elsewhere(cid):
			_pose(cid, Vector3.ZERO, e["back"] as Vector3, 0.0)


## True when the sequence, an entrance or a KO pose places `cid` (each adds the accent itself).
func _moved_elsewhere(cid: StringName) -> bool:
	if _entering.has(cid) or _ko_pose.has(cid):
		return true
	if _plan.is_empty():
		return false
	if StringName(str(_plan["actor"])) == cid or (_plan["kos"] as Array).has(cid):
		return true
	for r: Dictionary in _plan["reactions"]:
		if r["target"] == cid:
			return true
	return false


## [offset, basis] of `cid`'s accent now (none: [ZERO, IDENTITY]).
func _accent_now(cid: StringName) -> Array:
	var e: Dictionary = _accents.get(cid, {})
	if e.is_empty() or float(e["t"]) < 0.0:
		return [Vector3.ZERO, Basis.IDENTITY]
	var spec: Dictionary = e["spec"]
	var u := clampf(float(e["t"]) / maxf(float(spec.get("sec", 0.0)), 0.0001), 0.0, 1.0)
	var env := sin(PI * u)
	var back: Vector3 = e["back"]
	var side := Vector3.UP.cross(back)
	var travel := (_rm("travel_scale") if reduced_motion else 1.0) * arena_travel
	var lean_k := _rm("lean_scale") if reduced_motion else 1.0
	var off := Vector3.UP * (float(spec.get("lift_m", 0.0)) - float(spec.get("crouch_m", 0.0))) * env
	off += back * float(spec.get("recoil_m", 0.0)) * travel * env
	var sway := float(spec.get("sway_deg", 0.0)) * sin(TAU * float(spec.get("sways", 0.0)) * u) * env
	var basis := _tipped(Basis.IDENTITY, back, float(spec.get("tilt_deg", 0.0)) * lean_k * env)
	return [off, _tipped(basis, side, sway * lean_k)]


# --- geometry -----------------------------------------------------------------------------


func _home(f: FighterStandIn) -> Transform3D:
	var key := f.get_instance_id()
	if not _homes.has(key):
		_homes[key] = f.transform
	return _homes[key] as Transform3D


func _home_of(cid: StringName) -> Transform3D:
	var f := _node_of(cid)
	return _home(f) if f != null else Transform3D()


## The middle of `ids`' marks (other than the actor's); the opposing side's middle when there are none.
func _centroid(ids: Array[StringName], actor_id: StringName) -> Vector3:
	var sum := Vector3.ZERO
	var n := 0
	for cid in ids:
		if cid != actor_id and _ctl.stage.stand_in(cid) != null:
			sum += _home_of(cid).origin
			n += 1
	if n == 0:
		return _home_of(actor_id).origin + _facing(actor_id)
	return sum / n


## The flat direction from `cid`'s mark toward the other side's fighters.
func _facing(cid: StringName) -> Vector3:
	var me := _engine.find(cid) if _engine != null else null
	return _facing_from(_home_of(cid).origin, me.team if me != null else &"")


## The flat direction from `from` toward the fighters not on `team` (every fighter when `team` is &"").
func _facing_from(from: Vector3, team: StringName) -> Vector3:
	var sum := Vector3.ZERO
	var n := 0
	for c in _engine.party_active + _engine.enemies:
		if team != &"" and c.team == team:
			continue
		if _ctl.stage.stand_in(c.id) != null:
			sum += _home_of(c.id).origin
			n += 1
	var d := _flat(sum / n - from) if n > 0 else Vector3.ZERO
	return d if d != Vector3.ZERO else Vector3.FORWARD


func _rm(key: String) -> float:
	return float((data.get("reduced_motion", {}) as Dictionary).get(key, 1.0))


static func _flat(v: Vector3) -> Vector3:
	var f := Vector3(v.x, 0.0, v.z)
	return f.normalized() if f.length() > 0.0 else Vector3.ZERO


static func _flat_len(v: Vector3) -> float:
	return Vector2(v.x, v.z).length()


static func _ease(u: float) -> float:
	return smoothstep(0.0, 1.0, clampf(u, 0.0, 1.0))


## 0 at u = 0, 1 at u = `top` (the contact), back to 0 at u = 1, eased both ways.
static func _peak(u: float, top: float) -> float:
	if u <= top:
		return _ease(u / maxf(top, 0.0001))
	return 1.0 - _ease((u - top) / maxf(1.0 - top, 0.0001))
