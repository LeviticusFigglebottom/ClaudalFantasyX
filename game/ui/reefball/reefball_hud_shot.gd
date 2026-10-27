class_name ReefballHudShot
extends Control
## Capture driver for the Reefball HUD shots (M3-UI-01, tests/screenshots/shots.json), over a
## plain night backdrop (the arena look is rendering's, game/levels/_tests/reefball/):
##   reefball_hud_choice - the Tidecup opening round on the player's first contact with a pass on
##                         offer, the cursor on a pass and its preview open;
##   reefball_hud_goal   - the same match played by the AI on both sides until the first float comes
##                         up, held just after it (the banner, the new score, the kickoff positions).
## The match is seeded, and the HUD is driven synchronously (pacing 0, flush()), so two captures
## are the same picture.

enum Mode { CHOICE, GOAL }

const MATCH := &"tidecup_opening"
const SEED := 7
const PLAYER_PROFILE := &"smart"
## Steps a capture may take before it gives up (a seeded match scores long before this).
const MAX_STEPS := 400

@export var mode := Mode.CHOICE
## False keeps the shared UiSettings a test set (the text-size and aspect walks); captures use fresh ones.
var fresh_settings := true

var match_state: ReefballMatch
var hud: ReefballHud
var controller: ReefballHudController


func _ready() -> void:
	var back := ColorRect.new()
	back.set_anchors_preset(Control.PRESET_FULL_RECT)
	back.color = get_theme_color(&"outline", HymnThemeBuilder.PALETTE_TYPE)
	add_child(back)
	if fresh_settings:
		UiSettings.set_shared(UiSettings.new())
	var db := ReefballDB.load_default()
	match_state = ReefballMatch.new()
	match_state.setup(db, MATCH, SEED)
	hud = ReefballHud.new()
	add_child(hud)
	controller = ReefballHudController.new()
	controller.pacing_scale = 0.0
	controller.manual = true
	add_child(controller)
	if mode == Mode.GOAL:
		controller.player_ai = ReefballAI.new(db.ai_profiles.get(PLAYER_PROFILE, {}))
	controller.start(match_state, hud)
	if mode == Mode.CHOICE:
		to_pass_choice()
	else:
		to_first_goal()


## Plays until the player chooses with a pass on offer, and puts the cursor on the first pass.
func to_pass_choice() -> bool:
	for _i in MAX_STEPS:
		if hud.is_choosing():
			for i in hud.options.size():
				if StringName(hud.options[i]["action"]) == ReefballMatch.PASS:
					hud.set_cursor(i)
					return true
			hud.choose(0)
		elif not controller.flush():
			return false
	return false


## Plays (the AI on both sides) until a float has just come up.
func to_first_goal() -> bool:
	for _i in MAX_STEPS:
		if hud.banner_shown():
			return true
		if not controller.flush():
			return false
	return false
