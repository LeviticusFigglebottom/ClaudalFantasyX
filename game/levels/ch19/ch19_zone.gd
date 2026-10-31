class_name Ch19Zone
extends Ch05Zone
## Ch19's greybox zone root, `ch19/iskarra_spire` (M5-A3P-1007; act3_ch19.md): drowned Iskarra's plaza and the
## Lamp Spire. It keeps Ch05Zone's calls (place_actor, give_if, the layout's light "variants", KitCollision's ramps) and
## Ch01Zone's (rest, give, hide_block, show_block); the layout comes from tools/act3/ch19_greybox.py. Ch9's held input
## plays the hitch (tie, load, pull) and the engine's three levers (a CutsceneHoldGate; data: ch19_field.json "hold").

const CH19_FIELD_PATH := "res://game/data/flow/ch19_field.json"
const KEY_CH19_HOLD := "hold"

## The hitch's and the engine's held input.
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
		hold_gate.setup(story.sequencer, read_json(CH19_FIELD_PATH).get(KEY_CH19_HOLD, {}))
