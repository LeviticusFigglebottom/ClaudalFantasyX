class_name VegetationScatter
extends MultiMeshInstance3D
## Seeded MultiMesh scatter of one vegetation mesh over a rectangle (M1-ENV-02). Deterministic: the
## same seed and settings give the same instances. Density is thinned by seeded patch noise (so
## clumps gather in drifts) and by a falloff towards the +X edge (the sea side of a Haluna beach).

## Scene that holds the mesh (a vegetation .glb) and the name of the mesh node inside it.
@export var source_scene: PackedScene
@export var mesh_node: StringName = &"saltgrass_a"
## Material applied to every instance (the glTF placeholder is ignored).
@export var material: Material
@export var count: int = 400
## Half extents (m) of the rectangle in local X and Z.
@export var half_extents_m: Vector2 = Vector2(6.0, 20.0)
@export var seed_value: int = 1
@export var scale_min: float = 0.75
@export var scale_max: float = 1.25
## 0 = uniform; 1 = no instances at the +X edge.
@export_range(0.0, 1.0) var sea_side_falloff: float = 0.6
## Patch noise: frequency (1/m) and how strongly it removes instances (0 = off). Instances survive
## where the noise (-1..1) is above `patch_threshold`, with a soft edge of `patch_softness`.
@export var patch_frequency: float = 0.12
@export_range(0.0, 1.0) var patch_strength: float = 0.7
@export_range(-1.0, 1.0) var patch_threshold: float = -0.1
@export_range(0.01, 1.0) var patch_softness: float = 0.25
## Instances closer than this to any point in `keep_clear` (xz, with radius in z of Vector3) are skipped.
@export var keep_clear: Array[Vector3] = []
## Attempts per requested instance before giving up (rejection sampling).
@export var max_attempts_factor: int = 6
## M2-ENV-11 (battle arenas): drop every instance onto this node's meshes (the first MeshInstance3D under
## it whose name has no "-lod" suffix: a kit ground .glb's LOD0), by a ray straight down in this scatter's
## frame. Instances that miss it, or land outside [height_min_m, height_max_m] in world Y, are skipped.
## Unset (the default), instances stay on this node's local plane, as before.
@export var ground: Node3D
@export var height_min_m: float = -1000.0
@export var height_max_m: float = 1000.0
## How far above the local plane the drop ray starts (m).
@export var ground_ray_from_m: float = 100.0

## The instance transforms of the last rebuild (the MultiMesh holds them too, but a headless renderer does not
## keep them, so tests read these).
var placed: Array[Transform3D] = []


func _ready() -> void:
	rebuild()


func rebuild() -> void:
	var mesh := _find_mesh()
	if mesh == null:
		push_warning("VegetationScatter %s: mesh '%s' not found" % [name, mesh_node])
		return
	var rng := RandomNumberGenerator.new()
	rng.seed = seed_value
	var noise := FastNoiseLite.new()
	noise.seed = seed_value
	noise.frequency = patch_frequency
	var xforms: Array[Transform3D] = []
	var attempts := 0
	var drop := _ground_dropper()
	while xforms.size() < count and attempts < count * max_attempts_factor:
		attempts += 1
		var p := Vector3(
			rng.randf_range(-1.0, 1.0) * half_extents_m.x, 0.0, rng.randf_range(-1.0, 1.0) * half_extents_m.y
		)
		var keep := 1.0 - sea_side_falloff * clampf((p.x / half_extents_m.x + 1.0) * 0.5, 0.0, 1.0)
		var n := noise.get_noise_2d(p.x, p.z)
		keep *= lerpf(
			1.0, smoothstep(patch_threshold - patch_softness, patch_threshold + patch_softness, n), patch_strength
		)
		var roll := rng.randf()
		var yaw := rng.randf() * TAU
		var s := rng.randf_range(scale_min, scale_max)
		if roll > keep or _blocked(p):
			continue
		if not drop.is_empty():
			var hit: Variant = _drop(drop, p)
			if hit == null:
				continue
			p = hit
		var basis := Basis(Vector3.UP, yaw).scaled(Vector3(s, s * rng.randf_range(0.85, 1.15), s))
		xforms.append(Transform3D(basis, p))
	var mm := MultiMesh.new()
	mm.transform_format = MultiMesh.TRANSFORM_3D
	mm.mesh = mesh
	mm.instance_count = xforms.size()
	for i in xforms.size():
		mm.set_instance_transform(i, xforms[i])
	multimesh = mm
	placed = xforms
	material_override = material
	tag(self)


## vegetation_detail groups (M1-ENV-05): a grass scatter thins with the MultiMesh fraction, may lose
## its shadows on Low, and scales its visibility range when it has one.
static func tag(mmi: MultiMeshInstance3D) -> void:
	mmi.add_to_group(GraphicsSettings.vegetation_group(GraphicsSettings.VEG_GROUP_MULTIMESH))
	mmi.add_to_group(GraphicsSettings.vegetation_group(GraphicsSettings.VEG_GROUP_SMALL_SHADOWS))
	if mmi.visibility_range_end > 0.0:
		mmi.add_to_group(GraphicsSettings.vegetation_group(GraphicsSettings.VEG_GROUP_LOD))


## The ground's triangle mesh and the transforms between this node and it ({} without a ground).
func _ground_dropper() -> Dictionary:
	if ground == null or not ground.is_inside_tree() or not is_inside_tree():
		return {}
	var mi := _ground_mesh(ground)
	if mi == null or mi.mesh == null:
		push_warning("VegetationScatter %s: ground %s has no mesh" % [name, ground.name])
		return {}
	var to_mesh := mi.global_transform.affine_inverse() * global_transform
	return {"tm": mi.mesh.generate_triangle_mesh(), "to_mesh": to_mesh, "from_mesh": to_mesh.affine_inverse()}


## p (local, on the plane) dropped onto the ground, or null when the ray misses or the height is out of range.
func _drop(drop: Dictionary, p: Vector3) -> Variant:
	var to_mesh: Transform3D = drop["to_mesh"]
	var from := to_mesh * (p + Vector3.UP * ground_ray_from_m)
	var dir := (to_mesh.basis * Vector3.DOWN).normalized()
	var hit: Dictionary = (drop["tm"] as TriangleMesh).intersect_ray(from, dir)
	if hit.is_empty():
		return null
	var local: Vector3 = (drop["from_mesh"] as Transform3D) * (hit["position"] as Vector3)
	var world_y := (global_transform * local).y
	if world_y < height_min_m or world_y > height_max_m:
		return null
	return local


static func _ground_mesh(node: Node) -> MeshInstance3D:
	if node is MeshInstance3D and not String(node.name).contains("-lod"):
		return node as MeshInstance3D
	for c in node.get_children():
		var found := _ground_mesh(c)
		if found != null:
			return found
	return null


func _blocked(p: Vector3) -> bool:
	for c: Vector3 in keep_clear:
		if Vector2(p.x - c.x, p.z - c.y).length() < c.z:
			return true
	return false


func _find_mesh() -> Mesh:
	if source_scene == null:
		return null
	var root := source_scene.instantiate()
	var found := root.find_child(String(mesh_node), true, false) as MeshInstance3D
	var mesh: Mesh = found.mesh if found else null
	root.free()
	return mesh
