class_name HeroFieldParty
extends Node
## The party's followers in the field (M2-HER-1102, ADR 0190): the joined heroes after the leader
## (Game.state.party_ids, at most field.followers.max, in party order) walk behind the player on his
## breadcrumb trail, each a HeroFieldActor (same gait blend and eased turn) on a plain Node3D anchor:
## no physics body, so they never block the player or trip a trigger.
##
## Follower i keeps (i + 1) * spacing_m of trail behind the leader. It steers to that trail point at
## the leader's speed plus follow_gain * the gap (at most max_speed_mps), accelerating at accel_mps2
## and braking at decel_mps2, and never comes nearer than min_gap_m to the body ahead. A ray to the
## floor (the player excluded) sets its feet. After a teleport of the leader, a long gap (catch_up_m)
## or a hide, the trail is laid straight behind the leader and the followers are put on it at once.
##
## They hide while a cutscene that holds the player plays (CutsceneSequencer.is_playing() with
## hold_player), while the zone's CutsceneStage shows the same hero as a visible Actors/<id>, and
## while the player is hidden. The party is re-read every frame, so a join (PartyJoins on
## EventBus.flag_changed, or a zone writing party_ids) adds a follower at once. Tuning:
## game/data/hero_motion/hero_motion.json "field.followers". Added by HeroFieldActor.attach.

const NAME := &"HeroParty"

var controller: FieldController
## The leader's body (its hero id is never a follower).
var leader: HeroFieldActor
## Follower anchors in trail order; each has a HeroFieldActor child named HeroFieldActor.NAME.
var followers: Array[Node3D] = []
## The breadcrumb trail, oldest first (world positions of the leader).
var trail: PackedVector3Array = PackedVector3Array()

var _cfg: Dictionary = {}
var _party: Array[StringName] = []
var _velocities: Array[Vector3] = []
var _last_leader := Vector3.ZERO
var _hidden := false
var _rescan_left := 0.0
var _stages: Array[Node] = []
var _sequencers: Array[Node] = []
var _started := false


## Every node under `root` whose script (or a base of it) has the global class name `type_name`.
static func find_scripted(root: Node, type_name: StringName) -> Array[Node]:
	var out: Array[Node] = []
	_collect(root, type_name, out)
	return out


static func _collect(n: Node, type_name: StringName, out: Array[Node]) -> void:
	var s := n.get_script() as Script
	while s != null:
		if s.get_global_name() == type_name:
			out.append(n)
			break
		s = s.get_base_script()
	for c in n.get_children():
		_collect(c, type_name, out)


func _ready() -> void:
	name = NAME
	_cfg = HeroFieldActor.field_data().get("followers", {}) as Dictionary


func _physics_process(delta: float) -> void:
	advance(delta)


## One step: re-read the party, rescan the zone now and then, move the trail and the followers.
func advance(delta: float) -> void:
	if controller == null or not is_instance_valid(controller) or not controller.is_inside_tree():
		return
	if _cfg.is_empty():
		_cfg = HeroFieldActor.field_data().get("followers", {}) as Dictionary
	sync_party()
	_rescan_left -= delta
	if _rescan_left <= 0.0:
		rescan()
	var lead := controller.global_position
	if not _started:
		_started = true
		_last_leader = lead
		catch_up()
	var jumped := lead.distance_to(_last_leader) > (leader.loco.teleport_m if leader != null else 0.0)
	var leader_speed := Vector2(lead.x - _last_leader.x, lead.z - _last_leader.z).length() / maxf(delta, 1e-6)
	_last_leader = lead
	var hide := should_hide()
	if hide != _hidden:
		_hidden = hide
		for f in followers:
			f.visible = not hide
		if not hide:
			catch_up()
			return
	if hide:
		return
	if jumped:
		catch_up()
		return
	_record(lead)
	var catch := float(_cfg.get("catch_up_m", 0.0))
	for i in followers.size():
		var target := trail_point((i + 1) * float(_cfg.get("spacing_m", 0.0)))
		if (
			Vector2(target.x - followers[i].global_position.x, target.z - followers[i].global_position.z).length()
			> catch
		):
			catch_up()
			return
	for i in followers.size():
		_move(i, leader_speed, delta)


