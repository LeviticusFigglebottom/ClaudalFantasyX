class_name FieldMagicRules
extends RefCounted
## The seam between the field Magic page (MagicMenuModel) and combat-systems' field cast rules (the human's playtest
## FAST-TRACK 5, 2026-11-03; combat-systems' M3-CMB-05 `FieldSpell`, game/progression/field_spell.gd). The page
## never decides what a spell does: it asks these three.
##   usable(caster: BattleCombatant) -> Array[StringName]   the caster's field spells, in its own order
##   refusal(caster, skill_id, targets: Array[BattleCombatant]) -> StringName   &"" when it may be cast, else why
##     (no targets: the caster alone; one: that hero as the target)
##   cast(caster, skill_id, targets) -> Dictionary   applies it to the combatants given and spends the MP
## live() binds the class named by magic_menu.json "rules_class" (FieldSpell) when the project has it, looked up by
## name so this page builds before that class is merged; without it the field menu shows no Magic row. Tests build
## one from Callables.

## FieldSpell's RESULT_OK; every other id it returns is a refusal (MagicMenuModel.REFUSAL_KEYS words it).
const SPELL_OK := &"ok"

var usable: Callable
var refusal: Callable
var cast: Callable

var _spell_script: Script
var _db: BattleDB


func _init(usable_fn: Callable = Callable(), refusal_fn: Callable = Callable(), cast_fn: Callable = Callable()) -> void:
	usable = usable_fn
	refusal = refusal_fn
	cast = cast_fn


func is_valid() -> bool:
	return usable.is_valid() and refusal.is_valid() and cast.is_valid()


## The rules over the global class `class_id` (FieldSpell's static castable and for_skill), or null when missing.
static func live(class_id: String = "") -> FieldMagicRules:
	var want := class_id if class_id != "" else str(MagicMenuModel.load_data().get("rules_class", ""))
	if want == "":
		return null
	for g: Dictionary in ProjectSettings.get_global_class_list():
		if str(g.get("class", "")) != want:
			continue
		var script := load(str(g.get("path", ""))) as Script
		if script == null or not script.has_method(&"castable") or not script.has_method(&"for_skill"):
			push_warning("FieldMagicRules: %s has no static castable() and for_skill()" % want)
			return null
		return over_spell_class(script, BattleDB.load_default())
	return null


## Rules over a FieldSpell-shaped class: castable(db, caster), for_skill(db, sid) and, on the spell, caster_error,
## target_error and cast(caster, party, chosen).
static func over_spell_class(script: Script, db: BattleDB) -> FieldMagicRules:
	var r := FieldMagicRules.new()
	r._spell_script = script
	r._db = db
	r.usable = r._usable
	r.refusal = r._refusal
	r.cast = r._cast
	return r


func _usable(caster: BattleCombatant) -> Array[StringName]:
	var out: Array[StringName] = []
	for sid: Variant in _spell_script.call(&"castable", _db, caster):
		out.append(StringName(str(sid)))
	return out


func _refusal(caster: BattleCombatant, sid: StringName, targets: Array[BattleCombatant]) -> StringName:
	var spell: Object = _spell_script.call(&"for_skill", _db, sid)
	if spell == null:
		return &"not_known"
	var err := StringName(str(spell.call(&"caster_error", caster)))
	if err == SPELL_OK and not targets.is_empty():
		err = StringName(str(spell.call(&"target_error", caster, targets[0])))
	return &"" if err == SPELL_OK else err


func _cast(caster: BattleCombatant, sid: StringName, targets: Array[BattleCombatant]) -> Dictionary:
	var spell: Object = _spell_script.call(&"for_skill", _db, sid)
	if spell == null or targets.is_empty():
		return {"ok": false}
	return spell.call(&"cast", caster, targets, targets[0]) as Dictionary
