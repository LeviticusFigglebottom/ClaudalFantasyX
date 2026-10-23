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
## Scripted shots (M1-ARC-05): play_shot() takes the camera for a cutscene and suspends volume
## selection until release(), which blends back to the winning volume's shot. This is the hook the
## cutscene sequencer drives from `@camera` cues (contract in docs/kb/tech/field_camera.md).
## M1-ARC-08: while a scripted shot is held, the director also holds the chapter autosave
## (SaveSystem.hold_autosave), so a chapter change made mid-cutscene is saved after release().
##
## Time passes only through update(delta) (called from _process when auto_update is on), so tests
## and capture scenes drive it deterministically.

signal shot_changed(shot: CameraShot, hard_cut: bool, blend_sec: float)
## The camera has settled on `shot` (M1-ARC-07: the sequencer contract). Fires once per transition
## that lands, always as the last thing update() does, after that frame's pose is on the camera:
## when a blend completes, in the update() that first applies a cut, and in the next update() after
## a play_shot()/release() that did not move the camera. A move issued from a blend_finished
## handler (a sequencer resuming from its await) therefore lands on a later update(), never the
## one that is emitting. Never synchronously inside play_shot()/release()/a volume change, so
## `play_shot(...)` then `await blend_finished` cannot miss it. snap() is the exception: it settles
## at once and emits (for a blend it cut short, or the cut it made) before it returns. A transition
## superseded before it lands does not fire; the one that replaced it does. Leaving the tree with a
## move still owed emits it too (see _exit_tree), so an awaiting sequencer never hangs on a zone
## unload; it should check is_inside_tree() when it resumes.
signal blend_finished(shot: CameraShot)
## A scripted shot took the camera (play_shot). blend_sec is 0 for a cut.
signal scripted_shot_started(shot: CameraShot, blend_sec: float)
## release() handed the camera back; `shot` is the shot it returns to. blend_sec is 0 for a cut.
signal scripted_shot_released(shot: CameraShot, blend_sec: float)
## snap() finished: the camera is settled on `shot` with no blend.
signal snapped(shot: CameraShot)

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
var _blend_ease: StringName = &""
## The shot play_shot() holds; null while volumes select the shot.
var _scripted_shot: CameraShot
## What was active when the script took over (release() falls back to it outside every volume).
var _return_shot: CameraShot
var _return_volume: CameraVolume
var _aim_warned: Dictionary = {}
## A cut or a no-move scripted transition landed; the next update() emits blend_finished.
var _settle_pending := false


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


## Jumps straight to the shot for the target's current position (zone load, teleport, capture):
## a hard cut that also ends any blend in progress (even into the shot already active) and resets
## tracking, then emits `snapped`. While a scripted shot is held, it snaps onto that shot instead.
func snap() -> void:
	if volumes.is_empty():
		collect_volumes()
	_inside.clear()
	if target != null:
		_update_occupancy()
	if _scripted_shot == null:
		var best := _pick_volume()
		if best != null:
			_enter(best, true)
		elif active_shot == null and initial_shot != null:
			_activate(initial_shot, null, true, 0.0)
	var was_blending := _blending
	_end_blend()
	if active_shot != null:
		_shot_state.erase(active_shot)
	update(0.0)
	if was_blending:
		blend_finished.emit(active_shot)
	if active_shot != null:
		snapped.emit(active_shot)


# --- Scripted shots (cutscene sequencer) ---------------------------------------------------------


## Takes the camera to `shot` until release(): volume selection is suspended while it is held.
## blend_sec < 0 resolves like a volume entry (the shot's blend_sec, then default_blend_sec) and
## honours the shot's hard_cut; an explicit blend_sec wins over both, and 0 cuts. `ease` names an
## ease from field_camera.json for this blend only (empty = the shot's own curve or ease). Calling
## it again while held moves on to the next scripted shot, blending from wherever the camera is.
## Playing the shot already active is a no-move (a cut onto it ends any blend into it); either way
## blend_finished follows on the next update(), so a sequencer can always await it.
func play_shot(shot: CameraShot, blend_sec: float = CameraShot.USE_DEFAULT, ease: StringName = &"") -> void:
	if shot == null:
		push_error("FieldCameraDirector: play_shot(null)")
		return
	var dur := blend_sec
	var cut := false
	if dur < 0.0:
		dur = shot.blend_sec if shot.blend_sec >= 0.0 else float(data.get("default_blend_sec", 0.0))
		cut = shot.hard_cut
	cut = cut or dur <= 0.0 or active_shot == null
	if _scripted_shot == null:
		_return_shot = active_shot
		_return_volume = active_volume
		_hold_autosave(true)
	_scripted_shot = shot
	var moves := shot != active_shot
	if moves:
		_activate(shot, null, cut, dur, ease)
	else:
		_settle_in_place(cut)
		active_volume = null
	scripted_shot_started.emit(shot, dur if moves and not cut else 0.0)


