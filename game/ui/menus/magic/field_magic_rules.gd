class_name FieldMagicRules
extends RefCounted
## The seam between the field Magic page (MagicMenuModel) and combat-systems' field cast rules (M3-CMB-1252; the
## human's playtest FAST-TRACK 5, 2026-11-03). The page never decides what a spell does: it asks these three.
##   usable(caster: BattleCombatant) -> Array[StringName]   the caster's field-usable skills, in its own order
##   refusal(caster, skill_id, targets: Array[BattleCombatant]) -> StringName   &"" when it may be cast, else why
##   cast(caster, skill_id, targets) -> Dictionary   applies it to the combatants given and spends the MP
## live() binds the class named by magic_menu.json "rules_class" (combat-systems' static API) when the project has
## it, else returns null and the field menu shows no Magic row: no dead page before the rules land. Tests build
## one from Callables.

var usable: Callable
var refusal: Callable
var cast: Callable


func _init(usable_fn: Callable = Callable(), refusal_fn: Callable = Callable(), cast_fn: Callable = Callable()) -> void:
	usable = usable_fn
	refusal = refusal_fn
	cast = cast_fn


func is_valid() -> bool:
	return usable.is_valid() and refusal.is_valid() and cast.is_valid()


## The rules from the global class `class_id` (static usable, refusal and cast), or null when it is missing.
static func live(class_id: String = "") -> FieldMagicRules:
	var want := class_id if class_id != "" else str(MagicMenuModel.load_data().get("rules_class", ""))
	if want == "":
		return null
	for g: Dictionary in ProjectSettings.get_global_class_list():
		if str(g.get("class", "")) != want:
			continue
		var script := load(str(g.get("path", ""))) as Script
		if script == null:
			return null
		for m: String in ["usable", "refusal", "cast"]:
			if not script.has_method(m):
				push_warning("FieldMagicRules: %s has no static %s()" % [want, m])
				return null
		return FieldMagicRules.new(Callable(script, "usable"), Callable(script, "refusal"), Callable(script, "cast"))
	return null
