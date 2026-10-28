class_name BattleOutro
extends Node
## The battle's last beat (M2-BPR-05; docs/kb/tech/battle_presentation.md "Victory and escape"). Listen-only:
## on engine.battle_finished it waits for the final action's choreography, then the standing party plays its
## victory (the `victory` clip, else a stand-in's small hops, staggered) or, after an escape, walks back off the
## field. BattleController holds the result panel BattleStage.outro_hold() for it (in place, no new line).
## Instant when the choreography is (pacing 0, skip animations); captures never see it.

const VICTORY := &"victory"
const ESCAPE := &"escape"

## The outro playing (&"" when none), and its clock in seconds at battle speed.
var playing: StringName = &""
var elapsed := 0.0
## False holds the clock (captures, tests); advance() still moves it.
var live := true

var _choreo: BattleChoreo
var _engine: BattleEngine
var _ids: Array[StringName] = []
## Fighters whose victory clip has started (each on its own stagger, like the hops).
var _clip_started: Dictionary = {}
## The outro waiting for the last action's choreography to finish.
var _pending: StringName = &""


static func attached(choreo: BattleChoreo, engine: BattleEngine) -> BattleOutro:
	var o := BattleOutro.new()
	o.name = "BattleOutro"
	choreo.add_child(o)
	o._choreo = choreo
	o._engine = engine
	engine.battle_finished.connect(o._on_battle_finished)
	return o


func cfg(kind: StringName) -> Dictionary:
	return (_choreo.data.get("outro", {}) as Dictionary).get(String(kind), {}) as Dictionary


func _on_battle_finished(outcome: StringName) -> void:
	var kind := &""
	if outcome == BattleEngine.OUTCOME_VICTORY:
		kind = VICTORY
	elif outcome in [BattleEngine.OUTCOME_ESCAPED, BattleEngine.OUTCOME_SCRIPTED_ESCAPE]:
		kind = ESCAPE  # M3-BPR-415: the Reach survived, the last of them up: the party goes (ADR 0100)
	if kind == &"" or not _choreo.animating():
		return
	_pending = kind
	_choreo.after_sequence(_begin.bind(kind))


func _begin(kind: StringName) -> void:
	_pending = &""
	playing = kind
	elapsed = 0.0
	_ids.clear()
	_clip_started.clear()
	for c in _engine.party_active:
		if c.is_alive() and _choreo.stand_in(c.id) != null:
			_ids.append(c.id)
	_apply()


## Total seconds of the outro `kind` at battle speed 1 (the last fighter's stagger included).
func duration(kind: StringName) -> float:
	var c := cfg(kind)
	return (
		float(c.get("delay_sec", 0.0))
		+ maxf(float(c.get("sec", 0.0)), clip_sec(kind))
		+ float(c.get("stagger_sec", 0.0)) * maxi(_ids.size() - 1, 0)
	)


## The longest one-shot clip of `kind` (its cfg clip) among the standing party's models, capped at clip_max_sec: the
## result panel waits for a real hero's victory pose to finish (M3-BPR-415). 0 for stand-ins and looping clips.
func clip_sec(kind: StringName) -> float:
	var c := cfg(kind)
	var clip := StringName(str(c.get("clip", "")))
	var longest := 0.0
	for p in _engine.party_active:
		var player := BattleClips.player_of(_choreo.stand_in(p.id)) if p.is_alive() else null
		if player != null and player.has_animation(clip):
			var a := player.get_animation(clip)
			if a.loop_mode == Animation.LOOP_NONE:
				longest = maxf(longest, a.length)
	return minf(longest, float(c.get("clip_max_sec", longest)))


## Real seconds left (0 when none plays).
func remaining_sec() -> float:
	if playing == &"":
		return 0.0
	return maxf(duration(playing) - elapsed, 0.0) / _choreo.speed


## How long the result panel waits: `base`, or the outro's rest plus its settle.
func hold(base: float) -> float:
	if playing == &"" and _pending == &"":
		return base
	var rest := remaining_sec() + _choreo.remaining_sec()
	if _pending != &"":
		rest += duration(_pending) / _choreo.speed
	return maxf(
		base, rest + float((_choreo.data.get("outro", {}) as Dictionary).get("settle_sec", 0.0)) / _choreo.speed
	)


func _process(delta: float) -> void:
	if live:
		advance(delta)


func advance(delta: float) -> void:
	if playing == &"":
		return
	elapsed += delta * _choreo.speed
	_apply()
	if elapsed >= duration(playing):
		_end()


func _end() -> void:
	if playing == VICTORY:
		for cid in _ids:
			_choreo.rest(cid)
	playing = &""


## Victory: each fighter (staggered) hops `hops` times, `hop_m` high, unless its model plays the clip. Escape:
## everyone walks `back_m` back off the field and stays there under the result panel.
func _apply() -> void:
	var c := cfg(playing)
	var t0 := elapsed - float(c.get("delay_sec", 0.0))
	var sec := maxf(float(c.get("sec", 0.0)), 0.0001)
	for i in _ids.size():
		var cid := _ids[i]
		var f := _choreo.stand_in(cid)
		if f == null:
			continue
		var u := clampf((t0 - float(c.get("stagger_sec", 0.0)) * i) / sec, 0.0, 1.0)
		var fwd := _choreo.facing(cid)
		if playing == VICTORY:
			var clip := StringName(str(c.get("clip", "")))
			if BattleClips.has_clip(f, clip):
				if t0 >= float(c.get("stagger_sec", 0.0)) * i and not _clip_started.has(cid):
					_clip_started[cid] = true
					BattleClips.play(f, clip, _choreo.speed)
				continue
			var hop := absf(sin(PI * u * float(c.get("hops", 1)))) * float(c.get("hop_m", 0.0))
			_choreo.pose(cid, Vector3.UP * hop, fwd, 0.0)
		else:
			var back := float(c.get("back_m", 0.0)) * (_choreo.rm("travel_scale") if _choreo.reduced_motion else 1.0)
			_choreo.pose(cid, -fwd * back * BattleChoreo.ease01(u), -fwd, 0.0)
