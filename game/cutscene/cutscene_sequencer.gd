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
## actor has one, `@vfx` spawns a GlimmerField (CutsceneVfx), `@music` falls back to music_stand_ins.

signal finished(scene_id: StringName)
signal event_requested(event_name: StringName, args: Array)
signal line_shown(step: DialogueStep)
signal cue_played(cue: StringName, args: Array, kwargs: Dictionary)
## Internal: a timed wait (`@wait`, a fade, an auto-advance hold) ran out.
signal wait_elapsed
## Internal: whatever play() awaited (a line advance, a wait, a choice, a camera landing) arrived,
## or the sequencer left the tree and released it with null.
signal resumed(value: Variant)
## The player held ui_cancel long enough: the scene fast-forwarded to its next choice or its end.
signal skipped(scene_id: StringName)

const CONFIG_PATH := "res://game/data/cutscene/sequencer.json"
const ANIM_LOOK_AT := &"look_at"
const GAIT_RUN := &"run"
const FADE_OUT := &"out"
const SWITCH_ON := &"on"
const DEFAULT_SEED := 1
## Process after the FieldCameraDirector (priority 0), so the breath turns the pose it just set.
const PROCESS_AFTER_DIRECTOR := 10
## cues.json keys this sequencer accepts but does not perform yet; each warns once per scene.
## A line tagged #timed shows and the scene goes on: its @waits pace it (a sung verse in time with its cue).
const TAG_TIMED := "timed"
const UNSUPPORTED_KWARGS := {
	&"anim": ["loop"],
	&"vfx": ["follow", "anchors"],  # M3-ARC-1326 hands them to a stage VFX host; none reads them yet
}

## Tests and captures: no waits, no typewriter, lines and options answer themselves.
var instant := false
## Lines advance by themselves once revealed (autoplay, captures), after `auto_advance_hold_sec`, or longer when
## `auto_advance_read_cps` > 0: a line stays up until it could be read at that pace (overheard barks).
var auto_advance := false
var auto_advance_hold_sec := 1.5
var auto_advance_read_cps := 0.0
## The option index chosen when `instant` or `auto_advance`.
var auto_choice := 0
## When a scene ends faded out, fade back in. A host that changes scene right after sets false.
var restore_fade := true
## Freeze the stage's player for the scene. Overheard barks (M2-FP-13) set false: Rhen walks on
## while the lines advance by themselves (auto_advance).
var hold_player := true
## M2-FP-107: freeze the player's input like hold_player, but the scene is no staged cutscene, so the
## party's followers (HeroFieldParty, which hides for hold_player scenes) stay in view. Barks set it.
var freeze_player := false
## A replay (the Memories gallery, SPEC §6.11): flags read the live game but every <<set>> stays in
## this play (ReplayFlagAccess), and <<event>>s are recorded in `events` but never emitted or forwarded
## to the EventBus, so a replayed scene starts no battle and changes no save.
var replay := false
## Every <<event>> of the last play(), in order: [{"name": StringName, "args": Array}].
var events: Array[Dictionary] = []
## Soft failures (a missing shot, actor, mark or track), each reported once.
var warnings: Array[String] = []
## Every @face cue of the last play(), [actor, expression, sec]. Actors whose meshes have blend
## shapes and a sequencer.json "face_poses" row also show it (CutsceneFace), blink (M2-FP-18,
## sequencer.json "blink") and lip-sync each line's text to its reveal (M2-CHR-10, lipsync.json).
var faces: Array = []
## The grade the scene has put on its level (M2-FP-120), taken off at its end.
var grade := CutsceneGrade.new()
var config: Dictionary = {}
var overlay: CutsceneOverlay
var runner: DialogueRunner
var music: AudioStreamPlayer
var music_track: StringName = &""
## True while this scene's music is Audio's (a music.json cue, M2-AUD-07): music_track is then "".
var music_by_audio := false

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
## M2-FP-103: actor -> the posing clip it holds (sequencer.json hold_clips) until its next @anim or @mark;
## a held actor's lines don't play talk or idle over the pose.
var _held: Dictionary = {}
var _breath: CutsceneCameraBreath
## M2-FP-106: the zone's villagers (FieldNpc) this scene's lines have turned to Rhen.
var _npc_talk := CutsceneNpcTalk.new()
var _vfx_count := 0
## True while a skip fast-forwards (until the next choice or the end).
var _skipping := false
var _skip_held := false
var _hold := 0.0
## What play() is awaiting right now: &"line", &"wait", &"land", &"choice" or &"" (none).
var _awaiting: StringName = &""
## The source signal and handler of the await in progress (disconnected when released early).
var _await_sig: Signal
var _await_cb: Callable = Callable()
## actor id -> CutsceneFace (null when the actor has no face shapes), per play().
var _face_rigs: Dictionary = {}
## actor id -> face-poses JSON "emotions" + "blend_in_s", per play().
var _pose_tables: Dictionary = {}
## game/data/cutscene/lipsync.json, read on the first face rig.
var _lipsync: Dictionary = {}
## The rig lip-syncing the line on screen, if any.
var _speaking: CutsceneFace
## The close-shot key light (M2-FP-10), made on the first close shot, freed when the scene ends.
var _key: CutsceneKeyLight


