class_name UiAudio
extends Node
## The menus' sounds, by listening (M2-AUD-05; ADR 0031; docs/kb/tech/audio_runtime.md). The director hands it each
## node that enters the tree; a node whose script's global class name has a row in game/data/audio/ui_sfx.json
## `hooks` is watched, and nothing in the menu is written:
## - `signals`: {signal: sfx row}: each named signal plays its row (its arguments are dropped with unbind).
## - `on_enter` / `on_exit`: a row when the menu is attached (deferred, after its _ready) or leaves the tree.
## - `watch`: [{expr, sfx | rise | fall | values | on_true}]: an Expression read once a frame with `node` as its
##   input (and this helper's methods, such as page_with_row, in scope). A change plays `sfx`; `rise` / `fall` when
##   a number goes up or down; `values` maps the new value (as a string) to a row; `on_true` only when the new
##   value is truthy. The first read is the baseline, and a read that fails (a page not built yet) changes nothing.
## One frame plays at most one UI row: the first of `priority` among those asked for (a pop that also moves the
## cursor plays the cancel, not both). The director steps it once a frame, paused tree or not (the field menu
## pauses the tree).

## The meta a node may carry to name its hook instead of its script's class (tests' stand-ins; M3-AUD-15).
const META_CLASS := &"audio_class"

## Plays a row: (id: StringName) -> void. The director sets it to its play_sfx; tests set their own.
var player: Callable = Callable()
## ui_sfx.json's hooks by class name.
var hooks: Dictionary = {}
## Row ids, most important first.
var priority: Array[StringName] = []
## Each watched node: {node, hook, watch: [{expr: Expression, row: Dictionary, last: Variant, seen: bool}]}.
var watched: Array[Dictionary] = []
var _pending: Array[StringName] = []


func _init(table: Dictionary = {}) -> void:
	configure(table)


## Reads a ui_sfx.json document.
func configure(table: Dictionary) -> void:
	hooks.clear()
	for h: Variant in table.get("hooks", []):
		if h is Dictionary and str((h as Dictionary).get("class", "")) != "":
			hooks[str((h as Dictionary)["class"])] = h
	priority.clear()
	for p: Variant in table.get("priority", []):
		priority.append(StringName(str(p)))


## The hook row for `node` ({} when its class has none).
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
	return not hook_for(node).is_empty()


## Connects to `node`'s signals and starts reading its watch expressions.
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
		var argc := _arg_count(node, StringName(sig))
		var play := request.bind(StringName(str(sigs[sig])))
		if argc >= 0:
			node.connect(StringName(sig), play.unbind(argc) if argc > 0 else play)
	if hook.has("on_exit"):
		node.tree_exiting.connect(request.bind(StringName(str(hook["on_exit"]))))
	var exprs: Array[Dictionary] = []
	for row: Variant in hook.get("watch", []):
		var e := Expression.new()
		if row is Dictionary and e.parse(str((row as Dictionary).get("expr", "")), ["node"]) == OK:
			exprs.append({"expr": e, "row": row, "last": null, "seen": false})
	watched.append({"node": node, "hook": hook, "watch": exprs})
	_read(watched[-1], false)
	if hook.has("on_enter"):
		request(StringName(str(hook["on_enter"])))


## Asks for row `id` this frame (the highest-priority ask plays in step()).
func request(id: StringName) -> void:
	if id != &"":
		_pending.append(id)


## Reads every watch, then plays this frame's row. AudioDirector.advance calls it; tests call it directly.
func step() -> void:
	var alive: Array[Dictionary] = []
	for w in watched:
		if is_instance_valid(w["node"]) and (w["node"] as Node).is_inside_tree():
			_read(w, true)
			alive.append(w)
	watched = alive
	if _pending.is_empty():
		return
	var best := _pending[0]
	for id in _pending:
		if _rank(id) < _rank(best):
			best = id
	_pending.clear()
	if player.is_valid():
		player.call(best)


func _read(w: Dictionary, play: bool) -> void:
	for x: Dictionary in w["watch"]:
		var e := x["expr"] as Expression
		var v: Variant = e.execute([w["node"]], self, false)
		if e.has_execute_failed():
			continue
		if x["seen"] and play and typeof(v) == typeof(x["last"]) and v != x["last"]:
			var id := change_row(x["row"], x["last"], v)
			if id != &"":
				request(id)
		elif x["seen"] and play and typeof(v) != typeof(x["last"]):
			request(change_row(x["row"], null, v))
		x["last"] = v
		x["seen"] = true


