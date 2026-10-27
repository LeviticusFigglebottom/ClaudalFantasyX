class_name CutsceneSound
extends RefCounted
## `@sfx <id> [vol=] [at=]` (M2-FP-118): Audio's sfx row (sfx*.json: its files, bus, variation and cooldown) when
## audio has one, from the `at` place when the cue names one; else the cutscene's own `<sfx_dir>/<id>.ogg`.


## Plays the cue from `host`; false when no such sound exists.
static func play(host: Node, sfx_dir: String, id: StringName, vol: float, at: Node3D) -> bool:
	if Audio.sfx != null and Audio.sfx.has(id):
		if at != null:
			Audio.play_sfx_at(id, at.global_position, {"gain": vol})
		else:
			Audio.play_sfx(id, {"gain": vol})
		return true
	var path := "%s%s.ogg" % [sfx_dir, id]
	if not ResourceLoader.exists(path):
		return false
	var p := AudioStreamPlayer.new()
	p.stream = load(path)
	p.volume_db = linear_to_db(vol)
	p.finished.connect(p.queue_free)
	host.add_child(p)
	p.play()
	return true
