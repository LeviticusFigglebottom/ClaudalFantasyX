extends TestCase
## M1-CMB-03: preemptive and ambush openings (BattleOpening, formulas.md § Openings). Headless on
## a fixture DB, so tuning the sandbox tables never breaks these rules.

const SEED := 7

var engine: BattleEngine


func before_each() -> void:
	engine = BattleEngine.new()


# --- what an encounter asks for ------------------------------------------------------------------


func test_setting_defaults_to_a_roll_and_scripted_fights_open_normally() -> void:
	assert_eq(BattleOpening.setting({}), BattleOpening.ROLL)
	assert_eq(BattleOpening.setting({"scripted": true}), BattleOpening.NORMAL)
	assert_eq(BattleOpening.setting({"scripted": true, "opening": "ambush"}), BattleOpening.AMBUSH, "a story ambush")
	assert_eq(BattleOpening.setting({"opening": "preemptive"}), BattleOpening.PREEMPTIVE)
	assert_eq(BattleOpening.setting({"opening": "roll", "scripted": true}), BattleOpening.ROLL)
	assert_eq(BattleOpening.setting({"opening": "first_strike"}), BattleOpening.NORMAL, "unknown: normal")


func test_from_roll_splits_one_draw_between_the_chances() -> void:
	assert_eq(BattleOpening.from_roll(1, 11, 5), BattleOpening.PREEMPTIVE)
	assert_eq(BattleOpening.from_roll(11, 11, 5), BattleOpening.PREEMPTIVE)
	assert_eq(BattleOpening.from_roll(12, 11, 5), BattleOpening.AMBUSH)
	assert_eq(BattleOpening.from_roll(16, 11, 5), BattleOpening.AMBUSH)
	assert_eq(BattleOpening.from_roll(17, 11, 5), BattleOpening.NORMAL)
	assert_eq(BattleOpening.from_roll(100, 11, 5), BattleOpening.NORMAL)


# --- choose() ------------------------------------------------------------------------------------


func test_a_fixed_opening_draws_nothing_from_the_rng() -> void:
	for enc: StringName in [&"story", &"ambushed", &"odd"]:
		_setup(enc)
		var before := engine.rng.state
		var got := BattleOpening.choose(engine)
		assert_eq(engine.rng.state, before, "%s: no draw" % enc)
		assert_eq(
			got, {&"story": BattleOpening.NORMAL, &"ambushed": BattleOpening.AMBUSH, &"odd": BattleOpening.NORMAL}[enc]
		)


func test_a_rolled_opening_draws_once_and_is_deterministic() -> void:
	_setup(&"open")
	var twin := RandomNumberGenerator.new()
	twin.seed = SEED
	var party_agi := BattleOpening.mean_agility(engine.party_active)
	var enemy_agi := BattleOpening.mean_agility(engine.enemies)
	assert_eq(party_agi, 15.0, "the living active party: (20 + 10) / 2")
	assert_eq(enemy_agi, 17.5)
	var want := BattleOpening.from_roll(
		twin.randi_range(1, Formulas.PCT),
		Formulas.preemptive_chance(party_agi, enemy_agi),
		Formulas.ambush_chance(party_agi, enemy_agi)
	)
	assert_eq(BattleOpening.choose(engine), want)
	assert_eq(engine.rng.state, twin.state, "exactly one draw")


func test_rolled_openings_land_near_their_chances() -> void:
	# Party 15 vs enemies 17.5: preemptive 8 + round(-2.5) = 5%, ambush 8 + round(2.5) = 11%.
	var counts := {BattleOpening.NORMAL: 0, BattleOpening.PREEMPTIVE: 0, BattleOpening.AMBUSH: 0}
	for s in 2000:
		engine = BattleEngine.new()
		engine.setup(_db(), _ids(["fast", "slow"]), _ids(["spare"]), &"open", s)
		var got := BattleOpening.choose(engine)
		counts[got] = int(counts[got]) + 1
	assert_between(float(counts[BattleOpening.PREEMPTIVE]) / 2000.0, 0.03, 0.07, "about 5%")
	assert_between(float(counts[BattleOpening.AMBUSH]) / 2000.0, 0.08, 0.14, "about 11%")


