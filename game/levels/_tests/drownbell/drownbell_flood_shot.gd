extends Node
## Screenshot fixture (M2-RND-04): the Drownbell's Flood phase at full height, with its two polyps glowing under
## the water, on the battle sandbox (the parent). Starts the boss battle, enters the Flood through BossMechanics
## (as the fight does at 40% HP) and holds the water at the flood's top so the frame needs no 8 s rise.

const PARTY: Array[StringName] = [&"rhen", &"asha", &"toma"]
const SEED := 20261023
const FLOOD_HP_PCT := 40


func _ready() -> void:
	_start.call_deferred()


func _start() -> void:
	var ctl := get_parent() as BattleController
	ctl.set_meta(BattleBossIntro.META_PLAYED, "drownbell")  # M3-BPR-02: a flood frame, not the boss's intro
	ctl.start_battle(PARTY, [], &"drownbell", SEED)
	var bell := ctl.engine.enemies[0]
	bell.hp = bell.max_hp * FLOOD_HP_PCT / 100
	BossMechanics.check_phases(ctl.engine)
	var boss := (ctl.stage.get_node(^"BattleVfx") as BattleVfx).boss
	boss.settle()
	ctl.stage.settle_actors()  # M2-CRE-08: the bell model's sink and tilt, at their end
	# M3-BPR-426's phase moment (the camera eases onto the bell as the Flood starts) is not this frame: the big17 gate
	# froze it mid push-in, the party out of shot.
	ctl.stage.choreo.camera.end_moment()
