class_name BattleSwell
extends RefCounted
## Swell gauges (SPEC §6.2, formulas.md § Swell). Headless and deterministic: no Nodes and no
## RNG. The gauge state lives on each BattleCombatant (`swell`, `swell_mode`); this class holds
## the rules from game/data/battle/swell.json, fills gauges from the engine's action_resolved
## signal, and resolves a technique with its interactive input's result passed in, so tests
## and the simulator never need the input UI.
##
## Use: `var swell := BattleSwell.new(BattleSwell.load_config())`, then `swell.attach(engine)`
## after engine.setup() (and apply_fixture). Hold the instance for the whole battle: a signal
## connection does not keep its RefCounted target alive.
##
## Unlocks through play (M2-CMB-01): swell.json "unlocks" rows count events (the same triggers the
## modes fill from) and call unlock_mode() at their count. The party-wide record of unlocked modes
## and counts goes in and out as plain data (load_saved / to_saved, save v6, M2-ARC-01); the glue
## that reads and writes Game.state is BattleSwellCarry (game/battle/scene/).
##
## For menus (M2-UI-01): mode_rows(c) lists the choosable modes with their keys and which one `c`
## uses, set_mode(c, mode) chooses one, progress_toward(mode) says how far a locked mode is, and
## mode_unlocked fires when play unlocks one.

## A mode became choosable through play (unlock_mode), not while a saved record is loaded.
signal mode_unlocked(mode: StringName)

const DATA_PATH := "res://game/data/battle/swell.json"
const TRIGGER_DAMAGE_TAKEN := &"damage_taken"
const TRIGGER_DAMAGE_DEALT := &"damage_dealt"
const TRIGGER_ALLY_HURT := &"ally_hurt"
const TRIGGER_HEAL_ITEM := &"heal_item"
const TRIGGERS: Array[StringName] = [TRIGGER_DAMAGE_TAKEN, TRIGGER_DAMAGE_DEALT, TRIGGER_ALLY_HURT, TRIGGER_HEAL_ITEM]
const FAIL_NOT_FULL := &"swell_not_full"
const FAIL_UNKNOWN := &"unknown_technique"
const FAIL_CANCELLED := &"swell_cancelled"
## Keys of the input result perform() takes: {cancelled: bool, grades: [grade id, ...]}.
const RESULT_CANCELLED := "cancelled"
const RESULT_GRADES := "grades"
## Keys of the saved record (to_saved / load_saved; GameStateData.swell, save v6).
const SAVED_UNLOCKED := "unlocked"
const SAVED_PROGRESS := "progress"

static var _cache: Dictionary = {}

var engine: BattleEngine
## Mode, input and hero rows from swell.json, by id.
var modes: Dictionary = {}
var inputs: Dictionary = {}
var heroes: Dictionary = {}
## The mode a hero starts in.
var default_mode: StringName = &""
## The modes a player may choose: every `starts_unlocked` mode, plus unlock_mode().
var unlocked: Array[StringName] = []
## Unlock rule rows from swell.json "unlocks", in data order.
var unlock_rules: Array[Dictionary] = []
## Events counted so far per unlock rule id (String keys). Ids no rule has any more are kept as
## loaded, so a later build that restores the rule picks the count back up.
var progress: Dictionary = {}

## Saved unlocked ids that swell.json does not know (kept as saved, never dropped).
var _unknown_unlocked: Array[String] = []

## True while a technique resolves: a Swell never feeds a gauge.
var _resolving := false


## `config` is the "swell" object of swell.json (load_config()).
func _init(config: Dictionary = {}) -> void:
	modes = _index(config.get("modes", []))
	inputs = _index(config.get("inputs", []))
	heroes = _index(config.get("heroes", []))
	default_mode = StringName(str(config.get("default_mode", "")))
	for mid: StringName in modes:
		if bool((modes[mid] as Dictionary).get("starts_unlocked", false)):
			unlocked.append(mid)
	for row: Variant in config.get("unlocks", []):
		unlock_rules.append(row as Dictionary)


