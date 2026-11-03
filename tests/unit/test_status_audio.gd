extends TestCase
## M3-AUD-866 (the human's playtest FAST-TRACKs 3 and 5, 11-03): status effects you can hear. Every status in
## statuses.json has its own apply cue that exists; a hit that adds one plays it in place of the generic status sound
## (the view's `status` effect is silenced); an item that lifts a harmful status plays the cure, a beneficial one the
## fade; a revive plays the revive; a miss plays none. Driven through the view's and the engine's signals, as in play.

const ENCOUNTER := &"sandbox_reef"
const STATUSES := "res://game/data/battle/statuses.json"

var engine: BattleEngine
var dir: AudioDirector
var vfx: BattleVfx
var audio: BattleAudio
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
	audio = BattleAudio.new()
	audio.name = "BattleAudio"
	dir.add_child(audio)
	audio.attach(dir, null, engine, vfx)
	dir.flush_pending()


func _teardown() -> void:
	if audio != null and is_instance_valid(audio):
		audio.free()
	for p: Node in dir.find_children("*", "AudioStreamPlayer", true, false):
		(p as AudioStreamPlayer).stop()
	dir.free()
	vfx.free()


func test_every_status_has_its_own_cue_that_exists() -> void:
	var rows := AudioData.table(BattleAudio.TABLE).get("statuses", {}) as Dictionary
	var own := rows.get("apply", {}) as Dictionary
	var sfx := AudioData.sfx_rows()
	var doc: Variant = JSON.parse_string(FileAccess.get_file_as_string(STATUSES))
	var ids: Array = []
	for row: Variant in (doc as Dictionary).get("statuses", doc) as Array:
		ids.append(str((row as Dictionary)["id"]))
	assert_true(ids.size() >= 21, "statuses.json read")
	var seen := {}
	for id: String in ids:
		assert_true(own.has(id), "%s has its own cue" % id)
		var cue := str(own.get(id, ""))
		assert_true(sfx.has(cue), "%s: %s is an sfx row" % [id, cue])
		assert_false(seen.has(cue), "%s's cue is its own" % id)
		seen[cue] = true
		for f: Variant in (sfx.get(cue, {}) as Dictionary).get("files", []):
			assert_true(ResourceLoader.exists(str(f)), "%s exists" % f)
	for key: String in ["cure", "fade", "revive", "generic"]:
		assert_true(sfx.has(str(rows.get(key, ""))), "%s is an sfx row" % key)
	_teardown()


func test_a_status_added_plays_its_own_cue_not_the_generic() -> void:
	var r := _result(&"attack", [{"target_id": _foe(), "hit": true, "amount": 0, "statuses_added": [&"poison"]}])
	_view_plays(r)
	engine.action_resolved.emit(r)
	assert_true(audio.played.has(&"status_poison"), "poison's own cue: %s" % [audio.played])
	var generic := audio._players.get(&"status_apply", null) as AudioStreamPlayer
	assert_true(generic == null or not generic.playing, "the generic status sound is silenced")
	_done_counts(&"status_poison", 1)
	_teardown()


func test_two_statuses_on_two_targets_each_play() -> void:
	var foe2 := engine.enemies[mini(1, engine.enemies.size() - 1)].id
	var r := _result(
		&"attack",
		[
			{"target_id": _foe(), "hit": true, "amount": 0, "statuses_added": [&"slow"]},
			{"target_id": foe2, "hit": true, "amount": 0, "statuses_added": [&"darkness"]},
			{"target_id": foe2, "hit": false, "amount": 0, "statuses_added": [&"sleep"]},
		]
	)
	engine.action_resolved.emit(r)
	var got := audio.play_statuses(r)
	assert_eq(got, [&"status_slow", &"status_darkness"] as Array[StringName], "a miss plays nothing")
	_teardown()


func test_the_generic_is_dropped_when_it_comes_after() -> void:
	var r := _result(&"attack", [{"target_id": _foe(), "hit": true, "amount": 0, "statuses_added": [&"haste"]}])
	engine.action_resolved.emit(r)
	_view_plays(r)  # the view's effect arriving second
	assert_false(audio.played.has(&"status_apply"), "dropped: %s" % [audio.played])
	assert_true(audio.played.has(&"status_haste"))
	_teardown()


func test_a_status_with_no_row_keeps_the_generic() -> void:
	var r := _result(&"attack", [{"target_id": _foe(), "hit": true, "amount": 0, "statuses_added": [&"no_such"]}])
	_view_plays(r)
	engine.action_resolved.emit(r)
	assert_true(audio.played.has(&"status_apply"), "the generic still sounds")
	_teardown()


func test_cure_fade_and_revive() -> void:
	var ally := engine.party_active[0].id
	var r := ActionResult.new()
	r.actor_id = ally
	r.item_id = &"tonic"
	r.hits.append({"target_id": ally, "hit": true, "amount": -10, "statuses_removed": [&"poison"]})
	r.hits.append({"target_id": ally, "hit": true, "amount": 0, "statuses_removed": [&"protect"]})
	r.hits.append({"target_id": ally, "hit": true, "amount": -1, "revived": true, "statuses_added": []})
	assert_eq(audio.play_statuses(r), [&"status_cure", &"status_fade", &"revive"] as Array[StringName], "in hit order")
	_teardown()


func _done_counts(id: StringName, want: int) -> void:
	assert_eq(audio.played.count(id), want, "%s once" % id)


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
