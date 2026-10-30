class_name BattleEngine
extends RefCounted
## Headless, deterministic CTB battle engine. Given the same DB, roster and seed, a battle
## always plays out identically, which is what the balancing simulator and tests rely on.
##
## Flow: setup() -> begin() -> loop { is_party_turn() ? perform()/swap()/escape()
##                                                 : run_enemy_turn() } until outcome != "".
## Time stops between calls: nothing advances while the player is choosing.
## run_enemy_turn() also plays any combatant that is not in control of itself (Berserk or
## Confuse, on either side): is_party_turn() is false for those turns.

signal turn_started(actor: BattleCombatant)
signal action_resolved(result: ActionResult)
signal battle_finished(outcome: StringName)
## After every acted turn (including automatic and idle ones), once its end-of-turn effects
## ran: `changes` lists them in order as {target_id, cause, amount, doom}. cause is &"poison",
## &"regen" (amount < 0 heals, > 0 under Zombie), &"doom_tick" (doom = count left) or &"doom"
## (the count ran out; amount = HP lost). amount follows the hit convention: HP lost.
signal turn_ended(actor: BattleCombatant, changes: Array[Dictionary])
## A turn eaten by Stop or Sleep (reason &"stop" wins if both). Doom still ticks on it, so
## `changes` uses the turn_ended format (doom_tick / doom only).
signal turn_lost(actor: BattleCombatant, reason: StringName, changes: Array[Dictionary])
## Boss mechanics (BossMechanics). Each signal's meaning and arguments: battle_ctb.md "The Drownbell" (VFX hooks).
signal phase_changed(enemy: BattleCombatant, phase_id: StringName)
signal combatants_joined(added: Array[BattleCombatant])
signal charge_started(actor: BattleCombatant, skill_id: StringName, turns: int)
signal charge_broken(enemy: BattleCombatant, skill_id: StringName)
## M4-A2P-022: a restores_part skill mended `enemy`'s part (the charge skill id its creatures.json break_parts keys).
signal part_restored(enemy: BattleCombatant, skill_id: StringName)
signal field_cleared(field_id: StringName, fallen: Array[BattleCombatant])

const OUTCOME_VICTORY := &"victory"
const OUTCOME_DEFEAT := &"defeat"
const OUTCOME_ESCAPED := &"escaped"
## A set piece's objective ends it as a scripted way out (the Reach's last phase, M3-CMB-01): never
## the Escape command, and it counts as surviving the fight (BattleSetPiece; set_piece_battles.md).
const OUTCOME_SCRIPTED_ESCAPE := &"scripted_escape"
const MAX_ACTIVE := 3
## swap_refusal: a hero held by the roots (rooted_turns > 0, M4-A2P-020).
const FAIL_ROOTED := &"rooted"
## Consecutive turns lost to Stop/Sleep with nobody able to act before the battle is ruled a
## stalemate (only reachable with "until cured" durations on everyone; ends as defeat).
const MAX_CONSECUTIVE_LOST_TURNS := 1000

var db: BattleDB
var rng := RandomNumberGenerator.new()
var timeline := CtbTimeline.new()
var party_active: Array[BattleCombatant] = []
var party_reserve: Array[BattleCombatant] = []
var enemies: Array[BattleCombatant] = []
var current: BattleCombatant
var now := 0
var outcome: StringName = &""
var encounter_id: StringName = &""
## Scripted fights forbid escape.
var scripted := false
## Optional hook run once on every party combatant (active and reserve) right after setup()
## builds it from characters.json, e.g. `progress.apply_to` to layer Lattice gains on (SPEC §6.4).
## It receives the BattleCombatant and must stay deterministic. Set it before setup().
var party_modifier := Callable()
## Optional reward hook: (credited ids: Array[StringName]) -> int lume multiplier, e.g.
## `equipment_effects.currency_multiplier` (Full Net). Unset = x1. See currency_award().
var currency_multiplier := Callable()
## Set story flags, passed in before setup() (the engine never reads Game): "requires_flag" skills.
var story_flags: Array[StringName] = []
## Fields in force (a phase row's "field", e.g. &"flood"); a "clears_field" skill ends one.
var fields: Array[StringName] = []
## How the battle opens (BattleOpening: normal, preemptive or ambush). Set it after setup() and
## before begin(); live play uses BattleOpening.choose(self). Normal leaves the rolled ticks be.
var opening: StringName = BattleOpening.NORMAL
## Vowbound summons (SPEC §6.3): the rows and bound ids, and who is on the field. Set it before
## begin(); the default has no Vowbound. See summon() and BattleVowbound.
var vowbound := BattleVowbound.new()
## Set pieces (M3-CMB-01, BattleSetPiece): the scripted timeline entries on the field (no HP; the
## Climb, the Surge, Pell), the ones waiting for a phase ({phase, entry}), each field's turn-start
## rules, the objective and its count, and the encounter's party rules.
var entries: Array[BattleCombatant] = []
var pending_entries: Array[Dictionary] = []
var field_rules: Dictionary = {}
var objective: Dictionary = {}
var objective_count := 0
var locked_active: Array[StringName] = []
var locked_key := ""
## M4-A2P-024 (BattleEcho): the last skill an enemy-side combatant used, for an echo skill to copy. &"" = none yet.
var last_foe_skill: StringName = &""
var unavailable: Array[StringName] = []
var unavailable_key := ""

