extends TestCase
## M3-AUD-800: the battle's sound layers on the real battle presentation (no stand-ins). A sandbox battle is built the
## way tests/unit/test_battle_choreo.gd builds it (the real BattleController, BattleChoreo and the sandbox foes'
## CreatureActor models), and a test AudioDirector attaches what the Audio autoload would attach for it, by the same
## calls its deferred node-added hooks make (AudioDirector.attach_battle on the BattleVfx, ChoreoAudio.attach_to on
## the BattleChoreo, CreatureAudio's model watch). Time moves frame by frame through every listener on one clock.
## Each layer is heard once: Rhen's melee whoosh, then his weapon accent on the contact, with BattleAudio's element
## hit on the same contact and nothing doubled; the whoosh crests on the contact at 1x and 2x; a KO collapses once; a
## creature's action plays its attack and, its model being heard, its movement from the clip once; a hurt layers
## under the hit; a retry leaves one ChoreoAudio and one BattleAudio; the boss card's sting ducks the music and lets
## go. Nothing is really played: the director's bank is a _HeardBank (SfxBank's rules, its history, no playback) and
## the battle has no music cue, so no playback outlives the test in the AudioServer.

const SANDBOX := "res://game/battle/scene/battle_sandbox.tscn"
const SEED := 20261022
const DT := 1.0 / 60.0
const MAX_SEC := 12.0
const EPS := 0.04
const RHEN := &"rhen"
const RHEN_ACCENT := &"accent_hooks"
const MELEE_WHOOSH := &"whoosh_melee"
const KO_ROW := &"ko_collapse"
const SANDBOX_CREATURES: Array[String] = ["reef_crab", "lantern_eel", "gull_harrier"]
const BOSS_ENCOUNTER := &"drownbell"
const LATER_ACTIONS := 3

var ctl: BattleController
var choreo: BattleChoreo
var dir: AudioDirector
var battle: BattleAudio
var listener: ChoreoAudio
var creatures: CreatureAudio
var settings: UiSettings
var prev_settings: UiSettings
var now_ms := 1000
## [row, listener clock] for every ChoreoAudio play.
var heard: Array = []
## [row, msec] for every play the bank made.
var bank_log: Array = []
var _game_audio: AudioDirector


func before_each() -> void:
	now_ms = 1000
	heard = []
	prev_settings = UiSettings.shared()
	settings = UiSettings.new()
	UiSettings.set_shared(settings)
	_mute_game_audio(true)
	dir = AudioDirector.new()
	_host().add_child(dir)
	dir.set_process(false)
	dir.sfx.free()
	dir.sfx = _HeardBank.new()
	dir.sfx.name = "Sfx"
	dir.add_child(dir.sfx)
	dir.setup(AudioData.table(AudioData.MIX), {}, {"sfx": AudioData.sfx_rows()})  # no music: nothing streams
	dir.sfx.clock = func() -> int: return now_ms
	bank_log = []
	dir.sfx.played.connect(func(id: StringName, _file: String) -> void: bank_log.append([id, now_ms]))
	var packed := load(SANDBOX) as PackedScene
	ctl = packed.instantiate() as BattleController
	ctl.auto_start = false
	ctl.pacing_scale = 0.0
	ctl.persist_progress = false
	_host().add_child(ctl)
	_start(SEED)


## Starts (or retries) the sandbox battle and attaches the listeners the director's hooks would.
func _start(rng_seed: int) -> void:
	var active: Array[StringName] = [RHEN, &"asha"]
	var reserve: Array[StringName] = [&"toma", &"ysolde"]
	var p := LatticeProgress.new(LatticeBoard.load_board(), LatticeRules.load_file())
	for cid: StringName in [RHEN, &"asha", &"toma", &"ysolde"]:
		p.add_character(cid)
	ctl.start_battle(active, reserve, &"sandbox_reef", rng_seed, p)
	choreo = ctl.stage.choreo
	choreo.live = false
	choreo.reduced_motion = false
	choreo.skip = false
	choreo.speed = 1.0
	dir.attach_battle(ctl.stage.get_node(^"BattleVfx"))
	battle = dir.listeners[ctl.stage.get_node(^"BattleVfx")] as BattleAudio
	creatures = battle.creatures
	creatures.set_process(false)
	# CreatureAudio's own deferred watch, for every node in the tree under the controller (its scope).
	for n: Node in ctl.find_children("*", "", true, false):
		if creatures.model_base(n) != "":
			creatures._watch_later(n.get_instance_id())
	listener = ChoreoAudio.attach_to(choreo, dir)
	listener.set_process(false)
	listener.player = func(id: StringName, opts: Dictionary) -> void:
		heard.append([id, listener._clock])
		dir.play_sfx(id, opts)


