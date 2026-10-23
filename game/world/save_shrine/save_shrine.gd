class_name SaveShrine
extends Interactable
## A save shrine (M1-ARC-03, SPEC §5.2, §6.6): an INTERACT Interactable that, when used,
##   1. sets `save_shrine_used` (and the instance's own `sets_flag`, e.g. Haluna's ch02_saved_once),
##   2. records `location_id` (when set) as the party's location in Game.state, and makes this
##      shrine the respawn point (Game.state.respawn_*; spawn: respawn_spawn_name()),
##   3. restores the party: EventBus.party_full_heal_requested(id). Game fills every member's HP
##      and MP and cures party_rest.json "shrine_cures" (M1-ARC-06),
##   4. emits EventBus.save_shrine_used(id, location_id),
##   5. attunes the shrine in the teleport network (ShrineNetwork; saved in Game.state),
##   6. opens the save menu (SaveMenu, SAVE mode) with {"shrine_id": id} in the save's meta.
## Steps 2, 3 and 5 all happen before the menu opens, so the save records the healed party,
## the attunement and the respawn point.
## Its look is bound light (art color script rule 2): a salt-glass core in `glimmer_bound`, and a
## GlimmerField in MACHINE mode that holds perfectly still. Scene: save_shrine.tscn.

signal menu_opened(menu: SaveMenu)
signal menu_closed(outcome: SaveMenuModel.Outcome)

const DEFAULT_PROMPT_KEY := "SAVE_SHRINE_PROMPT"
## Shown under the menu title after the party is restored.
const RESTORED_KEY := "SAVE_SHRINE_RESTORED"

## The party's location after resting here (GameStateData.location_id); empty keeps it.
@export var location_id: StringName = &""
## Off for shrines whose menu a cutscene opens itself (tests also use it).
@export var opens_menu := true
## Teleport network node id (a "shrines" row in locations.json). Empty = not in the network.
@export var network_id: StringName = &""
## Spawn marker the party respawns at after Continue. Empty: the shrine's registry row, else the
## location's own spawn (game/data/world/locations.json).
@export var respawn_spawn: StringName = &""

var menu: SaveMenu


func _ready() -> void:
	if prompt_key == "":
		prompt_key = DEFAULT_PROMPT_KEY
	super()
	ShrineNetwork.register(self)


func _exit_tree() -> void:
	ShrineNetwork.unregister(self)


func _fire(kind: StringName) -> void:
	super(kind)
	rest()


## Everything a use does after the base Interactable effects. Returns the opened menu (or null).
func rest() -> SaveMenu:
	Game.set_flag(&"save_shrine_used", true)
	if location_id != &"":
		Game.state.location_id = location_id
	Game.state.respawn_location_id = Game.state.location_id
	Game.state.respawn_spawn = respawn_spawn_name()
	EventBus.party_full_heal_requested.emit(id)
	EventBus.save_shrine_used.emit(id, Game.state.location_id)
	ShrineNetwork.attune(self)
	return open_menu() if opens_menu else null


## The spawn the party returns to after resting here (see respawn_spawn).
func respawn_spawn_name() -> StringName:
	if respawn_spawn != &"":
		return respawn_spawn
	var point := ShrineNetwork.registry_point(network_id)
	if not point.is_empty():
		return StringName(str(point[LocationRegistry.KEY_SPAWN]))
	return &""


func is_menu_open() -> bool:
	return menu != null and is_instance_valid(menu) and menu.is_open()


func open_menu() -> SaveMenu:
	if is_menu_open():
		return menu
	menu = SaveMenu.open_in(self, SaveMenuModel.Mode.SAVE, {"shrine_id": String(id)}, RESTORED_KEY)
	menu.closed.connect(_on_menu_closed)
	menu_opened.emit(menu)
	return menu


# --- Teleport network ---------------------------------------------------------------------------


## Attuned shrine ids this shrine can send the party to (ShrineNetwork.destinations_from).
func teleport_destinations() -> Array[StringName]:
	return ShrineNetwork.destinations_from(self)


## Travels to another attuned shrine through the location registry. False when refused.
func request_teleport(destination_id: StringName) -> bool:
	return ShrineNetwork.request_teleport(self, destination_id)


func _on_menu_closed(outcome: SaveMenuModel.Outcome) -> void:
	menu = null
	menu_closed.emit(outcome)
