extends TestCase
## M1-ART-02: the per-category post-import scripts (game/core/import/, rules in game/data/import/).
## The fixture tests/fixtures/import/import_probe.glb (build_import_probe.py) goes through the real
## import with the Haluna kit script, so these tests read what the pipeline produced: the -col
## proxy as a body, materials, LOD ranges and PLACEHOLDER metadata. The rest drive AssetImportRules
## on in-memory trees, check the committed assets' imports, and check the .import wiring.

const LodRangeModel := preload("res://tests/unit/lod_range_model.gd")
const PROBE := "res://tests/fixtures/import/import_probe.glb"
const PROBE_NOTE := "PLACEHOLDER: M1-ART-02 import test fixture, never placed in a level"
const KIT_DIR := "res://assets/environments/kits/haluna/"
const VEG_DIR := "res://assets/environments/vegetation/"
const BASE_BODY := "res://assets/characters/base_body/base_body_slender.glb"
const BUST := "res://assets/characters/shader_test/shader_test_bust.glb"
const ASHA_DIR := "res://assets/characters/asha/"
const KINDS: Array[String] = [
	"ashcrown_kit",
	"base_body",
	"brightwater_ferry_kit",
	"brine_shoals_kit",
	"characters",
	"coilspire_kit",
	"corrow_kit",
	"creatures",
	"crowd",
	"haluna_kit",
	"oruvel_kit",
	"oruvel_underway_kit",
	"pemakar_kit",
	"shader_test",
	"tamsule_bell_kit",
	"vegetation",
	"wildlife",
]
## M2-FP-07: the clip names the first-playable scripts call (`@anim asha <clip>`).
const HERO_CLIPS: Array[String] = [
	"idle",
	"walk",
	"run",
	"talk",
	"kneel_over_rhen",
	"laugh",
	"rise_to_stand",
	"offer_hand",
	"walk_to_chamber",
	"emerge_doorway",
	"face_west"
]
const LOOPED_CLIPS: Array[String] = ["idle", "walk", "run", "talk", "walk_to_chamber"]
const EPS := 1e-4

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


func _rules(kind: String) -> Dictionary:
	var r := AssetImportRules.load_rules(kind)
	assert_false(r.is_empty(), "rules for %s" % kind)
	return r


func _assert_range(mi: MeshInstance3D, begin: float, end: float, begin_margin: float, end_margin: float) -> void:
	assert_between(mi.visibility_range_begin, begin - EPS, begin + EPS, "%s begin" % mi.name)
	assert_between(mi.visibility_range_end, end - EPS, end + EPS, "%s end" % mi.name)
	assert_between(
		mi.visibility_range_begin_margin, begin_margin - EPS, begin_margin + EPS, "%s begin margin" % mi.name
	)
	assert_between(mi.visibility_range_end_margin, end_margin - EPS, end_margin + EPS, "%s end margin" % mi.name)


## LOD `lod` of a chain switching at `ends` has LodChain's range (no fade: the rules have none) and,
## below the last LOD, LOD lod+1 (`next`) as its visibility parent (M1-ENV-10).
func _assert_chain(mi: MeshInstance3D, lod: int, ends: Array, margin: float, next: MeshInstance3D) -> void:
	var r := LodChain.range_for(lod, PackedFloat32Array(ends), margin, 0.0, next != null)
	_assert_range(mi, r["begin"], r["end"], r["begin_margin"], r["end_margin"])
	assert_eq(mi.visibility_range_fade_mode, GeometryInstance3D.VISIBILITY_RANGE_FADE_DISABLED, "%s hard" % mi.name)
	assert_true(mi.get_node_or_null(mi.visibility_parent) == next, "%s visibility parent" % mi.name)


# ---- the imported fixture ----------------------------------------------------------------------


