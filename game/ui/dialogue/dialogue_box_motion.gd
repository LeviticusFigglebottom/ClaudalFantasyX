class_name DialogueBoxMotion
extends RefCounted
## The dialogue box's transitions (the playtest note "parts look primitive": the box snapped in and out;
## docs/kb/tech/ui.md § Dialogue box motion). When the box is shown its panel fades in while rising
## `rise_px` into place over `open_sec`; dismiss() fades it out while sinking over `close_sec` and then
## hides it; a new speaker's name fades in over `name_sec`. Durations: game/data/ui/menu_motion.json
## "dialogue_box".
##
## As MenuMotion does, nothing is written before a tween's first step, so a test that runs no frames
## sees the box at rest, and finish() drives a running transition to its end. Reduced motion (UiSettings),
## a box outside the tree or a duration of 0 make every transition instant. Every duration ends inside a
## capture's 30 settle frames, so a screenshot grabs the box at rest.

## dismiss() has finished: the box is hidden (at once when it is instant).
signal dismissed

const DATA_PATH := "res://game/data/ui/menu_motion.json"
const SECTION := "dialogue_box"

var box: Control
var panel: Control
var name_label: Control
## 0 = gone, 1 = at rest. The value last written to the panel.
var progress := 1.0

var _d: Dictionary = {}
var _tween: Tween
var _name_tween: Tween
var _dur := 0.0
var _rest_top := 0.0
var _rest_bottom := 0.0
var _measured := false


func _init(for_box: Control, for_panel: Control, for_name: Control) -> void:
	box = for_box
	panel = for_panel
	name_label = for_name
	var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(DATA_PATH))
	if typeof(parsed) == TYPE_DICTIONARY and typeof((parsed as Dictionary).get(SECTION)) == TYPE_DICTIONARY:
		_d = (parsed as Dictionary)[SECTION] as Dictionary
	else:
		push_error("DialogueBoxMotion: could not read '%s' from %s" % [SECTION, DATA_PATH])


## A duration from the data (open_sec, close_sec, name_sec).
func seconds(key: String) -> float:
	return float(_d.get(key, 0.0))


func is_instant(key: String) -> bool:
	return (
		UiSettings.shared().reduced_motion()
		or not is_instance_valid(box)
		or not box.is_inside_tree()
		or seconds(key) <= 0.0
	)


## True while the panel is coming in or going out.
func is_moving() -> bool:
	return _tween != null and _tween.is_valid() and _tween.is_running()


## True while a new speaker's name is fading in.
func is_name_moving() -> bool:
	return _name_tween != null and _name_tween.is_valid() and _name_tween.is_running()


## True while dismiss() is fading the box out.
func is_dismissing() -> bool:
	return is_moving() and _tween.has_meta(&"out")


## The panel fades and rises in (the box has just been shown).
func play_in() -> void:
	_stop()
	if is_instant("open_sec"):
		_apply(1.0)
		return
	_measure()
	_dur = seconds("open_sec")
	_tween = box.create_tween()
	_tween.tween_method(_apply, 0.0, 1.0, _dur).set_trans(Tween.TRANS_CUBIC).set_ease(Tween.EASE_OUT)


## The panel fades and sinks out, then the box hides and `dismissed` fires. Shortened when the panel was
## still coming in.
func play_out() -> void:
	var from := progress
	_stop()
	if is_instant("close_sec"):
		_apply(1.0)
		box.visible = false
		dismissed.emit()
		return
	_measure()
	_dur = seconds("close_sec") * from
	_tween = box.create_tween()
	_tween.set_meta(&"out", true)
	_tween.tween_method(_apply, from, 0.0, _dur).set_trans(Tween.TRANS_CUBIC).set_ease(Tween.EASE_IN)
	_tween.finished.connect(_on_out_done)


## A new speaker: the name fades in.
func play_name() -> void:
	if _name_tween != null and _name_tween.is_valid():
		_name_tween.kill()
	_name_tween = null
	if is_instant("name_sec") or not is_instance_valid(name_label):
		if is_instance_valid(name_label):
			name_label.modulate.a = 1.0
		return
	_name_tween = box.create_tween()
	_name_tween.tween_method(_apply_name, 0.0, 1.0, seconds("name_sec")).set_ease(Tween.EASE_OUT)


## Drives every running transition to its end now (tests).
func finish() -> void:
	if is_moving():
		_tween.custom_step(_dur)
	if _name_tween != null and _name_tween.is_valid() and _name_tween.is_running():
		_name_tween.custom_step(seconds("name_sec"))


## Steps the panel's transition by `sec` (tests).
func advance(sec: float) -> void:
	if is_moving():
		_tween.custom_step(sec)


func _apply(t: float) -> void:
	if not is_instance_valid(panel):
		return
	progress = t
	panel.modulate.a = t
	if _measured:
		var dy := float(_d.get("rise_px", 0.0)) * (1.0 - t)
		panel.offset_top = _rest_top + dy
		panel.offset_bottom = _rest_bottom + dy


func _apply_name(t: float) -> void:
	if is_instance_valid(name_label):
		name_label.modulate.a = t


func _measure() -> void:
	if not _measured:
		_rest_top = panel.offset_top
		_rest_bottom = panel.offset_bottom
		_measured = true


func _stop() -> void:
	if _tween != null and _tween.is_valid():
		_tween.kill()
	_tween = null


func _on_out_done() -> void:
	_apply(1.0)  # at rest for the next show, hidden
	if is_instance_valid(box):
		box.visible = false
	dismissed.emit()
