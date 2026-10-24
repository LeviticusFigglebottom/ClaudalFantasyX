class_name MenuMotion
extends RefCounted
## A full-screen menu's open and close transitions (M2-MNU-303; docs/kb/tech/ui.md § Menu motion): the
## field menu and every FieldSubmenu page fade in while rising game/data/ui/menu_motion.json's slide_px
## into place, and fade out while sinking when they close. Durations live in that file.
##
## The root is a menu UiFrame.centre() has made the reference frame; its covers (scrim, caustic
## backdrop, the click catcher) are re-stretched over the whole screen on every step, so only the
## content moves. Over the open world the covers fade with the page; with `static_backdrop` (a page over
## another menu, whose backdrop is the same) they stay at full strength and only the content fades.
##
## Nothing is written until the tween's first step: a test that runs no frames sees the page at rest
## from the start, and finish() drives a running transition to its end. Reduced motion (UiSettings), a
## root outside the tree or a duration of 0 make both transitions instant. Captures settle 30 frames at
## a fixed 60 fps, longer than any duration here, so they always grab the page at rest.

## Emitted when the open (or return) transition has come to rest, and at once when it is instant.
signal settled
## Emitted when the close transition has finished, and at once when it is instant.
signal gone

const DATA_PATH := "res://game/data/ui/menu_motion.json"
const SECTION := "menu_motion"

var root: Control
## 0 = gone, 1 = at rest. The value last written to the root.
var progress := 1.0

var _d: Dictionary = {}
var _tween: Tween
var _dur := 0.0
var _static := false
var _rest_top := 0.0
var _rest_bottom := 0.0
## Instance id -> the alpha a child had at rest (a static backdrop fades each content child).
var _rest_alpha: Dictionary = {}
var _measured := false


func _init(for_root: Control) -> void:
	root = for_root
	_d = load_data()


static func load_data() -> Dictionary:
	var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(DATA_PATH))
	if typeof(parsed) != TYPE_DICTIONARY or typeof((parsed as Dictionary).get(SECTION)) != TYPE_DICTIONARY:
		push_error("MenuMotion: could not read '%s' from %s" % [SECTION, DATA_PATH])
		return {}
	return (parsed as Dictionary)[SECTION] as Dictionary


## Keeps every MenuPage under `root` on the shared Reduced motion setting while `root` is in the tree,
## so a choice made in Settings over an open menu reaches its cursors at once (cursor easing).
static func follow_reduced_motion(root: Control) -> void:
	var settings := UiSettings.shared()
	var on_change := func(key: StringName) -> void:
		if key != UiSettings.REDUCED_MOTION or not is_instance_valid(root):
			return
		for n in root.find_children("*", "", true, false):
			if n is MenuPage:
				(n as MenuPage).reduced_motion = settings.reduced_motion()
	settings.changed.connect(on_change)
	var stop := func() -> void:
		if settings.changed.is_connected(on_change):
			settings.changed.disconnect(on_change)
	root.tree_exited.connect(stop, CONNECT_ONE_SHOT)


## A duration from menu_motion.json (open_sec, close_sec, return_sec).
func seconds(key: String) -> float:
	return float(_d.get(key, 0.0))


## True when the transitions jump straight to their end (Reduced motion, or nothing to animate on).
func is_instant(key: String = "open_sec") -> bool:
	return (
		UiSettings.shared().reduced_motion()
		or not is_instance_valid(root)
		or not root.is_inside_tree()
		or seconds(key) <= 0.0
	)


## True while a transition is running.
func is_moving() -> bool:
	return _tween != null and _tween.is_valid() and _tween.is_running()


