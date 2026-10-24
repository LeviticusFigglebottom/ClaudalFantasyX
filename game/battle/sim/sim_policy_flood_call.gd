class_name SimPolicyFloodCall
extends SimPolicyNaiveSwell
## "Call into the flood" (M2-FP-17): the masher of naive_swell who, the moment a field rises, has
## the caller call its Vowbound (sim_policies.json call_vowbound "field_up") and then leaves it out
## until it falls or the battle ends. The player who answers the Drownbell's flood with Ilun and
## nothing else: banded at no more than the encounter's smart ceiling, and it must never stall.


func policy_name() -> StringName:
	return &"flood_call"


func decide(engine: BattleEngine) -> void:
	if call_vowbound(engine):
		return
	super.decide(engine)
