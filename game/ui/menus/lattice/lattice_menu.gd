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
## M3-MNU-04: toggles the whole-board overview (lattice_menu.json overview.action; remappable).
const OVERVIEW_ACTION := &"lattice_overview"
const DATA_PATH := "res://game/data/ui/lattice_menu.json"
const PORTRAIT_PAGE := &"lattice"

var sheet: PartySheet
var model: LatticeMenuModel
## The node under the cursor.
var cursor: StringName = &""

var _board: LatticeBoardView
var _confirm: MenuPage
var _plan: Dictionary = {}
var _hero_label: Label
## M2-MNU-301: the hero on show's head beside the hero line.
var _portrait: HeroPortraitFrame
var _points: Label
var _facets: Label
var _node_title: Label
var _node_gives: Label
var _node_facet: Label
var _node_woken: Label
var _plan_line: Label
var _status: Label
var _legend: LatticeLegend
## The side panel's lines, top to bottom (_layout_side stacks them).
var _flow: Array[Control] = []
var _help: Label
var _overview_button: Button


static func create(with_sheet: PartySheet = null) -> LatticeMenu:
	var menu := LatticeMenu.new()
	menu.sheet = with_sheet
	return menu


## Opens the page on its own CanvasLayer under `host` (null sheet = the live party).
static func open_in(host: Node, with_sheet: PartySheet = null) -> LatticeMenu:
	return FieldSubmenu.mount(create(with_sheet), host) as LatticeMenu


func data_path() -> String:
	return DATA_PATH


func portrait() -> HeroPortraitFrame:
	return _portrait


func data_section() -> String:
	return "lattice_menu"


## Adds the overview action to the InputMap when it is missing (the page's _build_page calls it, and
## the Controls page before it captures its defaults, so the action is remappable).
static func ensure_action() -> void:
	var page := FieldInput.load_json(DATA_PATH).get("lattice_menu", {}) as Dictionary
	var o := page.get("overview", {}) as Dictionary
	FieldInput.add_actions(o.get("action", {}) as Dictionary, float(o.get("deadzone", 0.0)))


func handle_input(event: InputEvent) -> bool:
	if not is_open():
		return false
	InputNames.note(event, float((_d.get("overview", {}) as Dictionary).get("deadzone", 0.0)))
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
	elif event.is_action_pressed(OVERVIEW_ACTION):
		toggle_overview()
	else:
		used = super(event)
	return used


## M3-MNU-04: the whole board at a glance, or back to the cursor view on the same node. The cursor,
## the side panel and every action work the same in both.
func toggle_overview(animate: bool = true) -> void:
	_board.set_overview(not _board.overview, animate)


func is_overview() -> bool:
	return _board.overview


func overview_button() -> Button:
	return _overview_button


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
	_layout_side()


## Chooses confirm row `index` (0 does it, 1 steps back).
func choose(index: int) -> void:
	if not _confirm.visible:
		return
	_confirm.set_cursor(index, false)
	var row := _confirm.current_row()
	_close_confirm()
	if StringName(str(row.get("id", ""))) != ROW_DO:
		return
	var action := StringName(str(model.plan(cursor)["action"]))
	var result := model.act(cursor)
	_board.center_on(cursor, true)
	_refresh()
	_say(str(result["text"]), bool(result["ok"]))
	if bool(result["ok"]) and action in [LatticeMenuModel.ACT_ACTIVATE, LatticeMenuModel.ACT_OPEN]:
		_board.play_wake(cursor)  # pillar 5: the node visibly wakes


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
	_portrait = HeroPortraitFrame.new()
	_portrait.crop = HeroPortraitFrame.Crop.FACE
	HudLayout.place(_portrait, _d.get("portrait", {}))
	add_child(_portrait)
	var bm: Dictionary = _d.get("board", {})
	_board = LatticeBoardView.new()
	HudLayout.place(_board, bm)
	_board.reduced_motion = UiSettings.shared().reduced_motion()
	_board.setup(bm, model, _d.get("overview", {}))
	_board.node_clicked.connect(_on_node_clicked)
	_board.overview_changed.connect(func(_on: bool) -> void: _label_overview_button())
	add_child(_board)
	_build_side()
	_build_overview_button()
	_confirm = _menu_page(_d.get("confirm", {}), CONFIRM_PAGE_ID, " ", 2)
	_confirm.row_hovered.connect(func(i: int) -> void: _confirm.set_cursor(i))
	_confirm.row_clicked.connect(choose)
	_confirm.visible = false
	cursor = model.position()
	if cursor == &"" and not model.board().nodes.is_empty():
		cursor = model.board().nodes.keys()[0]
	_board.center_on(cursor, false)
	_refresh()


