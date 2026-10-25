extends TestCase
## ReefballAI (M3-RBL-01): option values from previewed odds, the loft floor, the whim roll, and
## the direction of play while the float is unfetched.

const EPS := 0.0001


func _profile(m: ReefballMatch) -> ReefballAI:
	return ReefballAI.new(m.db.ai_profiles[&"test"])


func test_value_of_a_sure_score() -> void:
	var m := ReefballFixture.begun()
	_place_open(m, 1)
	var ai := _profile(m)
	assert_between(ai.value(m, m.preview(ReefballMatch.RISE)), 10.0 - EPS, 10.0 + EPS)
	assert_eq(ai.choose(m)["action"], ReefballMatch.RISE, "a sure score beats everything")


func test_value_of_a_pass() -> void:
	var m := ReefballFixture.begun()
	_place_open(m, 3)
	m.diver(&"e_keep").depth = 1
	m.diver(&"e_keep").breath = 6
	var ai := _profile(m)
	var p := m.preview(ReefballMatch.PASS, &"e_keep")
	var odds: float = p["odds"]
	# advance 2 bands × 2.0, fresh 1.0 × (0.5 - 1.0); miss × turnover_cost 3.0
	var want := odds * (4.0 - 0.5) - (1.0 - odds) * 3.0
	assert_between(ai.value(m, p), want - EPS, want + EPS)


func test_low_odds_loft_is_never_taken() -> void:
	var m := ReefballFixture.begun()
	_place_open(m, 2)
	m.diver(&"w_keep").depth = 0
	m.diver(&"w_keep").stats["ward"] = 20
	m.holder.stats["loft"] = 1
	var ai := _profile(m)
	var loft := m.preview(ReefballMatch.LOFT)
	assert_true(float(loft["odds"]) < 0.3)
	assert_eq(ai.value(m, loft), -INF)
	assert_ne(ai.choose(m)["action"], ReefballMatch.LOFT)


func test_unfetched_float_goes_down() -> void:
	var m := ReefballFixture.begun()
	_place_open(m, 1)
	m.fetched = false
	var ai := _profile(m)
	var dive := ai.value(m, m.preview(ReefballMatch.DIVE))
	assert_between(dive, 2.0 - EPS, 2.0 + EPS, "advance toward the weep")
	m.fetched = true
	assert_between(ai.value(m, m.preview(ReefballMatch.DIVE)), -2.0 - EPS, -2.0 + EPS, "away from the ring")
	m.fetched = false
	m.holder.depth = 2
	assert_between(ai.value(m, m.preview(ReefballMatch.DIVE)), 5.0 - EPS, 5.0 + EPS, "plus fetch_value at band 3")
	assert_between(ai.value(m, m.preview(ReefballMatch.RISE)), -2.0 - EPS, -2.0 + EPS)


func test_whim_rolls_only_when_set() -> void:
	var m := ReefballFixture.begun()
	var state := m.rng.state
	_profile(m).choose(m)
	assert_eq(m.rng.state, state, "whim_pct 0 draws nothing")
	var whimsical := ReefballAI.new({"whim_pct": 100, "score_value": 10.0, "advance_value": 2.0})
	_place_open(m, 1)
	var pick := whimsical.choose(m)
	assert_ne(m.rng.state, state)
	assert_ne(pick["action"], ReefballMatch.RISE, "always the second best")


func test_nothing_to_choose_when_finished() -> void:
	var m := ReefballFixture.begun()
	m.finished = true
	assert_true(_profile(m).choose(m).is_empty())


func _place_open(m: ReefballMatch, depth: int) -> void:
	for id: StringName in [&"w_carry", &"w_mate", &"w_keep"]:
		m.diver(id).depth = 4
	m.holder.depth = depth
