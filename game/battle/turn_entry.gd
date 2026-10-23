class_name TurnEntry
extends RefCounted
## One predicted slot in the turn-order timeline UI.

var combatant_id: StringName
var time: int
var team: StringName
## The combatant will lose this turn (Stop/Sleep) if nothing changes.
var skipped := false
## This entry is the previewed actor's next turn after the candidate action.
var is_preview := false
## Doom countdown shown on this turn (0 = not doomed). The combatant falls at the end of a
## turn showing 1, so no later entry for it follows.
var doom := 0


func _init(
	cid: StringName, t: int, team_id: StringName, skip: bool = false, preview: bool = false, doom_count: int = 0
) -> void:
	combatant_id = cid
	time = t
	team = team_id
	skipped = skip
	is_preview = preview
	doom = doom_count
