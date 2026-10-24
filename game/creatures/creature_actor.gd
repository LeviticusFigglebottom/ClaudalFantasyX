class_name CreatureActor
extends Node3D
## A battle creature's actor scene root (M2-CRE-03, docs/kb/art/creatures/pipeline.md). The scene instances the
## creature's GLB (skeleton, surfaces, clips); this script plays the clips the battle asks for and goes back to
## idle, holds the KO, freezes under Petrify, plays a boss's phase change and swaps its breakable parts. All of it
## comes from game/data/creatures/creatures.json. Presentation only: it is told what to show and never reads or
## writes combat state. FighterStandIn calls it; BattleActorMotion decides when.

const DATA_PATH := "res://game/data/creatures/creatures.json"
## Buckets a path hash is cut into for the fidget interval.
const FIDGET_BUCKETS := 10007

static var _data: Dictionary = {}

## The creatures.json row this actor reads.
@export var creature_id: StringName = &""

## The clip playing now (or the last one), for tests and captures.
var current_clip: StringName = &""

var _row: Dictionary = {}
var _player: AnimationPlayer
var _idle: StringName = &""
var _ko := false
var _frozen := false
var _phase: StringName = &""
var _surfaces: Array[GeometryInstance3D] = []
var _fade: Tween
var _phase_tween: Tween
var _phase_pose: Array = []  # [position, rotation] the phase moves the model to
var _hide_after: Array = []  # nodes a phase hides once its clip has played (hullgnaw's falling frames)
var _show_after: Array = []  # nodes a phase shows once its clip has played (the spar-wraith's water sheath)
## Hits taken (rotates the row's `hit_variants`).
var _hits := 0
## Seconds idling since the last fidget, and when the next one plays (the row's `idle_variety`).
var _idle_clock := 0.0
var _next_fidget := 0.0
var _fidgets := 0
## Charge skill -> broken (the boss's breakable parts).
var _broken: Dictionary = {}


static func data() -> Dictionary:
	if _data.is_empty():
		var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(DATA_PATH))
		if typeof(parsed) != TYPE_DICTIONARY:
			push_error("CreatureActor: could not read %s" % DATA_PATH)
			return {}
		_data = parsed as Dictionary
	return _data


## The defaults merged with creature `id`'s row (one level deep for dictionaries).
static func row_for(id: StringName) -> Dictionary:
	var out := (data().get("defaults", {}) as Dictionary).duplicate(true)
	var row: Dictionary = (data().get("creatures", {}) as Dictionary).get(String(id), {})
	for k: Variant in row:
		if typeof(row[k]) == TYPE_DICTIONARY and typeof(out.get(k)) == TYPE_DICTIONARY:
			(out[k] as Dictionary).merge(row[k] as Dictionary, true)
		else:
			out[k] = row[k]
	return out


func _ready() -> void:
	_row = row_for(creature_id)
	_idle = StringName(str(_row.get("idle", "idle")))
	for n in find_children("*", "GeometryInstance3D", true, false):
		_surfaces.append(n as GeometryInstance3D)
	var players := find_children("*", "AnimationPlayer", true, false)
	if not players.is_empty():
		_player = players[0] as AnimationPlayer
		for clip: Variant in _row.get("loop", []):
			if _player.has_animation(StringName(str(clip))):
				_player.get_animation(StringName(str(clip))).loop_mode = Animation.LOOP_LINEAR
		_player.animation_finished.connect(_on_clip_finished)
	for part: Variant in _row.get("break_parts", {}):
		_show_part(StringName(str(part)), false)
	for p: Variant in (_row.get("phases", {}) as Dictionary).values():  # what a phase brings in starts hidden
		for n: Variant in (p as Dictionary).get("show", []) + (p as Dictionary).get("show_after", []):
			var node := find_child(str(n), true, false) as Node3D
			if node != null:
				node.visible = false
	_play(_idle)


func has_clip(clip: StringName) -> bool:
	return _player != null and _player.has_animation(clip)


## The clip an action plays: clip_by_skill, else clip_by_kind by the skill's kind ("" when neither names one).
func clip_for(skill_id: StringName, kind: StringName) -> StringName:
	var by_skill: Dictionary = _row.get("clip_by_skill", {})
	if by_skill.has(String(skill_id)):
		return StringName(str(by_skill[String(skill_id)]))
	return StringName(str((_row.get("clip_by_kind", {}) as Dictionary).get(String(kind), "")))


## Plays the clip for an action; false if the actor is down, frozen, or has no such clip.
func play_action(skill_id: StringName, kind: StringName) -> bool:
	return play_clip(clip_for(skill_id, kind))


func play_hit() -> bool:
	return play_clip(StringName(str(_row.get("hit", "hit"))))