func _build_overview_button() -> void:
	ensure_action()
	var bm: Dictionary = (_d.get("overview", {}) as Dictionary).get("button", {})
	var frame := Panel.new()  # the button's frame: a small tide-notch panel, exactly its size
	frame.theme_type_variation = &"PanelSmall"
	frame.mouse_filter = Control.MOUSE_FILTER_IGNORE
	HudLayout.place(frame, bm)
	add_child(frame)
	# M2-MNU-11: the banner title ends before the button's frame (it spanned the panel, under the button).
	if _title_label != null:
		_title_label.size.x = maxf(frame.position.x - _title_label.position.x - HudLayout.num(bm, "title_gap"), 0.0)
		_title_label.clip_text = true
		_title_label.text_overrun_behavior = TextServer.OVERRUN_TRIM_ELLIPSIS
	_overview_button = Button.new()
	_overview_button.theme_type_variation = &"CommandButton"
	_overview_button.focus_mode = Control.FOCUS_NONE
	_overview_button.pressed.connect(toggle_overview)
	HudLayout.place(_overview_button, bm)
	add_child(_overview_button)
	_label_overview_button()


## The button names what it does and the key (or pad button, once the pad was used) that does it too.
func _label_overview_button() -> void:
	var key := InputNames.first_name(OVERVIEW_ACTION)
	if _board.overview:
		_overview_button.text = tr("LATTICE_MENU_OVERVIEW_BACK_FMT").format({"key": key})
	else:
		_overview_button.text = tr("LATTICE_MENU_OVERVIEW_FMT").format({"key": key})


func _build_side() -> void:
	var sm: Dictionary = _d.get("side", {})
	var side := PanelContainer.new()
	side.theme_type_variation = &"PanelSmall"
	side.mouse_filter = Control.MOUSE_FILTER_IGNORE
	HudLayout.place(side, sm)
	add_child(side)
	_points = _side_label(&"MenuLabel")
	_points.add_theme_color_override(&"font_color", _c(&"focus_gold"))
	_facets = _side_label(&"DimLabel")
	var rule := OrnamentRule.new()
	rule.custom_minimum_size = Vector2(
		0.0, float(get_theme_constant(&"ornament_node_px", HymnThemeBuilder.PALETTE_TYPE)) * 2.0
	)
	add_child(rule)
	_flow.append(rule)
	_node_title = _side_label(&"BodyLabel")
	_node_gives = _side_label(&"SmallLabel")
	_node_facet = _side_label(&"DimLabel")
	_node_woken = _side_label(&"DimLabel")
	_plan_line = _side_label(&"MenuLabel")
	var legend_metrics: Dictionary = _d.get("legend", {})
	_legend = LatticeLegend.new()
	HudLayout.place(_legend, legend_metrics)
	add_child(_legend)
	_legend.setup_legend(_d.get("board", {}), legend_metrics, model.legend_rows())
	_status = _label(&"HelpLabel", HudLayout.rect_of(_d.get("status", {})))
	_status.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	_status.vertical_alignment = VERTICAL_ALIGNMENT_TOP
	UiSettings.shared().changed.connect(_on_settings_changed)


## A side-panel line, stacked by _layout_side in the order made.
func _side_label(variation: StringName) -> Label:
	var l := Label.new()
	l.theme_type_variation = variation
	l.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	l.mouse_filter = Control.MOUSE_FILTER_IGNORE
	# Its width before any text: a wrapped label shapes (and caches its minimum height) at the width
	# it has when its text first changes, and a 0-wide label would reserve a line per letter.
	var sm: Dictionary = _d.get("side", {})
	l.size = Vector2(HudLayout.rect_of(sm).size.x - HudLayout.num(sm, "pad") * 2.0, 0.0)
	add_child(l)
	_flow.append(l)
	return l


