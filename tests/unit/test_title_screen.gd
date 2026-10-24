extends TestCase
## M2-UI-22: the title screen's dressing. The logotype is drawn from theme fonts (localized words that
## fit their rect); the backdrop has the caustic layer, seeded motes that drift deterministically and
## hold still under reduced motion; the build label shows only in debug builds.

const TEST_DIR := "user://test_title_screen"

var made: Array[Node] = []
var _saved_dir := ""
var _saved_clock := true


func before_each() -> void:
	_cleanup()
	UiSettings.set_shared(UiSettings.new())
	_saved_dir = SaveSystem.save_dir
	_saved_clock = Game.play_clock_running
	SaveSystem.save_dir = TEST_DIR


func test_the_logo_words_are_localized_and_fit_the_logo() -> void:
	var menu := _open()
	var logo := menu.logo
	assert_true(logo != null and logo.get_parent() == menu, "the title has a logo")
	for k in TitleLogo.WORD_KEYS:
		assert_ne(tr(k), k, "%s has a translation" % k)
	assert_eq(logo.words(), [tr("TITLE_LOGO_HYMN"), tr("TITLE_LOGO_JOIN"), tr("TITLE_LOGO_UNDERTOW")])
	var d := TitleMenu.load_data()["logo"] as Dictionary
	assert_eq(logo.size, HudLayout.rect_of(d).size, "placed at its data rect")
	assert_true(logo.word_size() > logo.get_theme_font_size(&"font_size", &"TitleLabel"), "bigger than a title")
	for w in logo.word_widths():
		assert_between(w, 1.0, logo.size.x, "each word fits the logo")
	assert_true(logo.join_extent() <= logo.size.x, "the join rules fit too")
	assert_true(float(d["undertow_baseline"]) < float(d["wave_y"]), "the flourish sits under the name")
	assert_true(logo.position.y + float(d["wave_y"]) < HudLayout.rect_of(TitleMenu.load_data()["choices"]).position.y)
	_close(menu)


func test_the_logo_waves_drift_but_hold_under_reduced_motion() -> void:
	var menu := _open()
	var logo := menu.logo
	assert_eq(logo.wave_phase(), 0.0)
	logo.advance(1.0)
	var moved := logo.wave_phase()
	assert_true(moved > 0.0, "the tide flourish drifts")
	UiSettings.shared().set_value(UiSettings.REDUCED_MOTION, true)
	logo.advance(1.0)
	assert_eq(logo.wave_phase(), moved, "reduced motion holds it")
	_close(menu)


func test_the_backdrop_has_caustics_and_seeded_motes() -> void:
	var menu := _open()
	var b := menu.backdrop
	assert_true(b != null and menu.get_child(0) == b, "the backdrop is under everything")
	assert_true(b.caustics != null and b.caustics.get_parent() == b, "it reuses the caustic layer")
	var d := TitleMenu.load_data()["backdrop"] as Dictionary
	assert_eq(b.mote_count(), int(d["motes"]))
	var twin := TitleBackdrop.new()
	twin.size = b.size
	twin.setup(d)
	for i in b.mote_count():
		assert_eq(twin.mote_position(i), b.mote_position(i), "the seed gives the same picture every run")
	twin.free()
	_close(menu)


func test_the_motes_drift_deterministically_and_hold_under_reduced_motion() -> void:
	var menu := _open()
	var b := menu.backdrop
	var d := TitleMenu.load_data()["backdrop"] as Dictionary
	var start := b.mote_position(0)
	for i in 60:
		b.advance(1.0 / 60.0)
	var after := b.mote_position(0)
	assert_ne(after, start, "a mote moves")
	var twin := TitleBackdrop.new()
	twin.size = b.size
	twin.setup(d)
	twin.advance(b.elapsed())
	assert_true(twin.mote_position(0).is_equal_approx(after), "position depends only on elapsed time")
	twin.free()
	for i in b.mote_count():
		assert_between(b.mote_alpha(i), 0.0, 1.0)
	UiSettings.shared().set_value(UiSettings.REDUCED_MOTION, true)
	var t := b.elapsed()
	b.advance(1.0)
	assert_eq(b.elapsed(), t, "reduced motion: nothing moves")
	assert_eq(b.mote_position(0), after)
	_close(menu)


func test_the_build_label_shows_only_in_debug_builds() -> void:
	assert_true(TitleMenu.shows_version({"debug_only": true}, true))
	assert_false(TitleMenu.shows_version({"debug_only": true}, false), "hidden in a release")
	assert_true(TitleMenu.shows_version({"debug_only": false}, false), "unless the data shows it")
	assert_true(TitleMenu.shows_version({}, true))
	assert_false(TitleMenu.shows_version({}, false), "debug-only by default")
	var debug := _open(true)
	var label := debug.version_label()
	assert_true(label != null and label.get_parent() == debug, "a debug build shows the label")
	assert_true(label.text.contains(str(TitleMenu.load_data()["version"]["fallback"])), label.text)
	assert_ne(tr("TITLE_BUILD_LABEL"), "TITLE_BUILD_LABEL")
	_close(debug)
	var release := _open(false)
	assert_true(release.version_label() == null, "a release build has none")
	assert_eq(release.find_children("VersionLabel", "Label", true, false).size(), 0)
	_close(release)


func test_boot_has_no_placeholder_label() -> void:
	var state := (load("res://game/core/boot.tscn") as PackedScene).get_state()
	for i in state.get_node_count():
		assert_ne(state.get_node_name(i), &"Label", "the title draws its own name now")


func _open(debug: bool = true) -> TitleMenu:
	var menu := TitleMenu.new()
	menu.save_system = SaveSystem
	menu.debug_build = debug
	(Engine.get_main_loop() as SceneTree).current_scene.add_child(menu)
	made.append(menu)
	return menu


func _close(menu: TitleMenu) -> void:
	made.erase(menu)
	if is_instance_valid(menu):
		menu.get_parent().remove_child(menu)
		menu.free()
	SaveSystem.save_dir = _saved_dir
	Game.play_clock_running = _saved_clock
	DirAccess.remove_absolute(TEST_DIR)
	UiSettings.set_shared(null)  # later suites read the shared settings


func _cleanup() -> void:
	for n in made:
		if is_instance_valid(n):
			n.get_parent().remove_child(n)
			n.free()
	made.clear()
