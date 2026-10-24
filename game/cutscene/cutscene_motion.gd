class_name CutsceneMotion
extends RefCounted
## The shape of a cutscene actor's motion (M2-FP-29; docs/kb/tech/cutscenes.md "Motion"): turns ease in
## and out over a time scaled by the angle, and a walk accelerates, cruises and decelerates instead of
## starting and stopping at full speed. Pure functions of time; CutsceneSequencer drives them with the
## tunings in game/data/cutscene/sequencer.json.


## `t` (0..1) through Godot's ease() curve: a negative curve eases in and out (-2 is a smoothstep-like
## S), 1 is linear.
static func eased(t: float, curve: float) -> float:
	return ease(clampf(t, 0.0, 1.0), curve)


## How long a turn through `angle` radians takes: min_sec for none, max_sec for a half turn.
static func turn_duration(angle: float, min_sec: float, max_sec: float) -> float:
	return lerpf(min_sec, max_sec, clampf(absf(angle) / PI, 0.0, 1.0))


## The accelerate and decelerate times for a walk of `dist` metres at `speed`, shortened together when
## the walk is too short to reach full speed. Returns Vector2(accel_sec, decel_sec).
static func ramps(dist: float, speed: float, accel_sec: float, decel_sec: float) -> Vector2:
	var ramp_m := speed * (accel_sec + decel_sec) * 0.5
	if ramp_m <= dist or ramp_m <= 0.0:
		return Vector2(accel_sec, decel_sec)
	var k := sqrt(dist / ramp_m)
	return Vector2(accel_sec * k, decel_sec * k)


## The time a walk of `dist` metres takes with its ramps.
static func walk_duration(dist: float, speed: float, accel_sec: float, decel_sec: float) -> float:
	if dist <= 0.0 or speed <= 0.0:
		return 0.0
	var r := ramps(dist, speed, accel_sec, decel_sec)
	var top := _top_speed(dist, speed, r)
	return r.x + r.y + maxf(dist - top * (r.x + r.y) * 0.5, 0.0) / top


## The share of the walk covered `sec` seconds into it (0..1): a linear speed ramp up, a cruise and a
## ramp down, so the position eases in and out.
static func walk_fraction(sec: float, dist: float, speed: float, accel_sec: float, decel_sec: float) -> float:
	if dist <= 0.0 or speed <= 0.0:
		return 1.0
	var r := ramps(dist, speed, accel_sec, decel_sec)
	var v := _top_speed(dist, speed, r)
	var a := r.x
	var d := r.y
	var cruise := maxf(dist - v * (a + d) * 0.5, 0.0) / v
	var s: float
	if sec <= 0.0:
		s = 0.0
	elif sec < a:
		s = v * sec * sec / (2.0 * a)
	elif sec < a + cruise:
		s = v * a * 0.5 + v * (sec - a)
	else:
		var u := minf(sec - a - cruise, d)
		s = v * a * 0.5 + v * cruise + (v * (u - u * u / (2.0 * d)) if d > 0.0 else 0.0)
	return clampf(s / dist, 0.0, 1.0)


## The speed reached: full speed, unless the shortened ramps alone cover the walk (then lower, so the
## ramps meet exactly at the far end).
static func _top_speed(dist: float, speed: float, r: Vector2) -> float:
	var ramp_m := speed * (r.x + r.y) * 0.5
	if ramp_m <= dist or r.x + r.y <= 0.0:
		return speed
	return 2.0 * dist / (r.x + r.y)
