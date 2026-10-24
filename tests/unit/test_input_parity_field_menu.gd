extends TestCase
## M2-UI-26 (input parity): the field menu's own levels (root, Swell heroes and modes, the Quit
## confirm) and the Settings hub it opens, walked with the keyboard, the controller and the mouse
## through real InputEvents (InputDriver, ParityHost). After each child closes, the parent must
## take the input again with its cursor where it was.

var menu: FieldMenu
var state: GameStateData


func before_each() -> void:
	state = GameStateData.new()
	menu = null
	UiSettings.set_shared(UiSettings.new())


func test_swell_heroes_and_modes_with_each_device() -> void:
	for kind in InputDriver.KINDS:
		var d := InputDriver.new(kind)
		var who := d.label()
		_open()
		var root := menu.root_page()
		var swell := ParityHost.row_of(root, FieldMenuModel.ROW_SWELL)
		ParityHost.move_to(d, root, swell)
		assert_eq(root.cursor, swell, "%s: the cursor reaches Swell" % who)
		assert_eq(menu.desc_text(), menu.model.root_desc(FieldMenuModel.ROW_SWELL), "%s: its line follows" % who)
		ParityHost.choose(d, root, swell)
		assert_eq(menu.level, FieldMenu.Level.HEROES, "%s: Swell opens the heroes" % who)
		assert_true(menu.detail_page().visible)
		ParityHost.choose(d, menu.detail_page(), 0)
		assert_eq(menu.level, FieldMenu.Level.MODES, "%s: a hero opens their modes" % who)
		assert_eq(menu.hero, &"rhen")
		var wake := ParityHost.row_of(menu.detail_page(), &"wake")
		ParityHost.move_to(d, menu.detail_page(), wake)
		assert_eq(menu.detail_page().cursor, wake, "%s: the cursor reaches Wake" % who)
		assert_eq(menu.desc_text(), menu.model.mode_desc(&"rhen", &"wake"), "%s: its line follows" % who)
		ParityHost.choose(d, menu.detail_page(), wake)
		assert_eq(state.swell_mode_of(&"rhen", &"ballast"), &"wake", "%s: Confirm sets the mode" % who)
		ParityHost.back(d, menu.detail_page())
		assert_eq(menu.level, FieldMenu.Level.HEROES, "%s: Cancel goes back to the heroes" % who)
		assert_eq(menu.detail_page().current_row()["id"], &"rhen", "%s: on the hero it came from" % who)
		ParityHost.back(d, menu.detail_page())
		assert_eq(menu.level, FieldMenu.Level.ROOT, "%s: and to the root" % who)
		assert_eq(root.cursor, swell, "%s: the root cursor is where it was" % who)
		var other := ParityHost.row_of(root, FieldMenuModel.ROW_BESTIARY)
		ParityHost.move_to(d, root, other)
		assert_eq(root.cursor, other, "%s: the root has the input again" % who)
		ParityHost.back(d, root)
		assert_false(menu.is_open(), "%s: Cancel on the root closes the menu" % who)
		_close()
	_done()


func test_quit_confirm_stays_with_each_device() -> void:
	for kind in InputDriver.KINDS:
		var d := InputDriver.new(kind)
		var who := d.label()
		_open()
		var root := menu.root_page()
		var quit := ParityHost.row_of(root, FieldMenuModel.ROW_QUIT)
		ParityHost.choose(d, root, quit)
		assert_eq(menu.level, FieldMenu.Level.QUIT, "%s: Quit asks first" % who)
		assert_eq(menu.detail_page().current_row()["id"], FieldMenuModel.QUIT_STAY, "%s: Stay first" % who)
		ParityHost.choose(d, menu.detail_page(), 0)
		assert_eq(menu.level, FieldMenu.Level.ROOT, "%s: Stay goes back" % who)
		assert_true(menu.is_open())
		ParityHost.choose(d, root, quit)
		ParityHost.back(d, menu.detail_page())
		assert_eq(menu.level, FieldMenu.Level.ROOT, "%s: Cancel goes back too" % who)
		assert_eq(root.cursor, quit, "%s: on Quit" % who)
		_close()
	_done()


func test_settings_hands_the_input_back_with_each_device() -> void:
	for kind in InputDriver.KINDS:
		var d := InputDriver.new(kind)
		var who := d.label()
		_open()
		var root := menu.root_page()
		var at := ParityHost.row_of(root, FieldMenuModel.ROW_SETTINGS)
		ParityHost.choose(d, root, at)
		assert_true(menu.settings_menu != null and menu.settings_menu.is_open(), "%s: Settings opens" % who)
		d.press(&"ui_down")
		assert_eq(root.cursor, at, "%s: the hidden root takes no input" % who)
		ParityHost.back(d, menu.settings_menu)
		assert_true(menu.settings_menu == null, "%s: Cancel closes Settings" % who)
		assert_true(menu.visible, "%s: the field menu is back" % who)
		assert_eq(root.cursor, at, "%s: on Settings" % who)
		var other := ParityHost.row_of(root, FieldMenuModel.ROW_CLOSE)
		ParityHost.move_to(d, root, other)
		assert_eq(root.cursor, other, "%s: the root has the input again" % who)
		ParityHost.choose(d, root, other)
		assert_false(menu.is_open(), "%s: Close closes" % who)
		_close()
	_done()


func test_a_dimmed_root_holds_its_cursor_under_hover_and_wheel_but_a_click_returns() -> void:
	_open()
	var root := menu.root_page()
	var swell := ParityHost.row_of(root, FieldMenuModel.ROW_SWELL)
	ParityHost.choose(InputDriver.new(InputDriver.Kind.MOUSE), root, swell)
	assert_eq(menu.level, FieldMenu.Level.HEROES)
	var other := ParityHost.row_of(root, FieldMenuModel.ROW_STATUS)
	ParityHost.hover_away()
	InputDriver.hover(root.row_node(other))
	assert_eq(root.cursor, swell, "the path taken stays readable: hover leaves a dimmed page alone")
	InputDriver.wheel(root.row_node(swell), 1)
	assert_eq(root.cursor, swell, "and so does the wheel")
	assert_eq(menu.level, FieldMenu.Level.HEROES)
	InputDriver.click(root.row_node(other))
	assert_true(menu.child != null and menu.child is StatusMenu, "a click on the root goes back to it and opens")
	ParityHost.back(InputDriver.new(InputDriver.Kind.MOUSE), menu.child)
	assert_eq(menu.level, FieldMenu.Level.ROOT)
	assert_eq(root.cursor, other)
	_close()
	_done()


func test_the_wheel_steps_the_root() -> void:
	_open()
	var root := menu.root_page()
	var at := root.cursor
	InputDriver.wheel(root.row_node(at), 1)
	assert_ne(root.cursor, at, "the wheel moves the cursor")
	assert_eq(menu.desc_text(), menu.model.root_desc(StringName(str(root.current_row()["id"]))), "the line follows")
	InputDriver.wheel(root.row_node(root.cursor), -1)
	assert_eq(root.cursor, at, "and back")
	_close()
	_done()


func _open() -> void:
	state = GameStateData.new()
	menu = ParityHost.open_field_menu(state)


func _close() -> void:
	ParityHost.free_field_menu(menu)
	menu = null


func _done() -> void:
	UiSettings.set_shared(null)
