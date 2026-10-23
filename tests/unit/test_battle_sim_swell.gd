extends TestCase
## M2-CMB-01: Swell in the balancing simulator. BattleSim.swell_quality (`--swell`) attaches a
## BattleSwell, policies unleash a full gauge first with a scripted input result, naive never does,
## and the sandbox bands hold with Swell played at good (balance_report.md, 2026-10-23 entry).

const REEF := &"sandbox_reef"
const SEEDS := 200
const ACTIVE: Array[StringName] = [&"rhen", &"asha"]
const RESERVE: Array[StringName] = [&"toma", &"ysolde"]

## Swell rules the helpers attach, held for the test: a signal connection does not keep them alive.
var _swell_keep: Array[BattleSwell] = []


func test_run_cli_takes_a_swell_quality() -> void:
	var sim := BattleSim.new()
	var args := {"encounter": "sandbox_reef", "active": "rhen,asha", "seeds": "1", "policies": "smart"}
	assert_true(sim.run_cli(args)["ok"])
	assert_eq(sim.swell_quality, &"", "no swell argument: off")
	args["swell"] = "perfect"
	assert_true(sim.run_cli(args)["ok"])
	assert_eq(sim.swell_quality, SwellInput.QUALITY_PERFECT)
	var res: Dictionary = sim.run_cli(args)["results"][0]
	assert_true(res.has("mean_swells"))
	assert_true(((res["runs"] as Array)[0] as Dictionary).has("swells"))
	args["swell"] = "off"
	assert_true(sim.run_cli(args)["ok"])
	assert_eq(sim.swell_quality, &"")
	args["swell"] = "psychic"
	var bad := sim.run_cli(args)
	assert_false(bad["ok"])
	assert_true(str(bad["error"]).contains("psychic"))


func test_summarize_averages_swells() -> void:
	var runs: Array[Dictionary] = [
		{"outcome": "victory", "turns": 10, "party_ko": 0, "items": 0, "swells": 1},
		{"outcome": "defeat", "turns": 12, "party_ko": 2, "items": 0, "swells": 0},
	]
	assert_eq(BattleSim.summarize(runs)["mean_swells"], 0.5)


func test_policies_unleash_but_naive_never_does() -> void:
	var sim := BattleSim.new()
	sim.swell_quality = SwellInput.QUALITY_GOOD
	var kit := sim.loadout(&"m1_starting")
	var lowest := sim.run_many(REEF, ACTIVE, RESERVE, &"lowest_hp", 30, 1, Callable(), kit)
	assert_true(float(lowest["mean_swells"]) > 0.0, "a hit party fills Ballast and unleashes")
	var naive_on := sim.run_many(REEF, ACTIVE, RESERVE, &"naive", 30, 1, Callable(), kit)
	assert_eq(naive_on["mean_swells"], 0.0)
	sim.swell_quality = &""
	var naive_off := sim.run_many(REEF, ACTIVE, RESERVE, &"naive", 30, 1, Callable(), kit)
	assert_eq(naive_on, naive_off, "gauges that are never spent change nothing")
	assert_false(sim.make_policy(&"naive").unleashes_swell())
	assert_true(sim.make_policy(&"smart").unleashes_swell())
	sim.swell_quality = SwellInput.QUALITY_GOOD
	var masher := sim.run_many(REEF, ACTIVE, RESERVE, &"naive_swell", 30, 1, Callable(), kit)
	assert_true(float(masher["mean_swells"]) > 0.0, "naive_swell presses the Swell row")
	assert_true(sim.make_policy(&"naive_swell").unleashes_swell())


# --- naive_swell and the role answer's focus (M2-NIT-03) ------------------------------------


