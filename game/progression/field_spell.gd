class_name FieldSpell
extends RefCounted
## M3-CMB-05 (the human's playtest, 2026-11-03): a spell cast from the field menu, out of battle.
## Rules only, Node-free; ui-menus draws the screen (M3-MNU-05). formulas.md § Field spells.
##
## A skill is castable here when its skills.json row says `"field_usable": true` (validate_data
## `field_usable_errors`: an ally target, and a heal or a `cleanses` list). It runs on the party's
## combatants as the field menus build them (PartySheet.combatant: base, Lattice, gear and saved
## vitals), so the caster's skills, magic and MP are the real ones:
##   for_skill(db, id)          the spell, or null when the skill is unknown or battle-only
##   castable(db, caster)       the caster's field spells, in their skill order
##   caster_error(caster)       why the caster can't cast it now (down, no MP), or RESULT_OK
##   target_error(caster, t)    why it would do nothing for (or would harm) `t`, or RESULT_OK
##   reach(caster, party, t)    who a cast chosen on `t` reaches (all_allies: everyone it helps)
##   preview(caster, party, t)  the cast on copies: {ok, error, mp_cost, changes}, nothing changes
##   cast(caster, party, t)     the cast itself: the caster pays mp_cost once; returns the same
## The result also carries M3-CMB-1252's shape (ui-menus' Magic page): mp_spent (0 when refused),
## healed {id: HP gained}, cured {id: [status ids]} and revived [ids] (no field spell revives yet).
## A change is {id, hp_before, hp_after, removed: [status ids]}. The caller writes the vitals back
## (GameStateData.record_vitals, as ItemsMenuModel._save does) for the caster and every target.
## Deterministic: heals use Formulas.field_heal_amount (no RNG out of battle).

const RESULT_OK := &"ok"
const ERR_UNKNOWN := &"unknown"
const ERR_CASTER_DOWN := &"caster_down"
const ERR_NO_MP := &"no_mp"
const ERR_SILENCED := &"silenced"
const STATUS_SILENCE := &"silence"
const ERR_NOT_KNOWN := &"not_known"
const ERR_FALLEN := &"fallen"
const ERR_PETRIFIED := &"petrified"
const ERR_WOULD_HURT := &"would_hurt"
const ERR_NOTHING := &"nothing_to_do"
const ERR_NO_ONE := &"no_one"
const KIND_HEAL := &"heal"
const TARGET_SELF := &"self"
const TARGET_ALL_ALLIES := &"all_allies"
const TARGET_ALL_OTHER_ALLIES := &"all_other_allies"
const KEY_FIELD_USABLE := "field_usable"

var skill_id: StringName
var row: Dictionary = {}


## The field spell for `sid`, or null when the skill is unknown or not field_usable.
static func for_skill(db: BattleDB, sid: StringName) -> FieldSpell:
	var r := db.skill(sid)
	if not is_field_usable(r):
		return null
	var s := FieldSpell.new()
	s.skill_id = sid
	s.row = r
	return s


static func is_field_usable(r: Dictionary) -> bool:
	return bool(r.get(KEY_FIELD_USABLE, false))


## The field spells `caster` knows, in their skill order (each once).
static func castable(db: BattleDB, caster: BattleCombatant) -> Array[StringName]:
	var out: Array[StringName] = []
	if caster == null:
		return out
	for sid in caster.skills:
		if not out.has(sid) and is_field_usable(db.skill(sid)):
			out.append(sid)
	return out


func name_key() -> String:
	return str(row.get("name_key", ""))


func mp_cost() -> int:
	return int(row.get("mp_cost", 0))


func target() -> StringName:
	return StringName(str(row.get("target", "")))


## True for a spell that reaches several allies for one cost (all_allies, all_other_allies).
func is_group() -> bool:
	return target() in [TARGET_ALL_ALLIES, TARGET_ALL_OTHER_ALLIES]


## Why `caster` can't cast this now, or RESULT_OK.
func caster_error(caster: BattleCombatant) -> StringName:
	if caster == null:
		return ERR_UNKNOWN
	if not caster.skills.has(skill_id):
		return ERR_NOT_KNOWN
	if not caster.is_alive():
		return ERR_CASTER_DOWN
	if bool(row.get("magic", false)) and caster.has_status(STATUS_SILENCE):
		return ERR_SILENCED  # as in battle; Silence never outlasts a battle, so only a hand-made state hits this
	if caster.mp < mp_cost():
		return ERR_NO_MP
	return RESULT_OK


