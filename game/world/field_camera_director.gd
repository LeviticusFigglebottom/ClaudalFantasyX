class_name FieldCameraDirector
extends Node3D
## Directed field camera (SPEC §6.6, M1-ARC-01; docs/kb/tech/field_camera.md).
##
## Each update it finds the CameraVolumes containing the target (FieldShapes, no physics wait),
## picks the winner (highest priority, then most recently entered) and, when that changes,
## transitions to the winner's CameraShot: a hard cut, or a blend whose duration and curve come
## from the volume, the shot or field_camera.json. A blend runs from the live outgoing shot (or
## from a snapshot, when a new change interrupts a blend) to the live incoming shot, so tracking
## shots keep moving while they blend. Leaving every volume keeps the current shot.
## There is no free orbit camera: CameraShot.Mode.ORBIT is honoured only with hub_orbit_enabled.
##
## Time passes only through update(delta) (called from _process when auto_update is on), so tests
## and capture scenes drive it deterministically.

signal shot_changed(shot: CameraShot, hard_cut: bool, blend_sec: float)
signal blend_finished(shot: CameraShot)

const DATA_PATH := "res://game/data/world/field_camera.json"
const TWEEN_CLASS := "Tween"

@export var camera_path: NodePath
@export var target_path: NodePath
## Shot positions and paths are relative to this node. Empty = the scene owner (level root).
@export var rail_root_path: NodePath
## Hub zones only (SPEC §6.6): allow CameraShot.Mode.ORBIT shots, steered by field_camera_* actions.
@export var hub_orbit_enabled := false
## Used when the target starts outside every volume.
@export var initial_shot: CameraShot
@export var auto_update := true

var camera: Camera3D
var target: Node3D
var rail_root: Node3D
var data: Dictionary = {}
var volumes: Array[CameraVolume] = []
var active_volume: CameraVolume
var active_shot: CameraShot
## Shot ids in the order they became active (debug overlay, tests).
var history: Array[StringName] = []
var current_pose: CameraPose
var orbit_yaw := 0.0

var _previous_shot: CameraShot
var _from_snapshot: CameraPose
var _blending := false
var _blend_elapsed := 0.0
var _blend_duration := 0.0
var _blend_weight := 1.0
var _inside: Dictionary = {}
var _seq := 0
var _shot_state: Dictionary = {}
var _orbit_warned := false


func _ready() -> void:
	data = FieldInput.load_json(DATA_PATH)
	camera = get_node_or_null(camera_path) as Camera3D
	target = get_node_or_null(target_path) as Node3D
	var root_node: Node = get_node_or_null(rail_root_path) if not rail_root_path.is_empty() else owner
	if root_node == null:
		root_node = get_parent()
	rail_root = root_node as Node3D if root_node is Node3D else self
	if camera == null:
		push_error("FieldCameraDirector: camera_path does not point at a Camera3D")
	collect_volumes.call_deferred()
	snap.call_deferred()


func _process(delta: float) -> void:
	if not auto_update:
		return
	if hub_orbit_enabled:
		var axis := Input.get_axis(FieldInput.CAMERA_LEFT, FieldInput.CAMERA_RIGHT)
		orbit_yaw -= axis * deg_to_rad(_orbit_value("yaw_speed_deg_per_sec")) * delta
	update(delta)


## Finds every CameraVolume under the rail root (or registers the given ones).
func collect_volumes(explicit: Array[CameraVolume] = []) -> void:
	volumes.clear()
	if not explicit.is_empty():
		volumes.append_array(explicit)
		return
	var base: Node = rail_root if rail_root != null else self
	for n in base.find_children("*", "CameraVolume", true, false):
		volumes.append(n as CameraVolume)


## Jumps straight to the shot for the target's current position (zone load, teleport, capture).
func snap() -> void:
	if volumes.is_empty():
		collect_volumes()
	_inside.clear()
	_update_occupancy()
	var best := _pick_volume()
	if best != null:
		_enter(best, true)
	elif active_shot == null and initial_shot != null:
		_activate(initial_shot, null, true, 0.0)
	update(0.0)


## Advances selection, blends and tracking by `delta` seconds and applies the pose to the camera.
func update(delta: float) -> void:
	if target == null:
		return
	_update_occupancy()
	var best := _pick_volume()
	if best != null and best != active_volume:
		_enter(best, false)
	if active_shot == null:
		return
	var to_pose := evaluate(active_shot, delta)
	if _blending:
		_blend_elapsed += delta
		var t := clampf(_blend_elapsed / _blend_duration, 0.0, 1.0) if _blend_duration > 0.0 else 1.0
		_blend_weight = blend_curve_weight(active_shot, t)
		var from_pose := evaluate(_previous_shot, delta) if _previous_shot != null else _from_snapshot
		current_pose = CameraPose.blend(from_pose, to_pose, _blend_weight)
		if t >= 1.0:
			_blending = false
			_blend_weight = 1.0
			_previous_shot = null
			blend_finished.emit(active_shot)
	else:
		current_pose = to_pose
	if camera != null:
		current_pose.apply_to(camera)


