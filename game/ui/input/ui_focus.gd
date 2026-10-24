class_name UiFocus
extends RefCounted
## The mouse on focus-driven lists of Buttons (M2-UI-26, input parity; ADR 0036): screens whose
## keyboard and pad go through Control focus (ui_up / ui_down / ui_accept) get the mouse's half
## with one call per button. A Button already takes a click; this adds:
##   - hover moves the focus to the button (so the highlight is where the pointer is, and Confirm
##     after a hover picks what was hovered);
##   - the wheel moves the focus to the button's neighbour above or below.
## A disabled or unfocusable button is left alone.


## Makes `b` follow the pointer: hover focuses it, the wheel over it focuses its neighbour.
static func follow_pointer(b: BaseButton) -> void:
	b.mouse_entered.connect(_on_hover.bind(b))
	b.gui_input.connect(_on_input.bind(b))


static func _on_hover(b: BaseButton) -> void:
	if b.is_inside_tree() and not b.disabled and b.focus_mode != Control.FOCUS_NONE and not b.has_focus():
		b.grab_focus()


static func _on_input(event: InputEvent, b: BaseButton) -> void:
	var mb := event as InputEventMouseButton
	if mb == null or not mb.pressed:
		return
	if mb.button_index != MOUSE_BUTTON_WHEEL_UP and mb.button_index != MOUSE_BUTTON_WHEEL_DOWN:
		return
	b.accept_event()
	var from: Control = b.get_viewport().gui_get_focus_owner() if b.is_inside_tree() else null
	if from == null:
		from = b
	var next := from.find_valid_focus_neighbor(SIDE_TOP if mb.button_index == MOUSE_BUTTON_WHEEL_UP else SIDE_BOTTOM)
	if next != null:
		next.grab_focus()
