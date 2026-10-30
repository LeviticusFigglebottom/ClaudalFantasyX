class_name SettingsMenu
extends Control
## The Settings hub (M2-UI-09): one short page, Graphics, Accessibility and Controls (M2-UI-13),
## each opening its SettingsPage over the hub; closing a page comes back to the hub with the cursor where it was.
## Opened from the title's Settings row (TitleMenu) and the field menu's Settings row (FieldMenu,
## through open_in, on its own CanvasLayer). Follows UiSettings like every settings page.
## Input: ui_up / ui_down move, ui_accept opens, ui_cancel closes; hover moves, a click opens.
## While a page is open it takes the input. Layout: game/data/ui/graphics_menu.json ("page",
## "help", "backdrop_alpha", "hub").

signal closed
## The close transition has finished (at once under Reduced motion): the hub frees itself, and
## open_in's layer with it (M2-MNU-305, MenuMotion).
signal gone

const ROW_GRAPHICS := &"graphics"
const ROW_ACCESSIBILITY := &"accessibility"
const ROW_CONTROLS := &"controls"
const ROW_AUDIO := &"audio"
## Every hub row in order; Audio shows only when UiSettings has an Audio row (row_ids()).
const ROW_IDS: Array[StringName] = [ROW_GRAPHICS, ROW_AUDIO, ROW_ACCESSIBILITY, ROW_CONTROLS]
const LABEL_KEYS := {
	ROW_GRAPHICS: "SET_MENU_GRAPHICS",
	ROW_AUDIO: "SET_MENU_AUDIO",
	ROW_ACCESSIBILITY: "SET_MENU_ACCESSIBILITY",
	ROW_CONTROLS: "SET_MENU_CONTROLS",
}
## The hub's controls line (Up and Down, Confirm, Cancel).
const CONTROLS_KEY := "SET_MENU_CONTROLS_HUB"
const HELP_KEYS := {
	ROW_GRAPHICS: "SET_MENU_HELP_GRAPHICS",
	ROW_AUDIO: "SET_MENU_HELP_AUDIO",
	ROW_ACCESSIBILITY: "SET_MENU_HELP_ACCESSIBILITY",
	ROW_CONTROLS: "SET_MENU_HELP_CONTROLS",
}

## The page open over the hub (null when none).
var page: SettingsPage
## Opened over the field menu, whose scrim and caustics are the same: the backdrop stays still and
## only the content moves (MenuMotion's static backdrop). Set before it enters the tree.
var over_menu := false
## The accessibility settings the hub and its Accessibility page use (shared unless a test sets one).
var ui_settings: UiSettings
## Where the Accessibility and Controls pages save ("" = nowhere; tests).
var save_path := UiSettings.CONFIG_PATH
## Where the Graphics page applies (null = this menu's viewport; tests pass their own).
var graphics_viewport: Viewport

var _list: MenuPage
var _help: Label
var _controls: Label
var _backdrop: ColorRect
var _caustics: CausticBackdrop
var _data: Dictionary = {}
var _open := false
var _motion: MenuMotion


## Opens the hub on its own CanvasLayer under `host` (the field menu); the layer frees itself when
## the hub closes. It processes while the tree is paused.
static func open_in(host: Node, over: bool = false) -> SettingsMenu:
	var menu := SettingsMenu.new()
	menu.over_menu = over
	var layer := CanvasLayer.new()
	layer.layer = int((GraphicsMenuModel.load_data().get("hub", {}) as Dictionary).get("canvas_layer", 1))
	layer.process_mode = Node.PROCESS_MODE_ALWAYS
	layer.add_child(menu)
	menu.gone.connect(layer.queue_free)
	host.add_child(layer)
	return menu


func _ready() -> void:
	name = &"SettingsMenu"
	process_mode = Node.PROCESS_MODE_ALWAYS
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	mouse_filter = Control.MOUSE_FILTER_STOP
	if ui_settings == null:
		ui_settings = UiSettings.shared()
	ui_settings.follow(self)
	_data = GraphicsMenuModel.load_data()
	_backdrop = ColorRect.new()
	_backdrop.set_anchors_preset(Control.PRESET_FULL_RECT)
	_backdrop.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(_backdrop)
	_paint_backdrop()
	_caustics = CausticBackdrop.new()  # ADR 0033
	add_child(_caustics)
	var pm := _data.get("page", {}) as Dictionary
	_list = MenuPage.new()
	var r := HudLayout.rect_of(pm)
	_list.position = r.position
	_list.size = Vector2(r.size.x, MenuPage.height_for(pm, row_ids().size()))
	add_child(_list)
	_list.reduced_motion = ui_settings.reduced_motion()
	_list.setup(pm, &"settings", tr("SET_MENU_TITLE"), _rows())
	_list.row_hovered.connect(func(_i: int) -> void: _render())
	_list.row_clicked.connect(_on_row_clicked)
	_help = Label.new()
	_help.theme_type_variation = &"HelpDimLabel"
	HudLayout.place(_help, _data.get("help", {}) as Dictionary)
	_help.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_help.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	_help.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_help.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	_help.text_overrun_behavior = TextServer.OVERRUN_TRIM_ELLIPSIS
	add_child(_help)
	_controls = SettingsPage.controls_line(_data)
	add_child(_controls)
	UiFrame.centre(self)  # M2-UI-29
	_open = true
	_render()
	MenuMotion.follow_reduced_motion(self)
	_motion = MenuMotion.new(self)
	_motion.gone.connect(gone.emit)
	gone.connect(queue_free)
	_motion.play_in(over_menu)


