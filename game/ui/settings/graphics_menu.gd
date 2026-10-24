class_name GraphicsMenu
extends Control
## The Graphics settings page (M1-UI-10; graphics_settings.md, "The Graphics menu"): a modal
## page over a dark backdrop. Logic is GraphicsMenuModel; this is its view (a MenuPage whose right
## column shows each value, plus a help line) and input. Every change saves and applies at once.
## Input: ui_up / ui_down move, ui_left / ui_right (or ui_accept, forward) change the value,
## ui_cancel closes; a click on a row steps its value forward.
## Opened from the title (TitleMenu, Settings). Layout: game/data/ui/graphics_menu.json.

signal closed

var model: GraphicsMenuModel

var _page: MenuPage
var _help: Label
var _open := false


func _init(vp: Viewport = null) -> void:
	model = GraphicsMenuModel.new(vp)
	name = &"GraphicsMenu"


func _ready() -> void:
	set_anchors_preset(Control.PRESET_FULL_RECT)
	mouse_filter = Control.MOUSE_FILTER_STOP
	if model.viewport == null:
		model.viewport = get_viewport()
	var backdrop := ColorRect.new()
	backdrop.set_anchors_preset(Control.PRESET_FULL_RECT)
	backdrop.mouse_filter = Control.MOUSE_FILTER_IGNORE
	var deep := get_theme_color(&"panel_low", HymnThemeBuilder.PALETTE_TYPE)
	backdrop.color = Color(deep, float(model.data.get("backdrop_alpha", 1.0)))
	add_child(backdrop)
	var pm := model.data.get("page", {}) as Dictionary
	_page = MenuPage.new()
	var r := HudLayout.rect_of(pm)
	_page.position = r.position
	_page.size = Vector2(r.size.x, MenuPage.height_for(pm, model.row_ids().size()))
	add_child(_page)
	_page.setup(pm, &"graphics", tr("GFX_MENU_TITLE"), _rows())
	_page.row_clicked.connect(_on_row_clicked)
	_help = Label.new()
	_help.theme_type_variation = &"HelpLabel"
	HudLayout.place(_help, model.data.get("help", {}) as Dictionary)
	_help.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_help.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	_help.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_help.add_theme_color_override(&"font_color", get_theme_color(&"text_dim", HymnThemeBuilder.PALETTE_TYPE))
	add_child(_help)
	model.changed.connect(_render)
	_open = true
	_render()


func _unhandled_input(event: InputEvent) -> void:
	if handle_input(event):
		get_viewport().set_input_as_handled()


## Applies one input event. Returns true when the page used it. Tests call this directly.
func handle_input(event: InputEvent) -> bool:
	if not _open:
		return false
	if event.is_action_pressed(&"ui_up", true):
		model.move(-1)
	elif event.is_action_pressed(&"ui_down", true):
		model.move(1)
	elif event.is_action_pressed(&"ui_left", true):
		model.cycle(-1)
	elif event.is_action_pressed(&"ui_right", true) or event.is_action_pressed(&"ui_accept"):
		model.cycle(1)
	elif event.is_action_pressed(&"ui_cancel"):
		close()
	else:
		return false
	return true


func is_open() -> bool:
	return _open


func close() -> void:
	if not _open:
		return
	_open = false
	closed.emit()
	queue_free()


## The value shown on `row` (tests and captures read it).
func value_shown(row: StringName) -> String:
	var i := model.row_ids().find(row)
	return str(_page.rows[i].get("right", "")) if i >= 0 and i < _page.rows.size() else ""


func help_text() -> String:
	return _help.text


func _rows() -> Array[Dictionary]:
	var out: Array[Dictionary] = []
	for id in model.row_ids():
		out.append({"id": id, "label": model.label(id), "right": model.value_text(id), "right_role": &"focus_gold"})
	return out


func _render() -> void:
	_page.replace_rows(_rows())
	_page.set_cursor(model.cursor, is_inside_tree())
	_help.text = tr(model.help_key())


func _on_row_clicked(index: int) -> void:
	if model.cursor == index:
		model.cycle(1)
	else:
		model.set_cursor(index)
