class_name PrewarmEntryMesh
extends RefCounted
## The mesh a ShaderPrewarm registry entry draws with (prewarm_materials.json "mesh" and "mesh_node"; moved out
## of shader_prewarm.gd at the big8 merge to keep that file under the lint's line limit).


## The mesh an entry draws: its "mesh" key (a Mesh, or the first/named MeshInstance3D of a scene),
## else the stage quad.
static func of(entry: Dictionary, fallback: Mesh) -> Mesh:
	var path := str(entry.get("mesh", ""))
	if path.is_empty() or not ResourceLoader.exists(path):
		if not path.is_empty():
			push_warning("%s: prewarm mesh not found: %s" % [ShaderPrewarm.LOG_PREFIX, path])
		return fallback
	var res := load(path)
	if res is Mesh:
		return res as Mesh
	if res is PackedScene:
		var inst := (res as PackedScene).instantiate()
		var want := str(entry.get("mesh_node", ""))
		var mi: MeshInstance3D = null
		if want != "":
			mi = inst.find_child(want, true, false) as MeshInstance3D
		else:
			var found := inst.find_children("*", "MeshInstance3D", true, false)
			mi = (
				(inst as MeshInstance3D)
				if inst is MeshInstance3D
				else (found[0] as MeshInstance3D if found.size() > 0 else null)
			)
		var mesh := mi.mesh if mi != null else null
		inst.free()
		if mesh != null:
			return mesh
	push_warning("%s: %s has no mesh to prewarm with" % [ShaderPrewarm.LOG_PREFIX, path])
	return fallback
