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
## A freeze-frame capture: the sequence never ends, so the controller's hand-off holds forever.
var frozen := false
## Every plan started, in order (tests and tools).
var played: Array[Dictionary] = []
## The victory pose and the escape (M2-BPR-05).
var outro: BattleOutro
## The battle camera director following this sequencer (M2-BPR-03).
var camera: BattleCameraDirector

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
## Fighters walking onto their mark (a swap or a call): combatant id -> seconds walked.
var _entering: Dictionary = {}


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
	var c := BattleChoreo.new()
	c.name = NODE_NAME
	controller.stage.add_child(c)
	controller.stage.choreo = c
	c.attach(controller, engine)
	c.outro = BattleOutro.attached(c, engine)
	c.camera = BattleCameraDirector.attached(controller, c)
	return c


func _init() -> void:
	data = load_data()


func attach(controller: BattleController, engine: BattleEngine) -> void:
	_ctl = controller
	_engine = engine
	engine.action_resolved.connect(_on_action_resolved)
	var settings := UiSettings.shared()
	if settings != null:
		_read_settings(settings)
		settings.changed.connect(func(_key: StringName) -> void: _read_settings(settings))


func _read_settings(settings: UiSettings) -> void:
	reduced_motion = settings.reduced_motion()
	var keys := settings.settings()
	if keys.has(SETTING_SPEED):
		set_speed(float(settings.get_value(SETTING_SPEED)))
	if keys.has(SETTING_ANIMATIONS):
		skip = str(settings.get_value(SETTING_ANIMATIONS)) == ANIMATIONS_SKIP


func set_speed(v: float) -> void:
	var s := data.get("speeds", {}) as Dictionary
	speed = clampf(v, float(s.get("min", 1.0)), float(s.get("max", 1.0)))


func _process(delta: float) -> void:
	if live:
		advance(delta)


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


## Seconds of the current sequence still to play, at the battle speed (0 when none plays).
func remaining_sec() -> float:
	if _plan.is_empty():
		return 0.0
	return maxf(float(_plan["total"]) - _t, 0.0) / speed


## How long the controller holds after an action: `base`, or the choreography's rest plus a settle.
func hold_after(base: float) -> float:
	if _plan.is_empty():
		return base
	_announce()
	if frozen:
		return INF
	return maxf(base, remaining_sec() + float(data.get("settle_sec", 0.0)) / speed)


## Runs `cb` once the current sequence has finished (at once when none plays).
func after_sequence(cb: Callable) -> void:
	if _plan.is_empty():
		cb.call()
	else:
		_after.append(cb)


## True while the stage should hold `cid`'s KO look back (its collapse beat has not come yet).
func holds_ko(cid: StringName) -> bool:
	return _held_ko.has(cid)


## Pillar 4 while an action plays: the controller has already moved the order on, so the timeline head is who
## acts next ("Next", not "Acting now"), and the help line names the action being played (the enemy and
## automatic turns, and a Swell's input grade, already say it). hold_after calls it, right after the hand-off
## has redrawn the order.
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


## The style an action plays: item_style for an item, else style_by_skill, style_by_target, style_by_kind.
func style_id_for(result: ActionResult) -> String:
	if result.item_id != &"":
		return str(data.get("item_style", FALLBACK_STYLE))
	var sid := String(result.skill_id)
	var by_skill := data.get("style_by_skill", {}) as Dictionary
	if by_skill.has(sid):
		return str(by_skill[sid])
	var row: Dictionary = _engine.db.skill(result.skill_id) if _engine != null else {}
	var by_target := data.get("style_by_target", {}) as Dictionary
	if by_target.has(str(row.get("target", ""))):
		return str(by_target[str(row["target"])])
	return str((data.get("style_by_kind", {}) as Dictionary).get(str(row.get("kind", "")), FALLBACK_STYLE))


func style(id: String) -> Dictionary:
	var styles := data.get("styles", {}) as Dictionary
	return styles.get(id, styles.get(FALLBACK_STYLE, {})) as Dictionary


