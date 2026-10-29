class_name ZoneKitDressing
extends HalunaDresser
## Swaps an Act I greybox zone's look for env-art's kit (ADR 0200; docs/kb/tech/chapter_flow.md "Kit
## dressing"). A child of a GreyboxZone root, instanced in the zone's .tscn. The greybox keeps the
## gameplay (collision, spawns, triggers, marks, the story); this node only dresses it:
##   pieces       HalunaDresser's placements (kit_dir, materials_dir, LOD chain, material slots), plus
##                  "block": <id>  the piece shows and hides with Greybox/<id> (it follows the block's
##                    visibility_changed), so `hide_block`, `show_block` and the layout's "states" rows
##                    drive it with the story's block;
##                  "spin_with": <id>  the piece turns about its own Z as Greybox/<id> turns about Y (a flue-key's
##                    wheel with the trial's Key block);
##                  "turn_with": <id>  the piece turns about Y as Greybox/<id> does (Ashcrown's vein-gates, which
##                    the trial view turns in 90° steps);
##                  "collide": true  a box collider from the piece's LOD0 bounds (decor off the route);
##                    "trimesh": the piece's LOD1 (else LOD0) mesh as a static trimesh, for a kit's walk
##                    surfaces (treads, walls) whose shape is the gameplay. Never for stepped flights: the
##                    controller has no step-up, so stairs are ramps in the zone's collision.
##                    "trimesh_lod0": the same from LOD0 (a terrain whose LOD1 is too coarse to walk on).
##                  "collide_lod0_in": [{"pos", "size", "yaw"?}]  boxes in the layout's frame where a "trimesh"
##                    collides from LOD0 (a doorway a closed LOD1 shell would seal).
##                  "scale_y": the piece's vertical scale, over HalunaDresser's uniform "scale" (env-art's Iskarra
##                    towers are squat or tall copies of one tower);
##                  "kit_dir" (+ "materials_dir", default <kit_dir>materials/)  a piece from another kit
##                    (Corrow's trader is the ferry kit's hull); each kit keeps its own material cache.
##                  "material_paths": {slot: "res://...tres"}  one slot's material swapped for a zone's own, the
##                    piece's other slots kept from its kit (Coilspire's inner laterite without its green joints).
##   kit_material_paths  {slot: "res://...tres"}: the same swap on every piece from the zone's own kit (no "kit_dir"),
##                  under each row's own "material_paths" (Corrow's weathered lacquer, copper and iron, M3-ENV-1326).
##   greybox      {"hide_all": bool, "keep": [ids]}: hides the greybox meshes (collision stays), except
##                  the kept ones (story pieces no kit has yet).
##   fire_lights  [{"at": [x, y, z], "energy", "range", "block"?, "shadow"?, "attenuation"?, "color"?}] omnis
##                  in "fire_light_color" or their own "color" (shadowless unless "shadow"); a "block" light
##                  follows its block.
##   multimeshes  [{"name", "piece", "transforms": [[x, y, z, yaw_rad]], "block"?}]: many copies of one kit
##                  piece's LOD0 (with its slot materials) as one shadowless MultiMesh (Pemakar's leaf-boats).
##   far_lights   [{"name", "points": [[x, y, z]], "size_m": [near, far], "color", "energy", "block"?}]: lights
##                  too small to model at their range, as camera-facing quads (env_far_lights), larger with
##                  distance from the origin out to FAR_SIZE_RANGE_M.
##   waters       [{"name", "pos": [x, y, z], "size": [x, z], "material", "wave_set"?, "sea_glow"?, "block"?}]: still
##                  water a story shows (a flood, a drowned lane) as a WaterSurface over a plane of that size, centred
##                  at pos (the node stays unrotated at y, the plane offset to x, z); it never publishes the water
##                  level (the zone's sea does), and a "block" water follows its block.
##   storms       [{"name", "at": [x, y, z], "preset", "azimuth_deg", "block"?}]: Rendering's Undertow
##                  (UndertowStorm, game/data/vfx/undertow.json "presets") marking the point it approaches from
##                  `azimuth_deg`, on the zone's Water, sun and WorldEnvironment; a "block" storm follows its block
##                  and stops processing while hidden (no rain, shadow or flash before the story brings it).
##   drops        [{"name", "at": [x, y, z], "profile", "block"?}]: Rendering's held water (WaterSphereRig, a
##                  game/data/vfx/water_sphere.json "profiles" row) centred at `at` (the Tamsule Bell's drop,
##                  M3-RND-26); a "block" drop follows its block.
##   smokes       [{"name", "at": [x, y, z], "yaw_deg", "scale"?, "profile"?, "seed"?, "block"?}]: Rendering's
##                  volumetric columns (SmokeColumn, game/data/vfx/smoke_column.json "columns", M3-RND-21), framed
##                  as the kit's smoke_plume pieces (yawed so +X is downwind, uniform scale); a "block" one follows
##                  its block.
##   ebbing       {}: Ch9's Ebbing motes (EbbingMotes, game/data/vfx/ebbing.json, M3-C09-03): the held fields
##                  the chapter's `@vfx glimmer_held` cues play, on the zone's stage.
##   environment  a res:// Environment: the zone's WorldEnvironment takes a copy (sky, grade, fog).
##   time_of_day_h  the hymn_time_of_day the sky reads.
## It writes hymn_sun_direction from the zone's sun every frame, so the sky's sun follows the story's
## light rows (Ch06Zone's dusk, ...).