func test_naive_swell_aims_where_the_cursor_starts() -> void:
	var e := _engine([&"rhen"])
	var p := _attach(e, SimPolicyNaiveSwell.new())
	assert_eq(p.policy_name(), &"naive_swell")
	var foes := e.living_foes_of(e.current)
	foes[1].hp = 5  # the weakest foe is not the first one
	var first_hp := foes[0].hp
	e.current.swell = Formulas.SWELL_MAX
	assert_true(p.unleash_swell(e))
	assert_true(foes[0].hp < first_hp, "Lamp Dive went to the first foe")
	assert_eq(foes[1].hp, 5, "not to the weakest")


func test_role_answer_swells_at_the_foe_it_answers() -> void:
	var e := _engine([&"rhen"])
	var p := _attach(e, SimPolicyRoleAnswer.new())
	var crab := _foe(e, &"reef_crab")
	var harrier := _foe(e, &"gull_harrier")
	crab.hp = 5  # the weakest foe, but Rhen answers the harrier
	var harrier_hp := harrier.hp
	e.current.swell = Formulas.SWELL_MAX
	assert_eq(p.swell_focus(e, e.current), harrier)
	assert_true(p.unleash_swell(e))
	assert_true(harrier.hp < harrier_hp, "Lamp Dive went to the answered foe")
	assert_eq(crab.hp, 5)


func test_role_answer_swaps_to_the_answer_before_unleashing() -> void:
	var e := BattleEngine.new()
	e.setup(BattleDB.load_default(), [&"rhen", &"asha"] as Array[StringName], [&"ysolde"] as Array[StringName], REEF, 3)
	e.begin()
	_turn_of(e, &"rhen")
	var p := _attach(e, SimPolicyRoleAnswer.new())
	var rhen := e.current
	_foe(e, &"gull_harrier").hp = 0  # Rhen's own foe is down: his focus is the eel, Ysolde's answer
	rhen.swell = Formulas.SWELL_MAX
	assert_false(p.unleash_swell(e), "the free swap comes first")
	p.take_turn(e)
	assert_true(e.party_reserve.has(rhen), "Rhen stepped back for Ysolde")
	assert_eq(rhen.swell, Formulas.SWELL_MAX, "the gauge waits in reserve")
	assert_eq(p.swells_used, 0)
	for f in e.enemies:
		f.hp = 0
	assert_false(p._swaps_out(e, e.current), "no foe left: no focus, no swap")


func test_the_sandbox_bands_hold_with_swell_played_at_good() -> void:
	var sim := BattleSim.new()
	sim.swell_quality = SwellInput.QUALITY_GOOD
	var kit := sim.loadout(&"m1_starting")
	var answer := sim.run_many(REEF, ACTIVE, RESERVE, &"role_answer", SEEDS, 1, Callable(), kit)
	var smart := sim.run_many(REEF, ACTIVE, RESERVE, &"smart", SEEDS, 1, Callable(), kit)
	assert_true(float(answer["win_pct"]) >= 85.0, "role answer %.1f%%" % answer["win_pct"])
	assert_true(float(smart["win_pct"]) >= 85.0, "smart %.1f%%" % smart["win_pct"])
	assert_true(float(smart["mean_turns"]) >= 16.0, "the ease ceiling holds: %.1f turns" % smart["mean_turns"])
	# M2-CMB-02: with the Verse a song for the others, the masher's second life is gone (22.0% over
	# these 200 seeds, 23.8% over the report's 1000; balance_targets.md's line is 25%).
	var masher := sim.run_many(REEF, ACTIVE, RESERVE, &"naive_swell", SEEDS, 1, Callable(), kit)
	assert_true(float(masher["win_pct"]) <= 25.0, "naive_swell %.1f%%" % masher["win_pct"])
	var a := sim.run_one(REEF, ACTIVE, RESERVE, sim.make_policy(&"smart"), 9, Callable(), kit)
	var b := sim.run_one(REEF, ACTIVE, RESERVE, sim.make_policy(&"smart"), 9, Callable(), kit)
	assert_eq(a, b, "seed 9 plays the same battle with Swell on")


# --- unleash_swell ---------------------------------------------------------------------------


