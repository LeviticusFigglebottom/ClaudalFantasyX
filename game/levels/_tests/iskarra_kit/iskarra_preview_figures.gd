extends Node3D
## The Iskarra preview's figures (M3-ENV-724): the heroes that have models, standing at their Prologue vigil marks
## as the battle stand-ins (FighterStandIn, its idle), so the shots read the city's scale against real people
## instead of capsules. The Prologue's own staging is slice-polish's (game/levels/prologue/). Ysolde stays out until
## her battle stand-in has its scene (M2-HER-1108): until then it is a capsule, which read as a prop at I02's edge.

## Hero ids, one per mark.
@export var heroes: Array[StringName] = []
## Feet positions and the yaw (degrees) each faces, one per hero.
@export var marks: Array[Vector3] = []
@export var yaws_deg: Array[float] = []


func _ready() -> void:
	for i in mini(heroes.size(), marks.size()):
		var f := FighterStandIn.new()
		f.setup(heroes[i], BattleStage.stand_in_spec(heroes[i]), {})
		var yaw := deg_to_rad(yaws_deg[i]) if i < yaws_deg.size() else 0.0
		f.transform = Transform3D(Basis(Vector3.UP, yaw), marks[i])
		add_child(f)
		f.set_ring(FighterStandIn.RING_NONE, Color.WHITE)
