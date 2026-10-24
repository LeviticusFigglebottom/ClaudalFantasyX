class_name EquipMenu
extends FieldSubmenu
## The field menu's Equip page (M2-MNU-02, SPEC §6.5): each hero's weapon and armor with their
## ability slots, a stat-delta preview before anything is worn, and Customize (craft an ability
## into an empty slot with items). Words and rules: EquipMenuModel over a PartySheet. Layout:
## game/data/ui/equip_menu.json. docs/kb/tech/ui.md "Equip and Customize pages".
##
## Four levels, left to right: HEROES (the party) -> GEAR (the hero's slots, each followed by its
## piece's ability slots) -> PIECES (what the hero can wear in that slot, a "· Customize" row under
## each spare piece with an empty slot, and "Take it off") or RECIPES (Customize: what can be
## crafted into the chosen empty slot, of a worn piece from GEAR or a spare from PIECES; Cancel and
## a craft return where it came from, M2-MNU-09). The preview on the right
## shows each stat now -> after, the delta in the gain or loss color with its sign (not hue alone),
## and the abilities gained or lost, or the recipe with what is held and what is short.
##
## Input (keyboard and controller through ui_*): ui_up / ui_down move; ui_left / ui_right and
## ui_page_up / ui_page_down change hero on GEAR; ui_accept chooses (a craft asks for a second
## Confirm, since it cannot be undone); ui_cancel goes back a level and closes from HEROES.
## Mouse: hover to move, click to choose.

enum Level { HEROES, GEAR, PIECES, RECIPES }

const DATA_PATH := "res://game/data/ui/equip_menu.json"
const HELP_KEYS := {
	Level.HEROES: "EQUIP_MENU_HELP_HEROES",
	Level.GEAR: "EQUIP_MENU_HELP_GEAR",
	Level.PIECES: "EQUIP_MENU_HELP_PIECES",
	Level.RECIPES: "EQUIP_MENU_HELP_RECIPES",
}
const PREVIEW_COLS: Array[String] = ["name", "now", "arrow", "next", "delta"]

var sheet: PartySheet
var model: EquipMenuModel
var level := Level.HEROES
## The hero on show, the slot being changed (PIECES), and the piece and slot index being
## customized (RECIPES).
var hero: StringName = &""
var slot: StringName = &""
var piece_uid := EquipmentBag.NO_PIECE
var ability_index := -1
## Where RECIPES returns to: GEAR (a worn piece's empty slot) or PIECES (a spare's "· Customize").
var recipes_from := Level.GEAR

var _heroes: MenuPage
var _gear: MenuPage
var _choice: MenuPage
var _help: Label
var _desc: Label
var _status: Label
var _preview_title: Label
## One row of Labels per stat (PREVIEW_COLS order).
var _stat_cells: Array[Array] = []
var _changes: VBoxContainer
## A receipt or refusal that stays on the status line until the cursor moves.
var _notice: Dictionary = {}
## The ability a first Confirm asked about (RECIPES): a second Confirm on it crafts.
var _armed: StringName = &""
var _refused := false
var _built := false


static func create(with_sheet: PartySheet = null) -> EquipMenu:
	var menu := EquipMenu.new()
	menu.sheet = with_sheet
	return menu


## Opens the page on its own CanvasLayer under `host` (null sheet = the live party).
static func open_in(host: Node, with_sheet: PartySheet = null) -> EquipMenu:
	return FieldSubmenu.mount(create(with_sheet), host) as EquipMenu


func data_path() -> String:
	return DATA_PATH


func data_section() -> String:
	return "equip_menu"


func hero_page() -> MenuPage:
	return _heroes


func gear_page() -> MenuPage:
	return _gear


func choice_page() -> MenuPage:
	return _choice


func desc_text() -> String:
	return _desc.text


func status_text() -> String:
	return _status.text


## True when the status line is a refusal (drawn in the danger color).
func status_is_refusal() -> bool:
	return _refused and _status.text != ""


func help_text() -> String:
	return _help.text


func preview_title() -> String:
	return _preview_title.text


