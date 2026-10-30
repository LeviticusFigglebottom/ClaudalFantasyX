class_name HeroFieldParty
extends Node
## The party's followers in the field (M2-HER-1102, ADR 0190): the joined heroes after the leader
## (Game.state.party_ids, then with include_reserve the reserve_ids, at most field.followers.max, in that order; the
## big15 playtest: the slice's Toma, in reserve, never walked with Rhen and Asha) walk behind the player on his
## breadcrumb trail, each a HeroFieldActor (same gait blend and eased turn) on a plain Node3D anchor:
## no physics body, so they never block the player or trip a trigger.
##
## Follower i keeps (i + 1) * spacing_m of trail behind the leader. It steers to that trail point at
## the leader's speed plus follow_gain * the gap (at most max_speed_mps), accelerating at accel_mps2
## and braking at decel_mps2, and never comes nearer than min_gap_m to the body ahead. A ray to the
## floor (the player excluded) sets its feet, but only a floor within step_m of the height the leader
## walked at that trail point (a rail above, a gap at a pier's edge below is not his floor; his height
## stands), and the feet ease toward it at vertical_mps, so a stair or a slope never pops. After a
## teleport of the leader (a step over teleport_m, or faster than jump_mps), a long gap (catch_up_m) or a hide, the
## trail is laid straight behind the leader and the followers are put on it at once.
##
## They hide while a cutscene that holds the player plays (CutsceneSequencer.is_playing() with
## hold_player), while the zone's CutsceneStage shows the same hero as a visible Actors/<id>, and
## while the player is hidden. When a held cutscene finishes, the party members it staged (cued) and left within
## hand_off_radius_m of the leader are handed back to the field: their stage actors hide, so the followers (spaced
## behind the leader by catch_up) take over, and a reserve member stops standing on the spawn (the human's playtest:
## after Cutscene A the stage Asha and Toma stood still inside Rhen and Asha's follower stayed hidden). A later held
## cutscene that cues one of them shows it again. Field staging that no cutscene left by the leader (Asha waiting at
## Ch8's stair-head) stays as the zone set it. The party is re-read every frame, so a join (PartyJoins on
## EventBus.flag_changed, or a zone writing party_ids) adds a follower at once. A follower never stands in the line of
## sight from the field camera to the leader: a trail point within sight_clear_m of that line, between the camera and
## him, moves aside off it (the side it is on, kept until it is clear, the other side if a wall is there), so a camera
## trailing him from behind never shows a follower covering him (the big14 playtest: Asha hid Rhen at the start).
## Tuning: game/data/hero_motion/hero_motion.json "field.followers". Added by HeroFieldActor.attach.

const NAME := &"HeroParty"
## Nearer than this to the speaker (flat metres), a follower keeps its heading: the direction would be noise.
const FACE_MIN_M := 0.05
## How far past camera_near_m a follower stood beyond the leader goes (just clear of it).
const LENS_CLEAR_M := 0.05

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
## The leader's travel direction this frame (flat, unit), or zero while he stands.
var _lead_dir := Vector3.ZERO
## Stage actors handed back to the field after a cutscene (hidden by this node; shown again when a cutscene cues them).
var _handed: Array[Node3D] = []
## Sequencers whose signals this node listens to, by instance id; and per sequencer the actor ids its scene cued.
var _watched: Dictionary = {}
var _cued: Dictionary = {}
## Per follower, the side (+1 or -1 along the sight line's right) it stepped to off the camera's line to the leader;
## 0 while its trail point is clear of the line.
var _sight_side: Array[int] = []
## Set when the leader talks to someone (FieldController.interacted): stopped followers turn to face `_face_at`
## until the leader walks on.
var _facing := false
var _face_at := Vector3.ZERO


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
	if controller != null and not controller.interacted.is_connected(face_speaker):
		controller.interacted.connect(face_speaker)


