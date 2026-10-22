extends Node3D
## Field test zone driver (M1-ARC-01): places the player on a named spawn marker and snaps the
## camera director, so tests and screenshot shots start from a known frame. Three volumes:
## Lane (fixed shot), Court (pan-follow), Causeway (dolly, priority 1, overlapping the court).

## Name of a Marker3D under Spawns/.
@export var start_spawn: StringName = &"Lane"
## Yaw (degrees) the player faces at the spawn.
@export var start_yaw_deg: float = 0.0

@onready var player: FieldController = $Player
@onready var director: FieldCameraDirector = $CameraDirector


func _ready() -> void:
	place_at(start_spawn, start_yaw_deg)


## Moves the player to Spawns/<spawn> and snaps the camera (teleport-style).
func place_at(spawn: StringName, yaw_deg: float = 0.0) -> bool:
	var marker := get_node_or_null(NodePath("Spawns/%s" % spawn)) as Marker3D
	if marker == null:
		push_warning("field_test: no spawn '%s'" % spawn)
		return false
	player.global_position = marker.global_position
	player.rotation.y = deg_to_rad(yaw_deg)
	player.velocity = Vector3.ZERO
	if player.motor != null:
		player.motor.facing_yaw = player.rotation.y
	director.snap()
	return true
