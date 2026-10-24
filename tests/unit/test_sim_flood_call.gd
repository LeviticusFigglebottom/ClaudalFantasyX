extends TestCase
## M2-FP-17: the Drownbell suite plays the real Vowbound call. The ch03_drownbell loadout binds Ilun
## (the call_ilun stand-in is gone: M2-UI-05's Call row is the only way); the flood_call policy
## (call_vowbound "field_up") calls Ilun only once a field is up and never sends him back.

const REEF := &"sandbox_reef"
const ILUN := &"ilun"

var sim: BattleSim
var _swell_keep: Array[BattleSwell] = []


func before_each() -> void:
	sim = BattleSim.new()


func test_the_drownbell_loadout_binds_ilun() -> void:
	var kit := sim.loadout(&"ch03_drownbell")
	assert_eq(kit["vowbound"], ["ilun"])
	assert_false(sim.db.skills.has(&"call_ilun"), "the stand-in is gone")
	assert_true(&"flood_call" in BattleSim.POLICY_NAMES)
	assert_eq(str(sim.make_policy(&"flood_call").config.get("call_vowbound", "")), "field_up")


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


func test_usable_skills_skips_a_field_clear_with_no_field_up() -> void:
	# A generic rule the stand-in used to exercise (boss_mechanics.gd refusal): a skill that clears a
	# field is not usable while that field is down, and is once it rises.
	var db := BattleDB.load_default()
	db.skills[&"test_clear"] = {
		"id": "test_clear",
		"kind": "magical",
		"power": 1,
		"rank": 3,
		"element": "none",
		"target": "all_foes",
		"mp_cost": 0,
		"magic": true,
		"clears_field": "flood"
	}
	var e := BattleEngine.new()
	e.setup(db, [&"asha"] as Array[StringName], [] as Array[StringName], REEF, 3)
	var asha := e.find(&"asha")
	asha.skills.append(&"test_clear")
	assert_false(SimPolicy.usable_skills(e, asha).has(&"test_clear"), "no field: refused")
	e.fields.append(&"flood")
	assert_true(SimPolicy.usable_skills(e, asha).has(&"test_clear"), "the field is up")


func test_loadout_flags_reach_the_engine() -> void:
	var r := sim.run_one(
		REEF,
		[&"rhen", &"asha"] as Array[StringName],
		[&"toma"] as Array[StringName],
		sim.make_policy(&"naive"),
		3,
		Callable(),
		{"flags": ["ch03_ilun_bound"]}
	)
	assert_true(str(r.get("outcome", "")) != "", "a loadout with story flags plays through")


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