## The leader is talking to `speaker`: every follower standing still turns (eased, through its body) to face it,
## and keeps facing it until the leader walks on.
func face_speaker(speaker: Node3D) -> void:
	if speaker == null or not is_instance_valid(speaker) or not speaker.is_inside_tree():
		return
	_face_at = speaker.global_position
	_facing = true


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
	var leader_speed := Vector2(lead.x - _last_leader.x, lead.z - _last_leader.z).length() / maxf(delta, 1e-6)
	# a step no walk makes (a place_at a few metres off, under the body's own teleport_m) is a jump too
	var jumped := (
		lead.distance_to(_last_leader) > (leader.loco.teleport_m if leader != null else 0.0)
		or leader_speed > float(_cfg.get("jump_mps", INF))
	)
	var travel := Vector3(lead.x - _last_leader.x, 0.0, lead.z - _last_leader.z)
	_lead_dir = travel.normalized() if leader_speed > float(_cfg.get("face_release_mps", 0.0)) else Vector3.ZERO
	if leader_speed > float(_cfg.get("face_release_mps", 0.0)):
		_facing = false
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
		var target := follow_point(i)
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
	var ids: Array[StringName] = Game.state.party_ids.duplicate()
	if bool(_cfg.get("include_reserve", false)):
		ids.append_array(Game.state.reserve_ids)  # the reserve walks with the party too (battle swaps them in)
	for id: StringName in ids:
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
	for s in _sequencers:
		_watch(s as CutsceneSequencer)
	for s in _stages:
		HeroFieldActor.attach_stage(s as CutsceneStage)


func _watch(seq: CutsceneSequencer) -> void:
	var key := seq.get_instance_id()
	if _watched.has(key):
		return
	_watched[key] = true
	seq.cue_played.connect(_on_cue.bind(seq))
	seq.finished.connect(_on_finished.bind(seq))


func _on_cue(_cue: StringName, args: Array, _kwargs: Dictionary, seq: CutsceneSequencer) -> void:
	if not seq.hold_player or args.is_empty():
		return
	var id := StringName(str(args[0]))
	var cued: Array = _cued.get(seq.get_instance_id(), [])
	if not cued.has(id):
		cued.append(id)
	_cued[seq.get_instance_id()] = cued
	for a in _handed.duplicate():
		if is_instance_valid(a) and StringName(a.name) == id:
			a.visible = true  # the scene stages it again
			_handed.erase(a)


func _on_finished(_scene_id: StringName, seq: CutsceneSequencer) -> void:
	var cued: Array = _cued.get(seq.get_instance_id(), [])
	_cued.erase(seq.get_instance_id())
	if seq.hold_player:
		hand_off(cued)


## Hides the stage actors among `actor_ids` that play a party member (not the leader) and stand within
## hand_off_radius_m of the leader, so the followers take over (see the class notes). Returns how many it hid.
func hand_off(actor_ids: Array) -> int:
	if controller == null or not is_instance_valid(controller):
		return 0
	var lead := controller.global_position
	var lead_id := leader.hero_id if leader != null else HeroFieldActor.leader_id()
	var radius := float(_cfg.get("hand_off_radius_m", 0.0))
	var n := 0
	for s in find_scripted(controller.get_parent(), &"CutsceneStage") if controller.get_parent() != null else []:
		var folder := (s as CutsceneStage).get_node_or_null(CutsceneStage.ACTORS)
		if folder == null:
			continue
		for c in folder.get_children():
			var a := c as Node3D
			if a == null or a is FieldController or not a.is_visible_in_tree() or not actor_ids.has(StringName(a.name)):
				continue
			var hero := HeroFieldActor.hero_of(StringName(a.name))
			if hero == lead_id or not (hero in Game.state.party_ids or hero in Game.state.reserve_ids):
				continue
			if Vector2(a.global_position.x - lead.x, a.global_position.z - lead.z).length() > radius:
				continue
			a.visible = false
			_handed.append(a)
			n += 1
	return n


