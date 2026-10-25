class_name LatticeMenuShot
extends Control
## Capture driver for the Lattice page shots (M2-MNU-01, tests/screenshots/shots.json). It opens
## LatticeMenu on a fixed scratch save, so the player's save never moves a baseline. Every step is
## taken through LatticeMenuModel (the real rules), never written into the save by hand:
##   - Rhen woke the first two nodes of his spine (Agility, Strength), Asha and Toma one each;
##   - "path": Rhen's cursor on rh_05, three nodes on, the planned walk and its cost on show;
##   - "activate": Rhen has walked onto Kick Off the Wall (rh_03), the confirm asking to wake it;
##   - "overview" (M3-MNU-04): the "path" state with the whole board framed, every hero named.

const HEROES: Array[StringName] = [&"rhen", &"asha", &"toma"]
const FACETS := {"facet_speed": 3, "facet_power": 2, "facet_mind": 2, "facet_ability": 1, "facet_key_1": 1}
const MOVEMENT := 7
## Each hero's walk: node ids to step onto in turn, waking each one.
const WALKS := {&"rhen": [&"rh_01", &"rh_02"], &"asha": [&"as_01"], &"toma": [&"ts_01"]}
const PATH_CURSOR := &"rh_05"
const ACTIVATE_AT := &"rh_03"

## Which view to stage: &"path", &"activate" or &"overview".
@export var view: StringName = &"path"

var menu: LatticeMenu


func _ready() -> void:
	var back := ColorRect.new()
	back.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	back.color = get_theme_color(&"panel_low", HymnThemeBuilder.PALETTE_TYPE)
	back.color.a = 1.0
	add_child(back)
	var state := GameStateData.new()
	state.inventory = FACETS.duplicate()
	var sheet := PartySheet.new(state, HEROES)
	var model := LatticeMenuModel.new(sheet)
	for cid: StringName in HEROES:
		model.show_hero(cid)
		model.traveler().movement_points = MOVEMENT
		for nid: Variant in WALKS[cid]:
			model.act(nid)  # walk there
			model.act(nid)  # and wake it
	if view == &"activate":
		model.show_hero(&"rhen")
		model.act(ACTIVATE_AT)
	menu = LatticeMenu.create(sheet)
	menu.pause_tree = false
	add_child(menu)
	if view == &"activate":
		menu.set_cursor(ACTIVATE_AT, false)
		menu.request_act()
	else:
		menu.set_cursor(PATH_CURSOR, false)
		if view == &"overview":
			menu.toggle_overview(false)  # M3-MNU-04: the whole board, every hero named
