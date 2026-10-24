class_name FrameClock
extends RefCounted
## Wall-clock frame timer for every hitch and frame-time statistic (M2-ARC-05, ADR 0029).
##
## Godot caps the process `delta` at about 140-150 ms (4.6.3 and 4.7.2: a 500 ms stall reports 135-147 ms;
## M1-RND-29), so a statistic built on `delta` never sees a frame over that, and ADR 0029's 1 s hidden-frame
## budget can never trip. Anything that judges a frame against a budget times it with a FrameClock instead:
## the wall time between two marks, from Time.get_ticks_usec.
##
## Use: reset() when the window starts (or reset_at() with a timestamp you already took), then lap() once per
## frame: it returns the ms since the previous mark and makes now the new mark. lap_at(now_usec) does the
## same for a timestamp the caller read (SceneRouter.VisibleWindow). since_ms() reads without marking.
## Tests inject the clock: FrameClock.new(fake_now), where fake_now is a Callable returning microseconds.

const USEC_PER_MSEC := 1000.0
const UNSET := -1

var _now: Callable
var _mark_usec := UNSET


## `now_usec`: a Callable returning the current time in microseconds (default: Time.get_ticks_usec).
func _init(now_usec: Callable = Callable()) -> void:
	_now = now_usec if now_usec.is_valid() else Callable(Time, &"get_ticks_usec")


## The clock's current time in microseconds.
func now_usec() -> int:
	return int(_now.call())


## Starts (or restarts) the window now.
func reset() -> void:
	_mark_usec = now_usec()


## Starts (or restarts) the window at `t_usec`.
func reset_at(t_usec: int) -> void:
	_mark_usec = t_usec


## True once reset() (or a lap) has set a mark.
func is_started() -> bool:
	return _mark_usec != UNSET


## The wall ms since the last mark, and now becomes the mark. On a clock never started it only marks: 0.
func lap() -> float:
	return lap_at(now_usec())


## lap() for a timestamp the caller already read.
func lap_at(t_usec: int) -> float:
	var ms := ms_between(_mark_usec, t_usec) if is_started() else 0.0
	_mark_usec = t_usec
	return ms


## The wall ms since the last mark, without moving it (0 before the first mark).
func since_ms() -> float:
	return ms_between(_mark_usec, now_usec()) if is_started() else 0.0


static func ms_between(from_usec: int, to_usec: int) -> float:
	return (to_usec - from_usec) / USEC_PER_MSEC