## True while the followers should not show (see the class notes).
func should_hide() -> bool:
	if not controller.is_visible_in_tree():
		return true
	for s in _sequencers:
		if not is_instance_valid(s):  # checked before the cast: casting a freed object is a script error
			continue
		var seq := s as CutsceneSequencer
		if seq.hold_player and seq.is_playing():
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
	# The trail goes straight back, else turned to the first side where every follower stands clear of the walls
	# (arriving with his back to one), else to the side where most do; one still blocked starts on his own spot.
	var best_dir := back
	var best := -1
	for turn_deg: Variant in _cfg.get("catch_up_turns_deg", [0.0]):
		var dir := back.rotated(Vector3.UP, deg_to_rad(float(turn_deg)))
		_lay_trail(lead, dir, sample, count)
		var n := 0
		for i in followers.size():
			n += 0 if blocked(trail_point((i + 1) * float(_cfg.get("spacing_m", 0.0)))) else 1
		if n > best:
			best = n
			best_dir = dir
		if n == followers.size():
			break
	_lay_trail(lead, best_dir, sample, count)
	_last_leader = lead
	_sight_side.clear()  # a new layout picks its sides afresh
	var placed: Array[Vector3] = [lead]
	for i in followers.size():
		var at := _formation_spot(i, placed)
		placed.append(at)
		followers[i].global_position = _grounded(at, at.y)
		followers[i].rotation.y = yaw
		_velocities[i] = Vector3.ZERO
		var body := followers[i].get_node_or_null(NodePath(String(HeroFieldActor.NAME))) as HeroFieldActor
		if body != null:
			body.snap()
	_apply_staged()


## True when `at` is within camera_near_m (flat) of the field camera: a follower laid out there stands in the lens's
## foreground (the PC's GPU QA row 37: at the causeway's spawns Toma's shield filled the frame, a metre from the lens).
func near_camera(at: Vector3) -> bool:
	var near := float(_cfg.get("camera_near_m", 0.0))
	var cam := controller.get_viewport().get_camera_3d() if controller.is_inside_tree() else null
	if near <= 0.0 or cam == null:
		return false
	return Vector2(at.x - cam.global_position.x, at.z - cam.global_position.z).length() < near


## Follower i's place when the party is laid out: its trail point if that is clear (no wall, at least min_gap_m
## from every body in `placed`), moved off the lens as follow_point() moves it when it is near the camera (the same
## spot it then follows: a layout behind the lens that follow_point() pulls in front of it re-ran catch_up() every few
## frames, Ch13's Sanctum Gate), else further back along the trail, else a ring around the leader; never on top
## of another body (the human's playtest: followers stacked inside each other at a spawn).
func _formation_spot(i: int, placed: Array[Vector3]) -> Vector3:
	var spacing := float(_cfg.get("spacing_m", 0.0))
	var gap := float(_cfg.get("min_gap_m", 0.0))
	var lead := controller.global_position
	var steps := int(_cfg.get("spawn_search_steps", 0))
	var own := sight_clear(i, trail_point((i + 1) * spacing))
	if near_camera(own):
		own = off_lens(i, own)
		if _clear_of(own, placed, gap) and not blocked(own):
			return own
	for k in steps + 1:
		var at := sight_clear(i, trail_point((i + 1) * spacing + k * gap))
		if _clear_of(at, placed, gap) and not blocked(at) and not near_camera(at):
			return at
	for ring in range(1, steps + 1):
		for turn in 12:
			var dir := Vector3.FORWARD.rotated(Vector3.UP, TAU * turn / 12.0)
			var at := lead + dir * (spacing * ring)
			if _clear_of(at, placed, gap) and not blocked(at) and not near_camera(at):
				return at
	for ring in range(1, steps + 1):  # walls everywhere: at least never on top of another body
		for turn in 12:
			var at := lead + Vector3.FORWARD.rotated(Vector3.UP, TAU * turn / 12.0) * (gap * ring)
			if _clear_of(at, placed, gap):
				return at
	return trail_point((i + 1) * spacing)


static func _clear_of(at: Vector3, placed: Array[Vector3], gap: float) -> bool:
	for q in placed:
		if Vector2(at.x - q.x, at.z - q.z).length() < gap - 1e-3:
			return false
	return true


func _lay_trail(lead: Vector3, back: Vector3, sample: float, count: int) -> void:
	trail = PackedVector3Array()
	for k in range(count, 0, -1):
		trail.append(lead + back * (k * sample))


