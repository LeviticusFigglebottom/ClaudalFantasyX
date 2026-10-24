class_name LatticeLegend
extends LatticeBoardView
## The Lattice page's key (M2-MNU-01, pillar 4): one row per look a node can have, its sample drawn
## exactly as the board draws it (LatticeBoardView._draw_shape) and the meaning in words beside it.
## Rows: {kind (LatticeNode.KIND_*), state (LatticeMenuModel.STATE_*), text}. Metrics: the board's,
## plus lattice_menu.json "legend" (row_pitch, sample_x, text_x).

var rows: Array[Dictionary] = []
var _lm: Dictionary = {}


func setup_legend(board_metrics: Dictionary, legend_metrics: Dictionary, legend_rows: Array[Dictionary]) -> void:
	_m = board_metrics
	_lm = legend_metrics
	rows = legend_rows
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	queue_redraw()


func _draw() -> void:
	var pitch := HudLayout.num(_lm, "row_pitch")
	var font := get_theme_font(&"font", &"DimLabel")
	var fs := get_theme_font_size(&"font_size", &"DimLabel")
	var region := _region_color(LatticeNode.new())
	for i in rows.size():
		var row := rows[i]
		var n := LatticeNode.new()
		n.kind = StringName(str(row.get("kind", LatticeNode.KIND_STAT)))
		n.gate_level = 1
		var y := pitch * (i + 0.5)
		var k := HudLayout.num(_lm, "sample_scale")
		draw_set_transform(Vector2(HudLayout.num(_lm, "sample_x"), y), 0.0, Vector2(k, k))
		_draw_shape(n, Vector2.ZERO, StringName(str(row.get("state", ""))), region)
		if bool(row.get("marker", false)):
			_hero_ring(
				Vector2.ZERO, _half_size(n), _num("marker_gap_px"), _role(&"focus_gold"), _role(&"lamp_node_glow")
			)
		draw_set_transform(Vector2.ZERO)
		var base := y + (font.get_ascent(fs) - font.get_descent(fs)) * 0.5
		var x := HudLayout.num(_lm, "text_x")
		draw_string(font, Vector2(x, base), str(row.get("text", "")), 0, size.x - x, fs, _role(&"text_dim"))
