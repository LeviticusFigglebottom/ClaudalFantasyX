class_name BattleMenus
extends RefCounted
## Builds CommandMenu rows and help-line text from read-only engine state, through localization
## keys only. Row: {id, label, right, right_role, enabled, help, skill}.

const PAGE_ROOT := &"root"
const PAGE_SKILLS := &"skills"
const PAGE_SWAP := &"swap"
const ROW_ATTACK := &"attack"
const ROW_SKILLS := &"skills"
const ROW_ESCAPE := &"escape"
const ROW_SWAP := &"swap"
const ATTACK_SKILL := &"attack"

## Ranks at or above this show in the swell color (docs/kb/art/ui.md §6.1).
var rank_swell_from := 3


func _init(swell_from: int = 3) -> void:
	rank_swell_from = swell_from


func display_name(c: BattleCombatant) -> String:
	if c == null:
		return ""
	return tr(c.name_key) if c.name_key != "" else String(c.id)


func skill_name(engine: BattleEngine, skill_id: StringName) -> String:
	var key := str(engine.db.skill(skill_id).get("name_key", ""))
	return tr(key) if key != "" else String(skill_id)


## Root page: Attack, Skills, Escape, then Swap (always the last row).
func root_rows(engine: BattleEngine) -> Array[Dictionary]:
	var actor := engine.current
	var rows: Array[Dictionary] = []
	var attack := engine.db.skill(ATTACK_SKILL)
	rows.append(
		_row(
			ROW_ATTACK,
			tr("HUD_CMD_ATTACK"),
			_rank_text(int(attack.get("rank", Formulas.DEFAULT_RANK))),
			_rank_role(int(attack.get("rank", Formulas.DEFAULT_RANK))),
			actor.skills.has(ATTACK_SKILL),
			ATTACK_SKILL
		)
	)
	rows.append(_row(ROW_SKILLS, tr("HUD_CMD_SKILLS"), "", &"text_dim", not skill_ids(actor).is_empty()))
	var chance := escape_chance(engine)
	var esc := _row(ROW_ESCAPE, tr("HUD_CMD_ESCAPE"), _pct_text(chance), &"text_dim", not engine.scripted)
	rows.append(esc)
	rows.append(_row(ROW_SWAP, tr("HUD_CMD_SWAP"), tr("HUD_COST_FREE"), &"focus", _has_living_reserve(engine)))
	return rows


## The actor's skills other than Attack, in their learned order.
func skill_ids(actor: BattleCombatant) -> Array[StringName]:
	var out: Array[StringName] = []
	for s in actor.skills:
		if s != ATTACK_SKILL:
			out.append(s)
	return out


func skill_rows(engine: BattleEngine) -> Array[Dictionary]:
	var actor := engine.current
	var rows: Array[Dictionary] = []
	for sid in skill_ids(actor):
		var sk := engine.db.skill(sid)
		var rank := int(sk.get("rank", Formulas.DEFAULT_RANK))
		var mp := int(sk.get("mp_cost", 0))
		var usable := actor.mp >= mp and not (bool(sk.get("magic", false)) and actor.has_status(&"silence"))
		var row := _row(sid, skill_name(engine, sid), _rank_text(rank), _rank_role(rank), usable, sid)
		row["mp"] = tr("HUD_MP_FMT").format({"mp": mp}) if mp > 0 else ""
		rows.append(row)
	return rows


func reserve_rows(engine: BattleEngine) -> Array[Dictionary]:
	var rows: Array[Dictionary] = []
	for c in engine.party_reserve:
		var right := tr("HUD_HP_FMT").format({"hp": c.hp, "max": c.max_hp})
		rows.append(_row(c.id, display_name(c), right, &"text_dim", c.is_alive()))
	return rows


func escape_chance(engine: BattleEngine) -> int:
	return Formulas.escape_chance(_mean_agility(engine.party_active), _mean_agility(engine.enemies))


