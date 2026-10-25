extends TestCase
## M3-AUD-14: the creatures' voices and movement (game/audio/creature_audio.gd, creature_voices.json,
## sfx_creatures.json). Every enemy has a voice whose files import; the battle opens with one idle; a creature's
## action plays its attack (and its movement while no model is heard); a damaging hit plays one hurt per kind, a KO
## one death; a hero's action and a miss play nothing; a model's clips play its movement by name; reduced audio
## leaves the idle and the movement out; BattleAudio brings the listener along. Driven through the signals it
## listens to, with the SFX bank's clock replaced, as in tests/unit/test_battle_audio.gd.

const ENCOUNTER := &"sandbox_reef"

var engine: BattleEngine
var dir: AudioDirector
var ca: CreatureAudio
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


func _attach(battle: BattleAudio = null) -> void:
	ca = CreatureAudio.new()
	dir.add_child(ca)
	ca.set_process(false)  # the test flushes the queue on its own clock
	ca.attach(dir, null, engine, battle)


func _teardown() -> void:
	if ca != null and is_instance_valid(ca):
		ca.free()
	for p: Node in dir.find_children("*", "AudioStreamPlayer", true, false):
		(p as AudioStreamPlayer).stop()
	dir.free()


## Lets `ms` pass and plays what fell due.
func _wait(ms: int) -> void:
	now_ms += ms
	ca.flush(now_ms)


func test_every_enemy_has_a_voice_whose_files_import() -> void:
	_attach()
	var creatures := ca.data.get("creatures", {}) as Dictionary
	for e: Variant in BattleDB.load_default().enemies.values():
		var eid := str((e as Dictionary).get("id", ""))
		assert_true(creatures.has(eid), "enemy %s has a voice row or is silent" % eid)
	for cid: String in creatures:
		if creatures[cid] is String:
			continue
		for ev: String in (creatures[cid] as Dictionary).get("events", {}):
			var sid := ca.sfx_for(cid, StringName(ev))
			assert_true(dir.sfx.has(sid), "%s.%s -> sfx row %s" % [cid, ev, sid])
			for f: Variant in (dir.sfx.rows.get(String(sid), {}) as Dictionary).get("files", []):
				assert_true(ResourceLoader.exists(str(f)), "%s: %s imports" % [sid, f])
	_teardown()


func test_the_battle_opens_with_one_idle() -> void:
	_attach()
	_wait(1)
	assert_eq(ca.played, [] as Array[String], "the idle waits its delay")
	_wait(1000)
	assert_eq(ca.played, ["reef_crab:idle"] as Array[String], "the first voiced enemy, once")
	engine.combatants_joined.emit([engine.enemies[0]] as Array[BattleCombatant])
	_wait(1000)
	assert_eq(ca.played.size(), 1, "a kind's idle waits its cooldown")
	_teardown()


func test_a_creature_action_plays_its_attack_and_its_movement() -> void:
	_attach()
	_wait(2000)
	ca.played.clear()
	engine.action_resolved.emit(_result(engine.enemies[0].id, &"pinch", []))
	_wait(0)
	assert_eq(ca.played, ["reef_crab:attack", "reef_crab:move"] as Array[String], "no model heard: move with it")
	ca.played.clear()
	engine.action_resolved.emit(_result(engine.party_active[0].id, &"attack", []))
	_wait(1000)
	assert_eq(ca.played, [] as Array[String], "a hero's action has no creature voice")
	_teardown()


