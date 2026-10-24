extends TestCase
## M2-FP-09: FlowRouting never loses a scene change. While the router is busy it waits a frame at a
## time (driven here by a signal the test emits), then makes the change exactly once.

signal tick

var busy_frames := 0
var calls := 0


func before_each() -> void:
	FlowRouting.busy = func() -> bool: return busy_frames > 0
	FlowRouting.next_frame = func() -> Signal: return tick


func test_a_change_waits_for_an_idle_router_then_happens_once() -> void:
	busy_frames = 3
	FlowRouting.when_free(func() -> void: calls += 1)
	for i in 3:
		assert_eq(calls, 0, "held while busy (frame %d)" % i)
		busy_frames -= 1
		tick.emit()
	assert_eq(calls, 1, "made once the router is idle")
	tick.emit()
	assert_eq(calls, 1, "and only once")
	_done()


func test_an_idle_router_changes_at_once() -> void:
	busy_frames = 0
	FlowRouting.when_free(func() -> void: calls += 1)
	assert_eq(calls, 1)
	_done()


## M2-FP-11: two hand-offs waiting on one busy router. The router goes idle, the first changes scene
## (which makes the router busy again), and the second waits for that change to finish instead of
## firing on the same idle frame and being dropped.
func test_two_waiters_take_turns() -> void:
	busy_frames = 2
	var order: Array[String] = []
	var change := func(tag: String) -> void:
		order.append(tag)
		busy_frames = 2  # a scene change keeps the router busy for a while
	FlowRouting.when_free(change.bind("first"))
	FlowRouting.when_free(change.bind("second"))
	assert_eq(FlowRouting.waiting(), 2)
	busy_frames = 0
	tick.emit()
	assert_eq(order, ["first"] as Array[String], "one change per idle frame")
	for i in 2:
		assert_eq(order.size(), 1, "the second waits while the first change runs (frame %d)" % i)
		busy_frames -= 1
		tick.emit()
	assert_eq(order, ["first", "second"] as Array[String], "then the second, in call order")
	assert_eq(FlowRouting.waiting(), 0)
	_done()


func test_the_end_card_and_field_battle_latches_go_through_it() -> void:
	for path in ["res://game/flow/end_card.gd", "res://game/flow/field_battle.gd", "res://game/flow/haluna_story.gd"]:
		var src := FileAccess.get_file_as_string(path)
		assert_false(src.contains("SceneRouter.change_scene("), "%s changes scene only through FlowRouting" % path)
	_done()


func _done() -> void:
	FlowRouting.reset()
	FlowRouting.busy = Callable()
	FlowRouting.next_frame = Callable()
