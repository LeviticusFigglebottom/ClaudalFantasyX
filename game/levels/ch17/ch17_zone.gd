class_name Ch17Zone
extends Ch05Zone
## Ch17's greybox zone root, `ch17/hollowmere` (first built for Ch15's dawn, M4-C15-02; act_outline.md Ch15, Ch17):
## the Saltwright town. It keeps Ch05Zone's calls (place_actor, give_if, the layout's light "variants", KitCollision's
## ramps) and Ch01Zone's (rest, give, hide_block, show_block) for the story its beat sheet brings; the layout comes
## from tools/act1/ch15_16_greybox.py.
##
## Act III (M5-A3P-1001; act3_ch17.md §2 B05, B10): the held inputs. Inside a scene, between <<event hold_input <id>>>
## and <<event hold_input_end>>, the scene's time runs only while the player holds the field's interact action (the
## ledger's page-turns, the first lamp's three holds), as Ch9's Ebbing does. Data: ch17_field.json "hold".

const CH17_FIELD_PATH := "res://game/data/flow/ch17_field.json"
const KEY_CH17_HOLD := "hold"

## The ledger's and the first lamp's held input.
var hold_gate: CutsceneHoldGate
## ch17_field.json.
var ch17_field: Dictionary = {}


func build() -> void:
	if hold_gate != null:
		return
	super()
	ch17_field = read_json(CH17_FIELD_PATH)
	hold_gate = CutsceneHoldGate.new()
	hold_gate.name = "HoldGate"
	add_child(hold_gate)


func _ready() -> void:
	super()
	hold_gate.setup(story.sequencer, ch17_field.get(KEY_CH17_HOLD, {}))
