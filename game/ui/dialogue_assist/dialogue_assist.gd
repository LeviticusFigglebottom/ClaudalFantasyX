class_name DialogueAssist
extends Control
## Reading aids on the dialogue box (M2-UI-25, intro audit 5), UI-owned and attached to every
## DialogueBox by one line in its _ready (DialogueAssist.attach(self)); it never restyles the box.
##   - The continue glyph: a small gold chevron under a lamp diamond at the bottom right of the
##     box's panel, shown while a fully revealed line waits for Confirm. It bobs gently (its phase
##     from accumulated delta, so --fixed-fps captures hold; reduced motion: still).
##   - The backlog: each fully revealed line goes into the session's DialogueBacklog; the
##     remappable `dialogue_backlog` action (L, pad Y) opens DialogueBacklogPage while the box is up.
##   - Auto-advance: with the Accessibility setting `dialogue_auto` On, a waiting line advances by
##     itself after a hold that grows with its length, by emitting the box's advance_requested.
##     Never while choices are up, the backlog is open or the tree is paused; never an empty line.
## Layout and timing: game/data/ui/dialogue_assist.json.

const DATA_PATH := "res://game/data/ui/dialogue_assist.json"
const ACTION := &"dialogue_backlog"
## The box's panel, whose bottom-right corner the glyph sits in (the whole box when missing).
const PANEL_PATH := ^"Panel"

var box: DialogueBox
var backlog: DialogueBacklog
## The open backlog page (null when closed).
var page: DialogueBacklogPage
## Whether an opened backlog pauses the tree (captures turn it off).
var pause_backlog := true

var _d: Dictionary = {}
var _glyph: Control
var _waiting := false
var _hold := 0.0
var _hold_need := 0.0
var _bob_t := 0.0


## Adds the assist under `b` (the box's _ready calls it), and returns it.
static func attach(b: DialogueBox) -> DialogueAssist:
	ensure_action()
	var a := DialogueAssist.new()
	a.box = b
	b.add_child(a)
	return a


## Adds `dialogue_backlog` to the InputMap when it is missing (also called before the Controls page
## captures its defaults, so the action is remappable).
static func ensure_action() -> void:
	var d := load_data()
	FieldInput.add_actions(d.get("action", {}) as Dictionary, float(d.get("deadzone", 0.0)))


static func load_data() -> Dictionary:
	var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(DATA_PATH))
	if typeof(parsed) != TYPE_DICTIONARY or typeof((parsed as Dictionary).get("dialogue_assist")) != TYPE_DICTIONARY:
		push_error("DialogueAssist: could not read 'dialogue_assist' from %s" % DATA_PATH)
		return {}
	return (parsed as Dictionary)["dialogue_assist"] as Dictionary


func _ready() -> void:
	name = &"DialogueAssist"
	_d = load_data()
	if box == null:
		box = get_parent() as DialogueBox
	if backlog == null:
		backlog = DialogueBacklog.shared()
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	UiSettings.shared().follow(self)
	_glyph = Control.new()
	_glyph.name = &"ContinueGlyph"
	_glyph.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_glyph.draw.connect(_draw_glyph)
	_glyph.visible = false
	add_child(_glyph)
	if box != null:
		box.reveal_finished.connect(_on_reveal_finished)
		box.advance_requested.connect(_on_advance_requested)


func _exit_tree() -> void:
	if backlog_open():
		page.close()


func _process(delta: float) -> void:
	step(delta)


func _unhandled_input(event: InputEvent) -> void:
	if event.is_action_pressed(ACTION) and can_open_backlog():
		open_backlog()
		get_viewport().set_input_as_handled()


## Steps the glyph and the auto-advance hold by `delta` seconds (from _process; tests call it).
func step(delta: float) -> void:
	if box == null:
		return
	if _waiting and box.is_revealing():
		_waiting = false  # a new line started
	var shown := glyph_shown()
	_glyph.visible = shown
	if shown:
		var period := _num(_glyph_data(), "bob_sec")
		_bob_t = fmod(_bob_t + delta, period) if period > 0.0 else 0.0
		_place_glyph()
	if not auto_ready():
		return
	_hold += delta
	if _hold >= _hold_need:
		_waiting = false
		box.advance_requested.emit()


## True while a fully revealed line with text is on screen, waiting for Confirm.
func is_waiting() -> bool:
	return _waiting


