class_name SwellRingClock
extends RefCounted
## Real-time driver for an open SwellTimingRing (M1-UI-05, input fairness). The ring itself stays
## node-free and deterministic; this is the one place that reads the wall clock.
##
## - step(delta, true): a rendered frame's delta, clamped to the ring's max_step_sec. One long frame
##   (a shader prewarm, a GC pause, a load spike) then pauses the ring instead of skipping a beat or
##   turning it into a miss the player never saw.
## - press(): first catches the ring up from the last step to the moment the input is handled
##   (clamped the same way), so a press is graded against "now", not against the previous frame.
##   The next rendered frame subtracts what was caught up, so no time is counted twice.
## - step(delta, false): simulated time (tests and capture scripts): exact, never clamped.
## - One clock (M1-NIT-01, review-sweep-J S1 for UI-05): a frame's delta is game time, which
##   Engine.time_scale scales, so press() scales its wall-clock catch-up by the same time_scale
##   before clamping it. Under a slow-mo or a frozen capture (time_scale 0) the ring and the
##   catch-up then agree; pacing (BattleController) still never scales the ring.

const USEC_PER_SEC := 1000000.0

var ring: SwellTimingRing
## The wall clock in microseconds. Tests inject a fake one.
var now_usec := Callable(Time, &"get_ticks_usec")
## Engine.time_scale (game seconds per wall-clock second). Tests inject a fake one.
var time_scale := func() -> float: return Engine.time_scale

var _last_usec := 0
var _caught_up := 0.0


func _init(r: SwellTimingRing, clock: Callable = Callable()) -> void:
	ring = r
	if clock.is_valid():
		now_usec = clock
	_last_usec = int(now_usec.call())


## Moves the ring on: by a rendered frame's delta when `frame` (from _process), else by exactly
## `delta` (simulated time).
func step(delta: float, frame: bool) -> void:
	if frame:
		ring.advance(maxf(ring.clamp_step(delta) - _caught_up, 0.0))
	else:
		ring.advance(delta)
	_caught_up = 0.0
	_last_usec = int(now_usec.call())


## Grades a press at the moment it is handled; `catch_up` false grades it where the ring stands
## (a frozen capture). Returns the ring's grade (&"" when ignored).
func press(catch_up: bool = true) -> StringName:
	var now := int(now_usec.call())
	if catch_up:
		var scale := float(time_scale.call())
		var dt := ring.clamp_step(float(now - _last_usec) / USEC_PER_SEC * scale)
		ring.advance(dt)
		_caught_up += dt
	_last_usec = now
	return ring.press()
