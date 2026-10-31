class_name CreditsRollModel
extends RefCounted
## The closing credits' timing (M5-A3P-1700; act3_ending CR), Node-free. Data: game/data/ui/credits.json. CreditsRoll is
## the view.
##
## Time runs in roll seconds: `lead_in_sec` of black, then the roll climbs from 0 to 1 over `roll_sec`, then it holds
## `end_hold_sec` on the last line and is done. A vignette (`vignettes`: id, `at` as a fraction of the roll, hold_sec)
## stops the roll at its point: the roll fades out over fade_sec, the vignette's `scene` plays for hold_sec (the view
## puts it behind the roll and emits its id), and the roll fades back in. A vignette with no scene yet is passed over.
## Holding Confirm runs the roll `fast_factor` times faster, never through a vignette. Once the credits have been seen
## in full (`seen_before`), holding Cancel for skip_hold_sec ends them.

enum Phase { LEAD_IN, ROLL, VIGNETTE, END_HOLD, DONE }

const DATA_PATH := "res://game/data/ui/credits.json"
const SECTION := "credits"
## The flag set when the credits have run to their end (skip is offered after that).
const SEEN_FLAG := &"credits_seen"

var data: Dictionary = {}
var phase := Phase.LEAD_IN
## How far the roll is, 0..1.
var progress := 0.0
## True when skip is allowed (the credits have been seen in full before).
var seen_before := false
## The vignette playing now ({} when none) and the ones already played, by id.
var vignette: Dictionary = {}
var played: Array[StringName] = []

var _t := 0.0
var _skip_held := 0.0


func _init(config: Dictionary = {}, seen: bool = false) -> void:
	data = config if not config.is_empty() else load_data()
	seen_before = seen


static func load_data() -> Dictionary:
	var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(DATA_PATH))
	if not parsed is Dictionary or not (parsed as Dictionary).get(SECTION) is Dictionary:
		push_error("CreditsRollModel: could not read '%s' from %s" % [SECTION, DATA_PATH])
		return {}
	return (parsed as Dictionary)[SECTION] as Dictionary


## The rows top to bottom: {kind: &"title" | &"line", key, gap_before (px)}.
func rows() -> Array[Dictionary]:
	var col := data.get("column", {}) as Dictionary
	var out: Array[Dictionary] = []
	var first := true
	for s: Variant in data.get("sections", []):
		var sec := s as Dictionary
		var gap := 0.0 if first else float(col.get("section_gap", 0.0))
		out.append({"kind": &"title", "key": str(sec.get("title_key", "")), "gap_before": gap})
		first = false
		for k: Variant in sec.get("lines", []):
			out.append({"kind": &"line", "key": str(k), "gap_before": float(col.get("line_gap", 0.0))})
	return out


## Steps the roll by `delta` real seconds. `fast`: Confirm is held; `skip`: Cancel is held. Returns the vignette id
## that starts in this step (&"" when none).
func advance(delta: float, fast: bool = false, skip: bool = false) -> StringName:
	if phase == Phase.DONE:
		return &""
	_skip_held = _skip_held + delta if skip and seen_before else 0.0
	if _skip_held >= float(data.get("skip_hold_sec", 0.0)) and seen_before and skip:
		phase = Phase.DONE
		return &""
	match phase:
		Phase.LEAD_IN:
			_t += delta
			if _t >= float(data.get("lead_in_sec", 0.0)):
				phase = Phase.ROLL
				_t = 0.0
		Phase.ROLL:
			return _roll(delta * (float(data.get("fast_factor", 1.0)) if fast else 1.0))
		Phase.VIGNETTE:
			_t += delta
			if _t >= vignette_sec():
				phase = Phase.ROLL
				vignette = {}
				_t = 0.0
		Phase.END_HOLD:
			_t += delta
			if _t >= float(data.get("end_hold_sec", 0.0)):
				phase = Phase.DONE
	return &""


## The roll's opacity: faded out across a vignette (fade_sec at each end), else 1 (0 in the lead-in).
func alpha() -> float:
	var fade := maxf(float(data.get("fade_sec", 0.0)), 0.001)
	match phase:
		Phase.LEAD_IN, Phase.DONE:
			return 0.0
		Phase.VIGNETTE:
			var out := clampf(1.0 - _t / fade, 0.0, 1.0)
			var back := clampf((_t - (vignette_sec() - fade)) / fade, 0.0, 1.0)
			return maxf(out, back)
	return 1.0


## The vignettes that will play: those naming the in-engine scene that plays them (a row whose `scene` is empty, or
## not there yet, is passed over, so the roll never stops on black for a vignette that cannot show).
func vignettes() -> Array[Dictionary]:
	var out: Array[Dictionary] = []
	for v: Variant in data.get("vignettes", []):
		var row := v as Dictionary
		var scene := str(row.get("scene", ""))
		if scene != "" and ResourceLoader.exists(scene):
			out.append(row)
	return out


## How long the vignette on show holds the roll (its own hold_sec).
func vignette_sec() -> float:
	return float(vignette.get("hold_sec", 0.0))


func is_done() -> bool:
	return phase == Phase.DONE


## Seconds from the first black to the last line's end at normal speed, vignettes included.
func total_sec() -> float:
	var total := float(data.get("lead_in_sec", 0.0)) + float(data.get("roll_sec", 0.0))
	total += float(data.get("end_hold_sec", 0.0))
	for row in vignettes():
		total += float(row.get("hold_sec", 0.0))
	return total


func _roll(step: float) -> StringName:
	var roll := maxf(float(data.get("roll_sec", 0.0)), 0.001)
	var next := minf(progress + step / roll, 1.0)
	for row in vignettes():
		var id := StringName(str(row.get("id", "")))
		var at := float(row.get("at", 2.0))
		if not played.has(id) and progress < at and next >= at:
			progress = at
			played.append(id)
			vignette = row
			phase = Phase.VIGNETTE
			_t = 0.0
			return id
	progress = next
	if progress >= 1.0:
		phase = Phase.END_HOLD
		_t = 0.0
	return &""
