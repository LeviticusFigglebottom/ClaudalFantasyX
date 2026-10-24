class_name LatticeMenu
extends FieldSubmenu
## STUB (M2-MNU-01, the Menus track): the field menu's Lattice page. Built over a PartySheet.
## Layout: game/data/ui/lattice_menu.json.

const DATA_PATH := "res://game/data/ui/lattice_menu.json"

var sheet: PartySheet


static func create(with_sheet: PartySheet = null) -> LatticeMenu:
	var menu := LatticeMenu.new()
	menu.sheet = with_sheet
	return menu


## Opens the page on its own CanvasLayer under `host` (null sheet = the live party).
static func open_in(host: Node, with_sheet: PartySheet = null) -> LatticeMenu:
	return FieldSubmenu.mount(create(with_sheet), host) as LatticeMenu


func data_path() -> String:
	return DATA_PATH


func data_section() -> String:
	return "lattice_menu"


func _build_page() -> void:
	if sheet == null:
		sheet = PartySheet.from_game()
	var help := _framed_panel(_d.get("panel", {}), tr("FIELD_MENU_LATTICE"))
	help.text = tr("FIELD_MENU_HELP_BACK")
