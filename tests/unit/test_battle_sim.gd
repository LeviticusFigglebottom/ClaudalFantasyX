extends TestCase
## BattleSim and the SimPolicy family (M1-CMB-05) through their public API: CLI parsing and
## dispatch (what tools/balance/sim_main.gd calls), aggregation, and each policy's decisions.

const REEF := &"sandbox_reef"


class IdlePolicy:
	extends SimPolicy

	func decide(_engine: BattleEngine) -> void:
		pass


# --- CLI ---------------------------------------------------------------------------------


func test_parse_args_and_split_ids() -> void:
	var args := BattleSim.parse_args(["--encounter=reef", "--seeds=5", "stray", "--flag", "--out=/a=b"])
	assert_eq(args, {"encounter": "reef", "seeds": "5", "out": "/a=b"})
	assert_eq(BattleSim.split_ids(" a, b,,c "), [&"a", &"b", &"c"] as Array[StringName])
	assert_eq(BattleSim.split_ids(""), [] as Array[StringName])


func test_run_cli_runs_each_policy() -> void:
	var args := {"encounter": "sandbox_reef", "active": "rhen,asha", "reserve": "toma,ysolde", "seeds": "3"}
	args["policies"] = "naive,smart"
	args["first-seed"] = "7"
	var res := BattleSim.new().run_cli(args)
	assert_true(res["ok"], str(res["error"]))
	var results: Array = res["results"]
	assert_eq(results.size(), 2)
	var first: Dictionary = results[0]
	assert_eq(first["policy"], "naive")
	assert_eq(first["n"], 3)
	assert_eq(first["first_seed"], 7)
	assert_eq((first["runs"] as Array).size(), 3)
	assert_eq((first["runs"] as Array)[0]["seed"], 7)


func test_run_cli_defaults_to_every_policy() -> void:
	var res := BattleSim.new().run_cli({"encounter": "sandbox_reef", "active": "rhen,asha", "seeds": "1"})
	assert_true(res["ok"])
	assert_eq((res["results"] as Array).size(), BattleSim.POLICY_NAMES.size())


func test_run_cli_rejects_bad_requests() -> void:
	var sim := BattleSim.new()
	assert_false(sim.run_cli({})["ok"])
	assert_false(sim.run_cli({"encounter": "nowhere", "active": "rhen", "seeds": "1"})["ok"])
	assert_false(sim.run_cli({"encounter": "sandbox_reef", "seeds": "1"})["ok"], "needs an active party")
	assert_false(sim.run_cli({"encounter": "sandbox_reef", "active": "rhen", "seeds": "0"})["ok"])
	var bad := sim.run_cli({"encounter": "sandbox_reef", "active": "rhen", "seeds": "1", "policies": "naive,psychic"})
	assert_false(bad["ok"])
	assert_true(str(bad["error"]).contains("psychic"))
	assert_eq((bad["results"] as Array).size(), 0, "nothing runs on a bad policy list")


# --- runner and aggregation --------------------------------------------------------------


func test_make_policy_names_and_unknown() -> void:
	var sim := BattleSim.new()
	for policy in BattleSim.POLICY_NAMES:
		assert_eq(sim.make_policy(policy).policy_name(), policy)
	assert_eq(sim.make_policy(&"psychic"), null)
	assert_eq(SimPolicy.new().policy_name(), &"base")
	assert_eq(int(sim.make_policy(&"smart").config.get("heal_below_pct", 0)) > 0, true, "smart reads its config")


func test_run_many_aggregates_seeds() -> void:
	var sim := BattleSim.new()
	var active: Array[StringName] = [&"rhen", &"asha"]
	var reserve: Array[StringName] = [&"toma"]
	var agg := sim.run_many(REEF, active, reserve, &"lowest_hp", 4, 11)
	assert_eq(agg["n"], 4)
	assert_eq(agg["policy"], "lowest_hp")
	assert_eq(agg["encounter"], "sandbox_reef")
	assert_eq(agg["first_seed"], 11)
	assert_between(agg["win_pct"], 0.0, 100.0)
	assert_true(int(agg["p90_turns"]) >= 1)


