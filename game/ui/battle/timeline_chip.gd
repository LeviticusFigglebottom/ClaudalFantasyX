class_name TimelineChip
extends Control
## One turn in the TurnTimeline (docs/kb/art/ui.md §6.1). Ally and enemy differ by SHAPE as well
## as fill: allies have a square left edge, enemies a chevron cut pointing left. A ghost is the
## acting fighter's predicted next turn (dashed gold frame, half alpha); a skipped turn
## (Stop/Sleep) is hatched and dimmed; `moved` draws a ▲/▼ for chips the preview shifts.
## A Doomed turn carries an hourglass and its count (TurnEntry.doom). The chip acting now has a
## heavier focus frame with an outer glow and a caption ("Acting now", or why it acts alone).
## The portrait shows the fighter's face or bestiary picture (BattlePortraits) inside its shape (an ally's square,
## a foe's diamond); the initial stands in only where none is baked yet.
## A scripted entry (a set piece's Climb or Surge, M3-UI-100) is neither ally nor foe to the eye: a raised fill,
## a dashed frame and a round portrait (battle_hud.json timeline entry_fill_role / entry_frame_role).

const TEAM_ENEMY := &"enemy"

var combatant_id: StringName = &""
var team: StringName = &"party"
var label_text := ""
var tint := Color.WHITE
var is_current := false
var ghost := false
var skipped := false
## -1 = moves earlier (▲), +1 = later (▼), 0 = unchanged.
var moved := 0
var targeted := false
var target_color := Color.WHITE
## Doom count shown on this turn (0 = none).
var doom := 0
## Slot 0 caption under the name ("" hides it).
var caption := ""
## The telegraphed skill this turn is committed to ("" = none), shown after the name (M2-FP-06).
var intent_label := ""
## A scripted timeline entry, not a fighter (the identity's "entry"; M3-UI-100).
var entry := false
## The running slide/fade, killed when a newer layout arrives (TurnTimeline._move).
var move_tween: Tween

var _metrics: Dictionary = {}
var _name: Label
var _initial: Label
var _face: Texture2D
var _caption: Label
var _doom_glyph: StatusGlyph
var _doom_label: Label


func _init() -> void:
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	_initial = Label.new()
	_initial.theme_type_variation = &"HudNumber"
	_initial.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_initial.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	add_child(_initial)
	_name = Label.new()
	_name.theme_type_variation = &"SmallLabel"
	_name.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	_name.text_overrun_behavior = TextServer.OVERRUN_TRIM_ELLIPSIS
	_name.clip_text = true
	add_child(_name)
	_caption = Label.new()
	_caption.theme_type_variation = &"DimLabel"
	_caption.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	_caption.text_overrun_behavior = TextServer.OVERRUN_TRIM_ELLIPSIS
	_caption.clip_text = true
	_caption.visible = false
	add_child(_caption)
	_doom_glyph = StatusGlyph.new(&"doom")
	_doom_glyph.visible = false
	add_child(_doom_glyph)
	_doom_label = Label.new()
	_doom_label.theme_type_variation = &"BadgeNumber"
	_doom_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_doom_label.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	_doom_label.visible = false
	add_child(_doom_label)


func setup(metrics: Dictionary) -> void:
	_metrics = metrics


## Applies a slot from TurnTimeline.build_slots plus the combatant's identity.
func apply(slot: Dictionary, identity: Dictionary, current: bool) -> void:
	combatant_id = slot["id"]
	team = slot["team"]
	ghost = bool(slot["ghost"])
	skipped = bool(slot["skipped"])
	moved = int(slot["moved"])
	targeted = bool(slot.get("targeted", false))
	doom = int(slot.get("doom", 0))
	caption = str(slot.get("caption", "")) if current else ""
	is_current = current
	label_text = str(identity.get("label", String(combatant_id)))
	tint = identity.get("tint", Color.WHITE)
	entry = bool(identity.get("entry", false))
	intent_label = str(slot.get("intent_label", ""))
	# A committed turn names its skill alone ("The Toll"): the glyph and the side colour already say
	# whose turn it is, and "<name> · <skill>" ran past the chip's width (M2-FP-12).
	_name.text = label_text if intent_label == "" else intent_label
	_initial.text = label_text.left(1)
	_face = null if entry else BattlePortraits.texture(combatant_id)
	_initial.visible = _face == null
	_caption.text = caption
	_doom_label.text = str(doom) if doom > 0 else ""
	_layout_children()
	queue_redraw()


func _notification(what: int) -> void:
	if what == NOTIFICATION_RESIZED:
		_layout_children()


