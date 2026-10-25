extends TestCase
## M2-HER-1102: HeroFieldParty, Asha and Toma on Rhen's trail: followers come from the live party
## (leader excluded, party order), keep their trail spacing and never crowd the leader, catch up after
## a teleport, react to a join, and hide while the stage shows the same hero or a cutscene holds the
## player.

const ZONE := "res://game/levels/_tests/field/field_test.tscn"
const DT := 1.0 / 60.0
const WALK_FRAMES := 240
const UP := Vector2(0, -1)
const SLACK_M := 0.35

var zone: Node3D
var player: FieldController
var party: HeroFieldParty
var _party_was: Array[StringName] = []


func before_each() -> void:
	_party_was = Game.state.party_ids.duplicate()
	Game.state.party_ids = [&"rhen", &"asha", &"toma"] as Array[StringName]
	zone = (load(ZONE) as PackedScene).instantiate() as Node3D
	_host().add_child(zone)
	(zone.get_node("CameraDirector") as FieldCameraDirector).auto_update = false
	player = zone.get_node("Player") as FieldController
	player.set_physics_process(false)
	player.set_process_unhandled_input(false)
	party = player.get_node(NodePath(String(HeroFieldParty.NAME))) as HeroFieldParty
	party.set_physics_process(false)
	zone.call("place_at", &"Court")
	party.advance(DT)


func test_followers_come_from_the_party_in_order() -> void:
	assert_eq(party.followers.size(), 2, "two followers")
	assert_eq(_ids(), [&"asha", &"toma"] as Array[StringName], "party order, the leader excluded")
	assert_true(party.body_of(&"asha") != null and party.body_of(&"asha").model != null, "Asha has a body")
	_done()


func test_no_follower_for_a_hero_not_in_the_party() -> void:
	Game.state.party_ids = [&"rhen", &"asha"] as Array[StringName]
	party.advance(DT)
	assert_eq(_ids(), [&"asha"] as Array[StringName])
	assert_true(party.body_of(&"toma") == null, "Toma has not joined")
	Game.state.party_ids.append(&"toma")
	party.advance(DT)
	assert_eq(_ids(), [&"asha", &"toma"] as Array[StringName], "a join adds a follower at once")
	_done()


func test_followers_keep_their_spacing_on_the_trail() -> void:
	var spacing := float(party._cfg["spacing_m"])
	var gap_min := float(party._cfg["min_gap_m"])
	player.input_override = UP
	var closest := INF
	for i in WALK_FRAMES:
		_step()
		closest = minf(closest, _flat(player.global_position, party.followers[0].global_position))
		closest = minf(closest, _flat(party.followers[0].global_position, party.followers[1].global_position))
	assert_true(closest >= gap_min - 0.01, "never nearer than min_gap_m (closest %.2f)" % closest)
	var d0 := _flat(player.global_position, party.followers[0].global_position)
	var d1 := _flat(party.followers[0].global_position, party.followers[1].global_position)
	assert_between(d0, spacing - SLACK_M, spacing + SLACK_M, "Asha a spacing behind Rhen at a run (%.2f)" % d0)
	assert_between(d1, spacing - SLACK_M, spacing + SLACK_M, "Toma a spacing behind Asha (%.2f)" % d1)
	var behind := (party.followers[0].global_position - player.global_position).dot(Vector3.FORWARD)
	assert_true(behind < 0.0, "she is behind him, not beside or ahead")
	assert_true(party.body_of(&"asha").loco.speed > 1.0, "and walks (the gait blend sees her speed)")
	player.input_override = Vector2.ZERO
	for i in WALK_FRAMES:
		_step()
	assert_true(party.body_of(&"asha").loco.speed < 0.05, "she stops when he stops")
	assert_between(
		_flat(player.global_position, party.followers[0].global_position), spacing - SLACK_M, spacing + SLACK_M
	)
	_done()


func test_feet_on_the_floor() -> void:
	for i in 30:
		_step()
	for f in party.followers:
		assert_between(
			f.global_position.y, player.global_position.y - 0.05, player.global_position.y + 0.05, "on the ground"
		)
	_done()


func test_a_teleport_catches_the_followers_up() -> void:
	zone.call("place_at", &"Causeway")
	party.advance(DT)
	var spacing := float(party._cfg["spacing_m"])
	for i in party.followers.size():
		var d := _flat(player.global_position, party.followers[i].global_position)
		assert_between(d, (i + 1) * spacing - 0.05, (i + 1) * spacing + 0.05, "follower %d put on the new trail" % i)
		assert_eq(party.body_of(_ids()[i]).loco.speed, 0.0, "with no gait from the jump")
	_done()


func test_hidden_while_the_stage_shows_the_same_hero() -> void:
	var stage := CutsceneStage.new()
	stage.name = "CutsceneStage"
	var actors := Node3D.new()
	actors.name = "Actors"
	stage.add_child(actors)
	var asha := Node3D.new()
	asha.name = "asha"
	actors.add_child(asha)
	zone.add_child(stage)
	party.rescan()
	party.advance(DT)
	assert_false(party.followers[0].visible, "no double Asha while the stage shows her")
	assert_true(party.followers[1].visible, "Toma still follows")
	asha.visible = false
	party.advance(DT)
	assert_true(party.followers[0].visible, "back when the stage hides her")
	_done()


func test_hidden_while_a_cutscene_holds_the_player() -> void:
	var seq := CutsceneSequencer.new()
	zone.add_child(seq)
	party.rescan()
	seq._playing = true
	party.advance(DT)
	for f in party.followers:
		assert_false(f.visible, "hidden during the cutscene")
	seq._playing = false
	party.advance(DT)
	for f in party.followers:
		assert_true(f.visible, "back after it")
	_done()


func _step() -> void:
	player.step(DT)
	party.advance(DT)
	for f in party.followers:
		var b := f.get_node(NodePath(String(HeroFieldActor.NAME))) as HeroFieldActor
		b.advance(DT)


func _ids() -> Array[StringName]:
	var out: Array[StringName] = []
	for f in party.followers:
		out.append(StringName(f.get_meta(&"hero_id")))
	return out


static func _flat(a: Vector3, b: Vector3) -> float:
	return Vector2(a.x - b.x, a.z - b.z).length()


func _done() -> void:
	zone.free()
	Game.state.party_ids = _party_was


func _host() -> Node:
	return (Engine.get_main_loop() as SceneTree).current_scene
