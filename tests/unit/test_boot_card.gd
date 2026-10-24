extends TestCase
## M2-ARC-03: the boot card (BootCard) covers the title while the boot warm-ups run and lifts only once they
## are done, and SceneRouter's reveal API (hold_reveal, measure_reveal, warm_fonts_now / fonts_ready) that
## boot.gd uses with it. The card is driven frame by frame through step(ms); the launch itself runs in a real
## process in test_scene_router_swap.gd (test_launch_reveals_the_title_only_after_the_warm_up).

const BOOT_SCRIPT := "res://game/core/boot.gd"
const FRAME_MS := 16.0
const LIFT_SEC := 0.35
const FADE_IN_SEC := 0.5
## M2-ARC-05: what Godot hands _process for a long stall (it caps delta at ~150 ms; M1-RND-29).
const CAPPED_DELTA_MS := 147.0
const STALL_MS := 500.0
const REAL_STALL_MS := 400.0
const USEC_PER_MS := 1000.0
## M2-ARC-08: a slow first launch on a fake clock (60 s of 500 ms frames, six times the old 10 s cap).
const SLOW_FRAMES := 120
const SLOW_FRAME_MS := 500.0
## One frame longer than the data's stall time-out (a synchronous driver compile), which still made progress.
const LONG_FRAME_MS := 12000.0
const TEST_STALL_MS := 3000.0
const TEST_CAP_MS := 20000.0
## M1-RND-29: the measured first launch (Low, RX 9070 XT); the cap must leave this much headroom over it.
const FIRST_RUN_MEASURED_MS := 9500.0
const CAP_HEADROOM := 10.0
## M2-ARC-12: Godot's ticks (CLOCK_MONOTONIC_RAW) run about 1% slow against the sleep clock under WSL2, so a
## real stall may read a little under its length. The test still tells a real stall from the ~150 ms capped delta.
const CLOCK_SKEW_TOLERANCE := 0.95

var _nodes: Array[Node] = []


## A clock the test moves by hand (microseconds).
class FakeClock:
	extends RefCounted

	var t := 1_000_000

	func now() -> int:
		return t


## A stand-in for the ShaderPrewarm warm-up: busy until `running` is false.
class Worker:
	extends Node

	var running := true

	func is_running() -> bool:
		return running


## M2-ARC-08: a warm-up that reports progress (ShaderPrewarm.wait_progress / progress_fraction) and can be
## cancelled (ShaderPrewarm.cancel).
class ProgressWorker:
	extends Worker

	var progress := 0
	var fraction := 0.0
	var cancelled := false

	func wait_progress() -> int:
		return progress

	func progress_fraction() -> float:
		return fraction

	func cancel() -> void:
		cancelled = true
		running = false


func _cover(fade_in: float = 0.0, lift: float = 0.0) -> BootCard:
	var card := BootCard.cover(_host(), fade_in, lift)
	_nodes.append(card)
	return card


func _worker() -> Worker:
	var w := Worker.new()
	_host().add_child(w)
	_nodes.append(w)
	return w


func _progress_worker() -> ProgressWorker:
	var w := ProgressWorker.new()
	_host().add_child(w)
	_nodes.append(w)
	return w


func _done() -> void:
	for n in _nodes:
		if is_instance_valid(n):
			n.free()
	_nodes.clear()


func test_the_card_is_opaque_at_once_above_the_game_and_blocks_the_mouse() -> void:
	var card := _cover()
	assert_eq(card.layer, BootCard.LAYER)
	assert_true(BootCard.LAYER < SceneRouter.FADE_LAYER, "under the router's fade")
	assert_eq(card.alpha(), 1.0, "opaque on its first frame")
	var rect := card.get_child(0) as ColorRect
	assert_eq(rect.mouse_filter, Control.MOUSE_FILTER_STOP, "clicks never reach the title under it")
	var clear := RenderingServer.get_default_clear_color()
	assert_eq(Color(rect.color, 1.0), Color(clear, 1.0), "the title's own background, nothing drawn on it")
	assert_true(card.is_waiting())
	assert_false(card.is_lifted())
	_done()


