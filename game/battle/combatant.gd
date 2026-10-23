class_name BattleCombatant
extends RefCounted
## Runtime state of one fighter. Pure data + small helpers; no scene dependencies so the
## engine runs headless (§5.2 determinism).

const TEAM_PARTY := &"party"
const TEAM_ENEMY := &"enemy"

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
	return c


## Still in the fight: HP above 0 and not turned to stone. Petrify counts as KO for the
## timeline, targeting, outcome checks and XP credit (formulas.md § Statuses).
func is_alive() -> bool:
	return hp > 0 and not statuses.has(&"petrify")


func is_petrified() -> bool:
	return hp > 0 and statuses.has(&"petrify")


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


## Strength after Power Break, then Berserk (Berserk multiplies the broken value).
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
	var before := hp
	hp = clampi(hp - amount, 0, max_hp)
	if amount > 0 and has_status(&"sleep"):
		statuses.erase(&"sleep")
	if hp == 0:
		statuses.clear()
		provoker_id = &""
	return hp - before


## Restores `amount` HP from a heal skill or Regen. Under Zombie the same amount is dealt as
## damage instead. Returns the actual HP delta (negative = lost), like apply_damage.
func restore_hp(amount: int) -> int:
	return apply_damage(amount if has_status(&"zombie") else -amount)


## KO now (Doom reaching zero): HP 0 and every status cleared.
func fall() -> void:
	hp = 0
	statuses.clear()
	provoker_id = &""


## Returns false (and does nothing) if the target is KO'd or petrified. Petrify replaces
## every other status: stone has no poison, haste or countdown.
func add_status(status: StringName, duration: int) -> bool:
	if not is_alive():
		return false
	if status == &"petrify":
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
	if not has_status(&"provoke"):
		provoker_id = &""
	if doomed and hp > 0:
		fall()
		return true
	return false
