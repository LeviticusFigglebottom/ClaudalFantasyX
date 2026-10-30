class_name BattleCover
extends RefCounted
## M4-A2P-021: foes that take cover between their turns (act2_plan §4.6). Static and headless.
##   enemies.json "glide": true   the gallery ray: up above the water line after one of its turns, back down after the
##                                next, so it can be struck only every other round (it acts either way).
##   enemies.json "ambush": true  the glass skate: buried in the sand from the start until it has acted once.
## Covered foes are `untargetable` (living_foes_of and every targeting rule skip them; the sim's policies too).
## Pillar 4 and no stalls: cover never takes the last foe the party can strike. If every living foe would be covered,
## the first covered one in encounter order stays up (or comes up at the next turn start, if the others fell).


## At the battle's start (after the opening): every ambusher goes under, then one stays up if all would be hidden.
static func begin(engine: BattleEngine) -> void:
	for e in engine.enemies:
		if e.ambushes and e.is_alive():
			_hide(e)
	keep_one(engine)


## At the end of `actor`'s own turn: an ambusher comes up for good, a glider goes up or comes down.
static func on_turn_end(engine: BattleEngine, actor: BattleCombatant) -> void:
	if actor.team == BattleCombatant.TEAM_PARTY or not actor.is_alive():
		return
	if actor.ambushes:
		actor.ambushes = false
		_surface(actor)
	elif actor.glides:
		if actor.covered:
			_surface(actor)
		else:
			_hide(actor)
	keep_one(engine)


## When no living foe may be struck and one is only covered (never a phase's untargetable), the first such foe in
## encounter order comes up.
static func keep_one(engine: BattleEngine) -> void:
	var first: BattleCombatant = null
	for e in engine.enemies:
		if not e.is_alive():
			continue
		if not e.untargetable:
			return
		if first == null and e.covered:
			first = e
	if first != null:
		_surface(first)


static func _hide(e: BattleCombatant) -> void:
	e.covered = true
	e.untargetable = true


static func _surface(e: BattleCombatant) -> void:
	if e.covered:
		e.covered = false
		e.untargetable = false
