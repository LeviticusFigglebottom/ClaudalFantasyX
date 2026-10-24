class_name LipSync
extends RefCounted
## Text-driven lip sync for one speaking face (M2-CHR-10; docs/kb/tech/cutscenes.md, "Faces").
## Headless and deterministic: no nodes, no global randomness. Tables and every curve constant:
## game/data/cutscene/lipsync.json (its "doc" explains each key).
##
##   start(text, cps, emotion, seed, reveal_times)  FaceVisemes turns the text into viseme segments,
##       timed to the DialogueBox reveal: character i spans i / cps .. (i + 1) / cps s, or, given
##       the box's reveal_times() (M2-UI-27), the span ending when the box shows it, so the mouth
##       rests while the reveal lingers at punctuation (starts_for). The segments are blended
##       by dominance (co-articulation: neighbours shape each other; bilabials and pauses dominate;
##       rounding is anticipated), sampled at sample_hz, scaled by the emotion's intensity and
##       slew-limited per shape, so no weight ever moves faster than max_rate_per_s and every
##       closure is still reached on time. The curve ends at rest tail_s after the last character.
##   advance(delta), weights()  the shapes now (blend shape name -> weight), idle drift included.
##   stop()  the reveal was skipped: release toward rest at release_per_s from where the mouth is.

const CONFIG_PATH := "res://game/data/cutscene/lipsync.json"
const DEFAULT_KEY := "default"

var cfg: Dictionary = {}

var _segments: Array[Dictionary] = []
## When each character position starts speaking (s, before lead_s); see starts_for.
var _starts := PackedFloat64Array()
## blend shape -> PackedFloat32Array of the slew-limited curve, one sample per 1 / sample_hz s.
var _curves: Dictionary = {}
var _dt := 0.0
var _t := 0.0
var _speech_end := 0.0
var _end := 0.0
var _playing := false
var _released := false
var _held: Dictionary = {}
var _idle_env := 0.0
var _idle_phase: PackedFloat32Array = PackedFloat32Array()
var _rng := RandomNumberGenerator.new()


static func load_config() -> Dictionary:
	var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(CONFIG_PATH))
	if not parsed is Dictionary:
		push_error("LipSync: cannot read %s" % CONFIG_PATH)
		return {}
	return parsed


func _init(config: Dictionary) -> void:
	cfg = config


## Every blend shape some viseme names (a rig needs them all for lip sync).
func viseme_shapes() -> Array[StringName]:
	var out: Array[StringName] = []
	for row: Variant in (cfg.get("shapes", {}) as Dictionary).values():
		for shape: Variant in (row as Dictionary).keys():
			if not out.has(StringName(str(shape))):
				out.append(StringName(str(shape)))
	return out


## The line's emotion tag -> its mouth intensity ("default" for none or an unlisted tag).
static func intensity_for(emotion: StringName, config: Dictionary) -> float:
	var table: Dictionary = config.get("intensity", {})
	return float(table.get(String(emotion), table.get(DEFAULT_KEY, 1.0)))


## The time (s, before lead_s) each character position x in 0..n starts speaking, for a text of
## `n` characters revealed at `cps`. Without `reveal_times` that is x / cps. With the box's
## reveal_times (DialogueBox.reveal_times(): when each character shows, punctuation pauses included,
## M2-UI-27) character x spans the 1 / cps before it shows, and position n is the last reveal.
static func starts_for(
	n: int, cps: float, reveal_times: PackedFloat64Array = PackedFloat64Array()
) -> PackedFloat64Array:
	var out := PackedFloat64Array()
	var timed := reveal_times.size() >= n and n > 0
	for x in n + 1:
		if not timed:
			out.append(float(x) / cps)
		elif x < n:
			out.append(reveal_times[x] - 1.0 / cps)
		else:
			out.append(reveal_times[n - 1])
	return out


