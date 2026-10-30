extends TestCase
## M3-CRE-613: the villagers' routines and the VillagerLayer. The head (NpcLook) eases without snapping or
## overshoot and stays within reach; a villager glances at a party that comes near, but not behind itself;
## a chat pair faces each other and takes turns (never both talking), in bouts; a worker looks down at its
## work and up now and then; a storm sends a villager to its shelter, braced with looks at the sky, and home
## again after; a talk ends when the player gets control back; the layer turns a zone's stand-ins into
## villagers (placeholders hidden, talk wired, bodies riding along, the storm flag obeyed); and Haluna's
## data resolves in the real zone.

const FISHER := "res://assets/characters/villagers/fisher/fisher_actor.tscn"
const NETMENDER := "res://assets/characters/villagers/netmender/netmender_actor.tscn"
const STAGE_DATA := "res://game/levels/_tests/npc/villager_layer_stage.json"
const ADOPT_DATA := "res://game/levels/_tests/npc/villager_layer_adopt.json"
const HALUNA := "res://game/levels/ch02/haluna/haluna.tscn"
const KELL := "res://assets/characters/villagers/kell/kell_actor.tscn"
const ORUVEL := "res://game/levels/ch01/oruvel/oruvel.tscn"
const DT := 1.0 / 60.0
const STORM_FLAG := &"ch01_gulls_cried"

var made: Array[Node] = []


func _near(actual: float, expected: float, tol: float, msg: String) -> void:
	assert_between(actual, expected - tol, expected + tol, msg)


func _holder() -> Node3D:
	var h := Node3D.new()
	var tree := Engine.get_main_loop() as SceneTree
	(tree.current_scene if tree.current_scene != null else tree.root).add_child(h)
	made.append(h)
	return h


func _npc(id: StringName, at: Vector3 = Vector3.ZERO, yaw: float = 0.0, scene: String = FISHER) -> FieldNpc:
	var n := FieldNpc.new()
	n.name = String(id).capitalize()
	n.npc_id = id
	n.auto_process = false
	n.actor_scene = load(scene) as PackedScene
	n.position = at
	n.rotation.y = yaw
	_holder().add_child(n)
	return n


func _player(at: Vector3) -> Node3D:
	var p := Node3D.new()
	p.name = &"StandInPlayer"
	_holder().add_child(p)
	p.global_position = at
	return p


func _run(npcs: Array, sec: float) -> void:
	for i in roundi(sec / DT):
		for n: FieldNpc in npcs:
			n.tick(DT)


func _done() -> void:
	for n in made:
		if is_instance_valid(n):
			n.get_parent().remove_child(n)
			n.free()
	made.clear()


func test_the_head_eases_within_its_reach_and_never_snaps() -> void:
	var tuning := FieldNpc.tuning_for(&"fisher")["look"] as Dictionary
	var look := NpcLook.new(tuning)
	look.look(deg_to_rad(60.0), deg_to_rad(10.0))
	var cap := deg_to_rad(float(tuning["max_rate_deg_per_sec"])) * DT + 0.0001
	var peak := 0.0
	for i in roundi(3.0 / DT):
		var before := look.yaw
		look.advance(DT)
		assert_true(absf(look.yaw - before) <= cap, "frame %d stays under the rate cap" % i)
		peak = maxf(peak, look.yaw)
	_near(look.yaw, deg_to_rad(60.0), 0.01, "it settles on the target")
	assert_true(peak <= deg_to_rad(60.0) + 0.002, "without overshoot")
	look.look(deg_to_rad(170.0), deg_to_rad(80.0))
	_near(look.target_yaw, deg_to_rad(float(tuning["max_yaw_deg"])), 0.0001, "the yaw is clamped")
	_near(look.target_pitch, deg_to_rad(float(tuning["max_pitch_up_deg"])), 0.0001, "so is the pitch")
	assert_false(look.can_reach(deg_to_rad(150.0)), "it can't look behind itself")
	look.free()


