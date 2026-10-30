class_name CutsceneCard
extends RefCounted
## M2-FP-121: a line tagged `#card` (a time card, Ch1's "One month earlier.") is UI's ActCard caption on black
## (game/ui/cards/act_card.gd; its fade-in, hold and fade-out are act_card.json's), not a line in the dialogue box. The
## sequencer goes on once the words are gone; the card's black is freed under the overlay's, so the scene's own
## `@fade in` brings the picture up. A scene whose first fade is `in` starts black, and a card before that fade
## doesn't change that (it is shown on black).

const TAG := "card"


## Opens the card for `step` under `host`, showing its line's loc key.
static func open(host: Node, step: DialogueStep) -> ActCard:
	var card := ActCard.open_in(host)
	card.show_caption(String(step.text_key))
	return card


## Frees the card and its layer.
static func close(card: ActCard) -> void:
	if is_instance_valid(card) and is_instance_valid(card.get_parent()):
		card.get_parent().queue_free()


## True when the scene's first node fades in before any line that isn't a card: it starts on black.
static func starts_black(scene_id: StringName) -> bool:
	var data: Variant = JSON.parse_string(FileAccess.get_file_as_string(DialogueRunner.scene_path(scene_id)))
	if not data is Dictionary:
		return false
	var nodes: Dictionary = (data as Dictionary).get("nodes", {})
	var start: Dictionary = nodes.get(str((data as Dictionary).get("start", "")), {})
	for op: Dictionary in start.get("ops", []):
		if str(op.get("cue", "")) == "fade":
			return str((op.get("args", []) as Array)[0]) == "in"
		if str(op.get("op", "")) == "line" and not (op.get("tags", []) as Array).has(TAG):
			return false
	return false
