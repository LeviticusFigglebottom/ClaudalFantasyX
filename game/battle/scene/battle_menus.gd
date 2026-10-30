class_name BattleMenus
extends RefCounted
## Builds CommandMenu rows and help-line text from read-only engine state, through localization
## keys only. Row: {id, label, right, right_role, enabled, help, skill}.

const PAGE_ROOT := &"root"
const PAGE_SKILLS := &"skills"
const PAGE_SWAP := &"swap"
const PAGE_ITEMS := &"items"
const PAGE_SWELL := &"swell"
const ROW_ATTACK := &"attack"
const ROW_SKILLS := &"skills"
const ROW_ESCAPE := &"escape"
const ROW_SWAP := &"swap"
const ROW_ITEMS := &"items"
const ROW_SWELL := &"swell"
## A Swell page row that chooses a fill mode (M2-UI-01) carries the mode id under this key.
const KEY_SWELL_MODE := "swell_mode"
const ROW_SWELL_MODE_PREFIX := "swell_mode_"
## Vowbound rows (M2-UI-05): the caller's Call rows ("call_<id>", the id under KEY_VOWBOUND), and
## the Vowbound's own Dismiss and finisher rows.
const ROW_CALL_PREFIX := "call_"
const KEY_VOWBOUND := "vowbound"
const ROW_DISMISS := &"dismiss"
const ROW_UNLEASH := &"unleash"
const ATTACK_SKILL := &"attack"
const AUTO_BERSERK := &"berserk"
const AUTO_CONFUSE := &"confuse"
## Every ActionResult.fail_reason the engine and the controller can produce. Each has its own
## line in fail_text(); tests/unit/test_battle_controller.gd checks this list against the engine.
const FAIL_REASONS: Array[StringName] = [
	&"no_mp",
	&"silenced",
	&"no_valid_target",
	&"provoked",
	&"auto_turn",
	&"not_your_turn",
	&"battle_over",
	&"unknown_skill",
	&"no_valid_action",
	&"no_item",
	&"unknown_item",
	&"swell_not_full",
	&"unknown_technique",
	&"swell_cancelled",
	&"vowbound_out",
	&"unknown_vowbound",
	&"not_bound",
	&"not_caller",
	&"vowbound_fallen",
	&"no_vowbound",
]

## Ranks at or above this show in the swell color (docs/kb/art/ui.md §6.1).
var rank_swell_from := 3


func _init(swell_from: int = 3) -> void:
	rank_swell_from = swell_from


func display_name(c: BattleCombatant) -> String:
	if c == null:
		return ""
	var key := c.name_key
	if c.team == BattleCombatant.TEAM_PARTY:
		key = CharacterNames.key_for(c.id, key)  # "The Kirru" until named (M3-C09-05)
	return tr(key) if key != "" else String(c.id)


func skill_name(engine: BattleEngine, skill_id: StringName) -> String:
	var key := str(engine.db.skill(skill_id).get("name_key", ""))
	return tr(key) if key != "" else String(skill_id)


## Root page: Attack, Swell (for a hero with a Swell, M1-CMB-04; M2-UI-01 keeps it on the menu
## while the gauge fills, so the fill mode can be chosen: the right column names the input when
## the gauge is full, else the mode in force), Skills, Items (only when the battle has a bag:
## capture fixtures have none), Escape, then Swap (always the last row). A caller gets its Call
## rows after Skills (call_rows); while a Vowbound holds the field the page is its own
## (vowbound_root_rows).
func root_rows(engine: BattleEngine, items: BattleItemSource = null, swell: BattleSwell = null) -> Array[Dictionary]:
	if engine.vowbound.is_out():
		return vowbound_root_rows(engine)
	var actor := engine.current
	var rows: Array[Dictionary] = [_attack_row(engine)]
	# Only an input the HUD draws (SwellRingView.draws: every kind since M2-UI-03).
	var has_page := swell != null and swell.has_swell(actor) and actor.is_alive()
	if has_page and not swell.techniques(actor).is_empty() and SwellRingView.draws(swell.input_for(actor)):
		var input_key := str(swell.input_for(actor).get("name_key", ""))
		if swell.is_ready(actor):
			rows.append(_row(ROW_SWELL, tr("HUD_CMD_SWELL"), tr(input_key) if input_key != "" else "", &"swell", true))
		else:
			var mode_name := swell_mode_name(swell, actor.swell_mode)
			rows.append(_row(ROW_SWELL, tr("HUD_CMD_SWELL"), mode_name, &"text_dim", true))
	rows.append(_row(ROW_SKILLS, tr("HUD_CMD_SKILLS"), "", &"text_dim", not skill_ids(actor).is_empty()))
	rows.append_array(call_rows(engine))
	if items != null:
		rows.append(_row(ROW_ITEMS, tr("HUD_CMD_ITEMS"), "", &"text_dim", _any_usable(engine, items)))
	var chance := escape_chance(engine)
	var esc := _row(ROW_ESCAPE, tr("HUD_CMD_ESCAPE"), _pct_text(chance), &"text_dim", not engine.scripted)
	rows.append(esc)
	rows.append(_row(ROW_SWAP, tr("HUD_CMD_SWAP"), tr("HUD_COST_FREE"), &"focus", _has_living_reserve(engine)))
	return rows