static func load_config() -> Dictionary:
	var f := FileAccess.open(CONFIG_PATH, FileAccess.READ)
	if f == null:
		push_error("CutsceneSequencer: cannot read %s" % CONFIG_PATH)
		return {}
	var parsed: Variant = JSON.parse_string(f.get_as_text())
	return parsed if parsed is Dictionary else {}


func _ready() -> void:
	process_priority = PROCESS_AFTER_DIRECTOR  # M2-FP-104: the camera breath goes on the director's pose
	_ensure_overlay()


func _process(delta: float) -> void:
	advance(delta)


## The field's interact key (E, which starts a bark) also advances lines, like ui_accept does in
## the DialogueBox, so a player never has to switch keys mid-conversation.
func _unhandled_input(event: InputEvent) -> void:
	if _playing and event.is_action(&"ui_cancel"):
		set_skip_held(event.is_pressed())
		get_viewport().set_input_as_handled()
		return
	if not _playing or overlay == null or not overlay.box.visible or overlay.choices.visible:
		return
	if not InputMap.has_action(FieldInput.INTERACT):
		return  # no field in this scene (prologue, a cutscene set): ui_accept only
	if not event.is_action_pressed(FieldInput.INTERACT) or event.is_action_pressed(&"ui_accept"):
		return
	if overlay.box.is_revealing():
		overlay.box.skip_reveal()
	else:
		overlay.box.advance_requested.emit()
	get_viewport().set_input_as_handled()


## Leaving the tree mid-scene ends it: the autosave hold and the player go back at once, and the
## await in progress is released so play() returns false to its host instead of hanging.
func _exit_tree() -> void:
	if _playing:
		_aborted = true
		_restore_player()
		_key_drop()
		SaveSystem.release_autosave(self)
		if _awaiting != &"":
			_release_await(null)
		else:
			_playing = false


func is_playing() -> bool:
	return _playing


func is_skipping() -> bool:
	return _skipping


## The key light while a close shot keys the cast (M2-FP-10), else null.
func key_light() -> CutsceneKeyLight:
	return _key if _key != null and is_instance_valid(_key) and _key.is_engaged() else null


## Holding ui_cancel for `skip_hold_sec` (sequencer.json) skips; advance() counts the hold.
func set_skip_held(held: bool) -> void:
	_skip_held = held
	if not held:
		_hold = 0.0
		if overlay != null:
			overlay.set_skip_progress(0.0)


## Fast-forwards to the next choice (which is then shown, so the player still chooses) or to the
## end. Flags, branches and events run exactly as in a normal play; the camera snaps, waits and
## moves complete at once. Returns false when nothing is playing or a skip is already running.
func skip() -> bool:
	if not _playing or _skipping or _awaiting == &"choice":
		return false
	_skipping = true
	set_skip_held(false)
	skipped.emit(_scene_id)
	_complete_motions()
	match _awaiting:
		&"line":
			overlay.box.skip_reveal()
			overlay.box.advance_requested.emit()
		&"wait":
			_wait_left = 0.0
			wait_elapsed.emit()
		&"land":
			if _director_alive():
				_director.snap()
	return true


## Plays `scene_id` (a compiled scene under game/data/dialogue/compiled/) to its end on `stage`.
## Returns false when the scene could not be loaded or the cutscene was cut short. Await it.
func play(scene_id: StringName, stage: CutsceneStage) -> bool:
	if _playing:
		push_error("CutsceneSequencer: play(%s) while %s is playing" % [scene_id, _scene_id])
		return false
	runner = DialogueRunner.new(ReplayFlagAccess.new() if replay else null)
	runner.forward_events_to_bus = not replay
	if not runner.load_scene(scene_id) or not runner.start():
		push_error("CutsceneSequencer: cannot start scene '%s'" % scene_id)
		return false
	CutsceneStaging.apply(stage)  # M4-CIN-1304: cinematics' own shots and marks for the zone
	_begin(scene_id, stage)
	var step := runner.next()
	while not step.is_end() and not _aborted:
		if step.is_line():
			await _line(step)
		elif step.is_options():
			var picked: int = await _options(step)
			if not _aborted and picked >= 0:
				runner.choose(picked)
		else:
			await _cue(step)
		if not _aborted:
			step = runner.next()
	await _finish()
	return not _aborted


