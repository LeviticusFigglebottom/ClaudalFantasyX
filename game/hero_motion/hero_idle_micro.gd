class_name HeroIdleMicro
extends SkeletonModifier3D
## Idle micro-motion for a hero body (M2-HER-1104, ADR 0190): breathing (the chest lifts, the shoulders rise)
## and a slow weight shift (the hips roll and yaw, the legs and spine counter them), layered after
## whatever clip or pose the skeleton shows, plus a head lead: while the body turns, the neck and head
## turn ahead of it. Add it with HeroMotion.add_micro_motion(actor). Tuning:
## game/data/hero_motion/idle_micro.json.
##
## Deterministic: the clock starts at 0 and only advances by the frames' delta, and each actor's breath
## and sway phases and periods come from a hash of its id (no randomness). `amount` (0..1) scales the
## breathing and the sway and eases toward its target over amount_fade_sec; walking sets it to 0. A rig
## without the listed bones gets nothing for them: a missing bone is skipped, never an error.

const DATA_PATH := "res://game/data/hero_motion/idle_micro.json"
## Rotation kinds a contribution turns about (resolved to skeleton-space axes in apply()).
const PITCH := &"pitch"
const ROLL := &"roll"
const YAW := &"yaw"
const LIFT := &"lift"
## Hash salts so the breath and the sway of one actor get independent phases and periods.
const SALT_BREATH := "breath"
const SALT_SWAY := "sway"
## Buckets a hash is cut into for a phase or a period share.
const HASH_BUCKETS := 10007
## The model's facing when its rig has no foot bones to read it from (the hero glTFs face +Z).
const DEFAULT_FORWARD := Vector3(0.0, 0.0, 1.0)
const FOOT_BONES: Array[String] = ["DEF-foot.L", "DEF-foot.R"]

## The actor this body belongs to (its phases come from it). Set before it enters the tree.
var actor_id: StringName = &""
## Target strength of the breathing and the sway: 1 standing, 0 walking.
var amount := 1.0
## The eased strength actually applied (moves toward `amount` over amount_fade_sec).
var amount_now := 1.0
## Seconds since the modifier started (advance() moves it).
var clock := 0.0
## Measure the turn rate from the skeleton's yaw each frame; false: a driver sets `turn_rate`.
var use_measured_rate := true
## The body's turn speed (radians per second, + = counter-clockwise from above) the head leads by.
var turn_rate := 0.0

var data: Dictionary = {}
var _breath_phase := 0.0
var _breath_period := 0.0
var _sway_phase := 0.0
var _sway_period := 0.0
var _last_yaw := 0.0
var _has_yaw := false


func _init(id: StringName = &"", tuning: Dictionary = {}) -> void:
	data = tuning if not tuning.is_empty() else load_data()
	set_actor(id)


static func load_data() -> Dictionary:
	var f := FileAccess.open(DATA_PATH, FileAccess.READ)
	if f == null:
		push_error("HeroIdleMicro: cannot read %s" % DATA_PATH)
		return {}
	var parsed: Variant = JSON.parse_string(f.get_as_text())
	return parsed if parsed is Dictionary else {}


## Seeds the phases and periods from `id` (the same id always breathes the same way).
func set_actor(id: StringName) -> void:
	actor_id = id
	var b := data.get("breath", {}) as Dictionary
	var s := data.get("sway", {}) as Dictionary
	_breath_phase = TAU * share(id, SALT_BREATH)
	_sway_phase = TAU * share(id, SALT_SWAY)
	_breath_period = _period(b, share(id, SALT_BREATH + SALT_SWAY))
	_sway_period = _period(s, share(id, SALT_SWAY + SALT_BREATH))


## A deterministic share in [0, 1) for an id and a salt (String.hash is stable across runs).
static func share(id: StringName, salt: String) -> float:
	return float(posmod(("%s/%s" % [id, salt]).hash(), HASH_BUCKETS)) / float(HASH_BUCKETS)


func _period(section: Dictionary, u: float) -> float:
	var base := float(section.get("period_sec", 0.0))
	var spread := float(section.get("period_spread", 0.0))
	return base * (1.0 + spread * (2.0 * u - 1.0))


func breath_period() -> float:
	return _breath_period


func sway_period() -> float:
	return _sway_period


## Moves the clock, eases the amount, and (when measuring) reads the turn rate from `body_yaw`.
func advance(delta: float, body_yaw: float = 0.0) -> void:
	if delta <= 0.0:
		return
	clock += delta
	var fade := float(data.get("amount_fade_sec", 0.0))
	amount_now = amount if fade <= 0.0 else move_toward(amount_now, amount, delta / fade)
	if not use_measured_rate:
		return
	if not _has_yaw:
		_has_yaw = true
		_last_yaw = body_yaw
		return
	var raw := angle_difference(_last_yaw, body_yaw) / delta
	_last_yaw = body_yaw
	var lead := data.get("head_lead", {}) as Dictionary
	var smooth := float(lead.get("rate_smoothing_sec", 0.0))
	turn_rate = raw if smooth <= 0.0 else lerpf(turn_rate, raw, 1.0 - exp(-delta / smooth))


## Breath in [0, 1] (0 exhaled, 1 inhaled) at the current clock.
func breath() -> float:
	if _breath_period <= 0.0:
		return 0.0
	return 0.5 - 0.5 * cos(TAU * clock / _breath_period + _breath_phase)


