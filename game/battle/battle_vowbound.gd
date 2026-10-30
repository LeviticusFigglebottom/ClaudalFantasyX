class_name BattleVowbound
extends RefCounted
## Vowbound summons (SPEC §6.3, M2-CMB-04; rules in battle_ctb.md § Vowbound and formulas.md
## § Vowbound). A called Vowbound **replaces the whole active party** on the field, with its own
## HP, MP, skills and Swell; its stats grow from the caller's (Formulas.vowbound_stat).
##
## Headless and Node-free: no random rolls at all. The engine owns one (`BattleEngine.vowbound`)
## and calls it through BattleEngine.summon() and dismiss(); the battle scene reads `summon`,
## `stood_down` and the two signals, and unleashes the finisher with unleash(). Pass the rows
## and the Vowbound the party has bound (from story flags: the engine never reads Game) before
## begin(), e.g. `engine.vowbound = BattleVowbound.new(BattleVowbound.load_config(), known)`.
## One instance serves one battle.

## A Vowbound took the field (the party stood down); it now holds the current turn.
signal called(vowbound: BattleCombatant)
## The Vowbound left the field and the party came back: `fell` when it was KO'd or turned to
## stone (it cannot be called again this battle), otherwise dismissed or the battle was won.
signal departed(vowbound: BattleCombatant, fell: bool)

const DATA_PATH := "res://game/data/battle/vowbound.json"
## Refusals (summon, dismiss, unleash), checked in this order.
const FAIL_BATTLE_OVER := &"battle_over"
const FAIL_NOT_YOUR_TURN := &"not_your_turn"
const FAIL_OUT := &"vowbound_out"
const FAIL_UNKNOWN := &"unknown_vowbound"
const FAIL_NOT_BOUND := &"not_bound"
const FAIL_NOT_CALLER := &"not_caller"
const FAIL_SILENCED := &"silenced"
const FAIL_FALLEN := &"vowbound_fallen"
const FAIL_NONE_OUT := &"no_vowbound"
const FAIL_NOT_FULL := &"swell_not_full"
## The stat keys of a row's "base" and "scale_pct" and the combatant field each one sets.
const STAT_FIELDS := {
	"hp": "max_hp",
	"mp": "max_mp",
	"strength": "strength",
	"magic": "magic",
	"defense": "defense",
	"magic_defense": "magic_defense",
	"agility": "agility",
	"accuracy": "accuracy",
	"evasion": "evasion",
	"luck": "luck",
}

static var _cache: Dictionary = {}

## vowbound.json rows by id.
var rows: Dictionary = {}
## The Vowbound the party may call this battle (bound through the story).
var known: Array[StringName] = []
## The Vowbound on the field, or null.
var summon: BattleCombatant
## The active party that stood down for it, in slot order (KO'd members included).
var stood_down: Array[BattleCombatant] = []
## The caller's end-of-turn changes at the last call (BattleEngine.turn_ended format): the call
## ends the caller's turn at once (ADR 0027 A3), so Poison, Regen and Doom tick then.
var call_changes: Array[Dictionary] = []

## Each stood-down member's ticks left before its turn when the Vowbound was called.
var _offsets: Array[int] = []
## Every Vowbound called this battle, by id: HP, MP, statuses and gauge last while it is away.
var _called: Dictionary = {}


## `config` is the "vowbound" array of vowbound.json (load_config()); `bound` lists the ids the
## party may call.
func _init(config: Array = [], bound: Array[StringName] = []) -> void:
	for row: Variant in config:
		var d: Dictionary = row
		rows[StringName(str(d["id"]))] = d
	known = bound.duplicate()


## The "vowbound" array of `path` (parsed once per path, then shared read-only).
static func load_config(path: String = DATA_PATH) -> Array:
	if not _cache.has(path):
		var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(path))
		var root: Dictionary = parsed if typeof(parsed) == TYPE_DICTIONARY else {}
		if not root.has("vowbound"):
			push_error("BattleVowbound: could not read 'vowbound' from %s" % path)
		_cache[path] = root.get("vowbound", [])
	return _cache[path]


func is_out() -> bool:
	return summon != null


## The Vowbound the current actor may call now, in data order (for the command menu).
func callable_ids(engine: BattleEngine) -> Array[StringName]:
	var out: Array[StringName] = []
	for vid: StringName in rows:
		if refusal(engine, vid) == &"":
			out.append(vid)
	return out


