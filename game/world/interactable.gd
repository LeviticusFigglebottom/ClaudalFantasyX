class_name Interactable
extends Area3D
## A field interactable or touch trigger (M1-ARC-01). Emits on the EventBus (FieldEvents) and
## reads/writes story flags only through Game.get_flag / Game.set_flag, with flags declared in
## game/data/flags.tres (undeclared names are reported at _ready, and test_field_interactables
## checks every authored scene).
##
## activation = INTERACT: FieldController calls try_interact() when the player presses
##   field_interact while inside the area (nearest wins).
## activation = TOUCH: FieldController calls on_touched() when the player first enters the area.
## Gating: `requires_flag` must be truthy (when set) and `blocked_by_flag` falsy (when set).
## Effect: emits FieldEvents.INTERACTED / TRIGGER_ENTERED with `payload`, then sets `sets_flag`
## to true. `once` disables the interactable after the first use (and keeps it disabled on a
## reload when `sets_flag` is already set).

signal used(interactable: Interactable)

enum Activation { INTERACT, TOUCH }

const GROUP := &"field_interactable"
const KIND_INTERACT := &"interact"
const KIND_TOUCH := &"touch"

@export var id: StringName = &""
@export var activation: Activation = Activation.INTERACT
## Localization key of the on-screen prompt ("Examine", "Pull"...). Player-facing, so tr() keyed.
@export var prompt_key: String = ""
@export var requires_flag: StringName = &""
@export var blocked_by_flag: StringName = &""
@export var sets_flag: StringName = &""
@export var once: bool = false
## Forwarded on the bus: dialogue id, item id, scene path... whatever the listener needs.
@export var payload: Dictionary = {}

var uses := 0


func _ready() -> void:
	add_to_group(GROUP)
	monitoring = false
	monitorable = false
	for f in declared_flag_names():
		if not Game.registry.is_declared(f):
			push_error("Interactable %s uses undeclared flag '%s' (declare it in %s)" % [id, f, Game.FLAGS_PATH])


## Every flag this interactable names (for validation).
func declared_flag_names() -> Array[StringName]:
	var out: Array[StringName] = []
	for f in [requires_flag, blocked_by_flag, sets_flag]:
		if f != &"":
			out.append(f)
	return out


func contains_point(world_point: Vector3) -> bool:
	return FieldShapes.area_contains(self, world_point)


func is_available() -> bool:
	if once and (uses > 0 or (sets_flag != &"" and bool(Game.get_flag(sets_flag)))):
		return false
	if requires_flag != &"" and not bool(Game.get_flag(requires_flag)):
		return false
	if blocked_by_flag != &"" and bool(Game.get_flag(blocked_by_flag)):
		return false
	return true


## Uses the interactable if it is available. Returns true when it fired.
func try_interact() -> bool:
	if activation != Activation.INTERACT or not is_available():
		return false
	_fire(KIND_INTERACT)
	FieldEvents.emit_interacted(id, KIND_INTERACT, payload)
	return true


## Touch triggers fire on entry. Returns true when it fired.
func on_touched() -> bool:
	if activation != Activation.TOUCH or not is_available():
		return false
	_fire(KIND_TOUCH)
	FieldEvents.emit_trigger(id, payload)
	return true


func _fire(_kind: StringName) -> void:
	uses += 1
	if sets_flag != &"":
		Game.set_flag(sets_flag, true)
	used.emit(self)
