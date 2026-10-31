class_name LedgerReader
extends Control
## The ledger on screen (M5-A3P-1706; act3_ch17 B05 "The ledger": held page-turns, a blank-page end). attach() to the
## scene's CutsceneSequencer: each #narration entry whose line id starts with `line_prefix` is written on the open page
## (it still captions below, so the words are never only on the page), and each held gate opened with `turn_prompt`
## turns the page when the scene reaches its end (hold_input_end): the written page slides away and the next comes up
## blank. Past the ledger's last entry nothing more is written, so the turns land on blank pages. The page fades in
## at its first entry or turn and out when the scene ends. It takes no input: the hold is CutsceneHoldGate's.
## Layout and the hooks: game/data/ui/ledger_reader.json.

## A page turned (the count so far).
signal page_turned(count: int)

const DATA_PATH := "res://game/data/ui/ledger_reader.json"
const EVENT_BEGIN := CutsceneHoldGate.EVENT_BEGIN
const EVENT_END := CutsceneHoldGate.EVENT_END

var model := LedgerReaderModel.new()
var data: Dictionary = {}
var sequencer: CutsceneSequencer

var _page: Control
var _entries: Control
var _turning := false
var _tween: Tween


## A reader on its own canvas layer under `host`, attached to `seq`.
static func mount(host: Node, seq: CutsceneSequencer) -> LedgerReader:
	var cfg := load_data()
	var layer := CanvasLayer.new()
	layer.layer = int(cfg.get("canvas_layer", 1))
	host.add_child(layer)
	var reader := LedgerReader.new()
	reader.data = cfg
	layer.add_child(reader)
	reader.attach(seq)
	return reader


static func load_data() -> Dictionary:
	var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(DATA_PATH))
	if not parsed is Dictionary or not (parsed as Dictionary).get("ledger_reader") is Dictionary:
		push_error("LedgerReader: could not read 'ledger_reader' from %s" % DATA_PATH)
		return {}
	return (parsed as Dictionary)["ledger_reader"] as Dictionary


func _ready() -> void:
	if data.is_empty():
		data = load_data()
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	UiSettings.shared().follow(self)
	_build()
	UiFrame.centre(self)
	modulate.a = 0.0


## Listens to `seq`: its lines (the entries) and its hold gates (the turns); it fades out when the scene ends.
func attach(seq: CutsceneSequencer) -> void:
	sequencer = seq
	seq.line_shown.connect(on_line)
	seq.event_requested.connect(on_event)
	seq.finished.connect(func(_id: StringName) -> void: close())


## A line the scene shows: an entry of the ledger is written on the open page.
func on_line(step: DialogueStep) -> void:
	if not String(step.line_id).begins_with(str(data.get("line_prefix", ""))) or str(data.get("line_prefix", "")) == "":
		return
	model.write(String(step.text_key))
	_show()
	_add_entry(String(step.text_key))


## A scene event: a turn gate opening, and its end, which turns the page.
func on_event(event_name: StringName, args: Array) -> void:
	if event_name == EVENT_BEGIN:
		_turning = not args.is_empty() and str(args[0]) == str(data.get("turn_prompt", ""))
		if _turning:
			_show()
	elif event_name == EVENT_END and _turning:
		_turning = false
		turn()


## Turns the page: the written one slides away, and the next comes up blank.
func turn() -> void:
	model.turn()
	var old := _entries
	_entries = _new_entries()
	page_turned.emit(model.turned())
	if UiSettings.shared().reduced_motion() or not is_inside_tree():
		old.queue_free()
		return
	var t := create_tween().set_parallel()
	t.tween_property(
		old, "position:x", old.position.x - HudLayout.num(data, "turn_px"), HudLayout.num(data, "turn_sec")
	)
	t.tween_property(old, "modulate:a", 0.0, HudLayout.num(data, "turn_sec"))
	t.chain().tween_callback(old.queue_free)


## Fades the page out and frees it (the scene has ended).
func close() -> void:
	var layer := get_parent() if get_parent() is CanvasLayer else self
	if not is_inside_tree() or UiSettings.shared().reduced_motion():
		layer.queue_free()
		return
	_fade(0.0).tween_callback(layer.queue_free)


## The entries written on the open page, as shown (tests and shots).
func shown_text() -> PackedStringArray:
	var out: PackedStringArray = []
	for c in _entries.get_children():
		out.append((c as Label).text)
	return out


func _show() -> void:
	if modulate.a < 1.0 and (_tween == null or not _tween.is_running()):
		if UiSettings.shared().reduced_motion() or not is_inside_tree():
			modulate.a = 1.0
		else:
			_fade(1.0)


func _fade(to: float) -> Tween:
	if _tween != null:
		_tween.kill()
	_tween = create_tween()
	_tween.tween_property(self, "modulate:a", to, HudLayout.num(data, "fade_sec"))
	return _tween


func _add_entry(key: String) -> void:
	var pm := data.get("page", {}) as Dictionary
	var w := HudLayout.rect_of(pm).size.x - HudLayout.num(pm, "pad") * 2.0
	var y := 0.0
	for c in _entries.get_children():
		y = maxf(y, (c as Control).position.y + (c as Control).size.y + HudLayout.num(data, "line_gap"))
	var l := Label.new()
	l.theme_type_variation = StringName(str(data.get("entry_variation", "BodyLabel")))
	l.text = tr(key)
	l.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	l.mouse_filter = Control.MOUSE_FILTER_IGNORE
	l.position = Vector2(0.0, y)
	l.size = Vector2(w, 0.0)
	_entries.add_child(l)
	l.size.y = HudLayout.lines_height(l)


func _new_entries() -> Control:
	var pm := data.get("page", {}) as Dictionary
	var pad := HudLayout.num(pm, "pad")
	var c := Control.new()
	c.mouse_filter = Control.MOUSE_FILTER_IGNORE
	c.position = Vector2(pad, pad + HudLayout.num(pm, "title_height") + HudLayout.num(pm, "rule_gap"))
	_page.add_child(c)
	return c


func _build() -> void:
	var pm := data.get("page", {}) as Dictionary
	var panel := Panel.new()
	HudLayout.place(panel, pm)
	panel.mouse_filter = Control.MOUSE_FILTER_IGNORE
	panel.clip_contents = true  # a turning page slides out of it, not across the screen
	add_child(panel)
	_page = panel
	var pad := HudLayout.num(pm, "pad")
	var r := HudLayout.rect_of(pm)
	var title := Label.new()
	title.theme_type_variation = &"HeaderLabel"
	title.text = tr(str(data.get("title_key", "")))
	title.position = Vector2(pad, pad)
	title.size = Vector2(r.size.x - pad * 2.0, HudLayout.num(pm, "title_height"))
	title.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	title.mouse_filter = Control.MOUSE_FILTER_IGNORE
	panel.add_child(title)
	var rule := ColorRect.new()
	rule.color = get_theme_color(&"line_gold", HymnThemeBuilder.PALETTE_TYPE)
	rule.position = Vector2(pad, pad + title.size.y)
	rule.size = Vector2(r.size.x - pad * 2.0, 2.0)
	rule.mouse_filter = Control.MOUSE_FILTER_IGNORE
	panel.add_child(rule)
	_entries = _new_entries()