const KEY_BLOCK := "block"
const KEY_COLLIDE := "collide"
const KEY_COLLIDE_LOD0_IN := "collide_lod0_in"
const KEY_SPIN := "spin_with"
const KEY_TURN := "turn_with"
const GLOW := &"Glow"
## glow(): the light a lit story piece casts (a charged bowl), shadowless and never in the fog (test_fog_lamps).
const GLOW_ENERGY := 2.2
const GLOW_RANGE_M := 5.0
const GLOW_HEIGHT_M := 1.2
const KEY_KIT_DIR := "kit_dir"
const KEY_SCALE_Y := "scale_y"
const KEY_MATERIALS_DIR := "materials_dir"
const COLLIDE_TRIMESH := "trimesh"
const COLLIDE_TRIMESH_LOD0 := "trimesh_lod0"
const KEY_MULTIMESHES := "multimeshes"
const KEY_FAR_LIGHTS := "far_lights"
const KEY_WATERS := "waters"
const KEY_STORMS := "storms"
const KEY_DROPS := "drops"
const KEY_SMOKES := "smokes"
const KEY_EBBING := "ebbing"
const KEY_MATERIAL_PATHS := "material_paths"
const KEY_KIT_MATERIAL_PATHS := "kit_material_paths"
const DEFAULT_WAVES := "res://game/world/water/lagoon_waves.tres"
## The waters' plane cells (m): fine enough for the wave field's short waves to read on a still lake.
const WATER_CELL_M := 2.0
const FAR_LIGHT_SHADER := "res://game/shaders/environment/env_far_lights.gdshader"
const FAR_SIZE_RANGE_M := 700.0
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
var _spinners: Array[Array] = []  ## [piece, block, the piece's own basis]
var _turners: Array[Array] = []  ## [piece, block, the piece's own basis]


func dress() -> void:
	layout = _load_json(layout_path)
	if layout.is_empty():
		push_error("ZoneKitDressing: cannot read %s" % layout_path)
		return
	zone = get_parent() as GreyboxZone
	_rng.seed = int(layout.get("seed", 1))
	var kit_paths: Dictionary = layout.get(KEY_KIT_MATERIAL_PATHS, {})
	for spec: Dictionary in layout.get("pieces", []):
		var piece := _place_from_kit(spec)
		if piece == null:
			continue
		if not kit_paths.is_empty() and not spec.has(KEY_KIT_DIR):
			swap_slots(piece, kit_paths)
		if spec.has(KEY_MATERIAL_PATHS):
			swap_slots(piece, spec[KEY_MATERIAL_PATHS])
		if spec.has(KEY_SCALE_Y):
			var s := float(spec.get("scale", 1.0))
			piece.basis = piece.basis.scaled(Vector3(1.0, float(spec[KEY_SCALE_Y]) / s, 1.0))
		var collide: Variant = spec.get(KEY_COLLIDE, false)
		if collide is String and collide == COLLIDE_TRIMESH:
			piece.add_child(trimesh_collider(piece, true, lod0_boxes(spec.get(KEY_COLLIDE_LOD0_IN, []))))
		elif collide is String and collide == COLLIDE_TRIMESH_LOD0:
			piece.add_child(trimesh_collider(piece, false))
		elif collide is bool and collide:
			piece.add_child(box_collider(piece))
		_attach(piece, str(spec.get(KEY_BLOCK, "")))
		var spin := block(str(spec.get(KEY_SPIN, "")))
		if spin != null:
			_spinners.append([piece, spin, piece.basis])
		var turn := block(str(spec.get(KEY_TURN, "")))
		if turn != null:
			_turners.append([piece, turn, piece.basis])
	_place_fire_lights()
	_place_multimeshes()
	_place_far_lights()
	_place_waters()
	_place_storms()
	_place_drops()
	_place_smokes()
	_place_ebbing()
	_hide_greybox()
	_apply_environment()
	if layout.has(KEY_TIME_OF_DAY):
		RenderingServer.global_shader_parameter_set(GLOBAL_TIME_OF_DAY, float(layout[KEY_TIME_OF_DAY]))
	dressed.emit()


