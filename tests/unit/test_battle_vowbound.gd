extends TestCase
## M2-CMB-04: Vowbound summons (SPEC §6.3; battle_ctb.md § Vowbound, formulas.md § Vowbound). A called
## Vowbound replaces the whole active party, takes the caller's turn (which ends there, ADR 0027
## A3), fights with its own HP, MP, skills and Swell, and gives the field back when dismissed, when
## it falls, or at victory.

const REEF := &"sandbox_reef"
const ILUN := &"ilun"

var engine: BattleEngine
## Held for the test: a signal connection does not keep it alive.
var swell: BattleSwell
var events: Array[String] = []


func before_each() -> void:
	engine = _engine(3, [ILUN] as Array[StringName])
	swell = BattleSwell.new(BattleSwell.load_config())
	swell.attach(engine)
	events.clear()
	engine.vowbound.called.connect(func(v: BattleCombatant) -> void: events.append("called:%s" % v.id))
	engine.vowbound.departed.connect(
		func(v: BattleCombatant, fell: bool) -> void: events.append("departed:%s:%s" % [v.id, fell])
	)
	engine.begin()
	_turn_of(engine, &"asha")


static func _engine(rng_seed: int, bound: Array[StringName]) -> BattleEngine:
	var e := BattleEngine.new()
	e.setup(
		BattleDB.load_default(), [&"rhen", &"asha"] as Array[StringName], [&"toma"] as Array[StringName], REEF, rng_seed
	)
	e.vowbound = BattleVowbound.new(BattleVowbound.load_config(), bound)
	return e


func test_ilun_is_built_from_ashas_stats_at_her_level() -> void:
	var asha := engine.find(&"asha")
	assert_true(engine.summon(ILUN))
	var ilun := engine.vowbound.summon
	assert_eq(ilun.id, ILUN)
	assert_eq(ilun.team, BattleCombatant.TEAM_PARTY)
	assert_eq(ilun.level, asha.level)
	var want := {
		"max_hp": 240,
		"max_mp": 40,
		"strength": 7,
		"magic": 22,
		"defense": 20,
		"magic_defense": 28,
		"agility": 11,
		"accuracy": 12,
		"evasion": 7,
		"luck": 16
	}
	for field: String in want:
		assert_eq(int(ilun.get(field)), int(want[field]), "formulas.md § Vowbound: %s" % field)
	assert_eq(ilun.hp, ilun.max_hp, "full HP")
	assert_eq(ilun.mp, ilun.max_mp, "full MP")
	assert_eq(ilun.affinity_for(&"water"), &"absorb")
	assert_eq(ilun.skills, [&"attack", &"brine_lash", &"tidal_ward"] as Array[StringName])


func test_the_call_replaces_the_party_and_hands_ilun_the_turn() -> void:
	var rhen := engine.find(&"rhen")
	var asha := engine.find(&"asha")
	var now := engine.now
	var started: Array[StringName] = []
	engine.turn_started.connect(func(c: BattleCombatant) -> void: started.append(c.id))
	assert_true(engine.summon(ILUN))
	var ilun := engine.vowbound.summon
	assert_eq(engine.party_active, [ilun] as Array[BattleCombatant], "the whole party stands down")
	assert_eq(engine.vowbound.stood_down, [rhen, asha] as Array[BattleCombatant])
	assert_eq(engine.current, ilun, "Ilun takes Asha's turn")
	assert_eq(engine.now, now, "no time passes")
	assert_eq(started, [ILUN] as Array[StringName])
	assert_eq(events, ["called:ilun"] as Array[String])
	assert_true(engine.is_party_turn())
	for entry in engine.preview():
		assert_false(entry.combatant_id in [&"rhen", &"asha"], "the stood-down party leaves the timeline")
	assert_eq(engine.find(&"rhen"), rhen, "find() still reaches the stood-down party")


