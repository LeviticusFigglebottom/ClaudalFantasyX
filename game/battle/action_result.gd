class_name ActionResult
extends RefCounted
## Outcome of one action, consumed by battle UI/VFX glue and by tests.

var actor_id: StringName
var skill_id: StringName
var ok := true
## Why the action could not be taken (&"no_mp", &"silenced", &"not_your_turn", ...).
var fail_reason: StringName = &""
## One Dictionary per target: {target_id, hit, crit, amount, statuses_added: Array}, plus
## "reflected_from": <id> when Reflect bounced a spell from that combatant onto target_id.
var hits: Array[Dictionary] = []
## Set for item use (BattleEngine.use_item); skill_id is then empty. Item hits also carry
## mp_amount, revived, statuses_removed and delay_ticks (ItemBattleAction.resolve_on), and
## "zombie_felled" when a revive item KO'd a Zombie.
var item_id: StringName = &""
## End-of-turn effects of this action (Poison, Regen, Doom), as BattleEngine.turn_ended sends
## them. Empty for failed actions.
var end_of_turn: Array[Dictionary] = []
## Set when the actor was not in control: &"berserk" or &"confuse" (the engine chose).
var auto_reason: StringName = &""
## Set for a Swell technique (BattleSwell.perform): the power bonus its input earned, in percent.
var swell_bonus_pct := 0


static func failed(actor: StringName, skill: StringName, reason: StringName) -> ActionResult:
	var r := ActionResult.new()
	r.actor_id = actor
	r.skill_id = skill
	r.ok = false
	r.fail_reason = reason
	return r
