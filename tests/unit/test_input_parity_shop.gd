extends TestCase
## M2-UI-26 (input parity): the shop and the inn, walked with the keyboard, the controller and the
## mouse through real InputEvents (InputDriver). Scratch state; the tree is never paused here.

const NAMES := {&"rhen": "CHAR_RHEN", &"asha": "CHAR_ASHA", &"toma": "CHAR_TOMA"}

var db: ItemDB
var state: GameStateData
var flags: FlagReader
var made: Array[Node] = []


func before_each() -> void:
	InputDriver.clear_screen()
	db = ItemDB.load_default()
	state = GameStateData.new()
	flags = FlagReader.new()
	flags.values["ch02_met_asha"] = true
	UiSettings.set_shared(UiSettings.new())


func test_buy_two_and_leave_with_each_device() -> void:
	for kind in InputDriver.KINDS:
		var d := InputDriver.new(kind)
		state = GameStateData.new()
		state.currency = 500
		var menu := _shop()
		_accept(d, menu.root_page(), menu.root_page().cursor)
		assert_eq(menu.level, ShopMenu.Level.BUY, "%s: Buy opens the stock" % d.label())
		var page := menu.detail_page()
		var goods := StringName(str(page.current_row().get("goods", "")))
		if kind == InputDriver.Kind.MOUSE:
			InputDriver.click(menu.count_steppers()[1])
		else:
			d.press(&"ui_right")
		assert_eq(menu.count, 2, "%s: one more" % d.label())
		if kind == InputDriver.Kind.MOUSE:
			InputDriver.wheel(menu._status, 1)
			assert_eq(menu.count, 1, "mouse: the wheel over the status line turns it back")
			InputDriver.click(menu.count_steppers()[1])
		var held := menu.model.party.inventory.count(goods)
		_accept(d, page, page.cursor)
		assert_eq(menu.model.party.inventory.count(goods), held + 2, "%s: two bought" % d.label())
		_cancel(d, menu)
		assert_eq(menu.level, ShopMenu.Level.ROOT, "%s: Cancel goes back to the root" % d.label())
		var at := menu.root_page().cursor
		if kind == InputDriver.Kind.MOUSE:
			InputDriver.wheel(menu.root_page().row_node(at), 1)
		else:
			d.press(&"ui_down")
		assert_eq(menu.root_page().cursor, at + 1, "%s: the root has the input again" % d.label())
		_cancel(d, menu)
		assert_false(menu.is_open(), "%s: Cancel at the root leaves" % d.label())
		_free()
	_done()


func test_the_inn_rests_and_leaves_with_each_device() -> void:
	for kind in InputDriver.KINDS:
		var d := InputDriver.new(kind)
		state = GameStateData.new()
		state.currency = 500
		var healed: Array[StringName] = []
		var menu := (load(InnMenu.SCENE_PATH) as PackedScene).instantiate() as InnMenu
		menu.pause_tree = false
		var heal := func(source: StringName) -> void: healed.append(source)
		menu.configure(InnMenuModel.new(Inn.new(db, &"haluna_inn"), PartyGoods.from_state(db, state), flags, heal))
		_add(menu)
		var rest := InnMenuModel.ROOT_IDS.find(InnMenuModel.ROW_REST)
		if kind == InputDriver.Kind.MOUSE:
			InputDriver.click(menu.root_page().row_node(rest))
		else:
			for i in 4:
				if menu.root_page().cursor == rest:
					break
				d.press(&"ui_up")
			d.press(&"ui_accept")
		assert_eq(healed.size(), 1, "%s: a night's rest" % d.label())
		_cancel(d, menu)
		assert_false(menu.is_open(), "%s: Cancel leaves" % d.label())
		_free()
	_done()


## ADR 0040: the Reefball outfitter, bought from and left with each device.
func test_the_outfitter_buys_and_leaves_with_each_device() -> void:
	for kind in InputDriver.KINDS:
		var d := InputDriver.new(kind)
		state = GameStateData.new()
		state.currency = 500
		var bag: Dictionary = {}
		var model := ReefballOutfitterModel.new(
			ReefballDB.load_default(),
			PartyGoods.from_state(db, state).wallet,
			func(f: StringName) -> Variant: return bag.get(f, ""),
			func(f: StringName, v: Variant) -> void: bag[f] = v
		)
		var menu := (load(ReefballOutfitterMenu.SCENE_PATH) as PackedScene).instantiate() as ReefballOutfitterMenu
		menu.pause_tree = false
		menu.configure(model)
		_add(menu)
		_accept(d, menu.root_page(), 0)
		assert_true(model.is_owned(&"brass_thread_band"), "%s: Confirm buys the first piece" % d.label())
		assert_true(model.is_worn(&"brass_thread_band"), "%s: and the side wears it" % d.label())
		if kind == InputDriver.Kind.MOUSE:
			InputDriver.wheel(menu.root_page().row_node(0), 1)
		else:
			d.press(&"ui_down")
		assert_eq(menu.root_page().cursor, 1, "%s: the cursor moves on" % d.label())
		_cancel(d, menu)
		assert_false(menu.is_open(), "%s: Cancel leaves" % d.label())
		_free()
	_done()


func _shop() -> ShopMenu:
	var menu := (load(ShopMenu.SCENE_PATH) as PackedScene).instantiate() as ShopMenu
	menu.pause_tree = false
	menu.configure(
		ShopMenuModel.new(db, Shop.new(db, &"haluna_market"), PartyGoods.from_state(db, state), flags, NAMES)
	)
	_add(menu)
	return menu


func _accept(d: InputDriver, page: MenuPage, index: int) -> void:
	if d.kind == InputDriver.Kind.MOUSE:
		InputDriver.click(page.row_node(index))
	else:
		d.press(&"ui_accept")


func _cancel(d: InputDriver, over: Control) -> void:
	if d.kind == InputDriver.Kind.MOUSE:
		InputDriver.right_click(over)
	else:
		d.press(&"ui_cancel")


func _add(n: Node) -> void:
	var tree := Engine.get_main_loop() as SceneTree
	(tree.current_scene if tree.current_scene != null else tree.root).add_child(n)
	made.append(n)


func _free() -> void:
	for n in made:
		if is_instance_valid(n) and n.get_parent() != null:
			n.get_parent().remove_child(n)
			n.free()
	made.clear()


func _done() -> void:
	_free()
	UiSettings.set_shared(null)
