extends TestCase
## ReefballMatch (M3-RBL-01): setup, kickoff, legal actions, preview == resolution, turnovers,
## scoring, breath, swimming, the clock and overtime, signals and determinism. Fixture tables
## (tests/fixtures/reefball); the real data is played in test_reefball_sim.gd.

const EPS := 0.0001


func _place(m: ReefballMatch, depths: Dictionary) -> void:
	for id: StringName in depths:
		m.diver(id).depth = int(depths[id])


## Every west diver out of the way at the weep (east's carrier then plays in open water).
func _clear_west(m: ReefballMatch) -> void:
	_place(m, {&"w_carry": 4, &"w_mate": 4, &"w_keep": 4})


func _actions(m: ReefballMatch) -> Array[String]:
	var out: Array[String] = []
	for a in m.legal_actions():
		out.append("%s:%s" % [a["action"], a["target"]])
	return out


func test_setup_rejects_unknown_match_and_side() -> void:
	var m := ReefballMatch.new()
	assert_false(m.setup(ReefballFixture.db(), &"nope", 1))
	var raw := ReefballFixture.tables()
	raw["matches"][0]["sides"] = ["east", "nowhere"]
	assert_false(m.setup(ReefballFixture.db(raw), ReefballFixture.MATCH, 1))


func test_begin_kicks_off_at_the_weep() -> void:
	var m := ReefballFixture.begun()
	assert_eq(m.holder.id, &"e_carry")
	assert_eq(m.holder.depth, m.bed())
	assert_true(m.fetched, "the weep is below fetch_depth")
	assert_true(m.is_player_contact())
	assert_eq(m.strokes_left, 10)
	var want := {&"e_mate": 3, &"e_keep": 1, &"w_carry": 3, &"w_mate": 3, &"w_keep": 0}
	for id: StringName in want:
		assert_eq(m.diver(id).depth, want[id], "%s kickoff band" % id)


func test_legal_actions_at_kickoff() -> void:
	var m := ReefballFixture.begun()
	assert_eq(_actions(m), ["rise:", "pass:e_mate", "pass:e_keep"] as Array[String], "no dive at the weep, no loft")
	var rise := m.preview(ReefballMatch.RISE)
	# contesters w_carry and w_mate (band 3): 0.8 + 0.04 * 0 - 0.1
	assert_between(rise["odds"], 0.7 - EPS, 0.7 + EPS)
	assert_eq(rise["fail_to"], &"w_carry", "best strip, ties by order")
	assert_eq(rise["strokes"], 2)
	assert_eq(rise["breath"], 2)
	var long := m.preview(ReefballMatch.PASS, &"e_keep")
	assert_between(long["odds"], 0.72 - EPS, 0.72 + EPS, "open three-band pass")
	assert_eq(long["fail_to"], &"w_keep", "nearest opponent to the receiver's band")


func test_illegal_actions_are_refused_without_a_roll() -> void:
	var m := ReefballFixture.begun()
	var state := m.rng.state
	assert_false(m.perform(ReefballMatch.DIVE)["ok"], "at the weep")
	assert_false(m.perform(ReefballMatch.LOFT)["ok"], "too deep")
	assert_false(m.perform(ReefballMatch.PASS, &"w_mate")["ok"], "an opponent")
	assert_false(m.perform(ReefballMatch.PASS, &"e_carry")["ok"], "yourself")
	assert_false(m.perform(&"kick")["ok"], "unknown action")
	m.diver(&"e_mate").depth = 0
	assert_false(m.perform(ReefballMatch.PASS, &"e_mate")["ok"], "nobody receives at the ring")
	assert_eq(m.rng.state, state, "no roll drawn")
	assert_eq(m.strokes_left, 10)


## M3-RBL-201: every action not on the menu is listed with why, and only those.
func test_refused_actions_say_why() -> void:
	var m := ReefballFixture.begun()
	m.diver(&"e_mate").depth = 0
	var got: Array[String] = []
	for r in m.refused_actions():
		got.append("%s:%s:%s" % [r["action"], r["target"], r["reason_key"]])
	var want: Array[String] = [
		"dive::RBL_REFUSE_DIVE_BED", "pass:e_mate:RBL_REFUSE_PASS_RING", "loft::RBL_REFUSE_LOFT_DEEP"
	]
	assert_eq(got, want, "at the weep, a mate at the ring, too deep to loft")
	_clear_west(m)
	m.holder.depth = 1
	m.fetched = false
	var reasons: Array[String] = []
	for r in m.refused_actions():
		reasons.append(str(r["reason_key"]))
	assert_true(reasons.has("RBL_REFUSE_RISE_UNFETCHED"), "no rise into the ring unfetched")
	assert_true(reasons.has("RBL_REFUSE_LOFT_UNFETCHED"), "no loft unfetched")
	for r in m.refused_actions():
		assert_true(m.preview(r["action"], r["target"]).is_empty(), "a refused action has no preview")
	for o in m.legal_actions():
		for r in m.refused_actions():
			assert_false(o["action"] == r["action"] and o["target"] == r["target"], "never both")
	m.finished = true
	assert_true(m.refused_actions().is_empty(), "nothing once the match is over")


