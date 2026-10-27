extends Node
## Screenshot fixture (M3-BPR-418): an arena by id on the battle sandbox (the parent), for arenas whose encounters
## aren't written yet (the Act II boss arenas). The sandbox's own fight on it at the first turn, instant pacing, no
## floats. shots.json battle_arena_<id>.

@export var arena: String = ""
@export var party: Array[StringName] = [&"rhen", &"asha", &"toma"]
@export var encounter: StringName = &"sandbox_reef"
@export var rng_seed := 20261027

var _started := false


func _ready() -> void:
	_start.call_deferred()


func _start() -> void:
	if _started:
		return
	_started = true
	var ctl := get_parent() as BattleController
	ctl.pacing_scale = 0.0
	ctl.show_damage_numbers = false
	ctl.hud.apply_settings(UiSettings.new())
	ctl.start_battle(party, [], encounter, rng_seed)
	BattleArena.apply_scene(ctl, BattleArena.scene_of(arena))
