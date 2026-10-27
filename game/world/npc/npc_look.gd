class_name NpcLook
extends SkeletonModifier3D
## Where a villager's head looks (M3-CRE-613; docs/kb/tech/field_npc.md "Attention"). FieldNpc sets a
## target (a yaw and a pitch relative to the body, or "ahead") and advances it each tick; this modifier
## turns the neck and head bones by the eased angles after the clip and HeroIdleMicro have posed them, so
## a glance rides on top of idle, talk, work or walk. The yaw turns about up and the pitch about the
## body's side axis, both shared across `bones` (a bone missing from a rig is skipped).
##
## Easing: each angle follows its target through a critically damped spring (`smoothing_sec`), its speed
## capped at `max_rate_deg_per_sec`, so a glance starts soft, never snaps and settles without overshoot.
## Deterministic: the state only moves by advance(delta). Tuning: npc.json `look`.

## Rotation kinds (resolved to skeleton-space axes in apply()).
const YAW := &"yaw"
const PITCH := &"pitch"

var data: Dictionary = {}
## Target angles (radians): + yaw turns the head to the body's left (counter-clockwise from above), + pitch
## lifts the chin.
var target_yaw := 0.0
var target_pitch := 0.0
## The eased angles applied this frame (radians) and their speeds (radians per second).
var yaw := 0.0
var pitch := 0.0
var _yaw_speed := 0.0
var _pitch_speed := 0.0


func _init(tuning: Dictionary = {}) -> void:
	data = tuning


func _num(key: String) -> float:
	return float(data.get(key, 0.0))


## Aims at a yaw and pitch relative to the body (radians), clamped to the data's limits.
func look(rel_yaw: float, rel_pitch: float) -> void:
	var y_cap := deg_to_rad(_num("max_yaw_deg"))
	target_yaw = clampf(wrapf(rel_yaw, -PI, PI), -y_cap, y_cap)
	target_pitch = clampf(rel_pitch, -deg_to_rad(_num("max_pitch_down_deg")), deg_to_rad(_num("max_pitch_up_deg")))


## Back to straight ahead.
func look_ahead() -> void:
	look(0.0, 0.0)


## True when `rel_yaw` (radians, relative to the body) is inside the head's reach.
func can_reach(rel_yaw: float) -> bool:
	return absf(wrapf(rel_yaw, -PI, PI)) <= deg_to_rad(_num("max_yaw_deg"))


## Eases the angles toward the targets over `delta` seconds.
func advance(delta: float) -> void:
	if delta <= 0.0:
		return
	var r := _spring(yaw, _yaw_speed, target_yaw, delta)
	yaw = r.x
	_yaw_speed = r.y
	r = _spring(pitch, _pitch_speed, target_pitch, delta)
	pitch = r.x
	_pitch_speed = r.y


## One step of a critically damped spring toward `goal` (semi-implicit Euler, sub-stepped so a long
## frame stays stable), its speed capped. Returns (value, speed).
func _spring(value: float, speed: float, goal: float, delta: float) -> Vector2:
	var smooth := _num("smoothing_sec")
	if smooth <= 0.0:
		return Vector2(goal, 0.0)
	var omega := 2.0 / smooth
	var cap := deg_to_rad(_num("max_rate_deg_per_sec"))
	var steps := maxi(1, ceili(delta / maxf(_num("max_substep_sec"), 0.001)))
	var h := delta / float(steps)
	for i in steps:
		var accel := omega * omega * (goal - value) - 2.0 * omega * speed
		speed += accel * h
		if cap > 0.0:
			speed = clampf(speed, -cap, cap)
		value += speed * h
	return Vector2(value, speed)


## Every rotation this frame: [{"bone", "kind", "angle"}]. Pure (no skeleton), for tests.
func contributions() -> Array[Dictionary]:
	var out: Array[Dictionary] = []
	var bones := data.get("bones", {}) as Dictionary
	for bone: Variant in bones:
		var share := float(bones[bone])
		out.append({"bone": String(bone), "kind": YAW, "angle": yaw * share})
		out.append({"bone": String(bone), "kind": PITCH, "angle": pitch * share})
	return out


## Turns the bones of `skel`'s current pose, parents first. Returns how many bones it turned.
func apply(skel: Skeleton3D) -> int:
	if skel == null:
		return 0
	var fwd := HeroIdleMicro.forward_of(skel)
	var side := fwd.cross(Vector3.UP).normalized()
	var by_bone: Dictionary = {}
	for c: Dictionary in contributions():
		var idx := skel.find_bone(String(c["bone"]))
		var angle := float(c["angle"])
		if idx < 0 or is_zero_approx(angle):
			continue
		# + pitch lifts the chin: about forward x up (HeroIdleMicro's pitch axis) a positive turn tips forward up.
		var axis := Vector3.UP if StringName(c["kind"]) == YAW else side
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


func _process_modification_with_delta(_delta: float) -> void:
	apply(get_skeleton())
