class_name Customize
extends RefCounted
## The Customize menu's logic (SPEC §6.5): craft an ability into an empty slot of one owned
## piece by spending the items its recipe lists (game/data/items/customize.json).
##
## Rules (docs/kb/design/economy.md): the piece must have an empty slot; the ability must fit
## the piece's equip slot (weapon/armor) and not already be on it; the party must hold every
## recipe item. Crafted abilities are permanent. The ability goes into the FIRST empty slot
## unless a slot index is given, so the same inputs always give the same piece.

const RESULT_OK := &"ok"
const ERR_UNKNOWN_PIECE := &"unknown_piece"
const ERR_UNKNOWN_ABILITY := &"unknown_ability"
const ERR_NO_RECIPE := &"no_recipe"
const ERR_WRONG_SLOT_KIND := &"ability_does_not_fit"
const ERR_ALREADY_HAS := &"already_has_ability"
const ERR_NO_EMPTY_SLOT := &"no_empty_slot"
const ERR_SLOT_FILLED := &"slot_filled"
const ERR_MISSING_ITEMS := &"missing_items"
const FIRST_EMPTY := -1

var db: ItemDB


func _init(item_db: ItemDB) -> void:
	db = item_db


## Items one crafting of `ability_id` consumes: [{"item", "count"}] ([] if it has no recipe).
func cost(ability_id: StringName) -> Array[Dictionary]:
	return db.recipe(ability_id)


## Recipe items the party is short of: item id -> how many more it needs. Empty if affordable.
func shortfall(ability_id: StringName, inventory: Inventory) -> Dictionary:
	var out: Dictionary = {}
	for part in cost(ability_id):
		var iid: StringName = part["item"]
		var need := int(part["count"]) - inventory.count(iid)
		if need > 0:
			out[iid] = need
	return out


## Abilities that could be crafted onto this piece right now (fits, not present, has a
## recipe), in abilities.json order, ignoring whether the party holds the items.
func candidates(bag: EquipmentBag, uid: int) -> Array[StringName]:
	var out: Array[StringName] = []
	if not bag.has_piece(uid) or bag.first_empty_slot(uid) < 0:
		return out
	for aid: StringName in db.abilities:
		if _fit_error(bag, uid, aid) == RESULT_OK:
			out.append(aid)
	return out


## Why `ability_id` can't be crafted onto piece `uid` (at `slot`, or the first empty slot), or
## RESULT_OK. Changes nothing.
func craft_error(
	bag: EquipmentBag, uid: int, ability_id: StringName, inventory: Inventory, slot: int = FIRST_EMPTY
) -> StringName:
	if not bag.has_piece(uid):
		return ERR_UNKNOWN_PIECE
	var fit := _fit_error(bag, uid, ability_id)
	if fit != RESULT_OK:
		return fit
	var err := _slot_error(bag, uid, slot)
	if err != RESULT_OK:
		return err
	if not shortfall(ability_id, inventory).is_empty():
		return ERR_MISSING_ITEMS
	return RESULT_OK


## Crafts the ability, consuming the recipe items. Returns RESULT_OK or an ERR_*.
func craft(
	bag: EquipmentBag, uid: int, ability_id: StringName, inventory: Inventory, slot: int = FIRST_EMPTY
) -> StringName:
	var err := craft_error(bag, uid, ability_id, inventory, slot)
	if err != RESULT_OK:
		return err
	for part in cost(ability_id):
		inventory.remove(part["item"], int(part["count"]))
	bag.set_slot(uid, bag.first_empty_slot(uid) if slot == FIRST_EMPTY else slot, ability_id)
	return RESULT_OK


func _fit_error(bag: EquipmentBag, uid: int, ability_id: StringName) -> StringName:
	if db.ability(ability_id).is_empty():
		return ERR_UNKNOWN_ABILITY
	if cost(ability_id).is_empty():
		return ERR_NO_RECIPE
	if not db.ability_fits(ability_id, db.slot_of(bag.base_of(uid))):
		return ERR_WRONG_SLOT_KIND
	if bag.abilities_of(uid).has(ability_id):
		return ERR_ALREADY_HAS
	return RESULT_OK


func _slot_error(bag: EquipmentBag, uid: int, slot: int) -> StringName:
	if slot == FIRST_EMPTY:
		return RESULT_OK if bag.first_empty_slot(uid) >= 0 else ERR_NO_EMPTY_SLOT
	var slots := bag.slots_of(uid)
	if slot < 0 or slot >= slots.size():
		return ERR_NO_EMPTY_SLOT
	return RESULT_OK if slots[slot] == &"" else ERR_SLOT_FILLED
