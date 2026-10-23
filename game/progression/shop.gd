class_name Shop
extends RefCounted
## One shop from game/data/items/shops.json (SPEC §6.6 towns, §6.11). Stock is gated by story
## flags, read through an injected FlagReader so the logic stays headless and testable.
##
## Rules (docs/kb/design/economy.md): the shop is open once its requires_flag is set; a stock
## row shows once its own requires_flag is set; buying costs ItemDB.price_of × count and needs
## room in the bag; any shop buys any sellable item or unequipped piece at ItemDB.sell_price_of.
## Key items never sell. Every action returns RESULT_OK or an ERR_* and *_error() previews it.

const RESULT_OK := &"ok"
const ERR_UNKNOWN_SHOP := &"unknown_shop"
const ERR_CLOSED := &"shop_closed"
const ERR_NOT_IN_STOCK := &"not_in_stock"
const ERR_BAD_COUNT := &"bad_count"
const ERR_NO_ROOM := &"no_room"
const ERR_NO_FUNDS := &"not_enough_currency"
const ERR_NOT_SELLABLE := &"not_sellable"
const ERR_NOT_ENOUGH := &"not_enough_items"
const ERR_UNKNOWN_PIECE := &"unknown_piece"
const ERR_EQUIPPED := &"piece_equipped"

var db: ItemDB
var id: StringName
var row: Dictionary


func _init(item_db: ItemDB, shop_id: StringName) -> void:
	db = item_db
	id = shop_id
	row = db.shops.get(shop_id, {})


func exists() -> bool:
	return not row.is_empty()


func name_key() -> String:
	return str(row.get("name_key", ""))


func is_open(flags: FlagReader) -> bool:
	return exists() and flags.is_set(StringName(str(row.get("requires_flag", ""))))


## Goods on sale right now, in data order. Empty while the shop is closed.
func stock(flags: FlagReader) -> Array[StringName]:
	var out: Array[StringName] = []
	if not is_open(flags):
		return out
	for entry: Variant in row.get("stock", []):
		var e: Dictionary = entry
		if flags.is_set(StringName(str(e.get("requires_flag", "")))):
			out.append(StringName(str(e["item"])))
	return out


func buy_price(goods_id: StringName, count: int = 1) -> int:
	return db.price_of(goods_id) * count


func sell_price(goods_id: StringName, count: int = 1) -> int:
	return db.sell_price_of(goods_id) * count


func buy_error(goods_id: StringName, count: int, party: PartyGoods, flags: FlagReader) -> StringName:
	if not is_open(flags):
		return ERR_CLOSED if exists() else ERR_UNKNOWN_SHOP
	if count <= 0:
		return ERR_BAD_COUNT
	if not stock(flags).has(goods_id):
		return ERR_NOT_IN_STOCK
	if not db.is_equipment(goods_id) and party.inventory.room(goods_id) < count:
		return ERR_NO_ROOM
	if not party.wallet.can_afford(buy_price(goods_id, count)):
		return ERR_NO_FUNDS
	return RESULT_OK


## Buys `count` of an item, or `count` new pieces of equipment. Returns RESULT_OK or an ERR_*.
func buy(goods_id: StringName, count: int, party: PartyGoods, flags: FlagReader) -> StringName:
	var err := buy_error(goods_id, count, party, flags)
	if err != RESULT_OK:
		return err
	party.wallet.spend(buy_price(goods_id, count))
	if db.is_equipment(goods_id):
		for i in count:
			party.equipment.add_piece(goods_id)
	else:
		party.inventory.add(goods_id, count)
	return RESULT_OK


func sell_error(item_id: StringName, count: int, party: PartyGoods) -> StringName:
	if not exists():
		return ERR_UNKNOWN_SHOP
	if count <= 0:
		return ERR_BAD_COUNT
	if not party.inventory.is_sellable(item_id):
		return ERR_NOT_SELLABLE
	if not party.inventory.has(item_id, count):
		return ERR_NOT_ENOUGH
	return RESULT_OK


## Sells `count` of a bag item. Lume beyond the purse cap is lost (the UI should warn).
func sell(item_id: StringName, count: int, party: PartyGoods) -> StringName:
	var err := sell_error(item_id, count, party)
	if err != RESULT_OK:
		return err
	party.inventory.remove(item_id, count)
	party.wallet.earn(sell_price(item_id, count))
	return RESULT_OK


func sell_piece_error(uid: int, party: PartyGoods) -> StringName:
	if not exists():
		return ERR_UNKNOWN_SHOP
	if not party.equipment.has_piece(uid):
		return ERR_UNKNOWN_PIECE
	if party.equipment.wearer_of(uid) != &"":
		return ERR_EQUIPPED
	if sell_price(party.equipment.base_of(uid)) <= 0:
		return ERR_NOT_SELLABLE
	return RESULT_OK


## Sells an unequipped piece at its base piece's sell price (crafted abilities add nothing).
func sell_piece(uid: int, party: PartyGoods) -> StringName:
	var err := sell_piece_error(uid, party)
	if err != RESULT_OK:
		return err
	var price := sell_price(party.equipment.base_of(uid))
	party.equipment.remove_piece(uid)
	party.wallet.earn(price)
	return RESULT_OK