## The "swell" object of `path` (parsed once per path, then shared read-only).
static func load_config(path: String = DATA_PATH) -> Dictionary:
	if not _cache.has(path):
		var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(path))
		var root: Dictionary = parsed if typeof(parsed) == TYPE_DICTIONARY else {}
		if not root.has("swell"):
			push_error("BattleSwell: could not read 'swell' from %s" % path)
		_cache[path] = root.get("swell", {})
	return _cache[path]


## Why `config` (load_config()) cannot be trusted with saved Swell state ("" when it can): it
## is missing or torn (no "swell" object), has no modes, or its default mode is not one of them.
## The data-tables gate's `swell` check (DataHealth) closes saving while this is non-empty.
static func config_problem(config: Dictionary) -> String:
	var rows: Variant = config.get("modes", [])
	if typeof(rows) != TYPE_ARRAY or (rows as Array).is_empty():
		return "swell.json is missing, unreadable or lists no modes"
	for row: Variant in rows as Array:
		if (
			typeof(row) == TYPE_DICTIONARY
			and str((row as Dictionary).get("id", "")) == str(config.get("default_mode", ""))
		):
			return ""
	return "swell.json's default_mode is not one of its modes"


## Starts following `battle`: every party member with a swell.json row gets the default mode
## (a mode already set, e.g. carried from the field, is kept while it is choosable) and gauges
## fill from now on.
func attach(battle: BattleEngine) -> void:
	engine = battle
	for c in engine.party_active + engine.party_reserve:
		if has_swell(c) and not unlocked.has(c.swell_mode):
			c.swell_mode = default_mode
	if not engine.action_resolved.is_connected(_on_action_resolved):
		engine.action_resolved.connect(_on_action_resolved)


func has_swell(c: BattleCombatant) -> bool:
	return c != null and c.team == BattleCombatant.TEAM_PARTY and heroes.has(c.id)


func is_full(c: BattleCombatant) -> bool:
	return c != null and c.swell >= Formulas.SWELL_MAX


## The techniques `c` may unleash, in data order (only those the battle's tables define).
func techniques(c: BattleCombatant) -> Array[StringName]:
	var out: Array[StringName] = []
	if not has_swell(c) or engine == null:
		return out
	for tid: Variant in (heroes[c.id] as Dictionary).get("techniques", []):
		if engine.db.skills.has(StringName(str(tid))):
			out.append(StringName(str(tid)))
	return out


func is_technique(c: BattleCombatant, skill_id: StringName) -> bool:
	return techniques(c).has(skill_id)


## True when the Swell command belongs on `c`'s menu: a full gauge and a technique to use.
func is_ready(c: BattleCombatant) -> bool:
	return is_full(c) and c.is_alive() and not techniques(c).is_empty()


## The interactive input row `c` uses (swell.json "inputs"), or {}.
func input_for(c: BattleCombatant) -> Dictionary:
	if not has_swell(c):
		return {}
	return inputs.get(StringName(str((heroes[c.id] as Dictionary).get("input", ""))), {})


## Hero `hero_id`'s input row in a swell.json "swell" object (`config`), or {} (no Swell).
static func input_row_of(config: Dictionary, hero_id: StringName) -> Dictionary:
	for h: Variant in config.get("heroes", []):
		if str((h as Dictionary).get("id", "")) == String(hero_id):
			var input_id := str((h as Dictionary).get("input", ""))
			for i: Variant in config.get("inputs", []):
				if str((i as Dictionary).get("id", "")) == input_id:
					return i as Dictionary
	return {}


## Chooses `c`'s fill mode. Refused for a combatant with no Swell or a mode not unlocked yet.
## The gauge keeps its points.
func set_mode(c: BattleCombatant, mode: StringName) -> bool:
	if not has_swell(c) or not unlocked.has(mode):
		return false
	c.swell_mode = mode
	return true


## Makes `mode` choosable (unlocked through play, or by a story beat) and emits mode_unlocked.
## False if it is unknown or already unlocked.
func unlock_mode(mode: StringName) -> bool:
	if not modes.has(mode) or unlocked.has(mode):
		return false
	unlocked.append(mode)
	mode_unlocked.emit(mode)
	return true


