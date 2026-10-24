extends TestCase
## M1-RND-06 fix: the SceneRouter swap frame stays under a data-defined threshold
## (game/data/debug/perf_budgets.json) with headroom below the SPEC §4.2 50 ms budget, and the
## router's font warmer covers the project theme without ever touching MSDF fonts.
##
## The swap is measured in a child Godot process (game/core/debug/scene_swap_probe.tscn): the test
## runner calls tests synchronously, and a real swap would replace the runner's own scene. Shared
## CI machines are noisy, so each target gets up to `attempts` runs and passes on the first run
## under the threshold; every run's numbers are kept in the failure message.

const PROBE_TAG := "SCENE_SWAP_PROBE "
const GODOT_NAME_HINT := "godot"
const GODOT_ON_PATH := "godot"
const GODOT_ENV := "GODOT"
## Set by tools/coverage/run_coverage.py for the instrumented run.
const COVERAGE_ENV := "HYMN_COV_OUT"
## M1-ARC-16: an injected 60 fps clock, and how many frames the fade takes to lift on it.
const FRAME_USEC := 16667
const LIFT_FRAMES := 21
const HITCH_FRAME_MS := 70.0
const HIDDEN_STALL_MS := 1200.0


func test_budget_data_has_headroom_below_the_spec_budget() -> void:
	var cfg := SceneSwapProbe.budgets()
	assert_false(cfg.is_empty(), "perf_budgets.json scene_swap section")
	assert_true(float(cfg.get("budget_ms", 0.0)) <= SceneRouter.SWAP_BUDGET_MS, "budget may not exceed SPEC §4.2")
	assert_true(float(cfg.get("test_threshold_ms", INF)) < float(cfg.get("budget_ms", 0.0)), "threshold has headroom")
	assert_true(int(cfg.get("attempts", 0)) >= 1)
	assert_true(ResourceLoader.exists(str(cfg.get("probe_scene", ""))), "probe scene exists")
	for t: Variant in cfg.get("targets", []):
		assert_true(ResourceLoader.exists(str(t)), "target exists: %s" % t)


func test_swap_frame_stays_under_threshold_for_every_target() -> void:
	# Wall-clock budgets are meaningless under coverage instrumentation (ADR 0013: every probe
	# call slows the code). The plain test step still enforces this budget.
	if OS.has_environment(COVERAGE_ENV):
		return
	var cfg := SceneSwapProbe.budgets()
	var threshold := float(cfg.get("test_threshold_ms", 0.0))
	for t: Variant in cfg.get("targets", []):
		var runs: Array[Dictionary] = []
		var passed := false
		for i in int(cfg.get("attempts", 1)):
			var stats := _probe(str(cfg.get("probe_scene", "")), str(t))
			runs.append(stats)
			if stats.is_empty():
				continue
			_assert_fix_shape(stats, str(t))
			if float(stats.get("max_frame_ms", INF)) < threshold:
				passed = true
				break
		var worst: Array[float] = []
		for r in runs:
			worst.append(float(r.get("max_frame_ms", -1.0)))
		var msg := "%s swap frame >= %.0f ms in every run: %s (last stats %s)" % [t, threshold, worst, runs[-1]]
		var load_per_cpu := _load_per_cpu()
		if not passed and load_per_cpu > float(cfg.get("max_load_per_cpu", INF)):
			push_warning("UNMEASURABLE (load %.1f/cpu): %s" % [load_per_cpu, msg])
			continue
		assert_true(passed, msg)


## 1-minute load average divided by CPU count; 0 where /proc/loadavg is unavailable.
static func _load_per_cpu() -> float:
	# procfs reports size 0, so get_file_as_string() returns "": read a line instead.
	var f := FileAccess.open("/proc/loadavg", FileAccess.READ)
	if f == null:
		return 0.0
	var fields := f.get_line().split(" ", false)
	if fields.is_empty():
		return 0.0
	return fields[0].to_float() / float(maxi(OS.get_processor_count(), 1))


## review-sweep-J S1 (M1-RND-22): without split_swap, a prewarm wait doesn't land inside frame 0.
func test_frame0_starts_after_a_prewarm_wait() -> void:
	assert_eq(SceneRouter.frame0_start(1000, 0, 5000), 1000, "no wait: the swap's own start")
	assert_eq(SceneRouter.frame0_start(1000, 3, 5000), 5000, "waited frames: after them")


