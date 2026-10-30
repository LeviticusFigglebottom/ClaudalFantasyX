class_name MusicDeck
extends Node
## The music bed (M2-AUD-02; docs/kb/tech/audio_runtime.md): two players that crossfade, stems that fade in and
## out inside one synchronized stream (the Drownbell's phase 2), a resume point per cue, and a hold that silences
## the bed while something else (a cutscene) owns the music. Time passes only through advance(delta).
## Changes land on the beat (M3-AUD-864): a new cue or a stop with a fade waits for the next beat of the cue sounding
## (grid_of: the row's `beat`, else its file's .loop.json), so the old cue fades from a beat and the new one enters on it; a resumed cue picks
## up on a beat of its own. A beat longer than beat_max_wait_sec is halved until it fits, so no change waits longer.

signal cue_started(cue: StringName)

const SLOTS := 2
## A wait shorter than this is no wait (the change lands now).
const BEAT_EPS := 0.02

## The cue playing (or fading in) now; &"" for none.
var current: StringName = &""
## Fades below this level count as silence (mix.json music.floor_db).
var floor_db := -60.0
## 0..1: the hold. 0 while a cutscene owns the music.
var hold := 1.0
## Where each resumable cue stopped (seconds).
var positions: Dictionary = {}
## mix.json music.beat_sync_max_wait_sec; 0 changes at once (no beat sync).
var beat_max_wait_sec := 0.0
## (slot's player) -> its playback position in seconds; tests replace it. Default: the player's own position.
var position_source := Callable()
## Where the last cue started (seconds into it).
var started_from := 0.0
var _slots: Array[FadeVoice] = []
var _rows: Dictionary = {}
var _hold_target := 1.0
var _hold_rate := 0.0
## Per-stem fades of the current cue: [gain, target, rate].
var _stems: Array = []
var _bus: StringName = &"Music"
## A change waiting for its beat: {cue (&"" for a stop), stream, sec, left}; {} when none.
var _queued: Dictionary = {}
## Each cue's beat grid (grid_of), cached.
var _grids: Dictionary = {}


func _init(bus: StringName = &"Music") -> void:
	_bus = bus
	for i in SLOTS:
		var p := AudioStreamPlayer.new()
		p.name = "Slot%d" % i
		p.bus = bus
		add_child(p)
		_slots.append(FadeVoice.new(p))


## Plays cue `cue_id` (row from music.json) with a crossfade of `sec`. The same cue playing already is left be.
## Returns false when the row names no stream that loads.
## A fade of 0 or less changes at once; any other waits for the beat (wait_for_beat), while `current` already names
## the new cue.
func play(cue_id: StringName, row: Dictionary, sec: float) -> bool:
	if cue_id == current and (_active() != null or _queued.get("cue", &"") == cue_id):
		return true
	if not _queued.is_empty() and _sounding() != null and _sounding().id == cue_id:
		_queued = {}  # back to the cue still sounding before the change landed: it simply carries on
		current = cue_id
		return true
	var stream := build_stream(row)
	if stream == null:
		return false
	_rows[cue_id] = row
	current = cue_id
	_stems = []
	if stream is AudioStreamSynchronized:
		var on: Array = row.get("start_stems", [0])
		for i in (stream as AudioStreamSynchronized).stream_count:
			var g := 1.0 if on.has(i) else 0.0
			_stems.append([g, g, 0.0])
	var wait := wait_for_beat(sec)
	if wait > 0.0:
		_queued = {"cue": cue_id, "stream": stream, "sec": sec, "left": wait}
		return true
	_queued = {}
	_start(cue_id, stream, sec)
	return true


