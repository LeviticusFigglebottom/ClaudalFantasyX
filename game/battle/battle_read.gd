class_name BattleRead
extends RefCounted
## The Read ability (SPEC §6.1, M1-CMB-03): what reading a foe reveals. Static and Node-free.
##
## A Read skill is a skills.json "support" row with "read": true. It always lands (no hit roll,
## no Reflect: it is not magic) and costs its rank like any action. The engine puts reveal() on
## the hit as hit["read"], so the HUD and the bestiary log (BattleBestiary, Bestiary) read it from
## the ActionResult. Nothing here touches state or the rng.

const SKILL_FLAG := "read"
## SPEC §6.8 element order, for listing affinities. Any other element follows, sorted.
const ELEMENT_ORDER: Array[StringName] = [&"fire", &"water", &"lightning", &"ice", &"holy", &"glimmer"]
## Affinity groups a reveal lists, in this order. "normal" is never listed.
const AFFINITY_GROUPS: Array[StringName] = [&"weak", &"resist", &"immune", &"absorb"]
const STAT_KEYS: Array[String] = [
	"strength", "magic", "defense", "magic_defense", "agility", "accuracy", "evasion", "luck"
]


static func is_read(sk: Dictionary) -> bool:
	return bool(sk.get(SKILL_FLAG, false))


## What Read shows about `target`, whose enemies.json row is `row` ({} for a party member):
## {enemy_id (the row id, "" without a row), target_id, name_key, lore_key, level, hp, max_hp,
##  mp, max_mp, stats: {strength, magic, defense, magic_defense, agility, accuracy, evasion,
##  luck}, affinities: {weak, resist, immune, absorb: [element ids]}, delay_immune,
##  statuses: [status ids, sorted]}.
## HP, MP and statuses are the target's at the moment it is read; the stats are its battle
## values before breaks (Weakened and the rest show as statuses).
static func reveal(target: BattleCombatant, row: Dictionary) -> Dictionary:
	var stats := {}
	for key in STAT_KEYS:
		stats[key] = int(target.get(key))
	var statuses: Array[String] = []
	for sid: Variant in target.statuses:
		statuses.append(String(sid))
	statuses.sort()
	return {
		"enemy_id": str(row.get("id", "")),
		"target_id": String(target.id),
		"name_key": target.name_key,
		"lore_key": str(row.get("lore_key", "")),
		"level": target.level,
		"hp": target.hp,
		"max_hp": target.max_hp,
		"mp": target.mp,
		"max_mp": target.max_mp,
		"stats": stats,
		"affinities": affinity_groups(target.affinities),
		"delay_immune": target.delay_immune,
		"statuses": statuses,
	}


## {weak, resist, immune, absorb: [element ids]} in SPEC element order (then any other, sorted).
static func affinity_groups(affinities: Dictionary) -> Dictionary:
	var elements: Array[StringName] = ELEMENT_ORDER.duplicate()
	var extra: Array[StringName] = []
	for el: Variant in affinities:
		var e := StringName(str(el))
		if not elements.has(e):
			extra.append(e)
	extra.sort_custom(func(a: StringName, b: StringName) -> bool: return String(a) < String(b))
	elements.append_array(extra)
	var out := {}
	for group in AFFINITY_GROUPS:
		var listed: Array[String] = []
		for e in elements:
			if StringName(str(affinities.get(e, ""))) == group:
				listed.append(String(e))
		out[String(group)] = listed
	return out
