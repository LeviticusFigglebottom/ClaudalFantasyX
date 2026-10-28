class_name LifeAudio
extends Node
## Village and wildlife life in the field, by listening (M3-AUD-814; ADR 0031; docs/kb/tech/audio_runtime.md
## "Life"). The director hands it each node that enters the tree; a node whose script's global class (or a base
## class's, or its `audio_class` meta) is a game/data/audio/life.json `hooks` row is watched, read once a frame and
## never written. Every member it reads is named in life.json and looked up by name, so it loads and runs whether or
## not creatures' FieldNpc and WildlifeLayer are on this branch.
## - villager: a chat turn that starts plays a murmur turn in the villager's voice at its head; work plays the
##   villager's work row at its work point every `work.every_sec`.
## - wildlife: a flock calls now and then from one of its gulls, a gull taking off claps off, a crab bolting
##   scuttles, a startled shoal darts. Positions are in the layer's space.
## - villager steps (M3-AUD-826): each villager gets its own FootstepAudio over footsteps.json with `villager.steps`
##   on top (quieter, a shorter stride, cloth but no hero gear), so the routes they walk are heard.
## Only nodes within `hear_m` of the ear (the viewport's camera) are read. Time passes only through advance(delta)
## (AudioDirector.advance calls it; tests call it directly).

const META_CLASS := &"audio_class"
const KIND_VILLAGER := &"villager"
const KIND_WILDLIFE := &"wildlife"

## Plays a row at a place: (id: StringName, at: Vector3) -> void.
var player_at: Callable = Callable()
## Plays a footstep row: (id: StringName, at: Vector3, opts: Dictionary) -> void (the villagers' FootstepAudio).
var step_player: Callable = Callable()
## footsteps.json, the base of the villagers' steps (empty: villagers take no steps).
var footstep_data: Dictionary = {}
## The ear's position, or null for none (every node is heard): () -> Variant. Defaults to the viewport camera.
var ear: Callable = Callable()
## True while a line of dialogue is on screen: () -> bool (M3-AUD-850). Villagers' chat never murmurs over a line;
## their work goes on, ducked with the World bus. The director sets it; unset, nothing is held.
var quiet: Callable = Callable()
## life.json.
var data: Dictionary = {}
## Hook kind by class name.
var kinds: Dictionary = {}
## Each watched node: {node, kind, state: Dictionary}.
var watched: Array[Dictionary] = []
var _rng := RandomNumberGenerator.new()


func _init(table: Dictionary = {}) -> void:
	configure(table)


## Reads a life.json document.
func configure(table: Dictionary) -> void:
	data = table
	kinds.clear()
	for h: Variant in table.get("hooks", []):
		if h is Dictionary and str((h as Dictionary).get("class", "")) != "":
			kinds[str(h["class"])] = StringName(str((h as Dictionary).get("kind", "")))
	_rng.seed = int(table.get("seed", 0))


## Points the player at `dir`'s play_sfx_at.
func bind_director(dir: AudioDirector) -> void:
	player_at = func(id: StringName, at: Vector3) -> void: dir.play_sfx_at(id, at)
	step_player = func(id: StringName, at: Vector3, opts: Dictionary) -> void: dir.play_sfx_at(id, at, opts)
	quiet = func() -> bool: return dir.ducks.has(AudioDirector.REASON_DIALOGUE)


## The hook kind for `node` (&"" when it has none).
func kind_for(node: Node) -> StringName:
	if node.has_meta(META_CLASS):
		return kinds.get(str(node.get_meta(META_CLASS)), &"") as StringName
	var s := node.get_script() as Script
	while s != null:
		var cls := String(s.get_global_name())
		if kinds.has(cls):
			return kinds[cls]
		s = s.get_base_script()
	return &""


## True when `node` has a hook (the director then calls watch() deferred).
func wants(node: Node) -> bool:
	return not kinds.is_empty() and kind_for(node) != &""


func watch(node: Node) -> void:
	if not is_instance_valid(node) or not node.is_inside_tree() or not node is Node3D:
		return
	for w: Dictionary in watched:
		if w["node"] == node:
			return
	var kind := kind_for(node)
	if kind == &"":
		return
	var w := {"node": node, "kind": kind, "state": {}}
	if kind == KIND_VILLAGER:
		w["steps"] = _villager_steps(node as Node3D)
	watched.append(w)


## The villagers' footstep table: footsteps.json with life.json's villager.steps over it.
func villager_step_table() -> Dictionary:
	if footstep_data.is_empty():
		return {}
	var table := footstep_data.duplicate(true)
	var cfg := (data.get("villager", {}) as Dictionary).get("steps", {}) as Dictionary
	for k: String in cfg:
		if k == "gear" and not bool(cfg[k]):
			(table.get("foley", {}) as Dictionary).erase("gear")
		elif not k.begins_with("_"):
			table[k] = cfg[k]
	table.erase("contacts")  # villagers' clips are not the heroes': step by distance
	return table


