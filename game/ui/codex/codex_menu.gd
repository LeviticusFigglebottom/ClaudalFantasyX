class_name CodexMenu
extends Control
## The lore codex (M3-UI-03, SPEC §6.11): the categories on the left (each with "3 of 8" found and
## "New" while it holds an unread entry), the chosen category's unlocked entries in the middle
## ("New" on each one not yet opened; locked ones are never listed), and on the right the
## highlighted entry's title and text, or the category's own line while the cursor is on the left.
## Words and unlocks: CodexModel. Layout: game/data/ui/codex_menu.json (1920x1080 reference). It
## follows UiSettings (text size, palette, reduced motion), like the bestiary it is modelled on.
##
## Input (keyboard and controller through ui_*): ui_up / ui_down choose in the column that has the
## cursor; ui_accept or ui_right go from a category into its entries, and from an entry
## whose text is longer than its page into the text (Column.TEXT: ui_up / ui_down scroll it, so a
## pad, which has no Page keys, can read it all); ui_left or ui_cancel come back a column;
## ui_cancel on the categories closes. ui_page_up / ui_page_down scroll the text anywhere. Mouse:
## hover a row to show it (an entry row takes the cursor into the entries), click a category to
## open it, the wheel steps a list or scrolls the text it is over, right click is Cancel (UiInput).
## Opening an entry marks it read (CodexModel.mark_read). Open it with CodexMenu.open_in(host)
## (its own CanvasLayer; it pauses the tree while open) or instance codex_menu.tscn after
## configure(model).

signal closed
## The close transition has finished (at once under Reduced motion): open_in's layer frees itself
## (M2-MNU-305, MenuMotion).
signal gone

enum Column { CATEGORIES, ENTRIES, TEXT }

const SCENE_PATH := "res://game/ui/codex/codex_menu.tscn"
const DATA_PATH := "res://game/data/ui/codex_menu.json"
const SCRIM_SHADER := preload("res://game/ui/shaders/scrim.gdshader")
const CATEGORIES_PAGE := &"codex_categories"
const ENTRIES_PAGE := &"codex_entries"

## Pause the tree while open (the field must not move under a menu).
@export var pause_tree := true
## Opened over the field menu, whose scrim and caustics are the same: the backdrop stays still and
## only the content moves (MenuMotion's static backdrop). Set before it enters the tree.
var over_menu := false

var model: CodexModel
var column := Column.CATEGORIES
## The category on show, and the entry on show (&"" while the cursor is on the categories).
var category: StringName = &""
var current_id: StringName = &""

var _d: Dictionary = {}
var _cats: MenuPage
var _list: MenuPage
var _summary: Label
var _help: Label
var _title: Label
var _sub: Label
var _clip: Control
var _body: Label
var _thumb: ColorRect
var _scroll := 0.0
var _cat_rows: Array[Dictionary] = []
var _entries: Array[Dictionary] = []
var _owns_pause := false
var _is_closed := false
var _motion: MenuMotion
var _reader: DocumentReader


## Instances the menu on its own CanvasLayer under `host` and opens it; the layer frees itself
## when the menu closes. `with_model` defaults to the game's codex (CodexModel.from_game()).
static func open_in(host: Node, with_model: CodexModel = null, over: bool = false) -> CodexMenu:
	var menu := (load(SCENE_PATH) as PackedScene).instantiate() as CodexMenu
	menu.configure(with_model)
	menu.over_menu = over
	var layer := CanvasLayer.new()
	layer.layer = int(load_data().get("canvas_layer", 1))
	layer.process_mode = Node.PROCESS_MODE_ALWAYS
	layer.add_child(menu)
	menu.gone.connect(layer.queue_free)
	host.add_child(layer)
	return menu


static func load_data() -> Dictionary:
	var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(DATA_PATH))
	if typeof(parsed) != TYPE_DICTIONARY or typeof((parsed as Dictionary).get("codex_menu")) != TYPE_DICTIONARY:
		push_error("CodexMenu: could not read 'codex_menu' from %s" % DATA_PATH)
		return {}
	return (parsed as Dictionary)["codex_menu"] as Dictionary


## Sets the model before the menu enters the tree (null = the game's codex).
func configure(with_model: CodexModel = null) -> void:
	model = with_model


func _ready() -> void:
	if model == null:
		model = CodexModel.from_game()
	_d = load_data()
	process_mode = Node.PROCESS_MODE_ALWAYS
	set_anchors_preset(Control.PRESET_FULL_RECT)
	mouse_filter = Control.MOUSE_FILTER_STOP
	UiSettings.shared().follow(self)
	_build()
	UiFrame.centre(self)  # M2-UI-29
	_cats.replace_rows(_category_page_rows())
	_show_category(0)
	if pause_tree and not get_tree().paused:
		get_tree().paused = true
		_owns_pause = true
	MenuMotion.follow_reduced_motion(self)
	_motion = MenuMotion.new(self)
	_motion.gone.connect(gone.emit)
	_motion.play_in(over_menu)


