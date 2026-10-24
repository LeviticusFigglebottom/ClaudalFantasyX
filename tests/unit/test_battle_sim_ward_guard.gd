extends TestCase
## M3-CMB-01: the simulator's side of the set pieces, on test_battle_set_piece.gd's fixture DB:
## SimWardGuard (cover a grip that comes before the guard's next turn, Provoke a second, Haul a bare
## Climb), the ward_guard policy, the guard_ward config of role_answer and smart, the scripted_escape
## win, the no-foe fallback, and the Vowbound that answers the field that is up.

const SetPiece := preload("res://tests/unit/test_battle_set_piece.gd")
const SEED := 7
const STEPS := 400

var engine: BattleEngine


func before_each() -> void:
	engine = BattleEngine.new()
	engine.story_flags.append(&"hoist")
	engine.setup(
		SetPiece._db(), [&"guard", &"hero", &"liss"] as Array[StringName], [] as Array[StringName], &"stair", SEED
	)
	engine.begin()


func test_a_grip_before_the_guards_next_turn_is_a_threat() -> void:
	_to_turn_of(&"guard")
	var mite := _telegraph(engine.enemies[0])
	var threats := SimWardGuard.threats_before_next_turn(engine, engine.current, engine.ward())
	assert_eq(threats, [mite] as Array[BattleCombatant])
	mite.clear_charge()
	assert_true(SimWardGuard.threats_before_next_turn(engine, engine.current, engine.ward()).is_empty())


func test_the_guard_holds_the_stair_on_a_threat() -> void:
	_to_turn_of(&"guard")
	_telegraph(engine.enemies[0])
	assert_true(SimWardGuard.act(engine))
	assert_eq(engine.ward().covered_by, &"guard")


func test_with_the_stair_held_a_second_threat_is_provoked() -> void:
	_to_turn_of(&"guard")
	_telegraph(engine.enemies[0])
	var second := _telegraph(engine.enemies[1])
	engine.ward().covered_by = &"guard"
	assert_true(SimWardGuard.act(engine))
	assert_true(second.has_status(&"provoke"), "the second grip is drawn onto him")


func test_a_hauled_rope_is_a_threat_once_a_wing_would_dive_it() -> void:
	_to_turn_of(&"guard")
	var mite := engine.enemies[0]
	var entry := TurnEntry.new(mite.id, engine.now + 1, mite.team)
	assert_false(SimWardGuard.threat(engine, mite, entry, engine.ward()), "it pecks a bare rope")
	engine.ward().add_status(&"haste", 2)
	assert_true(SimWardGuard.threat(engine, mite, entry, engine.ward()), "and dives a hauled one")


func test_liss_hauls_a_bare_climb_but_not_in_the_dark() -> void:
	_to_turn_of(&"liss")
	engine.fields.append(&"dark")
	engine.field_rules[&"dark"] = [{"on": "ward", "status": "slow", "duration": 1}]
	assert_false(SimWardGuard.act(engine), "storm_dark's Slow would erase the Haste at once")
	engine.fields.clear()
	engine.field_rules.clear()
	assert_true(SimWardGuard.act(engine))
	assert_true(engine.ward().has_status(&"haste"))


func test_no_guard_before_the_objective_counts() -> void:
	engine = BattleEngine.new()
	engine.setup(SetPiece._db(), [&"guard", &"hero"] as Array[StringName], [] as Array[StringName], &"reach", SEED)
	engine.begin()
	_to_turn_of(&"guard")
	assert_false(BattleSetPiece.objective_running(engine))
	assert_false(SimWardGuard.act(engine), "the Reach's Climb matters only from the Breach")


func test_the_ward_guard_policy_guards_then_mashes() -> void:
	var sim := BattleSim.new(SetPiece._db())
	var p := sim.make_policy(&"ward_guard")
	assert_eq(p.policy_name(), &"ward_guard")
	assert_true(BattleSim.POLICY_NAMES.has(&"ward_guard"))
	_to_turn_of(&"guard")
	_telegraph(engine.enemies[0])
	p.take_turn(engine)
	assert_eq(engine.ward().covered_by, &"guard")
	_to_turn_of(&"hero")
	var foe_hp := engine.enemies[0].hp + engine.enemies[1].hp
	p.take_turn(engine)
	assert_true(engine.enemies[0].hp + engine.enemies[1].hp < foe_hp, "no threat: it mashes Attack")


