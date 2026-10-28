class_name ChoreoAudio
extends Node
## The battle choreography's sound layers (M3-AUD-13; ADR 0031; docs/kb/tech/audio_runtime.md "Choreography
## layers"). The director builds one when a node whose script's global class name has a row in
## game/data/audio/choreo_sfx.json `hooks` enters the tree (the battle-presentation track's BattleChoreo), and frees
## it when that node leaves. **Listens only**: it never writes combat state or moves anything.
##
## - Everything about the other track is reached **by name**: the signals in the hook row (has_signal guards, extra
##   arguments unbound), and the methods current(), style_id_for(), entering(), leaving(), animating(),
##   after_sequence() and the `speed` property (has_method / get guards). So it compiles and runs on a branch
##   without those classes, and a missing piece plays nothing.
## - **Beats** (signal `beat(kind, actor_id)`): approach and return play footfalls spread over the beat; strike
##   starts the style's whoosh so its crest (`peaks`) lands on the contact; ko plays the collapse.
## - **Contact** (signal `contact(result)`, also emitted at once when actions land instantly): the weapon's accent.
##   BattleVfx plays the element hit on the same contact (BattleAudio), so this is the softer layer on top of it,
##   never the hit itself.
## - **Moves without a signal**: a fighter walking on or off its mark and the Vowbound's rise, sink and fall are read
##   from entering() / leaving() once a frame, as each one starts (its clock reaching 0).
## - **The engine** (found as the `engine` of the node's nearest ancestor that has one): the Vowbound's call, which
##   way it left (departed: fell or dismissed), and the Flood phase (the party's brace, after the action playing; its
##   phase and stagger are the choreography's own, from the node's `data` bosses row: flood_for()).
## - **A retry** replaces the choreography node: attach_to frees any listener whose node has left the tree, so one
##   ChoreoAudio hears the battle.
## - **Reduced audio** (UiSettings `reduced_audio`, followed live): `reduced_skip` drops the contact accents and the
##   footfalls, so BattleAudio's one layer per action stays the only one.
## Time passes only through advance(delta): _process calls it; tests call it directly.

const TABLE := "choreo_sfx"
const WEAPON := "@weapon"
const REDUCED_AUDIO := &"reduced_audio"
const SKIP_CONTACT := "contact"
const SKIP_STEPS := "steps"
const ROLE_BEAT := "beat"
const ROLE_CONTACT := "contact"
const BEAT_APPROACH := &"approach"
const BEAT_STRIKE := &"strike"
const BEAT_RETURN := &"return"
const BEAT_KO := &"ko"
const FLOOD_PHASE := "phase"
const FLOOD_STAGGER := "stagger_sec"

## Overrides the class match (tests: stand-ins built at runtime have no global class name): (node) -> class name.
static var matcher: Callable = Callable()

## choreo_sfx.json.
var data: Dictionary = {}
## Plays a row: (id: StringName, opts: Dictionary) -> void. The director sets it to its play_sfx.
var player: Callable = Callable()
## The choreography node listened to, its hook row, and the battle's engine (null when none was found).
var node: Node
var hook: Dictionary = {}
var engine: BattleEngine
## The reduced-audio setting in force.
var reduced := false
## Every row this listener played, in order (tests).
var played: Array[StringName] = []
var _clock := 0.0
## Rows waiting for their time: [{at, id}], in the order asked.
var _queue: Array[Dictionary] = []
## Fighters whose entrance / exit has already sounded (until it ends).
var _entered: Dictionary = {}
var _left: Dictionary = {}
## Vowbound id -> true when it fell (BattleVowbound.departed).
var _fell: Dictionary = {}
var _settings: UiSettings


func _init(table: Dictionary = {}) -> void:
	data = table


func _process(delta: float) -> void:
	advance(delta)


## The hook row of `table` for `n` ({} when its class has none).
static func hook_for(table: Dictionary, n: Node) -> Dictionary:
	if n == null:
		return {}
	var hooks: Dictionary = {}
	for h: Variant in table.get("hooks", []):
		if h is Dictionary and str((h as Dictionary).get("class", "")) != "":
			hooks[str((h as Dictionary)["class"])] = h
	if matcher.is_valid():
		return hooks.get(str(matcher.call(n)), {}) as Dictionary
	var s := n.get_script() as Script
	while s != null:
		var cls := String(s.get_global_name())
		if hooks.has(cls):
			return hooks[cls]
		s = s.get_base_script()
	return {}


## True when the director should attach a listener to `n`.
static func wants(n: Node) -> bool:
	return not hook_for(AudioData.table(TABLE), n).is_empty()


