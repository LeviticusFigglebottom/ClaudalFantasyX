class_name InputDriver
extends RefCounted
## Drives a screen the way a player would (M2-UI-26, the input parity audit): every press is a real
## InputEvent pushed through the root viewport, so it travels _input -> GUI -> _unhandled_input
## exactly as live input does. One driver per input kind:
##   KEYS  - the action's first InputEventKey binding (press and release);
##   PAD   - the action's first InputEventJoypadButton binding, else its stick direction;
##   MOUSE - hover (motion), left click, right click (Cancel, through UiInput), wheel.
## Parity tests walk each screen once per kind (`for kind in InputDriver.KINDS`).

enum Kind { KEYS, PAD, MOUSE }

const KINDS: Array[Kind] = [Kind.KEYS, Kind.PAD, Kind.MOUSE]

var kind: Kind


func _init(k: Kind) -> void:
	kind = k


static func name_of(k: Kind) -> String:
	return ["keys", "pad", "mouse"][k]


func label() -> String:
	return name_of(kind)


static func root() -> Window:
	return (Engine.get_main_loop() as SceneTree).root


## Frees every Control and CanvasLayer an earlier test left under the test scene, and unpauses.
## The runner has no after_each and never ends a frame between tests, so a leftover menu would
## cover the screen and take this test's clicks. Every parity test's before_each calls it.
static func clear_screen() -> void:
	var tree := Engine.get_main_loop() as SceneTree
	var host: Node = tree.current_scene if tree.current_scene != null else tree.root
	if host == tree.root:
		return  # no test scene: never sweep the root (the autoloads live there)
	for c in host.get_children():
		if c is Control or c is CanvasLayer:
			host.remove_child(c)
			c.free()
	tree.paused = false
	park_pointer()


## Lets go of every mouse button and moves the pointer to a corner, so the viewport's pointer state
## (the last position, a button an earlier test left held, the control that had mouse focus) never
## carries into the next test: the full suite showed mouse steps failing only after other tests.
static func park_pointer() -> void:
	var at := Vector2(1.0, 1.0)
	for b in [MOUSE_BUTTON_LEFT, MOUSE_BUTTON_RIGHT]:
		var up := InputEventMouseButton.new()
		up.button_index = b
		up.pressed = false
		up.position = at
		up.global_position = at
		root().push_input(up, true)
	var m := InputEventMouseMotion.new()
	m.position = at
	m.global_position = at
	root().push_input(m, true)


## Presses and releases `action` with this driver's device. MOUSE has no action bindings: it
## falls back to the keyboard for actions a mouse does not have (a parity test uses the mouse's
## own gestures where one exists: click, right click, wheel).
func press(action: StringName) -> void:
	var ev := event_for(action, kind if kind != Kind.MOUSE else Kind.KEYS)
	assert(ev != null, "InputDriver: '%s' has no %s binding" % [action, label()])
	send(ev, true)
	send(ev, false)


## Presses `action` and keeps it down (a hold: Toma's brace, hold to confirm, hold to skip) until
## let_go(). MOUSE falls back to the keyboard, as press() does.
func hold(action: StringName) -> void:
	send(event_for(action, kind if kind != Kind.MOUSE else Kind.KEYS), true)


## Lets go of an action held with hold().
func let_go(action: StringName) -> void:
	send(event_for(action, kind if kind != Kind.MOUSE else Kind.KEYS), false)


## A fresh event for `action` on device `k` (null when the action has none).
static func event_for(action: StringName, k: Kind) -> InputEvent:
	if not InputMap.has_action(action):
		return null
	var axis: InputEventJoypadMotion = null
	for ev in InputMap.action_get_events(action):
		if k == Kind.KEYS and ev is InputEventKey:
			var key := InputEventKey.new()
			key.keycode = (ev as InputEventKey).keycode
			key.physical_keycode = (ev as InputEventKey).physical_keycode
			return key
		if k == Kind.PAD and ev is InputEventJoypadButton:
			var b := InputEventJoypadButton.new()
			b.button_index = (ev as InputEventJoypadButton).button_index
			return b
		if k == Kind.PAD and ev is InputEventJoypadMotion and axis == null:
			axis = InputEventJoypadMotion.new()
			axis.axis = (ev as InputEventJoypadMotion).axis
			axis.axis_value = signf((ev as InputEventJoypadMotion).axis_value)
	return axis


