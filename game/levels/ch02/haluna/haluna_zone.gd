class_name HalunaZone
extends Node3D
## The playable Haluna zone (M2-FP-02; README.md beside this file). It instances Environment's mood
## scene (terrain, kit dressing, sea, sun, the save shrine) without editing it, and adds what play
## needs: walk collision built at runtime (HalunaCollision), Rhen as a FieldController under the
## FieldCameraDirector's volumes (a hub orbit as the whole-zone fallback), spawns, three villagers,
## the battle and causeway triggers, and the CutsceneStage for Cutscene A.
##
## This script only places things. The story driver listens on FieldEvents for the NPC barks
## (`payload.dialogue`), the tideline battle (`payload.battle`) and the causeway head
## (`payload.cutscene`), and plays Cutscene A on `stage`.

## Spawn used at _ready (a loader then calls place_at with its own spawn).
@export var start_spawn: StringName = &"Shrine"
## Raised above the marker on placement so the capsule settles onto the ground.
@export var spawn_lift_m: float = 0.02

@onready var player: FieldController = $Player
@onready var director: FieldCameraDirector = $CameraDirector
@onready var stage: CutsceneStage = $CutsceneStage
@onready var collision: HalunaCollision = $Collision
@onready var mood: Node3D = $HalunaMood
@onready var field_camera: Camera3D = $FieldCamera


func _ready() -> void:
	_release_mood_cameras()
	collision.build()
	field_camera.make_current()
	# After Cutscene A the girl and the guardian have walked up to the village.
	set_beach_cast_visible(not bool(Game.get_flag(&"ch02_met_asha")))
	place_at(start_spawn, spawn_yaw_deg(start_spawn))


## Moves the player to Spawns/<spawn>, facing `yaw_deg`, and snaps the camera (teleport-style).
func place_at(spawn: StringName, yaw_deg: float = 0.0) -> bool:
	var marker := spawn_marker(spawn)
	if marker == null:
		push_warning("HalunaZone: no spawn '%s'" % spawn)
		return false
	player.global_position = marker.global_position + Vector3.UP * spawn_lift_m
	player.rotation.y = deg_to_rad(yaw_deg)
	player.velocity = Vector3.ZERO
	if player.motor != null:
		player.motor.facing_yaw = player.rotation.y
	director.snap()
	return true


func spawn_marker(spawn: StringName) -> Marker3D:
	return get_node_or_null(NodePath("Spawns/%s" % spawn)) as Marker3D


## The facing authored on a spawn marker, in degrees (what WorldReturn passes to place_at).
func spawn_yaw_deg(spawn: StringName) -> float:
	var marker := spawn_marker(spawn)
	return rad_to_deg(marker.rotation.y) if marker != null else 0.0


func spawn_names() -> Array[StringName]:
	var out: Array[StringName] = []
	for m in get_node(^"Spawns").get_children():
		out.append(StringName(m.name))
	return out


## Shows or hides Cutscene A's cast (Actors under the stage); the player is never touched.
func set_beach_cast_visible(on: bool) -> void:
	var actors := stage.get_node_or_null(CutsceneStage.ACTORS)
	if actors == null:
		return
	for a in actors.get_children():
		(a as Node3D).visible = on


## The mood scene's five composed HalunaShotCameras (H01 is current there) must not take the view.
func _release_mood_cameras() -> void:
	for n in mood.find_children("*", "Camera3D", true, false):
		(n as Camera3D).current = false