func _notification(what: int) -> void:
	if what == NOTIFICATION_THEME_CHANGED and _backdrop != null:
		_paint_backdrop()


func _unhandled_input(event: InputEvent) -> void:
	if handle_input(event):
		get_viewport().set_input_as_handled()


## Applies one input event. Returns true when the hub (or its open page) used it. Tests call it.
func handle_input(event: InputEvent) -> bool:
	if not _open:
		return false
	if is_page_open():
		return page.handle_input(event)
	if event.is_action_pressed(&"ui_up", true):
		_list.move(-1)
	elif event.is_action_pressed(&"ui_down", true):
		_list.move(1)
	elif event.is_action_pressed(&"ui_accept"):
		open_page(current())
	elif event.is_action_pressed(&"ui_cancel"):
		close()
	else:
		return false
	_render()
	return true


## The row under the cursor.
func current() -> StringName:
	return StringName(str(_list.current_row().get("id", "")))


## Opens page `row` (ROW_GRAPHICS, ROW_AUDIO, ROW_ACCESSIBILITY or ROW_CONTROLS) over the hub.
## Returns it (null if unknown).
func open_page(row: StringName) -> SettingsPage:
	if is_page_open():
		return page
	match row:
		ROW_GRAPHICS:
			page = GraphicsMenu.new(graphics_viewport)
		ROW_AUDIO:
			page = AudioMenu.new(ui_settings, save_path)
		ROW_ACCESSIBILITY:
			page = AccessibilityMenu.new(ui_settings, save_path)
		ROW_CONTROLS:
			page = ControlsMenu.new(save_path)
			page.ui_settings = ui_settings
		_:
			return null
	_set_hub_visible(false)
	page.closed.connect(_on_page_closed)
	add_child(page)
	return page


func is_page_open() -> bool:
	return page != null and is_instance_valid(page) and page.is_open()


func is_open() -> bool:
	return _open


func close() -> void:
	if not _open:
		return
	if is_page_open():
		page.close()
	_open = false
	if _motion != null:
		_motion.play_out(over_menu)  # it never takes the pointer again while it fades (M2-UI-26)
	else:
		visible = false
		gone.emit()
	closed.emit()


## The open, close and return transitions (null before _ready). Tests drive them with motion().finish().
func motion() -> MenuMotion:
	return _motion


func help_text() -> String:
	return _help.text


func controls_text() -> String:
	return _controls.text


func row_labels() -> PackedStringArray:
	var out: PackedStringArray = []
	for r in _list.rows:
		out.append(str(r.get("label", "")))
	return out


## The hub's rows: ROW_IDS, without Audio while UiSettings has none of its rows (M3-UI-02).
func row_ids() -> Array[StringName]:
	var out: Array[StringName] = []
	var no_audio := AudioMenuModel.new(ui_settings, "").row_ids().is_empty()
	for id in ROW_IDS:
		if not (id == ROW_AUDIO and no_audio):
			out.append(id)
	return out


func _rows() -> Array[Dictionary]:
	var out: Array[Dictionary] = []
	for id in row_ids():
		out.append({"id": id, "label": tr(LABEL_KEYS[id]), "enabled": true})
	return out


func _render() -> void:
	_help.text = tr(str(HELP_KEYS.get(current(), "")))
	SettingsPage.show_controls(_controls, CONTROLS_KEY if _list.visible else "", _data)  # hidden under an open page


## The hub's own page, help and backdrop hide under an open page (its backdrop would double up).
func _set_hub_visible(on: bool) -> void:
	for c: CanvasItem in [_list, _help, _controls, _backdrop, _caustics]:
		c.visible = on


func _paint_backdrop() -> void:
	var deep := get_theme_color(&"panel_low", HymnThemeBuilder.PALETTE_TYPE)
	_backdrop.color = Color(deep, float(_data.get("backdrop_alpha", 1.0)))


func _on_page_closed() -> void:
	page = null
	_set_hub_visible(true)
	if _open and _motion != null:
		_motion.play_in(true, "return_sec")  # the hub's rows fade back in as the page fades out
	_list.replace_rows(_rows())  # in the text size or palette just chosen
	_render()


func _on_row_clicked(index: int) -> void:
	if not _open or is_page_open():
		return
	_list.set_cursor(index, false)
	open_page(current())
