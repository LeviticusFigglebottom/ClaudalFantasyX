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
##   6. opens the save menu (SaveMenu, SAVE mode) with {"shrine_id": id} in the save's meta,
##   7. after it closes (not on a load), offers the other attuned shrines (ShrineTravelMenu).
## Steps 2, 3 and 5 all happen before the menu opens, so the save records the healed party,
## the attunement and the respawn point.
## Its look is bound light (art color script rule 2): a salt-glass core in `glimmer_bound`, and a
## GlimmerField in MACHINE mode that holds perfectly still. Scene: save_shrine.tscn.

signal menu_opened(menu: SaveMenu)
signal menu_closed(outcome: SaveMenuModel.Outcome)
## The travel list opened after the save menu (other attuned shrines to go to; ShrineTravelMenu).
signal travel_opened(menu: ShrineTravelMenu)

const DEFAULT_PROMPT_KEY := "SAVE_SHRINE_PROMPT"
## Shown under the menu title after the party is restored.
const RESTORED_KEY := "SAVE_SHRINE_RESTORED"
## Act II's heresy (M4-A2P-082): the flag that darkens Order shrines, their prompt, and the bark a dark one plays.
const HERETIC_FLAG := &"ch14_declared_heretics"
const DARK_PROMPT_KEY := "SAVE_SHRINE_DARK_PROMPT"
const DARK_SCENE := "dark_shrine"
const KEY_DIALOGUE := "dialogue"

## The party's location after resting here (GameStateData.location_id); empty keeps it.
@export var location_id: StringName = &""
## Off for shrines whose menu a cutscene opens itself (tests also use it).
@export var opens_menu := true
## An Order shrine (Act II, M4-A2P-082): from the heresy on (HERETIC_FLAG) it goes dark. Its bound light is out, it
## heals and saves nothing, and using it plays the one-line DARK_SCENE bark (ZoneStory). Kirru and Saltwright shrines
## leave this off and keep working.
@export var order := false
## Teleport network node id (a "shrines" row in locations.json). Empty = not in the network.
@export var network_id: StringName = &""
## Spawn marker the party respawns at after Continue. Empty: the shrine's registry row, else the
## location's own spawn (game/data/world/locations.json).
@export var respawn_spawn: StringName = &""

var menu: SaveMenu
## The travel list, while open (null otherwise).
var travel_menu: ShrineTravelMenu
# The prompt and payload an Order shrine has while lit (it swaps them while dark).
var _lit_prompt_key := ""
var _lit_payload: Dictionary = {}


func _ready() -> void:
	if prompt_key == "":
		prompt_key = DEFAULT_PROMPT_KEY
	_lit_prompt_key = prompt_key
	_lit_payload = payload.duplicate()
	super()
	ShrineNetwork.register(self)
	EventBus.flag_changed.connect(_on_flag_changed)
	_refresh_dark()


## True for an Order shrine once the party are heretics (`order` and HERETIC_FLAG).
func is_dark() -> bool:
	return order and bool(Game.get_flag(HERETIC_FLAG))


func _on_flag_changed(flag: StringName, _value: Variant) -> void:
	if flag == HERETIC_FLAG:
		_refresh_dark()


## The dark shrine's prompt, payload and unlit core, or the lit ones back.
func _refresh_dark() -> void:
	var dark := is_dark()
	prompt_key = DARK_PROMPT_KEY if dark else _lit_prompt_key
	payload = {KEY_DIALOGUE: DARK_SCENE} if dark else _lit_payload.duplicate()
	for path: NodePath in [^"Visual/Core", ^"Visual/BoundGlimmer"]:
		var n := get_node_or_null(path) as Node3D
		if n != null:
			n.visible = not dark


func _exit_tree() -> void:
	ShrineNetwork.unregister(self)


func _fire(kind: StringName) -> void:
	super(kind)
	if not is_dark():  # a dark shrine only answers with its bark (the payload)
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
	if outcome != SaveMenuModel.Outcome.LOADED:  # a load leaves this place; otherwise the road is offered
		open_travel()


## Offers the other attuned shrines (ShrineTravelMenu). Null when there is nowhere to go.
func open_travel() -> ShrineTravelMenu:
	var offer := teleport_destinations()
	if offer.is_empty() or not is_inside_tree():
		return null
	travel_menu = ShrineTravelMenu.open_in(self, self, offer)
	travel_menu.closed.connect(func() -> void: travel_menu = null)
	travel_opened.emit(travel_menu)
	return travel_menu
