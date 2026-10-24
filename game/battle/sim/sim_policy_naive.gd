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