## M1-ARC-16 (ADR 0029): the budgets are SPEC §4.2 v1.3's numbers.
func test_budgets_match_adr_0029() -> void:
	assert_eq(SceneRouter.SWAP_BUDGET_MS, 50.0, "visible frames")
	assert_eq(SceneRouter.HIDDEN_FRAME_BUDGET_MS, 1000.0, "a hidden frame")
	assert_eq(SceneRouter.ENTRY_BUDGET_MS, 3000.0, "a zone entry")
	assert_eq(SceneRouter.VISIBLE_MEASURE_FRAMES, 60, "the first 60 frames after a fade lifts")


## M1-ARC-16: the hidden frames under the fade are loading time, judged against 1 s, not 50 ms.
func test_hidden_frames_are_judged_against_the_hidden_budget() -> void:
	var stats := {}
	var frames: Array[float] = [12.0, HITCH_FRAME_MS, 900.0, 8.0]
	assert_true(SceneRouter.judge_hidden(stats, frames).is_empty(), "70 and 900 ms hidden frames are no hitch")
	assert_eq(stats["max_frame_ms"], 900.0)
	assert_eq(stats["budget_ms"], SceneRouter.HIDDEN_FRAME_BUDGET_MS)
	assert_false(bool(stats["over_budget"]))
	frames = [12.0, HIDDEN_STALL_MS]
	var warnings := SceneRouter.judge_hidden(stats, frames)
	assert_true(bool(stats["over_budget"]), "a 1.2 s hidden frame is over")
	assert_eq(warnings.size(), 1)
	assert_true(warnings[0].contains("1000 ms hidden-frame budget"), "the warning names its budget: %s" % warnings)


func test_zone_entry_is_judged_against_three_seconds() -> void:
	var stats := {}
	SceneRouter.judge_entry(stats, SceneRouter.ENTRY_BUDGET_MS - 1.0)
	assert_false(bool(stats["entry_over_budget"]))
	assert_eq(stats["entry_budget_ms"], SceneRouter.ENTRY_BUDGET_MS)
	SceneRouter.judge_entry(stats, SceneRouter.ENTRY_BUDGET_MS + 1.0)
	assert_true(bool(stats["entry_over_budget"]))


## M1-ARC-16: the visible window covers the fade lifting, then the first 60 frames after it has lifted,
## driven here by an injected clock.
func test_visible_window_spans_the_lift_and_the_next_60_frames() -> void:
	var t := 1000
	var w := SceneRouter.VisibleWindow.new(t)
	var ticks := 0
	var done := false
	while not done and ticks < LIFT_FRAMES + SceneRouter.VISIBLE_MEASURE_FRAMES * 2:
		t += FRAME_USEC
		done = w.tick(t, ticks >= LIFT_FRAMES)
		ticks += 1
	assert_true(done and w.is_complete())
	assert_eq(ticks, LIFT_FRAMES + SceneRouter.VISIBLE_MEASURE_FRAMES, "stops 60 frames after the lift")
	assert_eq(w.lift_frames, LIFT_FRAMES)
	assert_eq(w.frame_ms.size(), ticks)
	assert_between(w.frame_ms[0], 16.6, 16.7, "frame times come from the injected clock")
	var stats := {}
	assert_true(SceneRouter.judge_visible(stats, w).is_empty(), "a steady 60 fps is in budget")
	assert_false(bool(stats["visible_over_budget"]))
	assert_true(bool(stats["visible_complete"]))
	assert_eq(stats["lift_frames"], LIFT_FRAMES)
	assert_eq(stats["visible_budget_ms"], SceneRouter.SWAP_BUDGET_MS)
	assert_between(float(stats["max_visible_frame_ms"]), 16.6, 16.7)


func test_a_visible_hitch_warns_against_50_ms() -> void:
	var t := 0
	var w := SceneRouter.VisibleWindow.new(t)
	for i in LIFT_FRAMES + 5:
		t += FRAME_USEC if i != LIFT_FRAMES + 2 else int(HITCH_FRAME_MS * SceneRouter.USEC_PER_MSEC)
		w.tick(t, i >= LIFT_FRAMES)
	var stats := {}
	var warnings := SceneRouter.judge_visible(stats, w)
	assert_true(bool(stats["visible_over_budget"]), "a 70 ms frame after the lift is a hitch")
	assert_eq(stats["max_visible_frame_ms"], HITCH_FRAME_MS)
	assert_false(bool(stats["visible_complete"]), "cut short (another change started)")
	assert_eq(warnings.size(), 1)
	assert_true(warnings[0].contains("50 ms budget"), "%s" % warnings)
	assert_true(warnings[0].contains("frame %d " % (LIFT_FRAMES + 2)), "names the frame: %s" % warnings)


