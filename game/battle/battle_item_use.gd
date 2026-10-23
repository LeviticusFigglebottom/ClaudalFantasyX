class_name BattleItemUse
extends RefCounted
## Item use in battle (formulas.md § Items), split out of BattleEngine (M2-CMB-03). Static and
## headless: every function reads or changes the battle through the engine it is given, and the
## engine keeps the public names (use_item, item_defeats_party, preview_item) and hands in its
## own turn ending, so the turn flow stays in one place.


## One `item_id` used by the current party member: a failed result (not_your_turn, unknown_item,
## no_item or no_valid_target) costing nothing, or the hits with one item consumed, then
## action_resolved and `end_turn` (the engine's: (actor, rank) -> end-of-turn changes).
static func use(
	engine: BattleEngine,
	item_id: StringName,
	targets: Array[BattleCombatant],
	items: BattleItemSource,
	end_turn: Callable
) -> ActionResult:
	var actor := engine.current
	var fail := &""
	var action: ItemBattleAction = null
	if not engine.is_party_turn():
		fail = &"not_your_turn"
	elif items == null or items.action_for(item_id) == null:
		fail = &"unknown_item"
	elif items.count(item_id) <= 0:
		fail = &"no_item"
	else:
		action = items.action_for(item_id)
	var valid: Array[BattleCombatant] = []
	if action != null:
		valid = valid_targets(engine, actor, action, targets)
		if valid.is_empty():
			fail = &"no_valid_target"
	if fail != &"":
		var r := ActionResult.failed(actor.id, &"", fail)
		r.item_id = item_id
		return r
	var result := ActionResult.new()
	result.actor_id = actor.id
	result.item_id = item_id
	for t in valid:
		result.hits.append(_resolve_on(engine, action, t))
	items.consume(item_id)
	engine.action_resolved.emit(result)
	result.end_of_turn = end_turn.call(actor, action.rank)
	return result


## See BattleEngine.item_defeats_party.
static func defeats_party(
	engine: BattleEngine, item_id: StringName, targets: Array[BattleCombatant], items: BattleItemSource
) -> bool:
	if items == null or not engine.is_party_turn():
		return false
	var action := items.action_for(item_id)
	if action == null or items.count(item_id) <= 0:
		return false
	var hit := valid_targets(engine, engine.current, action, targets)
	if hit.is_empty():
		return false
	for e in engine.enemies:
		if _standing_after(action, hit, e):
			for c in engine.party_active:
				if _standing_after(action, hit, c):
					return false
			return true
	return false  # the last foe falls first: victory


static func _standing_after(action: ItemBattleAction, hit: Array[BattleCombatant], c: BattleCombatant) -> bool:
	return BattleEngine.item_leaves_standing(action, c) if hit.has(c) else c.is_alive()


## See BattleEngine.preview_item.
static func preview(
	engine: BattleEngine, item_id: StringName, target: BattleCombatant, items: BattleItemSource, count: int
) -> Array[TurnEntry]:
	var action := items.action_for(item_id) if items != null else null
	var current := engine.current
	if action == null or current == null:
		return engine.timeline.predict(count)
	var recipient := current if action.target == ItemBattleAction.TARGET_SELF else target
	var rejoin := func(c: BattleCombatant) -> int: return rejoin_time(c, engine)
	var p := BattleItemRules.preview_inputs(action, recipient, rejoin)
	var revived: Array[BattleCombatant] = p["revived"]
	return engine.timeline.predict(
		count, current, action.rank, recipient, p["delay"], p["changes"], p["overrides"], revived
	)


## Filters `targets` to those `action` may reach from `actor`: at most one unless it hits a group.
static func valid_targets(
	engine: BattleEngine, actor: BattleCombatant, action: ItemBattleAction, targets: Array[BattleCombatant]
) -> Array[BattleCombatant]:
	var out: Array[BattleCombatant] = []
	for t in targets:
		if t == null or out.has(t) or not BattleEngine.item_can_target(action, t):
			continue
		var ok := false
		match action.target:
			ItemBattleAction.TARGET_SELF:
				ok = t == actor
			ItemBattleAction.TARGET_SINGLE_ALLY, ItemBattleAction.TARGET_ALL_ALLIES:
				ok = engine.party_active.has(t)
			_:
				ok = engine.enemies.has(t)
		if ok:
			out.append(t)
	if not String(action.target).begins_with("all_") and out.size() > 1:
		out.resize(1)
	return out


## One item hit. A revive on a living Zombie fells it; a real revive or a petrify cure rejoins
## the timeline at rejoin_time (time never runs backwards, as for a swap-in) with a fresh
## delay count (formulas.md § Time).
static func _resolve_on(engine: BattleEngine, action: ItemBattleAction, t: BattleCombatant) -> Dictionary:
	if BattleEngine.item_fells(action, t):
		var before := t.hp
		t.fall()
		var felled := {"target_id": t.id, "hit": true, "crit": false, "amount": before, "statuses_added": []}
		felled["revived"] = false
		felled["zombie_felled"] = true
		return felled
	var was_stone := t.is_petrified()
	var res := BattleItemRules.without_delay(action).resolve_on(t)
	res["hit"] = true
	res["crit"] = false
	var ranks := BattleItemRules.delay_ranks(action)
	if ranks > 0 and t.is_alive():
		res["delay_ticks"] = engine.push_delay(t, ranks)
	if bool(res["revived"]) or was_stone and t.is_alive():
		t.next_time = rejoin_time(t, engine)  # back from KO or stone: never before now
		t.delays_taken = 0
		t.participated = true
	return res


## When `c` acts again after coming back mid-battle: a default-rank delay from now.
static func rejoin_time(c: BattleCombatant, engine: BattleEngine) -> int:
	return engine.now + Formulas.action_delay(c.agility, Formulas.DEFAULT_RANK, c.speed_mult())