## Plays a one-shot clip, then idles again. Refused while KO'd or petrified. In a phase whose `clips` map names a
## stand-in for `clip` (the Undertow's Reach strikes from its lifted or drawn-back pose), that clip plays instead.
## A hit rotates through the row's `hit_variants` (the hit, then its mirrored heavier `hit_b`, ...) outside phases
## that map their own hit.
func play_clip(clip: StringName) -> bool:
	var mapped := phase_clip(clip)
	if mapped == clip and clip == StringName(str(_row.get("hit", "hit"))) and not _ko and not _frozen:
		mapped = _next_hit(clip)
	if _ko or _frozen or not has_clip(mapped):
		return false
	_play(mapped)
	return true


func _next_hit(clip: StringName) -> StringName:
	var options: Array[StringName] = []
	for v: Variant in _row.get("hit_variants", []):
		if has_clip(StringName(str(v))):
			options.append(StringName(str(v)))
	if options.is_empty():
		return clip
	_hits += 1
	return options[(_hits - 1) % options.size()]


## The clip the current phase plays for `clip` (its `clips` map), or `clip` itself.
func phase_clip(clip: StringName) -> StringName:
	if _phase == &"":
		return clip
	var phase_row: Dictionary = (_row.get("phases", {}) as Dictionary).get(String(_phase), {})
	var mapped := StringName(str((phase_row.get("clips", {}) as Dictionary).get(String(clip), "")))
	return mapped if mapped != &"" and has_clip(mapped) else clip


## When `clip` lands its blow (creatures.json `contact`, seconds into the clip), for presentation that syncs hit
## reactions and VFX to it (the battle-presentation track's choreography). -1 when the clip has no contact beat.
func contact_time(clip: StringName) -> float:
	return float((_row.get("contact", {}) as Dictionary).get(String(phase_clip(clip)), -1.0))


## The clip's length in seconds (0 if the actor has no such clip).
func clip_length(clip: StringName) -> float:
	return _player.get_animation(clip).length if has_clip(clip) else 0.0


func is_ko() -> bool:
	return _ko


## KO: plays the KO clip, holds its last pose, then fades every surface to `alpha` (battle_sandbox.json
## ko_alpha). A revive brings it back to idle. Repeated calls with the same state do nothing.
func set_ko(on: bool, alpha: float) -> void:
	if on == _ko:
		return
	_ko = on
	if _fade != null and _fade.is_valid():
		_fade.kill()
	if on:
		var clip := StringName(str(_row.get("ko", "ko")))
		var wait := 0.0
		if has_clip(clip) and not _frozen:
			_play(clip)
			wait = _player.get_animation(clip).length
		if is_inside_tree():
			_fade = create_tween()
			_fade.tween_interval(wait)
			_fade.tween_method(_set_transparency, 0.0, 1.0 - alpha, float(_row.get("ko_fade_sec", 0.0)))
		else:
			_set_transparency(1.0 - alpha)
		return
	_set_transparency(0.0)
	_play(_idle)


## Petrify: the clip stops where it is (FighterStandIn swaps the surfaces to stone).
func set_frozen(on: bool) -> void:
	_frozen = on
	if _player == null:
		return
	if on:
		_player.pause()
	elif not _player.is_playing():
		_player.play()


## A boss's phase change (creatures.json `phases`): plays its clip, hides and shows its listed nodes (the Cinder
## Matron's crust bursting off), hides its `hide_after` and shows its `show_after` nodes once the clip has played
## (the hullgnaw's frames fall first; the spar-wraith's water sheath comes after its drop), moves the model by its
## offset and tilt over its time (at once when `instant`, for captures), and idles on the phase's idle clip
## afterwards. An unknown phase does nothing.
func enter_phase(phase_id: StringName, instant := false) -> bool:
	var phases: Dictionary = _row.get("phases", {})
	if not phases.has(String(phase_id)) or phase_id == _phase:
		return false
	_phase = phase_id
	var p: Dictionary = phases[String(phase_id)]
	_idle = StringName(str(p.get("idle", _idle)))
	var off: Array = p.get("offset_m", [0.0, 0.0, 0.0])
	var tilt := Vector3.ZERO
	var tilt_deg: Array = p.get("tilt_deg", [0.0, 0.0, 0.0])
	for i in 3:
		tilt[i] = deg_to_rad(float(tilt_deg[i]))
	var model := _model()
	if model != null:
		if _phase_tween != null and _phase_tween.is_valid():
			_phase_tween.kill()
		var sec := float(p.get("sec", 0.0))
		var target := Vector3(float(off[0]), float(off[1]), float(off[2]))
		_phase_pose = [target, tilt]
		if is_inside_tree() and sec > 0.0 and not instant:
			_phase_tween = create_tween().set_parallel(true).set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN_OUT)
			_phase_tween.tween_property(model, "position", target, sec)
			_phase_tween.tween_property(model, "rotation", tilt, sec)
		else:
			model.position = target
			model.rotation = tilt
	for n: Variant in p.get("hide", []):
		var node := find_child(str(n), true, false) as Node3D
		if node != null:
			node.visible = false
	for n: Variant in p.get("show", []):
		var node := find_child(str(n), true, false) as Node3D
		if node != null:
			node.visible = true
	var clip := StringName(str(p.get("clip", "")))
	if not _ko and not _frozen:
		_play(clip if has_clip(clip) else _idle)
	_hide_after = p.get("hide_after", [])
	_show_after = p.get("show_after", [])
	if is_inside_tree() and not instant and has_clip(clip):
		get_tree().create_timer(clip_length(clip)).timeout.connect(_apply_hide_after.bind(phase_id))
	else:
		_apply_hide_after(phase_id)
	return true


