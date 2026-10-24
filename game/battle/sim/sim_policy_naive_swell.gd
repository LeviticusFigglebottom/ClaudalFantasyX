class_name SimPolicyNaiveSwell
extends SimPolicyNaive
## "Naive with Swell" (M2-NIT-03, report only): the masher of `naive` who also presses the Swell row
## whenever it shows. The HUD draws that row in the swell colour on a pulsing gauge, so this is the
## player the menu invites. Like `naive`, a damage technique goes to the first living foe (where the
## cursor starts); a healing one still waits for a hurt ally (swell_heal_below_pct), the generous case.
## The report shows its win rate next to the `naive` band, so Swell's pull on a masher stays visible
## (balance_targets.md; about 30% is the line that needs a deliberate decision).
## M2-CMB-05: with a Vowbound bound it calls it at once ("call_vowbound": "at_once"), the masher of
## ADR 0027's Vowbound line; once out, the Vowbound mashes Attack and unleashes when full.


func policy_name() -> StringName:
	return &"naive_swell"


func unleashes_swell() -> bool:
	return true


func swell_focus(engine: BattleEngine, actor: BattleCombatant) -> BattleCombatant:
	var foes := engine.living_foes_of(actor)
	return null if foes.is_empty() else foes[0]


func decide(engine: BattleEngine) -> void:
	if not call_vowbound(engine):
		super.decide(engine)