## Item drops rolled once at victory (item id -> count). See drop_awards().
var _drops: Dictionary = {}


func setup(
	battle_db: BattleDB,
	active_ids: Array[StringName],
	reserve_ids: Array[StringName],
	encounter: StringName,
	rng_seed: int
) -> void:
	db = battle_db
	rng.seed = rng_seed
	timeline.tempo = tempo_rank
	encounter_id = encounter
	opening = BattleOpening.NORMAL
	party_active.clear()
	party_reserve.clear()
	enemies.clear()
	fields.clear()
	var enc: Dictionary = db.encounters.get(encounter, {})
	for cid in BattleSetPiece.available_ids(active_ids, enc):
		party_active.append(_make_party_member(cid))
	for cid in BattleSetPiece.available_ids(reserve_ids, enc):
		party_reserve.append(_make_party_member(cid))
	assert(party_active.size() <= MAX_ACTIVE, "BattleEngine: too many active party members")
	scripted = bool(enc.get("scripted", false))
	BossMechanics.lend_skills(self, enc)
	BossMechanics.forbid_skills(self, enc)
	var n := 0
	for eid: Variant in enc.get("enemies", []):
		n += 1
		var row: Dictionary = db.enemies[StringName(str(eid))]
		enemies.append(BattleCombatant.from_dict(StringName("%s#%d" % [eid, n]), BattleCombatant.TEAM_ENEMY, row))
	BattleSetPiece.setup(self, enc)
	rebuild_roster()


## Starting state for tests and capture fixtures (never play). Call after setup() and before
## begin(). `state` maps a combatant id, or a base enemy id for every copy ("reef_crab"), to
## {hp?: int (clamped to 1..max_hp), statuses?: [{id, duration}], provoked_by?: id,
## swell?: int (clamped to 0..SWELL_MAX)}.
## Statuses go through add_status, so wards and Petrify rules hold.
func apply_fixture(state: Dictionary) -> void:
	for c in party_active + party_reserve + enemies + entries:
		var row: Dictionary = state.get(String(c.id), state.get(String(c.id).get_slice("#", 0), {}))
		if row.has("hp"):
			c.hp = clampi(int(row["hp"]), 1, c.max_hp)
		for st: Variant in row.get("statuses", []):
			var sd: Dictionary = st
			c.add_status(StringName(str(sd.get("id", ""))), int(sd.get("duration", -1)))
		if row.has("provoked_by"):
			c.provoker_id = StringName(str(row["provoked_by"]))
		if row.has("swell"):
			c.swell = clampi(int(row["swell"]), 0, Formulas.SWELL_MAX)


func begin() -> void:
	for c in _field():
		c.next_time = Formulas.initial_ticks(c.agility, rng.randi_range(0, Formulas.base_delay(c.agility)))
		c.participated = c.team == BattleCombatant.TEAM_PARTY
	BattleOpening.apply(opening, party_active, enemies)
	BattleCover.begin(self)
	_advance()


## True when the player chooses the current action: a party member in control of itself.
func is_party_turn() -> bool:
	return is_player_side_turn() and auto_reason(current) == &""


## The current actor is on the party side, whether or not the player controls it (never a scripted
## entry: the Climb and Pell act on their own, through run_enemy_turn()).
func is_player_side_turn() -> bool:
	if outcome != &"" or current == null:
		return false
	return current.team == BattleCombatant.TEAM_PARTY and not current.is_entry()


## The current actor acts on its own this turn (Berserk or Confuse); run_enemy_turn() plays it.
func is_auto_turn() -> bool:
	return outcome == &"" and current != null and auto_reason(current) != &""


## Why `c` is not in control of itself: &"confuse" (wins if both), &"berserk", or &"" if it is.
static func auto_reason(c: BattleCombatant) -> StringName:
	if c.has_status(&"confuse"):
		return &"confuse"
	if c.has_status(&"berserk"):
		return &"berserk"
	return &""


## Provoke: the combatant `actor` must hit with a single-foe skill, or null if it is free to
## choose. Only skills whose target is "single_foe" are forced; the provoker must be alive and
## on the field. The UI uses this to lock the target cursor; perform() rejects anything else.
func forced_target(actor: BattleCombatant, skill_id: StringName) -> BattleCombatant:
	if actor == null or not actor.has_status(&"provoke"):
		return null
	if String(db.skill(skill_id).get("target", "single_foe")) != "single_foe":
		return null
	return _valid_provoker(actor)


