class_name Ch13Zone
extends Ch05Zone
## Ch13's greybox zone root, `ch13/ansedra`, `ch13/sanctum` and `ch13/lamp_archive` (M4-C13-02; act_outline.md
## Ch13): the holy city on its mirror lagoon, the Glimmer temple and the Order's library. It keeps Ch05Zone's calls
## (place_actor, give_if, the layout's light "variants") and Ch01Zone's (rest, give, hide_block, show_block) for the
## story the beat sheet (M4-C13-01) brings; the layouts come from tools/act2/ch13_greybox.py.
##
## M4-A2P-104: the escape's first ripples. Each pole stroke a scene cues (`@sfx pole_stroke`, ch14_first_ripple)
## sends a ring out across the lagoon from the barge's stern (RippleField.strike); the barge is a greybox block that
## doesn't travel yet, so the field has no wake_target.

const SFX_CUE := &"sfx"
const SFX_POLE_STROKE := &"pole_stroke"
const BLOCK_STERN := "BargeStern"


func _ready() -> void:
	super()
	if story != null:
		story.sequencer.cue_played.connect(_on_cue)


## A ring from the barge's stern on each pole stroke; nothing in a zone without a field or a barge.
func _on_cue(cue: StringName, args: Array, _kwargs: Dictionary) -> void:
	if cue != SFX_CUE or args.is_empty() or StringName(str(args[0])) != SFX_POLE_STROKE:
		return
	var field := RippleField.find(get_tree())
	var stern := _block(BLOCK_STERN)
	if field != null and stern != null:
		field.strike(stern.global_position)