## Builds a listener for `n` under `dir` (the director calls this deferred, after the node's own setup).
static func attach_to(n: Node, dir: AudioDirector) -> ChoreoAudio:
	if not is_instance_valid(n) or not n.is_inside_tree() or dir.listeners.has(n):
		return null
	drop_stale(dir)
	var l := ChoreoAudio.new(AudioData.table(TABLE))
	l.name = "ChoreoAudio"
	l.player = func(id: StringName, opts: Dictionary) -> void: dir.play_sfx(id, opts)
	dir.add_child(l)
	l.attach(n, engine_of(n))
	dir.listeners[n] = l
	return l


## Frees `dir`'s ChoreoAudio listeners whose choreography has left the tree (a retry's old one), before the director's
## own once-a-frame sweep gets to them.
static func drop_stale(dir: AudioDirector) -> void:
	for key: Variant in dir.listeners.keys():
		var l: Variant = dir.listeners[key]
		if not (is_instance_valid(l) and l is ChoreoAudio):
			continue
		if not is_instance_valid(key) or not (key as Node).is_inside_tree():
			dir.listeners.erase(key)
			(l as Node).queue_free()


## The `engine` of `n`'s nearest ancestor (itself first) that has a BattleEngine there; null when none.
static func engine_of(n: Node) -> BattleEngine:
	var p := n
	while p != null:
		var e: Variant = p.get(&"engine")
		if e is BattleEngine:
			return e as BattleEngine
		p = p.get_parent()
	return null


func attach(n: Node, eng: BattleEngine) -> void:
	node = n
	engine = eng
	hook = hook_for(data, n)
	var sigs := hook.get("signals", {}) as Dictionary
	_connect(str(sigs.get(ROLE_BEAT, "")), _on_beat, 2)
	_connect(str(sigs.get(ROLE_CONTACT, "")), _on_contact, 1)
	if engine != null:
		engine.phase_changed.connect(_on_phase_changed)
		engine.vowbound.called.connect(_on_called)
		engine.vowbound.departed.connect(_on_departed)
	_settings = UiSettings.shared()
	if _settings != null:
		_settings.changed.connect(_on_setting_changed)
	_apply_reduced()


## Connects `node`'s signal `sig` to `fn`, which takes the signal's first `takes` arguments (the rest unbound).
func _connect(sig: String, fn: Callable, takes: int) -> void:
	if sig == "" or not node.has_signal(StringName(sig)):
		return
	var argc := -1
	for s: Dictionary in node.get_signal_list():
		if str(s["name"]) == sig:
			argc = (s["args"] as Array).size()
	if argc < takes:
		push_warning("ChoreoAudio: %s.%s has %d arguments, %d needed" % [node.name, sig, argc, takes])
		return
	node.connect(StringName(sig), fn.unbind(argc - takes) if argc > takes else fn)


func _exit_tree() -> void:
	if _settings != null and _settings.changed.is_connected(_on_setting_changed):
		_settings.changed.disconnect(_on_setting_changed)


func _on_setting_changed(key: StringName) -> void:
	if key == REDUCED_AUDIO:
		_apply_reduced()


func _apply_reduced() -> void:
	reduced = _settings != null and bool(_settings.get_value(REDUCED_AUDIO))


func _skips(what: String) -> bool:
	return reduced and (data.get("reduced_skip", []) as Array).has(what)


# --------------------------------------------------------------------------- the beats


func _on_beat(kind: StringName, actor_id: StringName) -> void:
	var plan := _plan()
	if plan.is_empty():
		return
	var srow := style_row(str(plan.get("style", "")))
	var speed := _speed()
	match kind:
		BEAT_APPROACH:
			_steps(
				str(srow.get("approach", "")),
				int(srow.get("approach_steps", 0)),
				float(plan.get("approach_end", 0.0)) / speed,
				actor_id
			)
		BEAT_STRIKE:
			var w := strike_row(srow, weapon_of(actor_id))
			if w != &"":
				var to_contact := (float(plan.get("contact", 0.0)) - float(plan.get("approach_end", 0.0))) / speed
				_at(maxf(to_contact - float((data.get("peaks", {}) as Dictionary).get(String(w), 0.0)), 0.0), w)
		BEAT_RETURN:
			var sec := (float(plan.get("return_end", 0.0)) - float(plan.get("recover_end", 0.0))) / speed
			_steps(str(srow.get("return", "")), int(srow.get("return_steps", 0)), sec, actor_id)
		BEAT_KO:
			for k: Variant in plan.get("kos", []):
				if not _is_vowbound(StringName(str(k))):  # a Vowbound is drawn under instead (vowbound.fall)
					_play(StringName(str(data.get("ko", ""))))
					return


func _on_contact(result: ActionResult) -> void:
	if result == null or not result.ok or _skips(SKIP_CONTACT):
		return
	var id := contact_row(_style_of(result), result)
	if id != &"":
		_play(id)