func test_refusals_cost_nothing() -> void:
	var asha := engine.find(&"asha")
	assert_eq(engine.vowbound.refusal(engine, &"nobody"), BattleVowbound.FAIL_UNKNOWN)
	asha.add_status(&"silence", 2)
	assert_eq(engine.vowbound.refusal(engine, ILUN), BattleVowbound.FAIL_SILENCED, "the call is a verse")
	assert_false(engine.summon(ILUN))
	asha.statuses.erase(&"silence")
	assert_eq(engine.vowbound.callable_ids(engine), [ILUN] as Array[StringName])
	var unbound := _engine(3, [] as Array[StringName])
	unbound.begin()
	_turn_of(unbound, &"asha")
	assert_eq(unbound.vowbound.refusal(unbound, ILUN), BattleVowbound.FAIL_NOT_BOUND)
	assert_true(unbound.vowbound.callable_ids(unbound).is_empty())
	_turn_of(unbound, &"rhen")
	assert_eq(unbound.vowbound.refusal(unbound, ILUN), BattleVowbound.FAIL_NOT_BOUND)
	_turn_of(engine, &"rhen")
	assert_eq(engine.vowbound.refusal(engine, ILUN), BattleVowbound.FAIL_NOT_CALLER, "only Asha calls Ilun")
	assert_false(engine.summon(ILUN))
	assert_eq(engine.party_active.size(), 2, "nothing changed")
	assert_false(engine.vowbound.is_out())


func test_an_unreadable_config_has_no_vowbound() -> void:
	var cfg := BattleVowbound.load_config("res://tests/unit/no_such_vowbound.json")
	assert_eq(cfg, [], "a missing file reads as no rows (and logs an error)")
	var none := BattleVowbound.new(cfg, [ILUN] as Array[StringName])
	assert_true(none.rows.is_empty())
	assert_eq(none.refusal(engine, ILUN), BattleVowbound.FAIL_UNKNOWN)


func test_no_call_on_a_foes_turn_or_after_the_battle() -> void:
	engine.perform(&"attack", [engine.enemies[1]] as Array[BattleCombatant])
	while engine.is_party_turn():
		engine.perform(&"attack", [engine.enemies[1]] as Array[BattleCombatant])
	assert_eq(engine.vowbound.refusal(engine, ILUN), BattleVowbound.FAIL_NOT_YOUR_TURN)
	for e in engine.enemies:
		e.hp = 0
	engine.run_enemy_turn()
	assert_ne(engine.outcome, &"")
	assert_eq(engine.vowbound.refusal(engine, ILUN), BattleVowbound.FAIL_BATTLE_OVER)
	assert_eq(engine.vowbound.dismiss_refusal(engine), BattleVowbound.FAIL_BATTLE_OVER)
	assert_false(engine.summon(ILUN))


func test_foes_can_only_reach_the_vowbound() -> void:
	var rhen := engine.find(&"rhen")
	var asha := engine.find(&"asha")
	var hp := [rhen.hp, asha.hp]
	assert_true(engine.summon(ILUN))
	var ilun := engine.vowbound.summon
	engine.perform(&"tidal_ward", [ilun] as Array[BattleCombatant])
	var guard := 0
	while engine.outcome == &"" and engine.vowbound.is_out() and guard < 12:
		guard += 1
		if engine.is_party_turn():
			engine.perform(&"attack", [engine.living_foes_of(ilun)[0]] as Array[BattleCombatant])
		else:
			engine.run_enemy_turn()
	assert_eq([rhen.hp, asha.hp], hp, "the stood-down party is out of reach")
	assert_true(ilun.hp < ilun.max_hp, "Ilun takes the hits")


func test_a_dismissal_brings_the_party_back_where_it_left_off() -> void:
	var rhen := engine.find(&"rhen")
	var asha := engine.find(&"asha")
	var rhen_wait := rhen.next_time - engine.now
	var call_wait := Formulas.action_delay(asha.agility, Formulas.DEFAULT_RANK, asha.speed_mult())
	assert_true(engine.summon(ILUN))
	var ilun := engine.vowbound.summon
	ilun.max_hp = 5000  # this test is about the dismissal, not whether he outlasts the round
	ilun.hp = ilun.max_hp
	engine.perform(&"brine_lash", [engine.enemies[1]] as Array[BattleCombatant])
	_turn_of(engine, ILUN)
	assert_eq(engine.vowbound.dismiss_refusal(engine), &"")
	var at := engine.now
	assert_true(engine.dismiss())
	assert_eq(engine.party_active, [rhen, asha] as Array[BattleCombatant])
	assert_eq(asha.next_time, at + call_wait, "the call was Asha's action: she pays its rank (3)")
	assert_eq(rhen.next_time, at + rhen_wait, "Rhen keeps the ticks he had left")
	assert_ne(engine.current, ilun, "the dismissal spent Ilun's turn")
	assert_eq(events, ["called:ilun", "departed:ilun:false"] as Array[String])
	assert_eq(engine.vowbound.dismiss_refusal(engine), BattleVowbound.FAIL_NONE_OUT)
	assert_false(engine.dismiss())
	# Called again, he comes back as he left.
	var hp := ilun.hp
	var mp := ilun.mp
	_turn_of(engine, &"asha")
	assert_true(engine.summon(ILUN))
	assert_eq(engine.vowbound.summon, ilun)
	assert_eq([ilun.hp, ilun.mp], [hp, mp])