func test_it_never_opens_before_it_is_armed() -> void:
	var card := _cover()
	for i in 10:
		assert_false(card.step(FRAME_MS), "frame %d: not armed" % i)
	assert_true(card.is_waiting(), "work added a frame later (call_deferred) cannot be missed")
	card.arm()
	assert_true(card.step(FRAME_MS), "armed with no work: opens on the next frame")
	_done()


func test_it_waits_for_a_running_warm_up_and_for_a_freed_node() -> void:
	var card := _cover()
	var warm := _worker()
	var other := _worker()
	var opened: Array[Dictionary] = []
	card.opened.connect(func(s: Dictionary) -> void: opened.append(s))
	card.wait_for_node(warm)
	card.wait_for_node(other)
	card.wait_for_node(null)
	card.arm()
	for i in 3:
		assert_false(card.step(FRAME_MS), "both still running")
	warm.running = false
	assert_false(card.step(FRAME_MS), "the second one still runs")
	other.free()
	assert_true(card.step(FRAME_MS), "a freed node is done")
	assert_eq(opened.size(), 1, "opened once")
	assert_eq(int(opened[0]["reveal_wait_frames"]), 5)
	assert_between(float(opened[0]["reveal_wait_ms"]), 5 * FRAME_MS - 0.01, 5 * FRAME_MS + 0.01)
	assert_true(bool(opened[0]["reveal_work_done"]))
	_done()


func test_it_waits_for_its_conditions() -> void:
	var card := _cover()
	var flag := [false]
	card.wait_until(func() -> bool: return bool(flag[0]))
	card.arm()
	assert_false(card.step(FRAME_MS))
	flag[0] = true
	assert_true(card.step(FRAME_MS))
	_done()


func test_the_worst_hidden_frame_is_recorded() -> void:
	var card := _cover()
	var warm := _worker()
	card.wait_for_node(warm)
	card.arm()
	card.step(FRAME_MS)
	card.step(420.0)
	warm.running = false
	card.step(FRAME_MS)
	assert_eq(float(card.wait_stats()["reveal_wait_max_frame_ms"]), 420.0, "a stall under the card is hidden time")
	_done()


## M2-ARC-05: a frame stalled past Godot's ~150 ms delta cap shows at its true length, timed by the card's
## clock, whatever `delta` _process is handed.
func test_a_stall_past_the_delta_cap_is_reported_at_its_true_length() -> void:
	var fake := FakeClock.new()
	var card := _cover()
	card.clock = FrameClock.new(fake.now)
	card.clock.reset()
	var warm := _worker()
	card.wait_for_node(warm)
	card.arm()
	fake.t += int(FRAME_MS * USEC_PER_MS)
	card._process(FRAME_MS / BootCard.MSEC_PER_SEC)
	fake.t += int(STALL_MS * USEC_PER_MS)
	card._process(CAPPED_DELTA_MS / BootCard.MSEC_PER_SEC)
	var stats := card.wait_stats()
	assert_eq(float(stats["reveal_wait_max_frame_ms"]), STALL_MS, "the wall time, not the capped delta")
	assert_eq(float(stats["reveal_wait_ms"]), STALL_MS + FRAME_MS)
	assert_eq(int(stats["reveal_wait_frames"]), 2)
	_done()


## M2-ARC-05's acceptance: a real stall (OS.delay_msec) reads at least its length.
func test_a_real_stall_under_the_card_reads_at_least_its_length() -> void:
	var card := _cover()
	card.wait_for_node(_worker())
	card.arm()
	card._process(FRAME_MS / BootCard.MSEC_PER_SEC)
	OS.delay_msec(int(REAL_STALL_MS))
	card._process(CAPPED_DELTA_MS / BootCard.MSEC_PER_SEC)
	assert_true(
		float(card.wait_stats()["reveal_wait_max_frame_ms"]) >= REAL_STALL_MS * CLOCK_SKEW_TOLERANCE,
		"%s" % card.wait_stats()
	)
	_done()


