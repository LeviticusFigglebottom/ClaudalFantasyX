extends TestCase
## One test per formula in docs/kb/design/formulas.md. Expected values are hand-computed
## there; if a formula changes, update the doc, this file, and formulas.gd together.


func test_base_delay() -> void:
	assert_eq(Formulas.base_delay(10), 100)
	assert_eq(Formulas.base_delay(0), 267)
	assert_eq(Formulas.base_delay(22), 58)
	assert_eq(Formulas.base_delay(255), 7)
	assert_eq(Formulas.base_delay(-5), 267, "negative agility clamps to 0")


func test_action_delay_scales_with_rank_and_speed() -> void:
	assert_eq(Formulas.action_delay(10, 3), 300)
	assert_eq(Formulas.action_delay(10, 2), 200)
	assert_eq(Formulas.action_delay(10, 3, Formulas.HASTE_SPEED_MULT), 150)
	assert_eq(Formulas.action_delay(10, 3, Formulas.SLOW_SPEED_MULT), 600)
	assert_eq(Formulas.action_delay(10, 0), Formulas.MIN_DELAY, "never below MIN_DELAY")
	assert_eq(Formulas.action_delay(0, 3, Formulas.HASTE_SPEED_MULT), 401, "400.5 rounds half away from zero")


func test_initial_ticks() -> void:
	assert_eq(Formulas.initial_ticks(10, 0), 300)
	assert_eq(Formulas.initial_ticks(10, 100), 200)


func test_damage_pipeline() -> void:
	# power 8, strength 16, level 5, defense 10, variance 100: 8 * 21 * 100/110 = 152.72...
	assert_eq(Formulas.damage(8, 16, 5, 10, 100, &"normal", false, false, false), 152)
	assert_eq(Formulas.damage(8, 16, 5, 10, 100, &"normal", true, false, false), 305, "crit x2")
	assert_eq(Formulas.damage(8, 16, 5, 10, 100, &"normal", false, true, false), 76, "barrier x1/2")
	assert_eq(Formulas.damage(8, 16, 5, 10, 100, &"weak", false, false, false), 229)
	assert_eq(Formulas.damage(8, 16, 5, 10, 100, &"resist", false, false, false), 76)
	assert_eq(Formulas.damage(8, 16, 5, 10, 100, &"immune", false, false, false), 0)
	assert_eq(Formulas.damage(8, 16, 5, 10, 100, &"absorb", false, false, false), -152, "absorb heals")


func test_damage_is_exact_not_float() -> void:
	# 7 * 10 * 100/105 * 0.93 = 62 exactly; a float pipeline floors this to 61.
	assert_eq(Formulas.damage(7, 5, 5, 5, 93, &"normal", false, false, false), 62)


func test_damage_variance_bounds() -> void:
	assert_eq(Formulas.damage(10, 10, 0, 0, Formulas.VARIANCE_MIN_PCT, &"normal", false, false, false), 92)
	assert_eq(Formulas.damage(10, 10, 0, 0, Formulas.VARIANCE_MAX_PCT, &"normal", false, false, false), 108)


func test_damage_cap() -> void:
	assert_eq(Formulas.damage(100, 255, 99, 0, 100, &"normal", false, false, false), Formulas.DAMAGE_CAP)
	assert_eq(Formulas.damage(100, 255, 99, 0, 100, &"normal", false, false, true), 35400)
	assert_eq(Formulas.damage(255, 255, 99, 0, 100, &"normal", true, false, true), Formulas.DAMAGE_CAP_BROKEN)
	assert_eq(Formulas.damage(100, 255, 99, 0, 100, &"absorb", false, false, false), -Formulas.DAMAGE_CAP)


func test_heal_amount() -> void:
	assert_eq(Formulas.heal_amount(10, 18, 5, 100, false), 230)
	assert_eq(Formulas.heal_amount(1000, 99, 99, 100, false), Formulas.DAMAGE_CAP)
	assert_eq(Formulas.heal_amount(10, 18, 5, 93, false), 213, "230 * 0.93 = 213.9 floors")


func test_hit_chance() -> void:
	assert_eq(Formulas.hit_chance(95, 14, 14, false), 95)
	assert_eq(Formulas.hit_chance(95, 10, 30, false), 75)
	assert_eq(Formulas.hit_chance(95, 14, 14, true), 19, "darkness x0.2")
	assert_eq(Formulas.hit_chance(0, 0, 50, false), Formulas.HIT_MIN_PCT)
	assert_eq(Formulas.hit_chance(100, 50, 0, false), Formulas.HIT_MAX_PCT)


func test_crit_chance() -> void:
	assert_eq(Formulas.crit_chance(18, 4), 11)
	assert_eq(Formulas.crit_chance(4, 18), 0)
	assert_eq(Formulas.crit_chance(200, 0), Formulas.CRIT_MAX_PCT)


func test_broken_stat() -> void:
	assert_eq(Formulas.broken_stat(17, true), 8)
	assert_eq(Formulas.broken_stat(17, false), 17)


func test_poison_and_regen() -> void:
	assert_eq(Formulas.poison_damage(420), 42)
	assert_eq(Formulas.regen_heal(420), 34)
	assert_eq(Formulas.poison_damage(5), 1)


func test_escape_chance() -> void:
	assert_eq(Formulas.escape_chance(20.0, 10.0), 70)
	assert_eq(Formulas.escape_chance(10.0, 40.0), Formulas.ESCAPE_MIN_PCT)
	assert_eq(Formulas.escape_chance(60.0, 0.0), Formulas.ESCAPE_MAX_PCT)
