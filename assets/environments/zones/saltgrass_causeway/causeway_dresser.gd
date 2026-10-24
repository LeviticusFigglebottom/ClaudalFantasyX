class_name CausewayDresser
extends HalunaDresser
## Dresses the Saltgrass Causeway (vertical_slice.md B06, M2-ENV-10) from causeway_layout.json, which
## assets_src/environments/kits/haluna/causeway_zone.py generates. Every piece carries its own height (the
## generator and the terrain share one height function), so nothing here queries a terrain; `instances`
## are baked scatter transforms (the saltgrass), built as one MultiMesh each.

const XFORM_FIELDS := 5  ## x, y, z, yaw degrees, scale


func dress() -> void:
	layout = _load_json(layout_path)
	if layout.is_empty():
		push_error("CausewayDresser: cannot read %s" % layout_path)
		return
	for spec: Dictionary in layout.get("pieces", []):
		_place_piece(spec)
	for spec: Dictionary in layout.get("instances", []):
		_place_instances(spec)
	dressed.emit()


## The m2-slice hand-off: the walkable path polyline (x, y, z per point, on the slabs' top).
func path_points() -> PackedVector3Array:
	var out := PackedVector3Array()
	for p: Array in layout.get("path", []):
		out.append(Vector3(float(p[0]), float(p[1]), float(p[2])))
	return out


func anchors() -> Dictionary:
	return layout.get("anchors", {}) as Dictionary


func _place_instances(spec: Dictionary) -> void:
	var packed := _load_scene(String(spec["glb"]))
	if packed == null:
		return
	var src := packed.instantiate()
	var mi_src := src.find_child(String(spec.get("mesh_node", "")), true, false) as MeshInstance3D
	if mi_src == null:
		src.free()
		return
	var rows: Array = spec.get("xforms", [])
	var mm := MultiMesh.new()
	mm.transform_format = MultiMesh.TRANSFORM_3D
	mm.mesh = mi_src.mesh
	mm.instance_count = rows.size()
	for i in rows.size():
		var r: Array = rows[i]
		if r.size() < XFORM_FIELDS:
			continue
		var basis := Basis(Vector3.UP, deg_to_rad(float(r[3]))).scaled(Vector3.ONE * float(r[4]))
		mm.set_instance_transform(i, Transform3D(basis, Vector3(float(r[0]), float(r[1]), float(r[2]))))
	var mmi := MultiMeshInstance3D.new()
	mmi.name = String(spec.get("name", "Instances"))
	mmi.multimesh = mm
	mmi.material_override = load(String(spec["material"])) as Material
	mmi.visibility_range_end = float(spec.get("visibility_end_m", 0.0))
	VegetationScatter.tag(mmi)
	add_child(mmi)
	src.free()
	placed[mmi.name] = rows.size()
