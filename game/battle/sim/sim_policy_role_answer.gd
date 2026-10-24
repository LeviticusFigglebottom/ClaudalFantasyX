class_name SimPolicyRoleAnswer
extends SimPolicy
## "Role answer" (SPEC §6.1): the elegant-answer play enemies.json encodes in role_answer.
## Each turn: if the actor answers a living foe, it takes the weakest such foe. Otherwise the
## focus is the lowest-HP foe, and if that foe's answer waits in reserve, it swaps in for the
## actor (free) and takes the turn. The answerer opens with a Break skill its foe lacks, then
## uses its best expected damage per rank.


func policy_name() -> StringName:
	return &"role_answer"


func decide(engine: BattleEngine) -> void:
	var actor := engine.current
	if call_vowbound(engine):  # the Drownbell's answer: Ilun into the flood (M2-FP-17)
		return
	var target := _target_for(engine, actor)
	if target == null:
		return
	var answer := role_answer(engine, target)
	if answer != actor.id and may_leave(engine, actor) and _reserve_ready(engine, answer):
		if engine.swap(actor.id, answer):
			actor = engine.current
	attack_as_answer(engine, actor, target)


## Weakest living foe this actor answers, else the weakest living foe.
func _target_for(engine: BattleEngine, actor: BattleCombatant) -> BattleCombatant:
	var foes := engine.living_foes_of(actor)
	var mine: Array[BattleCombatant] = []
	for f in foes:
		if role_answer(engine, f) == actor.id:
			mine.append(f)
	return lowest_hp(mine) if not mine.is_empty() else lowest_hp(foes)


## Override to keep someone on the field (the smart policy keeps a needed healer).
func may_leave(_engine: BattleEngine, _actor: BattleCombatant) -> bool:
	return true


func attack_as_answer(engine: BattleEngine, actor: BattleCombatant, target: BattleCombatant) -> void:
	var sid := &""
	if role_answer(engine, target) == actor.id:
		sid = break_skill(engine, actor, target)
	if sid == &"":
		sid = best_damage_skill(engine, actor, target)
	if sid != &"":
		use(engine, sid, target)


## M2-NIT-03: a ready technique takes the foe this actor answers too (the weakest such foe, else
## the weakest), instead of always the weakest: the Swell no longer pulls the answer off its focus.
func swell_focus(engine: BattleEngine, actor: BattleCombatant) -> BattleCombatant:
	return _target_for(engine, actor)


## M2-NIT-03: the free swap to the focus foe's answer comes before a ready technique (the gauge
## keeps its points in reserve), so the Swell never costs the answer its turn.
func unleash_swell(engine: BattleEngine) -> bool:
	if _swaps_out(engine, engine.current):
		return false
	return super.unleash_swell(engine)


## True when decide() would swap `actor` out for the reserve member who answers its focus foe.
func _swaps_out(engine: BattleEngine, actor: BattleCombatant) -> bool:
	var target := _target_for(engine, actor)
	if target == null:
		return false
	var answer := role_answer(engine, target)
	return answer != actor.id and may_leave(engine, actor) and _reserve_ready(engine, answer)


static func _reserve_ready(engine: BattleEngine, cid: StringName) -> bool:
	for c in engine.party_reserve:
		if c.id == cid:
			return c.is_alive()
	return false