## The Attack row plays the actor's attack_skill: Attack, or an encounter's override (M3-CMB-01:
## Toma's Stand Firm at the stair-head), which the row then names.
func _attack_row(engine: BattleEngine) -> Dictionary:
	var sid := engine.current.attack_skill
	var rank := int(engine.db.skill(sid).get("rank", Formulas.DEFAULT_RANK))
	var known := engine.current.skills.has(sid)
	known = known and not BossMechanics.forbidden_now(engine, engine.current, engine.db.skill(sid))
	var label := tr("HUD_CMD_ATTACK") if sid == ATTACK_SKILL else skill_name(engine, sid)
	return _row(ROW_ATTACK, label, _rank_text(rank), _rank_role(rank), known, sid)


## The acting caller's Call rows (M2-UI-05, ADR 0027): one per Vowbound it has bound, in data
## order. Open, a row shows the call's rank (the caller pays it once the party is back); greyed,
## it names the refusal on the right ("Silenced", "Fallen"). A caller with none bound yet gets no
## row (Lead decision on M2-UI-05: no dead row hinting at Chapter 3), nor does a non-caller.
func call_rows(engine: BattleEngine) -> Array[Dictionary]:
	var vb := engine.vowbound
	var bound: Array[StringName] = []
	for vid: StringName in vb.rows:
		var caller := StringName(str((vb.rows[vid] as Dictionary).get("caller", "")))
		if caller == engine.current.id and vb.known.has(vid):
			bound.append(vid)
	var rows: Array[Dictionary] = []
	for vid in bound:
		var fail := vb.refusal(engine, vid)
		var rank := int((vb.rows[vid] as Dictionary).get("call_rank", Formulas.DEFAULT_RANK))
		var label := tr("HUD_CMD_CALL_FMT").format({"name": vowbound_name(vb, vid)})
		var row := _row(StringName(ROW_CALL_PREFIX + String(vid)), label, _rank_text(rank), _rank_role(rank), true)
		if fail != &"":
			row["right"] = call_refusal_word(fail)
			row["right_role"] = &"text_dim"
			row["enabled"] = false
		row[KEY_VOWBOUND] = vid
		rows.append(row)
	return rows


## The short word a greyed Call row shows for `reason` (BattleVowbound.refusal).
func call_refusal_word(reason: StringName) -> String:
	match reason:
		BattleVowbound.FAIL_SILENCED:
			return tr("HUD_CALL_SILENCED")
		BattleVowbound.FAIL_FALLEN:
			return tr("HUD_CALL_FALLEN")
		BattleVowbound.FAIL_NOT_BOUND:
			return tr("HUD_CALL_NOT_BOUND")
	return tr("HUD_CALL_REFUSED")


