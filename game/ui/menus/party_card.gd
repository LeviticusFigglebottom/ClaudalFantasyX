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
## The stat rows' dim names ("HP", "MP"), laid out with their numbers.
var _heads: Array[Label] = []
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
	_portrait = HeroPortraitFrame.new()
	add_child(_portrait)
	_name = _label(&"BodyLabel", Rect2())
	_name.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_hp_text = _stat_row("FIELD_MENU_PARTY_HP")
	_hp = _gauge(&"hp")
	_mp_text = _stat_row("FIELD_MENU_PARTY_MP")
	_mp = _gauge(&"mp")
	_layout()


## Places the portrait, the name and the two stat rows down the card. A line is the metrics' line_height grown with
## the text size setting (130%: the Act I UI pass of 2026-10-30, where the name sat on the HP row; at 100% nothing
## moves); the portrait gives up what the text needs, so the card keeps its size.
func _layout() -> void:
	var card := size
	var pad := HudLayout.num(_m, "pad")
	var gap := HudLayout.num(_m, "gap")
	var gauge_h := HudLayout.num(_m, "gauge_height")
	var gauge_gap := HudLayout.num(_m, "gauge_gap")
	var line_h := HudLayout.num(_m, "line_height") * UiSettings.shared().text_scale()
	var text_h := line_h * 3.0 + gauge_h * 2.0 + gauge_gap
	var px := clampf(card.y - pad * 2.0 - gap - text_h, 0.0, HudLayout.num(_m, "portrait_px"))
	_portrait.position = Vector2((card.x - px) * 0.5, pad)
	_portrait.size = Vector2(px, px)
	var w := card.x - pad * 2.0
	var y := pad + px + gap
	_place(_name, Rect2(pad, y, w, line_h))
	y += line_h
	for i in 2:
		var number := _hp_text if i == 0 else _mp_text
		_place(_heads[i], Rect2(pad, y, w, line_h))
		_place(number, Rect2(pad, y, w, line_h))
		var gauge := _hp if i == 0 else _mp
		gauge.position = Vector2(pad, y + line_h)
		gauge.size = Vector2(w, gauge_h)
		y += line_h + gauge_h + gauge_gap


static func _place(l: Control, r: Rect2) -> void:
	l.position = r.position
	l.size = r.size


## Shows hero `cid` named `display_name` with `v` ({hp, max_hp, mp, max_mp, fallen}).
func show_hero(cid: StringName, display_name: String, v: Dictionary) -> void:
	_hero = cid
	_layout()  # the text size may have changed since the card was built
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


## A dim stat name on the left (`key`) and its number on the right (placed by _layout); returns the number label.
func _stat_row(key: String) -> Label:
	var head := _label(&"DimLabel", Rect2())
	head.text = tr(key)
	_heads.append(head)
	var value := _label(&"HudNumber", Rect2())
	value.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
	return value


func _gauge(role: StringName) -> HudGauge:
	var g := HudGauge.new(role)
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
