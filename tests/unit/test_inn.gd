extends TestCase
## M2-UI-06: Inn (game/progression/inn.gd) over shops.json "inns": open on its flag, a rest costs
## the data price, a refused rest changes nothing, and a paid rest calls the heal exactly once.

var db: ItemDB
var state: GameStateData
var party: PartyGoods
var flags: FlagReader
var healed: Array[StringName] = []


func before_each() -> void:
	db = ItemDB.load_default()
	state = GameStateData.new()
	party = PartyGoods.from_state(db, state)
	flags = FlagReader.new()
	flags.values["ch02_met_asha"] = true
	healed = []


func _heal(source: StringName) -> void:
	healed.append(source)


func test_haluna_has_an_inn_with_a_data_price() -> void:
	var inn := Inn.new(db, &"haluna_inn")
	assert_true(inn.exists())
	assert_eq(inn.name_key(), "INN_HALUNA")
	assert_eq(inn.desc_key(), "INN_HALUNA_DESC")
	assert_eq(inn.price(), int(db.inns[&"haluna_inn"]["price"]), "the price is the data's")
	assert_true(inn.price() > 0)


func test_a_rest_pays_and_heals_once() -> void:
	var inn := Inn.new(db, &"haluna_inn")
	party.wallet.earn(inn.price() + 5)
	assert_eq(inn.rest_error(party, flags), Inn.RESULT_OK)
	assert_eq(inn.rest(party, flags, _heal), Inn.RESULT_OK)
	assert_eq(state.currency, 5)
	assert_eq(healed, [&"haluna_inn"] as Array[StringName], "one heal, from this inn")


func test_refusals_change_nothing() -> void:
	var inn := Inn.new(db, &"haluna_inn")
	party.wallet.earn(inn.price() - 1)
	assert_eq(inn.rest(party, flags, _heal), Inn.ERR_NO_FUNDS)
	assert_eq(state.currency, inn.price() - 1)
	assert_eq(inn.rest(party, FlagReader.new(), _heal), Inn.ERR_CLOSED, "shut until its flag")
	assert_false(inn.is_open(FlagReader.new()))
	var none := Inn.new(db, &"no_such_inn")
	assert_false(none.exists())
	assert_eq(none.price(), 0)
	assert_eq(none.rest(party, flags, _heal), Inn.ERR_UNKNOWN_INN)
	assert_eq(healed.size(), 0, "no refused rest heals")


func test_an_unset_heal_still_pays_and_fixtures_load_inns() -> void:
	var fixture := ItemDB.from_tables({"shops": {"rules": {}, "inns": [{"id": "free_bed", "price": 0}]}})
	var inn := Inn.new(fixture, &"free_bed")
	var goods := PartyGoods.from_state(fixture, GameStateData.new())
	assert_true(inn.is_open(FlagReader.new()), "no requires_flag: always open")
	assert_eq(inn.rest(goods, FlagReader.new(), Callable()), Inn.RESULT_OK, "a free bed needs no lume")


func test_a_reader_from_a_fresh_access_keeps_reading_the_game_flags() -> void:
	var saved := Game.state
	Game.state = GameStateData.new()
	var live := FlagReader.from_access(GameFlagAccess.new())
	assert_false(live.is_set(&"ch02_met_asha"))
	Game.set_flag(&"ch02_met_asha", true)
	assert_true(live.is_set(&"ch02_met_asha"), "the access outlives from_access()")
	assert_true(Inn.new(db, &"haluna_inn").is_open(live))
	Game.state = saved
