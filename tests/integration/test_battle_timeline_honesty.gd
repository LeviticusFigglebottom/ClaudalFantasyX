extends TestCase
## M3-CMB-02: the human's Ch1 playtest ("the enemies act more often than the timeline says, and twice on some
## turns"). Pins the three ways that could happen on the live path (FieldBattle + BattleChoreo), and the one it was:
##   - the timeline must match the engine's real order and ticks, foes whose skills are quicker or slower than a
##     standard action included (it predicted every foe at DEFAULT_RANK, so a rank-2 shoal jumped the queue);
##   - one engine action is one choreography playback, for the right actor, in order;
##   - battle_speed changes no actor, order or tick.

const FIELD_SCENE := "res://game/flow/field_battle.tscn"
const SEED := 20261024
const DT := 1.0 / 60.0
## Turns compared against the opening prediction (never more than the timeline shows).
const TURNS := 12
## Live actions played per run.
const ACTIONS := 10
## Frames before a stalled live run fails (each action takes a few seconds of paced choreography).
const MAX_FRAMES := 40000
## Every Ch1 fight and the slice's tideline, each solo Rhen as the chapter plays it (ADR 0034).
const ENCOUNTERS: Array[StringName] = [
	&"ch01_wickfry",
	&"ch01_oil_slug",
	&"ch01_shaft_limpet",
	&"ch01_underway_shoals",
	&"ch01_underway_limpet",
	&"ch01_scuttlers",
	&"ch01_hullgnaw",
	&"ch02_tideline",
]

# --- engine: the prediction is the order played ------------------------------------------------


func test_the_opening_timeline_is_the_order_played_in_every_ch1_fight() -> void:
	for enc in ENCOUNTERS:
		var engine := _engine(enc)
		var predicted := engine.preview()
		var played := _play_engine(engine, TURNS)
		assert_true(played.size() >= 4, "%s: several turns before the first KO or phase change" % enc)
		for i in played.size():
			var e: TurnEntry = predicted[i]
			assert_eq("%s@%d" % [e.combatant_id, e.time], played[i], "%s turn %d: the timeline said it" % [enc, i])


func test_a_foe_quicker_or_slower_than_a_standard_action_shows_its_real_turns() -> void:
	# The Tower Limpet's clamp is rank 4 and pushes Rhen back: predicting it as a standard action (the old rule)
	# put its next turn too early and Rhen's too.
	var engine := _engine(&"ch01_shaft_limpet")
	engine.timeline.tempo = Callable()
	var old := engine.preview()
	engine.timeline.tempo = engine.tempo_rank
	var honest := engine.preview()
	var played := _play_engine(engine, TURNS)
	assert_ne(_ids(old, played.size()), played, "the DEFAULT_RANK prediction was not the order played")
	assert_eq(_ids(honest, played.size()), played, "the AI's rank is")


func test_predicted_rank_follows_the_ai_rules_turn_by_turn() -> void:
	# Hullgnaw's ribs: the Coil (rank 2) on every third own turn, Rib Lash (rank 3) otherwise.
	var engine := _engine(&"ch01_hullgnaw")
	var gnaw := engine.enemies[0]
	var coil := int(engine.db.skill(&"gnaw_coil")["rank"])
	var lash := int(engine.db.skill(&"rib_lash")["rank"])
	assert_ne(coil, lash, "the fixture needs two ranks")
	var ranks: Array[int] = []
	for ahead in 6:
		ranks.append(EnemyAI.predicted_rank(engine, gnaw, ahead))
	assert_eq(ranks, [coil, lash, lash, coil, lash, lash] as Array[int])
	var draws := engine.rng.state
	engine.preview()
	assert_eq(engine.rng.state, draws, "a prediction draws nothing from the battle RNG")
	assert_eq(engine.tempo_rank(engine.party_active[0], 0), {}, "the player's turns stay standard")


# --- live: the HUD and the choreography follow the engine ---------------------------------------


func test_live_one_action_one_playback_and_the_hud_timeline_is_the_engine_order() -> void:
	for enc: StringName in [&"ch01_underway_shoals", &"ch01_shaft_limpet"]:
		var run := _play_live(enc, 1.0)
		var log: Array = run["actions"]
		assert_eq(log.size(), ACTIONS, "%s: played %d actions" % [enc, ACTIONS])
		assert_eq(run["plays"], run["actors"], "%s: each engine action played once, by its actor, in order" % enc)
		assert_eq(int(run["finished"]), log.size(), "%s: every playback finished once" % enc)
		var shown: Array = run["shown"]
		var turns: Array = run["turns"]
		var n := mini(shown.size(), turns.size())
		assert_true(n >= 4, "%s: compared several turns" % enc)
		assert_eq(shown.slice(0, n), turns.slice(0, n), "%s: the HUD's opening order is the order played" % enc)


