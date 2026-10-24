class_name LatticeMenu
extends FieldSubmenu
## The field menu's Lattice page (M2-MNU-01, SPEC §6.4, pillars 4 and 5): the board drawn whole in
## our own look (LatticeBoardView), a cursor to choose any node, and beside it the node's words
## before anything is spent: what it gives, its Facet and how many the party holds, who woke it, and
## what Confirm would do and cost (or why it can't). Words and actions: LatticeMenuModel.
## Layout: game/data/ui/lattice_menu.json. docs/kb/tech/ui.md § Lattice page.
##
## Input: ui_left / right / up / down move the cursor to the nearest node that way; ui_page_up /
## ui_page_down show the previous / next hero; ui_accept opens a two-row confirm (walk there, wake
## the node the hero stands on, or open the gate beside them) whose first row names the cost;
## Confirm there does it, Cancel or "Not now" steps back. A refused plan says why on the status line
## and opens nothing. Cancel closes the page. Mouse: a click puts the cursor on a node, a second
## click on it acts; the confirm rows hover and click like any MenuPage.

const DIRECTIONS := {
	&"ui_left": Vector2.LEFT,
	&"ui_right": Vector2.RIGHT,
	&"ui_up": Vector2.UP,
	&"ui_down": Vector2.DOWN,
}
const ROW_DO := &"do"
const ROW_CANCEL := &"cancel"
const CONFIRM_PAGE_ID := &"lattice_confirm"

var sheet: PartySheet
var model: LatticeMenuModel
## The node under the cursor.
var cursor: StringName = &""

var _board: LatticeBoardView
var _confirm: MenuPage
var _plan: Dictionary = {}
var _hero_label: Label
var _points: Label
var _facets: Label
var _node_title: Label
var _node_gives: Label
var _node_facet: Label
var _node_woken: Label
var _plan_line: Label
var _status: Label
var _legend: LatticeLegend
var _help: Label


static func create(with_sheet: PartySheet = null) -> LatticeMenu:
	var menu := LatticeMenu.new()
	menu.sheet = with_sheet
	return menu


## Opens the page on its own CanvasLayer under `host` (null sheet = the live party).
static func open_in(host: Node, with_sheet: PartySheet = null) -> LatticeMenu:
	return FieldSubmenu.mount(create(with_sheet), host) as LatticeMenu


func data_path() -> String:
	return "res://game/data/ui/lattice_menu.json"


func data_section() -> String:
	return "lattice_menu"


func handle_input(event: InputEvent) -> bool:
	if not is_open():
		return false
	if _confirm.visible:
		return _confirm_input(event)
	var used := true
	var dir := _direction(event)
	if dir != Vector2.ZERO:
		move_cursor(dir)
	elif event.is_action_pressed(&"ui_page_up", true):
		switch_hero(-1)
	elif event.is_action_pressed(&"ui_page_down", true):
		switch_hero(1)
	elif event.is_action_pressed(&"ui_accept"):
		request_act()
	else:
		used = super(event)
	return used


## Moves the cursor to the nearest node in board direction `dir` (y down). True if it moved.
func move_cursor(dir: Vector2) -> bool:
	var bm: Dictionary = _d.get("board", {})
	var next := model.nearest_in_direction(
		cursor, dir, HudLayout.num(bm, "cone_cos"), HudLayout.num(bm, "angle_weight")
	)
	if next == cursor:
		return false
	set_cursor(next)
	return true


## Puts the cursor on `nid` (the camera follows) and clears the status line.
func set_cursor(nid: StringName, animate: bool = true) -> void:
	if not model.board().has_lattice_node(nid):
		return
	cursor = nid
	_status.text = ""
	_board.center_on(nid, animate)
	_refresh()


## Shows the previous (-1) or next (1) hero, the cursor on where they stand.
func switch_hero(delta: int) -> bool:
	if not model.switch_hero(delta):
		return false
	set_cursor(model.position())
	return true


