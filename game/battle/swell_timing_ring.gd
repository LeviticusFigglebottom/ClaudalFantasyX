class_name SwellTimingRing
extends RefCounted
## Rhen's Swell input, the lantern-flicker timing ring (SPEC §6.2; formulas.md § Swell). After a
## short lead-in the lamp flares `beats` times on a fixed rhythm, a ring closing on it each time;
## the player presses once per flare, at its brightest. Node-free input logic: the HUD draws it
## (SwellRingView) and tests drive it the same way, through advance(), press() and cancel().
## result() is what BattleSwell.perform() takes.
##
## - One press per beat. A press before the beat opens is ignored; a press in the beat is graded
##   by its distance from the peak; a beat that ends unpressed is a miss. Mashing cannot help:
##   the first press in a beat is the one that counts.
## - Cancelable only before the first grade, so an input cannot be retried until it goes well.

const GRADE_PERFECT := &"perfect"
const GRADE_GOOD := &"good"
const GRADE_MISS := &"miss"

var beats := 1
var lead_in_sec := 0.0
var beat_sec := 1.0
## Where the flare peaks inside its beat, as a fraction of beat_sec.
var peak_at := 0.0
## Largest distance from the peak (seconds) for each grade.
var perfect_sec := 0.0
var good_sec := 0.0
## Seconds since the ring opened (advance()).
var elapsed := 0.0
## One grade per finished beat, in order.
var grades: Array[StringName] = []
var cancelled := false


## `input` is a swell.json "inputs" row of kind timing_ring.
func _init(input: Dictionary = {}) -> void:
	beats = maxi(int(input.get("beats", beats)), 1)
	lead_in_sec = float(input.get("lead_in_sec", lead_in_sec))
	beat_sec = float(input.get("beat_sec", beat_sec))
	peak_at = float(input.get("peak_at", peak_at))
	perfect_sec = float(input.get("perfect_sec", perfect_sec))
	good_sec = float(input.get("good_sec", good_sec))


## The grade for a press `offset_sec` away from the peak (either side).
static func grade_for(offset_sec: float, perfect: float, good: float) -> StringName:
	var d := absf(offset_sec)
	if d <= perfect:
		return GRADE_PERFECT
	if d <= good:
		return GRADE_GOOD
	return GRADE_MISS


func beat_start(i: int) -> float:
	return lead_in_sec + i * beat_sec


func peak_time(i: int) -> float:
	return beat_start(i) + peak_at * beat_sec


## The beat waiting for a press (== grades.size()); beats once done.
func current_beat() -> int:
	return mini(grades.size(), beats)


## Seconds from now to the current beat's peak (negative once it has passed).
func time_to_peak() -> float:
	return peak_time(current_beat()) - elapsed


## Total length if every beat runs out (the longest the input can take).
func duration_sec() -> float:
	return beat_start(beats)


func is_done() -> bool:
	return cancelled or grades.size() >= beats


## Moves time on by `delta` seconds; every beat that ends unpressed becomes a miss.
func advance(delta: float) -> void:
	if is_done():
		return
	elapsed += maxf(delta, 0.0)
	while not is_done() and elapsed >= beat_start(grades.size() + 1):
		grades.append(GRADE_MISS)


## Presses now: grades the current beat and returns its grade, or &"" when the press is ignored
## (done, or the beat has not opened yet).
func press() -> StringName:
	if is_done() or elapsed < beat_start(current_beat()):
		return &""
	var grade := grade_for(elapsed - peak_time(current_beat()), perfect_sec, good_sec)
	grades.append(grade)
	return grade


## Backs out before the first grade. False (and nothing changes) once a beat is graded.
func cancel() -> bool:
	if is_done() or not grades.is_empty():
		return false
	cancelled = true
	return true


## {cancelled, grades} for BattleSwell.perform().
func result() -> Dictionary:
	return {BattleSwell.RESULT_CANCELLED: cancelled, BattleSwell.RESULT_GRADES: grades.duplicate()}