## Timeline for the UI. With `skill_id`, shows the order as if `current` used that skill on
## `target`: its rank, any delay push, and any time statuses it inflicts (assumed to land).
func preview(
	skill_id: StringName = &"", target: BattleCombatant = null, count: int = CtbTimeline.PREVIEW_LENGTH
) -> Array[TurnEntry]:
	if skill_id == &"" or current == null:
		return timeline.predict(count)
	var sk := db.skill(skill_id)
	var changes: Dictionary = {}
	var recipient := current if String(sk.get("target", "")) == "self" else target
	if recipient != null:
		# Reflect is deterministic, so the preview shows where the spell will really land.
		recipient = reflect_recipient(current, recipient, sk)
		for inflict: Variant in sk.get("statuses", []):
			var inf: Dictionary = inflict
			var sid := StringName(str(inf["id"]))
			if CtbTimeline.PREVIEW_STATUSES.has(sid):
				var row: Dictionary = db.statuses.get(sid, {})
				if not changes.has(recipient):
					changes[recipient] = {}
				changes[recipient][sid] = int(inf.get("duration", row.get("default_duration", -1)))
	for t in _hit_set(sk, recipient):
		if t.has_status(&"sleep") and _wakes(current, t, sk):
			if not changes.has(t):
				changes[t] = {}
			changes[t][CtbTimeline.WAKES] = 0
		if BossMechanics.would_break(current, t, sk):  # the weak point's last hit (assumed to land)
			if not changes.has(t):
				changes[t] = {}
			changes[t][CtbTimeline.BREAKS_CHARGE] = 0
	return timeline.predict(
		count, current, int(sk.get("rank", Formulas.DEFAULT_RANK)), recipient, int(sk.get("delay_ranks", 0)), changes
	)


## Who `sk` would hit: the (reflected) single recipient, or everyone on the group's side.
func _hit_set(sk: Dictionary, recipient: BattleCombatant) -> Array[BattleCombatant]:
	match String(sk.get("target", "single_foe")):
		"all_foes":
			return living_foes_of(current)
		"all_allies":
			return living_allies_of(current)
		"all_other_allies":
			return living_other_allies_of(current)
	var out: Array[BattleCombatant] = []
	if recipient != null:
		out.append(recipient)
	return out


## Whether `sk` from `actor` would deal HP damage to `t` (assumed to land), which wakes Sleep:
## physical or magical power through a non-immune, non-absorbing affinity, or a heal on a Zombie.
func _wakes(actor: BattleCombatant, t: BattleCombatant, sk: Dictionary) -> bool:
	var kind := String(sk.get("kind", ""))
	if kind == "heal":
		return t.has_status(&"zombie")
	if not kind in ["physical", "magical"] or int(sk.get("power", 0)) <= 0:
		return false
	return Formulas.affinity_hurts_more(t.affinity_for(attack_element(actor, t, sk)), &"immune")


## Executes `skill_id` for the current actor. Ends the actor's turn on success. Fails with
## &"auto_turn" while the actor is Berserk/Confused (call run_enemy_turn() instead).
func perform(skill_id: StringName, targets: Array[BattleCombatant]) -> ActionResult:
	if outcome != &"" or current == null:
		return ActionResult.failed(&"", skill_id, &"battle_over")
	if is_auto_turn():
		return ActionResult.failed(current.id, skill_id, &"auto_turn")
	return _perform(current, skill_id, targets)


## Uses one `item_id` from `items` on `targets` as the current party member's action
## (formulas.md § Items): validates targets, resolves every effect, consumes one item, and
## ends the turn with the item's rank. Fails, costing nothing, with not_your_turn,
## unknown_item, no_item or no_valid_target. Items ignore Silence, Provoke and Reflect.
func use_item(item_id: StringName, targets: Array[BattleCombatant], items: BattleItemSource) -> ActionResult:
	if outcome != &"" or current == null:
		return ActionResult.failed(&"", &"", &"battle_over")
	return BattleItemUse.use(self, item_id, targets, items, _end_turn)


## Item rules (BattleItemRules): who `item` may target, whether it fells a living Zombie, leaves
## `c` standing, or downs it. Kept here as the engine's public names.
static func item_can_target(item: ItemBattleAction, c: BattleCombatant) -> bool:
	return BattleItemRules.can_target(item, c)


static func item_fells(item: ItemBattleAction, c: BattleCombatant) -> bool:
	return BattleItemRules.fells(item, c)


static func item_leaves_standing(item: ItemBattleAction, c: BattleCombatant) -> bool:
	return BattleItemRules.leaves_standing(item, c)


static func item_downs(item: ItemBattleAction, c: BattleCombatant) -> bool:
	return BattleItemRules.downs(item, c)


## Whether the current party member using `item_id` on `targets` would lose on the spot: no
## active member stands once it resolves (a Zombie reviving or healing itself to a KO as the
## last one standing; a group revive that also brings someone back is not a defeat). The last
## foe falling wins first, as in _check_outcome. Read-only; filters targets as use_item() does;
## stone counts as down. False if the use is refused.
func item_defeats_party(item_id: StringName, targets: Array[BattleCombatant], items: BattleItemSource) -> bool:
	return BattleItemUse.defeats_party(self, item_id, targets, items)


## Timeline if the current actor used `item_id` on `target`: the item's rank, its delay push,
## time statuses it adds, a revived ally rejoining, and a target the item downs (item_downs: a
## revived Zombie, or a Zombie a heal item KOs) leaving the order.
func preview_item(
	item_id: StringName, target: BattleCombatant, items: BattleItemSource, count: int = CtbTimeline.PREVIEW_LENGTH
) -> Array[TurnEntry]:
	return BattleItemUse.preview(self, item_id, target, items, count)


