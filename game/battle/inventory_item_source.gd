class_name InventoryItemSource
extends BattleItemSource
## BattleItemSource over the party's real Inventory (game/progression, M1-PRG-02):
##   engine.use_item(&"salt_tonic", targets, InventoryItemSource.new(item_db, inventory))
## Pass the live inventory (GameStateData.inventory wrapped in Inventory) so a use is saved.

var db: ItemDB
var inventory: Inventory


func _init(item_db: ItemDB, bag: Inventory) -> void:
	db = item_db
	inventory = bag


func action_for(item_id: StringName) -> ItemBattleAction:
	return ItemBattleAction.for_item(db, item_id)


func count(item_id: StringName) -> int:
	return inventory.count(item_id)


func consume(item_id: StringName) -> bool:
	return inventory.remove(item_id, ItemBattleAction.USES_PER_ACTION)


## Battle-usable items the party holds, in inventory listing order (for the Items menu).
func usable() -> Array[StringName]:
	return ItemBattleAction.usable_items(db, inventory)
