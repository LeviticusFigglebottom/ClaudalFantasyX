extends TestCase
## M2-CMB-07: a live victory pays the engine's lume into the purse and its drops into the bag
## (BattleRewards.pay through Wallet and Inventory over Game.state), the victory panel lists them,
## a save keeps them, and live battles wear the party's gear (Full Net doubles the lume).
## Tests and capture fixtures list the spoils but never pay them.

const SANDBOX := "res://game/battle/scene/battle_sandbox.tscn"
const SEED := 20261022
const ENCOUNTER := &"sandbox_reef"
const TEST_DIR := "user://test_battle_rewards_payout"
const T_SAVED := 1792489500
## formulas.md § Rewards: Reef Crab 24 + Lantern Eel 20 + Gull Harrier 18.
const SANDBOX_LUME := 62

var ctl: BattleController
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
	Game.state = GameStateData.new()
	ctl = null


# --- live victory --------------------------------------------------------------------------------


func test_a_live_victory_pays_exactly_what_the_engine_computed() -> void:
	Game.state.currency = 7
	Game.state.inventory = {"salt_tonic": 2}
	_controller(true)
	_play_elegant_answer()
	assert_eq(ctl.engine.outcome, BattleEngine.OUTCOME_VICTORY, "this seed wins with the Toma swap")
	var lume := ctl.engine.currency_award()
	var drops := ctl.engine.drop_awards()
	assert_eq(lume, SANDBOX_LUME, "no gear, no multiplier")
	assert_eq(Game.state.currency, 7 + lume)
	var want := {"salt_tonic": 2}
	for iid: StringName in drops:
		want[String(iid)] = int(want.get(String(iid), 0)) + int(drops[iid])
	assert_eq(Game.state.inventory, want, "every drop is in the bag, nothing else changed")
	assert_eq(int(ctl.last_spoils[BattleRewards.KEY_LUME]), lume)
	assert_eq(int(ctl.last_spoils[BattleRewards.KEY_LUME_ADDED]), lume)
	assert_eq(int(ctl.last_spoils[BattleRewards.KEY_PURSE]), 7 + lume)
	assert_true(bool(ctl.last_spoils[BattleRewards.KEY_PAID]))
	_done()


func test_the_victory_panel_lists_the_lume_purse_and_each_drop() -> void:
	_controller(true)
	_play_elegant_answer()
	var spoils := _spoil_rows()
	var drops := ctl.engine.drop_awards()
	assert_eq(spoils.size(), 1 + drops.size(), "one lume row and one row per dropped item")
	assert_eq(str(spoils[0]["label"]), "Lume")
	assert_eq(str(spoils[0]["xp_text"]), "+%d lume" % SANDBOX_LUME)
	assert_eq(str(spoils[0]["moves_text"]), "purse %d lume" % Game.state.currency)
	var db := ItemDB.load_default()
	var i := 1
	for iid: StringName in drops:
		assert_eq(str(spoils[i]["label"]), tr(str(db.item(iid)["name_key"])), "%s by name" % iid)
		assert_eq(str(spoils[i]["xp_text"]), "×%d" % int(drops[iid]))
		i += 1
	var fighters := ctl.hud.result.result_rows.filter(func(r: Dictionary) -> bool: return not r.has("spoils"))
	assert_eq(fighters.size() + spoils.size(), ctl.hud.result.result_rows.size(), "fighters first, then spoils")
	_done()


func test_a_save_and_load_keep_the_paid_lume_and_drops() -> void:
	Game.state.party_ids = [&"rhen"] as Array[StringName]
	_controller(true)
	_play_elegant_answer()
	assert_eq(ctl.engine.outcome, BattleEngine.OUTCOME_VICTORY)
	var purse := Game.state.currency
	var bag := Game.state.inventory.duplicate(true)
	assert_eq(purse, SANDBOX_LUME)
	assert_eq(SaveSystem.save_to_slot(1, Game.state), OK)
	var back := SaveSystem.load_from_slot(1)
	assert_true(back != null)
	if back != null:
		assert_eq(back.currency, purse)
		assert_eq(back.inventory, bag, "the same bag")
		for iid: Variant in back.inventory:
			assert_eq(typeof(back.inventory[iid]), TYPE_INT, "%s loads as a whole number, not a JSON float" % iid)
	_done()


