class_name KitCollision
extends RefCounted
## Kit collision for Act I zones dressed on a kit's heights (ADR 0200), shared by the zone roots that need it
## (Ch04Zone and its subclasses, Ch05Zone and its subclasses). A zone calls `merge(self)` before
## GreyboxZone._build_blocks and `build_ramps(self)` after it:
##   layout "collision_path": a JSON file whose "blocks" and "ramps" join the layout's own (generated from the
##     kit by tools/act1/, so the hand-written layout keeps only the story).
##   "stairs": HeroStairs' steep flights (ADR 0193), read from the layout by HeroStairs.build_from_layout.
##   "ramps": [{"id", "from": [x, y, z], "to": [x, y, z], "width", "thick"?, "color"?}] a solid slab whose top
##     runs from `from` to `to` (a stair's flight: the controller has no step-up, so stairs are ramps under
##     45 deg). Built under Greybox/<id> like a block, so hide_block works on it.

const KEY_COLLISION := "collision_path"
const KEY_RAMPS := "ramps"
const KEY_BLOCKS := "blocks"
## HeroStairs' flights (ADR 0193): the collision file's "stairs" rows join the layout's, as its blocks and ramps do.
const KEY_STAIRS := "stairs"
const RAMP_THICK_M := 0.4


## Adds the collision file's blocks and ramps to the zone's layout (before its blocks are built).
static func merge(zone: GreyboxZone) -> void:
	if not zone.layout.has(KEY_COLLISION):
		return
	var extra := GreyboxZone.read_json(str(zone.layout[KEY_COLLISION]))
	for key: String in [KEY_BLOCKS, KEY_RAMPS, KEY_STAIRS]:
		if extra.has(key):
			var rows: Array = (zone.layout.get(key, []) as Array).duplicate()
			rows.append_array(extra[key])
			zone.layout[key] = rows


## Builds the layout's ramps under Greybox (after its blocks).
static func build_ramps(zone: GreyboxZone) -> void:
	var root := zone.get_node(NodePath(String(GreyboxZone.GREYBOX)))
	for r: Dictionary in zone.layout.get(KEY_RAMPS, []):
		root.add_child(ramp(r, str(r.get("color", zone.setting("block_color")))))


## A ramp row as a solid slab (not added to the tree): a StaticBody3D named by its id, with a Mesh and a Shape
## like a block's, its top face running from "from" to "to".
static func ramp(r: Dictionary, color: String) -> StaticBody3D:
	var a := GreyboxZone._vec3(r.get("from", [0, 0, 0]))
	var b := GreyboxZone._vec3(r.get("to", [0, 0, 1]))
	var size := Vector3(float(r.get("width", 2.0)), float(r.get("thick", RAMP_THICK_M)), a.distance_to(b))
	var basis := Basis.looking_at(b - a, Vector3.UP)
	var body := StaticBody3D.new()
	body.name = str(r.get("id", "Ramp"))
	body.transform = Transform3D(basis, (a + b) * 0.5 - basis.y * size.y * 0.5)
	var mesh := BoxMesh.new()
	mesh.size = size
	var mat := StandardMaterial3D.new()
	mat.albedo_color = Color.html(color)
	mesh.material = mat
	var mi := MeshInstance3D.new()
	mi.name = "Mesh"
	mi.mesh = mesh
	body.add_child(mi)
	var shape := BoxShape3D.new()
	shape.size = size
	var cs := CollisionShape3D.new()
	cs.name = "Shape"
	cs.shape = shape
	body.add_child(cs)
	return body