func test_fixture_collision_proxy_becomes_a_body_with_no_mesh() -> void:
	var root := _scene(PROBE)
	var col := _rules("haluna_kit")["collision"] as Dictionary
	var proxy := root.get_node_or_null("probe_post-col")
	assert_true(proxy is StaticBody3D, "the -col node is a StaticBody3D, got %s" % proxy)
	if proxy is StaticBody3D:
		var body := proxy as StaticBody3D
		assert_eq(body.collision_layer, int(col["layer"]), "layer from the rules")
		assert_eq(body.collision_mask, int(col["mask"]), "mask from the rules")
		assert_true(body.get_meta(AssetImportRules.COLLISION_META, false), "tagged hymn_collision")
		var shapes := body.find_children("*", "CollisionShape3D", false, false)
		assert_eq(shapes.size(), 1, "one shape")
		if shapes.size() == 1:
			var shape := (shapes[0] as CollisionShape3D).shape
			assert_true(shape is ConcavePolygonShape3D, "the kit's proxies are trimesh")
			assert_eq((shape as ConcavePolygonShape3D).get_faces().size(), 36, "the proxy box's 12 triangles")
		assert_true(body.owner == root, "the moved body is saved with the scene")
	for mi: Node in root.find_children("*", "MeshInstance3D", true, false):
		assert_false(String(mi.name).ends_with("-col"), "no visible proxy mesh (%s)" % mi.name)
	assert_true(root.get_node_or_null("probe_marker-noimp") == null, "-noimp helpers are not imported")
	_done()


func test_fixture_materials_override_by_slot_and_keep_the_gltf_slot() -> void:
	var root := _scene(PROBE)
	var post := root.get_node("probe_post") as MeshInstance3D
	var slab := root.get_node("probe_slab") as MeshInstance3D
	assert_eq(post.get_surface_override_material(0), load(KIT_DIR + "materials/kit_timber.tres"))
	assert_eq(slab.get_surface_override_material(0), load(KIT_DIR + "materials/kit_lashing.tres"))
	assert_eq(post.mesh.surface_get_material(0).resource_name, "kit_timber", "the glTF slot survives for dressers")
	_done()


func test_fixture_lod_ranges_follow_the_rules() -> void:
	var root := _scene(PROBE)
	var lods := _rules("haluna_kit")["lods"] as Dictionary
	var ends: Array = lods["end_m"]
	var m := float(lods["margin_m"])
	var lod0 := root.get_node("probe_post") as MeshInstance3D
	var lod1 := root.get_node("probe_post-lod1") as MeshInstance3D
	_assert_chain(lod0, 0, ends, m, lod1)
	_assert_chain(lod1, 1, ends, m, null)
	_assert_range(lod1, float(ends[0]), float(ends[1]), m, m)
	_done()


func test_fixture_placeholder_extras_tag_the_node_and_the_root() -> void:
	var root := _scene(PROBE)
	assert_eq(root.get_meta(AssetImportRules.TAG_META, &""), AssetImportRules.PLACEHOLDER, "root tagged")
	assert_eq(root.get_meta(AssetImportRules.NOTES_META, PackedStringArray()), PackedStringArray([PROBE_NOTE]))
	assert_eq(root.get_meta(AssetImportRules.KIND_META, &""), &"haluna_kit", "the rules that dressed it")
	assert_eq(root.get_node("probe_slab").get_meta(AssetImportRules.TAG_META, &""), AssetImportRules.PLACEHOLDER)
	assert_false(root.get_node("probe_post").has_meta(AssetImportRules.TAG_META), "undeclared nodes stay untagged")
	_done()


# ---- the committed assets ----------------------------------------------------------------------


func test_base_body_is_placeholder_and_keeps_its_gltf_materials() -> void:
	var root := _scene(BASE_BODY)
	assert_eq(root.get_meta(AssetImportRules.TAG_META, &""), AssetImportRules.PLACEHOLDER)
	var notes: PackedStringArray = root.get_meta(AssetImportRules.NOTES_META, PackedStringArray())
	assert_eq(notes.size(), 1, "one note (the bodies share it)")
	assert_true(notes.size() == 1 and notes[0].contains("M1-CHR-01"), "the build's hymn_note")
	for node: Node in root.find_children("*", "MeshInstance3D", true, false):
		var mi := node as MeshInstance3D
		assert_eq(mi.get_meta(AssetImportRules.TAG_META, &""), AssetImportRules.PLACEHOLDER, "%s tagged" % mi.name)
		for i in mi.mesh.get_surface_count():
			assert_true(mi.get_surface_override_material(i) == null, "%s keeps its PLACEHOLDER_* material" % mi.name)
	_done()


func test_kit_placeholder_pieces_are_tagged_and_finished_pieces_are_not() -> void:
	for piece: String in ["shell_shrine_massing"]:
		var root := _scene(KIT_DIR + piece + ".glb")
		assert_eq(root.get_meta(AssetImportRules.TAG_META, &""), AssetImportRules.PLACEHOLDER, piece)
		var notes: PackedStringArray = root.get_meta(AssetImportRules.NOTES_META, PackedStringArray())
		assert_true(notes.size() == 1 and notes[0].begins_with("PLACEHOLDER: "), "%s note %s" % [piece, notes])
	# M2-ENV-07: the two trees are real now (they keep their old piece names, untagged).
	for piece: String in ["dock_haluna", "banyan_hero", "windbreak_tree"]:
		var finished := _scene(KIT_DIR + piece + ".glb")
		assert_false(finished.has_meta(AssetImportRules.TAG_META), "%s is not placeholder" % piece)
	_done()


