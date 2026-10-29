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

var _materials_assigned := false
## Material paths request_materials() started loading on other threads (M2-ENV-05).
var _requested: PackedStringArray = []


func _ready() -> void:
	apply()


## M2-ENV-05: starts loading the replacement materials (and their textures) on the loader's threads, so
## they decode while HalunaZone.prebuild() dresses the zone; assign_materials() then collects them. Same
## paths as _assign_materials() would load. Safe off the tree.
func request_materials() -> void:
	model = get_child(0) as Node3D if get_child_count() > 0 else null
	if model == null or materials_dir == "" or _materials_assigned:
		return
	for path in _material_paths():
		if not path in _requested and ResourceLoader.load_threaded_request(path, "", true) == OK:
			_requested.append(path)


## Replaces the imported materials (once). M2-FP-05: loading them cost ~1 s on the main thread, so
## HalunaZone.prebuild() calls this off the tree, on the thread that instantiates the zone.
func assign_materials() -> void:
	if _materials_assigned:
		return
	_materials_assigned = true
	model = get_child(0) as Node3D if get_child_count() > 0 else null
	if model != null:
		_assign_materials()


## Assigns the materials (unless done already) and poses the skeleton. Needs the tree (the pose is
## measured in global space, where the skeleton's bone transforms are up to date).
func apply() -> void:
	assign_materials()
	model = get_child(0) as Node3D if get_child_count() > 0 else null
	if model == null:
		return
	var found := model.find_children("*", "Skeleton3D", true, false)
	if found.is_empty():
		return
	skeleton = found[0] as Skeleton3D
	skeleton.reset_bone_poses()
	model.position = Vector3.ZERO
	# M2-FP-103: a real clip (the cutscene's @anim) carries its own ground contact, so the static pose's
	# lowering comes off the moment one starts; otherwise a kneel clip kneels into the sand.
	var ap := model.find_child("AnimationPlayer", true, false) as AnimationPlayer
	if ap != null and not ap.animation_started.is_connected(_on_clip_started):
		ap.animation_started.connect(_on_clip_started)
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
	HeroHelperBones.drive(skeleton)  # M2-ENV-14: the skirt panels and shoulder correctives follow the hand-set pose
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
			var path := _material_path(mi.mesh.surface_get_material(s))
			if path != "":
				mi.set_surface_override_material(s, _take(path))


## The replacement material's path for an imported surface material, or "" when there is none.
func _material_path(src: Material) -> String:
	if src == null:
		return ""
	var path := materials_dir.path_join(src.resource_name + ".tres")
	return path if ResourceLoader.exists(path) else ""


func _material_paths() -> PackedStringArray:
	var out := PackedStringArray()
	for n in model.find_children("*", "MeshInstance3D", true, false):
		var mi := n as MeshInstance3D
		if mi.mesh == null:
			continue
		for s in mi.mesh.get_surface_count():
			var path := _material_path(mi.mesh.surface_get_material(s))
			if path != "" and not path in out:
				out.append(path)
	return out


## The material at `path`: from its threaded load when request_materials() started one (waits for it),
## else loaded now.
func _take(path: String) -> Material:
	if path in _requested:
		var got := ResourceLoader.load_threaded_get(path) as Material
		if got != null:
			return got
	return load(path) as Material


func _on_clip_started(_clip: StringName) -> void:
	if model != null and is_instance_valid(model):
		model.position = Vector3.ZERO
