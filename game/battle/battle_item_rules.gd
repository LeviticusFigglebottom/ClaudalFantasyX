class_name BattleItemRules
extends RefCounted
## Read-only item rules the engine and its previews share (formulas.md § Items). Split out of
## BattleEngine (M1-CMB-04) to keep the engine under the file-length cap; BattleEngine keeps its
## public static item_* names as thin wrappers, so callers did not change.


## Whether `item` may target `c`: the item's own life-state rule (revives take the KO'd;
## stone only takes an item whose cure lists petrify), plus a living Zombie for revive items,
## whom revival fells.
static func can_target(item: ItemBattleAction, c: BattleCombatant) -> bool:
	if item.targets_fallen and c.is_alive() and c.has_status(&"zombie"):
		return true
	return item.can_target(c)


## Whether `item` fells `c` outright instead of acting on it: a revive on a living (Zombie)
## target. BattleEngine resolves items with the same rule, so the UI warning and play agree.
static func fells(item: ItemBattleAction, c: BattleCombatant) -> bool:
	return item.targets_fallen and c.is_alive()


## Whether `c` (a target can_target admits) is_alive right after `item` resolves on it: the
## effects run in order on a sim_copy (items use no RNG).
static func leaves_standing(item: ItemBattleAction, c: BattleCombatant) -> bool:
	if fells(item, c):
		return false
	var probe := c.sim_copy()
	without_delay(item).resolve_on(probe)
	return probe.is_alive()


## Whether `item` takes a standing `c` out of the fight: felled as a Zombie by a revive, KO'd
## by a heal on a Zombie or by damage, or turned to stone.
static func downs(item: ItemBattleAction, c: BattleCombatant) -> bool:
	return c.is_alive() and not leaves_standing(item, c)


## The item without its delay effects: the engine applies delay itself (diminishing returns).
static func without_delay(action: ItemBattleAction) -> ItemBattleAction:
	var a := ItemBattleAction.new()
	a.item_id = action.item_id
	a.name_key = action.name_key
	a.target = action.target
	a.rank = action.rank
	a.targets_fallen = action.targets_fallen
	for eff in action.effects:
		if StringName(str(eff.get("type", ""))) != ItemBattleAction.EFFECT_DELAY:
			a.effects.append(eff)
	return a


static func delay_ranks(action: ItemBattleAction) -> int:
	var total := 0
	for eff in action.effects:
		if StringName(str(eff.get("type", ""))) == ItemBattleAction.EFFECT_DELAY:
			total += int(eff["ranks"])
	return total


## The preview inputs for `action` on `recipient` (preview_item): {changes, overrides, revived,
## delay} for CtbTimeline.predict. `rejoin` maps a combatant to the time it rejoins the order.
static func preview_inputs(action: ItemBattleAction, recipient: BattleCombatant, rejoin: Callable) -> Dictionary:
	var changes: Dictionary = {}
	var overrides: Dictionary = {}
	var revived: Array[BattleCombatant] = []
	var delay := 0
	if recipient != null:
		var mine: Dictionary = {}
		for eff in action.effects:
			match StringName(str(eff.get("type", ""))):
				ItemBattleAction.EFFECT_ADD_STATUS:
					var sid := StringName(str(eff["status"]))
					if CtbTimeline.PREVIEW_STATUSES.has(sid):
						mine[sid] = int(eff["duration"])
				ItemBattleAction.EFFECT_DELAY:
					delay += int(eff["ranks"])
				ItemBattleAction.EFFECT_DAMAGE:
					var aff := recipient.affinity_for(StringName(str(eff.get("element", "none"))))
					if recipient.has_status(&"sleep") and Formulas.affinity_hurts_more(aff, &"immune"):
						mine[CtbTimeline.WAKES] = 0
				ItemBattleAction.EFFECT_CURE:
					if (
						recipient.is_petrified()
						and (eff.get("statuses", []) as Array).has(String(BattleCombatant.STATUS_PETRIFY))
					):
						revived.append(recipient)
						overrides[recipient] = rejoin.call(recipient)
					elif recipient.has_status(&"sleep") and (eff.get("statuses", []) as Array).has("sleep"):
						mine[CtbTimeline.WAKES] = 0
				ItemBattleAction.EFFECT_REVIVE:
					if recipient.hp <= 0:
						revived.append(recipient)
						overrides[recipient] = rejoin.call(recipient)
		if downs(action, recipient):
			mine[CtbTimeline.FALLS] = -1
		changes[recipient] = mine
	return {"changes": changes, "overrides": overrides, "revived": revived, "delay": delay}