func _teardown() -> void:
	dir.stop_all_players()  # none plays (_HeardBank, no music); kept so a change to that cannot leak a playback
	ctl.free()
	dir.free()
	UiSettings.set_shared(prev_settings)
	_mute_game_audio(false)


## The game's own Audio autoload hears EventBus too and is never advanced here: keep it off the stings meanwhile.
func _mute_game_audio(on: bool) -> void:
	_game_audio = (Engine.get_main_loop() as SceneTree).root.get_node_or_null(^"Audio") as AudioDirector
	var bus := (Engine.get_main_loop() as SceneTree).root.get_node_or_null(^"EventBus")
	if _game_audio == null or bus == null:
		return
	var cb := _game_audio.stings.on_event
	if on and bus.is_connected(&"dialogue_event", cb):
		bus.disconnect(&"dialogue_event", cb)
	elif not on and not bus.is_connected(&"dialogue_event", cb):
		bus.connect(&"dialogue_event", cb)


## One frame for everything: the choreography, the listeners, the SFX bank's clock and the controller's hand-off.
func _frame() -> void:
	now_ms += int(round(DT * 1000.0))
	choreo.advance(DT)
	listener.advance(DT)
	creatures.flush(now_ms)
	dir.stings.advance(DT)
	ctl.tick(DT)


## Frames until the current sequence (and anything it queued) has played.
func _play_out() -> void:
	var t := 0.0
	while (choreo.playing() or not listener._queue.is_empty()) and t < MAX_SEC:
		_frame()
		t += DT
	for i in 30:  # the hurt / death delays and the settle
		_frame()


func _to_turn_of(cid: StringName) -> void:
	var guard := 0
	while ctl.current_actor_id() != cid and guard < 16:
		guard += 1
		ctl.act(&"attack", [ctl.engine.living_foes_of(ctl.engine.current)[0].id])


func _foe() -> BattleCombatant:
	for e in ctl.engine.enemies:
		if e.is_alive():
			return e
	return null


func _ids() -> Array[StringName]:
	var out: Array[StringName] = []
	for e: Array in heard:
		out.append(e[0] as StringName)
	return out


func _count(list: Array, id: Variant) -> int:
	var n := 0
	for v: Variant in list:
		n += 1 if v == id else 0
	return n


func _history_count(id: StringName) -> int:
	var n := 0
	for h: Array in dir.sfx.history:
		n += 1 if StringName(str(h[0])) == id else 0
	return n


func _ms_of(id: StringName) -> int:
	for e: Array in bank_log:
		if e[0] == id:
			return int(e[1])
	return -1


func _clock_of(id: StringName) -> float:
	for e: Array in heard:
		if e[0] == id:
			return float(e[1])
	return -1.0


# --- the hooks find the real classes ---------------------------------------------------------


func test_the_real_choreography_and_models_are_heard() -> void:
	assert_true(ChoreoAudio.wants(choreo), "BattleChoreo matches choreo_sfx.json's hook by its class name")
	assert_false(ChoreoAudio.hook_for(listener.data, choreo).has("pending"), "the hook is live")
	assert_eq(listener.node, choreo)
	assert_true(listener.engine == ctl.engine, "the controller's engine, found from the choreography's ancestors")
	for sig: StringName in [&"beat", &"contact"]:
		var mine := 0
		for conn: Dictionary in choreo.get_signal_connection_list(sig):
			mine += 1 if (conn["callable"] as Callable).get_object() == listener else 0
		assert_eq(mine, 1, "BattleChoreo.%s is heard once" % sig)
	for m: StringName in [&"current", &"style_id_for", &"entering", &"leaving", &"animating", &"after_sequence"]:
		assert_true(choreo.has_method(m), "BattleChoreo.%s" % m)
	assert_true(typeof(choreo.get(&"speed")) == TYPE_FLOAT, "BattleChoreo.speed")
	var styles := (BattleChoreo.load_data()["styles"] as Dictionary).keys()
	for sid: String in listener.data["styles"] as Dictionary:
		if bool(((listener.data["styles"] as Dictionary)[sid] as Dictionary).get("pending", false)):
			continue  # a row made ahead of battle-presentation's style (M3-BPR-410's charge)
		assert_true(styles.has(sid), "choreo_sfx style %s is a choreo.json style" % sid)
	for sid: String in styles:
		assert_true((listener.data["styles"] as Dictionary).has(sid), "choreo.json style %s has a sound row" % sid)
	for base in SANDBOX_CREATURES:
		assert_eq(int(creatures.models.get(base, 0)), 1, "%s's CreatureActor is heard, under the controller" % base)
	_teardown()


