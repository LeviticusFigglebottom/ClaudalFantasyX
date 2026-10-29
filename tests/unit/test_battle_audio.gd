extends TestCase
## M2-AUD-04: the battle's sound (game/audio/battle_audio.gd, battle_sfx.json, sfx_battle.json). Every BattleVfx
## effect has a sound that exists; a fire hit, a KO, the Flood, the opening stingers and the Vowbound's call and
## dismiss play theirs; a fallback hook never doubles a sound the view already played; repeats on an action's
## other targets layer; and reduced audio keeps one layer per action, swaps in the soft Flood and lowers the bank.
## The listener is driven through the signals it listens to (the view's effect_played, the engine's), as in play.

const ENCOUNTER := &"sandbox_reef"
const DROWNBELL_ENCOUNTER := &"drownbell"
const FLOOD := &"flood"

var engine: BattleEngine
var dir: AudioDirector
var vfx: BattleVfx
var audio: BattleAudio
var settings: UiSettings
var prev_settings: UiSettings
var now_ms := 1000


func before_each() -> void:
	now_ms = 1000
	engine = BattleEngine.new()
	var party: Array[StringName] = [&"rhen", &"asha"]
	var reserve: Array[StringName] = []
	engine.setup(BattleDB.load_default(), party, reserve, ENCOUNTER, 7)
	dir = AudioDirector.new()
	_host().add_child(dir)
	dir.setup(AudioData.table(AudioData.MIX), AudioData.table(AudioData.MUSIC), {"sfx": AudioData.sfx_rows()})
	dir.set_process(false)
	dir.sfx.clock = func() -> int: return now_ms
	vfx = BattleVfx.new()
	vfx._engine = engine
	prev_settings = UiSettings.shared()
	settings = UiSettings.new()
	UiSettings.set_shared(settings)


func _attach() -> void:
	audio = BattleAudio.new()
	audio.name = "BattleAudio"
	dir.add_child(audio)
	audio.attach(dir, null, engine, vfx)
	dir.flush_pending()  # the battle cue loads on a worker thread


func _teardown() -> void:
	if audio != null and is_instance_valid(audio):
		audio.free()
	# Stop every player first: a playback still running when its player is freed outlives it in the AudioServer.
	for p: Node in dir.find_children("*", "AudioStreamPlayer", true, false):
		(p as AudioStreamPlayer).stop()
	dir.free()
	vfx.free()
	UiSettings.set_shared(prev_settings)


func test_every_effect_maps_to_a_sound_that_exists() -> void:
	_attach()
	var table := AudioData.table(BattleAudio.TABLE)
	var hooks := table.get("vfx", {}) as Dictionary
	for eid: String in BattleVfx.load_data()["effects"] as Dictionary:
		assert_true(hooks.has(eid), "effect %s has a sound" % eid)
		var sid := StringName(str(hooks.get(eid, "")))
		assert_true(dir.sfx.has(sid), "%s -> sfx row %s" % [eid, sid])
		for f: Variant in (dir.sfx.rows.get(String(sid), {}) as Dictionary).get("files", []):
			assert_true(ResourceLoader.exists(str(f)), "%s: %s imports" % [sid, f])
	for section: String in ["skills", "events", "fields_cleared", "phases", "openings", "outcomes", "reduced"]:
		var rows := table.get(section, {}) as Dictionary
		for key: String in rows:
			assert_true(dir.sfx.has(StringName(str(rows[key]))), "%s.%s -> %s" % [section, key, rows[key]])
	assert_true(FileAccess.file_exists("res://assets/audio/sfx/drownbell_toll.ogg"), "the cutscene's @sfx toll")
	_teardown()


func test_a_fire_hit_plays_the_fire_sound() -> void:
	_attach()
	var r := _result(&"ember", [{"target_id": _foe(), "hit": true, "amount": 12, "statuses_added": []}])
	_view_plays(r)
	engine.action_resolved.emit(r)
	# M3-BPR-421 / M3-AUD-861: Ember's own effect has its own sound (a small flame climbing), and the damage it does
	# plays the fire hit under it.
	assert_eq(audio.played[0], &"abl_ember", "Ember's own sound")
	assert_true(audio.played.has(&"hit_fire"), "and the fire hit lands: %s" % [audio.played])
	var fire: Array = dir.sfx.history.filter(func(h: Array) -> bool: return h[0] == &"hit_fire")
	assert_true(not fire.is_empty() and str(fire[0][1]).contains("/battle/hit_fire_"), "one of the fire variants")
	_teardown()


