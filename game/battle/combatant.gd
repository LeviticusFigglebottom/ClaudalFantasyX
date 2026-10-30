class_name BattleCombatant
extends RefCounted
## Runtime state of one fighter. Pure data + small helpers; no scene dependencies so the
## engine runs headless (§5.2 determinism).

const TEAM_PARTY := &"party"
const TEAM_ENEMY := &"enemy"
## Metadata key where EquipmentEffects.apply_to (game/progression) leaves the engine-facing
## equipment data: {attack_elements, on_hit_statuses, status_wards, low_hp_statuses, abilities}.
## Must equal EquipmentEffects.META_KEY (a test checks it).
const EQUIPMENT_META := &"equipment_effects"
## The petrify (stone) status id (statuses.json). The one copy in code: the timeline, BattleVitals
## and the item action use it, and the engine derives its String PETRIFY_ID from it (M1-ARC-11,
## after review-sweep-G on M1-CMB-08; M1-ARC-12).
const STATUS_PETRIFY := &"petrify"

var id: StringName
var name_key: String
var team: StringName
var level: int = 1
var max_hp: int = 1
var hp: int = 1
var max_mp: int = 0
var mp: int = 0
var strength: int = 0
var magic: int = 0
var defense: int = 0
var magic_defense: int = 0
var agility: int = 0
var accuracy: int = 0
var evasion: int = 0
var luck: int = 0
var skills: Array[StringName] = []
## Element id -> affinity (&"weak", &"resist", &"immune", &"absorb"). Missing = &"normal".
var affinities: Dictionary = {}
## Status id -> remaining duration in this combatant's own turns (-1 = until cured).
var statuses: Dictionary = {}
var ai_rules: Array = []
var xp_reward: int = 0
var break_damage_cap := false

## CTB: absolute tick at which this combatant next acts.
var next_time: int = 0
## Number of turns taken this battle (used for scripted AI and XP credit).
var turns_taken: int = 0
## True once this combatant has been on the field at any point (XP credit rule).
var participated := false
## Who inflicted Provoke on this combatant (its single-foe actions must target them). An id,
## not a reference, so two combatants never hold each other (RefCounted cycle).
var provoker_id: StringName = &""
## Low-HP auto-statuses this combatant's equipment switched on (so healing removes only those,
## never the same status from another source).
var low_hp_owned: Array[StringName] = []
## Delays received since this combatant's last own turn (diminishing returns; formulas.md).
var delays_taken := 0
## M4-A2P-020: own turns left held by the roots (a skill's root_turns): while > 0 a hero on the field can't be swapped
## out (BattleEngine.FAIL_ROOTED). Counts down at the end of each own turn, like a timed status.
var rooted_turns := 0
## Data flag (enemies.json "delay_immune", e.g. bosses): delay effects add no ticks.
var delay_immune := false
## Swell gauge, 0..Formulas.SWELL_MAX (SPEC §6.2). BattleSwell fills and empties it.
var swell := 0
## The fill mode in force (a swell.json mode id). &"" = this combatant has no Swell (enemies,
## and heroes with no swell.json row); the HUD draws no gauge for them.
var swell_mode: StringName = &""