# --- a melee action: whoosh, contact accent, the element hit, once each ------------------------


func test_a_melee_attack_whooshes_then_lands_its_accent_once() -> void:
	_to_turn_of(RHEN)
	ctl.pacing_scale = 1.0
	var foe := _foe()
	foe.hp = foe.max_hp
	heard.clear()
	battle.played.clear()
	dir.sfx.history.clear()
	ctl.act(&"attack", [foe.id])
	var plan := choreo.current()
	assert_eq(str(plan.get("style", "")), "melee")
	assert_eq(_ids().size() > 0, true, "the approach's footfalls start at once")
	assert_false(_ids().has(RHEN_ACCENT), "nothing touches before the blow")
	_play_out()
	var ids := _ids()
	assert_eq(_count(ids, MELEE_WHOOSH), 1, "one whoosh")
	assert_eq(_count(ids, RHEN_ACCENT), 1, "one accent: the contact is not doubled")
	assert_true(ids.find(MELEE_WHOOSH) < ids.find(RHEN_ACCENT), "the whoosh, then the accent")
	assert_eq(_history_count(RHEN_ACCENT), 1, "the bank played the accent once")
	assert_false(battle.played.has(RHEN_ACCENT), "BattleAudio never plays the accent")
	assert_true(battle.played.size() > 0, "BattleAudio's element hit lands on the same contact")
	for id: StringName in battle.played:
		assert_eq(_count(battle.played, id), 1, "%s once" % id)
	assert_eq(_count(ids, KO_ROW), 0, "a foe left standing does not collapse")
	_teardown()


func test_the_whoosh_crests_on_the_contact_at_1x_and_2x() -> void:
	for speed: float in [1.0, 2.0]:
		if speed != 1.0:
			_start(SEED)  # the same opening, at the other speed
		_to_turn_of(RHEN)
		ctl.pacing_scale = 1.0
		choreo.speed = speed
		var foe := _foe()
		foe.hp = foe.max_hp
		heard.clear()
		var start := listener._clock
		assert_true(ctl.act(&"attack", [foe.id]).ok, "Rhen attacks at %sx" % speed)
		var contact := start + float(choreo.current()["contact"]) / speed  # the contact beat, in real seconds
		_play_out()
		var peak := float((listener.data["peaks"] as Dictionary)[String(MELEE_WHOOSH)])
		assert_true(_clock_of(MELEE_WHOOSH) > start, "the whoosh played at %sx" % speed)
		var crest := _clock_of(MELEE_WHOOSH) + peak
		assert_between(crest, contact - EPS, contact + EPS, "the crest lands on the contact at %sx" % speed)
		assert_between(_clock_of(RHEN_ACCENT), contact - EPS, contact + EPS, "the accent on it at %sx" % speed)
		ctl.pacing_scale = 0.0
	_teardown()


# --- a KO -----------------------------------------------------------------------------------


func test_a_ko_collapses_once() -> void:
	_to_turn_of(RHEN)
	ctl.pacing_scale = 1.0
	var foe := _foe()
	foe.hp = 1
	heard.clear()
	creatures.played.clear()
	ctl.act(&"attack", [foe.id])
	assert_eq(choreo.current()["kos"], [foe.id] as Array[StringName])
	_play_out()
	assert_eq(_count(_ids(), KO_ROW), 1, "one collapse")
	assert_eq(_count(_ids(), RHEN_ACCENT), 1, "and one accent")
	var base := BattleVfx.base_id(foe.id)
	assert_eq(creatures.played.count("%s:death" % base), 1, "its death cry once, under the KO")
	assert_eq(creatures.played.count("%s:hurt" % base), 0, "no hurt for a felling blow")
	_teardown()


