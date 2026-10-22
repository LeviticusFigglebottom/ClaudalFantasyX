class_name GameFlagAccess
extends DialogueFlagAccess
## Production flag access: reads and writes through the Game autoload, which rejects undeclared
## flags and emits EventBus.flag_changed.


func get_flag(flag: StringName) -> Variant:
	return Game.get_flag(flag, false)


func set_flag(flag: StringName, value: Variant) -> void:
	Game.set_flag(flag, value)
