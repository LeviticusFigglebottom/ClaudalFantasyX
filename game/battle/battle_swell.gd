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


## The "swell" object of `path` (parsed once per path, then shared read-only).
static func load_config(path: String = DATA_PATH) -> Dictionary:
	if not _cache.has(path):
		var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(path))
		var root: Dictionary = parsed if typeof(parsed) == TYPE_DICTIONARY else {}
		if not root.has("swell"):
			push_error("BattleSwell: could not read 'swell' from %s" % path)
		_cache[path] = root.get("swell", {})
	return _cache[path]


## Starts following `battle`: every party member with a swell.json row gets the default mode
## (a mode already set, e.g. carried from the field, is kept) and gauges fill from now on.
func attach(battle: BattleEngine) -> void:
	engine = battle
	for c in engine.party_active + engine.party_reserve:
		if has_swell(c) and c.swell_mode == &"":
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


## Chooses `c`'s fill mode. Refused for a combatant with no Swell or a mode not unlocked yet.
## The gauge keeps its points.
func set_mode(c: BattleCombatant, mode: StringName) -> bool:
	if not has_swell(c) or not unlocked.has(mode):
		return false
	c.swell_mode = mode
	return true


## Makes `mode` choosable (unlocked through play). False if it is unknown or already unlocked.
func unlock_mode(mode: StringName) -> bool:
	if not modes.has(mode) or unlocked.has(mode):
		return false
	unlocked.append(mode)
	return true


## The power bonus (percent) an input result earns: the sum of its grades' bonuses (`input`'s
## "grades"), over at most `beats` grades. Unknown grades earn 0.
static func bonus_pct(input: Dictionary, result: Dictionary) -> int:
	var table: Dictionary = input.get("grades", {})
	var grades: Array = result.get(RESULT_GRADES, [])
	var total := 0
	for i in mini(grades.size(), int(input.get("beats", grades.size()))):
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
## or Formulas.swell_gain over the HP share at its rate.
func _gain(c: BattleCombatant, trigger: StringName, amount: int, ref_max_hp: int) -> void:
	var mode: Dictionary = modes.get(c.swell_mode, {})
	if StringName(str(mode.get("trigger", ""))) != trigger:
		return
	var points := int(mode["flat"]) if mode.has("flat") else Formulas.swell_gain(amount, ref_max_hp, int(mode["rate"]))
	c.swell = Formulas.swell_fill(c.swell, points)


static func _index(rows: Variant) -> Dictionary:
	var out: Dictionary = {}
	for row: Variant in rows as Array:
		var d: Dictionary = row
		out[StringName(str(d["id"]))] = d
	return out
