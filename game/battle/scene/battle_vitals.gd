class_name BattleVitals
extends RefCounted
## Party HP/MP carry-over for live battles (M1-CMB-08; the save side is M1-ARC-06, see
## docs/kb/tech/architecture.md "Saves" and docs/kb/design/battle_ctb.md "Carried vitals").
##
## A live battle (BattleController with persist_progress on and no fixture) starts from
## Game.state.party_vitals and writes them back when it ends:
##   setup()      composes the Lattice with Game.vitals_modifier() (run last) and builds the engine,
##                then lines up the party (line_up) so a fallen member does not hold an active slot
##                while a living reserve waits.
##   send_back()  emits EventBus.battle_party_returned after a victory or an escape; Game records
##                HP, MP and carried statuses. A defeat records nothing: the run goes back to the
##                last save (or Retry replays the same start), so it never saves an all-KO party.
##                M2-ARC-01: the combatants also carry their Swell gauge and mode, and with the
##                battle's BattleSwell it emits EventBus.battle_swell_returned (unlocks) too.
## Capture fixtures and tests (persist_progress off) never read or write vitals.
## M2-CMB-07: setup() also puts the party's equipped gear between the Lattice and the vitals, and
## sets the engine's currency_multiplier from it (Full Net), as the balance simulator does.
## Glue, not engine core: it only sets the engine's hooks and calls setup().

const KEY_ACTIVE := "active"
const KEY_RESERVE := "reserve"
const KEY_RAISE := "raise"
const KEY_ENCOUNTER := "encounter"
const KEY_SEED := "seed"
const STATUS_STONE := BattleCombatant.STATUS_PETRIFY


## Builds `engine` for `plan` ({active, reserve, encounter, seed}, BattleController._setup). With
## `carry`, the party starts from `state`'s vitals (default: the live Game.state). `progress` may
## be null (no Lattice).
static func setup(
	engine: BattleEngine,
	db: BattleDB,
	plan: Dictionary,
	progress: LatticeProgress,
	carry: bool,
	state: GameStateData = null
) -> void:
	# Order matters: Lattice, then equipment, then the carried vitals LAST, because the vitals clamp HP
	# and MP to the final maxima (review-sweep-G S3 on M1-CMB-08). M2-MNU-02 / M2-CMB-07: a live battle wears
	# the save's gear (EquipmentEffects, owning hooks) and its lume multiplier (Full Net).
	var hooks: Array[Callable] = []
	if progress != null:
		hooks.append(progress.apply_to)
	if carry:
		# M2-CMB-07: a live battle wears the party's gear, and Full Net multiplies its lume.
		var fx := live_gear(state if state != null else Game.state)
		hooks.append(fx.modifier())
		engine.currency_multiplier = func(ids: Array[StringName]) -> int: return fx.currency_multiplier(ids)
		hooks.append(Game.vitals_modifier(state))
	var active: Array[StringName] = plan.get(KEY_ACTIVE, [])
	var reserve: Array[StringName] = plan.get(KEY_RESERVE, [])
	var encounter := StringName(str(plan.get(KEY_ENCOUNTER, "")))
	var rng_seed := int(plan.get(KEY_SEED, 0))
	engine.party_modifier = EquipmentEffects.compose(hooks) if not hooks.is_empty() else Callable()
	engine.setup(db, active, reserve, encounter, rng_seed)
	if not carry:
		return
	var order := line_up(engine.party_active, engine.party_reserve)
	if order.is_empty():
		return
	var raise: Array[StringName] = order[KEY_RAISE]
	if not raise.is_empty():
		hooks.append(raise_modifier(raise))
		engine.party_modifier = EquipmentEffects.compose(hooks)
	# setup() is deterministic and rolls nothing, so building again only moves the members.
	engine.setup(db, order[KEY_ACTIVE], order[KEY_RESERVE], encounter, rng_seed)


## The party's equipped gear in `state` as battle effects (EquipmentEffects over a copy of the
## equipment, so a battle never writes to the save's bag).
static func live_gear(state: GameStateData) -> EquipmentEffects:
	var item_db := ItemDB.load_default()
	return EquipmentEffects.new(item_db, EquipmentBag.new(item_db, state.equipment.duplicate(true)))


## The battle-start lineup rule for carried KO and stone (battle_ctb.md "Carried vitals"):
##   1. Each fallen active member (BattleCombatant.is_alive() false: 0 HP, or stone) trades places
##      with the first living reserve member not yet used, in active-slot and reserve order. The
##      fallen member goes to the reserve in that member's place.
##   2. A fallen member with no living reserve left keeps its slot (revive it, or swap it out).
##   3. If no active member stands after that, nobody in the party does: the active members get
##      up with 1 HP and their stone breaks (KEY_RAISE), so a fight never opens already lost.
## Returns {} when the lineup needs no change, else {active, reserve, raise} as id lists.
static func line_up(active: Array[BattleCombatant], reserve: Array[BattleCombatant]) -> Dictionary:
	var act: Array[StringName] = []
	var res: Array[StringName] = []
	for c in active:
		act.append(c.id)
	for c in reserve:
		res.append(c.id)
	var used: Array[int] = []
	var moved := false
	var standing := false
	for i in active.size():
		if active[i].is_alive():
			standing = true
			continue
		for j in reserve.size():
			if reserve[j].is_alive() and not used.has(j):
				used.append(j)
				act[i] = reserve[j].id
				res[j] = active[i].id
				moved = true
				standing = true
				break
	var raise: Array[StringName] = []
	if not standing:
		raise = act.duplicate()
	if not moved and raise.is_empty():
		return {}
	return {KEY_ACTIVE: act, KEY_RESERVE: res, KEY_RAISE: raise}


## A party_modifier (run after the vitals) that stands `ids` up: at least 1 HP, stone broken.
static func raise_modifier(ids: Array[StringName]) -> Callable:
	var keep := ids.duplicate()
	return func(c: BattleCombatant) -> void:
		if keep.has(c.id):
			c.statuses.erase(STATUS_STONE)
			c.hp = maxi(c.hp, 1)


## After a victory or an escape: hands every party combatant (active, then reserve) to
## EventBus.battle_party_returned, which Game.record_party turns into saved vitals (Swell gauges
## and modes included), then `swell`'s record to EventBus.battle_swell_returned. Returns whether
## it sent them (false for a defeat or an unfinished battle).
static func send_back(engine: BattleEngine, swell: BattleSwell = null) -> bool:
	if engine.outcome != BattleEngine.OUTCOME_VICTORY and engine.outcome != BattleEngine.OUTCOME_ESCAPED:
		return false
	var party: Array = []
	for c in engine.party_active + engine.party_reserve:
		party.append(c)
	EventBus.battle_party_returned.emit(engine.encounter_id, engine.outcome, party)
	if swell != null:
		EventBus.battle_swell_returned.emit(swell.to_saved())
	return true
