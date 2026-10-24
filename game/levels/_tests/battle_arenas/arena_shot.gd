extends Node
## Screenshot fixture (M2-BPR-07): an encounter's arena on the battle sandbox (the parent), at the first turn,
## instant pacing, no floats. shots.json battle_arena_*.

@export var encounter: StringName = &""
@export var party: Array[StringName] = [&"rhen", &"asha", &"toma"]
@export var rng_seed := 20261024


func _ready() -> void:
	_start.call_deferred()


func _start() -> void:
	var ctl := get_parent() as BattleController
	ctl.pacing_scale = 0.0
	ctl.show_damage_numbers = false
	ctl.hud.apply_settings(UiSettings.new())
	ctl.start_battle(party, [], encounter, rng_seed)
