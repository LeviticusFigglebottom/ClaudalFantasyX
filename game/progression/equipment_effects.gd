class_name EquipmentEffects
extends RefCounted
## What a character's equipped pieces do in battle (SPEC §6.5). apply_to() is a
## BattleEngine.party_modifier, composable with LatticeProgress.apply_to through compose():
##   engine.party_modifier = EquipmentEffects.compose([progress.apply_to, effects.modifier()])
## Lifetime: Godot method Callables do not keep a RefCounted alive. modifier() returns a hook that
## owns its EquipmentEffects; for a bare method (`progress.apply_to`) the caller must hold the
## object for the life of the engine setup. compose() reports an invalid hook instead of skipping
## it silently (M1-PRG-03).
##
## apply_to() handles everything the engine already supports: piece stats and stat_bonus
## abilities (added, like the Lattice; HP/MP raise max and current), "always" auto-statuses
## (added with duration -1), element guards (affinities, never weakened), and Unfettered
## (break_damage_cap). Effects that need engine support are written as plain data onto the
## combatant's metadata under META_KEY for Combat to read (request task M1-CMB-06):
##   {"abilities": [ability ids], "attack_elements": [element], "on_hit_statuses":
##    [{"id", "chance", "duration"}], "status_wards": [status], "low_hp_statuses":
##    [{"id", "hp_below_pct", "duration"}]}
## Economy and field abilities are party-wide queries: currency_multiplier(), encounter_rate_pct().

const META_KEY := &"equipment_effects"
const KEY_ABILITIES := &"abilities"
const KEY_ATTACK_ELEMENTS := &"attack_elements"
const KEY_ON_HIT_STATUSES := &"on_hit_statuses"
const KEY_STATUS_WARDS := &"status_wards"
const KEY_LOW_HP_STATUSES := &"low_hp_statuses"

const CAT_ON_HIT_ELEMENT := &"on_hit_element"
const CAT_STATUS_STRIKE := &"status_strike"
const CAT_STAT_BONUS := &"stat_bonus"
const CAT_ELEMENT_GUARD := &"element_guard"
const CAT_STATUS_WARD := &"status_ward"
const CAT_AUTO_STATUS := &"auto_status"
const CAT_ECONOMY := &"economy"
const CAT_FIELD := &"field"
const CAT_SPECIAL := &"special"
const TRIGGER_ALWAYS := &"always"
const TRIGGER_LOW_HP := &"low_hp"
## Auto-statuses last the whole battle (the engine's "until cured").
const WHOLE_BATTLE := -1
## Affinities from weakest to strongest defence; a guard only ever moves a combatant right.
const AFFINITY_ORDER: Array[StringName] = [&"weak", &"normal", &"resist", &"immune", &"absorb"]
## Identity values for the party-wide queries (no ability equipped).
const NO_CURRENCY_MULT := 1
const FULL_ENCOUNTER_RATE_PCT := 100
const COMBATANT_STATS: Array[StringName] = [
	&"strength", &"magic", &"defense", &"magic_defense", &"agility", &"accuracy", &"evasion", &"luck"
]

var db: ItemDB
var bag: EquipmentBag


func _init(item_db: ItemDB, equipment_bag: EquipmentBag) -> void:
	db = item_db
	bag = equipment_bag


## Chains several party_modifier hooks into one, called in order. An invalid hook is an error,
## not a silent skip: a bound method Callable (`fx.apply_to`) does not keep a RefCounted alive,
## so a hook whose owner was freed would otherwise drop its gear without a word. Pass owning
## hooks (`fx.modifier()`), or keep `fx` and the LatticeProgress referenced for the whole setup.
static func compose(modifiers: Array[Callable]) -> Callable:
	var mods := modifiers.duplicate()
	for i in mods.size():
		if not (mods[i] as Callable).is_valid():
			push_error("EquipmentEffects.compose: modifier %d is not valid (was its owner freed?)" % i)
	return func(c: BattleCombatant) -> void:
		for m: Callable in mods:
			if m.is_valid():
				m.call(c)
			else:
				push_error("EquipmentEffects.compose: skipped an invalid modifier for %s" % c.id)


