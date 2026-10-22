class_name SimPolicyNaive
extends SimPolicy
## "Naive": the player mashes Attack on the first living foe and never swaps.


func policy_name() -> StringName:
	return &"naive"


func decide(engine: BattleEngine) -> void:
	use(engine, &"attack", engine.living_foes_of(engine.current)[0])
