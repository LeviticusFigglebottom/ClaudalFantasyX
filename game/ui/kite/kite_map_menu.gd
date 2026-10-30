class_name KiteMapMenu
extends FieldSubmenu
## The Kite's world map (SPEC §6.6, Act III; act_outline.md Ch18; M3-UI-205): the places the Kite can
## land, by name, with the chart beside them (KiteChart); choosing one asks first (Stay under the
## cursor), and Fly closes the page and goes (KiteMapModel.fly). "Search the chart" names a cell
## (Left / Right: the column, Up / Down: the row) and Confirm searches it for a secret place, which
## joins the list once found. The place the party stands in is marked Here and can't be chosen.
## Layout: game/data/ui/kite_map.json.
##
## Input: ui_up / ui_down move, ui_accept chooses, ui_cancel backs out or leaves; while searching,
## ui_left / ui_right change the column and ui_up / ui_down the row. Mouse: hover moves, click chooses;
## while searching, the pointer over the chart names a square and a click searches it.

signal flight_chosen(destination: StringName)

enum Level { LIST, CONFIRM, SEARCH }

const DATA_PATH := "res://game/data/ui/kite_map.json"
const ROW_SEARCH := &"search"
const ROW_LEAVE := &"leave"
const ROW_STAY := &"stay"
const ROW_FLY := &"fly"

var level := Level.LIST
var model: KiteMapModel
## The destination being confirmed (&"" on the list).
var picked: StringName = &""
## Where the Kite flew (&"" until a flight goes; the page closes then).
var flown: StringName = &""
## The cell being searched ([column, row]).
var cell := Vector2i.ZERO

var _rows: MenuPage
var _chart: KiteChart
var _desc: Label
var _help: Label
var _notice := ""


static func create(with_model: KiteMapModel) -> KiteMapMenu:
	var menu := KiteMapMenu.new()
	menu.model = with_model
	return menu


static func open_in(host: Node, with_model: KiteMapModel) -> KiteMapMenu:
	return FieldSubmenu.mount(create(with_model), host) as KiteMapMenu


func data_path() -> String:
	return DATA_PATH


func data_section() -> String:
	return "kite_map"


func rows_page() -> MenuPage:
	return _rows


func chart() -> KiteChart:
	return _chart


func desc_text() -> String:
	return _desc.text


func help_text() -> String:
	return _help.text


func handle_input(event: InputEvent) -> bool:
	if not is_open():
		return false
	if level == Level.SEARCH:
		return _search_input(event)
	if event.is_action_pressed(&"ui_up", true):
		_move(-1)
	elif event.is_action_pressed(&"ui_down", true):
		_move(1)
	elif event.is_action_pressed(&"ui_accept"):
		accept()
	elif event.is_action_pressed(&"ui_cancel"):
		back()
	else:
		return false
	return true


## Chooses the highlighted row: a place asks first; Fly goes; Stay steps back; Search opens the search.
func accept() -> void:
	var id := StringName(str(_rows.current_row().get("id", "")))
	if level == Level.CONFIRM:
		if id == ROW_FLY:
			fly(picked)
		else:
			back()
		return
	match id:
		ROW_LEAVE:
			close()
		ROW_SEARCH:
			level = Level.SEARCH
			_notice = ""
			_render()
		_:
			if model.is_here(id):
				return
			picked = id
			level = Level.CONFIRM
			_notice = ""
			_show_rows(_confirm_rows(), 0)  # Stay under the cursor


func back() -> void:
	if level == Level.LIST:
		close()
		return
	var at := maxi(model.ids().find(picked), 0) if level == Level.CONFIRM else _list_rows().size() - 2
	level = Level.LIST
	picked = &""
	_show_rows(_list_rows(), at)


## Flies to `destination`: the page closes first, then the Kite goes. A refusal reopens the list with why.
func fly(destination: StringName) -> bool:
	flight_chosen.emit(destination)
	if model.fly(destination):
		flown = destination
		close()
		return true
	level = Level.LIST
	picked = &""
	_notice = tr("KITE_REFUSED_FMT").format({"place": model.place_name(destination)})
	_show_rows(_list_rows(), maxi(model.ids().find(destination), 0))
	return false


## Searches the named cell: a secret there joins the list (and the cursor goes to it); else says so.
func search() -> Dictionary:
	var name := cell_name()
	var found := model.search(name)
	level = Level.LIST
	if found.is_empty():
		_notice = tr("KITE_SEARCH_NOTHING_FMT").format({"cell": name})
		_show_rows(_list_rows(), _list_rows().size() - 2)
	else:
		var id := StringName(str(found["id"]))
		_notice = tr("KITE_SEARCH_FOUND_FMT").format({"cell": name, "place": model.place_name(id)})
		_show_rows(_list_rows(), maxi(model.ids().find(id), 0))
	return found


## The searched cell's name ("F2").
func cell_name() -> String:
	var cols := model.columns()
	return "%s%d" % [str(cols[cell.x]) if not cols.is_empty() else "", cell.y + 1]


