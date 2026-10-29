extends TestCase
## M3-C04-02: the Ch4 zone root (Ch04Zone): its dressing follows the story flags (the layout's
## "states"), applied in order when the zone is ready, so a zone reloaded by a battle or a save comes
## up right; and it stands actors on marks.

const WAKE := "res://game/levels/ch04/haluna_wake/haluna_wake.tscn"
const FERRY := "res://game/levels/ch04/brightwater_ferry/brightwater_ferry.tscn"

var zone: Ch04Zone
var saved_state: GameStateData


func before_each() -> void:
	saved_state = Game.state
	Game.state = GameStateData.new()


func test_a_ferry_loaded_after_the_boss_comes_up_with_the_sails_down() -> void:
	for f: StringName in [
		&"ch04_started", &"ch04_ysolde_joined", &"ch04_boarded_derelict", &"ch04_spar_wraith_defeated"
	]:
		Game.set_flag(f)
	_open(FERRY)
	assert_false(zone.block_shown("SailsSet"))
	assert_true(zone.block_shown("SailsLowered"))
	assert_false(zone.block_shown("spar_wraith"), "the wraith is gone")
	assert_false(zone.block_shown("Gangplank"), "the gangplank is shipped")
	assert_true(zone.block_shown("SternGate"))
	assert_false(zone.block_shown("NameBoardWrapped"), "the board is still on her stern")
	var asha := zone.stage.actor(&"asha")
	assert_true(asha.position.distance_to(zone.stage.mark(&"derelict_asha").position) < 0.01, "the party is aboard her")
	_done()


func test_later_rows_win_and_a_fresh_wake_shows_its_lamps() -> void:
	Game.set_flag(&"ch03_rhen_sworn_guardian")
	_open(WAKE)
	assert_true(zone.story_set_shown("ch04_wake"), "the lamps to the wall and the feast")
	assert_true(zone.story_set_shown("ch04_shell_imra_faded"), "Imra's shell, faded")
	assert_false(zone.story_set_shown("ch04_shell_asha"), "the gap in the wall is still a gap")
	Game.set_flag(&"ch04_started")
	Game.set_flag(&"ch04_shell_set")
	zone.refresh_states()
	assert_true(zone.story_set_shown("ch04_shell_asha"), "shown by a later row")
	_done()


func test_the_wake_is_the_real_haluna_at_night() -> void:
	Game.set_flag(&"ch03_rhen_sworn_guardian")
	_open(WAKE)
	assert_true(zone.dressing is HalunaMood, "Haluna's own dressing (ADR 0041)")
	assert_true((zone.dressing as HalunaMood).is_night(), "at its night mood")
	assert_true(zone.haluna_collision != null and zone.haluna_collision.shape_count > 0, "on Haluna's walk collision")
	assert_eq(zone.get_node(^"Greybox").get_child_count(), 0, "no greybox block left")
	_done()


func test_the_wakes_field_camera_is_halunas() -> void:
	Game.set_flag(&"ch03_rhen_sworn_guardian")
	_open(WAKE)
	var vols := zone.get_node(^"HalunaCameraVolumes")
	# As many as ch02/haluna has (10 since M2-FP-109's NemeTable and DockEnd), read from its scene, so a volume added
	# there reaches the wake without this test going stale.
	var want := _haluna_volume_count()
	assert_true(want >= 8, "ch02/haluna has its volumes (%d)" % want)
	assert_eq(vols.get_child_count(), want, "the wake has ch02/haluna's volumes")
	var market := vols.get_node(^"Market") as CameraVolume
	assert_eq(market.shot.id, &"H09", "with their shots")
	assert_true(market.contains_point(Vector3(-46.5, 3.0, -0.5)), "and their shapes, where Haluna has them")
	zone.director.collect_volumes()
	assert_true(zone.director.volumes.has(market), "the director picks them up")
	_done()


func test_placing_an_actor_needs_the_actor_and_the_mark() -> void:
	_open(FERRY)
	assert_true(zone.place_actor("toma", "ferry_toma"))
	assert_true(zone.stage.actor(&"toma").position.distance_to(zone.stage.mark(&"ferry_toma").position) < 0.01)
	assert_false(zone.place_actor("toma", "no_such_mark"))
	assert_false(zone.place_actor("nobody", "ferry_toma"))
	_done()


func _haluna_volume_count() -> int:
	var state := (load(Ch04Zone.HALUNA_SCENE) as PackedScene).get_state()
	var n := 0
	for i in state.get_node_count():
		var path := String(state.get_node_path(i)).trim_prefix("./").split("/")
		if path.size() == 2 and path[0] == Ch04Zone.HALUNA_VOLUMES:
			n += 1
	return n


func _open(path: String) -> void:
	zone = (load(path) as PackedScene).instantiate() as Ch04Zone
	zone.story.autostart = false
	_host().add_child(zone)
	zone.set_process(false)
	zone.director.auto_update = false
	zone.player.set_physics_process(false)
	if zone.encounters != null:
		zone.encounters.set_physics_process(false)


func _done() -> void:
	if zone != null and is_instance_valid(zone):
		_host().remove_child(zone)
		zone.free()
	zone = null
	Game.state = saved_state


func _host() -> Node:
	return (Engine.get_main_loop() as SceneTree).current_scene
