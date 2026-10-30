class_name StatusMenu
extends FieldSubmenu
## The field menu's Status page (M2-MNU-03): one hero at a time, chosen from the list on the left.
## Name, level, HP and MP with gauges; every battle stat as its total with the split base + Lattice
## + gear (pillar 5: growth you can see); worn weapon and armor with their abilities; the Swell
## gauge and the fill mode in use; Lattice progress (movement points banked, nodes woken, skills
## learned there); and the statuses a fight would start with. Words: StatusMenuModel over a
## PartySheet. Layout: game/data/ui/status_menu.json. Nothing here changes the save.
##
## Input (keyboard and controller through ui_*): ui_up / ui_down, ui_left / ui_right and
## ui_page_up / ui_page_down change the hero (wrapping), ui_cancel closes. Mouse: hover or click a
## hero, the wheel steps.

const DATA_PATH := "res://game/data/ui/status_menu.json"
const LIST_ID := &"status_heroes"
const PORTRAIT_PAGE := &"status"

var sheet: PartySheet
var model: StatusMenuModel
## The hero on show (&"" with no heroes).
var hero: StringName = &""

var _list: MenuPage
var _help: Label
## M2-MNU-301: the hero's portrait beside the name and vitals.
var _portrait: HeroPortraitFrame
## Built per hero and freed on the next one (labels and gauges of the detail).
var _detail: Array[Control] = []
var _shown: Dictionary = {}


static func create(with_sheet: PartySheet = null) -> StatusMenu:
	var menu := StatusMenu.new()
	menu.sheet = with_sheet
	return menu


## Opens the page on its own CanvasLayer under `host` (null sheet = the live party).
static func open_in(host: Node, with_sheet: PartySheet = null) -> StatusMenu:
	return FieldSubmenu.mount(create(with_sheet), host) as StatusMenu


func data_path() -> String:
	return DATA_PATH


func data_section() -> String:
	return "status_menu"


func list_page() -> MenuPage:
	return _list


func help_text() -> String:
	return _help.text


func portrait() -> HeroPortraitFrame:
	return _portrait


## The StatusMenuModel.page() on show.
func shown_page() -> Dictionary:
	return _shown.duplicate(true)


## Every text on the detail side, in build order (tests read it).
func detail_texts() -> Array[String]:
	var out: Array[String] = []
	for n in _detail:
		if n is Label:
			out.append((n as Label).text)
	return out


func detail_gauges() -> Array[HudGauge]:
	var out: Array[HudGauge] = []
	for n in _detail:
		if n is HudGauge:
			out.append(n as HudGauge)
	return out


func handle_input(event: InputEvent) -> bool:
	if not is_open():
		return false
	var step := 0
	if event.is_action_pressed(&"ui_up", true) or event.is_action_pressed(&"ui_left", true):
		step = -1
	elif event.is_action_pressed(&"ui_down", true) or event.is_action_pressed(&"ui_right", true):
		step = 1
	elif event.is_action_pressed(&"ui_page_up", true):
		step = -1
	elif event.is_action_pressed(&"ui_page_down", true):
		step = 1
	else:
		step = _wheel(event)
	if step != 0:
		if _list.move(step):
			show_hero(StringName(str(_list.current_row().get("id", ""))))
		return true
	if event.is_action_pressed(&"ui_accept"):
		return true  # nothing to confirm: the page already shows the hero under the cursor
	return super.handle_input(event)


## Shows `cid` (the list cursor follows).
func show_hero(cid: StringName) -> void:
	for i in _list.row_count():
		if StringName(str(_list.rows[i].get("id", ""))) == cid:
			_list.set_cursor(i, false)
	hero = cid
	_render()


func _build_page() -> void:
	if sheet == null:
		sheet = PartySheet.from_game()
	if model == null:
		model = StatusMenuModel.new(sheet)
	_help = _framed_panel(_d.get("panel", {}), tr("FIELD_MENU_STATUS"))
	_help.text = tr("STATUS_MENU_HELP")
	var lm: Dictionary = _d.get("list", {})
	var rows := model.hero_rows()
	_list = _menu_page(lm, LIST_ID, "", rows.size())
	_list.replace_rows(rows)
	_list.row_hovered.connect(_on_row)
	_list.row_clicked.connect(_on_row)
	_portrait = HeroPortraitFrame.new()
	HudLayout.place(_portrait, _d.get("portrait", {}))
	add_child(_portrait)
	hero = StringName(str(_list.current_row().get("id", "")))
	_render()


