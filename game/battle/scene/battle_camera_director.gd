class_name BattleCameraDirector
extends Node
## Battle camera director (M2-BPR-03). Docs: docs/kb/tech/battle_presentation.md, Camera director.
## - **Listens only.** BattleChoreo.attached builds it under the sequencer. It follows the sequencer's `posed`
##   (every pose of a sequence, with its time) and `sequence_finished`, and writes only %BattleCamera's transform
##   and fov. BattleStage.shake() keeps its h_offset on top.
## - **Shots** are data (choreo.json "camera"): a party action's lead shot (actor, cast or finisher by style) and
##   its contact shot (the target); an enemy action a gentle push toward its target. Every shot is framed off the
##   battle axis taken from the authored default, so the party stays screen-right, the foes screen-left, and the
##   camera never rolls.
## - **Deterministic.** The camera is a pure function of the plan and its plan time: the shots are placed once
##   when a sequence starts, then frame_at(t) blends them with eased weights. The same time gives the same frame
##   (freeze-frame captures seek), at any battle speed.
## - **Tactical clarity.** The out blend ends exactly on the sequence end, so the default frame is back before the
##   controller's hand-off (sequence + settle) opens the next command menu. A shot that would put a target outside
##   the HUD-safe frame, or the actor (at its strike point) off screen, falls back to the default.
## - **Accessibility.** Reduced motion and skip animations keep the camera on the default: no travel, no cuts.

const NODE_NAME := "BattleCameraDirector"
const META_DEFAULT := &"battle_camera_default"
const META_FOV := &"battle_camera_default_fov"
const ANCHOR_ACTOR := "actor"
const ANCHOR_STRIKE := "strike"
const ANCHOR_TARGET := "target"
const ANCHOR_DEFAULT := "default"
const ANCHORS: Array[String] = [ANCHOR_ACTOR, ANCHOR_STRIKE, ANCHOR_TARGET, ANCHOR_DEFAULT]
const LEAD := "lead"
const CONTACT := "contact"
const FALLBACK_STYLE := "melee"

## choreo.json "camera".
var data: Dictionary = {}
var camera: Camera3D
## The camera's authored transform and fov (the readable wide every sequence returns to).
var default_transform := Transform3D.IDENTITY
var default_fov := 0.0
## The shots framing the current sequence: {"lead": id, "contact": id}; "" where it stays on the default
## (none in the data, or a shot that failed the safe frame).
var shot_ids: Dictionary = {}
## Camera moments played (shot ids, in order; tests and tools). M3-BPR-426.
var moments_played: Array[StringName] = []

var _choreo: BattleChoreo
var _ctl: BattleController
var _plan: Dictionary = {}
var _lead: Dictionary = {}
var _contact: Dictionary = {}
var _moment: Dictionary = {}
var _in_end := 0.0
var _contact_start := 0.0
var _contact_end := 0.0
var _out_start := 0.0
var _out_end := 0.0


## Builds the director under `choreo` and points it at the stage camera (a retry replaces it with the sequencer).
static func attached(controller: BattleController, choreo: BattleChoreo) -> BattleCameraDirector:
	var d := BattleCameraDirector.new()
	d.name = NODE_NAME
	choreo.add_child(d)
	d.attach(controller, choreo)
	return d


func attach(controller: BattleController, choreo: BattleChoreo) -> void:
	_ctl = controller
	_choreo = choreo
	data = choreo.data.get("camera", {}) as Dictionary
	camera = controller.stage.camera
	if camera == null:
		return
	if not camera.has_meta(META_DEFAULT):  # the first attach keeps the authored frame (a retry finds it)
		camera.set_meta(META_DEFAULT, camera.transform)
		camera.set_meta(META_FOV, camera.fov)
	default_transform = camera.get_meta(META_DEFAULT) as Transform3D
	default_fov = float(camera.get_meta(META_FOV))
	_fit_rest_to_the_fight()
	rest()
	choreo.posed.connect(_on_posed)
	choreo.sequence_finished.connect(func(_actor: StringName) -> void: rest())


