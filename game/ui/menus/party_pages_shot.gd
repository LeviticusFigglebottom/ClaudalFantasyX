class_name PartyPagesShot
extends Control
## Capture driver for the Items and Status pages (M2-MNU-03, tests/screenshots/shots.json). It
## opens the page over a PartySheet on a fixed scratch save, so the player's save never moves a
## baseline:
##   - &"items": a mixed bag sorted by kind, the cursor on a Reef Draught (its description);
##   - &"items_use": a Salt Tonic's hero picker, Rhen wounded, Asha fallen, Toma low on MP and
##     poisoned, the cursor on Rhen with "Rhen: HP a → b" under it;
##   - &"items_key": the Key Items view (M3-MNU-03), the cursor on the second key item;
##   - &"status": Rhen with Coral-Bitten Hooks (two abilities) and a Reefline Harness, five Lattice
##     nodes woken, a part-filled Swell gauge on Wake and a carried Poison.

const HEROES: Array[StringName] = [&"rhen", &"asha", &"toma"]
const BAG := {
	"salt_tonic": 6,
	"reef_draught": 2,
	"quiet_tea": 3,
	"bitterleaf": 1,
	"relighting_wick": 1,
	"ember_pot": 2,
	"crab_carapace": 4,
	"tide_pearl": 1,
	"facet_power": 3,
	"facet_speed": 1,
	"brass_lantern": 1,
	"net_float_charm": 1,
	"gauge_wheel_brass": 1,
	"kell_wick": 1,
}
const VITALS := {
	"rhen": {"hp": 151, "swell": 46, "swell_mode": "wake"},
	"asha": {"hp": 0},
	"toma": {"hp": 388, "mp": 4, "statuses": ["poison"]},
}
const STATUS_VITALS := {"rhen": {"hp": 377, "mp": 15, "swell": 46, "swell_mode": "wake", "statuses": ["poison"]}}
const SAVED_SWELL := {"unlocked": ["ballast", "wake", "tether"]}
const WEAPON := &"rhen_coral_hooks"
const WEAPON_EXTRA := &"steady_arm"
const ARMOR := &"rhen_reefline_harness"
## Customized: no poison ward, so the carried Poison still shows (a ward would refuse it, as in battle).
const ARMOR_ABILITIES: Array[StringName] = [&"hard_carapace", &"deep_lungs"]
## How many stat or ability nodes Rhen has woken, nearest his start first, and the points banked.
const WOKEN := 5
const MOVEMENT := 3

## Which page to stage: &"items", &"items_use", &"items_key" or &"status".
@export var view: StringName = &"items"

var page: FieldSubmenu


func _ready() -> void:
	var back := ColorRect.new()
	back.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	back.color = get_theme_color(&"panel_low", HymnThemeBuilder.PALETTE_TYPE)
	back.color.a = 1.0
	add_child(back)
	var state := GameStateData.new()
	state.party_ids = HEROES.duplicate()
	state.swell = SAVED_SWELL.duplicate(true)
	state.inventory = BAG.duplicate(true)
	state.party_vitals = (STATUS_VITALS if view == &"status" else VITALS).duplicate(true)
	var sheet := PartySheet.new(state, HEROES)
	if view == &"status":
		_dress_rhen(sheet)
		var status := StatusMenu.create(sheet)
		status.pause_tree = false
		add_child(status)
		page = status
		return
	var items := ItemsMenu.create(sheet)
	items.pause_tree = false
	ItemsMenu.session_sort = ItemsMenuModel.SORT_KIND
	add_child(items)
	page = items
	if view == &"items_use":
		items.accept()  # Salt Tonic, first in the bag: the picker, Rhen first
	elif view == &"items_key":
		items.handle_input(_ev(&"ui_page_down"))  # Key Items
		items.handle_input(_ev(&"ui_down"))
	else:
		items.handle_input(_ev(&"ui_down"))  # Reef Draught


## Rhen's gear and Lattice for the status shot (the same calls the Equip and Lattice pages make).
func _dress_rhen(sheet: PartySheet) -> void:
	var bag := sheet.goods.equipment
	var weapon := bag.add_piece(WEAPON)
	bag.set_slot(weapon, bag.first_empty_slot(weapon), WEAPON_EXTRA)
	bag.equip(&"rhen", weapon)
	var armor := bag.add_piece(ARMOR)
	for i in ARMOR_ABILITIES.size():
		bag.set_slot(armor, i, ARMOR_ABILITIES[i])
	bag.equip(&"rhen", armor)
	var lattice := sheet.lattice
	var t := lattice.traveler(&"rhen")
	var woken := 0
	var queue: Array[StringName] = [t.position]
	var seen := {t.position: true}
	while not queue.is_empty() and woken < WOKEN:
		var nid: StringName = queue.pop_front()
		var n := lattice.board.lattice_node(nid)
		if n != null and n.is_activatable() and not t.activated.has(nid):
			t.activated[nid] = true
			woken += 1
		for next in lattice.board.neighbors(nid):
			var nn := lattice.board.lattice_node(next)
			if not seen.has(next) and nn != null and not nn.is_gate():
				seen[next] = true
				queue.append(next)
	t.movement_points = MOVEMENT
	sheet.save_lattice()


func _ev(action: StringName) -> InputEventAction:
	var ev := InputEventAction.new()
	ev.action = action
	ev.pressed = true
	return ev
