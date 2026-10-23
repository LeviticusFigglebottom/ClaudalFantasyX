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
	var used := clock.ring.buttons_used()
	for action: StringName in BUTTONS:
		if not used.has(BUTTONS[action]):
			continue
		if event.is_action_pressed(action):
			clock.press(live, BUTTONS[action])
			return true
		if event.is_action_released(action):
			clock.release(live, BUTTONS[action])
			return true
	return false