func test_a_villager_glances_at_a_party_that_comes_near() -> void:
	var n := _npc(&"neme")
	assert_true(n.look != null, "the villager has a head")
	var p := _player(Vector3(30.0, 0.0, 0.0))
	n.player = p
	_run([n], 1.0)
	_near(n.look.yaw, 0.0, deg_to_rad(50.0), "far away: no glance at the party")
	# Ahead and to the left (the villager faces -Z; its left is -X).
	p.global_position = Vector3(-2.5, 0.0, -3.5)
	_run([n], 1.0)
	assert_true(n.look.yaw > deg_to_rad(20.0), "it glances to its left at the party (%.1f)" % rad_to_deg(n.look.yaw))
	_near(n.yaw(), 0.0, 0.0001, "only the head turns: the party is outside face_radius_m")
	var hold := (FieldNpc.tuning_for(&"neme")["glance"] as Dictionary)["hold_sec"] as Array
	_run([n], float(hold[1]) + 1.0)
	assert_true(n.look.target_yaw < deg_to_rad(20.0), "after the hold it looks away again")
	_done()


func test_no_glance_behind_its_back() -> void:
	var n := _npc(&"neme")
	n.player = _player(Vector3(0.3, 0.0, 3.0))
	n._look_next = 1e9  # no look-around in this test
	_run([n], 1.5)
	_near(n.look.target_yaw, 0.0, 0.0001, "a party behind it is out of the head's reach")
	_done()


func test_a_chat_pair_faces_each_other_and_takes_turns() -> void:
	var a := _npc(&"fisher", Vector3(0.0, 0.0, 0.0), PI * 0.5)
	var b := _npc(&"netmender", Vector3(2.0, 0.0, 0.0), 0.0, NETMENDER)
	a.partner = b
	b.partner = a
	var talking := {}
	var both := 0
	var faced := false
	for i in roundi(20.0 / DT):
		a.tick(DT)
		b.tick(DT)
		var a_talks := a.current_clip == &"talk"
		var b_talks := b.current_clip == &"talk"
		if a.chat_speaking() != a_talks or b.chat_speaking() != b_talks:
			fail("chat_speaking() disagrees with the talk clip at frame %d" % i)
			break
		if a_talks and b_talks:
			both += 1
		if a_talks:
			talking[&"fisher"] = true
		if b_talks:
			talking[&"netmender"] = true
		if absf(angle_difference(a.yaw(), HeroLocomotion.yaw_of(Vector3(1, 0, 0)))) < 0.02:
			faced = true
	assert_true(faced, "the fisher turns to face the netmender")
	assert_eq(both, 0, "never both talking at once")
	assert_eq(talking.size(), 2, "each takes a turn")
	_done()


func test_a_chat_pair_goes_back_to_work_between_bouts() -> void:
	var a := _npc(&"fisher", Vector3(0.0, 0.0, 0.0), 0.0)
	var b := _npc(&"netmender", Vector3(2.0, 0.0, 0.0), 0.0, NETMENDER)
	a.partner = b
	b.partner = a
	var chat_frames := 0
	var quiet_frames := 0
	var back_to_rest := false
	for i in roundi(60.0 / DT):
		a.tick(DT)
		b.tick(DT)
		if b.chatting():
			chat_frames += 1
		else:
			quiet_frames += 1
			if quiet_frames > 120 and absf(angle_difference(b.yaw(), b.rest_yaw)) < 0.02:
				back_to_rest = true
	assert_true(chat_frames > 0 and quiet_frames > 0, "bouts of chat and of quiet")
	assert_true(back_to_rest, "in the quiet the netmender turns back to its own work")
	_done()


func test_a_worker_looks_down_at_its_work_and_up_now_and_then() -> void:
	var n := _npc(&"netmender", Vector3.ZERO, 0.0, NETMENDER)
	assert_true(n.working(), "the netmender works at rest")
	var down := 0
	var up := 0
	for i in roundi(20.0 / DT):
		n.tick(DT)
		if n.look.target_pitch < deg_to_rad(-20.0):
			down += 1
		elif absf(n.look.target_pitch) < 0.01:
			up += 1
	assert_true(down > up, "mostly head down on the work (%d down, %d up)" % [down, up])
	assert_true(up > 0, "and a look up now and then")
	_done()


