class_name ShrineNetwork
extends RefCounted
## The save shrines' teleport network (SPEC §6.6), M1-ARC-06.
##   register(shrine) / unregister(shrine)   shrines in the loaded zone (SaveShrine does this)
##   attune(shrine)                          a rest attunes the shrine: its network id is appended
##                                           to Game.state.attuned_shrines (saved, v4)
##   is_attuned(network_id)                  in Game.state.attuned_shrines
##   destinations_from(shrine)               attuned shrines the registry can place the party at,
##                                           in attunement order, without the shrine itself
##   request_teleport(shrine, destination)   sends the party through the LocationRegistry to the
##                                           destination's location and spawn (SceneRouter swap),
##                                           and makes it the respawn point
## Shrine rows live in game/data/world/locations.json ("shrines"). `registry` and `travel` are
## static so tests can point them at fixtures; travel takes (location_id, spawn) and returns bool,
## and defaults to SceneRouter.world_return.go_to.

static var registry: LocationRegistry
static var travel: Callable = Callable()
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


## Records the shrine as attuned (once). Returns true when it was newly attuned.
static func attune(shrine: SaveShrine) -> bool:
	return attune_id(shrine.network_id)


static func attune_id(network_id: StringName) -> bool:
	if network_id == &"" or Game.state.attuned_shrines.has(network_id):
		return false
	Game.state.attuned_shrines.append(network_id)
	return true


static func is_attuned(network_id: StringName) -> bool:
	return network_id != &"" and Game.state.attuned_shrines.has(network_id)


## Attuned shrines the party could travel to from `shrine`: listed in the registry, not the
## shrine itself, in attunement order. A shrine outside the network has no destinations.
static func destinations_from(shrine: SaveShrine) -> Array[StringName]:
	var out: Array[StringName] = []
	if shrine == null or shrine.network_id == &"":
		return out
	for nid in Game.state.attuned_shrines:
		if nid != shrine.network_id and _registry().has_shrine(nid):
			out.append(nid)
	return out


## True for a network shrine the registry marks as the Order's once the party are heretics (SaveShrine.is_dark for a
## shrine that is not loaded): the travel list greys it and a trip there is refused.
static func is_dark(network_id: StringName) -> bool:
	return _registry().shrine_is_order(network_id) and bool(Game.get_flag(SaveShrine.HERETIC_FLAG))


## Travels to `destination_id`. Refused (false) when the shrine is not in the network, the
## destination is not one of destinations_from(shrine), is dark (is_dark), or its location cannot be entered (not
## listed, or a stand-in scene marked "playable": false; LocationRegistry.can_enter).
## On success the destination becomes the respawn point.
static func request_teleport(shrine: SaveShrine, destination_id: StringName) -> bool:
	if not destinations_from(shrine).has(destination_id) or is_dark(destination_id):
		return false
	var point := _registry().shrine_point(destination_id)
	var loc := StringName(str(point.get(LocationRegistry.KEY_LOCATION, "")))
	var spawn := StringName(str(point.get(LocationRegistry.KEY_SPAWN, "")))
	if not _registry().can_enter(loc):
		return false
	var go := travel if travel.is_valid() else _router_travel()
	if not go.is_valid() or not bool(go.call(loc, spawn)):
		return false
	Game.state.respawn_location_id = loc
	Game.state.respawn_spawn = spawn
	return true


static func _registry() -> LocationRegistry:
	if registry == null:
		registry = LocationRegistry.load_default()
	return registry


static func _router_travel() -> Callable:
	var tree := Engine.get_main_loop() as SceneTree
	var router := tree.root.get_node_or_null(^"SceneRouter") if tree != null else null
	if router == null or bool(router.call(&"is_busy")):
		return Callable()
	var wr: Variant = router.get(&"world_return")
	return Callable(wr as Object, &"go_to") if wr is WorldReturn else Callable()


## The registry's {location_id, spawn} for a network id ({} when not listed or empty).
static func registry_point(network_id: StringName) -> Dictionary:
	if network_id == &"":
		return {}
	return _registry().shrine_point(network_id)


## The name_key of a network shrine's location ("" when not listed): the travel list's words (ShrineTravelMenu).
static func name_key_of(network_id: StringName) -> String:
	var loc := StringName(str(registry_point(network_id).get(LocationRegistry.KEY_LOCATION, "")))
	return _registry().name_key_of(loc) if loc != &"" else ""


## The name_key of a location ("" when not listed): the Kite's words for a place (KiteMapModel).
static func registry_name_key(location_id: StringName) -> String:
	return _registry().name_key_of(location_id) if location_id != &"" else ""


## Travels to a location through the SceneRouter, as a shrine's trip does, when the registry lets the
## party enter it (the Kite: KiteMapModel.from_game). False when refused or the router is busy.
static func travel_to(location_id: StringName, spawn: StringName) -> bool:
	if not _registry().can_enter(location_id):
		return false
	var go := travel if travel.is_valid() else _router_travel()
	return go.is_valid() and bool(go.call(location_id, spawn))