## Hands the camera back to the volumes: blends to the winning volume's shot (or, outside every
## volume, to the shot that was active before play_shot). blend_sec < 0 resolves like a volume
## entry (volume override, shot, default) and blends even onto a shot whose own hard_cut is set;
## pass 0 to cut. The returning volume's force_hard_cut always wins (it marks a set where a blend
## would sweep through geometry or flip the screen axis), even over an explicit blend_sec.
## blend_finished follows like any other transition. Returns false, and does nothing, when no
## scripted shot is held.
func release(blend_sec: float = CameraShot.USE_DEFAULT, ease: StringName = &"") -> bool:
	if _scripted_shot == null:
		return false
	var held := _scripted_shot
	_scripted_shot = null
	_hold_autosave(false)
	if target != null:
		_update_occupancy()
	var best := _pick_volume()
	var shot: CameraShot = best.shot if best != null else _return_shot
	var v: CameraVolume = best if best != null else _return_volume
	_return_shot = null
	_return_volume = null
	if shot == null:
		shot = held
	var dur := blend_sec
	if dur < 0.0 and best != null:
		dur = best.blend_sec_override
	if dur < 0.0:
		dur = shot.blend_sec
	if dur < 0.0:
		dur = float(data.get("default_blend_sec", 0.0))
	var cut := dur <= 0.0 or (v != null and v.force_hard_cut)
	var moves := shot != active_shot
	if moves:
		_activate(shot, v, cut, dur, ease)
	else:
		_settle_in_place(cut)
		active_volume = v
	scripted_shot_released.emit(shot, dur if moves and not cut else 0.0)
	return true


## True when no blend is running and no blend_finished is still owed: the camera is on its shot.
## A sequencer that may already be settled checks this before awaiting blend_finished.
func is_settled() -> bool:
	return not _blending and not _settle_pending


## True while play_shot() holds the camera.
func is_scripted() -> bool:
	return _scripted_shot != null


func scripted_shot() -> CameraShot:
	return _scripted_shot


## M1-ARC-08: a held scripted shot is a cutscene in progress, so the autosave waits for it. Without
## the SaveSystem autoload (a bare script test) this does nothing. A freed director never blocks:
## SaveSystem keeps holders by WeakRef. Leaving the tree releases the hold (the zone is unloading).
func _hold_autosave(on: bool) -> void:
	var tree := Engine.get_main_loop() as SceneTree
	var saves: Node = tree.root.get_node_or_null(^"SaveSystem") if tree != null else null
	if saves != null:
		saves.call(&"hold_autosave" if on else &"release_autosave", self)


## Leaving the tree (zone unload, the director freed mid-cutscene) ends any move in progress and
## pays an owed blend_finished, so a coroutine awaiting it resumes instead of hanging forever.
func _exit_tree() -> void:
	_hold_autosave(false)
	if is_settled() or active_shot == null:
		return
	_end_blend()
	_settle_pending = false
	blend_finished.emit(active_shot)


## Advances selection, blends and tracking by `delta` seconds and applies the pose to the camera.
## Without a target (a cutscene staged without the player, M1-ARC-09) volumes are not consulted,
## but the active shot is still evaluated, blended and applied, and blend_finished still fires.
## Nothing else advances time: while the tree is paused, or with auto_update off, whoever owns the
## director must call update() or an awaited blend_finished never comes.
func update(delta: float) -> void:
	if target != null:
		_update_occupancy()
	if _scripted_shot == null:
		var best := _pick_volume()
		if best != null and best != active_volume:
			_enter(best, false)
	if active_shot == null:
		return
	var to_pose := evaluate(active_shot, delta)
	var landed := false
	if _blending:
		_blend_elapsed += delta
		var t := clampf(_blend_elapsed / _blend_duration, 0.0, 1.0) if _blend_duration > 0.0 else 1.0
		_blend_weight = blend_curve_weight(active_shot, t, _blend_ease)
		var from_pose := evaluate(_previous_shot, delta) if _previous_shot != null else _from_snapshot
		current_pose = CameraPose.blend(from_pose, to_pose, _blend_weight)
		if t >= 1.0:
			_blending = false
			_blend_weight = 1.0
			_previous_shot = null
			landed = true
	else:
		current_pose = to_pose
	if camera != null:
		current_pose.apply_to(camera)
	# Snapshot, clear, then emit last: a play_shot()/release() made by a handler sets its own flags,
	# which wait for the next update() (M1-ARC-07 review-sweep-D S1).
	landed = landed or _settle_pending
	_settle_pending = false
	if landed:
		blend_finished.emit(active_shot)


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
		"scripted": _scripted_shot != null,
		"aim": String(active_shot.aim_node) if active_shot != null else "",
	}


