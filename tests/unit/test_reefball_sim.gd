extends TestCase
## ReefballSim and ReefballDB (M3-RBL-01) on fixture and REAL tables: the real data loads, every
## match ends, seeds replay, and the Tidecup opening round sits in its balance bands
## (tools/balance/reefball_targets.json, docs/kb/design/reefball.md § Balance).

const TARGETS_PATH := "res://tools/balance/reefball_targets.json"


func test_real_data_loads() -> void:
	var db := ReefballDB.load_default()
	assert_true(db.load_errors.is_empty(), str(db.load_errors))
	assert_true(db.matches.has(&"tidecup_opening"))
	var m := ReefballMatch.new()
	assert_true(m.setup(db, &"tidecup_opening", 1))
	assert_eq(m.side_ids, [&"oruvel", &"pemakar"] as Array[StringName])
	assert_eq(m.diver(&"rhen").side, m.player_side, "Rhen dives for Oruvel (ADR 0017)")
	assert_eq((db.sides[&"oruvel"] as Dictionary)["captain"], "tavi", "Tavi Orse captains")


func test_missing_tables_read_as_empty() -> void:
	var db := ReefballDB.load_dir("res://tests/fixtures/reefball/no_such_dir")
	assert_eq(db.load_errors.size(), ReefballDB.TABLES.size())
	assert_true(db.matches.is_empty() and db.rules.is_empty())


func test_from_tables_indexes_roles_and_profiles() -> void:
	var db := ReefballFixture.db()
	assert_true(db.roles.has(&"chaser") and db.roles.has(&"keeper"))
	assert_true(db.ai_profiles.has(&"test"))
	assert_true(db.sides.has(&"east"))


func test_play_is_deterministic_and_ends() -> void:
	var sim := ReefballSim.new(ReefballFixture.db())
	for policy: StringName in [&"naive", &"test"]:
		var a := sim.play(ReefballFixture.MATCH, policy, 9)
		assert_eq(a, sim.play(ReefballFixture.MATCH, policy, 9), String(policy))
		assert_false(a["stalled"])
	assert_true(sim.play(&"nope", &"naive", 1).is_empty())


func test_run_aggregates() -> void:
	var sim := ReefballSim.new(ReefballFixture.db())
	var r := sim.run(ReefballFixture.MATCH, &"test", 20)
	assert_eq(r["n"], 20)
	assert_eq(int(r["wins"]) + int(r["draws"]) + int(r["losses"]), 20)
	assert_between(r["win_pct"], 0.0, 100.0)
	assert_eq(r["stalled"], 0)


func test_naive_carries_it_up_itself() -> void:
	var m := ReefballFixture.begun()
	assert_eq(ReefballSim.naive_choice(m)["action"], ReefballMatch.RISE)
	m.holder.depth = 1
	m.fetched = false
	assert_eq(ReefballSim.naive_choice(m)["action"], ReefballMatch.DIVE, "fetch it first")


func test_naive_passes_when_it_can_neither_rise_nor_dive() -> void:
	var raw := ReefballFixture.tables()
	raw["rules"]["bands"] = [{"id": "ring"}, {"id": "weep"}]
	raw["rules"]["fetch_depth"] = 1
	var m := ReefballFixture.begun(1, raw)
	m.fetched = false
	assert_eq(ReefballSim.naive_choice(m)["action"], ReefballMatch.PASS)


func test_unknown_ids_and_bad_tables() -> void:
	assert_eq(ReefballFixture.begun().diver(&"nobody"), null)
	var db := ReefballDB.from_tables({"rules": {"roles": "not a list"}, "sides": [{"no_id": 1}]})
	assert_true(db.roles.is_empty() and db.sides.is_empty())


func test_cli() -> void:
	var args := ReefballSim.parse_args(
		PackedStringArray(["--match=fixture", "--policies=naive,test", "--seeds=3", "x"])
	)
	assert_eq(args, {"match": "fixture", "policies": "naive,test", "seeds": "3"})
	var sim := ReefballSim.new(ReefballFixture.db())
	var ok := sim.run_cli(args)
	assert_true(ok["ok"])
	assert_eq((ok["results"] as Array).size(), 2)
	assert_false(sim.run_cli({"match": "nope", "seeds": "3", "policies": "naive"})["ok"])
	assert_false(sim.run_cli({"match": "fixture", "seeds": "0", "policies": "naive"})["ok"])
	assert_false(sim.run_cli({"match": "fixture", "seeds": "3", "policies": "nobody"})["ok"])
	assert_false(sim.run_cli({"match": "fixture", "seeds": "3", "policies": ""})["ok"])
	assert_true(sim.has_policy(&"naive") and sim.has_policy(&"test"))


func test_tidecup_sits_in_its_bands() -> void:
	var suite: Dictionary = (JSON.parse_string(FileAccess.get_file_as_string(TARGETS_PATH)) as Dictionary)["suites"][0]
	var sim := ReefballSim.new()
	var slack := float(suite["test_slack_pp"])
	var bands: Dictionary = suite["bands"]
	for policy: String in bands:
		var r := sim.run(StringName(str(suite["match"])), StringName(policy), int(suite["test_seeds"]))
		assert_eq(r["stalled"], 0, policy)
		if bands[policy] == null:
			continue
		var band: Array = bands[policy]
		assert_between(r["win_pct"], float(band[0]) - slack, float(band[1]) + slack, "%s win %%" % policy)
		if policy == "smart":
			assert_between(r["draw_pct"], 0.0, float(suite["max_draw_pct"]) + slack, "smart draws")
