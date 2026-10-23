extends TestCase
## Shop: flag-gated stock, buy/sell with lume, sell ratio from data (M1-PRG-02).

var db: ItemDB
var state: GameStateData
var party: PartyGoods
var flags: FlagReader


func before_each() -> void:
	db = ItemDB.load_default()
	state = GameStateData.new()
	party = PartyGoods.from_state(db, state)
	flags = FlagReader.new()
	flags.values["ch02_met_asha"] = true


func test_shop_is_closed_until_its_flag() -> void:
	var market := Shop.new(db, &"haluna_market")
	var closed := FlagReader.new()
	assert_false(market.is_open(closed))
	assert_eq(market.stock(closed), [] as Array[StringName])
	party.wallet.earn(100)
	assert_eq(market.buy(&"salt_tonic", 1, party, closed), Shop.ERR_CLOSED)
	assert_true(market.is_open(flags))


func test_stock_follows_story_flags_in_data_order() -> void:
	var market := Shop.new(db, &"haluna_market")
	var before := market.stock(flags)
	assert_eq(before[0], &"salt_tonic")
	assert_false(before.has(&"relighting_wick"))
	flags.values["ch03_drownbell_defeated"] = true
	var after := market.stock(flags)
	assert_true(after.has(&"relighting_wick"))
	assert_eq(after.slice(0, before.size()), before, "new rows append, old order holds")


func test_buy_spends_lume_and_adds_items() -> void:
	var market := Shop.new(db, &"haluna_market")
	party.wallet.earn(100)
	assert_eq(market.buy_price(&"salt_tonic", 2), 80)
	assert_eq(market.buy(&"salt_tonic", 2, party, flags), Shop.RESULT_OK)
	assert_eq(state.currency, 20)
	assert_eq(party.inventory.count(&"salt_tonic"), 2)


func test_cannot_overspend() -> void:
	var market := Shop.new(db, &"haluna_market")
	party.wallet.earn(79)
	assert_eq(market.buy(&"salt_tonic", 2, party, flags), Shop.ERR_NO_FUNDS)
	assert_eq(state.currency, 79)
	assert_eq(party.inventory.count(&"salt_tonic"), 0)


func test_buy_refuses_items_not_in_stock_and_bad_counts() -> void:
	var market := Shop.new(db, &"haluna_market")
	party.wallet.earn(5000)
	assert_eq(market.buy(&"relighting_wick", 1, party, flags), Shop.ERR_NOT_IN_STOCK)
	assert_eq(market.buy(&"brass_lantern", 1, party, flags), Shop.ERR_NOT_IN_STOCK)
	assert_eq(market.buy(&"salt_tonic", 0, party, flags), Shop.ERR_BAD_COUNT)
	assert_eq(Shop.new(db, &"nowhere").buy(&"salt_tonic", 1, party, flags), Shop.ERR_UNKNOWN_SHOP)


func test_buy_refuses_past_the_stack_cap() -> void:
	var market := Shop.new(db, &"haluna_market")
	party.wallet.earn(9000)
	party.inventory.add(&"salt_tonic", db.stack_cap - 1)
	assert_eq(market.buy(&"salt_tonic", 2, party, flags), Shop.ERR_NO_ROOM)
	assert_eq(market.buy(&"salt_tonic", 1, party, flags), Shop.RESULT_OK)


func test_equipment_shop_creates_pieces() -> void:
	var forge := Shop.new(db, &"haluna_forge")
	party.wallet.earn(1000)
	assert_eq(forge.buy(&"rhen_coral_hooks", 1, party, flags), Shop.RESULT_OK)
	assert_eq(state.currency, 1000 - db.price_of(&"rhen_coral_hooks"))
	var uids := party.equipment.uids()
	assert_eq(uids.size(), 1)
	assert_eq(party.equipment.abilities_of(uids[0]), [&"ember_edge"] as Array[StringName])
	assert_eq(forge.buy(&"toma_reach_tide_shield", 1, party, flags), Shop.ERR_NOT_IN_STOCK)


func test_sell_uses_ratio_and_floors() -> void:
	var market := Shop.new(db, &"haluna_market")
	party.inventory.add(&"lit_age_brass", 3)
	party.inventory.add(&"bitterleaf", 1)
	assert_eq(market.sell_price(&"lit_age_brass"), 90)
	assert_eq(market.sell(&"lit_age_brass", 2, party), Shop.RESULT_OK)
	assert_eq(state.currency, 180)
	assert_eq(party.inventory.count(&"lit_age_brass"), 1)
	assert_eq(market.sell_price(&"bitterleaf"), 7, "15 / 2 floors to 7")


func test_cannot_sell_key_items_or_more_than_held() -> void:
	var market := Shop.new(db, &"haluna_market")
	party.inventory.add(&"brass_lantern", 1)
	party.inventory.add(&"salt_tonic", 1)
	assert_eq(market.sell(&"brass_lantern", 1, party), Shop.ERR_NOT_SELLABLE)
	assert_eq(market.sell(&"salt_tonic", 2, party), Shop.ERR_NOT_ENOUGH)
	assert_eq(market.sell(&"salt_tonic", -1, party), Shop.ERR_BAD_COUNT)
	assert_eq(party.inventory.count(&"brass_lantern"), 1)


func test_sell_piece_only_when_unequipped() -> void:
	var forge := Shop.new(db, &"haluna_forge")
	party.equipment.grant_starting(&"rhen")
	var worn := party.equipment.equipped(&"rhen", ItemDB.SLOT_WEAPON)
	assert_eq(forge.sell_piece(worn, party), Shop.ERR_EQUIPPED)
	var spare := party.equipment.add_piece(&"rhen_coral_hooks")
	assert_eq(forge.sell_piece(spare, party), Shop.RESULT_OK)
	assert_eq(state.currency, db.sell_price_of(&"rhen_coral_hooks"))
	assert_false(party.equipment.has_piece(spare))
	assert_eq(forge.sell_piece(spare, party), Shop.ERR_UNKNOWN_PIECE)


func test_wallet_caps_and_never_goes_negative() -> void:
	var w := Wallet.new(state, 100)
	assert_eq(w.earn(150), 100)
	assert_eq(w.amount(), 100)
	assert_false(w.spend(101))
	assert_false(w.can_afford(-1))
	assert_true(w.spend(100))
	assert_eq(w.earn(-5), 0)


func test_flag_reader_reads_through_an_access_object() -> void:
	var access := DialogueFlagAccess.new()
	access.set_flag(&"ch02_met_asha", true)
	var reader := FlagReader.from_access(access)
	assert_true(reader.is_set(&"ch02_met_asha"))
	assert_false(reader.is_set(&"ch03_drownbell_defeated"))
	assert_true(reader.is_set(&""), "no gate means open")
	access.set_flag(&"test_counter", 2)
	assert_true(reader.is_set(&"test_counter"))
	assert_true(Shop.new(db, &"haluna_market").is_open(reader))
