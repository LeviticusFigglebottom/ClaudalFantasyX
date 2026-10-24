extends TestCase
## M2-FP-15: B11, Haluna's dock at night. After the Drownbell an arrival lights the night stand-in,
## puts Rhen and the cast on the dock, plays the scene (Toma walks up mid-scene), swears Rhen in and
## hands off to the end card. Once sworn, the villagers' barks are their night blessings.

const ZONE := "res://game/levels/ch02/haluna/haluna.tscn"
const END_CARD := "res://game/flow/end_card.tscn"

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
	var noon := sun.light_energy
	var shared_env := (zone.mood.find_children("*", "WorldEnvironment", true, false)[0] as WorldEnvironment).environment
	var shared_ambient := shared_env.ambient_light_energy
	story.begin()
	assert_true(zone.is_night)
	assert_true(sun.light_energy < noon, "the sun is dimmed")
	assert_eq(shared_env.ambient_light_energy, shared_ambient, "the shared Environment resource is untouched")
	assert_true(zone.get_node_or_null("NightLamps") != null and zone.get_node("NightLamps").get_child_count() > 0)
	assert_true(zone.get_node_or_null("NPCs/Dock") == null, "the dock villagers have gone home")
	var dock := zone.spawn_marker(&"DockNight")
	assert_true(zone.player.global_position.distance_to(dock.global_position) < 0.5, "Rhen on the dock")
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
