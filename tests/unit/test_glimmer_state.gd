extends TestCase
## M1-RND-02: GlimmerState, the pure glimmer state machine (modes, the 1.5 s release, signals).

const DURATION := 1.5
const HALF := 0.75
const STEP := 0.05
const EPS := 1e-5

var st: GlimmerState
var events: Array[String] = []


func before_each() -> void:
	st = GlimmerState.new()
	events.clear()
	st.mode_changed.connect(func(m: GlimmerState.Mode) -> void: events.append("mode:%s" % GlimmerState.mode_name(m)))
	st.release_started.connect(func(d: float) -> void: events.append("start:%s" % str(d)))
	st.release_finished.connect(func() -> void: events.append("finish"))


func test_starts_held_and_free() -> void:
	assert_eq(st.mode, GlimmerState.Mode.HELD)
	assert_eq(st.release_blend, 0.0)
	assert_eq(st.machine_amount, 0.0)
	assert_false(st.is_releasing())
	assert_eq(st.release_progress(), 0.0)
	assert_eq(GlimmerState.new(GlimmerState.Mode.MACHINE).machine_amount, 1.0, "initial mode argument")


func test_set_mode_is_immediate_and_signals_only_on_change() -> void:
	st.set_mode(GlimmerState.Mode.RELEASED)
	assert_eq(st.release_blend, 1.0)
	assert_eq(st.machine_amount, 0.0)
	st.set_mode(GlimmerState.Mode.MACHINE)
	assert_eq(st.release_blend, 0.0)
	assert_eq(st.machine_amount, 1.0)
	st.set_mode(GlimmerState.Mode.MACHINE)
	assert_eq(events, ["mode:released", "mode:machine"] as Array[String])


func test_release_from_held_eases_over_the_duration() -> void:
	assert_true(st.release(DURATION))
	assert_eq(st.mode, GlimmerState.Mode.RELEASED, "mode reads released from the first frame")
	assert_true(st.is_releasing())
	assert_eq(st.release_blend, 0.0, "nothing has moved before the first advance")
	var last := 0.0
	var t := 0.0
	while t + STEP < HALF - EPS:
		st.advance(STEP)
		t += STEP
		assert_true(st.release_blend >= last, "blend never goes backwards")
		last = st.release_blend
	st.advance(HALF - t)
	assert_between(st.release_progress(), 0.5 - EPS, 0.5 + EPS)
	assert_between(st.release_blend, 0.5 - EPS, 0.5 + EPS, "smoothstep(0.5) = 0.5")
	st.advance(HALF)
	assert_false(st.is_releasing())
	assert_eq(st.release_blend, 1.0)
	assert_eq(st.release_progress(), 1.0)
	assert_eq(events, ["start:1.5", "mode:released", "finish"] as Array[String])


func test_release_is_ignored_when_already_released_or_releasing() -> void:
	st.set_mode(GlimmerState.Mode.RELEASED)
	assert_false(st.release(DURATION))
	st.set_mode(GlimmerState.Mode.HELD)
	assert_true(st.release(DURATION))
	assert_false(st.release(DURATION), "second call during the transition")


func test_release_from_machine_frees_the_bound_motes() -> void:
	st.set_mode(GlimmerState.Mode.MACHINE)
	st.release(DURATION)
	st.advance(HALF)
	assert_between(st.machine_amount, 0.5 - EPS, 0.5 + EPS)
	assert_between(st.release_blend, 0.5 - EPS, 0.5 + EPS)
	st.advance(DURATION)
	assert_eq(st.machine_amount, 0.0)
	assert_eq(st.release_blend, 1.0)


func test_zero_duration_releases_on_the_spot() -> void:
	assert_true(st.release(0.0))
	assert_false(st.is_releasing())
	assert_eq(st.release_blend, 1.0)
	assert_eq(events, ["start:0.0", "mode:released", "finish"] as Array[String])


func test_set_mode_during_a_release_cancels_or_completes_it() -> void:
	st.release(DURATION)
	st.advance(HALF)
	st.set_mode(GlimmerState.Mode.HELD)
	assert_false(st.is_releasing())
	assert_eq(st.release_blend, 0.0, "cancelled back to held")
	st.release(DURATION)
	st.advance(HALF)
	events.clear()
	st.set_mode(GlimmerState.Mode.RELEASED)
	assert_false(st.is_releasing())
	assert_eq(st.release_blend, 1.0, "completed")
	assert_eq(events, ["finish"] as Array[String], "already released: no mode_changed")


func test_advance_ignores_negative_time_and_idle_states() -> void:
	st.advance(1.0)
	assert_eq(st.release_blend, 0.0)
	st.release(DURATION)
	st.advance(-1.0)
	assert_eq(st.release_progress(), 0.0)


func test_shader_state_exposes_the_transition_endpoints() -> void:
	var idle := st.shader_state()
	assert_eq(idle, {"blend_from": 0.0, "blend_to": 0.0, "machine_from": 0.0, "machine_to": 0.0, "progress": 1.0})
	st.set_mode(GlimmerState.Mode.MACHINE)
	st.release(DURATION)
	st.advance(HALF)
	var mid := st.shader_state()
	assert_eq(mid["blend_from"], 0.0)
	assert_eq(mid["blend_to"], 1.0)
	assert_eq(mid["machine_from"], 1.0)
	assert_eq(mid["machine_to"], 0.0)
	assert_between(float(mid["progress"]), 0.5 - EPS, 0.5 + EPS)


func test_blend_color_hits_the_palette_endpoints() -> void:
	var held := Color("#7FC6D9")
	var released := Color("#FFE9B8")
	var machine := Color("#4FB3B0")
	assert_eq(st.blend_color(held, released, machine), held)
	st.set_mode(GlimmerState.Mode.RELEASED)
	assert_eq(st.blend_color(held, released, machine), released)
	st.set_mode(GlimmerState.Mode.MACHINE)
	assert_eq(st.blend_color(held, released, machine), machine)


func test_mode_names_round_trip() -> void:
	for m: int in GlimmerState.Mode.values():
		assert_eq(GlimmerState.mode_from_name(GlimmerState.mode_name(m)), m)
	assert_eq(GlimmerState.mode_from_name("Released"), GlimmerState.Mode.RELEASED)
	assert_eq(GlimmerState.mode_from_name("fireflies"), -1)
