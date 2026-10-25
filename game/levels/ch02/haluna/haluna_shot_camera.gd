class_name HalunaShotCamera
extends Camera3D
## A composed mood-test camera driven by a CameraShot resource (field_camera.md): the same FIXED
## framing, vertical FOV and depth of field the FieldCameraDirector would apply, so the five ◆ shots
## of haluna.md §5.1 can drop straight into the zone's camera volumes later.

@export var shot: CameraShot


func _ready() -> void:
	apply_shot()


func apply_shot() -> void:
	if shot == null:
		return
	keep_aspect = Camera3D.KEEP_HEIGHT
	var pose := CameraPose.looking(shot.position, shot.look_at, shot.fov_deg, shot.dof_dict(), shot.roll_deg)
	pose.apply_to(self)