## The modes `c` may choose, in data order: {id, name_key, desc_key, trigger, current}. Empty for
## a combatant with no Swell.
func mode_rows(c: BattleCombatant) -> Array[Dictionary]:
	if not has_swell(c):
		return [] as Array[Dictionary]
	return mode_rows_for(c.id, c.swell_mode)


## mode_rows() for hero `hero_id` using `current` (out of battle: BattleSwellCarry.mode_rows).
func mode_rows_for(hero_id: StringName, current: StringName) -> Array[Dictionary]:
	var out: Array[Dictionary] = []
	if not heroes.has(hero_id):
		return out
	for mid: StringName in modes:
		if not unlocked.has(mid):
			continue
		var row: Dictionary = modes[mid]
		(
			out
			. append(
				{
					"id": mid,
					"name_key": str(row.get("name_key", "")),
					"desc_key": str(row.get("desc_key", "")),
					"trigger": StringName(str(row.get("trigger", ""))),
					"current": current == mid,
				}
			)
		)
	return out


## How far play has come towards unlocking `mode`: {count, need} of its first unlock rule (need 0
## when no rule unlocks it), count == need once it is unlocked.
func progress_toward(mode: StringName) -> Dictionary:
	for rule in unlock_rules:
		if StringName(str(rule.get("mode", ""))) == mode:
			var need := int(rule.get("count", 0))
			var got := need if unlocked.has(mode) else mini(int(progress.get(str(rule.get("id", "")), 0)), need)
			return {"count": got, "need": need}
	return {"count": 0, "need": 0}


## Restores the party-wide record (GameStateData.swell): modes unlocked through play and the
## counts towards the others. Unknown ids are kept for to_saved(); nothing emits mode_unlocked.
func load_saved(record: Dictionary) -> void:
	var ids: Variant = record.get(SAVED_UNLOCKED, [])
	for v: Variant in ids if typeof(ids) == TYPE_ARRAY else []:
		var mid := StringName(str(v))
		if not modes.has(mid):
			if not _unknown_unlocked.has(str(v)):
				_unknown_unlocked.append(str(v))
		elif not unlocked.has(mid):
			unlocked.append(mid)
	var counts: Variant = record.get(SAVED_PROGRESS, {})
	if typeof(counts) == TYPE_DICTIONARY:
		for k: Variant in counts:
			progress[str(k)] = int((counts as Dictionary)[k])


## The record to save: {unlocked: [mode ids unlocked through play, then unknown saved ids],
## progress: {rule id: count}}. Modes that start unlocked are not listed.
func to_saved() -> Dictionary:
	var ids: Array[String] = []
	for mid in unlocked:
		if not bool((modes[mid] as Dictionary).get("starts_unlocked", false)):
			ids.append(String(mid))
	for v in _unknown_unlocked:
		if not ids.has(v):
			ids.append(v)
	return {SAVED_UNLOCKED: ids, SAVED_PROGRESS: progress.duplicate()}


## The power bonus (percent) an input result earns: the sum of its grades' bonuses (`input`'s
## "grades"), over at most as many grades as the input can give (SwellInput.grade_count; `beats`
## for a row of unknown kind). Unknown grades earn 0.
static func bonus_pct(input: Dictionary, result: Dictionary) -> int:
	var table: Dictionary = input.get("grades", {})
	var grades: Array = result.get(RESULT_GRADES, [])
	var made := SwellInput.create(input)
	var cap := made.grade_count() if made != null else int(input.get("beats", grades.size()))
	var total := 0
	for i in mini(grades.size(), cap):
		total += int(table.get(str(grades[i]), 0))
	return total


## Why the current actor may not unleash `technique_id` now, or &"" if it may.
func refusal(technique_id: StringName) -> StringName:
	if engine == null or engine.outcome != &"" or engine.current == null:
		return &"battle_over"
	if not engine.is_party_turn():
		return &"auto_turn" if engine.is_auto_turn() else &"not_your_turn"
	if not is_technique(engine.current, technique_id):
		return FAIL_UNKNOWN
	return &"" if is_full(engine.current) else FAIL_NOT_FULL


