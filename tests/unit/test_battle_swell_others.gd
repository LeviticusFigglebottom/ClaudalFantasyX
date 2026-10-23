extends TestCase
## M2-CMB-02: the "all_other_allies" target kind, every living active ally but the user. Shallows
## Verse uses it, so Asha's song is for the others, never the singer: Ballast fills when she is
## nearly down, and a Verse that healed her too was a second life a masher could not lose with
## (balance_report.md, 2026-10-23 M2-CMB-02).

const REEF := &"sandbox_reef"
const VERSE := &"shallows_verse"
const GOOD := {"cancelled": false, "grades": [&"good", &"good", &"good", &"good", &"good"]}

var engine: BattleEngine
## Held for the test: a signal connection does not keep it alive.
var swell: BattleSwell


func before_each() -> void:
	engine = BattleEngine.new()
	engine.setup(
		BattleDB.load_default(), [&"rhen", &"asha"] as Array[StringName], [&"toma"] as Array[StringName], REEF, 3
	)
	swell = BattleSwell.new(BattleSwell.load_config())
	swell.attach(engine)
	engine.begin()
	_turn_of(engine, &"asha")


func test_the_verse_row_skips_the_singer() -> void:
	assert_eq(str(engine.db.skill(VERSE).get("target", "")), "all_other_allies")


func test_living_other_allies_leave_out_the_asker_on_both_sides() -> void:
	var asha := engine.find(&"asha")
	var rhen := engine.find(&"rhen")
	assert_eq(engine.living_other_allies_of(asha), [rhen] as Array[BattleCombatant])
	assert_eq(engine.living_allies_of(asha).size(), 2, "the plain list is unchanged")
	var foe := engine.enemies[0]
	var others := engine.living_other_allies_of(foe)
	assert_false(others.has(foe))
	assert_eq(others.size(), engine.living_allies_of(foe).size() - 1, "a foe's allies, less itself")
	rhen.hp = 0
	assert_true(engine.living_other_allies_of(asha).is_empty(), "the fallen are out of reach")


func test_the_verse_heals_every_other_active_ally_and_never_the_singer() -> void:
	var asha := engine.find(&"asha")
	var rhen := engine.find(&"rhen")
	var toma := engine.find(&"toma")
	asha.hp = 10
	rhen.hp = 10
	toma.hp = 10
	asha.swell = Formulas.SWELL_MAX
	var all: Array[BattleCombatant] = [asha, rhen, toma, engine.enemies[0]]
	var res := swell.perform(VERSE, all, GOOD)
	assert_true(res.ok, str(res.fail_reason))
	assert_eq(res.hits.size(), 1, "one hit: Rhen; not the singer, the reserve or a foe")
	assert_eq(StringName(str(res.hits[0].get("target_id", ""))), &"rhen")
	assert_true(rhen.hp > 10, "Rhen healed")
	assert_eq(asha.hp, 10, "the singer is not healed")
	assert_eq(toma.hp, 10, "the reserve is out of reach")
	assert_eq(asha.swell, 0, "the gauge is spent")


func test_a_singer_alone_has_nobody_to_sing_for() -> void:
	var asha := engine.find(&"asha")
	engine.find(&"rhen").hp = 0
	asha.swell = Formulas.SWELL_MAX
	var mp := asha.mp
	var res := swell.perform(VERSE, [asha] as Array[BattleCombatant], GOOD)
	assert_false(res.ok)
	assert_eq(res.fail_reason, &"no_valid_target")
	assert_eq(asha.swell, Formulas.SWELL_MAX, "a refusal costs nothing")
	assert_eq(asha.mp, mp)
	assert_eq(engine.current, asha, "still her turn")


## The timeline preview reaches the same allies the song does: a sleeping Zombie Rhen, whom the
## heal harms, wakes in the preview exactly as in play.
func test_the_preview_matches_the_song() -> void:
	var rhen := engine.find(&"rhen")
	rhen.add_status(&"zombie", -1)
	rhen.add_status(&"sleep", 3)
	engine.find(&"asha").swell = Formulas.SWELL_MAX
	var predicted := _entries(engine.preview(VERSE, null, 14))
	assert_true(swell.perform(VERSE, engine.party_active.duplicate(), GOOD).ok)
	assert_eq(_entries(engine.preview(&"", null, 14)), predicted)
	assert_false(rhen.has_status(&"sleep"), "the harm woke him")


