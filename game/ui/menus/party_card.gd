class_name PartyCard
extends Control
## One hero of the active line on the field menu's root (M2-MNU-304): a framed portrait (HeroPortraitFrame,
## the "field_menu" page's emotion, worried when fallen), the name, and HP and MP as gauges with numbers, so
## the menu opens on the party rather than on a list. Metrics: field_menu.json "party" (reference px). A
## view only; FieldMenu fills it from FormationMenuModel.vitals. Ignores the mouse.

const PAGE := &"field_menu"

var _m: Dictionary = {}
var _panel: Panel
var _portrait: HeroPortraitFrame
var _name: Label
var _hp: HudGauge
var _mp: HudGauge
var _hp_text: Label
var _mp_text: Label
var _hero: StringName = &""


## Builds the card at `metrics` (the "party" block: card_w x card_h).
func setup(metrics: Dictionary) -> void:
	_m = metrics
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	var card := Vector2(HudLayout.num(_m, "card_w"), HudLayout.num(_m, "card_h"))
	size = card
	var pad := HudLayout.num(_m, "pad")
	_panel = Panel.new()
	_panel.theme_type_variation = &"PanelSmall"
	_panel.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_panel.size = card
	add_child(_panel)
	var px := HudLayout.num(_m, "portrait_px")
	_portrait = HeroPortraitFrame.new()
	_portrait.position = Vector2((card.x - px) * 0.5, pad)
	_portrait.size = Vector2(px, px)
	add_child(_portrait)
	var line_h := HudLayout.num(_m, "line_height")
	var y := pad + px + HudLayout.num(_m, "gap")
	_name = _label(&"BodyLabel", Rect2(pad, y, card.x - pad * 2.0, line_h))
	_name.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	y += line_h
	var gauge_h := HudLayout.num(_m, "gauge_height")
	var row := Rect2(pad, y, card.x - pad * 2.0, line_h)
	_hp_text = _stat_row(row, "FIELD_MENU_PARTY_HP")
	_hp = _gauge(&"hp", Rect2(pad, row.end.y, row.size.x, gauge_h))
	row.position.y = row.end.y + gauge_h + HudLayout.num(_m, "gauge_gap")
	_mp_text = _stat_row(row, "FIELD_MENU_PARTY_MP")
	_mp = _gauge(&"mp", Rect2(pad, row.end.y, row.size.x, gauge_h))


## Shows hero `cid` named `display_name` with `v` ({hp, max_hp, mp, max_mp, fallen}).
func show_hero(cid: StringName, display_name: String, v: Dictionary) -> void:
	_hero = cid
	var fallen := bool(v.get("fallen", false))
	_portrait.show_hero(cid, display_name, HeroPortraits.page_emotion(PAGE, fallen))
	_name.text = display_name
	_hp_text.text = tr("FIELD_MENU_PARTY_HP_FMT").format({"hp": int(v.get("hp", 0)), "max": int(v.get("max_hp", 0))})
	_mp_text.text = tr("FIELD_MENU_PARTY_MP_FMT").format({"mp": int(v.get("mp", 0)), "max": int(v.get("max_mp", 0))})
	_hp.set_value(int(v.get("hp", 0)), int(v.get("max_hp", 0)))
	_mp.set_value(int(v.get("mp", 0)), int(v.get("max_mp", 0)))
	modulate.a = HudLayout.num(_m, "fallen_alpha") if fallen else 1.0


func hero() -> StringName:
	return _hero


func portrait() -> HeroPortraitFrame:
	return _portrait


## The card's words, in order (tests).
func shown_text() -> PackedStringArray:
	return PackedStringArray([_name.text, _hp_text.text, _mp_text.text])


## A dim stat name on the left of `r` (`key`) and its number on the right; returns the number label.
func _stat_row(r: Rect2, key: String) -> Label:
	_label(&"DimLabel", r).text = tr(key)
	var value := _label(&"HudNumber", r)
	value.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
	return value


func _gauge(role: StringName, r: Rect2) -> HudGauge:
	var g := HudGauge.new(role)
	g.position = r.position
	g.size = r.size
	g.low_fraction = HudLayout.num(_m, "low_fraction")
	add_child(g)
	return g


func _label(variation: StringName, r: Rect2) -> Label:
	var l := Label.new()
	l.theme_type_variation = variation
	l.position = r.position
	l.size = r.size
	l.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	l.text_overrun_behavior = TextServer.OVERRUN_TRIM_ELLIPSIS
	l.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(l)
	return l
