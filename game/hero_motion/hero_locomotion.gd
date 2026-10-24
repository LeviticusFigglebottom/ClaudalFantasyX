class_name HeroLocomotion
extends RefCounted
## Pure hero motion maths (M2-HER-1101, ADR 0190): an eased, rate-capped yaw and the gait blend a hero's
## AnimationTree reads from ground speed. No Nodes and no randomness, so tests drive it frame by frame.
## HeroFieldActor (the field), the cutscene turn helper and the battle actors share one of these per body.
##
## Turning never snaps: each step the yaw moves at most max_rate * delta. The turn speed ramps up at
## max_accel (no instant whip) and eases out in proportion to the error left (settle_gain), so the body
## comes to rest on its heading instead of stopping dead. Tuning: game/data/hero_motion/hero_motion.json.

const DATA_PATH := "res://game/data/hero_motion/hero_motion.json"
const IDLE := 0
const WALK := 1
const RUN := 2
## Within this of its heading (radians, ~0.03°) a turn has landed: the eased tail would otherwise run forever.
const ARRIVE_RAD := 0.0005

var max_rate_rad := 0.0
var max_accel_rad := 0.0
var settle_gain := 0.0
var min_move_speed := 0.0
var walk_clip_mps := 0.0
var run_clip_mps := 0.0
var max_playback_scale := 1.0
var speed_smoothing_sec := 0.0
var teleport_m := 0.0

## The visible body's yaw (radians, Basis(UP, yaw) * FORWARD faces the way the body faces).
var yaw := 0.0
## Its current turn speed (radians per second, signed).
var yaw_rate := 0.0
## The filtered ground speed the gait blend reads (m/s).
var speed := 0.0


func _init(data: Dictionary = {}) -> void:
	configure(data if not data.is_empty() else load_data())


static func load_data() -> Dictionary:
	var f := FileAccess.open(DATA_PATH, FileAccess.READ)
	if f == null:
		push_error("HeroLocomotion: cannot read %s" % DATA_PATH)
		return {}
	var parsed: Variant = JSON.parse_string(f.get_as_text())
	return parsed if parsed is Dictionary else {}


func configure(d: Dictionary) -> void:
	var t := d.get("turn", {}) as Dictionary
	max_rate_rad = deg_to_rad(float(t.get("max_rate_deg_per_sec", 0.0)))
	max_accel_rad = deg_to_rad(float(t.get("max_accel_deg_per_sec2", 0.0)))
	settle_gain = float(t.get("settle_gain", 0.0))
	min_move_speed = float(t.get("min_move_speed_mps", 0.0))
	var g := d.get("gait", {}) as Dictionary
	walk_clip_mps = float(g.get("walk_clip_mps", 0.0))
	run_clip_mps = float(g.get("run_clip_mps", 0.0))
	max_playback_scale = float(g.get("max_playback_scale", 1.0))
	speed_smoothing_sec = float(g.get("speed_smoothing_sec", 0.0))
	teleport_m = float(g.get("teleport_m", 0.0))


## Puts the body on `to_yaw` at once with no turn speed (spawns, teleports, cuts): the only snap allowed.
func reset_yaw(to_yaw: float) -> void:
	yaw = to_yaw
	yaw_rate = 0.0


## One turn step toward `target_yaw`. Returns the new yaw; |change| <= max_rate * delta always.
func step_yaw(target_yaw: float, delta: float) -> float:
	if delta <= 0.0:
		return yaw
	var err := angle_difference(yaw, target_yaw)
	var want := clampf(err * settle_gain, -max_rate_rad, max_rate_rad)
	yaw_rate = move_toward(yaw_rate, want, max_accel_rad * delta)
	var turn := clampf(yaw_rate * delta, -max_rate_rad * delta, max_rate_rad * delta)
	if absf(err) <= ARRIVE_RAD or (absf(turn) >= absf(err) and signf(turn) == signf(err)):
		# Arrived this step: land on the heading and shed the turn speed rather than overshoot.
		turn = err
		yaw_rate = 0.0
	yaw = wrapf(yaw + turn, -PI, PI)
	return yaw


## One gait step from the measured ground speed (m/s). Returns the filtered speed.
func step_speed(ground_speed: float, delta: float) -> float:
	if speed_smoothing_sec <= 0.0 or delta <= 0.0:
		speed = ground_speed
	else:
		speed = lerpf(speed, ground_speed, 1.0 - exp(-delta / speed_smoothing_sec))
	return speed


## Drops the gait to `to_speed` at once (spawns, teleports).
func reset_speed(to_speed: float = 0.0) -> void:
	speed = to_speed


## The BlendSpace1D position for the filtered speed: the speed itself, with the points at
## 0 (idle), walk_clip_mps (walk) and run_clip_mps (run).
func blend_position() -> float:
	return clampf(speed, 0.0, run_clip_mps)


## Idle, walk and run weights (they sum to 1) for a ground speed, as the BlendSpace1D mixes them.
func weights(at_speed: float) -> PackedFloat32Array:
	var s := clampf(at_speed, 0.0, run_clip_mps)
	var w := PackedFloat32Array([0.0, 0.0, 0.0])
	if s <= walk_clip_mps:
		var t := s / walk_clip_mps if walk_clip_mps > 0.0 else 1.0
		w[IDLE] = 1.0 - t
		w[WALK] = t
	else:
		var u := (s - walk_clip_mps) / (run_clip_mps - walk_clip_mps)
		w[WALK] = 1.0 - u
		w[RUN] = u
	return w


## The gait's playback scale: 1 inside the blend; above run_clip_mps the run speeds up so the feet keep
## planting, up to max_playback_scale.
func playback_scale(at_speed: float) -> float:
	if run_clip_mps <= 0.0 or at_speed <= run_clip_mps:
		return 1.0
	return minf(at_speed / run_clip_mps, max_playback_scale)


## True when a body moving at `ground_speed` should turn toward its travel rather than its node's facing.
func is_moving(ground_speed: float) -> bool:
	return ground_speed > min_move_speed


## True when a frame's move of `distance_m` is a teleport (no gait, the yaw snaps).
func is_teleport(distance_m: float) -> bool:
	return teleport_m > 0.0 and distance_m > teleport_m


## Yaw of a planar direction, FieldMotor's convention (Basis(UP, yaw) * FORWARD = dir).
static func yaw_of(dir: Vector3) -> float:
	return atan2(-dir.x, -dir.z)
