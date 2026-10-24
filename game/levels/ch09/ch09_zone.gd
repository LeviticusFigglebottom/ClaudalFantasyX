class_name Ch09Zone
extends Ch05Zone
## Ch9's greybox zone root, `ch09/corrow_night` (M3-C09-02; act1_ch09.md; docs/kb/tech/chapter_flow.md
## "Ch9"): Corrow on the night of the Ebbing and the dawn road after it. It keeps Ch05Zone's calls
## (place_actor, give_if, the layout's light "variants") and Ch01Zone's (rest, give, hide_block,
## show_block), and adds three things:
##   the held input   a CutsceneHoldGate on the story's sequencer: inside a scene, between <<event
##                    hold_input raise_staff>> and <<event hold_input_end>>, the scene's time runs only
##                    while the player holds the field's interact action ("Hold to raise the staff").
##                    No timing, no score, no fail (act1_ch09.md B04-B07). Data: ch09_field.json "hold".
##   variant "place"  a "variants" row may also stand stage actors on marks, {actor id: mark id}, so a
##                    zone reloaded at dawn has the party on the road and Kerrid at the milestone.
##   "clip_marks"     the layout's placeholder clips ({"actor/clip": mark}; CutsceneStage.clip_marks):
##                    `@anim asha pole_out` cuts Asha onto the raft mid-harbour until her rig has the clip.
## Ch9 has no fights, no encounters and no tutorial prompts.

const CH09_FIELD_PATH := "res://game/data/flow/ch09_field.json"
const KEY_CH09_HOLD := "hold"
const KEY_CLIP_MARKS := "clip_marks"
const KEY_PLACE := "place"

## The Ebbing's held input.
var hold_gate: CutsceneHoldGate
## ch09_field.json.
var ch09_field: Dictionary = {}


func build() -> void:
	if hint != null:
		return
	super()
	ch09_field = read_json(CH09_FIELD_PATH)
	stage.clip_marks = (layout.get(KEY_CLIP_MARKS, {}) as Dictionary).duplicate()
	hold_gate = CutsceneHoldGate.new()
	hold_gate.name = "HoldGate"
	add_child(hold_gate)


func _ready() -> void:
	super()
	hold_gate.setup(story.sequencer, ch09_field.get(KEY_CH09_HOLD, {}))


## Ch05Zone's variants, then each holding row's "place": its actors stand on their marks (shown).
func apply_variant() -> void:
	super()
	for r: Variant in layout.get(KEY_VARIANTS, []):
		var row: Dictionary = r
		if not ZoneStory.holds(row.get("when", {})):
			continue
		var place: Dictionary = row.get(KEY_PLACE, {})
		for id: Variant in place:
			place_actor(str(id), str(place[id]))
