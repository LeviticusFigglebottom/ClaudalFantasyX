class_name KiteChart
extends Control
## The Kite's chart (KiteMapMenu): Maresh's sea in its grid (column letters along the top, row
## numbers down the side, faint cell lines), each region's name where its people live, a gem for each
## place the Kite can land, a ring on the one under the cursor, and while searching, the cell being
## searched outlined. Every position is a kite.json "at" (fractions of the chart). Draw metrics:
## kite_map.json "chart". The pointer over it names the square under it (cell_pointed).

## The pointer is over chart square `square` ([column, row]); `clicked` when the left button went down there.
signal cell_pointed(square: Vector2i, clicked: bool)

var model: KiteMapModel
## The destination under the cursor (&"" for none) and the searched cell ([column, row], or [-1, -1]).
var cursor: StringName = &""
var search_cell := Vector2i(-1, -1)

var _m: Dictionary = {}


func setup(metrics: Dictionary, with_model: KiteMapModel) -> void:
	_m = metrics
	model = with_model
	mouse_filter = Control.MOUSE_FILTER_PASS
	HudLayout.place(self, metrics)


func point(at: Array) -> Vector2:
	return Vector2(float(at[0]) * size.x, float(at[1]) * size.y)


## The chart square ([column, row]) under local point `at`.
func cell_under(at: Vector2) -> Vector2i:
	var cols := maxi(model.columns().size(), 1)
	var rows := maxi(model.row_count(), 1)
	return Vector2i(
		clampi(int(at.x / maxf(size.x, 1.0) * cols), 0, cols - 1),
		clampi(int(at.y / maxf(size.y, 1.0) * rows), 0, rows - 1)
	)


func _gui_input(event: InputEvent) -> void:
	if event is InputEventMouseMotion:
		cell_pointed.emit(cell_under((event as InputEventMouseMotion).position), false)
	elif event is InputEventMouseButton:
		var mb := event as InputEventMouseButton
		if mb.pressed and mb.button_index == MOUSE_BUTTON_LEFT:
			cell_pointed.emit(cell_under(mb.position), true)
			accept_event()


func _draw() -> void:
	draw_rect(Rect2(Vector2.ZERO, size), _role(&"panel_deep"))
	var cols := model.columns()
	var rows := model.row_count()
	var line := _role(&"line_gold", HudLayout.num(_m, "grid_alpha"))
	var font := get_theme_font(&"font", &"SmallLabel")
	var fs := get_theme_font_size(&"font_size", &"SmallLabel")
	for c in cols.size():
		var x := size.x * c / maxf(cols.size(), 1.0)
		draw_line(Vector2(x, 0.0), Vector2(x, size.y), line, 1.0)
		draw_string(
			font,
			Vector2(x + HudLayout.num(_m, "label_pad"), -HudLayout.num(_m, "label_pad")),
			str(cols[c]),
			0,
			-1,
			fs,
			_role(&"text_dim")
		)
	for r in rows:
		var y := size.y * r / maxf(rows, 1.0)
		draw_line(Vector2(0.0, y), Vector2(size.x, y), line, 1.0)
		draw_string(
			font,
			Vector2(-HudLayout.num(_m, "row_label_px"), y + font.get_ascent(fs)),
			str(r + 1),
			0,
			-1,
			fs,
			_role(&"text_dim")
		)
	if search_cell.x >= 0:
		var cw := size.x / maxf(cols.size(), 1.0)
		var ch := size.y / maxf(rows, 1.0)
		draw_rect(
			Rect2(Vector2(cw * search_cell.x, ch * search_cell.y), Vector2(cw, ch)),
			_role(&"focus_gold"),
			false,
			HudLayout.num(_m, "cursor_px")
		)
	for r: Variant in model.data.get("regions", []):
		var reg := r as Dictionary
		var text := tr(str(reg.get("name_key", "")))
		var w := font.get_string_size(text, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x
		draw_string(font, point(reg["at"]) - Vector2(w * 0.5, 0.0), text, 0, -1, fs, _role(&"text_dim"))
	var gem := HudLayout.num(_m, "gem_px")
	for d in model.destinations():
		var at := point(d["at"]) + Vector2(0.0, HudLayout.num(_m, "gem_offset_px"))
		var here := model.is_here(StringName(str(d["id"])))
		draw_circle(at, gem, _role(&"text_dim") if here else _role(&"focus"))
		if StringName(str(d["id"])) == cursor:
			draw_arc(
				at,
				gem + HudLayout.num(_m, "ring_gap_px"),
				0.0,
				TAU,
				24,
				_role(&"focus_gold"),
				HudLayout.num(_m, "cursor_px"),
				true
			)


func _role(role: StringName, alpha_scale: float = 1.0) -> Color:
	var c := get_theme_color(role, HymnThemeBuilder.PALETTE_TYPE)
	return Color(c, c.a * alpha_scale)
