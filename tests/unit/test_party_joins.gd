extends TestCase
## M2-CMB-07 follow-up: heroes join the party with their starting gear on the join path
## (PartyJoins, first_playable.json "party"): Rhen on a fresh New Game, Asha and Toma when
## ch02_met_asha is set (Rhen and Asha active, Toma in reserve). Idempotent: a second join or a load
## never grants again, and worn gear is never replaced. A load also normalises inventory counts to whole numbers.

const TEST_DIR := "user://test_party_joins"
const T_SAVED := 1792489500

var _saved_state: GameStateData
var _saved_dir := ""
var _saved_clock: Callable


func before_each() -> void:
	_saved_state = Game.state
	_saved_dir = SaveSystem.save_dir
	_saved_clock = SaveSystem.clock
	SaveSystem.save_dir = TEST_DIR
	SaveSystem.clock = func() -> int: return T_SAVED
	_clear(TEST_DIR)


func test_a_fresh_new_game_has_rhen_geared() -> void:
	Game.new_game()
	assert_eq(Game.state.party_ids, [&"rhen"] as Array[StringName])
	var bag := _bag(Game.state)
	assert_eq(bag.base_of(bag.equipped(&"rhen", &"weapon")), &"rhen_salvage_hooks")
	assert_eq(bag.base_of(bag.equipped(&"rhen", &"armor")), &"rhen_patched_tether")
	assert_eq(bag.uids().size(), 2, "one weapon, one armor")
	_done()


func test_meeting_asha_brings_asha_and_toma_geared_once() -> void:
	Game.new_game()
	Game.set_flag(&"ch02_met_asha")
	assert_eq(Game.state.party_ids, [&"rhen", &"asha"] as Array[StringName])
	assert_eq(Game.state.reserve_ids, [&"toma"] as Array[StringName], "Toma joins the reserve (the slice's layout)")
	var bag := _bag(Game.state)
	for cid: StringName in [&"asha", &"toma"]:
		assert_ne(bag.equipped(cid, &"weapon"), EquipmentBag.NO_PIECE, "%s has a weapon" % cid)
		assert_ne(bag.equipped(cid, &"armor"), EquipmentBag.NO_PIECE, "%s has armor" % cid)
	var pieces := bag.uids().size()
	Game.set_flag(&"ch02_met_asha")  # set again: nothing more
	Game.set_flag(&"ch02_met_asha", false)
	assert_eq(PartyGoods.joined_members(Game.state).size(), 3)
	assert_eq(_bag(Game.state).uids().size(), pieces, "no second set of gear")
	_done()


func test_a_flag_without_a_join_changes_nothing() -> void:
	var st := GameStateData.new()
	var cfg := {"new_game": ["rhen"], "joins": {"ch02_met_asha": ["asha"]}}
	assert_eq(PartyJoins.on_flag(st, &"prologue_seen", true, cfg), [] as Array[StringName])
	assert_eq(PartyJoins.on_flag(st, &"ch02_met_asha", false, cfg), [] as Array[StringName], "unset: no join")
	assert_eq(st.party_ids, [] as Array[StringName])
	assert_eq(PartyJoins.on_flag(st, &"ch02_met_asha", true, cfg), [&"asha"] as Array[StringName])
	_done()


func test_worn_gear_is_never_replaced_by_a_join() -> void:
	var st := GameStateData.new()
	var item_db := ItemDB.load_default()
	var bag := EquipmentBag.new(item_db, st.equipment)
	var hooks := bag.add_piece(&"rhen_coral_hooks")
	bag.equip(&"rhen", hooks)
	var goods := PartyGoods.from_state(item_db, st)
	assert_true(goods.join(st, &"rhen"))
	assert_false(goods.join(st, &"rhen"), "already joined")
	assert_eq(st.party_ids, [&"rhen"] as Array[StringName])
	assert_eq(bag.equipped(&"rhen", &"weapon"), hooks, "the bought hooks stay on")
	assert_true(goods.join(st, &"ysolde", true), "a reserve join")
	assert_false(goods.join(st, &"ysolde"), "a reserve member has joined too")
	assert_eq(st.reserve_ids, [&"ysolde"] as Array[StringName])
	assert_eq(st.party_ids, [&"rhen"] as Array[StringName])
	assert_ne(bag.equipped(&"ysolde", &"weapon"), EquipmentBag.NO_PIECE)
	_done()


func test_a_load_after_joining_grants_nothing_more() -> void:
	Game.new_game()
	Game.set_flag(&"ch02_met_asha")
	var saved_equipment := Game.state.equipment.duplicate(true)
	assert_eq(SaveSystem.save_to_slot(1, Game.state), OK)
	var back := SaveSystem.load_from_slot(1)
	assert_true(back != null)
	if back != null:
		assert_eq(PartyGoods.joined_members(back), [&"rhen", &"asha", &"toma"] as Array[StringName])
		assert_eq(_bag(back).uids().size(), _bag(Game.state).uids().size(), "no double grant on load")
		var before := EquipmentBag.new(ItemDB.load_default(), saved_equipment)
		for cid: StringName in [&"rhen", &"asha", &"toma"]:
			for slot: StringName in [&"weapon", &"armor"]:
				assert_eq(_bag(back).equipped(cid, slot), before.equipped(cid, slot), "%s %s unchanged" % [cid, slot])
	_done()


func test_a_load_makes_inventory_counts_whole_numbers() -> void:
	var back := GameStateData.from_dict(
		JSON.parse_string(JSON.stringify({"inventory": {"salt_tonic": 3, "crab_carapace": 1}}))
	)
	assert_eq(back.inventory, {"salt_tonic": 3, "crab_carapace": 1})
	for iid: Variant in back.inventory:
		assert_eq(typeof(back.inventory[iid]), TYPE_INT, "%s" % iid)
	_done()


func _bag(st: GameStateData) -> EquipmentBag:
	return EquipmentBag.new(ItemDB.load_default(), st.equipment)


func _done() -> void:
	SaveSystem.cancel_pending_autosave()
	_clear(TEST_DIR)
	SaveSystem.save_dir = _saved_dir
	SaveSystem.clock = _saved_clock
	Game.state = _saved_state


func _clear(dir_path: String) -> void:
	if not DirAccess.dir_exists_absolute(dir_path):
		return
	for f in DirAccess.get_files_at(dir_path):
		DirAccess.remove_absolute(dir_path.path_join(f))
	DirAccess.remove_absolute(dir_path)
