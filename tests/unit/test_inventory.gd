extends TestCase
## Inventory: stacking, caps, key items, deterministic ordering (M1-PRG-02).

var db: ItemDB


static func fixture() -> ItemDB:
	var rules := {
		"stack_cap": 99,
		"key_item_cap": 1,
		"currency_cap": 1000,
		"category_order": ["consumable", "material", "facet", "key"]
	}
	var rows := [
		{"id": "lantern", "category": "key", "name_key": "K"},
		{"id": "facet_power", "category": "facet", "facet": "facet_power", "price": 60},
		{"id": "tonic", "category": "consumable", "price": 40, "battle": {}},
		{"id": "coral", "category": "material", "price": 30, "stack_cap": 10},
		{"id": "salve", "category": "consumable", "price": 121},
	]
	var shop_rules := {"sell_ratio_num": 1, "sell_ratio_den": 2, "min_sell_price": 1}
	return ItemDB.from_tables({"items": {"rules": rules, "items": rows}, "shops": {"rules": shop_rules}})


func before_each() -> void:
	db = fixture()


func test_add_stacks_and_counts() -> void:
	var inv := Inventory.new(db)
	assert_eq(inv.add(&"tonic", 3), 3)
	assert_eq(inv.add(&"tonic", 2), 2)
	assert_eq(inv.count(&"tonic"), 5)
	assert_true(inv.has(&"tonic", 5))
	assert_false(inv.has(&"tonic", 6))
	assert_false(inv.has(&"tonic", 0), "has() needs a positive amount")


func test_global_cap_clamps_and_reports_added() -> void:
	var inv := Inventory.new(db)
	inv.add(&"tonic", 97)
	assert_eq(inv.room(&"tonic"), 2)
	assert_eq(inv.add(&"tonic", 5), 2, "only what fits is added")
	assert_eq(inv.count(&"tonic"), 99)
	assert_eq(inv.add(&"tonic", 1), 0)


func test_per_item_cap_overrides_global() -> void:
	var inv := Inventory.new(db)
	assert_eq(inv.add(&"coral", 25), 10)
	assert_eq(db.cap_of(&"coral"), 10)


func test_key_items_cap_at_one_and_never_sell() -> void:
	var inv := Inventory.new(db)
	assert_eq(inv.add(&"lantern", 3), 1)
	assert_eq(inv.count(&"lantern"), 1)
	assert_true(inv.is_key_item(&"lantern"))
	assert_false(inv.is_sellable(&"lantern"))
	assert_eq(db.sell_price_of(&"lantern"), 0)


func test_unknown_items_are_refused() -> void:
	var inv := Inventory.new(db)
	assert_eq(inv.add(&"no_such_thing", 1), 0)
	assert_eq(inv.room(&"no_such_thing"), 0)
	assert_true(inv.counts.is_empty())


func test_remove_is_all_or_nothing_and_erases_empty_stacks() -> void:
	var inv := Inventory.new(db)
	inv.add(&"tonic", 2)
	assert_false(inv.remove(&"tonic", 3))
	assert_eq(inv.count(&"tonic"), 2)
	assert_true(inv.remove(&"tonic", 2))
	assert_false(inv.counts.has("tonic"), "an empty stack is erased")
	assert_false(inv.remove(&"tonic", 0))


func test_ids_sort_by_category_then_data_order() -> void:
	var inv := Inventory.new(db)
	for iid: StringName in [&"lantern", &"salve", &"coral", &"facet_power", &"tonic"]:
		inv.add(iid, 1)
	var want: Array[StringName] = [&"tonic", &"salve", &"coral", &"facet_power", &"lantern"]
	assert_eq(inv.ids(), want)
	assert_eq(inv.ids_in(ItemDB.CATEGORY_CONSUMABLE), [&"tonic", &"salve"] as Array[StringName])


func test_ids_do_not_depend_on_insertion_order() -> void:
	var a := Inventory.new(db)
	var b := Inventory.new(db)
	for iid: StringName in [&"coral", &"tonic", &"lantern"]:
		a.add(iid, 1)
	for iid: StringName in [&"lantern", &"tonic", &"coral"]:
		b.add(iid, 1)
	assert_eq(a.ids(), b.ids())


func test_sell_price_uses_ratio_from_data_and_floors() -> void:
	assert_eq(db.sell_price_of(&"tonic"), 20)
	assert_eq(db.sell_price_of(&"salve"), 60, "121 / 2 floors to 60")


func test_wraps_backing_dictionary_in_place() -> void:
	var backing: Dictionary = {}
	var inv := Inventory.new(db, backing)
	inv.add(&"tonic", 4)
	assert_eq(int(backing["tonic"]), 4)


func test_facets_share_the_same_bag() -> void:
	var inv := Inventory.new(db)
	inv.add(&"facet_power", 2)
	var facets := inv.facets()
	assert_true(facets.consume(&"facet_power", 1))
	assert_eq(inv.count(&"facet_power"), 1)


func test_normalize_fixes_loaded_data() -> void:
	var backing := {"tonic": 3.0, "coral": 40, "ghost": 2, "salve": 0}
	var inv := Inventory.new(db, backing)
	assert_eq(inv.normalize(), ["ghost"] as Array[String])
	assert_eq(backing, {"tonic": 3, "coral": 10})
	assert_eq(typeof(backing["tonic"]), TYPE_INT)


func test_real_catalogue_has_slice_items_and_facets() -> void:
	var real := ItemDB.load_default()
	for iid: StringName in [&"salt_tonic", &"relighting_wick", &"drag_net", &"brass_lantern", &"net_float_charm"]:
		assert_true(real.has_item(iid), "missing %s" % iid)
	var rules := LatticeRules.load_file()
	for fid: StringName in rules.facets:
		assert_eq(real.category_of(fid), ItemDB.CATEGORY_FACET, "Facet %s is an item" % fid)
	assert_true(real.is_key_item(&"net_float_charm"))
	assert_true(real.stack_cap > 0 and real.currency_cap > 0)