## M3-RBL-201: who an option is up against, and whether a success fetches the float.
func test_preview_names_who_presses_and_whether_it_fetches() -> void:
	var m := ReefballFixture.begun()
	var rise := m.preview(ReefballMatch.RISE)
	assert_eq(rise["against"], [&"w_carry", &"w_mate"] as Array[StringName], "the rise's contesters")
	assert_false(rise["fetches"], "a rise never fetches")
	var dive_m := ReefballFixture.begun()
	_clear_west(dive_m)
	dive_m.holder.depth = 2
	dive_m.fetched = false
	var dive := dive_m.preview(ReefballMatch.DIVE)
	assert_eq(dive["against"], [] as Array[StringName], "a dive is up against nobody")
	assert_true(dive["fetches"], "down to fetch_depth: fetched on a success")
	var p := m.preview(ReefballMatch.PASS, &"e_mate")
	assert_eq(
		p["against"],
		m.opponents_at(m.holder.side, m.diver(&"e_mate").depth).map(func(d: ReefballDiver) -> StringName: return d.id)
	)
	assert_false(p["fetches"], "the float is already fetched")
	m.holder.depth = 2
	_place(m, {&"w_keep": 0, &"w_carry": 2, &"w_mate": 4})
	var loft := m.preview(ReefballMatch.LOFT)
	assert_eq(loft["against"], [&"w_keep", &"w_carry"] as Array[StringName], "wardens, then pressers")
	assert_false(loft["fetches"])


func test_unfetched_float_cannot_score() -> void:
	var m := ReefballFixture.begun()
	_clear_west(m)
	m.holder.depth = 1
	m.fetched = false
	assert_true(m.preview(ReefballMatch.RISE).is_empty(), "no rise into the ring")
	assert_true(m.preview(ReefballMatch.LOFT).is_empty(), "no loft")
	m.fetched = true
	assert_true(m.preview(ReefballMatch.RISE)["scores"])
	assert_false(m.preview(ReefballMatch.LOFT).is_empty())


func test_preview_odds_are_the_roll_odds() -> void:
	for s in range(1, 41):
		var m := ReefballFixture.begun(s)
		var p := m.preview(ReefballMatch.RISE)
		var r := m.perform(ReefballMatch.RISE)
		assert_eq(r["odds"], p["odds"])
		assert_eq(r["success"], float(r["roll"]) < float(p["odds"]), "seed %d" % s)
		if r["success"]:
			assert_eq(m.holder.id, &"e_carry")
			assert_eq(m.holder.depth, 3)
		else:
			assert_eq(m.holder.id, p["fail_to"], "the previewed taker gets the float")


func test_rise_into_the_ring_scores_and_kicks_off_for_the_other_side() -> void:
	var m := ReefballFixture.begun()
	_clear_west(m)
	m.holder.depth = 1
	var scored: Array = []
	m.float_scored.connect(func(side: int, score: Array) -> void: scored.append([side, score]))
	var r := m.perform(ReefballMatch.RISE)
	assert_true(r["success"] and r["scored"])
	assert_eq(m.score, [1, 0] as Array[int])
	assert_eq(scored, [[0, [1, 0]]])
	assert_eq(m.holder.id, &"w_carry", "west's kickoff diver")
	assert_eq(m.holder.depth, m.bed())
	assert_false(m.is_player_contact())


func test_dive_and_deep_pass_fetch_the_float() -> void:
	var m := ReefballFixture.begun(1, ReefballFixture.still())
	_clear_west(m)
	m.holder.depth = 1
	m.fetched = false
	m.diver(&"e_mate").depth = 2
	assert_eq(m.preview(ReefballMatch.DIVE)["odds"], 1.0)
	m.perform(ReefballMatch.DIVE)
	assert_false(m.fetched, "band 2 is above fetch_depth")
	m.diver(&"e_mate").depth = 3
	m.perform(ReefballMatch.PASS, &"e_mate")
	assert_eq(m.holder.id, &"e_mate")
	assert_true(m.fetched, "received at fetch_depth")
	m.fetched = false
	m.perform(ReefballMatch.DIVE)
	assert_true(m.fetched, "dived to the weep")


