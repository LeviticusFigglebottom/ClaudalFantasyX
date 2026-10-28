extends TestCase
## The Reefball outfitter (ADR 0040, M3-C07-05): Reefball-only gear bought with lume and worn by the side in
## its matches, never battle equipment. Buying wears a piece when nothing of its kind is on; choosing an owned
## piece puts it on (in place of the other of its kind) or takes it off; a short purse refuses and changes
## nothing. The worn pieces reach the match (ReefballMatch.setup) and its HUD names them. The runner runs no
## frames and has no after_each.

const BAND := &"brass_thread_band"
const BAND_2 := &"kelp_dyed_band"
const FLOAT := &"cork_practice_float"

var flags: Dictionary = {}
var state: GameStateData
var db: ReefballDB
var model: ReefballOutfitterModel


func before_each() -> void:
	flags = {}
	state = GameStateData.new()
	state.currency = 1000
	db = ReefballDB.load_default()
	var bag := flags  # captured by value-reference, not through self: no cycle with the model
	model = ReefballOutfitterModel.new(
		db,
		Wallet.new(state, 9999),
		func(f: StringName) -> Variant: return bag.get(f, ""),
		func(f: StringName, v: Variant) -> void: bag[f] = v
	)


func test_rows_list_every_piece_with_its_price_then_leave() -> void:
	var rows := model.rows()
	assert_eq(rows.size(), db.gear.size() + 1)
	assert_eq(str(rows[0]["label"]), tr("RBL_GEAR_BRASS_THREAD_BAND"))
	assert_eq(str(rows[0]["right"]), tr("CURRENCY_AMOUNT") % 240)
	assert_eq(StringName(str(rows[-1]["id"])), ReefballOutfitterModel.ROW_LEAVE)
	assert_true(model.row_desc(BAND).contains(tr("RBL_STAT_GRIP") + " +1"), "what it adds, in words")
	assert_eq(model.row_desc(ReefballOutfitterModel.ROW_LEAVE), tr("RBL_OUTFIT_LEAVE_DESC"))
	assert_eq(model.row_line(ReefballOutfitterModel.ROW_LEAVE), {})


func test_buying_pays_owns_and_wears_when_nothing_of_its_kind_is_on() -> void:
	assert_true(bool(model.row_line(BAND)["ok"]))
	var line := model.choose(BAND)
	assert_true(bool(line["ok"]))
	assert_eq(state.currency, 1000 - 240)
	assert_true(model.is_owned(BAND) and model.is_worn(BAND))
	assert_eq(flags[&"rbl_worn_band"], "brass_thread_band", "the worn flag holds the id")
	model.choose(BAND_2)
	assert_true(model.is_owned(BAND_2))
	assert_false(model.is_worn(BAND_2), "a band is already on: bought, not worn")
	assert_eq(str(model.rows()[0]["right"]), tr("RBL_OUTFIT_WORN"))
	assert_eq(str(model.rows()[1]["right"]), tr("RBL_OUTFIT_OWNED"))


func test_choosing_an_owned_piece_swaps_or_takes_it_off() -> void:
	model.choose(BAND)
	model.choose(BAND_2)
	assert_true(
		str(model.row_line(BAND_2)["text"]).contains(tr("RBL_GEAR_BRASS_THREAD_BAND")), "names what it replaces"
	)
	model.choose(BAND_2)
	assert_true(model.is_worn(BAND_2) and not model.is_worn(BAND), "one band at a time")
	assert_true(str(model.row_line(BAND_2)["text"]).contains(tr("RBL_GEAR_KELP_DYED_BAND")))
	model.choose(BAND_2)
	assert_eq(model.worn_of("band"), &"", "taken off")
	assert_eq(
		model.row_line(BAND)["text"], tr("RBL_OUTFIT_WEAR_FMT").format({"name": tr("RBL_GEAR_BRASS_THREAD_BAND")})
	)
	assert_eq(model.choose(&"no_such_gear"), {})


func test_a_short_purse_refuses_and_changes_nothing() -> void:
	state.currency = 100
	var line := model.row_line(FLOAT)
	assert_false(bool(line["ok"]), "a refusal")
	assert_eq(model.choose(FLOAT), line)
	assert_eq(state.currency, 100)
	assert_false(model.is_owned(FLOAT))


func test_the_worn_pieces_reach_the_match_and_its_hud() -> void:
	model.choose(BAND)
	model.choose(FLOAT)
	var bag := flags
	var worn := ReefballOutfitterModel.worn_ids(db, func(f: StringName) -> Variant: return bag.get(f, ""))
	assert_eq(worn, [BAND, FLOAT] as Array[StringName])
	var m := ReefballMatch.new()
	assert_true(m.setup(db, &"tidecup_opening", 7, worn))
	assert_eq(m.worn_gear, worn)
	var hud := ReefballHud.new()
	ParityHost.scene_root().add_child(hud)
	hud.bind(m)
	assert_true(hud.gear_text().contains(tr("RBL_GEAR_BRASS_THREAD_BAND")), "the HUD names what the side wears")
	assert_true(hud.gear_text().contains(tr("RBL_GEAR_CORK_PRACTICE_FLOAT")))
	hud.get_parent().remove_child(hud)
	hud.free()


func test_town_services_opens_it_and_a_choice_buys() -> void:
	var host := Node.new()
	ParityHost.scene_root().add_child(host)
	var services := TownServices.new()
	host.add_child(services)
	services.model_factory = func(_key: String, _id: StringName) -> RefCounted: return model
	var menu := services.handle({"reefball_outfitter": "tamsule"}) as ReefballOutfitterMenu
	assert_true(menu != null and menu.is_open(), "the payload opens the outfitter")
	assert_eq(menu.title_text(), tr("RBL_OUTFIT_TITLE"))
	assert_eq(menu.purse_text(), tr("SHOP_MENU_PURSE_FMT").format({"amount": tr("CURRENCY_AMOUNT") % 1000}))
	assert_true(menu.status_text().contains(tr("RBL_GEAR_BRASS_THREAD_BAND")), "what choosing it does")
	menu.accept()
	assert_true(model.is_owned(BAND), "Confirm buys")
	assert_eq(menu.status_text(), tr("RBL_OUTFIT_BOUGHT_FMT").format({"name": tr("RBL_GEAR_BRASS_THREAD_BAND")}))
	assert_eq(str(menu.root_page().rows[0]["right"]), tr("RBL_OUTFIT_WORN"))
	menu.handle_input(_ev(&"ui_down"))
	assert_eq(menu.root_page().cursor, 1)
	menu.root_page().set_cursor(menu.root_page().rows.size() - 1, false)
	menu.accept()
	assert_false(menu.is_open(), "Leave closes")
	menu.motion().finish()
	host.get_tree().paused = false
	host.get_parent().remove_child(host)
	host.free()
	Audio.stop_all_players()


func _ev(action: StringName) -> InputEventAction:
	var ev := InputEventAction.new()
	ev.action = action
	ev.pressed = true
	return ev