## Brings the followers in line with Game.state.party_ids (leader excluded, at most `max`).
func sync_party() -> void:
	var want: Array[StringName] = []
	var lead_id := leader.hero_id if leader != null else HeroFieldActor.leader_id()
	for id: StringName in Game.state.party_ids:
		if id != lead_id and not id in want and HeroFieldActor.scene_path(id) != "":
			want.append(id)
	want = want.slice(0, int(_cfg.get("max", 0)))
	if want == _party:
		return
	_party = want
	var keep: Dictionary = {}
	for f in followers:
		keep[StringName(f.get_meta(&"hero_id", ""))] = f
	var next: Array[Node3D] = []
	var vel: Array[Vector3] = []
	for id in want:
		var f := keep.get(id) as Node3D
		if f == null:
			f = _new_follower(id)
			if f == null:
				continue
		else:
			keep.erase(id)
		next.append(f)
		vel.append(Vector3.ZERO)
	for f: Node3D in keep.values():
		f.queue_free()
	followers = next
	_velocities = vel
	if _started:
		catch_up()


func _new_follower(id: StringName) -> Node3D:
	var body := HeroFieldActor.create(id)
	if body == null:
		return null
	var anchor := Node3D.new()
	anchor.name = "Follower_%s" % id
	anchor.set_meta(&"hero_id", String(id))
	anchor.top_level = true
	add_child(anchor)
	anchor.global_position = controller.global_position
	anchor.add_child(body)
	body.bind(anchor)
	anchor.visible = not _hidden
	return anchor


## The follower body for hero `id`, or null.
func body_of(id: StringName) -> HeroFieldActor:
	for f in followers:
		if StringName(f.get_meta(&"hero_id", "")) == id:
			return f.get_node(NodePath(String(HeroFieldActor.NAME))) as HeroFieldActor
	return null


## Finds the zone's cutscene stages and sequencers again (gives new stage hero capsules their bodies).
func rescan() -> void:
	_rescan_left = float(_cfg.get("rescan_sec", 0.0))
	var root := controller.get_parent()
	if root == null:
		_stages = []
		_sequencers = []
		return
	_stages = find_scripted(root, &"CutsceneStage")
	_sequencers = find_scripted(root, &"CutsceneSequencer")
	for s in _stages:
		HeroFieldActor.attach_stage(s as CutsceneStage)


## True while the followers should not show (see the class notes).
func should_hide() -> bool:
	if not controller.is_visible_in_tree():
		return true
	for s in _sequencers:
		var seq := s as CutsceneSequencer
		if is_instance_valid(seq) and seq.hold_player and seq.is_playing():
			return true
	return false


## True while follower `id` should not show because a stage shows the same hero.
func staged(id: StringName) -> bool:
	for s in _stages:
		if not is_instance_valid(s):
			continue
		var a := (s as CutsceneStage).get_node_or_null(NodePath("%s/%s" % [CutsceneStage.ACTORS, id])) as Node3D
		if a != null and a.is_visible_in_tree():
			return true
	return false


## Lays the trail straight behind the leader (against his facing) and puts every follower on it.
func catch_up() -> void:
	var lead := controller.global_position
	var yaw := controller.motor.facing_yaw if controller.motor != null else controller.rotation.y
	var back := -(Basis(Vector3.UP, yaw) * Vector3.FORWARD)
	var sample := maxf(float(_cfg.get("trail_sample_m", 0.0)), 0.01)
	var reach := (followers.size() + 1) * float(_cfg.get("spacing_m", 0.0))
	var count := mini(int(ceil(reach / sample)) + 1, int(_cfg.get("trail_max_points", 0)))
	trail = PackedVector3Array()
	for k in range(count, 0, -1):
		trail.append(lead + back * (k * sample))
	_last_leader = lead
	for i in followers.size():
		var p := _grounded(trail_point((i + 1) * float(_cfg.get("spacing_m", 0.0))))
		followers[i].global_position = p
		followers[i].rotation.y = yaw
		_velocities[i] = Vector3.ZERO
		var body := followers[i].get_node_or_null(NodePath(String(HeroFieldActor.NAME))) as HeroFieldActor
		if body != null:
			body.snap()
	_apply_staged()