func _render() -> void:
	for n in _detail:
		n.queue_free()
	_detail.clear()
	_shown = model.page(hero) if hero != &"" else {}
	if _shown.is_empty():
		_portrait.show_hero(&"", "")
		_add_label(&"HelpLabel", HudLayout.rect_of(_d.get("vitals", {})), tr("FIELD_MENU_NO_HEROES"))
		return
	var emotion := HeroPortraits.page_emotion(PORTRAIT_PAGE, bool(_shown["fallen"]))
	_portrait.show_hero(hero, str(_shown["name"]), emotion)
	_render_vitals(_d.get("vitals", {}))
	_render_stats(_d.get("stats", {}))
	var gap := HudLayout.num(_d.get("section", {}), "section_gap")
	var below := _render_swell(_d.get("swell", {}), _list.position.y + _list.size.y + gap)
	_render_carried(_d.get("carried", {}), below + gap)
	_render_side(_d.get("side", {}))


func _render_vitals(vm: Dictionary) -> void:
	var r := HudLayout.rect_of(vm)
	var sec: Dictionary = _d.get("section", {})
	var line_h := HudLayout.num(sec, "line_height")
	var name_h := HudLayout.num(vm, "name_height")
	var gauge_h := HudLayout.num(vm, "gauge_height")
	var gap := HudLayout.num(vm, "gap")
	_add_label(&"BannerLabel", Rect2(r.position.x, r.position.y, r.size.x, name_h), str(_shown["name"]))
	var lvl := _add_label(&"DimLabel", Rect2(r.position.x, r.position.y, r.size.x, name_h), str(_shown["level_text"]))
	lvl.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
	var y := r.position.y + name_h + gap
	# A note (Kerrid's after the reveal) tucks under the name row; the gap between the gauges narrows to keep the
	# block's height.
	var note := str(_shown.get("note", ""))
	var after_gauge := gap * 2.0
	if note != "":
		var note_y := r.position.y + name_h - HudLayout.num(vm, "note_lift")
		var nl := _add_label(
			&"HelpDimLabel", Rect2(r.position.x, note_y, r.size.x, HudLayout.num(vm, "note_height")), note
		)
		HudLayout.fit_label(nl, r.size.x, HudLayout.num(vm, "note_min_scale"))
		y = nl.position.y + nl.size.y + gap
		after_gauge = gap
	for v: Array in [["hp", "STATUS_MENU_HP", "max_hp"], ["mp", "STATUS_MENU_MP", "max_mp"]]:
		var role := StringName(str(v[0]))
		var tag := _add_label(&"HudName", Rect2(r.position.x, y, r.size.x, line_h), tr(str(v[1])))
		tag.add_theme_color_override(&"font_color", _c(&"text_dim"))
		var value := tr("STATUS_MENU_VITAL_FMT").format({"value": _shown[role], "max": _shown[v[2]]})
		var num := _add_label(&"HudNumber", Rect2(r.position.x, y, r.size.x, line_h), value)
		num.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
		if role == &"hp" and bool(_shown["fallen"]):
			num.text = "%s  %s" % [tr(StatusMenuModel.FALLEN_KEY), num.text]
			num.add_theme_color_override(&"font_color", _c(&"danger"))
		y += line_h + gap
		_add_gauge(role, Rect2(r.position.x, y, r.size.x, gauge_h), int(_shown[role]), int(_shown[v[2]]))
		y += gauge_h + after_gauge


