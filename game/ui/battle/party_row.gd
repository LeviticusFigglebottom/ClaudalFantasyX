class_name PartyRow
extends Control
## One active fighter in the PartyPanel: portrait, name, status strip, HP and MP numbers with
## bars. Reads a BattleCombatant; never writes to it.
## - The fighter acting now gets a raised fill, a solid focus bar on the left edge and a ▶ mark
##   (hollow when Berserk/Confuse plays the turn for them).
## - The portrait is the hero's face (BattlePortraits; worried while down), its initial only where none
##   is baked yet. Petrify greys the row and turns the portrait to stone (strata lines, not hue alone).
## - Doom shows its count beside the hourglass glyph; Regen under Zombie shows inverted.
## - A hero with a Swell (BattleCombatant.swell_mode set) whose input the HUD draws
##   (SwellRingView.draws_hero, M2-CMB-01) gets the Swell gauge under the name
##   (docs/kb/art/ui.md §6.2: 64 x 4 px, ui_swell). Full, it is framed (a night gap, then a white line) and pulses on a
##   1.6 s sine; with reduced motion it holds the full glow instead of pulsing.

var combatant: BattleCombatant
var is_current := false
var reduced_motion := false
## Why the current turn plays itself (&"berserk" / &"confuse"), or &"" when the player chooses.
var auto_reason: StringName = &""
var is_targeted := false
var tint := Color.WHITE
## Draws the Swell gauge whatever the fighter's mode: a called Vowbound has its own gauge and no
## fill mode (M2-UI-05). Set before setup().
var show_swell := false

var _m: Dictionary = {}
var _name: Label
var _initial: Label
var _face: Texture2D
var _face_down := false
## Where the HP and MP numbers' slot ends (the gauges' top).
var _numbers_bottom := 0.0
var _hp_label: Label
var _mp_label: Label
var _hp: HudGauge
var _mp: HudGauge
var _swell: HudGauge
var _pulse_t := 0.0
var _status_strip: HBoxContainer
var _statuses: Array[StringName] = []
var _status_key := ""
var _doom_label: Label


func setup(metrics: Dictionary, c: BattleCombatant, label: String, portrait_tint: Color = Color.WHITE) -> void:
	_m = metrics
	combatant = c
	tint = portrait_tint
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	var pad := HudLayout.num(_m, "pad_x")
	var gap := HudLayout.num(_m, "column_gap")
	var strip := HudLayout.num(_m, "status_strip_px")
	var name_w := HudLayout.num(_m, "name_width")
	var portrait := portrait_rect()
	var name_x := portrait.end.x + HudLayout.num(_m, "portrait_gap")
	var hp_x := name_x + name_w + gap
	var hp_w := HudLayout.num(_m, "hp_width")
	var mp_x := hp_x + hp_w + gap
	var mp_w := HudLayout.num(_m, "mp_width")
	var h := HudLayout.num(_m, "row_height")
	var bar_y := h - strip * 0.5 - HudLayout.num(_m, "hp_bar_px")
	_initial = _label(&"HudNumber", portrait)
	_initial.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_initial.text = label.left(1)
	_sync_face()
	_name = _label(&"HudName", Rect2(name_x, strip * 0.5, name_w, h - strip * 0.5 * 2.0))
	_name.text = label
	_name.text_overrun_behavior = TextServer.OVERRUN_TRIM_ELLIPSIS
	_name.clip_text = true
	_status_strip = HBoxContainer.new()
	_status_strip.position = Vector2(hp_x, 0.0)
	_status_strip.size = Vector2(hp_w + gap + mp_w, strip)
	_status_strip.add_theme_constant_override(&"separation", int(HudLayout.num(_m, "status_gap")))
	_status_strip.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(_status_strip)
	var num_h := bar_y - strip
	_hp_label = _label(&"HudNumber", Rect2(hp_x, strip, hp_w, num_h))
	_mp_label = _label(&"HudNumber", Rect2(mp_x, strip, mp_w, num_h))
	_hp_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
	_mp_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
	_numbers_bottom = bar_y
	_hp = HudGauge.new(&"hp")
	_hp.low_fraction = HudLayout.num(_m, "low_hp_fraction")
	_hp.hatch_px = HudLayout.num(_m, "hatch_px")
	_hp.position = Vector2(hp_x, bar_y)
	_hp.size = Vector2(hp_w, HudLayout.num(_m, "hp_bar_px"))
	add_child(_hp)
	_mp = HudGauge.new(&"mp")
	_mp.position = Vector2(mp_x, bar_y + HudLayout.num(_m, "hp_bar_px") - HudLayout.num(_m, "mp_bar_px"))
	_mp.size = Vector2(mp_w, HudLayout.num(_m, "mp_bar_px"))
	add_child(_mp)
	if show_swell or (c.swell_mode != &"" and SwellRingView.draws_hero(c.id)):
		var swell_px := HudLayout.num(_m, "swell_bar_px")
		_swell = HudGauge.new(&"swell")
		_swell.position = Vector2(name_x, bar_y + HudLayout.num(_m, "hp_bar_px") - swell_px)
		_swell.size = Vector2(HudLayout.num(_m, "swell_width"), swell_px)
		_swell.full_gap_px = HudLayout.num(_m, "swell_full_gap_px")
		_swell.full_frame_px = HudLayout.num(_m, "swell_full_frame_px")
		add_child(_swell)
	set_process(false)
	refresh(false)


