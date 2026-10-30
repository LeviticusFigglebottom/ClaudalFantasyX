extends TestCase
## M3-CRE-659 (ADR 0152): Act I's crowd. A crowd row turns a synthetic greybox stage actor into a villager (the
## capsule hidden, the person's tints on the body's materials, their work clip at rest, a group's offsets inside one
## stand-in); every crowd body's actor loads headless with idle, talk, walk and its people's work clips; and the real
## Brine Shoals zone resolves its crowd rows.

const CROWD := "res://game/data/world/npc/crowd.json"
const ASHCROWN := "res://game/levels/ch05/ashcrown/ashcrown.tscn"
const BRINE_SHOALS := "res://game/levels/ch06/brine_shoals/brine_shoals.tscn"
const CORROW := "res://game/levels/ch08/corrow/corrow.tscn"
const TEST_DATA := "user://crowd_layer_test.json"
const DT := 1.0 / 60.0
const BASE_CLIPS: Array[StringName] = [&"idle", &"talk", &"walk"]
## M3-CRE-662: the shared clip libraries. Standing clips sampled at these times keep each body's toes on its own floor.
const PLANTED_CLIPS: Array[StringName] = [&"idle", &"talk"]
const PLANTED_TIMES: Array[float] = [0.0, 1.3, 2.6]
const TOES: Array[String] = ["DEF-toe.L", "DEF-toe.R"]
const FLOOR_TOLERANCE_M := 0.02
const SCALE_TOLERANCE := 0.0001

var made: Array[Node] = []


func _holder() -> Node3D:
	var h := Node3D.new()
	var tree := Engine.get_main_loop() as SceneTree
	(tree.current_scene if tree.current_scene != null else tree.root).add_child(h)
	made.append(h)
	return h


func _done() -> void:
	for n in made:
		if is_instance_valid(n):
			n.get_parent().remove_child(n)
			n.free()
	made.clear()


func _people() -> Dictionary:
	var out := {}
	for p: Variant in VillagerLayer.load_data(CROWD).get("people", []) as Array:
		out[str(p["id"])] = p
	return out


## A zone shaped like a GreyboxZone's stage: CutsceneStage/Actors/<id> holding a capsule `StandIn`.
func _greybox_zone(actor_ids: Array[String]) -> Node3D:
	var zone := _holder()
	var stage := Node3D.new()
	stage.name = &"CutsceneStage"
	zone.add_child(stage)
	var actors := Node3D.new()
	actors.name = &"Actors"
	stage.add_child(actors)
	for id in actor_ids:
		var a := Node3D.new()
		a.name = id
		a.position = Vector3(3.0 * actors.get_child_count(), 0.0, -2.0)
		actors.add_child(a)
		var capsule := MeshInstance3D.new()
		capsule.name = &"StandIn"
		capsule.mesh = CapsuleMesh.new()
		a.add_child(capsule)
	return zone


func _layer(zone: Node3D, rows: Array) -> VillagerLayer:
	var f := FileAccess.open(TEST_DATA, FileAccess.WRITE)
	f.store_string(JSON.stringify({"zone": "_tests/crowd", "villagers": rows}))
	f.close()
	var layer := VillagerLayer.new()
	layer.zone_id = &"_tests/crowd"
	layer.data_path = TEST_DATA
	layer.auto_build = false
	zone.add_child(layer)
	return layer


## The first colour of `slot` found on the actor's surfaces (Color(0, 0, 0, 0) if none).
func _slot_colour(actor: Node, slot: StringName) -> Color:
	for node: Node in actor.find_children("*", "MeshInstance3D", true, false):
		var mi := node as MeshInstance3D
		for i in mi.mesh.get_surface_count():
			if NpcTints.slot_of(mi, i) == slot:
				return NpcTints.colour_of(mi, i)
	return Color(0, 0, 0, 0)