## M3-AUD-803 (with battle-presentation's M2-BPR-11): a KO is heard once. The stage re-applies every fighter's KO
## state after every action, and later actions must never replay the fallen foe's collapse, death cry or release.
func test_a_ko_is_heard_once_through_later_actions() -> void:
	_to_turn_of(RHEN)
	ctl.pacing_scale = 1.0
	var foe := _foe()
	foe.hp = 1
	heard.clear()
	creatures.played.clear()
	battle.played.clear()
	ctl.act(&"attack", [foe.id])
	_play_out()
	var base := BattleVfx.base_id(foe.id)
	var release := _count(battle.played, &"ko_release")
	assert_eq(_count(_ids(), KO_ROW), 1, "one collapse")
	assert_eq(creatures.played.count("%s:death" % base), 1, "one death cry")
	assert_true(release <= 1, "at most one glimmer release")
	for e in ctl.engine.enemies:
		if e.is_alive():
			e.hp = e.max_hp  # the battle goes on through the later actions
	for i in LATER_ACTIONS:
		ctl.stage.refresh_ko(ctl.engine)
		_to_turn_of(RHEN)
		var living := ctl.engine.living_foes_of(ctl.engine.current)
		if living.is_empty():
			break
		ctl.act(&"attack", [living[0].id])
		_play_out()
	assert_eq(_count(_ids(), KO_ROW), 1, "later actions never replay the collapse")
	assert_eq(creatures.played.count("%s:death" % base), 1, "nor the death cry")
	assert_eq(_count(battle.played, &"ko_release"), release, "nor the release")
	_teardown()


# --- a creature's action and a hurt ------------------------------------------------------------


func test_a_hero_blow_hurts_a_creature_once() -> void:
	_to_turn_of(RHEN)
	ctl.pacing_scale = 1.0
	var foe := _foe()
	foe.hp = foe.max_hp
	creatures.played.clear()
	battle.played.clear()
	assert_true(creatures.contact_source == choreo, "hurts and deaths are timed on the choreography's contact")
	ctl.act(&"attack", [foe.id])
	_play_out()
	var base := BattleVfx.base_id(foe.id)
	assert_eq(creatures.played.count("%s:hurt" % base), 1, "one hurt, layered under the hit")
	var hurt_ms := _ms_of(creatures.sfx_for(base, CreatureAudio.HURT))
	var hit_ms := _ms_of(battle.played[0]) if not battle.played.is_empty() else -1
	var delay := int((creatures.data["delays_ms"] as Dictionary)["hurt"])
	assert_true(hit_ms > 0, "the element hit played")
	assert_between(hurt_ms - hit_ms, delay - 20, delay + 20, "the hurt follows the hit by its delay, not the action")
	_teardown()


func test_a_creature_attacks_and_moves_once_from_its_clip() -> void:
	_to_turn_of(RHEN)
	ctl.pacing_scale = 1.0
	for e in ctl.engine.enemies + ctl.engine.party_active:
		e.hp = e.max_hp
	ctl.act(&"attack", [_foe().id])
	creatures.played.clear()
	# Frames until a creature's own choreography has played out.
	var t := 0.0
	var actor := &""
	while t < MAX_SEC * 3.0:
		_frame()
		t += DT
		if choreo.playing():
			var a := StringName(str(choreo.current().get("actor", "")))
			var c := ctl.engine.find(a)
			if c != null and c.team != BattleCombatant.TEAM_PARTY:
				actor = a
				break
	assert_true(actor != &"", "a creature took its turn")
	var base := BattleVfx.base_id(actor)
	var model := BattleClips.creature_of(ctl.stage.stand_in(actor))
	assert_true(model != null, "%s is a CreatureActor model" % base)
	assert_true(int(creatures.models.get(base, 0)) > 0, "its model is heard")
	creatures.flush(now_ms)
	assert_eq(creatures.played.count("%s:attack" % base), 1, "its attack voice as the action starts")
	assert_eq(creatures.played.count("%s:move" % base), 0, "no movement with the attack while its model is heard")
	var clips: Array[StringName] = []
	var player := BattleClips.player_of(ctl.stage.stand_in(actor))
	player.animation_started.connect(func(clip: StringName) -> void: clips.append(clip))
	_play_out()
	var mapped := creatures.data.get("clips", {}) as Dictionary
	var moving := 0
	for clip in clips:
		moving += 1 if mapped.has(String(clip)) else 0
	assert_eq(moving, 1, "the model played one action clip (%s)" % [clips])
	assert_eq(creatures.played.count("%s:attack" % base), 1, "its attack voice once")
	assert_eq(creatures.played.count("%s:move" % base), 1, "its movement once, from that clip")
	_teardown()