## True when a follower standing at `at` (its feet) would overlap a wall: a body_radius_m sphere at body_height_m
## over its feet against the world's colliders (the player's own capsule aside). Steps and curbs lower than that
## don't count.
func blocked(at: Vector3) -> bool:
	var world := controller.get_world_3d()
	if world == null:
		return false
	var q := PhysicsShapeQueryParameters3D.new()
	var ball := SphereShape3D.new()
	ball.radius = float(_cfg.get("body_radius_m", 0.0))
	q.shape = ball
	q.transform = Transform3D(Basis.IDENTITY, at + Vector3.UP * float(_cfg.get("body_height_m", 0.0)))
	q.exclude = [controller.get_rid()]
	return not world.direct_space_state.intersect_shape(q, 1).is_empty()


## The step from `from` by `step`, kept out of walls: slid along the wall it would enter (its surface normal), or
## no step when that is blocked too.
func _clear_step(from: Vector3, step: Vector3) -> Vector3:
	if HeroStairs.near_flight(controller, from + step) or not blocked(from + step):
		return step  # a steep flight's blocking collision is not a wall to a follower climbing its steps
	var world := controller.get_world_3d()
	var q := PhysicsShapeQueryParameters3D.new()
	var ball := SphereShape3D.new()
	ball.radius = float(_cfg.get("body_radius_m", 0.0))
	q.shape = ball
	q.transform = Transform3D(Basis.IDENTITY, from + step + Vector3.UP * float(_cfg.get("body_height_m", 0.0)))
	q.exclude = [controller.get_rid()]
	var rest := world.direct_space_state.get_rest_info(q)
	if not rest.is_empty():
		var n := rest["normal"] as Vector3
		n = Vector3(n.x, 0.0, n.z).normalized()
		var slid := step - n * minf(step.dot(n), 0.0)
		# a slide that keeps almost nothing of the step (straight into a post) is no way on: steer instead
		var kept := slid.length() >= step.length() * float(_cfg.get("slide_min_share", 0.0))
		if n.length_squared() > 0.0 and kept and not blocked(from + slid):
			return slid
	# Still blocked (a post or a rail end the slide catches on): steer around it, the smallest turn first, so a
	# follower never freezes against it (the human's playtest: followers "sit still" at the causeway's rail posts).
	for turn_deg: Variant in _cfg.get("steer_turns_deg", []):
		var turned := step.rotated(Vector3.UP, deg_to_rad(float(turn_deg)))
		if not blocked(from + turned):
			return turned
	return Vector3.ZERO


func _record(lead: Vector3) -> void:
	var sample := float(_cfg.get("trail_sample_m", 0.0))
	if trail.is_empty() or Vector2(lead.x - trail[-1].x, lead.z - trail[-1].z).length() >= sample:
		trail.append(lead)
		var cap := int(_cfg.get("trail_max_points", 0))
		if trail.size() > cap:
			trail = trail.slice(trail.size() - cap)


## Where follower `i` heads: its trail point, moved off the camera's line of sight to the leader (sight_clear), and
## beside him instead when that spot is in the lens's foreground (near_camera: a close camera behind a spawn).
func follow_point(i: int) -> Vector3:
	var at := sight_clear(i, trail_point((i + 1) * float(_cfg.get("spacing_m", 0.0))))
	return off_lens(i, at) if near_camera(at) else at