func is_blending() -> bool:
	return _blending


## 0 at the start of a blend, 1 when settled (curve-shaped, not linear time).
func blend_weight() -> float:
	return _blend_weight


func blend_duration() -> float:
	return _blend_duration


## Yaw of the live camera around +Y (FieldMotor's reference for camera-relative input).
func camera_yaw() -> float:
	if current_pose == null:
		return FieldMotor.yaw_of_basis(camera.global_basis) if camera != null else 0.0
	return FieldMotor.yaw_of_basis(Basis(current_pose.rotation))


func active_shot_id() -> StringName:
	return active_shot.id if active_shot != null else &""


## Debug overlay / tests: everything the director is doing right now.
func state_snapshot() -> Dictionary:
	return {
		"shot": active_shot_id(),
		"volume": String(active_volume.name) if active_volume != null else "",
		"blending": _blending,
		"blend_weight": _blend_weight,
		"blend_sec": _blend_duration,
		"inside": _inside.size(),
		"history": history.duplicate(),
	}


# --- Shot evaluation -----------------------------------------------------------------------------


## Where `shot` wants the camera this frame. Tracking state (smoothed aim, dolly progress) is kept
## per shot, so an outgoing shot keeps tracking while it blends out.
func evaluate(shot: CameraShot, delta: float) -> CameraPose:
	var fov := shot.fov_deg if shot.fov_deg > 0.0 else float(data.get("default_fov_deg", 0.0))
	var aim_target := target.global_position + shot.target_offset
	match _effective_mode(shot):
		CameraShot.Mode.PAN_FOLLOW:
			var from := _to_world(shot.position)
			var desired := pan_aim(from, _to_world(shot.look_at), aim_target, shot.follow_weight, shot.max_pan_deg)
			var rate := _rate(shot.follow_smoothing, "pan_follow_smoothing_per_sec")
			var aim := _smoothed(shot, "aim", desired, rate, delta) as Vector3
			return CameraPose.looking(from, aim, fov, shot.dof_dict(), shot.roll_deg)
		CameraShot.Mode.DOLLY:
			var desired_t := dolly_progress(shot)
			var rate := _rate(shot.follow_smoothing, "dolly_follow_smoothing_per_sec")
			var dolly_t := float(_smoothed(shot, "dolly_t", desired_t, rate, delta))
			return CameraPose.looking(dolly_position(shot, dolly_t), aim_target, fov, shot.dof_dict(), shot.roll_deg)
		CameraShot.Mode.ORBIT:
			var dist := shot.orbit_distance if shot.orbit_distance > 0.0 else _orbit_value("distance_m")
			var height := shot.orbit_height if shot.orbit_height > 0.0 else _orbit_value("height_m")
			var offset := Basis(Vector3.UP, orbit_yaw) * Vector3(0.0, height, dist)
			return CameraPose.looking(target.global_position + offset, aim_target, fov, shot.dof_dict(), shot.roll_deg)
	return CameraPose.looking(_to_world(shot.position), _to_world(shot.look_at), fov, shot.dof_dict(), shot.roll_deg)


## Pan-follow aim: authored aim moved toward the player by `weight`, at most `max_deg` away.
static func pan_aim(from: Vector3, authored: Vector3, player: Vector3, weight: float, max_deg: float) -> Vector3:
	var desired := authored.lerp(player, weight)
	var base_dir := authored - from
	var want_dir := desired - from
	var angle := base_dir.angle_to(want_dir)
	var max_rad := deg_to_rad(max_deg)
	if angle <= max_rad or angle == 0.0:
		return desired
	var limited := base_dir.slerp(want_dir, max_rad / angle)
	return from + limited.normalized() * want_dir.length()


## The target's projected progress along the shot's track (0..1), mapped to dolly progress.
func dolly_progress(shot: CameraShot) -> float:
	var track := _path(shot.track_path if not shot.track_path.is_empty() else shot.dolly_path)
	if track == null or track.curve == null or track.curve.get_baked_length() <= 0.0:
		return 0.0
	var local := track.to_local(target.global_position)
	var progress := track.curve.get_closest_offset(local) / track.curve.get_baked_length()
	return clampf(shot.progress_offset + progress * shot.progress_scale, 0.0, 1.0)


func dolly_position(shot: CameraShot, t: float) -> Vector3:
	var dolly := _path(shot.dolly_path)
	if dolly == null or dolly.curve == null:
		push_warning("FieldCameraDirector: shot %s has no dolly path" % shot.id)
		return _to_world(shot.position)
	return dolly.to_global(dolly.curve.sample_baked(t * dolly.curve.get_baked_length()))