# --- Shot evaluation -----------------------------------------------------------------------------


## Where `shot` wants the camera this frame. Tracking state (smoothed aim, dolly progress) is kept
## per shot, so an outgoing shot keeps tracking while it blends out. A shot with an aim_node frames
## that node (plus aim_offset) instead of the player in every mode; FIXED then looks at it.
func evaluate(shot: CameraShot, delta: float) -> CameraPose:
	var fov := shot.fov_deg if shot.fov_deg > 0.0 else float(data.get("default_fov_deg", 0.0))
	var subject := subject_node(shot)
	var aim_target := aim_point(shot)
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
			var centre := subject.global_position if subject != null else _to_world(shot.look_at)
			return CameraPose.looking(centre + offset, aim_target, fov, shot.dof_dict(), shot.roll_deg)
	var fixed_aim := aim_target if subject != target else _to_world(shot.look_at)
	return CameraPose.looking(_to_world(shot.position), fixed_aim, fov, shot.dof_dict(), shot.roll_deg)


## The node `shot` frames: its aim_node (relative to the rail root, or absolute) when set and
## found, else the player. A missing aim_node warns once per shot and falls back to the player.
func subject_node(shot: CameraShot) -> Node3D:
	if shot.aim_node.is_empty():
		return target
	var base: Node = rail_root if rail_root != null else self
	var n := base.get_node_or_null(shot.aim_node) as Node3D
	if n == null:
		if not _aim_warned.has(shot):
			_aim_warned[shot] = true
			push_warning(
				"FieldCameraDirector: shot %s aim_node %s not found; using the player" % [shot.id, shot.aim_node]
			)
		return target
	return n


## The world point `shot` aims at: its aim node plus aim_offset, or the player plus target_offset.
## With neither (no player in the scene), the shot's authored look_at.
func aim_point(shot: CameraShot) -> Vector3:
	var subject := subject_node(shot)
	if subject == null:
		return _to_world(shot.look_at)
	if subject != target:
		return subject.global_position + shot.aim_offset
	return target.global_position + shot.target_offset


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
	if subject_node(shot) == null:
		return clampf(shot.progress_offset, 0.0, 1.0)
	var local := track.to_local(subject_node(shot).global_position)
	var progress := track.curve.get_closest_offset(local) / track.curve.get_baked_length()
	return clampf(shot.progress_offset + progress * shot.progress_scale, 0.0, 1.0)


func dolly_position(shot: CameraShot, t: float) -> Vector3:
	var dolly := _path(shot.dolly_path)
	if dolly == null or dolly.curve == null:
		push_warning("FieldCameraDirector: shot %s has no dolly path" % shot.id)
		return _to_world(shot.position)
	return dolly.to_global(dolly.curve.sample_baked(t * dolly.curve.get_baked_length()))


## Curve weight for normalized blend time t: `ease_override` (a play_shot/release ease), else the
## shot's Curve, else its named ease, else default.
func blend_curve_weight(shot: CameraShot, t: float, ease_override: StringName = &"") -> float:
	if ease_override == &"" and shot != null and shot.blend_curve != null:
		return clampf(shot.blend_curve.sample_baked(t), 0.0, 1.0)
	var ease_name := String(ease_override)
	if ease_name == "" and shot != null and shot.blend_ease != &"":
		ease_name = String(shot.blend_ease)
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


func _activate(shot: CameraShot, v: CameraVolume, cut: bool, dur: float, ease: StringName = &"") -> void:
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
	_blend_ease = ease
	_settle_pending = cut
	if cut:
		_previous_shot = null
	history.append(shot.id)
	shot_changed.emit(shot, cut, _blend_duration)


# --- Helpers -------------------------------------------------------------------------------------


## A scripted transition onto the shot already active: a cut ends any blend into it; then, unless a
## blend is still running (it will emit when it lands), blend_finished is owed on the next update().
func _settle_in_place(cut: bool) -> void:
	if cut and _blending:
		_end_blend()
	if not _blending:
		_settle_pending = true


func _end_blend() -> void:
	_blending = false
	_previous_shot = null
	_from_snapshot = null
	_blend_elapsed = 0.0
	_blend_duration = 0.0
	_blend_weight = 1.0


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
