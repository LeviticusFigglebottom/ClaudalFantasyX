class_name BattleItemSource
extends RefCounted
## The bag BattleEngine.use_item() draws from (M1-CMB-06). The engine never touches the party
## Inventory directly: callers inject an implementation, InventoryItemSource for play or a
## fake in tests. This base class holds nothing, so every item is unavailable.


## The battle action for `item_id`, or null if it has none (not a battle item, or unknown).
func action_for(_item_id: StringName) -> ItemBattleAction:
	return null


## How many of `item_id` the party holds.
func count(_item_id: StringName) -> int:
	return 0


## Takes one `item_id` out of the bag. False (and nothing changes) if none are left.
func consume(_item_id: StringName) -> bool:
	return false


## Battle-usable item ids held, in menu order.
func usable() -> Array[StringName]:
	return []
