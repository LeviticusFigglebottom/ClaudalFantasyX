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


func test_drain_heal() -> void:
	assert_eq(Formulas.drain_heal(152, 50), 76)
	assert_eq(Formulas.drain_heal(7, 50), 3, "3.5 floors")
	assert_eq(Formulas.drain_heal(0, 50), 0)
	assert_eq(Formulas.drain_heal(-40, 50), 0, "an absorbed hit drains nothing")


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


func test_revive_hp() -> void:
	assert_eq(Formulas.revive_hp(420, 25), 105)
	assert_eq(Formulas.revive_hp(301, 25), 75, "75.25 floors")
	assert_eq(Formulas.revive_hp(3, 25), 1, "never below 1")


func test_item_damage_is_fixed() -> void:
	assert_eq(Formulas.item_damage(150, &"normal"), 150)
	assert_eq(Formulas.item_damage(150, &"weak"), 225)
	assert_eq(Formulas.item_damage(151, &"resist"), 75, "75.5 truncates")
	assert_eq(Formulas.item_damage(150, &"immune"), 0)
	assert_eq(Formulas.item_damage(150, &"absorb"), -150, "absorb heals")
	assert_eq(Formulas.item_damage(20000, &"normal"), Formulas.DAMAGE_CAP)
	assert_eq(Formulas.item_damage(20000, &"absorb"), -Formulas.DAMAGE_CAP)


func test_affinity_order_for_attack_elements() -> void:
	assert_true(Formulas.affinity_hurts_more(&"weak", &"normal"))
	assert_true(Formulas.affinity_hurts_more(&"normal", &"resist"))
	assert_true(Formulas.affinity_hurts_more(&"resist", &"immune"))
	assert_true(Formulas.affinity_hurts_more(&"immune", &"absorb"))
	assert_false(Formulas.affinity_hurts_more(&"normal", &"normal"), "ties are not 'more'")


func test_delay_push_diminishes_and_respects_immunity() -> void:
	assert_eq(Formulas.delay_push(10, 2, 0), 200, "first delay: base 100 x 2 ranks")
	assert_eq(Formulas.delay_push(10, 2, 1), 100, "second before the target acts: halved")
	assert_eq(Formulas.delay_push(10, 2, 2), 50)
	assert_eq(Formulas.delay_push(10, 1, 3), 12, "100 / 8 = 12.5 truncates")
	assert_eq(Formulas.delay_push(10, 2, 99), 200 / 65536, "capped at DELAY_STACK_MAX_STEPS halvings")
	assert_eq(Formulas.delay_push(10, 2, 0, true), 0, "delay-immune")
	assert_eq(Formulas.delay_push(10, 0, 0), 0)


func test_swell_gain_from_an_hp_share() -> void:
	assert_eq(Formulas.swell_gain(95, 420, 120), 27, "Ballast: 95 of 420 HP lost at rate 120 (27.1 floors)")
	assert_eq(Formulas.swell_gain(152, 380, 50), 20, "Wake: 152 dealt to a 380 HP foe at rate 50")
	assert_eq(Formulas.swell_gain(95, 300, 60), 19, "Tether: an ally loses 95 of 300 at rate 60")
	assert_eq(Formulas.swell_gain(1, 420, 120), 1, "any positive amount gives at least 1")
	assert_eq(Formulas.swell_gain(0, 420, 120), 0, "no HP moved, no gain")
	assert_eq(Formulas.swell_gain(-50, 420, 120), 0, "a heal is not a gain")
	assert_eq(Formulas.swell_gain(95, 420, 0), 0, "rate 0")
	assert_eq(Formulas.swell_gain(9999, 10, 120), Formulas.SWELL_MAX, "one share fills at most the gauge")
	assert_eq(Formulas.swell_gain(5, 0, 10), 50, "a 0 max HP counts as 1")


func test_swell_fill_clamps_to_the_gauge() -> void:
	assert_eq(Formulas.swell_fill(40, 27), 67)
	assert_eq(Formulas.swell_fill(90, 27), Formulas.SWELL_MAX)
	assert_eq(Formulas.swell_fill(10, -20), 0)


func test_swell_power_scales_with_the_input_bonus() -> void:
	assert_eq(Formulas.swell_power(12, 0), 12, "a missed input keeps the base power")
	assert_eq(Formulas.swell_power(12, 90), 22, "three perfect beats: 12 x 190 / 100 = 22.8 floors")
	assert_eq(Formulas.swell_power(12, 45), 17, "perfect, good, miss: 17.4 floors")
	assert_eq(Formulas.swell_power(12, -10), 12, "a negative bonus counts as 0")


