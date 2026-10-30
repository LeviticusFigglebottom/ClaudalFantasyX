extends Node3D
## Review stage for the Kirru crowd bodies (the Lead, 2026-10-30; assets_src/crowd/kirru/kirru_bodies.json): each body
## as the VillagerLayer gives a `body` row, idling out of step on Pell's field clips (crowd_kirru_clips.tres), with
## Pell himself at the end of the row for scale and likeness (kirru_lineup_front, kirru_lineup_faces).

const BODIES := "res://assets_src/crowd/kirru/kirru_bodies.json"
const PELL := "res://assets/characters/pell/pell.glb"
## Lineup spacing (m).
@export var spacing_m := 1.2


func _ready() -> void:
	var ids: Array = (VillagerLayer.load_data(BODIES).get("bodies", {}) as Dictionary).keys()
	ids.sort()
	var row := Node3D.new()
	row.name = "Lineup"
	add_child(row)
	for i in ids.size():
		var id := str(ids[i])
		var npc := FieldNpc.new()
		npc.name = id
		npc.npc_id = StringName(id)
		npc.actor_scene = load(VillagerLayer.CROWD_ACTOR_PATH % [id, id]) as PackedScene
		npc.position = Vector3((i - ids.size() * 0.5) * spacing_m, 0.0, 0.0)
		npc.rotation.y = PI  # FieldNpc faces -Z; the cameras look from +Z
		row.add_child(npc)
	var pell := (load(PELL) as PackedScene).instantiate() as Node3D
	pell.name = "Pell"
	pell.position = Vector3(ids.size() * 0.5 * spacing_m, 0.0, 0.0)
	row.add_child(pell)
	for player: Node in pell.find_children("*", "AnimationPlayer", true, false):
		var ap := player as AnimationPlayer
		if ap.has_animation(&"idle"):
			ap.play(&"idle")
