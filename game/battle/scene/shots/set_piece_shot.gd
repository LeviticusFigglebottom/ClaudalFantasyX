extends Node
## Screenshot fixture (M3-UI-100): a set piece's wave on the battle sandbox (the parent), live data: the party's
## first turn with the scripted entries on the timeline, Kerrid kept out, and the objective meter at `groups_up`.
## Instant pacing and no floats, as the arena shots. shots.json battle_ch08_stair_hold.

@export var encounter: StringName = &""
@export var party: Array[StringName] = [&"rhen"]
@export var reserve: Array[StringName] = []
@export var rng_seed := 20261027
@export var groups_up := 0


func _ready() -> void:
	_start.call_deferred()


func _start() -> void:
	var ctl := get_parent() as BattleController
	ctl.pacing_scale = 0.0
	ctl.show_damage_numbers = false
	ctl.hud.apply_settings(UiSettings.new())
	ctl.start_battle(party, reserve, encounter, rng_seed)
	ctl.engine.objective_count = groups_up
	ctl.set_piece.refresh()
