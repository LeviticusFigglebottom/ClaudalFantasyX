extends TestCase
## M1-ARC-13 (QA review-sweep-I S1; ADR 0018 Amendment 5): the data-tables gate.
##   - MUST: a torn, missing or empty lattice_*.json (or facets.json) never drops Lattice
##     progress: LatticeProgress freezes the saved dict, nothing is written back, and no save is
##     written while it is broken;
##   - unknown node ids, positions, characters and gates round-trip untouched on a sound board;
##   - every other table that saved state is judged against (items, battle characters and
##     statuses, locations, flags, party_rest) is behind the same gate, each tested torn, missing
##     and empty.

const TEST_DIR := "user://test_save_data_tables"
const DATA_DIR := "user://test_save_data_tables_data"
const T_SAVED := 1792489500
## The three ways a table breaks. Every guarded table is tested with each.
const TORN := &"torn"
const MISSING := &"missing"
const EMPTY := &"empty"
const BREAKS: Array[StringName] = [TORN, MISSING, EMPTY]
const FLAGS_HEAD := (
	'[gd_resource type="Resource" script_class="FlagRegistry" load_steps=2 format=3]\n\n'
	+ '[ext_resource type="Script" path="res://game/core/flag_registry.gd" id="1_flags"]\n\n'
	+ '[resource]\nscript = ExtResource("1_flags")\n'
)

var _saved_dir := ""
var _saved_clock: Callable
var _saved_enabled := true
var _saved_state: GameStateData
var _saved_play_clock := true
var _saved_registry: FlagRegistry
var _saved_rest: Dictionary = {}


func before_each() -> void:
	_saved_dir = SaveSystem.save_dir
	_saved_clock = SaveSystem.clock
	_saved_enabled = SaveSystem.autosave_enabled
	_saved_state = Game.state
	_saved_play_clock = Game.play_clock_running
	_saved_registry = Game.registry
	_saved_rest = Game.rest_rules
	SaveSystem.save_dir = TEST_DIR
	SaveSystem.clock = func() -> int: return T_SAVED
	SaveSystem.autosave_enabled = true
	SaveSystem.cancel_pending_autosave()
	_mend()
	_clear(TEST_DIR)
	_clear(DATA_DIR)
	Game.state = GameStateData.new()


# --- the gate itself ------------------------------------------------------------------------------


func test_one_gate_covers_every_table_and_the_shipped_build_is_healthy() -> void:
	var expected: Array[StringName] = [
		DataHealth.ITEMS,
		DataHealth.LATTICE,
		DataHealth.BATTLE,
		DataHealth.LOCATIONS,
		DataHealth.FLAGS,
		DataHealth.PARTY_REST,
	]
	assert_eq(SaveSystem.data_health().tables(), expected)
	assert_eq(SaveSystem.data_tables_problem(), "", "the shipped tables are sound")
	assert_eq(SaveSystem.data_tables_problem(_ch6_state()), "")
	assert_eq(SaveSystem.report_data_tables(), "", "nothing to report at startup")
	var h := DataHealth.new()
	h.add_check(&"a", func(_st: GameStateData) -> String: return "")
	h.add_check(&"b", func(_st: GameStateData) -> String: return "torn")
	assert_eq(h.problems(), ["b: torn"] as Array[String])
	assert_false(h.is_healthy())
	assert_eq(h.problem_of(&"none"), "", "a table without a check is not a problem")
	_done()


# --- MUST: the Lattice ----------------------------------------------------------------------------


func test_a_broken_lattice_board_names_itself() -> void:
	assert_eq(LatticeBoard.load_board().integrity_problem(), "", "the shipped board is sound")
	for how in BREAKS:
		var board := _board(how)
		assert_ne(board.integrity_problem(), "", "%s board" % how)
		assert_eq(board.id, LatticeBoard.DEFAULT_BOARD, "%s board keeps its id" % how)
	assert_eq(LatticeRules.load_file().integrity_problem(), "", "the shipped rules are sound")
	for how in BREAKS:
		assert_ne(_rules(how).integrity_problem(), "", "%s facets.json" % how)
	_done()