## The stat table as shown: [{name, now, arrow, next, delta}] (texts).
func preview_cells() -> Array[Dictionary]:
	var out: Array[Dictionary] = []
	for cells in _stat_cells:
		var row := {}
		for i in PREVIEW_COLS.size():
			row[PREVIEW_COLS[i]] = (cells[i] as Label).text
		out.append(row)
	return out


## The color a preview cell is drawn in (tests: gains and losses use the theme's roles).
func preview_cell_color(row: int, col: String) -> Color:
	return (_stat_cells[row][PREVIEW_COLS.find(col)] as Label).get_theme_color(&"font_color")


## The lines under the stat table (abilities gained and lost, or the recipe), as shown.
func changes_lines() -> Array[String]:
	var out: Array[String] = []
	for c in _changes.get_children():
		if not c.is_queued_for_deletion():
			out.append((c as Label).text)
	return out


func handle_input(event: InputEvent) -> bool:
	if not is_open():
		return false
	if event.is_action_pressed(&"ui_up", true):
		_move(-1)
	elif event.is_action_pressed(&"ui_down", true):
		_move(1)
	elif event.is_action_pressed(&"ui_left", true) or event.is_action_pressed(&"ui_page_up", true):
		change_hero(-1)
	elif event.is_action_pressed(&"ui_right", true) or event.is_action_pressed(&"ui_page_down", true):
		change_hero(1)
	elif event.is_action_pressed(&"ui_accept"):
		accept()
	elif event.is_action_pressed(&"ui_cancel"):
		back()
	else:
		return false
	return true


## Chooses the highlighted row.
func accept() -> void:
	match level:
		Level.HEROES:
			if _heroes.current_row().is_empty():
				return
			hero = StringName(str(_heroes.current_row()["id"]))
			level = Level.GEAR
			_gear.replace_rows(model.gear_rows(hero))
			_gear.set_cursor(0, false)
		Level.GEAR:
			_accept_gear(_gear.current_row())
		Level.PIECES:
			var row := _choice.current_row()
			if row.is_empty():
				return
			if StringName(str(row.get("kind", ""))) == EquipMenuModel.KIND_CUSTOMIZE:
				_open_recipes(int(row["uid"]), int(row["index"]), Level.PIECES)
				_render()
				return
			var result := model.choose_piece(hero, slot, row)
			_notice = result
			if bool(result.get("ok", false)):
				_back_to_gear(StringName("slot:%s" % slot))
				_notice = result
		Level.RECIPES:
			_accept_recipe(_choice.current_row())
	_render()


## Goes back one level; closes from HEROES.
func back() -> void:
	match level:
		Level.HEROES:
			close()
			return
		Level.GEAR:
			level = Level.HEROES
			_notice = {}
		Level.RECIPES when recipes_from == Level.PIECES:
			_back_to_pieces(piece_uid)
		_:
			_back_to_gear(_gear.current_row().get("id", &""))
	_render()


## Shows the previous or next hero's gear (GEAR only; wraps).
func change_hero(delta: int) -> void:
	if level != Level.GEAR or model.heroes().size() < 2:
		return
	var i := posmod(_heroes.cursor + delta, model.heroes().size())
	_heroes.set_cursor(i, false)
	hero = model.heroes()[i]
	var at := _gear.cursor
	_gear.replace_rows(model.gear_rows(hero))
	_gear.set_cursor(mini(at, _gear.row_count() - 1), false)
	_notice = {}
	_render()


func _accept_gear(row: Dictionary) -> void:
	if row.is_empty():
		return
	match StringName(str(row.get("kind", ""))):
		EquipMenuModel.KIND_SLOT:
			slot = StringName(str(row["slot"]))
			level = Level.PIECES
			_notice = {}
			_choice.set_header(model.pieces_title(hero, slot))
			_choice.replace_rows(model.piece_rows(hero, slot))
			var worn := model.worn(hero, slot)
			_choice.set_cursor(maxi(_index_of(_choice, StringName("piece:%d" % worn)), 0), false)
		EquipMenuModel.KIND_ABILITY:
			if StringName(str(row.get("ability", ""))) != &"":
				var uid := int(row["uid"])
				_notice = {"text": model.craft_refusal(Customize.ERR_SLOT_FILLED, uid, row["ability"]), "ok": false}
				return
			slot = StringName(str(row["slot"]))
			_open_recipes(int(row["uid"]), int(row["index"]), Level.GEAR)


