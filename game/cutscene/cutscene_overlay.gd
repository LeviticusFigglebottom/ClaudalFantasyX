class_name CutsceneOverlay
extends CanvasLayer
## Screen-space layers of a cutscene (M2-FP-01): letterbox bars, the fade, the dialogue box and
## the option menu, bottom to top. The fade sits under the box so narration can play over black.
## Sizes are fractions of the screen (anchors), so it holds at any window size.

const BOX_SCENE := "res://game/ui/dialogue/dialogue_box.tscn"

var box: DialogueBox
var choices: CutsceneChoices
var fade_rect: ColorRect
var bar_top: ColorRect
var bar_bottom: ColorRect

var _ratio := 0.0
var _letterbox := 0.0


func _init(cfg: Dictionary = {}) -> void:
	name = "CutsceneOverlay"
	layer = int(cfg.get("layer", 1))
	_ratio = float(cfg.get("letterbox_ratio", 0.0))
	var black := Color(str(cfg.get("fade_color", "#000000")))
	bar_top = _full_rect("LetterboxTop", black)
	bar_bottom = _full_rect("LetterboxBottom", black)
	fade_rect = _full_rect("Fade", black)
	set_fade(0.0)
	set_letterbox(0.0)
	box = (load(BOX_SCENE) as PackedScene).instantiate() as DialogueBox
	box.visible = false
	add_child(box)
	var ccfg: Dictionary = cfg.get("choices", {})
	choices = CutsceneChoices.new(ccfg)
	choices.anchor_left = 1.0
	choices.anchor_right = 1.0
	choices.anchor_top = 1.0
	choices.anchor_bottom = 1.0
	choices.grow_horizontal = Control.GROW_DIRECTION_BEGIN
	choices.grow_vertical = Control.GROW_DIRECTION_BEGIN
	choices.offset_right = -float(ccfg.get("right_px", 0))
	choices.offset_bottom = -float(ccfg.get("bottom_px", 0))
	choices.custom_minimum_size.x = float(ccfg.get("min_width_px", 0))
	add_child(choices)


## 0 = clear, 1 = opaque.
func set_fade(alpha: float) -> void:
	fade_rect.color.a = clampf(alpha, 0.0, 1.0)
	fade_rect.visible = fade_rect.color.a > 0.0


func fade_alpha() -> float:
	return fade_rect.color.a


## 0 = no bars, 1 = full bars (letterbox_ratio of the screen height each).
func set_letterbox(t: float) -> void:
	_letterbox = clampf(t, 0.0, 1.0)
	var h := _letterbox * _ratio
	bar_top.anchor_top = 0.0
	bar_top.anchor_bottom = h
	bar_bottom.anchor_top = 1.0 - h
	bar_bottom.anchor_bottom = 1.0
	bar_top.visible = h > 0.0
	bar_bottom.visible = h > 0.0


func letterbox() -> float:
	return _letterbox


func _full_rect(node_name: String, color: Color) -> ColorRect:
	var r := ColorRect.new()
	r.name = node_name
	r.color = color
	r.mouse_filter = Control.MOUSE_FILTER_IGNORE
	r.anchor_right = 1.0
	r.anchor_bottom = 1.0
	add_child(r)
	return r
