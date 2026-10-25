extends SceneTree
## Prints each creature mesh surface's triangles and its import-time LOD chain (docs/kb/art/creatures/pipeline.md §4).
## godot --headless --path . -s tools/dev/creature_lods.gd [-- id ...]   (no ids: every creature folder)

func _init() -> void:
	var ids := Array(OS.get_cmdline_user_args())
	if ids.is_empty():
		ids = Array(DirAccess.get_directories_at("res://assets/creatures"))
	for id: String in ids:
		if not ResourceLoader.exists("res://assets/creatures/%s/%s.glb" % [id, id]):
			continue
		var scene := load("res://assets/creatures/%s/%s.glb" % [id, id]) as PackedScene
		var root := scene.instantiate()
		for mi: MeshInstance3D in root.find_children("*", "MeshInstance3D", true, false):
			var info: Array[String] = []
			for s in mi.mesh.get_surface_count():
				var d: Dictionary = RenderingServer.mesh_get_surface(mi.mesh.get_rid(), s)
				var tri := int(d.get("index_count", 0)) / 3
				var lods: Array = d.get("lods", [])
				var counts: Array[int] = []
				for l: Dictionary in lods:
					counts.append(int((l["index_data"] as PackedByteArray).size() / (2 if tri * 3 <= 65535 else 4) / 3))
				info.append("%d tris, lods %s" % [tri, str(counts)])
			print(id, "/", mi.name, ": ", "; ".join(info))
		root.free()
	quit()