func _villager_steps(npc: Node3D) -> FootstepAudio:
	var table := villager_step_table()
	if table.is_empty():
		return null
	var f := FootstepAudio.new(table)
	f.name = "VillagerSteps"
	f.player = step_player
	add_child(f)
	var scene := npc.get_tree().current_scene if npc.is_inside_tree() else null
	f.attach(npc, scene.scene_file_path if scene != null else "")
	return f


## Leaving the tree (a zone change, the game quitting) drops every watched node, so nothing is read after its
## zone is freed.
func _exit_tree() -> void:
	for w in watched:
		if is_instance_valid(w.get("steps")):
			(w["steps"] as Node).queue_free()
	watched.clear()


func advance(delta: float) -> void:
	var at_ear: Variant = _ear_position()
	var hear := float(data.get("hear_m", INF))
	for i in range(watched.size() - 1, -1, -1):
		var w := watched[i]
		# Validity before the cast: a freed villager or layer (a zone torn down at shutdown) can't be cast (big12).
		if not is_instance_valid(w["node"]) or not (w["node"] as Node3D).is_inside_tree():
			if is_instance_valid(w.get("steps")):
				(w["steps"] as Node).queue_free()
			watched.remove_at(i)
			continue
		var node := w["node"] as Node3D
		if w["kind"] == KIND_VILLAGER:
			var near := at_ear == null or node.global_position.distance_to(at_ear as Vector3) <= hear
			_villager(node, w["state"] as Dictionary, delta, near)
			var steps := w.get("steps") as FootstepAudio
			if steps != null and near:
				steps.advance(delta)
		elif w["kind"] == KIND_WILDLIFE:
			_wildlife(node, w["state"] as Dictionary, delta, at_ear, hear)


func _ear_position() -> Variant:
	if ear.is_valid():
		return ear.call()
	var cam := get_viewport().get_camera_3d() if is_inside_tree() else null
	return cam.global_position if cam != null else null


func _play(row: String, at: Vector3) -> void:
	if row != "" and player_at.is_valid():
		player_at.call(StringName(row), at)


func _range(pair: Variant) -> float:
	if pair is Array and (pair as Array).size() == 2:
		return _rng.randf_range(float(pair[0]), float(pair[1]))
	return float(pair) if pair is float or pair is int else 1.0


## `node.method()` when it has the method, else `fallback`.
static func _ask(node: Object, method: String, fallback: Variant) -> Variant:
	return node.call(StringName(method)) if method != "" and node.has_method(StringName(method)) else fallback


# --------------------------------------------------------------------------- villagers


## True while `npc` speaks its turn of a chat: its own read when it has one, else its speaker field names it.
func speaking(npc: Node) -> bool:
	var cfg := data.get("villager", {}) as Dictionary
	var method := str(cfg.get("speaking_method", ""))
	if method != "" and npc.has_method(StringName(method)):
		return bool(npc.call(StringName(method)))
	if not bool(_ask(npc, str(cfg.get("chatting_method", "")), false)):
		return false
	var id: Variant = npc.get(StringName(str(cfg.get("id_prop", ""))))
	var speaker: Variant = npc.get(StringName(str(cfg.get("speaker_prop", ""))))
	return id != null and speaker != null and str(speaker) != "" and str(speaker) == str(id)


## The murmur row for villager `id`: its voices row (low or high), else one by a hash of the id.
func murmur_row(id: String) -> String:
	var cfg := data.get("villager", {}) as Dictionary
	var voice := str((cfg.get("voices", {}) as Dictionary).get(id, "high" if hash(id) % 2 == 1 else "low"))
	return str((cfg.get("murmur", {}) as Dictionary).get(voice, ""))


func _villager(npc: Node3D, st: Dictionary, delta: float, near: bool) -> void:
	var cfg := data.get("villager", {}) as Dictionary
	var id := str(npc.get(StringName(str(cfg.get("id_prop", "")))))
	var talking := speaking(npc)
	var hushed := quiet.is_valid() and bool(quiet.call())
	if talking and not bool(st.get("talking", false)) and near and not hushed:
		_play(murmur_row(id), npc.global_position + Vector3.UP * float(cfg.get("head_m", 0.0)))
	st["talking"] = talking
	var work := cfg.get("work", {}) as Dictionary
	var row := str((work.get("rows", {}) as Dictionary).get(id, ""))
	if row == "" or not bool(_ask(npc, str(work.get("working_method", "")), false)):
		st.erase("work_left")
		return
	if not st.has("work_left"):
		st["work_left"] = _range(work.get("every_sec", 1.0)) * _rng.randf()  # a random phase into the first gap
	st["work_left"] = float(st["work_left"]) - delta
	if float(st["work_left"]) > 0.0:
		return
	st["work_left"] = _range(work.get("every_sec", 1.0))
	if near:
		var at: Variant = _ask(npc, str(work.get("point_method", "")), npc.global_position)
		_play(row, at as Vector3 if at is Vector3 else npc.global_position)