func test_a_crowd_row_dresses_a_greybox_actor() -> void:
	var people := _people()
	var mender: Dictionary = people["corrow_netmender"]
	var zone := _greybox_zone(["netmender"])
	var layer := _layer(
		zone,
		[
			{
				"npc_id": "corrow_netmender",
				"crowd": "corrow_netmender",
				"stand_in": "CutsceneStage/Actors/netmender",
				"attach": "child"
			}
		]
	)
	assert_eq(layer.build(), 1, "the crowd row makes one villager")
	var stand_in := zone.get_node(^"CutsceneStage/Actors/netmender") as Node3D
	var npc := layer.villager(&"corrow_netmender")
	assert_true(npc != null and npc.get_parent() == stand_in, "it rides inside the stage actor")
	assert_false((stand_in.get_node(^"StandIn") as Node3D).visible, "the capsule is hidden")
	assert_true(npc.actor != null, "wearing its crowd body")
	assert_eq(
		npc.actor.scene_file_path,
		VillagerLayer.CROWD_ACTOR_PATH % [mender["body"], mender["body"]],
		"the body the roster assigned"
	)
	var tinted := 0
	for slot: String in ["cloth_a", "cloth_b", "cloth_c", "hair"]:
		var got := _slot_colour(npc.actor, StringName(slot))
		if got.a == 0.0:
			continue  # this body's costume has no piece in that slot
		tinted += 1
		var want := Color.html(str(mender["tints"][slot]))
		assert_true(got.is_equal_approx(want), "%s tinted %s, got %s" % [slot, want, got])
	assert_true(tinted >= 3, "the hair and the cloth it wears are tinted (%d slots)" % tinted)
	var work := StringName(str(mender["work"]))
	assert_true(npc.anim != null and npc.anim.has_animation(work), "the body carries the work clip")
	for i in 30:
		npc.tick(DT)
	assert_true(npc.working(), "at rest it works")
	assert_eq(npc.current_clip, work, "and plays its work clip")
	_done()


func test_tints_are_per_person_on_a_shared_body() -> void:
	var people := _people()
	var by_body := {}
	var pair: Array = []
	for id: String in people:
		var body := str(people[id]["body"])
		if by_body.has(body):
			pair = [by_body[body], id]
			break
		by_body[body] = id
	assert_eq(pair.size(), 2, "some body is worn twice")
	var zone := _greybox_zone(["a", "b"])
	var layer := _layer(
		zone,
		[
			{"npc_id": pair[0], "crowd": pair[0], "stand_in": "CutsceneStage/Actors/a", "attach": "child"},
			{"npc_id": pair[1], "crowd": pair[1], "stand_in": "CutsceneStage/Actors/b", "attach": "child"},
		]
	)
	assert_eq(layer.build(), 2, "two people on one body")
	var one := layer.villager(StringName(pair[0]))
	var two := layer.villager(StringName(pair[1]))
	var c1 := _slot_colour(one.actor, &"cloth_a")
	var c2 := _slot_colour(two.actor, &"cloth_a")
	assert_true(c1.is_equal_approx(Color.html(str(people[pair[0]]["tints"]["cloth_a"]))), "the first wears its own")
	assert_true(c2.is_equal_approx(Color.html(str(people[pair[1]]["tints"]["cloth_a"]))), "the second its own")
	_done()


func test_a_group_stands_inside_one_capsule_at_its_offsets() -> void:
	var zone := _greybox_zone(["wrights"])
	var rows: Array = []
	var offsets: Array = [[-1.0, 0.0, 0.0, 10.0], [1.0, 0.0, 0.5, -10.0]]
	for i in 2:
		var id := "brine_shoals_wright_%d" % (i + 1)
		rows.append(
			{
				"npc_id": id,
				"crowd": id,
				"stand_in": "CutsceneStage/Actors/wrights",
				"attach": "child",
				"offset": offsets[i]
			}
		)
	var layer := _layer(zone, rows)
	assert_eq(layer.build(), 2, "both rows on the one group actor")
	var stand_in := zone.get_node(^"CutsceneStage/Actors/wrights")
	assert_eq(stand_in.find_children("*", "FieldNpc", true, false).size(), 2, "two villagers inside it, not adopted")
	var first := layer.villager(&"brine_shoals_wright_1")
	assert_true(first.position.is_equal_approx(Vector3(-1.0, 0.0, 0.0)), "at its offset")
	assert_between(rad_to_deg(first.rotation.y), 9.9, 10.1, "turned by its offset yaw")
	_done()


