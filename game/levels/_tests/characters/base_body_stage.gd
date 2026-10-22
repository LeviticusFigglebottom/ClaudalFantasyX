class_name BaseBodyStage
extends Node3D
## One turntable stage for the M1-CHR-01 base-body review (neutral three-point light, grey backdrop).
## Instances `body_scene` (a base_body_<variant>.glb) under the Turntable node. With `spin_degrees_per_second`
## left at 0 the pose is static, which the screenshot shots rely on; set it to orbit the body when viewing by hand.
## The Face camera is aimed at the midpoint of the DEF-eye bones, so it frames any variant's head.
## The imported body is PLACEHOLDER art (SPEC §8.4): the tag is copied onto the instance's metadata.

@export var body_scene: PackedScene
@export var spin_degrees_per_second: float = 0.0
@export var face_distance: float = 1.35
@export var face_yaw_degrees: float = 30.0
@export var face_aim_drop: float = 0.035
## Deformation check: bone name -> local Euler rotation in degrees, applied once at _ready.
@export var test_pose: Dictionary = {}

@onready var _turntable: Node3D = $Turntable
@onready var _face_camera: Camera3D = $Cameras/Face


func _ready() -> void:
	if body_scene == null:
		push_warning("BaseBodyStage %s: no body_scene" % name)
		return
	var body := body_scene.instantiate() as Node3D
	body.name = "Body"
	body.set_meta(&"hymn_tag", &"PLACEHOLDER")
	_turntable.add_child(body)
	_aim_face_camera(body)
	_apply_test_pose(body)


func _process(delta: float) -> void:
	if spin_degrees_per_second != 0.0:
		_turntable.rotate_y(deg_to_rad(spin_degrees_per_second) * delta)


func _find_skeleton(body: Node3D) -> Skeleton3D:
	var skeletons := body.find_children("*", "Skeleton3D", true, false)
	return null if skeletons.is_empty() else skeletons[0] as Skeleton3D


func _apply_test_pose(body: Node3D) -> void:
	var skel := _find_skeleton(body)
	if skel == null or test_pose.is_empty():
		return
	for bone_name: Variant in test_pose:
		var idx := skel.find_bone(String(bone_name))
		if idx < 0:
			push_warning("BaseBodyStage: no bone %s" % bone_name)
			continue
		var deg: Vector3 = test_pose[bone_name]
		var extra := Basis.from_euler(Vector3(deg_to_rad(deg.x), deg_to_rad(deg.y), deg_to_rad(deg.z)))
		var rest := skel.get_bone_rest(idx).basis
		skel.set_bone_pose_rotation(idx, (rest * extra).get_rotation_quaternion())


func _aim_face_camera(body: Node3D) -> void:
	var skel := _find_skeleton(body)
	if skel == null:
		return
	var left := skel.find_bone("DEF-eye.L")
	var right := skel.find_bone("DEF-eye.R")
	if left < 0 or right < 0:
		return
	var mid_local := (skel.get_bone_global_rest(left).origin + skel.get_bone_global_rest(right).origin) * 0.5
	var target := skel.global_transform * mid_local - Vector3(0.0, face_aim_drop, 0.0)
	var yaw := deg_to_rad(face_yaw_degrees)
	var eye := target + Vector3(-sin(yaw), 0.0, cos(yaw)) * face_distance
	_face_camera.look_at_from_position(eye, target, Vector3.UP)
