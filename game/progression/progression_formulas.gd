class_name ProgressionFormulas
extends RefCounted
## Progression formulas. Mirrors the "Progression" section of docs/kb/design/formulas.md
## EXACTLY; change the doc, this file, and tests/unit/test_lattice_formulas.gd together.
## Like Formulas, these constants ARE the formulas (the one allowed home for such numbers).

## Lattice points (LP) needed for the first movement point, and the growth schedule.
const LP_BASE := 30
const LP_GROWTH := 5
const LP_STEP := 10
## Banked movement points never exceed this; LP keeps pooling while a character is at the cap.
const MOVEMENT_POINT_CAP := 99


## LP a character gains from a battle: exactly the XP the battle credits them
## (formulas.md XP credit rule: on the field at some point and alive at victory).
static func lp_gain(credited_xp: int) -> int:
	return maxi(credited_xp, 0)


## LP needed for the next movement point, given how many movement points were earned so far.
static func lp_threshold(movement_earned: int) -> int:
	return LP_BASE + LP_GROWTH * (maxi(movement_earned, 0) / LP_STEP)


## Converts pooled LP into movement points. `room` = how many more points fit under the cap.
## Returns Vector2i(movement points gained, LP left in the pool).
static func convert_lp(lp_pool: int, movement_earned: int, room: int) -> Vector2i:
	var pool := maxi(lp_pool, 0)
	var gained := 0
	while gained < room:
		var need := lp_threshold(movement_earned + gained)
		if pool < need:
			break
		pool -= need
		gained += 1
	return Vector2i(gained, pool)


## Room left under MOVEMENT_POINT_CAP.
static func movement_room(banked: int) -> int:
	return maxi(MOVEMENT_POINT_CAP - banked, 0)
