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


## M2-UI-28 (localisation readiness): makes `l`, a help or hint line sitting at the foot of its
## panel, wrap onto as many lines as its text needs and grow upward from that foot, so a longer
## language or a larger text size never runs it past the panel's side. A line that fits looks as
## it did (same rect, same alignment); only a longer one takes more lines, above, and a shorter
## text after it gives them back (a grown Control never shrinks on its own). Call it after
## placing `l`; returns `l`.
static func wrap_upward(l: Label) -> Label:
	l.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	l.grow_vertical = Control.GROW_DIRECTION_BEGIN
	var h := l.size.y
	var foot := l.position.y + h
	var refit := func() -> void:
		var want := maxf(h, l.get_combined_minimum_size().y)
		if l.size.y != want:
			l.size = Vector2(l.size.x, want)
		if l.position.y != foot - l.size.y:
			l.position.y = foot - l.size.y
	l.minimum_size_changed.connect(refit)
	# A hidden label skips its minimum-size update, so a text set while hidden refits on its draw.
	l.draw.connect(refit, CONNECT_DEFERRED)
	return l
