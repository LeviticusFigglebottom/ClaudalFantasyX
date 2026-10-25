class_name Ch07Zone
extends Ch01Zone
## A Ch7 greybox zone root (M3-C07-02; docs/kb/tech/chapter_flow.md "Ch7"): Tamsule's port and the
## story's stand-in for the Bell's galleries. It reuses Ch01Zone's story calls (give, rest,
## hide_block, show_block) and adds one, reached with a ZoneStory `zone` step:
##   checkpoint(spawn)   respawn here at `spawn` and request an autosave at the next safe point
##                       (SaveSystem.request_autosave): B04's save before the naming, so a reload
##                       starts at the pool steps and the galleries scene is not replayed
##                       (act1_ch07.md §5.1). The save is written once the run has ended, when no
##                       cutscene holds it.
##   stand(actor, mark)  puts a stage actor on a mark, facing the mark's yaw, with no walk: a zone
##                       entered after a beat moved someone (Tavi at his boat after B07) starts
##                       with them where the beat left them.
## Ch7 has no foes, no tutorial prompts and no fog; Ch01Zone's ch01_field.json prompts go unused.


## Moves the respawn point to this zone's `spawn` and asks for the autosave. False when there is no
## such spawn (nothing changes).
func checkpoint(spawn: String) -> bool:
	if spawn_marker(StringName(spawn)) == null:
		push_warning("Ch07Zone %s: no checkpoint spawn '%s'" % [location_id, spawn])
		return false
	Game.state.respawn_location_id = location_id
	Game.state.respawn_spawn = StringName(spawn)
	SaveSystem.request_autosave(SaveSystem.REASON_CHAPTER)
	return true


## Puts the stage actor `actor` on the stage mark `mark`, turned to the mark's facing. False when
## either is missing (nothing moves).
func stand(actor: String, mark: String) -> bool:
	var a := stage.actor(StringName(actor)) if stage != null else null
	var m := stage.mark(StringName(mark)) if stage != null else null
	if a == null or m == null:
		push_warning("Ch07Zone %s: cannot stand '%s' on '%s'" % [location_id, actor, mark])
		return false
	# Marks and actors both sit under the stage, whose Marks and Actors folders don't move.
	a.position = m.position
	a.rotation.y = m.rotation.y
	return true
