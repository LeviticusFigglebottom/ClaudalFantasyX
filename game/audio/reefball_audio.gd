class_name ReefballAudio
extends Node
## Reefball's sounds and its crowd, by listening (M3-AUD-17; ADR 0031; docs/kb/tech/audio_runtime.md "Reefball").
## The director hands it each node that enters the tree. A node whose script's global class name (or a base class's,
## or its `audio_class` meta) has a row in game/data/audio/reefball_hooks.json `hooks` is watched; its signals are
## connected by name, only when the node has them, so this loads and runs whether or not those classes exist yet.
## Nothing it listens to is ever written.
## - `signals`: {signal: action}. An action plays `sfx_at` at a place (the signal's first Vector3 or Node3D argument,
##   else the hooked node) and `sfx` flat, then moves the crowd (`crowd`: murmur, excited or silence), and with
##   `restore_after_sec` brings `restore` back after that long (the naming rite carries its own stands going quiet).
## - `on_enter` / `on_exit`: an action when the node is attached (deferred, after its _ready) or leaves the tree.
## - `sphere`: the node is the water sphere (its global position is the centre; `radius_method` gives the radius).
##   Once a frame each swimmer (a Node3D in one of `swim.groups`) is read: crossing the wall inward plays
##   `swim.enter`, outward `swim.exit` (with `swim.edge_m` of hysteresis), and every `swim.stroke_m` swum inside
##   plays `swim.stroke`, all at the swimmer. A swimmer's first read is its baseline, and a jump longer than
##   `swim.teleport_m` is not swum.
## - `muffle` (M3-AUD-22): while the ear (the viewport's Camera3D with `use_camera`, else the first node in
##   `ear_groups`) is inside a sphere, the director's BusMuffle is on for `reason`: the world heard through water.
## The crowd's beds are ambience.json beds; a move keeps the zone's other beds and swaps only the crowd's.
## Time passes only through advance(delta) (AudioDirector.advance calls it; tests call it directly).

## The meta a node may carry to name the hook it uses instead of its script's class (tests' stand-ins, set pieces).
const META_CLASS := &"audio_class"
const CROWD_MURMUR := &"murmur"
const CROWD_EXCITED := &"excited"
const CROWD_SILENCE := &"silence"

## Plays a row flat: (id: StringName) -> void.
var player: Callable = Callable()
## Plays a row at a place: (id: StringName, at: Vector3) -> void.
var player_at: Callable = Callable()
## The ambience beds on now: () -> Array[StringName].
var beds_now: Callable = Callable()
## Sets the ambience beds: (ids: Array[StringName], sec: float) -> void.
var ambience: Callable = Callable()
## Turns a muffle reason on or off: (reason: StringName, on: bool) -> void.
var muffler: Callable = Callable()
## reefball_hooks.json's hooks by class name, and its crowd and swim blocks.
var hooks: Dictionary = {}
var crowd_cfg: Dictionary = {}
var swim_cfg: Dictionary = {}
var muffle_cfg: Dictionary = {}
## Whether the ear is inside a sphere (the muffle is on).
var ear_inside := false
## The crowd's state now (&"" before any move).
var crowd: StringName = &""
## Every row played, in order: [id, positional] (tests).
var played: Array = []
## Each watched node: {node, hook}.
var watched: Array[Dictionary] = []
## Each swimmer's state by instance id: {inside: bool, last: Vector3, swum: float}.
var swimmers: Dictionary = {}
## A crowd move waiting: {crowd, left} ({} when none).
var _restore: Dictionary = {}


func _init(table: Dictionary = {}) -> void:
	configure(table)


## Reads a reefball_hooks.json document.
func configure(table: Dictionary) -> void:
	hooks.clear()
	for h: Variant in table.get("hooks", []):
		if h is Dictionary and str((h as Dictionary).get("class", "")) != "":
			hooks[str((h as Dictionary)["class"])] = h
	crowd_cfg = table.get("crowd", {}) as Dictionary
	swim_cfg = table.get("swim", {}) as Dictionary
	muffle_cfg = table.get("muffle", {}) as Dictionary


## Points the players at `dir`'s play_sfx / play_sfx_at and its ambience beds.
func bind_director(dir: AudioDirector) -> void:
	player = func(id: StringName) -> void: dir.play_sfx(id)
	player_at = func(id: StringName, at: Vector3) -> void: dir.play_sfx_at(id, at)
	ambience = func(ids: Array[StringName], sec: float) -> void: dir.set_ambience(ids, sec)
	muffler = func(reason: StringName, on: bool) -> void: dir.muffle.set_reason(reason, on)
	beds_now = func() -> Array[StringName]:
		var out: Array[StringName] = []
		for id: StringName in dir.beds:
			if (dir.beds[id] as FadeVoice).is_active():
				out.append(id)
		return out