func _start(cue_id: StringName, stream: AudioStream, sec: float) -> void:
	var row := _rows.get(cue_id, {}) as Dictionary
	_fade_out_all(sec)
	var slot := _free_slot()
	var p := slot.player as AudioStreamPlayer
	p.stream = stream
	slot.id = cue_id
	slot.base_db = float(row.get("volume_db", 0.0))
	slot.gain = 0.0 if sec > 0.0 else 1.0
	slot.fade_to(1.0, sec)
	var from := float(positions.get(cue_id, 0.0)) if bool(row.get("resume", false)) else 0.0
	positions.erase(cue_id)
	var grid := beat_grid(cue_id)
	if from > 0.0 and not grid.is_empty():  # pick up on a beat of its own
		var off := float(grid["offset"])
		from = maxf(0.0, off + floorf((from - off) / float(grid["beat"])) * float(grid["beat"]))
	started_from = from
	p.play(from)
	_apply_stems()
	slot.step(0.0, floor_db, hold)
	cue_started.emit(cue_id)


## Seconds until the next beat of the cue sounding now, the beat halved until it is at most beat_max_wait_sec.
## 0 (change now) for an immediate change (sec <= 0), with beat sync off, while the bed is held silent, or when
## nothing sounds or the sounding cue has no beat grid.
func wait_for_beat(sec: float) -> float:
	if sec <= 0.0 or beat_max_wait_sec <= 0.0 or hold <= BEAT_EPS:
		return 0.0
	var s := _sounding()
	if s == null:
		return 0.0
	var grid := beat_grid(s.id)
	if grid.is_empty():
		return 0.0
	var beat := float(grid["beat"])
	while beat > beat_max_wait_sec:
		beat *= 0.5
	var p := s.player as AudioStreamPlayer
	var pos := float(position_source.call(p)) if position_source.is_valid() else p.get_playback_position()
	var wait := beat - fposmod(pos - float(grid["offset"]), beat)
	return 0.0 if wait < BEAT_EPS or wait > beat - BEAT_EPS else wait


## The beat grid of cue `cue_id` (a row this deck has played), cached: grid_of its row.
func beat_grid(cue_id: StringName) -> Dictionary:
	if not _grids.has(cue_id):
		_grids[cue_id] = grid_of(_rows.get(cue_id, {}) as Dictionary)
	return _grids[cue_id]


## A cue row's beat grid, {beat, offset} seconds: from the row's `beat` ({bpm, downbeat_offset_s}; "free" for an
## unmetered piece, which has none), else its first file's .loop.json; {} when neither gives a tempo.
static func grid_of(row: Dictionary) -> Dictionary:
	var meta: Variant = row.get("beat", null)
	var files := AudioData.cue_files(row)
	if meta == null and not files.is_empty():
		var path := files[0].get_basename() + ".loop.json"
		if FileAccess.file_exists(path):
			meta = JSON.parse_string(FileAccess.get_file_as_string(path))
	if meta is Dictionary and float((meta as Dictionary).get("bpm", 0.0)) > 0.0:
		var m := meta as Dictionary
		return {"beat": 60.0 / float(m["bpm"]), "offset": float(m.get("downbeat_offset_s", 0.0))}
	return {}


## A change waiting for its beat: the cue (&"" for a stop), else &"" when none waits.
func queued_cue() -> StringName:
	return StringName(_queued.get("cue", &""))


func has_queued() -> bool:
	return not _queued.is_empty()


## Fades the bed out over `sec`.
func stop(sec: float) -> void:
	current = &""
	var wait := wait_for_beat(sec)
	if wait > 0.0:
		_queued = {"cue": &"", "stream": null, "sec": sec, "left": wait}
		return
	_queued = {}
	_fade_out_all(sec)


## Brings stem `index` of the current cue in (on) or out over `sec`.
func set_stem(index: int, on: bool, sec: float) -> void:
	if index < 0 or index >= _stems.size():
		return
	var s: Array = _stems[index]
	s[1] = 1.0 if on else 0.0
	s[2] = 0.0 if sec <= 0.0 else absf(float(s[1]) - float(s[0])) / sec
	if sec <= 0.0:
		s[0] = s[1]
	_apply_stems()


## A stem's gain now (0..1); -1 when the cue has no such stem.
func stem_gain(index: int) -> float:
	return float((_stems[index] as Array)[0]) if index >= 0 and index < _stems.size() else -1.0


