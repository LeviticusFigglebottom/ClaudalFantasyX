class_name CutsceneAudio
extends Node
## Cutscene foley by listening (M3-AUD-817; ADR 0031; docs/kb/tech/audio_runtime.md "Cutscene foley"). The director
## hands it every CutsceneSequencer that enters the tree; it connects the sequencer's cue_played and plays
## game/data/audio/cutscene_foley.json's row for an `@anim` clip, an `@light` switch or an `@vfx` effect, at the
## actor, the light or the place. It never writes the cutscene, and plays nothing while the sequencer is skipping.
## The actors' steps are their own FootstepAudio listeners (AudioDirector.attach_cast), not this.
## M3-AUD-847: a stage's lit lamps (cutscene_foley.json `lamps`: lights named by `match`, globs) crackle at the
## lamp at random gaps while they are visible and lit; the director steps it once a frame.

## Plays a row at a place: (id: StringName, at: Vector3) -> void.
var player_at: Callable = Callable()
var data: Dictionary = {}
## Every row played, in order (tests).
var played: Array[StringName] = []
## Each watched lamp: {light: Light3D, left: float (seconds to its next crackle)}.
var lamps: Array[Dictionary] = []
var _rng := RandomNumberGenerator.new()


func _init(table: Dictionary = {}) -> void:
	data = table
	_rng.seed = hash("cutscene_lamps")


## Watches every light under `stage` that `lamps.match` names (once each).
func watch_lamps(stage: Node) -> void:
	var cfg := data.get("lamps", {}) as Dictionary
	if not is_instance_valid(stage) or cfg.is_empty():
		return
	for n in stage.find_children("*", "Light3D", true, false):
		if lamps.any(func(l: Dictionary) -> bool: return l["light"] == n):
			continue
		for pattern: Variant in cfg.get("match", []):
			if String(n.name).match(str(pattern)):
				lamps.append({"light": n, "left": _gap(cfg)})
				break


## Steps the lamps: a lit, visible lamp crackles when its gap runs out.
func advance(delta: float) -> void:
	var cfg := data.get("lamps", {}) as Dictionary
	for i in range(lamps.size() - 1, -1, -1):
		var l := lamps[i]
		if not is_instance_valid(l["light"]) or not (l["light"] as Node).is_inside_tree():
			lamps.remove_at(i)
			continue
		var light := l["light"] as Light3D
		if not light.is_visible_in_tree() or light.light_energy <= 0.0:
			continue
		l["left"] = float(l["left"]) - delta
		if float(l["left"]) <= 0.0:
			_play(str(cfg.get("row", "")), light.global_position)
			l["left"] = _gap(cfg)


func _gap(cfg: Dictionary) -> float:
	var pair: Variant = cfg.get("every_sec", [1.0, 1.0])
	if pair is Array and (pair as Array).size() == 2:
		return _rng.randf_range(float(pair[0]), float(pair[1]))
	return 1.0


func _exit_tree() -> void:
	lamps.clear()


func bind_director(dir: AudioDirector) -> void:
	player_at = func(id: StringName, at: Vector3) -> void: dir.play_sfx_at(id, at)


## Connects `seq`'s cue_played once.
func watch(seq: Node) -> void:
	if not is_instance_valid(seq) or not seq.has_signal(&"cue_played"):
		return
	var fn := on_cue.bind(seq)
	if not seq.is_connected(&"cue_played", fn):
		seq.connect(&"cue_played", fn)


## The row `table` gives `key`: its exact entry, else the first glob that matches, else &"" (none).
static func row_in(table: Dictionary, key: String) -> Variant:
	if table.has(key):
		return table[key]
	for pattern: String in table:
		if key.match(pattern):
			return table[pattern]
	return null


func on_cue(cue: StringName, args: Array, kwargs: Dictionary, seq: Node) -> void:
	if not is_instance_valid(seq) or (seq.has_method(&"is_skipping") and bool(seq.call(&"is_skipping"))):
		return
	match cue:
		&"anim":
			if args.size() >= 2:
				var row: Variant = row_in(data.get("anim", {}) as Dictionary, str(args[1]))
				var actor := _place(seq, StringName(str(args[0])))
				if row != null and actor != null:
					_play(str(row), actor.global_position + Vector3.UP * float(data.get("at_height_m", 0.0)))
		&"light":
			if args.size() >= 2:
				_light(seq, str(args[0]), str(args[1]))
		&"vfx":
			if args.size() >= 1:
				var row: Variant = row_in(data.get("vfx", {}) as Dictionary, str(args[0]))
				var at := _place(seq, StringName(str(kwargs.get("at", ""))))
				if row != null:
					_play(str(row), at.global_position if at != null else _fallback(seq))


func _light(seq: Node, light_name: String, state: String) -> void:
	var rows: Variant = row_in(data.get("light", {}) as Dictionary, light_name)
	if not rows is Dictionary:
		return
	var scene := seq.get_tree().current_scene if seq.is_inside_tree() else null
	var light := scene.find_child(light_name, true, false) as Light3D if scene != null else null
	if state == "off" and (light == null or not light.is_visible_in_tree() or light.light_energy <= 0.0):
		return  # already dark: nothing to put out
	var at := light.global_position if light != null else _fallback(seq)
	_play(str((rows as Dictionary).get(state, "")), at)


## The stage's place (a mark or an actor) for `id`, or null. The stage is the current scene's CutsceneStage.
func _place(seq: Node, id: StringName) -> Node3D:
	if id == &"" or not seq.is_inside_tree():
		return null
	var scene := seq.get_tree().current_scene
	if scene == null:
		return null
	for stage: Node in scene.find_children("*", "CutsceneStage", true, false):
		var p := (stage as CutsceneStage).place(id)
		if p != null:
			return p
	return null


func _fallback(seq: Node) -> Vector3:
	var cam := seq.get_viewport().get_camera_3d() if seq.is_inside_tree() else null
	return cam.global_position if cam != null else Vector3.ZERO


func _play(id: String, at: Vector3) -> void:
	if id == "":
		return
	played.append(StringName(id))
	if player_at.is_valid():
		player_at.call(StringName(id), at)
