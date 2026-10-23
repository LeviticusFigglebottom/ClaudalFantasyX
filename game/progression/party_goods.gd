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


## Every hero who has joined (`party_ids` then `reserve_ids`, first occurrence only), in order.
static func joined_members(state: GameStateData) -> Array[StringName]:
	var out: Array[StringName] = []
	for cid in state.party_ids + state.reserve_ids:
		if not out.has(cid):
			out.append(cid)
	return out


## Fills any missing starting gear for every joined hero (EquipmentBag.grant_starting, which is
## idempotent). SaveSystem runs it after each load, so a migrated v2 save whose heroes joined
## before equipment existed loads with their weapons (M1-PRG-03). Returns who received gear.
func ensure_starting_gear(state: GameStateData) -> Array[StringName]:
	var out: Array[StringName] = []
	for cid in joined_members(state):
		if equipment.grant_starting(cid):
			out.append(cid)
	return out
