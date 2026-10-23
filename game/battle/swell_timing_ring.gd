class_name SwellTimingRing
extends SwellInput
## Rhen's Swell input, the lantern-flicker timing ring (SPEC §6.2; formulas.md § Swell). After a
## short lead-in the lamp flares `beats` times on a fixed rhythm, a ring closing on it each time;
## the player presses once per flare, at its brightest. Node-free input logic: the HUD draws it
## (SwellRingView) and tests drive it the same way, through advance(), press() and cancel().
## result() is what BattleSwell.perform() takes. Shared input rules: SwellInput.
##
## - One press per beat. A press before the beat opens is ignored; a press in the beat is graded
##   by its distance from the peak; a beat that ends unpressed is a miss. Mashing cannot help:
##   the first press in a beat is the one that counts. Only the accept button presses the ring.

var beats := 1
var beat_sec := 1.0
## Where the flare peaks inside its beat, as a fraction of beat_sec.
var peak_at := 0.0
## Largest distance from the peak (seconds) for each grade.
var perfect_sec := 0.0
var good_sec := 0.0


## `input` is a swell.json "inputs" row of kind timing_ring.
func _init(input: Dictionary = {}) -> void:
	super(input)
	kind = SwellInput.KIND_TIMING_RING
	beats = maxi(int(input.get("beats", beats)), 1)
	beat_sec = float(input.get("beat_sec", beat_sec))
	peak_at = float(input.get("peak_at", peak_at))
	perfect_sec = float(input.get("perfect_sec", perfect_sec))
	good_sec = float(input.get("good_sec", good_sec))


func grade_count() -> int:
	return beats


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


## Every beat that ends unpressed becomes a miss.
func _on_time() -> void:
	while not is_done() and elapsed >= beat_start(grades.size() + 1):
		grades.append(GRADE_MISS)


## Presses now: grades the current beat and returns its grade, or &"" when the press is ignored
## (done, the beat has not opened yet, or not the accept button).
func press(button: StringName = BUTTON_ACCEPT) -> StringName:
	if button != BUTTON_ACCEPT or is_done() or elapsed < beat_start(current_beat()):
		return &""
	var grade := grade_for(elapsed - peak_time(current_beat()), perfect_sec, good_sec)
	grades.append(grade)
	return grade