func test_every_crowd_body_loads_with_its_clips() -> void:
	var data := VillagerLayer.load_data(CROWD)
	var work := {}
	for p: Dictionary in data["people"]:
		if str(p["work"]) != "":
			work[str(p["body"])] = (work.get(str(p["body"]), []) as Array) + [StringName(str(p["work"]))]
	for body: String in data["bodies"] as Dictionary:
		var scene := load(VillagerLayer.CROWD_ACTOR_PATH % [body, body]) as PackedScene
		assert_true(scene != null, "%s: actor scene loads" % body)
		if scene == null:
			continue
		var actor := scene.instantiate() as Node3D
		_holder().add_child(actor)
		var anim := HeroMotion.player_of(actor)
		assert_true(anim != null, "%s: an AnimationPlayer from the import rule" % body)
		if anim == null:
			continue
		var clips: Array = BASE_CLIPS.duplicate()
		clips.append_array(work.get(body, []) as Array)
		for clip: Variant in clips:
			assert_true(anim.has_animation(StringName(clip)), "%s: clip %s" % [body, clip])
		var dressed := false
		for slot: StringName in [&"cloth_a", &"cloth_b", &"cloth_c"]:
			dressed = dressed or _slot_colour(actor, slot).a > 0.0
		assert_true(dressed, "%s: dressed by its cloth materials" % body)
	_done()


## M3-CRE-662: each body wears its group's one library (the same resource for every member), its armature carries
## the library's root name, its hips track is scaled to its own height, and its standing clips keep its toes where
## its own rest pose has them (a child on the adult library's hips would float or sink by tens of cm).
func test_every_crowd_body_shares_its_groups_clips_at_its_own_height() -> void:
	var data := VillagerLayer.load_data(CROWD)
	var rules := AssetImportRules.load_rules("crowd").get("animations", {}) as Dictionary
	var libraries := rules.get("libraries", {}) as Dictionary
	var first_of := {}
	for body: String in data["bodies"] as Dictionary:
		var actor := (load(VillagerLayer.CROWD_ACTOR_PATH % [body, body]) as PackedScene).instantiate() as Node3D
		_holder().add_child(actor)
		var anim := HeroMotion.player_of(actor)
		var skel := HeroMotion.skeleton_of(actor)
		assert_true(anim != null and skel != null, "%s: a player and a skeleton" % body)
		if anim == null or skel == null:
			continue
		var lib_name := str(libraries.get(body, ""))
		var lib := anim.get_animation_library(&"")
		assert_eq(lib.resource_path, str(rules["library"]).replace(CrowdClipLibrary.LIBRARY_TOKEN, lib_name), body)
		if first_of.has(lib_name):
			assert_true(is_same(first_of[lib_name], lib), "%s: the one %s library resource" % [body, lib_name])
		first_of[lib_name] = lib
		assert_eq(String(skel.get_parent().name), str(rules["armature"]), "%s: the library's armature" % body)
		var rest_y := skel.get_bone_rest(skel.find_bone(str(rules["hips_bone"]))).origin.y
		var want := rest_y / float(lib.get_meta(StringName(str(rules["hips_meta"])), 1.0))
		assert_between(skel.motion_scale, want - SCALE_TOLERANCE, want + SCALE_TOLERANCE, "%s: motion_scale" % body)
		for clip in PLANTED_CLIPS:
			anim.play(clip)
			for t in PLANTED_TIMES:
				anim.seek(t, true)
				for toe in TOES:
					var b := skel.find_bone(toe)
					var dy := skel.get_bone_global_pose(b).origin.y - skel.get_bone_global_rest(b).origin.y
					var what := "%s: %s at %.1f s, %s off the floor" % [body, clip, t, toe]
					assert_between(dy, -FLOOR_TOLERANCE_M, FLOOR_TOLERANCE_M, what)
	var distinct := {}
	for lib_name: Variant in libraries.values():
		distinct[lib_name] = true
	assert_eq(first_of.size(), distinct.size(), "every group's library in use")
	_done()