## Runs the current enemy's AI turn, a scripted entry's turn (either side), or the current
## Berserk/Confused combatant's automatic turn on either side. Returns null if the player is in
## control of the current turn.
func run_enemy_turn() -> ActionResult:
	if outcome != &"" or current == null:
		return null
	var scripted_actor := current.team == BattleCombatant.TEAM_ENEMY or current.is_entry()
	# A telegraphed skill counts down (or fires) on every acted enemy turn, as the timeline shows.
	var charged := BossMechanics.charged_choice(self, current) if scripted_actor else {}
	if is_auto_turn() and charged.is_empty():
		return _run_auto_turn()
	if not scripted_actor:
		return null
	var choice := charged if not charged.is_empty() else EnemyAI.choose(self, current)
	if choice.is_empty():
		var idle := ActionResult.failed(current.id, &"", &"no_valid_action")
		_end_turn(current, Formulas.DEFAULT_RANK)
		return idle
	var actor := current
	var targets: Array[BattleCombatant] = choice["targets"]
	var result := _perform(actor, choice["skill"], targets)
	if not result.ok and current == actor:
		# Bad data (e.g. not enough MP) must never stall a battle: the enemy loses its turn.
		_end_turn(actor, Formulas.DEFAULT_RANK)
	return result


## Where a skill aimed at `target` really lands. Reflect bounces single-target magic (any
## skill with "magic": true aimed at one other combatant) to the living combatant on the
## other side from the reflector with the lowest HP (ties: field order). A bounced spell is
## never bounced again, so Reflect cannot chain.
func reflect_recipient(actor: BattleCombatant, target: BattleCombatant, sk: Dictionary) -> BattleCombatant:
	if target == null or target == actor or not target.has_status(&"reflect"):
		return target
	if not bool(sk.get("magic", false)):
		return target
	if not String(sk.get("target", "single_foe")) in ["single_foe", "single_ally"]:
		return target
	var best: BattleCombatant = null
	for c in living_foes_of(target):
		if best == null or c.hp < best.hp:
			best = c
	return best if best != null else target


func _perform(actor: BattleCombatant, skill_id: StringName, targets: Array[BattleCombatant]) -> ActionResult:
	var sk := db.skill(skill_id)
	if sk.is_empty() or not actor.skills.has(skill_id):
		return ActionResult.failed(actor.id, skill_id, &"unknown_skill")
	var cost := int(sk.get("mp_cost", 0))
	if actor.mp < cost:
		return ActionResult.failed(actor.id, skill_id, &"no_mp")
	if bool(sk.get("echo", false)):  # M4-A2P-024: Nhoa copies the last enemy action
		sk = BattleEcho.row(self, sk)
		if sk.is_empty():
			return ActionResult.failed(actor.id, skill_id, BattleEcho.FAIL_NOTHING)
	var result := _checked(actor, skill_id, sk, targets)
	BattleEcho.record(self, actor, skill_id, result.ok)
	return result


## A row the current party member need not have learned or pay MP for: a Swell technique,
## already gated and scaled by BattleSwell (SPEC §6.2). Otherwise the checks of perform().
func perform_row(skill_id: StringName, sk: Dictionary, targets: Array[BattleCombatant]) -> ActionResult:
	if outcome != &"" or current == null:
		return ActionResult.failed(&"", skill_id, &"battle_over")
	if not is_party_turn():
		return ActionResult.failed(current.id, skill_id, &"not_your_turn")
	return _checked(current, skill_id, sk, targets)


func _checked(
	actor: BattleCombatant, skill_id: StringName, sk: Dictionary, targets: Array[BattleCombatant]
) -> ActionResult:
	var refused := &"silenced" if bool(sk.get("magic", false)) and actor.has_status(&"silence") else &""
	if refused == &"" and not BattleCycle.allows(actor, skill_id):
		refused = BattleCycle.FAIL_OUT_OF_CYCLE  # M4-A2P-025: not this turn's element
	if refused == &"":
		refused = BossMechanics.refusal(self, sk)
	if refused != &"":
		return ActionResult.failed(actor.id, skill_id, refused)
	var valid := _valid_targets(actor, sk, targets)
	if valid.is_empty():
		return ActionResult.failed(actor.id, skill_id, &"no_valid_target")
	for t in valid:
		if BossMechanics.forbids(actor, sk, t):
			return ActionResult.failed(actor.id, skill_id, BossMechanics.FAIL_FORBIDDEN)
	var forced := forced_target(actor, skill_id)
	if forced != null and valid[0] != forced:
		return ActionResult.failed(actor.id, skill_id, &"provoked")
	return _execute_guarded(actor, skill_id, sk, valid)


## M3-CMB-01: a foe's ward skill lands on its provoker or the ward's coverer instead
## (BattleSetPiece.interceptor), resolved as its "on_cover" row on them; a cover is spent.
func _execute_guarded(
	actor: BattleCombatant, skill_id: StringName, sk: Dictionary, valid: Array[BattleCombatant]
) -> ActionResult:
	var guard := BattleSetPiece.interceptor(self, actor, sk)
	if guard == null:
		return _execute(actor, skill_id, sk, valid, &"")
	var w := ward()
	if w.covered_by == guard.id:
		w.covered_by = &""
	var row := BattleSetPiece.cover_row(self, sk)
	return _execute(actor, skill_id, row, [guard] as Array[BattleCombatant], &"", guard.id)


