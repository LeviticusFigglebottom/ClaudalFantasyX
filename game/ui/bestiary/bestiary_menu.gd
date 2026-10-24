class_name BestiaryMenu
extends Control
## The bestiary (M2-UI-02, SPEC §6.11): every foe the party has Read or defeated, listed on the
## left with its defeat count, and the chosen foe's page on the right (EnemyPageView, the same
## page as the battle Read panel, built from enemies.json by BestiaryMenuModel). Out of battle.
## Layout: game/data/ui/bestiary_menu.json (1920x1080 reference).
##
## Input (keyboard and controller through ui_*): ui_up / ui_down choose, ui_page_up / ui_page_down
## (or ui_left / ui_right) jump a page, ui_cancel closes. Mouse: hover a row to show it, the wheel
## steps. It follows UiSettings (text size, palette, reduced motion; M2-UI-09). Open it with
## BestiaryMenu.open_in(host) (its own CanvasLayer; it pauses the tree while open, like SaveMenu)
## or instance bestiary_menu.tscn after configure(model).

signal closed

const SCENE_PATH := "res://game/ui/bestiary/bestiary_menu.tscn"
const DATA_PATH := "res://game/data/ui/bestiary_menu.json"
const SCRIM_SHADER := preload("res://game/ui/shaders/scrim.gdshader")
const PAGE_ID := &"bestiary"

## Pause the tree while open (the field must not move under a menu).
@export var pause_tree := true

var model: BestiaryMenuModel
## The id of the entry on show (&"" for an empty book).
var current_id: StringName = &""

var _d: Dictionary = {}
var _list: MenuPage
var _view: EnemyPageView
var _summary: Label
var _help: Label
var _entries: Array[Dictionary] = []
var _owns_pause := false
var _is_closed := false


## Instances the menu on its own CanvasLayer under `host` and opens it; the layer frees itself
## when the menu closes. `with_model` defaults to the game's log (BestiaryMenuModel.from_game()).
static func open_in(host: Node, with_model: BestiaryMenuModel = null) -> BestiaryMenu:
	var menu := (load(SCENE_PATH) as PackedScene).instantiate() as BestiaryMenu
	menu.configure(with_model)
	var layer := CanvasLayer.new()
	layer.layer = int(load_data().get("canvas_layer", 1))
	layer.process_mode = Node.PROCESS_MODE_ALWAYS
	layer.add_child(menu)
	menu.closed.connect(layer.queue_free)
	host.add_child(layer)
	return menu


static func load_data() -> Dictionary:
	var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(DATA_PATH))
	if typeof(parsed) != TYPE_DICTIONARY or typeof((parsed as Dictionary).get("bestiary_menu")) != TYPE_DICTIONARY:
		push_error("BestiaryMenu: could not read 'bestiary_menu' from %s" % DATA_PATH)
		return {}
	return (parsed as Dictionary)["bestiary_menu"] as Dictionary


## Sets the model before the menu enters the tree (null = the game's log).
func configure(with_model: BestiaryMenuModel = null) -> void:
	model = with_model


func _ready() -> void:
	if model == null:
		model = BestiaryMenuModel.from_game()
	_d = load_data()
	process_mode = Node.PROCESS_MODE_ALWAYS
	set_anchors_preset(Control.PRESET_FULL_RECT)
	mouse_filter = Control.MOUSE_FILTER_STOP
	UiSettings.shared().follow(self)
	_build()
	refresh()
	if pause_tree and not get_tree().paused:
		get_tree().paused = true
		_owns_pause = true


func _exit_tree() -> void:
	_restore_pause()


func is_open() -> bool:
	return not _is_closed


## Re-reads the log and redraws (the cursor goes back to the first entry).
func refresh() -> void:
	_entries = model.entries()
	var rows: Array[Dictionary] = []
	for e in _entries:
		var row := {"id": e["id"], "label": e["name"], "right": model.count_text(e), "enabled": true}
		row["right_role"] = &"text" if bool(e["read"]) else &"text_dim"  # focus means the cursor (M2-UI-08)
		row["mp"] = "" if bool(e["read"]) else tr("BESTIARY_UNREAD_TAG")  # words, not hue alone
		rows.append(row)
	_list.replace_rows(rows)
	_summary.text = model.summary()
	_show(0)


func entries() -> Array[Dictionary]:
	return _entries.duplicate()


func page_view() -> EnemyPageView:
	return _view


func summary_text() -> String:
	return _summary.text


func _unhandled_input(event: InputEvent) -> void:
	if is_open() and handle_input(event):
		get_viewport().set_input_as_handled()