## The review-sweep-I path: a broken board at battle setup, then a victory, then a save. Nothing
## is placed, nothing is written back, the save is refused, and the real board sees it all again.
func test_a_broken_lattice_board_never_drops_or_saves_over_progress() -> void:
	var st := _ch6_state()
	var saved_lattice: Variant = _norm(st.lattice)
	assert_eq(SaveSystem.save_to_slot(1, st), OK, "saved with the real tables")
	for how in BREAKS:
		var board := _board(how)
		var p := LatticeProgress.from_dict(st.lattice, board, LatticeRules.load_file())
		assert_true(p.is_frozen(), "%s: frozen" % how)
		assert_true(p.travelers.is_empty(), "%s: nobody placed" % how)
		assert_false(p.add_character(&"rhen"), "%s: nobody joins" % how)
		assert_eq(p.award_battle(&"rhen", 500), 0, "%s: a victory awards nothing" % how)
		assert_eq(_norm(p.to_dict()), saved_lattice, "%s: to_dict is the save as it was" % how)
		assert_false(p.save_into(st), "%s: the write-back (battle_rewards.gd) is refused" % how)
		assert_eq(_norm(st.lattice), saved_lattice, "%s: the state keeps its progress" % how)
	_assert_gate_holds(DataHealth.LATTICE, _break_board)
	_assert_gate_holds(DataHealth.LATTICE, _break_rules)
	_done()


## A sound board's from_dict, then a victory write-back, then a save and a load: unknown node ids,
## a lost position, a character with no start and a gate the board lacks all round-trip.
func test_unknown_lattice_ids_round_trip_untouched() -> void:
	var st := _ch6_state()
	var rhen: Dictionary = st.lattice["characters"]["rhen"]
	(rhen["activated"] as Array).insert(1, "retired_node")
	rhen["position"] = "retired_node"
	st.lattice["characters"]["nobody"] = {
		"position": "nobody_start",
		"activated": ["nobody_start", "nb_01"],
		"movement_points": 3,
		"lattice_points": 4,
		"movement_earned": 5,
	}
	(st.lattice["opened_gates"] as Array).append("retired_gate")
	var saved_lattice: Variant = _norm(st.lattice)
	assert_eq(SaveSystem.save_to_slot(1, st), OK)
	var back := SaveSystem.load_from_slot(1)
	var p := LatticeProgress.from_dict(back.lattice, LatticeBoard.load_board(), LatticeRules.load_file())
	assert_false(p.is_frozen())
	var t := p.traveler(&"rhen")
	assert_eq(t.position, &"rhen_start", "rhen stands on the start meanwhile")
	assert_true(t.activated.has(&"retired_node"), "the unknown activation is kept")
	assert_true(p.save_into(back), "a sound board writes back")
	assert_eq(_norm(back.lattice), saved_lattice, "the write-back changes nothing")
	assert_eq(SaveSystem.save_to_slot(1, back), OK)
	var again := SaveSystem.load_from_slot(1)
	assert_eq(_norm(again.lattice), saved_lattice, "save, load and save again: untouched")
	assert_eq(t.movement_points, int(rhen["movement_points"]))
	var step := LatticeBoard.load_board().neighbors(&"rhen_start")[0]
	assert_eq(p.move(&"rhen", step), LatticeProgress.RESULT_OK)
	assert_eq(p.to_dict()["characters"]["rhen"]["position"], String(step), "a move replaces the saved position")
	_done()


# --- the other tables -----------------------------------------------------------------------------


func test_broken_item_tables_close_the_gate() -> void:
	for how in BREAKS:
		var db := _items(how)
		assert_ne(db.items_problem(), "", "%s items.json" % how)
		var backing := {"salt_tonic": 3, "retired_item": 2}
		assert_eq(Inventory.new(db, backing).normalize(), [] as Array[String], "%s: normalize drops nothing" % how)
		assert_eq(backing, {"salt_tonic": 3, "retired_item": 2}, "%s: the bag is untouched" % how)
	_assert_gate_holds(DataHealth.ITEMS, _break_items)
	_done()