## Spends the cost, resolves `sk` on already-validated targets (bouncing off Reflect), and
## ends the actor's turn. `intercepted` names who took a ward skill in the ward's place.
func _execute(
	actor: BattleCombatant,
	skill_id: StringName,
	sk: Dictionary,
	targets: Array[BattleCombatant],
	auto: StringName,
	intercepted: StringName = &""
) -> ActionResult:
	actor.mp -= int(sk.get("mp_cost", 0))
	var result := ActionResult.new()
	result.actor_id = actor.id
	result.skill_id = skill_id
	result.auto_reason = auto
	result.intercepted_by = intercepted
	for t in targets:
		var lands := reflect_recipient(actor, t, sk)
		var hit := BattleHits.resolve(self, actor, lands, sk)
		if lands != t:
			hit["reflected_from"] = t.id
		result.hits.append(hit)
	BattleSetPiece.counters(self, actor, sk, result)
	BossMechanics.after_action(self, actor, sk, result)
	action_resolved.emit(result)
	result.end_of_turn = _end_turn(actor, int(sk.get("rank", Formulas.DEFAULT_RANK)))
	return result


## Berserk / Confuse: the combatant uses its basic attack on a target the battle RNG picks
## (formulas.md § Statuses). Berserk hits a random foe (the provoker if Provoked); Confuse
## turns on a random ally other than itself with CONFUSE_ALLY_PCT, otherwise a random foe.
func _run_auto_turn() -> ActionResult:
	var actor := current
	var reason := auto_reason(actor)
	var skill_id := basic_attack(actor)
	var pool: Array[BattleCombatant] = []
	if skill_id != &"":
		pool = BattleAutoTurn.pool(self, actor, reason, skill_id)
	if pool.is_empty():
		var idle := ActionResult.failed(actor.id, skill_id, &"no_valid_action")
		idle.auto_reason = reason
		_end_turn(actor, Formulas.DEFAULT_RANK)
		return idle
	var targets: Array[BattleCombatant] = [pool[rng.randi_range(0, pool.size() - 1)]]
	return _execute(actor, skill_id, db.skill(skill_id), targets, reason)


## The skill a combatant uses when not in control (BattleAutoTurn.basic_attack). &"" if none.
func basic_attack(c: BattleCombatant) -> StringName:
	return BattleAutoTurn.basic_attack(db, c)


## Swaps an active member for a reserve member at no turn cost. The incoming member takes
## over a living outgoing member's slot in the timeline (and the current turn, if it was
## theirs). Replacing a KO'd member, the incoming one acts after a default-rank delay from
## now: time never runs backwards (docs/kb/design/battle_ctb.md).
func swap(out_id: StringName, in_id: StringName) -> bool:
	var idx := _swap_indices(out_id, in_id)
	if idx.x < 0:
		return false
	var out_idx := idx.x
	var in_idx := idx.y
	var leaving := party_active[out_idx]
	var entering := party_reserve[in_idx]
	entering.next_time = _swap_in_time(leaving, entering)
	# A living leaver hands over its slot, delays included; replacing the fallen starts fresh.
	entering.delays_taken = leaving.delays_taken if leaving.is_alive() else 0
	entering.participated = true
	party_active[out_idx] = entering
	party_reserve[in_idx] = leaving
	rebuild_roster()
	_prune_provoke()
	_sync_low_hp()
	if current == leaving:
		current = entering
		turn_started.emit(current)
	return true


## The timeline exactly as preview() would show it right after swap(out_id, in_id), using
## the same rule, without changing any state. Empty when swap() would refuse (not a player
## turn, unknown ids, or a fallen reserve). For the Swap menu's timeline chips (pillar 4).
func preview_swap(out_id: StringName, in_id: StringName, count: int = CtbTimeline.PREVIEW_LENGTH) -> Array[TurnEntry]:
	var idx := _swap_indices(out_id, in_id)
	if idx.x < 0:
		return []
	var leaving := party_active[idx.x]
	var entering := party_reserve[idx.y]
	var roster := _field()
	roster[idx.x] = entering  # party slots come first in _field(), in active order
	var tl := CtbTimeline.new()
	tl.set_roster(roster)
	tl.tempo = timeline.tempo
	return tl.predict(count, null, Formulas.DEFAULT_RANK, null, 0, {}, {entering: _swap_in_time(leaving, entering)})


## Vowbound (SPEC §6.3, battle_ctb.md § Vowbound): the current party member calls `vowbound_id`.
## The whole active party stands down and the Vowbound takes the turn. The caller's end of turn
## runs at once (Poison/Regen, countdowns, Doom, turn_ended; ADR 0027 A3), and its next turn
## waits the call's rank after the party comes back. False, changing nothing, on a refusal.
func summon(vowbound_id: StringName) -> bool:
	var caller := current
	if not vowbound.call_in(self, vowbound_id):
		return false
	vowbound.call_changes = _turn_ticks(caller)  # ADR 0027 A3: the call ends the caller's turn now
	return _field_changed(true)


