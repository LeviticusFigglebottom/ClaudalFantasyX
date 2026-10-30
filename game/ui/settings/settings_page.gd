class_name SettingsPage
extends Control
## One settings page (M1-UI-10's Graphics page, generalised by M2-UI-09): a modal page over a dark
## backdrop with a MenuPage whose right column shows each row's value, and a help line. The logic
## is a SettingsPageModel (GraphicsMenuModel, AccessibilityMenuModel); this is its view and input.
## Every change saves and applies at once. It follows UiSettings (text size, palette, reduced
## motion) live, so the Accessibility page previews its own changes.
## Input: ui_up / ui_down move, ui_left / ui_right (or ui_accept, forward) change the value,
## ui_cancel closes; hover moves the cursor, a click on the row under it steps its value.
## Layout: game/data/ui/graphics_menu.json ("page", "help", "backdrop_alpha").

signal closed
## The close transition has finished (at once under Reduced motion); the page frees itself then
## (M2-MNU-305, MenuMotion).
signal gone

## The page's logic (set by the subclass before _ready).
var page_model: SettingsPageModel
## The accessibility settings the page follows (UiSettings.shared() unless the subclass sets one).
var ui_settings: UiSettings

var _page: MenuPage
var _help: Label
var _backdrop: ColorRect
var _caustics: CausticBackdrop
var _open := false
var _motion: MenuMotion


func _ready() -> void:
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	mouse_filter = Control.MOUSE_FILTER_STOP
	if ui_settings == null:
		ui_settings = UiSettings.shared()
	ui_settings.follow(self)
	var data := page_model.layout()
	_backdrop = ColorRect.new()
	_backdrop.set_anchors_preset(Control.PRESET_FULL_RECT)
	_backdrop.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(_backdrop)
	_paint_backdrop()
	_caustics = CausticBackdrop.new()  # ADR 0033
	add_child(_caustics)
	var pm := data.get("page", {}) as Dictionary
	_page = MenuPage.new()
	var r := HudLayout.rect_of(pm)
	_page.position = r.position
	_page.size = Vector2(r.size.x, MenuPage.height_for(pm, page_model.row_ids().size()))
	add_child(_page)
	_page.reduced_motion = ui_settings.reduced_motion()
	_page.setup(pm, StringName(page_model.title_key()), tr(page_model.title_key()), _rows())
	_page.row_hovered.connect(_on_row_hovered)
	_page.row_clicked.connect(_on_row_clicked)
	_help = Label.new()
	_help.theme_type_variation = &"HelpDimLabel"
	HudLayout.place(_help, data.get("help", {}) as Dictionary)
	_help.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_help.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	_help.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	_help.text_overrun_behavior = TextServer.OVERRUN_TRIM_ELLIPSIS
	_help.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(_help)
	UiFrame.centre(self)  # M2-UI-29
	page_model.changed.connect(_render)
	_open = true
	_render()
	# Over the hub, whose backdrop is the same: only the content moves.
	MenuMotion.follow_reduced_motion(self)
	_motion = MenuMotion.new(self)
	_motion.gone.connect(gone.emit)
	gone.connect(queue_free)
	_motion.play_in(true)


func _notification(what: int) -> void:
	if what == NOTIFICATION_THEME_CHANGED and _backdrop != null:
		_paint_backdrop()


func _unhandled_input(event: InputEvent) -> void:
	if handle_input(event):
		get_viewport().set_input_as_handled()


## Applies one input event. Returns true when the page used it. Tests call this directly.
func handle_input(event: InputEvent) -> bool:
	if not _open:
		return false
	if is_busy():
		return true  # a subclass holds the page (the Graphics page's apply veil): swallow input
	if event.is_action_pressed(&"ui_up", true):
		page_model.move(-1)
	elif event.is_action_pressed(&"ui_down", true):
		page_model.move(1)
	elif event.is_action_pressed(&"ui_left", true):
		_change(-1)
	elif event.is_action_pressed(&"ui_right", true) or event.is_action_pressed(&"ui_accept"):
		_change(1)
	elif event.is_action_pressed(&"ui_cancel"):
		close()
	else:
		return false
	return true


func is_open() -> bool:
	return _open


func close() -> void:
	if not _open or is_busy():
		return
	_open = false
	if _motion != null:
		_motion.play_out(true)
	else:
		visible = false
		gone.emit()
	closed.emit()


## The open and close transitions (null before _ready). Tests drive them with motion().finish().
func motion() -> MenuMotion:
	return _motion


## The value shown on `row` (tests and captures read it).
func value_shown(row: StringName) -> String:
	var i := page_model.row_ids().find(row)
	return str(_page.rows[i].get("right", "")) if i >= 0 and i < _page.rows.size() else ""


## Override: true while the page must not take input or close (the Graphics page's apply veil).
func is_busy() -> bool:
	return false


## Override: steps the current row's value (the Graphics page puts a preset change behind its veil).
func _change(delta: int) -> void:
	page_model.cycle(delta)


func help_text() -> String:
	return _help.text


func _rows() -> Array[Dictionary]:
	var out: Array[Dictionary] = []
	for id in page_model.row_ids():
		var row := {"id": id, "label": page_model.label(id), "right": page_model.value_text(id)}
		row["right_role"] = &"focus_gold"
		out.append(row)
	return out


func _render() -> void:
	_page.replace_rows(_rows())
	_page.set_cursor(page_model.cursor, is_inside_tree())
	_help.text = tr(page_model.help_key())
	HudLayout.fit_lines(_help)  # a long row's help at 130 % shrinks a little before it ellipsizes


func _paint_backdrop() -> void:
	var deep := get_theme_color(&"panel_low", HymnThemeBuilder.PALETTE_TYPE)
	_backdrop.color = Color(deep, float(page_model.layout().get("backdrop_alpha", 1.0)))


func _on_row_hovered(index: int) -> void:
	if index != page_model.cursor:
		page_model.set_cursor(index)


func _on_row_clicked(index: int) -> void:
	if is_busy():
		return
	if page_model.cursor == index:
		_change(1)
	else:
		page_model.set_cursor(index)