## Advances every timed thing by `delta` seconds: waits, fades, letterbox, moves, turns, music.
func advance(delta: float) -> void:
	# A reveal that ended early (skipped) releases the mouth; a natural end runs its own tail.
	if _speaking != null and overlay != null and not overlay.box.is_revealing():
		_speaking.end_line(delta)
	for rig: Variant in _face_rigs.values():
		if rig != null:
			(rig as CutsceneFace).advance(delta)
	if _playing and _skip_held and not _skipping and _awaiting != &"choice":
		var need := float(config.get("skip_hold_sec", 0.0))
		_hold += delta
		overlay.set_skip_progress(clampf(_hold / need, 0.0, 1.0) if need > 0.0 else 1.0)
		if _hold >= need:
			skip()
	for key: StringName in _motions.keys():
		var m: Dictionary = _motions[key]
		m["elapsed"] = float(m["elapsed"]) + delta
		var d := float(m["duration"])
		var t := 1.0 if d <= 0.0 else clampf(float(m["elapsed"]) / d, 0.0, 1.0)
		(m["apply"] as Callable).call(t)
		if t >= 1.0:
			_motions.erase(key)
	_breathe(delta)
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
	_face_rigs.clear()
	_speaking = null
	# Every actor with a face table gets its rig now, so it blinks before its first line (M2-FP-18).
	for actor_id: String in (config.get("face_poses", {}) as Dictionary).keys():
		_face_of(StringName(actor_id))
	# M2-HER-1104: every hero body on the stage breathes, shifts its weight and leads its turns with its
	# head (HeroIdleMicro, docs/kb/tech/hero_motion.md); a capsule stand-in gets nothing.
	if stage != null:
		for member: Node3D in stage.cast():
			var member_id := &"rhen" if member == _player else StringName(String(member.name).to_lower())
			HeroMotion.add_micro_motion(member, member_id)
	SaveSystem.hold_autosave(self)
	if not hold_player and not freeze_player:
		_player = null
	if _player != null:
		_player_input_was = _player.accepts_input
		_player.accepts_input = false
		_player.velocity = Vector3.ZERO
	if CutsceneCard.starts_black(scene_id):
		overlay.set_fade(1.0)
	runner.event_triggered.connect(_on_event)
	runner.node_started.connect(func(n: StringName) -> void: _grade(runner.headers(n).get("grade", "")))  # M2-FP-120
	_grade(runner.headers().get("grade", ""))


func _finish() -> void:
	var skipped := _skipping
	_skipping = false
	_awaiting = &""
	set_skip_held(false)
	if not skipped and not _aborted:  # M2-HER-1113: a running walk or turn plays out rather than jump to its end
		await _wait_for(CutsceneMotion.actor_motion_left(_motions))
	_complete_motions()
	_key_off()
	if overlay != null:
		overlay.box.dismiss()  # M2-UI-202: the box fades out at the end of a scene
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
	_held.clear()
	_npc_talk.end_all()
	_key_drop()
	grade.restore()
	SaveSystem.release_autosave(self)
	_playing = false
	finished.emit(_scene_id)


func _restore_player() -> void:
	if _player != null and is_instance_valid(_player):
		_player.accepts_input = _player_input_was
	_player = null


