class_name FlagRegistry
extends Resource
## Declares every story flag the game may read or write. Keys are flag names, values are
## human-readable descriptions. tools/validate_data.py fails CI on any undeclared flag usage.

@export var flags: Dictionary = {}


func is_declared(flag: StringName) -> bool:
	return flags.has(String(flag))


func description(flag: StringName) -> String:
	return String(flags.get(String(flag), ""))
