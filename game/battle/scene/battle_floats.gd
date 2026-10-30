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


## Snapshot and floats at once (BattleChoreo splits them: the snapshot as the action resolves, the floats on
## its contact beat).
func on_action_resolved(result: ActionResult) -> void:
	snapshot(result)
	show_hits(result, true)


## Remembers the actor as the action resolved, for show_end_of_turn.
func snapshot(result: ActionResult) -> void:
	var actor := ctl.engine.find(result.actor_id)
	if actor != null:
		_snap = {
			"id": actor.id,
			"hp": actor.hp,
			"zombie": actor.has_status(&"zombie"),
			"regen": actor.has_status(&"regen"),
			"doom": actor.doom_count(),
		}


## The action's damage numbers, float words and heavy-hit shake. `flinch` = false when BattleChoreo moves the
## targets itself.
func show_hits(result: ActionResult, flinch: bool) -> void:
	var kind := str(ctl.engine.db.skill(result.skill_id).get("kind", ""))
	var stacks: Dictionary = {}
	var heavy := false
	if ctl.show_damage_numbers and result.intercepted_by != &"":
		# M3-UI-100: a guard stepped in front of the ward (Hold the Stair); the hits already name the guard.
		ctl.hud.pop_info(tr("HUD_FLOAT_INTERCEPTED"), ctl.head_pos(result.intercepted_by, &"damage"), &"focus_gold")
	for hit in result.hits:
		var tid: StringName = hit["target_id"]
		var target := ctl.engine.find(tid)
		var f := ctl.stage.stand_in(tid)
		# ActionResult.amount: positive = HP lost, negative = HP restored (BattleHits.resolve).
		var amount := int(hit["amount"])
		if flinch and f != null and amount > 0:
			f.flinch(ctl.stage.battle_speed(ctl.hud.battle_speed()))
		heavy = heavy or bool(hit.get("crit", false))
		if not ctl.show_damage_numbers or target == null:
			continue
		var n := int(stacks.get(tid, 0))
		stacks[tid] = n + 1
		var at := ctl.head_pos(tid, &"damage")
		var ally := target.team == BattleCombatant.TEAM_PARTY
		_set_piece_words(hit, at)
		_act2_words(result, hit, at)
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
	if heavy and flinch and ctl.show_damage_numbers and ctl.hud.animations_enabled():  # BattleImpact shakes a sequence
		ctl.stage.shake(ctl.stage.battle_speed(ctl.hud.battle_speed()))


## M3-UI-100: a set piece's float words on a hit: a counter (Stand Firm) over the one who struck back, a foe
## drawn off by the Kirru's Storm-Call.
func _set_piece_words(hit: Dictionary, at: Vector2) -> void:
	if hit.has("counter_by"):
		var by := StringName(str(hit["counter_by"]))
		ctl.hud.pop_info(tr("HUD_FLOAT_COUNTER"), ctl.head_pos(by, &"damage"), &"focus_gold")
	if bool(hit.get("withdrawn", false)):
		ctl.hud.pop_info(tr("HUD_FLOAT_WITHDRAWN"), at, &"text_dim")


## Act II's hit words (docs/kb/plan/act2/ui/hud.md sections 2 and 3): a drain's heal over its user (the fen
## leech, M4-CMB-1001), and a mended part over the boss a conduit crawler repaired (M4-A2P-022), named by its charge.
func _act2_words(result: ActionResult, hit: Dictionary, at: Vector2) -> void:
	var drained := int(hit.get("drained", 0))
	var user := ctl.engine.find(result.actor_id)
	if drained > 0 and user != null:
		var from := ctl.head_pos(result.actor_id, &"damage")
		ctl.hud.pop_number(str(drained), from, DamageNumber.KIND_HEAL, user.team == BattleCombatant.TEAM_PARTY, false)
		ctl.hud.pop_info(tr("HUD_FLOAT_DRAINED"), from, &"danger")
	if hit.has("part_restored"):
		var part := str(ctl.engine.db.skill(StringName(str(hit["part_restored"]))).get("name_key", ""))
		ctl.hud.pop_info(tr("HUD_FLOAT_REPAIRED_FMT").format({"part": tr(part)}), at, &"danger")


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
