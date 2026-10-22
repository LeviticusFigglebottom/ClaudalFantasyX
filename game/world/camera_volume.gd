class_name CameraVolume
extends Area3D
## A region of a field zone that selects an authored CameraShot (SPEC §6.6, M1-ARC-01).
## When the player stands inside several volumes, the highest `shot_priority` wins; equal priorities
## go to the volume entered most recently. Leaving every volume keeps the last shot (a composed
## frame is never dropped for a fallback). Containment is tested geometrically (FieldShapes)
## by FieldCameraDirector, so the volume needs one or more CollisionShape3D children but no
## physics layers; monitoring is turned off to keep it free.

const GROUP := &"field_camera_volume"

@export var shot: CameraShot
@export var shot_priority: int = 0
## Overrides the incoming shot's blend duration for transitions INTO this volume (-1 = shot's).
@export var blend_sec_override: float = CameraShot.USE_DEFAULT
## Forces a hard cut on entry regardless of the shot's own setting.
@export var force_hard_cut: bool = false


func _ready() -> void:
	add_to_group(GROUP)
	monitoring = false
	monitorable = false
	if shot == null:
		push_warning("CameraVolume %s has no shot" % get_path())


func contains_point(world_point: Vector3, epsilon: float = 0.0) -> bool:
	return FieldShapes.area_contains(self, world_point, epsilon)


func shot_id() -> StringName:
	return shot.id if shot != null else &""
