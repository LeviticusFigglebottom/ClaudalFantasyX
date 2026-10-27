class_name BattleImpact
extends Node
## Battle feel on the contact beat (M3-BPR-401; docs/kb/tech/battle_presentation.md "Impact"). The human's note:
## battles looked primitive. Each blow's weight comes from its damage against the target's max HP (`strength`,
## 0..1, a crit adds crit_bonus), all numbers in choreo.json `impact`:
## - **Hit-stop:** a heavy contact holds the choreography clock and the actor's and targets' clips for
##   hit_stop_frames (lerped by strength) at stop_fps.
## - **Shake:** the camera shake (BattleStage.shake) scaled by strength, from shake_min_strength up.
## - **Flash:** a short warm light pulse at the struck target (an OmniLight3D, energy capped, no fog banding);
##   never a screen flash.
## - **Recoil:** each damage reaction's recoil and tilt are scaled by recoil_scale (BattleChoreoPlan sets its weight);
##   a model with its own hit clip still gets clip_recoil_k of the root push.
## - **KO slow-mo:** the blow that fells the last foe slows the choreography clock to ko_slowmo.factor for its sec,
##   starting lead_sec before the collapse.
## Reduced motion: no shake, the flash at reduced_motion.flash_scale, a gentler slow-mo. The controller's hand-off
## waits for the stretched time (BattleChoreo.remaining_sec adds extra_sec). Presentation only, listen-only.

## A blow with weight landed (M3-BPR-401 audio hook): the hardest-hit target, the blow's strength (0..1) and the
## hit-stop it holds for (real seconds, 0 for none). Audio layers an impact by weight on it (BattleImpact events).
signal landed(target_id: StringName, strength: float, stop_sec: float)
## The sequence that fells the last foe slows down: from `from_sec` (plan time) for `sec` at `factor` (audio hook).
signal slowmo_planned(from_sec: float, sec: float, factor: float)

const KEY := "impact"

var cfg: Dictionary = {}
## Hit-stops and flashes started (tests).
var stops := 0
var flashes := 0

var _choreo: BattleChoreo
var _ctl: BattleController
var _engine: BattleEngine
var _stop_left := 0.0
var _held: Dictionary = {}  # AnimationPlayer -> true (its speed to restore is in meta BattleClips.HELD_META)
var _slow := Vector3(INF, -INF, 1.0)  # plan-time window [x, y) at factor z
var _light: OmniLight3D
var _flash_t := -1.0
var _flash_at := 0.0  # the plan time of the flash's contact (a held clock follows it: freeze-frames)
var _flash_peak := 0.0


static func attached(choreo: BattleChoreo, controller: BattleController, engine: BattleEngine) -> BattleImpact:
	var i := BattleImpact.new()
	i.name = "BattleImpact"
	i.cfg = choreo.data.get(KEY, {}) as Dictionary
	i._choreo = choreo
	i._ctl = controller
	i._engine = engine
	choreo.add_child(i)
	choreo.contact.connect(i._on_contact)
	return i


## A hit's weight, 0..1: its damage over the target's max HP, full at full_frac; a crit adds crit_bonus. 0 for a
## miss, a heal or no damage.
static func strength(data: Dictionary, engine: BattleEngine, hit: Dictionary) -> float:
	var c := data.get(KEY, {}) as Dictionary
	var amount := int(hit.get("amount", 0))
	if amount <= 0 or not bool(hit.get("hit", true)):
		return 0.0
	var t := engine.find(StringName(str(hit.get("target_id", "")))) if engine != null else null
	var max_hp := float(t.max_hp) if t != null else float(amount)
	var s := clampf(float(amount) / maxf(max_hp, 1.0) / maxf(float(c.get("full_frac", 1.0)), 0.001), 0.0, 1.0)
	if bool(hit.get("crit", false)):
		s = minf(1.0, s + float(c.get("crit_bonus", 0.0)))
	return s


## `pair` ([lo, hi]) at `s` (0..1).
static func lerp_pair(pair: Variant, s: float) -> float:
	var p := pair as Array if pair is Array else []
	if p.size() < 2:
		return 1.0
	return lerpf(float(p[0]), float(p[1]), clampf(s, 0.0, 1.0))


## A damage reaction's recoil weight for a blow of strength `s` (recoil_scale).
static func recoil_weight(data: Dictionary, s: float) -> float:
	return lerp_pair((data.get(KEY, {}) as Dictionary).get("recoil_scale", [1.0, 1.0]), s)


## Seconds (plan time) a contact of strength `s` holds for: 0 below heavy_strength.
static func hit_stop_sec(data: Dictionary, s: float) -> float:
	var c := data.get(KEY, {}) as Dictionary
	if s <= 0.0 or s < float(c.get("heavy_strength", 1.0)):
		return 0.0
	return roundf(lerp_pair(c.get("hit_stop_frames", [0, 0]), s)) / maxf(float(c.get("stop_fps", 60.0)), 1.0)


## The new sequence (BattleChoreo._start): its slow-mo window when it fells the last foe.
func on_plan(plan: Dictionary) -> void:
	_release()
	_stop_left = 0.0
	_slow = Vector3(INF, -INF, 1.0)
	var kos: Array = plan.get("kos", [])
	if kos.is_empty() or _engine == null or _engine.enemies.any(func(e: BattleCombatant) -> bool: return e.is_alive()):
		return  # only the blow that fells the last foe (the engine calls the victory after this action)
	var sm := cfg.get("ko_slowmo", {}) as Dictionary
	var factor := float(sm.get("factor", 1.0))
	if _choreo.reduced_motion:
		factor = float((cfg.get("reduced_motion", {}) as Dictionary).get("slowmo_factor", factor))
	var from := maxf(float(plan.get("ko_at", 0.0)) - float(sm.get("lead_sec", 0.0)), 0.0)
	_slow = Vector3(from, from + float(sm.get("sec", 0.0)), clampf(factor, 0.05, 1.0))
	slowmo_planned.emit(_slow.x, _slow.y - _slow.x, _slow.z)


