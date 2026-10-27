class_name BattlePauseMenu
extends FieldSubmenu
## The battle pause page (M2-MNU-04): Resume, Settings (the Settings hub over it) and Quit to the
## title, which asks first (Stay under the cursor, the line saying what is lost). While it is open
## the whole tree is paused (FieldSubmenu), so the engine, BattleChoreo, the camera and every tween
## hold still; closing lifts the pause. BattlePause opens it. Layout: game/data/ui/battle_pause.json.
##
## Input: ui_up / ui_down move, ui_accept chooses, ui_cancel (or the pause action again) resumes or
## backs out of the confirm. Mouse: hover moves, click chooses.

enum Level { ROOT, QUIT }

const DATA_PATH := "res://game/data/ui/battle_pause.json"
const PAUSE_ACTION := &"battle_pause"
const ROW_RESUME := &"resume"
const ROW_SETTINGS := &"settings"
const ROW_QUIT := &"quit"
const ROW_LABEL_KEYS := {
	ROW_RESUME: "BATTLE_PAUSE_RESUME",
	ROW_SETTINGS: "FIELD_MENU_SETTINGS",
	ROW_QUIT: "FIELD_MENU_QUIT",
}
const ROW_DESC_KEYS := {
	ROW_RESUME: "BATTLE_PAUSE_RESUME_DESC",
	ROW_SETTINGS: "FIELD_MENU_SETTINGS_DESC",
	ROW_QUIT: "BATTLE_PAUSE_QUIT_DESC",
}

var level := Level.ROOT
## The Settings hub opened from here (null when closed).
var settings_menu: SettingsMenu

var _rows: MenuPage
var _desc: Label
var _help: Label


static func create() -> BattlePauseMenu:
	return BattlePauseMenu.new()


## Opens the page on its own CanvasLayer under `host`.
static func open_in(host: Node) -> BattlePauseMenu:
	return FieldSubmenu.mount(create(), host) as BattlePauseMenu


func data_path() -> String:
	return DATA_PATH


func data_section() -> String:
	return "battle_pause"


func rows_page() -> MenuPage:
	return _rows


func desc_text() -> String:
	return _desc.text


func handle_input(event: InputEvent) -> bool:
	if not is_open() or (settings_menu != null and settings_menu.is_open()):
		return false
	if event.is_action_pressed(&"ui_up", true):
		_move(-1)
	elif event.is_action_pressed(&"ui_down", true):
		_move(1)
	elif event.is_action_pressed(&"ui_accept"):
		accept()
	elif event.is_action_pressed(&"ui_cancel") or event.is_action_pressed(PAUSE_ACTION):
		back()
	else:
		return false
	return true


## Chooses the highlighted row.
func accept() -> void:
	var id := StringName(str(_rows.current_row().get("id", "")))
	if level == Level.QUIT:
		if id == FieldMenuModel.QUIT_GO:
			quit_to_title()
		else:
			back()
		return
	match id:
		ROW_RESUME:
			close()
		ROW_SETTINGS:
			settings_menu = SettingsMenu.open_in(self)
			visible = false
			settings_menu.closed.connect(_on_settings_closed)
		ROW_QUIT:
			level = Level.QUIT
			_show_rows(_quit_rows(), 0)


## Backs out of the confirm, or resumes.
func back() -> void:
	if level == Level.QUIT:
		level = Level.ROOT
		_show_rows(_root_rows(), _root_rows().size() - 1)
	else:
		close()


func close() -> void:
	if settings_menu != null and settings_menu.is_open():
		settings_menu.close()
	super()


## Lifts the pause and returns to the title (FlowRouting waits for an idle router).
func quit_to_title() -> void:
	close()
	FlowRouting.change_scene(FieldMenu.TITLE_SCENE)


func _build_page() -> void:
	var dim := ColorRect.new()
	dim.set_anchors_preset(Control.PRESET_FULL_RECT)
	dim.mouse_filter = Control.MOUSE_FILTER_IGNORE
	dim.color = Color(_c(&"panel_low"), HudLayout.num(_d, "dim_alpha"))
	add_child(dim)
	_help = _framed_panel(_d.get("panel", {}), tr("BATTLE_PAUSE_TITLE"))
	var rm: Dictionary = _d.get("rows", {})
	_rows = _menu_page(rm, &"battle_pause", "", ROW_LABEL_KEYS.size())
	_rows.row_hovered.connect(func(_i: int) -> void: _render())
	_rows.row_clicked.connect(_on_clicked)
	var em: Dictionary = _d.get("desc", {})
	var top := _rows.position.y + _rows.size.y + HudLayout.num(em, "gap")
	_desc = _label(
		&"BodyLabel", Rect2(Vector2(_rows.position.x, top), Vector2(_rows.size.x, HudLayout.num(em, "height")))
	)
	_desc.vertical_alignment = VERTICAL_ALIGNMENT_TOP
	_desc.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	_show_rows(_root_rows(), 0)


func _root_rows() -> Array[Dictionary]:
	var out: Array[Dictionary] = []
	for id: StringName in ROW_LABEL_KEYS:
		out.append({"id": id, "label": tr(ROW_LABEL_KEYS[id]), "enabled": true})
	return out


func _quit_rows() -> Array[Dictionary]:
	return [
		{"id": FieldMenuModel.QUIT_STAY, "label": tr(FieldMenuModel.QUIT_STAY_KEY), "enabled": true},
		{"id": FieldMenuModel.QUIT_GO, "label": tr(FieldMenuModel.QUIT_GO_KEY), "enabled": true},
	]


func _show_rows(rows: Array[Dictionary], cursor: int) -> void:
	_rows.replace_rows(rows)
	_rows.set_cursor(cursor, false)
	_render()


func _move(delta: int) -> void:
	if _rows.move(delta):
		_render()


func _render() -> void:
	var id := StringName(str(_rows.current_row().get("id", "")))
	if level == Level.QUIT:
		_desc.text = tr(FieldMenuModel.QUIT_WARN_KEY if id == FieldMenuModel.QUIT_GO else "BATTLE_PAUSE_STAY_DESC")
		_help.text = tr("FIELD_MENU_HELP_QUIT")
	else:
		_desc.text = tr(str(ROW_DESC_KEYS.get(id, "")))
		_help.text = tr("BATTLE_PAUSE_HELP")
	var pm: Dictionary = _d.get("panel", {})
	UiFrame.fit_line(_help, HudLayout.rect_of(pm).size.x - HudLayout.num(pm, "pad") * 2.0)  # 130 % text (M2-UI-29)


func _on_clicked(index: int) -> void:
	if not is_open() or (settings_menu != null and settings_menu.is_open()):
		return
	_rows.set_cursor(index, false)
	accept()


func _on_settings_closed() -> void:
	settings_menu = null
	visible = true
	_render()