## The hook row for `node` ({} when it has none).
func hook_for(node: Node) -> Dictionary:
	if node.has_meta(META_CLASS):
		return hooks.get(str(node.get_meta(META_CLASS)), {}) as Dictionary
	var s := node.get_script() as Script
	while s != null:
		var cls := String(s.get_global_name())
		if hooks.has(cls):
			return hooks[cls]
		s = s.get_base_script()
	return {}


## True when `node` has a hook (the director then calls watch() deferred).
func wants(node: Node) -> bool:
	return not hooks.is_empty() and not hook_for(node).is_empty()


## Connects to `node`'s signals (those it has) and runs its on_enter.
func watch(node: Node) -> void:
	if not is_instance_valid(node) or not node.is_inside_tree():
		return
	for w: Dictionary in watched:
		if w["node"] == node:
			return
	var hook := hook_for(node)
	if hook.is_empty():
		return
	var sigs := hook.get("signals", {}) as Dictionary
	for sig: String in sigs:
		var argc := UiAudio._arg_count(node, StringName(sig))
		if argc < 0:
			continue
		var fire: Callable
		match argc:
			0:
				fire = _fire0.bind(sig, node)
			1:
				fire = _fire1.bind(sig, node)
			2:
				fire = _fire2.bind(sig, node)
			_:
				fire = _fire3.bind(sig, node).unbind(argc - 3) if argc > 3 else _fire3.bind(sig, node)
		node.connect(StringName(sig), fire)
	if hook.has("on_exit"):
		node.tree_exiting.connect(run.bind(hook["on_exit"], [], node))
	watched.append({"node": node, "hook": hook})
	if hook.has("on_enter"):
		run(hook["on_enter"], [], node)


## Runs action `action` ({sfx_at, sfx, crowd, restore, restore_after_sec}) for `node` with the signal's `args`.
func run(action: Variant, args: Array, node: Node) -> void:
	if not action is Dictionary:
		return
	var a := action as Dictionary
	for id: StringName in _ids(a.get("sfx_at")):
		var at: Variant = place_of(args, node)
		if at is Vector3 and player_at.is_valid():
			player_at.call(id, at)
			played.append([id, true])
		elif player.is_valid():
			player.call(id)
			played.append([id, false])
	for id: StringName in _ids(a.get("sfx")):
		if player.is_valid():
			player.call(id)
		played.append([id, false])
	if a.has("crowd"):
		set_crowd(StringName(str(a["crowd"])))
	if a.has("restore") and float(a.get("restore_after_sec", 0.0)) > 0.0:
		_restore = {"crowd": StringName(str(a["restore"])), "left": float(a["restore_after_sec"])}


## The place a positional row sounds: the first Vector3 or Node3D argument, else `node` if it is a Node3D, else null.
static func place_of(args: Array, node: Node) -> Variant:
	for v: Variant in args:
		if v is Vector3:
			return v
		if v is Node3D and is_instance_valid(v) and (v as Node3D).is_inside_tree():
			return (v as Node3D).global_position
	if node is Node3D and is_instance_valid(node) and node.is_inside_tree():
		return (node as Node3D).global_position
	return null


## Moves the crowd to `state` (murmur, excited or silence), keeping the zone's other beds.
func set_crowd(state: StringName) -> void:
	_restore = {}
	if state == crowd or not ambience.is_valid():
		crowd = state
		return
	var mine: Array[StringName] = [
		StringName(str(crowd_cfg.get("murmur", ""))), StringName(str(crowd_cfg.get("excited", "")))
	]
	var ids: Array[StringName] = []
	if beds_now.is_valid():
		for id: StringName in beds_now.call():
			if not mine.has(id):
				ids.append(id)
	if state == CROWD_MURMUR or state == CROWD_EXCITED:
		ids.append(mine[0] if state == CROWD_MURMUR else mine[1])
	var key := "rite_fade_sec" if state == CROWD_SILENCE else "fade_sec"
	ambience.call(ids, float(crowd_cfg.get(key, crowd_cfg.get("fade_sec", 1.0))))
	crowd = state


## Reads the swimmers against each sphere and runs a waiting crowd move.
func advance(delta: float) -> void:
	var alive: Array[Dictionary] = []
	for w in watched:
		if is_instance_valid(w["node"]) and (w["node"] as Node).is_inside_tree():
			alive.append(w)
	watched = alive
	if not _restore.is_empty():
		_restore["left"] = float(_restore["left"]) - delta
		if float(_restore["left"]) <= 0.0:
			set_crowd(_restore["crowd"])
	var spheres: Array[Node3D] = []
	for w in watched:
		if (w["hook"] as Dictionary).has("sphere") and w["node"] is Node3D:
			spheres.append(w["node"] as Node3D)
	if spheres.is_empty():
		swimmers.clear()
		_set_ear(false)
		return
	_read_ear(spheres)
	var seen: Dictionary = {}
	for s: Node3D in _swimmer_nodes():
		seen[s.get_instance_id()] = true
		_read_swimmer(s, spheres)
	for id: int in swimmers.keys():
		if not seen.has(id):
			swimmers.erase(id)