## Applies one input event. Returns true when the menu used it. Tests call this directly.
func handle_input(event: InputEvent) -> bool:
	if not is_open():
		return false
	if event.is_action_pressed(&"ui_up", true):
		_move(-1)
	elif event.is_action_pressed(&"ui_down", true):
		_move(1)
	elif event.is_action_pressed(&"ui_page_up", true) or event.is_action_pressed(&"ui_left", true):
		_page_step(-1)
	elif event.is_action_pressed(&"ui_page_down", true) or event.is_action_pressed(&"ui_right", true):
		_page_step(1)
	elif _wheel(event) != 0:
		_move(_wheel(event))
	elif event.is_action_pressed(&"ui_cancel"):
		close()
	elif event.is_action_pressed(&"ui_accept"):
		pass  # nothing to confirm: the page already shows the entry under the cursor
	else:
		return false
	return true


## Shows entry `index` (the list cursor follows).
func select(index: int) -> void:
	_list.set_cursor(index, false)
	_show(_list.cursor)


func close() -> void:
	if _is_closed:
		return
	_is_closed = true
	_restore_pause()
	closed.emit()


func _move(delta: int) -> void:
	if _list.move(delta):
		_show(_list.cursor)


## A page of the list at a time (page up / down, or left / right on a pad), stopping at either end
## rather than wrapping, so a long book is quick to cross (M2-UI-09).
func _page_step(direction: int) -> void:
	if _entries.is_empty():
		return
	var rows := int(HudLayout.num(_d.get("list", {}), "max_rows"))
	select(clampi(_list.cursor + direction * rows, 0, _entries.size() - 1))


## -1 / 1 for a mouse wheel turn up / down, else 0.
static func _wheel(event: InputEvent) -> int:
	var mb := event as InputEventMouseButton
	if mb == null or not mb.pressed:
		return 0
	if mb.button_index == MOUSE_BUTTON_WHEEL_UP:
		return -1
	return 1 if mb.button_index == MOUSE_BUTTON_WHEEL_DOWN else 0


func _show(index: int) -> void:
	if _entries.is_empty():
		current_id = &""
		_view.visible = false
		return
	var at := clampi(index, 0, _entries.size() - 1)
	current_id = StringName(str(_entries[at]["id"]))
	_view.visible = true
	_view.show_page(model.page(current_id))


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
	var title := _label(&"BannerLabel", Rect2(pr.position + Vector2(pad, pad), Vector2(pr.size.x * 0.5, title_h)))
	title.text = tr("BESTIARY_TITLE")
	var rule := OrnamentRule.new()  # ADR 0033: the gold rule under the title
	var node := float(get_theme_constant(&"ornament_node_px", HymnThemeBuilder.PALETTE_TYPE))
	rule.position = Vector2(title.position.x, title.position.y + title.size.y - node)
	rule.size = Vector2(title.size.x * 0.6, node * 2.0)
	add_child(rule)
	var right := Rect2(pr.position + Vector2(pr.size.x * 0.5, pad), Vector2(pr.size.x * 0.5 - pad, title_h))
	_summary = _label(&"DimLabel", right)
	_summary.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
	var help_h := HudLayout.num(pm, "help_height")
	var help_at := Vector2(pr.position.x + pad, pr.end.y - pad - help_h)
	_help = _label(&"HelpDimLabel", Rect2(help_at, Vector2(pr.size.x - pad * 2.0, help_h)))
	_help.text = tr("BESTIARY_HELP")
	var lm: Dictionary = _d.get("list", {})
	_list = MenuPage.new()
	HudLayout.place(_list, lm)
	add_child(_list)
	_list.reduced_motion = UiSettings.shared().reduced_motion()
	_list.setup(lm, PAGE_ID, "", [])
	_list.row_hovered.connect(func(i: int) -> void: _show(i))
	_list.row_clicked.connect(select)
	var gm: Dictionary = _d.get("page", {})
	var page_panel := PanelContainer.new()
	page_panel.theme_type_variation = &"PanelSmall"
	HudLayout.place(page_panel, gm)
	page_panel.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(page_panel)
	var margin := MarginContainer.new()
	margin.mouse_filter = Control.MOUSE_FILTER_IGNORE
	for side: StringName in [&"margin_left", &"margin_right", &"margin_top", &"margin_bottom"]:
		margin.add_theme_constant_override(side, int(HudLayout.num(gm, "pad")))
	page_panel.add_child(margin)
	_view = EnemyPageView.new()
	margin.add_child(_view)


func _label(variation: StringName, r: Rect2) -> Label:
	var l := Label.new()
	l.theme_type_variation = variation
	l.position = r.position
	l.size = r.size
	l.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	l.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(l)
	return l