func test_brine_shoals_crowd_comes_alive_in_the_real_zone() -> void:
	var zone := (load(BRINE_SHOALS) as PackedScene).instantiate() as Node3D
	_holder().add_child(zone)
	var layer := VillagerLayer.wire(zone, &"ch06/brine_shoals")
	layer.build()  # wired into a ready zone, the layer builds deferred; the runner steps no frame, so build it now
	assert_eq(layer.live_villagers().size(), 10, "the girl, the clerk, two children and six wrights")
	var wrights := zone.get_node_or_null(^"CutsceneStage/Actors/wrights")
	assert_true(wrights != null, "the group's stage actor")
	if wrights != null:
		assert_eq(wrights.find_children("*", "FieldNpc", true, false).size(), 6, "six wrights at the group capsule")
		var capsule := wrights.get_node_or_null(^"StandIn") as Node3D
		assert_true(capsule != null and not capsule.visible, "its capsule is hidden")
	_done()


## ZoneCast (M3-CIN-1217) dresses Ashcrown's tender as Haluna's Reed; the crowd row replaces that body with the crowd
## person (ADR 0152: Haluna's faces stand for no other town), so one body shows and the cutscenes' clips find it. (Once
## GreyboxZone adds its own layer, M3-CRE-657, the zone has done it by the time `wire` returns that layer.)
func test_a_crowd_person_replaces_the_zone_cast_villager() -> void:
	var zone := (load(ASHCROWN) as PackedScene).instantiate() as Node3D
	_holder().add_child(zone)
	var tender := zone.get_node_or_null(^"CutsceneStage/Actors/tender")
	assert_true(tender != null, "the tender's stage actor")
	var layer := VillagerLayer.wire(zone, &"ch05/ashcrown")
	layer.build()
	if tender != null:
		assert_true(tender.get_node_or_null(^"Cast") == null, "the cast villager is gone")
		assert_eq(tender.find_children("*", "AnimationPlayer", true, false).size(), 1, "one body on the actor")
		var npc := layer.villager(&"ashcrown_tender")
		assert_true(
			npc != null and HeroMotion.player_of(tender) == npc.anim, "the cutscene's clips play the crowd person"
		)
	_done()


## M2-CHR-100: a villager the zone placed first in another's model (HalunaVillagers' shop bodies) gives way to the
## row's crowd person, so one body shows; a row with no crowd person adopts what the zone placed, as before.
func test_a_borrowed_model_placed_first_gives_way_to_the_rows_own() -> void:
	var zone := _greybox_zone(["shop", "keep"])
	var placed: Array[FieldNpc] = []
	for id: String in ["shop", "keep"]:
		var npc := FieldNpc.new()
		npc.name = &"Villager"
		npc.npc_id = StringName(id)
		var path := "res://assets/characters/villagers/netmender/netmender_actor.tscn"
		var actor := (load(path) as PackedScene).instantiate() as Node3D
		actor.name = String(npc.actor_path)
		npc.add_child(actor)
		zone.get_node("CutsceneStage/Actors/" + id).add_child(npc)
		placed.append(npc)
	var person := _people()["oruvel_cook"] as Dictionary
	var rows := [
		{"npc_id": "shop", "crowd": "oruvel_cook", "attach": "child", "stand_in": "CutsceneStage/Actors/shop"},
		{"npc_id": "keep", "actor": "netmender", "attach": "child", "stand_in": "CutsceneStage/Actors/keep"},
	]
	var layer := _layer(zone, rows)
	layer.build()
	var shop := zone.get_node("CutsceneStage/Actors/shop")
	assert_false(is_instance_valid(placed[0]), "the borrowed model is gone")
	assert_eq(shop.find_children("*", "FieldNpc", true, false).size(), 1, "one villager in the shop body")
	var body := str(person["body"])
	var shop_npc := layer.villager(&"shop")
	assert_true(shop_npc != null, "the shop row's villager")
	if shop_npc != null:
		assert_eq(shop_npc.actor_scene.resource_path, VillagerLayer.CROWD_ACTOR_PATH % [body, body], "its own body")
	assert_true(
		is_instance_valid(placed[1]) and layer.villager(&"keep") == placed[1], "no crowd person: adopted, not rebuilt"
	)
	_done()


