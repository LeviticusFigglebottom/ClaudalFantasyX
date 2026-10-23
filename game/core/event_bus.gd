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
## A save became the live Game.state (SaveSystem.load_into_game). M1-ARC-06: WorldReturn (under
## SceneRouter) then moves the party to the respawn point once boot.gd has armed it.
@warning_ignore("unused_signal")
signal game_loaded(slot: int)
@warning_ignore("unused_signal")
signal field_interacted(interactable_id: StringName, kind: StringName, payload: Dictionary)
@warning_ignore("unused_signal")
signal field_trigger_entered(trigger_id: StringName, payload: Dictionary)
## M1-ARC-03. Game.set_chapter() emits it; SaveSystem autosaves to slot 0 on it.
@warning_ignore("unused_signal")
signal chapter_changed(chapter: int, previous: int)
## M1-ARC-03. A save shrine restores the party. M1-ARC-06: Game listens and fills every member's
## HP and MP and cures party_rest.json "shrine_cures" in Game.state.party_vitals.
@warning_ignore("unused_signal")
signal party_full_heal_requested(source_id: StringName)
## M1-ARC-03. A save shrine was used (tutorial prompts, audio sting, the teleport network later).
@warning_ignore("unused_signal")
signal save_shrine_used(shrine_id: StringName, location_id: StringName)
## M1-ARC-03. An autosave attempt finished (error is an Error code; OK on success).
@warning_ignore("unused_signal")
signal autosave_finished(reason: StringName, error: int)
## M1-ARC-06. The battle scene emits this once a battle has ended, with every party combatant
## (active and reserve; BattleCombatant). Game writes their HP, MP and carried statuses back into
## Game.state.party_vitals. Emitting it is the battle scene's job (request M1-CMB, see
## architecture.md "Saves"); the engine core stays untouched.
@warning_ignore("unused_signal")
signal battle_party_returned(encounter_id: StringName, outcome: StringName, party: Array)
