class_name SaveShrine
extends Interactable
## A save shrine (M1-ARC-03, SPEC §5.2, §6.6): an INTERACT Interactable that, when used,
##   1. sets `save_shrine_used` (and the instance's own `sets_flag`, e.g. Haluna's ch02_saved_once),
##   2. records `location_id` (when set) as the party's location in Game.state,
##   3. restores the party: EventBus.party_full_heal_requested(id). Party HP/MP/statuses are not
##      persisted in GameStateData yet, and the battle engine builds every fighter at full HP, so
##      the request is already true today; the party owner listens for it once HP persists,
##   4. emits EventBus.save_shrine_used(id, location_id),
##   5. opens the save menu (SaveMenu, SAVE mode) with {"shrine_id": id} in the save's meta,
##   6. attunes the shrine in the teleport network (ShrineNetwork: a stub until SPEC §6.6 "later").
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
## Teleport network node id (later: travel between attuned shrines). Empty = not in the network.
@export var network_id: StringName = &""

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
	EventBus.party_full_heal_requested.emit(id)
	EventBus.save_shrine_used.emit(id, Game.state.location_id)
	ShrineNetwork.attune(self)
	return open_menu() if opens_menu else null


func is_menu_open() -> bool:
	return menu != null and is_instance_valid(menu) and menu.is_open()


func open_menu() -> SaveMenu:
	if is_menu_open():
		return menu
	menu = SaveMenu.open_in(self, SaveMenuModel.Mode.SAVE, {"shrine_id": String(id)}, RESTORED_KEY)
	menu.closed.connect(_on_menu_closed)
	menu_opened.emit(menu)
	return menu


# --- Teleport network (stub) ---------------------------------------------------------------------


## Shrine ids this shrine could send the party to. Always empty until the network exists.
func teleport_destinations() -> Array[StringName]:
	return ShrineNetwork.destinations_from(self)


## Asks to travel to another shrine. Returns false: not built yet (SPEC §6.6 "later").
func request_teleport(destination_id: StringName) -> bool:
	return ShrineNetwork.request_teleport(self, destination_id)


func _on_menu_closed(outcome: SaveMenuModel.Outcome) -> void:
	menu = null
	menu_closed.emit(outcome)
