extends TestCase
## M3-ARC-01: a data-built greybox zone (GreyboxZone) and its data-driven story (ZoneStory) on the
## two-zone test chapter in game/levels/_tests/zone_story/: the layout builds, the arrival plays once
## and fills the party, a flag-gated trigger opens a battle that returns to the zone, an
## <<event>> steps Rhen back, zone calls and travel hand off, barks swap by flag and an overheard
## bark blocks nothing.

const ZONE_A := "res://game/levels/_tests/zone_story/zone_a.tscn"
const ZONE_B := "res://game/levels/_tests/zone_story/zone_b.tscn"

var zone: GreyboxZone
var story: ZoneStory
var saved_state: GameStateData
var speakers: Array[StringName] = []
var hand_offs: Array[Array] = []


func before_each() -> void:
	saved_state = Game.state
	Game.state = GameStateData.new()
	speakers.clear()
	hand_offs.clear()
	FieldEncounters.return_points.clear()
	_open(ZONE_A)


func test_the_zone_builds_from_its_layout() -> void:
	assert_eq(
		zone.spawn_names(), [&"Start", &"AfterFight", &"Encounter"] as Array[StringName], "plus the encounter return"
	)
	assert_between(zone.spawn_yaw_deg(&"Start"), 179.99, 180.01)
	assert_eq(zone.find_children("*", "Interactable", true, false).size(), 4, "four triggers")
	assert_eq(_trigger(&"gate").payload, {"beat": "gate"})
	assert_eq(_trigger(&"gate").activation, Interactable.Activation.TOUCH)
	assert_eq(_trigger(&"npc_asha").activation, Interactable.Activation.INTERACT)
	assert_true(zone.stage.actor(&"asha") != null, "Asha stands in")
	assert_eq(zone.stage.shot_ids().size(), 2, "two shots")
	assert_true(zone.stage.mark(&"spot") != null)
	var wall := zone.get_node("Greybox/Wall") as StaticBody3D
	assert_true(wall != null and wall.get_node("Shape") is CollisionShape3D, "a solid block collides")
	assert_true(zone.place_at(&"AfterFight", 90.0))
	assert_true(zone.player.position.distance_to(Vector3(4, 0, 2)) < 0.01, "placed on the spawn")
	assert_eq(story.cfg.get("party", {}).get("party", []), ["rhen"], "the story read the test chapter")
	_done()


func test_the_arrival_plays_once_and_fills_the_party() -> void:
	story.begin()
	assert_true(&"asha" in speakers, "the arrival scene played")
	assert_true(bool(Game.get_flag(&"test_flag")), "and set its flag")
	assert_eq(Game.state.party_ids, [&"rhen"] as Array[StringName], "the party joined")
	assert_false(story.busy, "free again")
	speakers.clear()
	story.begin()
	assert_eq(speakers, [] as Array[StringName], "only once")
	_done()


func test_a_gated_trigger_opens_a_battle_that_returns_here() -> void:
	assert_true(_trigger(&"gate").on_touched())
	assert_eq(hand_offs.size(), 0, "nothing before its flag")
	Game.set_flag(&"test_flag", true)
	Game.state.party_ids.assign([&"rhen"])
	assert_true(_trigger(&"gate").on_touched())
	assert_eq(hand_offs.size(), 1, "the battle")
	var r := hand_offs[0][1] as BattleRequest
	assert_eq(hand_offs[0][0], ZoneStory.KIND_BATTLE)
	assert_eq(r.encounter, &"ch02_tideline")
	assert_eq(r.return_location, &"zone_story_a")
	assert_eq(r.return_spawn, &"AfterFight")
	assert_eq(r.escape_spawn, &"Start")
	assert_eq(r.active, [&"rhen"] as Array[StringName], "the current party")
	assert_eq(r.rng_seed, 7)
	assert_true(story.busy and story.handed_off, "nothing else plays after a hand-off")
	_done()


func test_an_event_steps_rhen_back_without_leaving() -> void:
	zone.place_at(&"AfterFight")
	assert_true(_trigger(&"leave").on_touched())
	assert_eq(hand_offs.size(), 0, "the event stopped the run before the go step")
	assert_true(zone.player.position.distance_to(Vector3(0, 0, 8)) < 0.01, "back on Start")
	assert_false(story.busy)
	_done()


func test_zone_calls_and_travel_hand_off() -> void:
	story.play_beat(&"onward")
	assert_false(zone.stage.actor(&"asha").visible, "show_actor ran on the zone")
	assert_eq(hand_offs, [[ZoneStory.KIND_GO, {"location": "zone_story_b", "spawn": "In"}]] as Array[Array])
	_done()


func test_barks_swap_by_flag_and_overheard_ones_block_nothing() -> void:
	assert_eq(story.variant(&"test_dialogue_fixture"), &"test_dialogue_fixture")
	Game.set_flag(&"test_flag", true)
	assert_eq(story.variant(&"test_dialogue_fixture"), &"test_cutscene_fixture", "the flagged variant")
	story.overhear.instant = false
	assert_true(_trigger(&"overhear").on_touched())
	assert_true(story.overhear.is_playing(), "the overheard bark plays")
	assert_false(story.busy, "and blocks nothing")
	assert_true(_trigger(&"gate").on_touched(), "a beat still fires")
	assert_false(story.overhear.is_playing(), "and cuts it off")
	assert_eq(hand_offs.size(), 1)
	_done()