## Boss mechanics (BossMechanics, M2-FP-06; battle_ctb.md "The Drownbell").
## enemies.json "phases": rows applied in order as HP falls ({id, at_hp_pct, ...changes}).
var phases: Array = []
## Index of the phase in force (-1 = the opening one, before any "phases" row).
var phase_index := -1
## turns_taken when the phase in force began: EnemyAI's turn_mod counts from here.
var ai_turn_base := 0
## A telegraphed skill (a skill row's "charge"): fires on this combatant's own turn when
## charge_left reaches 1; charge_left counts the acted turns left, the firing one included.
var charge_skill: StringName = &""
var charge_left := 0
## The charged skill's row (rank, target, delay_ranks), so the timeline can predict it.
var charge_row: Dictionary = {}
## enemies.json "weak_point" ({hits, max_delay, name_key}): landed low-delay physical hits that
## break a charge. weak_hits counts them during the charge in progress.
var weak_point: Dictionary = {}
var weak_hits := 0
## enemies.json "field": the field this combatant is bound to; it falls when the field clears.
var field: StringName = &""
## enemies.json "reactions" (M3-C05-02, the Cinder Matron's quench): [{elements, from_phase?,
## cleanses?, statuses?}]. A landed hit of one of those elements cleanses and adds statuses on it.
var reactions: Array = []
## enemies.json "tags" (M3-C06-02): what a foe is, for an encounter's rules ("stillguard": a person
## of the Order, whom Toma will not strike in Ch6).
var tags: Array[StringName] = []
## enemies.json "yield_at_hp_pct" (M3-C06-02, the Stillguard Inquisitor and his hound): -1 fights to
## a KO. Otherwise a hit (or a fall) that leaves it at or below this share of its max HP ends its
## fight on its feet: it yields or runs, keeps at least 1 HP and leaves the field (is_alive() is
## false from then on, so it counts as down for the timeline, targeting and the outcome). Nobody dies.
var yield_at_hp_pct := -1
## True once it has yielded (see yield_at_hp_pct).
var yielded := false
## encounters.json "forbidden_skills" (M3-C06-02), on a party member: its offensive skills may not
## touch a foe carrying this tag (BossMechanics.forbids), and forbidden_key is the loc key that
## says why ("Toma will not strike the Stillguard."). &"" = no rule.
var forbidden_tag: StringName = &""
var forbidden_key := ""

## Set-piece battles (M3-CMB-01, BattleSetPiece; set_piece_battles.md).
## A scripted timeline entry (encounters.json "entries"): &"ward" (the Climb), &"tide" (the Surge)
## or &"guest" (Pell). &"" for every fighter. An entry has no HP, can't be KO'd and is never a target
## but of a "ward" skill (BattleSetPiece.ROLE_WARD); it acts on its own (data AI).
var entry_role: StringName = &""
## On a ward: who covers it (a "covers" skill, Toma's Hold the Stair): the next foe's ward skill
## lands on them instead. Cleared when it lands or at the coverer's next turn. &"" = uncovered.
var covered_by: StringName = &""
## A counter stance (a "counter" skill, Toma's Stand Firm): until this combatant's next turn, a
## landed physical hit from a foe is answered at once with this skill on the attacker. &"" = none.
var counter_skill: StringName = &""
## On an entry: a summon from its skills adds nothing while this many targetable foes stand
## (encounters.json entries "summon_cap"; the Surge's "max 3 standing"). -1 = no cap.
var summon_cap := -1
## A phase row's "untargetable" (nothing may target it; it still acts) and "damage_immune" (no hit
## takes HP): the Undertow's Reach drawn back over the sea.
var untargetable := false
var damage_immune := false
## M4-A2P-021 (BattleCover): enemies.json "glide" (up out of reach every other turn) and "ambush" (buried until its
## first turn); `covered` is cover's own untargetable, so a phase's untargetable is never lifted by it.
var glides := false
var ambushes := false
var covered := false
## enemies.json "hp_floor_pct": hits never take it below this share of max HP (the Reach can't fall
## before its last phase begins). -1 = none.
var hp_floor_pct := -1
## Left the field on its feet without being felled (Pell's Storm-Call draws it off; an objective
## victory sends the rest back down the wall). Counts as down; gives no XP, lume or drops.
var withdrawn := false
## The skill this combatant's Attack plays (encounters.json "attack_override": Toma's Attack becomes
## Stand Firm at the stair-head). The menus read it; &"attack" otherwise.
var attack_skill: StringName = &"attack"


