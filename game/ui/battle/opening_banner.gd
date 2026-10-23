class_name OpeningBanner
extends Control
## The banner for a preemptive or an ambush opening (M2-UI-02, SPEC §6.1, formulas.md § Openings):
## a title in the banner serif between two thin rules, the caption (BattleOpening.CAPTION_KEYS)
## and what it means for the order, top centre, clear of the timeline. art/ui.md §7's location
## banner, shortened for a battle: it fades in, holds and fades out (battle_hud.json
## "opening_banner"), and never takes input. Shown by BattleBestiary at the first turn.
##
## A dark band fading at its ends sits behind the words for contrast. Not hue alone: the rule
## ends carry the timeline's side shapes, square for the party (a preemptive strike) and a
## chevron for the foes (an ambush), and the words say which. Reduced motion keeps the fades but
## drops the rise.

const KIND_PREEMPTIVE := &"preemptive"
const KIND_AMBUSH := &"ambush"

var kind: StringName = &""
var reduced_motion := false

var _m: Dictionary = {}
var _title: Label
var _caption: Label
var _tween: Tween


func _ready() -> void:
	_m = HudLayout.section(&"opening_banner")
	HudLayout.place(self, _m)
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	var title_h := HudLayout.num(_m, "title_height")
	_title = _label(&"BannerLabel", Rect2(0.0, 0.0, size.x, title_h))
	_caption = _label(&"HelpLabel", Rect2(0.0, title_h, size.x, size.y - title_h))
	visible = false


## Shows the banner for opening `opening` (a BattleOpening id; a normal opening shows nothing).
## `animate` false holds it fully shown with no timer (captures and instant-pacing tests).
func show_opening(opening: StringName, animate: bool = true) -> void:
	if opening != KIND_PREEMPTIVE and opening != KIND_AMBUSH:
		hide_banner()
		return
	kind = opening
	if opening == KIND_PREEMPTIVE:
		_title.text = tr("HUD_OPENING_PREEMPTIVE_TITLE")
		_caption.text = " ".join([tr("HUD_OPENING_PREEMPTIVE"), tr("HUD_OPENING_PREEMPTIVE_EFFECT")])
	else:
		_title.text = tr("HUD_OPENING_AMBUSH_TITLE")
		_caption.text = " ".join([tr("HUD_OPENING_AMBUSH"), tr("HUD_OPENING_AMBUSH_EFFECT")])
	visible = true
	modulate.a = 1.0
	position.y = HudLayout.rect_of(_m).position.y
	queue_redraw()
	if _tween != null and _tween.is_valid():
		_tween.kill()
	if animate and is_inside_tree():
		_play()


func hide_banner() -> void:
	if _tween != null and _tween.is_valid():
		_tween.kill()
	visible = false
	kind = &""


func is_showing() -> bool:
	return visible


func title_text() -> String:
	return _title.text


func caption_text() -> String:
	return _caption.text


## The palette role of the rules: the side that acts first (focus for the party, danger for foes).
func rule_role() -> StringName:
	return &"danger" if kind == KIND_AMBUSH else &"focus"


func _play() -> void:
	var rest := HudLayout.rect_of(_m).position.y
	var rise := 0.0 if reduced_motion else HudLayout.num(_m, "rise_px")
	modulate.a = 0.0
	position.y = rest + rise
	_tween = create_tween()
	_tween.set_parallel(true).set_trans(Tween.TRANS_CUBIC).set_ease(Tween.EASE_OUT)
	_tween.tween_property(self, "modulate:a", 1.0, HudLayout.num(_m, "fade_in_sec"))
	_tween.tween_property(self, "position:y", rest, HudLayout.num(_m, "fade_in_sec"))
	_tween.chain().tween_interval(HudLayout.num(_m, "hold_sec"))
	_tween.chain().tween_property(self, "modulate:a", 0.0, HudLayout.num(_m, "fade_out_sec"))
	_tween.chain().tween_callback(hide_banner)


func _draw() -> void:
	if kind == &"":
		return
	_draw_band()
	var col := get_theme_color(rule_role(), HymnThemeBuilder.PALETTE_TYPE)
	var gold := get_theme_color(&"focus_gold", HymnThemeBuilder.PALETTE_TYPE)
	var half := HudLayout.num(_m, "rule_length") * 0.5
	var px := HudLayout.num(_m, "rule_px")
	var mark := HudLayout.num(_m, "mark_px")
	var cx := size.x * 0.5
	for y: float in [HudLayout.num(_m, "rule_top"), HudLayout.num(_m, "rule_bottom")]:
		draw_rect(Rect2(cx - half, y, half * 2.0, px), gold)
		for side: float in [-1.0, 1.0]:
			_draw_mark(Vector2(cx + side * (half + mark), y + px * 0.5), side, mark, col)


## A dark band behind the words, fading out at both ends, so the text holds its contrast over a
## bright sky (art/ui.md §9) without a panel frame.
func _draw_band() -> void:
	var deep := get_theme_color(&"panel_low", HymnThemeBuilder.PALETTE_TYPE)
	deep.a = HudLayout.num(_m, "band_alpha")
	var clear := deep
	clear.a = 0.0
	var fade := size.x * HudLayout.num(_m, "band_fade")
	var h := size.y
	draw_rect(Rect2(fade, 0.0, size.x - fade * 2.0, h), deep)
	for edge: Array in [[0.0, fade], [size.x, size.x - fade]]:
		var outer := float(edge[0])
		var inner := float(edge[1])
		var pts := PackedVector2Array([Vector2(outer, 0.0), Vector2(inner, 0.0), Vector2(inner, h), Vector2(outer, h)])
		draw_polygon(pts, PackedColorArray([clear, deep, deep, clear]))


## The side shape at each end of a rule: a square (the party's chips) or an outward chevron
## (the foes' chip edge).
func _draw_mark(at: Vector2, side: float, px: float, col: Color) -> void:
	if kind == KIND_PREEMPTIVE:
		draw_rect(Rect2(at - Vector2(px, px) * 0.5, Vector2(px, px)), col)
		return
	var tip := at + Vector2(side * px * 0.5, 0.0)
	var back := at - Vector2(side * px * 0.5, 0.0)
	var pts := PackedVector2Array([back + Vector2(0.0, -px * 0.5), tip, back + Vector2(0.0, px * 0.5)])
	draw_polyline(pts, col, HudLayout.num(_m, "chevron_px"), true)


func _label(variation: StringName, r: Rect2) -> Label:
	var l := Label.new()
	l.theme_type_variation = variation
	l.position = r.position
	l.size = r.size
	l.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	l.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	l.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(l)
	return l
