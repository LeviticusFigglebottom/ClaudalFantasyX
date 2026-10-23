class_name CutsceneSequencer
extends Node
## Plays a compiled `.dlg` scene on a CutsceneStage (M2-FP-01; docs/kb/tech/cutscenes.md).
##
## Usage:
##   var seq := CutsceneSequencer.new()
##   add_child(seq)
##   await seq.play(&"ch02_girl_on_the_beach", stage)
##   # act on the <<event>>s it reported (seq.events, or the event_requested signal) afterwards
##
## <<event start_battle x>> and <<event zone_unlock x>> are reported, never acted on here: the host
## (zone or flow code) decides what they mean once play() returns.
##
## Contract with the camera (docs/kb/tech/field_camera.md, "Scripted shots"): `@camera <id>` is
## play_shot(shot, blend or 0, ease), `@camera release` is release(blend or -1, ease), and every
## move is awaited ("move, then await"), then is_instance_valid(director) / is_leaving() are
## checked: a director leaving the tree ends the cutscene. The autosave is held from the first beat
## to the last (SaveSystem.hold_autosave), and the stage's player is frozen meanwhile.
##
## Time passes only through advance(delta), which _process calls; tests call it directly.
## `instant` (tests) makes every wait, fade and move take no time and lines advance by themselves.
## Cues the first playable has no content for are placeholders: `@face` only records, `@anim`
## turns the actor for `look_at` and otherwise plays a same-named AnimationPlayer clip when the
## actor has one, `@vfx` spawns CutsceneMotes, `@music` falls back to music_stand_ins.

signal finished(scene_id: StringName)
signal event_requested(event_name: StringName, args: Array)
signal line_shown(step: DialogueStep)
signal cue_played(cue: StringName, args: Array, kwargs: Dictionary)
## Internal: a timed wait (`@wait`, a fade, an auto-advance hold) ran out.
signal wait_elapsed

const CONFIG_PATH := "res://game/data/cutscene/sequencer.json"
const ANIM_LOOK_AT := &"look_at"
const GAIT_RUN := &"run"
const FADE_OUT := &"out"
const SWITCH_ON := &"on"
const DEFAULT_SEED := 1

## Tests and captures: no waits, no typewriter, lines and options answer themselves.
var instant := false
## Lines advance by themselves once revealed (autoplay, captures), after `auto_advance_hold_sec`.
var auto_advance := false
var auto_advance_hold_sec := 1.5
## The option index chosen when `instant` or `auto_advance`.
var auto_choice := 0
## When a scene ends faded out, fade back in. A host that changes scene right after sets false.
var restore_fade := true
## Every <<event>> of the last play(), in order: [{"name": StringName, "args": Array}].
var events: Array[Dictionary] = []
## Soft failures (a missing shot, actor, mark or track), each reported once.
var warnings: Array[String] = []
## Every @face cue of the last play() (placeholder: no face rig yet), [actor, expression, sec].
var faces: Array = []
var config: Dictionary = {}
var overlay: CutsceneOverlay
var runner: DialogueRunner
var music: AudioStreamPlayer
var music_track: StringName = &""

var _playing := false
var _aborted := false
var _scene_id: StringName = &""
var _stage: CutsceneStage
var _director: FieldCameraDirector
var _player: FieldController
var _player_input_was := true
var _wait_left := 0.0
## key -> {elapsed, duration, apply: Callable(t: float)}; a new motion on a key replaces the old.
var _motions: Dictionary = {}
var _vfx_count := 0


static func load_config() -> Dictionary:
	var f := FileAccess.open(CONFIG_PATH, FileAccess.READ)
	if f == null:
		push_error("CutsceneSequencer: cannot read %s" % CONFIG_PATH)
		return {}
	var parsed: Variant = JSON.parse_string(f.get_as_text())
	return parsed if parsed is Dictionary else {}


func _ready() -> void:
	_ensure_overlay()