## On the Vowbound's own turn, sends it away, which spends that turn: the party comes back and
## the next turn begins. False on a refusal (vowbound.dismiss_refusal()).
func dismiss() -> bool:
	if not (vowbound.recall(self, true) and _field_changed(false)):
		return false
	if not _check_outcome():
		_advance()
	return true


## A fallen Vowbound, or one still out at victory, gives the field back to the party.
func _recall() -> bool:
	return vowbound.recall(self, false) and _field_changed(false)


## After a summon changed who stands on the field: the order, Provoke and low-HP statuses, and
## the turn the new actor took over (`took_turn`).
func _field_changed(took_turn: bool) -> bool:
	timeline.set_roster(_field())
	_prune_provoke()
	_sync_low_hp()
	if took_turn:
		turn_started.emit(current)
	return true


## Attempts to flee (never while a Vowbound is out). A failed attempt costs a default-rank turn.
func escape() -> bool:
	if not is_party_turn() or scripted or vowbound.is_out():
		return false
	var chance := Formulas.escape_chance(_mean_agility(party_active), _mean_agility(enemies))
	if rng.randi_range(1, 100) <= chance:
		_finish(OUTCOME_ESCAPED)
		return true
	_end_turn(current, Formulas.DEFAULT_RANK)
	return false


## XP credit rule (formulas.md §XP, BattleSpoils): id -> the encounter's full XP for every party
## member who was ever on the field and is alive at victory. {} otherwise.
func xp_awards() -> Dictionary:
	return BattleSpoils.xp_awards(self)


## Ids credited under the XP rule (participated, alive at victory), in party order.
func credited_ids() -> Array[StringName]:
	var out: Array[StringName] = []
	for cid: StringName in xp_awards():
		out.append(cid)
	return out


## Battle lume (formulas.md § Rewards): the sum of every enemy's `currency`, times the
## currency_multiplier hook for the credited party (x1 when unset). 0 unless victorious.
func currency_award() -> int:
	return BattleSpoils.currency_award(self)


## Items dropped this battle (item id -> count), rolled once at victory (or a scripted escape). {}
## otherwise.
func drop_awards() -> Dictionary:
	return _drops.duplicate() if outcome in BattleSpoils.SPOILS_OUTCOMES else {}


## The element a skill really hits `target` with. The basic Attack ("attack", element "none")
## takes the wearer's equipment attack_elements: the one the target is weakest to, ties to the
## first in slot order. Every other skill keeps its own element.
func attack_element(actor: BattleCombatant, target: BattleCombatant, sk: Dictionary) -> StringName:
	var element := StringName(str(sk.get("element", "none")))
	if str(sk.get("id", "")) != "attack" or element != &"none":
		return element
	var best := element
	for el: Variant in actor.equipment().get("attack_elements", []):
		var cand := StringName(str(el))
		if best == &"none" or Formulas.affinity_hurts_more(target.affinity_for(cand), target.affinity_for(best)):
			best = cand
	return best


## The living foes `c` may target (an untargetable phase leaves a foe off this list; M3-CMB-01).
func living_foes_of(c: BattleCombatant) -> Array[BattleCombatant]:
	var out: Array[BattleCombatant] = []
	for f in _living(enemies if c.team == BattleCombatant.TEAM_PARTY else party_active):
		if not f.untargetable and BattleParts.may_strike(c, f):
			out.append(f)
	return out


func living_allies_of(c: BattleCombatant) -> Array[BattleCombatant]:
	return _living(party_active if c.team == BattleCombatant.TEAM_PARTY else enemies)


## Every living ally of `c` but `c` itself: the reach of an "all_other_allies" skill (M2-CMB-02).
func living_other_allies_of(c: BattleCombatant) -> Array[BattleCombatant]:
	var out := living_allies_of(c)
	out.erase(c)
	return out


func find(cid: StringName) -> BattleCombatant:
	for c in party_active + party_reserve + enemies + vowbound.stood_down + entries:
		if c.id == cid:
			return c
	return null


## The battle's ward entry (the Climb), or null (BattleSetPiece.ward).
func ward() -> BattleCombatant:
	return BattleSetPiece.ward(self)


## Why the current turn's swap would refuse to take `out_id` off the field for a reason the menu
## names: BattleSetPiece.FAIL_LOCKED (Toma holds the stair; locked_key says it), FAIL_ROOTED (a
## root crab's Root Drag holds it: rooted_turns, M4-A2P-020), else &"".
func swap_refusal(out_id: StringName) -> StringName:
	var locked := BattleSetPiece.swap_refusal(self, out_id)
	if locked != &"":
		return locked
	var c := find(out_id)
	if c != null and c.is_alive() and c.rooted_turns > 0 and party_active.has(c):
		return FAIL_ROOTED
	return &""


# --- internals ---------------------------------------------------------------------------


## Pushes `target` back by delay_push() (formulas.md § Time: halved for each earlier delay since
## its last turn; 0 if delay_immune) and counts it. Returns the ticks added.
func push_delay(target: BattleCombatant, ranks: int) -> int:
	var ticks := Formulas.delay_push(target.agility, ranks, target.delays_taken, target.delay_immune)
	target.next_time += ticks
	if ticks > 0:
		target.delays_taken += 1
	return ticks