## M2-ARC-05: the time-out is wall time too, so a few long stalls cannot stretch it past the stall time-out.
func test_the_time_out_counts_wall_time() -> void:
	var fake := FakeClock.new()
	var card := _cover()
	card.clock = FrameClock.new(fake.now)
	card.clock.reset()
	card.wait_for_node(_worker())
	card.arm()
	fake.t += int((card.wait.stall_ms + 1.0) * USEC_PER_MS)
	assert_true(card.step(card.clock.lap()), "one stalled frame past the stall time-out opens it")
	_done()


## M2-ARC-08: the wait's values come from data, and the safety cap is far above any measured first launch
## (9.5 s on Low, RX 9070 XT, M1-RND-29), so it never cuts a progressing one short.
func test_the_wait_values_come_from_data() -> void:
	var s := ProgressWait.load_settings()
	var card := _cover()
	assert_eq(card.wait.stall_ms, float(s["stall_timeout_ms"]))
	assert_eq(card.wait.max_ms, float(s["max_wait_ms"]))
	assert_true(card.wait.max_ms >= FIRST_RUN_MEASURED_MS * CAP_HEADROOM, "the cap is a safety net, not a budget")
	assert_true(card.wait.stall_ms < card.wait.max_ms)
	_done()


## M2-ARC-08's acceptance: a slow first launch that keeps progressing, on a fake clock, never opens the card
## however long it takes (here 60 s of 500 ms frames, six times the old cap), and opens once it is done.
func test_a_slow_but_progressing_warm_up_never_times_out() -> void:
	var fake := FakeClock.new()
	var card := _cover()
	card.clock = FrameClock.new(fake.now)
	card.clock.reset()
	var warm := _progress_worker()
	card.wait_for_node(warm)
	var opened: Array[Dictionary] = []
	card.opened.connect(func(s: Dictionary) -> void: opened.append(s))
	card.arm()
	for i in SLOW_FRAMES:
		fake.t += int(SLOW_FRAME_MS * USEC_PER_MS)
		warm.progress += 1
		card._process(CAPPED_DELTA_MS / BootCard.MSEC_PER_SEC)
	assert_true(card.is_waiting(), "60 s in, still progressing: still covered")
	assert_false(warm.cancelled)
	fake.t += int(LONG_FRAME_MS * USEC_PER_MS)
	warm.progress += 1
	card._process(CAPPED_DELTA_MS / BootCard.MSEC_PER_SEC)
	assert_true(card.is_waiting(), "one frame longer than the stall time-out that made progress is not a stall")
	warm.running = false
	fake.t += int(FRAME_MS * USEC_PER_MS)
	card._process(FRAME_MS / BootCard.MSEC_PER_SEC)
	assert_eq(opened.size(), 1)
	assert_true(bool(opened[0]["reveal_work_done"]))
	assert_eq(opened[0]["reveal_wait_end"], "done")
	_done()


## M2-ARC-08's acceptance: a warm-up whose progress stops opens the card after the stall time-out, unfinished,
## and is cancelled first so nothing stages under the title.
func test_a_stalled_warm_up_times_out_and_is_cancelled() -> void:
	var fake := FakeClock.new()
	var card := _cover()
	card.clock = FrameClock.new(fake.now)
	card.clock.reset()
	card.wait = ProgressWait.new(TEST_STALL_MS, TEST_CAP_MS)
	var warm := _progress_worker()
	card.wait_for_node(warm)
	var opened: Array[Dictionary] = []
	card.opened.connect(func(s: Dictionary) -> void: opened.append(s))
	card.arm()
	for i in 5:
		fake.t += int(SLOW_FRAME_MS * USEC_PER_MS)
		warm.progress += 1
		card._process(FRAME_MS / BootCard.MSEC_PER_SEC)
	var frames_to_stall := ceili(TEST_STALL_MS / SLOW_FRAME_MS)
	for i in frames_to_stall - 1:
		fake.t += int(SLOW_FRAME_MS * USEC_PER_MS)
		card._process(FRAME_MS / BootCard.MSEC_PER_SEC)
	assert_true(card.is_waiting(), "not yet a full stall time-out without progress")
	fake.t += int(SLOW_FRAME_MS * USEC_PER_MS)
	card._process(FRAME_MS / BootCard.MSEC_PER_SEC)
	assert_eq(opened.size(), 1, "the stall opens it")
	assert_false(bool(opened[0]["reveal_work_done"]))
	assert_eq(opened[0]["reveal_wait_end"], "stalled")
	assert_true(warm.cancelled, "the stalled warm-up is stopped before the title shows")
	_done()


