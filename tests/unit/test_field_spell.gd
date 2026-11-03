extends TestCase
## M3-CMB-05 (the human's playtest, 2026-11-03): healing spells cast from the field menu
## (FieldSpell, formulas.md § Field spells) on the party as the field menus build it
## (PartySheet.combatant): the data flag, the caster's MP, the exact heal, every refusal, group
## spells for one cost, previews that change nothing, and the vitals written back.

const HEROES: Array[StringName] = [&"rhen", &"asha", &"toma"]

var state: GameStateData
var sheet: PartySheet
var db: BattleDB


func before_each() -> void:
	state = GameStateData.new()
	state.party_ids = HEROES.duplicate()
	sheet = PartySheet.new(state, HEROES)
	db = sheet.battle_db


func test_mend_and_chorus_mend_are_field_usable_and_attacks_are_not() -> void:
	assert_true(FieldSpell.for_skill(db, &"mend") != null)
	assert_true(FieldSpell.for_skill(db, &"chorus_mend") != null)
	assert_true(FieldSpell.for_skill(db, &"ward") == null, "a battle buff ends with the battle")
	assert_true(FieldSpell.for_skill(db, &"attack") == null)
	assert_true(FieldSpell.for_skill(db, &"no_such_skill") == null)
	assert_eq(FieldSpell.castable(db, sheet.combatant(&"asha")), [&"mend"] as Array[StringName])
	assert_eq(FieldSpell.castable(db, sheet.combatant(&"rhen")), [] as Array[StringName])


func test_mend_heals_the_mean_roll_and_costs_its_mp() -> void:
	var asha := sheet.combatant(&"asha")
	var rhen := sheet.combatant(&"rhen")
	rhen.hp = 50
	var mend := FieldSpell.for_skill(db, &"mend")
	var party := _party([asha, rhen])
	var heal := Formulas.field_heal_amount(10, asha.effective_magic(), asha.level, false)
	var mp := asha.mp
	var seen := mend.preview(asha, party, rhen)
	assert_true(seen["ok"])
	assert_eq(rhen.hp, 50, "a preview changes nothing")
	assert_eq(asha.mp, mp)
	var done := mend.cast(asha, party, rhen)
	assert_eq(done, seen, "the preview is the result (no RNG)")
	assert_eq(rhen.hp, mini(rhen.max_hp, 50 + heal))
	assert_eq(asha.mp, mp - mend.mp_cost())
	assert_eq(mend.mp_cost(), 4)
	var ch: Dictionary = (done["changes"] as Array)[0]
	assert_eq(ch["id"], &"rhen")
	assert_eq(ch["hp_before"], 50)
	assert_eq(ch["hp_after"], rhen.hp)


func test_refusals_spend_nothing() -> void:
	var asha := sheet.combatant(&"asha")
	var rhen := sheet.combatant(&"rhen")
	var toma := sheet.combatant(&"toma")
	var mend := FieldSpell.for_skill(db, &"mend")
	var party := _party([asha, rhen, toma])
	assert_eq(mend.cast_error(asha, party, rhen), FieldSpell.ERR_NOTHING, "already at full HP")
	rhen.hp = 0
	assert_eq(mend.cast_error(asha, party, rhen), FieldSpell.ERR_FALLEN, "a heal can't raise the KO'd")
	toma.hp = 10
	toma.statuses[&"zombie"] = -1
	assert_eq(mend.cast_error(asha, party, toma), FieldSpell.ERR_WOULD_HURT)
	toma.statuses.erase(&"zombie")
	toma.statuses[BattleCombatant.STATUS_PETRIFY] = -1
	assert_eq(mend.cast_error(asha, party, toma), FieldSpell.ERR_PETRIFIED)
	toma.statuses.clear()
	asha.mp = 3
	assert_eq(mend.cast_error(asha, party, toma), FieldSpell.ERR_NO_MP)
	var refused := mend.cast(asha, party, toma)
	assert_false(refused["ok"])
	assert_eq(refused["error"], FieldSpell.ERR_NO_MP)
	assert_eq(asha.mp, 3, "nothing spent")
	assert_eq(toma.hp, 10, "nothing healed")
	asha.mp = 40
	asha.hp = 0
	assert_eq(mend.cast_error(asha, party, toma), FieldSpell.ERR_CASTER_DOWN)
	assert_eq(mend.cast_error(rhen, party, toma), FieldSpell.ERR_NOT_KNOWN, "Rhen doesn't know Mend")