## Why the current actor may not call `vowbound_id` now, or &"" if it may.
func refusal(engine: BattleEngine, vowbound_id: StringName) -> StringName:
	if engine.outcome != &"" or engine.current == null:
		return FAIL_BATTLE_OVER
	if not engine.is_party_turn():
		return FAIL_NOT_YOUR_TURN
	if is_out():
		return FAIL_OUT
	if not rows.has(vowbound_id):
		return FAIL_UNKNOWN
	var fail := &""
	if not known.has(vowbound_id):
		fail = FAIL_NOT_BOUND
	elif StringName(str((rows[vowbound_id] as Dictionary).get("caller", ""))) != engine.current.id:
		fail = FAIL_NOT_CALLER
	elif engine.current.has_status(&"silence"):
		fail = FAIL_SILENCED  # the call is a verse
	elif _called.has(vowbound_id) and not (_called[vowbound_id] as BattleCombatant).is_alive():
		fail = FAIL_FALLEN
	return fail


## Calls `vowbound_id` (BattleEngine.summon does the rest): the active party stands down and
## the Vowbound takes the current turn. The call is the caller's action: its end of turn runs at
## once (BattleEngine.summon, ADR 0027 A3), and it will wait the row's `call_rank` delay once the
## party is back, while every other member keeps the ticks it had left. The first call this
## battle builds the Vowbound from the caller's stats at full HP and MP; a later call brings it
## back as it left. False, changing nothing, on a refusal.
func call_in(engine: BattleEngine, vowbound_id: StringName) -> bool:
	if refusal(engine, vowbound_id) != &"":
		return false
	var caller := engine.current
	if not _called.has(vowbound_id):
		_called[vowbound_id] = build(rows[vowbound_id], vowbound_id, caller)
	var s: BattleCombatant = _called[vowbound_id]
	stood_down = engine.party_active.duplicate()
	_offsets.clear()
	var rank := int((rows[vowbound_id] as Dictionary).get("call_rank", Formulas.DEFAULT_RANK))
	for c in stood_down:
		var wait := c.next_time - engine.now
		if c == caller:
			wait = Formulas.action_delay(c.agility, rank, c.speed_mult())
			c.delays_taken = 0  # it acted: as BattleEngine._end_turn
		_offsets.append(maxi(wait, 0))
	s.next_time = engine.now
	s.delays_taken = 0
	engine.party_active.clear()
	engine.party_active.append(s)
	summon = s
	engine.current = s
	if not engine.action_resolved.is_connected(_on_action_resolved):
		engine.action_resolved.connect(_on_action_resolved)
	called.emit(s)
	return true


## The order right after the current actor calls `vowbound_id` (pillar 4, M2-UI-05; nothing
## changes): the Vowbound takes this turn, then it and the foes act as their ticks fall. The
## party is off the order until it comes back (preview_dismiss shows that). [] on a refusal.
func preview_call(
	engine: BattleEngine, vowbound_id: StringName, count: int = CtbTimeline.PREVIEW_LENGTH
) -> Array[TurnEntry]:
	if refusal(engine, vowbound_id) != &"":
		return []
	var s: BattleCombatant = _called.get(vowbound_id, null)
	if s == null:
		s = build(rows[vowbound_id], vowbound_id, engine.current)
	var roster: Array[BattleCombatant] = [s]
	roster.append_array(engine.enemies)
	roster.append_array(engine.entries)  # the Climb keeps climbing (M3-CMB-01)
	var tl := CtbTimeline.new()
	tl.set_roster(roster)
	tl.tempo = engine.timeline.tempo
	return tl.predict(count, null, Formulas.DEFAULT_RANK, null, 0, {}, {s: engine.now})


## The order right after the Vowbound is dismissed on this turn (pillar 4, M2-UI-05; nothing
## changes): the party is back, the caller after its call delay and the others at the ticks they
## kept. [] when the dismissal would be refused.
func preview_dismiss(engine: BattleEngine, count: int = CtbTimeline.PREVIEW_LENGTH) -> Array[TurnEntry]:
	if dismiss_refusal(engine) != &"":
		return []
	var roster: Array[BattleCombatant] = stood_down.duplicate()
	roster.append_array(engine.enemies)
	roster.append_array(engine.entries)  # the Climb keeps climbing (M3-CMB-01)
	var times: Dictionary = {}
	for i in stood_down.size():
		times[stood_down[i]] = engine.now + _offsets[i]
	var tl := CtbTimeline.new()
	tl.set_roster(roster)
	tl.tempo = engine.timeline.tempo
	return tl.predict(count, null, Formulas.DEFAULT_RANK, null, 0, {}, times)


## Why the current actor may not dismiss the Vowbound now, or &"" if it may: only the Vowbound
## itself, on a turn it controls.
func dismiss_refusal(engine: BattleEngine) -> StringName:
	if engine.outcome != &"" or engine.current == null:
		return FAIL_BATTLE_OVER
	if not is_out():
		return FAIL_NONE_OUT
	if not engine.is_party_turn() or engine.current != summon:
		return FAIL_NOT_YOUR_TURN
	return &""


