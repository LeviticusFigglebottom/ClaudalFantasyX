class_name TidecupMatch
extends Node
## Ch7's Reefball match, the story's side of the seam (M3-C07-1206; act1_ch07.md §5; docs/kb/tech/
## chapter_flow.md "Ch7"). The naming beat hands off here (a `scene` step); everything inside the match is
## the Reefball engine's (M3-RBL-01) and its HUD's (M3-UI-01); this node only frames it:
##   - builds the match from game/data/flow/ch07_tidecup.json (match id, seed);
##   - plays it through the HUD and its controller when the HUD is in the build, loaded by path so the
##     chapter runs before the UI track's branch lands (the scripts are duck-typed until then);
##   - else, or with `autoplay`, lets the engine's AI play both sides at once (a headless fallback);
##   - at the end sets the played flag always and the won flag on a win only, gives the win reward, and
##     goes back to the galleries' catch-pool. The result never branches the story.

signal finished(outcome: StringName)

const DATA_PATH := "res://game/data/flow/ch07_tidecup.json"
const HUD_SCRIPT := "res://game/ui/reefball/reefball_hud.gd"
const CONTROLLER_SCRIPT := "res://game/ui/reefball/reefball_hud_controller.gd"
const MATCH_OVER := &"match_over"

## Lets the AI play both sides at once (tests; the build without the HUD).
@export var autoplay := false

var data: Dictionary = {}
var db: ReefballDB
var match_state: ReefballMatch
## WIN, LOSS or DRAW once the match is over (ReefballMatch's, from the player side's view).
var outcome: StringName = &""
var hud: Node
var controller: Node

var _done := false


func _ready() -> void:
	data = GreyboxZone.read_json(DATA_PATH)
	db = ReefballDB.load_default()
	match_state = ReefballMatch.new()
	if not match_state.setup(db, StringName(str(data.get("match", ""))), int(data.get("seed", 0))):
		end_match(ReefballMatch.LOSS)
		return
	if autoplay or not has_hud():
		play_out()
	else:
		_start_hud()


## True when the UI track's Reefball HUD is in the build.
static func has_hud() -> bool:
	return ResourceLoader.exists(HUD_SCRIPT) and ResourceLoader.exists(CONTROLLER_SCRIPT)


## Plays the whole match at once, the engine's AI on both sides, and ends it.
func play_out() -> void:
	var player := ReefballAI.new(db.ai_profiles.get(StringName(str(data.get("autoplay_profile", ""))), {}))
	match_state.begin()
	for _i in int(data.get("max_contacts", 0)):
		if match_state.finished:
			break
		match_state.play_ai_contact(player if match_state.is_player_contact() else null)
	end_match(match_state.outcome if match_state.finished else ReefballMatch.LOSS)


func _start_hud() -> void:
	hud = (load(HUD_SCRIPT) as GDScript).new()
	controller = (load(CONTROLLER_SCRIPT) as GDScript).new()
	add_child(hud)
	add_child(controller)
	controller.connect(MATCH_OVER, func(result: StringName, _score: Array) -> void: end_match(result))
	controller.call(&"start", match_state, hud)


## Ends the match with `result`: the flags, the reward, and the way back (once; the HUD and the fallback call it).
func end_match(result: StringName) -> void:
	if _done:
		return
	_done = true
	outcome = result
	Game.set_flag(StringName(str(data.get("played_flag", ""))))
	if result == ReefballMatch.WIN:
		Game.set_flag(StringName(str(data.get("won_flag", ""))))
		var reward: Dictionary = data.get("win_reward", {})
		_give(reward.get("items", {}), int(reward.get("lume", 0)))
	finished.emit(result)
	var to: Dictionary = data.get("return", {})
	FlowRouting.go_to(StringName(str(to.get("location", ""))), StringName(str(to.get("spawn", ""))))


func _give(items: Dictionary, lume: int) -> void:
	var goods := PartyGoods.from_state(ItemDB.load_default(), Game.state)
	for id: Variant in items:
		goods.inventory.add(StringName(str(id)), int(items[id]))
	goods.wallet.earn(lume)
