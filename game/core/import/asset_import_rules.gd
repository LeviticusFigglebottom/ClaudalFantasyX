class_name AssetImportRules
extends RefCounted
## Data-driven post-import pass for one asset category (ADR 0005 step 4, task M1-ART-02).
##
## The EditorScenePostImport scripts next to this file (`<kind>_post_import.gd`) only name their
## category and call run(). Everything they do is read from `game/data/import/<kind>.json`, and this
## class has no editor dependency, so tests/unit/test_post_import.gd drives it on in-memory trees too.
## The steps, in order:
##   collision    `<name>-col` proxies (Godot's own suffix import has already given them a trimesh
##                StaticBody3D child): the visible proxy mesh is dropped and the body takes its place
##                and name, with the rules' shape (trimesh or convex), layer and mask. Every other
##                CollisionObject3D in the asset gets the same layer and mask.
##   materials    every MeshInstance3D surface gets a *surface override* material: by node name
##                (`by_node`), else `<slot_dir><glTF material name>.tres` when that file exists. The
##                mesh keeps its glTF material, so runtime dressers that key on its resource_name
##                (HalunaDresser, VegetationPlant, AshaStage) still find the slot and win over the
##                import with their own override.
##   lods         authored `<name>-lodN` chains become visibility ranges (`end_m`, `margin_m`); LODs
##                past the table are hidden. Auto-generated LODs are the .import option
##                `meshes/generate_lods`, which the rules state so tests can check the wiring.
##   placeholder  glTF extras that declare PLACEHOLDER (`hymn_tag: "PLACEHOLDER"` or a `placeholder`
##                note, on a node, mesh or material) tag that node, and the asset root, with
##                meta `hymn_tag = &"PLACEHOLDER"`; the root also lists the notes (SPEC §8.4).
## The root always gets `hymn_import_kind` so a scene can tell which rules dressed it.

const RULES_DIR := "res://game/data/import/"
const RULES_EXT := ".json"
const EXTRAS_META := &"extras"
const TAG_META := &"hymn_tag"
const NOTES_META := &"hymn_placeholder_notes"
const KIND_META := &"hymn_import_kind"
const COLLISION_META := &"hymn_collision"
const PLACEHOLDER := &"PLACEHOLDER"
const EXTRAS_TAG_KEY := "hymn_tag"
const EXTRAS_NOTE_KEYS: Array[String] = ["placeholder", "hymn_note"]
const ASSET_DIR_TOKEN := "{asset_dir}"
const SHAPE_TRIMESH := "trimesh"
const SHAPE_CONVEX := "convex"


## Loads `game/data/import/<kind>.json`; an empty Dictionary (and an error) if it is missing or torn.
static func load_rules(kind: String) -> Dictionary:
	var path := RULES_DIR + kind + RULES_EXT
	if not FileAccess.file_exists(path):
		push_error("AssetImportRules: no rules file %s" % path)
		return {}
	var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(path))
	if not parsed is Dictionary:
		push_error("AssetImportRules: %s is not a JSON object" % path)
		return {}
	return parsed


## The post-import entry point: loads the category's rules and applies them to `scene` in place.
static func run(scene: Node, kind: String, source_file: String) -> Node:
	var rules := load_rules(kind)
	if not rules.is_empty():
		apply(scene, rules, source_file)
	return scene


## Applies `rules` to an imported scene. Returns a report (counts, placeholder notes, warnings).
static func apply(scene: Node, rules: Dictionary, source_file: String = "") -> Dictionary:
	var report := {"collision": 0, "materials": 0, "lods": 0, "placeholder": false, "notes": [], "warnings": []}
	scene.set_meta(KIND_META, StringName(str(rules.get("kind", ""))))
	_apply_collision(scene, rules.get("collision", {}), report)
	var slot_dir := str(rules.get("materials", {}).get("slot_dir", ""))
	slot_dir = slot_dir.replace(ASSET_DIR_TOKEN, source_file.get_base_dir())
	for node: Node in scene.find_children("*", "MeshInstance3D", true, false):
		var mi := node as MeshInstance3D
		_apply_materials(mi, rules.get("materials", {}), slot_dir, report)
		_apply_lod(mi, rules.get("lods", {}), report)
	_apply_placeholder(scene, report)
	for w: String in report["warnings"]:
		push_warning("AssetImportRules %s: %s" % [source_file, w])
	return report


# ---- collision -------------------------------------------------------------------------------


static func _apply_collision(scene: Node, rules: Dictionary, report: Dictionary) -> void:
	if rules.is_empty():
		return
	var suffix := str(rules.get("proxy_suffix", ""))
	if suffix != "":
		for node: Node in scene.find_children("*" + suffix, "MeshInstance3D", true, false):
			_proxy_to_body(scene, node as MeshInstance3D, rules, report)
	for node: Node in scene.find_children("*", "CollisionObject3D", true, false):
		var body := node as CollisionObject3D
		body.collision_layer = int(rules.get("layer", body.collision_layer))
		body.collision_mask = int(rules.get("mask", body.collision_mask))
		body.set_meta(COLLISION_META, true)


