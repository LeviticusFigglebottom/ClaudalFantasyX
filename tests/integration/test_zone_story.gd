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
	FieldEncounters.reset()
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


func test_a_scene_right_before_a_hand_off_stays_on_black() -> void:
	var restores: Array[bool] = []
	story.sequencer.line_shown.connect(func(_s: DialogueStep) -> void: restores.append(story.sequencer.restore_fade))
	zone.place_at(&"AfterFight")
	story.play_beat(&"leave")
	assert_true(not restores.is_empty() and restores.back(), "a scene with more steps after it fades back in")
	restores.clear()
	story.play_beat(&"fade_hand_off")
	assert_true(not restores.is_empty() and not restores.back(), "one right before a hand-off does not (M3-C01-02)")
	assert_true(story.sequencer.restore_fade, "and the sequencer fades back in again afterwards")
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
	var floor_m := zone.encounters.min_gap_m  # the layout's 10-20 m, under the defaults' floor
	assert_between(gap, maxf(10.0, floor_m), maxf(20.0, floor_m))
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


func test_after_a_battle_the_walk_back_is_safe_and_the_meter_carries_on() -> void:
	# M2-FP-28, from the human's playtest: random battles came back to back with no walk between.
	Game.set_flag(&"test_flag", true)
	var fired: Array[StringName] = []
	zone.encounters.on_encounter = func(id: StringName) -> void: fired.append(id)
	var first_gap := zone.encounters.next_m
	zone.place_at(&"AfterFight")
	zone.encounters.walked(first_gap + 0.1)
	assert_eq(fired.size(), 1, "the battle")
	var grace := zone.encounters.grace_after_m
	assert_true(grace > 0.0, "a post-battle grace (greybox_defaults.json encounters.grace_m)")
	var next_gap := zone.encounters.next_m
	_done()  # the battle scene replaces the zone ...
	_open(ZONE_A)  # ... and the zone is instanced again on the way back
	Game.set_flag(&"test_flag", true)
	var enc := zone.encounters
	enc.on_encounter = func(id: StringName) -> void: fired.append(id)
	assert_eq(enc.next_m, next_gap, "the meter carries on: not the same first gap again")
	assert_eq(enc.grace_m, grace, "and the grace is still owed")
	enc._physics_process(0.0)  # the first frame anchors at the location's default spawn
	assert_true(zone.place_at(FieldEncounters.RETURN_SPAWN))
	enc._physics_process(0.0)
	assert_eq(enc.grace_m, grace, "the jump to the return spot is not walking")
	zone.player.position += Vector3(enc.max_step_m * 10.0, 0, 0)
	enc._physics_process(0.0)
	assert_eq(enc.grace_m, grace, "nor is any jump past max_step_m in one frame")
	assert_eq(enc.walked(grace - 0.1), &"", "nothing inside the grace")
	assert_eq(enc.walked_m, 0.0, "the grace is walked before the meter runs")
	assert_true(is_equal_approx(enc.grace_m, 0.1), "with 0.1 m of it left")
	assert_eq(enc.walked(next_gap), &"", "then the full gap")
	assert_true(enc.grace_s > 0.0, "a timed grace too (greybox_defaults.json encounters.grace_s)")
	assert_eq(enc.walked(0.2), &"", "which holds the battle past the gap")
	enc.field_time(enc.grace_s - 0.1)
	assert_eq(enc.walked(0.1), &"", "until its last second has passed")
	enc.field_time(0.1)
	assert_ne(enc.walked(0.1), &"", "and only then the next battle")
	assert_eq(fired.size(), 2)
	_done()


func test_any_battle_owes_the_grace_and_the_fade_back_is_not_field_time() -> void:
	# The Lead's FAST-TRACK (10-30, the human's playtest): a scripted fight, then a random one at once.
	Game.set_flag(&"test_flag", true)
	_done()  # a scripted battle replaces the zone ...
	EventBus.battle_ended.emit(&"ch02_tideline", &"victory")
	_open(ZONE_A)  # ... and the zone comes back
	Game.set_flag(&"test_flag", true)
	var enc := zone.encounters
	var fired: Array[StringName] = []
	enc.on_encounter = func(id: StringName) -> void: fired.append(id)
	assert_eq(enc.grace_m, enc.grace_after_m, "the walk back is owed")
	assert_true(enc.grace_s > 0.0 and is_equal_approx(enc.grace_s, enc.grace_after_s), "and the time")
	assert_false(FieldEncounters.battle_grace_owed, "taken once")
	enc.field_time(enc.grace_after_s * 10.0)
	assert_eq(enc.grace_s, enc.grace_after_s, "time before Rhen's first step (the fade back) never counts")
	assert_eq(enc.walked(enc.grace_after_m + enc.next_m + 0.1), &"", "walking alone doesn't end it")
	enc.field_time(enc.grace_after_s)
	assert_ne(enc.walked(0.1), &"", "time and distance both passed: the meter runs")
	assert_eq(fired.size(), 1)
	_done()


func test_no_gap_is_shorter_than_the_floor() -> void:
	Game.set_flag(&"test_flag", true)
	var enc := zone.encounters
	assert_true(enc.min_gap_m > 0.0, "a floor (greybox_defaults.json encounters.min_gap_m)")
	for i in 50:
		assert_true(enc._draw() >= enc.min_gap_m - 0.001, "every gap is at least the floor")
	_done()


func test_a_new_game_forgets_the_meters() -> void:
	Game.set_flag(&"test_flag", true)
	zone.encounters.remember()
	assert_true(FieldEncounters.meters.has("zone_story_a"))
	EventBus.new_game_started.emit()
	assert_false(FieldEncounters.meters.has("zone_story_a"))
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


func test_no_encounter_rolls_while_another_battle_is_opening() -> void:
	# M3-BPR-427 (GPU QA row 34): a fight started from outside the zone (the QA walk's BattleRequest.start) is opening;
	# a random one fired now would replace its request and send the battle to the sandbox fight.
	Game.set_flag(&"test_flag", true)
	var fired: Array[StringName] = []
	zone.encounters.on_encounter = func(id: StringName) -> void: fired.append(id)
	zone.place_at(&"AfterFight")
	BattleRequest._pending = BattleRequest.new()
	BattleRequest._opening = true
	assert_eq(zone.encounters.walked(zone.encounters.next_m + 0.1), &"", "held while the other battle opens")
	assert_eq(fired.size(), 0)
	BattleRequest.clear()
	assert_ne(zone.encounters.walked(0.1), &"", "and it fires on the next step once that battle has its request")
	_done()
