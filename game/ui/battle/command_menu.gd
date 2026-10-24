class_name CommandMenu
extends Control
## Bottom-left command menu (docs/kb/art/ui.md §6.3) with sub-menus that push to the right.
## Keyboard and controller go through the built-in ui_* actions (arrows/D-pad, accept, cancel);
## the mouse hovers and clicks rows. It only reports intent through signals: the battle
## controller decides what a choice means.

signal highlighted(page_id: StringName, row: Dictionary)
signal chosen(page_id: StringName, row: Dictionary)
signal cancelled(page_id: StringName)

## Accepts input only while active (the controller turns it off during enemy turns).
var active := true
## Reduced motion (UiSettings): sub-menus fade in place, the cursor jumps, the mote holds still.
var reduced_motion := false

var _m: Dictionary = {}
var _pages: Array[MenuPage] = []
var _root_rect := Rect2()
var _sub_rect := Rect2()


func _ready() -> void:
	_m = HudLayout.section(&"commands")
	set_anchors_preset(Control.PRESET_FULL_RECT)
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	_root_rect = HudLayout.rect_of(_m)
	_sub_rect = HudLayout.rect_of(HudLayout.section(&"reserve"))


## Replaces every page with a single root page.
func open_root(page_id: StringName, title: String, rows: Array[Dictionary]) -> void:
	for p in _pages:
		p.queue_free()
	_pages.clear()
	# The rect holds five rows; a longer root grows upward from the same foot (M2-UI-05).
	var h := maxf(_root_rect.size.y, MenuPage.height_for(_m, rows.size()))
	_add_page(page_id, title, rows, Rect2(_root_rect.position.x, _root_rect.end.y - h, _root_rect.size.x, h), false)


## Pushes a sub-menu to the right of the current page; the page below dims.
func push(page_id: StringName, title: String, rows: Array[Dictionary]) -> void:
	if not _pages.is_empty():
		_pages[-1].set_dimmed(true)
	var h := MenuPage.height_for(_m, rows.size())
	var r := Rect2(_sub_rect.position.x, _sub_rect.end.y - h, _sub_rect.size.x, h)
	_add_page(page_id, title, rows, r, true)


## Pops the top page (never the root). Returns false at the root.
func pop() -> bool:
	if _pages.size() <= 1:
		return false
	var top: MenuPage = _pages.pop_back()
	top.queue_free()
	_pages[-1].set_dimmed(false)
	_emit_highlight()
	return true


## Redraws the top page with `rows` in place (same size and position, the cursor kept), without
## a highlight signal: the caller has just acted on the row (M2-UI-01's fill-mode choice).
func refresh_top(rows: Array[Dictionary]) -> void:
	if not _pages.is_empty():
		_pages[-1].replace_rows(rows)


## Redraws the root page with `rows` in place (under a pushed page it stays dimmed).
func refresh_root(rows: Array[Dictionary]) -> void:
	if not _pages.is_empty():
		_pages[0].replace_rows(rows)


func depth() -> int:
	return _pages.size()


func page_id() -> StringName:
	return _pages[-1].page_id if not _pages.is_empty() else &""


func current_row() -> Dictionary:
	return _pages[-1].current_row() if not _pages.is_empty() else {}


func top_page() -> MenuPage:
	return _pages[-1] if not _pages.is_empty() else null


func move_cursor(delta: int) -> void:
	if not _pages.is_empty() and _pages[-1].move(delta):
		_emit_highlight()


## Selects the row with `row_id` on the top page (no signal unless it changes).
func select(row_id: StringName) -> void:
	var p := top_page()
	if p == null:
		return
	for i in p.rows.size():
		if StringName(str(p.rows[i].get("id", ""))) == row_id and i != p.cursor:
			p.set_cursor(i)
			_emit_highlight()
			return


func accept() -> void:
	var row := current_row()
	if row.is_empty() or not bool(row.get("enabled", true)):
		return
	chosen.emit(page_id(), row)


func cancel() -> void:
	cancelled.emit(page_id())


## Routes one input event; returns true if it was consumed.
func handle_input(event: InputEvent) -> bool:
	if not active or _pages.is_empty():
		return false
	if event.is_action_pressed(&"ui_up", true):
		move_cursor(-1)
	elif event.is_action_pressed(&"ui_down", true):
		move_cursor(1)
	elif event.is_action_pressed(&"ui_accept"):
		accept()
	elif event.is_action_pressed(&"ui_cancel"):
		cancel()
	else:
		return false
	return true


func set_menu_visible(on: bool) -> void:
	visible = on


func _add_page(pid: StringName, title: String, rows: Array[Dictionary], r: Rect2, animate: bool) -> void:
	var page := MenuPage.new()
	page.position = r.position
	page.size = r.size
	add_child(page)
	page.reduced_motion = reduced_motion
	page.setup(_m, pid, title, rows)
	page.row_hovered.connect(func(_i: int) -> void: _emit_highlight())
	page.row_clicked.connect(_on_row_clicked.bind(page))
	_pages.append(page)
	if animate and is_inside_tree():
		var dur := HudLayout.num(_m, "push_sec")
		if not reduced_motion:
			page.position.x += HudLayout.num(_m, "submenu_offset")
		page.modulate.a = 0.0
		var tw := page.create_tween().set_parallel(true)
		tw.tween_property(page, "position:x", r.position.x, dur).set_trans(Tween.TRANS_CUBIC)
		tw.tween_property(page, "modulate:a", 1.0, dur)
	_emit_highlight()


func _on_row_clicked(index: int, page: MenuPage) -> void:
	if not active or page != top_page():
		return
	page.set_cursor(index)
	accept()


func _emit_highlight() -> void:
	if not _pages.is_empty():
		highlighted.emit(page_id(), current_row())
