extends Node
## Global decoupled signal hub. Systems emit here instead of holding references to each other.

@warning_ignore("unused_signal")
signal battle_started(encounter_id: StringName)
@warning_ignore("unused_signal")
signal battle_ended(encounter_id: StringName, result: StringName)
@warning_ignore("unused_signal")
signal flag_changed(flag: StringName, value: Variant)
@warning_ignore("unused_signal")
signal dialogue_event(event_name: StringName, args: Array)
@warning_ignore("unused_signal")
signal scene_changed(scene_path: String)
@warning_ignore("unused_signal")
signal game_saved(slot: int)
@warning_ignore("unused_signal")
signal game_loaded(slot: int)
@warning_ignore("unused_signal")
signal field_interacted(interactable_id: StringName, kind: StringName, payload: Dictionary)
@warning_ignore("unused_signal")
signal field_trigger_entered(trigger_id: StringName, payload: Dictionary)
## M1-ARC-03. Game.set_chapter() emits it; SaveSystem autosaves to slot 0 on it.
@warning_ignore("unused_signal")
signal chapter_changed(chapter: int, previous: int)
## M1-ARC-03. A save shrine restores the party. Party HP/MP/statuses are not persisted in
## GameStateData yet, so whoever owns live party state (battle setup, the party menu) listens here.
@warning_ignore("unused_signal")
signal party_full_heal_requested(source_id: StringName)
## M1-ARC-03. A save shrine was used (tutorial prompts, audio sting, the teleport network later).
@warning_ignore("unused_signal")
signal save_shrine_used(shrine_id: StringName, location_id: StringName)
## M1-ARC-03. An autosave attempt finished (error is an Error code; OK on success).
@warning_ignore("unused_signal")
signal autosave_finished(reason: StringName, error: int)