func _render_stats(sm: Dictionary) -> void:
	var r := HudLayout.rect_of(sm)
	var widths: Array = sm.get("columns", [])
	var head_h := HudLayout.num(sm, "header_height")
	var pitch := HudLayout.num(sm, "row_pitch")
	var heads := ["", tr("STATUS_MENU_COL_TOTAL"), tr("STATUS_MENU_COL_BASE"), tr("STATUS_MENU_COL_LATTICE")]
	heads.append(tr("STATUS_MENU_COL_GEAR"))
	_row_cells(r.position, widths, head_h, heads, [&"text_dim", &"text_dim", &"text_dim", &"text_dim", &"text_dim"])
	_rule(Rect2(r.position.x, r.position.y + head_h, r.size.x, 0.0))
	var y := r.position.y + head_h
	for st: Dictionary in _shown["stats"]:
		var texts := [
			str(st["label"]),
			str(st["total"]),
			str(st["base"]),
			model.growth_text(int(st["lattice"])),
			model.growth_text(int(st["gear"])),
		]
		var roles := [&"text", &"text", &"text_dim", _growth_role(int(st["lattice"]), &"focus_gold")]
		roles.append(_growth_role(int(st["gear"]), &"mp"))
		_row_cells(Vector2(r.position.x, y), widths, pitch, texts, roles)
		y += pitch


func _growth_role(amount: int, up: StringName) -> StringName:
	if amount == 0:
		return &"text_disabled"
	return up if amount > 0 else &"danger"


## One table row: the first cell left-aligned, the numbers right-aligned in tabular figures.
func _row_cells(at: Vector2, widths: Array, h: float, texts: Array, roles: Array) -> void:
	var x := at.x
	for i in texts.size():
		var w := float(widths[i]) if i < widths.size() else 0.0
		var variation := &"HudName" if i == 0 else &"HudNumber"
		var l := _add_label(variation, Rect2(x, at.y, w, h), str(texts[i]))
		l.horizontal_alignment = HORIZONTAL_ALIGNMENT_LEFT if i == 0 else HORIZONTAL_ALIGNMENT_RIGHT
		l.add_theme_color_override(&"font_color", _c(StringName(str(roles[i]))))
		x += w


## The Swell section from `top` (under the hero list). Returns the y under it.
func _render_swell(wm: Dictionary, top: float) -> float:
	var r := HudLayout.rect_of(wm)
	r.position.y = top
	var sw: Dictionary = _shown["swell"]
	var y := _section_header(r, tr("STATUS_MENU_SWELL"))
	var gap := HudLayout.num(wm, "gap")
	if bool(sw["has"]):
		var gh := HudLayout.num(wm, "gauge_height")
		_add_gauge(&"swell", Rect2(r.position.x, y + gap, r.size.x, gh), int(sw["points"]), int(sw["max"]))
		y += gh + gap * 2.0
	return _line(Rect2(r.position.x, y, r.size.x, 0.0), str(sw["text"]), &"text")


func _render_carried(cm: Dictionary, top: float) -> void:
	var r := HudLayout.rect_of(cm)
	r.position.y = top
	var y := _section_header(r, tr("STATUS_MENU_CARRIED"))
	var names: Array = _shown["statuses"]
	var none := names.size() == 1 and str(names[0]) == tr(StatusMenuModel.NONE_KEY)
	var text := tr(StatusMenuModel.JOIN_KEY).join(PackedStringArray(names))
	y = _line(Rect2(r.position.x, y, r.size.x, 0.0), text, &"text_dim" if none else &"danger", true)
	var descs: Array = _shown.get("status_descs", [])
	var lines := int(HudLayout.num(cm, "desc_lines"))
	for desc: String in descs:  # what each one does; one alone needs no name, it is just above
		var shown := desc.get_slice(": ", 1) if descs.size() == 1 else desc
		y = _line(Rect2(r.position.x, y, r.size.x, 0.0), shown, &"text_dim", true, &"HelpDimLabel", lines)