func _layout_children() -> void:
	if _metrics.is_empty():
		return
	var pad := HudLayout.num(_metrics, "pad")
	var left := _left_edge()
	var side := size.y - pad * 2.0
	_initial.position = Vector2(left + pad, pad)
	_initial.size = Vector2(side, side)
	var right := _marks_width()
	var name_x := left + pad * 2.0 + side
	var name_w := maxf(size.x - name_x - right, 0.0)
	var show_caption := caption != "" and size.y > HudLayout.num(_metrics, "chip_height")
	var cap_h := HudLayout.num(_metrics, "caption_height") if show_caption else 0.0
	if show_caption:  # the readability pass (10-30): at 130 % text the caption grew past the chip's bottom border
		cap_h = maxf(cap_h, _caption.get_combined_minimum_size().y)
	_name.position = Vector2(name_x, 0.0)
	_name.size = Vector2(name_w, size.y - cap_h)
	_caption.visible = show_caption
	_caption.position = Vector2(name_x, size.y - cap_h - pad)
	_caption.size = Vector2(name_w, cap_h)
	# The Act I UI pass (2026-10-30): at 130 % text "Acting now" read "Acting ..." and long names lost their ends;
	# both shrink a little (to 80 % at most) before an ellipsis cuts them. Who acts next stays readable (pillar 4).
	HudLayout.fit_label(_name, name_w)
	HudLayout.fit_label(_caption, name_w)
	_layout_doom(right)
	var dim := skipped or ghost
	_name.modulate = Color(1, 1, 1, HudLayout.num(_metrics, "skipped_alpha")) if skipped else Color.WHITE
	_name.add_theme_color_override(&"font_color", _name_color() if not dim else _theme(&"text_dim"))


## Width reserved at the right edge for the arrow, the target mark and the Doom badge.
func _marks_width() -> float:
	var pad := HudLayout.num(_metrics, "pad")
	var w := HudLayout.num(_metrics, "arrow_px") + pad * 2.0
	if targeted:
		w += HudLayout.num(_metrics, "target_mark_px") * 2.0 + pad
	if doom > 0:
		w += HudLayout.num(_metrics, "doom_glyph_px") + HudLayout.num(_metrics, "doom_label_width") + pad
	return w


func _layout_doom(right: float) -> void:
	var on := doom > 0
	_doom_glyph.visible = on
	_doom_label.visible = on
	if not on:
		return
	var pad := HudLayout.num(_metrics, "pad")
	var g := HudLayout.num(_metrics, "doom_glyph_px")
	var lw := HudLayout.num(_metrics, "doom_label_width")
	var x := size.x - right + pad
	var y := (minf(size.y, HudLayout.num(_metrics, "chip_height")) - g) * 0.5
	_doom_glyph.position = Vector2(x, y)
	_doom_glyph.size = Vector2(g, g)
	_doom_label.position = Vector2(x + g, 0.0)
	_doom_label.size = Vector2(lw, minf(size.y, HudLayout.num(_metrics, "chip_height")))


func _draw() -> void:
	if _metrics.is_empty():
		return
	var shape := _shape()
	var fill := _theme(&"enemy_chip") if team == TEAM_ENEMY else _theme(&"ally_chip")
	if entry:
		fill = _theme(StringName(str(_metrics.get("entry_fill_role", ""))))
	if ghost:
		fill.a *= HudLayout.num(_metrics, "ghost_alpha")
	draw_colored_polygon(shape, fill)
	_draw_portrait()
	if skipped:
		_draw_hatch()
	if ghost:
		_draw_dashed(shape, _theme(&"focus_gold"))
	elif entry and not is_current:
		_draw_dashed(shape, _theme(StringName(str(_metrics.get("entry_frame_role", "")))))
	elif is_current:
		# The fighter acting now: an outer glow, a heavier frame, and a solid lamp bar on the edge.
		var glow := HudLayout.num(_metrics, "current_glow_px")
		_draw_loop(_inset(shape, -glow), _theme(&"focus_glow"), glow)
		_draw_loop(shape, _theme(&"focus"), HudLayout.num(_metrics, "current_frame_px"))
	if moved != 0:
		_draw_arrow()
	if targeted:
		var r := HudLayout.num(_metrics, "target_mark_px")
		var c := Vector2(size.x - r - HudLayout.num(_metrics, "pad"), size.y * 0.5)
		if moved != 0:
			c.x -= HudLayout.num(_metrics, "arrow_px") + r
		draw_arc(c, r, 0.0, TAU, 16, target_color, float(_theme_k(&"focus_px")))
		draw_circle(c, r * 0.35, target_color)


