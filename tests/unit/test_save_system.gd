extends TestCase

var saves: Node


func before_each() -> void:
	saves = (load("res://game/core/save_system.gd") as GDScript).new()


func test_round_trip_preserves_state() -> void:
	var s := GameStateData.new()
	s.flags = {"prologue_seen": true}
	s.party_ids = [&"rhen", &"asha"] as Array[StringName]
	s.inventory = {"potion": 3}
	s.currency = 250
	s.chapter = 2
	s.location_id = &"tidewall"
	var back: GameStateData = saves.deserialize(JSON.parse_string(JSON.stringify(saves.serialize(s))))
	assert_eq(back.flags.get("prologue_seen"), true)
	assert_eq(back.party_ids, [&"rhen", &"asha"] as Array[StringName])
	assert_eq(int(back.inventory.get("potion")), 3)
	assert_eq(back.currency, 250)
	assert_eq(back.chapter, 2)
	assert_eq(back.location_id, &"tidewall")
	saves.free()


func test_serialized_save_is_versioned() -> void:
	var d: Dictionary = saves.serialize(GameStateData.new())
	assert_eq(int(d["version"]), saves.SAVE_VERSION)
	saves.free()


func test_migrates_v0_coin_to_currency() -> void:
	var v0 := {"version": 0, "coin": 77, "chapter": 1}
	var back: GameStateData = saves.deserialize(v0)
	assert_true(back != null)
	assert_eq(back.currency, 77)
	assert_eq(back.chapter, 1)
	saves.free()


func test_rejects_newer_save() -> void:
	var future := {"version": 999, "state": {}}
	assert_eq(saves.migrate(future), {})
	saves.free()


func test_migrates_v1_adds_empty_lattice_progress() -> void:
	var v1 := {"version": 1, "state": {"currency": 5, "chapter": 2}}
	var migrated: Dictionary = saves.migrate(v1)
	assert_eq(int(migrated["version"]), saves.SAVE_VERSION)
	var back: GameStateData = saves.deserialize(v1)
	assert_eq(back.currency, 5)
	assert_eq(back.lattice, {"board": "standard", "characters": {}, "opened_gates": []})
	var p := LatticeProgress.from_dict(back.lattice, LatticeBoard.load_board(), LatticeRules.load_file())
	assert_true(p.travelers.is_empty())
	assert_true(p.add_character(&"rhen"), "heroes join on their start")
	saves.free()


func test_migrates_v0_all_the_way_to_current() -> void:
	var back: GameStateData = saves.deserialize({"version": 0, "coin": 9})
	assert_eq(back.currency, 9)
	assert_eq(back.lattice.get("board"), "standard")
	saves.free()


func test_v2_lattice_is_not_overwritten() -> void:
	var lattice := {"board": "standard", "characters": {"rhen": {"position": "rh_01"}}, "opened_gates": []}
	var back: GameStateData = saves.deserialize({"version": 2, "state": {"lattice": lattice}})
	assert_eq(back.lattice, lattice)
	saves.free()


func test_save_version_is_4() -> void:
	assert_eq(saves.SAVE_VERSION, 4)
	saves.free()


func test_migrates_v2_adds_empty_equipment_and_normalizes_inventory() -> void:
	var v2 := {
		"version": 2,
		"state": {"currency": 120, "inventory": {"salt_tonic": 3.0, "bitterleaf": 0, "drag_net": -2}},
	}
	var step: Dictionary = saves._migrate_v2_to_v3(v2)
	assert_eq(int(step["version"]), 3, "the v2 -> v3 step itself is unchanged")
	var migrated: Dictionary = saves.migrate(v2)
	assert_eq(int(migrated["version"]), saves.SAVE_VERSION)
	assert_eq(step["state"]["equipment"], migrated["state"]["equipment"])
	var st: Dictionary = migrated["state"]
	assert_eq(st["equipment"], {"next_uid": 1, "owned": {}, "loadout": {}})
	assert_eq(st["inventory"], {"salt_tonic": 3})
	assert_eq(typeof(st["inventory"]["salt_tonic"]), TYPE_INT, "counts become ints")
	var back: GameStateData = saves.deserialize(v2)
	assert_eq(back.currency, 120)
	var db := ItemDB.load_default()
	var goods := PartyGoods.from_state(db, back)
	assert_eq(goods.inventory.count(&"salt_tonic"), 3)
	assert_true(goods.equipment.grant_starting(&"rhen"), "heroes get starting gear after migrating")
	saves.free()


func test_v3_equipment_round_trips() -> void:
	var db := ItemDB.load_default()
	var s := GameStateData.new()
	var goods := PartyGoods.from_state(db, s)
	goods.equipment.grant_starting(&"rhen")
	goods.inventory.add(&"ember_coral", 4)
	goods.wallet.earn(500)
	var weapon := goods.equipment.equipped(&"rhen", &"weapon")
	assert_eq(Customize.new(db).craft(goods.equipment, weapon, &"ember_edge", goods.inventory), Customize.RESULT_OK)
	var back: GameStateData = saves.deserialize(JSON.parse_string(JSON.stringify(saves.serialize(s))))
	var again := PartyGoods.from_state(db, back)
	var uid := again.equipment.equipped(&"rhen", &"weapon")
	assert_eq(uid, weapon)
	assert_eq(again.equipment.abilities_of(uid), [&"ember_edge"] as Array[StringName])
	assert_eq(again.wallet.amount(), 500)
	assert_eq(again.inventory.count(&"ember_coral"), 0)
	var next := again.equipment.add_piece(&"rhen_coral_hooks")
	assert_true(next > weapon, "uids keep counting after a load")
	saves.free()


func test_v2_save_without_inventory_migrates() -> void:
	var back: GameStateData = saves.deserialize({"version": 2, "state": {"chapter": 3}})
	assert_eq(back.inventory, {})
	assert_eq(back.equipment.get("next_uid"), 1)
	saves.free()
