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
## The hold follows the shot across a reparent: leaving the tree drops it, re-entering with the
## shot still held takes it again (M1-ARC-07 review-sweep-E S2).
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
## unload. A coroutine resuming from that emit still sees is_inside_tree() == true (Godot runs it
## inside _exit_tree), so it must check is_leaving() when it resumes and stop driving the camera.
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
## True from _exit_tree until the director enters a tree again (M1-ARC-07 review-sweep-E S1).
var _leaving := false
## Occlusion pull-in (field_camera.json "occlusion"): how far from the leader's chest (m) the pulled-in camera is kept
## (INF: not pulled in; kept as a distance from him, not a pull from the shot's place, so a line that shortens under a
## blend never leaves the camera on him: the PC's row 66), the zone's occluder meshes (collect_occluders) and each mesh
## resource's TriangleMesh.
var _kept_m := INF
var _occluders: Array[MeshInstance3D] = []
var _occluders_read := false
var _tri_cache: Dictionary = {}


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
		elif initial_shot != null and (active_shot == null or active_volume != null):
			_activate(initial_shot, null, true, 0.0)  # outside every volume: the hub shot (M3-CIN-1251)
	var was_blending := _blending
	_kept_m = INF  # a cut starts from the shot's own place: pulled in again at once if a wall is there
	collect_occluders()  # a zone load or a teleport: the zone's walls as they stand now
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
		# Out of the tree, _enter_tree takes the hold when the director is added back.
		if is_inside_tree():
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


## True while the director is leaving the tree, or out of it: a sequencer resuming from
## `await blend_finished` checks this and stops, because the emit that woke it may be the one
## _exit_tree pays, where is_inside_tree() still reads true. Re-entering a tree clears it.
func is_leaving() -> bool:
	return _leaving or not is_inside_tree()


## True while play_shot() holds the camera.
func is_scripted() -> bool:
	return _scripted_shot != null


func scripted_shot() -> CameraShot:
	return _scripted_shot


## M1-ARC-08: a held scripted shot is a cutscene in progress, so the autosave waits for it. Without
## the SaveSystem autoload (a bare script test) this does nothing. A freed director never blocks:
## SaveSystem keeps holders by WeakRef. Leaving the tree releases the hold (the zone is unloading);
## entering one again while a scripted shot is still held takes it back (_enter_tree).
func _hold_autosave(on: bool) -> void:
	var tree := Engine.get_main_loop() as SceneTree
	var saves: Node = tree.root.get_node_or_null(^"SaveSystem") if tree != null else null
	if saves != null:
		saves.call(&"hold_autosave" if on else &"release_autosave", self)


## A director re-parented mid-cutscene (remove_child, then add_child) still holds its scripted
## shot, so it takes the autosave hold back: the hold follows the shot, not the tree.
func _enter_tree() -> void:
	_leaving = false
	if _scripted_shot != null:
		_hold_autosave(true)


## Leaving the tree (zone unload, the director freed mid-cutscene) ends any move in progress and
## pays an owed blend_finished, so a coroutine awaiting it resumes instead of hanging forever.
## _leaving is set before the emit: the resumed coroutine runs inside it, where is_inside_tree()
## is still true, and is_leaving() is how it knows to stop.
## Paying an owed emit also drops the scripted shot (M1-ARC-07 review-sweep-F F1): the sequencer
## that awaited it stops there, so nobody would release() it, and on a reparent _enter_tree would
## take the autosave hold back for good. A reparent mid-move therefore ends the cutscene; a settled
## scripted shot (nothing owed, nobody woken) is kept and its hold re-taken on re-entry.
func _exit_tree() -> void:
	_leaving = true
	_hold_autosave(false)
	if is_settled() or active_shot == null:
		return
	_end_blend()
	_settle_pending = false
	_drop_scripted_shot()
	blend_finished.emit(active_shot)


## Forgets the scripted shot without moving the camera: volume selection resumes on the next
## update() in a tree. Used only by _exit_tree when it pays an owed blend_finished.
func _drop_scripted_shot() -> void:
	_scripted_shot = null
	_return_shot = null
	_return_volume = null


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
		elif best == null and active_volume != null and initial_shot != null:
			# Walked out of every volume: back to the hub shot, not parked on the last volume (M3-CIN-1251).
			var dur := (
				initial_shot.blend_sec if initial_shot.blend_sec >= 0.0 else float(data.get("default_blend_sec", 0.0))
			)
			_activate(initial_shot, null, initial_shot.hard_cut or dur <= 0.0, dur)
	# Safe to return before the landed snapshot below: every path that sets _settle_pending or
	# starts a blend also sets active_shot, so nothing is owed here. Keep it that way.
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
	if _scripted_shot == null and subject_node(active_shot) == target:
		current_pose = clear_view(current_pose, delta)
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


