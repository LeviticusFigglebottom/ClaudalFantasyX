class_name HudLayout
extends RefCounted
## Battle HUD metrics from game/data/ui/battle_hud.json (docs/kb/art/ui.md §6). Every UI number
## lives there; components read one section each: HudLayout.section(&"timeline").

const DATA_PATH := "res://game/data/ui/battle_hud.json"

static var _cache: Dictionary = {}


static func data() -> Dictionary:
	if _cache.is_empty():
		var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(DATA_PATH))
		if typeof(parsed) != TYPE_DICTIONARY or typeof((parsed as Dictionary).get("battle_hud")) != TYPE_DICTIONARY:
			push_error("HudLayout: could not read 'battle_hud' from %s" % DATA_PATH)
			return {}
		_cache = (parsed as Dictionary)["battle_hud"] as Dictionary
	return _cache


static func section(sname: StringName) -> Dictionary:
	return data().get(String(sname), {}) as Dictionary


static func rect_of(sec: Dictionary) -> Rect2:
	var r: Array = sec.get("rect", [0, 0, 0, 0])
	return Rect2(float(r[0]), float(r[1]), float(r[2]), float(r[3]))


## Places `c` at its section's rect (top-left anchored, 1920x1080 reference coordinates).
static func place(c: Control, sec: Dictionary) -> void:
	var r := rect_of(sec)
	c.set_anchors_preset(Control.PRESET_TOP_LEFT)
	c.position = r.position
	c.size = r.size


static func num(sec: Dictionary, key: String) -> float:
	if not sec.has(key):
		push_error("HudLayout: missing metric '%s'" % key)
		return 0.0
	return float(sec[key])
