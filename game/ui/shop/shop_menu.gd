class_name ShopMenu
extends TownMenu
## The shop menu (M2-UI-06, SPEC §6.6): buy and sell at one shop (Shop, game/data/items/
## shops.json), prices in lume, every refusal said in words. A field Interactable whose payload
## is {"shop": "<shop id>"} opens it through TownServices. Words: ShopMenuModel.
##
## Three levels: ROOT (Buy / Sell / Leave) on the left; BUY (the stock) and SELL (the bag, then
## the owned pieces) on the right. The line under the right page says what the highlighted goods
## are; the status line under it says what the deal costs or earns, or why it is refused.
##
## Input (keyboard and controller through ui_*): ui_up / ui_down move, ui_left / ui_right change
## how many (BUY and SELL), ui_accept buys, sells or opens, ui_cancel goes back a level and
## leaves from the root. Mouse: hover to move, click to choose, the ‹ › steppers beside the status
## line (or the wheel over it) change how many, right click goes back (M2-UI-26).

enum Level { ROOT, BUY, SELL }

const SCENE_PATH := "res://game/ui/shop/shop_menu.tscn"
const SECTION := "shop_menu"

var model: ShopMenuModel
var level := Level.ROOT
## How many the next deal asks for (BUY and SELL; 1 for a piece).
var count := 1

var _root: MenuPage
var _detail: MenuPage
var _less: Label
var _more: Label
var _count: Label
## A receipt that stays on the status line until the cursor or the count moves.
var _notice: Dictionary = {}


## Instances the menu on its own CanvasLayer under `host` and opens it.
static func open_in(host: Node, with_model: ShopMenuModel) -> ShopMenu:
	var menu := (load(SCENE_PATH) as PackedScene).instantiate() as ShopMenu
	menu.configure(with_model)
	TownMenu.host_in(host, menu, SECTION)
	return menu


## Sets the model before the menu enters the tree.
func configure(with_model: ShopMenuModel) -> void:
	model = with_model


func root_page() -> MenuPage:
	return _root


func detail_page() -> MenuPage:
	return _detail


## The mouse's count steppers beside the status line (‹ fewer, › more), shown in BUY and SELL.
func count_steppers() -> Array[Label]:
	return [_less, _more] as Array[Label]


func handle_input(event: InputEvent) -> bool:
	if not is_open():
		return false
	if event.is_action_pressed(&"ui_up", true):
		_move(-1)
	elif event.is_action_pressed(&"ui_down", true):
		_move(1)
	elif event.is_action_pressed(&"ui_left", true):
		change_count(-1)
	elif event.is_action_pressed(&"ui_right", true):
		change_count(1)
	elif event.is_action_pressed(&"ui_accept"):
		accept()
	elif event.is_action_pressed(&"ui_cancel"):
		back()
	else:
		return false
	return true


## Chooses the highlighted row: opens a page from the root, or makes the deal.
func accept() -> void:
	match level:
		Level.ROOT:
			match StringName(str(_root.current_row().get("id", ""))):
				ShopMenuModel.ROW_BUY:
					_open(Level.BUY)
				ShopMenuModel.ROW_SELL:
					_open(Level.SELL)
				ShopMenuModel.ROW_LEAVE:
					close()
		Level.BUY:
			var gid := StringName(str(_detail.current_row().get("goods", "")))
			if gid != &"":
				_deal(model.buy(gid, count))
		Level.SELL:
			var row := _detail.current_row()
			if not row.is_empty():
				_deal(model.sell(row, count))


## Goes back one level; leaves from the root.
func back() -> void:
	if level == Level.ROOT:
		close()
		return
	level = Level.ROOT
	_notice = {}
	_render()


## Asks for one more or one fewer (wraps between 1 and the most this deal can take).
func change_count(delta: int) -> void:
	if level == Level.ROOT or _detail.current_row().is_empty():
		return
	var top := _max_count()
	var next := clampi(count + delta, 1, top)
	if next == count:
		next = 1 if delta > 0 else top
	if next == count:
		return
	count = next
	_notice = {}
	_render()


func _max_count() -> int:
	var limit := int(HudLayout.num(_d, "max_count"))
	if level == Level.BUY:
		return model.max_buy(StringName(str(_detail.current_row().get("goods", ""))), limit)
	return model.max_sell(_detail.current_row(), limit)


func _deal(result: Dictionary) -> void:
	_notice = result
	if bool(result.get("ok", false)):
		_detail.replace_rows(model.buy_rows() if level == Level.BUY else model.sell_rows())
		count = clampi(count, 1, _max_count()) if not _detail.current_row().is_empty() else 1
	_render()


func _open(to: Level) -> void:
	level = to
	count = 1
	_notice = {}
	_detail.replace_rows(model.buy_rows() if to == Level.BUY else model.sell_rows())
	_detail.set_cursor(0, false)
	_render()


func _move(delta: int) -> void:
	var page := _root if level == Level.ROOT else _detail
	if page.move(delta):
		count = 1
		_notice = {}
		_render()


func _section() -> String:
	return SECTION