func start(
	text: String,
	cps: float,
	emotion: StringName,
	rng_seed: int,
	reveal_times: PackedFloat64Array = PackedFloat64Array()
) -> void:
	_segments = FaceVisemes.segments(text, cfg)
	_curves = {}
	_t = 0.0
	_released = false
	_held = {}
	_idle_env = 0.0
	_playing = cps > 0.0 and not text.is_empty()
	if not _playing:
		return
	var hz := float(cfg.get("sample_hz", 0.0))
	_dt = 1.0 / maxf(hz, 1.0)
	_starts = starts_for(text.length(), cps, reveal_times)
	_speech_end = _starts[_starts.size() - 1] + float(cfg.get("lead_s", 0.0))
	_end = _speech_end + float(cfg.get("tail_s", 0.0))
	var count := ceili(_end / _dt) + 1
	var intensity := intensity_for(emotion, cfg)
	var samples: Array[Dictionary] = []
	for k in count:
		samples.append(blend_at(_segments, k * _dt, cps, cfg, _starts))
	var rates: Dictionary = cfg.get("max_rate_per_s", {})
	var peaks: Array = cfg.get("peak_shapes", [])
	for shape in viseme_shapes():
		# Packed arrays are values: fill a local one, then store it.
		var arr := PackedFloat32Array()
		arr.resize(count)
		for k in range(1, count - 1):  # the first and last samples stay at rest
			arr[k] = float(samples[k].get(shape, 0.0)) * intensity
		var rate := float(rates.get(String(shape), rates.get(DEFAULT_KEY, 0.0)))
		if peaks.has(String(shape)):
			arr = slew_limit_peaks(arr, rate * _dt)
			arr[0] = 0.0  # the line still starts and ends at rest
			arr[count - 1] = 0.0
		_curves[shape] = slew_limit(arr, rate * _dt)
	_rng.seed = rng_seed
	_idle_phase = PackedFloat32Array()
	for row: Variant in cfg.get("idle", []):
		_idle_phase.append(_rng.randf() * TAU)


## The co-articulated shapes at time `t` (s) for `segs` revealed at `cps`, before intensity and
## the slew limit: a dominance-weighted average of the segments' viseme rows, with base_rest as a
## constant pull to rest.
static func blend_at(
	segs: Array[Dictionary], t: float, cps: float, config: Dictionary, starts: PackedFloat64Array = PackedFloat64Array()
) -> Dictionary:
	var lead := float(config.get("lead_s", 0.0))
	var cutoff := float(config.get("cutoff_tau", 0.0))
	var dominance: Dictionary = config.get("dominance", {})
	var shapes: Dictionary = config.get("shapes", {})
	var num := {}
	var den := float(config.get("base_rest", 0.0))
	for s in segs:
		var v := String(s["v"])
		var dom: Dictionary = dominance.get(v, {})
		var start := _at(float(s["at"]), cps, starts) + lead
		var end := _at(float(s["at"]) + float(s["len"]), cps, starts) + lead
		var d := 0.0
		var tau := 1.0
		if t < start:
			d = start - t
			tau = float(dom.get("ahead", 0.0))
		elif t > end:
			d = t - end
			tau = float(dom.get("behind", 0.0))
		if d > 0.0 and (tau <= 0.0 or d > cutoff * tau):
			continue
		var weight := float(dom.get("a", 0.0)) * (exp(-d / tau) if d > 0.0 else 1.0)
		den += weight
		var row: Dictionary = shapes.get(v, {})
		for shape: Variant in row.keys():
			var key := StringName(str(shape))
			num[key] = float(num.get(key, 0.0)) + weight * float(row[shape])
	var out := {}
	if den <= 0.0:
		return out
	for key: StringName in num.keys():
		out[key] = float(num[key]) / den
	return _close(out, segs, t, cps, config, starts)


## Lip closures (bilabials, labiodentals) must land, whatever their neighbours ask: near the
## strongest closure segment the blend is pulled onto that viseme's row by
## closures[v] * exp(-d / closure_tau) (1 at full strength inside the segment), so the jaw and every
## other shape go to 0 there.
static func _close(
	w: Dictionary, segs: Array[Dictionary], t: float, cps: float, config: Dictionary, starts: PackedFloat64Array
) -> Dictionary:
	var closures: Dictionary = config.get("closures", {})
	var tau := float(config.get("closure_tau", 0.0))
	var lead := float(config.get("lead_s", 0.0))
	var best := 0.0
	var best_v := ""
	for s in segs:
		var v := String(s["v"])
		if not closures.has(v):
			continue
		var start := _at(float(s["at"]), cps, starts) + lead
		var end := _at(float(s["at"]) + float(s["len"]), cps, starts) + lead
		var d := maxf(0.0, maxf(start - t, t - end))
		if d > 0.0 and tau <= 0.0:
			continue
		var k := float(closures[v]) * (exp(-d / tau) if d > 0.0 else 1.0)
		if k > best:
			best = k
			best_v = v
	if best <= 0.0:
		return w
	var row: Dictionary = (config.get("shapes", {}) as Dictionary).get(best_v, {})
	var out := {}
	for key: StringName in w.keys():
		out[key] = float(w[key]) * (1.0 - best)
	for shape: Variant in row.keys():
		var key := StringName(str(shape))
		out[key] = lerpf(float(w.get(key, 0.0)), float(row[shape]), best)
	return out


