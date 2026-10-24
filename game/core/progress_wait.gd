class_name ProgressWait
extends RefCounted
## A wait that gives up on a stall, not on a fixed time (M2-ARC-08).
##
## The boot card and the router's reveal hold wait for the boot warm-up. A first launch (ShaderPrewarm.first_run)
## took 9.5 s on Low on an RX 9070 XT and is slower on a min-spec card, so a fixed 10 s cap would show the title
## mid-warm-up. Instead, step(frame_ms, progress) is fed each frame's wall ms (a FrameClock lap) and the work's
## progress count (any integer that changes whenever the work moves). The wait ends:
##   - STALLED: the progress count has not changed for stall_ms;
##   - CAPPED: max_ms in all, however much progress (a safety cap far above any measured first launch).
## Both values come from game/data/settings/boot_card.json (from_settings). Pure: no nodes, no clock of its own,
## so tests drive it frame by frame.

enum Verdict { WAITING, STALLED, CAPPED }

const SETTINGS_PATH := "res://game/data/settings/boot_card.json"
const LOG_PREFIX := "ProgressWait"

## No progress for this long ends the wait (ms).
var stall_ms: float
## The wait never runs longer than this (ms).
var max_ms: float
## Wall ms waited so far.
var waited_ms := 0.0
## Wall ms since the progress count last changed.
var stalled_ms := 0.0

var _progress := 0


func _init(stall_timeout_ms: float, max_wait_ms: float) -> void:
	stall_ms = stall_timeout_ms
	max_ms = max_wait_ms


## A wait with boot_card.json's stall_timeout_ms and max_wait_ms.
static func from_settings(path: String = SETTINGS_PATH) -> ProgressWait:
	var s := load_settings(path)
	return ProgressWait.new(float(s.get("stall_timeout_ms", 0.0)), float(s.get("max_wait_ms", 0.0)))


## boot_card.json as a Dictionary (empty, with a warning, when it cannot be read).
static func load_settings(path: String = SETTINGS_PATH) -> Dictionary:
	var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(path))
	if typeof(parsed) != TYPE_DICTIONARY:
		push_warning("%s: cannot read %s" % [LOG_PREFIX, path])
		return {}
	return parsed as Dictionary


## Records one frame of `frame_ms` wall ms after which the work's progress count reads `progress`.
func step(frame_ms: float, progress: int) -> Verdict:
	waited_ms += frame_ms
	if progress != _progress:
		_progress = progress
		stalled_ms = 0.0
	else:
		stalled_ms += frame_ms
	if waited_ms >= max_ms:
		return Verdict.CAPPED
	if stalled_ms >= stall_ms:
		return Verdict.STALLED
	return Verdict.WAITING


## The verdict's name for stats and warnings ("waiting", "stalled", "capped").
static func verdict_name(v: Verdict) -> String:
	return String(Verdict.find_key(v)).to_lower()
