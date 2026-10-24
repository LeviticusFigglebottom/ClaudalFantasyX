class_name ReplayFlagAccess
extends DialogueFlagAccess
## Flag access for a replayed cutscene (CutsceneSequencer.replay, the Memories gallery): it reads
## the live game's flags, so branches play as the player saw them, but writes stay in this object.
## A replay never changes Game.state.


func get_flag(flag: StringName) -> Variant:
	if values.has(String(flag)):
		return values[String(flag)]
	return Game.get_flag(flag, false)


func set_flag(flag: StringName, value: Variant) -> void:
	values[String(flag)] = value
