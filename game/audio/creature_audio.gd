class_name CreatureAudio
extends Node
## The creatures' own voices and movement in battle (M3-AUD-14; docs/kb/tech/audio_runtime.md). BattleAudio adds one
## as its child. **Listens only:** the engine's signals and, by name, the creature models' AnimationPlayers; it never
## writes combat state. game/data/audio/creature_voices.json maps an enemy's base id to its sfx rows:
## - **attack** on the creature's own action (`action_resolved`, the actor's base id);
## - **hurt** on a landed damaging hit that leaves it standing (once per creature kind per action), and **death**
##   when a hit or its own turn (poison) takes it to 0 HP, once until it stands again. Both play `under_db` softer and
##   `delays_ms` after the moment, so they layer under battle_sfx.json's hit and KO sounds instead of doubling them.
##   The moment is the blow's **contact**: when the battle has a choreography (a node under the scope that
##   choreo_sfx.json's hook names, BattleChoreo), its contact signal, the one BattleVfx plays the hit and KO on (at
##   once when actions land instantly); with none, the engine's action_resolved (M3-AUD-800);
## - **idle** when the battle opens (the first voiced enemy) and when creatures join, at most once per
##   `idle_cooldown_ms` per kind;
## - **move** from the model's clips: a node whose script's global class is a `model_classes` key (CreatureActor on
##   the creatures track) is heard through its AnimationPlayer's `animation_started`, `clips` mapping a clip to an
##   event. While no model is heard for a kind, its move plays with its attack (`move_on_action`).
## Plays wait in a queue for their time on the SFX bank's clock (tests flush it with their own clock).

const TABLE := "creature_voices"
const SILENT := "silent"
const ATTACK := &"attack"
const HURT := &"hurt"
const DEATH := &"death"
const IDLE := &"idle"
const MOVE := &"move"

var director: AudioDirector
var engine: BattleEngine
## creature_voices.json.
var data: Dictionary = {}
## Every play, in order, as "<base id>:<event>" (tests).
var played: Array[String] = []
## Base id -> how many of its models are heard now.
var models: Dictionary = {}
## The choreography whose contact times the hurts and deaths (null: the engine's action_resolved does).
var contact_source: Node
var _battle: BattleAudio
var _scope: Node
## [{at: msec, base, event}], in time order.
var _queue: Array[Dictionary] = []
## Combatant id -> true once its death played (cleared when it stands again).
var _dead: Dictionary = {}
## Base id -> msec of its last idle.
var _last_idle: Dictionary = {}


## `scope`: only models under it are heard (the battle's controller; null hears any). `battle`: the BattleAudio
## whose reduced-audio setting this follows (null: never reduced).
func attach(dir: AudioDirector, scope: Node, eng: BattleEngine, battle: BattleAudio = null) -> void:
	director = dir
	engine = eng
	_scope = scope
	_battle = battle
	data = AudioData.table(TABLE)
	if data.is_empty() or eng == null:
		return
	eng.action_resolved.connect(_on_action_resolved)
	eng.turn_ended.connect(_on_turn_ended)
	eng.combatants_joined.connect(_on_joined)
	if is_inside_tree():
		get_tree().node_added.connect(_on_node_added)
		if scope != null:
			for n in scope.find_children("*", "", true, false):
				_on_node_added(n)
				if contact_source == null:
					_hear_contacts(n)
	var first := _first_voiced(eng.enemies)
	if first != "":
		_request(first, IDLE)


## The creature_voices.json row for a combatant id or base id ({} when it has none or is "silent").
func row_for(cid: String) -> Dictionary:
	var row: Variant = (data.get("creatures", {}) as Dictionary).get(BattleVfx.base_id(StringName(cid)), {})
	return row if row is Dictionary else {}


## The sfx row `base` plays for `event` (&"" when none).
func sfx_for(base: String, event: StringName) -> StringName:
	return StringName(str((row_for(base).get("events", {}) as Dictionary).get(String(event), "")))


## Hears `node`'s model clips as creature `base` (its first AnimationPlayer's animation_started). False when it has
## no player with that signal.
func watch_model(node: Node, base: String) -> bool:
	if not is_instance_valid(node) or row_for(base).is_empty():
		return false
	var players := node.find_children("*", "AnimationPlayer", true, false)
	if players.is_empty() or not players[0].has_signal(&"animation_started"):
		return false
	var cb := _on_clip.bind(base)
	if players[0].is_connected(&"animation_started", cb):
		return true
	players[0].connect(&"animation_started", cb)
	models[base] = int(models.get(base, 0)) + 1
	node.tree_exiting.connect(_on_model_exiting.bind(base), CONNECT_ONE_SHOT)
	return true


## The base id property a model node's class names in model_classes ("" when the node is not a model).
func model_base(node: Node) -> String:
	var classes := data.get("model_classes", {}) as Dictionary
	var s := node.get_script() as Script
	while s != null:
		var cls := String(s.get_global_name())
		if classes.has(cls):
			var v: Variant = node.get(StringName(str(classes[cls])))
			return BattleVfx.base_id(StringName(str(v))) if v != null else ""
		s = s.get_base_script()
	return ""


