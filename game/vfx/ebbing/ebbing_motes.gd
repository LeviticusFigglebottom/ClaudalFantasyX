class_name EbbingMotes
extends Node3D
## Ch9's Ebbing (M3-C09-03; act1_ch09.md §9): the real held fields behind the chapter's `@vfx glimmer_held at=<mark>`
## cues. Docs: docs/kb/tech/ebbing.md. Data: game/data/vfx/ebbing.json.
## - One GlimmerField per cue mark, HELD (rule 1: this rig never calls release()), sinking toward `sea_direction`
##   through the zone's water and mirrored in it where the water is still.
## - The staff attractor: a StaffHead node the rig puts on Asha's body, low enough that the stream lags and sinks
##   behind it (item 3).
## - The mourner attractors: grief anchors on the kneeling mourners, each easing to nothing over `ramp_s` once the
##   staff passes it, so the motes leave reluctantly (item 4).
## - The cutaway's field (N13) takes no attractor and is never the scene focus (item 8).
## The sequencer offers each `@vfx` cue to the stage's `cutscene_vfx_hosts` group first (play_vfx; the hookup is
## M3-ARC-1326); a cue this rig takes draws no placeholder.

const DATA_PATH := "res://game/data/vfx/ebbing.json"
const VFX_HOSTS_GROUP := &"cutscene_vfx_hosts"
const EFFECT := "glimmer_held"
const STAFF_HEAD := &"StaffHead"

## path -> parsed data: each zone's Ebbing reads its own file (Ch9's by default; Ch15's held dead, M4-A2P-045).
static var _data_cache: Dictionary = {}

## The data this rig reads (a zone's dressing names its own: `"ebbing": {"data": ...}`).
var data_path := DATA_PATH

## The cutscene stage (mark(id), actor(id)), or the zone whose `stage` it is (ZoneKitDressing sets the zone: the
## zone builds its stage after its dressing is ready).
var stage: Object
var zone: Node
var data: Dictionary = {}
## mark id -> GlimmerField, the fields playing now.
var fields: Dictionary = {}
var staff_head: Node3D
## mourner actor id -> {"node", "fields": Array, "passed_s": float (< 0: not yet passed)}
var _mourners: Dictionary = {}


static func load_data(path: String = DATA_PATH) -> Dictionary:
	if not _data_cache.has(path):
		var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(path))
		if typeof(parsed) == TYPE_DICTIONARY:
			_data_cache[path] = parsed as Dictionary
		else:
			push_warning("EbbingMotes: cannot read %s" % path)
			return {}
	return _data_cache[path] as Dictionary


## A mourner's pull, over its full strength, `since_pass_s` after the staff passed it (< 0: not yet): 1, easing to 0
## over `ramp_s`.
static func mourner_share(since_pass_s: float, ramp_s: float) -> float:
	if since_pass_s < 0.0:
		return 1.0
	return 1.0 - smoothstep(0.0, maxf(ramp_s, 0.001), since_pass_s)


func _ready() -> void:
	data = load_data(data_path)
	add_to_group(VFX_HOSTS_GROUP)


## Offered every `@vfx` cue by the sequencer: plays the field for `at_id` and returns true when it is an Ebbing mark
## and the effect is held light; false leaves the cue to the placeholder.
func play_vfx(effect: String, at_id: StringName, _kwargs: Dictionary = {}) -> bool:
	if effect != EFFECT or not (data.get("fields", {}) as Dictionary).has(String(at_id)):
		return false
	return play(at_id)


## Starts the field for one mark (again: no-op). Its `ends` stop earlier fields unless `apply_ends` is false (a test
## frame holding every field at once).
func play(at_id: StringName, apply_ends: bool = true) -> bool:
	if fields.has(at_id):
		return true
	var row := (data.get("fields", {}) as Dictionary).get(String(at_id), {}) as Dictionary
	var mark := _mark(at_id)
	if row.is_empty() or mark == null:
		push_warning("EbbingMotes: no field or mark '%s'" % at_id)
		return false
	var field := build_field(row)
	field.name = "Field_%s" % at_id
	add_child(field)
	field.global_position = mark.global_position
	fields[at_id] = field
	if bool(row.get("staff", false)):
		_add_staff(field)
	if bool(row.get("mourners", false)):
		_add_mourners(field)
	for other: String in row.get("ends", []) if apply_ends else []:
		stop(StringName(other))
	return true


