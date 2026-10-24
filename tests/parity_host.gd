class_name ParityHost
extends RefCounted
## Shared steps for the field menu family's input parity tests (M2-UI-26): open the field menu on
## a scratch state, walk a MenuPage the way each InputDriver kind does (Up / Down presses for the
## keyboard and the pad, a hover for the mouse), choose (Confirm, or a click), back out (Cancel,
## or a right click), and point the mouse at a spot inside a Control (a glyph on the map, a node on
## the Lattice board). Every event is real and goes through the root viewport (InputDriver).

const NAMES := {&"rhen": "CHAR_RHEN", &"asha": "CHAR_ASHA", &"toma": "CHAR_TOMA"}
const HEROES: Array[StringName] = [&"rhen", &"asha", &"toma"]


static func scene_root() -> Node:
	var tree := Engine.get_main_loop() as SceneTree
	return tree.current_scene if tree.current_scene != null else tree.root


## The field menu over `state` (party `heroes`, the zone map `map` when given), not pausing the tree.
static func open_field_menu(
	state: GameStateData, heroes: Array[StringName] = HEROES, map: MapModel = null
) -> FieldMenu:
	var model := FieldMenuModel.new(state, heroes, NAMES)
	model.map = map
	var menu := (load(FieldMenu.SCENE_PATH) as PackedScene).instantiate() as FieldMenu
	menu.pause_tree = false
	menu.configure(model)
	scene_root().add_child(menu)
	return menu


## Closes and frees the menu and every layer a child page left under it.
static func free_field_menu(menu: FieldMenu) -> void:
	if menu == null or not is_instance_valid(menu):
		return
	FlowRouting.record = Callable()
	menu.close()
	for c in menu.get_children():
		if c is CanvasLayer:
			c.free()
	menu.get_parent().remove_child(menu)
	menu.free()
	(Engine.get_main_loop() as SceneTree).paused = false


## The index of row `id` on `page` (-1 when absent).
static func row_of(page: MenuPage, id: StringName) -> int:
	for i in page.row_count():
		if StringName(str(page.rows[i].get("id", ""))) == id:
			return i
	return -1


## Puts `page`'s cursor on row `index` the way `d` would: Down presses (at most one lap) for the
## keyboard and the pad, a hover for the mouse.
static func move_to(d: InputDriver, page: MenuPage, index: int) -> void:
	if d.kind == InputDriver.Kind.MOUSE:
		hover_away()
		InputDriver.hover(page.row_node(index))
		return
	for _n in page.row_count():
		if page.cursor == index:
			return
		d.press(&"ui_down")


## move_to, then Confirm (a left click on the row for the mouse).
static func choose(d: InputDriver, page: MenuPage, index: int) -> void:
	move_to(d, page, index)
	if d.kind == InputDriver.Kind.MOUSE:
		InputDriver.click(page.row_node(index))
	else:
		d.press(&"ui_accept")
	end_frame()


## Cancel: a right click over `over` for the mouse, else the device's Cancel.
static func back(d: InputDriver, over: Control) -> void:
	if d.kind == InputDriver.Kind.MOUSE:
		InputDriver.right_click(over)
	else:
		d.press(&"ui_cancel")
	end_frame()


## What the end of a frame does to a closed page: its layer (queue_free'd on close) goes away, so
## the next pointer move reaches the page under it, as it would a frame later in play.
static func end_frame() -> void:
	var gone: Array[Node] = []
	_queued(scene_root(), gone)
	for n in gone:
		if is_instance_valid(n):
			n.free()


static func _queued(n: Node, out: Array[Node]) -> void:
	for c in n.get_children():
		if c is CanvasLayer and c.is_queued_for_deletion():
			out.append(c)
		else:
			_queued(c, out)


## Moves the pointer to the window's top-left corner, so the next hover is a fresh enter.
static func hover_away() -> void:
	var m := InputEventMouseMotion.new()
	InputDriver.root().push_input(m, true)


## Viewport coordinates of `local`, a point inside `c` (as InputDriver.point_of).
static func point_in(c: Control, local: Vector2) -> Vector2:
	return c.get_global_transform_with_canvas() * local


## Moves the pointer to `local` inside `c`.
static func hover_at(c: Control, local: Vector2) -> void:
	var m := InputEventMouseMotion.new()
	m.position = point_in(c, local)
	m.global_position = m.position
	InputDriver.root().push_input(m, true)


## Left-clicks at `local` inside `c` (press and release, no movement between).
static func click_at(c: Control, local: Vector2) -> void:
	hover_at(c, local)
	var b := InputEventMouseButton.new()
	b.button_index = MOUSE_BUTTON_LEFT
	b.position = point_in(c, local)
	b.global_position = b.position
	b.button_mask = MOUSE_BUTTON_MASK_LEFT
	InputDriver.send(b, true)
	b.button_mask = 0
	InputDriver.send(b, false)


## Turns the wheel `steps` notches (negative: up) at `local` inside `c`.
static func wheel_at(c: Control, local: Vector2, steps: int) -> void:
	hover_at(c, local)
	for i in absi(steps):
		var b := InputEventMouseButton.new()
		b.button_index = MOUSE_BUTTON_WHEEL_DOWN if steps > 0 else MOUSE_BUTTON_WHEEL_UP
		b.position = point_in(c, local)
		b.global_position = b.position
		b.factor = 1.0
		InputDriver.send(b, true)
		InputDriver.send(b, false)
