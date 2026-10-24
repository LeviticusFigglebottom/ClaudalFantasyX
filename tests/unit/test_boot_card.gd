extends TestCase
## M2-ARC-03: the boot card (BootCard) covers the title while the boot warm-ups run and lifts only once they
## are done, and SceneRouter's reveal API (hold_reveal, measure_reveal, warm_fonts_now / fonts_ready) that
## boot.gd uses with it. The card is driven frame by frame through step(ms); the launch itself runs in a real
## process in test_scene_router_swap.gd (test_launch_reveals_the_title_only_after_the_warm_up).

const BOOT_SCRIPT := "res://game/core/boot.gd"
const FRAME_MS := 16.0
const LIFT_SEC := 0.35
const FADE_IN_SEC := 0.5

var _nodes: Array[Node] = []


## A stand-in for the ShaderPrewarm warm-up: busy until `running` is false.
class Worker:
	extends Node

	var running := true

	func is_running() -> bool:
		return running


func _cover(fade_in: float = 0.0, lift: float = 0.0) -> BootCard:
	var card := BootCard.cover(_host(), fade_in, lift)
	_nodes.append(card)
	return card


func _worker() -> Worker:
	var w := Worker.new()
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
	assert_false(card.step(BootCard.MAX_WAIT_MS - 1.0))
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
