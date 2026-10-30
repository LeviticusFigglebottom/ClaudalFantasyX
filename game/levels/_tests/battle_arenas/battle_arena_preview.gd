extends Node3D
## Battle arena preview (M2-ENV-11, screenshot fixture): one arena with the battle sandbox's slot layout
## and BattleCamera framing (read from battle_sandbox.tscn by BattleArenaLayout, so it follows Combat's
## scene) and the sandbox's stand-ins on the slots (FighterStandIn with battle_sandbox.json's specs).
## No battle runs: this is the frame the player sees before the first turn.

## The arena scene (assets/environments/arenas/<id>/<id>.tscn).
@export var arena_scene: PackedScene
## Combatant ids on the party and enemy slots, in slot order (stand-in specs from battle_sandbox.json).
@export var party: Array[StringName] = []
@export var enemies: Array[StringName] = []

@onready var _camera: Camera3D = $BattleCamera


func _ready() -> void:
	var arena := arena_scene.instantiate()
	arena.name = "Arena"
	add_child(arena)
	var layout := BattleArenaLayout.read()
	if layout.is_empty():
		return
	_camera.transform = layout["camera"]
	_camera.fov = float(layout["fov"])
	_camera.current = true
	var stage := Node3D.new()
	stage.name = "Fighters"
	add_child(stage)
	_seat(stage, party, layout["party"])
	_seat(stage, enemies, layout["enemy"])
	_frame_as_the_fight(stage, layout)


## The PC's GPU QA row 61: a boss previewed on Slot0 under the authored camera is not the frame its fight shows. As the
## battle does, a boss with a battle_sandbox.json boss_seats mark stands there (EnemySlots space; M3-CRB-011) and the
## camera takes its camera.rest_by_enemy fit (BattleCameraDirector.rest_fit; M3-BPR-425).
func _frame_as_the_fight(stage: Node3D, layout: Dictionary) -> void:
	if enemies.is_empty():
		return
	var seat: Variant = (BattleStage.config().get("boss_seats", {}) as Dictionary).get(String(enemies[0]))
	if seat is Array and (seat as Array).size() == 3:
		var v := seat as Array
		var f := stage.get_child(party.size()) as Node3D
		f.position = (layout["enemy_slots"] as Transform3D) * Vector3(float(v[0]), float(v[1]), float(v[2]))
	var fit := BattleCameraDirector.rest_fit(
		BattleChoreo.load_data().get("camera", {}) as Dictionary, _camera.transform, _camera.fov, enemies
	)
	_camera.transform = fit[0]
	_camera.fov = float(fit[1])


func _seat(stage: Node3D, ids: Array[StringName], slots: Array) -> void:
	for i in mini(ids.size(), slots.size()):
		var f := FighterStandIn.new()
		f.setup(ids[i], BattleStage.stand_in_spec(ids[i]), {})
		f.transform = slots[i]
		stage.add_child(f)
		f.set_ring(FighterStandIn.RING_NONE, Color.WHITE)
