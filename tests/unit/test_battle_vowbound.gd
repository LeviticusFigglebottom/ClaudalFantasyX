extends TestCase
## M2-CMB-04: Vowbound summons (SPEC §6.3; battle_ctb.md § Vowbound, formulas.md § Vowbound). A called
## Vowbound replaces the whole active party and takes the caller's turn, which ends at once (ADR 0027
## A3); it fights with its own HP, MP, skills and Swell (absorbed HP fills it, A1), Floodnet clears a
## flood (A2), and it gives the field back when dismissed, when it falls, or at victory (M2-CMB-05).

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
		"max_hp": 360,
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


func test_the_call_replaces_the_party_and_hands_ilun_the_turn_at_once() -> void:
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
	assert_eq(ilun.swell, Formulas.swell_gain(380, ilun.max_hp, 150), "his own HP share at rate 150")
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


func test_absorbed_water_fills_his_gauge_even_at_full_hp_but_a_heal_does_not() -> void:
	assert_true(engine.summon(ILUN))
	var ilun := engine.vowbound.summon
	assert_eq(ilun.hp, ilun.max_hp)
	var drink := ActionResult.new()
	drink.actor_id = engine.enemies[0].id
	drink.hits.append({"target_id": ILUN, "amount": 0, "absorbed": 90, "element": &"water"})
	engine.action_resolved.emit(drink)
	var gain := Formulas.swell_gain(90, ilun.max_hp, 150)
	assert_eq(gain, 37, "formulas.md § Vowbound worked example")
	assert_eq(ilun.swell, gain, "ADR 0027 A1: what he drinks fills the gauge, at full HP too")
	var mend := ActionResult.new()
	mend.actor_id = engine.enemies[0].id
	mend.hits.append({"target_id": ILUN, "amount": -90, "element": &"none"})
	engine.action_resolved.emit(mend)
	assert_eq(ilun.swell, gain, "a heal is not an absorb")


func test_the_crabs_brine_spit_is_drunk_and_fills_his_gauge() -> void:
	assert_true(engine.summon(ILUN))
	var ilun := engine.vowbound.summon
	var seen: Array = []  # [absorbed, HP change, gauge before, gauge after], after BattleVowbound's handler
	var before := [ilun.swell]
	engine.action_resolved.connect(
		func(r: ActionResult) -> void:
			if r.skill_id == &"brine_spit":
				for h in r.hits:
					if h["target_id"] == ILUN and h["hit"]:
						seen.append([int(h.get("absorbed", 0)), int(h["amount"]), before[0], ilun.swell])
			before[0] = ilun.swell
	)
	var guard := 0
	while seen.is_empty() and engine.outcome == &"" and engine.vowbound.is_out() and guard < 60:
		guard += 1
		before[0] = ilun.swell
		if engine.is_party_turn():
			ilun.hp = ilun.max_hp  # full HP: the absorb restores nothing, and still counts
			engine.perform(&"tidal_ward", [ilun] as Array[BattleCombatant])
			ilun.mp = ilun.max_mp
		else:
			engine.run_enemy_turn()
	assert_false(seen.is_empty(), "the crab spat brine at him")
	var absorbed: int = seen[0][0]
	assert_true(absorbed > 0, "he absorbs water")
	assert_true(int(seen[0][1]) <= 0, "it does not hurt him")
	assert_eq(seen[0][3], Formulas.swell_fill(seen[0][2], Formulas.swell_gain(absorbed, ilun.max_hp, 150)))


func test_floodnet_binds_without_water_and_clears_the_flood() -> void:
	assert_eq(str(engine.db.skill(&"floodnet")["element"]), "none", "ADR 0027 A2: the net binds; it is no wave")
	assert_true(engine.summon(ILUN))
	var ilun := engine.vowbound.summon
	var bound := engine.enemies[2]
	bound.max_hp = 9999  # Floodnet's hit must leave it standing for the clear
	bound.hp = bound.max_hp
	bound.field = &"flood"
	engine.fields.append(&"flood")
	var cleared: Array = []
	engine.field_cleared.connect(
		func(f: StringName, fallen: Array[BattleCombatant]) -> void: cleared.append([f, fallen.size()])
	)
	var crab := engine.enemies[0]
	var crab_hp := crab.hp
	ilun.swell = Formulas.SWELL_MAX
	var res := engine.vowbound.unleash(engine, engine.living_foes_of(ilun))
	assert_true(res.ok, str(res.fail_reason))
	assert_false(engine.fields.has(&"flood"), "the flood is cleared")
	assert_eq(cleared, [[&"flood", 1]], "the foe bound to it falls with it")
	assert_false(bound.is_alive())
	assert_true(crab.hp < crab_hp, "the crab drinks water, but not the net")


