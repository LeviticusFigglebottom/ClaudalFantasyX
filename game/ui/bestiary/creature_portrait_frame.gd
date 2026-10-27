class_name CreaturePortraitFrame
extends Control
## A creature's baked portrait in a small framed panel, for the bestiary page (M2-MNU-302, ADR 0120): a
## soft pool of light behind the creature (dark creatures still read on the deep-blue panel) and the
## picture (CreaturePortraits) fitted inside the frame less its inset. As a silhouette (a foe never Read)
## the same picture is modulated to a dark theme colour. An enemy without a portrait hides the frame.
## Metrics: game/data/ui/creature_portraits.json "frame". Ignores the mouse. The sibling of
## HeroPortraitFrame.

var _enemy: StringName = &""
var _silhouette := false
var _panel: Panel
var _glow: TextureRect
var _picture: TextureRect


func _init() -> void:
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	visible = false
	var fm := _metrics()
	_panel = Panel.new()
	_panel.theme_type_variation = StringName(str(fm.get("panel_variation", "")))
	_panel.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_panel.set_anchors_preset(Control.PRESET_FULL_RECT)
	add_child(_panel)
	_glow = _rect(&"Glow", HudLayout.num(fm, "inset"))
	_glow.stretch_mode = TextureRect.STRETCH_SCALE
	_picture = _rect(&"Portrait", HudLayout.num(fm, "inset"))
	_picture.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED


func _notification(what: int) -> void:
	if what == NOTIFICATION_THEME_CHANGED:
		_apply_colours()


## Shows enemy `enemy_id`'s portrait, as a silhouette when `silhouette`; hides the frame when it has none.
func show_creature(enemy_id: StringName, silhouette: bool = false) -> void:
	_enemy = enemy_id
	_silhouette = silhouette
	var tex := CreaturePortraits.texture(enemy_id) if enemy_id != &"" else null
	_picture.texture = tex
	visible = tex != null
	_apply_colours()


## The enemy on show (&"" when none).
func enemy() -> StringName:
	return _enemy if visible else &""


func is_silhouette() -> bool:
	return visible and _silhouette


func picture() -> TextureRect:
	return _picture


func _apply_colours() -> void:
	var fm := _metrics()
	var glow := get_theme_color(StringName(str(fm.get("glow_role", ""))), HymnThemeBuilder.PALETTE_TYPE)
	var dark := get_theme_color(StringName(str(fm.get("silhouette_role", ""))), HymnThemeBuilder.PALETTE_TYPE)
	_picture.modulate = dark if _silhouette else Color.WHITE
	var g := Gradient.new()
	g.set_color(0, glow)
	g.set_color(1, Color(glow, 0.0))
	var tex := GradientTexture2D.new()
	tex.gradient = g
	tex.fill = GradientTexture2D.FILL_RADIAL
	tex.fill_from = Vector2(0.5, 0.5)
	tex.fill_to = Vector2(0.5 + HudLayout.num(fm, "glow_radius"), 0.5)
	_glow.texture = tex


func _rect(node_name: StringName, inset: float) -> TextureRect:
	var r := TextureRect.new()
	r.name = node_name
	r.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	r.mouse_filter = Control.MOUSE_FILTER_IGNORE
	r.set_anchors_preset(Control.PRESET_FULL_RECT)
	r.offset_left = inset
	r.offset_top = inset
	r.offset_right = -inset
	r.offset_bottom = -inset
	add_child(r)
	return r


static func _metrics() -> Dictionary:
	return CreaturePortraits.data().get("frame", {})