func _build() -> void:
	var rm: Dictionary = _d.get("root", {})
	_root = _page(rm, &"shop_root", "", ShopMenuModel.ROOT_IDS.size())
	_root.row_hovered.connect(_on_hovered.bind(Level.ROOT))
	_root.row_clicked.connect(_on_clicked.bind(Level.ROOT))
	var dm: Dictionary = _d.get("detail", {})
	_detail = _page(dm, &"shop_detail", " ", int(HudLayout.num(dm, "max_rows")))
	_detail.row_hovered.connect(_on_hovered.bind(Level.BUY))
	_detail.row_clicked.connect(_on_clicked.bind(Level.BUY))
	_less = _stepper("‹", -1)
	_more = _stepper("›", 1)
	var sm: Dictionary = _d.get("steppers", {})
	_count = _label(
		&"HudNumber", Rect2(Vector2.ZERO, Vector2(HudLayout.num(sm, "count_width"), HudLayout.num(sm, "height")))
	)
	_count.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_status.mouse_filter = Control.MOUSE_FILTER_PASS
	_status.gui_input.connect(_on_status_input)
	_title.text = model.title()
	_root.replace_rows(model.root_rows())
	_root.set_cursor(_root.first_enabled(0, 1), false)


func _render() -> void:
	_render_lines()
	_place_steppers()


func _render_lines() -> void:
	var at_root := level == Level.ROOT
	_purse.text = model.purse_text()
	_root.set_dimmed(not at_root)
	_detail.visible = not at_root
	_detail.set_header(model.buy_title() if level == Level.BUY else model.sell_title())
	var dm: Dictionary = _d.get("detail", {})
	var top := HudLayout.rect_of(dm).position.y
	_detail.size.y = MenuPage.height_for(dm, maxi(_detail.row_count(), 1), true)
	_place_lines(top if at_root else top + _detail.size.y + HudLayout.num(_d.get("desc", {}), "gap"))
	if at_root:
		_desc.text = model.root_desc(StringName(str(_root.current_row().get("id", ""))))
		_set_status({})
		_help.text = tr("SHOP_MENU_HELP_ROOT")
		return
	_help.text = tr("SHOP_MENU_HELP_DEAL")
	var row := _detail.current_row()
	if row.is_empty():
		_desc.text = tr(ShopMenuModel.BUY_EMPTY_KEY if level == Level.BUY else ShopMenuModel.SELL_EMPTY_KEY)
		_set_status(_notice)  # the receipt for the last one sold stays
		return
	var gid := StringName(str(row.get("goods", "")))
	_desc.text = model.goods_desc(gid)
	if not _notice.is_empty():
		_set_status(_notice)
	elif level == Level.BUY:
		_set_status(model.buy_line(gid, count))
	else:
		_set_status(model.sell_line(row, count))


func _on_hovered(_index: int, page_level: Level) -> void:
	if (page_level == Level.ROOT) == (level == Level.ROOT):
		count = 1
		_notice = {}
		_render()


func _on_clicked(index: int, page_level: Level) -> void:
	if not is_open():
		return
	if page_level == Level.ROOT and level != Level.ROOT:
		level = Level.ROOT  # a click on the root page goes back to it
	elif page_level != Level.ROOT and level == Level.ROOT:
		return
	(_root if level == Level.ROOT else _detail).set_cursor(index, false)
	accept()


## A clickable count stepper (‹ or ›) for the mouse, in a gold-ruled keycap box; `delta` is what a
## click adds to the count.
func _stepper(glyph: String, delta: int) -> Label:
	var sm: Dictionary = _d.get("steppers", {})
	var l := _label(&"MenuLabel", Rect2(Vector2.ZERO, Vector2(HudLayout.num(sm, "width"), HudLayout.num(sm, "height"))))
	l.text = glyph
	l.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	l.mouse_filter = Control.MOUSE_FILTER_STOP
	l.mouse_default_cursor_shape = Control.CURSOR_POINTING_HAND
	l.add_theme_color_override(&"font_color", _c(&"focus_gold"))
	var box := StyleBoxFlat.new()
	box.bg_color = _c(&"panel_low")
	box.border_color = _c(&"line_gold")
	box.set_border_width_all(int(HudLayout.num(sm, "border_px")))
	box.set_corner_radius_all(int(HudLayout.num(sm, "radius_px")))
	l.add_theme_stylebox_override(&"normal", box)
	l.gui_input.connect(_on_stepper_input.bind(delta))
	return l


## The steppers and the count between them (‹ ×N ›) sit at the right end of the status line in
## BUY and SELL; the status line gives them room.
func _place_steppers() -> void:
	var sm: Dictionary = _d.get("steppers", {})
	var shown := level != Level.ROOT and not _detail.current_row().is_empty()
	for c: Control in [_less, _count, _more]:
		c.visible = shown
	_count.text = tr("SHOP_MENU_COUNT_FMT").format({"n": count})
	var full := HudLayout.rect_of(_d.get("detail", {})).size.x
	var w := HudLayout.num(sm, "width")
	var cw := HudLayout.num(sm, "count_width")
	var block := w * 2.0 + cw
	_status.size.x = full - (block + HudLayout.num(sm, "gap") if shown else 0.0)
	var x := _status.position.x + full - block
	_less.position = Vector2(x, _status.position.y)
	_count.position = Vector2(x + w, _status.position.y)
	_more.position = Vector2(x + w + cw, _status.position.y)


func _on_stepper_input(event: InputEvent, delta: int) -> void:
	var mb := event as InputEventMouseButton
	if mb != null and mb.pressed and mb.button_index == MOUSE_BUTTON_LEFT and is_open():
		change_count(delta)
		accept_event()


## The wheel over the status line changes how many (down: fewer, as on a dial).
func _on_status_input(event: InputEvent) -> void:
	var mb := event as InputEventMouseButton
	if mb == null or not mb.pressed or level == Level.ROOT or not is_open():
		return
	if mb.button_index == MOUSE_BUTTON_WHEEL_UP:
		change_count(1)
	elif mb.button_index == MOUSE_BUTTON_WHEEL_DOWN:
		change_count(-1)