func _shape() -> PackedVector2Array:
	var w := size.x
	var h := size.y
	if team == TEAM_ENEMY:
		var cut := HudLayout.num(_metrics, "chevron_px")
		return PackedVector2Array([Vector2(0, h * 0.5), Vector2(cut, 0), Vector2(w, 0), Vector2(w, h), Vector2(cut, h)])
	return PackedVector2Array([Vector2(0, 0), Vector2(w, 0), Vector2(w, h), Vector2(0, h)])


func _left_edge() -> float:
	return HudLayout.num(_metrics, "chevron_px") if team == TEAM_ENEMY else 0.0


func _draw_portrait() -> void:
	var pad := HudLayout.num(_metrics, "pad")
	var side := size.y - pad * 2.0
	var r := Rect2(Vector2(_left_edge() + pad, pad), Vector2(side, side))
	var col := tint
	if ghost:
		col.a *= HudLayout.num(_metrics, "ghost_alpha")
	if entry:
		draw_circle(r.get_center(), side * 0.5, col)  # an entry's portrait is round: a third shape cue
		return
	var pic := r.grow(-HudLayout.num(_metrics, "portrait_inset"))
	if team == TEAM_ENEMY:
		# Enemy portrait is a diamond, ally a square: a second shape cue. The foe's picture fills the diamond.
		var c := r.get_center()
		var hs := side * 0.5
		var diamond := PackedVector2Array(
			[c + Vector2(0, -hs), c + Vector2(hs, 0), c + Vector2(0, hs), c + Vector2(-hs, 0)]
		)
		draw_colored_polygon(diamond, col)
		if _face != null:
			var inner := diamond.duplicate()
			var uvs := PackedVector2Array()
			var k := 1.0 - HudLayout.num(_metrics, "portrait_inset") * 2.0 / side
			for i in inner.size():
				inner[i] = c + (inner[i] - c) * k
				uvs.append((inner[i] - (c - Vector2.ONE * hs * k)) / (side * k))
			draw_colored_polygon(inner, Color(1.0, 1.0, 1.0, col.a), uvs, _face)
		return
	draw_rect(r, col)
	if _face != null:
		draw_texture_rect(_face, pic, false, Color(1.0, 1.0, 1.0, col.a))


func _draw_hatch() -> void:
	var step := HudLayout.num(_metrics, "hatch_px")
	var col := _theme(&"text_dim")
	col.a *= HudLayout.num(_metrics, "skipped_alpha")
	var x := -size.y
	while x < size.x:
		draw_line(Vector2(x, size.y), Vector2(x + size.y, 0), col, 1.0)
		x += step


func _draw_dashed(shape: PackedVector2Array, col: Color) -> void:
	var dash := HudLayout.num(_metrics, "dash_px")
	var inset := _inset(shape, 0.5)
	for i in inset.size():
		var a := inset[i]
		var b := inset[(i + 1) % inset.size()]
		var length := a.distance_to(b)
		var t := 0.0
		while t < length:
			var e := minf(t + dash, length)
			draw_line(a.lerp(b, t / length), a.lerp(b, e / length), col, 1.0)
			t += dash * 2.0


func _draw_loop(shape: PackedVector2Array, col: Color, width: float) -> void:
	var loop := _inset(shape, width * 0.5)
	loop.append(loop[0])
	draw_polyline(loop, col, width)


func _draw_arrow() -> void:
	var a := HudLayout.num(_metrics, "arrow_px")
	var pad := HudLayout.num(_metrics, "pad")
	var c := Vector2(size.x - pad - a * 0.5, size.y * 0.5)
	var hh := a * 0.5
	var pts: PackedVector2Array
	if moved < 0:
		pts = PackedVector2Array([c + Vector2(-hh, hh * 0.8), c + Vector2(hh, hh * 0.8), c + Vector2(0, -hh * 0.8)])
	else:
		pts = PackedVector2Array([c + Vector2(-hh, -hh * 0.8), c + Vector2(hh, -hh * 0.8), c + Vector2(0, hh * 0.8)])
	draw_colored_polygon(pts, _theme(&"text_dim"))


## Pulls every vertex toward the centroid's side by `d` px on each axis (good enough for
## these convex chips: keeps 1 px lines inside the shape).
func _inset(shape: PackedVector2Array, d: float) -> PackedVector2Array:
	var out := PackedVector2Array()
	var center := Vector2(size.x * 0.5, size.y * 0.5)
	for p in shape:
		out.append(p + Vector2(signf(center.x - p.x) * d, signf(center.y - p.y) * d))
	return out


func _name_color() -> Color:
	return _theme(&"danger") if team == TEAM_ENEMY else _theme(&"text")


func _theme(role: StringName) -> Color:
	return get_theme_color(role, HymnThemeBuilder.PALETTE_TYPE)


func _theme_k(cname: StringName) -> int:
	return get_theme_constant(cname, HymnThemeBuilder.PALETTE_TYPE)
