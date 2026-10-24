extends TestCase
## M2-BPR-05 part 1: the encounter stinger (BattleStinger, game/data/flow/battle_transition.json) and the
## opening banner's timing. The data loads and names real swatches; the stinger is short, sits under the
## router's fade layer and never flashes past battle_vfx's cap; reduced motion is a plain cross-fade with
## no shader; BattleRequest.submit plays it before the router's change; the opening banner's timings are
## data and it waits (holding the battle) while the router's fade still covers the screen.

const PALETTE := "res://docs/kb/art/palette.json"
const EFFECTS := "res://game/data/vfx/battle/effects.json"
## The brief: about 0.6-0.9 s of stinger before the router's fade.
const MIN_SEC := 0.6
const MAX_SEC := 0.9
const SANDBOX := "res://game/battle/scene/battle_sandbox.tscn"
const BANNER_TIMINGS: Array[String] = ["fade_in_sec", "hold_sec", "fade_out_sec", "reveal_wait_max_sec"]
const STEP_SEC := 0.05
const EPS := 1e-5

var ctl: BattleController


func test_data_loads_and_names_real_swatches() -> void:
	var c := BattleStinger.load_config()
	assert_false(c.is_empty(), "battle_transition loads")
	assert_true(bool(c["enabled"]), "on in the game")
	assert_true(ResourceLoader.exists(str(c["shader"])), "the tide-line shader exists")
	var swatches := (JSON.parse_string(FileAccess.get_file_as_string(PALETTE)) as Dictionary)["swatches"] as Dictionary
	var names := c["swatches"] as Dictionary
	for key in BattleStinger.COLOR_UNIFORMS:
		assert_true(swatches.has(names.get(key, "")), "%s names a palette swatch" % key)
		var hex := str((swatches.get(names.get(key, ""), {}) as Dictionary).get("hex", ""))
		assert_eq(str(c[key]).to_upper(), hex.to_upper(), "%s is its swatch's hex" % key)
	var rm := c[BattleStinger.KEY_REDUCED] as Dictionary
	assert_true(names.has(rm["color"]), "the cross-fade colour is one of the swatches")
	for key in BattleStinger.FLOAT_UNIFORMS:
		assert_true(c.has(key), "data sets uniform %s" % key)


func test_durations_fit_the_brief_and_the_rise_eases_to_full() -> void:
	var c := BattleStinger.load_config()
	assert_between(BattleStinger.duration(c, false), MIN_SEC, MAX_SEC, "the stinger's length")
	assert_between(BattleStinger.duration(c, true), 0.0, MAX_SEC, "reduced motion is no longer")
	assert_eq(BattleStinger.rise_at(c, 0.0), 0.0, "starts at the bottom edge")
	var rise := float(c["rise_sec"])
	assert_eq(BattleStinger.rise_at(c, rise), 1.0, "full at rise_sec")
	assert_eq(BattleStinger.rise_at(c, BattleStinger.duration(c, false)), 1.0, "held through the hold")
	assert_true(BattleStinger.rise_at(c, rise * 0.5) > 0.5, "eases out: past half way at half time")


func test_it_never_flashes_and_sits_under_the_router_fade() -> void:
	var c := BattleStinger.load_config()
	var safety := (JSON.parse_string(FileAccess.get_file_as_string(EFFECTS)) as Dictionary)["safety"] as Dictionary
	var cap := float(safety["flash_max_alpha"])
	assert_true(float(c["foam_alpha"]) <= cap, "the foam crest is under the flash cap")
	assert_true(int(c["layer"]) < SceneRouter.FADE_LAYER, "the router's fade covers it")
	assert_true(float(c["dim"]) >= 0.0, "it only darkens the field")


