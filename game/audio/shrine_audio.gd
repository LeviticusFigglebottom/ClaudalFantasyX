class_name ShrineAudio
extends Node
## The Shell Shrine trial's sounds (M2-AUD-01; vertical_slice.md B07; docs/kb/tech/audio_runtime.md). The Audio
## autoload builds one when a ShellShrineLevel enters the tree. **Listens only** to the trial's signals and the
## level's charm_taken (pillar 4: you hear the water go where you sent it); it never touches the rules.
## Each moment is a row of game/data/audio/shrine_sfx.json (an sfx.json id and where it sounds, a layout point of
## the trial data); the inner pool's fill is a looping bed at the pool while the water reaches it.

const TABLE := "shrine_sfx"
## Height of the sounds above the floor (m).
const EAR_Y := 0.6

var director: AudioDirector
var level: ShellShrineLevel
var data: Dictionary = {}
## Every moment played, in order: [event, sfx id] (tests).
var played: Array = []
## The pool fill bed while the water reaches the pool.
var fill: FadeVoice


func attach(dir: AudioDirector, lvl: ShellShrineLevel) -> void:
	director = dir
	level = lvl
	data = AudioData.table(TABLE)
	var t := lvl.trial
	t.rotated.connect(_on_rotated)
	t.flow_changed.connect(_on_flow_changed)
	t.pool_filled.connect(_on_pool_filled)
	t.side_pool_drained.connect(_on_side_drained)
	lvl.charm_taken.connect(_on_charm_taken)
	_build_fill()
	_update_fill(t.trace())


func _process(delta: float) -> void:
	if fill != null:
		fill.step(delta, director.music.floor_db if director != null else -60.0)


## Plays event `event` (a shrine_sfx.json events row) at `at`. Returns the sfx id ("" when the row is absent).
func play_event(event: String, at: Vector3) -> StringName:
	var row := (data.get("events", {}) as Dictionary).get(event, {}) as Dictionary
	var id := StringName(str(row.get("sfx", "")))
	if id == &"" or director == null:
		return &""
	director.play_sfx_at(id, at)
	played.append([event, id])
	return id


## World position of a trial layout point (layout id, or a basin id).
func point(id: String) -> Vector3:
	var layout := level.trial.data.get("layout", {}) as Dictionary
	var xz: Array = layout.get(id, [0.0, 0.0])
	return level.to_global(Vector3(float(xz[0]), EAR_Y, float(xz[1])))


func _on_rotated(basin: StringName, _rotation: int) -> void:
	play_event("turn", point(String(basin)))


func _on_flow_changed(path: Array[StringName]) -> void:
	if path.is_empty():
		return
	var end := String(path.back())
	var t := level.trial
	var event := "spill"
	if end == String(t.goal()):
		event = "reach_pool"
	elif end == str(t.data.get("drain", "")):
		event = "reach_drain"
	var at := point(end) if event != "spill" else _spill_point(path)
	play_event(event, at)
	_update_fill(path)


func _on_pool_filled() -> void:
	play_event("door", point("door"))
	if fill != null:
		fill.fade_to(0.0, float(data.get("fill_out_sec", 0.0)))


func _on_side_drained() -> void:
	play_event("side_drain", point("side_pool"))


func _on_charm_taken() -> void:
	play_event("charm", point("side_pool"))


## Where spilled water lands: the outlet of the last basin on the path.
func _spill_point(path: Array[StringName]) -> Vector3:
	for i in range(path.size() - 1, -1, -1):
		if level.trial.data.get("basins", {}).has(String(path[i])):
			return level.outlet_point(path[i])
	return point(String(level.trial.data.get("source_into", "")))


func _build_fill() -> void:
	var row := (director.sfx.rows.get(str(data.get("fill_sfx", "")), {})) as Dictionary
	var files: Array = row.get("files", [])
	if files.is_empty() or not ResourceLoader.exists(str(files[0])):
		return
	var p := AudioStreamPlayer3D.new()
	p.name = "PoolFill"
	p.stream = load(str(files[0])) as AudioStream
	p.bus = StringName(str(row.get("bus", "World")))
	p.unit_size = float(row.get("unit_size_m", 6.0))
	add_child(p)
	p.global_position = point(String(level.trial.goal()))
	fill = FadeVoice.new(p)
	fill.base_db = float(row.get("volume_db", 0.0))


func _update_fill(path: Array[StringName]) -> void:
	if fill == null:
		return
	var t := level.trial
	var reaches: bool = not path.is_empty() and path.back() == t.goal() and t.pool_level < 1.0
	var sec := float(data.get("fill_in_sec" if reaches else "fill_out_sec", 0.0))
	if reaches and not (fill.player as AudioStreamPlayer3D).playing:
		(fill.player as AudioStreamPlayer3D).play()
	fill.fade_to(1.0 if reaches else 0.0, sec)