func _apply_hide_after(phase_id: StringName) -> void:
	if phase_id != _phase:
		return
	for n: Variant in _hide_after:
		var node := find_child(str(n), true, false) as Node3D
		if node != null:
			node.visible = false
	for n: Variant in _show_after:
		var node := find_child(str(n), true, false) as Node3D
		if node != null:
			node.visible = true


func phase() -> StringName:
	return _phase


## Jumps a phase change to its end (the model at its offset and tilt, the phase idle playing), as BattleBossVfx's
## settle() does for the flood water: captures and fixtures that enter a phase need no wait.
func settle() -> void:
	if _phase_tween != null and _phase_tween.is_valid():
		_phase_tween.kill()
	var model := _model()
	if model != null and not _phase_pose.is_empty():
		model.position = _phase_pose[0]
		model.rotation = _phase_pose[1]
	if not _ko and not _frozen and _phase != &"":
		_play(_idle)
	_apply_hide_after(_phase)


## A breakable part (creatures.json `break_parts`, keyed by the charge skill it silences): broken shows the
## part's `broken` nodes and hides its `whole` ones, and back. False for a skill with no part.
func set_part_broken(skill_id: StringName, broken: bool) -> bool:
	if not (_row.get("break_parts", {}) as Dictionary).has(String(skill_id)):
		return false
	_broken[skill_id] = broken
	_show_part(skill_id, broken)
	return true


func is_part_broken(skill_id: StringName) -> bool:
	return bool(_broken.get(skill_id, false))


func _show_part(skill_id: StringName, broken: bool) -> void:
	var part: Dictionary = (_row.get("break_parts", {}) as Dictionary).get(String(skill_id), {})
	for n: Variant in part.get("whole", []):
		var node := find_child(str(n), true, false) as Node3D
		if node != null:
			node.visible = not broken
	for n: Variant in part.get("broken", []):
		var node := find_child(str(n), true, false) as Node3D
		if node != null:
			node.visible = broken


func _model() -> Node3D:
	for c in get_children():
		if c is Node3D:
			return c as Node3D
	return null


## The idle fidget (the row's `idle_variety`): while it idles on its own idle clip, outside any phase, playing (a
## portrait's held pose is paused, so it never fidgets) and neither KO'd nor frozen, it plays the fidget once every
## `every_sec` [min, max], the interval picked from a hash of its node path, so a scene replays the same way.
func _process(delta: float) -> void:
	var cfg: Dictionary = _row.get("idle_variety", {})
	var clip := StringName(str(cfg.get("clip", "")))
	if clip == &"" or not has_clip(clip) or _ko or _frozen or _phase != &"" or current_clip != _idle:
		_idle_clock = 0.0
		return
	if not _player.is_playing():
		return
	if _next_fidget <= 0.0:
		_next_fidget = _fidget_interval(cfg)
	_idle_clock += delta
	if _idle_clock >= _next_fidget:
		_idle_clock = 0.0
		_fidgets += 1
		_next_fidget = _fidget_interval(cfg)
		_play(clip)


func _fidget_interval(cfg: Dictionary) -> float:
	var span: Array = cfg.get("every_sec", [1.0, 1.0])
	var u := float(absi(hash("%s:%d" % [str(get_path()), _fidgets])) % FIDGET_BUCKETS) / float(FIDGET_BUCKETS)
	return lerpf(float(span[0]), float(span[1]), u)


func _play(clip: StringName) -> void:
	if not has_clip(clip):
		return
	current_clip = clip
	_player.play(clip, float(_row.get("blend_sec", 0.0)))


func _on_clip_finished(clip: StringName) -> void:
	if _ko or _frozen or clip != current_clip:
		return
	_play(_idle)


func _set_transparency(t: float) -> void:
	for s in _surfaces:
		s.transparency = t
