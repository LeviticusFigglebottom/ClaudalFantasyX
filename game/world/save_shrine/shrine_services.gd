class_name ShrineServices
extends Node
## The zone-agnostic save shrine hook (M3-C07-05; TownServices' pattern). A greybox zone has no
## SaveShrine node, only layout triggers, so its shrine gives a heal and a checkpoint but no save
## menu, attunement or travel. This hook listens to FieldEvents.INTERACTED on the EventBus and, for
## a {"save_shrine": "<network id>"} payload (a locations.json "shrines" row), uses a SaveShrine for
## that row: it rests the party, attunes the shrine, opens the save menu and then the travel list,
## exactly like a placed shrine. The shrine is made once per id, under this node, at no position
## (it is never walked into: the zone's own trigger is the thing the player uses).
## Any other payload is ignored, and so is an id with no "shrines" row. The zone's own keys on the
## same trigger (a "beat") still run. FieldController adds one as a child in every zone.

signal opened(shrine: SaveShrine)

const KEY := "save_shrine"

## The shrines made so far, by network id.
var shrines: Dictionary = {}


func _enter_tree() -> void:
	FieldEvents.connect_interacted(_on_interacted)


func _exit_tree() -> void:
	if EventBus.is_connected(FieldEvents.INTERACTED, _on_interacted):
		EventBus.disconnect(FieldEvents.INTERACTED, _on_interacted)


## Rests at the shrine a payload names. Returns it, or null for any other payload, an unlisted id,
## or while that shrine's save menu or travel list is still open.
func handle(payload: Dictionary) -> SaveShrine:
	if not payload.has(KEY):
		return null
	var network_id := StringName(str(payload[KEY]))
	var point := ShrineNetwork.registry_point(network_id)
	if point.is_empty():
		push_warning("ShrineServices: no locations.json shrines row '%s'" % network_id)
		return null
	var shrine := shrine_for(network_id, point)
	if shrine.is_menu_open() or (shrine.travel_menu != null and is_instance_valid(shrine.travel_menu)):
		return null
	shrine.rest()
	opened.emit(shrine)
	return shrine


## The SaveShrine standing for `network_id` (made on first use; `point` is its registry row).
func shrine_for(network_id: StringName, point: Dictionary) -> SaveShrine:
	var have: SaveShrine = shrines.get(network_id)
	if have != null and is_instance_valid(have):
		return have
	var shrine := SaveShrine.new()
	shrine.name = "Shrine_%s" % network_id
	shrine.id = network_id
	shrine.network_id = network_id
	shrine.location_id = StringName(str(point.get(LocationRegistry.KEY_LOCATION, "")))
	add_child(shrine)
	shrines[network_id] = shrine
	return shrine


func _on_interacted(_id: StringName, _kind: StringName, payload: Dictionary) -> void:
	handle(payload)
