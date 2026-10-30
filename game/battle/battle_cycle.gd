class_name BattleCycle
extends RefCounted
## M4-A2P-025: a combatant that cycles its element in a fixed order (Kesh: Water, Lightning, Fire, Ice, Holy,
## Glimmer, the order the pilgrimage met them; plan/act2/bosses/kesh.md §4). Static and headless.
##   vowbound.json, characters.json or enemies.json "cycle": [skill ids], one skill per element, in order. On each of
##   its own turns only the current one may be used (the others are refused with FAIL_OUT_OF_CYCLE, and the AI never
##   picks them); skills not in the cycle (attack, defend) stay free. The cycle moves on at the end of every own turn
##   it acts (a lost turn holds it).
## Pillar 4: the timeline shows each of its coming turns' cycle skill as that TurnEntry's intent (skill_at).

const FAIL_OUT_OF_CYCLE := &"out_of_cycle"


## The cycle skill `c` holds `ahead` own turns from now (0 = this or its next turn), or &"" with no cycle.
static func skill_at(c: BattleCombatant, ahead: int) -> StringName:
	if c.cycle.is_empty():
		return &""
	return c.cycle[(c.cycle_index + maxi(ahead, 0)) % c.cycle.size()]


## True when `c` may use `skill_id` now: it isn't one of the cycle's, or it is the current one.
static func allows(c: BattleCombatant, skill_id: StringName) -> bool:
	return not c.cycle.has(skill_id) or skill_at(c, 0) == skill_id


## At the end of `c`'s own turn: the next element.
static func advance(c: BattleCombatant) -> void:
	if not c.cycle.is_empty():
		c.cycle_index = (c.cycle_index + 1) % c.cycle.size()