func test_the_stinger_plays_the_tide_line_and_finishes_once() -> void:
	var s := BattleStinger.make(false)
	var fired: Array[int] = [0]
	s.finished.connect(func() -> void: fired[0] += 1)
	_root().add_child(s)
	s.set_process(false)
	assert_eq(s.layer, int(s.cfg["layer"]))
	var mat := s.material_in_use()
	assert_true(mat != null and mat.shader != null, "the tide-line shader")
	assert_eq(float(mat.get_shader_parameter(&"crest")), float(s.cfg["crest"]), "uniforms come from data")
	assert_eq(float(mat.get_shader_parameter(BattleStinger.U_PROGRESS)), 0.0)
	var total := BattleStinger.duration(s.cfg, false)
	var guard := 0
	while not s.done and guard < 100:
		s.advance(STEP_SEC)
		guard += 1
	assert_true(s.done, "done after its duration")
	assert_between(s.elapsed, total, total + STEP_SEC, "no longer than the data says")
	assert_eq(float(mat.get_shader_parameter(BattleStinger.U_PROGRESS)), 1.0, "risen")
	s.advance(STEP_SEC)
	assert_eq(fired[0], 1, "finished fires once")
	s.free()


func test_reduced_motion_is_a_plain_crossfade() -> void:
	var s := BattleStinger.make(true)
	_root().add_child(s)
	s.set_process(false)
	assert_true(s.material_in_use() == null, "no shader: no sweep, no ripple")
	assert_eq(s.overlay().color.a, 0.0, "starts clear")
	var rm := s.cfg[BattleStinger.KEY_REDUCED] as Dictionary
	s.advance(float(rm["crossfade_sec"]) * 0.5)
	assert_between(s.overlay().color.a, 0.0, float(rm["alpha"]), "fading")
	s.advance(float(rm["crossfade_sec"]))
	assert_between(s.overlay().color.a, float(rm["alpha"]) - EPS, float(rm["alpha"]) + EPS, "held at its alpha")
	var deep := Color(str(s.cfg[str(rm["color"])]))
	assert_true(Color(s.overlay().color, 1.0).is_equal_approx(deep), "in the deep swatch")
	s.advance(float(rm["hold_sec"]))
	assert_true(s.done, "then done")
	s.free()


func test_an_encounter_bark_shows_its_line_holds_longer_and_tells_audio() -> void:
	var c := BattleStinger.load_config().duplicate(true)
	var row := {"line_key": "HUD_TL_NEXT", "speaker_key": "HUD_TL_NOW", "hold_extra_sec": 0.8}
	(c[BattleStinger.KEY_BARKS] as Dictionary)["rows"] = {"ch02_tideline": row}
	var heard: Array = []
	var on_event := func(ev: StringName, args: Array) -> void: heard.append([ev, args])
	EventBus.dialogue_event.connect(on_event)
	var s := BattleStinger.make(false, c, &"ch02_tideline")
	_root().add_child(s)
	s.set_process(false)
	assert_true(s.bark_label() != null, "the line shows over the water")
	assert_true(s.bark_label().text.contains(tr("HUD_TL_NEXT")), "the bark's line")
	assert_eq(heard.size(), 1, "audio hears it once")
	assert_eq(heard[0][0], BattleStinger.BARK_EVENT)
	assert_eq(heard[0][1][1], "HUD_TL_NEXT")
	var plain := BattleStinger.duration(c, false)
	assert_between(BattleStinger.duration(c, false, row), plain + 0.8 - EPS, plain + 0.8 + EPS, "held longer to read")
	s.advance(plain + EPS)
	assert_false(s.done, "still holding for the bark")
	EventBus.dialogue_event.disconnect(on_event)
	s.free()
	var none := BattleStinger.make(false, c, &"drownbell")
	assert_eq(none.bark, {}, "no row, no bark")
	none.free()


