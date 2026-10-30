extends TestCase
## M2-FP-15: B11, Haluna's dock at night. After the Drownbell an arrival puts the world in its night mood,
## puts Rhen and the cast on the dock, plays the scene (Toma walks up mid-scene), swears Rhen in and
## hands off to the end card. Once sworn, the villagers' barks are their night blessings.

const ZONE := "res://game/levels/ch02/haluna/haluna.tscn"
## B11 goes on into Ch4 through its chapter card (M3-CIN-1233), no longer the demo end card.
const END_CARD := "res://game/flow/chapter_card.tscn"

var zone: HalunaZone
var story: HalunaStory
var saved_state: GameStateData
var hand_offs: Array[Array] = []
var lines: Array[StringName] = []


func before_each() -> void:
	saved_state = Game.state
	Game.state = GameStateData.new()
	for f: StringName in [&"ch02_met_asha", &"ch02_tideline_won", &"ch02_ate_at_nemes", &"ch02_saved_once"]:
		Game.set_flag(f, true)
	zone = (load(ZONE) as PackedScene).instantiate() as HalunaZone
	story = zone.get_node("Story") as HalunaStory
	story.autostart = false
	_host().add_child(zone)
	zone.director.auto_update = false
	zone.player.set_physics_process(false)
	story.active = true
	story.sequencer.instant = true
	story.overhear.instant = true
	story.sequencer.line_shown.connect(func(s: DialogueStep) -> void: lines.append(s.speaker))
	story.hand_off = func(kind: StringName, target: String) -> void: hand_offs.append([kind, target])


func test_no_night_before_the_drownbell() -> void:
	story.begin()
	assert_false(zone.is_night)
	assert_eq(lines, [] as Array[StringName])
	_done()


func test_the_dock_at_night_swears_rhen_in_then_the_end_card() -> void:
	Game.set_flag(&"ch03_drownbell_defeated", true)
	var sun := zone.mood.get(&"sun") as DirectionalLight3D
	var moon := zone.mood.get(&"moon") as DirectionalLight3D
	var water := zone.mood.get(&"water") as WaterSurface
	var day_water := water.material
	var day_deep: Variant = day_water.get_shader_parameter(&"col_deep")
	story.begin()
	assert_true(zone.is_night)
	assert_eq(zone.mood.get(&"mood"), &"night", "the world's own night mood (M2-ENV-02)")
	assert_false(sun.visible, "no sun")
	assert_true(moon.visible, "the moon")
	assert_between(water.sea_glow_energy, 0.12 - 0.001, 0.12 + 0.001, "sea-glow 0.12")
	assert_eq(day_water.get_shader_parameter(&"col_deep"), day_deep, "the shared sea material is untouched")
	var houses := (zone.mood.get(&"dresser") as HalunaDresser).night_lamps()
	assert_true(houses != null and houses.visible and houses.get_child_count() > 0, "the oil lamps are lit")
	assert_true(zone.get_node_or_null("NightLamps") != null and zone.get_node("NightLamps").get_child_count() > 0)
	var dock := zone.get_node_or_null("NPCs/Dock") as Node3D
	assert_true(dock == null or not dock.is_visible_in_tree(), "the dock villagers have gone home")
	assert_true(dock == null or not dock.can_process(), "and stopped (their talk prompts too)")
	# M2-FP-115: he has walked out from the DockNight spawn to Asha at the dock end.
	var by_asha := zone.stage.mark(&"rhen_by_asha")
	assert_true(by_asha != null, "the night's mark beside Asha")
	assert_true(zone.player.global_position.distance_to(by_asha.global_position) < 0.5, "Rhen beside Asha")
	var asha := zone.stage.actor(&"asha")
	assert_true(asha.visible and asha.global_position.distance_to(Vector3(20.6, 1.4, 41.3)) < 0.1, "Asha at the end")
	var toma := zone.stage.actor(&"toma")
	var mark := zone.stage.mark(&"dock_toma")
	assert_true(mark != null and toma.global_position.distance_to(mark.global_position) < 0.05, "Toma walked up")
	assert_true(&"asha" in lines and &"toma" in lines and &"rhen" in lines)
	assert_true(bool(Game.get_flag(&"ch03_rhen_sworn_guardian")), "sworn")
	assert_eq(hand_offs, [[StringName(HalunaStory.KEY_CUTSCENE), END_CARD]] as Array[Array])
	speakers_reset()
	story.busy = false
	story.begin()
	assert_eq(lines, [] as Array[StringName], "only once")
	_done()


func test_asking_on_the_steps_adds_her_tell() -> void:
	Game.set_flag(&"ch03_drownbell_defeated", true)
	story.begin()
	var plain := lines.size()
	_done()
	before_each()
	Game.set_flag(&"ch03_drownbell_defeated", true)
	Game.set_flag(&"ch03_rhen_asked_after", true)
	story.begin()
	assert_eq(lines.size(), plain + 3, "Rhen almost asks; Asha asks about his day")
	_done()


func test_once_sworn_the_barks_are_blessings() -> void:
	Game.set_flag(&"ch03_rhen_sworn_guardian", true)
	var scenes: Array[StringName] = []
	story.sequencer.cue_played.connect(func(_c: StringName, _a: Array, _k: Dictionary) -> void: pass)
	story.sequencer.finished.connect(func(id: StringName) -> void: scenes.append(id))
	for id: StringName in [&"npc_market", &"npc_chapel", &"npc_dock", &"npc_lane"]:
		for n in zone.find_children("*", "Interactable", true, false):
			if (n as Interactable).id == id:
				(n as Interactable).try_interact()
	assert_eq(
		scenes,
		(
			[&"ch03_bark_market_night", &"ch03_bark_chapel_night", &"ch03_bark_dock_night", &"ch03_bark_lane_night"]
			as Array[StringName]
		)
	)
	_done()


func speakers_reset() -> void:
	lines.clear()


func _done() -> void:
	if zone != null and is_instance_valid(zone):
		_host().remove_child(zone)
		zone.free()
	zone = null
	lines.clear()
	hand_offs.clear()
	Game.state = saved_state


func _host() -> Node:
	return (Engine.get_main_loop() as SceneTree).current_scene
