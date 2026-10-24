extends TestCase
## M2-CMB-05 / M2-FP-17: the simulator's Vowbound play (SimPolicy.call_vowbound and vowbound_turn,
## the masher's own Vowbound turn, role_answer's field clear) on the real Drownbell data.

const PARTY: Array[StringName] = [&"rhen", &"asha", &"toma"]
const ILUN := &"ilun"

var engine: BattleEngine


func before_each() -> void:
	engine = BattleEngine.new()
	engine.story_flags = [&"ch03_ilun_bound"] as Array[StringName]
	engine.setup(BattleDB.load_default(), PARTY, [] as Array[StringName], &"drownbell", 9)
	var rows := BattleVowbound.load_config()
	engine.vowbound = BattleVowbound.new(rows, BattleVowbound.bound_by(rows, engine.story_flags))
	engine.begin()
	var bell := engine.enemies[0]
	bell.hp = bell.max_hp * 40 / 100
	BossMechanics.check_phases(engine)


func test_role_answer_still_clears_a_field_with_its_skill_when_it_has_one() -> void:
	var pol := SimPolicyRoleAnswer.new()
	pol.config = {"clear_field_skill": "call_ilun"}
	_turn_of(&"asha")
	assert_true(engine.find(&"asha").skills.has(&"call_ilun"), "the live fallback")
	pol.take_turn(engine)
	assert_false(engine.fields.has(&"flood"), "Call Ilun (the stand-in) cleared it")


func test_field_up_calls_ilun_and_a_full_gauge_unleashes_floodnet() -> void:
	var pol := SimPolicyRoleAnswer.new()
	pol.config = {"call_vowbound": SimPolicy.RULE_FIELD_UP}
	_turn_of(&"asha")
	pol.take_turn(engine)
	assert_true(engine.vowbound.is_out(), "the flood is up: Asha calls Ilun")
	assert_eq(pol.calls_used, 1)
	var ilun := engine.vowbound.summon
	ilun.swell = Formulas.SWELL_MAX
	pol.take_turn(engine)
	assert_false(engine.fields.has(&"flood"), "his finisher cleared the flood")
	assert_eq(pol.swells_used, 1)


func test_a_vowbound_with_nothing_to_hit_waits_and_one_with_no_skills_is_reported_stuck() -> void:
	var pol := SimPolicySmart.new()
	var masher := SimPolicyNaiveSwell.new()
	_turn_of(&"asha")
	assert_true(engine.summon(ILUN))
	var ilun := engine.vowbound.summon
	ilun.skills.clear()  # nothing to use and no escape while he is out: the stuck error is reported
	ilun.swell = 0
	_turn_of(ILUN)
	assert_eq(engine.current, ilun)
	var taken := ilun.turns_taken
	pol.vowbound_turn(engine)
	assert_eq(ilun.turns_taken, taken, "stuck: the basic fallback could not act")
	assert_eq(engine.current, ilun)
	_turn_of(ILUN)
	for e in engine.enemies:
		e.fall()
	var before := engine.current
	pol.vowbound_turn(engine)
	masher.vowbound_turn(engine)
	assert_eq(engine.current, before, "no foes: nothing to do")


func test_dismiss_when_clear_sends_him_home() -> void:
	var pol := SimPolicySmart.new()
	pol.config = {"dismiss_when_clear": true}
	_turn_of(&"asha")
	assert_true(engine.summon(ILUN))
	engine.fields.clear()
	pol.vowbound_turn(engine)
	assert_false(engine.vowbound.is_out(), "the field is down: he goes home")


func _turn_of(cid: StringName) -> void:
	var guard := 0
	while engine.outcome == &"" and engine.current.id != cid and guard < 80:
		guard += 1
		if engine.is_party_turn():
			engine.perform(&"attack", [engine.living_foes_of(engine.current)[0]] as Array[BattleCombatant])
		else:
			engine.run_enemy_turn()
