class_name BattleSummonCinematic
extends Node
## C10: a Vowbound's first call as an in-battle cinematic (M2-BPR-08; docs/kb/tech/battle_presentation.md
## "Ilun's first call"). The slice's one Vowbound and its first call must be unmissable (vertical_slice.md B10).
## - **When** (UiSettings summon_cinematic, the UI track's row, M2-UI-23): "short" (the default) plays it on the
##   first call of each Vowbound in a live story battle (its first_call_flags flag unset) and the short entry
##   (choreo.json vowbound.entry) after; "full" plays it on every call; "off" skips the rise (the Vowbound is
##   simply there). A capture fixture, instant pacing and "skip animations" play the short entry.
## - **What.** The water stills (a longer delay after the party steps off), the Vowbound rises slowly at its slot
##   in bound light (an OmniLight3D in glimmer_bound, fading in and holding steady: no flicker, no drift, no
##   trails; color script C10), the camera eases to a low frame on the slot and back to the default by the end.
##   Under reduced motion the camera stays on the default. Nothing flashes.
## - **Skip.** Confirm or cancel ends it at once (the Vowbound stands on its mark).
## Presentation only: BattleVowboundChoreo asks it for the entrance; it writes nothing but its seen-flag.

const KEY := "summon_cinematic"
const SETTING := &"summon_cinematic"
const SETTING_FULL := "full"
const SETTING_SHORT := "short"
const SETTING_OFF := "off"
const SHOT := "summon"

var cfg: Dictionary = {}
## The Vowbound whose cinematic plays (&"" when none).
var active_id: StringName = &""
## Seconds into it, at the battle speed.
var elapsed := 0.0
## Plays the full version even outside a live story battle (its freeze-frame capture).
var force_full := false
## False holds its clock (captures); advance() still moves it.
var live := true

var _choreo: BattleChoreo
var _ctl: BattleController
var _engine: BattleEngine
var _light: OmniLight3D
var _summon_pose: Dictionary = {}


static func attached(choreo: BattleChoreo, controller: BattleController, engine: BattleEngine) -> BattleSummonCinematic:
	var s := BattleSummonCinematic.new()
	s.name = "BattleSummonCinematic"
	s.cfg = choreo.data.get(KEY, {}) as Dictionary
	s._choreo = choreo
	s._ctl = controller
	s._engine = engine
	choreo.add_child(s)
	return s


## True when `cid`'s call should play the full cinematic now.
func wants_full(cid: StringName) -> bool:
	var setting := str(_setting())
	if not _choreo.animating() or setting == SETTING_OFF:
		return false
	var flag := first_call_flag(cid)
	if flag == &"":
		return false
	if force_full or (setting == SETTING_FULL and _live()):
		return true
	return _live() and not bool(Game.get_flag(flag))


## The entrance for `cid`'s call when this cinematic decides it ({} = the short entry): the full cinematic, or under
## "off" no rise at all.
func entry_for(cid: StringName) -> Dictionary:
	if first_call_flag(cid) != &"" and str(_setting()) == SETTING_OFF:
		return cfg.get("off_entry", {}) as Dictionary
	return begin(cid) if wants_full(cid) else {}


## The seen-flag of `cid`'s first call (choreo.json summon_cinematic.first_call_flags; &"" for none).
func first_call_flag(cid: StringName) -> StringName:
	var base := String(cid).get_slice("#", 0)
	return StringName(str((cfg.get("first_call_flags", {}) as Dictionary).get(base, "")))


## Starts the cinematic for `cid` and returns its entrance (BattleVowboundChoreo.enter_spec).
func begin(cid: StringName) -> Dictionary:
	active_id = cid
	elapsed = 0.0
	if _live() and not force_full and not bool(Game.get_flag(first_call_flag(cid))):
		Game.set_flag(first_call_flag(cid))
	_summon_pose = {}
	_place_light()
	advance(0.0)
	return cfg.get("entry", {}) as Dictionary


func playing() -> bool:
	return active_id != &""


