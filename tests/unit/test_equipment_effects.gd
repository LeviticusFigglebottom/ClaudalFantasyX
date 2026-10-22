extends TestCase
## EquipmentEffects: stats, auto-statuses, guards and engine-facing data through
## BattleEngine.party_modifier, composed with the Lattice (M1-PRG-02). No game/battle edits.

var db: ItemDB
var bdb: BattleDB


func before_each() -> void:
	db = ItemDB.load_default()
	bdb = BattleDB.load_default()


func _base(cid: StringName) -> BattleCombatant:
	return BattleCombatant.from_dict(cid, BattleCombatant.TEAM_PARTY, bdb.characters[cid])


func _wear(bag: EquipmentBag, cid: StringName, equip_id: StringName, extra: Array[StringName] = []) -> int:
	var uid := bag.add_piece(equip_id)
	for a in extra:
		bag.set_slot(uid, bag.first_empty_slot(uid), a)
	bag.equip(cid, uid)
	return uid


func test_piece_stats_and_stat_abilities_add() -> void:
	var bag := EquipmentBag.new(db)
	_wear(bag, &"rhen", &"rhen_coral_hooks", [&"steady_arm"])  # strength +1, ember_edge, steady_arm +3
	_wear(bag, &"rhen", &"rhen_reefline_harness", [&"deep_lungs"])  # hp +40, bitter_ward, deep_lungs +60
	var fx := EquipmentEffects.new(db, bag)
	assert_eq(fx.stat_bonuses(&"rhen"), {&"strength": 4, &"hp": 100})
	var c := _base(&"rhen")
	var str0 := c.strength
	var hp0 := c.max_hp
	fx.apply_to(c)
	assert_eq(c.strength, str0 + 4)
	assert_eq(c.max_hp, hp0 + 100)
	assert_eq(c.hp, c.max_hp, "HP bonus raises current HP too")


func test_duplicate_abilities_stack() -> void:
	var bag := EquipmentBag.new(db)
	_wear(bag, &"rhen", &"rhen_tidewalker_hooks", [&"steady_arm", &"steady_arm"])
	var fx := EquipmentEffects.new(db, bag)
	assert_eq(int(fx.stat_bonuses(&"rhen")[&"strength"]), 2 + 3 + 3)


func test_always_auto_status_starts_battle() -> void:
	var bag := EquipmentBag.new(db)
	_wear(bag, &"toma", &"toma_reach_tide_shield", [&"standing_guard", &"low_tide_haste"])
	var fx := EquipmentEffects.new(db, bag)
	assert_eq(fx.starting_statuses(&"toma"), [&"protect"] as Array[StringName])
	var c := _base(&"toma")
	fx.apply_to(c)
	assert_true(c.has_status(&"protect"))
	assert_eq(int(c.statuses[&"protect"]), EquipmentEffects.WHOLE_BATTLE)
	assert_false(c.has_status(&"haste"), "low-HP statuses wait for the engine")


func test_element_guard_sets_affinity_but_never_weakens() -> void:
	var bag := EquipmentBag.new(db)
	_wear(bag, &"toma", &"toma_chiselled_shield")  # ember_guard prefilled
	var fx := EquipmentEffects.new(db, bag)
	var c := _base(&"toma")
	fx.apply_to(c)
	assert_eq(c.affinity_for(&"fire"), &"resist")
	var immune := _base(&"toma")
	immune.affinities[&"fire"] = &"immune"
	fx.apply_to(immune)
	assert_eq(immune.affinity_for(&"fire"), &"immune")
	var weak := _base(&"toma")
	weak.affinities[&"fire"] = &"weak"
	fx.apply_to(weak)
	assert_eq(weak.affinity_for(&"fire"), &"resist")


func test_unfettered_breaks_damage_cap() -> void:
	var bag := EquipmentBag.new(db)
	_wear(bag, &"rhen", &"rhen_tidewalker_hooks", [&"unfettered"])
	var c := _base(&"rhen")
	EquipmentEffects.new(db, bag).apply_to(c)
	assert_true(c.break_damage_cap)