func test_vegetation_import_matches_vegetation_plant_defaults() -> void:
	var root := _scene(VEG_DIR + "palm_coconut_a.glb")
	var plant := VegetationPlant.new()
	var lods := _rules("vegetation")["lods"] as Dictionary
	assert_eq(PackedFloat32Array(lods["end_m"]), plant.lod_end_m, "the rules are VegetationPlant's defaults")
	assert_between(float(lods["margin_m"]), plant.lod_margin_m - EPS, plant.lod_margin_m + EPS, "margin")
	var ends := plant.lod_end_m
	for lod in ends.size():
		var node_name := "palm_coconut_a" if lod == 0 else "palm_coconut_a-lod%d" % lod
		var mi := root.get_node(node_name) as MeshInstance3D
		var next := root.get_node_or_null("palm_coconut_a-lod%d" % (lod + 1)) as MeshInstance3D
		_assert_chain(mi, lod, Array(ends), plant.lod_margin_m, next if lod + 1 < ends.size() else null)
		for i in mi.mesh.get_surface_count():
			var slot := mi.mesh.surface_get_material(i).resource_name
			assert_eq(mi.get_surface_override_material(i), load(VEG_DIR + "materials/%s.tres" % slot), slot)
	plant.free()
	_done()


## The bust keeps its glTF materials, with no import-time overrides (asset_import.md, "Shared
## materials and shader tiers"). The rule dates from when CharacterShaderTiers.apply_to_tree swapped
## shaders on shared materials in place. Since M1-RND-19 it copies before it swaps, so overrides
## would now be safe. The bust stays without them because CharacterShadingStage assigns its own.
func test_shader_test_meshes_get_no_import_materials() -> void:
	var root := _scene(BUST)
	assert_true((_rules("shader_test")["materials"] as Dictionary).is_empty(), "no material rules")
	assert_eq(root.get_meta(AssetImportRules.KIND_META, &""), &"shader_test", "the script ran")
	var seen := 0
	for node: Node in root.find_children("*", "MeshInstance3D", true, false):
		var mi := node as MeshInstance3D
		assert_true(mi.get_surface_override_material(0) == null, "%s has no import override" % mi.name)
		seen += 1
	assert_eq(seen, 11, "the bust's 11 meshes")
	_done()


# ---- AssetImportRules on in-memory trees -------------------------------------------------------


func _proxy_tree(proxy_name: String) -> Node3D:
	var root := Node3D.new()
	var mi := MeshInstance3D.new()
	mi.name = proxy_name
	mi.mesh = BoxMesh.new()
	mi.position = Vector3(1.0, 2.0, 3.0)
	root.add_child(mi)
	mi.owner = root
	var body := StaticBody3D.new()
	mi.add_child(body)
	body.owner = root
	var shape := CollisionShape3D.new()
	shape.shape = mi.mesh.create_trimesh_shape()
	body.add_child(shape)
	shape.owner = root
	_nodes.append(root)
	return root


func test_convex_rule_replaces_the_trimesh_and_keeps_the_transform() -> void:
	var root := _proxy_tree("rock-col")
	var report := AssetImportRules.apply(root, _rules("vegetation"), "res://x/rock.glb")
	assert_eq(int(report["collision"]), 1)
	var body := root.get_node_or_null("rock-col") as StaticBody3D
	assert_true(body != null, "the body took the proxy's name")
	if body != null:
		assert_eq(body.position, Vector3(1.0, 2.0, 3.0), "the proxy's transform")
		var shape := (body.get_child(0) as CollisionShape3D).shape
		assert_true(shape is ConvexPolygonShape3D, "vegetation proxies are convex")
		assert_eq((body.get_child(0) as Node3D).transform, Transform3D.IDENTITY, "the shape child stays at identity")
	_done()