# --- a retry ----------------------------------------------------------------------------------


func test_a_retry_leaves_one_listener_of_each() -> void:
	var old := listener
	var old_battle := battle
	_start(SEED + 1)
	var choreos := 0
	var battles := 0
	for key: Variant in dir.listeners:
		var l: Variant = dir.listeners[key]
		choreos += 1 if l is ChoreoAudio else 0
		battles += 1 if l is BattleAudio else 0
	assert_eq(choreos, 1, "one ChoreoAudio")
	assert_eq(battles, 1, "one BattleAudio")
	assert_true(old.is_queued_for_deletion(), "the old choreography's listener goes")
	assert_true(old_battle.is_queued_for_deletion(), "the old battle's listener goes")
	assert_eq(listener.node, choreo, "the new one hears the new choreography")
	assert_true(listener.engine == ctl.engine, "on the new engine")
	_to_turn_of(RHEN)
	ctl.pacing_scale = 1.0
	var foe := _foe()
	foe.hp = foe.max_hp
	heard.clear()
	ctl.act(&"attack", [foe.id])
	_play_out()
	assert_eq(_count(_ids(), RHEN_ACCENT), 1, "one accent after the retry")
	assert_eq(old.played.count(RHEN_ACCENT), 0, "the old listener heard nothing of it")
	_teardown()


# --- the stings ---------------------------------------------------------------------------------


func test_the_boss_card_sting_ducks_the_music_and_lets_go() -> void:
	var row := (dir.stings.data["events"] as Dictionary)["boss_intro"] as Dictionary
	# BattleBossIntro's announcement (claude/battle-presentation M3-BPR-02): [encounter id, title_key].
	EventBus.dialogue_event.emit(&"boss_intro", [BOSS_ENCOUNTER, "BOSS_TITLE"])
	assert_true(dir.ducks.has(StringName(str(row["duck"]))), "the music ducks as the intro's camera moves")
	assert_eq(dir.stings.played, [] as Array[StringName], "the sting waits for the title card (delay_sec)")
	var t := 0.0
	while t < float(row.get("delay_sec", 0.0)) + 0.05:
		_frame()
		t += DT
	assert_eq(dir.stings.played, [&"sting_boss_bell"] as Array[StringName], "the Drownbell's own sting, once")
	assert_eq(_history_count(&"sting_boss_bell"), 1, "the bank played it")
	while t < float(row["duck_sec"]) + 0.1:
		_frame()
		t += DT
	assert_false(dir.ducks.has(StringName(str(row["duck"]))), "and comes back after duck_sec")
	_teardown()


func test_the_encounter_bark_plays_its_sting_from_the_real_stinger() -> void:
	var c := BattleStinger.load_config().duplicate(true)
	var bark := {"line_key": "HUD_TL_NEXT", "speaker_key": "HUD_TL_NOW", "hold_extra_sec": 0.8}
	(c[BattleStinger.KEY_BARKS] as Dictionary)["rows"] = {"sandbox_reef": bark}
	var s := BattleStinger.make(false, c, &"sandbox_reef")
	_host().add_child(s)
	s.set_process(false)
	# battle-presentation's stinger also announces the tide line (battle_stinger, bcc8e94c): its sting comes first.
	assert_eq(
		dir.stings.played,
		[&"sting_tideline", &"sting_bark"] as Array[StringName],
		"the tide line's sting, then the lead-in line's, once each"
	)
	s.free()
	_teardown()


func _host() -> Node:
	var tree := Engine.get_main_loop() as SceneTree
	return tree.current_scene if tree.current_scene != null else tree.root


## SfxBank's rules (rows, cooldown, file pick, the file must load) and its history, without starting a playback.
class _HeardBank:
	extends SfxBank
	var quiet := AudioStreamPlayer.new()

	func _ready() -> void:
		quiet.name = "Quiet"
		add_child(quiet)

	func _play(id: StringName, _opts: Dictionary, _spatial: bool, _at: Vector3) -> Node:
		var row := rows.get(String(id), {}) as Dictionary
		if row.is_empty():
			return null
		var now := int(clock.call())
		var cooldown := int(row.get("cooldown_ms", 0))
		if cooldown > 0 and _last_ms.has(id) and now - int(_last_ms[id]) < cooldown:
			return null
		var file := _pick(id, row)
		if _stream(file) == null:
			return null
		_last_ms[id] = now
		history.append([id, file])
		played.emit(id, file)
		return quiet
