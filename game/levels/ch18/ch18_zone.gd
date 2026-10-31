class_name Ch18Zone
extends Ch05Zone
## Ch18's greybox zone root, `ch18/kite` (M5-A3P-1004; act3_ch18.md): Dace's hull flying, the Kite. It keeps
## Ch05Zone's calls (place_actor, give_if, the layout's light "variants", KitCollision's ramps) and Ch01Zone's (rest,
## give, hide_block, show_block); the layout comes from tools/act3/ch18_greybox.py. Ch9's held input plays the maiden
## flight's three lifts (a CutsceneHoldGate; data: ch18_field.json "hold").
## M5-A3P-1015: the Ending is played aboard. Once the Unbinding is done (ch21_unbound) its story reads the Ending's
## chapter file (chapter_path, set before the ZoneStory child is ready), and the held input takes the strain as Liss
## brings the Kite down by hand.

const CH18_FIELD_PATH := "res://game/data/flow/ch18_field.json"
const KEY_CH18_HOLD := "hold"
const ENDING_CHAPTER := "res://game/data/flow/chapters/ending.json"
const UNBOUND := &"ch21_unbound"

## The maiden flight's held input.
var hold_gate: CutsceneHoldGate


func _enter_tree() -> void:
	if bool(Game.get_flag(UNBOUND)):
		chapter_path = ENDING_CHAPTER
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
		hold_gate.setup(story.sequencer, read_json(CH18_FIELD_PATH).get(KEY_CH18_HOLD, {}))
