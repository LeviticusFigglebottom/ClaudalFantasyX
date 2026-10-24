class_name FormationMenu
extends FieldSubmenu
## The field menu's Formation page (M2-MNU-07, SPEC §6.1 and §6.11): the active line on the left
## (one row per place), the reserve on the right (each hero and one open place), every hero with
## HP and MP and their gauges. Pick a hero, then the spot they go to: a hero there swaps with them
## (active with active reorders the line; active with reserve trades places), an open place takes
## them in. The line under the active line says what Confirm would do, or why not (pillar 4), and
## warns when a fallen hero would stand in the active line. Every move is saved at once
## (GameStateData.party_ids / reserve_ids) and the next live battle starts from it. Words and rules:
## FormationMenuModel over a PartySheet. Layout: game/data/ui/formation_menu.json.
##
## Input (keyboard and controller through ui_*): ui_up / ui_down move in the list with the input,
## ui_left / ui_right (and ui_page_up / ui_page_down) cross to the other list, ui_accept picks a
## hero and then moves them, ui_cancel puts a picked hero back and else closes. Mouse: hover a row
## to move there (either list), click to Confirm on it, the wheel steps the list with the input
## (over a row, that row's list); right click is Cancel (UiInput).

const DATA_PATH := "res://game/data/ui/formation_menu.json"
const ACTIVE_ID := &"formation_active"
const RESERVE_ID := &"formation_reserve"
const PORTRAIT_PAGE := &"formation"

var sheet: PartySheet
var model: FormationMenuModel
## The list with the input (FormationMenuModel.LINE_ACTIVE / LINE_RESERVE).
var focus: StringName = FormationMenuModel.LINE_ACTIVE
## The picked hero's spot ({line, index}), or {} while nobody is picked.
var chosen: Dictionary = {}

var _lists: Dictionary = {}
var _help: Label
var _name: Label
var _place: Label
var _chosen_line: Label
var _plan: Label
var _warn: Label
var _chosen_frame: Panel
## M2-MNU-301: the highlighted hero's portrait beside the detail lines.
var _portrait: HeroPortraitFrame
var _gauges: Array[HudGauge] = []
## The last move's result ({ok, text, warn}), shown until the cursor moves.
var _notice: Dictionary = {}


static func create(with_sheet: PartySheet = null) -> FormationMenu:
	var menu := FormationMenu.new()
	menu.sheet = with_sheet
	return menu


## Opens the page on its own CanvasLayer under `host` (null sheet = the live party).
static func open_in(host: Node, with_sheet: PartySheet = null) -> FormationMenu:
	return FieldSubmenu.mount(create(with_sheet), host) as FormationMenu


func data_path() -> String:
	return DATA_PATH


func data_section() -> String:
	return FormationMenuModel.DATA_SECTION


func list_page(line: StringName) -> MenuPage:
	return _lists.get(line) as MenuPage


## The list with the input.
func focus_page() -> MenuPage:
	return list_page(focus)


## The spot under the cursor: {line, index}.
func cursor_spot() -> Dictionary:
	return {"line": focus, "index": focus_page().cursor}


## The hero under the cursor (&"" on an open place).
func current_hero() -> StringName:
	return model.hero_at(focus, focus_page().cursor)


func help_text() -> String:
	return _help.text


func plan_text() -> String:
	return _plan.text


func warn_text() -> String:
	return _warn.text


func chosen_text() -> String:
	return _chosen_line.text


## True when the plan line shows a refusal (danger).
func plan_refused() -> bool:
	return not bool(_shown_plan().get("ok", false))


func row_gauges() -> Array[HudGauge]:
	return _gauges.duplicate()


func portrait() -> HeroPortraitFrame:
	return _portrait


## The frame around the picked hero's row (hidden while nobody is picked).
func chosen_frame() -> Panel:
	return _chosen_frame