## M2-NIT-03: the convex shape is built in mesh space, so it must land where the proxy mesh was even
## when Godot's body or shape child is not at identity.
func test_convex_shape_stays_on_the_proxy_mesh_whatever_the_child_transforms() -> void:
	var root := _proxy_tree("rock-col")
	var mi := root.get_node("rock-col") as MeshInstance3D
	var mesh_xform := mi.transform
	var old_body := mi.get_child(0) as StaticBody3D
	old_body.transform = Transform3D(Basis(Vector3.UP, 0.5), Vector3(0.0, 1.5, 0.0))
	(old_body.get_child(0) as Node3D).transform = Transform3D(Basis(), Vector3(4.0, 0.0, 0.0))
	AssetImportRules.apply(root, _rules("vegetation"), "res://x/rock.glb")
	var body := root.get_node("rock-col") as StaticBody3D
	var placed := body.transform * (body.get_child(0) as CollisionShape3D).transform
	assert_true(placed.is_equal_approx(mesh_xform), "the convex shape sits on the mesh: %s" % placed)
	_done()


func test_proxy_without_a_body_is_reported_not_dropped() -> void:
	var root := Node3D.new()
	_nodes.append(root)
	var mi := MeshInstance3D.new()
	mi.name = "odd-col"
	mi.mesh = BoxMesh.new()
	root.add_child(mi)
	var report := AssetImportRules.apply(root, {"collision": {"proxy_suffix": "-col"}})
	assert_eq(int(report["collision"]), 0)
	assert_eq((report["warnings"] as Array).size(), 1, "one warning")
	assert_true(root.get_node_or_null("odd-col") is MeshInstance3D, "left as it was")
	_done()


func test_character_slots_resolve_in_the_asset_directory() -> void:
	var root := Node3D.new()
	_nodes.append(root)
	var mi := MeshInstance3D.new()
	mi.name = "HairHead"
	var mesh := BoxMesh.new()
	mesh.material = StandardMaterial3D.new()
	mesh.material.resource_name = "hair"
	mi.mesh = mesh
	root.add_child(mi)
	var report := AssetImportRules.apply(root, _rules("characters"), ASHA_DIR + "asha.glb")
	assert_eq(mi.get_surface_override_material(0), load(ASHA_DIR + "materials/hair.tres"), "{asset_dir} slot")
	assert_eq(int(report["materials"]), 1)
	mesh.material.resource_name = "no_such_slot"
	mi.set_surface_override_material(0, null)
	report = AssetImportRules.apply(root, _rules("characters"), ASHA_DIR + "asha.glb")
	assert_true(mi.get_surface_override_material(0) == null, "an unknown slot keeps the glTF material")
	assert_eq((report["warnings"] as Array).size(), 1, "and is reported")
	_done()


func test_lods_past_the_table_are_hidden_and_mesh_extras_tag_placeholder() -> void:
	var root := Node3D.new()
	_nodes.append(root)
	var far := MeshInstance3D.new()
	far.name = "tree-lod3"
	far.mesh = BoxMesh.new()
	far.mesh.set_meta(AssetImportRules.EXTRAS_META, {"hymn_tag": "PLACEHOLDER"})
	root.add_child(far)
	AssetImportRules.apply(root, {"lods": {"suffix": "-lod", "end_m": [10.0, 20.0], "margin_m": 1.0}})
	assert_false(far.visible, "LOD3 with a two-entry table is hidden")
	assert_eq(root.get_meta(AssetImportRules.TAG_META, &""), AssetImportRules.PLACEHOLDER, "mesh extras count")
	assert_eq(
		root.get_meta(AssetImportRules.NOTES_META, PackedStringArray()), PackedStringArray(), "a bare tag adds no note"
	)
	_done()


## M2-NIT-03: a mesh with no `<name>-lodN` sibling past LOD0 gets no range, so it cannot vanish at
## the LOD0 distance with nothing drawn behind it. A chain still gets every range.
func test_a_mesh_without_a_lod_chain_gets_no_visibility_range() -> void:
	var root := Node3D.new()
	_nodes.append(root)
	var names: Array[String] = ["loose", "tree", "tree-lod1"]
	for n in names:
		var mi := MeshInstance3D.new()
		mi.name = n
		mi.mesh = BoxMesh.new()
		root.add_child(mi)
	var report := AssetImportRules.apply(root, {"lods": {"suffix": "-lod", "end_m": [10.0, 20.0], "margin_m": 1.0}})
	var loose := root.get_node("loose") as MeshInstance3D
	assert_eq(loose.visibility_range_end, 0.0, "no range on an unchained mesh")
	assert_true(loose.visible)
	var tree := root.get_node("tree") as MeshInstance3D
	var tree_lod1 := root.get_node("tree-lod1") as MeshInstance3D
	_assert_chain(tree, 0, [10.0, 20.0], 1.0, tree_lod1)
	_assert_range(tree_lod1, 10.0, 20.0, 1.0, 1.0)
	assert_eq(int(report["lods"]), 2, "only the chain is counted")
	assert_eq(AssetImportRules.lod_base("tree-lod1", "-lod"), "tree")
	assert_eq(AssetImportRules.lod_base("dock-lodx", "-lod"), "dock-lodx", "not a LOD suffix")
	assert_eq(AssetImportRules.lod_base("tree", ""), "tree")
	_done()