func test_a_group_spell_reaches_everyone_it_helps_for_one_cost() -> void:
	var asha := sheet.combatant(&"asha")
	asha.skills.append(&"chorus_mend")  # learned on the Lattice in play
	var rhen := sheet.combatant(&"rhen")
	var toma := sheet.combatant(&"toma")
	var party := _party([asha, rhen, toma])
	var chorus := FieldSpell.for_skill(db, &"chorus_mend")
	assert_true(chorus.is_group())
	assert_eq(chorus.cast_error(asha, party, rhen), FieldSpell.ERR_NO_ONE, "everyone is full")
	rhen.hp = 20
	toma.hp = 0
	var mp := asha.mp
	var done := chorus.cast(asha, party, null)
	assert_true(done["ok"])
	assert_eq((done["changes"] as Array).size(), 1, "the full and the KO'd are skipped")
	assert_true(rhen.hp > 20)
	assert_eq(toma.hp, 0)
	assert_eq(asha.mp, mp - 14, "one cost for the group")


func test_a_cast_saves_like_a_field_item() -> void:
	state.party_vitals = {"rhen": {"hp": 30}}
	var asha := sheet.combatant(&"asha")
	var rhen := sheet.combatant(&"rhen")
	assert_eq(rhen.hp, 30)
	var done := FieldSpell.for_skill(db, &"mend").cast(asha, _party([asha, rhen]), rhen)
	assert_true(done["ok"])
	for c: BattleCombatant in [asha, rhen]:
		var held: Array[StringName] = []
		state.record_vitals(c.id, c.hp, c.max_hp, c.mp, c.max_mp, held, held)
	assert_eq(sheet.combatant(&"rhen").hp, rhen.hp, "the heal is in the save")
	assert_eq(sheet.combatant(&"asha").mp, asha.mp, "the MP spent is in the save")


func _party(list: Array) -> Array[BattleCombatant]:
	var out: Array[BattleCombatant] = []
	out.assign(list)
	return out


func test_self_and_all_other_allies_spells_and_null_inputs() -> void:
	var asha := sheet.combatant(&"asha")
	var rhen := sheet.combatant(&"rhen")
	var party := _party([asha, rhen])
	var self_cure := _spell(&"mend", {"kind": "support", "target": "self", "cleanses": ["poison"]})
	assert_eq(self_cure.cast_error(asha, party, rhen), FieldSpell.ERR_NOTHING, "self: the caster, not the pick")
	asha.statuses[&"poison"] = -1
	rhen.statuses[&"poison"] = -1
	var done := self_cure.cast(asha, party, rhen)
	assert_true(done["ok"])
	assert_false(asha.has_status(&"poison"))
	assert_true(rhen.has_status(&"poison"), "the pick is ignored")
	assert_eq((done["changes"] as Array)[0]["removed"], [&"poison"] as Array[StringName])
	var others := _spell(&"mend", {"kind": "heal", "power": 10, "target": "all_other_allies"})
	asha.hp = 10
	rhen.hp = 10
	assert_true(others.is_group())
	var reached := others.reach(asha, party, null)
	assert_eq(reached.size(), 1)
	assert_eq(reached[0], rhen, "not the caster")
	var mend := FieldSpell.for_skill(db, &"mend")
	assert_eq(mend.name_key(), "SKILL_MEND")
	assert_eq(mend.caster_error(null), FieldSpell.ERR_UNKNOWN)
	assert_eq(mend.target_error(asha, null), FieldSpell.ERR_UNKNOWN)
	assert_eq(FieldSpell.castable(db, null), [] as Array[StringName])