## Plays every queued sound due at `now_ms`.
func flush(now_ms: int) -> void:
	while not _queue.is_empty() and int(_queue[0]["at"]) <= now_ms:
		var q: Dictionary = _queue.pop_front()
		_play(str(q["base"]), q["event"] as StringName)


func _process(_delta: float) -> void:
	if not _queue.is_empty() and director != null and director.sfx != null:
		flush(int(director.sfx.clock.call()))


func _now() -> int:
	return int(director.sfx.clock.call()) if director != null and director.sfx != null else 0


func _request(base: String, event: StringName) -> void:
	if sfx_for(base, event) == &"":
		return
	if _battle != null and _battle.reduced and (data.get("reduced_skip", []) as Array).has(String(event)):
		return
	var now := _now()
	if event == IDLE:
		var cool := int(data.get("idle_cooldown_ms", 0))
		if _last_idle.has(base) and now - int(_last_idle[base]) < cool:
			return
		_last_idle[base] = now
	var at := now + int((data.get("delays_ms", {}) as Dictionary).get(String(event), 0))
	var i := _queue.size()
	while i > 0 and int(_queue[i - 1]["at"]) > at:
		i -= 1
	_queue.insert(i, {"at": at, "base": base, "event": event})


func _play(base: String, event: StringName) -> void:
	var id := sfx_for(base, event)
	if id == &"" or director == null or director.sfx == null:
		return
	var opts := {"pitch": float(row_for(base).get("pitch", 1.0))}
	if event == HURT or event == DEATH:
		opts["volume_db"] = float(data.get("under_db", 0.0))
	if director.play_sfx(id, opts) != null:
		played.append("%s:%s" % [base, event])


func _first_voiced(cs: Array[BattleCombatant]) -> String:
	for c in cs:
		var base := BattleVfx.base_id(c.id)
		if not row_for(base).is_empty():
			return base
	return ""


## Times the hurts and deaths on `n`'s contact signal when `n` is the choreography (choreo_sfx.json's hook, by name).
func _hear_contacts(n: Node) -> void:
	var hook := ChoreoAudio.hook_for(AudioData.table(ChoreoAudio.TABLE), n)
	var sig := StringName(str((hook.get("signals", {}) as Dictionary).get(ChoreoAudio.ROLE_CONTACT, "")))
	if sig == &"" or not n.has_signal(sig):
		return
	contact_source = n
	n.connect(sig, _on_contact)


func _on_action_resolved(result: ActionResult) -> void:
	if result == null or not result.ok:
		return
	var actor := BattleVfx.base_id(result.actor_id)
	if not row_for(actor).is_empty():
		_request(actor, ATTACK)
		if bool(data.get("move_on_action", false)) and int(models.get(actor, 0)) == 0:
			_request(actor, MOVE)
	if not is_instance_valid(contact_source):
		_on_contact(result)


## The blow lands (the choreography's contact, or the action itself when there is none): hurts and deaths.
func _on_contact(result: ActionResult) -> void:
	if result == null or not result.ok:
		return
	var hurt: Dictionary = {}
	for h: Dictionary in result.hits:
		var tid := StringName(str(h.get("target_id", "")))
		if tid == result.actor_id or not bool(h.get("hit", false)) or int(h.get("amount", 0)) <= 0:
			continue
		var base := BattleVfx.base_id(tid)
		var c := engine.find(tid)
		if c == null or row_for(base).is_empty():
			continue
		if c.hp <= 0:
			_died(c)
		elif not hurt.has(base):
			hurt[base] = true
			_dead.erase(tid)
			_request(base, HURT)


func _died(c: BattleCombatant) -> void:
	if _dead.has(c.id):
		return
	_dead[c.id] = true
	_request(BattleVfx.base_id(c.id), DEATH)


func _on_turn_ended(actor: BattleCombatant, _changes: Array[Dictionary]) -> void:
	if actor != null and actor.hp <= 0 and not row_for(String(actor.id)).is_empty():
		_died(actor)


func _on_joined(added: Array[BattleCombatant]) -> void:
	var base := _first_voiced(added)
	if base != "":
		_request(base, IDLE)


func _on_node_added(node: Node) -> void:
	if node.get_script() == null or (_scope != null and not _scope.is_ancestor_of(node)):
		return
	if model_base(node) != "":
		_watch_later.call_deferred(node.get_instance_id())


## Deferred: the model's own children (its GLB and AnimationPlayer) are in the tree by then.
func _watch_later(id: int) -> void:
	var node := instance_from_id(id) as Node
	if node != null and node.is_inside_tree():
		watch_model(node, model_base(node))


func _on_clip(clip: StringName, base: String) -> void:
	var event := StringName(str((data.get("clips", {}) as Dictionary).get(String(clip), "")))
	if event != &"":
		_request(base, event)


func _on_model_exiting(base: String) -> void:
	models[base] = maxi(0, int(models.get(base, 0)) - 1)


func _exit_tree() -> void:
	if is_inside_tree() and get_tree().node_added.is_connected(_on_node_added):
		get_tree().node_added.disconnect(_on_node_added)
