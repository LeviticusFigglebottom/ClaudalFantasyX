class_name Inventory
extends RefCounted
## The party's bag of stackable items (SPEC §6.5, §6.11): consumables, materials, Facets and key
## items. Wraps a Dictionary of item id (String) -> count; pass GameStateData.inventory to work on
## the live bag in place. FacetInventory can wrap the same Dictionary (see facets()).
##
## Rules (docs/kb/design/economy.md): a stack never exceeds ItemDB.cap_of(id); key items cap at
## key_item_cap and can't be sold; unknown ids are refused; listings are deterministic
## (category order from items.json, then data order).

var counts: Dictionary
var db: ItemDB


func _init(item_db: ItemDB, backing: Dictionary = {}) -> void:
	db = item_db
	counts = backing


func count(item_id: StringName) -> int:
	return int(counts.get(String(item_id), 0))


func has(item_id: StringName, amount: int = 1) -> bool:
	return amount > 0 and count(item_id) >= amount


## How many more of this item fit before the stack is full (0 for unknown ids).
func room(item_id: StringName) -> int:
	return maxi(db.cap_of(item_id) - count(item_id), 0)


## Adds up to `amount`, clamped to the stack cap. Returns how many were actually added; the
## rest is lost (callers that must not lose items check room() first, like Shop does).
func add(item_id: StringName, amount: int) -> int:
	if amount <= 0:
		return 0
	if not db.has_item(item_id):
		push_error("Inventory: unknown item '%s'" % item_id)
		return 0
	var added := mini(amount, room(item_id))
	if added > 0:
		counts[String(item_id)] = count(item_id) + added
	return added


## Removes `amount`; returns false (and changes nothing) if there are not enough.
func remove(item_id: StringName, amount: int) -> bool:
	if not has(item_id, amount):
		return false
	var left := count(item_id) - amount
	if left == 0:
		counts.erase(String(item_id))
	else:
		counts[String(item_id)] = left
	return true


func is_key_item(item_id: StringName) -> bool:
	return db.is_key_item(item_id)


func is_sellable(item_id: StringName) -> bool:
	return db.sell_price_of(item_id) > 0


## Held item ids (count > 0), sorted by category order, then items.json order.
func ids() -> Array[StringName]:
	var out: Array[StringName] = []
	for k: Variant in counts:
		var iid := StringName(str(k))
		if db.has_item(iid) and count(iid) > 0:
			out.append(iid)
	out.sort_custom(func(a: StringName, b: StringName) -> bool: return db.sort_rank(a) < db.sort_rank(b))
	return out


## Held ids of one category, in listing order.
func ids_in(category: StringName) -> Array[StringName]:
	var out: Array[StringName] = []
	for iid in ids():
		if db.category_of(iid) == category:
			out.append(iid)
	return out


## A FacetInventory over the same backing Dictionary, for LatticeProgress.activate/open_gate.
func facets() -> FacetInventory:
	return FacetInventory.new(counts)


## Makes the backing data canonical after a load: int counts, no empty stacks, unknown ids
## dropped (with a warning) and over-cap stacks clamped. Returns the dropped ids, sorted.
func normalize() -> Array[String]:
	var dropped: Array[String] = []
	for k: Variant in counts.keys():
		var key := str(k)
		var iid := StringName(key)
		var n := int(counts[k])
		counts.erase(k)
		if not db.has_item(iid):
			push_warning("Inventory: dropping unknown item '%s'" % key)
			dropped.append(key)
		elif n > 0:
			counts[key] = mini(n, db.cap_of(iid))
	dropped.sort()
	return dropped
