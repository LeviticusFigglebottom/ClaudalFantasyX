class_name CutsceneShotNode
extends Node
## Holds one authored CameraShot under a CutsceneStage's Shots folder (M2-FP-01). Shot positions
## are in the director's rail space (the level root by default), like CameraVolume shots.

@export var shot: CameraShot


## `shot.id`, or the node name when the shot has no id.
func shot_id() -> StringName:
	if shot != null and shot.id != &"":
		return shot.id
	return StringName(name)