func test_broken_battle_tables_close_the_gate() -> void:
	assert_eq(BattleDB.load_default().integrity_problem(), "")
	for how in BREAKS:
		assert_ne(_battle(how).integrity_problem(), "", "%s characters.json" % how)
	_assert_gate_holds(DataHealth.BATTLE, _break_battle)
	_done()


func test_broken_locations_close_the_gate() -> void:
	assert_eq(LocationRegistry.load_default().integrity_problem(), "")
	for how in BREAKS:
		assert_ne(_locations(how).integrity_problem(), "", "%s locations.json" % how)
	_assert_gate_holds(DataHealth.LOCATIONS, _break_locations)
	_done()


func test_broken_flag_registry_closes_the_gate() -> void:
	assert_eq(FlagRegistry.load_path(Game.FLAGS_PATH).integrity_problem(), "")
	for how in BREAKS:
		assert_ne(_flags(how).integrity_problem(), "", "%s flags.tres" % how)
	_assert_gate_holds(DataHealth.FLAGS, _break_flags)
	_done()


func test_broken_party_rest_closes_the_gate_and_records_nothing() -> void:
	assert_eq(Game.rest_rules_problem(Game.load_rest_rules()), "")
	var db := BattleDB.load_default()
	for how in BREAKS:
		assert_ne(Game.rest_rules_problem(_rest(how)), "", "%s party_rest.json" % how)
		Game.state = _ch6_state()
		var before: Variant = _norm(Game.state.party_vitals)
		Game.rest_rules = _rest(how)
		var c := BattleCombatant.from_dict(&"rhen", BattleCombatant.TEAM_PARTY, db.characters[&"rhen"])
		c.hp = 1
		Game.record_party(&"test", &"victory", [c])
		assert_eq(_norm(Game.state.party_vitals), before, "%s: rhen keeps his saved poison" % how)
		Game.rest_rules = _saved_rest
	_assert_gate_holds(DataHealth.PARTY_REST, _break_rest)
	_done()


# --- the shared probe -----------------------------------------------------------------------------


## For each way `table` breaks (`breaker`: Callable(how) that installs the broken table): the gate
## names it, a load keeps the save exactly as written, every write (manual, empty slot, autosave)
## is refused before a file is touched, and once mended the same slot loads and saves again.
func _assert_gate_holds(table: StringName, breaker: Callable) -> void:
	var st := _ch6_state()
	assert_eq(SaveSystem.save_to_slot(1, st), OK, "%s: saved with the real tables" % table)
	assert_eq(SaveSystem.save_to_slot(SaveSystem.AUTOSAVE_SLOT, st, SaveSystem.REASON_CHAPTER), OK)
	var slot_text := FileAccess.get_file_as_string(SaveSystem.slot_path(1))
	var auto_text := FileAccess.get_file_as_string(SaveSystem.slot_path(SaveSystem.AUTOSAVE_SLOT))
	var saved: Variant = _norm((JSON.parse_string(slot_text) as Dictionary)["state"])
	for how in BREAKS:
		var label := "%s %s" % [how, table]
		breaker.call(how)
		var problem := SaveSystem.data_tables_problem(st)
		assert_true(problem.begins_with("%s: " % table), "%s: the gate names it (%s)" % [label, problem])
		assert_ne(SaveSystem.report_data_tables(), "", "%s: reported" % label)
		var back := SaveSystem.load_from_slot(1)
		assert_true(back != null, "%s: the save still loads" % label)
		if back == null:
			continue
		assert_eq(_norm(back.to_dict()), saved, "%s: loaded exactly as saved" % label)
		assert_eq(SaveSystem.save_to_slot(1, back), ERR_UNCONFIGURED, "%s: a manual save is refused" % label)
		assert_eq(SaveSystem.save_to_slot(2, back), ERR_UNCONFIGURED, "%s: even into an empty slot" % label)
		assert_false(SaveSystem.slot_exists(2))
		assert_false(FileAccess.file_exists(SaveSystem.slot_path(1) + SaveSystem.TEMP_SUFFIX), "%s: no temp" % label)
		Game.state = back
		assert_eq(SaveSystem.autosave(), ERR_UNCONFIGURED, "%s: the autosave is refused" % label)
		assert_eq(FileAccess.get_file_as_string(SaveSystem.slot_path(1)), slot_text, "%s: slot 1 untouched" % label)
		assert_eq(
			FileAccess.get_file_as_string(SaveSystem.slot_path(SaveSystem.AUTOSAVE_SLOT)),
			auto_text,
			"%s: slot 0 untouched" % label
		)
		_mend()
		assert_eq(SaveSystem.data_tables_problem(st), "", "%s: mended" % label)
	assert_eq(SaveSystem.save_to_slot(1, SaveSystem.load_from_slot(1)), OK, "%s: saves again once mended" % table)


