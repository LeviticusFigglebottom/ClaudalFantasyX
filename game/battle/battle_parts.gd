class_name BattleParts
extends RefCounted
## M4-A2P-022: breakable parts that stay broken until something mends them (the Lamp Engine's rings and the conduit
## crawlers that tend them; plan/act2/bosses/lamp_engine.md). Static and headless.
##   enemies.json "parts": [charge skill ids]  a part per charged skill (creatures.json `break_parts` holds its meshes,
##                                             keyed the same). Breaking that charge on the weak point (BossMechanics)
##                                             breaks the part: it stays in `broken_parts`, and every skill whose
##                                             charge is that part is off the enemy's AI menu until it is restored.
##   skills.json "restores_part": true         on an ally: mends that ally's longest-broken part ("part_restored" on
##                                             the hit; BattleEngine.part_restored). Nothing to mend: no effect.
## EnemyAI reads them through the conditions ally_part_broken and ally_struck and the target selector broken_ally.
## M4-A2P-023, a part only one hero can break (Malcor Venn's flat-engine, which Liss breaks):
##   enemies.json "answered_by": hero id   only that hero may act on this foe. For anyone else it is off
##                                         living_foes_of and every target list, and a group skill passes over it
##                                         (never refused). "answered_key" is the loc key the target cursor says why.
##   enemies.json phase rows "when_down": enemy id   the phase also comes when no foe of that id stands (Venn boards
##                                         on the engine's break, or at 50%, whichever is first).


## True when `actor` may act on `target`: a foe answered by one hero is that hero's alone (M4-A2P-023).
static func may_strike(actor: BattleCombatant, target: BattleCombatant) -> bool:
	return target.answered_by == &"" or actor.team == target.team or actor.id == target.answered_by


## True when no living enemy of id `enemy` stands (a phase's "when_down").
static func is_down(engine: BattleEngine, enemy: StringName) -> bool:
	for e in engine.enemies:
		if e.is_alive() and BattleEngine.enemy_id(e) == enemy:
			return false
	return true


## The charge `actor` lost on the weak point: its part breaks when the row declares it.
static func on_charge_broken(actor: BattleCombatant, skill_id: StringName) -> void:
	if actor.parts.has(skill_id) and not actor.broken_parts.has(skill_id):
		actor.broken_parts.append(skill_id)


## True when `skill_id` is a gather whose charged part on `actor` is broken: the AI must not pick it.
static func silenced(engine: BattleEngine, actor: BattleCombatant, skill_id: StringName) -> bool:
	if actor.broken_parts.is_empty():
		return false
	var charge: Dictionary = engine.db.skill(skill_id).get("charge", {})
	return not charge.is_empty() and actor.broken_parts.has(StringName(str(charge.get("skill", ""))))


## `sk` with "restores_part" landing on `target`: the longest-broken part comes back. The part's id, or &"".
static func restore(engine: BattleEngine, target: BattleCombatant, sk: Dictionary) -> StringName:
	if not bool(sk.get("restores_part", false)) or target.broken_parts.is_empty() or not target.is_alive():
		return &""
	var part: StringName = target.broken_parts.pop_front()
	engine.part_restored.emit(target, part)
	return part


## The first living ally of `actor` (in encounter order, itself included) with a broken part, or null.
static func broken_ally(engine: BattleEngine, actor: BattleCombatant) -> BattleCombatant:
	for a in engine.living_allies_of(actor):
		if not a.broken_parts.is_empty():
			return a
	return null


## True once the party has landed a blow on any living ally of `actor` (a tender wakes when its keeper is struck).
static func ally_struck(engine: BattleEngine, actor: BattleCombatant) -> bool:
	for a in engine.living_allies_of(actor):
		if a.struck:
			return true
	return false