# --- menus -----------------------------------------------------------------------------------


func test_the_pick_holds_every_other_ally_under_its_own_name() -> void:
	var menus := BattleMenus.new()
	var asha := engine.find(&"asha")
	var rhen := engine.find(&"rhen")
	assert_eq(menus.skill_candidates(engine, VERSE), [rhen] as Array[BattleCombatant], "the singer is not lit")
	assert_eq(menus.default_targets(engine, VERSE, &""), [rhen] as Array[BattleCombatant])
	assert_true(menus.skill_candidates(engine, &"chorus_mend").has(asha), "a plain group heal still takes her")
	assert_eq(menus.group_label(false, "all_other_allies"), tr("HUD_GROUP_ALL_OTHER_ALLIES"))
	assert_eq(menus.group_label(false, "all_allies"), tr("HUD_GROUP_ALL_ALLIES"))
	assert_eq(menus.group_label(false), tr("HUD_GROUP_ALL_ALLIES"), "items name no skill target")
	assert_eq(menus.group_label(true, "all_other_allies"), tr("HUD_GROUP_ALL_FOES"))
	assert_true(menus.skill_help(engine, VERSE, -1).contains(tr("HUD_TARGET_ALL_OTHER_ALLIES")))


func test_the_swell_row_greys_out_with_nobody_to_sing_for() -> void:
	var menus := BattleMenus.new()
	var asha := engine.find(&"asha")
	asha.swell = Formulas.SWELL_MAX
	assert_true(_verse_row(menus)["enabled"], "full, Rhen standing")
	engine.find(&"rhen").hp = 0
	assert_false(_verse_row(menus)["enabled"], "full, but nobody else standing")
	asha.swell = 0
	engine.find(&"rhen").hp = 50
	assert_false(_verse_row(menus)["enabled"], "not full")


# --- simulator -------------------------------------------------------------------------------


func test_the_sim_holds_the_verse_while_only_the_singer_is_hurt() -> void:
	var p := SimPolicy.new()
	p.swell = swell
	p.swell_quality = SwellInput.QUALITY_GOOD
	p.swell_heal_below_pct = 60
	var asha := engine.find(&"asha")
	var rhen := engine.find(&"rhen")
	asha.swell = Formulas.SWELL_MAX
	rhen.hp = rhen.max_hp
	asha.hp = 1
	assert_false(p.unleash_swell(engine), "only the singer is hurt: the song waits")
	rhen.hp = rhen.max_hp / 4
	assert_true(p.unleash_swell(engine))
	assert_eq(asha.hp, 1, "and it never reaches her")
	assert_true(rhen.hp > rhen.max_hp / 4)


func test_sim_use_aims_an_other_allies_skill_at_the_others() -> void:
	var row: Dictionary = (engine.db.skill(&"chorus_mend")).duplicate(true)
	row["target"] = "all_other_allies"
	engine.db.skills[&"song_for_others"] = row
	var asha := engine.find(&"asha")
	asha.skills.append(&"song_for_others")
	var rhen := engine.find(&"rhen")
	asha.hp = 10
	rhen.hp = 10
	assert_true(SimPolicy.use(engine, &"song_for_others", rhen))
	assert_true(rhen.hp > 10)
	assert_eq(asha.hp, 10)


# --- helpers ---------------------------------------------------------------------------------


static func _entries(list: Array[TurnEntry]) -> Array[String]:
	var out: Array[String] = []
	for t in list:
		out.append("%s@%d" % [t.combatant_id, t.time])
	return out


func _verse_row(menus: BattleMenus) -> Dictionary:
	for r in menus.swell_rows(engine, swell):
		if StringName(str(r.get("id", ""))) == VERSE:
			return r
	return {}


## Plays enemy turns (and other party members' basic attacks) until it is `cid`'s turn.
static func _turn_of(e: BattleEngine, cid: StringName) -> void:
	var guard := 0
	while e.outcome == &"" and e.current.id != cid and guard < 50:
		guard += 1
		if e.is_party_turn():
			e.perform(&"attack", [e.living_foes_of(e.current)[0]] as Array[BattleCombatant])
		else:
			e.run_enemy_turn()
