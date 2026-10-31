class_name Ch10Zone
extends Ch05Zone
## Ch10's greybox zone root, `ch10/ossa_fen` and `ch10/reedhollow` (M4-C10-02; act_outline.md Ch10, act1_ch09.md
## §10): the first chapter of Act II. It keeps Ch05Zone's calls (place_actor, give_if, the layout's light "variants")
## and Ch01Zone's (rest, give, hide_block, show_block) for the story the beat sheet (M4-C10-01) brings; the layouts
## come from tools/act2/ch10_greybox.py.
## M5-A3P-1004: Ch18's farewell-tide, taught at Reedhollow, holds its turn_back input (Ch9's CutsceneHoldGate; data:
## ch18_field.json "hold").

const CH18_FIELD_PATH := "res://game/data/flow/ch18_field.json"
const KEY_CH18_HOLD := "hold"

## The farewell-tide's held input.
var hold_gate: CutsceneHoldGate


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
		hold_gate.setup(story.sequencer, read_json(CH18_FIELD_PATH).get(KEY_CH18_HOLD, {}))
