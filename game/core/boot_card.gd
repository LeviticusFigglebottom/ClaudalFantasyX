class_name BootCard
extends CanvasLayer
## An opaque card that hides the screen while warm-up work runs, then lifts (M2-ARC-03, ADR 0029).
##
## boot.gd covers the title with one while the resident shader warm-up (ShaderPrewarm.spawn_resident) and
## the router's font warm-up run, so their frames are hidden loading time, not visible hitches. The card is
## the empty title's own background (the renderer's clear colour) with nothing on it, so lifting it reads as
## the title fading in. It blocks the mouse; the owner blocks keys (boot turns off the title's
## _unhandled_input while it waits).
##
## Life cycle: cover() adds it (opaque at once, or fading in over `fade_in_sec`; `covered` fires once it is
## opaque). The owner adds the work: wait_for_node(node) (until the node is freed, or its is_running() turns
## false) and wait_until(condition). arm() starts the wait; before it, the card never opens, so work added
## a frame later (call_deferred) cannot be missed. Once everything is done (or after MAX_WAIT_MS), `opened`
## fires with the wait's stats and the card lifts over `lift_sec` (0: it is hidden at once, for a card under
## an opaque router fade); `revealed` fires when it has fully lifted. It stays in the tree, hidden, until its
## owner frees it.
##
## Reuse (M1-UI-11, a preset change on the title): cover(parent, SceneRouter.FADE_SEC); on `covered` start
## the warm-up and pass its node to wait_for_node(); arm(); on `opened` give the menu its input back and,
## to measure the reveal like a scene change, call SceneRouter.measure_reveal(path, card.is_lifted).
## hold_reveal_of(SceneRouter) keeps a router change from lifting its own fade until the card opens (boot
## does this when the title is reached through a SceneRouter change).

signal covered
signal opened(stats: Dictionary)
signal revealed

enum Phase { FADING_IN, WAITING, LIFTING, LIFTED }

## Just under SceneRouter's fade (FADE_LAYER 128), above every game and debug layer.
const LAYER := 127
## The longest the card waits for its work before it opens anyway (with a warning).
const MAX_WAIT_MS := 10000.0
const MSEC_PER_SEC := 1000.0
const LOG_PREFIX := "BootCard"

## Seconds the lift takes (0: hidden at once).
var lift_sec := 0.0
## Seconds the fade-in takes (0: opaque at once).
var fade_in_sec := 0.0

var _rect: ColorRect
var _phase := Phase.WAITING
var _armed := false
var _nodes: Array[WeakRef] = []
var _conditions: Array[Callable] = []
var _router: Node
var _wait_frames := 0
var _wait_ms := 0.0
var _max_frame_ms := 0.0
var _anim_sec := 0.0


## Adds a card under `parent`: opaque at once when `fade_in` is 0, else fading in over `fade_in` seconds.
static func cover(parent: Node, fade_in: float = 0.0, lift: float = 0.0) -> BootCard:
	var card := BootCard.new()
	card.fade_in_sec = fade_in
	card.lift_sec = lift
	parent.add_child(card)
	return card


func _init() -> void:
	name = "BootCard"
	layer = LAYER
	_rect = ColorRect.new()
	_rect.name = "Card"
	_rect.mouse_filter = Control.MOUSE_FILTER_STOP
	_rect.set_anchors_preset(Control.PRESET_FULL_RECT)
	_rect.color = RenderingServer.get_default_clear_color()
	add_child(_rect)


func _ready() -> void:
	if fade_in_sec > 0.0:
		_phase = Phase.FADING_IN
		_set_alpha(0.0)
	else:
		_set_alpha(1.0)
		covered.emit.call_deferred()


## Waits until `node` is freed, or until its is_running() is false (a ShaderPrewarm). Null is done.
func wait_for_node(node: Node) -> void:
	if node != null:
		_nodes.append(weakref(node))


## Waits until `condition` returns true (a freed object's Callable counts as true).
func wait_until(condition: Callable) -> void:
	_conditions.append(condition)


## Keeps `router`'s change from lifting its fade (SceneRouter.hold_reveal) until the card opens.
func hold_reveal_of(router: Node) -> void:
	if router != null and router.has_method(&"hold_reveal"):
		router.call(&"hold_reveal", self)
		_router = router


## Starts the wait: from the next poll the card opens once its work is done.
func arm() -> void:
	_armed = true


func is_armed() -> bool:
	return _armed


func is_waiting() -> bool:
	return _phase == Phase.FADING_IN or _phase == Phase.WAITING


## True once the card has fully lifted (nothing of it is drawn).
func is_lifted() -> bool:
	return _phase == Phase.LIFTED


func alpha() -> float:
	return _rect.color.a


## True when every node and condition it waits for is done.
func work_done() -> bool:
	for ref in _nodes:
		var n := ref.get_ref() as Node
		if n != null and (not n.has_method(&"is_running") or bool(n.call(&"is_running"))):
			return false
	for c in _conditions:
		if c.is_valid() and not bool(c.call()):
			return false
	return true


func _process(delta: float) -> void:
	step(delta * MSEC_PER_SEC)


## Advances the card by one frame of `frame_ms` (tests call it directly). Returns true on the frame it opens.
func step(frame_ms: float) -> bool:
	match _phase:
		Phase.FADING_IN:
			_anim_sec += frame_ms / MSEC_PER_SEC
			_set_alpha(clampf(_anim_sec / fade_in_sec, 0.0, 1.0))
			if _anim_sec >= fade_in_sec:
				_phase = Phase.WAITING
				covered.emit()
		Phase.WAITING:
			if not _armed:
				return false
			_wait_frames += 1
			_wait_ms += frame_ms
			_max_frame_ms = maxf(_max_frame_ms, frame_ms)
			var done := work_done()
			if done or _wait_ms >= MAX_WAIT_MS:
				if not done:
					push_warning("%s: opened after %.0f ms with its work unfinished" % [LOG_PREFIX, _wait_ms])
				_open(done)
				return true
		Phase.LIFTING:
			_anim_sec += frame_ms / MSEC_PER_SEC
			_set_alpha(1.0 - clampf(_anim_sec / lift_sec, 0.0, 1.0))
			if _anim_sec >= lift_sec:
				_finish_lift()
	return false


## The wait's stats: frames and ms waited, its worst frame (all hidden, ADR 0029: 1 s each).
func wait_stats() -> Dictionary:
	return {"reveal_wait_frames": _wait_frames, "reveal_wait_ms": _wait_ms, "reveal_wait_max_frame_ms": _max_frame_ms}


func _open(done: bool) -> void:
	var stats := wait_stats()
	stats["reveal_work_done"] = done
	if is_instance_valid(_router) and _router.has_method(&"release_reveal"):
		_router.call(&"release_reveal", self)
	_router = null
	_anim_sec = 0.0
	_phase = Phase.LIFTING
	opened.emit(stats)
	if lift_sec <= 0.0:
		_finish_lift()


func _finish_lift() -> void:
	_set_alpha(0.0)
	_phase = Phase.LIFTED
	_rect.mouse_filter = Control.MOUSE_FILTER_IGNORE
	visible = false
	revealed.emit()


func _set_alpha(a: float) -> void:
	_rect.color.a = a