## M2-ARC-08: the absolute safety cap opens the card even while the work progresses, and cancels it too.
func test_the_safety_cap_opens_a_progressing_wait() -> void:
	var card := _cover()
	card.wait = ProgressWait.new(TEST_STALL_MS, TEST_CAP_MS)
	var warm := _progress_worker()
	card.wait_for_node(warm)
	var opened: Array[Dictionary] = []
	card.opened.connect(func(s: Dictionary) -> void: opened.append(s))
	card.arm()
	var frames := ceili(TEST_CAP_MS / SLOW_FRAME_MS)
	for i in frames - 1:
		warm.progress += 1
		assert_false(card.step(SLOW_FRAME_MS), "frame %d: progressing, under the cap" % i)
	warm.progress += 1
	assert_true(card.step(SLOW_FRAME_MS), "the cap")
	assert_eq(opened[0]["reveal_wait_end"], "capped")
	assert_true(warm.cancelled)
	_done()


## M2-ARC-08: a condition with a progress Callable (the font warm-up) is not taken for a stalled one.
func test_a_condition_with_progress_keeps_the_card_waiting() -> void:
	var card := _cover()
	card.wait = ProgressWait.new(TEST_STALL_MS, TEST_CAP_MS)
	var units := [0]
	card.wait_until(func() -> bool: return false, func() -> int: return int(units[0]))
	card.arm()
	for i in int(TEST_STALL_MS / SLOW_FRAME_MS) * 2:
		units[0] = int(units[0]) + 1
		assert_false(card.step(SLOW_FRAME_MS), "frame %d: the units move" % i)
	var before := card.wait_progress()
	units[0] = int(units[0]) + 1
	assert_eq(card.wait_progress(), before + 1, "the condition's progress is in the card's count")
	_done()


## M2-ARC-08: the card's count moves when an item finishes, and SceneRouter sums it for the reveal hold.
func test_the_card_reports_its_progress_to_the_router() -> void:
	var card := _cover()
	var warm := _progress_worker()
	var plain := _worker()
	card.wait_for_node(warm)
	card.wait_for_node(plain)
	warm.progress = 7
	assert_eq(card.wait_progress(), 7, "the plain worker reports nothing until it is done")
	plain.running = false
	assert_eq(card.wait_progress(), 8, "a finished item counts one")
	var holders: Array[Object] = [card, RefCounted.new()]
	assert_eq(SceneRouter.holders_progress(holders), 8, "holders without wait_progress count 0")
	_done()


## M2-ARC-08: the first-launch cue. Only when asked (boot: ShaderPrewarm.first_run), one loc-keyed line and a
## bar of the warm-up's progress, invisible until its delay, then fading in; it lifts with the card.
func test_the_first_run_cue_is_quiet_and_only_on_request() -> void:
	var plain := _cover()
	plain.arm()
	assert_eq(plain.cue(), null, "no cue unless boot asks for one")
	var s := ProgressWait.load_settings()["cue"] as Dictionary
	var card := _cover(0.0, LIFT_SEC)
	var warm := _progress_worker()
	card.wait_for_node(warm)
	card.show_first_run_cue()
	var note := card.cue().get_node("Note") as Label
	assert_eq(note.text, tr(str(s["text_key"])), "the text is a loc key")
	assert_false(note.text == str(s["text_key"]), "and the key has a row")
	card.arm()
	warm.progress += 1
	card.step(float(s["delay_ms"]) - 1.0)
	assert_eq(card.cue_level(), 0.0, "nothing before the delay: a quick first launch shows no cue")
	warm.fraction = 0.5
	warm.progress += 1
	card.step(float(s["fade_in_ms"]) / 2.0 + 1.0)
	assert_between(card.cue_level(), 0.45, 0.55, "fading in")
	var fill := card.cue().get_node("Bar/Fill") as ColorRect
	assert_eq(fill.anchor_right, 0.5, "the bar shows the warm-up's progress")
	warm.fraction = 0.25
	warm.progress += 1
	card.step(FRAME_MS)
	assert_eq(fill.anchor_right, 0.5, "it never goes back")
	var level := card.cue_level()
	warm.running = false
	assert_true(card.step(FRAME_MS))
	card.step(LIFT_SEC * 500.0)
	assert_between(card.cue().modulate.a, level * 0.49, level * 0.51, "it lifts with the card")
	_done()