func test_only_the_vowbound_dismisses_itself() -> void:
	assert_eq(engine.vowbound.dismiss_refusal(engine), BattleVowbound.FAIL_NONE_OUT)
	assert_true(engine.summon(ILUN))
	var ilun := engine.vowbound.summon
	ilun.add_status(&"berserk", 3)
	assert_eq(engine.current, ilun)
	assert_eq(engine.vowbound.dismiss_refusal(engine), BattleVowbound.FAIL_NOT_YOUR_TURN, "not while berserk")
	ilun.statuses.erase(&"berserk")
	engine.perform(&"attack", [engine.enemies[1]] as Array[BattleCombatant])
	assert_ne(engine.current, ilun)
	assert_eq(engine.vowbound.dismiss_refusal(engine), BattleVowbound.FAIL_NOT_YOUR_TURN, "a foe's turn")
	assert_false(engine.dismiss())
	assert_true(engine.vowbound.is_out())


func test_a_fallen_vowbound_is_no_defeat() -> void:
	var asha := engine.find(&"asha")
	assert_true(engine.summon(ILUN))
	var ilun := engine.vowbound.summon
	ilun.hp = 1
	ilun.evasion = 0
	engine.perform(&"attack", [engine.enemies[1]] as Array[BattleCombatant])
	var guard := 0
	while engine.vowbound.is_out() and engine.outcome == &"" and guard < 30:
		guard += 1
		if engine.is_party_turn():
			engine.perform(&"attack", [engine.living_foes_of(ilun)[0]] as Array[BattleCombatant])
		else:
			engine.run_enemy_turn()
	assert_false(ilun.is_alive(), "a foe struck him down")
	assert_eq(engine.outcome, &"", "the battle goes on")
	assert_true(engine.party_active.has(asha), "the party is back")
	assert_eq(events, ["called:ilun", "departed:ilun:true"] as Array[String])
	_turn_of(engine, &"asha")
	assert_eq(engine.vowbound.refusal(engine, ILUN), BattleVowbound.FAIL_FALLEN, "not again this battle")


func test_no_swap_escape_or_item_while_the_vowbound_fights() -> void:
	assert_true(engine.summon(ILUN))
	var ilun := engine.vowbound.summon
	assert_false(engine.swap(ILUN, &"toma"), "the Vowbound cannot be swapped out")
	assert_true(engine.preview_swap(ILUN, &"toma").is_empty())
	assert_eq(engine.vowbound.refusal(engine, ILUN), BattleVowbound.FAIL_OUT)
	assert_false(engine.escape(), "no escape: it costs nothing")
	assert_eq(engine.current, ilun)
	var items_db := ItemDB.load_default()
	var inv := Inventory.new(items_db, {})
	inv.add(&"salt_tonic", 1)
	var bag := InventoryItemSource.new(items_db, inv)
	var res := engine.use_item(&"salt_tonic", [ilun] as Array[BattleCombatant], bag)
	assert_false(res.ok)
	assert_eq(res.fail_reason, BattleVowbound.FAIL_OUT, "a Vowbound uses no items")
	assert_eq(bag.count(&"salt_tonic"), 1)
	assert_false(engine.item_defeats_party(&"salt_tonic", [ilun] as Array[BattleCombatant], bag))


func test_the_vowbound_fills_its_own_gauge_and_unleashes_floodnet() -> void:
	var rhen := engine.find(&"rhen")
	var asha := engine.find(&"asha")
	var party_swell := [rhen.swell, asha.swell]
	assert_true(engine.summon(ILUN))
	var ilun := engine.vowbound.summon
	assert_eq(engine.vowbound.finisher(ilun), &"floodnet")
	var early := engine.vowbound.unleash(engine, engine.living_foes_of(ilun))
	assert_false(early.ok)
	assert_eq(early.fail_reason, BattleVowbound.FAIL_NOT_FULL)
	var hit := ActionResult.new()
	hit.actor_id = engine.enemies[0].id
	hit.hits.append({"target_id": ILUN, "amount": 380})
	engine.action_resolved.emit(hit)
	assert_eq(ilun.swell, Formulas.swell_gain(380, ilun.max_hp, _rate()), "his own HP share at his row's rate")
	assert_eq([rhen.swell, asha.swell], party_swell, "party gauges never see his hits")
	assert_eq(engine.perform(&"floodnet", engine.living_foes_of(ilun)).fail_reason, &"unknown_skill")
	ilun.swell = Formulas.SWELL_MAX
	var mp := ilun.mp
	var res := engine.vowbound.unleash(engine, engine.living_foes_of(ilun))
	assert_true(res.ok, str(res.fail_reason))
	assert_eq(res.skill_id, &"floodnet")
	assert_eq(res.hits.size(), 3, "all foes")
	assert_eq(ilun.swell, 0, "the gauge is spent")
	assert_eq(ilun.mp, mp, "no MP")
	assert_ne(engine.current, ilun, "the turn ended")
	assert_false(ilun.skills.has(&"floodnet"), "the finisher is not a learned skill")