## An Act II town's greybox names no actors: a row's `at` makes its stand-in at CrowdSpots/<name> and the person
## stands there (the Lead, 2026-10-30: Hollowmere's townsfolk).
func test_an_at_row_makes_its_own_spot() -> void:
	var zone := _holder()
	var rows := [
		{
			"npc_id": "netmender",
			"crowd": "hollowmere_netmender",
			"attach": "child",
			"stand_in": "CrowdSpots/hollowmere_netmender",
			"at": [4.0, 0.5, -2.0, 90.0],
		},
		{
			"npc_id": "stray",
			"crowd": "hollowmere_fisher",
			"attach": "child",
			"stand_in": "Elsewhere/x",
			"at": [0, 0, 0]
		},
	]
	var layer := _layer(zone, rows)
	layer.build()
	var spot := zone.get_node_or_null(^"CrowdSpots/hollowmere_netmender") as Node3D
	assert_true(spot != null, "the spot is made")
	if spot != null:
		assert_true(spot.position.is_equal_approx(Vector3(4.0, 0.5, -2.0)), "at its `at`")
		assert_true(is_equal_approx(spot.rotation.y, deg_to_rad(90.0)), "facing its yaw")
		assert_eq(spot.find_children("*", "FieldNpc", true, false).size(), 1, "the person stands in it")
	assert_true(layer.villager(&"stray") == null, "a spot outside CrowdSpots is refused")
	_done()


## M3-HER-1142: a `body` row wears a crowd body with no crowd person, and `silhouette` draws it as one glowing shape
## that casts no shadow; its `tuning` keeps it from glancing at the party.
func test_a_silhouette_row_wears_a_bare_crowd_body_as_one_glowing_shape() -> void:
	var zone := _greybox_zone(["figure"])
	var layer := _layer(
		zone,
		[
			{
				"npc_id": "storm_figure_test",
				"body": "crowd_man_lean_a",
				"silhouette": "#5fd6e0",
				"tuning": {"glance": {"radius_m": 0.0}},
				"stand_in": "CutsceneStage/Actors/figure",
				"attach": "child"
			}
		]
	)
	assert_eq(layer.build(), 1, "the body row makes one villager")
	var npc := layer.villager(&"storm_figure_test")
	assert_true(npc != null and npc.actor != null, "wearing a body")
	if npc == null or npc.actor == null:
		_done()
		return
	assert_eq(npc.actor.scene_file_path, VillagerLayer.CROWD_ACTOR_PATH % ["crowd_man_lean_a", "crowd_man_lean_a"])
	assert_false((zone.get_node(^"CutsceneStage/Actors/figure/StandIn") as Node3D).visible, "the capsule is hidden")
	var meshes := npc.actor.find_children("*", "MeshInstance3D", true, false)
	assert_true(meshes.size() > 0, "the body has meshes")
	var glow := Color.html("#5fd6e0")
	var detailed := 0
	for node: Node in meshes:
		var mi := node as MeshInstance3D
		assert_eq(mi.cast_shadow, GeometryInstance3D.SHADOW_CASTING_SETTING_OFF, "%s casts no shadow" % mi.name)
		for i in mi.mesh.get_surface_count():
			var mat := mi.get_surface_override_material(i) as ShaderMaterial
			assert_true(mat != null and mat.shader == NpcSilhouette.SHADER, "%s/%d wears the silhouette" % [mi.name, i])
			if mat == null:
				continue
			assert_true((mat.get_shader_parameter(&"glow") as Color).is_equal_approx(glow), "in its colour")
			if mat.get_shader_parameter(&"tex_albedo") is Texture2D:
				detailed += 1
	assert_true(detailed > 0, "its surfaces keep their own maps under the glow (cloth, seams: the PC's pass 3)")
	assert_eq(float((npc.tuning["glance"] as Dictionary)["radius_m"]), 0.0, "the row's tuning is merged")
	_done()


