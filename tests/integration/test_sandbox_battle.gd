extends TestCase
## Runs the M1 sandbox encounter on the REAL data tables: proves the data is loadable and
## internally consistent, that battles always end deterministically, and that balance sits
## in the M1 target bands (docs/kb/design/battle_ctb.md §Sandbox balance).

const SEEDS := 100
const NAIVE_MAX_WIN_PCT := 20
const SWAP_MIN_WIN_PCT := 70
## M1-CMB-05 bands via BattleSim (docs/kb/design/balance_targets.md). 200 seeds keeps the
## test fast; tools/balance/sim.py runs 1000 for the report.
const SIM_SEEDS := 200
const SIM_NAIVE_MIN_WIN_PCT := 1
const SIM_ROLE_ANSWER_MIN_WIN_PCT := 85
const SIM_SMART_MIN_WIN_PCT := 85
## The ease ceiling (tools/balance/targets.json `mean_turns_min`, M1-CMB-07): smart wins every
## seed, so only a shorter fight can show that the sandbox got easier.
const SIM_SMART_MIN_MEAN_TURNS := 16.0


func test_real_data_loads() -> void:
	var db := BattleDB.load_default()
	assert_true(db.encounters.has(&"sandbox_reef"))
	assert_eq(db.statuses.size(), 21, "all §6.8 statuses declared")


func test_sandbox_terminates_deterministically() -> void:
	var a := _play(1234, &"naive")
	var b := _play(1234, &"naive")
	assert_eq(a, b)
	assert_true(a[-1] in ["victory", "defeat"], "battle ended: %s" % a[-1])


func test_balance_bands_reward_swapping() -> void:
	var naive := _win_pct(&"naive")
	var swap := _win_pct(&"swap_toma")
	assert_true(naive <= NAIVE_MAX_WIN_PCT, "naive all-attack wins %d%% (max %d%%)" % [naive, NAIVE_MAX_WIN_PCT])
	assert_true(swap >= SWAP_MIN_WIN_PCT, "swap-in-Toma wins %d%% (min %d%%)" % [swap, SWAP_MIN_WIN_PCT])


func _win_pct(policy: StringName) -> int:
	var wins := 0
	for rng_seed in SEEDS:
		if _play(rng_seed, policy)[-1] == "victory":
			wins += 1
	return wins * 100 / SEEDS


## Policies: &"naive" attacks the first living foe; &"swap_toma" swaps Toma in for Asha on
## the first party turn, then attacks the lowest-HP foe.
func _play(rng_seed: int, policy: StringName) -> Array[String]:
	var e := BattleEngine.new()
	var active: Array[StringName] = [&"rhen", &"asha"]
	var reserve: Array[StringName] = [&"toma", &"ysolde"]
	e.setup(BattleDB.load_default(), active, reserve, &"sandbox_reef", rng_seed)
	e.begin()
	var out: Array[String] = []
	var swapped := false
	var guard := 0
	while e.outcome == &"" and guard < 1000:
		guard += 1
		if e.is_party_turn():
			if policy == &"swap_toma" and not swapped:
				e.swap(&"asha", &"toma")
				swapped = true
			var foes := e.living_foes_of(e.current)
			var target := foes[0]
			if policy == &"swap_toma":
				for f in foes:
					if f.hp < target.hp:
						target = f
			var t: Array[BattleCombatant] = [target]
			var r := e.perform(&"attack", t)
			out.append("%s>%s" % [r.actor_id, target.id])
		else:
			var r2 := e.run_enemy_turn()
			out.append("%s:%s" % [r2.actor_id, r2.skill_id])
	out.append(String(e.outcome))
	return out


func test_sim_bands_naive_rarely_wins_role_answer_does() -> void:
	var sim := BattleSim.new()
	var active: Array[StringName] = [&"rhen", &"asha"]
	var reserve: Array[StringName] = [&"toma", &"ysolde"]
	var kit := sim.loadout(&"m1_starting")  # the bands assume starting gear (balance_targets.md)
	assert_false(kit.is_empty())
	var naive := sim.run_many(&"sandbox_reef", active, reserve, &"naive", SIM_SEEDS, 1, Callable(), kit)
	var answer := sim.run_many(&"sandbox_reef", active, reserve, &"role_answer", SIM_SEEDS, 1, Callable(), kit)
	var naive_pct: float = naive["win_pct"]
	var answer_pct: float = answer["win_pct"]
	assert_between(naive_pct, SIM_NAIVE_MIN_WIN_PCT, NAIVE_MAX_WIN_PCT, "naive wins %.1f%%" % naive_pct)
	assert_true(answer_pct >= SIM_ROLE_ANSWER_MIN_WIN_PCT, "role answer wins %.1f%%" % answer_pct)
	assert_eq(naive["timeouts"], 0)
	assert_eq(answer["timeouts"], 0)


func test_sim_smart_band_has_an_ease_ceiling() -> void:
	var sim := BattleSim.new()
	var active: Array[StringName] = [&"rhen", &"asha"]
	var reserve: Array[StringName] = [&"toma", &"ysolde"]
	var kit := sim.loadout(&"m1_starting")
	var smart := sim.run_many(&"sandbox_reef", active, reserve, &"smart", SIM_SEEDS, 1, Callable(), kit)
	var win_pct: float = smart["win_pct"]
	var mean_turns: float = smart["mean_turns"]
	assert_true(win_pct >= SIM_SMART_MIN_WIN_PCT, "smart wins %.1f%%" % win_pct)
	assert_true(mean_turns >= SIM_SMART_MIN_MEAN_TURNS, "smart takes %.1f mean turns" % mean_turns)
	assert_eq(smart["timeouts"], 0)


func test_sim_is_deterministic_and_counts() -> void:
	var sim := BattleSim.new()
	var active: Array[StringName] = [&"rhen", &"asha"]
	var reserve: Array[StringName] = [&"toma", &"ysolde"]
	for policy in BattleSim.POLICY_NAMES:
		var p := sim.make_policy(policy)
		var a := sim.run_one(&"sandbox_reef", active, reserve, p, 42)
		var b := sim.run_one(&"sandbox_reef", active, reserve, sim.make_policy(policy), 42)
		assert_eq(a, b, "%s replays identically" % policy)
		assert_true(a["outcome"] in ["victory", "defeat"], "%s ended: %s" % [policy, a["outcome"]])
		assert_true(int(a["turns"]) >= int(a["party_turns"]))
		assert_eq(a["items"], 0, "no items yet")


func test_sim_summary_math() -> void:
	var runs: Array[Dictionary] = []
	for i in 10:
		var won := i < 3
		runs.append({"outcome": "victory" if won else "defeat", "turns": i + 1, "party_ko": 1, "items": 0})
	var s := BattleSim.summarize(runs)
	assert_eq(s["wins"], 3)
	assert_eq(s["win_pct"], 30.0)
	assert_eq(s["mean_turns"], 5.5)
	assert_eq(s["p90_turns"], 9, "nearest rank: ceil(0.9 x 10) = 9th value")
	assert_eq(s["mean_party_ko"], 1.0)
	assert_eq(BattleSim.percentile([] as Array[int], 90), 0)
