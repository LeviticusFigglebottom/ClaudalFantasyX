class_name DialogueOption
extends RefCounted
## One choice the player can pick. `index` is what DialogueRunner.choose() takes.
## Show it with tr(text_key).

var index: int = 0
var line_id: StringName = &""
var text_key: StringName = &""
var tags: PackedStringArray = PackedStringArray()


static func from_choice(choice: Dictionary, choice_index: int) -> DialogueOption:
	var o := DialogueOption.new()
	o.index = choice_index
	o.line_id = StringName(str(choice.get("id", "")))
	o.text_key = StringName(str(choice.get("key", "")))
	for t: Variant in choice.get("tags", []):
		o.tags.append(str(t))
	return o
