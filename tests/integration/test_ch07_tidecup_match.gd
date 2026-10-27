extends TestCase
## M3-C07-1206: TidecupMatch, the story's side of the Reefball seam (act1_ch07.md §5.4). The match always
## sets ch07_tidecup_played, sets ch07_tidecup_won and gives the win reward on a win only (a draw is a
## loss for rewards), goes back to the galleries' catch-pool, and plays to the end headless with the
## engine's AI on both sides.

const SCENE := "res://game/levels/ch07/tidecup_match/tidecup_match.tscn"
const DATA := "res://game/data/flow/ch07_tidecup.json"

var routed: Array = []


func before_each() -> void:
	Game.new_game()
	routed.clear()
	FlowRouting.record = func(change: Array) -> void: routed.append(change)


func _match(autoplay: bool) -> TidecupMatch:
	var m := (load(SCENE) as PackedScene).instantiate() as TidecupMatch
	m.autoplay = autoplay
	return m


func _free(m: TidecupMatch) -> void:
	if m.is_inside_tree():
		m.get_parent().remove_child(m)
	m.free()
	FlowRouting.record = Callable()


func test_a_win_sets_both_flags_and_gives_the_reward() -> void:
	var m := _match(true)
	m.data = GreyboxZone.read_json(DATA)
	var before := Game.state.currency
	m.end_match(ReefballMatch.WIN)
	assert_true(bool(Game.get_flag(&"ch07_tidecup_played")))
	assert_true(bool(Game.get_flag(&"ch07_tidecup_won")))
	assert_eq(Game.state.currency - before, int(m.data["win_reward"]["lume"]), "the win's lume")
	assert_eq(routed, [[&"ch07/tamsule_bell_galleries", &"CatchPool"]], "back to the catch-pool")
	m.end_match(ReefballMatch.LOSS)
	assert_eq(routed.size(), 1, "it ends once")
	_free(m)


func test_a_loss_or_a_draw_is_played_but_not_won() -> void:
	for result: StringName in [ReefballMatch.LOSS, ReefballMatch.DRAW]:
		Game.new_game()
		routed.clear()
		FlowRouting.record = func(change: Array) -> void: routed.append(change)
		var m := _match(true)
		m.data = GreyboxZone.read_json(DATA)
		var before := Game.state.currency
		m.end_match(result)
		assert_true(bool(Game.get_flag(&"ch07_tidecup_played")), "%s: played" % result)
		assert_false(bool(Game.get_flag(&"ch07_tidecup_won")), "%s: never the win flag" % result)
		assert_eq(Game.state.currency, before, "%s: no reward" % result)
		assert_eq(routed.size(), 1)
		_free(m)


func test_the_fallback_plays_the_match_to_its_end() -> void:
	var m := _match(true)
	(Engine.get_main_loop() as SceneTree).current_scene.add_child(m)
	assert_true(m.match_state.finished, "the engine's AI plays both sides to the whistle")
	assert_eq(m.outcome, m.match_state.outcome)
	assert_true(bool(Game.get_flag(&"ch07_tidecup_played")))
	assert_eq(routed.size(), 1)
	_free(m)