## Why this spell, cast by `caster`, would do nothing for `t` (or would harm them), or RESULT_OK.
## Says nothing about the caster (caster_error) or who a target kind may pick (reach).
func target_error(caster: BattleCombatant, t: BattleCombatant) -> StringName:
	if caster == null or t == null:
		return ERR_UNKNOWN
	if t.hp <= 0:
		return ERR_FALLEN
	if t.is_petrified():
		return ERR_PETRIFIED
	var trial := _apply(caster, t.sim_copy())
	if int(trial["hp_after"]) < int(trial["hp_before"]):
		return ERR_WOULD_HURT
	if int(trial["hp_after"]) == int(trial["hp_before"]) and (trial["removed"] as Array).is_empty():
		return ERR_NOTHING
	return RESULT_OK


## Who a cast chosen on `chosen` reaches: a group spell, every member of `party` it helps (not the
## caster for all_other_allies); a self spell, the caster when it helps; else `chosen` when it helps.
func reach(caster: BattleCombatant, party: Array[BattleCombatant], chosen: BattleCombatant) -> Array[BattleCombatant]:
	var out: Array[BattleCombatant] = []
	if is_group():
		for c in party:
			if target() == TARGET_ALL_OTHER_ALLIES and c == caster:
				continue
			if target_error(caster, c) == RESULT_OK:
				out.append(c)
		return out
	var t := caster if target() == TARGET_SELF else chosen
	if target_error(caster, t) == RESULT_OK:
		out.append(t)
	return out


## Why a cast chosen on `chosen` can't happen, or RESULT_OK: the caster's error first, then the
## target's (a group spell that helps nobody is ERR_NO_ONE).
func cast_error(caster: BattleCombatant, party: Array[BattleCombatant], chosen: BattleCombatant) -> StringName:
	var err := caster_error(caster)
	if err != RESULT_OK:
		return err
	if not reach(caster, party, chosen).is_empty():
		return RESULT_OK
	if is_group():
		return ERR_NO_ONE
	return target_error(caster, caster if target() == TARGET_SELF else chosen)


## The cast on detached copies: {ok, error, mp_cost, mp_before, mp_after, changes}. Changes nothing.
func preview(caster: BattleCombatant, party: Array[BattleCombatant], chosen: BattleCombatant) -> Dictionary:
	return _run(caster, party, chosen, false)


## Casts it: the caster pays mp_cost once and every target in reach() takes the effect. Returns the
## same dictionary as preview(); on an error nothing is spent or changed.
func cast(caster: BattleCombatant, party: Array[BattleCombatant], chosen: BattleCombatant) -> Dictionary:
	return _run(caster, party, chosen, true)


func _run(caster: BattleCombatant, party: Array[BattleCombatant], chosen: BattleCombatant, commit: bool) -> Dictionary:
	var out := {
		"ok": false,
		"error": RESULT_OK,
		"mp_cost": mp_cost(),
		"mp_spent": 0,
		"changes": [] as Array[Dictionary],
		"healed": {},
		"cured": {},
		"revived": [] as Array[StringName],
	}
	var err := cast_error(caster, party, chosen)
	out["error"] = err
	if err != RESULT_OK:
		return out
	out["mp_before"] = caster.mp
	out["mp_after"] = caster.mp - mp_cost()
	var changes: Array[Dictionary] = []
	for t in reach(caster, party, chosen):
		var ch := _apply(caster, t if commit else t.sim_copy())
		changes.append(ch)
		if int(ch["hp_after"]) != int(ch["hp_before"]):
			(out["healed"] as Dictionary)[ch["id"]] = int(ch["hp_after"]) - int(ch["hp_before"])
		if not (ch["removed"] as Array).is_empty():
			(out["cured"] as Dictionary)[ch["id"]] = ch["removed"]
	if commit:
		caster.mp -= mp_cost()
	out["changes"] = changes
	out["mp_spent"] = mp_cost()
	out["ok"] = true
	return out


## The effect on `t` (mutated): a heal (kind heal, Formulas.field_heal_amount from the caster's
## magic and level; a Zombie takes it as harm), then the `cleanses`.
func _apply(caster: BattleCombatant, t: BattleCombatant) -> Dictionary:
	var hp_before := t.hp
	var removed: Array[StringName] = []
	if StringName(str(row.get("kind", ""))) == KIND_HEAL:
		var amt := Formulas.field_heal_amount(
			int(row.get("power", 0)), caster.effective_magic(), caster.level, caster.break_damage_cap
		)
		t.restore_hp(amt)
	for s: Variant in row.get("cleanses", []):
		var sid := StringName(str(s))
		if t.has_status(sid):
			t.statuses.erase(sid)
			removed.append(sid)
	return {"id": t.id, "hp_before": hp_before, "hp_after": t.hp, "removed": removed}
