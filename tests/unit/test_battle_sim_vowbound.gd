extends TestCase
## M2-CMB-05: the simulator's Vowbound call rule (balance_targets.md, ADR 0027). A loadout's
## "vowbound" list binds the Vowbound; sim_policies.json "call_vowbound" says when a policy calls
## (naive_swell "at_once", role_answer and smart "on_field"); a called Vowbound unleashes its
## finisher when full (any policy that opens the Swell row) and stays out.

const REEF := &"sandbox_reef"
const ILUN := &"ilun"

var sim: BattleSim
## Swell rules the helpers attach, held for the test: a signal connection does not keep them alive.
var _swell_keep: Array[BattleSwell] = []


func before_each() -> void:
	sim = BattleSim.new()


func test_the_vowbound_loadout_binds_ilun_with_no_gear() -> void:
	var kit := sim.loadout(&"sandbox_vowbound")
	assert_eq(kit["vowbound"], ["ilun"])
	assert_true((kit["gear"] as Dictionary).is_empty())
	assert_eq(str(sim.make_policy(&"naive_swell").config.get("call_vowbound", "")), "at_once")
	assert_eq(str(sim.make_policy(&"role_answer").config.get("call_vowbound", "")), "on_field")
	assert_eq(str(sim.make_policy(&"smart").config.get("call_vowbound", "")), "on_field")
	assert_false(sim.make_policy(&"naive").config.has("call_vowbound"), "the plain masher never calls")


func test_the_masher_calls_ilun_on_ashas_first_turn() -> void:
	var e := _engine()
	var p := _attach(e, sim.make_policy(&"naive_swell"))
	p.take_turn(e)
	assert_true(e.vowbound.is_out(), "naive_swell calls at once")
	assert_eq(e.current, e.vowbound.summon, "and Ilun takes the turn")
	var plain := _engine()
	_attach(plain, sim.make_policy(&"naive")).take_turn(plain)
	assert_false(plain.vowbound.is_out())


func test_role_answer_and_smart_call_only_while_a_field_is_up() -> void:
	for policy: StringName in [&"role_answer", &"smart"]:
		var dry := _engine()
		_attach(dry, sim.make_policy(policy)).take_turn(dry)
		assert_false(dry.vowbound.is_out(), "%s: no field, no call" % policy)
		var flood := _engine()
		flood.fields.append(&"flood")
		_attach(flood, sim.make_policy(policy)).take_turn(flood)
		assert_true(flood.vowbound.is_out(), "%s: the flood rises, Ilun is called" % policy)


func test_the_role_answer_sends_ilun_back_once_the_flood_is_gone() -> void:
	var e := _engine()
	e.fields.append(&"flood")
	var p := _attach(e, sim.make_policy(&"role_answer"))
	p.take_turn(e)
	var ilun := e.vowbound.summon
	assert_eq(e.current, ilun)
	p.take_turn(e)
	assert_true(e.vowbound.is_out(), "he stays while the flood holds")
	_turn_of(e, ILUN)
	e.fields.clear()
	p.take_turn(e)
	assert_false(e.vowbound.is_out(), "dismissed on his first turn after the flood")


func test_a_full_vowbound_unleashes_its_finisher_first_and_stays_out() -> void:
	var e := _engine()
	var p := _attach(e, sim.make_policy(&"naive_swell"))
	p.take_turn(e)
	var ilun := e.vowbound.summon
	ilun.swell = Formulas.SWELL_MAX
	ilun.add_status(&"silence", 2)
	assert_false(p.unleash_vowbound(e), "Floodnet is magic: Silence holds it back")
	assert_eq(ilun.swell, Formulas.SWELL_MAX)
	ilun.statuses.erase(&"silence")
	var foes := e.living_foes_of(ilun)
	var hp: Array[int] = []
	for f in foes:
		f.max_hp = 9999  # Floodnet must not end the fight
		f.hp = f.max_hp
		hp.append(f.hp)
	p.take_turn(e)
	assert_eq(ilun.swell, 0, "Floodnet spent the gauge")
	assert_eq(p.swells_used, 1)
	for i in foes.size():
		assert_true(foes[i].hp < hp[i], "Floodnet hits every foe")
	assert_true(e.vowbound.is_out(), "no dismissal")
	var naive := sim.make_policy(&"naive")
	assert_false(naive.unleash_vowbound(e), "naive never opens the Swell row")


func test_no_vowbound_bound_means_no_call() -> void:
	var e := BattleEngine.new()
	e.setup(BattleDB.load_default(), [&"rhen", &"asha"] as Array[StringName], [&"toma"] as Array[StringName], REEF, 3)
	e.begin()
	_turn_of(e, &"asha")
	var p := _attach(e, sim.make_policy(&"naive_swell"))
	assert_false(p.call_vowbound(e))
	assert_false(p.unleash_vowbound(e))


func test_a_seeded_vowbound_suite_replays_and_calls_every_time() -> void:
	var kit := sim.loadout(&"sandbox_vowbound")
	sim.swell_quality = SwellInput.QUALITY_GOOD
	var active: Array[StringName] = [&"rhen", &"asha"]
	var reserve: Array[StringName] = [&"toma"]
	var a := sim.run_many(REEF, active, reserve, &"naive_swell", 20, 1, Callable(), kit)
	var b := sim.run_many(REEF, active, reserve, &"naive_swell", 20, 1, Callable(), kit)
	assert_eq(a, b, "deterministic")
	assert_eq(int(a["timeouts"]), 0)
	var plain := sim.run_many(REEF, active, reserve, &"naive", 20, 1, Callable(), kit)
	assert_ne(a, plain, "the call changes the fight")


# --- helpers ---------------------------------------------------------------------------------


## The sandbox with Ilun bound (Rhen and Asha active, Toma in reserve), on Asha's turn.
func _engine() -> BattleEngine:
	var e := BattleEngine.new()
	e.setup(BattleDB.load_default(), [&"rhen", &"asha"] as Array[StringName], [&"toma"] as Array[StringName], REEF, 3)
	e.vowbound = BattleVowbound.new(BattleVowbound.load_config(), [ILUN] as Array[StringName])
	e.begin()
	_turn_of(e, &"asha")
	return e


## Attaches Swell rules to `e` and gives them to `p`, played at good.
func _attach(e: BattleEngine, p: SimPolicy) -> SimPolicy:
	var sw := BattleSwell.new(BattleSwell.load_config())
	sw.attach(e)
	_swell_keep.append(sw)
	p.swell = sw
	p.swell_quality = SwellInput.QUALITY_GOOD
	p.swell_heal_below_pct = 60
	return p


## Plays enemy turns (and other party members' basic attacks) until it is `cid`'s turn.
static func _turn_of(e: BattleEngine, cid: StringName) -> void:
	var guard := 0
	while e.outcome == &"" and e.current.id != cid and guard < 50:
		guard += 1
		if e.is_party_turn():
			e.perform(&"attack", [e.living_foes_of(e.current)[0]] as Array[BattleCombatant])
		else:
			e.run_enemy_turn()