func test_live_battle_speed_changes_no_actor_order_or_tick() -> void:
	var slow := _play_live(&"ch01_underway_shoals", 0.75)
	var fast := _play_live(&"ch01_underway_shoals", 2.0)
	assert_eq((slow["actions"] as Array).size(), ACTIONS)
	assert_eq(fast["actions"], slow["actions"], "the same actor, skill and engine tick at every speed")


# --- helpers -----------------------------------------------------------------------------------


## A headless engine for `enc` with Rhen alone, begun.
func _engine(enc: StringName) -> BattleEngine:
	var engine := BattleEngine.new()
	var active: Array[StringName] = [&"rhen"]
	var reserve: Array[StringName] = []
	engine.setup(BattleDB.load_default(), active, reserve, enc, SEED)
	engine.begin()
	return engine


## Plays up to `turns` turns (Rhen attacks the first foe; foes run their AI) and returns "id@tick" for
## each turn taken, stopping before the first KO or boss phase change (they rightly reshape the order).
func _play_engine(engine: BattleEngine, turns: int) -> Array[String]:
	var out: Array[String] = []
	var reshaped := [false]
	engine.phase_changed.connect(func(_e: BattleCombatant, _p: StringName) -> void: reshaped[0] = true)
	var alive := _alive(engine)
	while out.size() < turns and engine.outcome == &"" and engine.current != null:
		out.append("%s@%d" % [engine.current.id, engine.now])
		if engine.is_party_turn():
			engine.perform(&"attack", [engine.living_foes_of(engine.current)[0]] as Array[BattleCombatant])
		else:
			engine.run_enemy_turn()
		if reshaped[0] or _alive(engine) != alive:
			break
	return out


func _alive(engine: BattleEngine) -> int:
	return engine.timeline.eligible().size()


func _ids(entries: Array[TurnEntry], n: int) -> Array[String]:
	var out: Array[String] = []
	for i in mini(n, entries.size()):
		out.append("%s@%d" % [entries[i].combatant_id, entries[i].time])
	return out


## Plays `enc` live at battle speed `speed` with readable pacing, ticking the controller and the choreography
## frame by frame. Returns {actions: ["actor skill @tick"], actors, plays: actor ids per resolved action and per
## playback, finished, shown: the HUD timeline's opening ids, turns: the ids that took the turns, until a KO}.
func _play_live(enc: StringName, speed: float) -> Dictionary:
	var ctl := (load(FIELD_SCENE) as PackedScene).instantiate() as FieldBattle
	ctl.auto_start = false
	ctl.persist_progress = false
	var tree := Engine.get_main_loop() as SceneTree
	(tree.current_scene if tree.current_scene != null else tree.root).add_child(ctl)
	var s := UiSettings.new()
	s.set_value(UiSettings.BATTLE_SPEED, speed)
	ctl.hud.apply_settings(s)
	ctl.pacing_scale = 1.0
	var active: Array[StringName] = [&"rhen"]
	var reserve: Array[StringName] = []
	ctl.start_battle(active, reserve, enc, SEED, BattleStage.lattice_for(active, {}))
	var choreo := ctl.stage.choreo
	choreo.live = false
	choreo.skip = false
	var engine := ctl.engine
	var out := {"actions": [], "actors": [], "plays": [], "finished": 0, "shown": [], "turns": []}
	for slot: Dictionary in ctl.hud.timeline.slots:
		(out["shown"] as Array).append(slot["id"])
	var first_ko := [false]
	var alive := _alive(engine)
	(out["turns"] as Array).append(engine.current.id)
	engine.action_resolved.connect(
		func(r: ActionResult) -> void:
			(out["actions"] as Array).append("%s %s @%d" % [r.actor_id, r.skill_id, engine.now])
			(out["actors"] as Array).append(r.actor_id)
	)
	engine.turn_started.connect(
		func(c: BattleCombatant) -> void:
			if _alive(engine) != alive:
				first_ko[0] = true
			if not first_ko[0]:
				(out["turns"] as Array).append(c.id)
	)
	choreo.sequence_finished.connect(func(_a: StringName) -> void: out["finished"] = int(out["finished"]) + 1)
	var before := choreo.played.size()
	var frames := 0
	while engine.outcome == &"" and (out["actions"] as Array).size() < ACTIONS and frames < MAX_FRAMES:
		frames += 1
		if engine.is_party_turn() and ctl.state == BattleController.STATE_COMMAND:
			ctl.act(&"attack", [engine.living_foes_of(engine.current)[0].id] as Array[StringName])
			continue
		choreo.advance(DT)
		ctl.tick(DT)
	while choreo.playing() and frames < MAX_FRAMES:  # let the last playback finish
		frames += 1
		choreo.advance(DT)
	assert_true(frames < MAX_FRAMES, "%s at %.2f: the live battle kept moving" % [enc, speed])
	for i in range(before, choreo.played.size()):
		(out["plays"] as Array).append(StringName(str(choreo.played[i]["actor"])))
	ctl.get_parent().remove_child(ctl)
	ctl.free()
	return out