static func from_dict(cid: StringName, team_id: StringName, d: Dictionary) -> BattleCombatant:
	var c := BattleCombatant.new()
	c.id = cid
	c.team = team_id
	c.name_key = String(d.get("name_key", ""))
	var st: Dictionary = d.get("stats", {})
	c.level = int(st.get("level", 1))
	c.max_hp = int(st.get("hp", 1))
	c.hp = c.max_hp
	c.max_mp = int(st.get("mp", 0))
	c.mp = c.max_mp
	c.strength = int(st.get("strength", 0))
	c.magic = int(st.get("magic", 0))
	c.defense = int(st.get("defense", 0))
	c.magic_defense = int(st.get("magic_defense", 0))
	c.agility = int(st.get("agility", 0))
	c.accuracy = int(st.get("accuracy", 0))
	c.evasion = int(st.get("evasion", 0))
	c.luck = int(st.get("luck", 0))
	for s: Variant in d.get("skills", []):
		c.skills.append(StringName(str(s)))
	for k: Variant in d.get("affinities", {}) as Dictionary:
		c.affinities[StringName(str(k))] = StringName(str(d["affinities"][k]))
	c.ai_rules = (d.get("ai", []) as Array).duplicate(true)
	c.xp_reward = int(d.get("xp", 0))
	c.delay_immune = bool(d.get("delay_immune", false))
	c.glides = bool(d.get("glide", false))
	c.ambushes = bool(d.get("ambush", false))
	c.phases = (d.get("phases", []) as Array).duplicate(true)
	c.weak_point = (d.get("weak_point", {}) as Dictionary).duplicate(true)
	c.field = StringName(str(d.get("field", "")))
	c.reactions = (d.get("reactions", []) as Array).duplicate(true)
	for t: Variant in d.get("tags", []):
		c.tags.append(StringName(str(t)))
	c.yield_at_hp_pct = int(d.get("yield_at_hp_pct", -1))
	c.hp_floor_pct = int(d.get("hp_floor_pct", -1))
	return c


## True for a scripted timeline entry (see entry_role).
func is_entry() -> bool:
	return entry_role != &""


## Leaves the field without falling (see withdrawn). Nothing for an entry.
func withdraw() -> void:
	if is_entry():
		return
	withdrawn = true
	statuses.clear()
	provoker_id = &""


## True while a telegraphed skill is gathering (see charge_skill).
func is_charging() -> bool:
	return charge_left > 0 and charge_skill != &""


## Drops any charge in progress (a break, a phase change, or the charged skill firing).
func clear_charge() -> void:
	charge_skill = &""
	charge_left = 0
	charge_row = {}
	weak_hits = 0


## A detached copy for read-only predictions (BattleEngine.item_downs): the state an item's
## effects read or write (HP, MP, statuses, affinities, equipment wards), never the timeline.
## Mutating it leaves this combatant untouched.
func sim_copy() -> BattleCombatant:
	var c := BattleCombatant.new()
	c.id = id
	c.team = team
	c.max_hp = max_hp
	c.hp = hp
	c.max_mp = max_mp
	c.mp = mp
	c.agility = agility
	c.affinities = affinities.duplicate()
	c.statuses = statuses.duplicate()
	c.delay_immune = delay_immune
	c.set_meta(EQUIPMENT_META, equipment())
	return c


## Still in the fight: HP above 0 and not turned to stone. Petrify counts as KO for the
## timeline, targeting, outcome checks and XP credit (formulas.md § Statuses).
func is_alive() -> bool:
	return hp > 0 and not yielded and not withdrawn and not statuses.has(STATUS_PETRIFY)


func is_petrified() -> bool:
	return hp > 0 and statuses.has(STATUS_PETRIFY)


## Engine-facing equipment data (see EQUIPMENT_META), {} for enemies and bare heroes.
func equipment() -> Dictionary:
	return get_meta(EQUIPMENT_META, {})


## An equipment status ward makes this combatant immune to `status`.
func is_warded(status: StringName) -> bool:
	return (equipment().get("status_wards", []) as Array).has(status)


## Low-HP auto-statuses (formulas.md § Equipment): on while HP × 100 < max_hp × hp_below_pct,
## off once healed to the threshold or above. Called by the engine after every HP change.
func sync_low_hp() -> void:
	if not is_alive():
		low_hp_owned.clear()
		return
	for entry: Variant in equipment().get("low_hp_statuses", []):
		var e: Dictionary = entry
		var sid := StringName(str(e["id"]))
		var below := hp * Formulas.PCT < max_hp * int(e["hp_below_pct"])
		if below and not has_status(sid):
			if add_status(sid, int(e.get("duration", -1))) and not low_hp_owned.has(sid):
				low_hp_owned.append(sid)
		elif not below and low_hp_owned.has(sid):
			statuses.erase(sid)
			low_hp_owned.erase(sid)


func has_status(status: StringName) -> bool:
	return statuses.has(status)


func affinity_for(element: StringName) -> StringName:
	return affinities.get(element, &"normal")


