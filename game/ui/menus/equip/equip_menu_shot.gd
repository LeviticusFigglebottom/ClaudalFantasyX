class_name EquipMenuShot
extends Control
## Capture driver for the Equip page shots (M2-MNU-02, tests/screenshots/shots.json). It opens
## EquipMenu on a fixed scratch save, so the player's save never moves a baseline: Rhen, Asha and
## Toma in their starting gear, the Net-Rack Forge's Coral Hooks (one empty slot) and Reefline
## Harness in the pack, one Tide Pearl and six Bitterleaf.
##   - "equip": Rhen's weapons, the cursor on the Coral Hooks: Strength up, Ember Edge gained;
##   - "customize": Rhen wearing the Coral Hooks, Customize on its empty slot, the cursor on Tide
##     Edge (4 Tide Pearls needed, 1 held, 3 short).

const HEROES: Array[StringName] = [&"rhen", &"asha", &"toma"]
const FORGE_WEAPON := &"rhen_coral_hooks"
const FORGE_ARMOR := &"rhen_reefline_harness"
const ITEMS := {&"tide_pearl": 1, &"bitterleaf": 6}

## Which view to stage: &"equip" or &"customize".
@export var view: StringName = &"equip"

var menu: EquipMenu


func _ready() -> void:
	var back := ColorRect.new()
	back.set_anchors_preset(Control.PRESET_FULL_RECT)
	back.color = get_theme_color(&"panel_low", HymnThemeBuilder.PALETTE_TYPE)
	back.color.a = 1.0
	add_child(back)
	var state := GameStateData.new()
	var sheet := PartySheet.new(state, HEROES)
	for cid in HEROES:
		sheet.goods.equipment.grant_starting(cid)
	var hooks := sheet.goods.equipment.add_piece(FORGE_WEAPON)
	sheet.goods.equipment.add_piece(FORGE_ARMOR)
	for iid: StringName in ITEMS:
		sheet.goods.inventory.add(iid, int(ITEMS[iid]))
	if view == &"customize":
		sheet.goods.equipment.equip(&"rhen", hooks)
	menu = EquipMenu.create(sheet)
	menu.pause_tree = false
	add_child(menu)
	menu.accept()  # Rhen's gear
	if view == &"customize":
		menu.handle_input(_ev(&"ui_down"))  # the hooks' Ember Edge
		menu.handle_input(_ev(&"ui_down"))  # the empty slot
		menu.accept()  # Customize: Tide Edge first
		return
	menu.accept()  # the weapons, the cursor on the worn Salvage Hooks
	menu.handle_input(_ev(&"ui_down"))  # the Coral Hooks


func _ev(action: StringName) -> InputEventAction:
	var ev := InputEventAction.new()
	ev.action = action
	ev.pressed = true
	return ev
