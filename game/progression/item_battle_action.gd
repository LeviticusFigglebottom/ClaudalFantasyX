class_name ItemBattleAction
extends RefCounted
## What using an item in battle does (SPEC §6.11 items; Combat wires it into BattleEngine in
## M1-CMB-06). Built from an items.json row's "battle" block by ItemBattleAction.for_item().
##
## Contract for Combat:
## - `target` uses the skill target vocabulary (single_ally, all_allies, single_foe, all_foes,
##   self). `targets_fallen` is true for revive items: they target KO'd allies ONLY.
## - `rank` is the CTB action rank of the turn (Formulas.action_delay).
## - `effects` run in order on each target. resolve_on() is the reference implementation and is
##   deterministic (no RNG): heal_hp {amount}, restore_mp {amount}, cure {statuses},
##   revive {hp_pct}, add_status {status, duration}, delay {ranks}, damage {amount, element}.
## - Use consumes exactly one item from the bag, after the action resolves (consume()).

const EFFECT_HEAL_HP := &"heal_hp"
const EFFECT_RESTORE_MP := &"restore_mp"
const EFFECT_CURE := &"cure"
const EFFECT_REVIVE := &"revive"
const EFFECT_ADD_STATUS := &"add_status"
const EFFECT_DELAY := &"delay"
const EFFECT_DAMAGE := &"damage"
const TARGET_SINGLE_ALLY := &"single_ally"
const TARGET_ALL_ALLIES := &"all_allies"
const TARGET_SELF := &"self"
const PCT := 100
const USES_PER_ACTION := 1

var item_id: StringName
var name_key: String
var target: StringName
var rank: int
var effects: Array[Dictionary] = []
var targets_fallen := false


## The battle action for an item, or null if it can't be used in battle.
static func for_item(db: ItemDB, iid: StringName) -> ItemBattleAction:
	var row := db.item(iid)
	if not row.has("battle"):
		return null
	var b: Dictionary = row["battle"]
	var a := ItemBattleAction.new()
	a.item_id = iid
	a.name_key = str(row.get("name_key", ""))
	a.target = StringName(str(b.get("target", "")))
	a.rank = int(b.get("rank", 0))
	for e: Variant in b.get("effects", []):
		var eff: Dictionary = e
		a.effects.append(eff)
		if StringName(str(eff.get("type", ""))) == EFFECT_REVIVE:
			a.targets_fallen = true
	return a


## Battle-usable items the party holds, in inventory listing order.
static func usable_items(db: ItemDB, inventory: Inventory) -> Array[StringName]:
	var out: Array[StringName] = []
	for iid in inventory.ids():
		if db.item(iid).has("battle"):
			out.append(iid)
	return out


## Takes one of the item from the bag. False if none are left.
func consume(inventory: Inventory) -> bool:
	return inventory.remove(item_id, USES_PER_ACTION)


func targets_allies() -> bool:
	return target in [TARGET_SINGLE_ALLY, TARGET_ALL_ALLIES, TARGET_SELF]


## Whether `c` is a legal target by life state (team checks are the engine's, as for skills).
func can_target(c: BattleCombatant) -> bool:
	return c.is_alive() != targets_fallen


## Applies every effect to `c`. Returns {"target_id", "amount", "mp_amount", "revived",
## "statuses_added", "statuses_removed", "delay_ticks"}. "amount" follows the engine's hit
## convention: HP lost, so healing is negative.
func resolve_on(c: BattleCombatant) -> Dictionary:
	var out := {
		"target_id": c.id,
		"amount": 0,
		"mp_amount": 0,
		"revived": false,
		"statuses_added": [],
		"statuses_removed": [],
		"delay_ticks": 0,
	}
	if not can_target(c):
		return out
	for eff in effects:
		_apply(c, eff, out)
	return out


func _apply(c: BattleCombatant, eff: Dictionary, out: Dictionary) -> void:
	match StringName(str(eff.get("type", ""))):
		EFFECT_HEAL_HP:
			out["amount"] = int(out["amount"]) - c.apply_damage(-int(eff["amount"]))
		EFFECT_RESTORE_MP:
			var before := c.mp
			c.mp = mini(c.mp + int(eff["amount"]), c.max_mp)
			out["mp_amount"] = int(out["mp_amount"]) + c.mp - before
		EFFECT_CURE:
			for s: Variant in eff.get("statuses", []):
				var sid := StringName(str(s))
				if c.has_status(sid):
					c.statuses.erase(sid)
					(out["statuses_removed"] as Array).append(sid)
		EFFECT_REVIVE:
			if not c.is_alive():
				c.hp = revive_hp(c.max_hp, int(eff["hp_pct"]))
				out["amount"] = int(out["amount"]) - c.hp
				out["revived"] = true
		EFFECT_ADD_STATUS:
			var sid := StringName(str(eff["status"]))
			if c.add_status(sid, int(eff["duration"])):
				(out["statuses_added"] as Array).append(sid)
		EFFECT_DELAY:
			if c.is_alive():
				var ticks := Formulas.base_delay(c.agility) * int(eff["ranks"])
				c.next_time += ticks
				out["delay_ticks"] = int(out["delay_ticks"]) + ticks
		EFFECT_DAMAGE:
			var dmg := fixed_damage(int(eff["amount"]), c.affinity_for(StringName(str(eff.get("element", "none")))))
			out["amount"] = int(out["amount"]) - c.apply_damage(dmg)
		_:
			push_error("ItemBattleAction: unknown effect '%s'" % eff.get("type", ""))


## HP a revive item restores: max(1, floor(max_hp × hp_pct / 100)).
static func revive_hp(max_hp: int, hp_pct: int) -> int:
	return maxi(1, max_hp * hp_pct / PCT)


## Item damage is fixed: it ignores stats, defense and barriers, takes the element ratio of the
## target's affinity (Formulas.ELEMENT_RATIO, so absorb heals), and is capped at DAMAGE_CAP.
static func fixed_damage(amount: int, affinity: StringName) -> int:
	var el: Array = Formulas.ELEMENT_RATIO.get(affinity, Formulas.ELEMENT_RATIO[&"normal"])
	return clampi(amount * int(el[0]) / int(el[1]), -Formulas.DAMAGE_CAP, Formulas.DAMAGE_CAP)
