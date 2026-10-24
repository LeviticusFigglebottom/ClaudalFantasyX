class_name StingAudio
extends RefCounted
## Stings on the battle presentation's announcements (M3-AUD-18; docs/kb/tech/audio_runtime.md "Battle stings").
## battle-presentation announces its moments on EventBus.dialogue_event(event, args): "battle_stinger" [encounter]
## as the tide line rises, "battle_bark" [encounter, line_key, speaker_key] for the lead-in line, and "boss_intro"
## [encounter_id, title_key] as a boss's title card shows. The director hands every dialogue_event to on_event;
## game/data/audio/battle_stings.json `events` names the row each plays:
## - `sfx`: the row; `by_arg`: {first argument (the encounter): row} overrides it (the Drownbell's own sting).
## - `duck` / `duck_sec`: a mix.json duck held that long under the sting (the boss card dips the battle music).
## - `reduced`: with reduced audio on, a row is swapped for its version without sub-bass.
## An event with no row is ignored. Listen-only: nothing here writes game state.
## Time passes only through advance(delta) (AudioDirector.advance calls it; tests call it directly).

## Plays a row: (id: StringName) -> void.
var player: Callable = Callable()
## Turns a mix.json duck on or off: (reason: StringName, on: bool) -> void.
var ducker: Callable = Callable()
## Whether reduced audio is on: () -> bool.
var reduced: Callable = Callable()
## battle_stings.json.
var data: Dictionary = {}
## Every row played, in order (tests).
var played: Array[StringName] = []
## Each duck held: reason -> seconds left.
var held: Dictionary = {}


func _init(table: Dictionary = {}) -> void:
	data = table


## Plays the sting battle_stings.json names for dialogue event `event` with `args`. Returns the row played, or &"".
func on_event(event: StringName, args: Array) -> StringName:
	var row := (data.get("events", {}) as Dictionary).get(String(event), {}) as Dictionary
	if row.is_empty():
		return &""
	var id := StringName(str(row.get("sfx", "")))
	if not args.is_empty():
		id = StringName(str((row.get("by_arg", {}) as Dictionary).get(str(args[0]), id)))
	if id == &"":
		return &""
	if reduced.is_valid() and bool(reduced.call()):
		id = StringName(str((data.get("reduced", {}) as Dictionary).get(String(id), id)))
	if player.is_valid():
		player.call(id)
	played.append(id)
	var reason := StringName(str(row.get("duck", "")))
	if reason != &"" and ducker.is_valid():
		ducker.call(reason, true)
		held[reason] = maxf(float(held.get(reason, 0.0)), float(row.get("duck_sec", 0.0)))
	return id


func advance(delta: float) -> void:
	for reason: StringName in held.keys():
		held[reason] = float(held[reason]) - delta
		if float(held[reason]) <= 0.0:
			held.erase(reason)
			if ducker.is_valid():
				ducker.call(reason, false)