func test_the_request_plays_the_stinger_before_the_router_change() -> void:
	var calls: Array[String] = []
	BattleRequest.change_scene = Callable()
	BattleRequest.play_stinger = func() -> void: calls.append("stinger")
	FlowRouting.record = func(change: Array) -> void: calls.append("change:%s" % str(change[0]))
	BattleRequest.start(&"ch02_tideline", &"ch02/haluna", &"BattleReturn")
	assert_eq(calls, ["stinger", "change:%s" % BattleRequest.scene_path()], "stinger first, then the change")
	assert_true(BattleRequest.pending() != null, "the request waits for the battle scene")
	BattleRequest.play_stinger = Callable()
	FlowRouting.record = Callable()
	BattleRequest.clear()


func test_a_recorded_change_skips_the_stinger() -> void:
	var calls: Array[String] = []
	BattleRequest.change_scene = func(_p: String) -> void: calls.append("change")
	BattleRequest.play_stinger = func() -> void: calls.append("stinger")
	BattleRequest.start(&"ch02_tideline", &"ch02/haluna", &"BattleReturn")
	assert_eq(calls, ["change"], "tests that record the change get no stinger")
	BattleRequest.change_scene = Callable()
	BattleRequest.play_stinger = Callable()
	BattleRequest.clear()


func test_banner_timings_are_data() -> void:
	var m := HudLayout.section(&"opening_banner")
	for key in BANNER_TIMINGS:
		assert_true(m.has(key) and float(m[key]) > 0.0, "opening_banner.%s" % key)


func test_the_banner_waits_for_the_fade_and_holds_the_battle() -> void:
	_sandbox()
	var banner := ctl.hud.opening_banner()
	var covered: Array[bool] = [true]
	banner.screen_covered = func() -> bool: return covered[0]
	banner.show_opening(BattleOpening.AMBUSH, true)
	assert_true(banner.is_pending(), "waits while the router's fade is up")
	assert_eq(banner.modulate.a, 0.0, "unseen meanwhile")
	assert_true(ctl.hud.holds_battle(), "the first foe does not act unseen")
	banner.step_pending(STEP_SEC)
	assert_true(banner.is_pending(), "still covered")
	covered[0] = false
	banner.step_pending(STEP_SEC)
	assert_false(banner.is_pending(), "plays once the fade has lifted")
	assert_false(ctl.hud.holds_battle(), "the battle goes on")
	assert_true(banner.is_showing())
	_free()


func test_the_banner_gives_up_waiting_after_its_cap() -> void:
	_sandbox()
	var banner := ctl.hud.opening_banner()
	banner.screen_covered = func() -> bool: return true
	banner.show_opening(BattleOpening.PREEMPTIVE, true)
	banner.step_pending(HudLayout.num(HudLayout.section(&"opening_banner"), "reveal_wait_max_sec"))
	assert_false(banner.is_pending(), "never waits forever")
	_free()


func test_an_uncovered_or_instant_banner_never_waits() -> void:
	_sandbox()
	var banner := ctl.hud.opening_banner()
	banner.screen_covered = func() -> bool: return false
	banner.show_opening(BattleOpening.AMBUSH, true)
	assert_false(banner.is_pending(), "nothing covers the screen: it plays at once")
	banner.screen_covered = func() -> bool: return true
	banner.show_opening(BattleOpening.AMBUSH, false)
	assert_false(banner.is_pending(), "instant pacing (captures) holds it shown, no wait")
	assert_eq(banner.modulate.a, 1.0)
	_free()


# --- helpers -------------------------------------------------------------------------------------


func _root() -> Node:
	var tree := Engine.get_main_loop() as SceneTree
	return tree.current_scene if tree.current_scene != null else tree.root


func _sandbox() -> void:
	ctl = (load(SANDBOX) as PackedScene).instantiate() as BattleController
	ctl.auto_start = false
	ctl.pacing_scale = 0.0
	ctl.persist_progress = false
	_root().add_child(ctl)
	ctl.hud.apply_settings(UiSettings.new())
	ctl.start_fixture(BattleFixture.load_fixture(&"read_panel"))


func _free() -> void:
	if ctl != null:
		ctl.get_parent().remove_child(ctl)
		ctl.free()
		ctl = null