## `at` moved beside the leader, square to the camera's line to him, (i + 1) * spacing_m out on follower i's side
## (the other side when that is blocked or still near the lens), else beyond him, away from the lens, that far or
## far enough to clear camera_near_m; with
## the camera close behind him (none of those clear of the lens), the unblocked one farthest from it; `at` unchanged
## when all are blocked.
func off_lens(i: int, at: Vector3) -> Vector3:
	var cam := controller.get_viewport().get_camera_3d() if controller.is_inside_tree() else null
	if cam == null:
		return at
	var lead := controller.global_position
	var line := Vector3(lead.x - cam.global_position.x, 0.0, lead.z - cam.global_position.z)
	if line.length() < 1e-3:
		return at
	var right := line.normalized().cross(Vector3.UP)
	var out := (i + 1) * float(_cfg.get("spacing_m", 0.0))
	var side := _sight_side[i] if i < _sight_side.size() and _sight_side[i] != 0 else (1 if i % 2 == 0 else -1)
	var base := Vector3(lead.x, at.y, lead.z)
	var spots: Array[Vector3] = [base + right * (side * out), base - right * (side * out)]
	# beyond him, away from the lens: out, or far enough past him to clear camera_near_m (a camera close behind him)
	var past := maxf(out, float(_cfg.get("camera_near_m", 0.0)) - line.length() + i * float(_cfg.get("min_gap_m", 0.0)))
	spots.append(base + line.normalized() * (past + LENS_CLEAR_M))
	var best := at
	var best_d := Vector2(at.x - cam.global_position.x, at.z - cam.global_position.z).length()
	for spot in spots:
		if blocked(spot):
			continue
		if not near_camera(spot):
			return spot
		var d := Vector2(spot.x - cam.global_position.x, spot.z - cam.global_position.z).length()
		if d > best_d:
			best = spot
			best_d = d
	return best


## `at`, or, when it lies between the field camera and the leader (at least sight_depth_m short of him), under the
## camera's line down to his chest (sight_chest_m: a camera looking down over her head_m sees him), within
## sight_clear_m of the line between them (flat), `at` moved square to that line until it is sight_clear_m off it: to
## the side follower `i` took since the last catch_up, else the side it stands on; the other side when a wall stands
## there or it would come nearer the leader than min_gap_m; then the same at each smaller sight_clear_shares of the
## clearance. Unchanged with no camera, or when nothing will do.
func sight_clear(i: int, at: Vector3) -> Vector3:
	while _sight_side.size() <= i:
		_sight_side.append(0)
	var clear := float(_cfg.get("sight_clear_m", 0.0))
	var cam := controller.get_viewport().get_camera_3d() if controller.is_inside_tree() else null
	if clear <= 0.0 or cam == null:
		_sight_side[i] = 0
		return at
	var lead := controller.global_position
	var line := Vector3(lead.x - cam.global_position.x, 0.0, lead.z - cam.global_position.z)
	var length := line.length()
	if length < 1e-3:
		_sight_side[i] = 0
		return at
	var dir := line / length
	var rel := Vector3(at.x - cam.global_position.x, 0.0, at.z - cam.global_position.z)
	var along := rel.dot(dir)
	var right := dir.cross(Vector3.UP)
	var off := rel.dot(right)
	var depth := float(_cfg.get("sight_depth_m", 0.0))
	if along <= 0.0 or along >= length - depth or absf(off) >= clear:  # level with him, it's beside him: no cover
		_sight_side[i] = 0
		return at
	var chest := lead.y + float(_cfg.get("sight_chest_m", 0.0))
	var line_y := cam.global_position.y + (chest - cam.global_position.y) * (along / length)
	if line_y > at.y + float(_cfg.get("head_m", 0.0)):  # the camera looks down at him over her head
		_sight_side[i] = 0
		return at
	if _sight_side[i] == 0:  # the side she stands on now, so she never walks across his line to reach her spot
		var side_off := off
		if i < followers.size():
			var cur := followers[i].global_position
			side_off = Vector3(cur.x - cam.global_position.x, 0.0, cur.z - cam.global_position.z).dot(right)
		_sight_side[i] = 1 if side_off >= 0.0 else -1
	var gap := float(_cfg.get("min_gap_m", 0.0))
	for share: Variant in _cfg.get("sight_clear_shares", [1.0]):  # full clearance, else less where walls are near
		for side: int in [_sight_side[i], -_sight_side[i]]:
			var moved := at + right * (side * clear * float(share) - off)
			if Vector2(moved.x - lead.x, moved.z - lead.z).length() >= gap and not blocked(moved):
				_sight_side[i] = side
				return moved
	return at


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
	var target := follow_point(i)
	var gap := Vector3(target.x - f.global_position.x, 0.0, target.z - f.global_position.z)
	var dist := gap.length()
	var want := Vector3.ZERO
	if dist > 1e-4:
		var speed := minf(
			leader_speed + dist * float(_cfg.get("follow_gain", 0.0)), float(_cfg.get("max_speed_mps", 0.0))
		)
		speed = minf(speed, HeroStairs.speed_cap_at(controller, f.global_position))  # a steep flight is taken slowly
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
		if _lead_dir != Vector3.ZERO and away.dot(_lead_dir) > 0.0:
			# It stands in the leader's way: it steps aside and lets him pass, then falls in behind, rather than
			# being shoved ahead of him (the human's playtest: walking back past the spawn left them stuck).
			var side := away - _lead_dir * away.dot(_lead_dir)
			if side.length_squared() < 1e-4:
				side = _lead_dir.cross(Vector3.UP)
			away = side.normalized()
		var spot := Vector3(ahead.x, p.y, ahead.z) + away * gap_min
		# eased back at most its top speed a frame: a follower held by a wall would otherwise be shoved in one jump
		p = p.move_toward(spot, float(_cfg.get("gap_push_mps", 0.0)) * delta)
		v -= away * minf(v.dot(away), 0.0)
	# the push rides on the step, so the step as a whole keeps the top speed (Ch7's galleries: 6.9 m/s without this)
	var step := Vector3(p.x - f.global_position.x, 0.0, p.z - f.global_position.z).limit_length(
		float(_cfg.get("max_speed_mps", INF)) * delta
	)
	p = Vector3(f.global_position.x + step.x, p.y, f.global_position.z + step.z)
	var moved := _clear_step(f.global_position, Vector3(p.x - f.global_position.x, 0.0, p.z - f.global_position.z))
	if moved.length_squared() < Vector3(p.x - f.global_position.x, 0.0, p.z - f.global_position.z).length_squared():
		v = moved / delta  # a wall took part of the step: the speed is what was left
	p = Vector3(f.global_position.x + moved.x, p.y, f.global_position.z + moved.z)
	_velocities[i] = v
	var floor_at := _grounded(p, target.y)
	if is_nan(HeroStairs.height_at(controller, p)):
		p.y = move_toward(f.global_position.y, floor_at.y, float(_cfg.get("vertical_mps", INF)) * delta)
	else:
		p.y = floor_at.y  # a flight's profile is already eased, step by step
	f.global_position = p
	var to := Vector3(_face_at.x - f.global_position.x, 0.0, _face_at.z - f.global_position.z)
	if _facing and v.length() <= float(_cfg.get("face_release_mps", 0.0)) and to.length() > FACE_MIN_M:
		f.rotation.y = HeroLocomotion.yaw_of(to)  # the body eases into it (HeroLocomotion's capped turn)
	elif v.length() > 0.0:
		f.rotation.y = HeroLocomotion.yaw_of(v)
	f.visible = not staged(StringName(f.get_meta(&"hero_id", "")))


