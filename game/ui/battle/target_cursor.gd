class_name TargetCursor
extends Control
## Target feedback in screen space (docs/kb/art/ui.md §6.4): a chevron above each chosen
## target (ui_danger for foes, ui_focus for allies: the shape is shared, the color and the
## target info panel say which side), the target info panel at the top left, and the marker over
## the fighter whose turn it is. The 3D ground ring is drawn by the battle scene.
## - Provoke: a fish-hook glyph hangs over the provoker while the actor is Provoked, and a locked
##   target's chevron gets a solid bar under it (the cursor cannot leave it).
## - Reflect: when the chosen target would bounce a spell, a dashed arc with an arrowhead and the
##   Reflect glyph runs from it to where the spell will really land.

## Target entries: {id, label, screen_pos: Vector2, hostile: bool, combatant: BattleCombatant,
## revealed: bool, forced: bool, bounce_pos: Vector2 (optional), bounce_id: StringName}. HP is
## shown for allies and for foes that have been Read (M1-CMB-03).
var targets: Array[Dictionary] = []
## Reduced motion (UiSettings): no bob and no breathing.
var reduced_motion := false
## Why the acting fighter's turn plays itself (&"berserk"/&"confuse"); hollow marker when set.
var actor_auto: StringName = &""

var _m: Dictionary = {}
var _marker_m: Dictionary = {}
var _marks_m: Dictionary = {}
var _info: PanelContainer
var _info_name: Label
var _info_hp: Label
var _info_gauge: HudGauge
var _info_status: HBoxContainer
var _info_note: Label
var _actor_pos := Vector2.ZERO
var _actor_shown := false
var _actor_mote: LampMote
var _provoke_glyph: StatusGlyph
var _bounce_glyph: StatusGlyph
var _t := 0.0


func _ready() -> void:
	_m = HudLayout.section(&"target_info")
	_marker_m = HudLayout.section(&"actor_marker")
	_marks_m = HudLayout.section(&"target_marks")
	set_anchors_preset(Control.PRESET_FULL_RECT)
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	_build_info()
	_actor_mote = LampMote.new()
	var px := HudLayout.num(_marker_m, "mote_px")
	_actor_mote.size = Vector2(px, px)
	_actor_mote.period_sec = HudLayout.num(_marker_m, "bob_sec")
	_actor_mote.visible = false
	# The glow sits behind the diamond drawn in _draw(), not over it.
	_actor_mote.show_behind_parent = true
	add_child(_actor_mote)
	_provoke_glyph = StatusGlyph.new(&"provoke")
	var pg := HudLayout.num(_marks_m, "provoke_px")
	_provoke_glyph.size = Vector2(pg, pg)
	_provoke_glyph.visible = false
	add_child(_provoke_glyph)
	_bounce_glyph = StatusGlyph.new(&"reflect")
	var bg := HudLayout.num(_marks_m, "bounce_glyph_px")
	_bounce_glyph.size = Vector2(bg, bg)
	_bounce_glyph.visible = false
	add_child(_bounce_glyph)
	clear()


func _process(delta: float) -> void:
	if reduced_motion:
		return
	_t += delta
	if not targets.is_empty() or _actor_mote.visible:
		queue_redraw()


func set_reduced_motion(on: bool) -> void:
	reduced_motion = on
	_actor_mote.breathing = not on
	queue_redraw()


func show_targets(entries: Array[Dictionary]) -> void:
	targets = entries
	_info.visible = not entries.is_empty()
	_place_bounce_glyph()
	if entries.is_empty():
		queue_redraw()
		return
	var first: Dictionary = entries[0]
	var c: BattleCombatant = first.get("combatant")
	var hostile := bool(first.get("hostile", false))
	_info_name.text = str(first.get("label", "")) if entries.size() == 1 else str(first.get("group_label", ""))
	var role := &"danger" if hostile else &"text"
	_info_name.add_theme_color_override(&"font_color", get_theme_color(role, HymnThemeBuilder.PALETTE_TYPE))
	var show_hp := entries.size() == 1 and c != null and (not hostile or bool(first.get("revealed", false)))
	_info_gauge.visible = show_hp
	_info_hp.visible = show_hp
	_info_note.visible = entries.size() == 1 and hostile and not show_hp
	if show_hp:
		_info_gauge.set_value(c.hp, c.max_hp)
		_info_hp.text = "%d/%d" % [c.hp, c.max_hp]
	_sync_status(c if entries.size() == 1 else null)
	queue_redraw()


func clear() -> void:
	show_targets([])


func targeted_ids() -> Array[StringName]:
	var out: Array[StringName] = []
	for e in targets:
		out.append(StringName(str(e.get("id", ""))))
	return out


