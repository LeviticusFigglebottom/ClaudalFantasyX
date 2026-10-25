extends TestCase
## SPEC §6.11 (the Memories gallery): a replayed cutscene reads the live flags but writes none, emits
## no <<event>>, and a zone prepared by ReplayStage starts no story and meets no encounter.

const FIXTURE := &"test_cutscene_fixture"
const ZONE := "res://game/levels/_tests/zone_story/zone_a.tscn"

var saved_state: GameStateData


func before_each() -> void:
	saved_state = Game.state
	Game.state = GameStateData.new()


func test_a_replay_writes_no_flag_and_emits_no_event() -> void:
	var seq := CutsceneSequencer.new()
	seq.instant = true
	seq.replay = true
	_host().add_child(seq)
	var emitted: Array[StringName] = []
	seq.event_requested.connect(func(n: StringName, _a: Array) -> void: emitted.append(n))
	seq.play(FIXTURE, null)
	assert_false(bool(Game.get_flag(&"test_flag")), "the fixture's <<set $test_flag>> stayed in the replay")
	assert_eq(emitted, [] as Array[StringName], "no event left the replay")
	assert_eq(seq.events.size(), 1, "but it was recorded")
	_host().remove_child(seq)
	seq.free()
	Game.state = saved_state


func test_replay_flags_read_the_live_game() -> void:
	Game.set_flag(&"test_flag", true)
	var access := ReplayFlagAccess.new()
	assert_true(bool(access.get_flag(&"test_flag")), "reads the game")
	access.set_flag(&"test_flag", false)
	assert_false(bool(access.get_flag(&"test_flag")), "its own write wins inside the replay")
	assert_true(bool(Game.get_flag(&"test_flag")), "and the game is untouched")
	Game.state = saved_state


func test_a_prepared_zone_starts_no_story_and_meets_no_encounter() -> void:
	var zone := (load(ZONE) as PackedScene).instantiate() as GreyboxZone
	assert_true(ReplayStage.prepare(zone) >= 1)
	assert_false(zone.story.autostart, "the story stays idle")
	assert_true(zone.encounters == null, "no field encounters")
	assert_eq(zone.find_children("*", "FieldEncounters", true, false).size(), 0)
	zone.free()
	Game.state = saved_state


func _host() -> Node:
	return (Engine.get_main_loop() as SceneTree).current_scene
