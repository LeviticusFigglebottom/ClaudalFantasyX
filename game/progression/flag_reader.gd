class_name FlagReader
extends RefCounted
## Read-only story-flag access for progression logic (shop stock gates). Injectable: by default
## it reads its own `values` (tests fill it). Give it a source to read real flags, for example
## `FlagReader.from_access(GameFlagAccess.new())` in the game, which goes through Game.get_flag
## and so through the flag registry. An empty flag name always reads as set.

var values: Dictionary = {}
## Optional func(flag: StringName) -> Variant.
var source: Callable
## The access from_access() wraps. A Callable does not keep its RefCounted object alive, so the
## reader holds it; without this a GameFlagAccess.new() passed in was freed at once and every
## flag read as unset (found by M2-UI-06).
var access: DialogueFlagAccess


func _init(flag_source: Callable = Callable()) -> void:
	source = flag_source


static func from_access(access: DialogueFlagAccess) -> FlagReader:
	var reader := FlagReader.new(access.get_flag)
	reader.access = access
	return reader


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
