extends TestCase
## ReefballFormulas (M3-RBL-01, docs/kb/design/reefball.md § Odds): each odds formula against a
## hand-computed value with the fixture coefficients.

const EPS := 0.0001

var rules: Dictionary


func before_each() -> void:
	rules = ReefballFixture.tables()["rules"]


func _near(actual: float, expected: float, msg: String = "") -> void:
	assert_between(actual, expected - EPS, expected + EPS, msg)


func _list(ds: Array) -> Array[ReefballDiver]:
	var out: Array[ReefballDiver] = []
	for d: ReefballDiver in ds:
		out.append(d)
	return out


func test_open_rise_is_sure() -> void:
	var c := ReefballFixture.diver(3)
	assert_eq(ReefballFormulas.rise_odds(rules, c, _list([])), 1.0)


func test_contested_rise() -> void:
	var c := ReefballFixture.diver(3, {"stroke": 12, "grip": 14})
	var a := ReefballFixture.diver(3, {"strip": 10}, 1, 1)
	var b := ReefballFixture.diver(2, {"strip": 11}, 1, 2)
	# 0.8 + 0.04 * (13 - 11) - 0.1 * (2 - 1)
	_near(ReefballFormulas.rise_odds(rules, c, _list([a, b])), 0.78)


func test_winded_actor_pays_the_penalty() -> void:
	var c := ReefballFixture.diver(3, {"stroke": 12, "grip": 14})
	var a := ReefballFixture.diver(3, {"strip": 11}, 1, 1)
	_near(ReefballFormulas.rise_odds(rules, c, _list([a])), 0.88)
	c.breath = 3
	assert_true(ReefballFormulas.winded(rules, c))
	_near(ReefballFormulas.rise_odds(rules, c, _list([a])), 0.68, "winded: -0.2")
	c.breath = 4
	assert_false(ReefballFormulas.winded(rules, c))


func test_contested_odds_clamp() -> void:
	var weak := ReefballFixture.diver(3, {"stroke": 1, "grip": 1})
	var strong := ReefballFixture.diver(3, {"stroke": 20, "grip": 20})
	var lo := ReefballFixture.diver(3, {"strip": 1}, 1, 1)
	var hi := ReefballFixture.diver(3, {"strip": 20}, 1, 2)
	_near(ReefballFormulas.rise_odds(rules, weak, _list([hi])), 0.05, "odds_min")
	_near(ReefballFormulas.rise_odds(rules, strong, _list([lo])), 0.95, "odds_max: contested is never sure")


func test_open_short_pass_is_sure() -> void:
	var p := ReefballFixture.diver(3)
	var r := ReefballFixture.diver(2, {}, 0, 1)
	assert_eq(ReefballFormulas.pass_odds(rules, p, r, _list([])), 1.0)


func test_open_long_pass_loses_distance() -> void:
	var p := ReefballFixture.diver(4, {"reach": 14})
	var r := ReefballFixture.diver(1, {"grip": 12}, 0, 1)
	# 0.62 + 0.02 * 13 - 0.07 * (3 - 1)
	_near(ReefballFormulas.pass_odds(rules, p, r, _list([])), 0.74)


func test_marked_pass() -> void:
	var p := ReefballFixture.diver(4, {"reach": 14})
	var r := ReefballFixture.diver(1, {"grip": 12}, 0, 1)
	var m1 := ReefballFixture.diver(1, {"strip": 10}, 1, 2)
	var m2 := ReefballFixture.diver(1, {"strip": 15}, 1, 3)
	# 0.74 - 0.02 * 15 - 0.06 * (2 - 1)
	_near(ReefballFormulas.pass_odds(rules, p, r, _list([m1, m2])), 0.38)
	var near := ReefballFixture.diver(2, {"reach": 14}, 0, 4)
	# 0.62 + 0.26 - 0.02 * 10: a marked pass is never sure, even one band
	_near(ReefballFormulas.pass_odds(rules, near, r, _list([m1])), 0.68)


func test_loft() -> void:
	var c := ReefballFixture.diver(2, {"loft": 14})
	var w := ReefballFixture.diver(0, {"ward": 15}, 1, 1)
	var pr := ReefballFixture.diver(2, {}, 1, 2)
	# 0.4 + 0.03 * 14 - 0.15 * (2 - 1) - 0.06 * 1 - 0.02 * 15
	_near(ReefballFormulas.loft_odds(rules, c, _list([w]), _list([pr])), 0.31)
	c.depth = 1
	# 0.4 + 0.42, no warden and no presser
	_near(ReefballFormulas.loft_odds(rules, c, _list([]), _list([])), 0.82)


func test_best_breaks_ties_by_order() -> void:
	var a := ReefballFixture.diver(1, {"strip": 12}, 1, 5)
	var b := ReefballFixture.diver(1, {"strip": 12}, 1, 2)
	var c := ReefballFixture.diver(1, {"strip": 9}, 1, 0)
	assert_eq(ReefballFormulas.best(_list([a, b, c]), "strip"), b)
	assert_eq(ReefballFormulas.best(_list([c, a]), "strip"), a)
	assert_eq(ReefballFormulas.best(_list([]), "strip"), null)
