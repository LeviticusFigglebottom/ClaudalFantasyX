class_name DialogueTextSettings
extends RefCounted
## Text-box tuning. Defaults come from game/data/dialogue/text_box.json; the settings menu
## (UI, later) overwrites chars_per_sec through set_chars_per_sec().

const DATA_PATH := "res://game/data/dialogue/text_box.json"

var chars_per_sec: float = 0.0
var min_chars_per_sec: float = 0.0
var max_chars_per_sec: float = 0.0
## One blip every N revealed non-space characters.
var blip_every_n_chars: int = 1
var blip_volume_db: float = 0.0
var narration_blip: bool = false
## Characters that open the mouth (mouth_flap signal).
var flap_vowels: String = ""
## Reveal pauses (M2-UI-27): seconds the reveal lingers after a punctuation mark, at
## pause_reference_cps; a faster text speed shortens them in proportion (time_scale_for).
var pauses: Dictionary = {}
var pause_reference_cps: float = 0.0
## Characters that may sit between a mark and its pause (a closing quote or bracket).
var pause_closers: String = ""


static func load_default() -> DialogueTextSettings:
	var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(DATA_PATH))
	if typeof(parsed) != TYPE_DICTIONARY or typeof((parsed as Dictionary).get("text_box")) != TYPE_DICTIONARY:
		push_error("DialogueTextSettings: could not read 'text_box' from %s" % DATA_PATH)
		return DialogueTextSettings.new()
	return from_dict((parsed as Dictionary)["text_box"] as Dictionary)


static func from_dict(d: Dictionary) -> DialogueTextSettings:
	var s := DialogueTextSettings.new()
	s.min_chars_per_sec = float(d.get("min_chars_per_sec", s.min_chars_per_sec))
	s.max_chars_per_sec = float(d.get("max_chars_per_sec", s.max_chars_per_sec))
	s.chars_per_sec = float(d.get("chars_per_sec", s.chars_per_sec))
	s.blip_every_n_chars = maxi(1, int(d.get("blip_every_n_chars", s.blip_every_n_chars)))
	s.blip_volume_db = float(d.get("blip_volume_db", s.blip_volume_db))
	s.narration_blip = bool(d.get("narration_blip", s.narration_blip))
	s.flap_vowels = str(d.get("flap_vowels", s.flap_vowels))
	s.pauses = (d.get("pauses", {}) as Dictionary).duplicate()
	s.pause_reference_cps = float(d.get("pause_reference_cps", s.pause_reference_cps))
	s.pause_closers = str(d.get("pause_closers", s.pause_closers))
	return s


## Seconds the reveal lingers after character `i` of `text` (0 when none). A mark pauses only
## where a sentence would breathe: followed by whitespace (after any closers), never at the end of
## the line and never inside a run of marks ("...", "?!": only the last one pauses).
func pause_after(text: String, i: int) -> float:
	if i < 0 or i >= text.length() - 1 or not pauses.has(text[i]):
		return 0.0
	var j := i + 1
	while j < text.length() and pause_closers.contains(text[j]):
		j += 1
	if j >= text.length() or not text[j].strip_edges().is_empty():
		return 0.0
	var k := float(pauses[text[i]])
	if pause_reference_cps > 0.0 and chars_per_sec > 0.0:
		k *= pause_reference_cps / chars_per_sec
	return k


## The time (seconds from the line's start) at which each character of `text` becomes visible,
## pauses included; empty when the reveal is instant (chars_per_sec 0).
func reveal_times(text: String) -> PackedFloat64Array:
	var out := PackedFloat64Array()
	if chars_per_sec <= 0.0:
		return out
	var paused := 0.0
	for i in text.length():
		out.append(float(i + 1) / chars_per_sec + paused)  # exact per index: no drift over a line
		paused += pause_after(text, i)
	return out


## Sets the reveal speed, clamped to the data file's allowed range.
func set_chars_per_sec(value: float) -> void:
	chars_per_sec = clampf(value, min_chars_per_sec, max_chars_per_sec)