## Customize: what can be crafted into slot `index` of piece `uid` (worn or spare).
func _open_recipes(uid: int, index: int, from: Level) -> void:
	piece_uid = uid
	ability_index = index
	recipes_from = from
	level = Level.RECIPES
	_notice = {}
	_armed = &""
	_choice.set_header(model.recipes_title(piece_uid))
	_choice.replace_rows(model.recipe_rows(piece_uid, ability_index))
	_choice.set_cursor(0, false)


func _accept_recipe(row: Dictionary) -> void:
	if row.is_empty():
		return
	var aid := StringName(str(row["ability"]))
	if _armed != aid:
		var line := model.recipe_line(piece_uid, ability_index, aid)
		if not bool(line["ok"]):
			_notice = line
			return
		_armed = aid
		_notice = {"text": model.craft_confirm_text(piece_uid, aid), "ok": true}
		return
	var result := model.craft(piece_uid, ability_index, aid)
	_armed = &""
	if not bool(result.get("ok", false)):
		_notice = result
		return
	if recipes_from == Level.PIECES:
		_back_to_pieces(piece_uid)
	else:
		_back_to_gear(StringName("ability:%s:%d" % [slot, ability_index]))
	_notice = result


## Back to the pieces for `slot`, the cursor on piece `uid`.
func _back_to_pieces(uid: int) -> void:
	level = Level.PIECES
	_armed = &""
	_notice = {}
	_choice.set_header(model.pieces_title(hero, slot))
	_choice.replace_rows(model.piece_rows(hero, slot))
	_choice.set_cursor(maxi(_index_of(_choice, StringName("piece:%d" % uid)), 0), false)


func _back_to_gear(row_id: Variant) -> void:
	level = Level.GEAR
	_armed = &""
	_notice = {}
	_gear.replace_rows(model.gear_rows(hero))
	var i := _index_of(_gear, StringName(str(row_id)))
	_gear.set_cursor(i if i >= 0 else 0, false)


func _move(delta: int) -> void:
	var page := _page_for(level)
	if page.move(delta):
		_notice = {}
		_armed = &""
		_render()


func _page_for(at: Level) -> MenuPage:
	match at:
		Level.HEROES:
			return _heroes
		Level.GEAR:
			return _gear
	return _choice


static func _index_of(page: MenuPage, id: StringName) -> int:
	for i in page.row_count():
		if StringName(str(page.rows[i].get("id", ""))) == id:
			return i
	return -1


# --- building ------------------------------------------------------------------------------------


func _build_page() -> void:
	if sheet == null:
		sheet = PartySheet.from_game()
	model = EquipMenuModel.new(sheet)
	_help = _framed_panel(_d.get("panel", {}), tr("FIELD_MENU_EQUIP"))
	var hm: Dictionary = _d.get("heroes", {})
	_heroes = _menu_page(hm, &"equip_heroes", tr("EQUIP_MENU_HEROES_TITLE"), int(HudLayout.num(hm, "max_rows")))
	_heroes.replace_rows(model.hero_rows())
	_heroes.size.y = MenuPage.height_for(hm, maxi(_heroes.row_count(), 1), true)
	_heroes.row_hovered.connect(_on_hovered.bind(Level.HEROES))
	_heroes.row_clicked.connect(_on_clicked.bind(Level.HEROES))
	var gm: Dictionary = _d.get("gear", {})
	_gear = _menu_page(gm, &"equip_gear", " ", int(HudLayout.num(gm, "max_rows")))
	_gear.row_hovered.connect(_on_hovered.bind(Level.GEAR))
	_gear.row_clicked.connect(_on_clicked.bind(Level.GEAR))
	var cm: Dictionary = _d.get("choice", {})
	_choice = _menu_page(cm, &"equip_choice", " ", int(HudLayout.num(cm, "max_rows")))
	_choice.row_hovered.connect(_on_hovered.bind(Level.PIECES))
	_choice.row_clicked.connect(_on_clicked.bind(Level.PIECES))
	for page in [_heroes, _gear, _choice]:
		_fit_in_rect(page.header_label())  # a long piece name stays in its own page (M2-MNU-05)
	_build_lines()
	_build_preview()
	if not model.heroes().is_empty():
		hero = model.heroes()[0]
		_gear.replace_rows(model.gear_rows(hero))
	_built = true
	_render()