## Where a chosen spell would really land after Reflect (&"" when nothing bounces).
func bounce_ids() -> Array[StringName]:
	var out: Array[StringName] = []
	for e in targets:
		if e.has("bounce_pos"):
			out.append(StringName(str(e.get("bounce_id", ""))))
	return out


func info_text() -> String:
	return _info_name.text if _info.visible else ""


## Places the marker above the acting fighter; pass `visible_on = false` to hide it. `auto`
## (&"berserk"/&"confuse") draws it hollow: the fighter acts, but nobody chooses for them.
func show_actor(screen_pos: Vector2, visible_on: bool = true, auto: StringName = &"") -> void:
	_actor_mote.visible = visible_on and auto == &""
	actor_auto = auto
	_actor_pos = screen_pos
	_actor_shown = visible_on
	var px := HudLayout.num(_marker_m, "mote_px")
	_actor_mote.size = Vector2(px, px)
	_actor_mote.position = _marker_center() - Vector2(px, px) * 0.5
	queue_redraw()


func actor_visible() -> bool:
	return _actor_shown


## Hangs the Provoke hook over the provoker (`visible_on = false` hides it).
func show_provoker(screen_pos: Vector2, visible_on: bool = true) -> void:
	_provoke_glyph.visible = visible_on
	var g := HudLayout.num(_marks_m, "provoke_px")
	var chevron := HudLayout.num(_marker_m, "size_px") * 1.2
	var gap := HudLayout.num(_marks_m, "provoke_gap_px")
	_provoke_glyph.position = screen_pos - Vector2(g * 0.5, chevron + gap + g)


func provoker_marked() -> bool:
	return _provoke_glyph.visible


## Bob offset in px (0 under reduced motion).
func _bob() -> float:
	if reduced_motion:
		return 0.0
	return sin(_t * TAU / maxf(HudLayout.num(_marker_m, "bob_sec"), 0.01)) * HudLayout.num(_marker_m, "bob_px")


func _marker_center() -> Vector2:
	return _actor_pos - Vector2(0.0, HudLayout.num(_marker_m, "lift_px") - _bob() * 0.5)


func _draw() -> void:
	var px := HudLayout.num(_marker_m, "size_px") * 0.5
	var bob := _bob()
	if _actor_shown:
		_draw_actor_marker()
	for e in targets:
		var p: Vector2 = e.get("screen_pos", Vector2.ZERO)
		var col := _c(&"danger" if bool(e.get("hostile", false)) else &"focus")
		var tip := p + Vector2(0.0, bob)
		var pts := PackedVector2Array([tip, tip + Vector2(-px, -px * 1.2), tip + Vector2(px, -px * 1.2)])
		draw_colored_polygon(pts, col)
		var outline := pts.duplicate()
		outline.append(pts[0])
		draw_polyline(outline, _c(&"outline"), 1.0, true)
		if bool(e.get("forced", false)):
			# Locked by Provoke: a solid bar over the chevron (the cursor cannot move off it).
			var w := float(get_theme_constant(&"focus_px", HymnThemeBuilder.PALETTE_TYPE))
			draw_line(tip + Vector2(-px, -px * 1.2 - w * 2.0), tip + Vector2(px, -px * 1.2 - w * 2.0), col, w)
		if e.has("bounce_pos"):
			_draw_bounce(p, e["bounce_pos"] as Vector2, col)
	# A panel-dark plate behind the hook and the bounce glyph keeps them legible over bright sky
	# (drawn last, so the bounce arc never crosses it; the glyphs are children, drawn on top).
	for g: StatusGlyph in [_provoke_glyph, _bounce_glyph]:
		if g.visible:
			draw_circle(g.position + g.size * 0.5, g.size.x * 0.5, _c(&"panel_deep"))


## The acting fighter: a focus diamond with a gold frame, a glow halo, and a stem down to the
## fighter's head, so "whose turn" reads at a glance and never looks like a target chevron.
func _draw_actor_marker() -> void:
	var h := HudLayout.num(_marker_m, "size_px") * 0.5
	var frame := HudLayout.num(_marker_m, "frame_px")
	var c := _marker_center()
	var dia := PackedVector2Array([c + Vector2(0, -h), c + Vector2(h, 0), c + Vector2(0, h), c + Vector2(-h, 0)])
	var ring := dia.duplicate()
	ring.append(dia[0])
	var stem_top := c + Vector2(0, h)
	var stem_end := stem_top + Vector2(0, HudLayout.num(_marker_m, "stem_px"))
	if actor_auto == &"":
		draw_line(stem_top, stem_end, _c(&"focus"), frame)
		draw_colored_polygon(dia, _c(&"focus"))
		draw_polyline(ring, _c(&"focus_gold"), frame, true)
		return
	# Auto turn (Berserk/Confuse): hollow diamond, dashed stem.
	_dashed(stem_top, stem_end, _c(&"focus"), frame, HudLayout.num(_marks_m, "bounce_dash_px") * 0.5)
	draw_polyline(ring, _c(&"focus"), frame, true)


