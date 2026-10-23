class_name CtbTimeline
extends RefCounted
## Conditional Turn-Based ordering. Each combatant has an absolute `next_time`; the lowest
## acts next. Ties break by higher agility, then by roster order (stable, deterministic).
## Predictions assume every future action uses DEFAULT_RANK and statuses stay as they are.

const PREVIEW_LENGTH := 16
## Statuses that change when a combatant acts; predictions simulate their countdown. Doom
## also removes the combatant once its count runs out.
const TIMED_STATUSES: Array[StringName] = [&"haste", &"slow", &"stop", &"sleep", &"doom"]
## Statuses a candidate action can inflict that the preview shows: the timed ones, plus
## Petrify, which takes the target off the timeline at once.
const PREVIEW_STATUSES: Array[StringName] = [
	&"haste", &"slow", &"stop", &"sleep", &"doom", BattleCombatant.STATUS_PETRIFY
]
## Pseudo-status for status_changes: the candidate action KOs this unit (e.g. a revive item on
## a Zombie), so it leaves the preview like Petrify.
const FALLS := &"_falls"
## Pseudo-status for status_changes: the candidate action damages this sleeping unit, which
## wakes it (applied before any statuses the action adds).
const WAKES := &"_wakes"

var _roster: Array[BattleCombatant] = []


func set_roster(roster: Array[BattleCombatant]) -> void:
	_roster = roster


## Combatants that occupy the timeline: alive (not KO'd, not petrified) and on the field.
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
## `delay_ranks` x its base delay, so the UI can show how an action reshapes the order.
## `status_changes` ({BattleCombatant: {status: duration}}) previews statuses the candidate
## action would apply (assumed to land): PREVIEW_STATUSES are honoured, others ignored.
## Timed statuses count down per simulated own turn exactly as the engine does, and a Doom
## count that runs out removes the combatant from later entries.
## `time_overrides` ({BattleCombatant: int}) replaces a combatant's next_time for this
## prediction only (BattleEngine.preview_swap uses it; nothing is mutated).
## `revived` lists fallen combatants the candidate action brings back (revive items): they are
## predicted from their time_overrides entry.
func predict(
	count: int = PREVIEW_LENGTH,
	preview_actor: BattleCombatant = null,
	preview_rank: int = Formulas.DEFAULT_RANK,
	delay_target: BattleCombatant = null,
	delay_ranks: int = 0,
	status_changes: Dictionary = {},
	time_overrides: Dictionary = {},
	revived: Array[BattleCombatant] = []
) -> Array[TurnEntry]:
	var sims: Array[Dictionary] = []
	for i in _roster.size():
		var c := _roster[i]
		if not c.is_alive() and not revived.has(c):
			continue
		var changes: Dictionary = status_changes.get(c, {})
		if changes.has(BattleCombatant.STATUS_PETRIFY) or changes.has(FALLS):
			continue
		var timed := _timed_copy(c)
		if changes.has(WAKES):
			timed.erase(&"sleep")
		for sid: StringName in changes:
			_sim_add_status(timed, sid, int(changes[sid]))
		var t: int = time_overrides.get(c, c.next_time)
		var first_is_preview := false
		if c == preview_actor:
			t += Formulas.action_delay(c.agility, preview_rank, _sim_speed(timed))
			first_is_preview = true
			if _sim_tick(timed):
				continue  # Doom runs out at the end of this very action
		if delay_target != null and c == delay_target and delay_ranks > 0:
			t += Formulas.delay_push(c.agility, delay_ranks, c.delays_taken, c.delay_immune)
		sims.append({"c": c, "idx": i, "t": t, "first_preview": first_is_preview, "timed": timed})
	var out: Array[TurnEntry] = []
	while out.size() < count and not sims.is_empty():
		var bi := 0
		for j in range(1, sims.size()):
			if _sim_before(sims[j], sims[bi]):
				bi = j
		var s: Dictionary = sims[bi]
		var c: BattleCombatant = s["c"]
		var timed: Dictionary = s["timed"]
		var skipped := timed.has(&"stop") or timed.has(&"sleep")
		var doom := maxi(int(timed.get(&"doom", 0)), 0)
		out.append(TurnEntry.new(c.id, int(s["t"]), c.team, skipped, bool(s["first_preview"]), doom))
		s["first_preview"] = false
		s["t"] = int(s["t"]) + Formulas.action_delay(c.agility, Formulas.DEFAULT_RANK, _sim_speed(timed))
		if _sim_tick(timed):
			sims.remove_at(bi)
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


## Mirrors BattleCombatant.tick_statuses: returns true when Doom ran out (the unit falls).
static func _sim_tick(timed: Dictionary) -> bool:
	var doomed := int(timed.get(&"doom", 0)) == 1
	for sid: StringName in timed.keys():
		var left: int = timed[sid]
		if left < 0:
			continue
		left -= 1
		if left <= 0:
			timed.erase(sid)
		else:
			timed[sid] = left
	return doomed


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
