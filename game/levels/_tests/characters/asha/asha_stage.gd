class_name AshaStage
extends Node3D
## M1-CHR-02 turntable / portrait stage for Asha at final fidelity. Lighting matches the M1-RND-04
## shading test (warm key #FFB87B, dusk rim #F2A64A, muted dome). Instances `character_scene`
## (assets/characters/asha/asha.glb), swaps every imported material for the hero shader material
## of the same name (`materials`), and applies a face pose, a verse-sleeve state and a test pose so
## each screenshot is a pure function of its exported settings. Docs:
## docs/kb/art/characters/asha_review.md.

## glTF material name -> hero material (skin_head, hair, cloth_sleeve, ...).
@export var materials: Dictionary = {}
@export var character_scene: PackedScene
## Emotion tag from game/data/dialogue/emotions.json, resolved through `face_poses`.
@export var emotion: String = "neutral"
## Extra blendshape weights on top of the emotion (shape name -> weight), like a Cinematics @face.
@export var face_extra: Dictionary = {}
## JSON with {"emotions": {tag: {shape: weight | [L, R]}}} (asha.md §6.3).
@export_file("*.json") var face_poses_path: String = ""
## Verse-sleeve state (asha.md §3.1): bands n <= verse_count are revealed.
@export_range(0, 7) var verse_count: int = 0
## Deformation check: bone name -> local Euler rotation in degrees, applied once at _ready.
@export var test_pose: Dictionary = {}
## Deformation check in world terms: bone name -> Euler degrees about the stage axes (X her left,
## Y up, Z the way she faces), applied in dictionary order (list parents before children).
@export var world_pose: Dictionary = {}
@export var spin_degrees_per_second: float = 0.0
@export var yaw_degrees: float = 0.0
## Portrait camera (`Cameras/Face`) aimed at the eye midpoint.
@export var face_distance: float = 0.62
@export var face_yaw_degrees: float = 25.0
@export var face_pitch_degrees: float = 0.0
@export var face_aim_drop: float = 0.03
## Wind pinned for the capture (globals; restored on exit).
@export var wind: Vector4 = Vector4.ZERO
@export var wind_time: float = 0.0
@export var tier: String = "high"
## SPEC §14 comparison: a second Asha at `compare_offset` whose skin materials (duplicated) get
## these shader parameters, e.g. {"painterly": 0.65}. Empty = no second character.
@export var compare_offset: Vector3 = Vector3.ZERO
@export var compare_skin: Dictionary = {}
@export var compare_face: Dictionary = {}

var _saved_globals: Dictionary = {}
var _character: Node3D

@onready var _turntable: Node3D = $Turntable


func _ready() -> void:
	_pin_wind()
	if character_scene == null:
		push_warning("AshaStage %s: no character_scene" % name)
		return
	_character = character_scene.instantiate() as Node3D
	_character.name = &"Asha"
	_turntable.rotation_degrees.y = yaw_degrees
	_turntable.add_child(_character)
	_assign_materials(_character)
	CharacterShaderTiers.apply_to_tree(_character, tier)
	_apply_face(_character)
	_apply_pose(_character)
	_aim_face_camera(_character)
	if not compare_skin.is_empty() or not compare_face.is_empty():
		_build_compare()


func _build_compare() -> void:
	var other := character_scene.instantiate() as Node3D
	other.name = &"AshaCompare"
	other.position = compare_offset
	other.rotation_degrees.y = yaw_degrees
	add_child(other)
	_assign_materials(other)
	CharacterShaderTiers.apply_to_tree(other, tier)
	for mi: MeshInstance3D in _meshes(other):
		for s: int in mi.get_surface_override_material_count():
			var sm := mi.get_surface_override_material(s) as ShaderMaterial
			if sm == null or sm.resource_name not in ["skin_head", "skin_body"]:
				continue
			var copy := sm.duplicate() as ShaderMaterial
			for key: String in compare_skin:
				copy.set_shader_parameter(StringName(key), compare_skin[key])
			mi.set_surface_override_material(s, copy)
	var saved := face_extra
	face_extra = saved.merged(compare_face, true)
	_apply_face(other)
	face_extra = saved


func _process(delta: float) -> void:
	if spin_degrees_per_second != 0.0:
		_turntable.rotate_y(deg_to_rad(spin_degrees_per_second) * delta)


func _exit_tree() -> void:
	for key: StringName in _saved_globals:
		RenderingServer.global_shader_parameter_set(key, _saved_globals[key])


func _pin_wind() -> void:
	for key: StringName in [&"hymn_wind", &"hymn_wind_time"]:
		var entry: Variant = ProjectSettings.get_setting("shader_globals/%s" % key, {})
		if entry is Dictionary and (entry as Dictionary).has("value"):
			_saved_globals[key] = (entry as Dictionary)["value"]
	RenderingServer.global_shader_parameter_set(&"hymn_wind", wind)
	RenderingServer.global_shader_parameter_set(&"hymn_wind_time", wind_time)


func _meshes(root: Node) -> Array[MeshInstance3D]:
	var out: Array[MeshInstance3D] = []
	var stack: Array[Node] = [root]
	while not stack.is_empty():
		var node: Node = stack.pop_back()
		stack.append_array(node.get_children())
		var mi := node as MeshInstance3D
		if mi != null and mi.mesh != null:
			out.append(mi)
	return out