func _render_side(sm: Dictionary) -> void:
	var r := HudLayout.rect_of(sm)
	var sec: Dictionary = _d.get("section", {})
	var line_h := HudLayout.num(sec, "line_height")
	var y := _section_header(Rect2(r.position, Vector2(r.size.x, 0.0)), tr("STATUS_MENU_GEAR"))
	for g: Dictionary in _shown["gear"]:
		var slot := _add_label(&"DimLabel", Rect2(r.position.x, y, r.size.x, line_h), str(g["slot_label"]))
		slot.vertical_alignment = VERTICAL_ALIGNMENT_BOTTOM
		y += line_h
		_line(Rect2(r.position.x, y, r.size.x, 0.0), str(g["name"]), &"text", false, &"MenuLabel")
		y += line_h
		if str(g["abilities"]) != "":
			y = _line(Rect2(r.position.x, y, r.size.x, 0.0), str(g["abilities"]), &"swell", true)
	y += HudLayout.num(sec, "section_gap")
	y = _section_header(Rect2(r.position.x, y, r.size.x, 0.0), tr("STATUS_MENU_LATTICE"))
	var lines: Array = (_shown["lattice"] as Dictionary)["lines"]
	for i in lines.size():
		y = _line(Rect2(r.position.x, y, r.size.x, 0.0), str(lines[i]), &"text", i == lines.size() - 1)
	# A caller's Vowbound (Act II screens.md section 3), here rather than under Swell: the left column has no room
	# once all seven heroes are in the list.
	var bound: Dictionary = _shown.get("bound", {})
	if bool(bound.get("has", false)):
		y += HudLayout.num(sec, "section_gap")
		y = _section_header(Rect2(r.position.x, y, r.size.x, 0.0), tr(StatusMenuModel.BOUND_KEY))
		_line(Rect2(r.position.x, y, r.size.x, 0.0), str(bound["text"]), &"text", true)


## A section title with the gold rule under it at `r`'s top. Returns the y under it.
func _section_header(r: Rect2, text: String) -> float:
	var h := HudLayout.num(_d.get("section", {}), "header_height")
	_add_label(&"HeaderLabel", Rect2(r.position.x, r.position.y, r.size.x, h), text)
	_rule(Rect2(r.position.x, r.position.y + h, r.size.x, 0.0))
	return r.position.y + h + HudLayout.num(_d.get("section", {}), "line_height") * 0.25


## One line of text (wrapping onto up to wrap_lines lines when `wrap`). Returns the y under it.
func _line(
	r: Rect2, text: String, role: StringName, wrap: bool = false, variation: StringName = &"HudName", lines: int = 0
) -> float:
	var sec: Dictionary = _d.get("section", {})
	var line_h := HudLayout.num(sec, "line_height")
	var wrap_lines := float(lines) if lines > 0 else HudLayout.num(sec, "wrap_lines")
	var h := line_h * (wrap_lines if wrap else 1.0)
	var l := _add_label(variation, Rect2(r.position.x, r.position.y, r.size.x, h), text)
	l.add_theme_color_override(&"font_color", _c(role))
	if wrap:
		l.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		l.vertical_alignment = VERTICAL_ALIGNMENT_TOP
		l.max_lines_visible = int(wrap_lines)
		l.text_overrun_behavior = TextServer.OVERRUN_TRIM_ELLIPSIS
		l.size = Vector2(r.size.x, h)  # M2-MNU-11: the text, set before autowrap, had widened it to one line
		return r.position.y + line_h * maxf(1.0, float(mini(l.get_line_count(), l.max_lines_visible)))
	l.text_overrun_behavior = TextServer.OVERRUN_TRIM_ELLIPSIS
	return r.position.y + h


func _rule(r: Rect2) -> void:
	var rule := OrnamentRule.new()
	var node := float(get_theme_constant(&"ornament_node_px", HymnThemeBuilder.PALETTE_TYPE))
	rule.position = Vector2(r.position.x, r.position.y - node)
	rule.size = Vector2(r.size.x, node * 2.0)
	add_child(rule)
	_detail.append(rule)


func _add_label(variation: StringName, r: Rect2, text: String) -> Label:
	var l := _label(variation, r)
	l.text = text
	_detail.append(l)
	return l


func _add_gauge(role: StringName, r: Rect2, value: int, maximum: int) -> void:
	var g := HudGauge.new(role)
	g.position = r.position
	g.size = r.size
	g.set_value(value, maximum)
	add_child(g)
	_detail.append(g)


func _on_row(index: int) -> void:
	if index >= 0 and index < _list.row_count():
		show_hero(StringName(str(_list.rows[index].get("id", ""))))


## -1 / 1 for a mouse wheel turn up / down, else 0.
static func _wheel(event: InputEvent) -> int:
	var mb := event as InputEventMouseButton
	if mb == null or not mb.pressed:
		return 0
	if mb.button_index == MOUSE_BUTTON_WHEEL_UP:
		return -1
	return 1 if mb.button_index == MOUSE_BUTTON_WHEEL_DOWN else 0
