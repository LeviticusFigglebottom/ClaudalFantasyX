class_name ReefballOutfitterMenu
extends TownMenu
## The Reefball outfitter (ADR 0040, M3-C07-05): Reefball-only gear for the side's matches, never
## battle equipment. Each piece shows its price, or Owned or Worn, on the right; the line about the
## highlighted piece says what it adds, and under it what choosing it does (buy, put on, swap, take
## off) or why not. Leave closes. A field Interactable whose payload is {"reefball_outfitter": "<id>"}
## opens it through TownServices. Words and choices: ReefballOutfitterModel. Layout: shop_menu.json
## "reefball_outfitter".
##
## Input: ui_up / ui_down move, ui_accept chooses, ui_cancel leaves. Mouse: hover moves, click chooses.

const SCENE_PATH := "res://game/ui/reefball/reefball_outfitter_menu.tscn"
const SECTION := "reefball_outfitter"

var model: ReefballOutfitterModel

var _root: MenuPage
var _notice: Dictionary = {}


static func open_in(host: Node, with_model: ReefballOutfitterModel) -> ReefballOutfitterMenu:
	var menu := (load(SCENE_PATH) as PackedScene).instantiate() as ReefballOutfitterMenu
	menu.configure(with_model)
	TownMenu.host_in(host, menu, SECTION)
	return menu


func configure(with_model: ReefballOutfitterModel) -> void:
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
	var id := StringName(str(_root.current_row().get("id", "")))
	if id == ReefballOutfitterModel.ROW_LEAVE:
		close()
		return
	_notice = model.choose(id)
	var at := _root.cursor
	_root.replace_rows(model.rows())
	_root.set_cursor(at, false)
	_render()


func _move(delta: int) -> void:
	if _root.move(delta):
		_notice = {}
		_render()


func _section() -> String:
	return SECTION


func _build() -> void:
	var rm: Dictionary = _d.get("root", {})
	_root = _page(rm, &"reefball_outfitter", "", int(HudLayout.num(rm, "max_rows")))
	_root.row_hovered.connect(_on_hovered)
	_root.row_clicked.connect(_on_clicked)
	_title.text = model.title()
	_root.replace_rows(model.rows())
	_root.set_cursor(0, false)
	_help.text = tr("RBL_OUTFIT_HELP")


func _render() -> void:
	_purse.text = model.purse_text()
	var id := StringName(str(_root.current_row().get("id", "")))
	_desc.text = model.row_desc(id)
	_set_status(_notice if not _notice.is_empty() else model.row_line(id))


func _on_hovered(_index: int) -> void:
	_notice = {}
	_render()


func _on_clicked(index: int) -> void:
	if not is_open():
		return
	_root.set_cursor(index, false)
	accept()