func _exit_tree() -> void:
	_restore_pause()


func is_open() -> bool:
	return not _is_closed


func categories_page() -> MenuPage:
	return _cats


func entries_page() -> MenuPage:
	return _list


func summary_text() -> String:
	return _summary.text


func title_text() -> String:
	return _title.text


func body_text() -> String:
	return _body.text


## The text's scroll offset in pixels, and the most it can scroll (0: it fits).
func scroll_offset() -> float:
	return _scroll


func max_scroll() -> float:
	return maxf(_text_height() - _clip.size.y, 0.0)


## The text area (the wheel over it scrolls; input parity tests hover it).
func text_area() -> Control:
	return _clip


func _unhandled_input(event: InputEvent) -> void:
	if is_open() and handle_input(event):
		get_viewport().set_input_as_handled()


## Applies one input event. Returns true when the menu used it. Tests call this directly.
func handle_input(event: InputEvent) -> bool:
	if not is_open() or reader_open():
		return false
	if event.is_action_pressed(&"ui_up", true):
		_move(-1)
	elif event.is_action_pressed(&"ui_down", true):
		_move(1)
	elif event.is_action_pressed(&"ui_page_up", true):
		scroll_by(-1)
	elif event.is_action_pressed(&"ui_page_down", true):
		scroll_by(1)
	elif event.is_action_pressed(&"ui_accept") or event.is_action_pressed(&"ui_right", true):
		enter()
	elif event.is_action_pressed(&"ui_left", true):
		if column != Column.CATEGORIES:
			back()
	elif event.is_action_pressed(&"ui_cancel"):
		back()
	else:
		return false
	return true


## True while a record is open in the document reader over the codex (it has the input).
func reader_open() -> bool:
	return _reader != null and is_instance_valid(_reader) and _reader.is_open()


## The document reader open over the codex (null when none).
func reader() -> DocumentReader:
	return _reader if reader_open() else null


## One column in: from the categories into the chosen category's entries (nothing when it has none
## found), from a record with a "reader" row into the document reader (M4-A2P-080), or from an entry into its text
## when the text is longer than its page.
func enter() -> void:
	if column == Column.ENTRIES:
		var rid := model.reader_of(current_id)
		var row := DocumentReaderModel.row_of(rid) if rid != &"" else {}
		if not row.is_empty():
			_reader = DocumentReader.open_in(self, DocumentReaderModel.new(row))
		elif max_scroll() > 0.0:
			column = Column.TEXT
			_list.set_dimmed(true)
		return
	if column == Column.TEXT or _entries.is_empty():
		return
	column = Column.ENTRIES
	_cats.set_dimmed(true)
	_list.set_dimmed(false)
	_show_entry(_list.cursor)


## One column back: text to entries, entries to categories; closes from the categories.
func back() -> void:
	if column == Column.CATEGORIES:
		close()
		return
	if column == Column.TEXT:
		column = Column.ENTRIES
		_list.set_dimmed(false)
		return
	column = Column.CATEGORIES
	_cats.set_dimmed(false)
	_list.set_dimmed(true)
	_show_category(_cats.cursor)


## Shows category `index` (the cursor goes to the categories).
func select_category(index: int) -> void:
	while column != Column.CATEGORIES:
		back()
	_cats.set_cursor(index, false)
	_show_category(_cats.cursor)


## Shows entry `index` of the category on show (the cursor goes to the entries).
func select_entry(index: int) -> void:
	if _entries.is_empty():
		return
	_list.set_cursor(index, false)
	if column == Column.TEXT:
		back()
	if column == Column.CATEGORIES:
		enter()
	else:
		_show_entry(_list.cursor)


## Scrolls the text one step down (1) or up (-1), within its length.
func scroll_by(direction: int) -> void:
	_set_scroll(_scroll + direction * HudLayout.num(_d.get("text", {}), "scroll_step_px"))


func close() -> void:
	if _is_closed:
		return
	_is_closed = true
	_restore_pause()
	_fade_out()
	closed.emit()


## The open and close transitions (null before _ready). Tests drive them with motion().finish().
func motion() -> MenuMotion:
	return _motion


## Fades the screen out; `gone` follows (at once without a transition). It never takes the pointer again.
func _fade_out() -> void:
	if _motion != null:
		_motion.play_out(over_menu)
	else:
		visible = false
		gone.emit()