func _process(delta: float) -> void:
	advance(delta)


func _exit_tree() -> void:
	if _playing:
		_aborted = true
		_restore_player()
		SaveSystem.release_autosave(self)
		_playing = false


func is_playing() -> bool:
	return _playing


## Plays `scene_id` (a compiled scene under game/data/dialogue/compiled/) to its end on `stage`.
## Returns false when the scene could not be loaded or the cutscene was cut short. Await it.
func play(scene_id: StringName, stage: CutsceneStage) -> bool:
	if _playing:
		push_error("CutsceneSequencer: play(%s) while %s is playing" % [scene_id, _scene_id])
		return false
	runner = DialogueRunner.new()
	if not runner.load_scene(scene_id) or not runner.start():
		push_error("CutsceneSequencer: cannot start scene '%s'" % scene_id)
		return false
	_begin(scene_id, stage)
	var step := runner.next()
	while not step.is_end() and not _aborted:
		if step.is_line():
			await _line(step)
		elif step.is_options():
			var picked: int = await _options(step)
			if not _aborted:
				runner.choose(picked)
		else:
			await _cue(step)
		if not _aborted:
			step = runner.next()
	await _finish()
	return not _aborted


## Advances every timed thing by `delta` seconds: waits, fades, letterbox, moves, turns, music.
func advance(delta: float) -> void:
	for key: StringName in _motions.keys():
		var m: Dictionary = _motions[key]
		m["elapsed"] = float(m["elapsed"]) + delta
		var d := float(m["duration"])
		var t := 1.0 if d <= 0.0 else clampf(float(m["elapsed"]) / d, 0.0, 1.0)
		(m["apply"] as Callable).call(t)
		if t >= 1.0:
			_motions.erase(key)
	if _wait_left > 0.0:
		_wait_left -= delta
		if _wait_left <= 0.0:
			_wait_left = 0.0
			wait_elapsed.emit()


func has_motion(key: StringName) -> bool:
	return _motions.has(key)


# --- flow ------------------------------------------------------------------------------------


func _begin(scene_id: StringName, stage: CutsceneStage) -> void:
	_ensure_overlay()
	_scene_id = scene_id
	_stage = stage
	_director = stage.director() if stage != null else null
	_player = stage.player() if stage != null else null
	_playing = true
	_aborted = false
	events.clear()
	faces.clear()
	SaveSystem.hold_autosave(self)
	if _player != null:
		_player_input_was = _player.accepts_input
		_player.accepts_input = false
		_player.velocity = Vector3.ZERO
	if _starts_black(scene_id):
		overlay.set_fade(1.0)
	runner.event_triggered.connect(_on_event)


func _finish() -> void:
	_complete_motions()
	if overlay != null:
		overlay.box.visible = false
		overlay.choices.clear()
	if not _aborted and _director_alive() and _director.is_scripted():
		_director.release()
		await _land()
	if overlay != null and _aborted:
		overlay.set_letterbox(0.0)
		overlay.set_fade(0.0)
	elif overlay != null:
		_set_letterbox(false)
		if restore_fade and overlay.fade_alpha() > 0.0:
			_start_fade(0.0, float(config.get("fade_back_sec", 0.0)))
			await _wait_for(float(config.get("fade_back_sec", 0.0)))
		_complete_motions()
	_restore_player()
	SaveSystem.release_autosave(self)
	_playing = false
	finished.emit(_scene_id)


func _restore_player() -> void:
	if _player != null and is_instance_valid(_player):
		_player.accepts_input = _player_input_was
	_player = null


func _line(step: DialogueStep) -> void:
	overlay.box.visible = true
	overlay.box.show_line(step)
	line_shown.emit(step)
	if instant:
		overlay.box.skip_reveal()
		return
	if auto_advance:
		if overlay.box.is_revealing():
			await overlay.box.reveal_finished
		await _wait_for(auto_advance_hold_sec)
		return
	await overlay.box.advance_requested