## The root page while a Vowbound holds the field (M2-UI-05): Attack, its finisher (greyed until
## the gauge is full, the right column showing how full), Skills and Dismiss, then Escape and Swap
## greyed out (refused while it is out: vowbound_out). Items is left off ("a Vowbound uses no
## items"), so the page stays at six rows, the most the root shows.
func vowbound_root_rows(engine: BattleEngine) -> Array[Dictionary]:
	var vb := engine.vowbound
	var s := engine.current
	var rows: Array[Dictionary] = [_attack_row(engine)]
	var tid := vb.finisher(s)
	if tid != &"":
		var rank := int(engine.db.skill(tid).get("rank", Formulas.DEFAULT_RANK))
		var ready := vb.unleash_refusal(engine) == &"" and not skill_candidates(engine, tid).is_empty()
		var right := _rank_text(rank)
		if not ready:
			right = tr("HUD_VOWBOUND_GAUGE_FMT").format(
				{"pct": roundi(float(Formulas.PCT) * s.swell / Formulas.SWELL_MAX)}
			)
		rows.append(
			_row(ROW_UNLEASH, skill_name(engine, tid), right, _rank_role(rank) if ready else &"text_dim", ready, tid)
		)
	rows.append(_row(ROW_SKILLS, tr("HUD_CMD_SKILLS"), "", &"text_dim", not skill_ids(s).is_empty()))
	var can_go := vb.dismiss_refusal(engine) == &""
	rows.append(_row(ROW_DISMISS, tr("HUD_CMD_DISMISS"), tr("HUD_DISMISS_COST"), &"text_dim", can_go))
	rows.append(_row(ROW_ESCAPE, tr("HUD_CMD_ESCAPE"), "", &"text_dim", false))
	rows.append(_row(ROW_SWAP, tr("HUD_CMD_SWAP"), "", &"text_dim", false))
	return rows


## The skill a root row plays: Attack, or the Vowbound's finisher on ROW_UNLEASH.
func root_skill(engine: BattleEngine, rid: StringName) -> StringName:
	if rid == ROW_UNLEASH and engine.vowbound.is_out():
		return engine.vowbound.finisher(engine.vowbound.summon)
	return engine.current.attack_skill if engine.current != null else ATTACK_SKILL


func vowbound_name(vb: BattleVowbound, vid: StringName) -> String:
	var key := str((vb.rows.get(vid, {}) as Dictionary).get("name_key", ""))
	return tr(key) if key != "" else String(vid)


## The help line on a Call row: who takes the turn, and what the call costs the caller once the
## party is back (pillar 4; the timeline shows the order with the Vowbound in it).
func call_help(engine: BattleEngine, vid: StringName) -> String:
	var vb := engine.vowbound
	var rank := int((vb.rows.get(vid, {}) as Dictionary).get("call_rank", Formulas.DEFAULT_RANK))
	var words := {"vowbound": vowbound_name(vb, vid), "caller": display_name(engine.current), "rank": rank}
	return tr("HUD_HELP_CALL_FMT").format(words)


## The help line on Dismiss: the turn is spent and the party is back, and when the caller acts
## again in `after` (BattleVowbound.preview_dismiss).
func dismiss_help(engine: BattleEngine, after: Array[TurnEntry]) -> String:
	var vb := engine.vowbound
	var s := vb.summon
	var parts: PackedStringArray = [tr("HUD_HELP_DISMISS_FMT").format({"vowbound": display_name(s)})]
	var caller := engine.find(StringName(str((vb.rows.get(s.id, {}) as Dictionary).get("caller", ""))))
	for i in after.size():
		if caller != null and after[i].combatant_id == caller.id:
			parts.append(next_turn_text(display_name(caller), i))
			break
	return " · ".join(parts)


## What happened when a Vowbound left the field: it fell (and cannot be called again this battle),
## or it was dismissed or the battle was won.
func departed_text(s: BattleCombatant, fell: bool) -> String:
	var key := "HUD_VOWBOUND_FELL_FMT" if fell else "HUD_VOWBOUND_LEFT_FMT"
	return tr(key).format({"vowbound": display_name(s)})


## The party panel's note while a Vowbound is out: who stood down for it.
func stood_down_text(engine: BattleEngine) -> String:
	var names: PackedStringArray = []
	for c in engine.vowbound.stood_down:
		names.append(display_name(c))
	return tr("HUD_VOWBOUND_STOOD_DOWN_FMT").format({"names": ", ".join(names)})


## The actor's skills other than Attack (or the skill its Attack plays), in their learned order.
func skill_ids(actor: BattleCombatant) -> Array[StringName]:
	var out: Array[StringName] = []
	for s in actor.skills:
		if s != ATTACK_SKILL and s != actor.attack_skill:
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
		usable = usable and BossMechanics.refusal(engine, sk) == &""  # e.g. Call Ilun with no field up
		usable = usable and not BossMechanics.forbidden_now(engine, actor, sk)  # Toma and the Stillguard
		usable = usable and BattleCycle.allows(actor, sid)  # M4-A2P-025: Kesh's voice for this turn only
		var row := _row(sid, skill_name(engine, sid), _rank_text(rank), _rank_role(rank), usable, sid)
		row["mp"] = tr("HUD_MP_FMT").format({"mp": mp}) if mp > 0 else ""
		row["glyph"] = MenuGlyph.for_skill_row(sk)
		rows.append(row)
	return rows