# --- Occlusion -----------------------------------------------------------------------------------


## `pose`, pulled in toward the leader when a wall a player sees (view_blocker) stands between it and his chest
## (field_camera.json "occlusion"): at once to margin_m short of the wall, then eased back out at release_mps once the
## view is clear.
## Never nearer him than min_distance_m. The pose keeps its rotation (sliding along its line to him keeps him framed).
## When the clear stretch is shorter than min_view_m (the camera would end up in his face), it cranes up or round
## instead (crane()); when nothing clears, it pulls in as before while min_distance_m is clear, and keeps the shot's own
## pose when not even that is (his chest boxed in) rather than push into his face.
func clear_view(pose: CameraPose, delta: float) -> CameraPose:
	var cfg := data.get("occlusion", {}) as Dictionary
	if target == null or not bool(cfg.get("enabled", false)) or not target.is_inside_tree():
		_kept_m = INF
		return pose
	var chest := target.global_position + Vector3.UP * float(cfg.get("chest_m", 0.0))
	var line := pose.origin - chest
	var length := line.length()
	if length < 1e-3:
		return pose
	var want := INF
	var hit := view_blocker(chest, pose.origin)
	if hit.is_empty() and length < float(cfg.get("standoff_m", 0.0)):
		# the shot itself sits in his face (a spawn on a pan-follow camera's spot: Ch4 wake's DockShore, the PC's row
		# 24): backed off along its own line to standoff_m (no jump: at standoff_m it's the shot's own place), or where
		# the most room is round him when that line is blocked
		_kept_m = INF
		var off := _backed_off(pose, chest, line / length * float(cfg.get("standoff_m", 0.0)), cfg)
		return off if off != null else pose
	if not hit.is_empty():
		var free := chest.distance_to(hit["position"] as Vector3) - float(cfg.get("margin_m", 0.0))
		if free < float(cfg.get("min_view_m", 0.0)):  # pulled in this far it'd sit in his face: crane up instead
			var craned := crane(pose, chest, cfg)
			if craned == null:  # under a ceiling with walls round (a cabin: the ferry's FerryAft, rows 25/47)
				craned = widest_view(pose, chest, cfg, free)
			# not even min_distance_m clear (his chest boxed in: Coilspire's Tier4 spawn stands inside the spiral's
			# steps): the shot's own pose, not a camera pushed into his face
			if craned != null or free < float(cfg.get("min_distance_m", 0.0)):
				_kept_m = INF
				return craned if craned != null else pose
		want = maxf(free, float(cfg.get("min_distance_m", 0.0)))
	if want <= _kept_m:
		_kept_m = want
	else:
		_kept_m = minf(want, _kept_m + float(cfg.get("release_mps", 0.0)) * delta)
	if _kept_m >= length:
		_kept_m = INF
		return pose
	var out := pose.copy()
	out.origin = chest + line / length * _kept_m
	return out