func test_a_storm_sends_a_villager_to_shelter_and_home_again() -> void:
	var n := _npc(&"fisher")
	var shelter := Marker3D.new()
	_holder().add_child(shelter)
	shelter.global_position = Vector3(3.0, 0.0, -2.0)
	shelter.global_rotation.y = PI
	n.shelter = shelter
	FieldNpc.set_storm_all(n.get_tree(), true)
	assert_true(n.storm, "set_storm_all reaches it")
	var fastest := 0.0
	var sky := false
	var brace := false
	for i in roundi(14.0 / DT):
		n.tick(DT)
		fastest = maxf(fastest, n.ground_speed)
		sky = sky or n.look.target_pitch > deg_to_rad(10.0)
		brace = brace or n.look.target_pitch < deg_to_rad(-5.0)
	assert_true(n.position.distance_to(Vector3(3.0, 0.0, -2.0)) < 0.1, "it reached the shelter")
	assert_true(fastest > float(n.tuning["walk_speed_mps"]), "hurrying (%.2f m/s)" % fastest)
	_near(angle_difference(n.yaw(), PI), 0.0, 0.05, "it rests facing the shelter's way")
	assert_true(sky and brace, "braced, with looks up at the sky")
	n.set_storm(false)
	_run([n], 14.0)
	assert_true(n.position.distance_to(Vector3.ZERO) < 0.1, "after the storm it walks home")
	_near(angle_difference(n.yaw(), 0.0), 0.0, 0.05, "and faces its old heading")
	_done()


func test_a_talk_ends_when_the_player_gets_control_back() -> void:
	var n := _npc(&"osu")
	var p := FieldController.new()
	_holder().add_child(p)
	p.set_physics_process(false)
	p.global_position = Vector3(0.0, 0.0, -1.2)
	n.begin_talk(p)
	p.accepts_input = false
	_run([n], 2.0)
	assert_true(n.is_talking(), "talking while the dialogue holds the player")
	p.accepts_input = true
	n.tick(DT)
	assert_false(n.is_talking(), "control back: the talk is over")
	n.begin_talk(p)
	_run([n], float(n.tuning["talk_unheld_sec"]) + 0.1)
	assert_false(n.is_talking(), "a bark that never held the player ends after talk_unheld_sec")
	_done()


func _stage() -> Node3D:
	var zone := _holder()
	var group := Node3D.new()
	group.name = &"NPCs"
	zone.add_child(group)
	var body := StaticBody3D.new()
	body.name = &"Walker"
	group.add_child(body)
	body.position = Vector3(1.0, 0.0, 0.0)
	for part: String in ["StandIn", "Facing", "Prop"]:
		var m := MeshInstance3D.new()
		m.name = part
		body.add_child(m)
	var talk := Interactable.new()
	talk.name = &"Talk"
	talk.id = &"test_villager_layer"
	group.add_child(talk)
	talk.position = Vector3(1.0, 1.0, 0.5)
	var other := StaticBody3D.new()
	other.name = &"Sitter"
	group.add_child(other)
	other.position = Vector3(-1.0, 0.0, 0.0)
	return zone


func test_the_layer_turns_stand_ins_into_villagers() -> void:
	var was: Variant = Game.get_flag(STORM_FLAG)  # an earlier test may leave the story flag set: a storm stops the walk
	Game.set_flag(STORM_FLAG, false)
	var zone := _stage()
	var layer := VillagerLayer.new()
	layer.data_path = STAGE_DATA
	layer.auto_build = false
	zone.add_child(layer)
	assert_eq(layer.build(), 2, "both rows placed")
	var walker := layer.villager(&"child")
	var body := zone.get_node("NPCs/Walker") as Node3D
	assert_eq(walker.get_parent(), body.get_parent(), "the villager sits beside its stand-in")
	assert_false((body.get_node("StandIn") as Node3D).visible, "the placeholder is hidden")
	assert_false((body.get_node("Prop") as Node3D).visible, "so are the listed props")
	assert_eq(layer.villager(&"neme").partner, null, "no partner unless the row names one")
	var talk := zone.get_node("NPCs/Talk") as Interactable
	walker.player = _player(Vector3(1.0, 0.0, -1.0))
	assert_true(talk.try_interact(), "the zone's talk spot fires")
	assert_true(walker.is_talking(), "and starts the villager's talk")
	walker.end_talk()
	walker.player.global_position = Vector3(50.0, 0.0, 50.0)
	var offset := talk.global_position - body.global_position
	for i in roundi(12.0 / DT):
		layer.tick(DT)
	assert_true(body.position.distance_to(Vector3(1.0, 0.0, 0.0)) > 0.5, "the body walked with the villager")
	_near(body.global_position.distance_to(walker.global_position), 0.0, 0.001, "on its feet")
	_near((talk.global_position - body.global_position).length(), offset.length(), 0.001, "the talk spot rides along")
	Game.set_flag(STORM_FLAG, was)
	_done()


