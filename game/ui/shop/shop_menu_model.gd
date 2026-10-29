class_name ShopMenuModel
extends RefCounted
## The words and choices of the shop menu (M2-UI-06, SPEC §6.6), Node-free, over one Shop and a
## PartyGoods (docs/kb/design/economy.md). The view is ShopMenu. Every string is a loc key from
## game/data/loc/strings.csv; amounts read through CURRENCY_AMOUNT ("%d lume").
##
## Rows (MenuPage dictionaries) carry their goods: "goods" (item or equipment id) and, on the
## sell page, "uid" (an owned equipment piece; NO_PIECE for a bag item). Every row stays
## choosable, so the cursor can rest on a refused one and the line under the page says why
## (pillar 4); a refused row's price is in the disabled color. Prices: Shop.buy_price and
## sell_price. Refusals: Shop.buy_error, sell_error and sell_piece_error, word for word.

const ROW_BUY := &"buy"
const ROW_SELL := &"sell"
const ROW_LEAVE := &"leave"
const ROOT_IDS: Array[StringName] = [ROW_BUY, ROW_SELL, ROW_LEAVE]
const ROOT_LABEL_KEYS := {ROW_BUY: "SHOP_MENU_BUY", ROW_SELL: "SHOP_MENU_SELL", ROW_LEAVE: "SHOP_MENU_LEAVE"}
const ROOT_DESC_KEYS := {
	ROW_BUY: "SHOP_MENU_BUY_DESC",
	ROW_SELL: "SHOP_MENU_SELL_DESC",
	ROW_LEAVE: "SHOP_MENU_LEAVE_DESC",
}
const NO_PIECE := EquipmentBag.NO_PIECE
const AMOUNT_KEY := "CURRENCY_AMOUNT"
const PURSE_KEY := "SHOP_MENU_PURSE_FMT"
const HELD_KEY := "SHOP_MENU_HELD_FMT"
const NO_PRICE_KEY := "SHOP_MENU_NO_PRICE"
const BUY_TITLE_KEY := "SHOP_MENU_BUY_TITLE"
const SELL_TITLE_KEY := "SHOP_MENU_SELL_TITLE"
const SELL_EMPTY_KEY := "SHOP_MENU_SELL_EMPTY"
const BUY_EMPTY_KEY := "SHOP_MENU_BUY_EMPTY"
const BUY_PREVIEW_KEY := "SHOP_MENU_BUY_PREVIEW_FMT"
const SELL_PREVIEW_KEY := "SHOP_MENU_SELL_PREVIEW_FMT"
const BOUGHT_KEY := "SHOP_MENU_BOUGHT_FMT"
const SOLD_KEY := "SHOP_MENU_SOLD_FMT"
const PURSE_FULL_KEY := "SHOP_MENU_PURSE_FULL_FMT"
const FOR_HERO_KEY := "SHOP_MENU_FOR_FMT"
const UNKNOWN_SHOP_TITLE_KEY := "SHOP_MENU_UNKNOWN_TITLE"
## Shop ERR_* -> the loc key that says it ({name}, {count}, {price}, {purse}, {room}, {held},
## {wearer} are filled in where the line uses them).
const REFUSAL_KEYS := {
	Shop.ERR_UNKNOWN_SHOP: "SHOP_ERR_UNKNOWN_SHOP",
	Shop.ERR_CLOSED: "SHOP_ERR_CLOSED",
	Shop.ERR_NOT_IN_STOCK: "SHOP_ERR_NOT_IN_STOCK",
	Shop.ERR_BAD_COUNT: "SHOP_ERR_BAD_COUNT",
	Shop.ERR_NO_ROOM: "SHOP_ERR_NO_ROOM_FMT",
	Shop.ERR_NO_FUNDS: "SHOP_ERR_NO_FUNDS_FMT",
	Shop.ERR_NOT_SELLABLE: "SHOP_ERR_NOT_SELLABLE_FMT",
	Shop.ERR_NOT_ENOUGH: "SHOP_ERR_NOT_ENOUGH_FMT",
	Shop.ERR_UNKNOWN_PIECE: "SHOP_ERR_UNKNOWN_PIECE",
	Shop.ERR_EQUIPPED: "SHOP_ERR_EQUIPPED_FMT",
}

var db: ItemDB
var shop: Shop
var party: PartyGoods
var flags: FlagReader
## Hero id -> name loc key (characters.json), for "For Rhen" and "Rhen is wearing it".
var name_keys: Dictionary = {}


func _init(
	item_db: ItemDB, with_shop: Shop, goods: PartyGoods, flag_reader: FlagReader, hero_names: Dictionary = {}
) -> void:
	db = item_db
	shop = with_shop
	party = goods
	flags = flag_reader
	name_keys = hero_names