## Weight shift in [-1, 1] at the current clock (+ = onto the body's left foot).
func sway() -> float:
	if _sway_period <= 0.0:
		return 0.0
	return sin(TAU * clock / _sway_period + _sway_phase)


## The head lead (radians) for the current turn rate: ahead of the turn, capped.
func head_lead() -> float:
	var lead := data.get("head_lead", {}) as Dictionary
	var cap := deg_to_rad(float(lead.get("max_deg", 0.0)))
	return clampf(turn_rate * float(lead.get("lead_sec", 0.0)), -cap, cap)


## Every rotation this frame: [{"bone": String, "kind": pitch|roll|yaw|lift, "angle": radians}], in the
## data's order. Pure (no skeleton), so tests read it directly.
func contributions() -> Array[Dictionary]:
	var out: Array[Dictionary] = []
	var b := data.get("breath", {}) as Dictionary
	var s := data.get("sway", {}) as Dictionary
	var h := data.get("head_lead", {}) as Dictionary
	var inhale := breath() * amount_now
	var chest := deg_to_rad(float(b.get("chest_pitch_deg", 0.0))) * inhale
	_shares(out, b.get("chest_bones", {}), PITCH, chest)
	_shares(out, b.get("head_bones", {}), PITCH, -chest * float(b.get("head_counter", 0.0)))
	var lift := deg_to_rad(float(b.get("shoulder_lift_deg", 0.0))) * inhale
	for bone: Variant in b.get("shoulder_bones", []):
		out.append({"bone": String(bone), "kind": LIFT, "angle": lift})
	var w := sway() * amount_now
	var roll := deg_to_rad(float(s.get("hips_roll_deg", 0.0))) * w
	var yaw := deg_to_rad(float(s.get("hips_yaw_deg", 0.0))) * w
	var hips := String(s.get("hips_bone", ""))
	if hips != "":
		out.append({"bone": hips, "kind": ROLL, "angle": roll})
		out.append({"bone": hips, "kind": YAW, "angle": yaw})
	for bone: Variant in s.get("leg_bones", []):
		out.append({"bone": String(bone), "kind": YAW, "angle": -yaw})
		out.append({"bone": String(bone), "kind": ROLL, "angle": -roll})
	_shares(out, s.get("spine_counter", {}), ROLL, roll)
	_shares(out, h.get("bones", {}), YAW, head_lead())
	return out


func _shares(out: Array[Dictionary], table: Variant, kind: StringName, total: float) -> void:
	if not table is Dictionary:
		return
	for bone: Variant in table:
		out.append({"bone": String(bone), "kind": kind, "angle": total * float(table[bone])})


## Applies this frame's contributions to `skel`'s current pose, parents first. Returns how many bones
## it turned (0 on a rig with none of the listed bones).
func apply(skel: Skeleton3D) -> int:
	if skel == null:
		return 0
	var up := Vector3.UP
	var fwd := forward_of(skel)
	var by_bone: Dictionary = {}
	for c: Dictionary in contributions():
		var idx := skel.find_bone(String(c["bone"]))
		var angle := float(c["angle"])
		if idx < 0 or is_zero_approx(angle):
			continue
		var axis := _axis(skel, idx, StringName(c["kind"]), up, fwd)
		if axis == Vector3.ZERO:
			continue
		var q: Quaternion = by_bone.get(idx, Quaternion.IDENTITY)
		by_bone[idx] = Quaternion(axis, angle) * q
	var bones: Array = by_bone.keys()
	bones.sort()
	for idx: int in bones:
		var parent := skel.get_bone_parent(idx)
		var p := Quaternion.IDENTITY
		if parent >= 0:
			p = skel.get_bone_global_pose(parent).basis.get_rotation_quaternion()
		var local := skel.get_bone_pose_rotation(idx)
		skel.set_bone_pose_rotation(idx, (p.inverse() * (by_bone[idx] as Quaternion) * p * local).normalized())
	return bones.size()


## Skeleton-space axis for a contribution: pitch lifts the chest back, roll tilts about the facing, yaw
## turns about up, lift raises a bone's tip (a shoulder) toward up.
func _axis(skel: Skeleton3D, idx: int, kind: StringName, up: Vector3, fwd: Vector3) -> Vector3:
	match kind:
		PITCH:
			return fwd.cross(up).normalized()
		ROLL:
			return fwd
		YAW:
			return up
		LIFT:
			var dir := skel.get_bone_global_pose(idx).basis.y.normalized()
			var axis := dir.cross(up)
			return axis.normalized() if axis.length() > 0.0001 else Vector3.ZERO
	return Vector3.ZERO


## The way the model faces in skeleton space, read from its feet (they point at the toes), else +Z.
static func forward_of(skel: Skeleton3D) -> Vector3:
	var sum := Vector3.ZERO
	for bone: String in FOOT_BONES:
		var idx := skel.find_bone(bone)
		if idx >= 0:
			var y := skel.get_bone_global_rest(idx).basis.y
			sum += Vector3(y.x, 0.0, y.z)
	return sum.normalized() if sum.length() > 0.0001 else DEFAULT_FORWARD


func _process_modification_with_delta(delta: float) -> void:
	var skel := get_skeleton()
	if skel == null:
		return
	var yaw := HeroLocomotion.yaw_of(skel.global_basis * forward_of(skel))
	advance(delta, yaw)
	apply(skel)