func _build_lines() -> void:
	_desc = _label(&"BodyLabel", HudLayout.rect_of(_d.get("desc", {})))
	_desc.vertical_alignment = VERTICAL_ALIGNMENT_TOP
	_desc.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	var dr := HudLayout.rect_of(_d.get("desc", {}))
	var sh := HudLayout.num(_d.get("status", {}), "height")
	_status = _label(&"BodyLabel", Rect2(dr.position + Vector2(0.0, dr.size.y), Vector2(dr.size.x, sh)))
	_status.vertical_alignment = VERTICAL_ALIGNMENT_TOP
	_status.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART  # never cut: a refusal must be read whole


func _build_preview() -> void:
	var pm: Dictionary = _d.get("preview", {})
	var pr := HudLayout.rect_of(pm)
	var back := Panel.new()
	back.position = pr.position
	back.size = pr.size
	back.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(back)
	var cols: Dictionary = pm.get("cols", {})
	var name_col: Array = cols.get("name", [0, 0])
	var header_h := HudLayout.num(pm, "header_height")
	var title_r := Rect2(
		pr.position + Vector2(float(name_col[0]), 0.0), Vector2(pr.size.x - float(name_col[0]) * 2.0, header_h)
	)
	_preview_title = _label(&"HeaderLabel", title_r)
	_preview_title.vertical_alignment = VERTICAL_ALIGNMENT_BOTTOM
	_preview_title.text_overrun_behavior = TextServer.OVERRUN_TRIM_ELLIPSIS
	_title_rule(title_r)
	var pitch := HudLayout.num(pm, "stat_pitch")
	var top := pr.position.y + HudLayout.num(pm, "stat_top")
	for i in EquipMenuModel.STAT_KEYS.size():
		var cells: Array = []
		for col in PREVIEW_COLS:
			var c: Array = cols.get(col, [0, 0])
			var r := Rect2(pr.position.x + float(c[0]), top + i * pitch, float(c[1]), pitch)
			var l := _label(&"BodyLabel" if col == "name" else &"HudNumber", r)
			l.horizontal_alignment = HORIZONTAL_ALIGNMENT_LEFT if col == "name" else HORIZONTAL_ALIGNMENT_RIGHT
			if col == "arrow":
				l.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
			if col == "name":
				_fit_in_rect(l)  # at a large text size the name ellipsizes; the numbers keep their columns
			cells.append(l)
		_stat_cells.append(cells)
	_changes = VBoxContainer.new()
	_changes.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_changes.position.x = pr.position.x + float(name_col[0])
	_changes.size.x = pr.size.x - float(name_col[0]) * 2.0
	_changes.clip_contents = true  # never past the panel's frame, whatever the text size
	add_child(_changes)
	_layout_preview()


## The stat rows' pitch: the data pitch, or the font's line height when the text size needs more
## (UiSettings text scale), so rows never overlap. The changes sit under the last row.
func _layout_preview() -> void:
	var pm: Dictionary = _d.get("preview", {})
	var pitch := preview_pitch()
	var top := HudLayout.rect_of(pm).position.y + HudLayout.num(pm, "stat_top")
	for i in _stat_cells.size():
		for l: Label in _stat_cells[i]:
			l.position.y = top + i * pitch
			l.size.y = pitch
	_changes.position.y = top + _stat_cells.size() * pitch + HudLayout.num(pm, "changes_gap")
	_changes.size.y = maxf(HudLayout.rect_of(pm).end.y - HudLayout.num(pm, "changes_pad") - _changes.position.y, 0.0)


## The row pitch the stat table uses now (reference pixels).
func preview_pitch() -> float:
	var pitch := HudLayout.num(_d.get("preview", {}), "stat_pitch")
	if _stat_cells.is_empty():
		return pitch
	for l: Label in _stat_cells[0]:
		pitch = maxf(pitch, ceilf(l.get_line_height()))
	return pitch


static func _fit_in_rect(l: Label) -> void:
	l.clip_text = true
	l.text_overrun_behavior = TextServer.OVERRUN_TRIM_ELLIPSIS


