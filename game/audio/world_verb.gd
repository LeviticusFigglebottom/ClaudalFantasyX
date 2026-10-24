class_name WorldVerb
extends RefCounted
## The area reverb on the World and Combat buses (M2-AUD-10; docs/kb/audio/mix.md §7; audio_runtime.md "Reverb").
## mix.md §4 planned one WorldVerb bus, but a Godot bus sends to one bus only, so World and Combat each carry their
## own AudioEffectReverb, and both follow the same preset. mix.json `reverb` names the buses, the default preset
## (a scene whose zone row names none) and the ramp; `reverb_presets` holds each preset's effect parameters. A zone
## row's `reverb` key picks the preset (AudioDirector.apply_zone). A change ramps every parameter linearly over
## `ramp_sec`; a preset with no wet signal switches the effects off once the ramp has reached it.

## The AudioEffectReverb properties a preset sets (a missing one keeps the effect's default).
const PARAMS: Array[StringName] = [
	&"room_size", &"damping", &"spread", &"hipass", &"dry", &"wet", &"predelay_msec", &"predelay_feedback"
]

## mix.json's `reverb` and `reverb_presets`.
var cfg: Dictionary = {}
var presets: Dictionary = {}
## The preset applied last (its target), and the parameters now.
var preset: StringName = &""
var now: Dictionary = {}
var _from: Dictionary = {}
var _to: Dictionary = {}
var _sec := 0.0
var _t := 0.0


## Reads mix.json and puts a reverb on each of its buses (reusing one that is already there).
func configure(mix_table: Dictionary) -> void:
	cfg = mix_table.get("reverb", {}) as Dictionary
	presets = mix_table.get("reverb_presets", {}) as Dictionary
	for bus in buses():
		effect_on(bus, true)


## The buses that carry the reverb.
func buses() -> Array[StringName]:
	var out: Array[StringName] = []
	for b: Variant in cfg.get("buses", []):
		out.append(StringName(str(b)))
	return out


## The preset a zone row asks for: its `reverb` key, else the default.
func preset_for(zone_row: Dictionary) -> StringName:
	return StringName(str(zone_row.get("reverb", cfg.get("default", ""))))


## The bus's AudioEffectReverb (added when `make` and missing; null when the bus does not exist).
static func effect_on(bus: StringName, make: bool = false) -> AudioEffectReverb:
	var idx := AudioServer.get_bus_index(bus)
	if idx < 0:
		return null
	for i in AudioServer.get_bus_effect_count(idx):
		var fx := AudioServer.get_bus_effect(idx, i)
		if fx is AudioEffectReverb:
			return fx as AudioEffectReverb
	if not make:
		return null
	var made := AudioEffectReverb.new()
	made.wet = 0.0
	made.dry = 1.0
	AudioServer.add_bus_effect(idx, made)
	AudioServer.set_bus_effect_enabled(idx, AudioServer.get_bus_effect_count(idx) - 1, false)
	return made


## Ramps to preset `id` over `sec` (< 0: the cfg's ramp_sec). False for an unknown preset (nothing changes).
func apply(id: StringName, sec: float = -1.0) -> bool:
	if not presets.has(String(id)):
		return false
	var target := presets[String(id)] as Dictionary
	preset = id
	_from = read_params()
	_to = {}
	for p in PARAMS:
		_to[p] = float(target.get(String(p), _from[p]))
	_sec = float(cfg.get("ramp_sec", 0.0)) if sec < 0.0 else sec
	_t = 0.0
	_set_enabled(true)
	if _sec <= 0.0:
		_write(1.0)
	return true


## Ends a running ramp where it is (tests that share the buses with the game's own director).
func stop() -> void:
	_to = {}


## True while a ramp is running.
func is_ramping() -> bool:
	return not _to.is_empty()


## Moves the ramp on by `delta` seconds (AudioDirector.advance). Writes nothing when no ramp runs, so a caller's own
## settings stand.
func advance(delta: float) -> void:
	if _to.is_empty():
		return
	_t += delta
	_write(1.0 if _sec <= 0.0 else clampf(_t / _sec, 0.0, 1.0))


## The first bus's effect parameters (the defaults of a new effect when there is none).
func read_params() -> Dictionary:
	var fx: AudioEffectReverb = null
	for bus in buses():
		fx = effect_on(bus)
		if fx != null:
			break
	if fx == null:
		fx = AudioEffectReverb.new()
	var out: Dictionary = {}
	for p in PARAMS:
		out[p] = float(fx.get(p))
	return out


func _write(u: float) -> void:
	now = {}
	for p in PARAMS:
		now[p] = lerpf(float(_from[p]), float(_to[p]), u)
	for bus in buses():
		var fx := effect_on(bus)
		if fx == null:
			continue
		for p in PARAMS:
			fx.set(p, now[p])
	if u >= 1.0:
		_to = {}
		if float(now[&"wet"]) <= 0.0:
			_set_enabled(false)


func _set_enabled(on: bool) -> void:
	for bus in buses():
		var idx := AudioServer.get_bus_index(bus)
		if idx < 0:
			continue
		for i in AudioServer.get_bus_effect_count(idx):
			if AudioServer.get_bus_effect(idx, i) is AudioEffectReverb:
				AudioServer.set_bus_effect_enabled(idx, i, on)