func _break_board(how: StringName) -> void:
	SaveSystem.data_health().lattice_boards[LatticeBoard.DEFAULT_BOARD] = _board(how)


func _break_rules(how: StringName) -> void:
	SaveSystem.data_health().lattice_rules = _rules(how)


func _break_items(how: StringName) -> void:
	SaveSystem._item_db = _items(how)


func _break_battle(how: StringName) -> void:
	SaveSystem.data_health().battle_db = _battle(how)


func _break_locations(how: StringName) -> void:
	SaveSystem.data_health().locations = _locations(how)


func _break_flags(how: StringName) -> void:
	Game.registry = _flags(how)


func _break_rest(how: StringName) -> void:
	Game.rest_rules = _rest(how)


## Every table back to the shipped files.
func _mend() -> void:
	SaveSystem._item_db = null
	SaveSystem._health = null
	if _saved_registry != null:
		Game.registry = _saved_registry
	Game.rest_rules = _saved_rest


# --- broken copies of each table ------------------------------------------------------------------


func _board(how: StringName) -> LatticeBoard:
	var dir := _dir("board", how)
	_put(
		LatticeBoard.path_for(LatticeBoard.DEFAULT_BOARD, dir),
		how,
		'{"board": {"id": "standard"}, "nodes": [',
		'{"board": {"id": "standard"}, "nodes": [], "edges": []}'
	)
	return LatticeBoard.load_board_from(dir, LatticeBoard.DEFAULT_BOARD)


func _rules(how: StringName) -> LatticeRules:
	var path := _dir("rules", how) + "/facets.json"
	_put(path, how, '{"rules": {"move_cost": 1', "{}")
	return LatticeRules.load_file(path)


func _items(how: StringName) -> ItemDB:
	var dir := _dir("items", how)
	_copy_tables(ItemDB.DATA_DIR, dir, ItemDB.TABLES)
	_put(dir + "/items.json", how, '{"rules": {"stack_cap": 99', '{"rules": {}, "items": []}')
	return ItemDB.load_dir(dir)


func _battle(how: StringName) -> BattleDB:
	var dir := _dir("battle", how)
	_copy_tables(BattleDB.DATA_DIR, dir, BattleDB.TABLES)
	_put(dir + "/characters.json", how, '{"characters": [{"id": "rhen"', '{"characters": []}')
	return BattleDB.load_dir(dir)


func _locations(how: StringName) -> LocationRegistry:
	var path := _dir("locations", how) + "/locations.json"
	_put(path, how, '{"default_location": "ch02/haluna", "locations": [', '{"locations": []}')
	return LocationRegistry.load_path(path)


## The torn registry is a real one saved in binary and cut in half: a torn text .tres would make
## Godot print "Parse Error", which ci_local.sh reads as a GDScript parse error.
func _flags(how: StringName) -> FlagRegistry:
	var dir := _dir("flags", how)
	if how != TORN:
		var path := dir + "/flags.tres"
		_put(path, how, "", FLAGS_HEAD + "flags = {}\n")
		return FlagRegistry.load_path(path)
	var whole := FlagRegistry.new()
	whole.flags = {"test_flag": "Reserved for automated tests."}
	var res_path := dir + "/flags.res"
	assert_eq(ResourceSaver.save(whole, res_path), OK)
	var bytes := FileAccess.get_file_as_bytes(res_path)
	var f := FileAccess.open(res_path, FileAccess.WRITE)
	f.store_buffer(bytes.slice(0, bytes.size() / 2))
	f.close()
	return FlagRegistry.load_path(res_path)