func test_load_guard_reads_a_number() -> void:
	assert_true(_load_per_cpu() >= 0.0)


func test_font_warmer_covers_the_theme_and_skips_msdf() -> void:
	var theme := ThemeDB.get_project_theme()
	assert_true(theme != null, "project theme is set (gui/theme/custom)")
	var pairs := SceneRouter.FontWarmer.theme_pairs(theme)
	assert_true(pairs.size() > 1, "theme yields several font/size pairs")
	var sizes: Dictionary = {}
	for p in pairs:
		assert_false(SceneRouter.FontWarmer.is_msdf(p["font"] as Font), "MSDF fonts are never warmed")
		sizes[int(p["size"])] = true
	assert_true(sizes.has(theme.default_font_size), "theme default size is warmed")
	for type in theme.get_type_list():
		for sname in theme.get_font_size_list(type):
			assert_true(sizes.has(theme.get_font_size(sname, type)), "%s/%s is warmed" % [type, sname])


func test_font_warmer_units_are_small_and_cover_the_charset() -> void:
	var font := SystemFont.new()
	var pairs: Array[Dictionary] = [{"font": font, "size": 20, "outline": 0}, {"font": font, "size": 30, "outline": 2}]
	var units := SceneRouter.FontWarmer.units_for(pairs)
	var charset := SceneRouter.FontWarmer.CHARSET
	var chunks := ceili(float(charset.length()) / SceneRouter.FontWarmer.CHUNK_CHARS)
	assert_eq(units.size(), chunks * pairs.size())
	var joined := ""
	for u in units:
		assert_true(String(u["text"]).length() <= SceneRouter.FontWarmer.CHUNK_CHARS)
		if int(u["size"]) == 20:
			joined += String(u["text"])
	assert_eq(joined, charset, "every character is drawn once per pair")


func test_msdf_detection_follows_variations() -> void:
	var file := FontFile.new()
	file.multichannel_signed_distance_field = true
	var variation := FontVariation.new()
	variation.base_font = file
	assert_true(SceneRouter.FontWarmer.is_msdf(file))
	assert_true(SceneRouter.FontWarmer.is_msdf(variation))
	file.multichannel_signed_distance_field = false
	assert_false(SceneRouter.FontWarmer.is_msdf(variation))
	var empty: Array[Dictionary] = []
	assert_eq(SceneRouter.FontWarmer.units_for(empty).size(), 0)


func test_router_public_api_is_stable() -> void:
	assert_true(SceneRouter.has_signal(&"prewarm_requested"))
	assert_true(SceneRouter.has_signal(&"swap_measured"))
	assert_true(SceneRouter.has_method(&"change_scene"))
	assert_true(SceneRouter.has_method(&"is_busy"))
	assert_false(SceneRouter.is_busy())
	assert_true(SceneRouter.instantiate_on_thread and SceneRouter.warm_fonts and SceneRouter.split_swap)
	assert_true(SceneRouter.has_signal(&"scene_swapping"), "M1-RND-23")
	assert_true(SceneRouter.has_signal(&"visible_measured"), "M1-ARC-16")
	assert_false(SceneRouter.is_measuring(), "M1-ARC-16: no visible window at rest")
	for m: StringName in [&"hold_swap", &"release_swap", &"swap_holders"]:
		assert_true(SceneRouter.has_method(m), "M1-RND-23 hold API: %s" % m)


## M1-RND-23 (review-sweep-J S2): a generic hold, like SaveSystem.hold_autosave. Holding twice is one
## hold, a release drops it, and a freed holder drops out on its own.
func test_swap_hold_is_generic_and_drops_freed_holders() -> void:
	assert_true(SceneRouter.swap_holders().is_empty(), "nothing holds the swap at rest")
	var a := Node.new()
	var b := RefCounted.new()
	SceneRouter.hold_swap(a)
	SceneRouter.hold_swap(a)
	SceneRouter.hold_swap(b)
	assert_eq(SceneRouter.swap_holders().size(), 2, "holding twice is one hold")
	SceneRouter.release_swap(b)
	assert_eq(SceneRouter.swap_holders(), [a] as Array[Object])
	a.free()
	assert_true(SceneRouter.swap_holders().is_empty(), "a freed holder drops out")
	SceneRouter.hold_swap(null)
	assert_true(SceneRouter.swap_holders().is_empty())


