extends TestCase
## M3-C05-02: the Ashcrown trial's rules (AshcrownTrial, game/data/trials/ashcrown.json;
## act1_ch05.md B08). Catch, turn, release, the stud ring counted in metres walked (never seconds),
## re-catching at the tier where a charge was lost, the linked pair, the plate, the sealed side vein
## and the landing. Plays the real data.

var trial: AshcrownTrial


func before_each() -> void:
	trial = AshcrownTrial.new()


func test_every_tier_is_solvable_within_its_band_and_none_starts_solved() -> void:
	assert_eq(trial.tier_count(), 4, "four inner tiers")
	for i in trial.tier_count():
		var band: Array = (trial.tiers()[i] as Dictionary).get("solution_turns", [0, 0])
		var n := trial.min_turns(i)
		assert_true(n >= int(band[0]) and n <= int(band[1]), "tier %d: %d moves, band %s" % [i + 1, n, band])
		assert_true(n > 0, "tier %d does not start solved" % (i + 1))


func test_nothing_answers_before_the_catch() -> void:
	assert_eq(trial.release(&"t1"), &"", "no charge, no run")
	assert_false(trial.catch(&"t2"), "only the crown's rod at first")
	assert_true(trial.catch(&"t1"))
	assert_false(trial.catch(&"t1"), "one charge at a time")
	assert_eq(trial.studs_left, trial.studs())


func test_tier_one_teaches_the_loop() -> void:
	trial.catch(&"t1")
	assert_eq(trial.release(&"t1"), AshcrownTrial.OUT_OPEN, "an open circuit keeps the charge")
	assert_true(trial.charged)
	assert_true(trial.turn(&"g1"))
	assert_eq(trial.trace(), [&"g1", &"spout"] as Array[StringName])
	assert_eq(trial.release(&"t1"), AshcrownTrial.OUT_NEXT)
	assert_eq(trial.tier, 1, "the strike pours to tier two's bowl")
	assert_true(trial.charged, "and charges it")
	assert_eq(trial.studs_left, trial.studs(), "with a fresh ring")
	assert_false(trial.turn(&"g1"), "tier one's gate is done")


func test_the_ring_is_counted_in_steps_and_a_faded_charge_is_caught_again_here() -> void:
	trial.catch(&"t1")
	trial.advance(10000.0)
	assert_true(trial.charged, "standing still costs nothing: no clock")
	var per := float(trial.data["metres_per_stud"])
	trial.walk(per * 0.5)
	assert_eq(trial.studs_left, trial.studs(), "half a stud's walk darkens nothing")
	trial.walk(per * 0.5)
	assert_eq(trial.studs_left, trial.studs() - 1)
	trial.walk(per * trial.studs())
	assert_false(trial.charged, "the last stud fades the charge")
	assert_eq(trial.tier, 0)
	assert_true(trial.catch(&"t1"), "caught again at the same tier")


func test_tier_two_dead_end_grounds_the_charge() -> void:
	_to_tier(1)
	trial.turn(&"g2a")
	assert_eq(trial.trace().back(), &"ground", "the obvious first turn routes into the ash drift")
	assert_eq(trial.release(&"t2"), AshcrownTrial.OUT_GROUND)
	assert_false(trial.charged)
	assert_eq(trial.tier, 1, "lost at tier two, never back at the crown")
	assert_false(trial.catch(&"t1"))
	assert_true(trial.catch(&"t2"), "tier two's own rod")
	for _i in 3:
		trial.turn(&"g2b")
	assert_eq(trial.release(&"t2"), AshcrownTrial.OUT_NEXT)


func test_the_linked_pair_turns_together_and_the_seal_opens_the_alcove() -> void:
	_to_tier(2)
	var b := int(trial.rotations[&"g3b"])
	trial.turn(&"g3a")
	assert_eq(int(trial.rotations[&"g3b"]), (b + 1) % trial.steps(), "turning one turns its twin")
	assert_eq(trial.trace(), [&"g3a", &"seal"] as Array[StringName])
	var opened := [false]
	trial.alcove_opened.connect(func() -> void: opened[0] = true)
	assert_eq(trial.release(&"t3"), AshcrownTrial.OUT_SEAL, "the sealed side vein")
	assert_true(trial.alcove_open and opened[0])
	assert_false(trial.charged, "it costs the charge")
	assert_true(trial.catch(&"t3"))
	trial.turn(&"g3a")
	for _i in 3:
		trial.turn(&"g3c")
	assert_eq(trial.trace().back(), &"spout")
	assert_eq(trial.release(&"t3"), AshcrownTrial.OUT_NEXT)


func test_the_plate_gate_passes_only_while_someone_stands_on_it_and_the_last_run_lands() -> void:
	_to_tier(3)
	assert_eq(trial.plate_held, &"p4b", "Toma starts on the wrong plate")
	trial.turn(&"g4a")
	trial.turn(&"g4a")
	trial.turn(&"g4b")
	assert_eq(trial.trace(), [&"g4a", &"p4a", &"none"] as Array[StringName], "nobody on p4a: open")
	assert_false(trial.turn(&"p4a"), "a plate does not turn")
	assert_true(trial.stand(&"p4a"))
	assert_eq(trial.trace(), [&"g4a", &"p4a", &"g4b", &"spout"] as Array[StringName])
	var did := [false]
	trial.landed.connect(func() -> void: did[0] = true)
	assert_eq(trial.release(&"t4"), AshcrownTrial.OUT_LANDED)
	assert_true(trial.done and did[0], "the strike hits the anvil-stone")
	assert_false(trial.catch(&"t4"), "the trial is over")


func test_the_hint_comes_once_after_idle_time() -> void:
	var due := [0]
	trial.hint_due.connect(func() -> void: due[0] += 1)
	trial.advance(float(trial.data["hint_idle_sec"]) - 1.0)
	trial.turn(&"g1")
	trial.advance(float(trial.data["hint_idle_sec"]) - 1.0)
	assert_eq(due[0], 0, "a turn resets the idle clock")
	trial.advance(2.0)
	trial.advance(1000.0)
	assert_eq(due[0], 1, "once")


## Solves tiers before `index` the shortest way and leaves the strike charged at `index`.
func _to_tier(index: int) -> void:
	var solutions := {
		0: [&"g1"],
		1: [&"g2a", &"g2b", &"g2b", &"g2b"],
		2: [&"g3a", &"g3a", &"g3c", &"g3c", &"g3c"],
	}
	trial.catch(&"t1")
	for i in index:
		for g: StringName in solutions[i]:
			trial.turn(g)
		assert_eq(trial.release(trial.tier_id(i)), AshcrownTrial.OUT_NEXT, "tier %d solved" % (i + 1))
	assert_eq(trial.tier, index)
	assert_true(trial.charged)
