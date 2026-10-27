extends Node
## M2-HER-1103 test stage: Rhen, Asha and Toma on the battle stage as their real hero actors (FighterStandIn's
## "scene", M2-UI-07), each shot frozen on one contract clip (docs/kb/tech/battle_presentation.md "Clip
## contract"). The choreography plays the action as in a fight (BattleChoreo, frozen at a beat); the hero's
## AnimationPlayer is then set to the same plan time and paused, so a freeze-frame shows the clip at that beat
## (a frozen plan does not move the players, which run in real time). Test-only (shots battle_heroes_*).

const BATTLE := "res://game/battle/scene/battle_sandbox.tscn"
const ACTIVE: Array[StringName] = [&"rhen", &"asha", &"toma"]
const RESERVE: Array[StringName] = [&"ysolde"]
const POSE_IDLE := &"idle"
const POSE_ATTACK := &"attack"
const POSE_HIT := &"hit"
const POSE_KO := &"ko"
const POSE_VICTORY := &"victory"
const POSE_CAST := &"cast"
const POSE_FINISHER := &"finisher"

## Which beat the shot freezes (one of the POSE_* ids).
@export var pose: StringName = POSE_IDLE
@export var encounter: StringName = &"ch02_tideline"
@export var rng_seed := 20261022
## Seconds into the idle loop every hero is frozen at, so the lineup does not depend on the frame count.
@export var idle_sec := 1.5
## Seconds after its reaction starts that a struck hero is frozen at (the hit's recoil).
@export var hit_after_sec := 0.14
@export var cast_before_contact_sec := 0.05
## Seconds into the KO clip it is held at (its last frame).
@export var ko_hold_sec := 1.2
@export var victory_sec := 1.0

var ctl: BattleController


func _ready() -> void:
	ctl = (load(BATTLE) as PackedScene).instantiate() as BattleController
	ctl.auto_start = false
	ctl.pacing_scale = 0.0
	ctl.show_damage_numbers = false
	ctl.persist_progress = false
	add_child(ctl)
	ctl.start_battle(ACTIVE, RESERVE, encounter, rng_seed, BattleStage.lattice_for(ACTIVE + RESERVE))
	var motion := HeroBattleActor.load_data()
	for cid in ACTIVE:  # each hero's own idle phase (HeroBattleActor), idle_sec on
		freeze(cid, BattleClips.IDLE, idle_sec + HeroBattleActor.idle_phase(motion, cid))
	match pose:
		POSE_ATTACK:
			_strike(&"rhen", &"attack", _foe(), &"contact", 0.0)
		POSE_FINISHER:
			_strike(&"rhen", &"lamp_dive", _foe(), &"contact", 0.0)
		POSE_CAST:
			_strike(&"asha", &"mend", &"rhen", &"contact", -cast_before_contact_sec)
		POSE_HIT:
			_struck(&"asha", false)
		POSE_KO:
			_struck(&"toma", true)
		POSE_VICTORY:
			for cid in ACTIVE:
				BattleClips.play(ctl.stage.stand_in(cid), BattleClips.VICTORY)
				freeze(cid, BattleClips.VICTORY, victory_sec)


## Sets `cid`'s model to `clip` at `at` seconds (no blend) and holds it there.
func freeze(cid: StringName, clip: StringName, at: float) -> void:
	var p := BattleClips.player_of(ctl.stage.stand_in(cid))
	if p == null or not p.has_animation(clip):
		push_warning("battle_heroes_stage: %s has no clip %s" % [cid, clip])
		return
	p.play(clip, 0.0)
	var length := p.get_animation(clip).length
	var t := fposmod(at, length) if p.get_animation(clip).loop_mode != Animation.LOOP_NONE else clampf(at, 0.0, length)
	p.seek(t, true)
	p.pause()


func _choreo() -> BattleChoreo:
	var c := ctl.stage.choreo
	c.force_play = true
	c.live = false
	c.frozen = true
	c.speed = 1.0
	c.reduced_motion = false
	c.skip = false
	return c


## `actor` uses `skill` on `target`, frozen at the plan's `beat` + `offset`; the actor's strike clip is set to the
## same moment (it started on the strike beat, approach_end).
func _strike(actor: StringName, skill: StringName, target: StringName, beat: StringName, offset: float) -> void:
	var c := _choreo()
	ctl.engine.action_resolved.emit(_result(actor, skill, [_hit(target, 1)]))
	var plan := c.current()
	var t := float(plan[String(beat)]) + offset
	c.seek(t)
	var clip := StringName(str(c.style(str(plan["style"])).get("clip", "")))
	freeze(actor, clip, t - float(plan["approach_end"]))


## A foe strikes `cid`: its hit clip just after its reaction starts, or, `felled`, its KO clip held at the end.
func _struck(cid: StringName, felled: bool) -> void:
	var c := _choreo()
	if felled:
		ctl.engine.find(cid).hp = 0
	ctl.engine.action_resolved.emit(_result(_foe(), &"attack", [_hit(cid, 10)]))
	var plan := c.current()
	if felled:
		c.seek(float(plan["total"]))
		freeze(cid, BattleClips.KO, ko_hold_sec)
		return
	var at := float(plan["contact"])
	for r: Dictionary in plan["reactions"]:
		if StringName(str(r["target"])) == cid:
			at = float(r["at"])
	c.seek(at + hit_after_sec)
	freeze(cid, BattleClips.HIT, hit_after_sec)


func _foe() -> StringName:
	for e in ctl.engine.enemies:
		if e.is_alive():
			return e.id
	return &""


func _hit(tid: StringName, amount: int) -> Dictionary:
	return {"target_id": tid, "hit": true, "crit": false, "amount": amount, "statuses_added": []}


func _result(actor: StringName, skill: StringName, hits: Array[Dictionary]) -> ActionResult:
	var r := ActionResult.new()
	r.actor_id = actor
	r.skill_id = skill
	r.hits = hits
	return r
