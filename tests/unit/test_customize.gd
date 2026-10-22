extends TestCase
## Customize: crafting abilities into empty slots at item costs (M1-PRG-02).

var db: ItemDB
var bag: EquipmentBag
var inv: Inventory
var cz: Customize


func before_each() -> void:
	db = ItemDB.load_default()
	bag = EquipmentBag.new(db)
	inv = Inventory.new(db)
	cz = Customize.new(db)


func test_cost_comes_from_data() -> void:
	assert_eq(cz.cost(&"ember_edge"), [{"item": &"ember_coral", "count": 4}] as Array[Dictionary])
	assert_eq(cz.cost(&"no_such_ability"), [] as Array[Dictionary])


func test_craft_fills_first_empty_slot_and_consumes_items() -> void:
	var uid := bag.add_piece(&"rhen_tidewalker_hooks")
	inv.add(&"ember_coral", 5)
	assert_eq(cz.craft_error(bag, uid, &"ember_edge", inv), Customize.RESULT_OK)
	assert_eq(cz.craft(bag, uid, &"ember_edge", inv), Customize.RESULT_OK)
	assert_eq(bag.slots_of(uid), [&"ember_edge", &"", &""] as Array[StringName])
	assert_eq(inv.count(&"ember_coral"), 1)


func test_multi_item_recipe_consumes_every_part() -> void:
	var uid := bag.add_piece(&"rhen_tidewalker_hooks")
	inv.add(&"smelling_salts", 4)
	inv.add(&"quiet_tea", 2)
	assert_eq(cz.craft(bag, uid, &"drowse_edge", inv), Customize.RESULT_OK)
	assert_eq(inv.count(&"smelling_salts"), 0)
	assert_eq(inv.count(&"quiet_tea"), 0)


func test_missing_items_change_nothing() -> void:
	var uid := bag.add_piece(&"rhen_tidewalker_hooks")
	inv.add(&"smelling_salts", 4)
	inv.add(&"quiet_tea", 1)
	assert_eq(cz.shortfall(&"drowse_edge", inv), {&"quiet_tea": 1})
	assert_eq(cz.craft(bag, uid, &"drowse_edge", inv), Customize.ERR_MISSING_ITEMS)
	assert_eq(inv.count(&"smelling_salts"), 4, "nothing consumed on failure")
	assert_eq(bag.abilities_of(uid), [] as Array[StringName])


func test_full_piece_is_refused() -> void:
	var uid := bag.add_piece(&"rhen_coral_hooks")  # 2 slots, ember_edge prefilled
	inv.add(&"storm_scale", 8)
	assert_eq(cz.craft(bag, uid, &"spark_edge", inv), Customize.RESULT_OK)
	assert_eq(cz.craft_error(bag, uid, &"tide_edge", inv), Customize.ERR_NO_EMPTY_SLOT)
	var none := bag.add_piece(&"rhen_salvage_hooks")
	bag.set_slot(none, 0, &"keen_sight")
	assert_eq(cz.craft_error(bag, none, &"spark_edge", inv), Customize.ERR_NO_EMPTY_SLOT)


func test_duplicate_ability_on_one_piece_is_refused() -> void:
	var uid := bag.add_piece(&"rhen_coral_hooks")
	inv.add(&"ember_coral", 4)
	assert_eq(cz.craft_error(bag, uid, &"ember_edge", inv), Customize.ERR_ALREADY_HAS)


func test_ability_must_fit_the_slot_kind() -> void:
	var armor := bag.add_piece(&"rhen_reefline_harness")
	inv.add(&"ember_coral", 10)
	assert_eq(cz.craft_error(bag, armor, &"ember_edge", inv), Customize.ERR_WRONG_SLOT_KIND)
	assert_eq(cz.craft(bag, armor, &"ember_guard", inv), Customize.RESULT_OK)


func test_unknown_piece_and_ability() -> void:
	var uid := bag.add_piece(&"rhen_tidewalker_hooks")
	assert_eq(cz.craft_error(bag, 999, &"ember_edge", inv), Customize.ERR_UNKNOWN_PIECE)
	assert_eq(cz.craft_error(bag, uid, &"no_such_ability", inv), Customize.ERR_UNKNOWN_ABILITY)


func test_explicit_slot_index() -> void:
	var uid := bag.add_piece(&"rhen_tidewalker_hooks")
	inv.add(&"gull_quill", 16)
	assert_eq(cz.craft(bag, uid, &"keen_sight", inv, 2), Customize.RESULT_OK)
	assert_eq(bag.slots_of(uid), [&"", &"", &"keen_sight"] as Array[StringName])
	assert_eq(cz.craft_error(bag, uid, &"steady_arm", inv, 2), Customize.ERR_SLOT_FILLED)
	assert_eq(cz.craft_error(bag, uid, &"steady_arm", inv, 7), Customize.ERR_NO_EMPTY_SLOT)


func test_candidates_list_what_fits() -> void:
	var uid := bag.add_piece(&"rhen_coral_hooks")
	var c := cz.candidates(bag, uid)
	assert_false(c.has(&"ember_edge"), "already on it")
	assert_true(c.has(&"tide_edge"))
	assert_false(c.has(&"ember_guard"), "armor-only")
	assert_true(c.has(&"full_net"))
	var full := bag.add_piece(&"rhen_salvage_hooks")
	bag.set_slot(full, 0, &"keen_sight")
	assert_eq(cz.candidates(bag, full), [] as Array[StringName])


func test_crafting_is_deterministic() -> void:
	var a := EquipmentBag.new(db)
	var b := EquipmentBag.new(db)
	var ia := Inventory.new(db)
	var ib := Inventory.new(db)
	for i in [ia, ib]:
		(i as Inventory).add(&"ember_coral", 8)
		(i as Inventory).add(&"tide_pearl", 8)
	for pair: Array in [[a, ia], [b, ib]]:
		var bg: EquipmentBag = pair[0]
		var uid := bg.add_piece(&"rhen_tidewalker_hooks")
		cz.craft(bg, uid, &"tide_edge", pair[1])
		cz.craft(bg, uid, &"ember_edge", pair[1])
	assert_eq(a.data, b.data)
	assert_eq(ia.counts, ib.counts)
