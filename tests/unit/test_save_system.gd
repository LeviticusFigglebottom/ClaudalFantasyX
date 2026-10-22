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
	assert_eq(int(migrated["version"]), 2)
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
