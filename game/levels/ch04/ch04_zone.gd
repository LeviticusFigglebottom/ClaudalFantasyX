class_name Ch04Zone
extends Ch01Zone
## A Ch4 greybox zone root (M3-C04-02; docs/kb/tech/chapter_flow.md "Ch4"). It reuses Ch01Zone's story
## calls as they are (rest, give, hide_block / show_block; Ch1's tutorial prompt table goes unused
## here, because Ch4's prompts are battle prompts) and adds the one thing Ch4's two zones need: a zone
## whose dressing follows the story flags, so it comes back right after a battle or a reload.
##   layout "states": [{"flag": f, "hide": [ids], "show": [ids], "place": {actor id: mark id}}]
##     Applied in order once the zone is ready, and again by refresh_states() (a `zone` step after a
##     scene that set a flag). Each row whose flag is set hides and shows its Greybox blocks or stage
##     actors (Ch01Zone.hide_block / show_block: a block's collision goes with it), and stands the
##     stage actors it places on those marks. Rhen is never one.
## Haluna's wake-night uses it for the windows going dark, Asha's shell in the wall, the village going
## home and the stranger at the wall; the ferry for the party crossing to the derelict and back, its
## sails, the wraith and the board. A battle reloads the zone, so this is what keeps it right.
## Kit collision (ADR 0200): the layout's "collision_path" and "ramps" (KitCollision).

const KEY_STATES := "states"
const KEY_PLACE := "place"


func _ready() -> void:
	super()
	refresh_states()


## The layout's blocks plus its collision file's; then the ramps (KitCollision).
func _build_blocks() -> void:
	KitCollision.merge(self)
	super()
	KitCollision.build_ramps(self)


## Applies every "states" row whose flag is set (see the class comment).
func refresh_states() -> void:
	for row: Dictionary in layout.get(KEY_STATES, []):
		if not bool(Game.get_flag(StringName(str(row.get("flag", ""))))):
			continue
		for id: Variant in row.get("hide", []):
			hide_block(str(id))
		for id: Variant in row.get("show", []):
			show_block(str(id))
		var place: Dictionary = row.get(KEY_PLACE, {})
		for id: Variant in place:
			place_actor(str(id), str(place[id]))


## Stands stage actor `id` on mark `mark_id` (its position and facing). False when either is missing.
func place_actor(id: String, mark_id: String) -> bool:
	var a := stage.actor(StringName(id))
	var m := stage.mark(StringName(mark_id))
	if a == null or m == null or a is FieldController:
		push_warning("Ch04Zone %s: cannot place '%s' on '%s'" % [location_id, id, mark_id])
		return false
	a.transform = m.transform  # Actors/ and Marks/ are sibling groups of the stage: one frame
	return true
