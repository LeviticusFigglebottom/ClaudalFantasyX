extends TestCase
## M2-FP-102/113: Haluna's villagers wear their M2-CHR-03 actors and live as FieldNpcs (M3-CRE-610) instead
## of standing as capsules: creatures' VillagerLayer (M3-CRE-613) owns the seven, HalunaVillagers the three shop
## bodies it doesn't cover yet. A talk starts on the villager's Interactable and ends with the bark.

const ZONE := "res://game/levels/ch02/haluna/haluna.tscn"
const DT := 1.0 / 60.0
const SETTLE_FRAMES := 30
## Every villager the zone must show, once each: VillagerLayer's seven and the three shop bodies.
const VILLAGERS: Array[StringName] = [
	&"vendor", &"reed", &"netmender", &"fisher", &"child", &"neme", &"osu", &"shopkeeper", &"smith", &"innkeeper"
]

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
	for n: Node in zone.find_children("*", "FieldNpc", true, false):
		out.append(n as FieldNpc)
	return out


func test_every_villager_is_alive_once_and_no_capsule_shows() -> void:
	_load()
	var ids: Array[StringName] = []
	for npc in _npcs():
		assert_false(npc.npc_id in ids, "%s appears once, not from two systems" % npc.npc_id)
		ids.append(npc.npc_id)
		assert_true(npc.actor != null, "%s wears an actor" % npc.npc_id)
		assert_true(npc.anim != null and npc.anim.has_animation(&"idle"), "%s has an idle clip" % npc.npc_id)
	for id in VILLAGERS:
		assert_true(id in ids, "%s is in the village" % id)
	for n: Node in zone.get_node(^"NPCs").find_children("StandIn", "MeshInstance3D", true, false):
		assert_false((n as Node3D).visible, "%s's capsule is hidden" % n.get_parent().name)
	assert_eq(zone.find_children("*", "VillagerLayer", true, false).size(), 1, "one VillagerLayer")
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
		if npc.npc_id in [&"netmender", &"fisher"]:
			assert_false(npc.is_visible_in_tree(), "%s has gone home for the night" % npc.npc_id)
			assert_false(npc.can_process(), "%s is stopped" % npc.npc_id)
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


## M2-FP-107: a bark freezes Rhen but keeps Asha and Toma in view (the party's followers hide only for a
## staged scene), and the story's sequencer holds the player again for the next staged one.
func test_a_bark_freezes_rhen_and_keeps_the_party_in_view() -> void:
	_load()
	var story := zone.get_node(^"Story") as HalunaStory
	story.sequencer.instant = true
	var party := zone.player.get_node_or_null(NodePath(String(HeroFieldParty.NAME))) as HeroFieldParty
	assert_true(party != null, "the player has the party's followers")
	party.rescan()
	var hidden: Array[bool] = []
	var frozen: Array[bool] = []
	story.sequencer.line_shown.connect(
		func(_s: DialogueStep) -> void:
			hidden.append(party.should_hide())
			frozen.append(not zone.player.accepts_input)
	)
	await story.call(&"_bark", &"ch02_bark_market")
	assert_false(hidden.is_empty(), "the bark played lines")
	assert_false(true in hidden, "the followers never hid")
	assert_false(false in frozen, "Rhen was frozen for every line")
	assert_true(zone.player.accepts_input, "and walks again after")
	assert_true(story.sequencer.hold_player, "the next staged scene holds the player again")
	_done()


## M2-FP-110: B05 at the causeway head is Asha and Toma talking. It no longer hides them (it isn't staged), and
## their lines play on the followers the player sees, because their stage actors are hidden after Cutscene A.
func test_the_causeway_head_talk_keeps_asha_and_toma_and_they_talk() -> void:
	var saved_party := Game.state.party_ids.duplicate()  # before the flag: its join hook adds Asha and Toma
	Game.set_flag(&"ch02_met_asha")
	Game.state.party_ids.assign([&"rhen", &"asha", &"toma"])
	_load()
	var party := zone.player.get_node(NodePath(String(HeroFieldParty.NAME))) as HeroFieldParty
	party.advance(1.0 / 60.0)  # builds the followers from party_ids
	party.rescan()
	assert_true(CutsceneNpcTalk.follower(zone, &"asha") != null, "Asha follows Rhen")
	var story := zone.get_node(^"Story") as HalunaStory
	story.sequencer.instant = true
	var hidden: Array[bool] = []
	story.sequencer.line_shown.connect(func(_s: DialogueStep) -> void: hidden.append(party.should_hide()))
	await story.call(&"_play_unstaged", &"ch02_low_tide")
	assert_false(hidden.is_empty(), "B05 played lines")
	assert_false(true in hidden, "Asha and Toma stayed in view")
	Game.state.party_ids.assign(saved_party)
	_done()
