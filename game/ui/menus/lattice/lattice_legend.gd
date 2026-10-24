class_name LatticeLegend
extends LatticeBoardView
## The Lattice page's key (M2-MNU-01, pillar 4): one row per look a node can have, its sample drawn
## exactly as the board draws it (LatticeBoardView._draw_shape) and the meaning in words beside it.
## Rows: {kind (LatticeNode.KIND_*), state (LatticeMenuModel.STATE_*), text}. Metrics: the board's,
## plus lattice_menu.json "legend" (row_pitch, sample_x, sample_scale, text_x).
## M2-MNU-05: a row's words wrap to the width and the row grows to hold them (at least row_pitch),
## so a larger text size never runs a row into the next; content_height() says how tall it all is.

var rows: Array[Dictionary] = []
## How many rows are drawn (the first ones; fit() sets it to what the room holds). -1: all.
var shown_rows := -1
var _lm: Dictionary = {}


func setup_legend(board_metrics: Dictionary, legend_metrics: Dictionary, legend_rows: Array[Dictionary]) -> void:
	_m = board_metrics
	_lm = legend_metrics
	rows = legend_rows
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	queue_redraw()


## Each shown row's height at the current width and text size.
func row_heights() -> Array[float]:
	var out: Array[float] = []
	var pitch := HudLayout.num(_lm, "row_pitch")
	var count := rows.size() if shown_rows < 0 else mini(shown_rows, rows.size())
	for i in count:
		out.append(maxf(pitch, _paragraph(str(rows[i].get("text", ""))).get_size().y))
	return out


## Shows as many of the first rows as fit in `room` px; returns how many.
func fit(room: float) -> int:
	shown_rows = -1
	var used := 0.0
	var count := 0
	for h in row_heights():
		if used + h > room:
			break
		used += h
		count += 1
	shown_rows = count
	queue_redraw()
	return count


func content_height() -> float:
	var total := 0.0
	for h in row_heights():
		total += h
	return total


func _draw() -> void:
	var region := _region_color(LatticeNode.new())
	var heights := row_heights()
	var k := HudLayout.num(_lm, "sample_scale")
	var top := 0.0
	for i in heights.size():
		var row := rows[i]
		var n := LatticeNode.new()
		n.kind = StringName(str(row.get("kind", LatticeNode.KIND_STAT)))
		n.gate_level = 1
		var y := top + heights[i] * 0.5
		draw_set_transform(Vector2(HudLayout.num(_lm, "sample_x"), y), 0.0, Vector2(k, k))
		_draw_shape(n, Vector2.ZERO, StringName(str(row.get("state", ""))), region)
		if bool(row.get("marker", false)):
			_hero_ring(
				Vector2.ZERO, _half_size(n), _num("marker_gap_px"), _role(&"focus_gold"), _role(&"lamp_node_glow")
			)
		draw_set_transform(Vector2.ZERO)
		var para := _paragraph(str(row.get("text", "")))
		var at := Vector2(HudLayout.num(_lm, "text_x"), y - para.get_size().y * 0.5)
		para.draw(get_canvas_item(), at, _role(&"text_dim"))
		top += heights[i]


func _paragraph(text: String) -> TextParagraph:
	var para := TextParagraph.new()
	para.break_flags = TextServer.BREAK_MANDATORY | TextServer.BREAK_WORD_BOUND | TextServer.BREAK_ADAPTIVE
	para.width = size.x - HudLayout.num(_lm, "text_x")
	para.add_string(text, get_theme_font(&"font", &"DimLabel"), get_theme_font_size(&"font_size", &"DimLabel"))
	return para