## Curve weight for normalized blend time t: the shot's Curve, else its named ease, else default.
func blend_curve_weight(shot: CameraShot, t: float) -> float:
	if shot != null and shot.blend_curve != null:
		return clampf(shot.blend_curve.sample_baked(t), 0.0, 1.0)
	var ease_name := String(shot.blend_ease) if shot != null and shot.blend_ease != &"" else ""
	if ease_name == "":
		ease_name = str(data.get("default_blend_ease", ""))
	var spec := (data.get("eases", {}) as Dictionary).get(ease_name, {}) as Dictionary
	if spec.is_empty():
		return t
	var trans := ClassDB.class_get_integer_constant(TWEEN_CLASS, str(spec.get("trans", ""))) as Tween.TransitionType
	var ease_type := ClassDB.class_get_integer_constant(TWEEN_CLASS, str(spec.get("ease", ""))) as Tween.EaseType
	return float(Tween.interpolate_value(0.0, 1.0, t, 1.0, trans, ease_type))


# --- Selection -----------------------------------------------------------------------------------


func _update_occupancy() -> void:
	var p := target.global_position
	var eps := float(data.get("volume_check_epsilon_m", 0.0))
	for v in volumes:
		if not is_instance_valid(v):
			continue
		var inside := v.contains_point(p, eps)
		if inside and not _inside.has(v):
			_seq += 1
			_inside[v] = _seq
		elif not inside and _inside.has(v):
			_inside.erase(v)


func _pick_volume() -> CameraVolume:
	var best: CameraVolume = null
	for v: CameraVolume in _inside:
		if v.shot == null:
			continue
		if best == null or v.shot_priority > best.shot_priority:
			best = v
		elif v.shot_priority == best.shot_priority and int(_inside[v]) > int(_inside[best]):
			best = v
	return best


func _enter(v: CameraVolume, force_cut: bool) -> void:
	var dur := v.blend_sec_override
	if dur < 0.0:
		dur = v.shot.blend_sec
	if dur < 0.0:
		dur = float(data.get("default_blend_sec", 0.0))
	var cut := force_cut or v.force_hard_cut or v.shot.hard_cut or dur <= 0.0 or active_shot == null
	_activate(v.shot, v, cut, dur)


func _activate(shot: CameraShot, v: CameraVolume, cut: bool, dur: float) -> void:
	if shot == active_shot:
		active_volume = v
		return
	if not cut and active_shot != null:
		if _blending and current_pose != null:
			_from_snapshot = current_pose.copy()
			_previous_shot = null
		else:
			_previous_shot = active_shot
	_shot_state.erase(shot)
	active_shot = shot
	active_volume = v
	_blending = not cut
	_blend_elapsed = 0.0
	_blend_duration = 0.0 if cut else dur
	_blend_weight = 1.0 if cut else 0.0
	if cut:
		_previous_shot = null
	history.append(shot.id)
	shot_changed.emit(shot, cut, _blend_duration)


# --- Helpers -------------------------------------------------------------------------------------


func _effective_mode(shot: CameraShot) -> CameraShot.Mode:
	if shot.mode == CameraShot.Mode.ORBIT and not hub_orbit_enabled:
		if not _orbit_warned:
			push_warning("FieldCameraDirector: shot %s is ORBIT but this is not a hub zone; using pan-follow" % shot.id)
			_orbit_warned = true
		return CameraShot.Mode.PAN_FOLLOW
	return shot.mode


## Exponential smoothing of a per-shot value; snaps on the first sample after activation.
func _smoothed(shot: CameraShot, key: String, desired: Variant, rate: float, delta: float) -> Variant:
	var st := _shot_state.get(shot, {}) as Dictionary
	if not st.has(key) or rate <= 0.0:
		st[key] = desired
	else:
		var k := 1.0 - exp(-rate * delta)
		var prev: Variant = st[key]
		st[key] = (
			(prev as Vector3).lerp(desired as Vector3, k)
			if desired is Vector3
			else lerpf(float(prev), float(desired), k)
		)
	_shot_state[shot] = st
	return st[key]


func _rate(shot_value: float, data_key: String) -> float:
	return shot_value if shot_value >= 0.0 else float(data.get(data_key, 0.0))


func _orbit_value(key: String) -> float:
	return float((data.get("orbit", {}) as Dictionary).get(key, 0.0))


func _to_world(p: Vector3) -> Vector3:
	return rail_root.global_transform * p if rail_root != null else p


func _path(path: NodePath) -> Path3D:
	if path.is_empty() or rail_root == null:
		return null
	return rail_root.get_node_or_null(path) as Path3D