## The row a watch plays when its value goes from `old` to `now` (&"" for none).
static func change_row(row: Dictionary, old: Variant, now: Variant) -> StringName:
	var values := row.get("values", {}) as Dictionary
	if values.has(str(now)):
		return StringName(str(values[str(now)]))
	if bool(row.get("on_true", false)) and not _truthy(now):
		return &""
	var num := typeof(now) in [TYPE_INT, TYPE_FLOAT] and typeof(old) in [TYPE_INT, TYPE_FLOAT]
	if num and row.has("rise") and float(now) > float(old):
		return StringName(str(row["rise"]))
	if num and row.has("fall") and float(now) < float(old):
		return StringName(str(row["fall"]))
	return StringName(str(row.get("sfx", "")))


static func _truthy(v: Variant) -> bool:
	match typeof(v):
		TYPE_NIL:
			return false
		TYPE_BOOL:
			return v
		TYPE_INT, TYPE_FLOAT:
			return float(v) != 0.0
		TYPE_STRING, TYPE_STRING_NAME:
			return str(v) != ""
		TYPE_OBJECT:
			return is_instance_valid(v)
	return true


func _rank(id: StringName) -> int:
	var i := priority.find(id)
	return i if i >= 0 else priority.size()


## The number of arguments `node`'s signal `sig` carries, or -1 when it has no such signal.
static func _arg_count(node: Object, sig: StringName) -> int:
	if not node.has_signal(sig):
		return -1
	for s: Dictionary in node.get_signal_list():
		if StringName(str(s["name"])) == sig:
			return (s["args"] as Array).size()
	return 0


# --------------------------------------------------------------------------- helpers for watch expressions


## `page`'s instance id when it shows a row whose id is `row_id` (a menu page: an object with `rows`), else 0.
## The Vowbound's own root page has the Dismiss row, so a new such page reads as a new non-zero value.
func page_with_row(page: Variant, row_id: String) -> int:
	if not page is Object or not is_instance_valid(page):
		return 0
	var rows: Variant = (page as Object).get(&"rows")
	if not rows is Array:
		return 0
	for r: Variant in rows:
		if r is Dictionary and str((r as Dictionary).get("id", "")) == row_id:
			return (page as Object).get_instance_id()
	return 0


## The Lattice nodes woken by every traveler of `progress` (a LatticeProgress: `travelers`, each with an `activated`
## dictionary), so showing another hero changes nothing; -1 when it cannot be read (M3-AUD-15).
func lattice_woken(progress: Variant) -> int:
	var tv: Variant = _travelers(progress)
	if tv == null:
		return -1
	var total := 0
	for t: Variant in (tv as Dictionary).values():
		var a: Variant = (t as Object).get(&"activated") if t is Object else null
		if a is Dictionary:
			total += (a as Dictionary).size()
	return total


## Where every traveler of `progress` stands, as one text (a walk changes it; showing another hero does not).
func lattice_places(progress: Variant) -> String:
	var tv: Variant = _travelers(progress)
	if tv == null:
		return ""
	var keys := (tv as Dictionary).keys()
	keys.sort()
	var parts: PackedStringArray = []
	for k: Variant in keys:
		var t: Variant = (tv as Dictionary)[k]
		parts.append("%s@%s" % [k, (t as Object).get(&"position") if t is Object else ""])
	return ",".join(parts)


## The pieces someone wears in `bag` (an EquipmentBag: uids() and wearer_of(uid)); -1 when it cannot be read.
func worn_count(bag: Variant) -> int:
	if not _has(bag, &"uids") or not _has(bag, &"wearer_of"):
		return -1
	var total := 0
	for uid: Variant in (bag as Object).call(&"uids"):
		if str((bag as Object).call(&"wearer_of", uid)) != "":
			total += 1
	return total


## Who wears what in `bag`, and each piece's crafted abilities, as one text (a swap or a craft changes it).
func gear_signature(bag: Variant) -> String:
	if not _has(bag, &"uids") or not _has(bag, &"wearer_of"):
		return ""
	var parts: PackedStringArray = []
	for uid: Variant in (bag as Object).call(&"uids"):
		var abilities: Variant = (bag as Object).call(&"abilities_of", uid) if _has(bag, &"abilities_of") else []
		parts.append("%s:%s:%s" % [uid, (bag as Object).call(&"wearer_of", uid), abilities])
	return ",".join(parts)


static func _has(o: Variant, method: StringName) -> bool:
	return o is Object and is_instance_valid(o) and (o as Object).has_method(method)


static func _travelers(progress: Variant) -> Variant:
	if not progress is Object or not is_instance_valid(progress):
		return null
	var tv: Variant = (progress as Object).get(&"travelers")
	return tv if tv is Dictionary else null
