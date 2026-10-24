extends Node
## Screenshot fixture (M3-BPR-02): a boss encounter's intro on the battle sandbox (the parent), live data, frozen
## `hold_share` of the way through its hold (the camera on the boss, the title card fully shown). Instant pacing and
## no floats, as the arena shots; the intro is forced on with its clock held. shots.json battle_boss_intro_*.

@export var encounter: StringName = &""
@export var party: Array[StringName] = [&"rhen"]
@export var rng_seed := 20261024
@export var hold_share := 0.5


func _ready() -> void:
	_start.call_deferred()


func _start() -> void:
	var ctl := get_parent() as BattleController
	ctl.pacing_scale = 0.0
	ctl.show_damage_numbers = false
	ctl.hud.apply_settings(UiSettings.new())
	var none: Array[StringName] = []
	ctl.start_battle(party, none, encounter, rng_seed)
	var choreo := ctl.stage.choreo
	choreo.speed = 1.0
	choreo.reduced_motion = false
	choreo.skip = false
	var intro := BattleBossIntro.of(ctl.stage)
	intro.force_play = true
	intro.live = false
	intro.play()
	intro.advance(float(intro.cfg.get("camera_in_sec", 0.0)) + float(intro.row.get("hold_sec", 0.0)) * hold_share)
