class_name HeroGaitClips
extends RefCounted
## The field body's gait transitions (M2-HER-1107, ADR 0190): walk and run starts and stops, turning in
## place and an idle variant, played over HeroFieldActor's locomotion blend from the characters track's
## in-place clips (M2-CHR-12) and their root curves in game/data/characters/locomotion.json. Pure maths
## and a small state machine: no Nodes and no randomness, so tests drive it frame by frame; the actor
## plays `clip` in an action slot at `time_scale` and, while turning, shows `turn_yaw()`.
##
## The gameplay node keeps moving the way it always does; this only picks what the feet show:
##   start  still for min_still_sec, then moving: walk_start (or run_start when the target speed is a run)
##          plays *by distance*: its time is wherever its root_travel_m curve has covered the ground the
##          body has, so the feet stay planted whatever the controller's acceleration. At its end (the
##          cycle's first frame) the blend takes over again.
##   stop   the target speed drops to 0 (the source says so) or the speed falls below stop_unknown_ratio x
##          walk speed: walk_stop / run_stop enters where its remaining root travel matches the distance
##          left to stop, plays by distance, and finishes in time once the body is still.
##   turn   still with the facing more than turn_min_deg away: turn_in_place_l90 / r90 / 180 plays and the
##          visible yaw follows its root_yaw_deg curve, scaled to land on the facing.
##   idle   after a per-hero idle time (a hash of its id) idle_variant plays once.
## A clip the model lacks (or whose curve the data lacks) is simply never chosen: the body then blends
## and spins as before. Tuning: game/data/hero_motion/hero_motion.json "field.gait_clips".

enum Phase { BLEND, START, STOP, TURN, IDLE_VARIANT }

const SALT_IDLE := "idle_variant"
## A clip within this of its end (seconds) has ended.
const END_EPS := 0.0001

## The phase and the gait clip the body shows (&"" while on the blend).
var phase: Phase = Phase.BLEND
var clip: StringName = &""
## Where in `clip` the body is (seconds) and the time scale this frame's advance plays it at.
var clip_time := 0.0
var time_scale := 1.0
## The cross-fade for the last change of `clip` (seconds).
var blend_sec := 0.0
## How long the body has been still, and still with nothing to do (idle variant clock).
var still_sec := 0.0
var idle_sec := 0.0
## True once the body moves (speed over start_speed_mps) until it is still (under still_speed_mps).
var moving := false
## The highest speed since the body started moving.
var peak_speed := 0.0
## The turn being played: from this yaw by this much (radians, + = left).
var turn_from := 0.0
var turn_total := 0.0

var walk_clip_mps := 0.0
var run_clip_mps := 0.0
var idle_after_sec := 0.0

var _cfg: Dictionary = {}
## role (walk_start, run_start, walk_stop, run_stop, turn_l90, turn_r90, turn_180, idle_variant) ->
## {name: StringName, row: the locomotion.json row} for the clips this body can play.
var _clips: Dictionary = {}
var _fps := 0.0
## Ground covered since the body was last still (a start's travel), and since a stop began.
var _travel := 0.0
var _base := 0.0
var _last_speed := 0.0
## A stop may still play for this run of motion (one per start: a stop that ran, or was skipped, spends it).
var _can_stop := false


## `cfg` is hero_motion.json field.gait_clips; `loco_hero` the hero's table from locomotion.json ({} when
## the file is missing); `has_clip` tells whether the model has a clip; `fps` is locomotion.json's key
## rate; `hero_id` seeds the idle variant's time.
func _init(
	cfg: Dictionary,
	loco_hero: Dictionary,
	has_clip: Callable,
	fps: float,
	walk_mps: float,
	run_mps: float,
	hero_id: StringName
) -> void:
	_cfg = cfg
	_fps = fps
	walk_clip_mps = walk_mps
	run_clip_mps = run_mps
	var names := cfg.get("clips", {}) as Dictionary
	for role: String in names.keys():
		var clip_name := StringName(str(names[role]))
		var row := loco_hero.get(String(clip_name), {}) as Dictionary
		if row.is_empty() or not has_clip.call(clip_name):
			continue
		var curve := "root_yaw_deg" if role.begins_with("turn_") else "root_travel_m"
		if role != "idle_variant" and (row.get(curve, []) as Array).size() < 2:
			continue
		_clips[StringName(role)] = {"name": clip_name, "row": row}
	idle_after_sec = (
		_f("idle_variant_after_sec") + _f("idle_variant_spread_sec") * HeroIdleMicro.share(hero_id, SALT_IDLE)
	)