## True when `action` has a binding on device `k`.
static func has_binding(action: StringName, k: Kind) -> bool:
	return event_for(action, k) != null


## Pushes `ev` (as a press or a release) through the root viewport. Mouse events carry viewport
## coordinates (point_of), so they go in as local.
static func send(ev: InputEvent, down: bool) -> void:
	var e := ev.duplicate() as InputEvent
	if e is InputEventKey:
		(e as InputEventKey).pressed = down
	elif e is InputEventJoypadButton:
		(e as InputEventJoypadButton).pressed = down
	elif e is InputEventJoypadMotion:
		if not down:
			(e as InputEventJoypadMotion).axis_value = 0.0
	elif e is InputEventMouseButton:
		(e as InputEventMouseButton).pressed = down
	root().push_input(e, e is InputEventMouse)


# --- Mouse --------------------------------------------------------------------------------------


## The centre of `c` in its viewport's coordinates (mouse events are pushed in those, local to the
## viewport, so the headless window's size and stretch never shift a click onto the next row).
static func point_of(c: Control) -> Vector2:
	return c.get_global_transform_with_canvas() * (c.size * 0.5)


## Moves the pointer onto `c` (hover).
static func hover(c: Control) -> void:
	var m := InputEventMouseMotion.new()
	m.position = point_of(c)
	m.global_position = m.position
	root().push_input(m, true)


## Hovers then clicks `c` with `button` (left by default).
static func click(c: Control, button: MouseButton = MOUSE_BUTTON_LEFT) -> void:
	hover(c)
	var b := InputEventMouseButton.new()
	b.button_index = button
	b.position = point_of(c)
	b.global_position = b.position
	b.button_mask = MOUSE_BUTTON_MASK_LEFT if button == MOUSE_BUTTON_LEFT else 0
	send(b, true)
	send(b, false)


## Right-clicks over `c` (Cancel on every screen, through UiInput).
static func right_click(c: Control) -> void:
	click(c, MOUSE_BUTTON_RIGHT)


## Moves the pointer to `at` (root viewport coordinates: a fighter's BattleController.head_pos,
## a point from point_of).
static func hover_at(at: Vector2) -> void:
	var m := InputEventMouseMotion.new()
	m.position = at
	m.global_position = at
	root().push_input(m, true)


## Hovers then clicks at `at` (root viewport coordinates) with `button`.
static func click_at(at: Vector2, button: MouseButton = MOUSE_BUTTON_LEFT) -> void:
	hover_at(at)
	button_at(at, button, true)
	button_at(at, button, false)


## Presses (`down`) or releases `button` at `at` without moving first: a held click is
## button_at(.., true) now and button_at(.., false) later.
static func button_at(at: Vector2, button: MouseButton, down: bool) -> void:
	var b := InputEventMouseButton.new()
	b.button_index = button
	b.position = at
	b.global_position = at
	b.button_mask = (MOUSE_BUTTON_MASK_LEFT if button == MOUSE_BUTTON_LEFT else 0) if down else 0
	send(b, down)


## Turns the wheel over `c`: `steps` notches down (negative: up).
static func wheel(c: Control, steps: int) -> void:
	hover(c)
	for i in absi(steps):
		var b := InputEventMouseButton.new()
		b.button_index = MOUSE_BUTTON_WHEEL_DOWN if steps > 0 else MOUSE_BUTTON_WHEEL_UP
		b.position = point_of(c)
		b.global_position = b.position
		b.factor = 1.0
		send(b, true)
		send(b, false)


## Left-drags from the centre of `c` by `delta` pixels (root window coordinates).
static func drag(c: Control, delta: Vector2) -> void:
	var at := point_of(c)
	var down := InputEventMouseButton.new()
	down.button_index = MOUSE_BUTTON_LEFT
	down.position = at
	down.global_position = at
	down.button_mask = MOUSE_BUTTON_MASK_LEFT
	send(down, true)
	var m := InputEventMouseMotion.new()
	m.position = at + delta
	m.global_position = m.position
	m.relative = delta
	m.button_mask = MOUSE_BUTTON_MASK_LEFT
	root().push_input(m, true)
	var up := down.duplicate() as InputEventMouseButton
	up.position = at + delta
	up.global_position = up.position
	up.button_mask = 0
	send(up, false)