## M3-BPR-425 (the PC's GPU QA row 36): a foe too big for the authored frame (camera.rest_by_enemy, by its enemy id)
## moves this fight's rest frame back_m along the view and up_m higher, still looking at the authored look point, at
## its own fov. The authored frame stays the camera's meta, so the next fight starts from it.
func _fit_rest_to_the_fight() -> void:
	var rows := data.get("rest_by_enemy", {}) as Dictionary
	if _ctl.engine == null or rows.is_empty():
		return
	for e in _ctl.engine.enemies:
		var row := rows.get(String(e.id).get_slice("#", 0), {}) as Dictionary
		if row.is_empty():
			continue
		var look := _default_pose()["look"] as Vector3
		var pos := (
			default_transform.origin
			+ default_transform.basis.z * float(row.get("back_m", 0.0))
			+ Vector3.UP * float(row.get("up_m", 0.0))
		)
		default_transform = Transform3D(Basis.looking_at(look - pos, Vector3.UP), pos)
		default_fov = float(row.get("fov", default_fov))
		return


## M3-BPR-426: a camera moment outside a sequence (a boss's phase change, its fall): `pose` ({pos, look, fov}, the
## camera's parent space), in over in_sec from the rest frame, held hold_sec, home over out_sec; `tag` names it in
## moments_played. BattleChoreo.busy_sec waits for it, so the next turn's menu finds the camera home. None under
## reduced motion, skipped animations or instant pacing (nothing would advance it), or for an empty pose; a sequence
## that starts takes the camera over. Returns whether it plays.
func play_moment(tag: StringName, pose: Dictionary, in_sec: float, hold_sec: float, out_sec: float) -> bool:
	_moment = {}
	if camera == null or still() or pose.is_empty() or not _choreo.animating():
		return false  # instant pacing plays no moment: the turn must not wait on one
	_moment = {"pose": pose, "in": in_sec, "hold": hold_sec, "out": out_sec, "t": 0.0}
	moments_played.append(tag)
	return true


## Seconds (battle speed applied by the caller) the camera moment still needs; 0 when none plays.
func moment_left() -> float:
	if _moment.is_empty():
		return 0.0
	return maxf(float(_moment["in"]) + float(_moment["hold"]) + float(_moment["out"]) - float(_moment["t"]), 0.0)


## Steps the camera moment (BattleChoreo.advance, while no sequence plays).
func advance_moment(delta: float) -> void:
	if _moment.is_empty():
		return
	_moment["t"] = float(_moment["t"]) + delta
	var t := float(_moment["t"])
	var total := float(_moment["in"]) + float(_moment["hold"]) + float(_moment["out"])
	if t >= total:
		_moment = {}
		rest()
		return
	var home := _default_pose()
	var w_in := _weight(t, 0.0, float(_moment["in"]))
	var w_out := _weight(t, total - float(_moment["out"]), total)
	var pose := _mix(_mix(home, _moment["pose"] as Dictionary, w_in), home, w_out)
	var pos: Vector3 = pose["pos"]
	camera.transform = Transform3D(Basis.looking_at((pose["look"] as Vector3) - pos, Vector3.UP), pos)
	camera.fov = float(pose["fov"])


## True when the camera keeps to the default whatever plays (reduced motion, skip animations).
func still() -> bool:
	return _choreo == null or _choreo.reduced_motion or _choreo.skip


## Puts the camera on the default frame and forgets the sequence.
func rest() -> void:
	_plan = {}
	shot_ids = {}
	if camera != null:
		camera.transform = default_transform
		camera.fov = rest_fov()


## The resting frame's fov: the default, narrowed while a foe gathers a telegraphed skill named in camera.pressure
## ({skill: {turns, max_fov_deg}}), a step a turn as its charge counts down (M3-BPR-406: the Reach's Breach, read
## as a closing clock). The plain default under reduced motion or skipped animations.
func rest_fov() -> float:
	if still() or _ctl == null or _ctl.engine == null:
		return default_fov
	var pressure := data.get("pressure", {}) as Dictionary
	var most := 0.0
	for e in _ctl.engine.enemies:
		var by := (pressure.get("by_enemy", {}) as Dictionary).get(String(e.id).get_slice("#", 0), {}) as Dictionary
		if e.is_alive() and e.is_charging() and (pressure.has(String(e.charge_skill)) or not by.is_empty()):
			var row := by if not by.is_empty() else pressure[String(e.charge_skill)] as Dictionary
			var turns := maxf(float(row.get("turns", 1)), 1.0)
			var k := clampf((turns - float(e.charge_left) + 1.0) / turns, 0.0, 1.0)
			most = maxf(most, float(row.get("max_fov_deg", 0.0)) * k)
	return default_fov - most


