class_name PartyGoods
extends RefCounted
## Everything the party owns that shops, Customize and rewards touch: the item bag, the
## equipment pieces and loadouts, and the purse. from_state() wraps a GameStateData in place,
## so changes made through these objects are what gets saved.

var db: ItemDB
var inventory: Inventory
var equipment: EquipmentBag
var wallet: Wallet


static func from_state(item_db: ItemDB, state: GameStateData) -> PartyGoods:
	var g := PartyGoods.new()
	g.db = item_db
	g.inventory = Inventory.new(item_db, state.inventory)
	g.equipment = EquipmentBag.new(item_db, state.equipment)
	g.wallet = Wallet.new(state, item_db.currency_cap)
	return g
