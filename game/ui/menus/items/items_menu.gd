class_name ItemsMenu
extends FieldSubmenu
## The field menu's Items page (M2-MNU-03): the bag with counts, sorted by kind, name or count;
## the highlighted item's category, count and description; and field use of restoratives on a
## chosen hero, with what it would do ("Rhen: HP 120 → 320") before it is spent. Words and rules:
## ItemsMenuModel over a PartySheet. Layout: game/data/ui/items_menu.json.
##
## Two levels. LIST: the bag on the left, the item on the right. PICK: the heroes (HP and MP, each
## with its gauge) replace the right column, and the line under them previews the use or says why
## it is refused (in the danger color). A use writes the saved vitals at once and stays in PICK, so
## a second tonic is one more Confirm; when the last one is spent the page goes back to LIST.
##
## M3-MNU-03: two views, tabs in the title row (ItemsMenuModel.VIEWS): the Bag (everything but key
## items, sortable, usable) and Key Items (each key item with its description; nothing to use, the
## line under it says it is kept).
##
## Input (keyboard and controller through ui_*): ui_up / ui_down move, ui_left / ui_right change
## the sort (the bag), ui_page_up / ui_page_down (the pad's shoulders) switch the view, ui_accept
## opens the picker or uses, ui_cancel goes back a level and closes from LIST. Mouse: hover moves,
## a click chooses, the wheel steps, a click on the sort line changes the sort, a click on a tab
## shows that view.

enum Level { LIST, PICK }

const DATA_PATH := "res://game/data/ui/items_menu.json"
const LIST_ID := &"items_list"
const PICK_ID := &"items_pick"

## The sort chosen this session: the page opens with it again until the game is closed.
static var session_sort: StringName = ItemsMenuModel.SORT_KIND

var sheet: PartySheet
var model: ItemsMenuModel
var level := Level.LIST
## The item the picker is for (PICK).
var item_id: StringName = &""

var _list: MenuPage
var _picker: MenuPage
var _sort: Label
## View id -> its tab label in the title row.
var _tabs: Dictionary = {}
var _help: Label
var _name: Label
var _held: Label
var _desc: Label
var _use: Label
var _preview: Label
var _gauges: Array[HudGauge] = []
## A receipt that stays on the preview line until the cursor moves.
var _notice: Dictionary = {}


static func create(with_sheet: PartySheet = null) -> ItemsMenu:
	var menu := ItemsMenu.new()
	menu.sheet = with_sheet
	return menu


## Opens the page on its own CanvasLayer under `host` (null sheet = the live party).
static func open_in(host: Node, with_sheet: PartySheet = null) -> ItemsMenu:
	return FieldSubmenu.mount(create(with_sheet), host) as ItemsMenu


func data_path() -> String:
	return DATA_PATH


func data_section() -> String:
	return "items_menu"


func list_page() -> MenuPage:
	return _list


func picker_page() -> MenuPage:
	return _picker


func help_text() -> String:
	return _help.text


func sort_text() -> String:
	return _sort.text


func desc_text() -> String:
	return _desc.text


## The line under the item: how to use it, or why it can't be used here.
func use_text() -> String:
	return _use.text


## The line under the picker: what the use would do, the receipt, or the refusal.
func preview_text() -> String:
	return _preview.text


## The id under the list cursor (&"" for an empty bag).
func current_item() -> StringName:
	return StringName(str(_list.current_row().get("id", "")))


func handle_input(event: InputEvent) -> bool:
	if not is_open():
		return false
	if event.is_action_pressed(&"ui_up", true):
		_move(-1)
	elif event.is_action_pressed(&"ui_down", true):
		_move(1)
	elif event.is_action_pressed(&"ui_left", true):
		change_sort(-1)
	elif event.is_action_pressed(&"ui_right", true):
		change_sort(1)
	elif event.is_action_pressed(&"ui_page_up", true):
		change_view(-1)
	elif event.is_action_pressed(&"ui_page_down", true):
		change_view(1)
	elif _wheel(event) != 0:
		_move(_wheel(event))
	elif event.is_action_pressed(&"ui_accept"):
		accept()
	elif event.is_action_pressed(&"ui_cancel"):
		back()
	else:
		return false
	return true