func test_lod_index_reads_the_suffix() -> void:
	assert_eq(AssetImportRules.lod_index("palm_coconut_a", "-lod"), 0)
	assert_eq(AssetImportRules.lod_index("palm_coconut_a-lod2", "-lod"), 2)
	assert_eq(AssetImportRules.lod_index("dock-lodx", "-lod"), 0)
	assert_eq(AssetImportRules.lod_index("dock-lod1", ""), 0)


# ---- LOD chains (M1-ENV-10) ---------------------------------------------------------------------


## An in-memory `tree`, `tree-lod1`... chain of `count` LODs under a fresh root.
func _chain_root(count: int) -> Array[MeshInstance3D]:
	var root := Node3D.new()
	_nodes.append(root)
	var chain: Array[MeshInstance3D] = []
	for lod in count:
		var mi := MeshInstance3D.new()
		mi.name = "tree" if lod == 0 else "tree-lod%d" % lod
		mi.mesh = BoxMesh.new()
		root.add_child(mi)
		chain.append(mi)
	return chain


## Each category's rules (and the imported fixture and a real kit piece) draw exactly one LOD at every
## distance up to the last switch-out, from a still camera, sweeping in and sweeping out: no hole within
## a switch margin, no double draw.
func test_a_distance_sweep_draws_exactly_one_lod() -> void:
	for kind: String in ["haluna_kit", "vegetation"]:
		var lods := _rules(kind)["lods"] as Dictionary
		var ends: Array = lods["end_m"]
		var chain := _chain_root(ends.size())
		AssetImportRules.apply(chain[0].get_parent(), {"lods": lods})
		var far := float(ends[ends.size() - 1]) - float(lods["margin_m"])
		var bad := LodRangeModel.hard_sweep_failures(chain, LodRangeModel.distances(far))
		assert_eq(bad.size(), 0, "%s: %s" % [kind, ", ".join(bad.slice(0, 6))])
	var kit_ends: Array = _rules("haluna_kit")["lods"]["end_m"]
	for pair: Array in [[PROBE, "probe_post"], [KIT_DIR + "dock_haluna.glb", "dock_haluna"]]:
		var root := _scene(str(pair[0]))
		var chain: Array[MeshInstance3D] = [
			root.get_node(str(pair[1])) as MeshInstance3D, root.get_node(str(pair[1]) + "-lod1") as MeshInstance3D
		]
		var bad := LodRangeModel.hard_sweep_failures(chain, LodRangeModel.distances(float(kit_ends[0]) * 2.0))
		assert_eq(bad.size(), 0, "%s: %s" % [pair[0], ", ".join(bad.slice(0, 6))])
	_done()


## A lone mesh (no chain) still gets no range and no visibility parent, so it draws at any distance.
func test_a_single_lod_mesh_gets_no_visibility_parent() -> void:
	var chain := _chain_root(1)
	AssetImportRules.apply(chain[0].get_parent(), {"lods": _rules("haluna_kit")["lods"]})
	assert_eq(chain[0].visibility_parent, NodePath(), "no parent")
	assert_eq(chain[0].visibility_range_end, 0.0, "no range")
	assert_eq(LodRangeModel.draws(chain, 5000.0, {}), [1] as Array[int], "draws at any distance")
	_done()


# ---- wiring ------------------------------------------------------------------------------------


func _import_files(dir: String) -> PackedStringArray:
	var out := PackedStringArray()
	for f in DirAccess.get_files_at(dir):
		if f.ends_with(".glb.import"):
			out.append(dir + f)
	return out


