class_name SwellInput
extends RefCounted
## One hero's interactive Swell input (SPEC §6.2: unique, short, cancelable; formulas.md § Swell).
## Node-free and deterministic: time moves only through advance(), and the player's buttons arrive
## through press() and release(). The HUD draws an input and BattleController feeds it
## (SwellRingClock, SwellInputKeys); tests and the simulator drive the same calls, or skip the
## input altogether with scripted_result(). result() is what BattleSwell.perform() takes.
##
## Kinds (swell.json "inputs" rows, `kind`), one per hero:
##   timing_ring  SwellTimingRing  Rhen: one press per lamp flare, graded by distance from its peak.
##   chant        SwellChant       Asha: a short phrase of direction buttons, each on its note.
##   brace        SwellBrace       Toma: hold through the blows, release on the counter.
##   glyph        SwellGlyph       Ysolde: trace a glyph's strokes before the window closes.
## Shared rules: one grade per step (grade_count() of them); a step is graded once and cannot be
## retried; the input can be cancelled only before its first grade, so it cannot be restarted until
## it goes well, and a cancel costs nothing.

const BUTTON_ACCEPT := &"accept"
const BUTTON_UP := &"up"
const BUTTON_DOWN := &"down"
const BUTTON_LEFT := &"left"
const BUTTON_RIGHT := &"right"
const DIRECTIONS: Array[StringName] = [BUTTON_UP, BUTTON_DOWN, BUTTON_LEFT, BUTTON_RIGHT]
const KIND_TIMING_RING := &"timing_ring"
const KIND_CHANT := &"chant"
const KIND_BRACE := &"brace"
const KIND_GLYPH := &"glyph"
const KINDS: Array[StringName] = [KIND_TIMING_RING, KIND_CHANT, KIND_BRACE, KIND_GLYPH]
## Fixed outcomes for scripted_result() (the balance simulator; tests).
const QUALITY_MISS := &"miss"
const QUALITY_GOOD := &"good"
const QUALITY_PERFECT := &"perfect"
const QUALITIES: Array[StringName] = [QUALITY_MISS, QUALITY_GOOD, QUALITY_PERFECT]
const GRADE_PERFECT := &"perfect"
const GRADE_GOOD := &"good"
const GRADE_MISS := &"miss"

## The row's kind.
var kind: StringName = &""
## Seconds before the first step can be graded (the input's wind-up).
var lead_in_sec := 0.0
## Largest step one rendered frame may move the input (clamp_step); 0 = no limit. Kept at or under
## the input's tightest window (validate_data), so a hitch can never jump a press across a grade.
var max_step_sec := 0.0
## Seconds since the input opened (advance()).
var elapsed := 0.0
## One grade per finished step, in order.
var grades: Array[StringName] = []
var cancelled := false
## Timing assist (M2-UI-01, an accessibility setting UiSettings applies to the row): a QUALITIES
## id ("good"); a step that would grade a miss records this quality's grade for that step instead
## (scripted_grades), so the floor speaks each kind's own grade names. &"" = no assist.
var assist_floor: StringName = &""
## Misses as played, before the assist (a kind that rewards a clean run reads this, not grades).
var raw_misses := 0


func _init(input: Dictionary = {}) -> void:
	kind = StringName(str(input.get("kind", kind)))
	lead_in_sec = float(input.get("lead_in_sec", lead_in_sec))
	max_step_sec = float(input.get("max_step_sec", max_step_sec))
	assist_floor = StringName(str(input.get("assist_floor", "")))


## The input for swell.json "inputs" row `input`, by its kind; null for an unknown kind.
static func create(input: Dictionary) -> SwellInput:
	match StringName(str(input.get("kind", ""))):
		KIND_TIMING_RING:
			return SwellTimingRing.new(input)
		KIND_CHANT:
			return SwellChant.new(input)
		KIND_BRACE:
			return SwellBrace.new(input)
		KIND_GLYPH:
			return SwellGlyph.new(input)
	return null


## The {cancelled, grades} a player who plays `input` at a fixed `quality` (QUALITIES) would
## produce: every step at that quality, in the kind's own grade names. {} for an unknown kind.
static func scripted_result(input: Dictionary, quality: StringName) -> Dictionary:
	var made := create(input)
	if made == null:
		return {}
	return {BattleSwell.RESULT_CANCELLED: false, BattleSwell.RESULT_GRADES: made.scripted_grades(quality)}


## The grade for a press `offset_sec` away from its mark (either side).
static func grade_for(offset_sec: float, perfect: float, good: float) -> StringName:
	var d := absf(offset_sec)
	if d <= perfect:
		return GRADE_PERFECT
	if d <= good:
		return GRADE_GOOD
	return GRADE_MISS


## How many grades a finished input holds.
func grade_count() -> int:
	return 1


## Override: the buttons this input listens to (the accept button by default). Input events for
## other buttons pass by it (SwellInputKeys), so they keep their usual meaning.
func buttons_used() -> Array[StringName]:
	return [BUTTON_ACCEPT] as Array[StringName]


## Override: the grades of a whole input played at `quality`.
func scripted_grades(quality: StringName) -> Array[StringName]:
	var out: Array[StringName] = []
	for i in grade_count():
		out.append(quality)
	return out


## `delta` limited to max_step_sec (SwellRingClock steps rendered frames through this).
func clamp_step(delta: float) -> float:
	return minf(delta, max_step_sec) if max_step_sec > 0.0 else delta


## Override: seconds from now to the next moment the input grades at its best (negative once it
## has passed). The capture scripts freeze an input relative to it.
func time_to_peak() -> float:
	return 0.0


## Override: the longest the input can take if the player does nothing.
func duration_sec() -> float:
	return lead_in_sec


func is_done() -> bool:
	return cancelled or grades.size() >= grade_count()


## Moves time on by `delta` seconds (negative counts as 0), then lets the kind grade what ran out.
func advance(delta: float) -> void:
	if is_done():
		return
	elapsed += maxf(delta, 0.0)
	_on_time()


## Override: grade every step whose time ran out.
func _on_time() -> void:
	pass


## A button went down now. Returns the grade it earned, or &"" when it earned none (ignored, or it
## only started something, like a hold).
func press(_button: StringName = BUTTON_ACCEPT) -> StringName:
	return &""


## A button came up now. Returns the grade it earned, or &"".
func release(_button: StringName = BUTTON_ACCEPT) -> StringName:
	return &""


## Records the next step's grade. Every kind grades through here, so the timing assist works the
## same for all of them: a miss becomes assist_floor's grade for this step.
func _record(grade: StringName) -> void:
	if grade == GRADE_MISS:
		raw_misses += 1
		if assist_floor != &"":
			grade = scripted_grades(assist_floor)[grades.size()]
	grades.append(grade)


## Backs out before the first grade. False (and nothing changes) once a step is graded.
func cancel() -> bool:
	if is_done() or not grades.is_empty():
		return false
	cancelled = true
	return true


## {cancelled, grades} for BattleSwell.perform().
func result() -> Dictionary:
	return {BattleSwell.RESULT_CANCELLED: cancelled, BattleSwell.RESULT_GRADES: grades.duplicate()}


static func _strings(rows: Variant) -> Array[StringName]:
	var out: Array[StringName] = []
	if typeof(rows) == TYPE_ARRAY:
		for v: Variant in rows as Array:
			out.append(StringName(str(v)))
	return out


static func _floats(rows: Variant) -> Array[float]:
	var out: Array[float] = []
	if typeof(rows) == TYPE_ARRAY:
		for v: Variant in rows as Array:
			out.append(float(v))
	return out