# --- rendering -----------------------------------------------------------------------------------


func _notification(what: int) -> void:
	if what == NOTIFICATION_THEME_CHANGED and _built:
		_render()  # palette swaps (UiSettings) recolor the deltas


func _render() -> void:
	_help.text = tr(HELP_KEYS[level])
	var choosing := level == Level.PIECES or level == Level.RECIPES
	_heroes.set_dimmed(level != Level.HEROES)
	_gear.visible = not choosing
	_gear.set_dimmed(level != Level.GEAR)
	_gear.set_header(model.gear_title(_shown_hero()) if _shown_hero() != &"" else "")
	_gear.size.y = MenuPage.height_for(_d.get("gear", {}), maxi(_gear.row_count(), 1), true)
	_choice.visible = choosing
	if choosing:
		_choice.size.y = MenuPage.height_for(_d.get("choice", {}), maxi(_choice.row_count(), 1), true)
	match level:
		Level.HEROES:
			_render_heroes()
		Level.GEAR:
			_render_gear()
		Level.PIECES:
			_render_pieces()
		Level.RECIPES:
			_render_recipes()


## The hero whose gear is on show: the highlighted one on HEROES, else the chosen one.
func _shown_hero() -> StringName:
	if level == Level.HEROES:
		return StringName(str(_heroes.current_row().get("id", "")))
	return hero


func _render_heroes() -> void:
	var cid := _shown_hero()
	if cid != hero and cid != &"":
		hero = cid
		_gear.replace_rows(model.gear_rows(hero))
		_gear.size.y = MenuPage.height_for(_d.get("gear", {}), maxi(_gear.row_count(), 1), true)
		_gear.set_header(model.gear_title(hero))
	_set_lines(tr("FIELD_MENU_EQUIP_DESC"), {})
	_show_preview(model.hero_name(cid) if cid != &"" else "", model.preview_none(cid) if cid != &"" else {}, false)
	_set_changes([])


func _render_gear() -> void:
	var row := _gear.current_row()
	_set_lines(model.gear_desc(row), _notice if not _notice.is_empty() else model.gear_line(row))
	_show_preview(model.hero_name(hero), model.preview_none(hero), false)
	_set_changes([])


func _render_pieces() -> void:
	var row := _choice.current_row()
	if row.is_empty():
		_set_lines("", _notice)
		_show_preview("", {}, false)
		_set_changes([])
		return
	var uid := int(row.get("uid", EquipMenuModel.NO_PIECE))
	if StringName(str(row.get("kind", ""))) == EquipMenuModel.KIND_CUSTOMIZE:
		_set_lines(model.customize_desc(uid), _notice)
		_show_preview(model.piece_name(uid), model.preview_none(hero), false)
		_set_changes([])
		return
	var removing := StringName(str(row.get("kind", ""))) == EquipMenuModel.KIND_REMOVE
	var desc := model.piece_desc(uid) if not removing else ""
	_set_lines(desc, _notice if not _notice.is_empty() else model.piece_line(hero, slot, row))
	var preview := model.preview_piece(hero, slot, uid)
	_show_preview(str(row.get("label", "")), preview, true)
	_set_changes(_ability_lines(preview))


func _render_recipes() -> void:
	var row := _choice.current_row()
	if row.is_empty():
		_set_lines(tr("EQUIP_MENU_NO_RECIPES"), _notice)
		_show_preview(model.piece_name(piece_uid), model.preview_none(hero), false)
		_set_changes([])
		return
	var aid := StringName(str(row["ability"]))
	_set_lines(
		model.ability_desc(aid), _notice if not _notice.is_empty() else model.recipe_line(piece_uid, ability_index, aid)
	)
	_show_preview(model.ability_name(aid), model.preview_craft(hero, piece_uid, ability_index, aid), true)
	var lines: Array[Dictionary] = []
	for part in model.recipe_parts(aid):
		lines.append({"text": part["text"], "role": &"text" if int(part["short"]) == 0 else &"danger"})
	_set_changes(lines)


