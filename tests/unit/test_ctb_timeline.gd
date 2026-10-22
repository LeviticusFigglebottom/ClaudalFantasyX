extends TestCase

var tl: CtbTimeline
var fast: BattleCombatant
var slow: BattleCombatant


func before_each() -> void:
	fast = _mk(&"fast", 26, 0)  # base delay 50
	slow = _mk(&"slow", 10, 0)  # base delay 100
	var roster: Array[BattleCombatant] = [slow, fast]
	tl = CtbTimeline.new()
	tl.set_roster(roster)


func test_lowest_time_acts_first() -> void:
	slow.next_time = 10
	fast.next_time = 20
	assert_eq(tl.next_actor(), slow)


func test_ties_break_by_agility_then_roster_order() -> void:
	assert_eq(tl.next_actor(), fast, "equal time: higher agility first")
	var twin := _mk(&"twin", 10, 0)
	var roster: Array[BattleCombatant] = [slow, twin]
	tl.set_roster(roster)
	assert_eq(tl.next_actor(), slow, "equal time and agility: roster order")


func test_dead_combatants_leave_timeline() -> void:
	fast.hp = 0
	assert_eq(tl.next_actor(), slow)
	for e in tl.predict(6):
		assert_eq(e.combatant_id, &"slow")


func test_predict_interleaves_by_speed() -> void:
	# fast acts every 150 at rank 3, slow every 300.
	var ids: Array[StringName] = []
	for e in tl.predict(6):
		ids.append(e.combatant_id)
	assert_eq(ids, [&"fast", &"slow", &"fast", &"fast", &"slow", &"fast"] as Array[StringName])


func test_predict_length() -> void:
	assert_eq(tl.predict().size(), CtbTimeline.PREVIEW_LENGTH)


func test_preview_low_rank_moves_actor_earlier() -> void:
	slow.next_time = 0
	fast.next_time = 100
	var heavy := tl.predict(4, slow, 6)  # slow returns at 0 + 600
	for e in heavy:
		assert_eq(e.combatant_id, &"fast", "rank 6 pushes slow out of the next 4 turns")
	var light := tl.predict(4, slow, 1)  # slow returns at 0 + 100, ties fast at 100
	assert_eq(light[0].combatant_id, &"fast", "tie at 100 goes to higher agility")
	assert_eq(light[1].combatant_id, &"slow")
	assert_eq(light[1].time, 100)
	assert_true(light[1].is_preview, "previewed turn is flagged")
	assert_false(light[0].is_preview)


func test_preview_delay_attack_pushes_target() -> void:
	slow.next_time = 120
	fast.next_time = 0
	var plain := tl.predict(2, fast, 3)
	var delayed := tl.predict(2, fast, 3, slow, 2)
	assert_eq(plain[0].combatant_id, &"slow")
	assert_eq(plain[0].time, 120)
	assert_eq(delayed[0].time, 150, "fast's next turn (0 + 150) now comes first")
	assert_eq(delayed[0].combatant_id, &"fast")


func test_haste_shortens_predicted_gaps() -> void:
	fast.add_status(&"haste", 4)
	var entries := tl.predict(3)
	var fast_times: Array[int] = []
	for e in entries:
		if e.combatant_id == &"fast":
			fast_times.append(e.time)
	assert_true(fast_times.size() >= 2)
	assert_eq(fast_times[1] - fast_times[0], 75)


func test_stopped_turns_are_flagged_skipped() -> void:
	slow.add_status(&"stop", 1)
	var first_slow: TurnEntry = null
	var second_slow: TurnEntry = null
	for e in tl.predict(8):
		if e.combatant_id == &"slow":
			if first_slow == null:
				first_slow = e
			elif second_slow == null:
				second_slow = e
	assert_true(first_slow.skipped)
	assert_false(second_slow.skipped)


static func _mk(cid: StringName, agility: int, t: int) -> BattleCombatant:
	var c := BattleCombatant.new()
	c.id = cid
	c.team = BattleCombatant.TEAM_PARTY
	c.agility = agility
	c.max_hp = 100
	c.hp = 100
	c.next_time = t
	return c