func _line(step: DialogueStep) -> void:
	if CutsceneCard.TAG in step.tags:  # M2-FP-121: a time card on black, not a line in the box
		overlay.set_fade(1.0)
		var card := CutsceneCard.open(self, step)
		if not _fast():
			await _await_on(&"wait", card.finished, _on_awaited_plain)
		CutsceneCard.close(card)
		return
	overlay.box.visible = true
	overlay.box.show_line(step)
	line_shown.emit(step)
	var speaker := _stage.actor(step.speaker) if _stage != null and step.speaker != &"" else null
	if speaker != null and not speaker.is_visible_in_tree():
		speaker = CutsceneNpcTalk.follower(_stage.get_parent(), step.speaker)  # M2-FP-110: the follower talks
	if speaker == null and _stage != null:
		_npc_talk.speak(_stage.get_parent(), step.speaker, _player)  # M2-FP-106: a villager turns and talks
	if speaker != null:
		if step.emotion != &"":
			_set_face(step.speaker, step.emotion, -1.0)
		_play_clip(speaker, &"talk")
		var rig := _face_of(step.speaker) if not step.is_sung() else null
		if _speaking != null and _speaking != rig:
			_speaking.end_line()
		_speaking = rig
		if rig != null:
			var cps := overlay.box.settings.chars_per_sec if overlay.box.settings != null else 0.0
			# The box's reveal times (M2-UI-27): the mouth rests while the reveal lingers at punctuation.
			rig.say(tr(String(step.text_key)), 0.0 if _fast() else cps, hash(step.text_key), overlay.box.reveal_times())
	if _fast():
		overlay.box.skip_reveal()
		return
	if TAG_TIMED in step.tags:
		return  # held by the script's own @wait, in time with its music (the first verse), not by input
	if auto_advance:
		if overlay.box.is_revealing():
			await _await_on(&"line", overlay.box.reveal_finished, _on_awaited_plain)
		await _wait_for(CutsceneMotion.read_hold(overlay.box, auto_advance_read_cps, auto_advance_hold_sec))
		return
	await _await_on(&"line", overlay.box.advance_requested, _on_awaited_plain)
	if speaker != null and is_instance_valid(speaker):
		_on_mouth_flap(step.speaker, false)
		_play_clip(speaker, &"idle")


func _options(step: DialogueStep) -> int:
	var pick := clampi(auto_choice, 0, step.options.size() - 1)
	if instant or auto_advance:
		return step.options[pick].index
	# A skip stops here: the player makes every choice themselves.
	_skipping = false
	overlay.choices.show_options(step.options)
	var chosen: Variant = await _await_on(&"choice", overlay.choices.chosen, _on_awaited_value)
	return int(chosen) if chosen != null else -1


func _cue(step: DialogueStep) -> void:
	cue_played.emit(step.cue, step.args, step.kwargs)
	for key: String in UNSUPPORTED_KWARGS.get(step.cue, []):
		if step.kwargs.has(key):
			_warn("@%s %s= is not performed yet (placeholder)" % [step.cue, key])
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
			var sec := float(step.args[2]) if step.args.size() > 2 else -1.0
			_set_face(StringName(str(step.args[0])), StringName(str(step.args[1])), sec)
		&"music":
			_cue_music(step)
		&"sfx":
			_cue_sfx(step)
		&"vfx":
			_cue_vfx(step)
		&"light":
			_cue_light(step)
		_:
			_warn("unknown cue @%s" % step.cue)


func _on_event(event_name: StringName, args: Array) -> void:
	events.append({"name": event_name, "args": args})
	if not replay:
		event_requested.emit(event_name, args)


# --- cues ------------------------------------------------------------------------------------


func _cue_camera(step: DialogueStep) -> void:
	if not _director_alive():
		_warn("@camera with no camera director on the stage")
		return
	var ease := StringName(str(step.kwargs.get("ease", "")))
	if step.is_camera_release():
		var back := float(step.kwargs.get("blend", CameraShot.USE_DEFAULT))
		_key_off()
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
		_key_for(_stage.shot_node(id))
		var who := str(step.kwargs.get("track", ""))  # M4-CIN-1302: one continuous move with an actor
		shot = CutsceneTrack.attach(self, shot, _actor(StringName(who)) if who != "" else null, _director)
		_director.play_shot(shot, blend, ease)
		_grade(step.kwargs.get("grade", ""))
	await _land()