func _options(step: DialogueStep) -> int:
	var pick := clampi(auto_choice, 0, step.options.size() - 1)
	if instant or auto_advance:
		return step.options[pick].index
	overlay.choices.show_options(step.options)
	var chosen: int = await overlay.choices.chosen
	return chosen


func _cue(step: DialogueStep) -> void:
	cue_played.emit(step.cue, step.args, step.kwargs)
	match step.cue:
		&"camera":
			await _cue_camera(step)
		&"wait":
			await _cue_wait(step)
		&"fade":
			await _cue_fade(step)
		&"letterbox":
			_set_letterbox(StringName(str(step.args[0])) == SWITCH_ON)
		&"mark":
			_cue_mark(step)
		&"anim":
			_cue_anim(step)
		&"face":
			faces.append(step.args.duplicate())
		&"music":
			_cue_music(step)
		&"sfx":
			_cue_sfx(step)
		&"vfx":
			_cue_vfx(step)
		_:
			_warn("unknown cue @%s" % step.cue)


func _on_event(event_name: StringName, args: Array) -> void:
	events.append({"name": event_name, "args": args})
	event_requested.emit(event_name, args)


# --- cues ------------------------------------------------------------------------------------


func _cue_camera(step: DialogueStep) -> void:
	if not _director_alive():
		_warn("@camera with no camera director on the stage")
		return
	var ease := StringName(str(step.kwargs.get("ease", "")))
	if step.is_camera_release():
		var back := float(step.kwargs.get("blend", CameraShot.USE_DEFAULT))
		if not _director.release(back, ease):
			return
	else:
		var id := StringName(str(step.args[0]))
		var shot := _stage.shot(id) if _stage != null else null
		if shot == null:
			_warn("no shot '%s' on the stage" % id)
			return
		var blend := float(step.kwargs.get("blend", 0.0))
		if blend > 0.0:
			overlay.box.visible = false
		_director.play_shot(shot, blend, ease)
	await _land()


## Waits for the director's move to land; a director that left the tree ends the cutscene.
func _land() -> void:
	if instant:
		_director.snap()
		return
	if not _director.is_settled():
		await _director.blend_finished
	if not is_instance_valid(_director) or _director.is_leaving():
		_director = null
		_aborted = true


func _cue_wait(step: DialogueStep) -> void:
	if step.is_music_wait():
		# No music markers are reported yet (no adaptive music player): hold for max= and release.
		await _wait_for(float(step.kwargs.get("max", config.get("music_wait_fallback_sec", 0.0))))
		if runner.is_waiting_for_marker():
			runner.release_wait()
		return
	await _wait_for(float(step.args[0]) if not step.args.is_empty() else 0.0)


func _cue_fade(step: DialogueStep) -> void:
	var out := StringName(str(step.args[0])) == FADE_OUT
	var sec := float(step.args[1])
	if step.args.size() > 2:
		var c := Color.from_string(str(step.args[2]), overlay.fade_rect.color)
		overlay.fade_rect.color = Color(c, overlay.fade_rect.color.a)
	if out:
		overlay.box.visible = false
	_start_fade(1.0 if out else 0.0, sec)
	await _wait_for(sec)


func _cue_mark(step: DialogueStep) -> void:
	var actor := _actor(StringName(str(step.args[0])))
	var target_id := StringName(str(step.args[1]))
	var target := _stage.mark(target_id) if _stage != null else null
	if actor == null:
		return
	if target == null:
		_warn("no mark '%s' on the stage" % target_id)
		return
	var gait := StringName(str(step.args[2])) if step.args.size() > 2 else &"walk"
	var speed := float(config.get("run_mps" if gait == GAIT_RUN else "walk_mps", 1.0))
	var from := actor.global_position
	var to := target.global_position
	var flat := Vector3(to.x - from.x, 0.0, to.z - from.z)
	if flat.length() > 0.01:
		_face(actor, flat)
	var dur := from.distance_to(to) / maxf(speed, 0.01)
	_start_motion(&"move:%s" % step.args[0], dur, func(t: float) -> void: _place(actor, from.lerp(to, t)))


