extends TestCase
## M2-FP-102: Haluna's villagers wear their M2-CHR-03 actors and live as FieldNpcs (M3-CRE-610) instead
## of standing as capsules; a talk starts on the villager's Interactable and ends with the bark.

const ZONE := "res://game/levels/ch02/haluna/haluna.tscn"
const DT := 1.0 / 60.0
const SETTLE_FRAMES := 30
## The rows with a body of their own (stand_in_for rows wear another's model).
const OWN_MODELS: Array[StringName] = [&"vendor", &"reed", &"netmender", &"fisher", &"child", &"neme", &"osu"]

var zone: HalunaZone
var saved_flags: Dictionary


func before_each() -> void:
	saved_flags = Game.state.flags.duplicate(true)


func _load() -> void:
	zone = (load(ZONE) as PackedScene).instantiate() as HalunaZone
	zone.prebuild()
	_host().add_child(zone)
	zone.director.auto_update = false
	zone.player.set_physics_process(false)
	zone.player.set_process_unhandled_input(false)


func _host() -> Node:
	var tree := Engine.get_main_loop() as SceneTree
	return tree.current_scene if tree.current_scene != null else tree.root


func _done() -> void:
	if zone != null:
		_host().remove_child(zone)
		zone.free()
		zone = null
	Game.state.flags = saved_flags


func _npcs() -> Array[FieldNpc]:
	var out: Array[FieldNpc] = []
	for n: Node in zone.find_children(HalunaVillagers.NODE_NAME, "", true, false):
		if n is FieldNpc:
			out.append(n as FieldNpc)
	return out


func test_every_row_has_a_live_villager_and_no_capsule_shows() -> void:
	_load()
	var rows: Array = HalunaVillagers.load_data().get(HalunaVillagers.KEY_ROWS, [])
	var npcs := _npcs()
	assert_eq(npcs.size(), rows.size(), "one FieldNpc per row")
	var ids: Array[StringName] = []
	for npc in npcs:
		ids.append(npc.npc_id)
		assert_true(npc.actor != null, "%s wears an actor" % npc.npc_id)
		assert_true(npc.anim != null and npc.anim.has_animation(&"idle"), "%s has an idle clip" % npc.npc_id)
		var body := npc.get_parent() as Node3D
		for path: String in ["StandIn", "Facing"]:
			var mesh := body.get_node_or_null(path) as Node3D
			assert_true(mesh == null or not mesh.visible, "%s's %s capsule is hidden" % [npc.npc_id, path])
		assert_true(body is StaticBody3D, "%s keeps its collision body" % npc.npc_id)
	for id in OWN_MODELS:
		assert_true(id in ids, "%s is in the village" % id)
	_done()


func test_villagers_idle_out_of_step() -> void:
	_load()
	for i in SETTLE_FRAMES:
		for npc in _npcs():
			npc.tick(DT)
	var phases := {}
	for npc in _npcs():
		phases[snappedf(npc.idle_phase(), 0.01)] = true
	assert_true(phases.size() > 1, "the villagers don't breathe in step")
	_done()


func test_a_talk_starts_on_the_villager_and_ends_with_the_bark() -> void:
	_load()
	var vendor: FieldNpc = null
	for npc in _npcs():
		if npc.npc_id == &"vendor":
			vendor = npc
	assert_true(vendor != null)
	var talk := zone.get_node(^"NPCs/Market/Talk") as Interactable
	talk.used.emit(talk)
	assert_true(vendor.is_talking(), "using the market Interactable starts the vendor's talk")
	HalunaVillagers.end_talks(zone)
	assert_false(vendor.is_talking(), "the bark's end ends it")
	_done()


func test_night_still_sends_the_dock_home() -> void:
	_load()
	zone.set_night({}, ["NPCs/Dock"])
	for npc in _npcs():
		assert_false(npc.npc_id in [&"netmender", &"fisher"], "%s has gone home for the night" % npc.npc_id)
	_done()


## M2-FP-106: a line spoken by a villager who is no stage actor (Neme at her table) turns that FieldNpc to
## Rhen and plays its talk for the scene; the scene's end lets it go.
func test_a_villagers_line_turns_her_to_rhen_for_the_scene() -> void:
	_load()
	var neme: FieldNpc = null
	for npc in _npcs():
		if npc.npc_id == &"neme":
			neme = npc
	assert_true(neme != null, "Neme is a FieldNpc")
	var seq := CutsceneSequencer.new()
	seq.instant = true
	zone.add_child(seq)
	var during: Array[bool] = []
	seq.line_shown.connect(func(_s: DialogueStep) -> void: during.append(neme.is_talking()))
	await seq.play(&"ch02_nemes_table", zone.stage)
	assert_true(during.size() > 1 and during[1], "she is talking by her second line")
	assert_false(neme.is_talking(), "the scene's end lets her go")
	seq.free()
	_done()
