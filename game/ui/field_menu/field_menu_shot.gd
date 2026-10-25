class_name FieldMenuShot
extends Control
## Capture driver for the field menu shots (M2-UI-04, tests/screenshots/shots.json). It opens
## FieldMenu on a fixed scratch save, so the player's save never moves a baseline:
##   - "root": the root page, the cursor on Swell (its line under the right page);
##   - "swell_modes": Rhen's fill modes with Tether unlocked and Wake in use, the cursor on Tether.
## The modes themselves come from swell.json (BattleSwellCarry), as in play. The party stands in
## Haluna (a MapModel on no flags), so the Map row (M2-UI-18) is on, as it is there in play. The root's
## Last saved block (M2-MNU-300) reads a fixed autosave at Haluna (FixedSaves), at UTC.

const HEROES: Array[StringName] = [&"rhen", &"asha", &"toma"]
const NAMES := {&"rhen": "CHAR_RHEN", &"asha": "CHAR_ASHA", &"toma": "CHAR_TOMA"}
const SAVED_SWELL := {"unlocked": ["ballast", "wake", "tether"]}
const RHEN_MODE := &"wake"
const MAP_ZONE := &"ch02/haluna"
const SAVED_LOCATION_KEY := "LOCATION_CH02_HALUNA"
## 2026-10-24 14:05 UTC.
const SAVED_AT := 1792850700

## Which view to stage: &"root" or &"swell_modes".
@export var view: StringName = &"root"

var menu: FieldMenu


## One readable autosave, as SaveSystem.slot_info reports it (slot_info and list_slots only).
class FixedSaves:
	extends Node

	func slot_info(slot: int) -> Dictionary:
		if slot != SaveSystem.AUTOSAVE_SLOT:
			return {"slot": slot, "status": SaveSystem.STATUS_EMPTY}
		return {"slot": slot, "status": SaveSystem.STATUS_OK, "saved_at": SAVED_AT, "location_key": SAVED_LOCATION_KEY}

	func list_slots(slots: Array[int]) -> Array[Dictionary]:
		var out: Array[Dictionary] = []
		for s in slots:
			out.append(slot_info(s))
		return out


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
	model.map = MapModel.new(MAP_ZONE, Vector3.INF, 0.0, func(_f: StringName) -> bool: return false)
	var saves := FixedSaves.new()
	add_child(saves)
	model.save_system = saves
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