## The party comes back (BattleEngine.dismiss / _recall do the rest): every stood-down member acts
## its kept ticks after now. A dismissal (`dismissing`, on the Vowbound's own turn) spends that
## turn; when it fell, or the battle was won, the current turn is left alone. False if no
## Vowbound is out, or a dismissal is refused.
func recall(engine: BattleEngine, dismissing: bool) -> bool:
	if dismissing and dismiss_refusal(engine) != &"" or not is_out():
		return false
	var s := summon
	engine.party_active.clear()
	engine.party_active.append_array(stood_down)
	for i in stood_down.size():
		stood_down[i].next_time = engine.now + _offsets[i]
	stood_down.clear()
	_offsets.clear()
	summon = null
	departed.emit(s, not s.is_alive())
	return true


## Why the Vowbound may not unleash its finisher now, or &"" if it may: on its own turn, with
## a full gauge (Silence and targets are checked as for any skill).
func unleash_refusal(engine: BattleEngine) -> StringName:
	var fail := dismiss_refusal(engine)
	if fail == &"" and summon.swell < Formulas.SWELL_MAX:
		fail = FAIL_NOT_FULL
	return fail


## The Vowbound's Swell: its row's finisher, played as its skill row (no interactive input; no
## MP; it need not be learned). On success the gauge empties and the turn ends.
func unleash(engine: BattleEngine, targets: Array[BattleCombatant]) -> ActionResult:
	var fail := unleash_refusal(engine)
	var tid := finisher(summon) if is_out() else &""
	if fail != &"":
		var actor_id := engine.current.id if engine.current != null else &""
		return ActionResult.failed(actor_id, tid, fail)
	var s := summon
	var result := engine.perform_row(tid, engine.db.skill(tid), targets)
	if result.ok:
		s.swell = 0
	return result


## The finisher skill id of a called Vowbound `c` (its row's "swell.technique"), or &"".
func finisher(c: BattleCombatant) -> StringName:
	var swell: Dictionary = _row_of(c).get("swell", {})
	return StringName(str(swell.get("technique", "")))


## A fresh Vowbound combatant from `row`, at the caller's level and full HP and MP: every stat
## is Formulas.vowbound_stat(base, the caller's stat, scale_pct), from the caller as it stands
## in battle (Lattice and gear included; its current HP, MP and statuses do not count).
static func build(row: Dictionary, vowbound_id: StringName, caller: BattleCombatant) -> BattleCombatant:
	var base: Dictionary = row.get("base", {})
	var scale: Dictionary = row.get("scale_pct", {})
	var stats := {"level": caller.level}
	for key: String in STAT_FIELDS:
		var own := int(caller.get(StringName(str(STAT_FIELDS[key]))))
		stats[key] = Formulas.vowbound_stat(int(base.get(key, 0)), own, int(scale.get(key, 0)))
	var d := {"name_key": row.get("name_key", ""), "stats": stats}
	d["skills"] = row.get("skills", [])
	d["affinities"] = row.get("affinities", {})
	d["cycle"] = row.get("cycle", [])  # M4-A2P-025: Kesh's six voices
	return BattleCombatant.from_dict(vowbound_id, BattleCombatant.TEAM_PARTY, d)


## The Vowbound's gauge fills from HP it loses to hits and, by ADR 0027 A1, from the HP it drinks
## by absorbing a hit's element (the hit's "absorbed": the rolled amount, so it counts at full HP
## too; formulas.md § Vowbound): Formulas.swell_gain over its own max HP at its row's
## "swell.rate". A heal does not count. Party Swell gauges never see it (BattleSwell).
func _on_action_resolved(result: ActionResult) -> void:
	if not is_out():
		return
	var swell: Dictionary = _row_of(summon).get("swell", {})
	var rate := int(swell.get("rate", 0))
	for hit in result.hits:
		if StringName(str(hit.get("target_id", ""))) != summon.id:
			continue
		var amount := maxi(int(hit.get("amount", 0)), int(hit.get("absorbed", 0)))
		summon.swell = Formulas.swell_fill(summon.swell, Formulas.swell_gain(amount, summon.max_hp, rate))


## The finisher skill id of the row `vowbound_id` (called or not), or &"".
func finisher_of(vowbound_id: StringName) -> StringName:
	var swell: Dictionary = (rows.get(vowbound_id, {}) as Dictionary).get("swell", {})
	return StringName(str(swell.get("technique", "")))


func _row_of(c: BattleCombatant) -> Dictionary:
	return rows.get(c.id, {}) if c != null else {}