func test_summarize_counts_timeouts_and_handles_empty() -> void:
	var runs: Array[Dictionary] = [
		{"outcome": "timeout", "turns": 4, "party_ko": 0, "items": 1},
		{"outcome": "victory", "turns": 2, "party_ko": 1, "items": 0},
	]
	var s := BattleSim.summarize(runs)
	assert_eq(s["timeouts"], 1)
	assert_eq(s["wins"], 1)
	assert_eq(s["mean_items"], 0.5)
	var none := BattleSim.summarize([] as Array[Dictionary])
	assert_eq(none["n"], 0)
	assert_eq(none["mean_turns"], 0.0)
	assert_eq(none["win_pct"], 0.0)


func test_base_policy_plays_basic_attacks_to_the_end() -> void:
	var sim := BattleSim.new()
	var active: Array[StringName] = [&"rhen", &"asha"]
	var r := sim.run_one(REEF, active, [] as Array[StringName], SimPolicy.new(), 3)
	assert_true(r["outcome"] in ["victory", "defeat"])


func test_idle_policy_falls_back_to_basic_attack() -> void:
	var engine := _real_engine(5)
	var actor := engine.current
	IdlePolicy.new().take_turn(engine)
	assert_ne(engine.current, actor, "the fallback ended the turn")


func test_policies_honour_provoke() -> void:
	var engine := _real_engine(5)
	var actor := engine.current
	var provoker := engine.enemies[2]
	actor.add_status(&"provoke", 3)
	actor.provoker_id = provoker.id
	var hp := provoker.hp
	SimPolicyNaive.new().take_turn(engine)
	assert_true(provoker.hp < hp or engine.current != actor, "the naive attack went to the provoker")
	assert_ne(engine.current, actor)


func test_basic_fallback_escapes_when_nothing_is_usable() -> void:
	var engine := BattleEngine.new()
	var active: Array[StringName] = [&"mage"]
	engine.setup(_fixture_db(), active, [] as Array[StringName], &"duo", 2)
	engine.begin()
	_to_party_turn(engine)
	engine.current.mp = 0
	var actor := engine.current
	SimPolicy.new().take_turn(engine)
	assert_true(engine.outcome == BattleEngine.OUTCOME_ESCAPED or engine.current != actor, "escape tried")


# --- policy helpers ----------------------------------------------------------------------


func test_use_targets_groups() -> void:
	var engine := _fixture_engine()
	var me := engine.current
	assert_true(SimPolicy.use(engine, &"zap_all", null))
	_to_party_turn(engine)
	me = engine.current
	me.hp = 10
	assert_true(SimPolicy.use(engine, &"mend_all", null))
	assert_true(me.hp > 10)


func test_best_damage_skill_counts_group_hits() -> void:
	var engine := _fixture_engine()
	var actor := engine.current
	var foe := engine.living_foes_of(actor)[0]
	assert_eq(SimPolicy.best_damage_skill(engine, actor, foe), &"zap_all", "two foes beat one for the same power")
	actor.mp = 0
	assert_eq(SimPolicy.best_damage_skill(engine, actor, foe), &"attack", "nothing affordable: basic attack")


func test_expected_damage_zero_for_reflect_and_support() -> void:
	var engine := _fixture_engine()
	var actor := engine.current
	var foe := engine.living_foes_of(actor)[0]
	assert_true(SimPolicy.expected_damage(engine, actor, &"zap", foe) > 0.0)
	foe.add_status(&"reflect", 3)
	assert_eq(SimPolicy.expected_damage(engine, actor, &"zap", foe), 0.0, "it would bounce")
	assert_eq(SimPolicy.expected_damage(engine, actor, &"mend_all", foe), 0.0)


func test_usable_skills_respects_silence_and_break_skill_ignores_groups() -> void:
	var engine := _fixture_engine()
	var actor := engine.current
	var foe := engine.living_foes_of(actor)[0]
	assert_true(SimPolicy.usable_skills(engine, actor).has(&"zap"))
	assert_eq(SimPolicy.break_skill(engine, actor, foe), &"", "the only Break skill here is a group skill")
	actor.add_status(&"silence", 2)
	var usable := SimPolicy.usable_skills(engine, actor)
	assert_false(usable.has(&"zap"))
	assert_true(usable.has(&"attack"))


func test_role_answer_does_nothing_without_foes() -> void:
	var engine := _real_engine(5)
	var actor := engine.current
	for e in engine.enemies:
		e.hp = 0
	SimPolicyRoleAnswer.new().decide(engine)
	assert_eq(engine.current, actor, "no target, no action")


