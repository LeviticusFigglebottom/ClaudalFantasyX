class_name ShrineNetwork
extends RefCounted
## Teleport-network hook for save shrines (SPEC §6.6: "later a teleport network"). STUB.
##
## The interface is fixed now so shrines, the field and a future travel menu can be written
## against it; the behaviour is not:
##   register(shrine) / unregister(shrine)  shrines in the loaded zone (SaveShrine does this)
##   attune(shrine)                         a use attunes the shrine (no persistence yet: no-op)
##   is_attuned(network_id)                 false until attunement is persisted
##   destinations_from(shrine)              always [] for now
##   request_teleport(shrine, destination)  always false for now (emits nothing)
##
## To build it: persist attuned network ids (a new GameStateData field and a SAVE_VERSION bump,
## owned by the Systems Architect), add a node-id -> scene + spawn table under game/data/world/,
## and route request_teleport through SceneRouter.change_scene + the zone's place_at(spawn).

static var _loaded: Dictionary = {}


static func register(shrine: SaveShrine) -> void:
	if shrine.network_id != &"":
		_loaded[shrine.network_id] = shrine


static func unregister(shrine: SaveShrine) -> void:
	if shrine.network_id != &"" and _loaded.get(shrine.network_id) == shrine:
		_loaded.erase(shrine.network_id)


## Shrines of the network in the loaded zone, by network id.
static func loaded_shrines() -> Dictionary:
	return _loaded.duplicate()


static func attune(_shrine: SaveShrine) -> void:
	pass


static func is_attuned(_network_id: StringName) -> bool:
	return false


static func destinations_from(_shrine: SaveShrine) -> Array[StringName]:
	return []


static func request_teleport(_shrine: SaveShrine, _destination_id: StringName) -> bool:
	return false
