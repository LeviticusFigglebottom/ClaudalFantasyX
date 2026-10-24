class_name SwellBrace
extends SwellInput
## Toma's Swell input, the hold-and-release brace (his character sheet; formulas.md § Swell). The
## blows of the technique's wind-up land at fixed times; the player holds the accept button
## through them and lets go on the counter. Node-free like every SwellInput.
##
## - Each blow is graded when it lands: `braced` while the button is held, a miss when it is not.
## - Letting go ends the brace: blows still to come are misses, and the release is graded by its
##   distance from the counter (perfect, good or miss). No release by the end of the counter's
##   window is a miss.
## - A release during the lead-in only lets go (nothing is graded), so the tap that chose the
##   technique cannot spoil the brace; pressing again holds again (M2-UI-03).
## - Holding again after a graded release does nothing; other buttons are ignored.

const GRADE_BRACED := &"braced"

## Each blow's time after the lead-in, in seconds (ascending).
var impacts_at: Array[float] = []
## The counter's time after the lead-in (after the last blow).
var counter_at := 0.0
var perfect_sec := 0.0
var good_sec := 0.0
var holding := false


## `input` is a swell.json "inputs" row of kind brace: impacts [sec], counter_at, perfect_sec,
## good_sec.
func _init(input: Dictionary = {}) -> void:
	super(input)
	kind = SwellInput.KIND_BRACE
	impacts_at = _floats(input.get("impacts", []))
	counter_at = float(input.get("counter_at", counter_at))
	perfect_sec = float(input.get("perfect_sec", perfect_sec))
	good_sec = float(input.get("good_sec", good_sec))


## One grade per blow, then the release.
func grade_count() -> int:
	return impacts_at.size() + 1


func scripted_grades(quality: StringName) -> Array[StringName]:
	var out: Array[StringName] = []
	for i in impacts_at.size():
		out.append(GRADE_MISS if quality == QUALITY_MISS else GRADE_BRACED)
	out.append(quality)
	return out


func impact_time(i: int) -> float:
	return lead_in_sec + impacts_at[i]


func counter_time() -> float:
	return lead_in_sec + counter_at


## How many blows are still to land.
func blows_left() -> int:
	return maxi(impacts_at.size() - grades.size(), 0)


## Seconds to the next blow, or to the counter once every blow has landed.
func time_to_peak() -> float:
	if blows_left() > 0:
		return impact_time(grades.size()) - elapsed
	return counter_time() - elapsed


func duration_sec() -> float:
	return counter_time() + good_sec


## Grades each blow as it lands, and a release that never came once the counter has passed.
func _on_time() -> void:
	while blows_left() > 0 and elapsed >= impact_time(grades.size()):
		_record(GRADE_BRACED if holding else GRADE_MISS)
	if not is_done() and blows_left() == 0 and elapsed > counter_time() + good_sec:
		_record(GRADE_MISS)


## Starts the hold. Earns no grade itself.
func press(button: StringName = BUTTON_ACCEPT) -> StringName:
	if button == BUTTON_ACCEPT and not is_done():
		holding = true
	return &""


## Lets go: every blow still to come is a miss, and the release is graded against the counter.
## During the lead-in it only lets go.
func release(button: StringName = BUTTON_ACCEPT) -> StringName:
	if button != BUTTON_ACCEPT or is_done() or not holding:
		return &""
	holding = false
	if elapsed < lead_in_sec:
		return &""
	while blows_left() > 0:
		_record(GRADE_MISS)
	var grade := grade_for(elapsed - counter_time(), perfect_sec, good_sec)
	_record(grade)
	return grades[-1]