func test_mean_agility_counts_only_the_living() -> void:
	_setup(&"open")
	engine.party_active[0].hp = 0
	assert_eq(BattleOpening.mean_agility(engine.party_active), 10.0)
	engine.party_active[1].hp = 0
	assert_eq(BattleOpening.mean_agility(engine.party_active), 0.0, "nobody standing")


# --- the ticks -----------------------------------------------------------------------------------


func test_a_normal_opening_keeps_the_rolled_ticks_and_setup_resets_it() -> void:
	var plain := _ticks_after_begin(BattleOpening.NORMAL)
	_setup(&"open")
	engine.opening = BattleOpening.AMBUSH
	_setup(&"open")
	assert_eq(engine.opening, BattleOpening.NORMAL, "setup() starts every battle normal")
	engine.begin()
	assert_eq(_ticks(), plain)


func test_preemptive_puts_every_party_turn_before_any_enemy() -> void:
	var plain := _ticks_after_begin(BattleOpening.NORMAL)
	var pre := _ticks_after_begin(BattleOpening.PREEMPTIVE)
	var lead := Formulas.opening_lead(maxi(int(plain["fast"]), int(plain["slow"])))
	assert_eq(pre["fast"], plain["fast"], "the favored side keeps its ticks")
	assert_eq(pre["slow"], plain["slow"])
	assert_eq(pre["quick#1"], int(plain["quick#1"]) + lead)
	assert_eq(pre["lump#2"], int(plain["lump#2"]) + lead)
	assert_true(mini(int(pre["quick#1"]), int(pre["lump#2"])) > maxi(int(pre["fast"]), int(pre["slow"])))
	assert_eq(_first_teams(2), [BattleCombatant.TEAM_PARTY, BattleCombatant.TEAM_PARTY])
	assert_true(engine.is_party_turn())


func test_an_ambush_puts_every_enemy_turn_before_any_party_turn() -> void:
	var plain := _ticks_after_begin(BattleOpening.NORMAL)
	var amb := _ticks_after_begin(BattleOpening.AMBUSH)
	var lead := Formulas.opening_lead(maxi(int(plain["quick#1"]), int(plain["lump#2"])))
	assert_eq(amb["quick#1"], plain["quick#1"])
	assert_eq(amb["fast"], int(plain["fast"]) + lead)
	assert_eq(amb["slow"], int(plain["slow"]) + lead)
	assert_true(mini(int(amb["fast"]), int(amb["slow"])) > maxi(int(amb["quick#1"]), int(amb["lump#2"])))
	assert_eq(_first_teams(2), [BattleCombatant.TEAM_ENEMY, BattleCombatant.TEAM_ENEMY])
	assert_false(engine.is_party_turn())


func test_the_timeline_shows_the_opening() -> void:
	_setup(&"open")
	engine.opening = BattleOpening.PREEMPTIVE
	engine.begin()
	var order := engine.preview(&"", null, 4)
	assert_eq(order.size(), 4)
	assert_eq(order[0].team, BattleCombatant.TEAM_PARTY)
	assert_eq(order[1].team, BattleCombatant.TEAM_PARTY)


func test_the_fallen_neither_set_nor_take_the_lead() -> void:
	var fast := _combatant(&"fast", BattleCombatant.TEAM_PARTY, 100)
	var down := _combatant(&"down", BattleCombatant.TEAM_PARTY, 900)
	down.hp = 0
	var foe := _combatant(&"foe", BattleCombatant.TEAM_ENEMY, 50)
	var foe_down := _combatant(&"foe_down", BattleCombatant.TEAM_ENEMY, 60)
	foe_down.hp = 0
	BattleOpening.apply(BattleOpening.PREEMPTIVE, _list([fast, down]), _list([foe, foe_down]))
	assert_eq(foe.next_time, 50 + Formulas.opening_lead(100), "a fallen member's ticks set no lead")
	assert_eq(foe_down.next_time, 60, "a fallen foe is not moved")
	assert_eq(down.next_time, 900)


