class_name GlimmerState
extends RefCounted
## Glimmer behaviour state machine (M1-RND-02). Pure: no nodes, no rendering, so it is unit-tested
## headlessly. GlimmerField owns one and feeds its two outputs to the particle shader:
##   release_blend   0 = held (cyan, sideways/down), 1 = released (gold, rising)
##   machine_amount  1 = bound (teal, perfectly still), 0 = free
## Meaning rules: docs/kb/art/color_script.md, narrative light rules 1-2. Docs: docs/kb/tech/glimmer.md.
##
## Transitions:
##   set_mode(m)       immediate; cancels a release in progress
##   release(duration) held or machine -> released, eased over duration (the 1.5 s release lerp);
##                     mode reads RELEASED from the first frame, is_releasing() until it completes
##   advance(delta)    steps a release; call once per frame

signal mode_changed(mode: Mode)
signal release_started(duration_s: float)
signal release_finished

enum Mode { HELD, RELEASED, MACHINE }

var mode: Mode = Mode.HELD
var release_blend: float = 0.0
var machine_amount: float = 0.0

var _releasing: bool = false
var _elapsed_s: float = 0.0
var _duration_s: float = 0.0
var _from_blend: float = 0.0
var _from_machine: float = 0.0


func _init(initial_mode: Mode = Mode.HELD) -> void:
	_snap(initial_mode)


## Switches immediately. Emits mode_changed only when the mode actually changes.
func set_mode(new_mode: Mode) -> void:
	var was_releasing := _releasing
	var changed := new_mode != mode
	_snap(new_mode)
	if was_releasing and new_mode == Mode.RELEASED:
		release_finished.emit()
	if changed:
		mode_changed.emit(mode)


## Starts the held -> released transition. Returns false (and does nothing) when the motes are
## already released or releasing. A duration <= 0 releases on the spot.
func release(duration_s: float) -> bool:
	if mode == Mode.RELEASED:
		return false
	_from_blend = release_blend
	_from_machine = machine_amount
	mode = Mode.RELEASED
	release_started.emit(maxf(duration_s, 0.0))
	mode_changed.emit(mode)
	if duration_s <= 0.0:
		_snap(Mode.RELEASED)
		release_finished.emit()
		return true
	_releasing = true
	_elapsed_s = 0.0
	_duration_s = duration_s
	return true


func advance(delta_s: float) -> void:
	if not _releasing:
		return
	_elapsed_s = minf(_elapsed_s + maxf(delta_s, 0.0), _duration_s)
	var eased := smoothstep(0.0, 1.0, release_progress())
	release_blend = lerpf(_from_blend, 1.0, eased)
	machine_amount = lerpf(_from_machine, 0.0, eased)
	if _elapsed_s >= _duration_s:
		_snap(Mode.RELEASED)
		release_finished.emit()


func is_releasing() -> bool:
	return _releasing


## Linear progress of the current release in [0, 1]; 1 when released, 0 otherwise.
func release_progress() -> float:
	if _releasing:
		return clampf(_elapsed_s / _duration_s, 0.0, 1.0)
	return 1.0 if mode == Mode.RELEASED else 0.0


## Transition endpoints for the particle shader, which staggers the release per mote (a wave from
## the release origin) while keeping the field-wide timing: {blend_from, blend_to, machine_from,
## machine_to, progress}. Outside a release from == to and progress is 1.
func shader_state() -> Dictionary:
	if _releasing:
		return {
			"blend_from": _from_blend,
			"blend_to": 1.0,
			"machine_from": _from_machine,
			"machine_to": 0.0,
			"progress": release_progress(),
		}
	return {
		"blend_from": release_blend,
		"blend_to": release_blend,
		"machine_from": machine_amount,
		"machine_to": machine_amount,
		"progress": 1.0,
	}


## The colour the motes show right now (linear blend; the shader blends in Oklab). For CPU-side
## consumers such as the fill light. Inputs are the palette colours for each mode.
func blend_color(held: Color, released: Color, machine: Color) -> Color:
	return held.lerp(released, release_blend).lerp(machine, machine_amount)


static func mode_from_name(mode_name: String) -> int:
	var key := mode_name.to_upper()
	return Mode[key] if Mode.has(key) else -1


static func mode_name(value: Mode) -> String:
	return String(Mode.find_key(value)).to_lower()


func _snap(new_mode: Mode) -> void:
	_releasing = false
	_elapsed_s = 0.0
	_duration_s = 0.0
	mode = new_mode
	release_blend = 1.0 if new_mode == Mode.RELEASED else 0.0
	machine_amount = 1.0 if new_mode == Mode.MACHINE else 0.0
