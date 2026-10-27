class_name ZoneKitDressing
extends HalunaDresser
## Swaps an Act I greybox zone's look for env-art's kit (ADR 0200; docs/kb/tech/chapter_flow.md "Kit
## dressing"). A child of a GreyboxZone root, instanced in the zone's .tscn. The greybox keeps the
## gameplay (collision, spawns, triggers, marks, the story); this node only dresses it:
##   pieces       HalunaDresser's placements (kit_dir, materials_dir, LOD chain, material slots), plus
##                  "block": <id>  the piece shows and hides with Greybox/<id> (it follows the block's
##                    visibility_changed), so `hide_block`, `show_block` and the layout's "states" rows
##                    drive it with the story's block;
##                  "collide": true  a box collider from the piece's LOD0 bounds (decor off the route);
##                    "trimesh": the piece's LOD1 (else LOD0) mesh as a static trimesh, for a kit's walk
##                    surfaces (treads, walls) whose shape is the gameplay. Never for stepped flights: the
##                    controller has no step-up, so stairs are ramps in the zone's collision.
##                  "kit_dir" (+ "materials_dir", default <kit_dir>materials/)  a piece from another kit
##                    (Corrow's trader is the ferry kit's hull); each kit keeps its own material cache.
##   greybox      {"hide_all": bool, "keep": [ids]}: hides the greybox meshes (collision stays), except
##                  the kept ones (story pieces no kit has yet).
##   fire_lights  [{"at": [x, y, z], "energy", "range", "block"?}] shadowless omnis in
##                  "fire_light_color"; a "block" light follows its block, like a piece.
##   environment  a res:// Environment: the zone's WorldEnvironment takes a copy (sky, grade, fog).
##   time_of_day_h  the hymn_time_of_day the sky reads.
## It writes hymn_sun_direction from the zone's sun every frame, so the sky's sun follows the story's
## light rows (Ch06Zone's dusk, ...).

const KEY_BLOCK := "block"
const KEY_COLLIDE := "collide"
const KEY_KIT_DIR := "kit_dir"
const KEY_MATERIALS_DIR := "materials_dir"
const COLLIDE_TRIMESH := "trimesh"
const KEY_GREYBOX := "greybox"
const KEY_FIRE := "fire_lights"
const KEY_ENVIRONMENT := "environment"
const KEY_TIME_OF_DAY := "time_of_day_h"
const GLOBAL_SUN := &"hymn_sun_direction"
const GLOBAL_TIME_OF_DAY := &"hymn_time_of_day"
const BLOCK_MESH := &"Mesh"
const FIRE_LIGHTS := &"FireLights"
const COLLIDER := &"Collider"

var zone: GreyboxZone

var _sun_written := Vector3.ZERO
var _followers: Dictionary = {}  ## block id -> Array of kit nodes
var _kit_caches: Dictionary = {}  ## materials dir -> that kit's material cache


func dress() -> void:
	layout = _load_json(layout_path)
	if layout.is_empty():
		push_error("ZoneKitDressing: cannot read %s" % layout_path)
		return
	zone = get_parent() as GreyboxZone
	_rng.seed = int(layout.get("seed", 1))
	for spec: Dictionary in layout.get("pieces", []):
		var piece := _place_from_kit(spec)
		if piece == null:
			continue
		var collide: Variant = spec.get(KEY_COLLIDE, false)
		if collide is String and collide == COLLIDE_TRIMESH:
			piece.add_child(trimesh_collider(piece))
		elif collide is bool and collide:
			piece.add_child(box_collider(piece))
		_attach(piece, str(spec.get(KEY_BLOCK, "")))
	_place_fire_lights()
	_hide_greybox()
	_apply_environment()
	if layout.has(KEY_TIME_OF_DAY):
		RenderingServer.global_shader_parameter_set(GLOBAL_TIME_OF_DAY, float(layout[KEY_TIME_OF_DAY]))
	dressed.emit()


func _process(_delta: float) -> void:
	if zone == null or zone.sun == null or not zone.sun.is_inside_tree():
		return
	var toward := zone.sun.global_basis.z.normalized()  # a light shines down its -Z
	if not toward.is_equal_approx(_sun_written):
		_sun_written = toward
		ShaderGlobals.set_value(GLOBAL_SUN, toward)


## HalunaDresser's placement, from the piece's own kit when it names one.
func _place_from_kit(spec: Dictionary) -> Node3D:
	if not spec.has(KEY_KIT_DIR):
		return _place_piece(spec)
	var saved := [layout.get(KEY_KIT_DIR, ""), layout.get(KEY_MATERIALS_DIR, ""), _material_cache]
	var kit := str(spec[KEY_KIT_DIR])
	var mats := str(spec.get(KEY_MATERIALS_DIR, kit + "materials/"))
	_kit_caches[saved[1]] = _material_cache
	layout[KEY_KIT_DIR] = kit
	layout[KEY_MATERIALS_DIR] = mats
	_material_cache = _kit_caches.get(mats, {})
	var piece := _place_piece(spec)
	_kit_caches[mats] = _material_cache
	layout[KEY_KIT_DIR] = saved[0]
	layout[KEY_MATERIALS_DIR] = saved[1]
	_material_cache = saved[2]
	return piece