## The Swell page: the actor's techniques (BattleSwell.techniques: name and rank, no MP; greyed out
## until the gauge is full, or while nobody is in reach, e.g. a song for the others with no other ally
## standing), then one row per unlocked fill mode (M2-UI-01, swell_mode_rows).
func swell_rows(engine: BattleEngine, swell: BattleSwell) -> Array[Dictionary]:
	var rows: Array[Dictionary] = []
	var full := swell.is_full(engine.current)
	for tid in swell.techniques(engine.current):
		var rank := int(engine.db.skill(tid).get("rank", Formulas.DEFAULT_RANK))
		var reach := not skill_candidates(engine, tid).is_empty()
		var row := _row(tid, skill_name(engine, tid), _rank_text(rank), _rank_role(rank), full and reach, tid)
		row["glyph"] = MenuGlyph.for_skill_row(engine.db.skill(tid))
		rows.append(row)
	rows.append_array(swell_mode_rows(swell, engine.current))
	return rows


## One row per fill mode `actor` may choose (BattleSwell.mode_rows, the M2-CMB-01 API: the unlocked
## modes in data order): the mode's name, and "In use" or the free cost on the right. Choosing one
## costs no time.
func swell_mode_rows(swell: BattleSwell, actor: BattleCombatant) -> Array[Dictionary]:
	var rows: Array[Dictionary] = []
	for m: Dictionary in swell.mode_rows(actor):
		var mid := StringName(str(m.get("id", "")))
		var current := bool(m.get("current", false))
		var right := tr("HUD_SWELL_MODE_IN_USE") if current else tr("HUD_COST_FREE")
		var rid := StringName(ROW_SWELL_MODE_PREFIX + String(mid))
		var key := str(m.get("name_key", ""))
		var row := _row(rid, tr(key) if key != "" else String(mid), right, &"swell" if current else &"focus", true)
		row[KEY_SWELL_MODE] = mid
		rows.append(row)
	return rows


func swell_mode_name(swell: BattleSwell, mode: StringName) -> String:
	var key := str((swell.modes.get(mode, {}) as Dictionary).get("name_key", ""))
	return tr(key) if key != "" else String(mode)


## The help line on a fill-mode row: what fills the gauge in that mode, and that choosing it is
## free (or that it is already in use).
func swell_mode_help(swell: BattleSwell, actor: BattleCombatant, mode: StringName) -> String:
	var key := str((swell.modes.get(mode, {}) as Dictionary).get("desc_key", ""))
	var words := {"mode": swell_mode_name(swell, mode), "desc": tr(key) if key != "" else ""}
	if actor.swell_mode == mode:
		return tr("HUD_HELP_SWELL_MODE_CURRENT_FMT").format(words)
	return tr("HUD_HELP_SWELL_MODE_FMT").format(words)


## The help line once a mode is chosen.
func swell_mode_set_text(swell: BattleSwell, actor: BattleCombatant) -> String:
	var words := {"name": display_name(actor), "mode": swell_mode_name(swell, actor.swell_mode)}
	return tr("HUD_SWELL_MODE_SET_FMT").format(words)


## The help line on the root Swell row: full and ready, or how full and in which mode.
func swell_root_help(engine: BattleEngine, swell: BattleSwell) -> String:
	var actor := engine.current
	if swell.is_ready(actor):
		return tr("HUD_HELP_SWELL_FMT").format({"name": display_name(actor)})
	var pct := roundi(float(Formulas.PCT) * actor.swell / Formulas.SWELL_MAX)
	var words := {"name": display_name(actor), "pct": pct, "mode": swell_mode_name(swell, actor.swell_mode)}
	return tr("HUD_HELP_SWELL_GAUGE_FMT").format(words)


## The help line for a technique: what its input asks, then the skill's own line.
func swell_help(engine: BattleEngine, swell: BattleSwell, tid: StringName, next_in: int) -> String:
	var input := swell.input_for(engine.current)
	var key := str(input.get("help_key", ""))
	var parts: PackedStringArray = []
	if key != "":
		# The count is data (swell.json "beats"), never written into the string (M1-UI-05).
		parts.append(tr(key).format({"beats": int(input.get("beats", 1))}))
	parts.append(skill_help(engine, tid, next_in))
	return " · ".join(parts)