func test_the_layer_follows_the_storm_flag() -> void:
	var was: Variant = Game.get_flag(STORM_FLAG)
	Game.set_flag(STORM_FLAG, false)
	var zone := _stage()
	var layer := VillagerLayer.new()
	layer.data_path = STAGE_DATA
	layer.auto_build = false
	zone.add_child(layer)
	layer.build()
	layer.tick(DT)
	assert_false(layer.villager(&"neme").storm, "calm while the flag is unset")
	Game.set_flag(STORM_FLAG, true)
	layer.tick(DT)
	assert_true(layer.villager(&"neme").storm, "the flag brings the storm")
	Game.set_flag(STORM_FLAG, was)
	_done()


func test_halunas_rows_resolve_in_the_zone() -> void:
	var data := VillagerLayer.load_data(VillagerLayer.path_for(&"ch02/haluna"))
	var rows: Array = data["villagers"]
	var zone := (load(HALUNA) as PackedScene).instantiate() as Node3D
	var layer := VillagerLayer.new()
	layer.zone_id = &"ch02/haluna"
	layer.auto_build = false
	zone.add_child(layer)
	_holder().add_child(zone)
	assert_eq(layer.build(), rows.size(), "every Haluna row finds its stand-in and its body")
	for row: Dictionary in rows:
		var stand_in := zone.get_node(NodePath(str(row["stand_in"])))
		var capsule := stand_in.get_node_or_null("StandIn") as Node3D  # Haluna's are gone from the scene (M3-ENV-748)
		assert_true(capsule == null or not capsule.visible, "%s's capsule is hidden" % row["npc_id"])
		if row.has("talk"):
			assert_true(zone.get_node_or_null(NodePath(str(row["talk"]))) is Interactable, "talk spot exists")
	assert_eq(layer.villager(&"fisher").partner, layer.villager(&"netmender"), "the dock pair chats")
	_done()


func test_wake_villagers_ride_inside_their_cutscene_actors() -> void:
	var zone := (load("res://game/levels/ch04/haluna_wake/haluna_wake.tscn") as PackedScene).instantiate() as Node3D
	_holder().add_child(zone)
	var layer := VillagerLayer.new()
	layer.zone_id = &"ch04/haluna_wake"
	layer.auto_build = false
	zone.add_child(layer)
	assert_eq(layer.build(), 7, "the seven Haluna villagers")
	var osu := layer.villager(&"osu")
	var actor := zone.get_node("CutsceneStage/Actors/osu") as Node3D
	assert_eq(osu.get_parent(), actor, "inside the cutscene actor")
	assert_false((actor.get_node("StandIn") as Node3D).visible, "its capsule is hidden")
	assert_eq(osu.route.size(), 0, "no route inside an actor")
	var staged := actor.global_rotation.y
	for i in roundi(4.0 / DT):
		layer.tick(DT)
	assert_false(osu.chatting(), "no chat at the wake: cinematics stages them facing the wall (M3-CIN-1220)")
	_near(absf(angle_difference(osu.global_rotation.y, staged)), 0.0, 0.05, "she keeps the facing her actor gives her")
	actor.position += Vector3(2.0, 0.0, 0.0)  # a cutscene moves the actor
	layer.tick(DT)
	_near(osu.global_position.distance_to(actor.global_position), 0.0, 0.001, "the villager goes with it")
	actor.visible = false  # a zone state hides the actor
	assert_false(osu.is_visible_in_tree(), "and its villager")
	assert_true(osu.partner == null, "no chat partner at the wake")
	_done()