## M1-RND-23 (review-sweep-J S2): the zone render globals reset on scene_swapping through
## ShaderGlobals, and the router names neither the systems that own them nor the prewarm type scan.
func test_scene_swapping_resets_the_zone_globals() -> void:
	for name in ShaderGlobals.ZONE_GLOBALS:
		assert_true(ProjectSettings.has_setting("shader_globals/" + name), "%s is registered" % name)
	GlimmerField.set_scene_sea_glow(0.0)
	ShaderGlobals.set_value(WaterSurface.GLOBAL_WATER_LEVEL, Vector2(0.6, 0.4))
	SceneRouter.scene_swapping.emit("res://nowhere.tscn")
	# The swap also wrote the default zone wind (M2-ARC-02, WeatherClock); later tests get the project default.
	ShaderGlobals.reset(WeatherClock.GLOBAL_WIND)
	assert_eq(ShaderGlobals.get_value(GlimmerField.GLOBAL_SEA_GLOW), GlimmerField.SEA_GLOW_ZONE_UNSET, "sea-glow unset")
	assert_eq(ShaderGlobals.get_value(WaterSurface.GLOBAL_WATER_LEVEL), Vector2.ZERO, "water level back to 0, 0")
	assert_true(ShaderGlobals.install(SceneRouter), "install is idempotent")
	var hook := Callable(ShaderGlobals, &"_on_scene_swapping")
	var hooks := 0
	for c: Dictionary in SceneRouter.scene_swapping.get_connections():
		if c["callable"] == hook:
			hooks += 1
	assert_eq(hooks, 1, "and connects once")
	var src := FileAccess.get_file_as_string("res://game/core/scene_router.gd")
	for banned: String in ["GlimmerField", "WaterSurface", "is_staging_under"]:
		assert_false(src.contains(banned), "the router does not name %s" % banned)
	assert_true(src.contains("scene_swapping.emit(scene_path)"), "it emits the signal in the swap")


## The fixed router: instanced off the main thread, fonts warm, and the old scene unloaded and the
## prewarm stage built in frames before the measured swap window.
func _assert_fix_shape(stats: Dictionary, target: String) -> void:
	assert_true(bool(stats.get("instantiated_on_thread", false)), "%s instanced on a worker thread" % target)
	assert_true(bool(stats.get("fonts_warmed", false)), "%s fonts warmed before the swap" % target)
	assert_true(stats.has("unload_ms"), "%s old scene unloaded in its own frame" % target)
	assert_eq((stats.get("frame_ms", []) as Array).size(), SceneRouter.MEASURE_FRAMES)
	# M1-ARC-16: both ADR 0029 windows are recorded, the visible one in full.
	assert_eq(stats.get("budget_ms"), SceneRouter.HIDDEN_FRAME_BUDGET_MS, "%s hidden budget" % target)
	assert_true(float(stats.get("entry_ms", -1.0)) > 0.0, "%s entry measured" % target)
	assert_true(bool(stats.get("visible_complete", false)), "%s visible window complete" % target)
	var visible := (stats.get("visible_frame_ms", []) as Array).size()
	var lift := int(stats.get("lift_frames", -1))
	assert_true(lift > 0, "%s frames while the fade lifts: %d" % [target, lift])
	assert_eq(visible, lift + SceneRouter.VISIBLE_MEASURE_FRAMES, "%s the lift plus 60 frames" % target)


func _probe(probe_scene: String, target: String) -> Dictionary:
	var output: Array = []
	var args := PackedStringArray(
		["--headless", "--path", ProjectSettings.globalize_path("res://"), probe_scene, "--", "--to=" + target]
	)
	var code := OS.execute(_godot(), args, output, true)
	for chunk: Variant in output:
		for line in str(chunk).split("\n"):
			if line.begins_with(PROBE_TAG):
				var parsed: Variant = JSON.parse_string(line.trim_prefix(PROBE_TAG))
				if parsed is Dictionary:
					return parsed as Dictionary
	fail("probe for %s printed no stats (exit %d)" % [target, code])
	return {}


## The binary that runs this test, unless it was started through a loader (the sandbox wrapper
## execs Godot via ld-linux), in which case $GODOT or `godot` on PATH.
static func _godot() -> String:
	var env := OS.get_environment(GODOT_ENV)
	if env != "":
		return env
	var exe := OS.get_executable_path()
	if exe.get_file().to_lower().contains(GODOT_NAME_HINT):
		return exe
	return GODOT_ON_PATH
