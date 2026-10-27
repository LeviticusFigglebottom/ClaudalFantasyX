class_name SimPolicyWardGuard
extends SimPolicyNaive
## "Ward guard" (M3-CMB-01, act1_ch08.md §9 Combat item 9): the masher of `naive` who has learned the
## set piece's one lesson. Before mashing, it guards the ward (SimWardGuard): Hold the Stair or
## Provoke when a grip comes before its next turn, Haul when the Climb has no Haste. Report only: it
## shows how far guarding alone carries a fight (balance_targets.md).


func policy_name() -> StringName:
	return &"ward_guard"


func decide(engine: BattleEngine) -> void:
	if not SimWardGuard.act(engine):
		super.decide(engine)