func test_smart_replaces_a_fallen_member() -> void:
	var engine := _real_engine(5)
	var actor := engine.current
	var fallen := engine.party_active[1] if engine.party_active[0] == actor else engine.party_active[0]
	fallen.hp = 0
	var smart := BattleSim.new().make_policy(&"smart")
	smart.take_turn(engine)
	assert_false(engine.party_active.has(fallen), "a living reserve took the fallen member's slot")
	assert_true(engine.party_reserve.has(fallen))


func test_smart_prefers_a_reserve_who_answers_a_foe() -> void:
	var engine := _real_engine(5)
	var actor := engine.current
	var fallen := engine.party_active[1] if engine.party_active[0] == actor else engine.party_active[0]
	fallen.hp = 0
	for e in engine.enemies:
		if SimPolicy.role_answer(engine, e) == &"toma":
			e.hp = 0  # nobody needs Toma any more; Ysolde still answers the eel
	var smart := BattleSim.new().make_policy(&"smart")
	smart.take_turn(engine)
	assert_true(engine.find(&"ysolde") in engine.party_active)


func test_smart_heals_the_most_hurt_ally() -> void:
	var engine := _real_engine(1)
	var guard := 0
	while engine.current.id != &"asha" and guard < 40:
		guard += 1
		if engine.is_party_turn():
			SimPolicyNaive.new().take_turn(engine)
		else:
			engine.run_enemy_turn()
	var rhen := engine.find(&"rhen")
	rhen.hp = 20
	var mp := engine.current.mp
	BattleSim.new().make_policy(&"smart").take_turn(engine)
	assert_true(rhen.hp > 20, "Mend went to Rhen")
	assert_true(engine.find(&"asha").mp < mp)


# --- helpers -----------------------------------------------------------------------------


func _real_engine(rng_seed: int) -> BattleEngine:
	var engine := BattleEngine.new()
	var active: Array[StringName] = [&"rhen", &"asha"]
	var reserve: Array[StringName] = [&"toma", &"ysolde"]
	engine.setup(BattleDB.load_default(), active, reserve, REEF, rng_seed)
	engine.begin()
	_to_party_turn(engine)
	return engine


func _fixture_engine() -> BattleEngine:
	var engine := BattleEngine.new()
	var active: Array[StringName] = [&"fighter"]
	engine.setup(_fixture_db(), active, [] as Array[StringName], &"duo", 1)
	engine.begin()
	_to_party_turn(engine)
	return engine


static func _to_party_turn(engine: BattleEngine) -> void:
	var guard := 0
	while not engine.is_party_turn() and engine.outcome == &"" and guard < 50:
		guard += 1
		engine.run_enemy_turn()


static func _fixture_db() -> BattleDB:
	var stats := {
		"level": 5,
		"hp": 500,
		"mp": 50,
		"strength": 10,
		"magic": 20,
		"defense": 5,
		"magic_defense": 5,
		"agility": 30,
		"accuracy": 0,
		"evasion": 0,
		"luck": 0,
	}
	var foe := stats.duplicate()
	foe["agility"] = 1
	foe["hp"] = 5000
	var ai := [{"pick": [{"skill": "attack", "target": "random_foe"}]}]
	return (
		BattleDB
		. from_tables(
			{
				"skills":
				[
					{"id": "attack", "kind": "physical", "power": 4, "rank": 3, "accuracy": 100},
					{"id": "zap", "kind": "magical", "power": 6, "rank": 3, "mp_cost": 2, "magic": true},
					{
						"id": "zap_all",
						"kind": "magical",
						"power": 6,
						"rank": 3,
						"mp_cost": 2,
						"magic": true,
						"target": "all_foes",
					},
					{"id": "mend_all", "kind": "heal", "power": 4, "rank": 3, "target": "all_allies", "magic": true},
					{
						"id": "crack_all",
						"kind": "physical",
						"power": 1,
						"rank": 3,
						"accuracy": 100,
						"target": "all_foes",
						"statuses": [{"id": "armor_break", "chance": 100, "duration": -1}],
					},
				],
				"statuses": [],
				"characters":
				[
					{"id": "fighter", "stats": stats, "skills": ["attack", "zap", "zap_all", "mend_all", "crack_all"]},
					{"id": "mage", "stats": stats, "skills": ["zap"]},
				],
				"enemies": [{"id": "dummy", "stats": foe, "skills": ["attack"], "ai": ai, "xp": 1}],
				"encounters": [{"id": "duo", "enemies": ["dummy", "dummy"]}],
			}
		)
	)
