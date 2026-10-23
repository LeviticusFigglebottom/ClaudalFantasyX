class_name HalunaActorPose
extends Node3D
## Holds a still placeholder pose on an imported character (M2-FP-02): the Haluna cutscene stage's
## Asha kneels on the beach until the cutscene system animates her. The node stays on the ground at
## its mark; its first child (the character scene) is posed and lowered so `ground_bones` touch it.
## Bones turn in the actor's own frame (X her left, Y up, Z the way she faces), in dictionary order
## (list parents before children), like the character stage's world_pose (asha_stage.gd).

## Bone name -> Euler degrees about the actor's axes.
@export var world_pose: Dictionary = {}
## Bones whose origins rest on the ground after posing (a knee, an ankle). Empty = no lowering.
@export var ground_bones: PackedStringArray = []
## Height of those bone origins above the ground (joint radius).
@export var ground_clearance_m: float = 0.0
## Folder of the character's shading materials: each imported surface material is replaced by
## `<dir>/<its name>.tres` when that exists (as the character stage does). Empty = keep the import's.
@export_dir var materials_dir: String = ""

var skeleton: Skeleton3D
var model: Node3D


func _ready() -> void:
	apply()


func apply() -> void:
	model = get_child(0) as Node3D if get_child_count() > 0 else null
	if model == null:
		return
	var found := model.find_children("*", "Skeleton3D", true, false)
	if found.is_empty():
		return
	skeleton = found[0] as Skeleton3D
	_assign_materials()
	skeleton.reset_bone_poses()
	model.position = Vector3.ZERO
	var rel := global_basis.orthonormalized().inverse() * skeleton.global_basis.orthonormalized()
	for bone_name: Variant in world_pose:
		var idx := skeleton.find_bone(String(bone_name))
		if idx < 0:
			push_warning("HalunaActorPose %s: no bone %s" % [name, bone_name])
			continue
		skeleton.force_update_all_bone_transforms()
		var deg: Vector3 = world_pose[bone_name]
		var turn := Basis.from_euler(Vector3(deg_to_rad(deg.x), deg_to_rad(deg.y), deg_to_rad(deg.z)))
		turn = rel.inverse() * turn * rel
		var global_pose := turn * skeleton.get_bone_global_pose(idx).basis
		var parent := skeleton.get_bone_parent(idx)
		var parent_basis := Basis.IDENTITY if parent < 0 else skeleton.get_bone_global_pose(parent).basis
		skeleton.set_bone_pose_rotation(idx, (parent_basis.inverse() * global_pose).get_rotation_quaternion())
	skeleton.force_update_all_bone_transforms()
	if ground_bones.is_empty():
		return
	var lowest := INF
	var to_self := global_transform.affine_inverse() * skeleton.global_transform
	for bone_name in ground_bones:
		var idx := skeleton.find_bone(bone_name)
		if idx >= 0:
			lowest = minf(lowest, (to_self * skeleton.get_bone_global_pose(idx).origin).y)
	if lowest < INF:
		model.position.y = ground_clearance_m - lowest


func _assign_materials() -> void:
	if materials_dir == "":
		return
	for n in model.find_children("*", "MeshInstance3D", true, false):
		var mi := n as MeshInstance3D
		if mi.mesh == null:
			continue
		for s in mi.mesh.get_surface_count():
			var src := mi.mesh.surface_get_material(s)
			if src == null:
				continue
			var path := materials_dir.path_join(src.resource_name + ".tres")
			if ResourceLoader.exists(path):
				mi.set_surface_override_material(s, load(path) as Material)