## The locomotion.json dictionary at `path`, or {} when it is missing (the clips are not in yet).
static func load_locomotion(path: String) -> Dictionary:
	if path == "" or not FileAccess.file_exists(path):
		return {}
	var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(path))
	return parsed if parsed is Dictionary else {}


## True when the body can play the clip for `role` (e.g. &"walk_start").
func has_role(role: StringName) -> bool:
	return _clips.has(role)


## Back to the blend with no clip, for a body now moving at `speed` (snaps and teleports pass 0; a
## cutscene clip holding the body resets it every frame). A body at rest counts as rested (a turn may
## play at once); a moving one never starts (it is already under way).
func reset(speed: float = 0.0) -> void:
	_set_clip(Phase.BLEND, &"", 0.0)
	moving = speed > _f("start_speed_mps")
	_can_stop = false
	still_sec = 0.0 if moving else _f("min_still_sec")
	idle_sec = 0.0
	peak_speed = speed if moving else 0.0
	_travel = 0.0
	_last_speed = speed
	time_scale = 1.0


## One frame. `yaw` is the visible yaw (radians), `speed` the filtered ground speed (m/s), `dist` the
## ground covered this frame (m), `heading_err` the angle from the visible yaw to the travel (radians),
## `facing_err` from the visible yaw to the node's facing (radians, + = left), `intent_mps` the speed the
## source is heading for (-1 when it cannot tell), `stop_dist_m` the distance it needs to stop (-1 when
## it cannot tell).
func step(
	yaw: float,
	speed: float,
	dist: float,
	heading_err: float,
	facing_err: float,
	intent_mps: float,
	stop_dist_m: float,
	delta: float
) -> void:
	if delta <= 0.0:
		return
	var was_moving := moving
	if not moving and speed > _f("start_speed_mps"):
		moving = true
		_can_stop = true
	elif moving and speed < _f("still_speed_mps"):
		moving = false
	if moving:
		peak_speed = maxf(peak_speed, speed)
		_travel += dist
	else:
		_travel = 0.0 if speed < _f("still_speed_mps") and intent_mps <= 0.0 else _travel + dist
	time_scale = 1.0
	match phase:
		Phase.START:
			_step_start(speed, intent_mps, stop_dist_m, delta)
		Phase.STOP:
			_step_stop(speed, dist, intent_mps, delta)
		Phase.TURN, Phase.IDLE_VARIANT:
			_step_timed(speed, facing_err, intent_mps)
		_:
			_step_blend(was_moving, yaw, speed, heading_err, facing_err, intent_mps, stop_dist_m, delta)
	if moving:
		still_sec = 0.0
		idle_sec = 0.0
	else:
		still_sec += delta
		idle_sec = idle_sec + delta if phase == Phase.BLEND else 0.0
		if speed < _f("still_speed_mps"):
			peak_speed = 0.0
	_last_speed = speed
	clip_time += time_scale * delta