func test_boot_shows_the_cue_only_on_a_first_run() -> void:
	var src := (load(BOOT_SCRIPT) as GDScript).source_code
	assert_true(src.contains("if warm != null and warm.first_run:\n\t\t_card.show_first_run_cue()"))
	assert_true(src.contains('Callable(router, &"font_warm_progress")'), "the font warm-up reports progress")
	_done()


func test_it_lifts_over_its_lift_time_then_hides() -> void:
	var card := _cover(0.0, LIFT_SEC)
	var revealed := [0]
	card.revealed.connect(func() -> void: revealed[0] = int(revealed[0]) + 1)
	card.arm()
	assert_true(card.step(FRAME_MS))
	assert_eq(card.alpha(), 1.0, "the lift starts from opaque")
	assert_false(card.is_lifted())
	card.step(LIFT_SEC * 500.0)
	assert_between(card.alpha(), 0.49, 0.51, "half way")
	assert_eq(int(revealed[0]), 0)
	card.step(LIFT_SEC * 500.0)
	assert_true(card.is_lifted(), "lifted")
	assert_eq(card.alpha(), 0.0)
	assert_false(card.visible, "nothing of it is drawn")
	assert_eq((card.get_child(0) as ColorRect).mouse_filter, Control.MOUSE_FILTER_IGNORE)
	assert_eq(int(revealed[0]), 1)
	_done()


func test_a_zero_lift_is_a_cut_after_opened() -> void:
	var card := _cover()
	var order: Array[String] = []
	card.opened.connect(func(_s: Dictionary) -> void: order.append("opened"))
	card.revealed.connect(func() -> void: order.append("revealed"))
	card.arm()
	card.step(FRAME_MS)
	assert_eq(order, ["opened", "revealed"] as Array[String], "opened first, in the same frame")
	assert_true(card.is_lifted())
	_done()


func test_it_opens_after_its_time_out_with_the_work_unfinished() -> void:
	var card := _cover()
	card.wait_for_node(_worker())
	card.arm()
	var opened: Array[Dictionary] = []
	card.opened.connect(func(s: Dictionary) -> void: opened.append(s))
	assert_false(card.step(card.wait.stall_ms - 1.0), "a worker that reports no progress: the stall time-out")
	assert_true(card.step(1.0), "never hangs the title")
	assert_false(bool(opened[0]["reveal_work_done"]))
	_done()


func test_a_fade_in_covers_before_the_wait() -> void:
	var card := _cover(FADE_IN_SEC)
	var covered := [0]
	card.covered.connect(func() -> void: covered[0] = int(covered[0]) + 1)
	card.arm()
	assert_eq(card.alpha(), 0.0, "starts clear")
	assert_false(card.step(FADE_IN_SEC * 500.0), "never opens while fading in")
	assert_between(card.alpha(), 0.49, 0.51)
	card.step(FADE_IN_SEC * 500.0)
	assert_eq(card.alpha(), 1.0)
	assert_eq(int(covered[0]), 1, "covered fires once opaque")
	assert_true(card.step(FRAME_MS), "then the wait")
	_done()


func test_the_card_holds_the_router_reveal_until_it_opens() -> void:
	assert_true(SceneRouter.reveal_holders().is_empty(), "nothing holds the reveal at rest")
	var card := _cover()
	card.hold_reveal_of(SceneRouter)
	assert_eq(SceneRouter.reveal_holders(), [card] as Array[Object])
	card.arm()
	card.step(FRAME_MS)
	assert_true(SceneRouter.reveal_holders().is_empty(), "released when it opens")
	var other := _cover()
	other.hold_reveal_of(SceneRouter)
	other.free()
	assert_true(SceneRouter.reveal_holders().is_empty(), "a freed card drops out")
	_done()