## Holds the bed silent (on) or lets it back (off) over `sec`.
func set_hold(on: bool, sec: float) -> void:
	_hold_target = 0.0 if on else 1.0
	_hold_rate = 0.0 if sec <= 0.0 else absf(_hold_target - hold) / sec
	if sec <= 0.0:
		hold = _hold_target


func is_held() -> bool:
	return _hold_target <= 0.0


## The playing slot's linear gain (0 when nothing plays).
func gain() -> float:
	var s := _active()
	return s.gain if s != null else 0.0


func player() -> AudioStreamPlayer:
	var s := _active()
	return s.player as AudioStreamPlayer if s != null else null


func advance(delta: float) -> void:
	if not _queued.is_empty():
		_queued["left"] = float(_queued["left"]) - delta
		if float(_queued["left"]) <= 0.0:
			var q := _queued
			_queued = {}
			if StringName(q["cue"]) == &"":
				_fade_out_all(float(q["sec"]))
			else:
				_start(StringName(q["cue"]), q["stream"] as AudioStream, float(q["sec"]))
	if hold != _hold_target:
		hold = _hold_target if _hold_rate <= 0.0 else move_toward(hold, _hold_target, _hold_rate * delta)
	for s: Array in _stems:
		if float(s[0]) != float(s[1]):
			s[0] = s[1] if float(s[2]) <= 0.0 else move_toward(float(s[0]), float(s[1]), float(s[2]) * delta)
	_apply_stems()
	for slot in _slots:
		var was_playing := (slot.player as AudioStreamPlayer).playing
		slot.step(delta, floor_db, hold)
		if was_playing and not (slot.player as AudioStreamPlayer).playing:
			slot.id = &""


## The stream for a cue row: the file, or an AudioStreamSynchronized of its stems. null when one fails to load.
static func build_stream(row: Dictionary) -> AudioStream:
	var files := AudioData.cue_files(row)
	if files.is_empty():
		return null
	if not row.has("stems"):
		return _load(files[0])
	var sync := AudioStreamSynchronized.new()
	sync.stream_count = files.size()
	for i in files.size():
		var s := _load(files[i])
		if s == null:
			return null
		sync.set_sync_stream(i, s)
	return sync


static func _load(path: String) -> AudioStream:
	if path == "" or not ResourceLoader.exists(path):
		return null
	return load(path) as AudioStream


## The slot heard now: the one fading toward the loudest level (the cue a queued change is leaving).
func _sounding() -> FadeVoice:
	var best: FadeVoice = null
	for slot in _slots:
		if slot.id != &"" and slot.target > 0.0 and (slot.player as AudioStreamPlayer).playing:
			if best == null or slot.gain > best.gain:
				best = slot
	return best


func _active() -> FadeVoice:
	for slot in _slots:
		if slot.id == current and current != &"" and slot.target > 0.0:
			return slot
	return null


func _fade_out_all(sec: float) -> void:
	for slot in _slots:
		if slot.id == &"" or slot.target <= 0.0:
			continue
		var p := slot.player as AudioStreamPlayer
		var row := _rows.get(slot.id, {}) as Dictionary
		if bool(row.get("resume", false)) and p.playing:
			positions[slot.id] = p.get_playback_position()
		slot.fade_to(0.0, sec)
		slot.step(0.0, floor_db, hold)


func _free_slot() -> FadeVoice:
	# The quietest slot: a free one, else the one furthest into its fade out.
	var best := _slots[0]
	for slot in _slots:
		if not (slot.player as AudioStreamPlayer).playing:
			return slot
		if slot.gain < best.gain:
			best = slot
	(best.player as AudioStreamPlayer).stop()
	best.id = &""
	return best


func _apply_stems() -> void:
	var s := _active()
	if s == null or not (s.player as AudioStreamPlayer).stream is AudioStreamSynchronized:
		return
	var sync := (s.player as AudioStreamPlayer).stream as AudioStreamSynchronized
	for i in mini(_stems.size(), sync.stream_count):
		var g := float((_stems[i] as Array)[0])
		sync.set_sync_stream_volume(i, linear_to_db(g) if g > 0.0 else -80.0)