func test_a_defeat_pays_nothing() -> void:
	Game.state.currency = 40
	Game.state.party_vitals = {"rhen": {"hp": 300}}  # test_battle_vitals' losing start
	_controller(true)
	var guard := 0
	while ctl.engine.outcome == &"" and guard < 200:
		guard += 1
		ctl.act(&"attack", [ctl.engine.living_foes_of(ctl.engine.current)[0].id])
	assert_eq(ctl.engine.outcome, BattleEngine.OUTCOME_DEFEAT, "the naive policy loses")
	assert_eq(Game.state.currency, 40)
	assert_eq(Game.state.inventory, {})
	assert_eq(_spoil_rows(), [] as Array[Dictionary])
	_done()


func test_a_test_battle_lists_the_spoils_but_never_pays() -> void:
	Game.state.currency = 5
	_controller(false)
	_play_elegant_answer()
	assert_eq(ctl.engine.outcome, BattleEngine.OUTCOME_VICTORY)
	assert_eq(Game.state.currency, 5, "persist_progress off: the save is untouched")
	assert_eq(Game.state.inventory, {})
	assert_false(bool(ctl.last_spoils[BattleRewards.KEY_PAID]))
	var spoils := _spoil_rows()
	assert_eq(str(spoils[0]["xp_text"]), "+%d lume" % SANDBOX_LUME)
	assert_eq(str(spoils[0]["moves_text"]), "", "no purse line when nothing was paid")
	_done()


func test_a_capture_fixture_never_pays() -> void:
	_controller(true, false)
	ctl.start_fixture(BattleFixture.load_fixture(&"victory"))
	ctl.engine._finish(BattleEngine.OUTCOME_VICTORY)
	BattleRewards.new().award_victory(ctl)
	assert_eq(Game.state.currency, 0)
	assert_eq(Game.state.inventory, {})
	assert_false(bool(ctl.last_spoils[BattleRewards.KEY_PAID]))
	_done()


# --- pay() on a bare engine ----------------------------------------------------------------------


func test_pay_respects_the_purse_cap_and_full_stacks() -> void:
	var item_db := ItemDB.load_default()
	var e := _won_engine({&"crab_carapace": 2, &"salt_tonic": 1})
	var st := GameStateData.new()
	st.currency = item_db.currency_cap - 10
	st.inventory = {"crab_carapace": item_db.cap_of(&"crab_carapace") - 1}
	var spoils := BattleRewards.pay(e, Wallet.new(st, item_db.currency_cap), Inventory.new(item_db, st.inventory))
	assert_eq(int(spoils[BattleRewards.KEY_LUME]), SANDBOX_LUME)
	assert_eq(int(spoils[BattleRewards.KEY_LUME_ADDED]), 10, "the cap holds the rest back")
	assert_eq(st.currency, item_db.currency_cap)
	assert_eq(int(spoils[BattleRewards.KEY_KEPT][&"crab_carapace"]), 1, "one fitted the stack")
	assert_eq(int(spoils[BattleRewards.KEY_KEPT][&"salt_tonic"]), 1)
	assert_eq(st.inventory["crab_carapace"], item_db.cap_of(&"crab_carapace"))
	var rows := BattleRewards.new().spoil_rows(spoils, item_db)
	assert_eq(rows.size(), 3)
	assert_eq(str(rows[1]["moves_text"]), "bag full, left behind", "the stack was full")
	assert_eq(str(rows[2]["moves_text"]), "")
	_done()


func test_pay_without_a_victory_pays_nothing() -> void:
	var e := _won_engine({&"salt_tonic": 1})
	e.outcome = BattleEngine.OUTCOME_ESCAPED
	var item_db := ItemDB.load_default()
	var st := GameStateData.new()
	var spoils := BattleRewards.pay(e, Wallet.new(st, item_db.currency_cap), Inventory.new(item_db, st.inventory))
	assert_eq(int(spoils[BattleRewards.KEY_LUME]), 0)
	assert_eq(st.currency, 0)
	assert_eq(st.inventory, {})
	assert_eq(BattleRewards.new().spoil_rows(spoils, item_db), [] as Array[Dictionary])
	_done()


# --- live gear and the starting purse ------------------------------------------------------------


