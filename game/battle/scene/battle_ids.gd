class_name BattleIds
extends RefCounted
## Id-list helpers for the battle scene, moved out of BattleController so it stays under the
## file-length cap (M2-FP-06 merge with M1-CMB-03).


## A JSON list (or any Array) as typed ids.
static func from(raw: Variant) -> Array[StringName]:
	var out: Array[StringName] = []
	for v: Variant in raw as Array:
		out.append(StringName(str(v)))
	return out


## The ids of `list`, in order.
static func of(list: Array[BattleCombatant]) -> Array[StringName]:
	var out: Array[StringName] = []
	for c in list:
		out.append(c.id)
	return out
