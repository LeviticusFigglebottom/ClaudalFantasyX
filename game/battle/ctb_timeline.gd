class_name CtbTimeline
extends RefCounted
## Conditional Turn-Based ordering. Each combatant has an absolute `next_time`; the lowest
## acts next. Ties break by higher agility, then by roster order (stable, deterministic).
## Predictions assume every future action uses DEFAULT_RANK and statuses stay as they are.

const PREVIEW_LENGTH := 16
## Statuses that change when a combatant acts; predictions simulate their countdown.
const TIMED_STATUSES: Array[StringName] = [&"haste", &"slow", &"stop", &"sleep"]

var _roster: Array[BattleCombatant] = []


func set_roster(roster: Array[BattleCombatant]) -> void:
	_roster = roster


## Combatants that occupy the timeline: alive and on the field.
func eligible() -> Array[BattleCombatant]:
	var out: Array[BattleCombatant] = []
	for c in _roster:
		if c.is_alive():
			out.append(c)
	return out


func next_actor() -> BattleCombatant:
	var best: BattleCombatant = null
	var best_idx := -1
	for i in _roster.size():
		var c := _roster[i]
		if not c.is_alive():
			continue
		if best == null or _before(c, i, best, best_idx):
			best = c
			best_idx = i
	return best


## Predicts the next `count` turns. If `preview_actor` is set, that combatant is assumed to
## act right now with `preview_rank`, and `delay_target` (optional) is pushed back by
## `delay_ranks` × its base delay, so the UI can show how an action reshapes the order.
## `status_changes` ({BattleCombatant: {status: duration}}) previews time statuses the
## candidate action would apply (assumed to land). Timed statuses (Haste, Slow, Stop, Sleep)
## count down per simulated own turn exactly as the engine does; other statuses are ignored.
func predict(
	count: int = PREVIEW_LENGTH,
	preview_actor: BattleCombatant = null,
	preview_rank: int = Formulas.DEFAULT_RANK,
	delay_target: BattleCombatant = null,
	delay_ranks: int = 0,
	status_changes: Dictionary = {}
) -> Array[TurnEntry]:
	var sims: Array[Dictionary] = []
	for i in _roster.size():
		var c := _roster[i]
		if not c.is_alive():
			continue
		var timed := _timed_copy(c)
		for sid: StringName in status_changes.get(c, {}):
			_sim_add_status(timed, sid, int(status_changes[c][sid]))
		var t := c.next_time
		var first_is_preview := false
		if c == preview_actor:
			t = c.next_time + Formulas.action_delay(c.agility, preview_rank, _sim_speed(timed))
			_sim_tick(timed)
			first_is_preview = true
		if delay_target != null and c == delay_target and delay_ranks > 0:
			t += Formulas.base_delay(c.agility) * delay_ranks
		sims.append({"c": c, "idx": i, "t": t, "first_preview": first_is_preview, "timed": timed})
	var out: Array[TurnEntry] = []
	if sims.is_empty():
		return out
	while out.size() < count:
		var bi := 0
		for j in range(1, sims.size()):
			if _sim_before(sims[j], sims[bi]):
				bi = j
		var s: Dictionary = sims[bi]
		var c: BattleCombatant = s["c"]
		var timed: Dictionary = s["timed"]
		var skipped := timed.has(&"stop") or timed.has(&"sleep")
		out.append(TurnEntry.new(c.id, int(s["t"]), c.team, skipped, bool(s["first_preview"])))
		s["first_preview"] = false
		s["t"] = int(s["t"]) + Formulas.action_delay(c.agility, Formulas.DEFAULT_RANK, _sim_speed(timed))
		_sim_tick(timed)
	return out


## Copies the time-relevant statuses of `c` ({status: turns left, -1 = until cured}).
static func _timed_copy(c: BattleCombatant) -> Dictionary:
	var out: Dictionary = {}
	for sid: StringName in TIMED_STATUSES:
		if c.has_status(sid):
			out[sid] = int(c.statuses[sid])
	return out


## Mirrors BattleCombatant.add_status (Haste and Slow replace each other).
static func _sim_add_status(timed: Dictionary, sid: StringName, duration: int) -> void:
	if not TIMED_STATUSES.has(sid):
		return
	timed[sid] = duration
	if sid == &"haste":
		timed.erase(&"slow")
	elif sid == &"slow":
		timed.erase(&"haste")


## Mirrors BattleCombatant.speed_mult.
static func _sim_speed(timed: Dictionary) -> float:
	var m := 1.0
	if timed.has(&"haste"):
		m *= Formulas.HASTE_SPEED_MULT
	if timed.has(&"slow"):
		m *= Formulas.SLOW_SPEED_MULT
	return m


## Mirrors BattleCombatant.tick_statuses.
static func _sim_tick(timed: Dictionary) -> void:
	for sid: StringName in timed.keys():
		var left: int = timed[sid]
		if left < 0:
			continue
		left -= 1
		if left <= 0:
			timed.erase(sid)
		else:
			timed[sid] = left


static func _before(a: BattleCombatant, ai: int, b: BattleCombatant, bi: int) -> bool:
	if a.next_time != b.next_time:
		return a.next_time < b.next_time
	if a.agility != b.agility:
		return a.agility > b.agility
	return ai < bi


static func _sim_before(a: Dictionary, b: Dictionary) -> bool:
	if int(a["t"]) != int(b["t"]):
		return int(a["t"]) < int(b["t"])
	var ca: BattleCombatant = a["c"]
	var cb: BattleCombatant = b["c"]
	if ca.agility != cb.agility:
		return ca.agility > cb.agility
	return int(a["idx"]) < int(b["idx"])
