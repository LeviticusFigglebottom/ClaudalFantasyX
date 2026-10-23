class_name SwellChant
extends SwellInput
## Asha's Swell input, the verse chant (SPEC §6.2 "a button-sequence chant"; formulas.md § Swell).
## A short phrase of notes follows the melody of a verse of the Hush: each note names a direction
## button and falls at its own time, so the phrase has a rhythm rather than a steady beat. The
## player presses each note's button on its note. Node-free like every SwellInput.
##
## - Notes are graded in order. A press before the current note's window opens is ignored; in the
##   window, the right button is graded by its distance from the note and any other button is a
##   miss. A note whose window closes unpressed is a miss. The first press in a window counts, so
##   mashing every button earns misses.
## - The accept button is not a note: it is ignored.

## One direction button per note, in order.
var buttons: Array[StringName] = []
## Each note's time after the lead-in, in seconds (ascending).
var notes_at: Array[float] = []
var perfect_sec := 0.0
var good_sec := 0.0


## `input` is a swell.json "inputs" row of kind chant: notes [{button, at}], perfect_sec, good_sec.
func _init(input: Dictionary = {}) -> void:
	super(input)
	kind = SwellInput.KIND_CHANT
	perfect_sec = float(input.get("perfect_sec", perfect_sec))
	good_sec = float(input.get("good_sec", good_sec))
	for n: Variant in input.get("notes", []):
		var note: Dictionary = n
		buttons.append(StringName(str(note.get("button", ""))))
		notes_at.append(float(note.get("at", 0.0)))


func buttons_used() -> Array[StringName]:
	return DIRECTIONS


func grade_count() -> int:
	return buttons.size()


## The note waiting for a press (== grades.size()); grade_count() once done.
func current_note() -> int:
	return mini(grades.size(), grade_count())


## When note `i` sounds, in seconds since the input opened (past the end: the last note).
func note_time(i: int) -> float:
	var j := mini(i, notes_at.size() - 1)
	return lead_in_sec + (notes_at[j] if j >= 0 else 0.0)


## The button the current note asks for (&"" once done).
func expected_button() -> StringName:
	return &"" if is_done() else buttons[current_note()]


func time_to_peak() -> float:
	return note_time(current_note()) - elapsed


func duration_sec() -> float:
	return note_time(grade_count() - 1) + good_sec if grade_count() > 0 else lead_in_sec


## Every note whose window closed unpressed is a miss.
func _on_time() -> void:
	while not is_done() and elapsed > note_time(current_note()) + good_sec:
		_record(GRADE_MISS)


func press(button: StringName = BUTTON_ACCEPT) -> StringName:
	if is_done() or not DIRECTIONS.has(button):
		return &""
	var i := current_note()
	if elapsed < note_time(i) - good_sec:
		return &""
	var grade := grade_for(elapsed - note_time(i), perfect_sec, good_sec) if button == buttons[i] else GRADE_MISS
	_record(grade)
	return grades[-1]