## Waits for the director's move to land; a director that left the tree ends the cutscene.
func _land() -> void:
	if _fast():
		_director.snap()
		return
	if not _director.is_settled():
		await _await_on(&"land", _director.blend_finished, _on_awaited_value)
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
	var walk: Dictionary = _motions.get(StringName("move:%s" % step.kwargs.get("arrive", "")), {})
	if step.kwargs.has("arrive"):  # M2-FP-119: until that actor's walk lands, wherever it set off from
		await _wait_for(float(walk.get("duration", 0.0)) - float(walk.get("elapsed", 0.0)))
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
	var id := StringName(str(step.args[0]))
	var actor := _actor(id)
	var target_id := StringName(str(step.args[1]))
	var target := _stage.mark(target_id) if _stage != null else null
	if actor == null:
		return
	if target == null:
		_warn("no mark '%s' on the stage" % target_id)
		return
	_held.erase(actor)  # a walk ends any held pose
	var gait := StringName(str(step.args[2])) if step.args.size() > 2 else &"walk"
	var speed := maxf(float(config.get("run_mps" if gait == GAIT_RUN else "walk_mps", 1.0)), 0.01)
	# M3-CIN-1221: the way runs from where the actor stands through the `via` marks in order to the mark (round a
	# rail, down a stair, along a deck): one walk over the whole way, its turns eased at each corner.
	var path := PackedVector3Array([actor.global_position])
	for via_id in str(step.kwargs.get("via", "")).split(",", false):
		var via := _stage.mark(StringName(via_id.strip_edges())) if _stage != null else null
		if via == null:
			_warn("no via mark '%s' on the stage" % via_id.strip_edges())
			continue
		path.append(via.global_position)
	path.append(target.global_position)
	var flat := CutsceneMotion.flat_dir(path, 0)
	if flat.length() > 0.01:
		_turn_to(id, actor, flat)  # turns into the walk, never snaps
	# M2-FP-29: a beat of anticipation, then the walk speeds up, cruises and slows to a stop; the
	# walk clip cross-fades in as it sets off and back to idle as it settles.
	var dist := CutsceneMotion.path_length(path)
	var accel := float(config.get("walk_accel_sec", 0.0))
	var decel := float(config.get("walk_decel_sec", 0.0))
	var lead := float(config.get("walk_anticipation_sec", 0.0))
	var walk := CutsceneMotion.walk_duration(dist, speed, accel, decel)
	var dur := lead + walk
	var state := {"walking": false, "m": 0.0, "sec": 0.0, "leg": 0}
	_start_motion(
		&"move:%s" % id,
		dur,
		func(t: float) -> void:
			if not is_instance_valid(actor):
				return
			var sec := t * dur - lead
			if sec > 0.0 and t < 1.0 and not state["walking"]:
				state["walking"] = true
				_play_clip(actor, gait)
				if gait == GAIT_RUN:
					HeroMotion.set_locomotion_speed(actor, speed)  # M2-HER-1104: a run sets off as a run
			var s := CutsceneMotion.walk_fraction(sec, dist, speed, accel, decel) * dist
			var leg := CutsceneMotion.path_leg(path, s)
			if leg > int(state["leg"]) and t < 1.0:
				state["leg"] = leg
				var turn := CutsceneMotion.flat_dir(path, leg)
				if turn.length() > 0.01:
					_turn_to(id, actor, turn)  # the corner, eased like the first turn
			_place(actor, CutsceneMotion.path_point(path, s))
			_locomotion(actor, state, s, t * dur)
			if t >= 1.0:
				if not state["walking"]:
					_play_clip(actor, gait)  # instant or skipped: the walk still happened
				_play_clip(actor, &"idle")
				HeroMotion.set_locomotion_speed(actor, 0.0)
	)


func _cue_anim(step: DialogueStep) -> void:
	if CutsceneGroup.play(step, _stage, config, _start_motion, _cue_anim):  # M4-CIN-1302: a group, member by member
		return
	var actor := _actor(StringName(str(step.args[0])))
	if actor == null:
		return
	var clip := StringName(str(step.args[1]))
	var standin := _stage.clip_mark(StringName(str(step.args[0])), clip) if _stage != null else null
	if standin != null:
		# Stand on the clip's mark, facing its -Z (CutsceneStage.clip_marks); a built clip then plays there too.
		# M2-FP-29: glide onto it and turn, eased, rather than appear there.
		_motions.erase(&"move:%s" % step.args[0])
		var start := actor.global_position
		var end := standin.global_position
		# M2-HER-1113: a mark farther than standin_cut_m is a cut (the shot changes with it), not a glide across it.
		var far := start.distance_to(end)
		var glide := float(config.get("standin_glide_sec", 0.0)) if far > 0.01 and far <= _standin_cut_m() else 0.0
		var curve := float(config.get("turn_ease", 1.0))
		_start_motion(
			&"move:%s" % step.args[0],
			glide,
			func(t: float) -> void: _place(actor, start.lerp(end, CutsceneMotion.eased(t, curve)))
		)
		_turn_to(StringName(str(step.args[0])), actor, -standin.global_basis.z)
		if not CutsceneClips.has_clip(actor, clip):
			return
	if clip == ANIM_LOOK_AT and step.args.size() > 2:
		var tid := StringName(str(step.args[2]))
		var target := _stage.place(tid) if _stage != null else null
		if target == null:
			_warn("no look_at target '%s' on the stage" % tid)
			return
		_turn_to(StringName(str(step.args[0])), actor, target.global_position - actor.global_position)
		return
	_held.erase(actor)
	var hold := String(clip) in (config.get("hold_clips", []) as Array)
	clip = CutsceneClips.built(config, StringName(str(step.args[0])), actor, clip)
	var body := HeroMotion.body_of(actor)
	if body != null:
		body.call(&"play_clip", clip, _clip_blend(), hold)  # M2-HER-1104: the hero body's AnimationTree
	elif not HeroMotion.play(actor, clip, _clip_blend()):  # else its AnimationPlayer
		return
	if hold:
		_held[actor] = clip