## LIST: opens the picker for a usable item (a refused one keeps its line). PICK: uses it.
func accept() -> void:
	if level == Level.LIST:
		var iid := current_item()
		if iid == &"" or model.item_error(iid) != ItemsMenuModel.RESULT_OK:
			return
		item_id = iid
		level = Level.PICK
		_notice = {}
		_picker.replace_rows(model.hero_rows(iid))
		_picker.set_cursor(0, false)
		_render()
		return
	var cid := StringName(str(_picker.current_row().get("id", "")))
	if cid == &"":
		return
	_notice = model.use(item_id, cid)
	if bool(_notice.get("ok", false)):
		_refresh_list()
		if model.inventory().count(item_id) <= 0:
			level = Level.LIST  # the receipt for the last one stays on the use line
			_render()
			return
		_picker.replace_rows(model.hero_rows(item_id))
	_render()


## Goes back one level; closes from LIST.
func back() -> void:
	_notice = {}
	if level == Level.LIST:
		close()
		return
	level = Level.LIST
	_render()


## Steps the view (LIST only); the cursor starts at the top of the new list.
func change_view(step: int) -> void:
	if level != Level.LIST:
		return
	show_view(ItemsMenuModel.VIEWS[posmod(ItemsMenuModel.VIEWS.find(model.view) + step, ItemsMenuModel.VIEWS.size())])


## Shows view `to` (an ItemsMenuModel.VIEWS id) from LIST; from PICK it goes back to LIST first.
func show_view(to: StringName) -> void:
	if not ItemsMenuModel.VIEWS.has(to):
		return
	level = Level.LIST
	_notice = {}
	if to != model.view:
		model.view = to
		_list.replace_rows(model.rows())
		_list.set_cursor(0, false)
	_render()


func tab_label(of_view: StringName) -> Label:
	return _tabs.get(of_view) as Label


## Steps the sort (the bag's LIST only), keeping the cursor on the same item.
func change_sort(step: int) -> void:
	if level != Level.LIST or model.view != ItemsMenuModel.VIEW_BAG:
		return
	var keep := current_item()
	_notice = {}
	model.next_sort(step)
	session_sort = model.sort
	_refresh_list(keep)
	_render()


func _build_page() -> void:
	if sheet == null:
		sheet = PartySheet.from_game()
	if model == null:
		model = ItemsMenuModel.from_sheet(sheet)
	model.sort = session_sort
	_help = _framed_panel(_d.get("panel", {}), tr("FIELD_MENU_ITEMS"))
	_sort = _label(&"DimLabel", HudLayout.rect_of(_d.get("sort", {})))
	_sort.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
	_sort.mouse_filter = Control.MOUSE_FILTER_STOP
	_sort.gui_input.connect(_on_sort_input)
	_build_tabs(_d.get("tabs", {}))
	var lm: Dictionary = _d.get("list", {})
	_list = _menu_page(lm, LIST_ID, "", int(HudLayout.num(lm, "max_rows")))
	_list.row_hovered.connect(_on_hovered.bind(Level.LIST))
	_list.row_clicked.connect(_on_clicked.bind(Level.LIST))
	_build_detail(_d.get("detail", {}))
	var pm: Dictionary = _d.get("picker", {})
	_picker = _menu_page(pm, PICK_ID, " ", sheet.heroes.size())
	_picker.row_hovered.connect(_on_hovered.bind(Level.PICK))
	_picker.row_clicked.connect(_on_clicked.bind(Level.PICK))
	_preview = _label(&"HelpLabel", Rect2())
	_preview.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	_preview.vertical_alignment = VERTICAL_ALIGNMENT_TOP
	_refresh_list()
	_render()


