class_name BattleEcho
extends RefCounted
## M4-A2P-024: Nhoa's echo (plan/act2/bosses/nhoa.md: she copies the last enemy action). Static and headless.
##   skills.json "echo": true   the skill resolves as the last action an enemy-side combatant took
##                              (BattleEngine.last_foe_skill), from the user against its own foes or allies: skill
##                              targets are relative to the user, so the copy reads the same way round. The copy
##                              never charges, summons, clears a field or counts as a Swell. Nothing to echo yet:
##                              refused with FAIL_NOTHING.

const FAIL_NOTHING := &"nothing_to_echo"
## The keys an echo never copies: what belongs to the original user, not to the action.
const NOT_COPIED: Array[String] = ["charge", "summon", "clears_field", "swell", "vowbound", "restores_part"]


## Remembers `skill_id` when an enemy-side combatant's action landed.
static func record(engine: BattleEngine, actor: BattleCombatant, skill_id: StringName, ok: bool) -> void:
	if ok and actor.team == BattleCombatant.TEAM_ENEMY and not actor.is_entry():
		engine.last_foe_skill = skill_id


## The row an echo skill `sk` resolves as now, or {} with nothing to echo. The echo's own rank and MP cost stand.
static func row(engine: BattleEngine, sk: Dictionary) -> Dictionary:
	if engine.last_foe_skill == &"":
		return {}
	var copy := engine.db.skill(engine.last_foe_skill).duplicate(true)
	if copy.is_empty():
		return {}
	for key in NOT_COPIED:
		copy.erase(key)
	copy["rank"] = sk.get("rank", copy.get("rank", Formulas.DEFAULT_RANK))
	copy["mp_cost"] = sk.get("mp_cost", 0)  # the echo's own cost, never the original's
	return copy
