extends TestCase
## The Lead's final-quality pass (2026-10-29): no focus dead ends. With the keyboard and with the pad, every row of the
## field menu's root is chosen, Confirm then goes DIVE levels deeper (each level's first row), and Cancel, pressed
## again and again, always walks back out until the menu closes,
## leaving no screen of its own showing. A page that keeps the input with no way back (a dead end) fails here, whatever
## its own parity test covers. The mouse's way back (a right click) is each screen's own parity test.

## More Cancel presses than any screen is deep (root, page, column, entry, confirm).
const MAX_BACKS := 8
## Confirm presses after a page opens: into its columns, an entry, a picker or a confirm.
const DIVE := 3

var menu: FieldMenu


func before_each() -> void:
	InputDriver.clear_screen()
	UiSettings.set_shared(UiSettings.new())


func test_cancel_always_walks_out_of_every_field_menu_page() -> void:
	FlowRouting.record = func(_change: Array) -> void: pass  # Quit to Title's Confirm changes no scene here
	for kind: InputDriver.Kind in [InputDriver.Kind.KEYS, InputDriver.Kind.PAD]:
		var d := InputDriver.new(kind)
		menu = ParityHost.open_field_menu(GameStateData.new())
		var ids: Array[StringName] = []
		for i in menu.root_page().row_count():
			ids.append(StringName(str(menu.root_page().rows[i].get("id", ""))))
		ParityHost.free_field_menu(menu)
		assert_true(ids.size() > 5, "the root lists its pages")
		for id in ids:
			menu = ParityHost.open_field_menu(GameStateData.new())
			ParityHost.choose(d, menu.root_page(), ParityHost.row_of(menu.root_page(), id))
			for _n in DIVE:
				if menu.is_open():
					d.press(&"ui_accept")
					_finish_motions(menu)
			var backs := 0
			while menu.is_open() and backs < MAX_BACKS:
				ParityHost.back(d, menu)
				_finish_motions(menu)
				backs += 1
			assert_false(menu.is_open(), "%s: Cancel walks out of %s (%d presses)" % [d.label(), id, backs])
			for layer in menu.find_children("*", "CanvasLayer", true, false):
				for c in (layer as CanvasLayer).get_children():
					if c is Control and (c as Control).is_visible_in_tree() and not c.is_queued_for_deletion():
						fail("%s: %s left %s showing" % [d.label(), id, c.get_path()])
			ParityHost.free_field_menu(menu)
	menu = null
	FlowRouting.record = Callable()
	UiSettings.set_shared(null)


## A page that fades out on close (MenuMotion) finishes its fade, as frames would in play.
static func _finish_motions(root: Node) -> void:
	for n in root.find_children("*", "", true, false):
		if n.has_method(&"motion") and n.call(&"motion") != null:
			(n.call(&"motion") as MenuMotion).finish()
	ParityHost.end_frame()
