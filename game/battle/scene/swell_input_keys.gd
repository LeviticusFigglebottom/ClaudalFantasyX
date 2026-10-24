class_name SwellInputKeys
extends RefCounted
## Maps input events onto an open SwellInput through its SwellRingClock (M2-CMB-01). ui_accept and
## the four ui_* directions press and release the matching SwellInput button, for the buttons the
## input uses (SwellInput.buttons_used; any other event is left unhandled); ui_cancel backs out
## (only before the first grade, SwellInput.cancel). BattleController never needs to know which
## kind of input is open.

## Input action -> SwellInput button.
const BUTTONS := {
	&"ui_accept": SwellInput.BUTTON_ACCEPT,
	&"ui_up": SwellInput.BUTTON_UP,
	&"ui_down": SwellInput.BUTTON_DOWN,
	&"ui_left": SwellInput.BUTTON_LEFT,
	&"ui_right": SwellInput.BUTTON_RIGHT,
}
const CANCEL := &"ui_cancel"


## Feeds `event` to `clock`'s input (`live` false: graded where a frozen input stands). True when
## the event was one of the input's (handled), false to let it pass.
static func feed(event: InputEvent, clock: SwellRingClock, live: bool) -> bool:
	if event.is_action_pressed(CANCEL):
		clock.ring.cancel()
		return true
	# Hold to confirm (M2-UI-14): Confirm's state is tracked for every kind, even one that does not
	# press it, and time catches up first, so a step graded at this moment sees the held state.
	var hold_event := clock.ring.assist_hold and (event.is_action(&"ui_accept"))
	if hold_event and not clock.ring.buttons_used().has(SwellInput.BUTTON_ACCEPT):
		clock.hold(live, event.is_pressed())
		return true
	var used := clock.ring.buttons_used()
	for action: StringName in BUTTONS:
		if not used.has(BUTTONS[action]):
			continue
		if event.is_action_pressed(action):
			if hold_event:
				clock.hold(live, true)
			clock.press(live, BUTTONS[action])
			return true
		if event.is_action_released(action):
			if hold_event:
				clock.hold(live, false)  # first: an early release is played by hand
			clock.release(live, BUTTONS[action])
			return true
	return false


## A hold-and-release input (SwellBrace) opened by a ui_accept press the menu has just used: if
## that accept is still held, it starts the hold, so the player does not have to press again
## before the first blow (M2-NIT-03 / M2-UI-03). `is_held` reads Input; tests inject their own.
## With hold to confirm (M2-UI-14) a held accept also starts holding, for any kind.
static func carry_held(clock: SwellRingClock, is_held: Callable = Input.is_action_pressed) -> bool:
	if not bool(is_held.call(&"ui_accept")):
		return false
	if clock.ring.assist_hold:
		clock.hold(false, true)
	if not (clock.ring is SwellBrace):
		return clock.ring.assist_hold
	clock.press(false, SwellInput.BUTTON_ACCEPT)
	return true
