extends TestCase
## The Drownbell end to end on the real data (M2-FP-06): the encounter Cutscene B starts, played
## headless by the balancing simulator's policies. Bands: balance_targets.md (Ch3 boss).

const PARTY: Array[StringName] = [&"rhen", &"asha", &"toma"]
const LOADOUT := &"ch03_drownbell"
const SEEDS := 200

var sim: BattleSim


func before_each() -> void:
	sim = BattleSim.new()


func test_encounter_data_is_the_two_phase_bell() -> void:
	var enc: Dictionary = sim.db.encounters[&"drownbell"]
	assert_true(bool(enc["scripted"]), "a story boss: no escape")
	assert_eq(enc["enemies"], ["drownbell"])
	var bell: Dictionary = sim.db.enemies[&"drownbell"]
	assert_true(bool(bell["delay_immune"]))
	assert_eq(int(bell["currency"]), 300, "economy.md: about 300 lume")
	assert_eq((bell["phases"] as Array).size(), 1)
	assert_eq(str(sim.db.skill(&"call_ilun")["requires_flag"]), "ch03_ilun_bound")
	assert_false(BattleStage.stand_in_spec(&"drownbell#1").is_empty())
	assert_false(BattleStage.stand_in_spec(&"spawn_polyp#2").is_empty())


func test_smart_party_wins_a_headless_fight_through_both_phases() -> void:
	var engine := BattleEngine.new()
	var kit := sim.loadout(LOADOUT)
	var fx := sim._equip(kit["gear"])
	engine.party_modifier = fx.apply_to
	engine.story_flags = [&"ch03_ilun_bound"]
	engine.setup(sim.db, PARTY, [], &"drownbell", 1)
	var seen: Array[String] = []
	engine.charge_started.connect(func(_c: BattleCombatant, s: StringName, _t: int) -> void: seen.append("charge:" + s))
	engine.phase_changed.connect(func(_e: BattleCombatant, p: StringName) -> void: seen.append("phase:" + p))
	engine.field_cleared.connect(func(f: StringName, _x: Array[BattleCombatant]) -> void: seen.append("cleared:" + f))
	var policy := sim.make_policy(&"smart")
	policy.reset()
	engine.begin()
	var n := 0
	while engine.outcome == &"" and n < 500:
		n += 1
		if engine.is_party_turn():
			policy.take_turn(engine)
		else:
			engine.run_enemy_turn()
	assert_eq(engine.outcome, BattleEngine.OUTCOME_VICTORY)
	assert_true(seen.has("charge:toll"), "phase 1 tolled or tried to")
	assert_true(seen.has("phase:flood"))
	assert_true(seen.has("cleared:flood"), "Asha called Ilun")
	assert_eq(engine.currency_award(), 300)
	assert_true(engine.xp_awards().has(&"asha"))


## A quick guard; the bands themselves are gated by tools/balance/sim.py --check at 1000 seeds. With the
## real Vowbound call (M2-FP-17) role_answer and smart's p90 sit near their band edges at 1000 seeds
## (71.0%, p90 60), so the 200-seed margins allow its sampling spread (64.5%, p90 62).
func test_bands_hold_at_200_seeds() -> void:
	var kit := sim.loadout(LOADOUT)
	var naive := sim.run_many(&"drownbell", PARTY, [], &"naive", SEEDS, 1, Callable(), kit)
	var role := sim.run_many(&"drownbell", PARTY, [], &"role_answer", SEEDS, 1, Callable(), kit)
	var smart := sim.run_many(&"drownbell", PARTY, [], &"smart", SEEDS, 1, Callable(), kit)
	assert_true(float(naive["win_pct"]) <= 10.0, "naive %.1f%%" % naive["win_pct"])
	assert_between(float(role["win_pct"]), 60.0, 95.0, "role_answer")
	assert_between(float(smart["win_pct"]), 75.0, 98.0, "smart")
	# M2-FP-17: the real Vowbound call; the masher who calls into the flood never stalls the fight.
	var flood := sim.run_many(&"drownbell", PARTY, [], &"flood_call", SEEDS, 1, Callable(), kit)
	assert_true(float(flood["win_pct"]) <= 95.0, "flood_call %.1f%%" % flood["win_pct"])
	for agg: Dictionary in [naive, role, smart, flood]:
		assert_eq(int(agg["timeouts"]), 0, "%s never stalls" % agg["policy"])
		assert_true(int(agg["p90_turns"]) <= 65, "%s p90 %d" % [agg["policy"], agg["p90_turns"]])


func test_without_ilun_the_flood_wins() -> void:
	var kit := sim.loadout(LOADOUT)
	kit.erase("flags")
	kit.erase("vowbound")  # neither the stand-in nor the real call (M2-FP-17)
	var agg := sim.run_many(&"drownbell", PARTY, [], &"smart", 20, 1, Callable(), kit)
	assert_true(float(agg["win_pct"]) <= 10.0, "no Ilun: %.1f%%" % agg["win_pct"])


func test_a_party_modifier_runs_alongside_the_gear() -> void:
	var seen: Array[StringName] = []
	var mark := func(c: BattleCombatant) -> void: seen.append(c.id)
	var r := sim.run_one(&"drownbell", PARTY, [], sim.make_policy(&"naive"), 1, mark, sim.loadout(LOADOUT))
	assert_eq(seen, PARTY)
	assert_eq(r["outcome"], "defeat")


func test_same_seed_same_fight() -> void:
	var kit := sim.loadout(LOADOUT)
	var a := sim.run_one(&"drownbell", PARTY, [], sim.make_policy(&"smart"), 42, Callable(), kit)
	var b := sim.run_one(&"drownbell", PARTY, [], sim.make_policy(&"smart"), 42, Callable(), kit)
	assert_eq(a, b)
