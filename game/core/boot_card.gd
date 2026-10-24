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
## false) and wait_until(condition, progress). arm() starts the wait; before it, the card never opens, so work
## added a frame later (call_deferred) cannot be missed. Once everything is done (or the wait gives up, below),
## `opened` fires with the wait's stats and the card lifts over `lift_sec` (0: it is hidden at once, for a card
## under an opaque router fade); `revealed` fires when it has fully lifted. It stays in the tree, hidden, until
## its owner frees it.
##
## Reuse (M1-UI-11, a preset change on the title): cover(parent, SceneRouter.FADE_SEC); on `covered` start
## the warm-up and pass its node to wait_for_node(); arm(); on `opened` give the menu its input back and,
## to measure the reveal like a scene change, call SceneRouter.measure_reveal(path, card.is_lifted).
## hold_reveal_of(SceneRouter) keeps a router change from lifting its own fade until the card opens (boot
## does this when the title is reached through a SceneRouter change).
##
## Frames are wall time (M2-ARC-05): each _process frame is timed by `clock` (a FrameClock, Time.get_ticks_usec
## between frames), never by `delta`, which Godot caps at about 150 ms. So the wait's stats, its time-outs and the
## fade and lift run on real time, and a stall under the card shows at its true length.
##
## The wait gives up on a stall, not after a fixed time (M2-ARC-08). A first launch (ShaderPrewarm.first_run)
## took 9.5 s on Low on an RX 9070 XT, within 0.5 s of the old 10 s cap. `wait` (a ProgressWait, values from
## game/data/settings/boot_card.json) is fed each frame's wall ms and wait_progress(): the waited nodes'
## wait_progress() (a ShaderPrewarm counts its frames of work), the conditions' progress Callables, and how many
## items are done. The card opens unfinished only when that count has not moved for stall_timeout_ms, or after
## max_wait_ms in all. Then it first cancels the waited nodes that can be (ShaderPrewarm.cancel(): the stage is
## cleared and no first-run marker written, so the next launch tries again) and nothing stages under the title.
## On a first launch boot calls show_first_run_cue(): one quiet line and a thin bar of the warm-up's progress.

signal covered
signal opened(stats: Dictionary)
signal revealed

enum Phase { FADING_IN, WAITING, LIFTING, LIFTED }

## Just under SceneRouter's fade (FADE_LAYER 128), above every game and debug layer.
const LAYER := 127
const MSEC_PER_SEC := 1000.0
const LOG_PREFIX := "BootCard"
const END_DONE := "done"
const PROGRESS_METHOD := &"wait_progress"
const FRACTION_METHOD := &"progress_fraction"
const CANCEL_METHOD := &"cancel"

## Seconds the lift takes (0: hidden at once).
var lift_sec := 0.0
## Seconds the fade-in takes (0: opaque at once).
var fade_in_sec := 0.0
## Times each frame (M2-ARC-05); started when the card enters the tree. Tests swap in a fake clock.
var clock := FrameClock.new()
## When the wait gives up (M2-ARC-08): a stall, or the safety cap. Tests swap in their own values.
var wait := ProgressWait.from_settings()

var _rect: ColorRect
var _phase := Phase.WAITING
var _armed := false
var _nodes: Array[WeakRef] = []
var _conditions: Array[Callable] = []
var _condition_progress: Array[Callable] = []
var _router: Node
var _wait_frames := 0
var _wait_ms := 0.0
var _max_frame_ms := 0.0
var _anim_sec := 0.0
## The first-launch cue (null unless show_first_run_cue() was called).
var _cue: VBoxContainer
var _cue_fill: ColorRect
var _cue_settings: Dictionary = {}
var _cue_level := 0.0
var _cue_fraction := 0.0


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
	clock.reset()
	if fade_in_sec > 0.0:
		_phase = Phase.FADING_IN
		_set_alpha(0.0)
	else:
		_set_alpha(1.0)
		covered.emit.call_deferred()


## Waits until `node` is freed, or until its is_running() is false (a ShaderPrewarm). Null is done. A node with
## wait_progress() reports its progress (M2-ARC-08), one with cancel() is stopped if the wait gives up.
func wait_for_node(node: Node) -> void:
	if node != null:
		_nodes.append(weakref(node))


## Waits until `condition` returns true (a freed object's Callable counts as true). `progress` (optional) returns
## an int that changes while the work moves, so a slow condition is not taken for a stalled one (M2-ARC-08).
func wait_until(condition: Callable, progress: Callable = Callable()) -> void:
	_conditions.append(condition)
	_condition_progress.append(progress)


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
		if not _node_done(ref):
			return false
	for c in _conditions:
		if not _condition_done(c):
			return false
	return true


## The wait's progress count (M2-ARC-08): the waited nodes' wait_progress(), the conditions' progress Callables
## and the number of items done. It changes whenever any of the work moves; SceneRouter reads it while the card
## holds its reveal.
func wait_progress() -> int:
	var total := 0
	for ref in _nodes:
		var n := ref.get_ref() as Node
		if _node_done(ref):
			total += 1
		elif n.has_method(PROGRESS_METHOD):
			total += int(n.call(PROGRESS_METHOD))
	for i in _conditions.size():
		if _condition_done(_conditions[i]):
			total += 1
		elif _condition_progress[i].is_valid():
			total += int(_condition_progress[i].call())
	return total


