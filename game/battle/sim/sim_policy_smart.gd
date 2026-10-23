class_name SimPolicySmart
extends SimPolicyRoleAnswer
## "Smart": role answer, plus three habits of a careful player.
## 1. A KO'd or petrified active member is replaced at once by a living reserve (preferring
##    one that answers a living foe).
## 2. A healer heals the most hurt active ally below heal_below_pct of max HP.
## 3. A healer stays on the field while any active ally is below keep_healer_below_pct.
## 4. Items: with no healer acting, a heal item goes to that most hurt ally; a fallen active
##    member with no reserve left to replace them gets a revive item.
## Thresholds live in game/data/battle/sim_policies.json ("smart").


func policy_name() -> StringName:
	return &"smart"


func decide(engine: BattleEngine) -> void:
	_replace_fallen(engine)
	var actor := engine.current
	var heal := _heal_skill(engine, actor)
	var hurt := _most_hurt(engine, actor)
	if hurt != null and _below(hurt, int(config.get("heal_below_pct", 0))):
		if heal != &"" and use(engine, heal, hurt):
			return
		if use_item_with(engine, ItemBattleAction.EFFECT_HEAL_HP, hurt):
			return
	for slot in engine.party_active:
		if not slot.is_alive() and use_item_with(engine, ItemBattleAction.EFFECT_REVIVE, slot):
			return
	super.decide(engine)


func may_leave(engine: BattleEngine, actor: BattleCombatant) -> bool:
	if _heal_skill(engine, actor) == &"":
		return true
	var hurt := _most_hurt(engine, actor)
	return hurt == null or not _below(hurt, int(config.get("keep_healer_below_pct", 0)))


func _replace_fallen(engine: BattleEngine) -> void:
	for slot in engine.party_active.duplicate():
		if slot.is_alive():
			continue
		var pick: BattleCombatant = null
		for r in engine.party_reserve:
			if not r.is_alive():
				continue
			if pick == null or _answers_someone(engine, r) and not _answers_someone(engine, pick):
				pick = r
		if pick != null:
			engine.swap(slot.id, pick.id)


static func _answers_someone(engine: BattleEngine, c: BattleCombatant) -> bool:
	for f in engine.enemies:
		if f.is_alive() and role_answer(engine, f) == c.id:
			return true
	return false


static func _heal_skill(engine: BattleEngine, actor: BattleCombatant) -> StringName:
	for sid in usable_skills(engine, actor):
		var sk := engine.db.skill(sid)
		if String(sk.get("kind", "")) == "heal" and String(sk.get("target", "")) == "single_ally":
			return sid
	return &""


## Living active ally (self included) with the lowest HP fraction.
static func _most_hurt(engine: BattleEngine, actor: BattleCombatant) -> BattleCombatant:
	var best: BattleCombatant = null
	for c in engine.living_allies_of(actor):
		if best == null or c.hp * best.max_hp < best.hp * c.max_hp:
			best = c
	return best


static func _below(c: BattleCombatant, pct: int) -> bool:
	return c.hp * 100 < c.max_hp * pct
