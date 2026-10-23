class_name SwellGlyph
extends SwellInput
## Ysolde's Swell input, the glyph trace (her character sheet; formulas.md § Swell). A Lamptongue
## glyph is shown whole on her folding book as a short run of strokes; the player traces it with
## the direction buttons, in order, before the window closes. There is no beat: the input asks
## for the right strokes, and a little speed. Node-free like every SwellInput.
##
## - Each stroke is graded as it is made: `traced` for the stroke the glyph asks for next, a miss
##   for any other direction. A stroke is never retried; the trace moves on.
## - After the last stroke, a glyph traced without a miss within swift_sec of the lead-in's end
##   earns `swift`; otherwise that last grade is a miss.
## - When window_sec runs out, every stroke left and the swift grade are misses.
## - Strokes before the lead-in ends, and the accept button, are ignored.

const GRADE_TRACED := &"traced"
const GRADE_SWIFT := &"swift"

## One direction per stroke, in order.
var strokes: Array[StringName] = []
## Seconds after the lead-in before the trace runs out.
var window_sec := 0.0
## Seconds after the lead-in within which a clean trace earns `swift`.
var swift_sec := 0.0


## `input` is a swell.json "inputs" row of kind glyph: strokes [direction], window_sec, swift_sec.
func _init(input: Dictionary = {}) -> void:
	super(input)
	kind = SwellInput.KIND_GLYPH
	strokes = _strings(input.get("strokes", []))
	window_sec = float(input.get("window_sec", window_sec))
	swift_sec = float(input.get("swift_sec", swift_sec))


func buttons_used() -> Array[StringName]:
	return DIRECTIONS


## One grade per stroke, then the swift grade.
func grade_count() -> int:
	return strokes.size() + 1


func scripted_grades(quality: StringName) -> Array[StringName]:
	var out: Array[StringName] = []
	for i in strokes.size():
		out.append(GRADE_MISS if quality == QUALITY_MISS else GRADE_TRACED)
	out.append(GRADE_SWIFT if quality == QUALITY_PERFECT else GRADE_MISS)
	return out


## The stroke waiting to be traced (== grades.size()); strokes.size() once every stroke is made.
func current_stroke() -> int:
	return mini(grades.size(), strokes.size())


## The direction the glyph asks for next (&"" once every stroke is made).
func expected_button() -> StringName:
	return &"" if current_stroke() >= strokes.size() or is_done() else strokes[current_stroke()]


## Seconds left to earn `swift` (negative once it can no longer be earned on time).
func time_to_peak() -> float:
	return lead_in_sec + swift_sec - elapsed


func duration_sec() -> float:
	return lead_in_sec + window_sec


## When the window closes, every stroke left and the swift grade are misses.
func _on_time() -> void:
	if elapsed > lead_in_sec + window_sec:
		while not is_done():
			grades.append(GRADE_MISS)


func press(button: StringName = BUTTON_ACCEPT) -> StringName:
	if is_done() or not DIRECTIONS.has(button) or elapsed < lead_in_sec:
		return &""
	var i := current_stroke()
	var grade := GRADE_TRACED if button == strokes[i] else GRADE_MISS
	grades.append(grade)
	if i == strokes.size() - 1:
		var clean := not grades.has(GRADE_MISS)
		grades.append(GRADE_SWIFT if clean and elapsed - lead_in_sec <= swift_sec else GRADE_MISS)
	return grade