func _apply_staged() -> void:
	for f in followers:
		f.visible = not _hidden and not staged(StringName(f.get_meta(&"hero_id", "")))


## `p` with its height on the floor under it (the player excluded) when that floor is within step_m of
## `ref_y` (the leader's height on the trail there; NAN: his height now), else at `ref_y`.
func _grounded(p: Vector3, ref_y: float = NAN) -> Vector3:
	var stair_y := HeroStairs.height_at(controller, p)  # M3-ARC-1216: on a steep flight, its steps are the floor
	if not is_nan(stair_y):
		return Vector3(p.x, stair_y, p.z)
	var ref := controller.global_position.y if is_nan(ref_y) else ref_y
	var up := float(_cfg.get("ray_up_m", 0.0))
	var down := float(_cfg.get("ray_down_m", 0.0))
	var world := controller.get_world_3d()
	if world != null:
		var from := Vector3(p.x, ref, p.z)
		var q := PhysicsRayQueryParameters3D.create(from + Vector3.UP * up, from + Vector3.DOWN * down)
		q.exclude = [controller.get_rid()]
		var hit := world.direct_space_state.intersect_ray(q)
		if not hit.is_empty():
			var y := (hit["position"] as Vector3).y
			if absf(y - ref) <= float(_cfg.get("step_m", INF)):
				return Vector3(p.x, y, p.z)
	return Vector3(p.x, ref, p.z)