func test_the_layer_adopts_villagers_a_zone_placed_itself() -> void:
	var zone := _stage()
	# What a zone's own wiring does (Haluna's HalunaVillagers): a FieldNpc inside each body.
	for body_name: String in ["Walker", "Sitter"]:
		var placed := FieldNpc.new()
		placed.name = &"Villager"
		placed.npc_id = &"child" if body_name == "Walker" else &"neme"
		placed.auto_process = false
		placed.actor_scene = load(FISHER) as PackedScene
		zone.get_node("NPCs/" + body_name).add_child(placed)
	var layer := VillagerLayer.new()
	layer.data_path = ADOPT_DATA
	layer.auto_build = false
	zone.add_child(layer)
	assert_eq(layer.build(), 2, "both rows found their villager")
	var walker := zone.get_node("NPCs/Walker")
	assert_eq(walker.find_children("*", "FieldNpc", false, false).size(), 1, "adopted, not doubled")
	assert_eq(walker.get_parent().find_children("*Villager", "FieldNpc", false, false).size(), 0, "none beside it")
	assert_eq(layer.villager(&"child"), walker.get_node("Villager"), "the zone's own villager")
	assert_eq(layer.villager(&"child").partner, layer.villager(&"neme"), "the layer wires the chat pair")
	_done()


## The big11 gate's teardown errors ("Trying to cast a freed object"): a zone's teardown can free its villagers and
## their riders before the layer that drives them. The layer must skip them; the runner fails this test on any
## script error.
func test_the_layer_survives_its_villagers_being_freed_first() -> void:
	var zone := _stage()
	var layer := VillagerLayer.new()
	layer.data_path = STAGE_DATA
	layer.auto_build = false
	zone.add_child(layer)
	layer.build()
	var walker := layer.villager(&"child")
	var mate := layer.villager(&"neme")
	walker.partner = mate
	mate.partner = walker
	zone.get_node("NPCs/Talk").free()  # a rider goes first
	layer.tick(DT)
	walker.get_parent().remove_child(walker)
	walker.free()  # then a villager, with its partner still standing
	layer.tick(DT)
	mate.tick(DT)
	layer.set_storm(true)
	assert_eq(layer.villager(&"child"), null, "a freed villager is simply gone")
	assert_eq(layer.live_villagers().size(), 1, "the other one stays")
	assert_false(mate.chatting(), "and it stops chatting with nobody")
	_done()


## M3-CRE-100: a row's `actor` dresses it in another villager's model; its own id stays for talk and tuning.
func test_a_row_can_wear_another_villagers_model() -> void:
	var data := VillagerLayer.load_data(STAGE_DATA)
	(data["villagers"] as Array)[1]["actor"] = "fisher"
	var path := "user://villager_layer_actor_test.json"
	var f := FileAccess.open(path, FileAccess.WRITE)
	f.store_string(JSON.stringify(data))
	f.close()
	var zone := _stage()
	var layer := VillagerLayer.new()
	layer.data_path = path
	layer.auto_build = false
	zone.add_child(layer)
	layer.build()
	var neme := layer.villager(&"neme")
	assert_true(neme != null, "the row keeps its own id")
	assert_eq(neme.actor_scene.resource_path, FISHER, "and wears the fisher's model")
	DirAccess.remove_absolute(ProjectSettings.globalize_path(path))
	_done()


## M3-CRE-100: Haluna adds its layer in its own _ready, then HalunaVillagers places the shop bodies' villagers. The
## layer builds at once (no capsule before the first frame, big14 gate) and puts the shop rows inside their bodies as
## `Villager`, so populate skips them: each villager shows once (not one from each system).
func test_a_layer_added_in_the_zones_ready_adopts_what_the_zone_places_after() -> void:
	var zone := (load(HALUNA) as PackedScene).instantiate() as Node3D
	_holder().add_child(zone)  # not prebuilt: the zone adds its VillagerLayer in its _ready, then places the shop bodies
	var layer := zone.get_node(^"VillagerLayer") as VillagerLayer
	assert_false(layer.villagers.is_empty(), "added in the zone's _ready, the layer builds at once")
	for n in zone.get_node(^"NPCs").find_children("StandIn", "GeometryInstance3D", true, false):
		assert_false((n as GeometryInstance3D).is_visible_in_tree(), "%s shows no capsule" % n.get_parent().name)
	var ids: Array[StringName] = []
	for n: Node in zone.find_children("*", "FieldNpc", true, false):
		var id := (n as FieldNpc).npc_id
		assert_false(id in ids, "%s shows once" % id)
		ids.append(id)
	for id: StringName in [&"shopkeeper", &"smith", &"innkeeper", &"vendor"]:
		assert_true(id in ids, "%s is in the village" % id)
	assert_true(layer.villager(&"shopkeeper") != null, "the layer owns the shop rows too (adopted)")
	_done()