## ADR 0027 A1: HP an absorb hit restores fills the gauge like HP lost; a heal does not.
func test_an_absorb_fills_the_gauge_and_a_heal_does_not() -> void:
	assert_true(engine.summon(ILUN))
	var ilun := engine.vowbound.summon
	ilun.hp = ilun.max_hp / 2
	var drink := ActionResult.new()
	drink.actor_id = engine.enemies[0].id
	drink.skill_id = &"brine_lash"  # water, which Ilun absorbs
	drink.hits.append({"target_id": ILUN, "amount": -120})
	engine.action_resolved.emit(drink)
	assert_eq(ilun.swell, Formulas.swell_gain(120, ilun.max_hp, _rate()), "he drinks the tide into the net")
	var before := ilun.swell
	var mend := ActionResult.new()
	mend.actor_id = ILUN
	mend.skill_id = &"mend"
	mend.hits.append({"target_id": ILUN, "amount": -120})
	engine.action_resolved.emit(mend)
	assert_eq(ilun.swell, before, "a heal is not an absorb")
	var tonic := ActionResult.new()
	tonic.actor_id = ILUN
	tonic.item_id = &"salt_tonic"
	tonic.hits.append({"target_id": ILUN, "amount": -120})
	engine.action_resolved.emit(tonic)
	assert_eq(ilun.swell, before, "nor is an item")


## ADR 0027 A3: the call is the caller's action, so its end of turn runs at the call: Poison ticks
## once, Doom counts down once, turns_taken and turn_ended. Only its next turn waits for the return.
func test_the_call_runs_the_callers_end_of_turn_once() -> void:
	var asha := engine.find(&"asha")
	asha.add_status(&"poison", 5)
	asha.add_status(&"doom", 4)
	var hp := asha.hp
	var doom := asha.doom_count()
	var taken := asha.turns_taken
	var ended: Array[StringName] = []
	engine.turn_ended.connect(func(c: BattleCombatant, _ch: Array[Dictionary]) -> void: ended.append(c.id))
	assert_true(engine.summon(ILUN))
	assert_eq(asha.hp, hp - Formulas.poison_damage(asha.max_hp), "Poison ticks once")
	assert_eq(asha.doom_count(), doom - 1, "Doom counts down once")
	assert_eq(asha.turns_taken, taken + 1)
	assert_eq(ended, [&"asha"] as Array[StringName], "her turn ended at the call")
	assert_eq(engine.current, engine.vowbound.summon, "Ilun has the turn")
	assert_true(engine.dismiss())
	assert_eq(asha.doom_count(), doom - 1, "the return does not tick her again")


## ADR 0027 A2: Floodnet is non-elemental and clears the flood, through the same path as the old
## call_ilun stand-in (skills.json clears_field).
func test_floodnet_clears_an_active_flood() -> void:
	var e := BattleEngine.new()
	e.setup(
		BattleDB.load_default(),
		[&"rhen", &"asha", &"toma"] as Array[StringName],
		[] as Array[StringName],
		&"drownbell",
		3
	)
	e.vowbound = BattleVowbound.new(BattleVowbound.load_config(), [ILUN] as Array[StringName])
	e.begin()
	var bell := e.enemies[0]
	bell.hp = bell.max_hp * 40 / 100
	BossMechanics.check_phases(e)
	assert_true(e.fields.has(&"flood"), "the flood is up")
	_turn_of(e, &"asha")
	assert_true(e.summon(ILUN))
	var ilun := e.vowbound.summon
	ilun.swell = Formulas.SWELL_MAX
	var row := e.db.skill(&"floodnet")
	assert_eq(str(row.get("element", "")), "none", "the net binds; it is not a wave")
	var res := e.vowbound.unleash(e, e.living_foes_of(ilun))
	assert_true(res.ok, str(res.fail_reason))
	assert_false(e.fields.has(&"flood"), "Floodnet clears the flood")
	for c in e.enemies.slice(1):
		assert_false(c.is_alive(), "%s fell with the field" % c.id)