## What the input earned, for the help line: "Perfect · Good · Miss: +45% power".
func swell_result_text(grades: Array, bonus_pct: int) -> String:
	var words: PackedStringArray = []
	for g: Variant in grades:
		words.append(grade_text(StringName(str(g))))
	return tr("HUD_SWELL_RESULT_FMT").format({"grades": " · ".join(words), "pct": bonus_pct})


## Any kind's grade in words (Perfect, Good, Braced, Traced, Swift; anything else reads as Miss).
func grade_text(grade: StringName) -> String:
	return tr(SwellRingView.grade_key(grade))


## Battle items the party holds, in bag order: name, count, rank. A row is greyed out while
## nobody on the field can take it (a Wick with no one fallen and no Zombie standing).
func item_rows(engine: BattleEngine, items: BattleItemSource) -> Array[Dictionary]:
	var rows: Array[Dictionary] = []
	if items == null:
		return rows
	for iid in items.usable():
		var action := items.action_for(iid)
		if action == null:
			continue
		var usable := not item_candidates(engine, action).is_empty()
		var row := _row(iid, item_name(items, iid), _rank_text(action.rank), _rank_role(action.rank), usable)
		row["item"] = iid
		row["glyph"] = MenuGlyph.for_goods(iid)
		row["mp"] = tr("HUD_ITEM_COUNT_FMT").format({"n": items.count(iid)})
		rows.append(row)
	return rows


## Who `action` may be aimed at right now, in field order: the acting fighter for self items,
## else the active allies or the foes that BattleEngine.item_can_target admits (revives take
## the fallen and living Zombies; only a petrify cure reaches stone). Items ignore Provoke.
func item_candidates(engine: BattleEngine, action: ItemBattleAction) -> Array[BattleCombatant]:
	var out: Array[BattleCombatant] = []
	if action == null or engine.current == null:
		return out
	var pool: Array[BattleCombatant] = []
	if action.target == ItemBattleAction.TARGET_SELF:
		pool.append(engine.current)
	elif action.targets_allies():
		pool = engine.party_active
	else:
		pool = engine.enemies
	for c in pool:
		if BattleEngine.item_can_target(action, c):
			out.append(c)
	return out


## Who the cursor may pick for `skill_id`: the provoker alone while Provoke forces it, otherwise
## every living foe or ally the skill's reach allows (never the actor for "all_other_allies").
func skill_candidates(engine: BattleEngine, skill_id: StringName) -> Array[BattleCombatant]:
	var kind := str(engine.db.skill(skill_id).get("target", "single_foe"))
	var forced := engine.forced_target(engine.current, skill_id)
	if forced != null:
		var only: Array[BattleCombatant] = [forced]
		return only
	if kind.ends_with("foe") or kind.ends_with("foes"):
		return engine.living_foes_of(engine.current)
	if kind == "all_other_allies":
		return engine.living_other_allies_of(engine.current)
	if kind == BattleSetPiece.TARGET_WARD:  # the Climb (M3-CMB-01)
		var ward: Array[BattleCombatant] = []
		if engine.ward() != null:
			ward.append(engine.ward())
		return ward
	return engine.living_allies_of(engine.current)


## The target a skill starts on: the provoker when Provoked, the last foe you hit (`last_foe`),
## the most hurt ally for heals, yourself for other ally skills, or everyone for group skills.
func default_targets(engine: BattleEngine, skill_id: StringName, last_foe: StringName) -> Array[BattleCombatant]:
	var sk := engine.db.skill(skill_id)
	var kind := str(sk.get("target", "single_foe"))
	var pool := skill_candidates(engine, skill_id)
	var out: Array[BattleCombatant] = []
	if pool.is_empty() and kind != "self":
		return out
	if kind == "self":
		out.append(engine.current)
	elif kind.begins_with("all_") or kind == BattleSetPiece.TARGET_WARD:
		out = pool
	elif kind == "single_foe":
		var last := engine.find(last_foe)
		out.append(last if last != null and last.is_alive() and pool.has(last) else pool[0])
	elif str(sk.get("kind", "")) == "heal":
		out.append(_most_hurt(pool))
	else:
		out.append(engine.current)
	return out


