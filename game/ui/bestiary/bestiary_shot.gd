class_name BestiaryShot
extends Control
## Capture driver for the bestiary_menu shot (M2-UI-02, tests/screenshots/shots.json). It opens
## BestiaryMenu on a fixed log over the frozen capture enemies (battle_fixtures.json, fixture
## "read_panel", which adds their lore keys), so neither the player's save nor a rebalance of
## enemies.json can move the baseline: a foe defeated but never Read, two Read foes, and an id the
## table no longer lists (kept in the log, not shown). The Lantern Eel's page is on show.

const FIXTURE := &"read_panel"
const LOG := {
	"reef_crab": {"read": false, "defeated": 2},
	"lantern_eel": {"read": true, "defeated": 1},
	"gull_harrier": {"read": true, "defeated": 4},
	"drowned_bell_old": {"read": true, "defeated": 1},
}
const SHOWN := 1

var menu: BestiaryMenu


func _ready() -> void:
	var back := ColorRect.new()
	back.set_anchors_preset(Control.PRESET_FULL_RECT)
	back.color = get_theme_color(&"panel_low", HymnThemeBuilder.PALETTE_TYPE)
	back.color.a = 1.0
	add_child(back)
	var fx := BattleFixture.load_fixture(FIXTURE)
	var book := Bestiary.new(LOG.duplicate(true))
	menu = (load(BestiaryMenu.SCENE_PATH) as PackedScene).instantiate() as BestiaryMenu
	menu.pause_tree = false
	menu.configure(BestiaryMenuModel.new(book, fx.db.enemies))
	add_child(menu)
	menu.select(SHOWN)