func _process(_delta: float) -> void:
	for sp: Array in _spinners:
		var turn := deg_to_rad((sp[1] as Node3D).rotation_degrees.y)
		(sp[0] as Node3D).basis = (sp[2] as Basis) * Basis(Vector3.BACK, turn)
	for tp: Array in _turners:
		(tp[0] as Node3D).basis = Basis(Vector3.UP, (tp[1] as Node3D).rotation.y) * (tp[2] as Basis)
	if zone == null or zone.sun == null or not zone.sun.is_inside_tree():
		return
	var toward := zone.sun.global_basis.z.normalized()  # a light shines down its -Z
	if not toward.is_equal_approx(_sun_written):
		_sun_written = toward
		ShaderGlobals.set_value(GLOBAL_SUN, toward)


## Every surface of `root`'s meshes whose kit slot (its source material's name) is a key of `paths` takes that
## path's material instead.
static func swap_slots(root: Node, paths: Dictionary) -> void:
	for n: Node in root.find_children("*", "MeshInstance3D", true, false):
		var mi := n as MeshInstance3D
		if mi.mesh == null:
			continue
		for i in mi.mesh.get_surface_count():
			var src := mi.mesh.surface_get_material(i)
			if src != null and paths.has(String(src.resource_name)):
				mi.set_surface_override_material(i, load(String(paths[String(src.resource_name)])) as Material)


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


## A "collide_lod0_in" list as [box's transform, half size] pairs.
static func lod0_boxes(rows: Array) -> Array[Array]:
	var out: Array[Array] = []
	for row: Dictionary in rows:
		var basis := Basis(Vector3.UP, deg_to_rad(float(row.get("yaw", 0.0))))
		out.append([Transform3D(basis, GreyboxZone._vec3(row["pos"])), GreyboxZone._vec3(row["size"]) * 0.5])
	return out


## A static trimesh of the piece's LOD1 meshes (LOD0 where a mesh has no LOD1; only LOD0 when not
## `prefer_lod1`), in the piece's frame. Inside the `lod0_in` boxes (lod0_boxes, in the frame of the piece's parent)
## it collides from LOD0 instead: the LOD1 triangles are clipped to outside the boxes, LOD0's to inside (a doorway a
## closed LOD1 shell would seal).
static func trimesh_collider(piece: Node3D, prefer_lod1: bool = true, lod0_in: Array[Array] = []) -> StaticBody3D:
	var body := StaticBody3D.new()
	body.name = COLLIDER
	var meshes := piece.find_children("*", "MeshInstance3D", true, false)
	var lod1: Dictionary = {}
	for child: Node in meshes:
		if String(child.name).ends_with(LOD_SUFFIX):
			lod1[String(child.name).trim_suffix(LOD_SUFFIX)] = true
	var patching := prefer_lod1 and not lod0_in.is_empty()
	for child: Node in meshes:
		var mi := child as MeshInstance3D
		var n := String(mi.name)
		var skip := n.ends_with(LOD_SUFFIX) if not prefer_lod1 else (not n.ends_with(LOD_SUFFIX) and lod1.has(n))
		if mi.mesh == null or (skip and not patching):
			continue
		var cs := CollisionShape3D.new()
		cs.transform = _relative(piece, mi)
		if not patching:
			cs.shape = mi.mesh.create_trimesh_shape()
		else:
			var shape := ConcavePolygonShape3D.new()
			shape.set_faces(_clip_faces(mi.mesh.get_faces(), piece.transform * cs.transform, lod0_in, skip))
			cs.shape = shape
		body.add_child(cs)
	return body