func test_a_full_gauge_unleashes_its_technique_first() -> void:
	var e := _engine([&"rhen"])
	var p := _policy(e)
	var rhen := e.current
	assert_false(p.unleash_swell(e), "not full yet")
	rhen.swell = Formulas.SWELL_MAX
	var weakest := SimPolicy.lowest_hp(e.living_foes_of(rhen))
	var hp_before := weakest.hp
	p.take_turn(e)
	assert_eq(rhen.swell, 0, "spent")
	assert_eq(p.swells_used, 1)
	assert_true(weakest.hp < hp_before, "Lamp Dive aims at the weakest foe")
	p.reset()
	assert_eq(p.swells_used, 0)


func test_a_healing_technique_waits_for_a_hurt_ally() -> void:
	var e := _engine([&"asha", &"rhen"])
	var p := _policy(e)
	var asha := e.find(&"asha")
	asha.swell = Formulas.SWELL_MAX
	_turn_of(e, &"asha")
	for c in e.party_active:
		c.hp = c.max_hp
	assert_false(p.unleash_swell(e), "everyone is above 60%: hold the Verse")
	var rhen := e.find(&"rhen")
	rhen.hp = rhen.max_hp / 4
	assert_true(p.unleash_swell(e))
	assert_true(rhen.hp > rhen.max_hp / 4, "Shallows Verse healed Rhen")
	assert_eq(asha.swell, 0)


func test_a_group_technique_hits_every_foe_and_provoke_is_honoured() -> void:
	var e := _engine([&"ysolde"])
	var p := _policy(e)
	var ysolde := e.find(&"ysolde")
	ysolde.swell = Formulas.SWELL_MAX
	_turn_of(e, &"ysolde")
	var before := _foe_hp(e)
	assert_true(p.unleash_swell(e))
	var after := _foe_hp(e)
	for i in before.size():
		assert_true(after[i] < before[i], "Written Light reached foe %d" % i)
	var t := _engine([&"toma"])
	var q := _policy(t)
	var toma := t.find(&"toma")
	toma.swell = Formulas.SWELL_MAX
	_turn_of(t, &"toma")
	var foes := t.living_foes_of(toma)
	var provoker := foes[foes.size() - 1]
	toma.add_status(&"provoke", 3)
	toma.provoker_id = provoker.id
	var hp_before := provoker.hp
	assert_true(q.unleash_swell(t))
	assert_true(provoker.hp < hp_before, "Return Tide went to the provoker")


func test_no_swell_or_no_target_unleashes_nothing() -> void:
	var e := _engine([&"rhen"])
	var p := SimPolicy.new()
	e.current.swell = Formulas.SWELL_MAX
	assert_false(p.unleash_swell(e), "no BattleSwell attached")
	var q := _policy(e)
	for f in e.enemies:
		f.hp = 0
	assert_false(q.unleash_swell(e), "nobody to aim at")
	assert_eq(e.current.swell, Formulas.SWELL_MAX, "nothing spent")


# --- helpers ---------------------------------------------------------------------------------


func _engine(active: Array[StringName]) -> BattleEngine:
	var e := BattleEngine.new()
	e.setup(BattleDB.load_default(), active, [] as Array[StringName], REEF, 3)
	e.begin()
	_turn_of(e, active[0])
	return e


## A policy on `e` with Swell attached (held for the test: a signal does not keep it alive).
func _policy(e: BattleEngine) -> SimPolicy:
	return _attach(e, SimPolicy.new())


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


## The living foe whose enemies.json id is `base` (combatant ids carry a #n suffix).
static func _foe(e: BattleEngine, base: StringName) -> BattleCombatant:
	for f in e.enemies:
		if BattleEngine.enemy_id(f) == base:
			return f
	return null


static func _foe_hp(e: BattleEngine) -> Array[int]:
	var out: Array[int] = []
	for f in e.enemies:
		out.append(f.hp)
	return out