func _step_blend(
	was_moving: bool,
	yaw: float,
	speed: float,
	heading_err: float,
	facing_err: float,
	intent_mps: float,
	stop_dist_m: float,
	delta: float
) -> void:
	var rested := still_sec >= _f("min_still_sec")
	var wants_move := moving or intent_mps > 0.0
	if wants_move and not was_moving and rested and _travel > 0.0:
		if absf(heading_err) <= deg_to_rad(_f("start_max_angle_deg")):
			var target := intent_mps if intent_mps > 0.0 else speed
			var role := &"run_start" if target > run_clip_pick() and has_role(&"run_start") else &"walk_start"
			if has_role(role):
				_set_clip(Phase.START, role, _f("blend_in_sec"))
				time_scale = _start_scale(0.0, delta)
				return
	if moving and _can_stop and _wants_stop(speed, intent_mps):
		_can_stop = false
		if peak_speed >= walk_clip_mps * _f("stop_min_speed_ratio"):
			_enter_stop(speed, stop_dist_m, delta)
			return
	if not moving and not wants_move and rested:
		var turn := turn_role(facing_err)
		if turn != &"":
			_enter_turn(turn, yaw, facing_err)
			return
		if idle_sec >= idle_after_sec and has_role(&"idle_variant"):
			_set_clip(Phase.IDLE_VARIANT, &"idle_variant", _f("blend_in_sec"))


func _step_start(speed: float, intent_mps: float, stop_dist_m: float, delta: float) -> void:
	if _wants_stop(speed, intent_mps) or (intent_mps < 0.0 and not moving and speed < _f("still_speed_mps")):
		# let go before the start finished: a stop if it got going, else straight back to the blend
		_can_stop = false
		if peak_speed >= walk_clip_mps * _f("stop_min_speed_ratio"):
			_enter_stop(speed, stop_dist_m, delta)
		else:
			_set_clip(Phase.BLEND, &"", _f("blend_in_sec"))
		return
	if clip == _name(&"walk_start") and has_role(&"run_start") and _travel <= _f("run_switch_max_travel_m"):
		var target := intent_mps if intent_mps > 0.0 else speed
		if target > run_clip_pick():
			_set_clip(Phase.START, &"run_start", _f("blend_in_sec"))
			time_scale = _start_scale(0.0, delta)
			return
	if clip_time >= _length() - END_EPS:
		_set_clip(Phase.BLEND, &"", _f("hand_back_sec"))
		return
	time_scale = _start_scale(clip_time, delta)


func _step_stop(speed: float, dist: float, intent_mps: float, delta: float) -> void:
	if intent_mps > 0.0 or (intent_mps < 0.0 and speed > _last_speed + _f("stop_abort_mps")):
		_set_clip(Phase.BLEND, &"", _f("blend_in_sec"))  # going again
		return
	if clip_time >= _length() - END_EPS:
		_set_clip(Phase.BLEND, &"", _f("hand_back_sec"))
		return
	_base += dist
	var want := time_at(_curve(), _fps, _base)
	var floor_scale := _f("stop_min_scale") if dist / delta >= _f("still_speed_mps") else 1.0
	time_scale = _scale_to(want, clip_time, delta, floor_scale)


func _step_timed(speed: float, facing_err: float, intent_mps: float) -> void:
	if phase == Phase.IDLE_VARIANT and (moving or intent_mps > 0.0 or turn_role(facing_err) != &""):
		_set_clip(Phase.BLEND, &"", _f("blend_in_sec"))
		return
	if phase == Phase.TURN and speed > _f("start_speed_mps"):
		_set_clip(Phase.BLEND, &"", _f("blend_in_sec"))  # moving off: the travel turn takes over
		return
	if clip_time >= _length() - END_EPS:
		if phase == Phase.IDLE_VARIANT:
			idle_sec = 0.0
		_set_clip(Phase.BLEND, &"", _f("hand_back_sec"))


## The source is coming to a stop: its target speed is 0, or (when it cannot tell) its speed is falling
## under stop_unknown_ratio x the walk clip speed.
func _wants_stop(speed: float, intent_mps: float) -> bool:
	if intent_mps == 0.0:
		return true
	return intent_mps < 0.0 and speed < walk_clip_mps * _f("stop_unknown_ratio") and speed < _last_speed + END_EPS


func _enter_stop(speed: float, stop_dist_m: float, delta: float) -> void:
	var role := &"run_stop" if peak_speed > run_clip_pick() and has_role(&"run_stop") else &"walk_stop"
	if not has_role(role):
		_set_clip(Phase.BLEND, &"", _f("blend_in_sec"))
		return
	var left := stop_dist_m
	if left < 0.0:
		left = speed * speed / (2.0 * _f("stop_decel_mps2"))
	_set_clip(Phase.STOP, role, _f("blend_in_sec"))
	var keys := _curve()
	_base = maxf(float(keys[keys.size() - 1]) - left, 0.0)
	time_scale = time_at(keys, _fps, _base) / delta  # one jump to the remaining travel, under the fade


