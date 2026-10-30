class_name ZoneMapShot
extends Control
## Capture driver for the zone map shots (M2-UI-18, tests/screenshots/shots.json). It opens the
## field menu on a scratch save, with a MapModel on fixed flags and a fixed player, and chooses its
## Map row, so the page shows as it does in play and the player's save never moves a baseline:
##   - "haluna": Haluna after supper at Neme's (the objective: the save shrine), the player just
##     up from the beach facing inland, the cursor on the shrine (the objective's place);
##   - "shrine": the Shell Shrine trial (the objective: the inner pool), the player by the
##     entrance facing in, the side pool drained (its errand listed);
##   - "underway" (M3-UI-04): Ch1's Underway after the glassfry shoal, the player in the galleries
##     facing north, the objective the stairwell lip, the bell-room hinge left as an errand;
##   - "keth_pass", "lowlight", "ansedra" (M3-UI-206): Act II's greyboxes where the map reads hardest (the
##     pass's raised landings and flights, the temple's drowned shaft, the city's domes on the lagoon), the
##     player at each zone's way in.

const HEROES: Array[StringName] = [&"rhen", &"asha", &"toma"]
const NAMES := {&"rhen": "CHAR_RHEN", &"asha": "CHAR_ASHA", &"toma": "CHAR_TOMA"}
const VIEWS := {
	&"haluna":
	{
		"zone": &"ch02/haluna",
		"at": Vector3(-8.0, 0.0, 6.0),
		"yaw": PI * 0.5,
		"flags": [&"ch02_met_asha", &"ch02_tideline_won", &"ch02_ate_at_nemes"],
	},
	&"shrine":
	{
		"zone": &"ch03/shell_shrine",
		"at": Vector3(-10.5, 0.0, 1.5),
		"yaw": -PI * 0.5,
		"flags": [&"ch03_side_pool_drained"],
	},
	&"underway":
	{
		"zone": &"ch01/oruvel_underway",
		"at": Vector3(80.0, 0.0, 0.0),
		"yaw": 0.0,
		"flags": [&"ch01_started", &"ch01_saw_bell_room", &"ch01_wickfry_won"],
	},
	&"keth_pass": {"zone": &"ch12/keth_pass", "at": Vector3(0.0, 0.0, 3.0), "yaw": 0.0, "flags": [&"ch12_started"]},
	&"lowlight":
	{
		"zone": &"ch11/lowlight",
		"at": Vector3(2.0, 0.0, 0.0),
		"yaw": -PI * 0.5,
		"flags": [&"ch11_started", &"ch11_reached_lowlight"]
	},
	&"ansedra": {"zone": &"ch13/ansedra", "at": Vector3(0.0, 0.0, 12.0), "yaw": 0.0, "flags": [&"ch13_started"]},
}

## Which view to stage: a VIEWS key.
@export var view: StringName = &"haluna"

var menu: FieldMenu


func _ready() -> void:
	var back := ColorRect.new()
	back.set_anchors_preset(Control.PRESET_FULL_RECT)
	back.color = get_theme_color(&"panel_low", HymnThemeBuilder.PALETTE_TYPE)
	back.color.a = 1.0
	add_child(back)
	var v: Dictionary = VIEWS.get(view, VIEWS[&"haluna"])
	var flags: Array = v["flags"]
	var model := FieldMenuModel.new(GameStateData.new(), HEROES, NAMES)
	model.map = MapModel.new(v["zone"], v["at"], v["yaw"], func(f: StringName) -> bool: return flags.has(f))
	menu = (load(FieldMenu.SCENE_PATH) as PackedScene).instantiate() as FieldMenu
	menu.pause_tree = false
	menu.configure(model)
	add_child(menu)
	for i in FieldMenuModel.ROOT_IDS.find(FieldMenuModel.ROW_MAP):
		menu.handle_input(_ev(&"ui_down"))
	menu.accept()  # the map page, the cursor on the objective's place


func _ev(action: StringName) -> InputEventAction:
	var ev := InputEventAction.new()
	ev.action = action
	ev.pressed = true
	return ev