func test_a_ko_plays_the_released_glimmer() -> void:
	_attach()
	engine.find(_foe()).hp = 0
	var r := _result(&"attack", [{"target_id": _foe(), "hit": true, "amount": 30, "statuses_added": []}])
	_view_plays(r)
	assert_eq(audio.played, [&"hit_none", &"ko_release"] as Array[StringName])
	_teardown()


func test_the_flood_phase_surges_and_brings_its_stem_in() -> void:
	_attach()
	engine.phase_changed.emit(engine.enemies[0], FLOOD)
	assert_eq(audio.played, [&"flood"] as Array[StringName], "the water rising")
	var battle := dir.music_data.get("battle", {}) as Dictionary
	var row := (battle.get("phases", {}) as Dictionary).get(String(FLOOD), {}) as Dictionary
	var cue := AudioData.battle_cue(dir.music_data, DROWNBELL_ENCOUNTER)
	if not row.is_empty() and (battle.get("encounters", {}) as Dictionary).has(String(DROWNBELL_ENCOUNTER)):
		assert_true(dir.play_music(cue, 0.0), "the drownbell cue plays")
		now_ms += 2000
		engine.phase_changed.emit(engine.enemies[0], FLOOD)
		dir.music.advance(float(row.get("sec", 0.0)) + 0.1)
		for i: Variant in row.get("stems_on", []):
			assert_true(dir.music.stem_gain(int(i)) > 0.99, "stem %s comes in at the Flood" % i)
	engine.field_cleared.emit(FLOOD, [] as Array[BattleCombatant])
	assert_true(audio.played.has(&"floodnet"), "Floodnet: Ilun clears the field")
	_teardown()


## M3-AUD-861: the Undertow's Reach plays its own cue, its Dark and Breach bring its stems in, and each seawall
## wave starts heavier than the last.
func test_the_reach_and_the_seawall_waves_play_their_stems() -> void:
	_attach()
	var cue := AudioData.battle_cue(dir.music_data, &"undertows_reach")
	assert_eq(cue, &"undertows_reach", "the Reach is not the default battle music")
	assert_true(dir.play_music(cue, 0.0), "its cue plays")
	var phases := (dir.music_data.get("battle", {}) as Dictionary).get("phases", {}) as Dictionary
	for ph: StringName in [&"dark", &"breach"]:
		var row := phases.get(String(ph), {}) as Dictionary
		engine.phase_changed.emit(engine.enemies[0], ph)
		dir.music.advance(float(row.get("sec", 0.0)) + 0.1)
		for i: Variant in row.get("stems_on", []):
			assert_true(dir.music.stem_gain(int(i)) > 0.99, "%s brings stem %s in" % [ph, i])
	var starts: Array[int] = []
	for enc: StringName in [&"ch08_stair_hold_1", &"ch08_stair_hold_2", &"ch08_stair_hold_3"]:
		var row := (
			(dir.music_data.get("cues", {}) as Dictionary).get(String(AudioData.battle_cue(dir.music_data, enc)), {})
			as Dictionary
		)
		starts.append((row.get("start_stems", []) as Array).size())
	assert_eq(starts, [1, 2, 3] as Array[int], "each wave starts with one more stem of seawall_hold")
	_teardown()


func test_the_opening_stinger_plays_once() -> void:
	engine.opening = BattleOpening.AMBUSH
	_attach()
	vfx.effect_played.emit(&"flash_ambush", Vector3.ZERO)
	assert_eq(audio.played, [&"stinger_ambush"] as Array[StringName])
	assert_eq(audio.play_key("openings", "ambush"), &"", "the fallback never doubles the view's stinger")
	now_ms += 1000
	assert_eq(audio.play_key("openings", "preemptive"), &"stinger_preemptive")
	_teardown()


func test_the_toll_rings_once_from_either_hook() -> void:
	_attach()
	var bell := engine.enemies[0]
	var r := _result(&"toll", [])
	r.actor_id = bell.id
	vfx.effect_played.emit(&"flash_toll", Vector3.ZERO)
	engine.action_resolved.emit(r)
	assert_eq(audio.played, [&"drownbell_toll"] as Array[StringName], "the flash's toll; the skill's is dropped")
	now_ms += 5000
	engine.action_resolved.emit(r)
	assert_eq(audio.played.size(), 2, "with no flash (one was suppressed), the skill rings it")
	_teardown()