func _cue_music(step: DialogueStep) -> void:
	var fade := float(step.kwargs.get("fade", config.get("music_fade_default_sec", 0.0)))
	var silent := float(config.get("silent_db", 0.0))
	if step.is_music_silence():
		music_track = &""
		if music_by_audio:
			CutsceneSound.music(AudioData.SILENCE, fade)
		music_by_audio = false
		_fade_music(silent, fade, true)
		return
	var track := StringName(str(step.args[0]))
	music_by_audio = CutsceneSound.music(track, fade, int(step.kwargs.get("stem", -1)))  # M2-AUD-07, M3-AUD-829
	if music_by_audio:
		music_track = &""
		_fade_music(silent, fade, true)
		return
	var stream := CutsceneSound.music_stream(config, track)
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
	var at_id := StringName(str(step.kwargs.get("at", "")))
	var at := _stage.place(at_id) if _stage != null and at_id != &"" else null
	var vol := float(step.kwargs.get("vol", 1.0))
	if not CutsceneSound.play(self, str(config.get("sfx_dir", "")), StringName(str(step.args[0])), vol, at):
		_warn("no sound '%s'" % step.args[0])


func _cue_vfx(step: DialogueStep) -> void:
	var rows: Dictionary = config.get("vfx", {})
	var effect := str(step.args[0])
	var at_id := StringName(str(step.kwargs.get("at", "")))
	var at := _stage.place(at_id) if _stage != null and at_id != &"" else null
	if not rows.has(effect) or (at_id != &"" and at == null):
		_warn("cannot place @vfx %s at '%s'" % [effect, at_id])
		return
	var host: Node3D = at if at != null else _stage
	if host != null and step.kwargs.has("release"):  # M4-CIN-1303: the light already there lets go and rises
		if not CutsceneVfx.release(host, float(step.kwargs["release"])):
			_warn("@vfx release=: nothing held at '%s'" % at_id)
		return
	if host == null or CutsceneVfxHosts.offer(get_tree(), effect, at_id, step.kwargs):  # M3-ARC-1326: a stage host
		return
	var vfx_name := "Vfx_%s_%d" % [effect, _vfx_count]
	var field := CutsceneVfx.spawn(rows[effect], effect, step.kwargs, host, vfx_name, finished)
	if field == null:
		_warn("no @vfx %s %s" % [effect, step.kwargs])
	elif float(rows[effect].get("end_after_sec", 0.0)) > 0.0:  # one shot's light (S08's bound Ilun), on scene time
		_start_motion(StringName("vfx_end:%d" % _vfx_count), rows[effect]["end_after_sec"], CutsceneVfx.ender(field))
	_vfx_count += 1


## M2-FP-120: a grade (CutsceneGrade) on the stage's level, from a node's `grade:` header or `@camera grade=`. One
## nobody has built yet is not a stage gap: it waits on Rendering (test_cutscene_directives' list).
func _grade(id: Variant) -> void:
	if str(id) != "":
		grade.apply(_stage, StringName(str(id)))


## M2-FP-102: `@light <name> on|off [sec]` (CutsceneLight).
func _cue_light(step: DialogueStep) -> void:
	var light_ease := float(config.get("light_ease", 1.0))
	if not CutsceneLight.cue(_stage, step.args, light_ease, SWITCH_ON, _start_motion):
		_warn("no light '%s' on the stage" % step.args[0])


# --- key light (M2-FP-10) --------------------------------------------------------------------


## Keys the cast for a close shot (or a shot forced ON), and lets the sun back for any other.
func _key_for(sn: CutsceneShotNode) -> void:
	if sn == null or not _wants_key(sn):
		_key_off()
		return
	var sun := _stage.sun()
	if sun == null:
		_warn("a close shot with no sun on the stage to key the cast from")
		_key_off()
		return
	if _key == null or not is_instance_valid(_key):
		_key = CutsceneKeyLight.new(config.get("key_light", {}))
		_stage.add_child(_key)
	_key.engage(sun, _stage.cast(), sn.key_yaw_deg, sn.key_pitch_deg, sn.key_energy_scale)