func _spell(sid: StringName, extra: Dictionary) -> FieldSpell:
	var s := FieldSpell.new()
	s.skill_id = sid
	s.row = {"id": String(sid), "name_key": "SKILL_MEND", "mp_cost": 2, "field_usable": true}
	s.row.merge(extra, true)
	return s


func test_a_field_mend_heals_what_a_battle_mend_would_at_the_same_stats() -> void:
	# M3-CMB-1252: the battle rolls variance 92..108; the field casts at its middle, 100. Over many seeds the
	# battle's heals bracket the field's, and the field's exact amount is among them.
	var field_amount := -1
	var battle: Array[int] = []
	for s in range(1, 121):
		var engine := BattleEngine.new()
		var active: Array[StringName] = [&"rhen", &"asha"]
		engine.setup(BattleDB.load_default(), active, [] as Array[StringName], &"sandbox_reef", s)
		engine.begin()
		if not _to_turn_of(engine, &"asha"):
			continue
		var asha := engine.current
		var rhen := engine.party_active[0]
		rhen.hp = 10
		if field_amount < 0:
			var copy := rhen.sim_copy()
			var res := FieldSpell.for_skill(engine.db, &"mend").preview(asha, _party([asha, copy]), copy)
			field_amount = int((res["healed"] as Dictionary)[&"rhen"])
		var targets: Array[BattleCombatant] = [rhen]
		engine.perform(&"mend", targets)
		battle.append(rhen.hp - 10)
	assert_true(battle.size() > 60, "reached Asha's turn on most seeds (%d)" % battle.size())
	var lo: int = battle.min()
	var hi: int = battle.max()
	assert_true(lo <= field_amount and field_amount <= hi, "field %d within battle %d..%d" % [field_amount, lo, hi])
	assert_true(battle.has(field_amount), "a battle Mend at variance 100 heals exactly the field amount")


func test_the_result_names_mp_spent_healed_and_cured_and_silence_refuses() -> void:
	var asha := sheet.combatant(&"asha")
	var rhen := sheet.combatant(&"rhen")
	rhen.hp = 40
	var mend := FieldSpell.for_skill(db, &"mend")
	var done := mend.cast(asha, _party([asha, rhen]), rhen)
	assert_eq(done["mp_spent"], 4)
	assert_eq((done["healed"] as Dictionary)[&"rhen"], rhen.hp - 40)
	assert_eq(done["cured"], {})
	assert_eq(done["revived"], [] as Array[StringName])
	asha.statuses[&"silence"] = 2
	rhen.hp = 40
	var refused := mend.cast(asha, _party([asha, rhen]), rhen)
	assert_eq(refused["error"], FieldSpell.ERR_SILENCED)
	assert_eq(refused["mp_spent"], 0)
	var cure := _spell(&"mend", {"kind": "support", "target": "single_ally", "cleanses": ["poison"], "magic": false})
	rhen.statuses[&"poison"] = -1
	assert_eq(cure.cast(asha, _party([asha, rhen]), rhen)["cured"], {&"rhen": [&"poison"] as Array[StringName]})


func _to_turn_of(engine: BattleEngine, cid: StringName) -> bool:
	for _i in 40:
		if engine.outcome != &"":
			return false
		if not engine.is_party_turn():
			engine.run_enemy_turn()
			continue
		if engine.current.id == cid:
			return true
		var foe := engine.living_foes_of(engine.current)
		if foe.is_empty():
			return false
		var one: Array[BattleCombatant] = [foe[0]]
		var sid := &"read" if engine.current.skills.has(&"read") else &"attack"
		engine.perform(sid, one)
	return false