## One clickable label per view, side by side from the tabs rect's left edge.
func _build_tabs(tm: Dictionary) -> void:
	var r := HudLayout.rect_of(tm)
	var x := r.position.x
	for v in ItemsMenuModel.VIEWS:
		var l := _label(&"HeaderLabel", Rect2(x, r.position.y, 0.0, r.size.y))
		l.text = model.view_label(v)
		l.size.x = l.get_minimum_size().x
		l.mouse_filter = Control.MOUSE_FILTER_STOP
		l.gui_input.connect(_on_tab_input.bind(v))
		_tabs[v] = l
		x += l.size.x + HudLayout.num(tm, "gap")


func _build_detail(dm: Dictionary) -> void:
	var r := HudLayout.rect_of(dm)
	var line_h := HudLayout.num(dm, "line_height")
	var gap := HudLayout.num(dm, "gap")
	var y := r.position.y
	_name = _label(&"HeaderLabel", Rect2(r.position.x, y, r.size.x, HudLayout.num(dm, "name_height")))
	y += _name.size.y
	_held = _label(&"DimLabel", Rect2(r.position.x, y, r.size.x, line_h))
	y += line_h + gap
	_desc = _label(&"HelpLabel", Rect2(r.position.x, y, r.size.x, HudLayout.num(dm, "desc_height")))
	_desc.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	_desc.vertical_alignment = VERTICAL_ALIGNMENT_TOP
	y += _desc.size.y + gap
	_use = _label(&"HelpLabel", Rect2(r.position.x, y, r.size.x, HudLayout.num(dm, "use_height")))
	_use.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	_use.vertical_alignment = VERTICAL_ALIGNMENT_TOP


## Rebuilds the bag rows, keeping the cursor on `keep` (default: the item under it now).
func _refresh_list(keep: StringName = &"") -> void:
	var on := keep if keep != &"" else current_item()
	var at := _list.cursor
	var rows := model.rows()
	_list.replace_rows(rows)
	for i in rows.size():
		if StringName(str(rows[i]["id"])) == on:
			at = i
	_list.set_cursor(clampi(at, 0, maxi(rows.size() - 1, 0)), false)


func _render() -> void:
	var picking := level == Level.PICK
	var bag := model.view == ItemsMenuModel.VIEW_BAG
	_sort.text = model.sort_text()
	_sort.visible = bag
	for v: StringName in _tabs:
		(_tabs[v] as Label).add_theme_color_override(
			&"font_color", _c(&"focus_gold" if v == model.view else &"text_dim")
		)
	_list.set_dimmed(picking)
	_picker.visible = picking
	for l: Label in [_name, _held, _desc, _use]:
		l.visible = not picking
	_preview.visible = picking
	_help.text = tr("ITEMS_MENU_HELP_PICK" if picking else ("ITEMS_MENU_HELP" if bag else "ITEMS_MENU_HELP_KEY"))
	if picking:
		_render_pick()
	else:
		_render_item()


func _render_item() -> void:
	_clear_gauges()
	var iid := current_item()
	if iid == &"":
		_name.text = ""
		_held.text = ""
		_desc.text = model.empty_text()
		_use.text = ""
		return
	_name.text = model.item_name(iid)
	_held.text = model.held_text(iid)
	_desc.text = model.desc(iid)
	var line := _notice if not _notice.is_empty() else model.item_line(iid)
	_use.text = str(line["text"])
	_set_role(_use, bool(line["ok"]))
	if model.view == ItemsMenuModel.VIEW_KEY:
		_use.add_theme_color_override(&"font_color", _c(&"text_dim"))  # kept, not refused