func _wants_key(sn: CutsceneShotNode) -> bool:
	if sn.key_light != CutsceneShotNode.KeyLight.AUTO:
		return sn.key_light == CutsceneShotNode.KeyLight.ON
	var shot := sn.shot
	if shot.moves_with_player() or _director.rail_root == null:
		return false  # the camera moves with the player: no fixed framing to judge
	var root := _director.rail_root.global_transform
	var aim := _director.aim_point(shot) if not shot.aim_node.is_empty() else root * shot.look_at
	var fov := shot.fov_deg if shot.fov_deg > 0.0 else float(_director.data.get("default_fov_deg", 0.0))
	return CutsceneKeyLight.is_close(root * shot.position, aim, fov, config.get("key_light", {}))


func _key_off() -> void:
	if _key != null and is_instance_valid(_key):
		_key.disengage()


## The scene is over: the sun keys everyone again and the light leaves the stage.
func _key_drop() -> void:
	_key_off()
	if _key != null and is_instance_valid(_key):
		_key.queue_free()
	_key = null


# --- helpers ---------------------------------------------------------------------------------


func _ensure_overlay() -> void:
	if config.is_empty():
		config = load_config()
	if overlay == null:
		overlay = CutsceneOverlay.new(config)
		add_child(overlay)
	if not overlay.box.mouth_flap.is_connected(_on_mouth_flap):
		overlay.box.mouth_flap.connect(_on_mouth_flap)
	if music == null:
		music = AudioStreamPlayer.new()
		music.name = "Music"
		add_child(music)


## Blends `actor_id`'s face to emotion `expr` over `sec` (< 0: the pose table's blend_in_s).
func _set_face(actor_id: StringName, expr: StringName, sec: float) -> void:
	var rig := _face_of(actor_id)
	var table: Dictionary = _pose_tables.get(actor_id, {})
	var poses: Dictionary = table.get("emotions", {})
	if rig == null or not poses.has(String(expr)):
		return
	rig.emotion = expr
	var t := sec if sec >= 0.0 else float(table.get("blend_in_s", 0.0))
	rig.blend_to(poses[String(expr)], 0.0 if _fast() else t)


func _face_of(actor_id: StringName) -> CutsceneFace:
	if _face_rigs.has(actor_id):
		return _face_rigs[actor_id]
	var rig: CutsceneFace = null
	var path := str((config.get("face_poses", {}) as Dictionary).get(String(actor_id), ""))
	var actor := _stage.actor(actor_id) if _stage != null else null
	if actor != null and path != "" and FileAccess.file_exists(path):
		if not _pose_tables.has(actor_id):
			var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(path))
			_pose_tables[actor_id] = parsed if parsed is Dictionary else {}
		if _lipsync.is_empty():
			_lipsync = LipSync.load_config()
		rig = CutsceneFace.new(actor, config.get("lip_flap", {}), _lipsync)
		rig.configure_blink(config.get("blink", {}), DEFAULT_SEED + hash(actor_id), actor_id)
		if not rig.has_shapes():
			rig = null
	_face_rigs[actor_id] = rig
	return rig


func _on_mouth_flap(speaker: StringName, open: bool) -> void:
	var rig := _face_of(speaker) if _playing else null
	if rig != null:
		rig.set_mouth_open(open)


## Plays the actor's clip for `role` (sequencer.json "clips": idle, talk, walk, run) when the rig
## has it, cross-faded from the current one and never restarting one already playing; nothing
## otherwise (M2-FP-07 asks Character for the clips). M2-HER-1104: through HeroMotion.play, so a hero
## body's play_clip (its AnimationTree) takes it, else the actor's AnimationPlayer.
func _play_clip(actor: Node3D, role: StringName) -> void:
	if _held.has(actor) and role != GAIT_RUN and role != &"walk":
		return  # M2-FP-103: a held pose (kneeling, a levelled spear) is not stood up by a line
	var clip := StringName(str((config.get("clips", {}) as Dictionary).get(String(role), "")))
	if clip != &"":
		HeroMotion.play(actor, clip, _clip_blend(), false)


## M2-FP-104: a landed scripted shot breathes (CutsceneCameraBreath); a blend, a skip or the field resets it.
func _breathe(delta: float) -> void:
	if _breath == null:
		_breath = CutsceneCameraBreath.new(config.get("camera_breath", {}) as Dictionary)
	if not _playing or _fast() or not _director_alive() or not _director.is_scripted() or _director.is_blending():
		_breath.reset()
		return
	_breath.apply(_director.camera, delta)