## formulas.md § Swell, "Their techniques" (M2-NIT-03): every input earns +45% at good and +90%
## played perfectly, so each technique's row power maps to the table's two columns.
func test_technique_powers_at_good_and_perfect() -> void:
	var db := BattleDB.load_default()
	var table := {
		&"shallows_verse": [4, 5, 7],
		&"return_tide": [14, 20, 26],
		&"written_light": [10, 14, 19],
		&"long_hold": [14, 20, 26],
		&"three_reel_charge": [9, 13, 17],
	}
	for tid: StringName in table:
		var want: Array = table[tid]
		assert_eq(int(db.skill(tid).get("power", -1)), want[0], "%s row power" % tid)
		assert_eq(Formulas.swell_power(want[0], 45), want[1], "%s played at good" % tid)
		assert_eq(Formulas.swell_power(want[0], 90), want[2], "%s played perfectly" % tid)


## M2-CMB-02: the Verse reaches every other active ally, never the singer (formulas.md § Swell).
func test_shallows_verse_is_a_song_for_the_others() -> void:
	var db := BattleDB.load_default()
	assert_eq(str(db.skill(&"shallows_verse").get("target", "")), "all_other_allies")
	assert_eq(str(db.skill(&"chorus_mend").get("target", "")), "all_allies", "the paid heal still takes her")


## The Verse against Chorus Mend, from Asha (magic 18, level 5) at variance 100: below a Chorus Mend
## at miss and good, above it only when chanted perfectly (formulas.md § Swell, M2-NIT-03).
func test_shallows_verse_beats_chorus_mend_only_when_perfect() -> void:
	var chorus := Formulas.heal_amount(6, 18, 5, 100, false)
	assert_eq(chorus, 138)
	assert_eq(Formulas.heal_amount(4, 18, 5, 100, false), 92, "missed")
	assert_eq(Formulas.heal_amount(Formulas.swell_power(4, 45), 18, 5, 100, false), 115, "good")
	assert_eq(Formulas.heal_amount(Formulas.swell_power(4, 90), 18, 5, 100, false), 161, "perfect")


## M2-CMB-04: a Vowbound's stats from its caller (formulas.md § Vowbound, Ilun from Asha at level 5).
func test_vowbound_stat_grows_from_the_caller() -> void:
	assert_eq(Formulas.vowbound_stat(60, 300, 100), 360, "Ilun's HP")
	assert_eq(Formulas.vowbound_stat(4, 6, 50), 7, "STR: 4 + floor(6 x 50 / 100)")
	assert_eq(Formulas.vowbound_stat(4, 14, 50), 11, "AGI")
	assert_eq(Formulas.vowbound_stat(2, 9, 50), 6, "floored: 2 + floor(4.5)")
	assert_eq(Formulas.vowbound_stat(14, 6, 0), 14, "a 0% scale keeps the base")
	assert_eq(Formulas.vowbound_stat(-5, -9, -50), 0, "negative inputs count as 0")


func test_opening_chances_follow_mean_agility() -> void:
	assert_eq(Formulas.preemptive_chance(15.0, 15.0), Formulas.OPENING_BASE_PCT, "equal agility: the base 8%")
	assert_eq(Formulas.preemptive_chance(18.0, 46.0 / 3.0), 11, "sandbox: 8 + round(2.67) = 11")
	assert_eq(Formulas.ambush_chance(18.0, 46.0 / 3.0), 5, "sandbox: 8 + round(-2.67) = 5")
	assert_eq(Formulas.preemptive_chance(10.5, 10.0), 9, "a half point rounds away from zero")
	assert_eq(Formulas.preemptive_chance(60.0, 0.0), Formulas.OPENING_MAX_PCT)
	assert_eq(Formulas.ambush_chance(60.0, 0.0), Formulas.OPENING_MIN_PCT)


func test_opening_lead_passes_the_favored_sides_latest_tick() -> void:
	assert_eq(Formulas.opening_lead(240), 241)
	assert_eq(Formulas.opening_lead(0), Formulas.OPENING_LEAD_TICKS)
	assert_eq(Formulas.opening_lead(-5), Formulas.OPENING_LEAD_TICKS, "never negative")
