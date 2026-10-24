extends TestCase
## M2-FP-16: ShellShrineTrial, the Shell Shrine puzzle's rules, on the real data.

var trial: ShellShrineTrial
var events: Array[String] = []


func before_each() -> void:
	trial = ShellShrineTrial.new()
	events.clear()
	trial.rotated.connect(func(b: StringName, r: int) -> void: events.append("rotated %s %d" % [b, r]))
	trial.flow_changed.connect(func(p: Array[StringName]) -> void: events.append("flow %s" % p.back()))
	trial.pool_filled.connect(func() -> void: events.append("filled"))
	trial.side_pool_drained.connect(func() -> void: events.append("drained"))
	trial.hint_due.connect(func() -> void: events.append("hint"))


func test_the_start_spills_and_the_door_is_shut() -> void:
	assert_eq(trial.trace()[0], StringName(str(trial.data["source_into"])))
	assert_false(trial.reaches(trial.goal()))
	assert_false(trial.door_open)
	var band: Array = trial.data["solution_moves"]
	var n := trial.min_turns_to(trial.goal())
	assert_between(n, float(band[0]), float(band[1]), "shortest solution %d turns" % n)
	assert_true(trial.min_turns_to(trial.drain()) > 0, "the side pool can be drained")


func test_a_turn_steps_the_lip_and_wraps() -> void:
	var b := trial.basin_ids()[0]
	var r0 := int(trial.rotations[b])
	for i in trial.steps():
		assert_true(trial.rotate(b))
	assert_eq(int(trial.rotations[b]), r0, "four turns come back round")
	assert_eq(trial.turns, trial.steps())
	assert_false(trial.rotate(&"no_such_basin"))


func test_the_shortest_solution_fills_the_pool_and_opens_the_door() -> void:
	_solve()
	assert_true(trial.reaches(trial.goal()))
	assert_true(events.has("flow inner_pool"), "the flow change is reported")
	trial.advance(float(trial.data["fill_sec"]) * 0.5)
	assert_between(trial.pool_level, 0.49, 0.51, "half full at half the fill time")
	assert_false(trial.door_open)
	trial.advance(float(trial.data["fill_sec"]))
	assert_true(trial.door_open)
	assert_eq(events.count("filled"), 1)
	assert_false(trial.rotate(trial.basin_ids()[0]), "the basins are still once the door is open")


func test_the_sluice_drains_the_side_pool_once() -> void:
	# b1 toward b2, b2 toward the sluice (data: b1 outlet 1, b2 outlet 2).
	trial.rotate(&"b1")
	trial.rotate(&"b2")
	trial.rotate(&"b2")
	assert_true(trial.reaches(trial.drain()))
	trial.advance(0.1)
	assert_true(trial.side_drained)
	trial.advance(0.1)
	assert_eq(events.count("drained"), 1, "it drains once")


func test_the_hint_comes_once_after_idling() -> void:
	var idle := float(trial.data["hint_idle_sec"])
	trial.advance(idle - 1.0)
	trial.rotate(&"b3")
	trial.advance(idle - 1.0)
	assert_false(events.has("hint"), "a turn resets the clock")
	trial.advance(2.0)
	trial.advance(idle * 2.0)
	assert_eq(events.count("hint"), 1)


func test_a_loop_spills() -> void:
	# b1 → b2, b2 → b3 (rotation 0), b3 → b2 (rotation 1, its start): round in circles.
	trial.rotate(&"b1")
	var path := trial.trace()
	assert_eq(path.back(), StringName(str(trial.data["spill"])), "water going round is lost: %s" % [path])


## Turns basins until the water reaches the goal, by the search's own shortest path (data-agnostic).
func _solve() -> void:
	var guard := 0
	while not trial.reaches(trial.goal()) and guard < 16:
		guard += 1
		var best := &""
		var best_n := 1 << 20
		for b in trial.basin_ids():
			var probe := ShellShrineTrial.new(trial.data)
			probe.rotations = trial.rotations.duplicate()
			probe.rotate(b)
			var n := probe.min_turns_to(probe.goal())
			if n >= 0 and n < best_n:
				best_n = n
				best = b
		trial.rotate(best)