## True when the camera stands on the default frame.
func at_default() -> bool:
	return (
		camera != null
		and camera.transform.is_equal_approx(default_transform)
		and is_equal_approx(camera.fov, rest_fov())
	)


func _on_posed(t: float) -> void:
	var plan := _choreo.current()
	if camera == null or plan.is_empty():
		return
	_moment = {}  # a sequence takes the camera over
	if still():
		rest()
		return
	if not is_same(plan, _plan):
		_setup(plan)
	var f := frame_at(t)
	camera.transform = f["transform"] as Transform3D
	camera.fov = float(f["fov"])


# --- the frame (a pure function of the plan and its time) ---------------------------------


## The camera's {transform, fov} at plan time `t` of the current sequence (the default when none plays).
func frame_at(t: float) -> Dictionary:
	var rest_frame := {"transform": default_transform, "fov": rest_fov()}
	if _plan.is_empty() or still() or (_lead.is_empty() and _contact.is_empty()):
		return rest_frame
	var w_out := _weight(t, _out_start, _out_end)
	if t <= 0.0 or w_out >= 1.0:
		return rest_frame
	var home := _default_pose()
	var pose := home
	if not _lead.is_empty():
		pose = _mix(pose, _lead, _weight(t, 0.0, _in_end))
	if not _contact.is_empty():
		pose = _mix(pose, _contact, _weight(t, _contact_start, _contact_end))
	pose = _mix(pose, home, w_out)
	var pos: Vector3 = pose["pos"]
	var xform := Transform3D(Basis.looking_at((pose["look"] as Vector3) - pos, Vector3.UP), pos)
	return {"transform": xform, "fov": float(pose["fov"])}


func _setup(plan: Dictionary) -> void:
	_plan = plan
	_lead = {}
	_contact = {}
	shot_ids = {LEAD: "", CONTACT: ""}
	var actor_id := StringName(str(plan["actor"]))
	var actor := _ctl.engine.find(actor_id) if _ctl.engine != null else null
	var pair := data.get("enemy", {}) as Dictionary
	if actor != null and actor.team == BattleCombatant.TEAM_PARTY:
		var by_style := data.get("by_style", {}) as Dictionary
		pair = by_style.get(str(plan["style"]), by_style.get(FALLBACK_STYLE, {})) as Dictionary
	elif (data.get("enemy_by_skill", {}) as Dictionary).has(str(plan.get("skill", ""))):  # M3-BPR-420: big moves
		pair = (data["enemy_by_skill"] as Dictionary)[str(plan["skill"])] as Dictionary
	elif (data.get("enemy_by_actor", {}) as Dictionary).has(String(actor_id).get_slice("#", 0)):  # M3-BPR-408
		pair = (data["enemy_by_actor"] as Dictionary)[String(actor_id).get_slice("#", 0)] as Dictionary  # the Ram
	var space := _space(actor_id)
	var from: Vector3 = space * (plan["from"] as Vector3)
	var to: Vector3 = space * (plan["to"] as Vector3)
	var aim: Vector3 = space * (plan.get("aim", plan["to"]) as Vector3)
	var targets := _target_points(plan, actor_id)
	var head := _actor_head(actor_id)
	# M3-BPR-420: a foe's body at its strike point must not stand between the lens and its targets (the Reach's lunge)
	var body := _body_box(actor_id) if actor != null and actor.team != BattleCombatant.TEAM_PARTY else AABB()
	body.position += to - from
	for slot: String in [LEAD, CONTACT]:
		var id := str(pair.get(slot, ""))
		var pose := shot_pose(id, from, to, aim)
		var actor_pts: Array[Vector3] = [head + to - from]  # the actor at its strike point: who acts
		if pose.is_empty() or not _frames(pose, targets, actor_pts) or _blocked(pose, body, targets):
			continue
		shot_ids[slot] = id
		if slot == LEAD:
			_lead = pose
		else:
			_contact = pose
	var c := float(plan["contact"])
	_in_end = minf(float(data.get("blend_in_sec", 0.0)), c)
	_contact_end = c
	_contact_start = maxf(c - float(data.get("to_contact_sec", 0.0)), 0.0)
	_out_end = float(plan["total"])
	var hold_until := c + float(data.get("hold_contact_sec", 0.0))
	_out_start = clampf(maxf(_out_end - float(data.get("blend_out_sec", 0.0)), hold_until), 0.0, _out_end)