## The PC's pass 3: freeing the storm figure logged "material is null" (a cached material outlived it). Its silhouette
## materials now belong to its meshes alone: once the figure is freed, nothing holds them.
func test_a_freed_silhouette_leaves_no_material_behind() -> void:
	var zone := _greybox_zone(["figure"])
	var layer := _layer(
		zone,
		[
			{
				"npc_id": "storm_figure_free",
				"body": "crowd_man_lean_a",
				"silhouette": "#5fd6e0",
				"stand_in": "CutsceneStage/Actors/figure",
				"attach": "child"
			}
		]
	)
	layer.build()
	var refs := _override_refs(layer.villager(&"storm_figure_free").actor)
	assert_true(refs.size() > 0, "the figure wore silhouette materials")
	_done()  # frees the zone, the figure and its meshes
	var alive := 0
	for r in refs:
		if r.get_ref() != null:
			alive += 1
	assert_eq(alive, 0, "no silhouette material outlives the figure")


## Weak references to every surface override under `actor`, gathered in a function of their own: GDScript keeps an
## expression's last value in a stack slot until its function returns, which would hold one material alive.
func _override_refs(actor: Node) -> Array[WeakRef]:
	var refs: Array[WeakRef] = []
	for node: Node in actor.find_children("*", "MeshInstance3D", true, false):
		var mi := node as MeshInstance3D
		for i in mi.mesh.get_surface_count():
			refs.append(weakref(mi.get_surface_override_material(i)))
	return refs


## M3-HER-1142: the real Corrow zone's storm figure is a body, not a capsule, once its layer is built.
func test_the_corrow_storm_figure_is_a_silhouette_in_the_real_zone() -> void:
	var zone := (load(CORROW) as PackedScene).instantiate() as Node3D
	_holder().add_child(zone)
	var layer := VillagerLayer.wire(zone, &"ch08/corrow")
	layer.build()
	var figure := zone.get_node_or_null(^"CutsceneStage/Actors/figure")
	assert_true(figure != null, "the figure's stage actor")
	var npc := layer.villager(&"corrow_storm_figure")
	assert_true(npc != null and npc.get_parent() == figure and npc.actor != null, "a body rides inside it")
	if figure != null:
		var capsule := figure.get_node_or_null(^"StandIn") as Node3D
		assert_true(capsule == null or not capsule.visible, "its capsule is hidden")
	_done()


## big17 (test_zone_cast): two crowd people at the same work start their work loop at their own phase, as the idle
## does, so Tamsule's fisher and boatman never haul in step.
func test_two_people_at_the_same_work_are_out_of_step() -> void:
	var zone := _greybox_zone(["fisher", "boatman"])
	var layer := _layer(
		zone,
		[
			{
				"npc_id": "tamsule_fisher",
				"crowd": "tamsule_fisher",
				"stand_in": "CutsceneStage/Actors/fisher",
				"attach": "child"
			},
			{
				"npc_id": "tamsule_boatman",
				"crowd": "tamsule_boatman",
				"stand_in": "CutsceneStage/Actors/boatman",
				"attach": "child"
			}
		]
	)
	assert_eq(layer.build(), 2)
	var a := layer.villager(&"tamsule_fisher")
	var b := layer.villager(&"tamsule_boatman")
	for i in 30:
		a.tick(DT)
		b.tick(DT)
	assert_true(a.working() and b.working(), "both at rest at their work")
	assert_eq(a.current_clip, b.current_clip, "the same work clip")
	var length := a.anim.get_animation(a.current_clip).length
	var gap := absf(a.anim.current_animation_position - b.anim.current_animation_position)
	assert_true(minf(gap, length - gap) > 0.05, "out of step (%.3f s apart)" % gap)
	_done()
