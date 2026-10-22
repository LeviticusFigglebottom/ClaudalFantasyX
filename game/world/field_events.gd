class_name FieldEvents
extends RefCounted
## Field signals on the EventBus (M1-ARC-01).
##
## EventBus (game/core/event_bus.gd) does not declare field signals yet. Until the Lead adds them,
## they are declared on the bus at runtime with add_user_signal, using exactly the names and
## arguments below. Listeners call FieldEvents.connect_interacted() / connect_trigger() (or
## ensure_signals() and then EventBus.connect). Once event_bus.gd declares them, ensure_signals()
## becomes a no-op and nothing else changes.

## field_interacted(interactable_id: StringName, kind: StringName, payload: Dictionary)
const INTERACTED := &"field_interacted"
## field_trigger_entered(trigger_id: StringName, payload: Dictionary)
const TRIGGER_ENTERED := &"field_trigger_entered"
const INTERACTED_ARGS := [
	{"name": "interactable_id", "type": TYPE_STRING_NAME},
	{"name": "kind", "type": TYPE_STRING_NAME},
	{"name": "payload", "type": TYPE_DICTIONARY},
]
const TRIGGER_ARGS := [
	{"name": "trigger_id", "type": TYPE_STRING_NAME},
	{"name": "payload", "type": TYPE_DICTIONARY},
]


static func ensure_signals(bus: Object = null) -> void:
	var b := _bus(bus)
	if b == null:
		return
	if not b.has_signal(INTERACTED):
		b.add_user_signal(INTERACTED, INTERACTED_ARGS)
	if not b.has_signal(TRIGGER_ENTERED):
		b.add_user_signal(TRIGGER_ENTERED, TRIGGER_ARGS)


static func emit_interacted(id: StringName, kind: StringName, payload: Dictionary, bus: Object = null) -> void:
	ensure_signals(bus)
	_bus(bus).emit_signal(INTERACTED, id, kind, payload)


static func emit_trigger(id: StringName, payload: Dictionary, bus: Object = null) -> void:
	ensure_signals(bus)
	_bus(bus).emit_signal(TRIGGER_ENTERED, id, payload)


static func connect_interacted(callable: Callable, bus: Object = null) -> void:
	ensure_signals(bus)
	_bus(bus).connect(INTERACTED, callable)


static func connect_trigger(callable: Callable, bus: Object = null) -> void:
	ensure_signals(bus)
	_bus(bus).connect(TRIGGER_ENTERED, callable)


## The EventBus autoload unless a stand-in bus is given (tests).
static func _bus(bus: Object) -> Object:
	if bus != null:
		return bus
	var tree := Engine.get_main_loop() as SceneTree
	return tree.root.get_node_or_null(^"EventBus") if tree != null else null