## Unleashes `technique_id` for the current party member on `targets`, with the interactive
## input's `result` ({cancelled, grades}). The technique's power is scaled by its input bonus
## (Formulas.swell_power) and it is otherwise played as its skill row (targets, Provoke,
## Reflect, rank). On success the gauge empties and the turn ends; a refusal or a cancelled
## input costs nothing (FAIL_CANCELLED keeps the gauge and the turn).
func perform(technique_id: StringName, targets: Array[BattleCombatant], result: Dictionary) -> ActionResult:
	var fail := refusal(technique_id)
	if fail == &"" and bool(result.get(RESULT_CANCELLED, false)):
		fail = FAIL_CANCELLED
	if fail != &"":
		var actor_id := engine.current.id if engine != null and engine.current != null else &""
		return ActionResult.failed(actor_id, technique_id, fail)
	var actor := engine.current
	var bonus := bonus_pct(input_for(actor), result)
	var row := engine.db.skill(technique_id).duplicate(true)
	row["power"] = Formulas.swell_power(int(row.get("power", 0)), bonus)
	_resolving = true
	var out := engine.perform_row(technique_id, row, targets)
	_resolving = false
	if out.ok:
		actor.swell = 0
		out.swell_bonus_pct = bonus
	return out


## Fills gauges from one resolved action (formulas.md § Swell): HP a party member lost
## (damage_taken; every other living active member: ally_hurt), HP a party member's action took
## from a foe (damage_dealt), and a party member's item use that restored HP or revived
## (heal_item). Misses and heals feed nothing else; a technique feeds nothing.
func _on_action_resolved(result: ActionResult) -> void:
	var actor := engine.find(result.actor_id)
	if _resolving or actor == null:
		return
	var healed := false
	for hit in result.hits:
		var t := engine.find(StringName(str(hit.get("target_id", ""))))
		var amount := int(hit.get("amount", 0))
		healed = healed or amount < 0 or bool(hit.get("revived", false))
		if t == null or amount <= 0:
			continue
		if t.team == BattleCombatant.TEAM_PARTY:
			_gain(t, TRIGGER_DAMAGE_TAKEN, amount, t.max_hp)
			for ally in engine.party_active:
				if ally != t and ally.is_alive():
					_gain(ally, TRIGGER_ALLY_HURT, amount, t.max_hp)
		elif actor.team == BattleCombatant.TEAM_PARTY:
			_gain(actor, TRIGGER_DAMAGE_DEALT, amount, t.max_hp)
	if healed and result.item_id != &"":
		_gain(actor, TRIGGER_HEAL_ITEM, 0, 0)


## Adds `c`'s points for one event when its mode listens to `trigger`: the mode's flat points,
## or Formulas.swell_gain over the HP share at its rate. The event also counts towards unlocks.
func _gain(c: BattleCombatant, trigger: StringName, amount: int, ref_max_hp: int) -> void:
	_count(c, trigger)
	var mode: Dictionary = modes.get(c.swell_mode, {})
	if StringName(str(mode.get("trigger", ""))) != trigger:
		return
	var points := int(mode["flat"]) if mode.has("flat") else Formulas.swell_gain(amount, ref_max_hp, int(mode["rate"]))
	c.swell = Formulas.swell_fill(c.swell, points)


## Counts one `trigger` event of hero `c` towards every unlock rule still locked that listens to it
## ("event"), and only while `c` uses the rule's "while_mode" when it names one. A rule reaching its
## "count" unlocks its mode.
func _count(c: BattleCombatant, trigger: StringName) -> void:
	if not has_swell(c):
		return
	for rule in unlock_rules:
		var mode := StringName(str(rule.get("mode", "")))
		if unlocked.has(mode) or StringName(str(rule.get("event", ""))) != trigger:
			continue
		if rule.has("while_mode") and StringName(str(rule["while_mode"])) != c.swell_mode:
			continue
		var rid := str(rule.get("id", ""))
		progress[rid] = int(progress.get(rid, 0)) + 1
		if int(progress[rid]) >= int(rule.get("count", 0)):
			unlock_mode(mode)


static func _index(rows: Variant) -> Dictionary:
	var out: Dictionary = {}
	for row: Variant in rows as Array:
		var d: Dictionary = row
		out[StringName(str(d["id"]))] = d
	return out
