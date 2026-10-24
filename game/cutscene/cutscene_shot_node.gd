class_name CutsceneShotNode
extends Node
## Holds one authored CameraShot under a CutsceneStage's Shots folder (M2-FP-01). Shot positions
## are in the director's rail space (the level root by default), like CameraVolume shots.

## AUTO keys the cast when the shot frames them at dialogue or portrait range (CutsceneKeyLight);
## ON and OFF force it either way (M2-FP-10).
enum KeyLight { AUTO, ON, OFF }

@export var shot: CameraShot

@export_group("Key light (M2-FP-10)")
@export var key_light: KeyLight = KeyLight.AUTO
## Turns the key away from the sun's direction about world up (positive = counter-clockwise).
@export var key_yaw_deg: float = 0.0
## Tilts the key about its own X axis (positive lowers it toward the horizon).
@export var key_pitch_deg: float = 0.0
## Multiplies the sun's intensity.
@export var key_energy_scale: float = 1.0


## `shot.id`, or the node name when the shot has no id.
func shot_id() -> StringName:
	if shot != null and shot.id != &"":
		return shot.id
	return StringName(name)
