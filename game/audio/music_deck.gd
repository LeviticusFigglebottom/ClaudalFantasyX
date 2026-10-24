class_name MusicDeck
extends Node
## The music bed (M2-AUD-02; docs/kb/tech/audio_runtime.md): two players that crossfade, stems that fade in and
## out inside one synchronized stream (the Drownbell's phase 2), a resume point per cue, and a hold that silences
## the bed while something else (a cutscene) owns the music. Time passes only through advance(delta).

signal cue_started(cue: StringName)

const SLOTS := 2

## The cue playing (or fading in) now; &"" for none.
var current: StringName = &""
## Fades below this level count as silence (mix.json music.floor_db).
var floor_db := -60.0
## 0..1: the hold. 0 while a cutscene owns the music.
var hold := 1.0
## Where each resumable cue stopped (seconds).
var positions: Dictionary = {}
var _slots: Array[FadeVoice] = []
var _rows: Dictionary = {}
var _hold_target := 1.0
var _hold_rate := 0.0
## Per-stem fades of the current cue: [gain, target, rate].
var _stems: Array = []
var _bus: StringName = &"Music"


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
func play(cue_id: StringName, row: Dictionary, sec: float) -> bool:
	if cue_id == current and _active() != null:
		return true
	var stream := build_stream(row)
	if stream == null:
		return false
	_fade_out_all(sec)
	var slot := _free_slot()
	var p := slot.player as AudioStreamPlayer
	p.stream = stream
	slot.id = cue_id
	slot.base_db = float(row.get("volume_db", 0.0))
	slot.gain = 0.0 if sec > 0.0 else 1.0
	slot.fade_to(1.0, sec)
	_rows[cue_id] = row
	_stems = []
	if stream is AudioStreamSynchronized:
		var on: Array = row.get("start_stems", [0])
		for i in (stream as AudioStreamSynchronized).stream_count:
			var g := 1.0 if on.has(i) else 0.0
			_stems.append([g, g, 0.0])
	var from := float(positions.get(cue_id, 0.0)) if bool(row.get("resume", false)) else 0.0
	positions.erase(cue_id)
	p.play(from)
	current = cue_id
	_apply_stems()
	slot.step(0.0, floor_db, hold)
	cue_started.emit(cue_id)
	return true


## Fades the bed out over `sec`.
func stop(sec: float) -> void:
	_fade_out_all(sec)
	current = &""


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
