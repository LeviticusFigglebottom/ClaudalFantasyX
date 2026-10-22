extends TestCase
## EquipmentBag: pieces with ability slots, per-character loadouts, starting gear (M1-PRG-02).

var db: ItemDB


func before_each() -> void:
	db = ItemDB.load_default()


func test_add_piece_copies_slots_and_prefilled_abilities() -> void:
	var bag := EquipmentBag.new(db)
	var uid := bag.add_piece(&"rhen_coral_hooks")
	assert_eq(uid, EquipmentBag.FIRST_UID)
	assert_eq(bag.base_of(uid), &"rhen_coral_hooks")
	assert_eq(bag.slots_of(uid), [&"ember_edge", &""] as Array[StringName])
	assert_eq(bag.abilities_of(uid), [&"ember_edge"] as Array[StringName])
	assert_eq(bag.first_empty_slot(uid), 1)
	assert_eq(bag.empty_slot_count(uid), 1)


func test_uids_are_sequential_and_never_reused() -> void:
	var bag := EquipmentBag.new(db)
	var a := bag.add_piece(&"rhen_salvage_hooks")
	var b := bag.add_piece(&"rhen_salvage_hooks")
	assert_eq(b, a + 1)
	assert_eq(bag.remove_piece(b), EquipmentBag.RESULT_OK)
	var c := bag.add_piece(&"rhen_salvage_hooks")
	assert_eq(c, b + 1, "a removed uid is not reused")
	assert_eq(bag.uids(), [a, c] as Array[int])
	assert_eq(bag.add_piece(&"no_such_piece"), EquipmentBag.NO_PIECE)


func test_each_piece_has_its_own_slots() -> void:
	var bag := EquipmentBag.new(db)
	var a := bag.add_piece(&"rhen_tidewalker_hooks")
	var b := bag.add_piece(&"rhen_tidewalker_hooks")
	assert_true(bag.set_slot(a, 0, &"steady_arm"))
	assert_eq(bag.abilities_of(a), [&"steady_arm"] as Array[StringName])
	assert_eq(bag.abilities_of(b), [] as Array[StringName])
	assert_false(bag.set_slot(a, 3, &"steady_arm"), "out of range")


func test_equip_checks_character_and_slot() -> void:
	var bag := EquipmentBag.new(db)
	var hooks := bag.add_piece(&"rhen_coral_hooks")
	var staff := bag.add_piece(&"asha_bellshell_staff")
	assert_eq(bag.equip(&"rhen", staff), EquipmentBag.ERR_WRONG_CHARACTER)
	assert_eq(bag.equip(&"rhen", 999), EquipmentBag.ERR_UNKNOWN_PIECE)
	assert_eq(bag.equip(&"rhen", hooks), EquipmentBag.RESULT_OK)
	assert_eq(bag.equipped(&"rhen", ItemDB.SLOT_WEAPON), hooks)
	assert_eq(bag.wearer_of(hooks), &"rhen")
	assert_eq(bag.equipped(&"rhen", ItemDB.SLOT_ARMOR), EquipmentBag.NO_PIECE)


func test_equip_replaces_the_slot() -> void:
	var bag := EquipmentBag.new(db)
	var old := bag.add_piece(&"rhen_salvage_hooks")
	var new_hooks := bag.add_piece(&"rhen_coral_hooks")
	bag.equip(&"rhen", old)
	bag.equip(&"rhen", new_hooks)
	assert_eq(bag.equipped(&"rhen", ItemDB.SLOT_WEAPON), new_hooks)
	assert_eq(bag.wearer_of(old), &"")


func test_weapon_is_required_armor_is_not() -> void:
	var bag := EquipmentBag.new(db)
	bag.grant_starting(&"rhen")
	assert_eq(bag.unequip(&"rhen", ItemDB.SLOT_WEAPON), EquipmentBag.ERR_SLOT_REQUIRED)
	assert_eq(bag.unequip(&"rhen", &"hat"), EquipmentBag.ERR_UNKNOWN_SLOT)
	assert_eq(bag.unequip(&"rhen", ItemDB.SLOT_ARMOR), EquipmentBag.RESULT_OK)
	assert_eq(bag.equipped(&"rhen", ItemDB.SLOT_ARMOR), EquipmentBag.NO_PIECE)


func test_equipped_pieces_cannot_be_removed() -> void:
	var bag := EquipmentBag.new(db)
	bag.grant_starting(&"toma")
	var spear := bag.equipped(&"toma", ItemDB.SLOT_WEAPON)
	assert_eq(bag.remove_piece(spear), EquipmentBag.ERR_EQUIPPED)
	assert_eq(bag.remove_piece(12345), EquipmentBag.ERR_UNKNOWN_PIECE)


func test_grant_starting_once_per_hero() -> void:
	var bag := EquipmentBag.new(db)
	assert_true(bag.grant_starting(&"asha"))
	assert_eq(bag.base_of(bag.equipped(&"asha", ItemDB.SLOT_WEAPON)), &"asha_vigil_staff")
	assert_eq(bag.base_of(bag.equipped(&"asha", ItemDB.SLOT_ARMOR)), &"asha_cord_bangle")
	assert_false(bag.grant_starting(&"asha"), "a second grant does nothing")
	assert_eq(bag.uids().size(), 2)
	assert_false(bag.grant_starting(&"nobody"))


func test_every_battle_character_has_starting_gear() -> void:
	var bdb := BattleDB.load_default()
	for cid: StringName in bdb.characters:
		var bag := EquipmentBag.new(db)
		assert_true(bag.grant_starting(cid), "no starting gear for %s" % cid)
		assert_eq(bag.equipped_uids(cid).size(), db.equip_slots.size())


func test_pieces_for_filters_by_character_and_slot() -> void:
	var bag := EquipmentBag.new(db)
	var a := bag.add_piece(&"rhen_salvage_hooks")
	bag.add_piece(&"rhen_patched_tether")
	bag.add_piece(&"toma_boarding_spear")
	var b := bag.add_piece(&"rhen_coral_hooks")
	assert_eq(bag.pieces_for(&"rhen", ItemDB.SLOT_WEAPON), [a, b] as Array[int])


func test_wraps_backing_dictionary_and_survives_json() -> void:
	var backing: Dictionary = {}
	var bag := EquipmentBag.new(db, backing)
	bag.grant_starting(&"rhen")
	var loaded: Dictionary = JSON.parse_string(JSON.stringify(backing))
	var again := EquipmentBag.new(db, loaded)
	assert_eq(again.uids(), bag.uids())
	assert_eq(again.equipped(&"rhen", ItemDB.SLOT_WEAPON), bag.equipped(&"rhen", ItemDB.SLOT_WEAPON))
	assert_eq(again.add_piece(&"rhen_coral_hooks"), 3)


func test_data_slot_counts_respect_the_rule() -> void:
	for eid: StringName in db.equipment:
		var row := db.equipment_row(eid)
		var slots := int(row["slots"])
		assert_true(slots >= 0 and slots <= db.max_slots, "%s has %d slots" % [eid, slots])
		assert_true((row["abilities"] as Array).size() <= slots, "%s overfilled" % eid)
		assert_ne(db.character_of(eid), &"", "%s has no wearer" % eid)