## The live menu: the shop `shop_id` over Game.state, with flags read through Game.get_flag.
static func from_game(shop_id: StringName) -> ShopMenuModel:
	var item_db := ItemDB.load_default()
	return ShopMenuModel.new(
		item_db,
		Shop.new(item_db, shop_id),
		PartyGoods.from_state(item_db, Game.state),
		FlagReader.from_access(GameFlagAccess.new()),
		FieldMenuModel.name_keys_from(BattleDB.load_default().characters)
	)


func title() -> String:
	return _tr(shop.name_key()) if shop.exists() else _tr(UNKNOWN_SHOP_TITLE_KEY)


func lume(amount: int) -> String:
	return _tr(AMOUNT_KEY) % amount


func purse_text() -> String:
	return _tr(PURSE_KEY).format({"amount": lume(party.wallet.amount())})


## Why the shop can't trade at all (shut, or unknown), or StringName() when it is open.
func closed_reason() -> StringName:
	if not shop.exists():
		return Shop.ERR_UNKNOWN_SHOP
	if not shop.is_open(flags):
		return Shop.ERR_CLOSED
	return Shop.RESULT_OK


## Buy, Sell, Leave. Buy and Sell are off while the shop is shut; the line says why.
func root_rows() -> Array[Dictionary]:
	var open := closed_reason() == Shop.RESULT_OK
	var out: Array[Dictionary] = []
	for id in ROOT_IDS:
		out.append({"id": id, "label": _tr(ROOT_LABEL_KEYS[id]), "enabled": open or id == ROW_LEAVE})
	return out


func root_desc(id: StringName) -> String:
	var why := closed_reason()
	if why != Shop.RESULT_OK and id != ROW_LEAVE:
		return refusal_text(why, &"")
	return _tr(str(ROOT_DESC_KEYS.get(id, "")))


func buy_title() -> String:
	return _tr(BUY_TITLE_KEY)


func sell_title() -> String:
	return _tr(SELL_TITLE_KEY)


## The stock on sale now: name, how many the party holds, and the price of one.
func buy_rows() -> Array[Dictionary]:
	var out: Array[Dictionary] = []
	for gid in shop.stock(flags):
		var ok := shop.buy_error(gid, 1, party, flags) == Shop.RESULT_OK
		(
			out
			. append(
				{
					"id": gid,
					"goods": gid,
					"glyph": MenuGlyph.for_goods(gid),
					"uid": NO_PIECE,
					"label": goods_name(gid),
					"mp": _tr(HELD_KEY).format({"count": held(gid)}),
					"right": lume(shop.buy_price(gid)),
					"right_role": &"text" if ok else &"text_disabled",
					"enabled": true,
				}
			)
		)
	return out


## The bag (listing order, Inventory.ids), then every owned piece (ascending uid). Key items and
## worn pieces are listed too, priced "—", so the line can say why they won't sell.
func sell_rows() -> Array[Dictionary]:
	var out: Array[Dictionary] = []
	for iid in party.inventory.ids():
		var ok := shop.sell_error(iid, 1, party) == Shop.RESULT_OK
		(
			out
			. append(
				{
					"id": StringName("item:%s" % iid),
					"goods": iid,
					"glyph": MenuGlyph.for_goods(iid),
					"uid": NO_PIECE,
					"label": goods_name(iid),
					"mp": _tr(HELD_KEY).format({"count": party.inventory.count(iid)}),
					"right": lume(shop.sell_price(iid)) if ok else _tr(NO_PRICE_KEY),
					"right_role": &"text" if ok else &"text_disabled",
					"enabled": true,
				}
			)
		)
	for uid in party.equipment.uids():
		var base := party.equipment.base_of(uid)
		var ok := shop.sell_piece_error(uid, party) == Shop.RESULT_OK
		var wearer := party.equipment.wearer_of(uid)
		(
			out
			. append(
				{
					"id": StringName("piece:%d" % uid),
					"goods": base,
					"glyph": MenuGlyph.for_goods(base),
					"uid": uid,
					"label": goods_name(base),
					"mp": hero_name(wearer) if wearer != &"" else "",
					"right": lume(shop.sell_price(base)) if ok else _tr(NO_PRICE_KEY),
					"right_role": &"text" if ok else &"text_disabled",
					"enabled": true,
				}
			)
		)
	return out


## How many of `goods_id` the party owns: bag count, or pieces with that base.
func held(goods_id: StringName) -> int:
	if not db.is_equipment(goods_id):
		return party.inventory.count(goods_id)
	var n := 0
	for uid in party.equipment.uids():
		if party.equipment.base_of(uid) == goods_id:
			n += 1
	return n


## The most a buy of `goods_id` may ask for: up to `limit`, and no more than the bag has room for.
func max_buy(goods_id: StringName, limit: int) -> int:
	if db.is_equipment(goods_id):
		return maxi(limit, 1)
	return clampi(party.inventory.room(goods_id), 1, maxi(limit, 1))