## Re-reads HP, MP and statuses. `animate` drains the bars instead of snapping.
func refresh(animate: bool, drain_sec: float = 0.0) -> void:
	if combatant == null:
		return
	var sec := drain_sec if animate else 0.0
	_hp.set_value(combatant.hp, combatant.max_hp, sec)
	_mp.set_value(combatant.mp, combatant.max_mp, sec)
	_hp_label.text = "%d/%d" % [combatant.hp, combatant.max_hp]
	_mp_label.text = "%d" % combatant.mp
	# The Act I UI pass (2026-10-30): at a larger text size a number outgrew its slot downward onto its gauge; its
	# bottom stays on the gauge's top (it grows up into the status strip). At 100 % it keeps its place.
	for l: Label in [_hp_label, _mp_label] if UiSettings.shared().text_scale() > 1.0 else []:
		l.position.y = minf(l.position.y, _numbers_bottom - maxf(l.size.y, l.get_combined_minimum_size().y))
	_refresh_swell(sec)
	var low := _hp.is_low() or combatant.hp <= 0
	_sync_face()
	if is_stone():
		_initial.add_theme_color_override(&"font_color", _c(&"stone_crack"))
	else:
		_initial.remove_theme_color_override(&"font_color")
	if is_stone():
		_hp_label.add_theme_color_override(&"font_color", _c(&"text_dim"))
	elif low:
		_hp_label.add_theme_color_override(&"font_color", _c(&"danger"))
	else:
		_hp_label.remove_theme_color_override(&"font_color")
	_sync_statuses()
	queue_redraw()


func hp_text() -> String:
	return _hp_label.text


## The Swell gauge, or null for a fighter with no Swell (tests).
func swell_gauge() -> HudGauge:
	return _swell


func _refresh_swell(sec: float) -> void:
	if _swell == null:
		return
	_swell.set_value(combatant.swell, Formulas.SWELL_MAX, sec)
	var full := combatant.swell >= Formulas.SWELL_MAX
	set_process(full and not reduced_motion)
	if not full:
		_pulse_t = 0.0
	_swell.glow = (_pulse_glow() if not reduced_motion else 1.0) if full else 0.0
	_swell.queue_redraw()


## The full gauge's glow on its sine pulse: swell_pulse_min..1 over swell_pulse_sec.
func _pulse_glow() -> float:
	var lo := HudLayout.num(_m, "swell_pulse_min")
	var phase := TAU * _pulse_t / HudLayout.num(_m, "swell_pulse_sec")
	return lo + (1.0 - lo) * 0.5 * (1.0 + cos(phase))


func _process(delta: float) -> void:
	_pulse_t += delta
	_swell.glow = _pulse_glow()
	_swell.queue_redraw()


func status_ids() -> Array[StringName]:
	return _statuses.duplicate()


func is_stone() -> bool:
	return combatant != null and combatant.is_petrified()


## The Doom count shown beside the hourglass ("" when not doomed).
func doom_text() -> String:
	return _doom_label.text if _doom_label != null and is_instance_valid(_doom_label) else ""


func portrait_rect() -> Rect2:
	var px := HudLayout.num(_m, "portrait_px")
	var h := HudLayout.num(_m, "row_height")
	return Rect2(HudLayout.num(_m, "pad_x"), (h - px) * 0.5, px, px)


