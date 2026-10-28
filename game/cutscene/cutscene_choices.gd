class_name CutsceneChoices
extends PanelContainer
## The option menu of a cutscene (M2-FP-01): one Button per DialogueOption, keyboard/controller
## through focus (ui_up / ui_down / ui_accept) and mouse clicks. Text is tr(option.text_key).

signal chosen(index: int)

var _list: VBoxContainer
var _buttons: Array[Button] = []
var _font_size := 0


func _init(cfg: Dictionary = {}) -> void:
	name = "Choices"
	visible = false
	_font_size = int(cfg.get("font_size", 0))
	_list = VBoxContainer.new()
	_list.add_theme_constant_override(&"separation", int(cfg.get("separation", 0)))
	add_child(_list)


## M2-FP-1001: the player's palette and text size, like every menu outside battle (M2-UI-09).
func _ready() -> void:
	UiSettings.shared().follow(self)


## Shows `options` and focuses the first. `chosen` fires with the picked DialogueOption.index.
func show_options(options: Array[DialogueOption]) -> void:
	clear()
	for opt in options:
		var b := Button.new()
		b.text = tr(opt.text_key)
		b.alignment = HORIZONTAL_ALIGNMENT_LEFT
		if _font_size > 0:  # the configured size, at the player's text size (the theme scales only its own)
			b.add_theme_font_size_override(&"font_size", roundi(_font_size * UiSettings.shared().text_scale()))
		b.pressed.connect(_on_pressed.bind(opt.index))
		UiFocus.follow_pointer(b)  # M2-UI-26: hover focuses, the wheel steps (UI-owned)
		_list.add_child(b)
		_buttons.append(b)
	visible = true
	if not _buttons.is_empty() and is_inside_tree():
		_buttons[0].grab_focus()


func clear() -> void:
	for b in _buttons:
		b.queue_free()
	_buttons.clear()
	visible = false


func option_texts() -> Array[String]:
	var out: Array[String] = []
	for b in _buttons:
		out.append(b.text)
	return out


## Picks option `index` as if its button were pressed (tests, captures).
func pick(index: int) -> void:
	if visible:
		_on_pressed(index)


func _on_pressed(index: int) -> void:
	clear()
	chosen.emit(index)
