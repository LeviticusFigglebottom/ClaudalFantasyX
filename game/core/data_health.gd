class_name DataHealth
extends RefCounted
## The one "data tables healthy" gate (M1-ARC-13, QA review-sweep-I S1; ADR 0018 Amendment 5).
##
## Every game/data table that saved state is judged against gets one named check: a Callable
## (state: GameStateData, may be null) -> String that returns "" while the table can be trusted
## and a short reason while it is missing, torn (fails to parse) or hollow (parses, but holds none
## of the rows a save refers to). SaveSystem owns one DataHealth (SaveSystem.data_health()) and
## asks it before it repairs a loaded save and before every write: while problem() is non-empty a
## load changes nothing and save_to_slot refuses with ERR_UNCONFIGURED. A table that breaks can
## then never turn into a save that has lost what the table could no longer describe.
##
## The tables and what in a save refers to them are listed in docs/kb/tech/architecture.md
## ("Data tables gate"). Add a check here, not a new per-table flag in SaveSystem, when a new
## table starts to judge saved state.

const ITEMS := &"items"
const LATTICE := &"lattice"
const BATTLE := &"battle"
const LOCATIONS := &"locations"
const FLAGS := &"flags"
const PARTY_REST := &"party_rest"
const BESTIARY := &"bestiary"
const SWELL := &"swell"

## The tables behind standard()'s checks, loaded on first use and cached. Tests replace one with
## a broken copy (LatticeBoard.load_board_from, BattleDB.load_dir, LocationRegistry.load_path)
## to simulate a broken build. Flags and party_rest are read from Game, which owns them.
var lattice_boards: Dictionary = {}
var lattice_rules: LatticeRules
var battle_db: BattleDB
var locations: LocationRegistry
## swell.json's "swell" object (BattleSwell.load_config), read on first use. Tests set it, with
## swell_loaded, to simulate a broken build.
var swell_config: Dictionary = {}
var swell_loaded := false

## Table name -> Callable(state: GameStateData) -> String, in the order they were added.
var _checks: Dictionary = {}


## The gate over every table saved state refers to. `item_check` judges the item tables (SaveSystem
## passes its item_tables_problem, which keeps the ARC-12 injection point).
static func standard(item_check: Callable) -> DataHealth:
	var h := DataHealth.new()
	h.add_check(ITEMS, item_check)
	# Bound methods, not lambdas: a lambda capturing `h` would keep it alive forever.
	h.add_check(LATTICE, h.lattice_problem)
	h.add_check(BATTLE, h.battle_problem)
	h.add_check(LOCATIONS, h.locations_problem)
	h.add_check(FLAGS, h.flags_problem)
	h.add_check(PARTY_REST, h.rest_problem)
	h.add_check(BESTIARY, h.bestiary_problem)
	h.add_check(SWELL, h.swell_problem)
	return h


## Adds (or replaces) the check for `table`.
func add_check(table: StringName, check: Callable) -> void:
	_checks[table] = check


func tables() -> Array[StringName]:
	var out: Array[StringName] = []
	for t: StringName in _checks:
		out.append(t)
	return out


## Why `table` cannot be trusted with `state` right now ("" when it can, or has no check).
func problem_of(table: StringName, state: GameStateData = null) -> String:
	if not _checks.has(table):
		return ""
	return str((_checks[table] as Callable).call(state))


## One "<table>: <reason>" line per broken table, in check order.
func problems(state: GameStateData = null) -> Array[String]:
	var out: Array[String] = []
	for t: StringName in _checks:
		var p := problem_of(t, state)
		if p != "":
			out.append("%s: %s" % [t, p])
	return out


## Every problem joined with "; ", or "" when all tables are healthy.
func problem(state: GameStateData = null) -> String:
	return "; ".join(problems(state))


func is_healthy(state: GameStateData = null) -> bool:
	return problem(state) == ""


# --- The standard checks --------------------------------------------------------------------------


## The Lattice board `board_id` (cached; LatticeBoard.load_board).
func lattice_board(board_id: StringName = LatticeBoard.DEFAULT_BOARD) -> LatticeBoard:
	if not lattice_boards.has(board_id):
		lattice_boards[board_id] = LatticeBoard.load_board(board_id)
	return lattice_boards[board_id] as LatticeBoard


## The board the save's Lattice progress names (the default board when it names none, or there is
## no state) and facets.json: Game.state.lattice. A save naming an id that is not a valid board id
## is a problem itself, and no path is built from it (M1-ARC-14, review-sweep-J nit).
func lattice_problem(state: GameStateData = null) -> String:
	var board_id := LatticeBoard.DEFAULT_BOARD
	if state != null and str(state.lattice.get("board", "")) != "":
		var named := str(state.lattice["board"])
		if not LatticeBoard.is_valid_id(named):
			return "the save names an invalid Lattice board id '%s'" % named
		board_id = StringName(named)
	var p := lattice_board(board_id).integrity_problem()
	if p != "":
		return p
	if lattice_rules == null:
		lattice_rules = LatticeRules.load_file()
	return lattice_rules.integrity_problem()


## characters.json and statuses.json (party_ids, reserve_ids, party_vitals), with the other
## battle tables.
func battle_problem(_state: GameStateData = null) -> String:
	if battle_db == null:
		battle_db = BattleDB.load_default()
	return battle_db.integrity_problem()


## locations.json (location_id, respawn, attuned_shrines).
func locations_problem(_state: GameStateData = null) -> String:
	if locations == null:
		locations = LocationRegistry.load_default()
	return locations.integrity_problem()


## flags.tres (flags), as Game loaded it.
func flags_problem(_state: GameStateData = null) -> String:
	var reg: FlagRegistry = Game.registry
	if reg == null:
		return "the flag registry is not loaded"
	return reg.integrity_problem()


## party_rest.json (the carried statuses in party_vitals), as Game loaded it.
func rest_problem(_state: GameStateData = null) -> String:
	return Game.rest_rules_problem(Game.rest_rules)


## enemies.json (the enemy ids in bestiary; M1-CMB-03), from the same battle tables.
func bestiary_problem(_state: GameStateData = null) -> String:
	if battle_db == null:
		battle_db = BattleDB.load_default()
	return battle_db.enemies_problem()


## swell.json (the modes in party_vitals' swell_mode and the ids in swell; M2-ARC-01): missing,
## torn, no modes, or a default mode it does not list (BattleSwell.config_problem).
func swell_problem(_state: GameStateData = null) -> String:
	if not swell_loaded:
		swell_config = BattleSwell.load_config()
		swell_loaded = true
	return BattleSwell.config_problem(swell_config)
