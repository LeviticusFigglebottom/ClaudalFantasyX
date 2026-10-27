class_name HeroPortraitFrame
extends Control
## A hero's portrait in a small framed panel, for the party pages (M2-MNU-301, ADR 0120): the baked
## picture (HeroPortraits) fills the frame less its inset, cropped to cover; with no picture the hero's
## initial stands in its place. `crop` FACE shows only the head (HeroPortraits.face), for small slots.
## Metrics: game/data/ui/hero_portraits.json "frame". Ignores the mouse.

enum Crop { BUST, FACE }

var crop: Crop = Crop.BUST

var _hero: StringName = &""
var _emotion: StringName = &""
var _panel: Panel
var _picture: TextureRect
var _initial: Label


func _init() -> void:
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	var fm: Dictionary = HeroPortraits.data().get("frame", {})
	_panel = Panel.new()
	_panel.theme_type_variation = StringName(str(fm.get("panel_variation", "")))
	_panel.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_panel.set_anchors_preset(Control.PRESET_FULL_RECT)
	add_child(_panel)
	var inset := HudLayout.num(fm, "inset")
	_picture = TextureRect.new()
	_picture.name = &"Portrait"
	_picture.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	_picture.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_COVERED
	_picture.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_picture.clip_contents = true
	_picture.set_anchors_preset(Control.PRESET_FULL_RECT)
	_picture.offset_left = inset
	_picture.offset_top = inset
	_picture.offset_right = -inset
	_picture.offset_bottom = -inset
	add_child(_picture)
	_initial = Label.new()
	_initial.theme_type_variation = StringName(str(fm.get("initial_variation", "")))
	_initial.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_initial.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	_initial.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_initial.set_anchors_preset(Control.PRESET_FULL_RECT)
	add_child(_initial)


## Shows `hero` (named `display_name`, whose first letter stands in without a picture) in `emotion`.
## &"" hides the frame.
func show_hero(hero: StringName, display_name: String, emotion: StringName = &"") -> void:
	_hero = hero
	_emotion = emotion
	visible = hero != &""
	var tex: Texture2D = null
	if hero != &"":
		tex = HeroPortraits.face(hero, emotion) if crop == Crop.FACE else HeroPortraits.texture(hero, emotion)
	_picture.texture = tex
	_picture.visible = tex != null
	_initial.text = display_name.left(1) if tex == null else ""
	_initial.visible = tex == null


func hero() -> StringName:
	return _hero


func emotion() -> StringName:
	return _emotion


## The picture (its texture is null while the initial stands in).
func picture() -> TextureRect:
	return _picture


## The initial shown without a picture ("" while the picture shows).
func initial_text() -> String:
	return _initial.text if _initial.visible else ""
