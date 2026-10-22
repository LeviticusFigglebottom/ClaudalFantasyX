extends TestCase
## TurnTimeline.build_slots: the pure layout behind the turn-order HUD (M1-UI-01).

var engine: BattleEngine


func before_each() -> void:
	engine = BattleEngine.new()
	var active: Array[StringName] = [&"rhen", &"asha"]
	var reserve: Array[StringName] = [&"toma", &"ysolde"]
	engine.setup(BattleDB.load_default(), active, reserve, &"sandbox_reef", 20261022)
	engine.begin()
	var guard := 0
	while not engine.is_party_turn() and guard < 20:
		engine.run_enemy_turn()
		guard += 1


func test_base_shows_sixteen_turns_with_current_first() -> void:
	var slots := TurnTimeline.build_slots(engine.current.id, engine.preview(), [], {}, CtbTimeline.PREVIEW_LENGTH)
	assert_eq(slots.size(), CtbTimeline.PREVIEW_LENGTH)
	assert_eq(slots[0]["id"], engine.current.id)
	assert_true(slots[0]["is_current"])
	for s in slots:
		assert_eq(int(s["moved"]), 0)
		assert_false(bool(s["ghost"]))


func test_preview_keeps_sixteen_slots_and_marks_the_ghost() -> void:
	var foe := engine.living_foes_of(engine.current)[0]
	var preview := engine.preview(&"attack", foe, CtbTimeline.PREVIEW_LENGTH - 1)
	var slots := TurnTimeline.build_slots(engine.current.id, engine.preview(), preview, {}, CtbTimeline.PREVIEW_LENGTH)
	assert_eq(slots.size(), CtbTimeline.PREVIEW_LENGTH)
	assert_eq(slots[0]["id"], engine.current.id, "slot 0 is still the fighter acting now")
	var ghosts := slots.filter(func(s: Dictionary) -> bool: return s["ghost"])
	assert_eq(ghosts.size(), 1)
	assert_eq(ghosts[0]["id"], engine.current.id)
	var keys: Dictionary = {}
	for s in slots:
		assert_false(keys.has(s["key"]), "keys are unique: %s" % s["key"])
		keys[s["key"]] = true


func test_rank_three_attack_changes_nothing() -> void:
	# The base prediction already assumes rank-3 actions, so Attack previews the same order.
	var foe := engine.living_foes_of(engine.current)[0]
	var preview := engine.preview(&"attack", foe, CtbTimeline.PREVIEW_LENGTH - 1)
	var base := engine.preview()
	var slots := TurnTimeline.build_slots(engine.current.id, base, preview, {}, CtbTimeline.PREVIEW_LENGTH)
	for i in slots.size():
		assert_eq(slots[i]["id"], base[i].combatant_id)
		assert_eq(int(slots[i]["moved"]), 0)


func test_slower_skill_moves_the_ghost_down() -> void:
	_to_turn_of(&"rhen")
	var foe := engine.living_foes_of(engine.current)[0]
	var base := engine.preview()
	var fast := TurnTimeline.build_slots(
		engine.current.id, base, engine.preview(&"quick_hit", foe, CtbTimeline.PREVIEW_LENGTH - 1), {}, 16
	)
	var slow := TurnTimeline.build_slots(
		engine.current.id, base, engine.preview(&"undertow_cut", foe, CtbTimeline.PREVIEW_LENGTH - 1), {}, 16
	)
	var g_fast := _ghost(fast)
	var g_slow := _ghost(slow)
	assert_true(int(g_fast["slot"]) < int(g_slow["slot"]), "rank 2 acts again sooner than rank 4")
	assert_true(int(g_fast["moved"]) <= 0, "Quick Hit never moves Rhen's next turn later")
	assert_true(int(g_slow["moved"]) >= 0, "Undertow Cut never moves it earlier")
	assert_ne(int(g_fast["moved"]), int(g_slow["moved"]), "and the two previews differ")
	assert_eq(g_fast["key"], g_slow["key"], "the same future turn keeps its key")


func test_delay_target_moves_down() -> void:
	_to_turn_of(&"rhen")
	var foe := engine.living_foes_of(engine.current)[0]
	var base := engine.preview()
	var prev := engine.preview(&"undertow_cut", foe, CtbTimeline.PREVIEW_LENGTH - 1)
	var slots := TurnTimeline.build_slots(engine.current.id, base, prev, {}, 16)
	var first_foe_turn := slots.filter(func(s: Dictionary) -> bool: return s["id"] == foe.id)[0] as Dictionary
	assert_eq(int(first_foe_turn["moved"]), 1, "a delayed foe's next turn slides down")


func test_affected_filter_hides_incidental_arrows() -> void:
	_to_turn_of(&"rhen")
	var foe := engine.living_foes_of(engine.current)[0]
	var prev := engine.preview(&"undertow_cut", foe, CtbTimeline.PREVIEW_LENGTH - 1)
	var affected: Array[StringName] = [engine.current.id, foe.id]
	var slots := TurnTimeline.build_slots(engine.current.id, engine.preview(), prev, {}, 16, affected)
	for s in slots:
		if not affected.has(s["id"]):
			assert_eq(int(s["moved"]), 0, "%s only slides; no arrow" % s["key"])


func test_offsets_keep_keys_stable_across_a_turn() -> void:
	var before := TurnTimeline.build_slots(engine.current.id, engine.preview(), [], {}, 16)
	var actor := engine.current
	var second_key: String = before[1]["key"]
	engine.perform(&"attack", engine.living_foes_of(actor).slice(0, 1))
	var offsets := {actor.id: 1}
	var after := TurnTimeline.build_slots(
		engine.current.id if engine.current else &"", engine.preview(), [], offsets, 16
	)
	assert_eq(after[0]["key"], second_key, "the next turn slides into slot 0 under the same key")


func test_skipped_turns_are_flagged() -> void:
	var foe := engine.living_foes_of(engine.current)[0]
	foe.add_status(&"stop", 2)
	var slots := TurnTimeline.build_slots(engine.current.id, engine.preview(), [], {}, 16)
	var skipped := slots.filter(func(s: Dictionary) -> bool: return s["id"] == foe.id and s["skipped"])
	assert_eq(skipped.size(), 2, "Stop for 2 turns marks exactly two of that foe's turns")


func _ghost(slots: Array[Dictionary]) -> Dictionary:
	for s in slots:
		if s["ghost"]:
			return s
	return {}


func _to_turn_of(cid: StringName) -> void:
	var guard := 0
	while engine.current.id != cid and guard < 20:
		guard += 1
		if engine.is_party_turn():
			engine.perform(&"attack", engine.living_foes_of(engine.current).slice(0, 1))
		else:
			engine.run_enemy_turn()