## True while the continue glyph is up: a line waits, the box is visible and no choice is asked.
func glyph_shown() -> bool:
	return _waiting and box.is_visible_in_tree() and not choices_up()


## The glyph's bob, in pixels down from its rest (0 under reduced motion).
func glyph_bob() -> float:
	var g := _glyph_data()
	var period := _num(g, "bob_sec")
	if UiSettings.shared().reduced_motion() or period <= 0.0:
		return 0.0
	return _num(g, "bob_px") * 0.5 * (1.0 - cos(TAU * _bob_t / period))


func glyph_control() -> Control:
	return _glyph


## True when auto-advance would count down now: the setting is on and a line waits, with no
## choices, no backlog and no pause in the way.
func auto_ready() -> bool:
	if not UiSettings.shared().dialogue_auto_enabled() or not _waiting:
		return false
	if not box.is_visible_in_tree() or choices_up() or backlog_open():
		return false
	return not (is_inside_tree() and get_tree().paused)


## The hold before a line of `chars` characters advances by itself.
func hold_for(chars: int) -> float:
	var a := _d.get("auto", {}) as Dictionary
	return _num(a, "base_sec") + _num(a, "per_char_sec") * float(chars)


## Seconds the waiting line has been held so far.
func held_sec() -> float:
	return _hold


## True while the box's cutscene overlay shows its options.
func choices_up() -> bool:
	if box == null:
		return false
	var overlay := box.get_parent() as CutsceneOverlay
	return overlay != null and overlay.choices != null and overlay.choices.visible


func backlog_open() -> bool:
	return page != null and is_instance_valid(page) and page.is_open()


## The backlog opens only while the box is up and nothing else holds the tree.
func can_open_backlog() -> bool:
	if box == null or not box.is_visible_in_tree() or backlog_open():
		return false
	return not get_tree().paused


## Opens the backlog page over the box (on its own CanvasLayer beside the box).
func open_backlog() -> DialogueBacklogPage:
	page = DialogueBacklogPage.new()
	page.backlog = backlog
	page.pause_tree = pause_backlog
	var host := box.get_parent() if box.get_parent() != null else box
	FieldSubmenu.mount(page, host)
	return page


func _on_reveal_finished() -> void:
	var text := box.shown_text()
	_waiting = false
	if text.strip_edges().is_empty():
		return
	backlog.record(box.speaker_name(), text)
	_waiting = true
	_hold = 0.0
	_hold_need = hold_for(text.length())
	_bob_t = 0.0


func _on_advance_requested() -> void:
	_waiting = false
	_hold = 0.0


## Puts the glyph's box at the panel's bottom-right corner, lowered by the bob.
func _place_glyph() -> void:
	var g := _glyph_data()
	var panel := box.get_node_or_null(PANEL_PATH) as Control
	var r := panel.get_rect() if panel != null else Rect2(Vector2.ZERO, box.size)
	var hw := _num(g, "half_width_px")
	var node := _num(g, "node_px")
	var line := _num(g, "line_px")
	_glyph.size = Vector2(hw * 2.0, node * 2.0 + _num(g, "node_gap_px") + _num(g, "height_px") + line)
	var corner := r.end - Vector2(_num(g, "right_px"), _num(g, "bottom_px"))
	_glyph.position = corner - _glyph.size + Vector2(0.0, glyph_bob())
	_glyph.queue_redraw()


## A gold chevron pointing down, under a small lamp diamond: "more follows".
func _draw_glyph() -> void:
	var g := _glyph_data()
	var hw := _num(g, "half_width_px")
	var node := _num(g, "node_px")
	var line := _num(g, "line_px")
	var top := node * 2.0 + _num(g, "node_gap_px")
	var tip := top + _num(g, "height_px")
	var gold := get_theme_color(&"focus_gold", HymnThemeBuilder.PALETTE_TYPE)
	_glyph.draw_polyline(
		PackedVector2Array([Vector2(line, top), Vector2(hw, tip), Vector2(hw * 2.0 - line, top)]), gold, line, true
	)
	_glyph.draw_colored_polygon(
		SwellRingView.diamond(Vector2(hw, node), node), get_theme_color(&"focus", HymnThemeBuilder.PALETTE_TYPE)
	)


func _glyph_data() -> Dictionary:
	return _d.get("glyph", {}) as Dictionary


func _num(sec: Dictionary, key: String) -> float:
	return HudLayout.num(sec, key)
