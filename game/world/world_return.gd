class_name WorldReturn
extends Node
## Return to the world after a load (M1-ARC-06). SceneRouter owns one (SceneRouter.world_return).
## On EventBus.game_loaded it resolves Game.state's respawn point through the LocationRegistry
## and asks the router to change to that scene and place the player at the spawn.
##
## It is OFF until something arms it: boot.gd sets `enabled = true` for the real game, so the
## test runner, screenshot captures and tools that load saves never change scene by accident.
##
##   resolve(state)                {location_id, scene, spawn, fallback} for a state's respawn
##   go_to(location_id, spawn)     change scene to a registered location (New Game, teleports)
##   place_player(root, spawn)     put the player on Spawns/<spawn> in a freshly loaded scene
##
## `change_scene` is the Callable that does the swap: (scene_path: String, spawn: StringName).
## It defaults to the router's change_scene; tests replace it to record the request.

## Emitted when a return or travel was requested: (location_id, scene_path, spawn).
signal travel_requested(location_id: StringName, scene_path: String, spawn: StringName)

const SPAWNS_NODE := "Spawns"
const PLAYER_GROUP := &"player"
const PLAYER_NODE := "Player"
const PLACE_METHOD := &"place_at"

## Off by default; boot.gd arms it (see the class comment).
var enabled := false
var registry: LocationRegistry
var change_scene: Callable = Callable()


func _ready() -> void:
	if registry == null:
		registry = LocationRegistry.load_default()
	if not EventBus.game_loaded.is_connected(_on_game_loaded):
		EventBus.game_loaded.connect(_on_game_loaded)


## Where `state` continues: its respawn point, else its current location (at the location's own
## spawn), else the default. A respawn that cannot be entered (not listed, or not playable) is
## skipped in favour of a good location_id (M1-ARC-11, review-sweep-G S3). Besides
## LocationRegistry.resolve's keys the result has "asked" (the id the result stands for, which a
## fallback replaced) and "respawn_skipped" (the respawn id that was passed over, or &"").
func resolve(state: GameStateData) -> Dictionary:
	var reg := _registry()
	var respawn := state.respawn_location_id
	if respawn != &"" and reg.can_enter(respawn):
		var at := reg.resolve(respawn, state.respawn_spawn)
		at["asked"] = respawn
		at["respawn_skipped"] = &""
		return at
	var to := reg.resolve(state.location_id)
	if not to.is_empty():
		to["asked"] = state.location_id if state.location_id != &"" else respawn
		to["respawn_skipped"] = respawn
	return to


## Sends the party to `location_id` (at `spawn`, or the location's own spawn). Updates
## Game.state.location_id, unless the id is unknown and the default stands in (see _travel).
## Returns false when the location does not resolve or no swap is set up.
func go_to(location_id: StringName, spawn: StringName = &"") -> bool:
	var to := _registry().resolve(location_id, spawn)
	return _travel(to, location_id)


## Moves the player of a loaded scene to Spawns/<spawn>: the scene's own place_at(spawn, yaw)
## when it has one (field zones snap their camera there), else the node in group "player" (or a
## child named Player) is moved to the marker's position and yaw. Returns true on success.
static func place_player(root: Node, spawn: StringName) -> bool:
	if root == null or spawn == &"":
		return false
	var marker := root.get_node_or_null(NodePath("%s/%s" % [SPAWNS_NODE, spawn])) as Node3D
	if marker == null:
		push_warning("WorldReturn: %s has no spawn '%s'" % [root.name, spawn])
		return false
	var yaw := marker.global_rotation.y if marker.is_inside_tree() else marker.rotation.y
	if root.has_method(PLACE_METHOD):
		return bool(root.call(PLACE_METHOD, spawn, rad_to_deg(yaw)))
	var player := _find_player(root)
	if player == null:
		push_warning("WorldReturn: %s has no player to place" % root.name)
		return false
	if marker.is_inside_tree() and player.is_inside_tree():
		player.global_position = marker.global_position
	else:
		player.position = marker.position
	player.rotation.y = yaw
	return true


func _on_game_loaded(_slot: int) -> void:
	if not enabled:
		return
	var to := resolve(Game.state)
	if to.is_empty():
		push_error("WorldReturn: no location to return to (check %s)" % LocationRegistry.DATA_PATH)
		return
	var wanted := StringName(str(to.get("asked", "")))
	var skipped := StringName(str(to.get("respawn_skipped", "")))
	if skipped != &"" and skipped != wanted:
		push_warning(
			(
				"WorldReturn: respawn '%s' %s; trying the saved location '%s'"
				% [skipped, _why_not(skipped), Game.state.location_id]
			)
		)
	_travel(to, wanted)


## Changes scene to a resolved location. Game.state.location_id becomes the location only when it
## resolved as asked: a fallback (a location missing from locations.json, renamed, or marked not
## playable) warns and keeps the state's own location_id, so the next save never records the
## stand-in (the test level) as where the party is (M1-ARC-11, after QA review-sweep-F on M1-ARC-06
## and review-sweep-G on M1-ENV-04).
func _travel(to: Dictionary, wanted: StringName = &"") -> bool:
	if to.is_empty():
		return false
	var fallback := bool(to.get("fallback", false))
	# An empty location (a v3 save migrated with none) is documented to use the default: no warning.
	if fallback and wanted != &"":
		push_warning(
			(
				"WorldReturn: location '%s' %s; going to the default '%s' and keeping the saved location"
				% [wanted, _why_not(wanted), to[LocationRegistry.KEY_LOCATION]]
			)
		)
	var swap := change_scene
	if not swap.is_valid():
		var router := get_parent()
		if router == null or not router.has_method(&"change_scene"):
			return false
		swap = Callable(router, &"change_scene")
	var loc := StringName(str(to[LocationRegistry.KEY_LOCATION]))
	var scene := str(to[LocationRegistry.KEY_SCENE])
	var spawn := StringName(str(to[LocationRegistry.KEY_SPAWN]))
	if not fallback:
		Game.state.location_id = loc
	travel_requested.emit(loc, scene, spawn)
	swap.call(scene, spawn)
	return true


## Why the party cannot be sent to `id`, for a warning.
func _why_not(id: StringName) -> String:
	if _registry().has_location(id):
		return 'has no player to place (marked "playable": false in %s)' % LocationRegistry.DATA_PATH
	return "is not in %s" % LocationRegistry.DATA_PATH


func _registry() -> LocationRegistry:
	if registry == null:
		registry = LocationRegistry.load_default()
	return registry


static func _find_player(root: Node) -> Node3D:
	if root.is_inside_tree():
		for n in root.get_tree().get_nodes_in_group(PLAYER_GROUP):
			if n is Node3D and (n == root or root.is_ancestor_of(n)):
				return n as Node3D
	return root.get_node_or_null(NodePath(PLAYER_NODE)) as Node3D
