class_name BattlePauseShot
extends Node
## Capture driver for the battle pause (M2-MNU-04, tests/screenshots/shots.json "battle_pause"):
## the battle sandbox plays its `player_preview` capture script (Rhen's Skills page, deterministic
## fixture), then the pause page opens over it without pausing the tree, so the capture's settle
## frames still run. The page is what the pause action opens in play.

const SANDBOX := "res://game/battle/scene/battle_sandbox.tscn"
## The sandbox capture state under the page.
const UNDER_STATE := &"player_preview"
## Frames to wait at most for the capture script to reach the player's turn.
const MAX_WAIT_FRAMES := 20

var controller: BattleController
var menu: BattlePauseMenu


func _ready() -> void:
	controller = (load(SANDBOX) as PackedScene).instantiate() as BattleController
	controller.scripted_state = UNDER_STATE
	add_child(controller)
	for i in MAX_WAIT_FRAMES:
		if controller.state != BattleController.STATE_IDLE and controller.state != BattleController.STATE_BUSY:
			break
		await get_tree().process_frame
	menu = BattlePauseMenu.create()
	menu.pause_tree = false
	FieldSubmenu.mount(menu, controller)