func _ability_lines(preview: Dictionary) -> Array[Dictionary]:
	var lines: Array[Dictionary] = []
	var gained: Array = preview.get("gained", [])
	var lost: Array = preview.get("lost", [])
	if not gained.is_empty():
		lines.append({"text": model.ability_change_text({"gained": gained}), "role": &"heal"})
	if not lost.is_empty():
		lines.append({"text": model.ability_change_text({"lost": lost}), "role": &"danger"})
	return lines


## The line about the row and, under it, the status (a refusal in the danger color).
func _set_lines(desc: String, line: Dictionary) -> void:
	_desc.text = desc
	_status.text = str(line.get("text", ""))
	_refused = not bool(line.get("ok", true))
	_status.add_theme_color_override(&"font_color", _c(&"danger" if _refused else &"text_dim"))
	# Both wrap whole, as tall as their text (no cap, no ellipsis: M2-MNU-05 at 130% text).
	_desc.size.y = _text_height(_desc) if desc != "" else 0.0
	var gap := HudLayout.num(_d.get("status", {}), "gap") if desc != "" else 0.0
	_status.position.y = _desc.position.y + _desc.size.y + gap
	_status.size.y = maxf(_text_height(_status), HudLayout.num(_d.get("status", {}), "height"))


static func _text_height(l: Label) -> float:
	var lines := l.get_line_count()
	var spacing := float(l.get_theme_constant(&"line_spacing"))
	return ceilf(lines * l.get_line_height() + maxi(lines - 1, 0) * spacing)


## Fills the stat table: now only (compare false), or now -> next with the signed delta.
func _show_preview(title: String, preview: Dictionary, compare: bool) -> void:
	_layout_preview()
	_preview_title.text = title
	var stats: Array = preview.get("stats", [])
	for i in _stat_cells.size():
		var cells: Array = _stat_cells[i]
		var has := i < stats.size()
		var s: Dictionary = stats[i] if has else {}
		var delta := int(s.get("delta", 0))
		(cells[0] as Label).text = str(s.get("label", ""))
		(cells[1] as Label).text = str(s.get("now", "")) if has else ""
		(cells[2] as Label).text = tr("EQUIP_MENU_ARROW") if has and compare else ""
		(cells[3] as Label).text = str(s.get("next", "")) if has and compare else ""
		(cells[4] as Label).text = model.delta_text(delta) if has and compare else ""
		var role := &"text_dim"  # unchanged: quiet, so the eye goes to what moves
		if delta > 0:
			role = &"heal"
		elif delta < 0:
			role = &"danger"
		(cells[0] as Label).add_theme_color_override(&"font_color", _c(&"text_dim"))
		(cells[1] as Label).add_theme_color_override(&"font_color", _c(&"text" if not compare else &"text_dim"))
		(cells[2] as Label).add_theme_color_override(&"font_color", _c(&"text_dim"))
		(cells[3] as Label).add_theme_color_override(&"font_color", _c(role))
		(cells[4] as Label).add_theme_color_override(&"font_color", _c(role))


func _set_changes(lines: Array[Dictionary]) -> void:
	for c in _changes.get_children():
		_changes.remove_child(c)
		c.queue_free()
	for line in lines:
		var l := Label.new()
		l.theme_type_variation = &"BodyLabel"
		l.text = str(line.get("text", ""))
		l.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		l.custom_minimum_size.x = _changes.size.x
		l.mouse_filter = Control.MOUSE_FILTER_IGNORE
		l.add_theme_color_override(&"font_color", _c(line.get("role", &"text")))
		_changes.add_child(l)


# --- mouse ---------------------------------------------------------------------------------------


func _on_hovered(_index: int, page_level: Level) -> void:
	if _page_for(page_level) != _page_for(level):
		return
	_notice = {}
	_armed = &""
	_render()


func _on_clicked(index: int, page_level: Level) -> void:
	if not is_open():
		return
	match page_level:
		Level.HEROES:
			level = Level.HEROES
			_heroes.set_cursor(index, false)
			_notice = {}
		Level.GEAR:
			if level != Level.HEROES and level != Level.GEAR:
				return
			if level == Level.HEROES:
				accept()  # into the highlighted hero's gear first
			_gear.set_cursor(index, false)
		_:
			if level != Level.PIECES and level != Level.RECIPES:
				return
			if _choice.cursor != index:
				_armed = &""
			_choice.set_cursor(index, false)
	accept()