func _move(delta: int) -> void:
	if column == Column.CATEGORIES:
		if _cats.move(delta):
			_show_category(_cats.cursor)
	elif column == Column.TEXT:
		scroll_by(delta)
	elif _list.move(delta):
		_show_entry(_list.cursor)


func _show_category(index: int) -> void:
	_cat_rows = model.categories()
	if _cat_rows.is_empty():
		return
	var cat := _cat_rows[clampi(index, 0, _cat_rows.size() - 1)]
	category = StringName(str(cat["id"]))
	current_id = &""
	_summary.text = model.summary()
	_entries = model.entries_in(category)
	_list.replace_rows(_entry_page_rows())
	_list.set_cursor(0, false)
	_list.set_header(model.entries_header(cat))
	_list.set_dimmed(column == Column.CATEGORIES)
	_title.text = str(cat["name"])
	_sub.text = model.count_text(cat) if not _entries.is_empty() else tr("CODEX_EMPTY_CATEGORY")
	_show_text(model.category_desc(category), &"BodyLabel")


func _show_entry(index: int) -> void:
	if _entries.is_empty():
		return
	var at := clampi(index, 0, _entries.size() - 1)
	current_id = StringName(str(_entries[at]["id"]))
	var record := model.is_record(current_id)
	_title.text = model.title(current_id)
	_sub.text = tr("CODEX_RECORD_TAG") if record else model.category_name(category)
	_show_text(model.body(current_id), &"FlavorLabel" if record else &"BodyLabel")
	if model.mark_read(current_id):  # the New markers go, here and on its category
		_entries = model.entries_in(category)
		_list.replace_rows(_entry_page_rows())
		_list.set_cursor(at, false)
		var cat_at := _cats.cursor
		_cats.replace_rows(_category_page_rows())
		_cats.set_cursor(cat_at, false)
		_summary.text = model.summary()


func _category_page_rows() -> Array[Dictionary]:
	var rows: Array[Dictionary] = []
	for c in model.categories():
		var row := {"id": c["id"], "label": c["name"], "right": model.count_text(c), "enabled": true}
		row["mp"] = tr("CODEX_NEW_TAG") if int(c["new"]) > 0 else ""
		rows.append(row)
	return rows


func _entry_page_rows() -> Array[Dictionary]:
	var rows: Array[Dictionary] = []
	for e in _entries:
		var row := {"id": e["id"], "label": e["title"], "enabled": true}
		row["right"] = "" if bool(e["read"]) else tr("CODEX_NEW_TAG")  # words, not hue alone
		row["right_role"] = &"focus_gold"
		rows.append(row)
	return rows


func _show_text(text: String, variation: StringName) -> void:
	_body.theme_type_variation = variation
	_body.text = text
	_set_scroll(0.0)


func _set_scroll(offset: float) -> void:
	_body.size = Vector2(_clip.size.x, _text_height())
	_scroll = clampf(offset, 0.0, max_scroll())
	_body.position.y = -_scroll
	var span := max_scroll()
	_thumb.visible = span > 0.0
	if span > 0.0:
		var h := _clip.size.y * _clip.size.y / (_clip.size.y + span)
		_thumb.size = Vector2(HudLayout.num(_d.get("text", {}), "thumb_px"), h)
		_thumb.position = Vector2(_clip.size.x - _thumb.size.x, (_clip.size.y - h) * _scroll / span)


## The body's height at the clip's width (its wrapped lines).
func _text_height() -> float:
	_body.size.x = _clip.size.x
	var line := float(_body.get_line_height()) + float(_body.get_theme_constant(&"line_spacing"))
	return _body.get_line_count() * line


func _on_clip_input(event: InputEvent) -> void:
	var mb := event as InputEventMouseButton
	if mb == null or not mb.pressed:
		return
	if mb.button_index == MOUSE_BUTTON_WHEEL_UP or mb.button_index == MOUSE_BUTTON_WHEEL_DOWN:
		scroll_by(-1 if mb.button_index == MOUSE_BUTTON_WHEEL_UP else 1)
		_clip.accept_event()


func _on_category_hovered(index: int) -> void:
	while column != Column.CATEGORIES:
		back()
	_show_category(index)


func _on_entry_hovered(index: int) -> void:
	select_entry(index)


func _restore_pause() -> void:
	if _owns_pause and is_inside_tree():
		get_tree().paused = false
	_owns_pause = false