func test_a_live_battle_wears_the_party_gear_and_full_net_doubles_the_lume() -> void:
	var item_db := ItemDB.load_default()
	var bag := EquipmentBag.new(item_db, Game.state.equipment)
	var hooks := bag.add_piece(&"rhen_coral_hooks")  # 2 slots: Ember Edge, one empty; strength +1
	assert_true(bag.set_slot(hooks, 1, &"full_net"))
	assert_eq(bag.equip(&"rhen", hooks), EquipmentBag.RESULT_OK)
	var saved := Game.state.equipment.duplicate(true)
	var bdb := BattleDB.load_default()
	var plan := {
		"active": [&"rhen", &"asha"] as Array[StringName],
		"reserve": [] as Array[StringName],
		"encounter": ENCOUNTER,
		"seed": SEED,
	}
	var bare := BattleEngine.new()
	BattleVitals.setup(bare, bdb, plan, null, false)
	var live := BattleEngine.new()
	BattleVitals.setup(live, bdb, plan, null, true)
	var ids: Array[StringName] = [&"rhen"]
	assert_eq(live.find(&"rhen").strength, bare.find(&"rhen").strength + 1, "the piece's stats")
	assert_eq(int(live.currency_multiplier.call(ids)), 2, "Full Net")
	assert_false(bare.currency_multiplier.is_valid(), "a test battle wears nothing")
	assert_eq(Game.state.equipment, saved, "a battle never writes the bag")
	_done()


func test_a_new_game_opens_with_the_starting_purse() -> void:
	var item_db := ItemDB.load_default()
	assert_eq(item_db.starting_currency, 100, "economy.md § Currency: the B03 purse")
	Game.new_game()
	assert_eq(Game.state.currency, item_db.starting_currency)
	SaveSystem.cancel_pending_autosave()
	_done()


# --- helpers -------------------------------------------------------------------------------------


## A sandbox engine already won, with `drops` as its rolled drops.
func _won_engine(drops: Dictionary) -> BattleEngine:
	var e := BattleEngine.new()
	var active: Array[StringName] = [&"rhen", &"asha"]
	e.setup(BattleDB.load_default(), active, [] as Array[StringName], ENCOUNTER, SEED)
	e.outcome = BattleEngine.OUTCOME_VICTORY
	e._drops = drops
	return e


func _spoil_rows() -> Array[Dictionary]:
	var out: Array[Dictionary] = []
	for r in ctl.hud.result.result_rows:
		if r.has(BattleRewards.ROW_SPOILS):
			out.append(r)
	return out


func _controller(persist: bool, start: bool = true) -> void:
	var packed := load(SANDBOX) as PackedScene
	ctl = packed.instantiate() as BattleController
	ctl.auto_start = false
	ctl.pacing_scale = 0.0
	ctl.persist_progress = persist
	ctl.bestiary.roll_openings = false  # rewards, not openings: a rolled ambush would change the fight
	var tree := Engine.get_main_loop() as SceneTree
	(tree.current_scene if tree.current_scene != null else tree.root).add_child(ctl)
	if not start:
		return
	var p := LatticeProgress.new(LatticeBoard.load_board(), LatticeRules.load_file())
	for cid: StringName in [&"rhen", &"asha", &"toma", &"ysolde"]:
		p.add_character(cid)
	var active: Array[StringName] = [&"rhen", &"asha"]
	var reserve: Array[StringName] = [&"toma", &"ysolde"]
	ctl.start_battle(active, reserve, ENCOUNTER, SEED, p)


## The vitals test's winning line (test_battle_vitals.gd): swap Toma in for Asha, then everyone hits
## the weakest foe.
func _play_elegant_answer() -> void:
	var guard := 0
	while ctl.engine.outcome == &"" and guard < 300:
		guard += 1
		var e := ctl.engine
		if e.find(&"asha") in e.party_active and e.find(&"toma") in e.party_reserve:
			ctl.swap_members(&"asha", &"toma")
			continue
		var foes := e.living_foes_of(e.current)
		var weakest := foes[0]
		for f in foes:
			if f.hp < weakest.hp:
				weakest = f
		ctl.act(&"attack", [weakest.id])


func _done() -> void:
	if ctl != null:
		ctl.get_parent().remove_child(ctl)
		ctl.free()
		ctl = null
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