# --------------------------------------------------------------------------- wildlife


func _members(layer: Node, cfg: Dictionary) -> Array:
	var groups: Variant = layer.get(StringName(str(cfg.get("groups", ""))))
	return groups as Array if groups is Array else []


func _heard(layer: Node3D, local: Vector3, at_ear: Variant, hear: float) -> bool:
	return at_ear == null or layer.to_global(local).distance_to(at_ear as Vector3) <= hear


func _wildlife(layer: Node3D, st: Dictionary, delta: float, at_ear: Variant, hear: float) -> void:
	var cfg := data.get("wildlife", {}) as Dictionary
	_gulls(layer, st, delta, cfg.get("gull", {}) as Dictionary, at_ear, hear)
	_crabs(layer, st, delta, cfg.get("crab", {}) as Dictionary, at_ear, hear)
	_fish(layer, st, cfg.get("fish", {}) as Dictionary, at_ear, hear)


func _gulls(layer: Node3D, st: Dictionary, delta: float, cfg: Dictionary, at_ear: Variant, hear: float) -> void:
	if cfg.is_empty():
		return
	var flocks := _members(layer, cfg)
	var timers := st.get("gull_left", []) as Array
	timers.resize(flocks.size())
	var states := st.get("gull_states", {}) as Dictionary
	var take := int(cfg.get("takeoff_state", -1))
	for f in flocks.size():
		var birds: Variant = (flocks[f] as Object).get(StringName(str(cfg.get("members", ""))))
		if not birds is Array or (birds as Array).is_empty():
			continue
		for b in (birds as Array).size():
			var bird := (birds as Array)[b] as Object
			var key := "%d/%d" % [f, b]
			var s := int(bird.get(&"state"))
			if s == take and int(states.get(key, take)) != take and _heard(layer, bird.get(&"pos"), at_ear, hear):
				_play(str(cfg.get("takeoff", "")), layer.to_global(bird.get(&"pos")))
			states[key] = s
		if timers[f] == null:
			timers[f] = _range(cfg.get("call_every_sec", 1.0)) * _rng.randf()
		timers[f] = float(timers[f]) - delta
		if float(timers[f]) <= 0.0:
			timers[f] = _range(cfg.get("call_every_sec", 1.0))
			var caller := (birds as Array)[_rng.randi_range(0, (birds as Array).size() - 1)] as Object
			if _heard(layer, caller.get(&"pos"), at_ear, hear):
				_play(str(cfg.get("call", "")), layer.to_global(caller.get(&"pos")))
	st["gull_left"] = timers
	st["gull_states"] = states


func _crabs(layer: Node3D, st: Dictionary, delta: float, cfg: Dictionary, at_ear: Variant, hear: float) -> void:
	if cfg.is_empty():
		return
	var beaches := _members(layer, cfg)
	var states := st.get("crab_states", {}) as Dictionary
	var cool := st.get("crab_cool", {}) as Dictionary
	var flee := int(cfg.get("flee_state", -1))
	for k in beaches.size():
		cool[k] = maxf(float(cool.get(k, 0.0)) - delta, 0.0)
		var crabs: Variant = (beaches[k] as Object).get(StringName(str(cfg.get("members", ""))))
		if not crabs is Array:
			continue
		for c in (crabs as Array).size():
			var crab := (crabs as Array)[c] as Object
			var key := "%d/%d" % [k, c]
			var s := int(crab.get(&"state"))
			var was := int(states.get(key, s))
			states[key] = s
			if s != flee or was == flee or float(cool[k]) > 0.0:
				continue
			var p := crab.get(&"pos") as Vector2
			var local := Vector3(p.x, float(crab.get(&"y")), p.y)
			if _heard(layer, local, at_ear, hear):
				_play(str(cfg.get("scuttle", "")), layer.to_global(local))
				cool[k] = float(cfg.get("cooldown_sec", 0.0))
	st["crab_states"] = states
	st["crab_cool"] = cool


func _fish(layer: Node3D, st: Dictionary, cfg: Dictionary, at_ear: Variant, hear: float) -> void:
	if cfg.is_empty():
		return
	var shoals := _members(layer, cfg)
	var was := st.get("fish_startled", {}) as Dictionary
	for k in shoals.size():
		var shoal := shoals[k] as Object
		var now := false
		var method := str(cfg.get("startle_method", ""))
		if method != "" and shoal.has_method(StringName(method)):
			now = bool(shoal.call(StringName(method)))
		else:
			var left: Variant = shoal.get(StringName(str(cfg.get("startle_prop", ""))))
			now = left != null and float(left) > 0.0
		if now and not bool(was.get(k, false)) and _heard(layer, shoal.get(&"lead"), at_ear, hear):
			_play(str(cfg.get("dart", "")), layer.to_global(shoal.get(&"lead")))
		was[k] = now
	st["fish_startled"] = was