func _rest(how: StringName) -> Dictionary:
	var path := _dir("rest", how) + "/party_rest.json"
	_put(path, how, '{"carried_statuses": ["poison"', "{}")
	return Game.load_rest_rules(path)


## A fresh folder per table and break (a reused path could be served from a cache).
func _dir(table: String, how: StringName) -> String:
	var dir := "%s/%s_%s" % [DATA_DIR, table, how]
	DirAccess.make_dir_recursive_absolute(dir)
	return dir


## Writes the `how` variant of a table at `path`: `torn` text, `empty` text, or nothing at all.
func _put(path: String, how: StringName, torn: String, empty: String = "") -> void:
	if how == TORN:
		_write_raw(path, torn)
	elif how == EMPTY:
		_write_raw(path, empty)
	elif FileAccess.file_exists(path):
		DirAccess.remove_absolute(path)


func _copy_tables(from_dir: String, to_dir: String, tables: Array[String]) -> void:
	for table in tables:
		_write_raw("%s/%s.json" % [to_dir, table], FileAccess.get_file_as_string("%s/%s.json" % [from_dir, table]))


# --- helpers --------------------------------------------------------------------------------------


## A chapter 6 run: rhen and asha on the real board (rhen one node out, with something activated
## and movement banked), a bag, a flag, a location and a carried poison.
func _ch6_state() -> GameStateData:
	var st := GameStateData.new()
	st.chapter = 6
	st.play_time_sec = 21600.0
	st.location_id = &"ch02/haluna"
	st.party_ids = [&"rhen", &"asha"] as Array[StringName]
	st.inventory = {"salt_tonic": 3}
	st.flags = {"test_flag": true}
	st.party_vitals = {"rhen": {"hp": 40, "statuses": ["poison"]}}
	var board := LatticeBoard.load_board()
	var rules := LatticeRules.load_file()
	var p := LatticeProgress.new(board, rules)
	assert_true(p.add_character(&"rhen") and p.add_character(&"asha"))
	var t := p.traveler(&"rhen")
	t.movement_points = 9
	var step := board.neighbors(&"rhen_start")[0]
	assert_eq(p.move(&"rhen", step), LatticeProgress.RESULT_OK)
	var inv := FacetInventory.new({})
	var facet := p.activation_facet(&"rhen")
	if facet != &"":
		inv.add(facet, rules.facet_cost(board.lattice_node(step)))
		assert_eq(p.activate(&"rhen", inv), LatticeProgress.RESULT_OK)
	t.lattice_points = 7
	t.movement_earned = 12
	st.lattice = p.to_dict()
	return st


## A value as it reads back from a save file (JSON numbers are floats).
func _norm(v: Variant) -> Variant:
	return JSON.parse_string(JSON.stringify(v))


func _write_raw(path: String, text: String) -> void:
	DirAccess.make_dir_recursive_absolute(path.get_base_dir())
	var f := FileAccess.open(path, FileAccess.WRITE)
	f.store_string(text)
	f.close()


func _done() -> void:
	SaveSystem.cancel_pending_autosave()
	SaveSystem._new_run = false
	_mend()
	_clear(TEST_DIR)
	_clear(DATA_DIR)
	SaveSystem.save_dir = _saved_dir
	SaveSystem.clock = _saved_clock
	SaveSystem.autosave_enabled = _saved_enabled
	Game.state = _saved_state
	Game.play_clock_running = _saved_play_clock


func _clear(dir_path: String) -> void:
	if not DirAccess.dir_exists_absolute(dir_path):
		return
	for sub in DirAccess.get_directories_at(dir_path):
		_clear(dir_path.path_join(sub))
	for f in DirAccess.get_files_at(dir_path):
		DirAccess.remove_absolute(dir_path.path_join(f))
	DirAccess.remove_absolute(dir_path)
