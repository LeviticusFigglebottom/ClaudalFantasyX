class_name MagicMenu
extends FieldSubmenu
## The field menu's Magic page (M3-UI-1251; the human's playtest FAST-TRACK 5, 2026-11-03): a hero casts a field-usable
## spell (Mend and the like) on the party outside battle, paying its MP, with what it would do ("Asha: MP 60 → 56 ·
## Rhen: HP 120 → 220") before it is cast. Words and steps: MagicMenuModel over a PartySheet and combat-systems'
## rules (FieldMagicRules). Layout: game/data/ui/magic_menu.json.
##
## Three levels. CASTER: the heroes on the left (MP, how many field spells). SPELL: the caster's spells beside them,
## the chosen spell's cost and line (how to cast it, or why not) on the right. PICK: the heroes the spell can go to
## replace the right column, with the preview line under them. A cast writes the save at once and stays in PICK, so a
## second Mend is one more Confirm; the receipt stays until the cursor moves.
##
## Input (keyboard and controller through ui_*): ui_up / ui_down move, ui_accept goes on (or casts), ui_cancel goes
## back a level and closes from CASTER. Mouse: hover moves, a click chooses, the wheel steps.

enum Level { CASTER, SPELL, PICK }

const DATA_PATH := "res://game/data/ui/magic_menu.json"
const CASTER_ID := &"magic_casters"
const SPELL_ID := &"magic_spells"
const PICK_ID := &"magic_pick"

var sheet: PartySheet
var model: MagicMenuModel
var level := Level.CASTER
## The hero casting (SPELL and PICK) and the spell (PICK).
var caster: StringName = &""
var spell: StringName = &""

var _casters: MenuPage
var _spells: MenuPage
var _picker: MenuPage
var _help: Label
var _name: Label
var _cost: Label
var _use: Label
var _preview: Label
var _gauges: Array[HudGauge] = []
## A receipt or refusal that stays on its line until the cursor moves.
var _notice: Dictionary = {}


static func create(with_sheet: PartySheet = null, with_model: MagicMenuModel = null) -> MagicMenu:
	var menu := MagicMenu.new()
	menu.sheet = with_sheet
	menu.model = with_model
	return menu


## Opens the page on its own CanvasLayer under `host` (null sheet = the live party).
static func open_in(host: Node, with_sheet: PartySheet = null) -> MagicMenu:
	return FieldSubmenu.mount(create(with_sheet), host) as MagicMenu


func data_path() -> String:
	return DATA_PATH


func data_section() -> String:
	return "magic_menu"


func caster_page() -> MenuPage:
	return _casters


func spell_page() -> MenuPage:
	return _spells


func picker_page() -> MenuPage:
	return _picker


func help_text() -> String:
	return _help.text


## The line under the spell (or the caster): how to go on, or why not.
func use_text() -> String:
	return _use.text


## The line under the picker: what the cast would do, the receipt, or the refusal.
func preview_text() -> String:
	return _preview.text


func is_refused() -> bool:
	return not _notice.is_empty() and not bool(_notice.get("ok", true))


func handle_input(event: InputEvent) -> bool:
	if not is_open():
		return false
	if event.is_action_pressed(&"ui_up", true):
		_move(-1)
	elif event.is_action_pressed(&"ui_down", true):
		_move(1)
	elif _wheel(event) != 0:
		_move(_wheel(event))
	elif event.is_action_pressed(&"ui_accept"):
		accept()
	elif event.is_action_pressed(&"ui_cancel"):
		back()
	else:
		return false
	return true


## CASTER: to the hero's spells (one with none keeps its line). SPELL: to the picker (a refused spell keeps its
## line). PICK: casts.
func accept() -> void:
	_notice = {}
	match level:
		Level.CASTER:
			var cid := _id(_casters)
			if cid == &"" or model.spells_of(cid).is_empty():
				_render()
				return
			caster = cid
			level = Level.SPELL
			_spells.replace_rows(model.spell_rows(caster))
			_spells.set_cursor(0, false)
		Level.SPELL:
			var sid := _id(_spells)
			if sid == &"":
				return
			if model.spell_error(caster, sid) != MagicMenuModel.RESULT_OK:
				_notice = model.spell_line(caster, sid)
				_render()
				return
			spell = sid
			level = Level.PICK
			_picker.replace_rows(model.hero_rows(caster, spell))
			_picker.set_cursor(0, false)
		Level.PICK:
			var tid := _id(_picker)
			if tid == &"":
				return
			_notice = model.cast_on(caster, spell, tid)
			if bool(_notice.get("ok", false)):
				_refresh_rows()
	_render()


