class_name BattleEntryCamera
extends Node
## M3-BPR-1325 (env-art-b's Fisher Stair marks): a set piece's entry has no fighter, so its turn would play on the
## default frame. When an entry acts (the Climb: a group reaches the wall-head) and the arena has the role's camera
## hint (choreo.json camera.moments.entry `hints` by the entry's role: ward -> CameraHints/the_stair_head), the camera
## eases to that hint once the action has played, holds, and comes home (BattleCameraDirector.play_moment: none
## under reduced motion or instant pacing; the next turn waits). Listens only.
## M3-BPR-406: a role listed in `skills` cuts only on those skills (the Kirru: Pell sounding Storm-Call, not the
## withdrawal itself, which reads best on the home frame), and a role in `once` cuts on its first such turn only.

var choreo: BattleChoreo
var engine: BattleEngine
var cfg: Dictionary = {}
## Entries whose turn moved the camera (tests).
var cut_for: Array[StringName] = []


## Builds it when the fight has a scripted entry and choreo.json has camera.moments.entry (else null).
static func attached(sequencer: BattleChoreo, battle: BattleEngine) -> BattleEntryCamera:
	var row := (
		((sequencer.data.get("camera", {}) as Dictionary).get("moments", {}) as Dictionary).get("entry", {})
		as Dictionary
	)
	if row.is_empty() or battle == null or (battle.entries.is_empty() and battle.pending_entries.is_empty()):
		return null
	var b := BattleEntryCamera.new()
	b.name = "BattleEntryCamera"
	sequencer.add_child(b)
	b.choreo = sequencer
	b.engine = battle
	b.cfg = row
	sequencer.contact.connect(b._on_contact)
	return b


func _on_contact(result: ActionResult) -> void:
	var c := engine.find(result.actor_id)
	if c == null or c.entry_role == &"" or choreo._ctl.stage.has_fighter(c.id):
		return
	var only := (cfg.get("skills", {}) as Dictionary).get(String(c.entry_role), []) as Array
	if not only.is_empty() and not only.has(String(result.skill_id)):
		return
	if (cfg.get("once", []) as Array).has(String(c.entry_role)) and cut_for.has(c.id):
		return
	var pose := hint_pose(c.entry_role)
	if not pose.is_empty():
		choreo.after_sequence(_play.bind(c.id, pose))


func _play(cid: StringName, pose: Dictionary) -> void:
	if (
		choreo.camera != null
		and choreo.camera.play_moment(
			&"entry",
			pose,
			float(cfg.get("in_sec", 0.0)),
			float(cfg.get("hold_sec", 0.0)),
			float(cfg.get("out_sec", 0.0))
		)
	):
		cut_for.append(cid)


## The role's camera hint as a director pose ({pos, look, fov}, the camera's parent space); {} when the arena has none.
func hint_pose(role: StringName) -> Dictionary:
	var arena := choreo._ctl.get_node_or_null(NodePath(String(BattleArena.ARENA_NODE)))
	var path := str((cfg.get("hints", {}) as Dictionary).get(String(role), ""))
	var m := arena.get_node_or_null(NodePath(path)) as Node3D if arena != null and path != "" else null
	if m == null or choreo.camera == null:
		return {}
	var x := choreo.camera._parent_inverse() * m.global_transform
	var look := x.origin - x.basis.z.normalized() * float(cfg.get("look_m", 8.0))
	return {"pos": x.origin, "look": look, "fov": float(cfg.get("fov", choreo.camera.default_fov))}