## Seconds of it left, at the battle speed (0 when none plays).
func remaining_sec() -> float:
	return maxf(total_sec() - elapsed, 0.0) / _choreo.speed if playing() else 0.0


## The whole cinematic: the entrance (its delay and rise) plus the held beat after it.
func total_sec() -> float:
	var e := cfg.get("entry", {}) as Dictionary
	return float(e.get("delay_sec", 0.0)) + float(e.get("sec", 0.0)) + float(cfg.get("hold_sec", 0.0))


func _process(delta: float) -> void:
	if live and playing():
		advance(delta)


func advance(delta: float) -> void:
	if not playing():
		return
	elapsed += delta * _choreo.speed
	_light_at(elapsed)
	_camera_at(elapsed)
	if elapsed >= total_sec():
		_end()


## Confirm or cancel skips it.
func _unhandled_input(event: InputEvent) -> void:
	if playing() and (event.is_action_pressed(&"ui_accept") or event.is_action_pressed(&"ui_cancel")):
		skip()
		get_viewport().set_input_as_handled()


## Ends it now: the Vowbound stands on its mark, the light holds steady, the camera is home.
func skip() -> void:
	if not playing():
		return
	_choreo.skip_entering(active_id)
	elapsed = total_sec()
	_light_at(elapsed)
	_end()


func _end() -> void:
	active_id = &""
	if _choreo.camera != null:
		_choreo.camera.rest()


## The bound light at the Vowbound's slot: fades in over light_in_sec from light_at_sec, then holds steady (it stays
## with the Vowbound while it is out and goes when the battle scene does).
func _place_light() -> void:
	if _light == null or not is_instance_valid(_light):
		_light = OmniLight3D.new()
		_light.name = "SummonLight"
		_light.light_color = Color(str(cfg.get("light_color", "#FFFFFF")))
		_light.omni_range = float(cfg.get("light_range_m", 0.0))
		_light.shadow_enabled = false
		_ctl.stage.add_child(_light)
	var f := _ctl.stage.stand_in(active_id)
	if f != null:
		_light.position = _ctl.stage.to_local(f.global_position) + Vector3.UP * float(cfg.get("light_height_m", 0.0))
	_light.light_energy = 0.0


func _light_at(t: float) -> void:
	if _light == null or not is_instance_valid(_light):
		return
	var k := clampf(
		(t - float(cfg.get("light_at_sec", 0.0))) / maxf(float(cfg.get("light_in_sec", 0.0)), 0.0001), 0.0, 1.0
	)
	_light.light_energy = float(cfg.get("light_energy", 0.0)) * k


func light() -> OmniLight3D:
	return _light


## Default -> the low summon frame over camera_in_sec, held, back to the default by the end. Reduced motion and skip
## animations keep the default.
func _camera_at(t: float) -> void:
	var director := _choreo.camera
	if director == null or director.camera == null or director.still():
		return
	if _summon_pose.is_empty():
		var f := _ctl.stage.stand_in(active_id)
		if f == null:
			return
		var slot := (f.get_parent() as Node3D).transform * _choreo.home_origin(active_id)
		_summon_pose = director.shot_pose(SHOT, slot, slot, slot)
		if _summon_pose.is_empty():
			return
	var home := director._default_pose()
	var w_in := BattleCameraDirector._weight(t, 0.0, float(cfg.get("camera_in_sec", 0.0)))
	var out_sec := float(cfg.get("camera_out_sec", 0.0))
	var w_out := BattleCameraDirector._weight(t, total_sec() - out_sec, total_sec())
	var pose := BattleCameraDirector._mix(BattleCameraDirector._mix(home, _summon_pose, w_in), home, w_out)
	var pos: Vector3 = pose["pos"]
	director.camera.transform = Transform3D(Basis.looking_at((pose["look"] as Vector3) - pos, Vector3.UP), pos)
	director.camera.fov = float(pose["fov"])


func _setting() -> Variant:
	var s := UiSettings.shared()
	if s == null or not s.settings().has(SETTING):
		return ""
	return s.get_value(SETTING)


func _live() -> bool:
	return _ctl.persist_progress and _ctl.fixture == null