## The target an item starts on: everyone for group items, the last foe you hit for foe items,
## the first fallen ally for a revive (else the first who can take it: a living Zombie), and
## otherwise the most hurt ally (yourself for self items, the only candidate).
func default_item_targets(
	engine: BattleEngine, action: ItemBattleAction, last_foe: StringName
) -> Array[BattleCombatant]:
	var pool := item_candidates(engine, action)
	var out: Array[BattleCombatant] = []
	if pool.is_empty():
		return out
	if String(action.target).begins_with("all_"):
		return pool
	var best := pool[0]
	if not action.targets_allies():
		var last := engine.find(last_foe)
		best = last if last != null and pool.has(last) else pool[0]
	elif action.targets_fallen:
		for c in pool:
			if c.hp <= 0:
				best = c
				break
	else:
		best = _most_hurt(pool)
	out.append(best)
	return out


func item_name(items: BattleItemSource, iid: StringName) -> String:
	var action := items.action_for(iid) if items != null else null
	return tr(action.name_key) if action != null and action.name_key != "" else String(iid)


## One help line for an item: its description (when the bag knows it) and when the actor acts
## again (`next_in` as in skill_help).
func item_help(engine: BattleEngine, items: BattleItemSource, iid: StringName, next_in: int) -> String:
	var parts: PackedStringArray = []
	var bag := items as InventoryItemSource
	if bag != null:
		var key := str(bag.db.item(iid).get("desc_key", ""))
		if key != "":
			parts.append(tr(key))
	if next_in >= 0:
		parts.append(next_turn_text(display_name(engine.current), next_in))
	return " · ".join(parts)


## Notes that change what an item will really do to `target`, most serious first: the use that
## loses the fight on the spot (a Zombie reviving itself as the last one standing), a revive
## that fells a living Zombie, and a heal that a Zombie turns to harm.
func item_notes(
	engine: BattleEngine, items: BattleItemSource, iid: StringName, target: BattleCombatant
) -> PackedStringArray:
	var out: PackedStringArray = []
	var action := items.action_for(iid) if items != null else null
	if action == null or target == null:
		return out
	var who := {"name": display_name(target)}
	var only: Array[BattleCombatant] = [target]
	if engine.item_defeats_party(iid, only, items):
		out.append(tr("HUD_HELP_ITEM_DEFEAT_FMT").format(who))
	elif BattleEngine.item_can_target(action, target) and BattleEngine.item_fells(action, target):
		out.append(tr("HUD_HELP_ITEM_FELLS_FMT").format(who))
	elif target.has_status(&"zombie") and _heals_hp(action):
		out.append(tr("HUD_HELP_ZOMBIE_FMT").format(who))
	return out


func reserve_rows(engine: BattleEngine) -> Array[Dictionary]:
	var rows: Array[Dictionary] = []
	for c in engine.party_reserve:
		var right := tr("HUD_HP_FMT").format({"hp": c.hp, "max": c.max_hp})
		rows.append(_row(c.id, display_name(c), right, &"text_dim", c.is_alive()))
	# M3-UI-100: a hero a set piece keeps out of the fight is listed, greyed, with the reason ("Not with the party").
	var reason := tr(engine.unavailable_key) if engine.unavailable_key != "" else ""
	for hid in engine.unavailable:
		var key := CharacterNames.key_for(
			hid, str((engine.db.characters.get(hid, {}) as Dictionary).get("name_key", ""))
		)
		rows.append(_row(hid, tr(key) if key != "" else String(hid), reason, &"text_dim", false))
	return rows


func escape_chance(engine: BattleEngine) -> int:
	return Formulas.escape_chance(_mean_agility(engine.party_active), _mean_agility(engine.enemies))


## One help line for a skill: kind and reach, what it inflicts, its delay push, and when the
## actor acts again (`next_in` = turns between now and the actor's next turn; -1 = unknown).
func skill_help(engine: BattleEngine, skill_id: StringName, next_in: int) -> String:
	var sk := engine.db.skill(skill_id)
	if BossMechanics.forbidden_now(engine, engine.current, sk):
		return fail_text(BossMechanics.FAIL_FORBIDDEN, engine.current)  # the greyed row says why
	if not BattleCycle.allows(engine.current, skill_id):
		return fail_text(BattleCycle.FAIL_OUT_OF_CYCLE, engine.current)  # M4-A2P-025: not this turn's element
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


func swap_out_help(incoming: BattleCombatant, engine: BattleEngine = null, out_id: StringName = &"") -> String:
	var locked := swap_lock_text(engine, out_id) if engine != null else ""
	return locked if locked != "" else tr("HUD_HELP_SWAP_OUT_FMT").format({"name": display_name(incoming)})