func test_the_vowbound_call_and_dismiss() -> void:
	_attach()
	var v := engine.party_active[0]
	engine.vowbound.called.emit(v)
	now_ms += 1000
	engine.vowbound.departed.emit(v, false)
	now_ms += 1000
	engine.vowbound.departed.emit(v, true)
	assert_eq(audio.played, [&"vowbound_call", &"vowbound_dismiss", &"ko_release"] as Array[StringName])
	_teardown()


func test_calling_ilun_plays_her_sting_on_the_music_bus() -> void:
	_attach()
	var ilun := BattleCombatant.new()
	ilun.id = &"ilun"
	engine.vowbound.called.emit(ilun)
	assert_eq(audio.played, [&"vowbound_call", &"ilun_summon"] as Array[StringName], "the call, then Ilun's own sting")
	var sting: AudioStreamPlayer = null
	for p: Node in dir.sfx.get_children():
		if String(p.name).begins_with("ilun_summon"):
			sting = p as AudioStreamPlayer
	assert_true(sting != null and sting.bus == &"Music", "the sting is music")
	_teardown()


func test_repeats_on_other_targets_layer_softer() -> void:
	_attach()
	vfx.effect_played.emit(&"heal", Vector3.ZERO)
	vfx.effect_played.emit(&"heal", Vector3.ZERO)
	assert_eq(audio.played, [&"heal", &"heal"] as Array[StringName], "full audio: every target")
	var layer_db := float(AudioData.table(BattleAudio.TABLE).get("layer_db", 0.0))
	assert_true(layer_db < 0.0, "a repeat is a softer layer")
	_teardown()


func test_reduced_audio_drops_repeats_softens_the_flood_and_lowers_the_bank() -> void:
	_attach()
	var reduced_level := float(AudioData.table(BattleAudio.TABLE).get("reduced_level", 1.0))
	assert_eq(dir.sfx.level, 1.0)
	settings.set_value(BattleAudio.REDUCED_AUDIO, true)
	assert_true(audio.reduced, "followed live")
	assert_true(is_equal_approx(dir.sfx.level, reduced_level), "the bank plays softer")
	vfx.effect_played.emit(&"heal", Vector3.ZERO)
	vfx.effect_played.emit(&"heal", Vector3.ZERO)
	assert_eq(audio.played, [&"heal"] as Array[StringName], "one layer per action")
	now_ms += 500
	vfx.effect_played.emit(&"heal", Vector3.ZERO)
	assert_eq(audio.played.size(), 2, "a later action still sounds")
	engine.phase_changed.emit(engine.enemies[0], FLOOD)
	assert_eq(audio.played[audio.played.size() - 1], &"flood_soft", "the Flood without its sub-bass")
	settings.set_value(BattleAudio.REDUCED_AUDIO, false)
	assert_true(is_equal_approx(dir.sfx.level, 1.0), "back to full")
	settings.set_value(BattleAudio.REDUCED_AUDIO, true)
	dir.remove_child(audio)
	assert_true(is_equal_approx(dir.sfx.level, 1.0), "leaving the battle puts the bank's level back")
	_teardown()


func test_overlapping_listeners_compose_the_level() -> void:
	settings.set_value(BattleAudio.REDUCED_AUDIO, true)
	_attach()
	var first := audio
	_attach()  # a retry: the new listener attaches before the old one leaves
	first.free()
	var reduced_level := float(AudioData.table(BattleAudio.TABLE).get("reduced_level", 1.0))
	assert_true(is_equal_approx(dir.sfx.level, reduced_level), "the retry keeps the reduced level")
	audio.free()
	assert_true(is_equal_approx(dir.sfx.level, 1.0), "and both gone, full level")
	_teardown()


## What the view would play for `r`, as effect_played (the view's particles need a stage; the listener only
## needs the signal).
func _view_plays(r: ActionResult) -> void:
	for e: Dictionary in vfx.effects_for(r):
		vfx.effect_played.emit(e["effect"], Vector3.ZERO)


func _result(skill: StringName, hits: Array) -> ActionResult:
	var r := ActionResult.new()
	r.actor_id = engine.party_active[0].id
	r.skill_id = skill
	for h: Dictionary in hits:
		r.hits.append(h)
	return r


func _foe() -> StringName:
	return engine.enemies[0].id


func _host() -> Node:
	return (Engine.get_main_loop() as SceneTree).current_scene
