extends TestCase
## M3-BPR-427 (GPU QA row 34): a second BattleRequest submitted while the first is still opening is dropped, so the
## battle opens on the first and never falls back to the sandbox fight; field encounters hold off meanwhile.

signal stinger_done

var _routed: Array = []


func before_each() -> void:
	BattleRequest.clear()
	BattleRequest.change_scene = Callable()
	BattleRequest.play_stinger = func() -> void: await stinger_done  # the runner steps no frames
	FlowRouting.record = func(args: Array) -> void: _routed.append(args)
	_routed.clear()


func after_each() -> void:
	BattleRequest.clear()
	BattleRequest.play_stinger = Callable()
	FlowRouting.record = Callable()


func test_a_second_submit_while_opening_is_dropped() -> void:
	var a := _req(&"ch06_ridge_skippers")
	var b := _req(&"ch04_bottle_hermit")
	BattleRequest.submit(a)  # live path: its stinger is still playing
	assert_true(BattleRequest.opening())
	BattleRequest.submit(b)
	assert_eq(BattleRequest.pending(), a, "the first request stays the one that opens")
	stinger_done.emit()
	assert_eq(_routed.size(), 1, "one scene change, not two")
	assert_eq(BattleRequest.take(), a, "the battle takes the first")
	assert_false(BattleRequest.opening(), "taking it ends the opening")


func test_after_the_battle_takes_it_a_new_submit_goes_through() -> void:
	BattleRequest.submit(_req(&"ch06_ridge_skippers"))
	stinger_done.emit()
	BattleRequest.take()
	var c := _req(&"ch06_shoal_skippers_b")
	BattleRequest.submit(c)
	assert_eq(BattleRequest.pending(), c)


func test_a_recorded_change_is_never_held() -> void:
	BattleRequest.change_scene = func(_p: String) -> void: pass
	BattleRequest.submit(_req(&"one"))
	assert_false(BattleRequest.opening(), "the tests' recorder path opens nothing")
	var two := _req(&"two")
	BattleRequest.submit(two)
	assert_eq(BattleRequest.pending(), two)


static func _req(enc: StringName) -> BattleRequest:
	var r := BattleRequest.new()
	r.encounter = enc
	return r
