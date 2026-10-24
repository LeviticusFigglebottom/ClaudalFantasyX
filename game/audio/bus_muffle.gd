class_name BusMuffle
extends RefCounted
## Hearing the world through water (M3-AUD-22; docs/kb/tech/audio_runtime.md "Reefball"): a low-pass on mix.json
## `muffle.buses`, ramped. Callers name a reason (Reefball's sphere is `underwater`); while any reason is on, each bus's
## AudioEffectLowPassFilter glides (in log frequency, over `ramp_sec`) to `cutoff_hz`, and back to `open_hz` when the
## last reason goes, after which the effects are switched off. The Music bus is left out on purpose: the score is not
## in the water. Time passes only through advance(delta) (AudioDirector.advance; tests call it directly).

## mix.json `muffle`.
var cfg: Dictionary = {}
## The reasons on now.
var reasons: Dictionary = {}
## The cutoff now (Hz).
var cutoff := 0.0
var _from := 0.0
var _to := 0.0
var _t := 0.0


## Reads mix.json and puts a (switched-off) low-pass on each of its buses, reusing one that is already there.
func configure(mix_table: Dictionary) -> void:
	cfg = mix_table.get("muffle", {}) as Dictionary
	cutoff = open_hz()
	_to = cutoff
	_from = cutoff
	for bus in buses():
		effect_on(bus, true)
	_write()


func buses() -> Array[StringName]:
	var out: Array[StringName] = []
	for b: Variant in cfg.get("buses", []):
		out.append(StringName(str(b)))
	return out


func open_hz() -> float:
	return float(cfg.get("open_hz", 20000.0))


func is_muffled() -> bool:
	return not reasons.is_empty()


## Turns `reason` on or off; the cutoff ramps toward the new target from where it is.
func set_reason(reason: StringName, on: bool) -> void:
	var was := is_muffled()
	if on:
		reasons[reason] = true
	else:
		reasons.erase(reason)
	if was == is_muffled():
		return
	_from = cutoff
	_to = float(cfg.get("cutoff_hz", open_hz())) if is_muffled() else open_hz()
	_t = 0.0


func advance(delta: float) -> void:
	if is_equal_approx(cutoff, _to):
		return
	var sec := float(cfg.get("ramp_sec", 0.0))
	_t += delta
	var u := 1.0 if sec <= 0.0 else clampf(_t / sec, 0.0, 1.0)
	cutoff = exp(lerpf(log(maxf(_from, 1.0)), log(maxf(_to, 1.0)), u))
	if u >= 1.0:
		cutoff = _to
	_write()


## The bus's AudioEffectLowPassFilter (added when `make` and missing; null when the bus does not exist).
static func effect_on(bus: StringName, make: bool = false) -> AudioEffectLowPassFilter:
	var idx := AudioServer.get_bus_index(bus)
	if idx < 0:
		return null
	for i in AudioServer.get_bus_effect_count(idx):
		var fx := AudioServer.get_bus_effect(idx, i)
		if fx is AudioEffectLowPassFilter:
			return fx as AudioEffectLowPassFilter
	if not make:
		return null
	var made := AudioEffectLowPassFilter.new()
	AudioServer.add_bus_effect(idx, made)
	AudioServer.set_bus_effect_enabled(idx, AudioServer.get_bus_effect_count(idx) - 1, false)
	return made


func _write() -> void:
	var on := cutoff < open_hz() - 1.0
	for bus in buses():
		var fx := effect_on(bus)
		if fx == null:
			continue
		fx.cutoff_hz = cutoff
		fx.resonance = float(cfg.get("resonance", fx.resonance))
		var idx := AudioServer.get_bus_index(bus)
		for i in AudioServer.get_bus_effect_count(idx):
			if AudioServer.get_bus_effect(idx, i) == fx:
				AudioServer.set_bus_effect_enabled(idx, i, on)