func _render_pick() -> void:
	var pm: Dictionary = _d.get("picker", {})
	_picker.set_header(model.pick_title(item_id))
	_picker.size.y = MenuPage.height_for(pm, maxi(_picker.row_count(), 1), true)
	var pv: Dictionary = _d.get("preview", {})
	_preview.position = Vector2(_picker.position.x, _picker.position.y + _picker.size.y + HudLayout.num(pv, "gap"))
	_preview.size = Vector2(_picker.size.x, HudLayout.num(pv, "height"))
	_place_gauges(pm)
	var cid := StringName(str(_picker.current_row().get("id", "")))
	var line := _notice if not _notice.is_empty() else model.preview(item_id, cid)
	_preview.text = str(line.get("text", ""))
	_set_role(_preview, bool(line.get("ok", false)))


## An HP and an MP gauge under each picker row's numbers.
func _place_gauges(pm: Dictionary) -> void:
	_clear_gauges()
	var gm: Dictionary = _d.get("gauge", {})
	var h := HudLayout.num(gm, "height")
	var gap := HudLayout.num(gm, "gap")
	var indent := HudLayout.num(pm, "text_indent") - HudLayout.num(pm, "row_inset")
	var cost_w := HudLayout.num(pm, "cost_width")
	var rank_w := HudLayout.num(pm, "rank_width")
	for i in _picker.row_count():
		var cid := StringName(str(_picker.rows[i].get("id", "")))
		var v := model.vitals(cid)
		var r := _picker.row_rect(i)
		var y := _picker.position.y + r.end.y - HudLayout.num(gm, "inset_bottom") - h
		var right_edge := _picker.position.x + r.end.x - indent * 0.5
		var mp_x := right_edge - rank_w
		var hp_x := right_edge - cost_w
		_gauge(&"hp", Rect2(hp_x, y, cost_w - rank_w - gap, h), int(v["hp"]), int(v["max_hp"]))
		_gauge(&"mp", Rect2(mp_x, y, rank_w, h), int(v["mp"]), int(v["max_mp"]))


func _gauge(role: StringName, r: Rect2, value: int, maximum: int) -> void:
	var g := HudGauge.new(role)
	g.position = r.position
	g.size = r.size
	g.set_value(value, maximum)
	add_child(g)
	_gauges.append(g)


func _clear_gauges() -> void:
	for g in _gauges:
		g.queue_free()
	_gauges.clear()


func picker_gauges() -> Array[HudGauge]:
	return _gauges.duplicate()


func _set_role(l: Label, ok: bool) -> void:
	l.add_theme_color_override(&"font_color", _c(&"text") if ok else _c(&"danger"))


func _move(delta: int) -> void:
	var page := _list if level == Level.LIST else _picker
	if page.move(delta):
		_notice = {}
		_render()


## -1 / 1 for a mouse wheel turn up / down, else 0.
static func _wheel(event: InputEvent) -> int:
	var mb := event as InputEventMouseButton
	if mb == null or not mb.pressed:
		return 0
	if mb.button_index == MOUSE_BUTTON_WHEEL_UP:
		return -1
	return 1 if mb.button_index == MOUSE_BUTTON_WHEEL_DOWN else 0


func _on_sort_input(event: InputEvent) -> void:
	var mb := event as InputEventMouseButton
	if mb != null and mb.pressed and mb.button_index == MOUSE_BUTTON_LEFT:
		change_sort(1)


func _on_tab_input(event: InputEvent, of_view: StringName) -> void:
	var mb := event as InputEventMouseButton
	if mb != null and mb.pressed and mb.button_index == MOUSE_BUTTON_LEFT:
		show_view(of_view)


func _on_hovered(_index: int, page_level: Level) -> void:
	if page_level == level:
		_notice = {}
		_render()


func _on_clicked(index: int, page_level: Level) -> void:
	if not is_open():
		return
	if page_level == Level.LIST and level == Level.PICK:
		level = Level.LIST  # a click on the bag goes back to it
		_notice = {}
	elif page_level == Level.PICK and level == Level.LIST:
		return
	(_list if level == Level.LIST else _picker).set_cursor(index, false)
	_render()
	accept()
