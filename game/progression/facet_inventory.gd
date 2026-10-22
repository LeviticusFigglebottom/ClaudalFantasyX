class_name FacetInventory
extends RefCounted
## Facet counts (SPEC §6.4). Facets are ordinary party items, so this wraps a Dictionary of
## item id (String) -> count; pass GameStateData.inventory to work on the live bag in place.

var counts: Dictionary


func _init(backing: Dictionary = {}) -> void:
	counts = backing


func count(facet_id: StringName) -> int:
	return int(counts.get(String(facet_id), 0))


func has(facet_id: StringName, amount: int) -> bool:
	return facet_id != &"" and count(facet_id) >= amount


func add(facet_id: StringName, amount: int) -> void:
	if amount <= 0:
		return
	counts[String(facet_id)] = count(facet_id) + amount


## Removes `amount` Facets; returns false (and changes nothing) if there are not enough.
func consume(facet_id: StringName, amount: int) -> bool:
	if not has(facet_id, amount):
		return false
	var left := count(facet_id) - amount
	if left == 0:
		counts.erase(String(facet_id))
	else:
		counts[String(facet_id)] = left
	return true