## apply_to as a party_modifier that OWNS this EquipmentEffects (the lambda holds a reference),
## so `engine.party_modifier = EquipmentEffects.new(db, bag).modifier()` works without the
## caller keeping `fx` alive. Prefer this over the bare `fx.apply_to`.
func modifier() -> Callable:
	var owner_ref: EquipmentEffects = self
	return func(c: BattleCombatant) -> void: owner_ref.apply_to(c)


## Every filled ability on `cid`'s equipped pieces: weapon first, then armor, in slot order.
## Duplicates are kept (two Steady Arms give the bonus twice).
func abilities_for(cid: StringName) -> Array[StringName]:
	var out: Array[StringName] = []
	for uid in bag.equipped_uids(cid):
		out.append_array(bag.abilities_of(uid))
	return out


## Stat name -> total bonus from piece stats and stat_bonus abilities.
func stat_bonuses(cid: StringName) -> Dictionary:
	var out: Dictionary = {}
	for uid in bag.equipped_uids(cid):
		var stats: Dictionary = db.equipment_row(bag.base_of(uid)).get("stats", {})
		for st: Variant in stats:
			_bump(out, StringName(str(st)), int(stats[st]))
	for aid in _of_category(cid, CAT_STAT_BONUS):
		var eff := _effect(aid)
		_bump(out, StringName(str(eff.get("stat", ""))), int(eff.get("amount", 0)))
	return out


## Statuses `cid` starts every battle with ("always" auto-statuses), unique, in slot order.
func starting_statuses(cid: StringName) -> Array[StringName]:
	var out: Array[StringName] = []
	for aid in _of_category(cid, CAT_AUTO_STATUS):
		var eff := _effect(aid)
		var sid := StringName(str(eff.get("status", "")))
		if StringName(str(eff.get("trigger", ""))) == TRIGGER_ALWAYS and not out.has(sid):
			out.append(sid)
	return out


## Element -> the strongest affinity any guard grants.
func element_guards(cid: StringName) -> Dictionary:
	var out: Dictionary = {}
	for aid in _of_category(cid, CAT_ELEMENT_GUARD):
		var eff := _effect(aid)
		var el := StringName(str(eff.get("element", "")))
		out[el] = _stronger(out.get(el, &"weak"), StringName(str(eff.get("affinity", ""))))
	return out


func breaks_damage_cap(cid: StringName) -> bool:
	for aid in _of_category(cid, CAT_SPECIAL):
		if bool(_effect(aid).get("break_damage_cap", false)):
			return true
	return false


## The engine-facing data written to the combatant's metadata (see the class comment).
func battle_data(cid: StringName) -> Dictionary:
	var elements: Array[StringName] = []
	for aid in _of_category(cid, CAT_ON_HIT_ELEMENT):
		var el := StringName(str(_effect(aid).get("element", "")))
		if not elements.has(el):
			elements.append(el)
	var wards: Array[StringName] = []
	for aid in _of_category(cid, CAT_STATUS_WARD):
		var sid := StringName(str(_effect(aid).get("status", "")))
		if not wards.has(sid):
			wards.append(sid)
	var strikes: Array[Dictionary] = []
	for aid in _of_category(cid, CAT_STATUS_STRIKE):
		var eff := _effect(aid)
		_merge_strike(strikes, StringName(str(eff["status"])), int(eff["chance"]), int(eff["duration"]))
	var low_hp: Array[Dictionary] = []
	for aid in _of_category(cid, CAT_AUTO_STATUS):
		var eff := _effect(aid)
		var sid := StringName(str(eff.get("status", "")))
		if StringName(str(eff.get("trigger", ""))) == TRIGGER_LOW_HP and not _has_id(low_hp, sid):
			low_hp.append({"id": sid, "hp_below_pct": int(eff["hp_below_pct"]), "duration": WHOLE_BATTLE})
	return {
		KEY_ABILITIES: abilities_for(cid),
		KEY_ATTACK_ELEMENTS: elements,
		KEY_ON_HIT_STATUSES: strikes,
		KEY_STATUS_WARDS: wards,
		KEY_LOW_HP_STATUSES: low_hp,
	}