## Dashed quadratic arc from the reflector to the real recipient, with an arrowhead.
func _draw_bounce(from: Vector2, to: Vector2, col: Color) -> void:
	var lift := HudLayout.num(_marks_m, "bounce_lift_px")
	var ctrl := (from + to) * 0.5 - Vector2(0.0, lift)
	var n := int(HudLayout.num(_marks_m, "bounce_segments"))
	var w := float(get_theme_constant(&"focus_px", HymnThemeBuilder.PALETTE_TYPE))
	var gold := _c(&"focus_gold")
	var prev := from
	for i in range(1, n + 1):
		var t := float(i) / n
		var q := from.lerp(ctrl, t).lerp(ctrl.lerp(to, t), t)
		if i % 2 == 1:
			draw_line(prev, q, gold, w, true)
		prev = q
	var dir := (to - ctrl).normalized()
	var a := HudLayout.num(_marks_m, "bounce_dash_px")
	var side := Vector2(-dir.y, dir.x)
	draw_colored_polygon(PackedVector2Array([to, to - dir * a * 1.6 + side * a, to - dir * a * 1.6 - side * a]), gold)
	# Where it lands: an outlined chevron in the action's color.
	var px := HudLayout.num(_marker_m, "size_px") * 0.5
	var ring := PackedVector2Array([to, to + Vector2(-px, -px * 1.2), to + Vector2(px, -px * 1.2), to])
	draw_polyline(ring, col, w, true)


func _place_bounce_glyph() -> void:
	_bounce_glyph.visible = false
	for e in targets:
		if not e.has("bounce_pos"):
			continue
		var from: Vector2 = e.get("screen_pos", Vector2.ZERO)
		var to: Vector2 = e["bounce_pos"]
		var top := (from + to) * 0.5 - Vector2(0.0, HudLayout.num(_marks_m, "bounce_lift_px") * 0.5)
		_bounce_glyph.position = top - _bounce_glyph.size * 0.5
		_bounce_glyph.visible = true
		return


func _dashed(a: Vector2, b: Vector2, col: Color, w: float, dash: float) -> void:
	var length := a.distance_to(b)
	var t := 0.0
	while t < length:
		draw_line(a.lerp(b, t / length), a.lerp(b, minf(t + dash, length) / length), col, w)
		t += dash * 2.0


func _c(role: StringName) -> Color:
	return get_theme_color(role, HymnThemeBuilder.PALETTE_TYPE)


func _build_info() -> void:
	_info = PanelContainer.new()
	_info.theme_type_variation = &"PanelSmall"
	HudLayout.place(_info, _m)
	_info.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(_info)
	var v := VBoxContainer.new()
	v.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_info.add_child(v)
	var top := HBoxContainer.new()
	v.add_child(top)
	_info_name = Label.new()
	_info_name.theme_type_variation = &"HudName"
	_info_name.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	top.add_child(_info_name)
	_info_status = HBoxContainer.new()
	top.add_child(_info_status)
	var bottom := HBoxContainer.new()
	bottom.alignment = BoxContainer.ALIGNMENT_BEGIN
	v.add_child(bottom)
	_info_gauge = HudGauge.new(&"hp")
	_info_gauge.custom_minimum_size = Vector2(HudLayout.num(_m, "hp_bar_width"), HudLayout.num(_m, "hp_bar_px"))
	_info_gauge.size_flags_vertical = Control.SIZE_SHRINK_CENTER
	bottom.add_child(_info_gauge)
	_info_hp = Label.new()
	_info_hp.theme_type_variation = &"HudNumber"
	bottom.add_child(_info_hp)
	_info_note = Label.new()
	_info_note.theme_type_variation = &"DimLabel"
	_info_note.text = tr("HUD_TARGET_UNREAD")
	bottom.add_child(_info_note)


func _sync_status(c: BattleCombatant) -> void:
	for ch in _info_status.get_children():
		_info_status.remove_child(ch)
		ch.queue_free()
	if c == null:
		return
	var px := float(HudLayout.section(&"party").get("status_icon_px", 0))
	for sid: StringName in c.statuses:
		var g := StatusGlyph.new(sid, StatusGlyph.inverted_for(c, sid))
		g.custom_minimum_size = Vector2(px, px)
		_info_status.add_child(g)