## `pose` raised straight up by crane_step_m at a time, up to crane_max_m, to the first height where no wall stands
## between it and the leader's `chest` and the camera itself isn't inside a solid (crane_clear_m), looking down at
## him; when none does (a ceiling right over him), a ring of spots round him (crane_ring_m out, crane_ring_up_m over his
## chest, crane_ring_turns of them, from the shot's side first); null when nothing clears (the PC's GPU QA row 38:
## Coilspire's Tier4, where the spiral's next turn over his head put the camera inside it).
func crane(pose: CameraPose, chest: Vector3, cfg: Dictionary) -> CameraPose:
	var step := float(cfg.get("crane_step_m", 0.0))
	var top := float(cfg.get("crane_max_m", 0.0))
	if step <= 0.0:
		return null
	var space := get_world_3d().direct_space_state if is_inside_tree() else null
	var probe := SphereShape3D.new()
	probe.radius = float(cfg.get("crane_clear_m", 0.0))
	var h := step
	while h <= top + 1e-4:
		var at := pose.origin + Vector3.UP * h
		if view_blocker(chest, at).is_empty() and not _inside_solid(space, probe, at):
			return CameraPose.looking(at, chest, pose.fov_deg, pose.dof)
		h += step
	# a ceiling right over him (a spiral's next turn): no height clears, so look in from the side instead, around
	# him from the shot's own side first, at crane_ring_m out and crane_ring_up_m over his chest
	var away := Vector3(pose.origin.x - chest.x, 0.0, pose.origin.z - chest.z)
	var start := atan2(away.x, away.z) if away.length_squared() > 1e-6 else 0.0
	var turns := maxi(int(cfg.get("crane_ring_turns", 0)), 1)
	for dist: Variant in cfg.get("crane_ring_m", []):
		for k in turns:
			# 0, +1, -1, +2, -2 ... steps round from the shot's side
			var n := (k + 1) / 2 * (1 if k % 2 == 1 else -1)
			var angle := start + TAU * n / turns
			var at := chest + Vector3(sin(angle), 0.0, cos(angle)) * float(dist)
			at.y += float(cfg.get("crane_ring_up_m", 0.0))
			if view_blocker(chest, at).is_empty() and not _inside_solid(space, probe, at):
				return CameraPose.looking(at, chest, pose.fov_deg, pose.dof)
	return null


## `from`, swung down round `aim` (same distance, same heading) so it looks down on it at most `max_pitch` radians;
## max_pitch <= 0 leaves it as it is. The hub orbit's (orbit.max_pitch_deg: Ch4's wake looked straight down on a party
## made tiny, the PC's row 24).
static func clamp_pitch(from: Vector3, aim: Vector3, max_pitch: float) -> Vector3:
	var v := from - aim
	var flat := Vector2(v.x, v.z)
	if max_pitch <= 0.0 or flat.length() < 1e-4 or atan2(v.y, flat.length()) <= max_pitch:
		return from
	var r := v.length()
	var h := flat.normalized() * r * cos(max_pitch)
	return aim + Vector3(h.x, r * sin(max_pitch), h.y)


## `pose` moved to `chest` + `back`, looking where it looked, when that line is clear and the spot isn't in a solid;
## else widest_view(); null when neither clears.
func _backed_off(pose: CameraPose, chest: Vector3, back: Vector3, cfg: Dictionary) -> CameraPose:
	var at := chest + back
	var probe := SphereShape3D.new()
	probe.radius = float(cfg.get("crane_clear_m", 0.0))
	var space := get_world_3d().direct_space_state if is_inside_tree() else null
	if view_blocker(chest, at).is_empty() and not _inside_solid(space, probe, at):
		var out := pose.copy()
		out.origin = at
		return out
	return widest_view(pose, chest, cfg)


## A pose standoff_m from the leader's `chest`, looking at him: crane_ring_up_m over it, then (under a low roof) level
## with it, in the first of crane_ring_turns directions round him, from the shot's own side, whose line is clear that
## far; when none is (a cabin), the one with the most clear room, margin_m short of its wall, if that beats `beat_m`.
## Null when no direction does better.
func widest_view(pose: CameraPose, chest: Vector3, cfg: Dictionary, beat_m := 0.0) -> CameraPose:
	var reach := float(cfg.get("standoff_m", 0.0))
	if reach <= 0.0:
		return null
	var space := get_world_3d().direct_space_state if is_inside_tree() else null
	var probe := SphereShape3D.new()
	probe.radius = float(cfg.get("crane_clear_m", 0.0))
	var margin := float(cfg.get("margin_m", 0.0))
	var away := Vector3(pose.origin.x - chest.x, 0.0, pose.origin.z - chest.z)
	var start := atan2(away.x, away.z) if away.length_squared() > 1e-6 else 0.0
	var turns := maxi(int(cfg.get("crane_ring_turns", 0)), 1)
	var best_at := Vector3.ZERO
	var best_m := beat_m
	for lift: float in [float(cfg.get("crane_ring_up_m", 0.0)), 0.0]:
		for k in turns:
			var n := (k + 1) / 2 * (1 if k % 2 == 1 else -1)  # 0, +1, -1, +2 ... round from the shot's side
			var angle := start + TAU * n / turns
			var dir := (Vector3(sin(angle), 0.0, cos(angle)) * reach + Vector3.UP * lift).normalized()
			var hit := view_blocker(chest, chest + dir * reach)
			var room := reach if hit.is_empty() else chest.distance_to(hit["position"] as Vector3) - margin
			if room <= best_m or _inside_solid(space, probe, chest + dir * room):
				continue
			if room >= reach:
				return CameraPose.looking(chest + dir * room, chest, pose.fov_deg, pose.dof)
			best_m = room
			best_at = chest + dir * room
	if best_m <= beat_m:
		return null
	return CameraPose.looking(best_at, chest, pose.fov_deg, pose.dof)


