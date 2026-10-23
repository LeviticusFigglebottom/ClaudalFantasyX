class_name CharacterShadingStage
extends Node3D
## M1-RND-04 character shading test stage: assigns the test materials to the procedural test
## meshes (assets/characters/shader_test/), pins the wind globals so captures are deterministic,
## and builds the side-by-side High / Low comparison rig. Docs: docs/kb/tech/character_shading.md.

## Mesh node name -> material, applied to every instance of the test scenes below.
@export var node_materials: Dictionary = {}
## Tier applied to the whole stage at start ("high", "medium" or "low"); handy for previews.
@export var tier: String = "high"
## Second bust instanced for the comparison shot: one copy at `compare_origin` keeps the stage
## tier, a copy offset by `compare_offset` gets `compare_tier` on duplicated materials.
@export var compare_scene: PackedScene
@export var compare_origin: Vector3 = Vector3.ZERO
@export var compare_offset: Vector3 = Vector3.ZERO
@export var compare_rotation_deg: float = 0.0
@export var compare_tier: String = "low"
## Cloth layout: the cloth test scene holds a drape and a sleeve at the same origin.
@export var sleeve_offset: Vector3 = Vector3.ZERO
@export var dissolve_sleeve_offset: Vector3 = Vector3.ZERO
@export var dissolve_sleeve_material: Material
## Wind pinned for the capture (globals; restored on exit so other scenes are unaffected).
@export var wind: Vector4 = Vector4.ZERO
@export var wind_time: float = 0.0

var _saved_globals: Dictionary = {}


func _ready() -> void:
	_pin_wind()
	_assign(self)
	_layout_cloth()
	CharacterShaderTiers.apply_to_tree(self, tier)
	if compare_scene != null:
		_build_compare()


func _exit_tree() -> void:
	# Restore the project defaults ([shader_globals] in project.godot); reading the live value
	# back (global_shader_parameter_get) is editor-only and slow.
	for key: StringName in _saved_globals:
		RenderingServer.global_shader_parameter_set(key, _saved_globals[key])


func _pin_wind() -> void:
	for key: StringName in [&"hymn_wind", &"hymn_wind_time"]:
		var entry: Variant = ProjectSettings.get_setting("shader_globals/%s" % key, {})
		if entry is Dictionary and (entry as Dictionary).has("value"):
			_saved_globals[key] = (entry as Dictionary)["value"]
	RenderingServer.global_shader_parameter_set(&"hymn_wind", wind)
	RenderingServer.global_shader_parameter_set(&"hymn_wind_time", wind_time)


func _assign(root: Node) -> int:
	var count := 0
	var single_tier: Array = CharacterShaderTiers.data().get(CharacterShaderTiers.KEY_SINGLE_TIER, [])
	var stack: Array[Node] = [root]
	while not stack.is_empty():
		var node: Node = stack.pop_back()
		stack.append_array(node.get_children())
		var gi := node as GeometryInstance3D
		if gi != null and node_materials.has(String(node.name)):
			var mat := node_materials[String(node.name)] as Material
			gi.material_override = mat
			# Eye shells (cornea, occlusion, tear line) must never cast shadows into the eye.
			var sm := mat as ShaderMaterial
			if sm != null and sm.shader != null and single_tier.has(sm.shader.resource_path):
				gi.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
			count += 1
	return count


func _layout_cloth() -> void:
	var sleeve := find_child("Sleeve", true, false) as MeshInstance3D
	if sleeve == null:
		return
	sleeve.position += sleeve_offset
	if dissolve_sleeve_material != null:
		var copy := sleeve.duplicate() as MeshInstance3D
		copy.name = &"SleeveDissolve"
		copy.position += dissolve_sleeve_offset - sleeve_offset
		copy.material_override = dissolve_sleeve_material
		sleeve.get_parent().add_child(copy)


func _build_compare() -> void:
	var rig := Node3D.new()
	rig.name = &"CompareRig"
	add_child(rig)
	var high := compare_scene.instantiate() as Node3D
	high.name = &"CompareHigh"
	high.position = compare_origin
	high.rotation_degrees.y = compare_rotation_deg
	rig.add_child(high)
	_assign(high)
	var low := compare_scene.instantiate() as Node3D
	low.name = &"CompareLow"
	low.position = compare_origin + compare_offset
	low.rotation_degrees.y = compare_rotation_deg
	rig.add_child(low)
	_assign(low)
	# Duplicate before swapping so the High copy (and the main bust) keep their tier.
	var stack: Array[Node] = [low]
	while not stack.is_empty():
		var node: Node = stack.pop_back()
		stack.append_array(node.get_children())
		var gi := node as GeometryInstance3D
		if gi != null and gi.material_override != null:
			gi.material_override = gi.material_override.duplicate()
	CharacterShaderTiers.apply_to_tree(low, compare_tier)
