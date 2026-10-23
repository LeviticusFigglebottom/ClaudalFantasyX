class_name SimPolicyLowestHp
extends SimPolicy
## "Lowest HP": Attack, always on the living foe with the least HP (focus fire), no swaps.


func policy_name() -> StringName:
	return &"lowest_hp"


func decide(engine: BattleEngine) -> void:
	use(engine, &"attack", lowest_hp(engine.living_foes_of(engine.current)))
