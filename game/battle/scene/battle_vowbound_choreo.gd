class_name BattleVowboundChoreo
extends RefCounted
## The Vowbound's call, entry, dismissal and fall on the stage (M2-BPR-04; docs/kb/tech/battle_presentation.md
## "Specials"). Presentation only: BattleChoreo.attached builds it, and it never writes combat state.
## - The engine's call and departure already happened when the stage re-seats (BattleVowboundHud -> BattleStage
##   .sync_party). The stage hands each stand-in it takes off to BattleChoreo.leave() and each one it places to
##   BattleChoreo.enter(); those ask leave_spec() / enter_spec() here what to play, from choreo.json "vowbound".
## - **The call:** the caller makes its call (an accent, "cast"), then the party steps off in slot order; the
##   Vowbound rises at its slot after them (a longer entrance than a swap's walk-in).
## - **The dismissal** (or a battle won while it is out): the Vowbound sinks back; the party walks back in.
## - **The fall:** struck down, it takes the blow, then tips back and is drawn under, slower: not the collapse.
## A swap, and every fighter at instant pacing, gets {} and goes as before.

var choreo: BattleChoreo
var engine: BattleEngine
## choreo.json "vowbound".
var cfg: Dictionary = {}
## Vowbound id -> its combatant, from the call (the departure asks whether it fell).
var _summoned: Dictionary = {}


func _init(sequencer: BattleChoreo, battle: BattleEngine) -> void:
	choreo = sequencer
	engine = battle
	cfg = sequencer.data.get("vowbound", {}) as Dictionary
	engine.vowbound.called.connect(_on_called)


func _on_called(vowbound: BattleCombatant) -> void:
	_summoned[vowbound.id] = vowbound


## What fighter `cid` plays as the stage takes it off ({} = it goes at once).
func leave_spec(cid: StringName) -> Dictionary:
	var vb := engine.vowbound
	if vb.rows.has(cid) and not vb.is_out():
		return _departure(cid)
	if not vb.is_out() or vb.summon == null:
		return {}  # a swap
	var c := engine.find(cid)
	var i := vb.stood_down.find(c)
	if c == null or i < 0 or c.hp <= 0:
		return {}  # a fallen member leaves with the rest of the party, unseen
	var spec := (cfg.get("step_off", {}) as Dictionary).duplicate()
	spec["delay_sec"] = float(spec.get("delay_sec", 0.0)) + float(spec.get("stagger_sec", 0.0)) * i
	if cid == StringName(str((vb.rows.get(vb.summon.id, {}) as Dictionary).get("caller", ""))):
		spec["accent"] = cfg.get("call", {})  # the caller makes its call before it steps off
	return spec


## What fighter `cid` plays as the stage places it ({} = the swap walk-in, choreo.json enter).
func enter_spec(cid: StringName) -> Dictionary:
	var vb := engine.vowbound
	if vb.is_out() and vb.summon != null and vb.summon.id == cid:
		return cfg.get("entry", {}) as Dictionary
	for vid: StringName in vb.rows:
		var gone := choreo.leaving(vid)
		if gone.is_empty():
			continue
		var back := cfg.get("return", {}) as Dictionary
		var spec := (choreo.data.get("enter", {}) as Dictionary).duplicate()
		var i := maxi(BattleIds.of(engine.party_active).find(cid), 0)
		var exit_sec := float((gone["spec"] as Dictionary).get("sec", 0.0))
		spec["delay_sec"] = (
			-float(gone["t"]) + exit_sec * float(back.get("share", 1.0)) + float(back.get("stagger_sec", 0.0)) * i
		)
		return spec
	return {}


## The Vowbound leaves: a dismissal (or a battle won) sinks it back once the action playing is done with it; a
## fall waits for the blow's collapse beat.
func _departure(cid: StringName) -> Dictionary:
	var s: BattleCombatant = _summoned.get(cid, null)
	var fell := s != null and not s.is_alive()
	var spec := (cfg.get("fall" if fell else "dismiss", {}) as Dictionary).duplicate()
	var plan := choreo.current()
	if plan.is_empty():
		return spec
	var wait := 0.0
	if fell and (plan["kos"] as Array).has(cid):
		wait = float(plan["ko_at"]) - choreo.plan_time()
	elif StringName(str(plan["actor"])) == cid or (plan["targets"] as Array).has(cid):
		wait = float(plan["total"]) - choreo.plan_time()
	spec["delay_sec"] = maxf(float(spec.get("delay_sec", 0.0)), wait)
	return spec