func test_every_glb_import_runs_its_category_script() -> void:
	var covered := {}
	for kind in KINDS:
		var rules := _rules(kind)
		assert_eq(str(rules["kind"]), kind, "%s.json names its kind" % kind)
		assert_true(ResourceLoader.exists(str(rules["script"])), "%s script exists" % kind)
		var pending: Dictionary = rules.get("adoption_pending", {})
		for dir: String in rules["assets"]:
			for path in _import_files(dir):
				assert_false(covered.has(path), "%s is in one category only" % path)
				covered[path] = kind
				var cfg := ConfigFile.new()
				assert_eq(cfg.load(path), OK, path)
				var want := "" if pending.has(dir) else str(rules["script"])
				assert_eq(str(cfg.get_value("params", "import_script/path", "")), want, path)
				assert_eq(bool(cfg.get_value("params", "meshes/generate_lods")), bool(rules["generate_lods"]), path)
				assert_true(bool(cfg.get_value("params", "meshes/ensure_tangents")), "%s ensures tangents" % path)
	for dir: String in _asset_dirs("res://assets/"):
		for path in _import_files(dir):
			assert_true(covered.has(path), "%s belongs to an import category" % path)


## M2-FP-07: Asha has adopted the character rules (asset_import.md); nothing is pending.
func test_asha_adopts_the_character_rules() -> void:
	var rules := _rules("characters")
	assert_true((rules["adoption_pending"] as Dictionary).is_empty(), "no hero is pending")
	assert_true((rules["assets"] as Array).has(ASHA_DIR), "Asha is a character asset")
	for path in _import_files(ASHA_DIR):
		var cfg := ConfigFile.new()
		cfg.load(path)
		assert_eq(str(cfg.get_value("params", "import_script/path", "")), str(rules["script"]), path)


## M2-FP-07: a hero with a clip library gets an AnimationPlayer at its root (M2-CHR-06: its LOD1 file too).
func test_hero_clips_become_an_animation_player() -> void:
	var rules := _rules("characters")
	var root := Node3D.new()
	_nodes.append(root)
	var report := AssetImportRules.apply(root, rules, ASHA_DIR + "asha.glb")
	var ap := root.get_node_or_null(^"AnimationPlayer") as AnimationPlayer
	assert_true(ap != null, "AnimationPlayer added")
	if ap != null:
		for clip: String in HERO_CLIPS:
			assert_true(ap.has_animation(clip), clip)
		assert_eq(ap.playback_default_blend_time, float(rules["animations"]["default_blend_s"]))
		assert_eq(int(report["animations"]), ap.get_animation_list().size())
	# M2-CHR-06: the LOD1 file (the battle-scale model) shares the hero's library
	var lod := Node3D.new()
	_nodes.append(lod)
	AssetImportRules.apply(lod, rules, ASHA_DIR + "asha_lod1.glb")
	var lod_ap := lod.get_node_or_null(^"AnimationPlayer") as AnimationPlayer
	assert_true(lod_ap != null and lod_ap.has_animation(&"idle"), "the LOD1 file gets the hero's clips")
	var other := Node3D.new()
	_nodes.append(other)
	AssetImportRules.apply(other, rules, "res://assets/characters/nobody/nobody.glb")
	assert_true(other.get_node_or_null(^"AnimationPlayer") == null, "no library, no player")
	_done()


## M2-FP-07: the imported Asha carries her clips, loops where the request says, and every track
## names a bone of her skeleton.
func test_imported_asha_plays_her_clips() -> void:
	var asha := _scene(ASHA_DIR + "asha.glb")
	var ap := asha.find_child("AnimationPlayer", true, false) as AnimationPlayer
	assert_true(ap != null, "the import gives Asha an AnimationPlayer")
	if ap == null:
		_done()
		return
	var skel := asha.find_children("*", "Skeleton3D", true, false)[0] as Skeleton3D
	for clip: String in HERO_CLIPS:
		assert_true(ap.has_animation(clip), clip)
		if not ap.has_animation(clip):
			continue
		var anim := ap.get_animation(clip)
		var looped := anim.loop_mode == Animation.LOOP_LINEAR
		assert_eq(looped, clip in LOOPED_CLIPS, "%s loop mode" % clip)
		for t: int in anim.get_track_count():
			var path := anim.track_get_path(t)
			assert_true(
				asha.get_node_or_null(NodePath(path.get_concatenated_names())) == skel, "%s track %d" % [clip, t]
			)
			assert_true(skel.find_bone(String(path.get_concatenated_subnames())) >= 0, "%s bone %s" % [clip, path])
	_done()


func _asset_dirs(dir: String) -> PackedStringArray:
	var out := PackedStringArray([dir])
	for sub in DirAccess.get_directories_at(dir):
		out.append_array(_asset_dirs(dir + sub + "/"))
	return out