func test_role_answer_and_smart_guard_the_ward_in_the_shipped_config() -> void:
	var sim := BattleSim.new()
	for name: StringName in [&"role_answer", &"smart"]:
		assert_true(bool(sim.make_policy(name).config.get("guard_ward", false)), "%s guards" % name)
	assert_false(bool(sim.make_policy(&"naive").config.get("guard_ward", false)))
	var p := SimPolicyRoleAnswer.new()
	p.config = {"guard_ward": true}
	_to_turn_of(&"guard")
	_telegraph(engine.enemies[0])
	p.take_turn(engine)
	assert_eq(engine.ward().covered_by, &"guard")


func test_a_scripted_escape_counts_as_a_win() -> void:
	var runs: Array[Dictionary] = [_run("scripted_escape"), _run("victory"), _run("defeat"), _run("timeout")]
	var agg := BattleSim.summarize(runs)
	assert_eq(agg["wins"], 2)
	assert_eq(agg["timeouts"], 1)


func test_the_reach_plays_to_a_scripted_escape_in_the_sim() -> void:
	var sim := BattleSim.new(SetPiece._db())
	sim.swell_quality = &""
	var res := sim.run_one(
		&"reach", [&"guard", &"hero"] as Array[StringName], [] as Array[StringName], sim.make_policy(&"naive"), SEED
	)
	assert_ne(res["outcome"], "timeout", "the untargetable phase never stalls the masher")


func test_with_no_foe_a_called_vowbound_is_sent_back() -> void:
	engine.vowbound = BattleVowbound.new([SetPiece._virel_row()], [&"spirit"] as Array[StringName])
	_to_turn_of(&"hero")
	assert_true(engine.summon(&"spirit"))
	for e in engine.enemies:
		e.apply_damage(e.max_hp)
	assert_true(SimPolicy._lawful_fallback(engine, engine.current))
	assert_false(engine.vowbound.is_out(), "dismissed: it had nothing to strike")


func test_the_vowbound_called_is_the_one_whose_finisher_clears_the_field_up() -> void:
	var rows: Array = [_vowbound("first", "attack"), _vowbound("lamp", "flare")]
	engine.vowbound = BattleVowbound.new(rows, [&"first", &"lamp"] as Array[StringName])
	var ids: Array[StringName] = [&"first", &"lamp"]
	assert_eq(SimPolicy.field_answer(engine, ids), &"first", "no field: the first")
	engine.fields.append(&"dark")
	assert_eq(SimPolicy.field_answer(engine, ids), &"lamp", "Flare Line for the dark")
	assert_eq(engine.vowbound.finisher_of(&"lamp"), &"flare")


# --- helpers -------------------------------------------------------------------------------------


## Makes `mite` telegraph its grip for its next turn, and puts that turn next on the order.
func _telegraph(mite: BattleCombatant) -> BattleCombatant:
	mite.charge_skill = &"grip"
	mite.charge_left = 1
	mite.charge_row = engine.db.skill(&"grip")
	mite.next_time = engine.now + 1
	return mite


static func _run(outcome: String) -> Dictionary:
	return {"outcome": outcome, "turns": 10, "party_ko": 0, "items": 0}


static func _vowbound(vid: String, finisher: String) -> Dictionary:
	var row := SetPiece._virel_row()
	row["id"] = vid
	row["swell"] = {"rate": 100, "technique": finisher}
	return row


func _to_turn_of(cid: StringName) -> void:
	for _i in STEPS:
		if engine.outcome != &"" or engine.current != null and engine.current.id == cid:
			return
		if engine.is_party_turn():
			engine.perform(&"guard", [engine.current] as Array[BattleCombatant])
		else:
			engine.run_enemy_turn()