## Confirm on the cursor node: opens the confirm when the plan can be done, else says why.
func request_act() -> void:
	_plan = model.plan(cursor)
	if not bool(_plan["ok"]):
		_say(str(_plan["text"]), false)
		return
	var rows: Array[Dictionary] = [
		{"id": ROW_DO, "label": str(_plan["confirm"]), "right": "", "enabled": true},
		{"id": ROW_CANCEL, "label": tr("LATTICE_MENU_CONFIRM_CANCEL"), "right": "", "enabled": true},
	]
	_confirm.set_header(model.node_title(cursor))
	_confirm.replace_rows(rows)
	_confirm.set_cursor(0, false)
	_confirm.visible = true
	_status.visible = false


## Chooses confirm row `index` (0 does it, 1 steps back).
func choose(index: int) -> void:
	if not _confirm.visible:
		return
	_confirm.set_cursor(index, false)
	var row := _confirm.current_row()
	_close_confirm()
	if StringName(str(row.get("id", ""))) != ROW_DO:
		return
	var result := model.act(cursor)
	_board.center_on(cursor, true)
	_refresh()
	_say(str(result["text"]), bool(result["ok"]))


func is_confirming() -> bool:
	return _confirm.visible


func confirm_page() -> MenuPage:
	return _confirm


func board_view() -> LatticeBoardView:
	return _board


func status_text() -> String:
	return _status.text


func plan_text() -> String:
	return _plan_line.text


## The side panel's lines, top to bottom (tests read what the page shows).
func side_texts() -> PackedStringArray:
	var out: PackedStringArray = []
	for l: Label in [_hero_label, _points, _facets, _node_title, _node_gives, _node_facet, _node_woken, _plan_line]:
		out.append(l.text)
	return out


func _build_page() -> void:
	if sheet == null:
		sheet = PartySheet.from_game()
	model = LatticeMenuModel.new(sheet)
	_help = _framed_panel(_d.get("panel", {}), model.title())
	_help.text = tr("LATTICE_MENU_HELP")
	_hero_label = _label(&"HeaderLabel", HudLayout.rect_of(_d.get("hero", {})))
	_hero_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
	var bm: Dictionary = _d.get("board", {})
	_board = LatticeBoardView.new()
	HudLayout.place(_board, bm)
	_board.reduced_motion = UiSettings.shared().reduced_motion()
	_board.setup(bm, model)
	_board.node_clicked.connect(_on_node_clicked)
	add_child(_board)
	_build_side()
	_confirm = _menu_page(_d.get("confirm", {}), CONFIRM_PAGE_ID, " ", 2)
	_confirm.row_hovered.connect(func(i: int) -> void: _confirm.set_cursor(i))
	_confirm.row_clicked.connect(choose)
	_confirm.visible = false
	cursor = model.position()
	if cursor == &"" and not model.board().nodes.is_empty():
		cursor = model.board().nodes.keys()[0]
	_board.center_on(cursor, false)
	_refresh()


func _build_side() -> void:
	var sm: Dictionary = _d.get("side", {})
	var side := PanelContainer.new()
	side.theme_type_variation = &"PanelSmall"
	side.mouse_filter = Control.MOUSE_FILTER_IGNORE
	HudLayout.place(side, sm)
	add_child(side)
	var r := HudLayout.rect_of(sm)
	var pad := HudLayout.num(sm, "pad")
	var legend_metrics: Dictionary = _d.get("legend", {})
	var foot := HudLayout.rect_of(legend_metrics)
	var box := VBoxContainer.new()
	box.mouse_filter = Control.MOUSE_FILTER_IGNORE
	box.position = r.position + Vector2(pad, pad)
	box.size = Vector2(r.size.x - pad * 2.0, foot.position.y - r.position.y - pad)
	box.add_theme_constant_override(&"separation", int(HudLayout.num(sm, "gap")))
	add_child(box)
	_points = _side_label(box, &"MenuLabel")
	_points.add_theme_color_override(&"font_color", _c(&"focus_gold"))
	_facets = _side_label(box, &"DimLabel")
	var rule := OrnamentRule.new()
	rule.custom_minimum_size = Vector2(
		0.0, float(get_theme_constant(&"ornament_node_px", HymnThemeBuilder.PALETTE_TYPE)) * 2.0
	)
	box.add_child(rule)
	_node_title = _side_label(box, &"BodyLabel")
	_node_gives = _side_label(box, &"SmallLabel")
	_node_facet = _side_label(box, &"DimLabel")
	_node_woken = _side_label(box, &"DimLabel")
	_plan_line = _side_label(box, &"MenuLabel")
	_legend = LatticeLegend.new()
	HudLayout.place(_legend, legend_metrics)
	add_child(_legend)
	_legend.setup_legend(_d.get("board", {}), legend_metrics, model.legend_rows())
	_status = _label(&"HelpLabel", HudLayout.rect_of(_d.get("status", {})))
	_status.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	_status.vertical_alignment = VERTICAL_ALIGNMENT_TOP


