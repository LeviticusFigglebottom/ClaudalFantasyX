class_name FieldMenuShot
extends Control
## Capture driver for the field menu shots (M2-UI-04, tests/screenshots/shots.json). It opens
## FieldMenu on a fixed scratch save, so the player's save never moves a baseline:
##   - "root": the root page, the cursor on Swell (its line under the right page);
##   - "swell_modes": Rhen's fill modes with Tether unlocked and Wake in use, the cursor on Tether.
## The modes themselves come from swell.json (BattleSwellCarry), as in play.

const HEROES: Array[StringName] = [&"rhen", &"asha", &"toma"]
const NAMES := {&"rhen": "CHAR_RHEN", &"asha": "CHAR_ASHA", &"toma": "CHAR_TOMA"}
const SAVED_SWELL := {"unlocked": ["ballast", "wake", "tether"]}
const RHEN_MODE := &"wake"

## Which view to stage: &"root" or &"swell_modes".
@export var view: StringName = &"root"

var menu: FieldMenu


func _ready() -> void:
	var back := ColorRect.new()
	back.set_anchors_preset(Control.PRESET_FULL_RECT)
	back.color = get_theme_color(&"panel_low", HymnThemeBuilder.PALETTE_TYPE)
	back.color.a = 1.0
	add_child(back)
	var state := GameStateData.new()
	state.swell = SAVED_SWELL.duplicate(true)
	var model := FieldMenuModel.new(state, HEROES, NAMES)
	model.choose_mode(&"rhen", RHEN_MODE)
	menu = (load(FieldMenu.SCENE_PATH) as PackedScene).instantiate() as FieldMenu
	menu.pause_tree = false
	menu.configure(model)
	add_child(menu)
	for i in FieldMenuModel.ROOT_IDS.find(FieldMenuModel.ROW_SWELL):
		menu.handle_input(_ev(&"ui_down"))  # down to Swell
	if view != &"swell_modes":
		return
	menu.accept()  # the heroes, Rhen first
	menu.accept()  # Rhen's modes, the cursor on Wake (in use)
	menu.handle_input(_ev(&"ui_down"))  # Tether, the next mode in swell.json


func _ev(action: StringName) -> InputEventAction:
	var ev := InputEventAction.new()
	ev.action = action
	ev.pressed = true
	return ev