func test_failed_loft_is_caught_at_the_ring_and_sunk() -> void:
	var raw := ReefballFixture.tables()
	raw["rules"]["odds_max"] = 0.0
	raw["rules"]["odds_min"] = 0.0
	var m := ReefballFixture.begun(3, raw)
	_place(m, {&"e_carry": 1, &"w_carry": 4, &"w_mate": 4, &"w_keep": 0})
	var r := m.perform(ReefballMatch.LOFT)
	assert_false(r["success"], "odds clamped to 0")
	assert_eq(m.holder.id, &"w_keep")
	assert_eq(m.holder.depth, 1, "nobody holds the float at the ring")
	assert_false(m.fetched, "west must fetch it before it can score")


func test_loft_without_a_warden_goes_to_a_presser_then_the_nearest() -> void:
	var m := ReefballFixture.begun()
	_place(m, {&"e_carry": 2, &"w_carry": 2, &"w_mate": 4, &"w_keep": 4})
	assert_eq(m.preview(ReefballMatch.LOFT)["fail_to"], &"w_carry")
	_place(m, {&"w_carry": 3})
	assert_eq(m.preview(ReefballMatch.LOFT)["fail_to"], &"w_carry", "nearest the ring")


func test_breath_costs_drain_and_recover() -> void:
	var m := ReefballFixture.begun()
	_clear_west(m)
	m.holder.depth = 2
	m.diver(&"w_keep").depth = 0
	m.diver(&"w_keep").breath = 5
	m.perform(ReefballMatch.RISE)
	assert_eq(m.diver(&"e_carry").breath, 12 - 2 - 1, "rise cost, then the depth drain")
	assert_eq(m.diver(&"e_mate").breath, 11, "drain only")
	assert_eq(m.diver(&"w_keep").breath, 8, "the ring gives breath back")
	m.diver(&"w_keep").breath = 11
	m.perform(ReefballMatch.PASS, &"e_mate")
	assert_eq(m.diver(&"w_keep").breath, 12, "capped at max")


func test_winded_divers_rest_at_the_ring_and_come_back() -> void:
	var m := ReefballFixture.begun()
	_clear_west(m)
	m.holder.depth = 2
	var mate := m.diver(&"e_mate")
	mate.breath = 4
	m.perform(ReefballMatch.RISE)
	assert_true(mate.resting, "drained to winded_at")
	assert_eq(mate.depth, 2, "swims one band toward the ring")
	mate.depth = 0
	mate.breath = 8
	m.perform(ReefballMatch.PASS, &"e_keep")
	assert_eq(mate.breath, 11)
	assert_false(mate.resting, "11 of 12 is past rested_pct")


func test_swimming_follows_roles_and_speed() -> void:
	var m := ReefballFixture.begun()
	m.diver(&"w_keep").stats["stroke"] = 14
	m.diver(&"w_mate").stats["stroke"] = 14
	_place(m, {&"w_carry": 4, &"w_mate": 4, &"w_keep": 3, &"e_mate": 4})
	m.holder.depth = 2
	m.perform(ReefballMatch.DIVE)
	# east holds at band 3: chasers attack one band above; west chasers defend its band
	assert_eq(m.diver(&"e_mate").depth, 3, "toward band 2, one band a contact")
	assert_eq(m.diver(&"w_carry").depth, 3)
	assert_eq(m.diver(&"w_mate").depth, 3, "a fast stroke stops on its band")
	assert_eq(m.diver(&"w_keep").depth, 1, "a fast stroke swims two bands toward the ring")


func test_attackers_never_wait_at_the_ring() -> void:
	var m := ReefballFixture.begun()
	_clear_west(m)
	m.holder.depth = 1
	m.diver(&"e_mate").depth = 1
	m.perform(ReefballMatch.PASS, &"e_mate")
	assert_eq(m.diver(&"e_carry").depth, 1, "chaser attack band is holder - 1 = 0, clamped to 1")


func test_divers_moved_reports_moves() -> void:
	var m := ReefballFixture.begun()
	var moves: Array = []
	m.divers_moved.connect(func(ms: Array) -> void: moves.append_array(ms))
	_clear_west(m)
	m.holder.depth = 2
	m.perform(ReefballMatch.PASS, &"e_keep")
	assert_true(moves.has({"id": &"e_carry", "from": 2, "to": 1}), str(moves))