## The parts of `faces` (in a mesh's frame, `to_parent` taking it to the boxes' frame) outside every box, or inside
## one when `inside`, as triangles in the mesh's frame.
static func _clip_faces(
	faces: PackedVector3Array, to_parent: Transform3D, boxes: Array[Array], inside: bool
) -> PackedVector3Array:
	var out := PackedVector3Array()
	var back := to_parent.affine_inverse()
	for i in range(0, faces.size(), 3):
		var outside: Array[PackedVector3Array] = [
			PackedVector3Array([to_parent * faces[i], to_parent * faces[i + 1], to_parent * faces[i + 2]])
		]
		var kept: Array[PackedVector3Array] = []
		for box: Array in boxes:
			var frame: Transform3D = box[0]
			var to_box := frame.affine_inverse()
			var rest: Array[PackedVector3Array] = []
			for poly in outside:
				var local := to_box * poly
				if _clear_of_box(local, box[1]):  # wholly past one face: nothing to cut (most of a mesh; ADR 0111)
					rest.append(poly)
					continue
				var pieces := _cut_by_box(local, box[1])
				for k in pieces.size():
					var world := frame * pieces[k]
					if k == 0:
						if inside and world.size() >= 3:
							kept.append(world)
					elif world.size() >= 3:
						rest.append(world)
			outside = rest
		if not inside:
			kept = outside
		for poly in kept:
			for k in range(1, poly.size() - 1):
				out.append_array([back * poly[0], back * poly[k], back * poly[k + 1]])
	return out


## True when every point of `poly` (in a box's frame) lies past the same face of the box of half size `h`, so the
## polygon cannot touch it. The clip then keeps it whole, as _cut_by_box would, without the per-plane work.
static func _clear_of_box(poly: PackedVector3Array, h: Vector3) -> bool:
	for axis in 3:
		var above := true
		var below := true
		for p in poly:
			above = above and p[axis] > h[axis]
			below = below and p[axis] < -h[axis]
		if above or below:
			return true
	return false


## A convex polygon (in a box's frame) cut by the box of half size `h`: [the part inside, the parts outside...].
static func _cut_by_box(poly: PackedVector3Array, h: Vector3) -> Array[PackedVector3Array]:
	var pieces: Array[PackedVector3Array] = [PackedVector3Array()]
	var rest := poly
	for axis in 3:
		for side: float in [-1.0, 1.0]:
			pieces.append(_clip(rest, axis, side * h[axis], side, false))
			rest = _clip(rest, axis, side * h[axis], side, true)
	pieces[0] = rest
	return pieces


## Sutherland-Hodgman: the part of `poly` with side * (p[axis] - limit) <= 0 (inward of the plane), or > 0 when not
## `inward`.
static func _clip(poly: PackedVector3Array, axis: int, limit: float, side: float, inward: bool) -> PackedVector3Array:
	var out := PackedVector3Array()
	var n := poly.size()
	for i in n:
		var a := poly[i]
		var b := poly[(i + 1) % n]
		var da := side * (a[axis] - limit)
		var db := side * (b[axis] - limit)
		var a_in := da <= 0.0 if inward else da > 0.0
		var b_in := db <= 0.0 if inward else db > 0.0
		if a_in:
			out.append(a)
		if a_in != b_in:
			out.append(a.lerp(b, da / (da - db)))
	return out


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