func _read_swimmer(s: Node3D, spheres: Array[Node3D]) -> void:
	var at := s.global_position
	var edge := float(swim_cfg.get("edge_m", 0.0))
	var inside := false
	var near := false
	for sp in spheres:
		var d := at.distance_to(sp.global_position)
		var r := radius_of(sp)
		inside = inside or d < r - edge
		near = near or d <= r + edge
	var id := s.get_instance_id()
	if not swimmers.has(id):
		swimmers[id] = {"inside": inside, "last": at, "swum": 0.0}
		return
	var st := swimmers[id] as Dictionary
	var was := bool(st["inside"])
	var now := inside or (was and near)  # inside the band keeps the last side
	var step := at.distance_to(st["last"] as Vector3)
	st["last"] = at
	if now != was:
		st["inside"] = now
		st["swum"] = 0.0
		_play_at(StringName(str(swim_cfg.get("enter" if now else "exit", ""))), at)
		return
	if not now or step > float(swim_cfg.get("teleport_m", INF)):
		return
	st["swum"] = float(st["swum"]) + step
	var stroke := float(swim_cfg.get("stroke_m", 0.0))
	if stroke > 0.0 and float(st["swum"]) >= stroke:
		st["swum"] = fmod(float(st["swum"]), stroke)
		_play_at(StringName(str(swim_cfg.get("stroke", ""))), at)


## The node that hears: the viewport's camera (muffle.use_camera), else the first node in muffle.ear_groups.
func ear() -> Node3D:
	if not is_inside_tree():
		return null
	if bool(muffle_cfg.get("use_camera", false)):
		var cam := get_viewport().get_camera_3d()
		if cam != null:
			return cam
	for g: Variant in muffle_cfg.get("ear_groups", []):
		for n: Node in get_tree().get_nodes_in_group(StringName(str(g))):
			if n is Node3D:
				return n as Node3D
	return null


func _read_ear(spheres: Array[Node3D]) -> void:
	var e := ear()
	if e == null:
		_set_ear(false)
		return
	var edge := float(swim_cfg.get("edge_m", 0.0))
	var inside := false
	var near := false
	for sp in spheres:
		var d := e.global_position.distance_to(sp.global_position)
		var r := radius_of(sp)
		inside = inside or d < r - edge
		near = near or d <= r + edge
	_set_ear(inside or (ear_inside and near))


func _set_ear(inside: bool) -> void:
	if inside == ear_inside:
		return
	ear_inside = inside
	var reason := StringName(str(muffle_cfg.get("reason", "")))
	if reason != &"" and muffler.is_valid():
		muffler.call(reason, inside)


## The sphere's radius: its `radius_method` (the hook's sphere block), else that block's `radius_m`.
func radius_of(sphere: Node) -> float:
	var cfg := hook_for(sphere).get("sphere", {}) as Dictionary
	var m := StringName(str(cfg.get("radius_method", "")))
	if m != &"" and sphere.has_method(m):
		return float(sphere.call(m))
	return float(cfg.get("radius_m", 0.0))


func _swimmer_nodes() -> Array[Node3D]:
	var out: Array[Node3D] = []
	if not is_inside_tree():
		return out
	for g: Variant in swim_cfg.get("groups", []):
		for n: Node in get_tree().get_nodes_in_group(StringName(str(g))):
			if n is Node3D and not out.has(n):
				out.append(n as Node3D)
	return out


func _play_at(id: StringName, at: Vector3) -> void:
	if id == &"":
		return
	if player_at.is_valid():
		player_at.call(id, at)
	played.append([id, true])


static func _ids(v: Variant) -> Array[StringName]:
	var out: Array[StringName] = []
	if v is String or v is StringName:
		if str(v) != "":
			out.append(StringName(str(v)))
	elif v is Array:
		for x: Variant in v:
			out.append(StringName(str(x)))
	return out


func _action(sig: String, node: Node) -> Variant:
	for w in watched:
		if w["node"] == node:
			return ((w["hook"] as Dictionary).get("signals", {}) as Dictionary).get(sig)
	return null


func _fire0(sig: String, node: Node) -> void:
	run(_action(sig, node), [], node)


func _fire1(a: Variant, sig: String, node: Node) -> void:
	run(_action(sig, node), [a], node)


func _fire2(a: Variant, b: Variant, sig: String, node: Node) -> void:
	run(_action(sig, node), [a, b], node)


func _fire3(a: Variant, b: Variant, c: Variant, sig: String, node: Node) -> void:
	run(_action(sig, node), [a, b, c], node)
