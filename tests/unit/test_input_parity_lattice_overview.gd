extends TestCase
## M3-MNU-04 (input parity): the Lattice page's whole-board overview toggles with each device through
## real InputEvents: the keyboard (M), the controller (X) and the mouse (the title bar's button).
## Reduced motion is on, so the camera snaps and the test reads the end state at once. Each test
## frees its page itself (the runner has no after_each).

const SPOT := &"rh_02"


func before_each() -> void:
	InputDriver.clear_screen()
	var s := UiSettings.new()
	s.set_value(UiSettings.REDUCED_MOTION, true)
	UiSettings.set_shared(s)


func test_the_overview_toggles_with_each_device() -> void:
	for kind in InputDriver.KINDS:
		var d := InputDriver.new(kind)
		var who := d.label()
		var page := _page()
		var view := page.board_view()
		page.set_cursor(SPOT, false)
		var near_zoom := view.zoom
		assert_true(
			kind == InputDriver.Kind.MOUSE or InputDriver.has_binding(LatticeMenu.OVERVIEW_ACTION, kind),
			"%s: the overview has a binding" % who
		)
		_toggle(d, page)
		assert_true(page.is_overview(), "%s: the whole board" % who)
		assert_eq(view.zoom, view.fit_zoom(), "%s: fitted" % who)
		assert_eq(page.cursor, SPOT, "%s: the cursor stays" % who)
		d.press(&"ui_left")
		assert_eq(page.cursor, &"rh_01", "%s: the cursor still moves" % who)
		assert_true(page.is_overview(), "%s: and the board stays framed" % who)
		_toggle(d, page)
		assert_false(page.is_overview(), "%s: back" % who)
		assert_eq(view.zoom, near_zoom, "%s: at the zoom it had" % who)
		assert_true(Rect2(Vector2.ZERO, view.size).has_point(view.screen_point(&"rh_01")), "%s: on the cursor" % who)
		_free(page)
	UiSettings.set_shared(null)


func _toggle(d: InputDriver, page: LatticeMenu) -> void:
	if d.kind == InputDriver.Kind.MOUSE:
		InputDriver.click(page.overview_button())
	else:
		d.press(LatticeMenu.OVERVIEW_ACTION)


func _page() -> LatticeMenu:
	var page := LatticeMenu.create(PartySheet.new(GameStateData.new(), ParityHost.HEROES))
	page.pause_tree = false
	ParityHost.scene_root().add_child(page)
	return page


func _free(page: LatticeMenu) -> void:
	page.close()
	page.get_parent().remove_child(page)
	page.free()
