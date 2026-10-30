extends TestCase
## M2-FP-13: Haluna's slice beats on the real zone. B02 Neme's table on the first arrival after the
## tideline win, B03's four "Cantor" fragments overheard on walk-past (Rhen keeps walking, nothing
## else is blocked), and B05 Low tide at the causeway head before the Shell Shrine trial.

const ZONE := "res://game/levels/ch02/haluna/haluna.tscn"
const FRAGMENTS := {
	&"overhear_market": &"ch02_bark_market",
	&"overhear_chapel": &"ch02_bark_chapel",
	&"overhear_dock": &"ch02_bark_dock",
	&"overhear_lane": &"ch02_bark_lane",
}
const NEME_SCENE := &"ch02_nemes_table"
const LOW_TIDE := &"ch02_low_tide"

var zone: HalunaZone
var story: HalunaStory
var saved_state: GameStateData
var speakers: Array[StringName] = []
var hand_offs: Array[Array] = []


func before_each() -> void:
	saved_state = Game.state
	Game.state = GameStateData.new()
	zone = (load(ZONE) as PackedScene).instantiate() as HalunaZone
	story = zone.get_node("Story") as HalunaStory
	story.autostart = false
	_host().add_child(zone)
	zone.director.auto_update = false
	zone.player.set_physics_process(false)
	zone.player.set_process_unhandled_input(false)
	story.active = true
	story.sequencer.instant = true
	story.sequencer.line_shown.connect(func(s: DialogueStep) -> void: speakers.append(s.speaker))
	story.hand_off = func(kind: StringName, target: String) -> void: hand_offs.append([kind, target])


func test_the_four_fragments_are_walk_past_triggers_after_the_beach() -> void:
	for id: StringName in FRAGMENTS:
		var t := _interactable(id)
		assert_true(t != null, "trigger %s" % id)
		if t == null:
			continue
		assert_eq(t.activation, Interactable.Activation.TOUCH)
		assert_true(t.once, "%s plays once" % id)
		assert_eq(t.requires_flag, &"ch02_ate_at_nemes", "%s waits for Neme's table (M4-A2P-115 A4)" % id)
		assert_eq(t.sets_flag, t.blocked_by_flag, "%s is heard once, across reloads (A6)" % id)
		assert_eq(t.payload, {"dialogue": String(FRAGMENTS[id]), "overheard": true})
		var runner := DialogueRunner.new(DialogueFlagAccess.new())
		runner.forward_events_to_bus = false
		assert_true(runner.load_scene(FRAGMENTS[id]) and runner.start(), "%s loads" % FRAGMENTS[id])
	var lane := _interactable(&"npc_lane")
	assert_true(
		lane != null and lane.payload == {"dialogue": "ch02_bark_lane_listen"},
		"the lane child also talks (A5: its own bark)"
	)
	_done()


## M4-A2P-115 A4: at dawn, before Neme's table, none of B03's town plays (the fragments, Osu, the causeway rule).
func test_dawn_before_nemes_table_has_no_b03() -> void:
	Game.set_flag(&"ch02_met_asha", true)
	for id: StringName in [&"overhear_market", &"overhear_dock", &"npc_dock", &"npc_osu", &"causeway_head_unsaved"]:
		assert_false(_interactable(id).is_available(), "%s waits for Neme's table" % id)
	_done()


func test_an_overheard_fragment_lets_rhen_walk_on_and_blocks_nothing() -> void:
	Game.set_flag(&"ch02_met_asha", true)
	Game.set_flag(&"ch02_ate_at_nemes", true)
	var market := _interactable(&"overhear_market")
	assert_true(market.on_touched())
	assert_true(story.overhear.is_playing(), "the fragment plays")
	assert_true(zone.player.accepts_input, "Rhen is not stopped")
	assert_false(story.busy, "the story is free")
	assert_false(market.is_available(), "once")
	# Lines advance by themselves on the overhear sequencer.
	var guard := 0
	while story.overhear.is_playing() and guard < 3000:
		guard += 1
		if story.overhear.overlay.box.is_revealing():
			story.overhear.overlay.box.skip_reveal()  # the typewriter runs on the box's own process
		story.overhear.advance(1.0 / 30.0)
	assert_false(story.overhear.is_playing(), "it ends by itself (%d frames)" % guard)
	assert_true(zone.player.accepts_input)
	# A second fragment is cut off when the tideline battle starts.
	assert_true(_interactable(&"overhear_lane").on_touched())
	assert_true(story.overhear.is_playing())
	var battle := _interactable(&"tideline_battle")
	assert_true(battle.on_touched(), "the battle still fires mid-fragment")
	assert_eq(hand_offs, [[StringName(HalunaStory.KEY_BATTLE), "ch02_tideline"]] as Array[Array])
	assert_false(story.overhear.is_playing(), "the fragment was cut off")
	_done()


func test_nemes_table_plays_once_after_the_tideline_win() -> void:
	Game.set_flag(&"ch02_met_asha", true)
	story.begin()
	assert_eq(speakers, [] as Array[StringName], "nothing before the battle is won")
	Game.set_flag(&"ch02_tideline_won", true)
	story.begin()
	assert_true(&"neme" in speakers, "Neme's table played")
	assert_true(bool(Game.get_flag(&"ch02_ate_at_nemes")), "and marked itself played")
	var village := zone.spawn_marker(&"Village")
	assert_true(zone.player.global_position.distance_to(village.global_position) < 0.5, "at Neme's door")
	assert_true(zone.player.accepts_input)
	speakers.clear()
	story.begin()
	assert_eq(speakers, [] as Array[StringName], "only once")
	_done()


func test_low_tide_plays_before_cutscene_b() -> void:
	Game.set_flag(&"ch02_met_asha", true)
	Game.set_flag(&"ch02_saved_once", true)
	assert_true(_interactable(&"causeway_head").on_touched())
	assert_true(&"toma" in speakers and &"asha" in speakers, "Toma and Asha at low tide")
	assert_eq(hand_offs.size(), 1, "then the hand-off")
	assert_eq(hand_offs[0][0], StringName(HalunaStory.KEY_GO))
	assert_eq(hand_offs[0][1], "ch03/saltgrass_causeway", "the Saltgrass Causeway, then the trial (M2-FP-25)")
	_done()


func test_new_speakers_and_lines_exist() -> void:
	var sp := DialogueSpeakers.load_default()
	assert_true(sp.has(&"neme") and sp.has(&"child"))
	for scene: StringName in [NEME_SCENE, LOW_TIDE, &"ch02_bark_lane"]:
		var runner := DialogueRunner.new(DialogueFlagAccess.new())
		runner.forward_events_to_bus = false
		assert_true(runner.load_scene(scene) and runner.start(), "%s compiles and starts" % scene)
	_done()


func _interactable(id: StringName) -> Interactable:
	for n in zone.find_children("*", "Interactable", true, false):
		if (n as Interactable).id == id:
			return n as Interactable
	return null


func _done() -> void:
	if zone != null:
		_host().remove_child(zone)
		zone.free()
	Game.state = saved_state


func _host() -> Node:
	return (Engine.get_main_loop() as SceneTree).current_scene
