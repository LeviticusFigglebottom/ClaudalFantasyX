class_name FlagReader
extends RefCounted
## Read-only story-flag access for progression logic (shop stock gates). Injectable: by default
## it reads its own `values` (tests fill it). Give it a source to read real flags, for example
## `FlagReader.from_access(GameFlagAccess.new())` in the game, which goes through Game.get_flag
## and so through the flag registry. An empty flag name always reads as set.

var values: Dictionary = {}
## Optional func(flag: StringName) -> Variant.
var source: Callable


func _init(flag_source: Callable = Callable()) -> void:
	source = flag_source


static func from_access(access: DialogueFlagAccess) -> FlagReader:
	return FlagReader.new(access.get_flag)


func is_set(flag: StringName) -> bool:
	if flag == &"":
		return true
	var v: Variant = source.call(flag) if source.is_valid() else values.get(String(flag), false)
	match typeof(v):
		TYPE_BOOL:
			return v
		TYPE_INT, TYPE_FLOAT:
			return v != 0
		TYPE_STRING, TYPE_STRING_NAME:
			return not str(v).is_empty()
	return false