func test_no_one_standing_on_the_favored_side_changes_nothing() -> void:
	var down := _combatant(&"down", BattleCombatant.TEAM_PARTY, 100)
	down.hp = 0
	var foe := _combatant(&"foe", BattleCombatant.TEAM_ENEMY, 50)
	BattleOpening.apply(BattleOpening.PREEMPTIVE, _list([down]), _list([foe]))
	assert_eq(foe.next_time, 50)
	BattleOpening.apply(&"bogus", _list([foe]), _list([down]))
	assert_eq(down.next_time, 100, "an unknown opening is a normal one")


func test_caption_keys_name_only_the_two_special_openings() -> void:
	assert_eq(BattleOpening.CAPTION_KEYS.size(), 2)
	assert_false(BattleOpening.CAPTION_KEYS.has(BattleOpening.NORMAL))
	for key: Variant in BattleOpening.CAPTION_KEYS.values():
		assert_ne(TranslationServer.translate(str(key)), str(key), "%s is localized" % key)


# --- helpers -------------------------------------------------------------------------------------


func _setup(enc: StringName) -> void:
	engine.setup(_db(), _ids(["fast", "slow"]), _ids(["spare"]), enc, SEED)


func _ticks_after_begin(opening: StringName) -> Dictionary:
	engine = BattleEngine.new()
	_setup(&"open")
	engine.opening = opening
	engine.begin()
	return _ticks()


func _ticks() -> Dictionary:
	var out := {}
	for c in engine.party_active + engine.enemies:
		out[String(c.id)] = c.next_time
	return out


## Teams of the first `n` turns played (each actor uses its cheapest rank-3 attack).
func _first_teams(n: int) -> Array:
	var teams: Array = []
	for i in n:
		teams.append(engine.current.team)
		if engine.is_party_turn():
			engine.perform(&"attack", _list([engine.living_foes_of(engine.current)[0]]))
		else:
			engine.run_enemy_turn()
	return teams


static func _combatant(cid: StringName, team: StringName, next_time: int) -> BattleCombatant:
	var c := BattleCombatant.from_dict(cid, team, {"stats": {"hp": 10, "agility": 10}})
	c.next_time = next_time
	return c


static func _list(items: Array) -> Array[BattleCombatant]:
	var out: Array[BattleCombatant] = []
	for c: Variant in items:
		out.append(c as BattleCombatant)
	return out


static func _ids(list: Array) -> Array[StringName]:
	var out: Array[StringName] = []
	for v: Variant in list:
		out.append(StringName(str(v)))
	return out


static func _fighter(agility: int, hp: int) -> Dictionary:
	return {
		"level": 5,
		"hp": hp,
		"mp": 0,
		"strength": 10,
		"magic": 0,
		"defense": 10,
		"magic_defense": 0,
		"agility": agility,
		"accuracy": 100,
		"evasion": 0,
		"luck": 0,
	}


static func _db() -> BattleDB:
	var attack := {"id": "attack", "kind": "physical", "power": 1, "rank": 3, "target": "single_foe"}
	var ai := [{"pick": [{"skill": "attack", "target": "random_foe"}]}]
	return (
		BattleDB
		. from_tables(
			{
				"skills": [attack],
				"statuses": [],
				"characters":
				[
					{"id": "fast", "stats": _fighter(20, 9000), "skills": ["attack"]},
					{"id": "slow", "stats": _fighter(10, 9000), "skills": ["attack"]},
					{"id": "spare", "stats": _fighter(40, 9000), "skills": ["attack"]},
				],
				"enemies":
				[
					{"id": "quick", "stats": _fighter(30, 9000), "skills": ["attack"], "ai": ai},
					{"id": "lump", "stats": _fighter(5, 9000), "skills": ["attack"], "ai": ai},
				],
				"encounters":
				[
					{"id": "open", "enemies": ["quick", "lump"]},
					{"id": "story", "scripted": true, "enemies": ["quick", "lump"]},
					{"id": "ambushed", "scripted": true, "opening": "ambush", "enemies": ["quick", "lump"]},
					{"id": "odd", "opening": "bogus", "enemies": ["quick", "lump"]},
				],
			}
		)
	)