func _record(lead: Vector3) -> void:
	var sample := float(_cfg.get("trail_sample_m", 0.0))
	if trail.is_empty() or Vector2(lead.x - trail[-1].x, lead.z - trail[-1].z).length() >= sample:
		trail.append(lead)
		var cap := int(_cfg.get("trail_max_points", 0))
		if trail.size() > cap:
			trail = trail.slice(trail.size() - cap)


## The point `dist` metres of trail behind the leader (along the leader, then the crumbs, newest
## first); past the oldest crumb it extends the last segment.
func trail_point(dist: float) -> Vector3:
	var at := controller.global_position
	var left := dist
	for k in range(trail.size() - 1, -1, -1):
		var seg := trail[k] - at
		var flat := Vector2(seg.x, seg.z).length()
		if flat >= left and flat > 0.0:
			return at + seg * (left / flat)
		left -= flat
		at = trail[k]
	if trail.size() >= 2:
		var dir := trail[0] - trail[1]
		var flat := Vector2(dir.x, dir.z).length()
		if flat > 0.0:
			return at + dir * (left / flat)
	return at


func _move(i: int, leader_speed: float, delta: float) -> void:
	var f := followers[i]
	var target := trail_point((i + 1) * float(_cfg.get("spacing_m", 0.0)))
	var gap := Vector3(target.x - f.global_position.x, 0.0, target.z - f.global_position.z)
	var dist := gap.length()
	var want := Vector3.ZERO
	if dist > 1e-4:
		var speed := minf(
			leader_speed + dist * float(_cfg.get("follow_gain", 0.0)), float(_cfg.get("max_speed_mps", 0.0))
		)
		want = gap / dist * minf(speed, dist / delta)
	var v := _velocities[i]
	var rate := (
		float(_cfg.get("accel_mps2", 0.0)) if want.length() >= v.length() else float(_cfg.get("decel_mps2", 0.0))
	)
	v = v.move_toward(want, rate * delta)
	var p := f.global_position + v * delta
	# never nearer than min_gap_m to the body ahead (the leader for the first follower)
	var ahead := controller.global_position if i == 0 else followers[i - 1].global_position
	var off := Vector3(p.x - ahead.x, 0.0, p.z - ahead.z)
	var gap_min := float(_cfg.get("min_gap_m", 0.0))
	if off.length() < gap_min:
		var away := off.normalized() if off.length_squared() > 0.0 else -gap.normalized()
		p = Vector3(ahead.x, p.y, ahead.z) + away * gap_min
		v -= away * minf(v.dot(away), 0.0)
	_velocities[i] = v
	f.global_position = _grounded(p)
	if v.length() > 0.0:
		f.rotation.y = HeroLocomotion.yaw_of(v)
	f.visible = not staged(StringName(f.get_meta(&"hero_id", "")))


func _apply_staged() -> void:
	for f in followers:
		f.visible = not _hidden and not staged(StringName(f.get_meta(&"hero_id", "")))


## `p` with its height on the floor under it (the player excluded), or the leader's height.
func _grounded(p: Vector3) -> Vector3:
	var up := float(_cfg.get("ray_up_m", 0.0))
	var down := float(_cfg.get("ray_down_m", 0.0))
	var world := controller.get_world_3d()
	if world != null:
		var q := PhysicsRayQueryParameters3D.create(p + Vector3.UP * up, p + Vector3.DOWN * down)
		q.exclude = [controller.get_rid()]
		var hit := world.direct_space_state.intersect_ray(q)
		if not hit.is_empty():
			return Vector3(p.x, (hit["position"] as Vector3).y, p.z)
	return Vector3(p.x, controller.global_position.y, p.z)
