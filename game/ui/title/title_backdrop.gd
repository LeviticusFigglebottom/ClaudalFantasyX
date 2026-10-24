class_name TitleBackdrop
extends Control
## The title's animated backdrop (M2-UI-22): under the logo and the menu, the menus' drifting
## caustic light (CausticBackdrop, ADR 0033), a few faint shafts of light slanting down from the
## surface and swaying, and lamp motes (teal and a share of gold) rising slowly with a sideways
## sway and a soft twinkle. Everything moves from the backdrop's own elapsed time, so --fixed-fps
## captures are deterministic, and the motes are laid out by a seeded RandomNumberGenerator, so
## every run starts from the same picture. Under reduced motion nothing moves (the caustic layer
## holds still on its own). Colors are theme roles (focus, ornament_gold); metrics and the seed are
## title_menu.json "backdrop", at the 1920 x 1080 reference.

## One mote's fixed traits, drawn from the seed: [base x 0..1, base y 0..1, radius, rise px/s,
## sway px, sway period s, sway phase, alpha, twinkle period s, twinkle phase, gold (1) or teal (0)].
enum M { X, Y, R, RISE, SWAY, SWAY_SEC, SWAY_PH, ALPHA, TW_SEC, TW_PH, GOLD }

var caustics: CausticBackdrop

var _d: Dictionary = {}
var _t := 0.0
var _motes: Array[PackedFloat32Array] = []


## Takes title_menu.json "backdrop", lays out the motes from its seed, and adds the caustic layer.
func setup(d: Dictionary) -> void:
	_d = d
	_motes = _roll_motes()
	if bool(d.get("caustics", true)) and caustics == null:
		caustics = CausticBackdrop.new()
		caustics.name = &"Caustics"
		caustics.show_behind_parent = true  # the shafts and motes draw over the caustic lines
		add_child(caustics)
	queue_redraw()


func _ready() -> void:
	name = &"TitleBackdrop"
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	mouse_filter = Control.MOUSE_FILTER_IGNORE


func _notification(what: int) -> void:
	if what == NOTIFICATION_THEME_CHANGED or what == NOTIFICATION_RESIZED:
		queue_redraw()


func _process(delta: float) -> void:
	advance(delta)


## Steps the motion by `delta` seconds (nothing under reduced motion). Tests call it directly.
func advance(delta: float) -> void:
	if UiSettings.shared().reduced_motion():
		return
	_t += delta
	queue_redraw()


## Seconds of motion so far (0 until something moves).
func elapsed() -> float:
	return _t


func mote_count() -> int:
	return _motes.size()


## Where mote `i` is now, in the backdrop's own coordinates.
func mote_position(i: int) -> Vector2:
	var m := _motes[i]
	var margin := _num("mote_margin_px")
	var span := size.y + 2.0 * margin
	var y := fposmod(m[M.Y] * span - m[M.RISE] * _t, span) - margin
	var x := m[M.X] * size.x + m[M.SWAY] * sin(TAU * _t / m[M.SWAY_SEC] + m[M.SWAY_PH])
	return Vector2(x, y)


## Mote `i`'s alpha now: its own, breathing with its twinkle, and fading out at the top and bottom.
func mote_alpha(i: int) -> float:
	var m := _motes[i]
	var depth := _num("mote_twinkle_depth")
	var twinkle := 1.0 - depth * 0.5 * (1.0 + sin(TAU * _t / m[M.TW_SEC] + m[M.TW_PH]))
	var edge := sin(PI * clampf(mote_position(i).y / maxf(size.y, 1.0), 0.0, 1.0))
	return m[M.ALPHA] * twinkle * edge


func _draw() -> void:
	if _d.is_empty():
		return
	_draw_shafts()
	_draw_motes()


## Slanted quads from the top edge, bright at the surface and fading to nothing below; the foot
## sways and the brightness breathes slowly.
func _draw_shafts() -> void:
	var light := get_theme_color(&"focus", HymnThemeBuilder.PALETTE_TYPE)
	var length := size.y * _num("shaft_length_pct") / 100.0
	var period := maxf(_num("shaft_sway_sec"), 0.001)
	var shafts: Array = _d.get("shafts", [])
	for i in shafts.size():
		var s: Array = shafts[i]
		var wave := sin(TAU * _t / period + float(i) * TAU / maxf(shafts.size(), 1.0))
		var foot := (float(s[0]) + float(s[3])) + wave * _num("shaft_sway_px")
		var top := float(s[0])
		var a := float(s[4]) * (1.0 - _num("shaft_pulse") * 0.5 * (1.0 + wave))
		var half_top := float(s[1]) * 0.5
		var half_foot := float(s[2]) * 0.5
		var pts := PackedVector2Array(
			[
				Vector2(top - half_top, 0.0),
				Vector2(top + half_top, 0.0),
				Vector2(foot + half_foot, length),
				Vector2(foot - half_foot, length),
			]
		)
		var lit := Color(light, a)
		var clear := Color(light, 0.0)
		draw_polygon(pts, PackedColorArray([lit, lit, clear, clear]))


func _draw_motes() -> void:
	var teal := get_theme_color(&"focus", HymnThemeBuilder.PALETTE_TYPE)
	var gold := get_theme_color(&"ornament_gold", HymnThemeBuilder.PALETTE_TYPE)
	var glow_scale := _num("mote_glow_scale")
	var glow_alpha := _num("mote_glow_alpha")
	for i in _motes.size():
		var m := _motes[i]
		var a := mote_alpha(i)
		if a <= 0.0:
			continue
		var at := mote_position(i)
		var base := gold if m[M.GOLD] > 0.5 else teal
		draw_circle(at, m[M.R] * glow_scale, Color(base, a * glow_alpha), true, -1.0, true)
		draw_circle(at, m[M.R], Color(base, a), true, -1.0, true)


func _roll_motes() -> Array[PackedFloat32Array]:
	var rng := RandomNumberGenerator.new()
	rng.seed = int(_d.get("seed", 0))
	var out: Array[PackedFloat32Array] = []
	for i in int(_d.get("motes", 0)):
		var m := PackedFloat32Array()
		m.resize(M.size())
		m[M.X] = rng.randf()
		m[M.Y] = rng.randf()
		m[M.R] = _roll(rng, "mote_px")
		m[M.RISE] = _roll(rng, "mote_rise_px_per_sec")
		m[M.SWAY] = _roll(rng, "mote_sway_px")
		m[M.SWAY_SEC] = maxf(_roll(rng, "mote_sway_sec"), 0.001)
		m[M.SWAY_PH] = rng.randf() * TAU
		m[M.ALPHA] = _roll(rng, "mote_alpha")
		m[M.TW_SEC] = maxf(_roll(rng, "mote_twinkle_sec"), 0.001)
		m[M.TW_PH] = rng.randf() * TAU
		m[M.GOLD] = 1.0 if rng.randf() * 100.0 < _num("mote_gold_pct") else 0.0
		out.append(m)
	return out


func _roll(rng: RandomNumberGenerator, key: String) -> float:
	var r: Array = _d.get(key, [0.0, 0.0])
	return rng.randf_range(float(r[0]), float(r[1]))


func _num(key: String) -> float:
	return HudLayout.num(_d, key)
