extends TestCase
## M3-ENV-01: the Tamsule Bell kit after the real import (game/data/import/tamsule_bell_kit.json): the
## kit materials load on their shaders, every glTF slot is overridden by the kit's .tres of the same
## name, the authored LOD1 chains draw exactly one LOD at every distance, the drop placeholder is tagged,
## and the preview scene keeps the water-drop contract (docs/kb/art/environments/tamsule_bell.md §1).

const LodRangeModel := preload("res://tests/unit/lod_range_model.gd")
const KIT_DIR := "res://assets/environments/kits/tamsule_bell/"
const MATERIAL_DIR := KIT_DIR + "materials/"
const PREVIEW := "res://game/levels/_tests/tamsule_bell_kit/tamsule_bell_kit.tscn"
const KIND := &"tamsule_bell_kit"
## The contract (bell.py DROP_*): the anchor at the drop's centre, the weep point, the surface.
const DROP_CENTER := Vector3(0.0, 31.5, 0.0)
const DROP_BOTTOM_Y := 20.0
const DROP_TOP_Y := 43.0
const PIECES: Array[String] = ["tamsule_bell", "gantry_leg", "gallery_segment_a", "catch_pool", "watch_boat"]
const EPS := 1e-3

var _nodes: Array[Node] = []


func _scene(path: String) -> Node:
	var packed := load(path) as PackedScene
	assert_true(packed != null, "%s loads as a PackedScene" % path)
	if packed == null:
		return Node3D.new()
	var node := packed.instantiate()
	_nodes.append(node)
	return node


func _done() -> void:
	for n in _nodes:
		if is_instance_valid(n):
			n.free()
	_nodes.clear()


func test_every_kit_material_loads_on_its_shader() -> void:
	var files := DirAccess.get_files_at(MATERIAL_DIR)
	var count := 0
	for f in files:
		if not f.ends_with(".tres"):
			continue
		count += 1
		var mat := load(MATERIAL_DIR + f) as Material
		assert_true(mat != null, "%s loads" % f)
		if mat is ShaderMaterial:
			assert_true((mat as ShaderMaterial).shader != null, "%s has its shader" % f)
	assert_true(count >= 20, "the kit's materials are written (%d)" % count)
	var bronze := load(MATERIAL_DIR + "tb_bell_bronze.tres") as ShaderMaterial
	assert_eq(bronze.shader.resource_path, "res://game/shaders/environment/env_bronze.gdshader", "bronze shader")


func test_imported_pieces_use_the_kit_materials_by_slot() -> void:
	for piece in PIECES:
		var root := _scene(KIT_DIR + piece + ".glb")
		assert_eq(root.get_meta(AssetImportRules.KIND_META, &""), KIND, "%s dressed by the kit rules" % piece)
		for node_name: String in [piece, piece + "-lod1"]:
			var mi := root.get_node_or_null(node_name) as MeshInstance3D
			assert_true(mi != null, "%s has %s" % [piece, node_name])
			if mi == null:
				continue
			for i in mi.mesh.get_surface_count():
				var slot := mi.mesh.surface_get_material(i).resource_name
				var want := load(MATERIAL_DIR + slot + ".tres")
				assert_true(want != null and mi.get_surface_override_material(i) == want, "%s %s" % [node_name, slot])
	_done()


func test_every_authored_chain_draws_exactly_one_lod() -> void:
	var lods := AssetImportRules.load_rules(String(KIND))["lods"] as Dictionary
	var ends: Array = lods["end_m"]
	var far := float(ends[ends.size() - 1]) - float(lods["margin_m"])
	for piece in PIECES:
		var root := _scene(KIT_DIR + piece + ".glb")
		var chain: Array[MeshInstance3D] = [
			root.get_node(piece) as MeshInstance3D, root.get_node(piece + "-lod1") as MeshInstance3D
		]
		assert_true(chain[0].get_node_or_null(chain[0].visibility_parent) == chain[1], "%s parent" % piece)
		var bad := LodRangeModel.hard_sweep_failures(chain, LodRangeModel.distances(far))
		assert_eq(bad.size(), 0, "%s: %s" % [piece, ", ".join(bad.slice(0, 6))])
	_done()


func test_only_the_drop_proxy_is_placeholder() -> void:
	var proxy := _scene(KIT_DIR + "reefball_drop_proxy.glb")
	assert_eq(proxy.get_meta(AssetImportRules.TAG_META, &""), AssetImportRules.PLACEHOLDER, "drop proxy tagged")
	for piece in PIECES:
		assert_false(_scene(KIT_DIR + piece + ".glb").has_meta(AssetImportRules.TAG_META), "%s finished" % piece)
	_done()


func test_preview_scene_keeps_the_drop_contract() -> void:
	var root := _scene(PREVIEW)
	var anchor := root.get_node_or_null("SphereAnchor") as Marker3D
	assert_true(anchor != null, "SphereAnchor exists")
	if anchor != null:
		assert_true(anchor.position.is_equal_approx(DROP_CENTER), "anchor at the drop centre: %s" % anchor.position)
		var drop := anchor.get_node_or_null("Drop") as Node3D
		assert_true(drop != null and drop.transform.is_equal_approx(Transform3D.IDENTITY), "Drop sits on the anchor")
	var column := root.get_node_or_null("ColumnAnchor") as Marker3D
	var ring := root.get_node_or_null("GoalRingAnchor") as Marker3D
	assert_true(column != null and absf(column.position.y - DROP_BOTTOM_Y) < EPS, "weep point")
	assert_true(ring != null and absf(ring.position.y - DROP_TOP_Y) < EPS, "goal ring at the surface")
	var cams := root.get_node("Cameras").get_children()
	assert_eq(cams.size(), 8, "T01-T08")
	for cam: Node in cams:
		assert_true(cam is HalunaShotCamera and (cam as HalunaShotCamera).shot != null, "%s composed" % cam.name)
	_done()