## True when a sphere `probe` at `at` overlaps a solid body (a crane height inside a step or a floor).
func _inside_solid(space: PhysicsDirectSpaceState3D, probe: SphereShape3D, at: Vector3) -> bool:
	if space == null or probe.radius <= 0.0:
		return false
	var q := PhysicsShapeQueryParameters3D.new()
	q.shape = probe
	q.transform = Transform3D(Basis.IDENTITY, at)
	q.collide_with_areas = false
	if target is CollisionObject3D:
		q.exclude = [(target as CollisionObject3D).get_rid()]
	return not space.intersect_shape(q, 1).is_empty()


## The nearest wall a player sees on the segment `from` -> `to`: {"position", "node"} of the first visible occluder
## mesh it crosses (see occluders()), or {} when the view is clear. Tested against the drawn triangles, not collision:
## a collider can miss a wall the player sees (Coilspire's shell) and walls nobody sees have colliders (bounds, a
## greybox wall hidden for a cutaway).
func view_blocker(from: Vector3, to: Vector3) -> Dictionary:
	if _occluders.is_empty() and not _occluders_read:
		collect_occluders()
	var seg := AABB(from, Vector3.ZERO).expand(to)
	var best := {}
	var best_d := INF
	for mi in _occluders:
		if not is_instance_valid(mi) or not mi.is_visible_in_tree():
			continue
		var xf := mi.global_transform
		if not (xf * mi.get_aabb()).intersects(seg):
			continue
		var inv := xf.affine_inverse()
		var hit := _triangles(mi.mesh).intersect_segment(inv * from, inv * to)
		if hit.is_empty():
			continue
		var at := xf * (hit["position"] as Vector3)
		var d := from.distance_to(at)
		if d < best_d:
			best_d = d
			best = {"position": at, "node": mi}
	return best


## Re-reads the zone's occluder meshes (visible or not; visibility is checked each frame): every MeshInstance3D under
## the rail root at least min_size_m across, with no transparent surface (foliage, glass, water), and not part of the
## target. Called on snap() and on the first check.
func collect_occluders() -> void:
	_occluders.clear()
	_occluders_read = true
	var cfg := data.get("occlusion", {}) as Dictionary
	var min_size := float(cfg.get("min_size_m", 0.0))
	var base: Node = rail_root if rail_root != null else self
	for n in base.find_children("*", "MeshInstance3D", true, false):
		var mi := n as MeshInstance3D
		if mi.mesh == null or (target != null and target.is_ancestor_of(mi)):
			continue
		var size := mi.get_aabb().size * mi.global_basis.get_scale().abs()
		if maxf(size.x, maxf(size.y, size.z)) < min_size or _see_through(mi):
			continue
		_occluders.append(mi)


static func _see_through(mi: MeshInstance3D) -> bool:
	for k in mi.mesh.get_surface_count():
		var mat := mi.get_active_material(k) as BaseMaterial3D
		if mat != null and mat.transparency != BaseMaterial3D.TRANSPARENCY_DISABLED:
			return true
	return false