## Goes back one level; closes from CASTER.
func back() -> void:
	_notice = {}
	match level:
		Level.CASTER:
			close()
			return
		Level.SPELL:
			level = Level.CASTER
		Level.PICK:
			level = Level.SPELL
	_render()


func _build_page() -> void:
	if sheet == null:
		sheet = PartySheet.from_game()
	if model == null:
		model = MagicMenuModel.from_sheet(sheet)
	_help = _framed_panel(_d.get("panel", {}), tr("FIELD_MENU_MAGIC"))
	var cm: Dictionary = _d.get("casters", {})
	_casters = _menu_page(cm, CASTER_ID, tr("MAGIC_MENU_CASTERS"), sheet.heroes.size())
	_casters.row_hovered.connect(_on_hovered.bind(Level.CASTER))
	_casters.row_clicked.connect(_on_clicked.bind(Level.CASTER))
	var sm: Dictionary = _d.get("spells", {})
	_spells = _menu_page(sm, SPELL_ID, " ", int(HudLayout.num(sm, "max_rows")))
	_spells.row_hovered.connect(_on_hovered.bind(Level.SPELL))
	_spells.row_clicked.connect(_on_clicked.bind(Level.SPELL))
	_build_detail(_d.get("detail", {}))
	var pm: Dictionary = _d.get("picker", {})
	_picker = _menu_page(pm, PICK_ID, " ", sheet.heroes.size())
	_picker.row_hovered.connect(_on_hovered.bind(Level.PICK))
	_picker.row_clicked.connect(_on_clicked.bind(Level.PICK))
	_preview = _label(&"HelpLabel", Rect2())
	_preview.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	_preview.vertical_alignment = VERTICAL_ALIGNMENT_TOP
	_casters.replace_rows(model.caster_rows())
	_casters.set_cursor(0, false)
	_render()


func _build_detail(dm: Dictionary) -> void:
	var r := HudLayout.rect_of(dm)
	var line_h := HudLayout.num(dm, "line_height")
	var y := r.position.y
	_name = _label(&"HeaderLabel", Rect2(r.position.x, y, r.size.x, HudLayout.num(dm, "name_height")))
	y += _name.size.y
	_cost = _label(&"DimLabel", Rect2(r.position.x, y, r.size.x, line_h))
	y += line_h + HudLayout.num(dm, "gap")
	_use = _label(&"HelpLabel", Rect2(r.position.x, y, r.size.x, HudLayout.num(dm, "use_height")))
	_use.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	_use.vertical_alignment = VERTICAL_ALIGNMENT_TOP


## After a cast: the MP and HP on every list are as they stand now (cursors kept).
func _refresh_rows() -> void:
	_keep_cursor(_casters, model.caster_rows())
	_keep_cursor(_spells, model.spell_rows(caster))
	_keep_cursor(_picker, model.hero_rows(caster, spell))


static func _keep_cursor(page: MenuPage, rows: Array[Dictionary]) -> void:
	var at := page.cursor
	page.replace_rows(rows)
	page.set_cursor(clampi(at, 0, maxi(page.row_count() - 1, 0)), false)


func _render() -> void:
	var picking := level == Level.PICK
	_casters.set_dimmed(level != Level.CASTER)
	_spells.visible = level != Level.CASTER
	_spells.set_dimmed(picking)
	_picker.visible = picking
	for l: Label in [_name, _cost, _use]:
		l.visible = not picking
	_preview.visible = picking
	_help.text = tr(["MAGIC_MENU_HELP_CASTER", "MAGIC_MENU_HELP_SPELL", "MAGIC_MENU_HELP_PICK"][level])
	match level:
		Level.CASTER:
			_render_caster()
		Level.SPELL:
			_render_spell()
		Level.PICK:
			_render_pick()


func _render_caster() -> void:
	_clear_gauges()
	var cid := _id(_casters)
	_name.text = sheet.hero_name(cid) if cid != &"" else ""
	_cost.text = ""
	var line := _notice if not _notice.is_empty() else model.caster_line(cid)
	_use.text = str(line.get("text", ""))
	_set_role(_use, bool(line.get("ok", false)))


