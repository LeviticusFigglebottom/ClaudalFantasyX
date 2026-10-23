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


## Shows `options` and focuses the first. `chosen` fires with the picked DialogueOption.index.
func show_options(options: Array[DialogueOption]) -> void:
	clear()
	for opt in options:
		var b := Button.new()
		b.text = tr(opt.text_key)
		b.alignment = HORIZONTAL_ALIGNMENT_LEFT
		if _font_size > 0:
			b.add_theme_font_size_override(&"font_size", _font_size)
		b.pressed.connect(_on_pressed.bind(opt.index))
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