## Lights or darkens the kit pieces that follow `block_id` (a story piece holding a charge): an OmniLight in `color`
## over each, and the colour as an emission overlay on its meshes. Returns how many pieces it touched.
func glow(block_id: String, on: bool, color: Color) -> int:
	var n := 0
	for piece: Node3D in followers(block_id):
		var light := piece.get_node_or_null(NodePath(String(GLOW))) as OmniLight3D
		if light == null and on:
			light = OmniLight3D.new()
			light.name = GLOW
			light.position = Vector3(0.0, GLOW_HEIGHT_M, 0.0)
			light.omni_range = GLOW_RANGE_M
			light.light_volumetric_fog_energy = 0.0  # the fog-lamp rule
			piece.add_child(light)
		if light != null:
			light.light_color = color
			light.light_energy = GLOW_ENERGY
			light.visible = on
		var overlay: StandardMaterial3D = null
		if on:
			overlay = StandardMaterial3D.new()
			overlay.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
			overlay.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
			overlay.blend_mode = BaseMaterial3D.BLEND_MODE_ADD
			overlay.albedo_color = Color(color, 0.35)
		for mi: Node in piece.find_children("*", "MeshInstance3D", true, false):
			(mi as MeshInstance3D).material_overlay = overlay
		n += 1
	return n


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
		_pause_hidden(n)


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
		light.light_color = Color.html(str(row["color"])) if row.has("color") else color
		light.light_energy = float(row.get("energy", 1.0))
		light.omni_range = float(row.get("range", 5.0))
		light.shadow_enabled = bool(row.get("shadow", false))
		light.omni_attenuation = float(row.get("attenuation", light.omni_attenuation))
		light.light_volumetric_fog_energy = 0.0  # the fog-lamp rule (test_fog_lamps)
		light.position = Vector3(float(at[0]), float(at[1]), float(at[2]))
		root.add_child(light)
		_attach(light, str(row.get(KEY_BLOCK, "")))


func _place_multimeshes() -> void:
	for r: Variant in layout.get(KEY_MULTIMESHES, []):
		var row: Dictionary = r
		var transforms: Array = row.get("transforms", [])
		var mesh := kit_mesh(str(row.get("piece", "")))
		if mesh == null or transforms.is_empty():
			push_warning("ZoneKitDressing: no multimesh for %s" % row.get("piece", ""))
			continue
		var mm := MultiMesh.new()
		mm.transform_format = MultiMesh.TRANSFORM_3D
		mm.mesh = mesh
		mm.instance_count = transforms.size()
		for i in transforms.size():
			var t: Array = transforms[i]
			var at := Vector3(float(t[0]), float(t[1]), float(t[2]))
			mm.set_instance_transform(i, Transform3D(Basis(Vector3.UP, float(t[3])), at))
		var mmi := MultiMeshInstance3D.new()
		mmi.name = str(row.get("name", "MultiMesh"))
		mmi.multimesh = mm
		mmi.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
		add_child(mmi)
		_attach(mmi, str(row.get(KEY_BLOCK, "")))
		placed[mmi.name] = transforms.size()


## A copy of a kit piece's LOD0 mesh with its slot materials on its surfaces (for a MultiMesh), or null.
func kit_mesh(piece: String) -> Mesh:
	var node := instance_piece(piece)
	if node == null:
		return null
	placed[piece] = int(placed[piece]) - 1  # a template, not a placement
	var mesh: Mesh = null
	for child: Node in node.find_children("*", "MeshInstance3D", true, false):
		var mi := child as MeshInstance3D
		if mi.mesh == null or String(mi.name).ends_with(LOD_SUFFIX):
			continue
		mesh = mi.mesh.duplicate() as Mesh
		for i in mesh.get_surface_count():
			var mat := mi.get_surface_override_material(i)
			if mat != null:
				mesh.surface_set_material(i, mat)
		break
	node.free()
	return mesh


func _place_far_lights() -> void:
	for r: Variant in layout.get(KEY_FAR_LIGHTS, []):
		var row: Dictionary = r
		var points: Array = row.get("points", [])
		if points.is_empty():
			continue
		var sizes: Array = row.get("size_m", [1.0, 1.0])
		var quad := QuadMesh.new()
		quad.size = Vector2(2.0, 2.0)  # half-size 1, so an instance's scale is its radius
		var mat := ShaderMaterial.new()
		mat.shader = load(FAR_LIGHT_SHADER) as Shader
		mat.set_shader_parameter(&"col_light", Color.html(str(row.get("color", "#FFFFFF"))))
		mat.set_shader_parameter(&"energy", float(row.get("energy", 1.0)))
		quad.material = mat
		var mm := MultiMesh.new()
		mm.transform_format = MultiMesh.TRANSFORM_3D
		mm.mesh = quad
		mm.instance_count = points.size()
		for i in points.size():
			var p: Array = points[i]
			var pos := Vector3(float(p[0]), float(p[1]), float(p[2]))
			var s := lerpf(
				float(sizes[0]), float(sizes[1]), clampf(Vector2(pos.x, pos.z).length() / FAR_SIZE_RANGE_M, 0, 1)
			)
			mm.set_instance_transform(i, Transform3D(Basis().scaled(Vector3.ONE * s), pos))
		var mmi := MultiMeshInstance3D.new()
		mmi.name = str(row.get("name", "FarLights"))
		mmi.multimesh = mm
		mmi.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
		add_child(mmi)
		_attach(mmi, str(row.get(KEY_BLOCK, "")))


