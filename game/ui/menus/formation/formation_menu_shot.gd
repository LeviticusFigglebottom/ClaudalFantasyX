class_name FormationMenuShot
extends Control
## Capture driver for the Formation page (M2-MNU-07, tests/screenshots/shots.json). It opens
## FormationMenu on a fixed scratch save, so the player's save never moves a baseline: Rhen, Asha
## and Toma in the active line, Ysolde in reserve; Rhen wounded, Asha fallen, Toma low on MP. Toma
## is picked and the cursor rests on Asha: the plan says they change places in the active line,
## and the warning says Asha has fallen.

const ACTIVE: Array[StringName] = [&"rhen", &"asha", &"toma"]
const RESERVE: Array[StringName] = [&"ysolde"]
const VITALS := {"rhen": {"hp": 151}, "asha": {"hp": 0}, "toma": {"mp": 4}}
## Toma's place in the active line (picked), and Asha's (the cursor).
const PICK_INDEX := 2
const CURSOR_INDEX := 1

var menu: FormationMenu


func _ready() -> void:
	var back := ColorRect.new()
	back.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	back.color = get_theme_color(&"panel_low", HymnThemeBuilder.PALETTE_TYPE)
	back.color.a = 1.0
	add_child(back)
	var state := GameStateData.new()
	state.party_ids = ACTIVE.duplicate()
	state.reserve_ids = RESERVE.duplicate()
	state.party_vitals = VITALS.duplicate(true)
	menu = FormationMenu.create(PartySheet.new(state, ACTIVE + RESERVE))
	menu.pause_tree = false
	add_child(menu)
	for _i in PICK_INDEX:
		menu.handle_input(_ev(&"ui_down"))
	menu.accept()  # Toma
	for _i in PICK_INDEX - CURSOR_INDEX:
		menu.handle_input(_ev(&"ui_up"))  # Asha


func _ev(action: StringName) -> InputEventAction:
	var ev := InputEventAction.new()
	ev.action = action
	ev.pressed = true
	return ev
