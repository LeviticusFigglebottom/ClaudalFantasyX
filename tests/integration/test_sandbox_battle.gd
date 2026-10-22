extends TestCase
## Runs the M1 sandbox encounter on the REAL data tables: proves the data is loadable and
## internally consistent, that battles always end deterministically, and that balance sits
## in the M1 target bands (docs/kb/design/battle_ctb.md §Sandbox balance).

const SEEDS := 100
const NAIVE_MAX_WIN_PCT := 20
const SWAP_MIN_WIN_PCT := 70


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