func _enter_turn(role: StringName, yaw: float, facing_err: float) -> void:
	_set_clip(Phase.TURN, role, _f("blend_in_sec"))
	turn_from = yaw
	turn_total = facing_err
	if role == &"turn_180" and facing_err < 0.0:
		turn_total = facing_err + TAU  # the 180 turns to the left


## The clip role for a still body whose facing is `facing_err` away (radians, + = left), or &"".
func turn_role(facing_err: float) -> StringName:
	var a := absf(facing_err)
	if a < deg_to_rad(_f("turn_min_deg")):
		return &""
	var side := &"turn_l90" if facing_err > 0.0 else &"turn_r90"
	if a >= deg_to_rad(_f("turn_180_min_deg")) and has_role(&"turn_180"):
		return &"turn_180"
	return side if has_role(side) else &""


## The yaw the turn clip shows now: from turn_from by turn_total, following its root_yaw_deg curve.
func turn_yaw() -> float:
	var keys := _curve()
	var end := float(keys[keys.size() - 1])
	var u := yaw_at(keys, _fps, clip_time) / end if end != 0.0 else 1.0
	return wrapf(turn_from + turn_total * u, -PI, PI)


## The speed over which a start or stop is a run's: run_pick_ratio x the walk clip's speed.
func run_clip_pick() -> float:
	return walk_clip_mps * _f("run_pick_ratio")


## The time (s) at which a curve of `keys` (one value per key at `fps`, non-decreasing) reaches `value`.
static func time_at(keys: Array, fps: float, value: float) -> float:
	if keys.size() < 2 or fps <= 0.0 or value <= float(keys[0]):
		return 0.0
	for i in range(1, keys.size()):
		var a := float(keys[i - 1])
		var b := float(keys[i])
		if value <= b:
			var u := (value - a) / (b - a) if b > a else 1.0
			return (float(i - 1) + u) / fps
	return float(keys.size() - 1) / fps


## The curve's value at time `t` (linear between keys at `fps`, held past the ends).
static func yaw_at(keys: Array, fps: float, t: float) -> float:
	if keys.is_empty():
		return 0.0
	var x := clampf(t * fps, 0.0, float(keys.size() - 1))
	var i := mini(int(floor(x)), keys.size() - 2)
	if i < 0:
		return float(keys[0])
	return lerpf(float(keys[i]), float(keys[i + 1]), x - float(i))


func _start_scale(now: float, delta: float) -> float:
	var want := time_at(_curve(), _fps, _travel)
	if now <= 0.0:
		return want / maxf(delta, END_EPS)  # the first frame jumps to the ground already covered
	return _scale_to(want, now, delta, 0.0)


func _scale_to(want: float, now: float, delta: float, floor_scale: float) -> float:
	var s := clampf((want - now) / delta, floor_scale, _f("max_scale"))
	return minf(s, maxf(_length() - now, 0.0) / delta)


func _set_clip(to: Phase, role: StringName, fade: float) -> void:
	phase = to
	clip = _name(role) if role != &"" else &""
	clip_time = 0.0
	blend_sec = fade


func _role() -> StringName:
	for role: StringName in _clips.keys():
		if (_clips[role] as Dictionary)["name"] == clip:
			return role
	return &""


func _name(role: StringName) -> StringName:
	return (_clips[role] as Dictionary)["name"] if _clips.has(role) else &""


func _row() -> Dictionary:
	var role := _role()
	return (_clips[role] as Dictionary)["row"] as Dictionary if role != &"" else {}


func _curve() -> Array:
	var row := _row()
	return row.get("root_yaw_deg", row.get("root_travel_m", [0.0, 0.0])) as Array


func _length() -> float:
	return float(_row().get("length_s", 0.0))


func _f(key: String) -> float:
	return float(_cfg.get(key, 0.0))
