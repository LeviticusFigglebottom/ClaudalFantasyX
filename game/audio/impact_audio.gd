class_name ImpactAudio
extends Node
## A blow's weight, heard (M3-AUD-816; ADR 0031; docs/kb/tech/audio_runtime.md "Impact"). The director hands it
## each node that enters the tree; a node whose script's global class (or a base class's, or its `audio_class` meta)
## is a game/data/audio/impact_audio.json `hooks` row (battle-presentation's BattleImpact, M3-BPR-401) has its
## signals connected by name, only when it has them, so this loads and runs without that class. It never writes
## what it hears.
## - `landed(target_id, strength, stop_sec)`: the highest `tiers` row whose min_strength the blow reaches plays
##   (under BattleVfx's element hit, which stays the hit itself). A hit-stop (stop_sec over hitstop.min_sec) ducks
##   `hitstop.duck` for its length plus hold_sec, so the music drops out under the frozen frame.
## - `slowmo_planned(from_sec, sec, factor)`: the sequence that fells the last foe. The swell plays at the
##   slow-mo's start (from_sec of plan time, over the choreography's `speed` when the hooked node's parent has one)
##   and `slowmo.duck` holds for the slowed time (sec / factor).
## Reduced audio (`reduced`): the rows in reduced_skip are not played. Time passes only through advance(delta).

const META_CLASS := &"audio_class"

## Plays a row flat: (id: StringName) -> void.
var player: Callable = Callable()
## Turns a duck reason on or off: (reason: StringName, on: bool) -> void.
var ducker: Callable = Callable()
## True under the Reduced audio setting: () -> bool.
var reduced: Callable = Callable()
var data: Dictionary = {}
## Hook rows by class name.
var hooks: Dictionary = {}
## Every row played, in order (tests).
var played: Array[StringName] = []
## Pending timed events: {at: float, kind: &"play"|&"duck_on"|&"duck_off", id: StringName}.
var _queue: Array[Dictionary] = []
var _clock := 0.0
## Duck reason -> the clock time it ends.
var _duck_until: Dictionary = {}
## Instance ids of the nodes already connected.
var _watched: Dictionary = {}


func _init(table: Dictionary = {}) -> void:
	configure(table)


func configure(table: Dictionary) -> void:
	data = table
	hooks.clear()
	for h: Variant in table.get("hooks", []):
		if h is Dictionary and str((h as Dictionary).get("class", "")) != "":
			hooks[str(h["class"])] = h


func bind_director(dir: AudioDirector) -> void:
	player = func(id: StringName) -> void: dir.play_sfx(id)
	ducker = dir.set_duck
	reduced = func() -> bool: return dir._reduced_audio()


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


func wants(node: Node) -> bool:
	return not hooks.is_empty() and not hook_for(node).is_empty()


## Connects `node`'s landed and slow-mo signals (named in its hook's `signals`), those it has, once.
func watch(node: Node) -> void:
	if not is_instance_valid(node) or not node.is_inside_tree() or _watched.has(node.get_instance_id()):
		return
	_watched[node.get_instance_id()] = true
	var sigs := hook_for(node).get("signals", {}) as Dictionary
	var landed := StringName(str(sigs.get("landed", "")))
	if landed != &"" and UiAudio._arg_count(node, landed) >= 3:
		node.connect(landed, on_landed)
	var slow := StringName(str(sigs.get("slowmo", "")))
	if slow != &"" and UiAudio._arg_count(node, slow) >= 3:
		node.connect(slow, on_slowmo.bind(node))


## The tier row for a blow of `strength` (&"" below every tier).
func tier_for(strength: float) -> StringName:
	var best := &""
	var best_min := -INF
	for t: Dictionary in data.get("tiers", []):
		var lo := float(t.get("min_strength", INF))
		if strength >= lo and lo > best_min:
			best = StringName(str(t.get("sfx", "")))
			best_min = lo
	return best


func on_landed(_target_id: StringName, strength: float, stop_sec: float) -> void:
	_play(tier_for(strength))
	var hs := data.get("hitstop", {}) as Dictionary
	if not hs.is_empty() and stop_sec > float(hs.get("min_sec", 0.0)):
		_duck(StringName(str(hs.get("duck", ""))), _clock, stop_sec + float(hs.get("hold_sec", 0.0)))


func on_slowmo(from_sec: float, sec: float, factor: float, node: Node = null) -> void:
	var cfg := data.get("slowmo", {}) as Dictionary
	if cfg.is_empty():
		return
	var speed := 1.0
	if node != null and is_instance_valid(node) and node.get_parent() != null:
		var v: Variant = node.get_parent().get(&"speed")
		if v is float or v is int:
			speed = maxf(float(v), 0.01)
	var start := _clock + maxf(from_sec, 0.0) / speed
	var slowed := sec / maxf(factor, 0.01)
	_queue.append({"at": start, "kind": &"play", "id": StringName(str(cfg.get("sfx", "")))})
	_duck(StringName(str(cfg.get("duck", ""))), start, slowed + float(cfg.get("hold_sec", 0.0)))


func advance(delta: float) -> void:
	_clock += delta
	for i in range(_queue.size() - 1, -1, -1):
		var e := _queue[i]
		if float(e["at"]) > _clock:
			continue
		_queue.remove_at(i)
		match e["kind"]:
			&"play":
				_play(e["id"] as StringName)
			&"duck_on":
				_set_duck(e["id"] as StringName, true)
	for reason: StringName in _duck_until.keys():
		if _clock >= float(_duck_until[reason]):
			_duck_until.erase(reason)
			_set_duck(reason, false)


func _duck(reason: StringName, start: float, sec: float) -> void:
	if reason == &"" or sec <= 0.0:
		return
	_duck_until[reason] = maxf(float(_duck_until.get(reason, 0.0)), start + sec)
	if start <= _clock:
		_set_duck(reason, true)
	else:
		_queue.append({"at": start, "kind": &"duck_on", "id": reason})


func _set_duck(reason: StringName, on: bool) -> void:
	if ducker.is_valid():
		ducker.call(reason, on)


func _play(id: StringName) -> void:
	if id == &"":
		return
	if reduced.is_valid() and bool(reduced.call()) and String(id) in (data.get("reduced_skip", []) as Array):
		return
	played.append(id)
	if player.is_valid():
		player.call(id)