func _side_label(box: VBoxContainer, variation: StringName) -> Label:
	var l := Label.new()
	l.theme_type_variation = variation
	l.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	l.mouse_filter = Control.MOUSE_FILTER_IGNORE
	box.add_child(l)
	return l


## Redraws the board marks and the side panel for the cursor node and the hero on show.
func _refresh() -> void:
	var list := model.heroes()
	if list.is_empty():
		_hero_label.text = ""
	else:
		_hero_label.text = tr("LATTICE_MENU_HERO_FMT").format(
			{"name": model.hero_name(), "i": model.hero_index + 1, "n": list.size()}
		)
	_points.text = model.points_text()
	_facets.text = model.facets_held_text()
	_node_title.text = model.node_title(cursor)
	_node_gives.text = model.node_gives(cursor)
	_node_facet.text = model.facet_line(cursor)
	_node_facet.visible = _node_facet.text != ""
	_node_woken.text = model.woken_line(cursor)
	_node_woken.visible = _node_woken.text != ""
	var p := model.plan(cursor)
	_plan_line.text = str(p["text"])
	_plan_line.add_theme_color_override(&"font_color", _c(&"focus") if bool(p["ok"]) else _c(&"danger"))
	_board.cursor = cursor
	var path: Array[StringName] = []
	if StringName(str(p["action"])) == LatticeMenuModel.ACT_WALK:
		path = p["path"] as Array[StringName]
	_board.path = path
	_board.path_ok = bool(p["ok"])
	_board.tag_text = _tag(p, path)
	_board.queue_redraw()
	_legend.rows = model.legend_rows()
	_legend.queue_redraw()


func _tag(p: Dictionary, path: Array[StringName]) -> String:
	if path.is_empty():
		return ""
	var cost := int(p["cost"])
	if cost == 0:
		return tr("LATTICE_MENU_TAG_FREE")
	return tr("LATTICE_MENU_TAG_COST_FMT").format({"n": cost})


func _say(text: String, ok: bool) -> void:
	_status.text = text
	_status.visible = true
	_status.add_theme_color_override(&"font_color", _c(&"text") if ok else _c(&"danger"))


func _confirm_input(event: InputEvent) -> bool:
	var used := true
	if event.is_action_pressed(&"ui_up", true):
		_confirm.move(-1)
	elif event.is_action_pressed(&"ui_down", true):
		_confirm.move(1)
	elif event.is_action_pressed(&"ui_accept"):
		choose(_confirm.cursor)
	elif event.is_action_pressed(&"ui_cancel"):
		_close_confirm()
	else:
		used = event.is_action_type()  # the page is modal: other actions do nothing meanwhile
	return used


func _close_confirm() -> void:
	_confirm.visible = false
	_status.visible = true


func _on_node_clicked(nid: StringName) -> void:
	if _confirm.visible:
		_close_confirm()
	if nid == cursor:
		request_act()
	else:
		set_cursor(nid)


static func _direction(event: InputEvent) -> Vector2:
	for action: StringName in DIRECTIONS:
		if event.is_action_pressed(action, true):
			return DIRECTIONS[action]
	return Vector2.ZERO
