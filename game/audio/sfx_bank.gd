class_name SfxBank
extends Node
## Plays sfx.json rows (M2-AUD-02; docs/kb/tech/audio_runtime.md): a small pool of players per row (`voices`, the
## oldest is cut), a file picked per play that never repeats twice running, pitch jitter from a seeded generator
## (the same session plays the same sequence), and a cooldown that drops plays too close together.
## play_at() uses positional players for world sounds.

signal played(id: StringName, file: String)

const SEED := 20261024
const DEFAULT_VOICES := 4

## sfx.json's "sfx" rows.
var rows: Dictionary = {}
## Gain scale on every play (the reduced-audio setting; 1 = off).
var level := 1.0
## (now) -> int msec; tests replace it.
var clock: Callable = Time.get_ticks_msec
## Every play, in order: [id, file] (tests; cleared by tests).
var history: Array = []
var _rng := RandomNumberGenerator.new()
var _pools: Dictionary = {}
var _next: Dictionary = {}
var _last_file: Dictionary = {}
var _last_ms: Dictionary = {}
var _streams: Dictionary = {}


func _init(sfx_rows: Dictionary = {}) -> void:
	rows = sfx_rows
	_rng.seed = SEED


func has(id: StringName) -> bool:
	return rows.has(String(id))


## Plays row `id`. opts: volume_db (added), pitch (scale), bus (overrides the row's). Returns the player, or
## null when the row is unknown, every file is missing, or the cooldown drops it.
func play(id: StringName, opts: Dictionary = {}) -> AudioStreamPlayer:
	return _play(id, opts, false, Vector3.ZERO) as AudioStreamPlayer


## The same, from world position `at` (an AudioStreamPlayer3D on the row's bus).
func play_at(id: StringName, at: Vector3, opts: Dictionary = {}) -> AudioStreamPlayer3D:
	return _play(id, opts, true, at) as AudioStreamPlayer3D


func _play(id: StringName, opts: Dictionary, spatial: bool, at: Vector3) -> Node:
	var row := rows.get(String(id), {}) as Dictionary
	if row.is_empty():
		return null
	var now := int(clock.call())
	var cooldown := int(row.get("cooldown_ms", 0))
	if cooldown > 0 and _last_ms.has(id) and now - int(_last_ms[id]) < cooldown:
		return null
	var file := _pick(id, row)
	var stream := _stream(file)
	if stream == null:
		return null
	_last_ms[id] = now
	var p := _voice(id, row, spatial)
	p.set(&"stream", stream)
	p.set(&"bus", StringName(str(opts.get("bus", row.get("bus", "SFX")))))
	var lvl := level * float(opts.get("gain", 1.0))
	p.set(&"volume_db", float(row.get("volume_db", 0.0)) + float(opts.get("volume_db", 0.0)) + linear_to_db(lvl))
	var jitter := float(row.get("pitch_jitter", 0.0))
	var pitch := float(opts.get("pitch", 1.0)) * (1.0 + (_rng.randf_range(-jitter, jitter) if jitter > 0.0 else 0.0))
	p.set(&"pitch_scale", maxf(pitch, 0.01))
	if spatial:
		(p as AudioStreamPlayer3D).global_position = at
		(p as AudioStreamPlayer3D).unit_size = float(row.get("unit_size_m", 6.0))
	p.call(&"play")
	history.append([id, file])
	played.emit(id, file)
	return p


func _pick(id: StringName, row: Dictionary) -> String:
	var files: Array = row.get("files", [])
	if files.is_empty():
		return ""
	if files.size() == 1:
		return str(files[0])
	var i := _rng.randi_range(0, files.size() - 2)
	var last := str(_last_file.get(id, ""))
	var pick := str(files[i])
	if pick == last:
		pick = str(files[files.size() - 1])
	_last_file[id] = pick
	return pick


func _stream(path: String) -> AudioStream:
	if _streams.has(path):
		return _streams[path]
	var s: AudioStream = null
	if path != "" and ResourceLoader.exists(path):
		s = load(path) as AudioStream
	_streams[path] = s
	return s


func _voice(id: StringName, row: Dictionary, spatial: bool) -> Node:
	var key := "%s%s" % [id, "@3d" if spatial else ""]
	var pool: Array = _pools.get(key, [])
	var size := maxi(1, int(row.get("voices", DEFAULT_VOICES)))
	for p: Node in pool:
		if not bool(p.get(&"playing")):
			return p
	if pool.size() < size:
		var p: Node = AudioStreamPlayer3D.new() if spatial else AudioStreamPlayer.new()
		p.name = "%s_%d" % [key.replace("@", "_"), pool.size()]
		add_child(p)
		pool.append(p)
		_pools[key] = pool
		return p
	var n := int(_next.get(key, 0)) % pool.size()
	_next[key] = n + 1
	pool[n].call(&"stop")
	return pool[n]