func test_a_hit_hurts_once_per_kind_and_a_ko_dies_once() -> void:
	_attach()
	_wait(2000)
	ca.played.clear()
	var foe := engine.enemies[0].id
	var hits := [_hit(foe, 20), _hit(foe, 15), _hit(engine.enemies[1].id, 0), {"target_id": foe, "hit": false}]
	engine.action_resolved.emit(_result(engine.party_active[0].id, &"attack", hits))
	_wait(10)
	assert_eq(ca.played, [] as Array[String], "the hurt sits just behind the hit sound")
	_wait(200)
	assert_eq(ca.played, ["reef_crab:hurt"] as Array[String], "one hurt; no voice for a 0 hit or a miss")
	var last: Array = dir.sfx.history[dir.sfx.history.size() - 1]
	assert_eq(last[0], ca.sfx_for("reef_crab", CreatureAudio.HURT))
	ca.played.clear()
	engine.find(foe).hp = 0
	engine.action_resolved.emit(_result(engine.party_active[0].id, &"attack", [_hit(foe, 30)]))
	engine.action_resolved.emit(_result(engine.party_active[0].id, &"attack", [_hit(foe, 30)]))
	engine.turn_ended.emit(engine.find(foe), [] as Array[Dictionary])
	_wait(500)
	assert_eq(ca.played, ["reef_crab:death"] as Array[String], "one death")
	_teardown()


func test_poison_taking_it_down_on_its_turn_is_a_death() -> void:
	_attach()
	_wait(2000)
	ca.played.clear()
	var eel := engine.enemies[1]
	eel.hp = 0
	engine.turn_ended.emit(eel, [] as Array[Dictionary])
	_wait(500)
	assert_eq(ca.played, ["lantern_eel:death"] as Array[String])
	_teardown()


func test_a_model_clip_plays_the_movement_by_name() -> void:
	_attach()
	_wait(2000)
	ca.played.clear()
	var model := Node3D.new()
	var player := AnimationPlayer.new()
	model.add_child(player)
	_host().add_child(model)
	var bare := Node3D.new()
	assert_false(ca.watch_model(bare, "lantern_eel"), "no AnimationPlayer: nothing to hear")
	bare.free()
	assert_true(ca.watch_model(model, "lantern_eel"), "its AnimationPlayer is heard")
	assert_eq(ca.model_base(model), "", "a node without a model class is not found on its own")
	player.animation_started.emit(&"attack")
	player.animation_started.emit(&"idle")
	_wait(0)
	assert_eq(ca.played, ["lantern_eel:move"] as Array[String], "attack -> move; idle has no sound")
	ca.played.clear()
	engine.action_resolved.emit(_result(engine.enemies[1].id, &"lure_glow", []))
	_wait(0)
	assert_eq(ca.played, ["lantern_eel:attack"] as Array[String], "with a model heard, its clips move it")
	model.free()
	assert_eq(int(ca.models.get("lantern_eel", 0)), 0, "the model left")
	_teardown()


func test_reduced_audio_leaves_out_the_idle_and_the_movement() -> void:
	var battle := BattleAudio.new()
	battle.reduced = true
	_attach(battle)
	_wait(2000)
	engine.action_resolved.emit(_result(engine.enemies[2].id, &"dive_rake", []))
	_wait(0)
	assert_eq(ca.played, ["gull_harrier:attack"] as Array[String])
	_teardown()
	battle.free()


func test_battle_audio_brings_the_creature_listener() -> void:
	var vfx := BattleVfx.new()
	vfx._engine = engine
	var audio := BattleAudio.new()
	dir.add_child(audio)
	audio.attach(dir, null, engine, vfx)
	dir.flush_pending()  # the battle cue loads on a worker thread
	assert_true(audio.creatures != null and audio.creatures.get_parent() == audio, "a CreatureAudio child")
	assert_true(audio.creatures.engine == engine, "on the same engine")
	audio.free()
	vfx.free()
	_teardown()


func _hit(tid: StringName, amount: int) -> Dictionary:
	return {"target_id": tid, "hit": true, "amount": amount, "statuses_added": []}


func _result(actor: StringName, skill: StringName, hits: Array) -> ActionResult:
	var r := ActionResult.new()
	r.actor_id = actor
	r.skill_id = skill
	for h: Dictionary in hits:
		r.hits.append(h)
	return r


func _host() -> Node:
	return (Engine.get_main_loop() as SceneTree).current_scene