## M2-HER-1104: tells a hero body how fast its root walks (`metres` covered at `now` seconds into the
## move), so a speed-driven gait blend follows the walk's ramps and the idle micro-motion fades out.
func _locomotion(actor: Node3D, state: Dictionary, metres: float, now: float) -> void:
	var dt := now - float(state["sec"])
	var mps := (metres - float(state["m"])) / dt if dt > 0.0 else 0.0
	state["m"] = metres
	state["sec"] = now
	HeroMotion.set_locomotion_speed(actor, mps)


## The cross-fade between two clips (sequencer.json clip_blend_sec; none while skipping or instant).
func _clip_blend() -> float:
	return 0.0 if _fast() else float(config.get("clip_blend_sec", 0.0))


## Awaits `sig` (connected one-shot to `handler`, which emits `resumed`), as `kind` for skip().
## _exit_tree can release it early with null.
func _await_on(kind: StringName, sig: Signal, handler: Callable) -> Variant:
	_awaiting = kind
	_await_sig = sig
	_await_cb = handler
	sig.connect(handler, CONNECT_ONE_SHOT)
	var v: Variant = await resumed
	_awaiting = &""
	_await_cb = Callable()
	return v


func _on_awaited_plain() -> void:
	resumed.emit(true)


func _on_awaited_value(value: Variant) -> void:
	resumed.emit(value)


func _release_await(value: Variant) -> void:
	if _await_cb.is_valid() and not _await_sig.is_null() and _await_sig.is_connected(_await_cb):
		_await_sig.disconnect(_await_cb)
	resumed.emit(value)


## No time passes: a test (`instant`) or a skip in progress.
func _fast() -> bool:
	return instant or _skipping


func _director_alive() -> bool:
	return _director != null and is_instance_valid(_director) and not _director.is_leaving()


func _actor(id: StringName) -> Node3D:
	var a := _stage.actor(id) if _stage != null else null
	if a == null:
		_warn("no actor '%s' on the stage" % id)
	return a


func _wait_for(sec: float) -> void:
	if _fast() or sec <= 0.0:
		return
	_wait_left = sec
	await _await_on(&"wait", wait_elapsed, _on_awaited_plain)


func _start_motion(key: StringName, duration: float, apply: Callable) -> void:
	if _fast() or duration <= 0.0:
		_motions.erase(key)
		apply.call(1.0)
		return
	_motions[key] = {"elapsed": 0.0, "duration": duration, "apply": apply}


func _standin_cut_m() -> float:
	return float(config.get("standin_cut_m", INF))


func _complete_motions() -> void:
	for key: StringName in _motions.keys():
		((_motions[key] as Dictionary)["apply"] as Callable).call(1.0)
	_motions.clear()


func _start_fade(to: float, sec: float) -> void:
	var from := overlay.fade_alpha()
	# M2-FP-102: the fade eases in and out (sequencer.json fade_ease), so a scene never pops to or from black.
	var curve := float(config.get("fade_ease", 1.0))
	_start_motion(
		&"fade", sec, func(t: float) -> void: overlay.set_fade(lerpf(from, to, CutsceneMotion.eased(t, curve)))
	)


func _set_letterbox(on: bool) -> void:
	var from := overlay.letterbox()
	var to := 1.0 if on else 0.0
	var sec := float(config.get("letterbox_sec", 0.0))
	var curve := float(config.get("letterbox_ease", 1.0))
	_start_motion(
		&"letterbox",
		sec,
		func(t: float) -> void: overlay.set_letterbox(lerpf(from, to, CutsceneMotion.eased(t, curve)))
	)


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
	# M2-FP-29: eased in and out, over a time that grows with the angle (turn_min_sec..turn_sec).
	var curve := float(config.get("turn_ease", 1.0))
	var sec := CutsceneMotion.turn_duration(
		to - from, float(config.get("turn_min_sec", 0.0)), float(config.get("turn_sec", 0.0))
	)
	_start_motion(
		&"turn:%s" % id, sec, func(t: float) -> void: _face_yaw(actor, lerpf(from, to, CutsceneMotion.eased(t, curve)))
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
func _warn(msg: String) -> void:
	var full := "CutsceneSequencer(%s): %s" % [_scene_id, msg]
	if full in warnings:
		return
	warnings.append(full)
	push_warning(full)
