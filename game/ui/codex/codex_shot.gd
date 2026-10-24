class_name CodexShot
extends Control
## Capture driver for the field_menu_codex shot (M3-UI-03, tests/screenshots/shots.json). It opens
## the field menu on a scratch save with a CodexModel on fixed flags (the party has crossed onto
## the Saltgrass Causeway and read the tide-readers' notice; Glimmer, the Undertow and Haluna are
## already read) and chooses its Codex row, then Places and the Saltgrass Causeway, so the page
## shows as it does in play ("New" on the Shell Shrine still) and the player's save never moves a
## baseline.

const HEROES: Array[StringName] = [&"rhen", &"asha", &"toma"]
const NAMES := {&"rhen": "CHAR_RHEN", &"asha": "CHAR_ASHA", &"toma": "CHAR_TOMA"}
const MAP_ZONE := &"ch02/haluna"
const FLAGS: Array[StringName] = [
	&"ch02_met_asha",
	&"ch02_tideline_won",
	&"ch03_causeway_arrived",
	&"ch03_shrine_door_open",
	&"codex_causeway_notice_found",
	&"codex_glimmer_read",
	&"codex_undertow_read",
	&"codex_haluna_read",
]
const CATEGORY := &"places"
const ENTRY := &"saltgrass_causeway"

var menu: FieldMenu
var flags: Dictionary = {}


func _ready() -> void:
	var back := ColorRect.new()
	back.set_anchors_preset(Control.PRESET_FULL_RECT)
	back.color = get_theme_color(&"panel_low", HymnThemeBuilder.PALETTE_TYPE)
	back.color.a = 1.0
	add_child(back)
	for f in FLAGS:
		flags[f] = true
	var model := FieldMenuModel.new(GameStateData.new(), HEROES, NAMES)
	model.map = MapModel.new(MAP_ZONE, Vector3.INF, 0.0, func(_f: StringName) -> bool: return false)
	model.codex = CodexModel.new(
		{}, func(f: StringName) -> bool: return flags.has(f), func(f: StringName) -> void: flags[f] = true
	)
	menu = (load(FieldMenu.SCENE_PATH) as PackedScene).instantiate() as FieldMenu
	menu.pause_tree = false
	menu.configure(model)
	add_child(menu)
	for i in FieldMenuModel.ROOT_IDS.find(FieldMenuModel.ROW_CODEX):
		menu.handle_input(_ev(&"ui_down"))
	menu.accept()  # the codex, over the field menu
	var codex := menu.codex_menu
	for c in codex.model.category_rows:
		if StringName(str(c["id"])) == CATEGORY:
			break
		codex.handle_input(_ev(&"ui_down"))
	codex.handle_input(_ev(&"ui_accept"))  # into Places: Haluna (read)
	for e in codex.model.entries_in(CATEGORY):
		if e["id"] == ENTRY:
			break
		codex.handle_input(_ev(&"ui_down"))


func _ev(action: StringName) -> InputEventAction:
	var ev := InputEventAction.new()
	ev.action = action
	ev.pressed = true
	return ev
