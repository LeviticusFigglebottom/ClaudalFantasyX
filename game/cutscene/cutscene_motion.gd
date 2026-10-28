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


## Seconds until every actor walk and turn among a sequencer's running `motions` ("move:<id>" and "turn:<id>"
## keys, each {elapsed, duration}) has ended (M2-HER-1113: a scene's end waits for them instead of jumping them).
static func actor_motion_left(motions: Dictionary) -> float:
	var left := 0.0
	for key: StringName in motions.keys():
		if String(key).begins_with("move:") or String(key).begins_with("turn:"):
			var m: Dictionary = motions[key]
			left = maxf(left, float(m["duration"]) - float(m["elapsed"]))
	return left


## M3-CIN-1221: the length of a polyline (the sum of its legs).
static func path_length(path: PackedVector3Array) -> float:
	var total := 0.0
	for i in range(1, path.size()):
		total += path[i - 1].distance_to(path[i])
	return total


## The index of the leg `s` metres along `path` lies on (0 for the first; the last leg past the end).
static func path_leg(path: PackedVector3Array, s: float) -> int:
	var run := 0.0
	for i in range(1, path.size()):
		run += path[i - 1].distance_to(path[i])
		if s < run:
			return i - 1
	return maxi(path.size() - 2, 0)


## The point `s` metres along `path` (clamped to its ends).
static func path_point(path: PackedVector3Array, s: float) -> Vector3:
	if path.is_empty():
		return Vector3.ZERO
	var left := maxf(s, 0.0)
	for i in range(1, path.size()):
		var leg := path[i - 1].distance_to(path[i])
		if left <= leg and leg > 0.0:
			return path[i - 1].lerp(path[i], left / leg)
		left -= leg
	return path[path.size() - 1]


## The level direction of leg `i` of `path` (from point i to point i + 1), or zero.
static func flat_dir(path: PackedVector3Array, i: int) -> Vector3:
	if i + 1 >= path.size():
		return Vector3.ZERO
	return Vector3(path[i + 1].x - path[i].x, 0.0, path[i + 1].z - path[i].z)


## How long an auto-advancing line holds once `box` has revealed it: at least `min_hold`, and long enough that the
## whole line was up for its length / `read_cps` seconds (no reading pace when `read_cps` <= 0).
static func read_hold(box: DialogueBox, read_cps: float, min_hold: float) -> float:
	if read_cps <= 0.0 or box == null:
		return min_hold
	var chars := float(box.shown_text().length())
	var reveal_cps := box.settings.chars_per_sec if box.settings != null else 0.0
	var revealed := chars / reveal_cps if reveal_cps > 0.0 else 0.0
	return maxf(min_hold, chars / read_cps - revealed)