## The most a sale may offer: what the bag holds (1 for a piece).
func max_sell(row: Dictionary, limit: int) -> int:
	if int(row.get("uid", NO_PIECE)) != NO_PIECE:
		return 1
	return clampi(party.inventory.count(StringName(str(row.get("goods", "")))), 1, maxi(limit, 1))


## What the highlighted goods are: its description, and whose it is for a piece.
func goods_desc(goods_id: StringName) -> String:
	var row := _goods_row(goods_id)
	var text := _tr(str(row.get("desc_key", "")))
	if db.is_equipment(goods_id):
		var who := db.character_of(goods_id)
		if who != &"":
			text += "\n" + _tr(FOR_HERO_KEY).format({"name": hero_name(who)})
	return text


## {text, ok}: what buying `count` of `goods_id` would cost, or why it can't happen.
func buy_line(goods_id: StringName, count: int) -> Dictionary:
	var err := shop.buy_error(goods_id, count, party, flags)
	if err != Shop.RESULT_OK:
		return {"text": refusal_text(err, goods_id, count), "ok": false}
	var price := shop.buy_price(goods_id, count)
	return {
		"text": _tr(BUY_PREVIEW_KEY).format({"count": count, "name": goods_name(goods_id), "price": lume(price)}),
		"ok": true,
	}


## {text, ok}: what selling `count` from a sell row would earn, or why the shop won't take it.
## Warns when the purse cap would swallow part of the price (Shop.sell drops the excess).
func sell_line(row: Dictionary, count: int) -> Dictionary:
	var goods_id := StringName(str(row.get("goods", "")))
	var uid := int(row.get("uid", NO_PIECE))
	var piece := uid != NO_PIECE
	var err := shop.sell_piece_error(uid, party) if piece else shop.sell_error(goods_id, count, party)
	if err != Shop.RESULT_OK:
		return {"text": refusal_text(err, goods_id, count, uid), "ok": false}
	var n := 1 if piece else count
	var price := shop.sell_price(goods_id, n)
	var text := _tr(SELL_PREVIEW_KEY).format({"count": n, "name": goods_name(goods_id), "price": lume(price)})
	var lost := price - maxi(party.wallet.cap - party.wallet.amount(), 0)
	if lost > 0:
		text += " " + _tr(PURSE_FULL_KEY).format({"lost": lume(lost)})
	return {"text": text, "ok": true}


## Buys `count` of `goods_id`. Returns {ok, text}: the receipt line, or the refusal.
func buy(goods_id: StringName, count: int) -> Dictionary:
	var price := shop.buy_price(goods_id, count)
	var err := shop.buy(goods_id, count, party, flags)
	if err != Shop.RESULT_OK:
		return {"text": refusal_text(err, goods_id, count), "ok": false}
	return {
		"text": _tr(BOUGHT_KEY).format({"count": count, "name": goods_name(goods_id), "price": lume(price)}),
		"ok": true,
	}


## Sells `count` from a sell row (a bag item, or the one piece). Returns {ok, text}.
func sell(row: Dictionary, count: int) -> Dictionary:
	var goods_id := StringName(str(row.get("goods", "")))
	var uid := int(row.get("uid", NO_PIECE))
	var piece := uid != NO_PIECE
	var n := 1 if piece else count
	var before := party.wallet.amount()
	var err := shop.sell_piece(uid, party) if piece else shop.sell(goods_id, n, party)
	if err != Shop.RESULT_OK:
		return {"text": refusal_text(err, goods_id, n, uid), "ok": false}
	var earned := party.wallet.amount() - before
	return {"text": _tr(SOLD_KEY).format({"count": n, "name": goods_name(goods_id), "price": lume(earned)}), "ok": true}


## One refusal in words (REFUSAL_KEYS), with the numbers that explain it.
func refusal_text(err: StringName, goods_id: StringName, count: int = 1, uid: int = NO_PIECE) -> String:
	var key := str(REFUSAL_KEYS.get(err, ""))
	if key == "":
		return ""
	var wearer := party.equipment.wearer_of(uid) if uid != NO_PIECE else &""
	var price := shop.buy_price(goods_id, count) if err == Shop.ERR_NO_FUNDS else 0
	return (
		_tr(key)
		. format(
			{
				"name": goods_name(goods_id),
				"count": count,
				"price": lume(price),
				"purse": lume(party.wallet.amount()),
				"room": party.inventory.room(goods_id),
				"held": party.inventory.count(goods_id),
				"wearer": hero_name(wearer),
			}
		)
	)


func goods_name(goods_id: StringName) -> String:
	var key := str(_goods_row(goods_id).get("name_key", ""))
	return _tr(key) if key != "" else String(goods_id)


func hero_name(cid: StringName) -> String:
	var key := str(name_keys.get(cid, ""))
	return _tr(key) if key != "" else String(cid)


func _goods_row(goods_id: StringName) -> Dictionary:
	return db.equipment_row(goods_id) if db.is_equipment(goods_id) else db.item(goods_id)


static func _tr(key: String) -> String:
	return TranslationServer.translate(key) if key != "" else ""
