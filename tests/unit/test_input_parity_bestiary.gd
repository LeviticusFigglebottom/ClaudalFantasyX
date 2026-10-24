extends TestCase
## M2-UI-26 (input parity): the bestiary (BestiaryMenu) opened from the field menu, walked with the
## keyboard, the controller and the mouse through real InputEvents: step the entries (the page on
## the right follows), jump a page, back out, and the field menu takes the input again.

const FOES: Array[StringName] = [&"reef_crab", &"gull_harrier", &"lantern_eel"]

var menu: FieldMenu
var _saved: GameStateData


func before_each() -> void:
	InputDriver.clear_screen()
	menu = null
	UiSettings.set_shared(UiSettings.new())
	_saved = Game.state
	Game.state = GameStateData.new()
	var book := Bestiary.new(Game.state.bestiary)
	for foe in FOES:
		book.record_defeated(foe, 1)


func test_open_step_and_back_with_each_device() -> void:
	for kind in InputDriver.KINDS:
		var d := InputDriver.new(kind)
		var who := d.label()
		menu = ParityHost.open_field_menu(Game.state)
		var root := menu.root_page()
		var at := ParityHost.row_of(root, FieldMenuModel.ROW_BESTIARY)
		ParityHost.choose(d, root, at)
		var book := menu.bestiary
		assert_true(book != null and book.is_open(), "%s: the bestiary opens" % who)
		assert_true(book.entries().size() >= 2, "%s: a book to walk" % who)
		var first := book.current_id
		var list := book._list
		ParityHost.move_to(d, list, 1)
		assert_eq(list.cursor, 1, "%s: the cursor moves" % who)
		assert_ne(book.current_id, first, "%s: the page follows" % who)
		assert_eq(book.current_id, StringName(str(book.entries()[1]["id"])))
		ParityHost.choose(d, list, 1)
		assert_true(book.is_open(), "%s: Confirm (or a click) keeps the book open" % who)
		assert_eq(list.cursor, 1)
		if kind != InputDriver.Kind.MOUSE:
			d.press(&"ui_left")
			assert_eq(list.cursor, 0, "%s: Left jumps a page back (stops at the top)" % who)
			assert_eq(book.current_id, first)
		ParityHost.back(d, book)
		assert_false(is_instance_valid(book), "%s: Cancel closes the book (its layer is gone)" % who)
		assert_true(menu.bestiary == null and menu.visible, "%s: back on the field menu" % who)
		assert_eq(root.cursor, at, "%s: on the Bestiary row" % who)
		var other := ParityHost.row_of(root, FieldMenuModel.ROW_CLOSE)
		ParityHost.move_to(d, root, other)
		assert_eq(root.cursor, other, "%s: the field menu has the input again" % who)
		ParityHost.free_field_menu(menu)
		menu = null
	_done()


func test_the_wheel_steps_over_the_list_and_over_the_page() -> void:
	menu = ParityHost.open_field_menu(Game.state)
	menu.root_page().set_cursor(ParityHost.row_of(menu.root_page(), FieldMenuModel.ROW_BESTIARY), false)
	menu.accept()
	var book := menu.bestiary
	var list := book._list
	InputDriver.wheel(list.row_node(0), 1)
	assert_eq(list.cursor, 1, "the wheel over the list")
	assert_eq(book.current_id, StringName(str(book.entries()[1]["id"])), "the page follows the wheel")
	InputDriver.wheel(book.page_view(), -1)
	assert_eq(list.cursor, 0, "the wheel over the foe's page steps too")
	assert_eq(book.current_id, StringName(str(book.entries()[0]["id"])))
	ParityHost.free_field_menu(menu)
	menu = null
	_done()


func _done() -> void:
	Game.state = _saved
	UiSettings.set_shared(null)