func _assign_materials(root: Node) -> int:
	var count := 0
	var single_tier: Array = CharacterShaderTiers.data().get(CharacterShaderTiers.KEY_SINGLE_TIER, [])
	for mi: MeshInstance3D in _meshes(root):
		for s: int in mi.mesh.get_surface_count():
			var src := mi.mesh.surface_get_material(s)
			if src == null or not materials.has(src.resource_name):
				continue
			var mat := materials[src.resource_name] as Material
			mi.set_surface_override_material(s, mat)
			var sm := mat as ShaderMaterial
			if sm != null and sm.shader != null and single_tier.has(sm.shader.resource_path):
				mi.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
			count += 1
	# the verse-sleeve state lives on the sleeve material instance of this stage only
	for mi: MeshInstance3D in _meshes(root):
		for s: int in mi.get_surface_override_material_count():
			var sm := mi.get_surface_override_material(s) as ShaderMaterial
			if sm != null and sm.get_shader_parameter(&"verse_count") != null:
				var copy := sm.duplicate() as ShaderMaterial
				copy.set_shader_parameter(&"verse_count", verse_count)
				mi.set_surface_override_material(s, copy)
	return count


func _face_weights() -> Dictionary:
	var weights: Dictionary = {}
	if face_poses_path != "" and FileAccess.file_exists(face_poses_path):
		var data: Variant = JSON.parse_string(FileAccess.get_file_as_string(face_poses_path))
		if data is Dictionary:
			var emotions: Dictionary = (data as Dictionary).get("emotions", {})
			var pose: Dictionary = emotions.get(emotion, {})
			for shape: String in pose:
				_put_weight(weights, shape, pose[shape])
	for shape: String in face_extra:
		_put_weight(weights, shape, face_extra[shape])
	return weights


func _put_weight(weights: Dictionary, shape: String, value: Variant) -> void:
	# a pair is L/R; a scalar applies to both sides of a paired shape, or to an unpaired shape
	if value is Array:
		var pair: Array = value
		weights["%s_L" % shape] = float(pair[0])
		weights["%s_R" % shape] = float(pair[1])
	else:
		weights[shape] = float(value)
		weights["%s_L" % shape] = float(value)
		weights["%s_R" % shape] = float(value)


func _apply_face(root: Node) -> void:
	var weights := _face_weights()
	for mi: MeshInstance3D in _meshes(root):
		var mesh := mi.mesh as ArrayMesh
		if mesh == null:
			continue
		for i: int in mesh.get_blend_shape_count():
			var shape := String(mesh.get_blend_shape_name(i))
			if weights.has(shape):
				mi.set_blend_shape_value(i, float(weights[shape]))


func _skeleton(root: Node) -> Skeleton3D:
	var found := root.find_children("*", "Skeleton3D", true, false)
	return null if found.is_empty() else found[0] as Skeleton3D


func _apply_pose(root: Node) -> void:
	var skel := _skeleton(root)
	if skel == null:
		return
	_apply_local_pose(skel)
	_apply_world_pose(skel)


func _apply_world_pose(skel: Skeleton3D) -> void:
	for bone_name: Variant in world_pose:
		var idx := skel.find_bone(String(bone_name))
		if idx < 0:
			push_warning("AshaStage: no bone %s" % bone_name)
			continue
		skel.force_update_all_bone_transforms()
		var deg: Vector3 = world_pose[bone_name]
		var turn := Basis.from_euler(Vector3(deg_to_rad(deg.x), deg_to_rad(deg.y), deg_to_rad(deg.z)))
		var to_skel := skel.global_transform.basis.orthonormalized().inverse()
		turn = to_skel * turn * to_skel.inverse()
		var global_basis := turn * skel.get_bone_global_pose(idx).basis
		var parent := skel.get_bone_parent(idx)
		var parent_basis := Basis.IDENTITY if parent < 0 else skel.get_bone_global_pose(parent).basis
		skel.set_bone_pose_rotation(idx, (parent_basis.inverse() * global_basis).get_rotation_quaternion())


func _apply_local_pose(skel: Skeleton3D) -> void:
	if test_pose.is_empty():
		return
	for bone_name: Variant in test_pose:
		var idx := skel.find_bone(String(bone_name))
		if idx < 0:
			push_warning("AshaStage: no bone %s" % bone_name)
			continue
		var deg: Vector3 = test_pose[bone_name]
		var extra := Basis.from_euler(Vector3(deg_to_rad(deg.x), deg_to_rad(deg.y), deg_to_rad(deg.z)))
		var rest := skel.get_bone_rest(idx).basis
		skel.set_bone_pose_rotation(idx, (rest * extra).get_rotation_quaternion())


func _aim_face_camera(root: Node) -> void:
	var cam := get_node_or_null(^"Cameras/Face") as Camera3D
	var skel := _skeleton(root)
	if cam == null or skel == null:
		return
	var left := skel.find_bone("DEF-eye.L")
	var right := skel.find_bone("DEF-eye.R")
	if left < 0 or right < 0:
		return
	skel.force_update_all_bone_transforms()
	var mid := (skel.get_bone_global_pose(left).origin + skel.get_bone_global_pose(right).origin) * 0.5
	var target := skel.global_transform * mid - Vector3(0.0, face_aim_drop, 0.0)
	var yaw := deg_to_rad(face_yaw_degrees)
	var pitch := deg_to_rad(face_pitch_degrees)
	var dir := Vector3(sin(yaw) * cos(pitch), sin(pitch), cos(yaw) * cos(pitch))
	cam.look_at_from_position(target + dir * face_distance, target, Vector3.UP)