func test_clock_ends_the_match() -> void:
	var m := ReefballFixture.begun()
	var finished: Array = []
	m.match_finished.connect(func(o: StringName, s: Array) -> void: finished.append([o, s]))
	m.score = [1, 0]
	m.strokes_left = 1
	_clear_west(m)
	var r := m.perform(ReefballMatch.PASS, &"e_mate")
	assert_true(m.finished)
	assert_eq(m.outcome, ReefballMatch.WIN)
	assert_eq(r["strokes_left"], 0)
	assert_eq(finished, [[ReefballMatch.WIN, [1, 0]]])
	assert_true(m.legal_actions().is_empty())
	assert_false(m.perform(ReefballMatch.RISE)["ok"])
	assert_false(m.is_player_contact())


func test_tie_goes_to_overtime_then_a_draw() -> void:
	var raw := ReefballFixture.tables()
	raw["rules"]["clock"]["overtime_strokes"] = 1
	var m := ReefballFixture.begun(1, raw)
	_clear_west(m)
	m.strokes_left = 1
	m.perform(ReefballMatch.PASS, &"e_mate")
	assert_false(m.finished)
	assert_true(m.in_overtime)
	assert_eq(m.overtime_period, 1)
	assert_eq(m.strokes_left, 1)
	assert_true(m.perform(ReefballMatch.DIVE)["success"], "a dive cannot score")
	assert_true(m.finished, "overtime_periods is 1")
	assert_eq(m.outcome, ReefballMatch.DRAW)


func test_a_score_in_overtime_wins_at_once() -> void:
	var m := ReefballFixture.begun()
	m.in_overtime = true
	m.overtime_period = 1
	m.strokes_left = 2
	_clear_west(m)
	m.holder.depth = 1
	m.perform(ReefballMatch.RISE)
	assert_true(m.finished)
	assert_eq(m.outcome, ReefballMatch.WIN)


func test_loss_from_the_player_side() -> void:
	var raw := ReefballFixture.tables()
	raw["matches"][0]["player_side"] = 1
	var m := ReefballFixture.begun(1, raw)
	_clear_west(m)
	m.holder.depth = 1
	m.strokes_left = 2
	m.perform(ReefballMatch.RISE)
	assert_eq(m.outcome, ReefballMatch.LOSS, "east scored; the player is west")


func test_signal_order() -> void:
	var m := ReefballFixture.begun()
	var log: Array[String] = []
	m.action_resolved.connect(func(_r: Dictionary) -> void: log.append("resolved"))
	m.float_scored.connect(func(_s: int, _sc: Array) -> void: log.append("scored"))
	m.divers_moved.connect(func(_m: Array) -> void: log.append("moved"))
	m.contact_started.connect(func(_h: StringName, _s: int) -> void: log.append("contact"))
	m.match_finished.connect(func(_o: StringName, _s: Array) -> void: log.append("finished"))
	_clear_west(m)
	m.holder.depth = 1
	m.perform(ReefballMatch.RISE)
	assert_eq(log, ["resolved", "scored", "moved", "contact"] as Array[String])
	log.clear()
	m.strokes_left = 1
	m.score = [2, 0]
	m.perform(ReefballMatch.PASS, &"w_mate")
	assert_eq(log, ["resolved", "moved", "finished"] as Array[String])


func test_same_seed_same_match() -> void:
	var a := _play_out(77)
	var b := _play_out(77)
	assert_eq(a, b)
	assert_true(a["contacts"] > 0)


func test_snapshot_shape() -> void:
	var snap := ReefballFixture.begun().snapshot()
	for k in ["sides", "score", "strokes_left", "holder", "fetched", "divers", "outcome", "overtime_period"]:
		assert_true(snap.has(k), k)
	assert_eq((snap["divers"] as Array).size(), 6)
	assert_eq(snap["divers"][0]["max_breath"], 12)


func test_ai_contact_with_no_action_is_refused() -> void:
	var m := ReefballFixture.begun()
	m.finished = true
	assert_false(m.play_ai_contact()["ok"])


func _play_out(seed_value: int) -> Dictionary:
	var m := ReefballFixture.begun(seed_value)
	while not m.finished:
		m.play_ai_contact()
	return m.snapshot()


func test_a_match_gated_on_a_key_item_opens_only_while_the_party_holds_it() -> void:
	# ADR 0040: the Oruvel Float is a key item; its effect is a gate (Oruvel's Act III league match).
	var gated := {"id": "league_oruvel", "requires_item": "oruvel_float"}
	var held: Array[StringName] = []
	var holds := func(item: StringName) -> bool: return held.has(item)
	assert_false(ReefballMatch.is_open(gated, holds), "no Float, no match")
	held.append(&"oruvel_float")
	assert_true(ReefballMatch.is_open(gated, holds), "the Float opens it")
	assert_true(ReefballMatch.is_open({"id": "tidecup_opening"}, holds), "an ungated match is always open")