## M3-CRE-656: a GreyboxZone stage actor that already wears a villager model (a layout row's `model`, M2-FP-111)
## becomes a FieldNpc carrying that very model, inside the stage actor node the cutscenes find.
func test_a_greybox_actor_model_is_adopted_into_a_villager() -> void:
	var zone := _holder()
	var actors := Node3D.new()
	actors.name = &"Actors"
	var stage := Node3D.new()
	stage.name = &"CutsceneStage"
	zone.add_child(stage)
	stage.add_child(actors)
	var kell := Node3D.new()
	kell.name = &"kell"
	actors.add_child(kell)
	var model := (load(KELL) as PackedScene).instantiate() as Node3D
	model.name = &"Model"
	kell.add_child(model)
	var triggers := Node3D.new()
	triggers.name = &"Triggers"
	zone.add_child(triggers)
	var talk := Interactable.new()
	talk.name = &"kell_stall"
	talk.id = &"test_kell_stall"
	triggers.add_child(talk)
	var layer := VillagerLayer.new()
	layer.zone_id = &"ch01/oruvel"
	layer.auto_build = false
	zone.add_child(layer)
	# rows with an `at` (the deck's vignettes, M3-CRE-666) make their own spots; of the rest, only Kell's actor is here
	var spots := 0
	for row: Variant in VillagerLayer.load_data(VillagerLayer.path_for(&"ch01/oruvel"))["villagers"]:
		if (row as Dictionary).has("at"):
			spots += 1
	assert_eq(layer.build(), 1 + spots, "Kell's row finds her stage actor")
	var npc := layer.villager(&"kell")
	assert_true(npc != null and npc.get_parent() == kell, "the villager rides inside the stage actor")
	assert_true(npc.actor == model, "it carries the greybox model itself, not a second one")
	assert_eq(kell.find_children("*", "FieldNpc", true, false).size(), 1, "one villager")
	assert_true(npc.anim != null and npc.anim.has_animation(&"idle"), "the model's clips drive it")
	talk.used.emit(talk)
	assert_true(npc.is_talking(), "her stall's talk spot starts her talk")
	_done()


## M3-CRE-656 in the real Oruvel (a GreyboxZone): wiring a layer after the zone is built adopts Kell's model.
func test_oruvels_kell_comes_alive_in_the_real_zone() -> void:
	var zone := (load(ORUVEL) as PackedScene).instantiate() as Node3D
	_holder().add_child(zone)
	var layer := VillagerLayer.wire(zone, &"ch01/oruvel")
	layer.build()  # the deferred build, made now: the runner steps no frames
	var kell := layer.villager(&"kell")
	assert_true(kell != null, "Kell is a villager")
	assert_true(kell != null and kell.actor != null and kell.actor.name == FieldNpc.ACTOR_NAME, "wearing her model")
	_done()


## ZoneCast (M3-CIN-1217) puts a villager's model on an Act I stage actor as `Cast`: a named villager's row adopts that
## model as it does a greybox `Model`, so one body shows and it lives.
func test_a_zone_cast_model_is_adopted_into_a_villager() -> void:
	var zone := _holder()
	var stage := Node3D.new()
	stage.name = &"CutsceneStage"
	zone.add_child(stage)
	var actors := Node3D.new()
	actors.name = &"Actors"
	stage.add_child(actors)
	var kell := Node3D.new()
	kell.name = &"kell"
	actors.add_child(kell)
	var model := (load(KELL) as PackedScene).instantiate() as Node3D
	model.name = &"Cast"
	kell.add_child(model)
	var layer := VillagerLayer.new()
	layer.zone_id = &"ch01/oruvel"
	layer.auto_build = false
	zone.add_child(layer)
	layer.build()
	var npc := layer.villager(&"kell")
	assert_true(npc != null and npc.actor == model, "the cast model itself, not a second body")
	assert_eq(kell.find_children("*", "AnimationPlayer", true, false).size(), 1, "one body on the actor")
	_done()
