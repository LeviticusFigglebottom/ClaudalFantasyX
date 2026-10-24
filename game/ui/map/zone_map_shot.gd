class_name ZoneMapShot
extends Control
## Capture driver for the zone map shots (M2-UI-18, tests/screenshots/shots.json). It opens the
## field menu on a scratch save, with a MapModel on fixed flags and a fixed player, and chooses its
## Map row, so the page shows as it does in play and the player's save never moves a baseline:
##   - "haluna": Haluna after supper at Neme's (the objective: the save shrine), the player just
##     up from the beach facing inland, the cursor on the shrine (the objective's place);
##   - "shrine": the Shell Shrine trial (the objective: the inner pool), the player by the
##     entrance facing in, the side pool drained (its errand listed).

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
}

## Which view to stage: &"haluna" or &"shrine".
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