func _sync_statuses() -> void:
	var ids: Array[StringName] = []
	for sid: StringName in combatant.statuses:
		if ids.size() < int(HudLayout.num(_m, "max_status_icons")):
			ids.append(sid)
	var key := "%s|%d|%s" % [",".join(ids), combatant.doom_count(), combatant.has_status(&"zombie")]
	if key == _status_key:
		return
	_status_key = key
	_statuses = ids
	_doom_label = null
	for ch in _status_strip.get_children():
		_status_strip.remove_child(ch)
		ch.queue_free()
	var px := HudLayout.num(_m, "status_icon_px")
	for sid in ids:
		var g := StatusGlyph.new(sid, StatusGlyph.inverted_for(combatant, sid))
		g.custom_minimum_size = Vector2(px, px)
		g.size_flags_vertical = Control.SIZE_SHRINK_CENTER
		_status_strip.add_child(g)
		if sid == &"doom":
			_doom_label = Label.new()
			_doom_label.theme_type_variation = &"BadgeNumber"
			_doom_label.text = str(combatant.doom_count())
			_doom_label.custom_minimum_size = Vector2(HudLayout.num(_m, "doom_label_width"), px)
			_doom_label.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
			_doom_label.mouse_filter = Control.MOUSE_FILTER_IGNORE
			_status_strip.add_child(_doom_label)


func _draw() -> void:
	if is_current or is_targeted:
		draw_rect(Rect2(Vector2.ZERO, size), _c(&"panel_raised"))
		var edge := _c(&"focus")
		var w := float(get_theme_constant(&"focus_px", HymnThemeBuilder.PALETTE_TYPE))
		if is_targeted:
			draw_rect(Rect2(Vector2.ONE * w * 0.5, size - Vector2.ONE * w), edge, false, w)
		if is_current:
			_draw_current_mark(edge)
	_draw_portrait()
	var out := combatant != null and not combatant.is_alive()
	if _name != null:
		_name.modulate = Color(1, 1, 1, _c(&"text_disabled").a) if out else Color.WHITE


## The current-actor mark: a solid lamp bar on the left edge and a ▶ beside the portrait.
func _draw_current_mark(col: Color) -> void:
	var bar := HudLayout.num(_m, "current_bar_px")
	draw_rect(Rect2(0, 0, bar, size.y), col)
	var m := HudLayout.num(_m, "current_mark_px")
	var x0 := bar + (HudLayout.num(_m, "pad_x") - bar - m) * 0.5
	var cy := size.y * 0.5
	var tri := PackedVector2Array([Vector2(x0, cy - m), Vector2(x0 + m, cy), Vector2(x0, cy + m)])
	if auto_reason == &"":
		draw_colored_polygon(tri, col)
	else:
		# The turn plays itself (Berserk/Confuse): the same mark, hollow.
		tri.append(tri[0])
		draw_polyline(tri, col, 1.0, true)


func _draw_portrait() -> void:
	if _m.is_empty():
		return
	var r := portrait_rect()
	if is_stone():
		draw_rect(r, _c(&"stone"))
		if _face != null:  # the face turned to stone: greyed under the strata
			var inset := HudLayout.num(_m, "portrait_inset")
			draw_texture_rect(_face, r.grow(-inset), false, _c(&"stone"))
		var crack := _c(&"stone_crack")
		var third := r.size.y / 3.0
		draw_line(r.position + Vector2(0, third), r.position + Vector2(r.size.x, third * 0.8), crack, 1.0)
		draw_line(r.position + Vector2(0, third * 2.0), r.position + Vector2(r.size.x, third * 2.2), crack, 1.0)
		draw_rect(r, crack, false, 1.0)
		return
	var col := tint
	if combatant != null and not combatant.is_alive():
		col.a *= _c(&"text_disabled").a
	draw_rect(r, col)
	if _face != null:
		var inset := HudLayout.num(_m, "portrait_inset")
		draw_texture_rect(_face, r.grow(-inset), false, Color(1.0, 1.0, 1.0, col.a))


## The face for this fighter (worried while down); the initial shows only where there is none.
func _sync_face() -> void:
	if combatant == null:
		return
	var down := not combatant.is_alive()
	if _face == null or down != _face_down:
		_face = BattlePortraits.texture(combatant.id, down)
		_face_down = down
	_initial.visible = _face == null


func _c(role: StringName) -> Color:
	return get_theme_color(role, HymnThemeBuilder.PALETTE_TYPE)


func _label(variation: StringName, r: Rect2) -> Label:
	var l := Label.new()
	l.theme_type_variation = variation
	l.position = r.position
	l.size = r.size
	l.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	l.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(l)
	return l