func handle_input(event: InputEvent) -> bool:
	if not is_open():
		return false
	var step := 0
	if event.is_action_pressed(&"ui_up", true):
		step = -1
	elif event.is_action_pressed(&"ui_down", true):
		step = 1
	else:
		step = _wheel(event)
	if step != 0:
		if focus_page().move(step):
			_moved()
		return true
	for action: StringName in [&"ui_left", &"ui_right", &"ui_page_up", &"ui_page_down"]:
		if event.is_action_pressed(action, true):
			_switch_focus(_other(focus), focus_page().cursor)
			return true
	if event.is_action_pressed(&"ui_accept"):
		accept()
		return true
	if event.is_action_pressed(&"ui_cancel") and not chosen.is_empty():
		put_back()
		return true
	return super.handle_input(event)


## Confirm on the spot under the cursor: pick the hero there, or move the picked hero there.
func accept() -> void:
	var at := cursor_spot()
	if chosen.is_empty():
		var p := model.plan(&"", -1, at["line"], at["index"])
		if bool(p["ok"]):
			chosen = at
			_notice = {}
		else:
			_notice = p
		_render()
		return
	var hero := _hero_of(chosen)
	var result := model.move(chosen["line"], chosen["index"], at["line"], at["index"])
	if not bool(result["ok"]):
		_notice = result
		_render()
		return
	chosen = {}
	_notice = result if result["kind"] != FormationMenuModel.KIND_KEEP else {}
	_refresh_lists()
	var spot := model.spot_of(hero)
	if not spot.is_empty():
		_switch_focus(spot["line"], spot["index"], false)
	_render()


## Puts the picked hero back (nothing moves).
func put_back() -> void:
	chosen = {}
	_notice = {}
	_render()


func _build_page() -> void:
	if sheet == null:
		sheet = PartySheet.from_game()
	if model == null:
		model = FormationMenuModel.new(sheet, _d.get("rules", {}))
	_help = _framed_panel(_d.get("panel", {}), tr("FIELD_MENU_FORMATION"))
	for line: StringName in [FormationMenuModel.LINE_ACTIVE, FormationMenuModel.LINE_RESERVE]:
		var m: Dictionary = _d.get(line, {})
		var page := _menu_page(m, ACTIVE_ID if line == FormationMenuModel.LINE_ACTIVE else RESERVE_ID, " ", 1)
		page.row_hovered.connect(_on_hovered.bind(line))
		page.row_clicked.connect(_on_clicked.bind(line))
		_lists[line] = page
	_chosen_frame = Panel.new()
	_chosen_frame.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_chosen_frame.add_theme_stylebox_override(&"panel", _frame_style())
	add_child(_chosen_frame)
	_portrait = HeroPortraitFrame.new()
	add_child(_portrait)
	_name = _label(&"HeaderLabel", Rect2())
	_place = _label(&"DimLabel", Rect2())
	_chosen_line = _wrapping(&"HelpLabel")
	_plan = _wrapping(&"HelpLabel")
	_warn = _wrapping(&"HelpLabel")
	_refresh_lists()
	_switch_focus(FormationMenuModel.LINE_ACTIVE, 0, false)
	_render()


## Rebuilds both lists from the model (titles, rows, heights, gauges).
func _refresh_lists() -> void:
	for line: StringName in _lists:
		var page := list_page(line)
		var m: Dictionary = _d.get(line, {})
		var rows := model.rows(line)
		page.replace_rows(rows)
		page.set_header(model.title(line))
		page.size.y = MenuPage.height_for(m, rows.size(), true)
	_place_gauges()


## Gives `line` the input with its cursor on `index` (clamped); the other list hides its cursor.
func _switch_focus(line: StringName, index: int, render: bool = true) -> void:
	focus = line
	var page := focus_page()
	page.set_cursor(clampi(index, 0, page.row_count() - 1), false)
	for l: StringName in _lists:
		list_page(l).set_cursor_shown(l == focus)
	if render:
		_moved()