## The mesh's triangles for segment tests, built once per mesh resource.
func _triangles(mesh: Mesh) -> TriangleMesh:
	if not _tri_cache.has(mesh):
		_tri_cache[mesh] = mesh.generate_triangle_mesh()
	return _tri_cache[mesh] as TriangleMesh


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
			desired = keep_in_frame(
				from,
				desired,
				aim_target,
				fov,
				float(data.get("keep_in_frame_share", 1.0)),
				float(data.get("keep_in_frame_aspect", 1.0))
			)
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
			var from := clamp_pitch(centre + offset, aim_target, deg_to_rad(_orbit_value("max_pitch_deg")))
			return CameraPose.looking(from, aim_target, fov, shot.dof_dict(), shot.roll_deg)
		CameraShot.Mode.FOLLOW:
			var heading := _to_world(shot.look_at) - _to_world(shot.position)
			heading = Vector3(heading.x, 0.0, heading.z).normalized()
			var dist := shot.follow_distance if shot.follow_distance > 0.0 else _follow_value("distance_m")
			var height := shot.follow_height if shot.follow_height > 0.0 else _follow_value("height_m")
			var centre := subject.global_position if subject != null else _to_world(shot.look_at)
			var desired := centre - heading * dist + Vector3.UP * height
			var rate := _rate(shot.follow_smoothing, "follow_smoothing_per_sec")
			var from := _smoothed(shot, "follow_pos", desired, rate, delta) as Vector3
			return CameraPose.looking(from, aim_target, fov, shot.dof_dict(), shot.roll_deg)
	var fixed_aim := aim_target if subject != target else _to_world(shot.look_at)
	# A safety net: a field volume's locked frame that would lose the leader turns to him. Never a cutscene's shot: its
	# frame is authored (O07's insert on a name-board has no one in it; M3-CIN-1235, row 58 regressed on big20).
	if subject == target and target != null and shot != _scripted_shot:
		fixed_aim = keep_in_frame(
			_to_world(shot.position),
			fixed_aim,
			aim_target,
			fov,
			float(data.get("keep_in_frame_fixed_share", 1.0)),
			float(data.get("keep_in_frame_aspect", 1.0))
		)
	return CameraPose.looking(_to_world(shot.position), fixed_aim, fov, shot.dof_dict(), shot.roll_deg)


## The node `shot` frames: its aim_node (relative to the rail root, or absolute) when set and
## found, else the player. A missing aim_node is an authoring bug (the shot frames the wrong thing),
## so it is loud (M1-ARC-09): push_error once per shot, recorded in missing_aim_nodes(), and the
## shot falls back to the player (or, with no player, to its authored look_at).
func subject_node(shot: CameraShot) -> Node3D:
	if shot.aim_node.is_empty():
		return target
	var base: Node = rail_root if rail_root != null else self
	var n := base.get_node_or_null(shot.aim_node) as Node3D
	if n == null:
		if not _aim_warned.has(shot):
			_aim_warned[shot] = true
			push_error(
				(
					"FieldCameraDirector: shot %s aim_node %s not found under %s; framing the player instead"
					% [shot.id, shot.aim_node, base.name]
				)
			)
		return target
	return n


## Ids of the shots whose aim_node was missing when evaluated (debug overlay, tests, M1-ARC-09).
func missing_aim_nodes() -> Array[StringName]:
	var ids: Array[StringName] = []
	for s: CameraShot in _aim_warned:
		ids.append(s.id)
	return ids


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


## The aim from `from` turned toward `subject` just enough that the subject sits within `share` of the frame's half
## angles of it, vertically (fov_deg, the vertical field of view) and horizontally (from `aspect`, width over height):
## a PAN_FOLLOW's capped pan never lets the leader leave the frame (the Lead's 10-29 walk audit: Coilspire's Tier1 and
## Tier2 lost Rhen for 3.6 s up the spiral), while a composition that keeps him inside (on a third) is left as authored.
static func keep_in_frame(
	from: Vector3, aim: Vector3, subject: Vector3, fov_deg: float, share: float, aspect: float = 1.0
) -> Vector3:
	var aim_dir := aim - from
	var to_subject := subject - from
	if aim_dir.length_squared() < 1e-8 or to_subject.length_squared() < 1e-8 or absf(aim_dir.normalized().y) > 0.999:
		return aim
	var basis := Basis.looking_at(aim_dir, Vector3.UP)
	var local := basis.inverse() * to_subject
	if local.z >= 0.0:
		return subject  # behind the camera: aim straight at him
	var half_v := deg_to_rad(fov_deg * 0.5)
	var limit_v := half_v * share
	var limit_h := atan(tan(half_v) * aspect) * share
	var yaw := atan2(local.x, -local.z)
	var pitch := atan2(local.y, -local.z)
	var turn_yaw := yaw - clampf(yaw, -limit_h, limit_h)
	var turn_pitch := pitch - clampf(pitch, -limit_v, limit_v)
	if turn_yaw == 0.0 and turn_pitch == 0.0:
		return aim
	var dir := Vector3.FORWARD.rotated(Vector3.RIGHT, turn_pitch).rotated(Vector3.UP, -turn_yaw)
	return from + (basis * dir).normalized() * aim_dir.length()


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


func _follow_value(key: String) -> float:
	return float((data.get("follow", {}) as Dictionary).get(key, 0.0))


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