## Ends `actor`'s acted turn: next delay, Poison/Regen, status countdown (Doom may fell it),
## then turn_ended. Returns the end-of-turn changes (also on ActionResult.end_of_turn).
func _end_turn(actor: BattleCombatant, rank: int) -> Array[Dictionary]:
	actor.next_time = now + Formulas.action_delay(actor.agility, rank, actor.speed_mult())
	actor.delays_taken = 0
	var changes := _turn_ticks(actor)
	BattleSetPiece.on_turn_end(self, actor)
	BossMechanics.check_phases(self)
	if not _check_outcome():
		_advance()
	return changes


## The end of `actor`'s turn that does not move the clock: Poison/Regen, the status countdown
## (Doom may fell it), turns_taken and turn_ended. A Vowbound call runs it for the caller at once
## (ADR 0027 A3); only the caller's next turn waits for the party's return.
func _turn_ticks(actor: BattleCombatant) -> Array[Dictionary]:
	var changes: Array[Dictionary] = []
	if actor.is_alive():
		if actor.has_status(&"poison"):
			changes.append(_change(actor, &"poison", -actor.apply_damage(Formulas.poison_damage(actor.max_hp))))
		if actor.has_status(&"regen"):
			# Zombie: Regen harms
			changes.append(_change(actor, &"regen", -actor.restore_hp(Formulas.regen_heal(actor.max_hp))))
	changes.append_array(_tick(actor))
	actor.turns_taken += 1
	BattleCover.on_turn_end(self, actor)
	BattleCycle.advance(actor)
	turn_ended.emit(actor, changes)
	return changes


## Counts `c`'s statuses down and reports Doom: a doom_tick while it counts, doom when it falls.
func _tick(c: BattleCombatant) -> Array[Dictionary]:
	var out: Array[Dictionary] = []
	var doomed := c.doom_count() > 0
	var hp := c.hp
	if c.tick_statuses():
		out.append(_change(c, &"doom", hp))
	elif doomed:
		var tick := _change(c, &"doom_tick", 0)
		tick["doom"] = c.doom_count()
		out.append(tick)
	return out


static func _change(c: BattleCombatant, cause: StringName, amount: int) -> Dictionary:
	return {"target_id": c.id, "cause": cause, "amount": amount, "doom": 0}


func _advance() -> void:
	current = null
	_prune_provoke()
	_sync_low_hp()
	var lost_turns := 0
	while outcome == &"":
		var actor := timeline.next_actor()
		if actor == null:
			_check_outcome()
			return
		now = actor.next_time
		if actor.has_status(&"stop") or actor.has_status(&"sleep"):
			# The turn is lost; statuses still count down so Stop/Sleep wear off.
			actor.next_time = now + Formulas.action_delay(actor.agility, Formulas.DEFAULT_RANK, actor.speed_mult())
			actor.delays_taken = 0
			var reason := &"stop" if actor.has_status(&"stop") else &"sleep"
			var changes := _tick(actor)  # Doom counts lost turns too
			turn_lost.emit(actor, reason, changes)
			if not actor.is_alive() and _check_outcome():
				return
			_prune_provoke()
			lost_turns += 1
			if lost_turns >= MAX_CONSECUTIVE_LOST_TURNS:
				push_error("BattleEngine: nobody can act (permanent Stop/Sleep); ruling a defeat")
				_finish(OUTCOME_DEFEAT)
			continue
		current = actor
		BattleCover.keep_one(self)  # M4-A2P-021: the visible foes may have fallen since
		BattleSetPiece.on_turn_start(self, actor)
		turn_started.emit(actor)
		return


## The skill row `c`'s turn `ahead` own turns on is predicted to use (CtbTimeline.tempo): its AI's
## for a foe or an automatic (Berserk/Confused) turn; {} (a standard action) for a turn the player chooses.
func tempo_rank(c: BattleCombatant, ahead: int) -> Dictionary:
	if c.team != BattleCombatant.TEAM_ENEMY and auto_reason(c) == &"":
		return {}
	return EnemyAI.predicted_skill(self, c, ahead)


## Petrified combatants count as KO here: is_alive() is false for stone.
## An objective encounter ends only on its objective (BattleSetPiece), or in defeat.
func _check_outcome() -> bool:
	var goal := BattleSetPiece.objective_outcome(self)
	if goal != &"":
		BattleSetPiece.withdraw_standing(self)
		_finish(goal)
	elif _living(enemies).is_empty() and objective.is_empty():
		_finish(OUTCOME_VICTORY)
	elif _living(party_active).is_empty():
		_recall()  # a fallen Vowbound is no defeat, unless the party it hands back has fallen too
		if _living(party_active).is_empty():
			_finish(OUTCOME_DEFEAT)
	return outcome != &""


func _finish(result: StringName) -> void:
	_recall()  # the party, not a Vowbound, is on the field when a battle ends
	outcome = result
	current = null
	if result in BattleSpoils.SPOILS_OUTCOMES:
		_drops = BattleSpoils.roll_drops(self)
	battle_finished.emit(result)


## The enemies.json row id of an enemy combatant ("reef_crab#2" -> &"reef_crab"). The one rule for
## an enemy's id: its row (stats, drops, Read's reveal) and its bestiary entry (Read and victory
## credit, BattleBestiary) both go through it, so they cannot drift if combatant ids change.
static func enemy_id(e: BattleCombatant) -> StringName:
	return StringName(String(e.id).get_slice("#", 0))