func test_reveal_hold_is_generic_like_the_swap_hold() -> void:
	var a := RefCounted.new()
	SceneRouter.hold_reveal(a)
	SceneRouter.hold_reveal(a)
	assert_eq(SceneRouter.reveal_holders().size(), 1, "holding twice is one hold")
	SceneRouter.release_reveal(a)
	assert_true(SceneRouter.reveal_holders().is_empty())
	SceneRouter.hold_reveal(null)
	assert_true(SceneRouter.reveal_holders().is_empty())
	assert_true(SceneRouter.swap_holders().is_empty(), "the reveal hold is not the swap hold")
	_done()


func test_the_reveal_wait_is_hidden_time_against_one_second() -> void:
	var stats := {}
	var ok := SceneRouter.judge_reveal_wait(stats, 40, 900.0, 300.0)
	assert_true(ok.is_empty(), "a 300 ms frame under the fade is loading time")
	assert_eq(stats["reveal_wait_frames"], 40)
	assert_eq(stats["reveal_wait_ms"], 900.0)
	assert_eq(stats["reveal_wait_max_frame_ms"], 300.0)
	var over := SceneRouter.judge_reveal_wait(stats, 3, 1500.0, SceneRouter.HIDDEN_FRAME_BUDGET_MS + 1.0)
	assert_eq(over.size(), 1, "a hidden frame over 1 s warns")
	_done()


func test_measure_reveal_starts_a_visible_window_with_the_card_stats() -> void:
	var saved := SceneRouter.last_swap_stats
	var card := _cover()
	var stats := SceneRouter.measure_reveal("res://game/core/boot.tscn", card.is_lifted, {"reveal_wait_ms": 12.0})
	assert_true(SceneRouter.is_measuring(), "the window runs")
	assert_true(bool(stats["reveal"]))
	assert_eq(stats["scene_path"], "res://game/core/boot.tscn")
	assert_eq(stats["reveal_wait_ms"], 12.0, "the card's wait stats are kept")
	assert_true(SceneRouter.last_swap_stats == stats, "it is the router's last stats")
	SceneRouter.cancel_visible_window()
	assert_false(SceneRouter.is_measuring(), "cancelled")
	SceneRouter.last_swap_stats = saved
	_done()


func test_fonts_ready_follows_the_font_warm_switch() -> void:
	var saved := SceneRouter.warm_fonts
	SceneRouter.warm_fonts = false
	assert_true(SceneRouter.fonts_ready(), "nothing will warm them: ready")
	SceneRouter.warm_fonts_now()
	assert_true(SceneRouter.fonts_ready())
	SceneRouter.warm_fonts = saved
	_done()


func test_boot_covers_the_title_only_as_the_game_scene() -> void:
	var src := (load(BOOT_SCRIPT) as GDScript).source_code
	assert_true(src.contains("if is_game_scene():\n\t\t_cover_until_warm()"), "the card only in the game")
	assert_true(src.contains("_title.set_process_unhandled_input(false)"), "the title takes no keys under it")
	assert_true(src.contains("measure_reveal"), "the router measures the reveal at launch")
	assert_true(src.contains("hold_reveal_of(router)"), "and holds a change's fade")
	assert_true(src.contains("warm_fonts_now"), "the font warm-up runs under the card")
	_done()


func test_graphics_runtime_exposes_the_running_warm_up() -> void:
	var warm := GraphicsRuntime.warm_resident_shaders(_host())
	assert_true(warm != null and warm.is_running(), "the warm-up runs")
	assert_true(GraphicsRuntime.current_warm_up() == warm, "a caller that did not spawn it can wait for it")
	warm.free()
	assert_eq(GraphicsRuntime.current_warm_up(), null, "none once it is gone")
	_done()


func _host() -> Node:
	return (Engine.get_main_loop() as SceneTree).current_scene