## M2-FP-17: with Ilun alone on the field the flood only feeds him, so the bell answers him with
## Hood Slam (enemies.json foes_all_absorb), and the slam's damage fills his gauge toward Floodnet.
func test_the_bell_answers_a_lone_ilun_in_the_flood() -> void:
	var e := BattleEngine.new()
	e.setup(
		BattleDB.load_default(),
		[&"rhen", &"asha", &"toma"] as Array[StringName],
		[] as Array[StringName],
		&"drownbell",
		5
	)
	e.vowbound = BattleVowbound.new(BattleVowbound.load_config(), [ILUN] as Array[StringName])
	e.begin()
	var bell := e.enemies[0]
	bell.hp = bell.max_hp * 40 / 100
	BossMechanics.check_phases(e)
	var with_party := EnemyAI.choose(e, bell)
	assert_ne(StringName(str(with_party.get("skill", ""))), &"hood_slam", "while the party stands, the flood surges")
	_turn_of(e, &"asha")
	assert_true(e.summon(ILUN))
	var alone := EnemyAI.choose(e, bell)
	assert_eq(StringName(str(alone.get("skill", ""))), &"hood_slam", "a lone absorber gets the hood")


func test_the_story_flag_binds_ilun() -> void:
	var cfg := BattleVowbound.load_config()
	assert_eq(BattleVowbound.bound_by(cfg, [&"ch03_ilun_bound"] as Array[StringName]), [ILUN] as Array[StringName])
	assert_eq(BattleVowbound.bound_by(cfg, [] as Array[StringName]), [] as Array[StringName])


func test_victory_gives_the_field_back_to_the_party_first() -> void:
	var rhen := engine.find(&"rhen")
	var asha := engine.find(&"asha")
	assert_true(engine.summon(ILUN))
	var ilun := engine.vowbound.summon
	var seen: Array[StringName] = []
	engine.battle_finished.connect(
		func(_o: StringName) -> void:
			for c in engine.party_active:
				seen.append(c.id)
	)
	engine.enemies[0].hp = 0  # the crab drinks the water, so Floodnet can't finish it
	for e in engine.enemies:
		e.hp = mini(e.hp, 1)
	ilun.swell = Formulas.SWELL_MAX
	assert_true(engine.vowbound.unleash(engine, engine.living_foes_of(ilun)).ok)
	assert_eq(engine.outcome, BattleEngine.OUTCOME_VICTORY)
	assert_eq(seen, [rhen.id, asha.id] as Array[StringName], "the party stands on the field when the battle ends")
	assert_false(engine.vowbound.is_out())
	assert_eq(engine.xp_awards().keys(), [&"rhen", &"asha"], "the party earns the XP; the Vowbound none")


func test_provoke_from_a_stood_down_hero_ends_with_the_call() -> void:
	var crab := engine.enemies[0]
	crab.add_status(&"provoke", 3)
	crab.provoker_id = &"asha"
	assert_true(engine.summon(ILUN))
	assert_false(crab.has_status(&"provoke"), "its provoker left the field")


func test_a_seeded_battle_with_a_call_replays_exactly() -> void:
	assert_eq(_play(11), _play(11))


static func _play(rng_seed: int) -> Array:
	var e := _engine(rng_seed, [ILUN] as Array[StringName])
	e.begin()
	var log: Array = []
	var guard := 0
	while e.outcome == &"" and guard < 200:
		guard += 1
		if e.is_party_turn():
			if e.current.id == &"asha" and e.summon(ILUN):
				log.append("call")
				continue
			var foe := e.living_foes_of(e.current)[0]
			log.append([e.current.id, e.perform(&"attack", [foe] as Array[BattleCombatant]).hits])
		else:
			var r := e.run_enemy_turn()
			log.append([r.actor_id, r.hits] if r != null else [])
	log.append(e.outcome)
	return log


## Ilun's gauge rate (vowbound.json swell.rate).
static func _rate() -> int:
	return int(((BattleVowbound.load_config()[0] as Dictionary)["swell"] as Dictionary)["rate"])


static func _turn_of(e: BattleEngine, cid: StringName) -> void:
	var guard := 0
	while e.outcome == &"" and e.current.id != cid and guard < 50:
		guard += 1
		if e.is_party_turn():
			var foes := e.living_foes_of(e.current)
			e.perform(&"attack", [foes[mini(1, foes.size() - 1)]] as Array[BattleCombatant])
		else:
			e.run_enemy_turn()