func _cue_anim(step: DialogueStep) -> void:
	var actor := _actor(StringName(str(step.args[0])))
	if actor == null:
		return
	var clip := StringName(str(step.args[1]))
	if clip == ANIM_LOOK_AT and step.args.size() > 2:
		var tid := StringName(str(step.args[2]))
		var target := _stage.place(tid) if _stage != null else null
		if target == null:
			_warn("no look_at target '%s' on the stage" % tid)
			return
		_turn_to(StringName(str(step.args[0])), actor, target.global_position - actor.global_position)
		return
	var ap := actor.find_child("AnimationPlayer", true, false) as AnimationPlayer
	if ap != null and ap.has_animation(clip):
		ap.play(clip)


func _cue_music(step: DialogueStep) -> void:
	var fade := float(step.kwargs.get("fade", config.get("music_fade_default_sec", 0.0)))
	var silent := float(config.get("silent_db", 0.0))
	if step.is_music_silence():
		music_track = &""
		_fade_music(silent, fade, true)
		return
	var track := StringName(str(step.args[0]))
	var stream := _music_stream(track)
	music_track = track
	if stream == null:
		_warn("no music for '%s' (and no stand-in)" % track)
		_fade_music(silent, fade, true)
		return
	if music.stream != stream or not music.playing:
		music.stream = stream
		music.volume_db = silent if fade > 0.0 else float(config.get("music_volume_db", 0.0))
		music.play()
	_fade_music(float(config.get("music_volume_db", 0.0)), fade, false)


func _cue_sfx(step: DialogueStep) -> void:
	var path := "%s%s.ogg" % [config.get("sfx_dir", ""), step.args[0]]
	if not ResourceLoader.exists(path):
		_warn("no sound '%s'" % step.args[0])
		return
	var p := AudioStreamPlayer.new()
	p.stream = load(path)
	p.volume_db = linear_to_db(float(step.kwargs.get("vol", 1.0)))
	p.finished.connect(p.queue_free)
	add_child(p)
	p.play()


func _cue_vfx(step: DialogueStep) -> void:
	var rows: Dictionary = config.get("vfx", {})
	var effect := str(step.args[0])
	var at_id := StringName(str(step.kwargs.get("at", "")))
	var at := _stage.place(at_id) if _stage != null and at_id != &"" else null
	if not rows.has(effect) or (at_id != &"" and at == null):
		_warn("cannot place @vfx %s at '%s'" % [effect, at_id])
		return
	var host: Node3D = at if at != null else _stage
	if host == null:
		return
	var motes := CutsceneMotes.new()
	motes.name = "Vfx_%s_%d" % [effect, _vfx_count]
	_vfx_count += 1
	host.add_child(motes)
	motes.build(
		rows[effect], int(step.kwargs.get("count", config.get("vfx_default_count", 1))), DEFAULT_SEED + _vfx_count
	)


# --- helpers ---------------------------------------------------------------------------------


func _ensure_overlay() -> void:
	if config.is_empty():
		config = load_config()
	if overlay == null:
		overlay = CutsceneOverlay.new(config)
		add_child(overlay)
	if music == null:
		music = AudioStreamPlayer.new()
		music.name = "Music"
		add_child(music)


func _director_alive() -> bool:
	return _director != null and is_instance_valid(_director) and not _director.is_leaving()


func _actor(id: StringName) -> Node3D:
	var a := _stage.actor(id) if _stage != null else null
	if a == null:
		_warn("no actor '%s' on the stage" % id)
	return a


func _wait_for(sec: float) -> void:
	if instant or sec <= 0.0:
		return
	_wait_left = sec
	await wait_elapsed