## The style an action plays: the node's own style_id_for (it works when actions land instantly too), else the plan.
func _style_of(result: ActionResult) -> String:
	if node != null and node.has_method(&"style_id_for"):
		return str(node.call(&"style_id_for", result))
	return str(_plan().get("style", ""))


## choreo_sfx.json's row for style `id` ({} when none).
func style_row(id: String) -> Dictionary:
	return (data.get("styles", {}) as Dictionary).get(id, {}) as Dictionary


## The weapon kind of fighter `cid` (its base id, before any "#n").
func weapon_of(cid: StringName) -> String:
	var base := String(cid).get_slice("#", 0)
	return str((data.get("weapons", {}) as Dictionary).get(base, data.get("weapon_default", "")))


## The whoosh a style's strike plays for `weapon` (&"" for none).
func strike_row(srow: Dictionary, weapon: String) -> StringName:
	var by := srow.get("strike_by_weapon", {}) as Dictionary
	return StringName(str(by[weapon] if by.has(weapon) else srow.get("strike", "")))


## The accent `result`'s contact plays in style `style_id` (&"" for none): the skill's own row, else the style's
## (by weapon, or the weapon's accent for "@weapon"); a row that needs a hit plays only when a blow landed for damage.
func contact_row(style_id: String, result: ActionResult) -> StringName:
	var skills := data.get("skills", {}) as Dictionary
	if skills.has(String(result.skill_id)):
		return StringName(str(skills[String(result.skill_id)]))
	var srow := style_row(style_id)
	var weapon := weapon_of(result.actor_id)
	var by := srow.get("contact_by_weapon", {}) as Dictionary
	var row := str(by[weapon] if by.has(weapon) else srow.get("contact", ""))
	var needs := bool(srow.get("needs_hit", str(srow.get("contact", "")) == WEAPON))
	if row == WEAPON:
		row = str((data.get("accents", {}) as Dictionary).get(weapon, ""))
	if row == "" or (needs and not landed(result)):
		return &""
	return StringName(row)


## True when one of `result`'s hits landed for damage on someone other than the actor.
static func landed(result: ActionResult) -> bool:
	for h: Dictionary in result.hits:
		if bool(h.get("hit", true)) and int(h.get("amount", 0)) > 0:
			if StringName(str(h.get("target_id", ""))) != result.actor_id:
				return true
	return false


# --------------------------------------------------------------------------- the engine


func _on_called(v: BattleCombatant) -> void:
	if _animating():
		_play(StringName(str((data.get("vowbound", {}) as Dictionary).get("call", ""))))
		if v != null:
			_layer(v.id, "call")


func _on_departed(v: BattleCombatant, fell: bool) -> void:
	if v != null:
		_fell[v.id] = fell


func _on_phase_changed(enemy: BattleCombatant, phase_id: StringName) -> void:
	var flood := flood_for(enemy)
	if String(phase_id) != str(flood.get(FLOOD_PHASE, "")) or not _animating():
		return
	var brace := _brace.bind(float(flood.get(FLOOD_STAGGER, 0.0)))
	if is_instance_valid(node) and node.has_method(&"after_sequence"):
		node.call(&"after_sequence", brace)
	else:
		brace.call()


## choreo_sfx.json `flood`, with the phase and stagger the choreography plays for `enemy`: its node's `data`
## (choreo.json) `bosses[<enemy base id>].flood` (BattleBossChoreo's brace), so the sound keeps the motion's timing.
func flood_for(enemy: BattleCombatant) -> Dictionary:
	var out := (data.get("flood", {}) as Dictionary).duplicate()
	var table: Variant = node.get(&"data") if is_instance_valid(node) and enemy != null else null
	if table is Dictionary:
		var bosses := (table as Dictionary).get("bosses", {}) as Dictionary
		var row: Variant = bosses.get(String(enemy.id).get_slice("#", 0), {})
		var f: Variant = (row as Dictionary).get("flood", {}) if row is Dictionary else {}
		for k: String in [FLOOD_PHASE, FLOOD_STAGGER]:
			if f is Dictionary and (f as Dictionary).has(k):
				out[k] = (f as Dictionary)[k]
	return out


## The party braces against the water in slot order, `stagger` plan seconds apart (BattleBossChoreo's brace; a
## fallen member takes no accent there, so it makes no sound here).
func _brace(stagger: float) -> void:
	if engine == null:
		return
	var id := StringName(str((data.get("flood", {}) as Dictionary).get("sfx", "")))
	for i in engine.party_active.size():
		if engine.party_active[i].hp > 0:
			_at(stagger * i / _speed(), id)


# --------------------------------------------------------------------------- time, entrances and exits