func test_the_next_zone_hands_to_its_scene() -> void:
	_done()
	_open(ZONE_B)
	story.begin()
	assert_eq(hand_offs, [[ZoneStory.KIND_SCENE, "res://game/flow/end_card.tscn"]] as Array[Array])
	_done()


func test_a_chapter_step_moves_the_story_on() -> void:
	Game.state.chapter = 2
	story.play_beat(&"promote")
	assert_eq(Game.state.chapter, 4, "set_chapter ran")
	assert_true(bool(Game.get_flag(&"test_flag")))
	_done()


func test_camera_volumes_and_rails_are_built() -> void:
	var rail := zone.get_node("CameraVolumes/Rail") as CameraVolume
	assert_true(rail != null and rail.shot.mode == CameraShot.Mode.DOLLY, "a dolly volume")
	assert_true(zone.get_node_or_null(NodePath(String(rail.shot.dolly_path))) is Path3D, "its dolly rail")
	assert_true(zone.get_node_or_null(NodePath(String(rail.shot.track_path))) is Path3D, "its track")
	var gate := zone.get_node("CameraVolumes/Gate") as CameraVolume
	assert_eq(gate.shot_priority, 1)
	assert_eq(gate.shot.mode, CameraShot.Mode.FIXED)
	assert_eq(zone.director.volumes.size(), 0, "collected on the next frame, as any zone's")
	zone.director.collect_volumes()
	assert_eq(zone.director.volumes.size(), 2)
	var glow := (zone.get_node("Greybox/Glow/Mesh") as MeshInstance3D).mesh.material as StandardMaterial3D
	assert_true(glow.emission_enabled, "an emissive block glows")
	_done()


func test_field_encounters_wait_for_their_flag_and_the_gap() -> void:
	var fired: Array[StringName] = []
	zone.encounters.on_encounter = func(id: StringName) -> void: fired.append(id)
	assert_eq(zone.encounters.walked(100.0), &"", "nothing before its when holds")
	Game.set_flag(&"test_flag", true)
	var gap := zone.encounters.next_m
	assert_between(gap, 10.0, 20.0)
	assert_eq(zone.encounters.walked(gap - 0.5), &"", "not before the gap")
	var id := zone.encounters.walked(1.0)
	assert_true(id in [&"ch02_tideline", &"sandbox_reef"], "then one from the table")
	assert_eq(fired, [id] as Array[StringName])
	assert_eq(zone.encounters.walked_m, 0.0, "and the count starts again")
	assert_true(FieldEncounters.return_points.has("zone_story_a"), "it remembers where Rhen stood")
	_done()


func test_an_encounter_returns_to_where_rhen_stood() -> void:
	Game.set_flag(&"test_flag", true)
	zone.place_at(&"AfterFight")
	zone.encounters.walked(zone.encounters.next_m + 0.1)
	assert_eq(hand_offs.size(), 1, "the random battle")
	var r := hand_offs[0][1] as BattleRequest
	assert_eq(r.return_spawn, FieldEncounters.RETURN_SPAWN)
	assert_eq(r.escape_spawn, FieldEncounters.RETURN_SPAWN)
	_done()
	_open(ZONE_A)
	assert_true(zone.place_at(FieldEncounters.RETURN_SPAWN))
	assert_true(zone.player.position.distance_to(Vector3(4, 0, 2)) < 0.01, "back where the fight started")
	_done()


func test_light_step_stretches_the_gap() -> void:
	var enc := FieldEncounters.new()
	enc.rate_pct = 50.0
	enc.min_m = 10.0
	enc.max_m = 10.0
	assert_eq(enc._draw(), 20.0, "half the rate, twice the distance")
	enc.free()
	_done()


func _open(path: String) -> void:
	zone = (load(path) as PackedScene).instantiate() as GreyboxZone
	story = zone.story
	story.autostart = false
	_host().add_child(zone)
	zone.director.auto_update = false
	zone.player.set_physics_process(false)
	zone.player.set_process_unhandled_input(false)
	story.active = true
	story.sequencer.instant = true
	story.overhear.instant = true
	story.sequencer.line_shown.connect(func(s: DialogueStep) -> void: speakers.append(s.speaker))
	story.hand_off = func(kind: StringName, target: Variant) -> void: hand_offs.append([kind, target])


func _trigger(id: StringName) -> Interactable:
	for n in zone.find_children("*", "Interactable", true, false):
		if (n as Interactable).id == id:
			return n as Interactable
	return null


func _done() -> void:
	SaveSystem.cancel_pending_autosave()
	if zone != null:
		_host().remove_child(zone)
		zone.free()
		zone = null
	Game.state = saved_state


func _host() -> Node:
	return (Engine.get_main_loop() as SceneTree).current_scene
