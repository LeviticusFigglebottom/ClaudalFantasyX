class_name BattleFloats
extends RefCounted
## Damage numbers, float words ("Reflected", "Heal turns to harm") and the camera shake for each
## resolved action, plus the end-of-turn HP changes an ActionResult cannot carry (M1-UI-02).
## Moved out of BattleController (M1-CMB-04) unchanged. A view: it reads the engine and the
## stage and never writes combat state.

var ctl: BattleController
## The acting fighter as the action resolved: {id, hp, zombie, regen, doom} (end-of-turn feedback).
var _snap: Dictionary = {}


func _init(controller: BattleController) -> void:
	ctl = controller


func reset() -> void:
	_snap = {}


func on_action_resolved(result: ActionResult) -> void:
	var actor := ctl.engine.find(result.actor_id)
	if actor != null:
		_snap = {
			"id": actor.id,
			"hp": actor.hp,
			"zombie": actor.has_status(&"zombie"),
			"regen": actor.has_status(&"regen"),
			"doom": actor.doom_count(),
		}
	var kind := str(ctl.engine.db.skill(result.skill_id).get("kind", ""))
	var stacks: Dictionary = {}
	var heavy := false
	for hit in result.hits:
		var tid: StringName = hit["target_id"]
		var target := ctl.engine.find(tid)
		var f := ctl.stage.stand_in(tid)
		# ActionResult.amount: positive = HP lost, negative = HP restored (BattleHits.resolve).
		var amount := int(hit["amount"])
		if f != null and amount > 0:
			f.flinch()
		heavy = heavy or bool(hit.get("crit", false))
		if not ctl.show_damage_numbers or target == null:
			continue
		var n := int(stacks.get(tid, 0))
		stacks[tid] = n + 1
		var at := ctl.head_pos(tid, &"damage")
		var ally := target.team == BattleCombatant.TEAM_PARTY
		if hit.has("reflected_from"):
			var from := StringName(str(hit["reflected_from"]))
			ctl.hud.pop_info(tr("HUD_FLOAT_REFLECTED"), ctl.head_pos(from, &"damage"), &"focus_gold")
		if not bool(hit["hit"]):
			ctl.hud.pop_number(tr("HUD_MISS"), at, DamageNumber.KIND_MISS, ally, false, n)
		elif amount > 0:
			ctl.hud.pop_number(str(amount), at, DamageNumber.KIND_DAMAGE, ally, bool(hit["crit"]), n)
			if kind == "heal":
				# Zombie: the heal landed as harm.
				ctl.hud.pop_info(tr("HUD_FLOAT_INVERTED"), at, &"danger")
		elif amount < 0:
			ctl.hud.pop_number(str(-amount), at, DamageNumber.KIND_HEAL, ally, false, n)
	if heavy and ctl.show_damage_numbers and ctl.hud.animations_enabled():
		ctl.stage.shake()


## End-of-turn HP changes the ActionResult cannot carry (Poison, Regen, Regen turned to harm by
## Zombie, and Doom running out), shown on the fighter who just acted.
func show_end_of_turn(actor_id: StringName) -> void:
	var snap := _snap
	_snap = {}
	if not ctl.show_damage_numbers or snap.is_empty() or StringName(str(snap["id"])) != actor_id:
		return
	var c := ctl.engine.find(actor_id)
	if c == null or not ctl.stage.has_fighter(actor_id):
		return
	var at := ctl.head_pos(actor_id, &"damage")
	var ally := c.team == BattleCombatant.TEAM_PARTY
	if int(snap["doom"]) == 1 and c.hp <= 0:
		ctl.hud.pop_info(tr("HUD_FLOAT_DOOM"), at, &"danger")
		return
	var delta := c.hp - int(snap["hp"])
	if delta < 0:
		ctl.hud.pop_number(str(-delta), at, DamageNumber.KIND_DAMAGE, ally, false)
		if bool(snap["zombie"]) and bool(snap["regen"]):
			ctl.hud.pop_info(tr("HUD_FLOAT_REGEN_INVERTED"), at, &"danger")
	elif delta > 0:
		ctl.hud.pop_number(str(delta), at, DamageNumber.KIND_HEAL, ally, false)