## Speed multiplier from Haste/Slow. Both at once cancel out.
func speed_mult() -> float:
	var m := 1.0
	if has_status(&"haste"):
		m *= Formulas.HASTE_SPEED_MULT
	if has_status(&"slow"):
		m *= Formulas.SLOW_SPEED_MULT
	return m


## Strength after Weakened, then Berserk (Berserk multiplies the broken value).
func effective_strength() -> int:
	var s := Formulas.broken_stat(strength, has_status(&"power_break"))
	return Formulas.berserk_strength(s) if has_status(&"berserk") else s


func effective_magic() -> int:
	return Formulas.broken_stat(magic, has_status(&"magic_break"))


func effective_defense() -> int:
	return 0 if has_status(&"armor_break") else defense


func effective_magic_defense() -> int:
	return 0 if has_status(&"mental_break") else magic_defense


## Applies signed HP change (positive = damage). Returns the actual HP delta (negative = lost).
func apply_damage(amount: int) -> int:
	if yielded or withdrawn or is_entry() or damage_immune and amount > 0:
		return 0  # it has left the fight, has no HP, or nothing can wound it now
	var before := hp
	hp = clampi(hp - amount, mini(_hp_floor(), hp), max_hp)
	if amount > 0 and has_status(&"sleep"):
		statuses.erase(&"sleep")
	if amount > 0 and before > 0 and _yields_at(hp):
		_yield()
	elif hp == 0:
		statuses.clear()
		provoker_id = &""
	return hp - before


## Restores `amount` HP from a heal skill or Regen. Under Zombie the same amount is dealt as
## damage instead. Returns the actual HP delta (negative = lost), like apply_damage.
func restore_hp(amount: int) -> int:
	return apply_damage(amount if has_status(&"zombie") else -amount)


## KO now (Doom reaching zero): HP 0 and every status cleared.
func fall() -> void:
	if is_entry():
		return  # no HP: an entry can't be KO'd
	if yield_at_hp_pct >= 0 and hp > 0:
		_yield()  # a yielding foe never goes down: Doom or a field's fall ends its fight on its feet
		return
	hp = 0
	statuses.clear()
	provoker_id = &""


## The least HP a hit can leave (hp_floor_pct of max HP, floored), 0 without a floor.
func _hp_floor() -> int:
	return maxi(max_hp * hp_floor_pct / Formulas.PCT, 0) if hp_floor_pct >= 0 else 0


## True when a hit leaving it on `left` HP ends its fight (see yield_at_hp_pct).
func _yields_at(left: int) -> bool:
	return yield_at_hp_pct >= 0 and not yielded and left * Formulas.PCT <= max_hp * yield_at_hp_pct


## Leaves the fight on its feet (see yield_at_hp_pct): at least 1 HP, every status gone.
func _yield() -> void:
	hp = maxi(hp, 1)
	yielded = true
	statuses.clear()
	provoker_id = &""


## Returns false (and does nothing) if the target is KO'd, petrified, or warded against it.
## Petrify replaces every other status: stone has no poison, haste or countdown.
func add_status(status: StringName, duration: int) -> bool:
	if not is_alive() or is_warded(status):
		return false
	if status == STATUS_PETRIFY:
		statuses.clear()
		provoker_id = &""
	statuses[status] = duration
	if status == &"haste":
		statuses.erase(&"slow")
	elif status == &"slow":
		statuses.erase(&"haste")
	return true


## Turns left on Doom (0 = not doomed). The combatant falls at the end of a turn shown as 1.
func doom_count() -> int:
	return maxi(int(statuses.get(&"doom", 0)), 0)


## Called at the end of each own turn (acted or lost): counts timed statuses down. Doom
## reaching zero KOs the combatant; returns true when that happened.
func tick_statuses() -> bool:
	var doomed := doom_count() == 1
	for s: StringName in statuses.keys():
		var left: int = statuses[s]
		if left < 0:
			continue
		left -= 1
		if left <= 0:
			statuses.erase(s)
		else:
			statuses[s] = left
	rooted_turns = maxi(rooted_turns - 1, 0)
	if not has_status(&"provoke"):
		provoker_id = &""
	if doomed and hp > 0:
		fall()
		return true
	return false