## The time of character position `x` (a segment edge; fractional inside a character): x / cps,
## or with `starts` (starts_for) the start of character floor(x) plus the fraction at 1 / cps, so
## the pause the reveal holds after a character stays outside every segment that ends there.
static func _at(x: float, cps: float, starts: PackedFloat64Array) -> float:
	if starts.is_empty():
		return x / cps
	var i := clampi(floori(x), 0, starts.size() - 1)
	if i >= starts.size() - 1:
		return starts[starts.size() - 1]
	return starts[i] + minf((x - float(i)) / cps, starts[i + 1] - starts[i])


## `x` limited to `step` per sample in both directions, never above `x`: a backward pass lets
## every low point (a closure, the final rest) be reached by starting the descent early, and a
## forward pass limits each rise. Peaks too short for the limit simply open less.
static func slew_limit(x: PackedFloat32Array, step: float) -> PackedFloat32Array:
	var n := x.size()
	var y := x.duplicate()
	if n == 0 or step <= 0.0:
		return y
	for i in range(n - 2, -1, -1):
		y[i] = minf(y[i], y[i + 1] + step)
	for i in range(1, n):
		y[i] = minf(y[i], y[i - 1] + step)
	return y


## The mirror of slew_limit for shapes that must reach their peaks (a lip closure): never below
## `x`, so the rise starts early (look-ahead) and the fall comes late.
static func slew_limit_peaks(x: PackedFloat32Array, step: float) -> PackedFloat32Array:
	var neg := PackedFloat32Array()
	for v in x:
		neg.append(-v)
	var lim := slew_limit(neg, step)
	var out := PackedFloat32Array()
	for v in lim:
		out.append(-v)
	return out


func advance(delta: float) -> void:
	if not _playing:
		return
	_t += delta
	var fade := maxf(float(cfg.get("idle_fade_s", 0.0)), delta)
	if _t < _speech_end and not _released:
		_idle_env = minf(1.0, _idle_env + delta / fade)
	else:
		_idle_env = maxf(0.0, _idle_env - delta / fade)
	var resting := _t >= _end
	if _released:
		var step := float(cfg.get("release_per_s", 0.0)) * delta
		resting = true
		for shape: StringName in _held.keys():
			_held[shape] = move_toward(float(_held[shape]), 0.0, step)
			resting = resting and float(_held[shape]) <= 0.0
	if resting and _idle_env <= 0.0:
		_playing = false


## The reveal was cut short: let go of the line from where the mouth is now. Within `grace` s of
## the line's natural end (the box and the face step in either order within a frame) it plays on.
func stop(grace: float = 0.0) -> void:
	if _playing and not _released and _t + grace < _speech_end:
		_held = _sample(_t)
		_released = true


func is_active() -> bool:
	return _playing


func segments() -> Array[Dictionary]:
	return _segments


## Seconds since start().
func time_s() -> float:
	return _t


## Seconds from the line's start to its last character's reveal.
func speech_end_s() -> float:
	return _speech_end


## blend shape -> weight now (viseme curve plus idle drift).
func weights() -> Dictionary:
	if not _playing:
		return {}
	var out: Dictionary = _held.duplicate() if _released else _sample(_t)
	var rows: Array = cfg.get("idle", [])
	for i in mini(rows.size(), _idle_phase.size()):
		var row: Dictionary = rows[i]
		var shape := StringName(str(row.get("shape", "")))
		var wave := 0.5 + 0.5 * sin(TAU * float(row.get("hz", 0.0)) * _t + _idle_phase[i])
		out[shape] = float(out.get(shape, 0.0)) + float(row.get("amp", 0.0)) * wave * _idle_env
	return out


func _sample(t: float) -> Dictionary:
	var out := {}
	var f := t / _dt
	var k := floori(f)
	for shape: StringName in _curves.keys():
		var arr: PackedFloat32Array = _curves[shape]
		if k < 0 or k >= arr.size() - 1:
			out[shape] = 0.0
			continue
		out[shape] = lerpf(arr[k], arr[k + 1], f - k)
	return out