func test_floodnet_is_never_greyed_out_by_a_missing_field() -> void:
	assert_true(engine.summon(ILUN))
	var ilun := engine.vowbound.summon
	var cleared: Array = []
	engine.field_cleared.connect(func(f: StringName, _fallen: Array[BattleCombatant]) -> void: cleared.append(f))
	assert_eq(BossMechanics.refusal(engine, engine.db.skill(&"floodnet")), &"", "a finisher is not refused")
	ilun.swell = Formulas.SWELL_MAX
	assert_true(engine.vowbound.unleash(engine, engine.living_foes_of(ilun)).ok)
	assert_true(cleared.is_empty(), "no field was up, so none is cleared")


func test_the_call_ends_the_callers_turn_at_once() -> void:
	var asha := engine.find(&"asha")
	var taken := asha.turns_taken
	var order: Array[String] = []
	engine.turn_ended.connect(func(c: BattleCombatant, _ch: Array[Dictionary]) -> void: order.append("end:%s" % c.id))
	engine.turn_started.connect(func(c: BattleCombatant) -> void: order.append("start:%s" % c.id))
	assert_true(engine.summon(ILUN))
	assert_eq(asha.turns_taken, taken + 1, "ADR 0027 A3: the call is Asha's turn")
	assert_eq(order, ["end:asha", "start:ilun"] as Array[String])


func test_a_poisoned_caller_ticks_once_per_call() -> void:
	var asha := engine.find(&"asha")
	asha.add_status(&"poison", -1)
	var ticks: Array[int] = []
	engine.turn_ended.connect(
		func(c: BattleCombatant, changes: Array[Dictionary]) -> void:
			for ch in changes:
				if c == asha and ch["cause"] == &"poison":
					ticks.append(int(ch["amount"]))
	)
	var hp := asha.hp
	assert_true(engine.summon(ILUN))
	var lost := Formulas.poison_damage(asha.max_hp)
	assert_eq(asha.hp, hp - lost, "ADR 0027 A3: Poison ticks at the call")
	assert_eq(engine.vowbound.call_changes, [{"target_id": &"asha", "cause": &"poison", "amount": lost, "doom": 0}])
	assert_true(engine.dismiss())
	assert_eq(ticks, [lost] as Array[int], "not again while she stood down or on the return")
	_keep_alive()
	_turn_of(engine, &"asha")
	assert_eq(ticks.size(), 1, "her own next turn has not ended yet")
	assert_true(engine.summon(ILUN))
	assert_eq(ticks.size(), 2, "once per call")


func test_a_doomed_caller_counts_down_once_per_call() -> void:
	var asha := engine.find(&"asha")
	asha.add_status(&"doom", 3)
	assert_true(engine.summon(ILUN))
	assert_eq(asha.doom_count(), 2)
	assert_eq(engine.vowbound.call_changes[-1]["cause"], &"doom_tick")
	assert_true(engine.dismiss())
	assert_eq(asha.doom_count(), 2, "the count holds while she stands down")
	_keep_alive()
	_turn_of(engine, &"asha")
	assert_true(engine.summon(ILUN))
	assert_eq(asha.doom_count(), 1)
	assert_true(engine.dismiss())
	_keep_alive()
	_turn_of(engine, &"asha")
	assert_eq(engine.current, asha)
	assert_true(engine.summon(ILUN))
	assert_false(asha.is_alive(), "Doom fells her at the third call")
	assert_eq(engine.vowbound.call_changes[-1]["cause"], &"doom")
	assert_eq(engine.current, engine.vowbound.summon, "Ilun still takes the field")


## Tops up the party so the foes can't end it while a test waits for a turn.
func _keep_alive() -> void:
	for c in engine.party_active + engine.party_reserve:
		if c.is_alive():
			c.hp = c.max_hp


func test_a_vowbound_that_hands_back_a_fallen_party_ends_in_defeat() -> void:
	var rhen := engine.find(&"rhen")
	var asha := engine.find(&"asha")
	rhen.fall()
	asha.add_status(&"doom", 1)
	assert_true(engine.summon(ILUN))
	assert_false(asha.is_alive(), "Doom took her at the call")
	assert_eq(engine.outcome, &"", "Ilun still stands")
	assert_true(engine.dismiss())
	assert_eq(engine.outcome, BattleEngine.OUTCOME_DEFEAT, "nobody is left to come back")


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
	engine.enemies[0].hp = 0  # leaves two foes for Floodnet
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


static func _turn_of(e: BattleEngine, cid: StringName) -> void:
	var guard := 0
	while e.outcome == &"" and e.current.id != cid and guard < 50:
		guard += 1
		if e.is_party_turn():
			var foes := e.living_foes_of(e.current)
			e.perform(&"attack", [foes[mini(1, foes.size() - 1)]] as Array[BattleCombatant])
		else:
			e.run_enemy_turn()