## Why `out_id` cannot leave the field this turn (a set piece's lock: "Holding the stair"), or "" (M3-UI-100).
func swap_lock_text(engine: BattleEngine, out_id: StringName) -> String:
	var why := engine.swap_refusal(out_id)
	if why != BattleSetPiece.FAIL_LOCKED and why != BattleEngine.FAIL_ROOTED:
		return ""
	var reason := tr(engine.locked_key) if engine.locked_key != "" else tr("HUD_FAIL_GENERIC")
	if why == BattleEngine.FAIL_ROOTED:  # M4-A2P-020: a root crab's Root Drag holds them
		reason = tr("HUD_SWAP_ROOTED")
	return tr("HUD_HELP_SWAP_LOCKED_FMT").format({"name": display_name(engine.find(out_id)), "reason": reason})


## The help line for a refused action: a localized sentence for every engine fail reason, never
## the raw id. `actor` is who tried; `provoker` names the forced target for &"provoked".
func fail_text(reason: StringName, actor: BattleCombatant, provoker: BattleCombatant = null) -> String:
	var text := tr("HUD_FAIL_GENERIC")
	match reason:
		&"no_mp":
			text = tr("HUD_FAIL_NO_MP")
		&"silenced":
			text = tr("HUD_FAIL_SILENCED_FMT")
		&"no_valid_target":
			text = tr("HUD_FAIL_NO_TARGET")
		&"provoked":
			text = tr("HUD_FAIL_PROVOKED_FMT")
		BattleCycle.FAIL_OUT_OF_CYCLE:
			text = tr("HUD_FAIL_OUT_OF_CYCLE")
		BattleEcho.FAIL_NOTHING:
			text = tr("HUD_FAIL_NOTHING_TO_ECHO")
		&"auto_turn":
			text = tr("HUD_FAIL_AUTO_TURN_FMT")
		&"not_your_turn":
			text = tr("HUD_FAIL_NOT_YOUR_TURN")
		&"battle_over":
			text = tr("HUD_FAIL_BATTLE_OVER")
		&"unknown_skill":
			text = tr("HUD_FAIL_UNKNOWN_SKILL")
		&"no_valid_action":
			text = tr("HUD_FAIL_NO_ACTION_FMT")
		&"no_item":
			text = tr("HUD_FAIL_NO_ITEM")
		&"unknown_item":
			text = tr("HUD_FAIL_UNKNOWN_ITEM")
		&"swell_not_full":
			text = tr("HUD_FAIL_SWELL_NOT_FULL_FMT")
		&"unknown_technique":
			text = tr("HUD_FAIL_UNKNOWN_TECHNIQUE")
		&"swell_cancelled":
			text = tr("HUD_FAIL_SWELL_CANCELLED")
		BossMechanics.FAIL_NO_FIELD:
			text = tr("HUD_FAIL_NO_FIELD")
		BossMechanics.FAIL_FORBIDDEN:
			text = tr(actor.forbidden_key) if actor != null and actor.forbidden_key != "" else text
		BattleVowbound.FAIL_OUT:
			text = tr("HUD_FAIL_VOWBOUND_OUT")
		BattleVowbound.FAIL_UNKNOWN:
			text = tr("HUD_FAIL_UNKNOWN_VOWBOUND")
		BattleVowbound.FAIL_NOT_BOUND:
			text = tr("HUD_FAIL_NOT_BOUND_FMT")
		BattleVowbound.FAIL_NOT_CALLER:
			text = tr("HUD_FAIL_NOT_CALLER_FMT")
		BattleVowbound.FAIL_FALLEN:
			text = tr("HUD_FAIL_VOWBOUND_FALLEN")
		BattleVowbound.FAIL_NONE_OUT:
			text = tr("HUD_FAIL_NO_VOWBOUND")
	return text.format({"name": display_name(actor), "provoker": display_name(provoker)})


## The victory banner's title key: the encounter's "victory_key" (M3-C06-02: "The Inquisitor
## yields."), else HUD_VICTORY.
static func victory_title_key(e: BattleEngine) -> String:
	var enc: Dictionary = e.db.encounters.get(e.encounter_id, {}) if e != null and e.db != null else {}
	return str(enc.get("victory_key", "HUD_VICTORY"))


## Announces a turn the player does not choose (Berserk/Confuse), before it plays.
func auto_announce(c: BattleCombatant, reason: StringName) -> String:
	if reason == AUTO_CONFUSE:
		return tr("HUD_AUTO_CONFUSE_FMT").format({"name": display_name(c)})
	return tr("HUD_AUTO_BERSERK_FMT").format({"name": display_name(c)})