## One help line for a skill: kind and reach, what it inflicts, its delay push, and when the
## actor acts again (`next_in` = turns between now and the actor's next turn; -1 = unknown).
func skill_help(engine: BattleEngine, skill_id: StringName, next_in: int) -> String:
	var sk := engine.db.skill(skill_id)
	var parts: PackedStringArray = []
	parts.append("%s, %s" % [_kind_text(str(sk.get("kind", ""))), _target_text(str(sk.get("target", "single_foe")))])
	for inflict: Variant in sk.get("statuses", []):
		var sid := str((inflict as Dictionary).get("id", ""))
		var key := str((engine.db.statuses.get(StringName(sid), {}) as Dictionary).get("name_key", ""))
		var status_name := tr(key) if key != "" else sid
		var fmt := "HUD_HELP_GRANTS_FMT" if StatusGlyph.is_buff(StringName(sid)) else "HUD_HELP_INFLICTS_FMT"
		parts.append(tr(fmt).format({"status": status_name}))
	var delay := int(sk.get("delay_ranks", 0))
	if delay > 0:
		parts.append(tr("HUD_HELP_DELAY_FMT").format({"n": delay}))
	if next_in >= 0:
		parts.append(next_turn_text(display_name(engine.current), next_in))
	return " · ".join(parts)


func next_turn_text(actor_name: String, next_in: int) -> String:
	if next_in <= 0:
		return tr("HUD_HELP_NEXT_ONE").format({"name": actor_name})
	return tr("HUD_HELP_NEXT_FMT").format({"name": actor_name, "n": next_in})


func escape_help(engine: BattleEngine) -> String:
	if engine.scripted:
		return tr("HUD_HELP_ESCAPE_SCRIPTED")
	return tr("HUD_HELP_ESCAPE_FMT").format({"pct": escape_chance(engine)})


func swap_in_help(engine: BattleEngine, incoming: BattleCombatant) -> String:
	return tr("HUD_HELP_SWAP_IN_FMT").format({"name": display_name(incoming), "out": display_name(engine.current)})


func swap_out_help(incoming: BattleCombatant) -> String:
	return tr("HUD_HELP_SWAP_OUT_FMT").format({"name": display_name(incoming)})


func group_label(hostile: bool) -> String:
	return tr("HUD_GROUP_ALL_FOES") if hostile else tr("HUD_GROUP_ALL_ALLIES")


func _row(
	rid: StringName, label: String, right: String, role: StringName, enabled: bool, skill: StringName = &""
) -> Dictionary:
	return {"id": rid, "label": label, "right": right, "right_role": role, "enabled": enabled, "skill": skill}


func _rank_text(rank: int) -> String:
	return tr("HUD_RANK_FMT").format({"rank": rank})


func _rank_role(rank: int) -> StringName:
	return &"swell" if rank >= rank_swell_from else &"text_dim"


func _pct_text(pct: int) -> String:
	return tr("HUD_CHANCE_FMT").format({"pct": pct})


func _kind_text(kind: String) -> String:
	match kind:
		"physical":
			return tr("HUD_KIND_PHYSICAL")
		"magical":
			return tr("HUD_KIND_MAGICAL")
		"heal":
			return tr("HUD_KIND_HEAL")
	return tr("HUD_KIND_SUPPORT")


func _target_text(target: String) -> String:
	match target:
		"all_foes":
			return tr("HUD_TARGET_ALL_FOES")
		"single_ally":
			return tr("HUD_TARGET_SINGLE_ALLY")
		"all_allies":
			return tr("HUD_TARGET_ALL_ALLIES")
		"self":
			return tr("HUD_TARGET_SELF")
	return tr("HUD_TARGET_SINGLE_FOE")


func _has_living_reserve(engine: BattleEngine) -> bool:
	for c in engine.party_reserve:
		if c.is_alive():
			return true
	return false


static func _mean_agility(list: Array[BattleCombatant]) -> float:
	var total := 0
	var n := 0
	for c in list:
		if c.is_alive():
			total += c.agility
			n += 1
	return float(total) / n if n > 0 else 0.0