func _start_motion(key: StringName, duration: float, apply: Callable) -> void:
	if instant or duration <= 0.0:
		_motions.erase(key)
		apply.call(1.0)
		return
	_motions[key] = {"elapsed": 0.0, "duration": duration, "apply": apply}


func _complete_motions() -> void:
	for key: StringName in _motions.keys():
		((_motions[key] as Dictionary)["apply"] as Callable).call(1.0)
	_motions.clear()


func _start_fade(to: float, sec: float) -> void:
	var from := overlay.fade_alpha()
	_start_motion(&"fade", sec, func(t: float) -> void: overlay.set_fade(lerpf(from, to, t)))


func _set_letterbox(on: bool) -> void:
	var from := overlay.letterbox()
	var to := 1.0 if on else 0.0
	var sec := float(config.get("letterbox_sec", 0.0))
	_start_motion(&"letterbox", sec, func(t: float) -> void: overlay.set_letterbox(lerpf(from, to, t)))


func _fade_music(to_db: float, sec: float, stop_after: bool) -> void:
	var from := music.volume_db
	var player := music
	_start_motion(
		&"music",
		sec,
		func(t: float) -> void:
			player.volume_db = lerpf(from, to_db, t)
			if t >= 1.0 and stop_after:
				player.stop()
	)


func _music_stream(track: StringName) -> AudioStream:
	var dir := str(config.get("music_dir", ""))
	var stand_ins: Dictionary = config.get("music_stand_ins", {})
	for name_id: String in [String(track), str(stand_ins.get(String(track), ""))]:
		var path := "%s%s.ogg" % [dir, name_id]
		if name_id != "" and ResourceLoader.exists(path):
			return load(path) as AudioStream
	return null


func _face(actor: Node3D, dir: Vector3) -> void:
	var yaw := atan2(-dir.x, -dir.z)
	actor.rotation.y = yaw
	if actor is FieldController and (actor as FieldController).motor != null:
		(actor as FieldController).motor.facing_yaw = yaw


func _turn_to(id: StringName, actor: Node3D, dir: Vector3) -> void:
	if Vector2(dir.x, dir.z).length() < 0.01:
		return
	var from := actor.rotation.y
	var to := from + angle_difference(from, atan2(-dir.x, -dir.z))
	_start_motion(
		&"turn:%s" % id,
		float(config.get("turn_sec", 0.0)),
		func(t: float) -> void: _face_yaw(actor, lerpf(from, to, t))
	)


func _face_yaw(actor: Node3D, yaw: float) -> void:
	if not is_instance_valid(actor):
		return
	_face(actor, Vector3(-sin(yaw), 0.0, -cos(yaw)))


func _place(actor: Node3D, pos: Vector3) -> void:
	if is_instance_valid(actor):
		actor.global_position = pos
		if actor is CharacterBody3D:
			(actor as CharacterBody3D).velocity = Vector3.ZERO


## True when the scene's first @fade (in its start node) is a fade in: the screen starts black.
func _starts_black(scene_id: StringName) -> bool:
	var f := FileAccess.open(DialogueRunner.scene_path(scene_id), FileAccess.READ)
	if f == null:
		return false
	var data: Variant = JSON.parse_string(f.get_as_text())
	if not data is Dictionary:
		return false
	var nodes: Dictionary = (data as Dictionary).get("nodes", {})
	var start: Dictionary = nodes.get(str((data as Dictionary).get("start", "")), {})
	for op: Dictionary in start.get("ops", []):
		if str(op.get("cue", "")) == "fade":
			return str((op.get("args", []) as Array)[0]) == "in"
		if str(op.get("op", "")) == "line":
			return false
	return false


func _warn(msg: String) -> void:
	var full := "CutsceneSequencer(%s): %s" % [_scene_id, msg]
	if full in warnings:
		return
	warnings.append(full)
	push_warning(full)
