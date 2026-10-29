class_name CutsceneSound
extends RefCounted
## `@sfx <id> [vol=] [at=]` (M2-FP-118): Audio's sfx row (sfx*.json: its files, bus, variation and cooldown) when
## audio has one, from the `at` place when the cue names one; else the cutscene's own `<sfx_dir>/<id>.ogg`.
## `@music <cue>` (M2-AUD-07): Audio plays a music.json cue on its deck (crossfaded, and carried past the scene's
## end into the zone, as Cutscene A's dawn runs into the village); any other cue is the sequencer's own player's,
## from `<music_dir>/<cue>.ogg` or its sequencer.json music_stand_ins file.


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


## Hands music cue `cue` (or AudioData.SILENCE) to Audio; false when music.json has no such cue. `stem` >= 0 brings
## that stem of the cue in over `fade` (M3-AUD-829: `@music undertow_rising stem=1 fade=2.0`, the run's pulse; the
## cue already playing carries on, since replaying the current cue is a no-op).
static func music(cue: StringName, fade: float, stem: int = -1) -> bool:
	if cue != AudioData.SILENCE and AudioData.cue(Audio.music_data, cue).is_empty():
		return false
	var played := Audio.play_music(cue, fade)
	if played and stem >= 0 and Audio.music != null:
		Audio.music.set_stem(stem, true, fade)
	return played


## The sequencer's own stream for cue `track`: its file under music_dir, else its stand-in's (null if neither).
static func music_stream(config: Dictionary, track: StringName) -> AudioStream:
	var dir := str(config.get("music_dir", ""))
	var stand_ins: Dictionary = config.get("music_stand_ins", {})
	for name_id: String in [String(track), str(stand_ins.get(String(track), ""))]:
		var path := "%s%s.ogg" % [dir, name_id]
		if name_id != "" and ResourceLoader.exists(path):
			return load(path) as AudioStream
	return null