## Real seconds `delta` as plan-clock seconds (before the battle speed): a hit-stop eats them, a slow-mo stretches.
func warp(delta: float, t: float) -> float:
	if _stop_left > 0.0:
		var use := minf(delta, _stop_left)
		_stop_left -= use
		delta -= use
		if _stop_left <= 0.0:
			_release()
	if delta <= 0.0:
		return 0.0
	return delta * _slow.z if t >= _slow.x and t < _slow.y else delta


## Real seconds the hit-stop and slow-mo still add to `plan` from plan time `t` (BattleChoreo.remaining_sec).
func extra_sec(plan: Dictionary, t: float) -> float:
	var speed := maxf(_choreo.speed, 0.01)
	var extra := _stop_left
	if t < float(plan.get("contact", 0.0)):
		extra += hit_stop_sec(_choreo.data, float(plan.get("impact", 0.0))) / speed
	var span := maxf(_slow.y - maxf(t, _slow.x), 0.0)
	if span > 0.0 and is_finite(span):
		extra += span * (1.0 / _slow.z - 1.0) / speed
	return extra


## The sequence ended: every held clip plays on.
func finish() -> void:
	_stop_left = 0.0
	_release()


func _on_contact(result: ActionResult) -> void:
	var plan := _choreo.current()
	if plan.is_empty():
		return  # instant pacing: no feel to add
	var peak := float(plan.get("impact", 0.0))
	var rm := cfg.get("reduced_motion", {}) as Dictionary
	var stop := hit_stop_sec(_choreo.data, peak)
	if stop > 0.0:
		stops += 1
		_stop_left = stop / maxf(_choreo.speed, 0.01)
		_hold([StringName(str(plan["actor"]))] + (plan["targets"] as Array))
	if peak >= float(cfg.get("shake_min_strength", 1.0)):
		var k := float(rm.get("shake_scale", 0.0)) if _choreo.reduced_motion else 1.0
		if k > 0.0:
			_ctl.stage.shake(_choreo.speed, lerp_pair(cfg.get("shake_scale", [1.0, 1.0]), peak) * k)
	if peak > 0.0:
		var struck := _struck(result)
		_flash(struck, peak, float(rm.get("flash_scale", 1.0)) if _choreo.reduced_motion else 1.0)
		landed.emit(struck, peak, _stop_left)


func _hold(ids: Array) -> void:
	for cid: Variant in ids:
		var p := BattleClips.player_of(_ctl.stage.stand_in(StringName(str(cid))))
		if p != null and not _held.has(p):
			_held[p] = true
			p.set_meta(BattleClips.HELD_META, p.speed_scale)  # a clip started during the hold keeps it (BattleClips)
			p.speed_scale = 0.0


func _release() -> void:
	for p: Variant in _held:
		if is_instance_valid(p):
			var ap := p as AnimationPlayer
			ap.speed_scale = float(ap.get_meta(BattleClips.HELD_META, 1.0))
			ap.remove_meta(BattleClips.HELD_META)
	_held.clear()


## The hardest-hit target of the action ("" when none was damaged).
func _struck(result: ActionResult) -> StringName:
	var best := &""
	var most := 0.0
	for hit: Dictionary in result.hits:
		var s := strength(_choreo.data, _engine, hit)
		if s > most:
			most = s
			best = StringName(str(hit.get("target_id", "")))
	return best


func _flash(tid: StringName, s: float, k: float) -> void:
	var f := _ctl.stage.stand_in(tid)
	var fc := cfg.get("flash", {}) as Dictionary
	if f == null or fc.is_empty() or s <= 0.0:
		return
	if _light == null:
		_light = OmniLight3D.new()
		_light.name = "ImpactFlash"
		_light.shadow_enabled = false
		_light.light_volumetric_fog_energy = 0.0  # fog rule: no banding in dense fog volumes
		_ctl.stage.add_child(_light)
	_light.light_color = Color.html(str(fc.get("color", "#FFFFFF")))
	_light.omni_range = float(fc.get("range_m", 1.0))
	var height := float(BattleStage.stand_in_spec(tid).get("height", 1.0)) * float(fc.get("height_frac", 0.5))
	_light.global_position = f.global_position + Vector3.UP * height
	_flash_peak = minf(lerp_pair(fc.get("energy", [0.0, 0.0]), s), float(fc.get("energy_cap", 0.0))) * k
	_flash_t = 0.0
	_flash_at = _choreo.time()
	flashes += 1
	_light_at(0.0)


func _process(delta: float) -> void:
	if _flash_t < 0.0 or _light == null:
		return
	_flash_t = _flash_t + delta * _choreo.speed if _choreo.live else maxf(_choreo.time() - _flash_at, 0.0)
	_light_at(_flash_t)


## The pulse: up at once, back to dark over flash.sec (eased out).
func _light_at(t: float) -> void:
	var sec := maxf(float((cfg.get("flash", {}) as Dictionary).get("sec", 0.1)), 0.001)
	var u := clampf(t / sec, 0.0, 1.0)
	_light.light_energy = _flash_peak * (1.0 - u) * (1.0 - u)
	_light.visible = u < 1.0
	if u >= 1.0:
		_flash_t = -1.0


func light() -> OmniLight3D:
	return _light