## What an action plays, with no nodes: {style, actor, targets, reactions [{target, kind}], kos, and the beat
## times approach_end, contact, strike_end, recover_end, return_end, ko_at, total}. {} for a failed action.
func plan_for(result: ActionResult) -> Dictionary:
	if result == null or not result.ok:
		return {}
	var sid := style_id_for(result)
	var st := style(sid)
	var a := float(st.get("approach_sec", 0.0))
	var s := float(st.get("strike_sec", 0.0))
	var c := a + s * float(st.get("contact_at", 1.0))
	var rec := a + s + float(st.get("recover_sec", 0.0))
	var ret := rec + float(st.get("return_sec", 0.0))
	var targets: Array[StringName] = []
	var reactions: Array[Dictionary] = []
	var kos: Array[StringName] = []
	var react_end := c
	var reaction := data.get("reaction", {}) as Dictionary
	for hit: Dictionary in result.hits:
		var tid := StringName(str(hit.get("target_id", "")))
		if not targets.has(tid):
			targets.append(tid)
		if tid == result.actor_id:
			continue
		var amount := int(hit.get("amount", 0))
		var kind := REACT_MISS if not bool(hit.get("hit", true)) else (REACT_DAMAGE if amount > 0 else "")
		if kind == "" and amount < 0:
			kind = REACT_HEAL
		if kind != "":
			reactions.append({"target": tid, "kind": kind})
			react_end = maxf(react_end, c + float((reaction.get(kind, {}) as Dictionary).get("sec", 0.0)))
		var t := _engine.find(tid) if _engine != null else null
		if amount > 0 and t != null and t.hp <= 0 and not kos.has(tid):
			kos.append(tid)
	var ko := data.get("ko", {}) as Dictionary
	var ko_at := c + float(ko.get("delay_sec", 0.0))
	var total := maxf(ret, react_end)
	if not kos.is_empty():
		total = maxf(total, ko_at + float(ko.get("collapse_sec", 0.0)))
	return {
		"style": sid,
		"actor": result.actor_id,
		"targets": targets,
		"reactions": reactions,
		"kos": kos,
		"approach_end": a,
		"contact": c,
		"strike_end": a + s,
		"recover_end": rec,
		"return_end": ret,
		"ko_at": ko_at,
		"total": total,
	}


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
			var gap := maxf(_flat_len(aim - from) - float(st.get("stop_short_m", 0.0)), 0.0)
			to = from + dir * gap
		TRAVEL_STEP:
			to = from + dir * float(st.get("step_m", 0.0))
	if reduced_motion:
		to = from + (to - from) * _rm("travel_scale")
	plan["from"] = from
	plan["to"] = to
	plan["dir"] = dir
	plan["aim"] = aim
	plan["actor_clip"] = BattleClips.has_clip(_ctl.stage.stand_in(actor_id), StringName(str(st.get("clip", ""))))
	for r: Dictionary in plan["reactions"]:
		var tid := StringName(str(r["target"]))
		var away := _flat(_home_of(tid).origin - from)
		r["dir"] = away if away != Vector3.ZERO else dir
		var clip := StringName(
			str(((data.get("reaction", {}) as Dictionary).get(r["kind"], {}) as Dictionary).get("clip", ""))
		)
		r["clip"] = BattleClips.has_clip(_ctl.stage.stand_in(tid), clip)
	for k: StringName in plan["kos"]:
		_held_ko[k] = true
	played.append(plan)
	_step_beats()
	_apply()


## Moves the current sequence (and any fighter walking onto its mark) on by `delta` real seconds.
func advance(delta: float) -> void:
	_advance_entering(delta)
	if _plan.is_empty():
		return
	_t += delta * speed
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
	_step_beats()
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
	if not (p["kos"] as Array).is_empty():
		_fire(BEAT_KO, float(p["ko_at"]), _beat_ko)
		_fire(
			&"ko_end",
			float(p["ko_at"]) + float((data.get("ko", {}) as Dictionary).get("collapse_sec", 0.0)),
			_release_kos
		)


func _fire(id: StringName, at: float, cb: Callable) -> void:
	if _fired.has(id) or _t < at or _plan.is_empty():
		return
	if cb.is_valid():
		cb.call()
	_fired[id] = true
	if id != &"ko_end":
		beat.emit(id, StringName(str(_plan.get("actor", ""))))


func _beat_approach() -> void:
	BattleClips.play(_ctl.stage.stand_in(StringName(str(_plan["actor"]))), BattleClips.READY, speed)


func _beat_strike() -> void:
	var clip := StringName(str(style(str(_plan["style"])).get("clip", "")))
	BattleClips.play(_ctl.stage.stand_in(StringName(str(_plan["actor"]))), clip, speed)


func _beat_contact() -> void:
	_ctl.floats.show_hits(_result, false)
	contact.emit(_result)
	var reaction := data.get("reaction", {}) as Dictionary
	for r: Dictionary in _plan["reactions"]:
		if bool(r["clip"]):
			var clip := StringName(str((reaction.get(r["kind"], {}) as Dictionary).get("clip", "")))
			BattleClips.play(_ctl.stage.stand_in(StringName(str(r["target"]))), clip, speed)