func _search_input(event: InputEvent) -> bool:
	if event.is_action_pressed(&"ui_left", true):
		cell.x = posmod(cell.x - 1, maxi(model.columns().size(), 1))
	elif event.is_action_pressed(&"ui_right", true):
		cell.x = posmod(cell.x + 1, maxi(model.columns().size(), 1))
	elif event.is_action_pressed(&"ui_up", true):
		cell.y = posmod(cell.y - 1, maxi(model.row_count(), 1))
	elif event.is_action_pressed(&"ui_down", true):
		cell.y = posmod(cell.y + 1, maxi(model.row_count(), 1))
	elif event.is_action_pressed(&"ui_accept"):
		search()
		return true
	elif event.is_action_pressed(&"ui_cancel"):
		back()
		return true
	else:
		return false
	_render()
	return true


func _build_page() -> void:
	var dim := ColorRect.new()
	dim.set_anchors_preset(Control.PRESET_FULL_RECT)
	dim.mouse_filter = Control.MOUSE_FILTER_IGNORE
	dim.color = Color(_c(&"panel_low"), HudLayout.num(_d, "dim_alpha"))
	add_child(dim)
	_help = _framed_panel(_d.get("panel", {}), tr("KITE_TITLE"))
	var rm: Dictionary = _d.get("rows", {})
	_rows = _menu_page(rm, &"kite_map", "", int(HudLayout.num(rm, "max_rows")))
	_rows.row_hovered.connect(func(_i: int) -> void: _render())
	_rows.row_clicked.connect(_on_clicked)
	var em: Dictionary = _d.get("desc", {})
	var top := _rows.position.y + _rows.size.y + HudLayout.num(em, "gap")
	_desc = _label(
		&"BodyLabel", Rect2(Vector2(_rows.position.x, top), Vector2(_rows.size.x, HudLayout.num(em, "height")))
	)
	_desc.vertical_alignment = VERTICAL_ALIGNMENT_TOP
	_desc.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	_chart = KiteChart.new()
	add_child(_chart)
	_chart.setup(_d.get("chart", {}), model)
	_chart.cell_pointed.connect(_on_cell_pointed)
	_show_rows(_list_rows(), 0)


func _list_rows() -> Array[Dictionary]:
	var out: Array[Dictionary] = []
	for id in model.ids():
		var here := model.is_here(id)
		var refused := model.refusal(id)  # greyed with its reason: seen from the air, never landed at
		var right := tr("KITE_HERE") if here else refused
		out.append({"id": id, "label": model.place_name(id), "right": right, "enabled": not here and refused == ""})
	out.append({"id": ROW_SEARCH, "label": tr("KITE_SEARCH"), "enabled": true})
	out.append({"id": ROW_LEAVE, "label": tr("KITE_LEAVE"), "enabled": true})
	return out


func _confirm_rows() -> Array[Dictionary]:
	return [
		{"id": ROW_STAY, "label": tr("KITE_STAY"), "enabled": true},
		{"id": ROW_FLY, "label": tr("KITE_FLY"), "enabled": true},
	]


func _show_rows(rows: Array[Dictionary], at: int) -> void:
	_rows.replace_rows(rows)
	_rows.set_cursor(_rows.first_enabled(clampi(at, 0, rows.size() - 1), 1), false)  # never on Here
	_render()


func _move(delta: int) -> void:
	if _rows.move(delta):
		_notice = ""
		_render()


func _render() -> void:
	var id := StringName(str(_rows.current_row().get("id", "")))
	_chart.search_cell = cell if level == Level.SEARCH else Vector2i(-1, -1)
	_chart.cursor = picked if level == Level.CONFIRM else id
	_chart.queue_redraw()
	match level:
		Level.SEARCH:
			_desc.text = tr("KITE_SEARCH_DESC_FMT").format({"cell": cell_name()})
			_help.text = tr("KITE_HELP_SEARCH")
		Level.CONFIRM:
			var place := model.place_name(picked)
			_desc.text = tr("KITE_CONFIRM_FMT").format({"place": place}) if id == ROW_FLY else tr("KITE_STAY_DESC")
			_help.text = tr("KITE_HELP_CONFIRM")
		_:
			var line := ""
			match id:
				ROW_SEARCH:
					line = tr("KITE_SEARCH_ROW_DESC")
				ROW_LEAVE:
					line = tr("KITE_LEAVE_DESC")
				_:
					var place := model.place_name(id)
					var region := model.region_name(id)
					var key := "KITE_PLACE_FMT" if region != "" and region != place else "KITE_PLACE_SHORT_FMT"
					line = tr(key).format({"place": place, "region": region, "cell": model.cell_of(id)})
			_desc.text = _notice if _notice != "" else line
			_help.text = tr("KITE_HELP")
	var pm: Dictionary = _d.get("panel", {})
	UiFrame.fit_line(_help, HudLayout.rect_of(pm).size.x - HudLayout.num(pm, "pad") * 2.0)


func _on_clicked(index: int) -> void:
	if not is_open() or level == Level.SEARCH:
		return
	_rows.set_cursor(index, false)
	accept()


func _on_cell_pointed(square: Vector2i, clicked: bool) -> void:
	if not is_open() or level != Level.SEARCH:
		return
	cell = square
	if clicked:
		search()
	else:
		_render()
