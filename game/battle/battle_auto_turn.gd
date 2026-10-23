class_name BattleAutoTurn
extends RefCounted
## Berserk and Confuse (formulas.md § Statuses): what a combatant that is not in control of itself
## does, split out of BattleEngine (M2-CMB-03). Static and headless; the engine still plays the
## turn (BattleEngine._run_auto_turn) and draws the target from this pool on its rng.


## The skill a combatant uses when not in control: "attack" if it knows it, otherwise its
## first affordable physical single-foe skill. &"" if it has none.
static func basic_attack(db: BattleDB, c: BattleCombatant) -> StringName:
	if c.skills.has(&"attack") and int(db.skill(&"attack").get("mp_cost", 0)) <= c.mp:
		return &"attack"
	for sid in c.skills:
		var sk := db.skill(sid)
		if (
			String(sk.get("kind", "")) == "physical"
			and String(sk.get("target", "single_foe")) == "single_foe"
			and int(sk.get("mp_cost", 0)) <= c.mp
		):
			return sid
	return &""


## Who `actor` may strike with `skill_id`. Confuse turns on a random ally other than itself with
## CONFUSE_ALLY_PCT (one roll on the battle rng), otherwise a random foe; Berserk hits a random
## foe, or only its provoker while Provoked.
static func pool(
	engine: BattleEngine, actor: BattleCombatant, reason: StringName, skill_id: StringName
) -> Array[BattleCombatant]:
	var foes := engine.living_foes_of(actor)
	if reason == &"confuse":
		var allies := engine.living_other_allies_of(actor)
		var turn_on_allies := engine.rng.randi_range(1, 100) <= Formulas.CONFUSE_ALLY_PCT
		if turn_on_allies and not allies.is_empty() or foes.is_empty():
			return allies
		return foes
	var forced := engine.forced_target(actor, skill_id)
	if forced != null:
		var only: Array[BattleCombatant] = [forced]
		return only
	return foes