func _field() -> Array[BattleCombatant]:
	var out: Array[BattleCombatant] = []
	out.append_array(party_active)
	out.append_array(enemies)
	out.append_array(entries)
	return out


## Filters `targets` to those `sk` may legally hit: alive, deduplicated, on the side its
## "target" field names (never the actor for "all_other_allies"), and exactly one for
## single-target skills.
func _valid_targets(actor: BattleCombatant, sk: Dictionary, targets: Array[BattleCombatant]) -> Array[BattleCombatant]:
	var kind := String(sk.get("target", "single_foe"))
	var out: Array[BattleCombatant] = []
	for t in targets:
		if t == null or not t.is_alive() or out.has(t) or BattleSetPiece.spares(sk, t):
			continue
		var is_foe := t.team != actor.team
		# M3-CMB-01: a ward skill takes only the ward; an entry is no other skill's target (but its own
		# self skills), and nothing targets the untargetable.
		if kind == BattleSetPiece.TARGET_WARD:
			if t.entry_role != BattleSetPiece.ROLE_WARD:
				continue
		elif t.is_entry() and t != actor or is_foe and t.untargetable:
			continue
		if is_foe and not BattleParts.may_strike(actor, t):
			continue  # M4-A2P-023: another hero's part (a group skill passes over it)
		match kind:
			"single_foe", "all_foes":
				if not is_foe:
					continue
			"single_ally", "all_allies", "all_other_allies":
				if is_foe or not party_active.has(t) and t.team == BattleCombatant.TEAM_PARTY:
					continue
				if kind == "all_other_allies" and t == actor:
					continue
			"self":
				if t != actor:
					continue
		out.append(t)
	if kind in ["single_foe", "single_ally", "self", BattleSetPiece.TARGET_WARD] and out.size() > 1:
		out.resize(1)
	return out


## Equipment low-HP auto-statuses follow every HP change: the engine re-checks the field after
## each action, end-of-turn tick and swap.
func _sync_low_hp() -> void:
	for c in _field():
		c.sync_low_hp()


## Combatants whose provoker fell or left the field lose Provoke at once.
func _prune_provoke() -> void:
	for c in _field():
		if c.has_status(&"provoke") and _valid_provoker(c) == null:
			c.statuses.erase(&"provoke")
			c.provoker_id = &""


func _valid_provoker(c: BattleCombatant) -> BattleCombatant:
	if c.provoker_id == &"":
		return null
	for p in _field():
		if p.id == c.provoker_id:
			return p if p.is_alive() and not p.untargetable else null
	return null


## (active index, reserve index) for a legal swap, or (-1, -1) when swap() must refuse.
func _swap_indices(out_id: StringName, in_id: StringName) -> Vector2i:
	if not is_party_turn() or vowbound.is_out():
		return Vector2i(-1, -1)
	var out_idx := _index_of(party_active, out_id)
	var in_idx := _index_of(party_reserve, in_id)
	if out_idx < 0 or in_idx < 0 or not party_reserve[in_idx].is_alive() or swap_refusal(out_id) != &"":
		return Vector2i(-1, -1)
	return Vector2i(out_idx, in_idx)


## The swap rule (docs/kb/design/battle_ctb.md): a living leaver hands over its slot (never
## earlier than now); a fallen one makes the entrant wait a default-rank delay from now.
func _swap_in_time(leaving: BattleCombatant, entering: BattleCombatant) -> int:
	if leaving.is_alive():
		return maxi(leaving.next_time, now)
	return now + Formulas.action_delay(entering.agility, Formulas.DEFAULT_RANK, entering.speed_mult())


## Puts the field (active party, then enemies in order) back on the timeline after it changed.
func rebuild_roster() -> void:
	timeline.set_roster(_field())


## Hero `level` is the fixed value from characters.json (ADR 0012): growth comes only from
## Lattice stats, so a modifier that touches `level` is undone. Flag-locked skills are dropped.
func _make_party_member(cid: StringName) -> BattleCombatant:
	var c := BattleCombatant.from_dict(cid, BattleCombatant.TEAM_PARTY, db.characters[cid])
	var fixed_level := c.level
	if party_modifier.is_valid():
		party_modifier.call(c)
		if c.level != fixed_level:
			push_error("BattleEngine: party_modifier changed %s's level; hero level is fixed (ADR 0012)" % cid)
			c.level = fixed_level
	BossMechanics.lock_skills(c, db, story_flags)
	return c


static func _living(list: Array[BattleCombatant]) -> Array[BattleCombatant]:
	var out: Array[BattleCombatant] = []
	for c in list:
		if c.is_alive():
			out.append(c)
	return out


static func _index_of(list: Array[BattleCombatant], cid: StringName) -> int:
	for i in list.size():
		if list[i].id == cid:
			return i
	return -1


static func _mean_agility(list: Array[BattleCombatant]) -> float:
	var alive := _living(list)
	if alive.is_empty():
		return 0.0
	var total := 0
	for c in alive:
		total += c.agility
	return float(total) / alive.size()