func _place_waters() -> void:
	for r: Variant in layout.get(KEY_WATERS, []):
		var row: Dictionary = r
		var at := GreyboxZone._vec3(row.get("pos", [0.0, 0.0, 0.0]))
		var size: Array = row.get("size", [10.0, 10.0])
		var plane := PlaneMesh.new()
		plane.size = Vector2(float(size[0]), float(size[1]))
		plane.subdivide_width = maxi(0, int(plane.size.x / WATER_CELL_M) - 1)
		plane.subdivide_depth = maxi(0, int(plane.size.y / WATER_CELL_M) - 1)
		plane.center_offset = Vector3(at.x, 0.0, at.z)
		var water := WaterSurface.new()
		water.name = str(row.get("name", "Water"))
		water.position = Vector3(0.0, at.y, 0.0)
		water.wave_set = load(str(row.get("wave_set", DEFAULT_WAVES))) as WaveSet
		water.material = load(str(row["material"])) as ShaderMaterial
		water.sea_glow_energy = float(row.get("sea_glow", 0.0))
		water.tide_line_y = at.y
		water.surface_mesh = plane
		add_child(water)
		_attach(water, str(row.get(KEY_BLOCK, "")))


func _place_storms() -> void:
	for r: Variant in layout.get(KEY_STORMS, []):
		var row: Dictionary = r
		var storm := UndertowStorm.new()
		storm.name = str(row.get("name", "Storm"))
		storm.position = GreyboxZone._vec3(row.get("at", [0.0, 0.0, 0.0]))
		storm.approach_azimuth_deg = float(row.get("azimuth_deg", 0.0))
		if zone != null:
			storm.water = zone.get_node_or_null(^"Water") as WaterSurface
			storm.sun = zone.sun
			storm.world_environment = zone.get_node_or_null(^"WorldEnvironment") as WorldEnvironment
		storm.preset = str(row.get("preset", ""))
		add_child(storm)
		_attach(storm, str(row.get(KEY_BLOCK, "")))
		_pause_hidden(storm)
		var far := StormFarPlane.new()
		far.name = "FarPlane"
		storm.add_child(far)  # the current camera reaches past the storm while it shows (M3-ENV-1308)


func _place_drops() -> void:
	for r: Variant in layout.get(KEY_DROPS, []):
		var row: Dictionary = r
		var drop := WaterSphereRig.new()
		drop.name = str(row.get("name", "Drop"))
		drop.position = GreyboxZone._vec3(row.get("at", [0.0, 0.0, 0.0]))
		drop.profile = str(row.get("profile", ""))
		add_child(drop)
		_attach(drop, str(row.get(KEY_BLOCK, "")))


func _place_smokes() -> void:
	for r: Variant in layout.get(KEY_SMOKES, []):
		var row: Dictionary = r
		var smoke := SmokeColumn.new()
		smoke.name = str(row.get("name", "Smoke"))
		smoke.profile = str(row.get("profile", "camp"))
		smoke.seed = float(row.get("seed", 0.0))
		var basis := Basis(Vector3.UP, deg_to_rad(float(row.get("yaw_deg", 0.0))))
		smoke.transform = Transform3D(
			basis.scaled(Vector3.ONE * float(row.get("scale", 1.0))), GreyboxZone._vec3(row.get("at", [0.0, 0.0, 0.0]))
		)
		add_child(smoke)
		_attach(smoke, str(row.get(KEY_BLOCK, "")))


func _place_ebbing() -> void:
	if not layout.has(KEY_EBBING):
		return
	var ebb := EbbingMotes.new()
	ebb.name = "Ebbing"
	ebb.zone = zone
	add_child(ebb)


## A hidden storm stops processing (its rain, zone shadow and flashes act on the zone's light).
static func _pause_hidden(node: Node3D) -> void:
	if node is UndertowStorm:
		node.process_mode = Node.PROCESS_MODE_INHERIT if node.visible else Node.PROCESS_MODE_DISABLED


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
