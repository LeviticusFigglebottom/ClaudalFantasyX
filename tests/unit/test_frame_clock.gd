extends TestCase
## M2-ARC-05: FrameClock times frames by wall clock, so a frame stalled past Godot's ~150 ms process-delta cap
## (M1-RND-29) is reported at its true length. Driven by a fake clock; BootCard's use of it is pinned in
## test_boot_card.gd, the router's VisibleWindow here.

## What Godot reports as `delta` for a long stall (M1-RND-29: a 500 ms stall reads 135-147 ms).
const CAPPED_DELTA_MS := 147.0
const STALL_MS := 500.0
const FRAME_MS := 16.0
const USEC := 1000
## M2-ARC-12: Godot's ticks (CLOCK_MONOTONIC_RAW) run about 1% slow against the sleep clock under WSL2, so a
## real stall may read a little under its length. The test still tells a real stall from the ~150 ms capped delta.
const CLOCK_SKEW_TOLERANCE := 0.95


## A clock the test moves by hand.
class FakeClock:
	extends RefCounted

	var t := 1_000_000

	func now() -> int:
		return t

	func advance_ms(ms: float) -> void:
		t += int(ms * USEC)


func test_a_lap_is_the_wall_time_since_the_last_mark() -> void:
	var fake := FakeClock.new()
	var clock := FrameClock.new(fake.now)
	clock.reset()
	fake.advance_ms(FRAME_MS)
	assert_eq(clock.lap(), FRAME_MS)
	fake.advance_ms(STALL_MS)
	var stalled := clock.lap()
	assert_eq(stalled, STALL_MS, "a stall reads at its true length")
	assert_true(stalled > CAPPED_DELTA_MS, "past the delta cap")
	fake.advance_ms(FRAME_MS)
	assert_eq(clock.lap(), FRAME_MS, "each lap starts at the previous one")


func test_an_unstarted_clock_only_marks() -> void:
	var fake := FakeClock.new()
	var clock := FrameClock.new(fake.now)
	assert_false(clock.is_started())
	assert_eq(clock.since_ms(), 0.0)
	assert_eq(clock.lap(), 0.0, "no mark yet: the first lap is 0")
	assert_true(clock.is_started())
	fake.advance_ms(FRAME_MS)
	assert_eq(clock.lap(), FRAME_MS)


func test_since_ms_reads_without_moving_the_mark() -> void:
	var fake := FakeClock.new()
	var clock := FrameClock.new(fake.now)
	clock.reset()
	fake.advance_ms(FRAME_MS)
	assert_eq(clock.since_ms(), FRAME_MS)
	fake.advance_ms(FRAME_MS)
	assert_eq(clock.since_ms(), FRAME_MS * 2.0)
	assert_eq(clock.lap(), FRAME_MS * 2.0)


func test_explicit_timestamps() -> void:
	var clock := FrameClock.new()
	clock.reset_at(2_000)
	assert_eq(clock.lap_at(2_000 + int(STALL_MS) * USEC), STALL_MS)
	assert_eq(FrameClock.ms_between(0, 1_500), 1.5)


func test_the_default_clock_is_ticks_usec() -> void:
	var clock := FrameClock.new()
	var before := Time.get_ticks_usec()
	var now := clock.now_usec()
	assert_true(now >= before and now <= Time.get_ticks_usec(), "reads Time.get_ticks_usec")


## Boot-smoke fix: the default clock keeps no Callable to the Time singleton (a FrameClock left in a coroutine
## suspended at quit pinned it past Godot's exit check), and the router keeps its clocks as members.
func test_the_default_clock_holds_no_callable_and_the_router_no_clock_locals() -> void:
	assert_false(FrameClock.new()._now.is_valid(), "the default calls Time.get_ticks_usec() directly")
	var src := (load("res://game/core/scene_router.gd") as GDScript).source_code
	assert_false(src.contains("var clock := FrameClock.new()"), "no FrameClock local in the router's coroutines")
	assert_true(src.contains("var _reveal_clock := FrameClock.new()"), "the reveal wait's clock is the router's")
	assert_true(src.contains("var _swap_clock := FrameClock.new()"), "the swap's clock is the router's")


func test_a_real_stall_reads_past_the_cap() -> void:
	var clock := FrameClock.new()
	clock.reset()
	OS.delay_msec(int(STALL_MS * 0.8))
	assert_true(clock.lap() >= STALL_MS * 0.8 * CLOCK_SKEW_TOLERANCE, "the wall clock sees the whole stall")


func test_the_router_visible_window_reports_a_stall_at_its_length() -> void:
	var fake := FakeClock.new()
	var w := SceneRouter.VisibleWindow.new(fake.now())
	fake.advance_ms(STALL_MS)
	w.tick(fake.now(), true)
	assert_eq(w.frame_ms[0], STALL_MS)
	var stats := {}
	assert_eq(SceneRouter.judge_visible(stats, w).size(), 1, "over the 50 ms visible budget")
	assert_eq(stats["max_visible_frame_ms"], STALL_MS)
