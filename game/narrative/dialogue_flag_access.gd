class_name DialogueFlagAccess
extends RefCounted
## How a DialogueRunner reads and writes story flags. This base class keeps flags in memory,
## so tests can pass it in as a fake. In the game, use GameFlagAccess, which goes through the
## Game autoload (and so through the flag registry). Unset flags read as `false`.

var values: Dictionary = {}


func get_flag(flag: StringName) -> Variant:
	return values.get(String(flag), false)


func set_flag(flag: StringName, value: Variant) -> void:
	values[String(flag)] = value