## Stacks the side panel by measured height (text size and wrapping change it; M2-MNU-05): the lines
## from the top, each as tall as its wrapped text; the foot (the confirm, else the status line, grown
## upward to fit its text) at the bottom; the key at its own row when the lines end above it, else
## right under them, and hidden when it would reach the foot. Nothing overlaps at any text size.
func _layout_side() -> void:
	if _legend == null or not is_instance_valid(_legend):
		return
	var sm: Dictionary = _d.get("side", {})
	var r := HudLayout.rect_of(sm)
	var pad := HudLayout.num(sm, "pad")
	var gap := HudLayout.num(sm, "gap")
	var x := r.position.x + pad
	var w := r.size.x - pad * 2.0
	var foot_top := r.end.y - pad
	if _confirm != null and _confirm.visible:
		foot_top = _confirm.position.y
	elif _status.visible and _status.text != "":
		var home := HudLayout.rect_of(_d.get("status", {}))
		var sh := _measure(_status, home.size.x)
		_status.position = Vector2(home.position.x, minf(home.position.y, r.end.y - pad - sh))
		_resize(_status, Vector2(home.size.x, sh))
		foot_top = _status.position.y
	var y := r.position.y + pad
	for c in _flow:
		if c.visible:
			var h := _measure(c, w)
			c.position = Vector2(x, y)
			_resize(c, Vector2(w, h))
			y += h + gap
	var lm: Dictionary = _d.get("legend", {})
	var legend_at := maxf(HudLayout.rect_of(lm).position.y, y)
	var shown := _legend.fit(foot_top - HudLayout.num(sm, "foot_gap") - legend_at)
	_legend.position.y = legend_at
	_legend.size.y = _legend.content_height()
	_legend.visible = shown >= int(HudLayout.num(lm, "min_rows"))


## Sizes `c` to `to`, width first: a wrapped label's minimum height is shaped at its width at the
## time, so setting both at once would clamp the height to what the old (narrower) width needed.
func _resize(c: Control, to: Vector2) -> void:
	c.size = Vector2(to.x, 0.0)
	c.size = to


## The height `c` needs at width `w`. A wrapped label is measured from its theme font as Label lays it
## out (each line the font's height, line_spacing between), not from its cached minimum size, which
## lags a text or theme change by a frame.
func _measure(c: Control, w: float) -> float:
	var l := c as Label
	if l == null:
		return c.get_combined_minimum_size().y
	var font := l.get_theme_font(&"font")
	var fs := l.get_theme_font_size(&"font_size")
	var para := TextParagraph.new()
	para.break_flags = TextServer.BREAK_MANDATORY | TextServer.BREAK_WORD_BOUND | TextServer.BREAK_ADAPTIVE
	para.width = w
	para.add_string(l.text, font, fs)
	var lines := maxi(para.get_line_count(), 1)
	var spacing := float(l.get_theme_constant(&"line_spacing"))
	return lines * font.get_height(fs) + (lines - 1) * spacing


## The side panel's flowing lines and the key, as laid out now (tests check that none overlap).
func side_rects() -> Array[Rect2]:
	var out: Array[Rect2] = []
	for c: Control in _flow + [_legend, _status, _confirm]:
		if c.visible and (not c is Label or (c as Label).text != ""):
			out.append(c.get_rect())
	return out


## Redraws the board marks and the side panel for the cursor node and the hero on show.
func _refresh() -> void:
	var list := model.heroes()
	if list.is_empty():
		_hero_label.text = ""
		_portrait.show_hero(&"", "")
	else:
		_hero_label.text = tr("LATTICE_MENU_HERO_FMT").format(
			{"name": model.hero_name(), "i": model.hero_index + 1, "n": list.size()}
		)
		_portrait.show_hero(model.hero(), model.hero_name(), HeroPortraits.page_emotion(PORTRAIT_PAGE))
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
	_layout_side()


func _tag(p: Dictionary, path: Array[StringName]) -> String:
	if p.has("need") and bool(p["ok"]):
		return tr("LATTICE_MENU_TAG_FACET_FMT").format({"n": int(p["need"]), "facet": str(p["facet"])})
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
	_layout_side()


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
	_layout_side()


## Text size changed while open: the theme follows (UiSettings.follow), so measure again once it has.
func _on_settings_changed(_key: StringName) -> void:
	_layout_side.call_deferred()


func _exit_tree() -> void:
	super()
	if UiSettings.shared().changed.is_connected(_on_settings_changed):
		UiSettings.shared().changed.disconnect(_on_settings_changed)


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