## `x-col` arrives as MeshInstance3D(x-col) > StaticBody3D > CollisionShape3D(trimesh). The body
## replaces the mesh node under the same parent, transform and name; the proxy mesh is never drawn.
static func _proxy_to_body(scene: Node, mi: MeshInstance3D, rules: Dictionary, report: Dictionary) -> void:
	var bodies := mi.find_children("*", "StaticBody3D", false, false)
	if bodies.is_empty():
		report["warnings"].append("%s has the collision suffix but no StaticBody3D" % mi.name)
		return
	var body := bodies[0] as StaticBody3D
	var parent := mi.get_parent()
	var proxy_name := mi.name
	var at := mi.get_index()
	var xform := mi.transform * body.transform
	var mesh := mi.mesh
	_own(body, null)
	mi.remove_child(body)
	parent.remove_child(mi)
	mi.free()
	body.name = proxy_name
	body.transform = xform
	parent.add_child(body)
	parent.move_child(body, at)
	if str(rules.get("shape", SHAPE_TRIMESH)) == SHAPE_CONVEX and mesh != null:
		for shape_node: Node in body.find_children("*", "CollisionShape3D", false, false):
			(shape_node as CollisionShape3D).shape = mesh.create_convex_shape()
	_own(body, scene)
	report["collision"] = int(report["collision"]) + 1


static func _own(node: Node, scene: Node) -> void:
	node.owner = scene
	for child: Node in node.get_children():
		_own(child, scene)


# ---- materials -------------------------------------------------------------------------------


static func _apply_materials(mi: MeshInstance3D, rules: Dictionary, slot_dir: String, report: Dictionary) -> void:
	if mi.mesh == null or rules.is_empty():
		return
	var by_node: Dictionary = rules.get("by_node", {})
	var warn := bool(rules.get("warn_unmapped", false))
	for i in mi.mesh.get_surface_count():
		if mi.get_surface_override_material(i) != null:
			continue
		var src := mi.mesh.surface_get_material(i)
		var slot := src.resource_name if src != null else ""
		var path := ""
		if by_node.has(String(mi.name)):
			path = str(by_node[String(mi.name)])
		elif slot != "" and slot_dir != "":
			path = slot_dir + slot + ".tres"
		var mat: Material = load(path) as Material if path != "" and ResourceLoader.exists(path) else null
		if mat == null:
			if warn:
				report["warnings"].append("%s surface %d ('%s'): no material at '%s'" % [mi.name, i, slot, path])
			continue
		mi.set_surface_override_material(i, mat)
		report["materials"] = int(report["materials"]) + 1


# ---- LODs ------------------------------------------------------------------------------------


## The LOD index of a node named `<name><suffix>N` (0 without the suffix), as VegetationPlant reads it.
static func lod_index(node_name: String, suffix: String) -> int:
	var at := node_name.rfind(suffix)
	if suffix == "" or at < 0:
		return 0
	var digits := node_name.substr(at + suffix.length())
	return int(digits) if digits.is_valid_int() else 0


static func _apply_lod(mi: MeshInstance3D, rules: Dictionary, report: Dictionary) -> void:
	var ends: Array = rules.get("end_m", [])
	if ends.is_empty():
		return
	var lod := lod_index(String(mi.name), str(rules.get("suffix", "")))
	var margin := float(rules.get("margin_m", 0.0))
	if lod >= ends.size():
		mi.visible = false
		return
	mi.visibility_range_begin = 0.0 if lod == 0 else float(ends[lod - 1])
	mi.visibility_range_end = float(ends[lod])
	mi.visibility_range_begin_margin = margin if lod > 0 else 0.0
	mi.visibility_range_end_margin = margin
	mi.visibility_range_fade_mode = GeometryInstance3D.VISIBILITY_RANGE_FADE_DISABLED
	report["lods"] = int(report["lods"]) + 1


# ---- PLACEHOLDER -----------------------------------------------------------------------------


## The PLACEHOLDER note an object's glTF extras declare, or "" when they declare none.
static func placeholder_note(obj: Object) -> String:
	if obj == null or not obj.has_meta(EXTRAS_META):
		return ""
	var extras: Variant = obj.get_meta(EXTRAS_META)
	if not extras is Dictionary:
		return ""
	var ex: Dictionary = extras
	for key: String in EXTRAS_NOTE_KEYS:
		if ex.has(key) and str(ex[key]) != "":
			return str(ex[key])
	return str(PLACEHOLDER) if str(ex.get(EXTRAS_TAG_KEY, "")) == str(PLACEHOLDER) else ""


static func _apply_placeholder(scene: Node, report: Dictionary) -> void:
	var notes := PackedStringArray()
	var tagged := false
	var nodes: Array[Node] = [scene]
	nodes.append_array(scene.find_children("*", "", true, false))
	for node in nodes:
		var note := _node_note(node)
		if note == "":
			continue
		tagged = true
		node.set_meta(TAG_META, PLACEHOLDER)
		if note != str(PLACEHOLDER) and not notes.has(note):
			notes.append(note)
	if not tagged:
		return
	scene.set_meta(TAG_META, PLACEHOLDER)
	scene.set_meta(NOTES_META, notes)
	report["placeholder"] = true
	report["notes"] = Array(notes)


## A node's own extras, else its mesh's or any surface material's.
static func _node_note(node: Node) -> String:
	var note := placeholder_note(node)
	if note != "" or not node is MeshInstance3D:
		return note
	var mesh := (node as MeshInstance3D).mesh
	note = placeholder_note(mesh)
	if note != "" or mesh == null:
		return note
	for i in mesh.get_surface_count():
		note = placeholder_note(mesh.surface_get_material(i))
		if note != "":
			return note
	return ""
