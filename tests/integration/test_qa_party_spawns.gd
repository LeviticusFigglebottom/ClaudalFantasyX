extends TestCase
## FAST-TRACK (the human's playtest, 2026-10-28): "when the game begins the rest of the party sits still and inside
## each other". Two guards:
## - At every spawn of every Act I zone (HeroGuardSources.field_zones), the party loads with no two bodies nearer
##   than min_gap_m (leader and followers), and once the leader walks, every follower is moving within FOLLOW_FRAMES.
## - The game's real start: New Game, Haluna, Cutscene A (Asha joins). After it, the stage Asha and Toma it left on
##   Rhen's spot are handed back (hidden), and Asha's follower shows, clear of him, and walks when he does.

const HALUNA := "res://game/levels/ch02/haluna/haluna.tscn"
const DT := 1.0 / 60.0
const SETTLE_FRAMES := 3
## A follower must be moving (MOVE_M from where it stood) this many frames after the leader starts.
const FOLLOW_FRAMES := 30
const MOVE_M := 0.05
const WALK_FRAMES := 60
const EPS_M := 0.01

var _state_was: GameStateData


func before_each() -> void:
	_state_was = Game.state


func test_no_spawn_stacks_the_party_and_the_followers_follow() -> void:
	Game.state = GameStateData.new()
	Game.state.party_ids = [&"rhen", &"asha", &"toma"] as Array[StringName]
	var gap := float((HeroFieldActor.field_data().get("followers", {}) as Dictionary).get("min_gap_m", 0.0))
	var checked := 0
	for path in HeroGuardSources.field_zones():
		var zone := (load(path) as PackedScene).instantiate() as Node3D
		var story := zone.get(&"story") as ZoneStory if "story" in zone else null
		if story != null:
			story.autostart = false
		_host().add_child(zone)
		var player := _controller(zone)
		var party := (
			player.get_node_or_null(NodePath(String(HeroFieldParty.NAME))) as HeroFieldParty if player != null else null
		)
		if party == null or not zone.has_method(&"spawn_names"):
			zone.free()
			continue
		player.set_physics_process(false)
		player.set_process_unhandled_input(false)
		party.set_physics_process(false)
		for sp: Variant in zone.call("spawn_names"):
			checked += 1
			var where := "%s %s" % [path.get_file(), sp]
			zone.call("place_at", sp, zone.call("spawn_yaw_deg", sp))
			for i in SETTLE_FRAMES:
				party.advance(DT)
			var bodies: Array[Vector3] = [player.global_position]
			for f in party.followers:
				bodies.append(f.global_position)
			for a in bodies.size():
				for b in range(a + 1, bodies.size()):
					var d := _flat(bodies[a], bodies[b])
					assert_true(
						d >= gap - EPS_M, "%s: bodies %d and %d stand %.2f m apart (min %.2f)" % [where, a, b, d, gap]
					)
			_assert_follow(player, party, where)
		zone.free()
	Game.state = _state_was
	assert_true(checked > 10, "spawns checked (%d)" % checked)


func test_the_game_start_hands_the_party_back_after_cutscene_a() -> void:
	Game.new_game()
	Game.set_flag(&"prologue_seen")
	var zone := (load(HALUNA) as PackedScene).instantiate() as Node3D
	_host().add_child(zone)
	var player := _controller(zone)
	player.set_physics_process(false)
	player.set_process_unhandled_input(false)
	var party := player.get_node(NodePath(String(HeroFieldParty.NAME))) as HeroFieldParty
	party.set_physics_process(false)
	party.advance(DT)  # the party's first frame comes long before a real cutscene ends: it watches the sequencers
	var story := zone.get_node("Story") as HalunaStory
	story.sequencer.instant = true
	story.active = true
	await story.begin()
	assert_true(bool(Game.get_flag(&"ch02_met_asha")), "Cutscene A played")
	for i in SETTLE_FRAMES:
		party.advance(DT)
	var stage := HeroFieldParty.find_scripted(zone, &"CutsceneStage")[0] as CutsceneStage
	for id: String in ["asha", "toma"]:
		var a := stage.actor(StringName(id))
		assert_true(a != null and not a.is_visible_in_tree(), "the stage %s is handed back to the field" % id)
	assert_eq(party.followers.size(), 2, "Asha follows, and Toma from the reserve (followers.include_reserve)")
	if not party.followers.is_empty():
		var f := party.followers[0]
		assert_true(f.is_visible_in_tree(), "her follower shows")
		var gap := float((HeroFieldActor.field_data().get("followers", {}) as Dictionary).get("min_gap_m", 0.0))
		assert_true(_flat(f.global_position, player.global_position) >= gap - EPS_M, "clear of Rhen")
		_assert_follow(player, party, "after Cutscene A")
	zone.free()
	Game.state = _state_was


## The human's "Trying to cast a freed object" entering a fight: a sequencer the party watches, freed before the party
## (a zone's teardown, a stage despawned), must not be cast on the party's next frame.
func test_a_freed_sequencer_is_not_cast() -> void:
	Game.new_game()
	var zone := (load(HALUNA) as PackedScene).instantiate() as Node3D
	_host().add_child(zone)
	var player := _controller(zone)
	player.set_physics_process(false)
	player.set_process_unhandled_input(false)
	var party := player.get_node(NodePath(String(HeroFieldParty.NAME))) as HeroFieldParty
	party.set_physics_process(false)
	party.rescan()
	var seqs := HeroFieldParty.find_scripted(zone, &"CutsceneSequencer")
	assert_true(not seqs.is_empty(), "Haluna has a sequencer to watch")
	var qa := QaLogger.new()
	OS.add_logger(qa)
	for s in seqs:
		s.free()
	party.should_hide()
	party.advance(DT)
	OS.remove_logger(qa)
	for e in qa.take():
		assert_true(e["kind"] == QaLogger.KIND_WARNING, "no error with its sequencers freed: %s" % e["text"])
	zone.free()
	Game.state = _state_was


## The leader walks on; every follower must be moving within FOLLOW_FRAMES.
func _assert_follow(player: FieldController, party: HeroFieldParty, where: String) -> void:
	var start: Array[Vector3] = []
	for f in party.followers:
		start.append(f.global_position)
	var moved_at: Array[int] = []
	moved_at.resize(party.followers.size())
	moved_at.fill(-1)
	player.input_override = Vector2(0, -1)
	for frame in WALK_FRAMES:
		player.step(DT)
		party.advance(DT)
		for k in party.followers.size():
			if moved_at[k] < 0 and _flat(start[k], party.followers[k].global_position) > MOVE_M:
				moved_at[k] = frame
	player.input_override = Vector2.ZERO
	for k in party.followers.size():
		assert_true(
			moved_at[k] >= 0 and moved_at[k] <= FOLLOW_FRAMES,
			"%s: follower %d moves within %d frames (moved at %d)" % [where, k, FOLLOW_FRAMES, moved_at[k]]
		)


static func _controller(zone: Node) -> FieldController:
	for n in zone.find_children("*", "CharacterBody3D", true, false):
		if n is FieldController:
			return n as FieldController
	return null


static func _flat(a: Vector3, b: Vector3) -> float:
	return Vector2(a.x - b.x, a.z - b.z).length()


func _host() -> Node:
	return (Engine.get_main_loop() as SceneTree).current_scene
