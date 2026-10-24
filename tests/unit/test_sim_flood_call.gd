extends TestCase
## M2-FP-17: the Drownbell suite plays the real Vowbound call. The ch03_drownbell loadout binds Ilun
## and retires the call_ilun stand-in ("retire_skills"); the flood_call policy (call_vowbound
## "field_up") calls Ilun only once a field is up and never sends him back.

const REEF := &"sandbox_reef"
const ILUN := &"ilun"

var sim: BattleSim
var _swell_keep: Array[BattleSwell] = []


func before_each() -> void:
	sim = BattleSim.new()


func test_the_drownbell_loadout_binds_ilun_and_retires_the_stand_in() -> void:
	var kit := sim.loadout(&"ch03_drownbell")
	assert_eq(kit["vowbound"], ["ilun"])
	assert_eq(kit["retire_skills"], ["call_ilun"])
	assert_true(&"flood_call" in BattleSim.POLICY_NAMES)
	assert_eq(str(sim.make_policy(&"flood_call").config.get("call_vowbound", "")), "field_up")


func test_retired_skills_leave_the_party() -> void:
	var e := BattleEngine.new()
	e.story_flags = [&"ch03_ilun_bound"] as Array[StringName]
	e.setup(BattleDB.load_default(), [&"rhen", &"asha", &"toma"] as Array[StringName], [], &"drownbell", 1)
	assert_true(e.find(&"asha").skills.has(&"call_ilun"), "the live game keeps the stand-in")
	BattleSim.retire_skills(e, sim.loadout(&"ch03_drownbell"))
	assert_false(e.find(&"asha").skills.has(&"call_ilun"), "the Drownbell suite plays the real call")
	assert_true(e.find(&"asha").skills.has(&"mend"), "and nothing else is taken")


func test_flood_call_waits_for_a_field_then_stays_out() -> void:
	var dry := _engine()
	_attach(dry, sim.make_policy(&"flood_call")).take_turn(dry)
	assert_false(dry.vowbound.is_out(), "no field, no call: it mashes")
	var e := _engine()
	e.fields.append(&"flood")
	var p := _attach(e, sim.make_policy(&"flood_call"))
	p.take_turn(e)
	assert_true(e.vowbound.is_out(), "the flood rises: Ilun is called")
	e.fields.clear()
	p.take_turn(e)
	assert_true(e.vowbound.is_out(), "the field is gone, but flood_call never sends him back")


func _engine() -> BattleEngine:
	var e := BattleEngine.new()
	e.setup(BattleDB.load_default(), [&"rhen", &"asha"] as Array[StringName], [&"toma"] as Array[StringName], REEF, 3)
	e.vowbound = BattleVowbound.new(BattleVowbound.load_config(), [ILUN] as Array[StringName])
	e.begin()
	_turn_of(e, &"asha")
	return e


func _attach(e: BattleEngine, p: SimPolicy) -> SimPolicy:
	var sw := BattleSwell.new(BattleSwell.load_config())
	sw.attach(e)
	_swell_keep.append(sw)
	p.swell = sw
	p.swell_quality = SwellInput.QUALITY_GOOD
	return p


static func _turn_of(e: BattleEngine, cid: StringName) -> void:
	var guard := 0
	while e.outcome == &"" and e.current.id != cid and guard < 50:
		guard += 1
		if e.is_party_turn():
			e.perform(&"attack", [e.living_foes_of(e.current)[0]] as Array[BattleCombatant])
		else:
			e.run_enemy_turn()