func advance(delta: float) -> void:
	_clock += delta
	if not _queue.is_empty():
		var due: Array[Dictionary] = []
		var rest: Array[Dictionary] = []
		for q in _queue:
			if float(q["at"]) <= _clock + 0.000001:
				due.append(q)
			else:
				rest.append(q)
		_queue = rest
		for q in due:
			_play(StringName(q["id"]))
	_poll()


func _poll() -> void:
	if not is_instance_valid(node) or not node.has_method(&"entering") or not node.has_method(&"leaving"):
		return
	for cid in _ids():
		_watch(cid, node.call(&"entering", cid) as Dictionary, _entered, _on_entered)
		_watch(cid, node.call(&"leaving", cid) as Dictionary, _left, _on_left)


## Calls `fn(cid, move)` once when `move` (an entrance or exit) reaches its start; forgets it when it ends.
func _watch(cid: StringName, move: Dictionary, seen: Dictionary, fn: Callable) -> void:
	if move.is_empty():
		seen.erase(cid)
	elif float(move.get("t", -1.0)) >= 0.0 and not seen.has(cid):
		seen[cid] = true
		fn.call(cid, move)


func _on_entered(cid: StringName, move: Dictionary) -> void:
	var sec := float((move.get("spec", {}) as Dictionary).get("sec", 0.0))
	if _is_vowbound(cid):
		var vb := data.get("vowbound", {}) as Dictionary
		_play(StringName(str(vb.get("rise_long" if sec >= float(vb.get("long_sec", INF)) else "rise", ""))))
		_layer(cid, "rise")
		return
	var row := data.get("enter", {}) as Dictionary
	_steps(str(row.get("sfx", "")), int(row.get("steps", 0)), sec / _speed(), cid)


func _on_left(cid: StringName, move: Dictionary) -> void:
	if _is_vowbound(cid):
		var vb := data.get("vowbound", {}) as Dictionary
		var fell := bool(_fell.get(cid, false))
		_play(StringName(str(vb.get("fall" if fell else "sink", ""))))
		_layer(cid, "fall" if fell else "sink")
		return
	var row := data.get("step_off", {}) as Dictionary
	var sec := float((move.get("spec", {}) as Dictionary).get("sec", 0.0))
	_steps(str(row.get("sfx", "")), int(row.get("steps", 0)), sec / _speed(), cid)


## Every fighter that can walk on or off: the party (active, reserve, stood down) and the Vowbound.
func _ids() -> Array[StringName]:
	var out: Array[StringName] = []
	if engine == null:
		return out
	for c: BattleCombatant in engine.party_active + engine.party_reserve + engine.vowbound.stood_down:
		if c != null and not out.has(c.id):
			out.append(c.id)
	for vid: Variant in engine.vowbound.rows:
		if not out.has(StringName(str(vid))):
			out.append(StringName(str(vid)))
	return out


## A Vowbound's own sound over the shared row for `moment` (call, rise, sink, fall): choreo_sfx.json
## `vowbound.layers.<id>` (M3-AUD-846: Ilun's net-float and wings). A missing key plays nothing.
func _layer(cid: StringName, moment: String) -> void:
	var layers := (data.get("vowbound", {}) as Dictionary).get("layers", {}) as Dictionary
	var row := layers.get(String(cid), {}) as Dictionary
	_play(StringName(str(row.get(moment, ""))))


func _is_vowbound(cid: StringName) -> bool:
	return engine != null and engine.vowbound.rows.has(cid)


## `count` footfalls of `row` spread evenly over `sec` (none for a fighter in no_steps, or under reduced audio).
func _steps(row: String, count: int, sec: float, cid: StringName) -> void:
	if row == "" or count <= 0 or sec <= 0.0 or _skips(SKIP_STEPS):
		return
	if (data.get("no_steps", []) as Array).has(String(cid).get_slice("#", 0)):
		return
	for i in count:
		_at(sec * i / count, StringName(row))


func _at(delay: float, id: StringName) -> void:
	if id == &"":
		return
	if delay <= 0.0:
		_play(id)
	else:
		_queue.append({"at": _clock + delay, "id": id})


func _play(id: StringName) -> void:
	if id == &"":
		return
	if player.is_valid():
		player.call(id, {})
	played.append(id)


func _plan() -> Dictionary:
	if is_instance_valid(node) and node.has_method(&"current"):
		var p: Variant = node.call(&"current")
		if p is Dictionary:
			return p
	return {}


func _speed() -> float:
	var s: Variant = node.get(&"speed") if is_instance_valid(node) else null
	return maxf(float(s), 0.01) if typeof(s) in [TYPE_FLOAT, TYPE_INT] else 1.0


func _animating() -> bool:
	if is_instance_valid(node) and node.has_method(&"animating"):
		return bool(node.call(&"animating"))
	return true
