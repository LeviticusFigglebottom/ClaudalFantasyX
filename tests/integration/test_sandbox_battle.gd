extends TestCase
## Runs the M1 sandbox encounter on the REAL data tables: proves the data is loadable and
## internally consistent, and that a naive policy always reaches an outcome.


func test_real_data_loads() -> void:
	var db := BattleDB.load_default()
	assert_true(db.encounters.has(&"sandbox_reef"))
	assert_eq(db.statuses.size(), 21, "all §6.8 statuses declared")


func test_sandbox_terminates_deterministically() -> void:
	var a := _play(1234)
	var b := _play(1234)
	assert_eq(a, b)
	assert_true(a[-1] in ["victory", "defeat"], "battle ended: %s" % a[-1])


func _play(rng_seed: int) -> Array[String]:
	var e := BattleEngine.new()
	var active: Array[StringName] = [&"rhen", &"asha"]
	var reserve: Array[StringName] = [&"toma", &"ysolde"]
	e.setup(BattleDB.load_default(), active, reserve, &"sandbox_reef", rng_seed)
	e.begin()
	var out: Array[String] = []
	var guard := 0
	while e.outcome == &"" and guard < 1000:
		guard += 1
		if e.is_party_turn():
			var foes := e.living_foes_of(e.current)
			var t: Array[BattleCombatant] = [foes[0]]
			var r := e.perform(&"attack", t)
			out.append("%s>%s" % [r.actor_id, t[0].id])
		else:
			var r2 := e.run_enemy_turn()
			out.append("%s:%s" % [r2.actor_id, r2.skill_id])
	out.append(String(e.outcome))
	return out