## Lets a field run out: no new motes; the ones in the air finish their life (sinking) before it goes.
func stop(at_id: StringName) -> void:
	var field := fields.get(at_id) as GlimmerField
	if field == null:
		return
	fields.erase(at_id)
	if field.motes != null:
		field.motes.emitting = false
	get_tree().create_timer(float(data.get("end_fade_s", 14.0))).timeout.connect(field.queue_free)


## A held field from one data row (pure but for the node: no attractors, not in the tree).
func build_field(row: Dictionary) -> GlimmerField:
	var field := GlimmerField.new()
	field.mode = GlimmerState.Mode.HELD
	var disc := str(row.get("shape", "box")) == "disc"
	field.emission_shape = GlimmerField.EmissionShape.DISC if disc else GlimmerField.EmissionShape.BOX
	field.emission_extents_m = _vec(row.get("extents_m", [3.0, 1.0, 3.0]))
	field.amount_multiplier = float(row.get("amount", 1.0))
	field.height_bias = float(row.get("height_bias", 1.0))
	field.sea_direction = _vec(data.get("sea_direction", [0.0, 0.0, 1.0])).normalized()
	field.water_height_m = float(data.get("water_height_m", 0.0))
	field.still_water_reflection = bool(row.get("reflection", false))
	field.follow_global_focus = bool(row.get("focus", true))
	return field


func _add_staff(field: GlimmerField) -> void:
	var s := data.get("staff", {}) as Dictionary
	if staff_head == null:
		var asha := _actor(StringName(str(s.get("actor", "asha"))))
		if asha == null:
			return
		staff_head = asha.get_node_or_null(NodePath(String(STAFF_HEAD))) as Node3D
		if staff_head == null:
			staff_head = Node3D.new()
			staff_head.name = STAFF_HEAD
			staff_head.position = _vec(s.get("head_offset_m", [0.0, 2.3, 0.0]))
			asha.add_child(staff_head)
	field.add_attractor(
		staff_head,
		float(s.get("strength", 0.2)),
		float(s.get("radius_m", 1.4)),
		float(s.get("swirl", 0.5)),
		float(s.get("half_height_m", 0.3))
	)


func _add_mourners(field: GlimmerField) -> void:
	var m := data.get("mourners", {}) as Dictionary
	for id: String in m.get("actors", []):
		var node := _actor(StringName(id))
		if node == null:
			continue
		if not _mourners.has(id):
			_mourners[id] = {"node": node, "fields": [], "passed_s": -1.0}
		(_mourners[id]["fields"] as Array).append(field)
		_set_mourner(field, node, float(m.get("strength", 0.7)))


func _set_mourner(field: GlimmerField, node: Node3D, strength: float) -> void:
	var m := data.get("mourners", {}) as Dictionary
	if strength <= 0.0:
		field.remove_attractor(node)
		return
	field.add_attractor(
		node, strength, float(m.get("radius_m", 0.8)), float(m.get("swirl", 0.6)), float(m.get("half_height_m", 0.5))
	)


func _process(delta: float) -> void:
	if _mourners.is_empty() or not is_instance_valid(staff_head):
		return
	var m := data.get("mourners", {}) as Dictionary
	var pass_r := float(m.get("pass_radius_m", 3.5))
	var ramp := float(m.get("ramp_s", 4.0))
	var head := staff_head.global_position
	for id: String in _mourners.keys():
		var row := _mourners[id] as Dictionary
		if not is_instance_valid(row["node"]):  # check the stored ref before casting it (a freed one fails the cast)
			_mourners.erase(id)
			continue
		var node := row["node"] as Node3D
		var p := node.global_position
		var passed := float(row["passed_s"])
		if passed < 0.0 and Vector2(head.x - p.x, head.z - p.z).length() <= pass_r:
			passed = 0.0
		elif passed >= 0.0:
			passed += delta
		row["passed_s"] = passed
		var strength := float(m.get("strength", 0.7)) * mourner_share(passed, ramp)
		for f: Variant in row["fields"]:
			if is_instance_valid(f):
				_set_mourner(f as GlimmerField, node, strength)
		if passed > ramp:
			_mourners.erase(id)


func _stage() -> Object:
	if stage == null and zone != null:
		stage = zone.get(&"stage") as Object
	return stage


func _mark(id: StringName) -> Node3D:
	var s := _stage()
	return s.call(&"mark", id) as Node3D if s != null and s.has_method(&"mark") else null


func _actor(id: StringName) -> Node3D:
	var s := _stage()
	return s.call(&"actor", id) as Node3D if s != null and s.has_method(&"actor") else null


static func _vec(a: Variant) -> Vector3:
	var arr := a as Array
	return Vector3(float(arr[0]), float(arr[1]), float(arr[2]))