## party_modifier hook: layers `c.id`'s equipment onto a freshly built combatant. Call it ONCE
## per combatant: stat bonuses add.
func apply_to(c: BattleCombatant) -> void:
	var bonus := stat_bonuses(c.id)
	for st: StringName in bonus:
		_add_stat(c, st, int(bonus[st]))
	var guards := element_guards(c.id)
	for el: StringName in guards:
		c.affinities[el] = _stronger(c.affinity_for(el), guards[el])
	for sid in starting_statuses(c.id):
		c.add_status(sid, WHOLE_BATTLE)
	if breaks_damage_cap(c.id):
		c.break_damage_cap = true
	c.set_meta(META_KEY, battle_data(c.id))


## The engine-facing data a modifier left on a combatant ({} if none was applied).
static func data_of(c: BattleCombatant) -> Dictionary:
	return c.get_meta(META_KEY, {})


## Battle lume multiplier for a victory: the highest economy multiplier worn by anyone in
## `cids` (pass the members credited under the XP rule). NO_CURRENCY_MULT if none.
func currency_multiplier(cids: Array[StringName]) -> int:
	var best := NO_CURRENCY_MULT
	for cid in cids:
		for aid in _of_category(cid, CAT_ECONOMY):
			best = maxi(best, int(_effect(aid).get("currency_mult", NO_CURRENCY_MULT)))
	return best


## Random-encounter rate for the field, in percent: the lowest any active member's field
## ability sets. FULL_ENCOUNTER_RATE_PCT if none.
func encounter_rate_pct(cids: Array[StringName]) -> int:
	var best := FULL_ENCOUNTER_RATE_PCT
	for cid in cids:
		for aid in _of_category(cid, CAT_FIELD):
			best = mini(best, int(_effect(aid).get("encounter_rate_pct", FULL_ENCOUNTER_RATE_PCT)))
	return best


func _of_category(cid: StringName, category: StringName) -> Array[StringName]:
	var out: Array[StringName] = []
	for aid in abilities_for(cid):
		if db.ability_category(aid) == category:
			out.append(aid)
	return out


func _effect(ability_id: StringName) -> Dictionary:
	return db.ability(ability_id).get("effect", {})


static func _bump(d: Dictionary, key: StringName, amount: int) -> void:
	d[key] = int(d.get(key, 0)) + amount


static func _stronger(a: StringName, b: StringName) -> StringName:
	return a if AFFINITY_ORDER.find(a) >= AFFINITY_ORDER.find(b) else b


static func _has_id(rows: Array[Dictionary], sid: StringName) -> bool:
	for r in rows:
		if r["id"] == sid:
			return true
	return false


## One entry per status: the highest chance wins, then the longer duration (-1 is longest).
static func _merge_strike(rows: Array[Dictionary], sid: StringName, chance: int, duration: int) -> void:
	for r in rows:
		if r["id"] == sid:
			r["chance"] = maxi(int(r["chance"]), chance)
			if duration == WHOLE_BATTLE or (int(r["duration"]) != WHOLE_BATTLE and duration > int(r["duration"])):
				r["duration"] = duration
			return
	rows.append({"id": sid, "chance": chance, "duration": duration})


static func _add_stat(c: BattleCombatant, stat: StringName, amount: int) -> void:
	match stat:
		&"hp":
			c.max_hp += amount
			c.hp += amount
		&"mp":
			c.max_mp += amount
			c.mp += amount
		_:
			if COMBATANT_STATS.has(stat):
				c.set(stat, int(c.get(stat)) + amount)
			else:
				push_error("EquipmentEffects: unknown stat '%s'" % stat)