## The zone's Greybox/<id> (a block), or null.
func block(id: String) -> Node3D:
	if zone == null or id == "":
		return null
	return zone.get_node_or_null(NodePath("%s/%s" % [GreyboxZone.GREYBOX, id])) as Node3D


## A static box around the piece's LOD0 meshes, in the piece's frame (not added to the tree).
static func box_collider(piece: Node3D) -> StaticBody3D:
	var box := AABB()
	var first := true
	for child: Node in piece.find_children("*", "MeshInstance3D", true, false):
		var mi := child as MeshInstance3D
		if mi.mesh == null or String(mi.name).ends_with(LOD_SUFFIX):
			continue
		var local := _relative(piece, mi) * mi.get_aabb()
		box = local if first else box.merge(local)
		first = false
	var body := StaticBody3D.new()
	body.name = COLLIDER
	var shape := BoxShape3D.new()
	shape.size = box.size
	var cs := CollisionShape3D.new()
	cs.shape = shape
	cs.position = box.get_center()
	body.add_child(cs)
	return body


## A static trimesh of the piece's LOD1 meshes (LOD0 where a mesh has no LOD1), in the piece's frame.
static func trimesh_collider(piece: Node3D) -> StaticBody3D:
	var body := StaticBody3D.new()
	body.name = COLLIDER
	var meshes := piece.find_children("*", "MeshInstance3D", true, false)
	var lod1: Dictionary = {}
	for child: Node in meshes:
		if String(child.name).ends_with(LOD_SUFFIX):
			lod1[String(child.name).trim_suffix(LOD_SUFFIX)] = true
	for child: Node in meshes:
		var mi := child as MeshInstance3D
		var n := String(mi.name)
		if mi.mesh == null or (not n.ends_with(LOD_SUFFIX) and lod1.has(n)):
			continue
		var cs := CollisionShape3D.new()
		cs.shape = mi.mesh.create_trimesh_shape()
		cs.transform = _relative(piece, mi)
		body.add_child(cs)
	return body


static func _relative(root: Node3D, node: Node3D) -> Transform3D:
	var t := Transform3D.IDENTITY
	var n: Node = node
	while n != null and n != root:
		if n is Node3D:
			t = (n as Node3D).transform * t
		n = n.get_parent()
	return t


## The kit nodes that follow each block id.
func followers(block_id: String) -> Array[Node3D]:
	var out: Array[Node3D] = []
	out.assign(_followers.get(block_id, []))
	return out


func _attach(node: Node3D, block_id: String) -> void:
	if block_id == "":
		return
	var b := block(block_id)
	if b == null:
		push_warning("ZoneKitDressing: no greybox block '%s' for %s" % [block_id, node.name])
		return
	if not _followers.has(block_id):
		_followers[block_id] = []
		b.visibility_changed.connect(_follow.bind(block_id))
	(_followers[block_id] as Array).append(node)
	node.visible = b.visible


func _follow(block_id: String) -> void:
	var shown := block(block_id).visible
	for n: Node3D in followers(block_id):
		n.visible = shown


func _place_fire_lights() -> void:
	var rows: Array = layout.get(KEY_FIRE, [])
	if rows.is_empty():
		return
	var root := Node3D.new()
	root.name = FIRE_LIGHTS
	add_child(root)
	var color := Color.html(str(layout.get("fire_light_color", "#E0702E")))
	for r: Variant in rows:
		var row: Dictionary = r
		var at: Array = row.get("at", [0.0, 0.0, 0.0])
		var light := OmniLight3D.new()
		light.light_color = color
		light.light_energy = float(row.get("energy", 1.0))
		light.omni_range = float(row.get("range", 5.0))
		light.shadow_enabled = false
		light.light_volumetric_fog_energy = 0.0  # the fog-lamp rule (test_fog_lamps)
		light.position = Vector3(float(at[0]), float(at[1]), float(at[2]))
		root.add_child(light)
		_attach(light, str(row.get(KEY_BLOCK, "")))


func _hide_greybox() -> void:
	var cfg: Dictionary = layout.get(KEY_GREYBOX, {})
	if zone == null or not bool(cfg.get("hide_all", false)):
		return
	var keep: Array = cfg.get("keep", [])
	var root := zone.get_node_or_null(NodePath(String(GreyboxZone.GREYBOX)))
	if root == null:
		return
	for b: Node in root.get_children():
		if keep.has(String(b.name)):
			continue
		var mesh := b.get_node_or_null(NodePath(String(BLOCK_MESH))) as MeshInstance3D
		if mesh != null:
			mesh.visible = false


func _apply_environment() -> void:
	var path := str(layout.get(KEY_ENVIRONMENT, ""))
	if zone == null or path == "":
		return
	var env := load(path) as Environment
	var we := zone.get_node_or_null(^"WorldEnvironment") as WorldEnvironment
	if env == null or we == null:
		push_warning("ZoneKitDressing: no environment %s or no WorldEnvironment" % path)
		return
	we.environment = env.duplicate()
