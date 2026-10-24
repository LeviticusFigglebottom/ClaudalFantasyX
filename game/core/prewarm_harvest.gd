class_name PrewarmHarvest
extends RefCounted
## ShaderPrewarm's harvest helpers (split out of shader_prewarm.gd, M2-RND-18): the draws a scene's stored
## properties or a live node list, and a scene instanced on a worker thread for the first run's live harvest.


## [material, mesh, source multimesh or null] pairs of one node's stored properties: a MeshInstance3D's
## or MultiMeshInstance3D's override, per-surface overrides, else the mesh's own surface materials.
static func state_draws(props: Dictionary) -> Array:
	var mm := props.get(&"multimesh") as MultiMesh
	var mesh := props.get(&"mesh") as Mesh
	if mm != null:
		mesh = mm.mesh
	if mesh == null:
		return []
	var out := []
	var override := props.get(&"material_override") as Material
	if override != null:
		out.append([override, mesh, mm])
		return out
	# A PrimitiveMesh builds its arrays on the first surface query, and that builds its StandardMaterial3D's
	# shader: about 75 ms each, synchronously in start() (Haluna's save shrine, M1-RND-27). It has one
	# surface, whose material is its `material`: read that, and the compile happens in the draw's batch.
	var primitive := mesh as PrimitiveMesh
	for i in 1 if primitive != null else mesh.get_surface_count():
		var m := props.get(StringName("surface_material_override/%d" % i)) as Material
		if m == null:
			m = primitive.material if primitive != null else mesh.surface_get_material(i)
		if m != null:
			out.append([m, mesh, mm])
	return out


## [material, mesh, source multimesh or null] for a live node: its override, per-surface overrides, else the
## mesh's own surface materials (as state_draws, from the node itself rather than its stored properties).
static func live_draws(g: GeometryInstance3D) -> Array:
	var mm: MultiMesh = (g as MultiMeshInstance3D).multimesh if g is MultiMeshInstance3D else null
	var mesh: Mesh = mm.mesh if mm != null else ((g as MeshInstance3D).mesh if g is MeshInstance3D else null)
	if mesh == null:
		return []
	if g.material_override != null:
		return [[g.material_override, mesh, mm]]
	var out := []
	for i in mesh.get_surface_count():
		var m: Material = (g as MeshInstance3D).get_surface_override_material(i) if g is MeshInstance3D else null
		if m == null:
			m = mesh.surface_get_material(i)
		if m != null:
			out.append([m, mesh, mm])
	return out


## Instances `packed` into box[0] on a worker thread (a zone prebuilds itself off the tree, as under SceneRouter).
## It's already loaded: a worker that loads could stall a quit (M2-RND-910).
static func instance_live(packed: PackedScene, box: Array) -> void:
	box[0] = packed.instantiate()
