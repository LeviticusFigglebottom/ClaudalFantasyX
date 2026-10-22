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
	return s


## Sets the reveal speed, clamped to the data file's allowed range.
func set_chars_per_sec(value: float) -> void:
	chars_per_sec = clampf(value, min_chars_per_sec, max_chars_per_sec)