## How far the reporting work is (0..1, the waited nodes' progress_fraction(); never goes back), for the cue.
func cue_fraction() -> float:
	var sum := 0.0
	var count := 0
	for ref in _nodes:
		var n := ref.get_ref() as Node
		if n != null and n.has_method(FRACTION_METHOD):
			sum += float(n.call(FRACTION_METHOD)) if not _node_done(ref) else 1.0
			count += 1
	if count > 0:
		_cue_fraction = maxf(_cue_fraction, clampf(sum / count, 0.0, 1.0))
	return _cue_fraction


## The first-launch cue (M2-ARC-08, pillar 1): one quiet line (boot_card.json cue.text_key) and a thin bar of the
## warm-up's progress near the bottom of the card. It fades in only after cue.delay_ms, so a quick first launch
## shows nothing, and lifts with the card. Boot calls it only when ShaderPrewarm.first_run is staging.
func show_first_run_cue(settings: Dictionary = {}) -> void:
	if _cue != null:
		return
	_cue_settings = settings if not settings.is_empty() else ProgressWait.load_settings().get("cue", {}) as Dictionary
	var s := _cue_settings
	_cue = VBoxContainer.new()
	_cue.name = "FirstRunCue"
	_cue.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_cue.alignment = BoxContainer.ALIGNMENT_END
	_cue.set_anchors_preset(Control.PRESET_FULL_RECT)
	_cue.offset_bottom = -float(s.get("bottom_margin_px", 0.0))
	_cue.add_theme_constant_override(&"separation", int(s.get("gap_px", 0.0)))
	_cue.modulate.a = 0.0
	var label := Label.new()
	label.name = "Note"
	label.text = tr(str(s.get("text_key", "")))
	label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	label.mouse_filter = Control.MOUSE_FILTER_IGNORE
	var ink := label.get_theme_color(&"font_color")
	label.modulate.a = float(s.get("text_alpha", 1.0))
	_cue.add_child(label)
	var track := ColorRect.new()
	track.name = "Bar"
	track.mouse_filter = Control.MOUSE_FILTER_IGNORE
	track.custom_minimum_size = Vector2(float(s.get("bar_width_px", 0.0)), float(s.get("bar_height_px", 0.0)))
	track.size_flags_horizontal = Control.SIZE_SHRINK_CENTER
	track.color = Color(ink, float(s.get("bar_track_alpha", 0.0)))
	_cue.add_child(track)
	_cue_fill = ColorRect.new()
	_cue_fill.name = "Fill"
	_cue_fill.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_cue_fill.color = Color(ink, float(s.get("bar_fill_alpha", 0.0)))
	_cue_fill.anchor_bottom = 1.0
	_cue_fill.anchor_right = 0.0
	track.add_child(_cue_fill)
	add_child(_cue)


## The cue (null when this launch shows none).
func cue() -> Control:
	return _cue


## How visible the cue is (0..1, before the card's own alpha).
func cue_level() -> float:
	return _cue_level


func _process(_delta: float) -> void:
	step(clock.lap())


## Advances the card by one frame of `frame_ms` wall ms (tests call it directly). Returns true on the frame it
## opens.
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
			if work_done():
				_open(END_DONE)
				return true
			var verdict := wait.step(frame_ms, wait_progress())
			if verdict != ProgressWait.Verdict.WAITING:
				var why := ProgressWait.verdict_name(verdict)
				push_warning(
					(
						"%s: opened after %.0f ms with its work unfinished (%s: no progress for %.0f ms)"
						% [LOG_PREFIX, _wait_ms, why, wait.stalled_ms]
					)
				)
				_cancel_work()
				_open(why)
				return true
			_update_cue()
		Phase.LIFTING:
			_anim_sec += frame_ms / MSEC_PER_SEC
			_set_alpha(1.0 - clampf(_anim_sec / lift_sec, 0.0, 1.0))
			if _anim_sec >= lift_sec:
				_finish_lift()
	return false


## The wait's stats: frames and ms waited, its worst frame (all hidden, ADR 0029: 1 s each).
func wait_stats() -> Dictionary:
	return {"reveal_wait_frames": _wait_frames, "reveal_wait_ms": _wait_ms, "reveal_wait_max_frame_ms": _max_frame_ms}


func _node_done(ref: WeakRef) -> bool:
	var n := ref.get_ref() as Node
	return n == null or (n.has_method(&"is_running") and not bool(n.call(&"is_running")))


func _condition_done(c: Callable) -> bool:
	return not c.is_valid() or bool(c.call())


## The wait gave up: stops the work that can be stopped, so nothing stages under the title once it shows.
func _cancel_work() -> void:
	for ref in _nodes:
		var n := ref.get_ref() as Node
		if n != null and not _node_done(ref) and n.has_method(CANCEL_METHOD):
			n.call(CANCEL_METHOD)


func _update_cue() -> void:
	if _cue == null:
		return
	var delay := float(_cue_settings.get("delay_ms", 0.0))
	var fade := maxf(float(_cue_settings.get("fade_in_ms", 0.0)), 1.0)
	_cue_level = clampf((_wait_ms - delay) / fade, 0.0, 1.0)
	_cue_fill.anchor_right = cue_fraction()
	_cue.modulate.a = _cue_level * _rect.color.a


func _open(end: String) -> void:
	var stats := wait_stats()
	stats["reveal_work_done"] = end == END_DONE
	stats["reveal_wait_end"] = end
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
	if _cue != null:
		_cue.modulate.a = _cue_level * a