## Fades and slides the root in over `key`'s duration (open_sec; return_sec when the field menu comes
## back from a page). `static_backdrop`: the covers stay put at full strength.
func play_in(static_backdrop: bool = false, key: String = "open_sec") -> void:
	_stop()
	if is_instant(key):
		_rest()
		settled.emit()
		return
	_begin(static_backdrop)
	_dur = seconds(key)
	_tween = root.create_tween()
	_tween.tween_method(_apply, 0.0, 1.0, _dur).set_trans(Tween.TRANS_CUBIC).set_ease(Tween.EASE_OUT)
	_tween.finished.connect(_on_in_done)


## Fades and sinks the root out (close_sec, shortened when it was still coming in), then hides it and
## emits `gone`. A static backdrop is hidden at once: the menu under it shows its own.
func play_out(static_backdrop: bool = false) -> void:
	var from := progress
	_stop()
	# A closing menu never takes the pointer again, though it is still drawn while it fades (M2-UI-26).
	root.propagate_call(&"set_mouse_filter", [Control.MOUSE_FILTER_IGNORE])
	if is_instant("close_sec"):
		_rest()
		root.visible = false
		gone.emit()
		return
	_begin(static_backdrop)
	if static_backdrop:
		for c in _covers():
			c.visible = false
	_dur = seconds("close_sec") * from
	_tween = root.create_tween()
	_tween.tween_method(_apply, from, 0.0, _dur).set_trans(Tween.TRANS_CUBIC).set_ease(Tween.EASE_IN)
	_tween.finished.connect(_on_out_done)


## Drives a running transition to its end now (tests; a page that must be at rest at once).
func finish() -> void:
	advance(_dur)


## Steps a running transition by `sec` (tests: a frame's worth shows it mid-way).
func advance(sec: float) -> void:
	if is_moving():
		_tween.custom_step(sec)


## Writes progress `t` (0 = gone, 1 = at rest): the alpha, then the slide (covers re-stretched).
func _apply(t: float) -> void:
	if not is_instance_valid(root):
		return
	progress = t
	if _static:
		var covers := _covers()
		for c in root.get_children():
			var ci := c as CanvasItem
			if ci != null and not covers.has(ci):
				ci.modulate.a = float(_rest_alpha.get(ci.get_instance_id(), 1.0)) * t
	else:
		root.modulate.a = t
	var dy := float(_d.get("slide_px", 0.0)) * (1.0 - t)
	root.offset_top = _rest_top + dy
	root.offset_bottom = _rest_bottom + dy
	UiFrame.fit(root)


func _begin(static_backdrop: bool) -> void:
	_static = static_backdrop
	if not _measured:
		_rest_top = root.offset_top
		_rest_bottom = root.offset_bottom
		_measured = true
	_rest_alpha.clear()
	if _static:
		for c in root.get_children():
			if c is CanvasItem:
				_rest_alpha[c.get_instance_id()] = (c as CanvasItem).modulate.a


## Puts everything back at rest (exactly the offsets and alphas it started from).
func _rest() -> void:
	if not is_instance_valid(root):
		return
	if _measured:
		_apply(1.0)
	progress = 1.0
	if not _static:
		root.modulate.a = 1.0


## Stops a running transition, putting the alphas back at rest (the next one starts from `progress`).
func _stop() -> void:
	if _tween != null and _tween.is_valid():
		_tween.kill()
	_tween = null
	if not is_instance_valid(root):
		return
	if _static:
		for c in root.get_children():
			var ci := c as CanvasItem
			if ci != null and _rest_alpha.has(ci.get_instance_id()):
				ci.modulate.a = float(_rest_alpha[ci.get_instance_id()])
	else:
		root.modulate.a = 1.0


func _on_in_done() -> void:
	_rest()
	settled.emit()


func _on_out_done() -> void:
	if is_instance_valid(root):
		root.visible = false
	gone.emit()


func _covers() -> Array[CanvasItem]:
	var out: Array[CanvasItem] = []
	for v: Variant in root.get_meta(UiFrame.META_COVERS, []) as Array:
		if is_instance_valid(v) and v is CanvasItem:
			out.append(v as CanvasItem)
	return out
