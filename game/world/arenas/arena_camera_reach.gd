class_name ArenaCameraReach
extends Node
## A storm arena's reach (the human's 11-03 FAST-TRACK 4; docs/kb/tech/battle_arenas.md): the Undertow stands
## kilometres off, past Godot's default far plane (4 km). While this node is in the tree, whichever camera draws (the
## battle camera, a boss intro's, a shot rig's) reaches at least `far_m`. A child of the arena, not its root: the
## battle moves an arena's children under its own Arena node and frees the root (BattleArena.apply).

## The far plane (m) the drawing camera needs at least.
@export var far_m: float = 0.0


func _ready() -> void:
	set_process(far_m > 0.0 and not Engine.is_editor_hint())


func _process(_delta: float) -> void:
	var cam := get_viewport().get_camera_3d()
	if cam != null and cam.far < far_m:
		cam.far = far_m