## A shot's {pos, look, fov} in the camera's parent space ({} for "" or an unknown shot). `from` is the actor's
## mark, `to` its strike point, `aim` the targets' middle.
func shot_pose(id: String, from: Vector3, to: Vector3, aim: Vector3) -> Dictionary:
	var shots := data.get("shots", {}) as Dictionary
	if id == "" or not shots.has(id):
		return {}
	var def := shots[id] as Dictionary
	var home := _default_pose()
	var raised := aim + Vector3.UP * float(def.get("look_up_m", 0.0))
	var look_at := float(def.get("look_at", 0.0))
	var pos: Vector3
	var look: Vector3
	var anchor := str(def.get("anchor", ANCHOR_DEFAULT))
	if anchor == ANCHOR_DEFAULT:
		pos = (home["pos"] as Vector3).lerp(raised, float(def.get("push", 0.0)))
		look = (home["look"] as Vector3).lerp(raised, look_at)
	else:
		var origin := from if anchor == ANCHOR_ACTOR else (to if anchor == ANCHOR_STRIKE else aim)
		pos = (
			origin
			- axis() * float(def.get("back_m", 0.0))
			+ viewer_side() * float(def.get("side_m", 0.0))
			+ Vector3.UP * float(def.get("up_m", 0.0))
		)
		look = from.lerp(aim, look_at) + Vector3.UP * float(def.get("look_up_m", 0.0))
	return {"pos": pos, "look": look, "fov": float(def.get("fov", default_fov))}


## The battle axis, party toward foes: the default camera's screen-left, flat.
func axis() -> Vector3:
	return BattleChoreo._flat(-default_transform.basis.x)


## Toward the default camera's side of the axis, flat (side_m > 0 keeps every shot on the viewer's side).
func viewer_side() -> Vector3:
	return BattleChoreo._flat(default_transform.basis.z)


# --- safe frame -----------------------------------------------------------------------------


## True when every target point lies inside the HUD-safe frame and every actor point on screen, seen from `pose`.
func _frames(pose: Dictionary, targets: Array[Vector3], actor_pts: Array[Vector3]) -> bool:
	var pos: Vector3 = pose["pos"]
	var xform := Transform3D(Basis.looking_at((pose["look"] as Vector3) - pos, Vector3.UP), pos)
	var safe := data.get("safe_frame", {}) as Dictionary
	for p in targets:
		if not in_frame(xform, float(pose["fov"]), p, safe):
			return false
	for p in actor_pts:
		if not in_frame(xform, float(pose["fov"]), p, {}):
			return false
	return true


## True when point `p` (camera parent space) projects inside the screen less `margins` (fractions per side).
func in_frame(xform: Transform3D, fov: float, p: Vector3, margins: Dictionary) -> bool:
	var q := xform.affine_inverse() * p
	var depth := -q.z
	if depth <= float(data.get("near_m", 0.0)):
		return false
	var half := tan(deg_to_rad(fov) * 0.5)
	var aspect := _aspect()
	var half_w := half * aspect
	var half_h := half
	if camera != null and camera.keep_aspect == Camera3D.KEEP_WIDTH:
		half_w = half
		half_h = half / aspect
	var x := q.x / (depth * half_w)
	var y := q.y / (depth * half_h)
	var left := -1.0 + 2.0 * float(margins.get("left", 0.0))
	var right := 1.0 - 2.0 * float(margins.get("right", 0.0))
	var bottom := -1.0 + 2.0 * float(margins.get("bottom", 0.0))
	var top := 1.0 - 2.0 * float(margins.get("top", 0.0))
	return x >= left and x <= right and y >= bottom and y <= top


