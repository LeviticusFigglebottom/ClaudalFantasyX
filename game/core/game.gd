extends Node
## Autoload "Game": owns the live GameStateData and the flag registry.

const FLAGS_PATH := "res://game/data/flags.tres"

var state: GameStateData = GameStateData.new()
var registry: FlagRegistry


func _ready() -> void:
	registry = load(FLAGS_PATH) as FlagRegistry
	if registry == null:
		push_error("Game: failed to load flag registry at %s" % FLAGS_PATH)
		registry = FlagRegistry.new()


func get_flag(flag: StringName, default: Variant = false) -> Variant:
	_check_declared(flag)
	return state.flags.get(String(flag), default)


func set_flag(flag: StringName, value: Variant = true) -> void:
	_check_declared(flag)
	state.flags[String(flag)] = value
	EventBus.flag_changed.emit(flag, value)


func new_game() -> void:
	state = GameStateData.new()


func _check_declared(flag: StringName) -> void:
	if not registry.is_declared(flag):
		push_error("Undeclared story flag '%s' (declare it in %s)" % [flag, FLAGS_PATH])