func _moved() -> void:
	_notice = {}
	_render()


func _render() -> void:
	_help.text = tr("FORMATION_MENU_HELP" if chosen.is_empty() else "FORMATION_MENU_HELP_PICKED")
	var at := cursor_spot()
	var hero := current_hero()
	_name.text = sheet.hero_name(hero) if hero != &"" else tr(FormationMenuModel.OPEN_KEY)
	var fallen := hero != &"" and bool(model.vitals(hero)["fallen"])
	_portrait.show_hero(hero, _name.text, HeroPortraits.page_emotion(PORTRAIT_PAGE, fallen))
	_place.text = model.place_text(at["line"], at["index"])
	_chosen_line.text = model.chosen_text(_hero_of(chosen)) if not chosen.is_empty() else ""
	var p := _shown_plan()
	_plan.text = str(p.get("text", ""))
	_plan.add_theme_color_override(&"font_color", _c(&"text") if bool(p.get("ok", false)) else _c(&"danger"))
	_warn.text = str(p.get("warn", ""))
	_warn.add_theme_color_override(&"font_color", _c(&"focus_gold"))
	_place_chosen_frame()
	_layout_detail()


## The plan for the cursor (or the last result, until the cursor moves).
func _shown_plan() -> Dictionary:
	if not _notice.is_empty():
		return _notice
	var at := cursor_spot()
	if chosen.is_empty():
		return model.plan(&"", -1, at["line"], at["index"])
	return model.plan(chosen["line"], chosen["index"], at["line"], at["index"])


## Name, place, the pick, the plan and the warning, stacked under the active line by their
## measured heights (they wrap at any text size).
func _layout_detail() -> void:
	var dm: Dictionary = _d.get("detail", {})
	var r := HudLayout.rect_of(dm)
	var active := list_page(FormationMenuModel.LINE_ACTIVE)
	var y := active.position.y + active.size.y + HudLayout.num(dm, "gap")
	var bottom := y + r.size.y
	var pm: Dictionary = _d.get("portrait", {})
	var side := HudLayout.num(pm, "size")
	_portrait.position = Vector2(r.position.x, y)
	_portrait.size = Vector2(side, side)
	var indent := side + HudLayout.num(pm, "gap")
	r = Rect2(r.position.x + indent, r.position.y, r.size.x - indent, r.size.y)
	var line_gap := HudLayout.num(dm, "line_gap")
	_name.position = Vector2(r.position.x, y)
	_name.size = Vector2(r.size.x, HudLayout.num(dm, "name_height"))
	y += _name.size.y
	_place.position = Vector2(r.position.x, y)
	_place.size = Vector2(r.size.x, HudLayout.num(dm, "line_height"))
	y += _place.size.y + line_gap
	for l: Label in [_chosen_line, _plan, _warn]:
		l.position = Vector2(r.position.x, y)
		l.size = Vector2(r.size.x, 0.0)
		l.visible = l.text != "" and y < bottom
		if not l.visible:
			continue
		var h := _text_height(l)
		l.update_minimum_size()  # its wrapped height at the new width, not at the last one (M2-UI-29)
		l.size = Vector2(r.size.x, minf(h, maxf(bottom - y, 0.0)))
		y += h + line_gap


## The height `l` needs for its text at its width (line count times the font's line height).
func _text_height(l: Label) -> float:
	var font := l.get_theme_font(&"font")
	var font_size := l.get_theme_font_size(&"font_size")
	var para := TextParagraph.new()
	para.width = l.size.x
	para.break_flags = TextServer.BREAK_MANDATORY | TextServer.BREAK_WORD_BOUND | TextServer.BREAK_ADAPTIVE
	para.add_string(l.text, font, font_size)
	return para.get_size().y + float(l.get_theme_constant(&"line_spacing")) * maxf(para.get_line_count() - 1.0, 0.0)


