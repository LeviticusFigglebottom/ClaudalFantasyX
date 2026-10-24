class_name InnMenu
extends TownMenu
## The inn menu (M2-UI-06, SPEC §6.6): Rest for the inn's price (shops.json "inns"), which heals
## the party exactly as a save shrine does but writes no save, or Leave. A field Interactable
## whose payload is {"inn": "<inn id>"} opens it through TownServices. Words: InnMenuModel.
##
## Input: ui_up / ui_down move, ui_accept rests or leaves, ui_cancel leaves. Mouse: hover to
## move, click to choose. After a rest the status line says the party woke restored, and the
## cursor moves to Leave.

const SCENE_PATH := "res://game/ui/shop/inn_menu.tscn"
const SECTION := "inn_menu"

var model: InnMenuModel

var _root: MenuPage
var _notice: Dictionary = {}


static func open_in(host: Node, with_model: InnMenuModel) -> InnMenu:
	var menu := (load(SCENE_PATH) as PackedScene).instantiate() as InnMenu
	menu.configure(with_model)
	TownMenu.host_in(host, menu, SECTION)
	return menu


func configure(with_model: InnMenuModel) -> void:
	model = with_model


func root_page() -> MenuPage:
	return _root


func handle_input(event: InputEvent) -> bool:
	if not is_open():
		return false
	if event.is_action_pressed(&"ui_up", true):
		_move(-1)
	elif event.is_action_pressed(&"ui_down", true):
		_move(1)
	elif event.is_action_pressed(&"ui_accept"):
		accept()
	elif event.is_action_pressed(&"ui_cancel"):
		close()
	else:
		return false
	return true


func accept() -> void:
	match StringName(str(_root.current_row().get("id", ""))):
		InnMenuModel.ROW_REST:
			_notice = model.rest()
			_root.replace_rows(model.root_rows())
			if bool(_notice.get("ok", false)):
				_root.set_cursor(InnMenuModel.ROOT_IDS.find(InnMenuModel.ROW_LEAVE), false)
			_render()
		InnMenuModel.ROW_LEAVE:
			close()


func _move(delta: int) -> void:
	if _root.move(delta):
		_notice = {}
		_render()


func _section() -> String:
	return SECTION


func _build() -> void:
	_root = _page(_d.get("root", {}), &"inn_root", "", InnMenuModel.ROOT_IDS.size())
	_root.row_hovered.connect(_on_hovered)
	_root.row_clicked.connect(_on_clicked)
	_title.text = model.title()
	_root.replace_rows(model.root_rows())
	_root.set_cursor(_root.first_enabled(0, 1), false)
	_help.text = tr("INN_MENU_HELP")


func _render() -> void:
	_purse.text = model.purse_text()
	var id := StringName(str(_root.current_row().get("id", "")))
	_desc.text = model.row_desc(id)
	if not _notice.is_empty():
		_set_status(_notice)
	elif id == InnMenuModel.ROW_REST or not _root.rows[0].get("enabled", true):
		_set_status(model.rest_line())
	else:
		_set_status({})


func _on_hovered(_index: int) -> void:
	_notice = {}
	_render()


func _on_clicked(index: int) -> void:
	if not is_open():
		return
	_root.set_cursor(index, false)
	accept()