## A KO with a clip on the model just lets the stage apply it (the model plays its own KO); a stand-in
## collapses procedurally in _apply until ko_end.
func _beat_ko() -> void:
	for k: StringName in _plan["kos"]:
		if BattleClips.has_clip(_ctl.stage.stand_in(k), BattleClips.KO):
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
	var pos := from
	var lean := 0.0
	if _t < a:
		var u := _ease(_t / a)
		pos = from.lerp(to, u)
		lean = lean_max * 0.5 * u
	elif _t < s_end:
		var u := (_t - a) / (s_end - a)
		var peak := _peak(u, (float(p["contact"]) - a) / (s_end - a))
		pos = to
		lean = lean_max * (0.5 + 0.5 * peak)
		if not bool(p["actor_clip"]):
			pos += dir * float(st.get("lunge_m", 0.0)) * peak
			pos += Vector3.UP * (float(st.get("lift_m", 0.0)) - float(st.get("crouch_m", 0.0))) * peak
	elif _t < rec:
		pos = to
		lean = lean_max * 0.5 * (1.0 - (_t - s_end) / maxf(rec - s_end, 0.0001))
	elif _t < ret:
		pos = to.lerp(from, _ease((_t - rec) / (ret - rec)))
	_pose(actor_id, pos - from, dir, 0.0 if bool(p["actor_clip"]) else lean)
	var poses: Dictionary = {}
	for r: Dictionary in p["reactions"]:
		var tid := StringName(str(r["target"]))
		if not _ko_pose.has(tid):
			poses[tid] = _reaction_pose(r)
	if _fired.has(BEAT_KO) and not _fired.has(&"ko_end"):
		_add_collapse(poses)
	for tid: StringName in poses:
		var q: Array = poses[tid]
		_pose(tid, q[0] as Vector3, q[1] as Vector3, float(q[2]))
	posed.emit(_t)


## [offset, toward, lean_deg] for a target's reaction at the current time (home when it has a clip).
func _reaction_pose(r: Dictionary) -> Array:
	var away: Vector3 = r["dir"]
	var def := (data.get("reaction", {}) as Dictionary).get(r["kind"], {}) as Dictionary
	var sec := float(def.get("sec", 0.0))
	var c := float(_plan["contact"])
	if bool(r["clip"]) or _t < c or sec <= 0.0:
		return [Vector3.ZERO, away, 0.0]
	var w := sin(PI * clampf((_t - c) / sec, 0.0, 1.0))
	var tilt_k := _rm("tilt_scale") if reduced_motion else 1.0
	match str(r["kind"]):
		REACT_DAMAGE:
			return [away * float(def.get("recoil_m", 0.0)) * w, away, float(def.get("tilt_deg", 0.0)) * w * tilt_k]
		REACT_HEAL:
			return [Vector3.UP * float(def.get("lift_m", 0.0)) * w, away, 0.0]
		REACT_MISS:
			return [Vector3.UP.cross(away).normalized() * float(def.get("dodge_m", 0.0)) * w, away, 0.0]
	return [Vector3.ZERO, away, 0.0]


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
	var f := _ctl.stage.stand_in(cid)
	if f == null:
		return
	var home := _home(f)
	var basis := home.basis
	var axis := Vector3.UP.cross(toward)
	if absf(lean_deg) > 0.0 and axis.length() > 0.0:
		basis = Basis(axis.normalized(), deg_to_rad(lean_deg)) * basis
	f.transform = Transform3D(basis, home.origin + offset)


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
	var f := _ctl.stage.stand_in(cid)
	if f != null:
		f.transform = _home(f)


# --- entering (swap, call) ----------------------------------------------------------------


## A fighter the stage just placed (a swap or a Vowbound's call) walks onto its mark from behind it.
func enter(cid: StringName) -> void:
	var f := _ctl.stage.stand_in(cid) if _ctl != null else null
	if f == null:
		return
	_home(f)
	if not animating():
		return
	_entering[cid] = 0.0
	BattleClips.play(f, StringName(str((data.get("enter", {}) as Dictionary).get("clip", ""))), speed)
	_advance_entering(0.0)


func is_entering(cid: StringName) -> bool:
	return _entering.has(cid)


func _advance_entering(delta: float) -> void:
	if _entering.is_empty():
		return
	var cfg := data.get("enter", {}) as Dictionary
	var sec := maxf(float(cfg.get("sec", 0.0)), 0.0001)
	var back := float(cfg.get("back_m", 0.0)) * (_rm("travel_scale") if reduced_motion else 1.0)
	for cid: StringName in _entering.keys():
		var walked := float(_entering[cid]) + delta * speed
		var f := _ctl.stage.stand_in(cid)
		if f == null or walked >= sec:
			_entering.erase(cid)
			_rest(cid)
			continue
		_entering[cid] = walked
		var fwd := _facing(cid)
		_pose(cid, -fwd * back * (1.0 - _ease(walked / sec)), fwd, 0.0)


# --- geometry -----------------------------------------------------------------------------


func _home(f: FighterStandIn) -> Transform3D:
	var key := f.get_instance_id()
	if not _homes.has(key):
		_homes[key] = f.transform
	return _homes[key] as Transform3D


func _home_of(cid: StringName) -> Transform3D:
	var f := _ctl.stage.stand_in(cid)
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
	var from := _home_of(cid).origin
	var sum := Vector3.ZERO
	var n := 0
	for c in _engine.party_active + _engine.enemies:
		if me != null and c.team == me.team:
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
