class_name Ch05AshcrownZone
extends Ch05Zone
## Ashcrown, `ch05/ashcrown` (M3-C05-02; act1_ch05.md B07 to B10): the pilgrim stair, the four inner
## tiers of the strike trial, and the anvil court. A Ch05Zone that is the view of AshcrownTrial (the
## rules; game/data/trials/ashcrown.json). Layout triggers carry {"trial": action, "id": piece}:
##   catch    a tier's catch-rod (id: the tier)       turn     a vein-gate (id: the gate)
##   stand    a floor plate (Toma moves there)        release  a tier's release lever (id: the tier)
## They answer only once ch05_trial_begun is set and while the story is free. The view:
##   - reports the metres the player walks (walk_metres; the stud ring is counted in steps);
##   - turns Greybox/<gate> by 90° a step, lights Greybox/Bowl_<tier> while it holds the charge;
##   - opens the stair down to a tier as the strike reaches it (hides Greybox/Stair_<tier>);
##   - moves the stage actor `plate_actor` (Toma) to the mark plate_<plate>;
##   - on the sealed side vein: sets the trial's alcove_flag and hides Greybox/QuenchSeal;
##   - on the landing: sets landed_flag (the anvil court's trigger wakes the Matron);
##   - plays the trial's hint_scene once on the hint sequencer after the idle time.
## The trial's state lives with the zone: a zone entered with landed_flag set (a return from the
## Matron) builds it solved.

const KEY_TRIAL := "trial"
const KEY_ID := "id"
const ACT_CATCH := "catch"
const ACT_TURN := "turn"
const ACT_STAND := "stand"
const ACT_RELEASE := "release"
const BEGUN_FLAG := &"ch05_trial_begun"
const BOWL := "Bowl_%s"
const STAIR := "Stair_%s"
const SEAL_BLOCK := "QuenchSeal"
const PLATE_MARK := "plate_%s"
const KEY_VIEW := "trial_view"

var trial: AshcrownTrial
## The last release's outcome (tests read it).
var last_outcome: StringName = &""

var _last_pos := Vector3.ZERO


func build() -> void:
	if trial != null:
		return
	super()
	trial = AshcrownTrial.new()
	trial.rotated.connect(_on_rotated)
	trial.plate_moved.connect(_on_plate_moved)
	trial.caught.connect(_on_caught)
	trial.faded.connect(_on_faded)
	trial.ran.connect(_on_ran)
	trial.alcove_opened.connect(_on_alcove)
	trial.landed.connect(_on_landed)
	trial.hint_due.connect(_on_hint)


func _ready() -> void:
	super()
	FieldEvents.connect_interacted(_on_interacted)
	if bool(Game.get_flag(_flag("landed_flag"))):
		trial.done = true
		for i in trial.tier_count():
			_open_stair(trial.tier_id(i))
	if bool(Game.get_flag(_flag("alcove_flag"))):
		trial.alcove_open = true
		hide_block(SEAL_BLOCK)
	_on_plate_moved(trial.plate_held)
	_last_pos = player.position


func _exit_tree() -> void:
	if EventBus.is_connected(FieldEvents.INTERACTED, _on_interacted):
		EventBus.disconnect(FieldEvents.INTERACTED, _on_interacted)


func _physics_process(delta: float) -> void:
	var step := player.position - _last_pos
	_last_pos = player.position
	walk_metres(Vector2(step.x, step.z).length())
	if live():
		trial.advance(delta)


## Places the player as GreyboxZone does; a placement is not a walk, so the stud ring ignores it.
func place_at(spawn: StringName, yaw_deg: float = 0.0) -> bool:
	var ok := super(spawn, yaw_deg)
	_last_pos = player.position
	return ok


## The party walked `metres` (the stud ring's clock).
func walk_metres(metres: float) -> void:
	trial.walk(metres)


## True while the trial's pieces answer: it has begun, is not over, and the story is free.
func live() -> bool:
	return bool(Game.get_flag(BEGUN_FLAG)) and not trial.done and story != null and story.is_free()


## Acts on one trial piece (what an interaction does). Returns true when the trial took it.
func act(action: String, id: String) -> bool:
	if not live():
		return false
	match action:
		ACT_CATCH:
			return trial.catch(StringName(id))
		ACT_TURN:
			return trial.turn(StringName(id))
		ACT_STAND:
			return trial.stand(StringName(id))
		ACT_RELEASE:
			return trial.release(StringName(id)) != &""
	push_warning("Ch05AshcrownZone: unknown trial action '%s'" % action)
	return false


func _on_interacted(_id: StringName, _kind: StringName, payload: Dictionary) -> void:
	if payload.has(KEY_TRIAL):
		act(str(payload[KEY_TRIAL]), str(payload.get(KEY_ID, "")))


func _on_rotated(gate: StringName, rotation: int) -> void:
	var n := _block(String(gate))
	if n != null:
		n.rotation_degrees.y = float(rotation) * 360.0 / float(trial.steps())


func _on_plate_moved(plate: StringName) -> void:
	var who := str((layout.get(KEY_VIEW, {}) as Dictionary).get("plate_actor", ""))
	var a := stage.actor(StringName(who)) if who != "" else null
	var m := stage.mark(StringName(PLATE_MARK % plate))
	if a != null and m != null:
		a.position = m.position


func _on_caught(tier: int) -> void:
	_glow(trial.tier_id(tier), true)
	_open_stair(trial.tier_id(tier))


func _on_faded(tier: int) -> void:
	_glow(trial.tier_id(tier), false)


func _on_ran(tier: int, _path: Array[StringName], outcome: StringName) -> void:
	last_outcome = outcome
	if outcome != AshcrownTrial.OUT_OPEN:
		_glow(trial.tier_id(tier), false)


func _on_alcove() -> void:
	Game.set_flag(_flag("alcove_flag"))
	hide_block(SEAL_BLOCK)


func _on_landed() -> void:
	Game.set_flag(_flag("landed_flag"))


func _on_hint() -> void:
	if hint != null and not hint.is_playing():
		hint.play(StringName(str(trial.data.get("hint_scene", ""))), stage)


## Opens the stair down to `tier` (its Greybox/Stair_<tier> block, where the layout has one).
func _open_stair(tier: StringName) -> void:
	if _block(STAIR % tier) != null:
		hide_block(STAIR % tier)


func _glow(tier: StringName, on: bool) -> void:
	var n := _block(BOWL % tier)
	if n == null:
		return
	var color := Color.html(str((layout.get(KEY_VIEW, {}) as Dictionary).get("charge_color", "#ffffff")))
	var dressing := get_node_or_null(^"Dressing") as ZoneKitDressing
	if dressing != null and dressing.glow(String(BOWL % tier), on, color) > 0:
		return  # the kit's bowl holds the charge (env-art-b); the greybox block is hidden
	var mi := n.get_node_or_null(^"Mesh") as MeshInstance3D
	if mi == null or not mi.mesh is BoxMesh:
		return
	var mat := ((mi.mesh as BoxMesh).material as StandardMaterial3D).duplicate() as StandardMaterial3D
	mat.emission_enabled = on
	mat.emission = Color.html(str((layout.get(KEY_VIEW, {}) as Dictionary).get("charge_color", "#ffffff")))
	mi.material_override = mat


func _flag(key: String) -> StringName:
	return StringName(str(trial.data.get(key, "")))
