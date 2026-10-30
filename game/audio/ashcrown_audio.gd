class_name AshcrownAudio
extends Node
## The Ashcrown strike trial's sounds (M3-AUD-825; act1_ch05.md B08; docs/kb/tech/audio_runtime.md "Ashcrown").
## The Audio autoload builds one when a Ch05AshcrownZone enters the tree. **Listens only** to the zone's
## AshcrownTrial (the catch, each stud going dark, the fade, every release's run by its outcome, the landing, the
## gates, the plates, the alcove) and never touches the rules. Rows and places are game/data/audio/ashcrown_sfx.json.
## M3-AUD-864: the same listener plays Ch8's Coilspire flue-key trial from coilspire_sfx.json (any trial whose signals
## a table names); `by_arg` picks an event's row by one of its arguments (a flue key turned open or shut).

## Plays a row at a place: (id: StringName, at: Vector3) -> void.
var player_at: Callable = Callable()
var data: Dictionary = {}
var zone: Node3D
## Every row played, in order: [event, sfx id] (tests).
var played: Array = []


func _init(table: Dictionary = {}) -> void:
	data = table


func bind_director(dir: AudioDirector) -> void:
	player_at = func(id: StringName, at: Vector3) -> void: dir.play_sfx_at(id, at)


## Connects `z`'s trial (by its signal names, once).
func attach(z: Node3D) -> void:
	zone = z
	var trial: Variant = z.get(&"trial")
	if not trial is Object:
		return
	var t := trial as Object
	for event: String in data.get("events", {}) as Dictionary:
		_connect(t, event)
	for event: String in data.get("by_arg", {}) as Dictionary:
		_connect(t, event)
	_connect(t, "ran")


func _connect(t: Object, sig: String) -> void:
	var argc := UiAudio._arg_count(t, StringName(sig))
	if argc < 0:
		return
	var fn: Callable
	match argc:
		0:
			fn = func() -> void: on_event(sig, [])
		1:
			fn = func(a: Variant) -> void: on_event(sig, [a])
		2:
			fn = func(a: Variant, b: Variant) -> void: on_event(sig, [a, b])
		_:
			fn = (func(a: Variant, b: Variant, c: Variant) -> void: on_event(sig, [a, b, c])).unbind(maxi(argc - 3, 0))
	t.connect(StringName(sig), fn)


## Plays `sig`'s row: an event's own, or for `ran` the row its outcome (the third argument) names.
func on_event(sig: String, args: Array) -> void:
	var row := ""
	var by := (data.get("by_arg", {}) as Dictionary).get(sig, {}) as Dictionary
	if sig == "ran":
		row = str((data.get("ran", {}) as Dictionary).get(str(args[2]) if args.size() > 2 else "", ""))
	elif not by.is_empty():
		var i := int(by.get("index", 0))
		row = str((by.get("rows", {}) as Dictionary).get(str(args[i]).to_lower() if args.size() > i else "", ""))
	else:
		row = str((data.get("events", {}) as Dictionary).get(sig, ""))
	if row == "":
		return
	played.append([sig, StringName(row)])
	if player_at.is_valid():
		player_at.call(StringName(row), place(sig, args))


## Where `sig` sounds: its `at` node under the zone (with the first argument in it), else the camera, else the zone.
func place(sig: String, args: Array) -> Vector3:
	var lift := Vector3.UP * float(data.get("height_m", 0.0))
	var path := str((data.get("at", {}) as Dictionary).get(sig, ""))
	if path != "" and is_instance_valid(zone):
		var n := zone.get_node_or_null(NodePath(path % str(args[0]) if "%s" in path and args.size() > 0 else path))
		if n is Node3D:
			return (n as Node3D).global_position + lift
	var cam := zone.get_viewport().get_camera_3d() if is_instance_valid(zone) and zone.is_inside_tree() else null
	if cam != null:
		return cam.global_position
	return zone.global_position + lift if is_instance_valid(zone) and zone.is_inside_tree() else Vector3.ZERO