func _build() -> void:
	var scrim := ColorRect.new()
	scrim.set_anchors_preset(Control.PRESET_FULL_RECT)
	scrim.mouse_filter = Control.MOUSE_FILTER_IGNORE
	var mat := ShaderMaterial.new()
	mat.shader = SCRIM_SHADER
	mat.set_shader_parameter(&"tint", get_theme_color(&"scrim", HymnThemeBuilder.PALETTE_TYPE))
	scrim.material = mat
	add_child(scrim)
	add_child(CausticBackdrop.new())  # ADR 0033
	var pm: Dictionary = _d.get("panel", {})
	var panel := Panel.new()
	HudLayout.place(panel, pm)
	panel.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(panel)
	var pr := HudLayout.rect_of(pm)
	var pad := HudLayout.num(pm, "pad")
	var title_h := HudLayout.num(pm, "title_height")
	var banner := _label(&"BannerLabel", Rect2(pr.position + Vector2(pad, pad), Vector2(pr.size.x * 0.5, title_h)))
	banner.text = tr("CODEX_TITLE")
	var rule := OrnamentRule.new()  # ADR 0033: the gold rule under the title
	var node := float(get_theme_constant(&"ornament_node_px", HymnThemeBuilder.PALETTE_TYPE))
	rule.position = Vector2(banner.position.x, banner.position.y + banner.size.y - node)
	rule.size = Vector2(banner.size.x * 0.6, node * 2.0)
	add_child(rule)
	var right := Rect2(pr.position + Vector2(pr.size.x * 0.5, pad), Vector2(pr.size.x * 0.5 - pad, title_h))
	_summary = _label(&"DimLabel", right)
	_summary.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
	var help_h := HudLayout.num(pm, "help_height")
	var help_at := Vector2(pr.position.x + pad, pr.end.y - pad - help_h)
	_help = _label(&"HelpDimLabel", Rect2(help_at, Vector2(pr.size.x - pad * 2.0, help_h)))
	_help.text = tr("CODEX_HELP")
	_cats = _page("categories", CATEGORIES_PAGE, "")
	_cats.row_hovered.connect(_on_category_hovered)
	_cats.row_clicked.connect(
		func(i: int) -> void:
			select_category(i)
			enter()
	)
	_list = _page("entries", ENTRIES_PAGE, " ")  # titled: the category and its count
	_list.row_hovered.connect(_on_entry_hovered)
	_list.row_clicked.connect(select_entry)
	_build_text()


func _page(key: String, pid: StringName, title: String) -> MenuPage:
	var m: Dictionary = _d.get(key, {})
	var page := MenuPage.new()
	HudLayout.place(page, m)
	add_child(page)
	page.reduced_motion = UiSettings.shared().reduced_motion()
	page.setup(m, pid, title, [])
	return page


func _build_text() -> void:
	var tm: Dictionary = _d.get("text", {})
	var page := PanelContainer.new()
	page.theme_type_variation = &"PanelSmall"
	HudLayout.place(page, tm)
	page.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(page)
	var r := HudLayout.rect_of(tm)
	var pad := HudLayout.num(tm, "pad")
	var inner := Rect2(r.position + Vector2(pad, pad), r.size - Vector2(pad, pad) * 2.0)
	var title_h := HudLayout.num(tm, "title_height")
	_title = _label(&"HeaderLabel", Rect2(inner.position, Vector2(inner.size.x, title_h)))
	_title.text_overrun_behavior = TextServer.OVERRUN_TRIM_ELLIPSIS
	var rule := OrnamentRule.new()
	var node := float(get_theme_constant(&"ornament_node_px", HymnThemeBuilder.PALETTE_TYPE))
	rule.position = Vector2(inner.position.x, inner.position.y + title_h - node)
	rule.size = Vector2(inner.size.x * 0.5, node * 2.0)
	add_child(rule)
	var sub_h := HudLayout.num(tm, "sub_height")
	_sub = _label(&"DimLabel", Rect2(inner.position + Vector2(0.0, title_h), Vector2(inner.size.x, sub_h)))
	var top := title_h + sub_h + HudLayout.num(tm, "gap")
	_clip = Control.new()
	_clip.clip_contents = true
	_clip.mouse_filter = Control.MOUSE_FILTER_STOP
	_clip.position = inner.position + Vector2(0.0, top)
	_clip.size = Vector2(inner.size.x, inner.size.y - top)
	_clip.gui_input.connect(_on_clip_input)
	add_child(_clip)
	_body = Label.new()
	_body.theme_type_variation = &"BodyLabel"
	_body.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	_body.vertical_alignment = VERTICAL_ALIGNMENT_TOP
	_body.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_body.size = _clip.size
	_clip.add_child(_body)
	_thumb = ColorRect.new()
	_thumb.color = get_theme_color(&"focus_gold", HymnThemeBuilder.PALETTE_TYPE)
	_thumb.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_thumb.visible = false
	_clip.add_child(_thumb)


func _label(variation: StringName, r: Rect2) -> Label:
	var l := Label.new()
	l.theme_type_variation = variation
	l.position = r.position
	l.size = r.size
	l.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	l.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(l)
	return l