## The design aspect (project viewport size), not the window's: the same shots pass in tests, captures and play.
## The layout keeps its height, so a wider window only shows more at the sides.
func _aspect() -> float:
	var w := float(ProjectSettings.get_setting("display/window/size/viewport_width", 1))
	var h := float(ProjectSettings.get_setting("display/window/size/viewport_height", 1))
	return w / maxf(h, 1.0)


## The fighter's visible meshes' bounds (camera parent space); an empty AABB for a primitive or a missing fighter.
func _body_box(actor_id: StringName) -> AABB:
	var f := _ctl.stage.stand_in(actor_id)
	if f == null or not f.has_actor():
		return AABB()
	var inv := _parent_inverse()
	var out := AABB()
	var first := true
	for n in f.actor().find_children("*", "MeshInstance3D", true, false):
		var mi := n as MeshInstance3D
		if mi.mesh != null and mi.is_visible_in_tree():
			var b := (inv * mi.global_transform) * mi.get_aabb()
			out = b if first else out.merge(b)
			first = false
	return out


## True when `body` (non-empty) stands across a sight line from the pose's lens to a target point. A point inside the
## body's bounds says nothing (a colossus's rest bounds take in the party under its hand) and never blocks.
static func _blocked(pose: Dictionary, body: AABB, targets: Array[Vector3]) -> bool:
	if body.size == Vector3.ZERO:
		return false
	for p in targets:
		if not body.has_point(p) and body.intersects_segment(pose["pos"] as Vector3, p) != null:
			return true
	return false


## Each target's feet and head (camera parent space), the actor itself left out.
func _target_points(plan: Dictionary, actor_id: StringName) -> Array[Vector3]:
	var out: Array[Vector3] = []
	var to_local := _parent_inverse()
	for tid: StringName in plan["targets"]:
		var f := _ctl.stage.stand_in(tid)
		if tid == actor_id or f == null:
			continue
		out.append(to_local * f.global_position)
		out.append(to_local * f.head_position())
	return out


## The actor's head on its mark (camera parent space).
func _actor_head(actor_id: StringName) -> Vector3:
	var f := _ctl.stage.stand_in(actor_id)
	return _parent_inverse() * f.head_position() if f != null else Vector3.ZERO


## Fighter-local (the plan's from/to/aim) to the camera's parent space.
func _space(actor_id: StringName) -> Transform3D:
	var f := _ctl.stage.stand_in(actor_id)
	if f == null or not f.is_inside_tree() or f.get_parent() == null:
		return Transform3D.IDENTITY
	return _parent_inverse() * (f.get_parent() as Node3D).global_transform


func _parent_inverse() -> Transform3D:
	var parent := camera.get_parent() as Node3D if camera != null else null
	if parent == null or not parent.is_inside_tree():
		return Transform3D.IDENTITY
	return parent.global_transform.affine_inverse()


# --- poses ----------------------------------------------------------------------------------


func _default_pose() -> Dictionary:
	var pos := default_transform.origin
	var look := pos - default_transform.basis.z.normalized() * float(data.get("default_look_m", 1.0))
	return {"pos": pos, "look": look, "fov": rest_fov()}


static func _mix(a: Dictionary, b: Dictionary, w: float) -> Dictionary:
	return {
		"pos": (a["pos"] as Vector3).lerp(b["pos"] as Vector3, w),
		"look": (a["look"] as Vector3).lerp(b["look"] as Vector3, w),
		"fov": lerpf(float(a["fov"]), float(b["fov"]), w),
	}


## 0 before `a`, 1 from `b` on, eased between (a cut when a == b).
static func _weight(t: float, a: float, b: float) -> float:
	if t >= b:
		return 1.0
	if t <= a:
		return 0.0
	return BattleChoreo._ease((t - a) / (b - a))