func test_engine_facing_data_on_metadata() -> void:
	var bag := EquipmentBag.new(db)
	_wear(bag, &"rhen", &"rhen_tidewalker_hooks", [&"ember_edge", &"bitter_edge", &"bitter_edge"])
	_wear(bag, &"rhen", &"rhen_reefline_harness", [&"low_tide_haste"])
	var c := _base(&"rhen")
	EquipmentEffects.new(db, bag).apply_to(c)
	var d := EquipmentEffects.data_of(c)
	assert_eq(d[EquipmentEffects.KEY_ATTACK_ELEMENTS], [&"fire"] as Array[StringName])
	assert_eq(d[EquipmentEffects.KEY_ON_HIT_STATUSES].size(), 1, "same status merges")
	assert_eq(d[EquipmentEffects.KEY_ON_HIT_STATUSES][0]["id"], &"poison")
	assert_eq(d[EquipmentEffects.KEY_STATUS_WARDS], [&"poison"] as Array[StringName])
	assert_eq(d[EquipmentEffects.KEY_LOW_HP_STATUSES][0]["id"], &"haste")
	assert_eq(d[EquipmentEffects.KEY_LOW_HP_STATUSES][0]["hp_below_pct"], 50)
	var want: Array[StringName] = [&"ember_edge", &"bitter_edge", &"bitter_edge", &"bitter_ward", &"low_tide_haste"]
	assert_eq(d[EquipmentEffects.KEY_ABILITIES], want)


func test_no_modifier_means_no_data() -> void:
	assert_eq(EquipmentEffects.data_of(_base(&"rhen")), {})


func test_currency_and_encounter_queries() -> void:
	var bag := EquipmentBag.new(db)
	_wear(bag, &"rhen", &"rhen_tidewalker_hooks", [&"full_net"])
	_wear(bag, &"asha", &"asha_pearl_bangle", [&"light_step"])
	var fx := EquipmentEffects.new(db, bag)
	assert_eq(fx.currency_multiplier([&"asha"] as Array[StringName]), EquipmentEffects.NO_CURRENCY_MULT)
	assert_eq(fx.currency_multiplier([&"asha", &"rhen"] as Array[StringName]), 2)
	assert_eq(fx.encounter_rate_pct([&"rhen"] as Array[StringName]), 100)
	assert_eq(fx.encounter_rate_pct([&"rhen", &"asha"] as Array[StringName]), 50)


func test_composes_with_lattice_through_party_modifier() -> void:
	var progress := LatticeProgress.new(LatticeBoard.load_board(), LatticeRules.load_file())
	progress.add_character(&"rhen")
	var t := progress.traveler(&"rhen")
	t.activated[&"rh_01"] = true  # agility +2 on the standard board
	var bag := EquipmentBag.new(db)
	bag.grant_starting(&"rhen")
	bag.grant_starting(&"asha")
	var fx := EquipmentEffects.new(db, bag)
	var base := _base(&"rhen")
	var engine := BattleEngine.new()
	engine.party_modifier = EquipmentEffects.compose([progress.apply_to, fx.apply_to])
	engine.setup(bdb, [&"rhen", &"asha"] as Array[StringName], [] as Array[StringName], &"sandbox_reef", 7)
	var rhen := engine.find(&"rhen")
	var lattice_bonus := int(progress.stat_bonuses(&"rhen").get(&"agility", 0))
	assert_eq(rhen.agility, base.agility + lattice_bonus)
	assert_eq(rhen.max_hp, base.max_hp + int(fx.stat_bonuses(&"rhen").get(&"hp", 0)))
	assert_true(rhen.has_meta(EquipmentEffects.META_KEY))
	assert_true(engine.find(&"asha").has_meta(EquipmentEffects.META_KEY))


func test_same_inputs_same_combatant() -> void:
	var bag := EquipmentBag.new(db)
	_wear(bag, &"asha", &"asha_dawnwick_staff", [&"clear_mind", &"full_net"])
	var fx := EquipmentEffects.new(db, bag)
	var a := _base(&"asha")
	var b := _base(&"asha")
	fx.apply_to(a)
	fx.apply_to(b)
	assert_eq(a.magic, b.magic)
	assert_eq(EquipmentEffects.data_of(a), EquipmentEffects.data_of(b))