func _place_chosen_frame() -> void:
	_chosen_frame.visible = not chosen.is_empty()
	if chosen.is_empty():
		return
	var page := list_page(chosen["line"])
	var inset := HudLayout.num(_d.get("chosen", {}), "inset_px")
	var r := page.row_rect(int(chosen["index"])).grow(-inset)
	_chosen_frame.position = page.position + r.position
	_chosen_frame.size = r.size


func _frame_style() -> StyleBoxFlat:
	var s := StyleBoxFlat.new()
	s.draw_center = false
	s.border_color = _c(&"focus_gold")
	s.set_border_width_all(int(HudLayout.num(_d.get("chosen", {}), "border_px")))
	return s


## An HP and an MP gauge under each hero row's numbers (as the Items picker).
func _place_gauges() -> void:
	for g in _gauges:
		g.queue_free()
	_gauges.clear()
	var gm: Dictionary = _d.get("gauge", {})
	var h := HudLayout.num(gm, "height")
	var gap := HudLayout.num(gm, "gap")
	for line: StringName in _lists:
		var page := list_page(line)
		var m: Dictionary = _d.get(line, {})
		var indent := HudLayout.num(m, "text_indent") - HudLayout.num(m, "row_inset")
		var cost_w := HudLayout.num(m, "cost_width")
		var rank_w := HudLayout.num(m, "rank_width")
		var shown := mini(page.row_count(), int(HudLayout.num(m, "max_rows")))
		for i in shown:
			var cid := model.hero_at(line, i)
			if cid == &"":
				continue
			var v := model.vitals(cid)
			var r := page.row_rect(i)
			var y := page.position.y + r.end.y - HudLayout.num(gm, "inset_bottom") - h
			var right_edge := page.position.x + r.end.x - indent * 0.5
			_gauge(&"hp", Rect2(right_edge - cost_w, y, cost_w - rank_w - gap, h), int(v["hp"]), int(v["max_hp"]))
			_gauge(&"mp", Rect2(right_edge - rank_w, y, rank_w, h), int(v["mp"]), int(v["max_mp"]))


func _gauge(role: StringName, r: Rect2, value: int, maximum: int) -> void:
	var g := HudGauge.new(role)
	g.position = r.position
	g.size = r.size
	g.set_value(value, maximum)
	add_child(g)
	_gauges.append(g)


func _wrapping(variation: StringName) -> Label:
	var l := _label(variation, Rect2())
	l.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	l.vertical_alignment = VERTICAL_ALIGNMENT_TOP
	return l


func _hero_of(spot: Dictionary) -> StringName:
	return model.hero_at(spot.get("line", &""), int(spot.get("index", -1))) if not spot.is_empty() else &""


func _on_hovered(index: int, line: StringName) -> void:
	if line != focus:
		_switch_focus(line, index)
	else:
		_moved()


func _on_clicked(index: int, line: StringName) -> void:
	if not is_open():
		return
	if line != focus or focus_page().cursor != index:
		_switch_focus(line, index, false)
	accept()


static func _other(line: StringName) -> StringName:
	return FormationMenuModel.LINE_RESERVE if line == FormationMenuModel.LINE_ACTIVE else FormationMenuModel.LINE_ACTIVE


## -1 / 1 for a mouse wheel turn up / down, else 0.
static func _wheel(event: InputEvent) -> int:
	var mb := event as InputEventMouseButton
	if mb == null or not mb.pressed:
		return 0
	if mb.button_index == MOUSE_BUTTON_WHEEL_UP:
		return -1
	return 1 if mb.button_index == MOUSE_BUTTON_WHEEL_DOWN else 0


## M2-AUD-15 (audio listens, never edits; ADR 0031): true while the line on show is a refused pick or move.
func is_refused() -> bool:
	return not _notice.is_empty() and not bool(_notice.get("ok", true))
