class_name Ch17Zone
extends Ch05Zone
## Ch17's greybox zone root, `ch17/hollowmere` (first built for Ch15's dawn, M4-C15-02; act_outline.md Ch15, Ch17):
## the Saltwright town. It keeps Ch05Zone's calls (place_actor, give_if, the layout's light "variants", KitCollision's
## ramps) and Ch01Zone's (rest, give, hide_block, show_block) for the story its beat sheet brings; the layout comes
## from tools/act2/ch15_16_greybox.py.
## M5-A3P-1001: the zone is Ch15's and Ch17's. Once Act II is over (ch16_act_two_complete) its story reads Ch17's
## chapter file (chapter_path, set before the ZoneStory child is ready), and Ch9's held input plays the ledger's
## page-turns and the first lamp (a CutsceneHoldGate; data: ch17_field.json "hold").

const CH17_CHAPTER := "res://game/data/flow/chapters/ch17.json"
const CH17_FIELD_PATH := "res://game/data/flow/ch17_field.json"
const ACT_TWO_DONE := &"ch16_act_two_complete"
const KEY_CH17_HOLD := "hold"

## The ledger's and the first lamp's held input.
var hold_gate: CutsceneHoldGate


func _enter_tree() -> void:
	if bool(Game.get_flag(ACT_TWO_DONE)):
		chapter_path = CH17_CHAPTER
	super()


func build() -> void:
	if hint != null:
		return
	super()
	hold_gate = CutsceneHoldGate.new()
	hold_gate.name = "HoldGate"
	add_child(hold_gate)


func _ready() -> void:
	super()
	if hold_gate != null:
		hold_gate.setup(story.sequencer, read_json(CH17_FIELD_PATH).get(KEY_CH17_HOLD, {}))