## What an automatic turn did: "Berserk: Rhen lashes out with Attack at Reef Crab."
func auto_result(engine: BattleEngine, c: BattleCombatant, result: ActionResult, reason: StringName) -> String:
	var who := display_name(c)
	var confused := reason == AUTO_CONFUSE
	if result == null or not result.ok or result.hits.is_empty():
		if confused:
			return tr("HUD_AUTO_CONFUSE_IDLE_FMT").format({"name": who})
		return tr("HUD_AUTO_BERSERK_IDLE_FMT").format({"name": who})
	var target := display_name(engine.find(StringName(str(result.hits[0].get("target_id", "")))))
	var args := {"name": who, "skill": skill_name(engine, result.skill_id), "target": target}
	if confused:
		return tr("HUD_AUTO_CONFUSE_ACTS_FMT").format(args)
	return tr("HUD_AUTO_BERSERK_ACTS_FMT").format(args)


## Slot 0's caption on the timeline: "Acting now", or why the fighter acts on its own.
func turn_caption(reason: StringName) -> String:
	match reason:
		AUTO_BERSERK:
			return tr("HUD_TL_BERSERK")
		AUTO_CONFUSE:
			return tr("HUD_TL_CONFUSE")
	return tr("HUD_TL_NOW")


## Extra help-line notes for a candidate action: the Provoke lock, a Reflect bounce, and a heal
## that a Zombie turns to harm. `lands_on` is where the action really lands (after Reflect).
func target_notes(
	engine: BattleEngine, skill_id: StringName, chosen: BattleCombatant, lands_on: BattleCombatant
) -> PackedStringArray:
	var out: PackedStringArray = []
	var forced := engine.forced_target(engine.current, skill_id)
	if chosen != null and lands_on != null and lands_on != chosen:
		out.append(tr("HUD_HELP_REFLECT_FMT").format({"name": display_name(lands_on)}))
	if forced != null:
		out.append(tr("HUD_HELP_PROVOKED_FMT").format({"name": display_name(forced)}))
	var kind := str(engine.db.skill(skill_id).get("kind", ""))
	if kind == "heal" and lands_on != null and lands_on.has_status(&"zombie"):
		out.append(tr("HUD_HELP_ZOMBIE_FMT").format({"name": display_name(lands_on)}))
	return out


## The help line for skill `skill_id` aimed at `chosen` and landing on `lands_on`: what changes the outcome
## (Provoke, Reflect, Zombie) reads before the generic description (a Swell technique's, or the skill's).
func skill_preview_help(
	engine: BattleEngine,
	swell: BattleSwell,
	skill_id: StringName,
	chosen: BattleCombatant,
	lands_on: BattleCombatant,
	next_in: int
) -> String:
	var parts := target_notes(engine, skill_id, chosen, lands_on)
	if swell.is_technique(engine.current, skill_id):
		parts.append(swell_help(engine, swell, skill_id, next_in))
	else:
		parts.append(skill_help(engine, skill_id, next_in))
	return " · ".join(parts)


## The group pick's name: all foes, all allies, or all other allies for a skill that skips its
## user (`target` is the skill row's "target"; "" for items).
func group_label(hostile: bool, target: String = "") -> String:
	if hostile:
		return tr("HUD_GROUP_ALL_FOES")
	return tr("HUD_GROUP_ALL_OTHER_ALLIES") if target == "all_other_allies" else tr("HUD_GROUP_ALL_ALLIES")


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
		"all_other_allies":
			return tr("HUD_TARGET_ALL_OTHER_ALLIES")
		"self":
			return tr("HUD_TARGET_SELF")
	return tr("HUD_TARGET_SINGLE_FOE")


## The lowest HP fraction in `pool` (first wins ties). `pool` is not empty.
static func _most_hurt(pool: Array[BattleCombatant]) -> BattleCombatant:
	var best := pool[0]
	for c in pool:
		if c.hp * best.max_hp < best.hp * c.max_hp:
			best = c
	return best


func _any_usable(engine: BattleEngine, items: BattleItemSource) -> bool:
	for iid in items.usable():
		if not item_candidates(engine, items.action_for(iid)).is_empty():
			return true
	return false


static func _heals_hp(action: ItemBattleAction) -> bool:
	for eff in action.effects:
		if StringName(str(eff.get("type", ""))) == ItemBattleAction.EFFECT_HEAL_HP:
			return true
	return false


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