func _render_spell() -> void:
	_clear_gauges()
	_spells.set_header(tr("MAGIC_MENU_SPELLS_FMT").format({"name": sheet.hero_name(caster)}))
	_spells.size.y = MenuPage.height_for(_d.get("spells", {}), maxi(_spells.row_count(), 1), true)
	var sid := _id(_spells)
	_name.text = model.spell_name(sid) if sid != &"" else ""
	var reach := tr("MAGIC_MENU_REACH_ALL" if model.is_all_allies(sid) else "MAGIC_MENU_REACH_ONE")
	_cost.text = tr("MAGIC_MENU_COST_LINE_FMT").format({"mp": model.spell_cost(sid), "reach": reach})
	var line := _notice if not _notice.is_empty() else model.spell_line(caster, sid)
	_use.text = str(line.get("text", ""))
	_set_role(_use, bool(line.get("ok", false)))


func _render_pick() -> void:
	var pm: Dictionary = _d.get("picker", {})
	_picker.set_header(model.pick_title(caster, spell))
	_picker.size.y = MenuPage.height_for(pm, maxi(_picker.row_count(), 1), true)
	var pv: Dictionary = _d.get("preview", {})
	_preview.position = Vector2(_picker.position.x, _picker.position.y + _picker.size.y + HudLayout.num(pv, "gap"))
	_preview.size = Vector2(_picker.size.x, HudLayout.num(pv, "height"))
	_place_gauges(pm)
	var line := _notice if not _notice.is_empty() else model.preview(caster, spell, _id(_picker))
	_preview.text = str(line.get("text", ""))
	_set_role(_preview, bool(line.get("ok", false)))


## An HP and an MP gauge under each picker row's numbers (the Items page's).
func _place_gauges(pm: Dictionary) -> void:
	_clear_gauges()
	var gm: Dictionary = _d.get("gauge", {})
	var h := HudLayout.num(gm, "height")
	var gap := HudLayout.num(gm, "gap")
	var indent := HudLayout.num(pm, "text_indent") - HudLayout.num(pm, "row_inset")
	var cost_w := HudLayout.num(pm, "cost_width")
	var rank_w := HudLayout.num(pm, "rank_width")
	for i in _picker.row_count():
		var c := sheet.combatant(StringName(str(_picker.rows[i].get("id", ""))))
		if c == null:
			continue
		var r := _picker.row_rect(i)
		var y := _picker.position.y + r.end.y - HudLayout.num(gm, "inset_bottom") - h
		var right_edge := _picker.position.x + r.end.x - indent * 0.5
		_gauge(&"hp", Rect2(right_edge - cost_w, y, cost_w - rank_w - gap, h), c.hp, c.max_hp)
		_gauge(&"mp", Rect2(right_edge - rank_w, y, rank_w, h), c.mp, c.max_mp)


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


func _set_role(l: Label, ok: bool) -> void:
	l.add_theme_color_override(&"font_color", _c(&"text") if ok else _c(&"danger"))


func _page_of(of_level: Level) -> MenuPage:
	return [_casters, _spells, _picker][of_level] as MenuPage


func _move(delta: int) -> void:
	if _page_of(level).move(delta):
		_notice = {}
		_render()


static func _id(page: MenuPage) -> StringName:
	return StringName(str(page.current_row().get("id", "")))


## -1 / 1 for a mouse wheel turn up / down, else 0.
static func _wheel(event: InputEvent) -> int:
	var mb := event as InputEventMouseButton
	if mb == null or not mb.pressed:
		return 0
	if mb.button_index == MOUSE_BUTTON_WHEEL_UP:
		return -1
	return 1 if mb.button_index == MOUSE_BUTTON_WHEEL_DOWN else 0


func _on_hovered(_index: int, page_level: Level) -> void:
	if page_level == level:
		_notice = {}
		_render()


## A click on an earlier level's list goes back to it and chooses there; a later level's is ignored.
func _on_clicked(index: int, page_level: Level) -> void:
	if not is_open() or page_level > level:
		return
	level = page_level
	_notice = {}
	_page_of(level).set_cursor(index, false)
	_render()
	accept()
