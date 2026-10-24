class_name SimPolicyNaive
extends SimPolicy
## "Naive": the player mashes Attack on the first living foe and never swaps. Mashing confirm picks
## the top row, so a full gauge is never unleashed (M2-CMB-01), as items are never used.


func policy_name() -> StringName:
	return &"naive"


func unleashes_swell() -> bool:
	return false


func decide(engine: BattleEngine) -> void:
	use(engine, &"attack", engine.living_foes_of(engine.current)[0])


## M2-CMB-05: a masher's Vowbound mashes too: its finisher when the Swell row lights (only for
## a policy that presses it), else Attack on the first living foe.
func vowbound_turn(engine: BattleEngine) -> void:
	var vb := engine.vowbound
	var foes := engine.living_foes_of(vb.summon)
	if foes.is_empty():
		return
	if unleashes_swell() and vb.unleash_refusal(engine) == &"":
		if vb.unleash(engine, foes).ok:
			swells_used += 1
			return
	_basic(engine)
