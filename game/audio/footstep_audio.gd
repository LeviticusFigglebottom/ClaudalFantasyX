class_name FootstepAudio
extends Node
## Footsteps and movement foley for one walker in the field (M2-AUD-05, M3-AUD-802; ADR 0031;
## docs/kb/tech/audio_runtime.md "Footsteps"), by listening: the director attaches one when a FieldController enters
## the tree. Once a frame it reads the walker's position (and grounded(), when it has one) and, when the walker
## carries a hero body, that body's animation clock. It never writes either.
##
## When a step plays (game/data/audio/footsteps.json):
## - Foot contacts, when the hero body has them. The body is the walker's `contacts.body` child (HeroFieldActor's
##   "HeroBody"), else the walker. In order: its `contacts.signal` signal (hero-integration's foot_contact(foot, run);
##   its `contacts.run_arg` argument, when present, says walk or run); else the clips'
##   contact markers (`contacts.markers`, M2-CHR-12's foot_l_down / foot_r_down) crossed by the playback position of
##   the body's AnimationTree (each clip node's parameters/<path>/current_position; inside a 1D blend space only the
##   dominant clip counts) or of its playing AnimationPlayer. A clip in `contacts.run_clips` is a run.
##   Contacts closer than `contacts.min_interval_sec` are one step (a cross-fade plays two clips at once). If the
##   walker covers `contacts.stall_m` with no contact (a body that is not animating), a distance step plays.
## - Otherwise, distance: the horizontal distance fills a stride; a walk takes `walk_step_m` strides and a run
##   (at or above run_above_m_s) `run_step_m`. A jump longer than `teleport_m` (a spawn or a warp) is not walked.
## Each step plays the surface's row for the gait at the feet, plus the foley layers (`foley`: cloth on every step,
## the hero's gear every `gear_every` steps). A walk that slows from `stop.from_m_s` to under `stop.below_m_s`
## (or stands still for stop_sec) after `stop.min_steps` steps plays the surface's stop scuff; a change of travel
## heading of `turn.min_deg` within `turn.window_sec` plays its turn scuff.
## The surface is the ground's: the highest-priority node in group `surface_areas.group` (its `surface` meta) or in
## group `surface_areas.group_prefix` + <surface> whose collision shapes hold the feet; else the scene's (its
## `scenes` row, else `default`). A surface row is one sfx id for every gait, or {walk, run, stop, turn}.
## A paused walker (the field menu pauses the tree) covers no distance and its body's clock stands, so it takes no
## steps.

const NO_SURFACE := &""

## Plays a row at a position: (id: StringName, at: Vector3, opts: Dictionary) -> void.
var player: Callable = Callable()
## The walker (a FieldController in the game, any Node3D in tests).
var walker: Node3D
## footsteps.json.
var data: Dictionary = {}
## The scene's surface (a key of data.surfaces); the ground under the feet may override it per step.
var surface: StringName = &""
## The surface the last sound played on.
var last_surface: StringName = &""
## Distance walked since the last step (m), and the last position read.
var stride := 0.0
var steps := 0
var stops := 0
var turns := 0
## The walker's smoothed horizontal speed (m/s).
var speed := 0.0
## Where steps come from: &"signal", &"tree", &"player", or &"" (distance).
var contact_source: StringName = &""
## The node whose contacts are read (the hero body, else the walker), once found.
var body: Node3D
var _tree: AnimationTree
var _anim: AnimationPlayer
## Tree clip nodes: {node: AnimationNodeAnimation, pos: param path, space: the blend space's param path or "",
## points: PackedFloat32Array of the space's point positions, index: this clip's point}.
var _clips: Array[Dictionary] = []
var _prev_pos: Dictionary = {}
var _prev_clip := &""
var _since_contact := 1e9
var _resolve_wait := 0.0
var _last := Vector3.ZERO
var _has_last := false
var _moving := false
var _still_sec := 0.0
var _walk_steps := 0
var _stop_armed := false
var _turn_ref := 0.0
var _turn_age := 0.0
var _turn_cool := 0.0
var _has_turn_ref := false


func _init(table: Dictionary = {}) -> void:
	data = table


## Starts listening to `node`; `scene_path` picks the surface.
func attach(node: Node3D, scene_path: String) -> void:
	walker = node
	surface = surface_for(data, scene_path)
	_has_last = false
	_drop_contacts()


func _exit_tree() -> void:
	_drop_contacts()


## The surface for `scene_path`: its scenes row, else the default.
static func surface_for(table: Dictionary, scene_path: String) -> StringName:
	var scenes := table.get("scenes", {}) as Dictionary
	return StringName(str(scenes.get(scene_path, table.get("default", ""))))


## The stride length at `pace` (m/s): a walk's below run_above_m_s, a run's at or above it.
static func step_length(table: Dictionary, pace: float) -> float:
	return float(table.get("run_step_m" if is_run(table, pace) else "walk_step_m", 1.0))


static func is_run(table: Dictionary, pace: float) -> bool:
	return pace >= float(table.get("run_above_m_s", 0.0))


## The sfx row surface `surf` plays for `kind` (walk, run, stop, turn): a plain row id serves walk and run only.
static func row_for(table: Dictionary, surf: StringName, kind: StringName) -> StringName:
	var row: Variant = (table.get("surfaces", {}) as Dictionary).get(String(surf), "")
	if row is Dictionary:
		return StringName(str((row as Dictionary).get(String(kind), "")))
	if kind == &"walk" or kind == &"run":
		return StringName(str(row))
	return &""


## The surface under `at`: the highest-priority surface area holding it (surface_areas), else `fallback`.
static func surface_at(table: Dictionary, tree: SceneTree, at: Vector3, fallback: StringName) -> StringName:
	var cfg := table.get("surface_areas", {}) as Dictionary
	if cfg.is_empty() or tree == null:
		return fallback
	var best := fallback
	var best_prio := -INF
	var meta := StringName(str(cfg.get("meta", "surface")))
	var prio_meta := StringName(str(cfg.get("priority_meta", "surface_priority")))
	var found: Array[Array] = []  # [node, surface]
	var group := StringName(str(cfg.get("group", "")))
	if group != &"":
		for n in tree.get_nodes_in_group(group):
			found.append([n, StringName(str(n.get_meta(meta, "")))])
	var prefix := str(cfg.get("group_prefix", ""))
	if prefix != "":
		for surf: String in table.get("surfaces", {}) as Dictionary:
			for n in tree.get_nodes_in_group(StringName(prefix + surf)):
				found.append([n, StringName(surf)])
	for pair in found:
		var n := pair[0] as Node3D
		var surf := pair[1] as StringName
		if n == null or surf == NO_SURFACE or not (table.get("surfaces", {}) as Dictionary).has(String(surf)):
			continue
		var prio := float(n.get_meta(prio_meta, 0.0))
		if prio > best_prio and holds(n, at):
			best = surf
			best_prio = prio
	return best


## True when one of `area`'s CollisionShape3D boxes, spheres, cylinders or capsules holds `at`.
static func holds(area: Node3D, at: Vector3) -> bool:
	var shapes := area.find_children("*", "CollisionShape3D", true, false)
	if area is CollisionShape3D:
		shapes.append(area)
	for s: Node in shapes:
		var cs := s as CollisionShape3D
		if cs == null or cs.disabled or cs.shape == null or not cs.is_inside_tree():
			continue
		var p := cs.global_transform.affine_inverse() * at
		var sh := cs.shape
		if sh is BoxShape3D:
			var h := (sh as BoxShape3D).size * 0.5
			if absf(p.x) <= h.x and absf(p.y) <= h.y and absf(p.z) <= h.z:
				return true
		elif sh is SphereShape3D:
			if p.length() <= (sh as SphereShape3D).radius:
				return true
		elif sh is CylinderShape3D:
			var cy := sh as CylinderShape3D
			if Vector2(p.x, p.z).length() <= cy.radius and absf(p.y) <= cy.height * 0.5:
				return true
		elif sh is CapsuleShape3D:
			var cap := sh as CapsuleShape3D
			if Vector2(p.x, p.z).length() <= cap.radius and absf(p.y) <= cap.height * 0.5:
				return true
	return false


## Reads the walker once and plays what it did. AudioDirector.advance calls it; tests call it directly.
func advance(delta: float) -> void:
	if not is_instance_valid(walker) or not walker.is_inside_tree():
		return
	_since_contact += delta
	_turn_cool = maxf(_turn_cool - delta, 0.0)
	_find_contacts(delta)
	var at := walker.global_position
	if not _has_last:
		_last = at
		_has_last = true
		_read_clips(true)
		return
	var dx := Vector2(at.x - _last.x, at.z - _last.z)
	var moved := dx.length()
	_last = at
	if moved > float(data.get("teleport_m", 3.0)):
		_read_clips(true)
		return
	if not _on_ground():
		_read_clips(true)
		return
	# Render frames between physics ticks read no movement: only a pause longer than stop_sec ends a walk, and
	# the pace is a smoothed speed.
	var k := clampf(delta / maxf(float(data.get("speed_smooth_sec", 0.15)), 1e-4), 0.0, 1.0)
	speed = lerpf(speed, moved / maxf(delta, 1e-4), k)
	_read_clips(false)
	if moved <= float(data.get("still_m", 0.0)):
		_still_sec += delta
		_check_stop(at)
		if _still_sec >= float(data.get("stop_sec", 0.2)):
			if _moving:
				_end_walk(at)
			_moving = false
			speed = 0.0
		return
	_still_sec = 0.0
	if not _moving:
		_moving = true
		_has_turn_ref = false
		stride = step_length(data, 0.0) * float(data.get("first_step", 0.5))
	stride += moved
	_check_turn(at, dx, delta)
	_check_stop(at)
	if contact_source != &"":
		if stride >= float((data.get("contacts", {}) as Dictionary).get("stall_m", INF)):
			stride = 0.0
			_step(at, is_run(data, speed))
		return
	var length := step_length(data, speed)
	if stride >= length:
		stride = fmod(stride, length)
		_step(at, is_run(data, speed))


func _on_ground() -> bool:
	return not walker.has_method(&"grounded") or bool(walker.call(&"grounded"))


# --------------------------------------------------------------------------- contacts


func _cfg() -> Dictionary:
	return data.get("contacts", {}) as Dictionary


## Finds the hero body and its contact source (retried every contacts.retry_sec until one is found: the body
## arrives after the controller).
func _find_contacts(delta: float) -> void:
	if contact_source != &"" or _cfg().is_empty():
		return
	_resolve_wait -= delta
	if _resolve_wait > 0.0:
		return
	_resolve_wait = float(_cfg().get("retry_sec", 0.5))
	var named := walker.get_node_or_null(NodePath(str(_cfg().get("body", "")))) as Node3D
	var candidates: Array[Node3D] = [walker]
	if named != null:
		candidates.push_front(named)
	var sig := StringName(str(_cfg().get("signal", "")))
	for c in candidates:
		if sig != &"" and c.has_signal(sig):
			body = c
			var names: Array[String] = []
			for s: Dictionary in c.get_signal_list():
				if StringName(str(s["name"])) == sig:
					for arg: Dictionary in s["args"]:
						names.append(str(arg["name"]))
			c.connect(sig, _contact_callable(names))
			contact_source = &"signal"
			return
	for c in candidates:
		if _scan_tree(c):
			body = c
			contact_source = &"tree"
			return
		if _scan_player(c):
			body = c
			contact_source = &"player"
			return


func _drop_contacts() -> void:
	var sig := StringName(str(_cfg().get("signal", "")))
	if is_instance_valid(body) and sig != &"" and body.has_signal(sig):
		for c: Dictionary in body.get_signal_connection_list(sig):
			var cb := c["callable"] as Callable
			if cb.get_object() == self:
				body.disconnect(sig, cb)
	body = null
	_tree = null
	_anim = null
	_clips.clear()
	_prev_pos.clear()
	contact_source = &""
	_resolve_wait = 0.0


## The handler for a contact signal with arguments `names`: when one is contacts.run_arg (hero-integration's
## foot_contact(foot, run)), its value says walk or run (the live clip's gait); otherwise the pace does.
func _contact_callable(names: Array[String]) -> Callable:
	var at := names.find(str(_cfg().get("run_arg", "")))
	if at < 0:
		return _on_foot_contact if names.is_empty() else _on_foot_contact.unbind(names.size())
	match names.size():
		1:
			return func(a: Variant) -> void: _on_foot_contact_gait([a], at)
		2:
			return func(a: Variant, b: Variant) -> void: _on_foot_contact_gait([a, b], at)
		_:
			return func(a: Variant, b: Variant, c: Variant) -> void: _on_foot_contact_gait([a, b, c], at)


func _on_foot_contact() -> void:
	if not is_instance_valid(walker) or not walker.is_inside_tree() or not _on_ground():
		return
	_contact(is_run(data, speed))


func _on_foot_contact_gait(args: Array, at: int) -> void:
	if not is_instance_valid(walker) or not walker.is_inside_tree() or not _on_ground():
		return
	_contact(bool(args[at]) if at < args.size() else is_run(data, speed))


func _contact(run: bool) -> void:
	if _since_contact < float(_cfg().get("min_interval_sec", 0.0)):
		return
	_since_contact = 0.0
	stride = 0.0
	_step(_feet(), run)


func _feet() -> Vector3:
	return body.global_position if is_instance_valid(body) and body.is_inside_tree() else walker.global_position


func _marks(anim: Animation) -> PackedFloat32Array:
	var out := PackedFloat32Array()
	if anim == null:
		return out
	for m: Variant in _cfg().get("markers", []):
		if anim.has_marker(StringName(str(m))):
			out.append(anim.get_marker_time(StringName(str(m))))
	return out


## Finds the clip nodes of the first AnimationTree under `node`; true when one of its clips has contact markers.
func _scan_tree(node: Node3D) -> bool:
	var trees := node.find_children("*", "AnimationTree", true, false)
	if trees.is_empty():
		return false
	var t := trees[0] as AnimationTree
	if t.tree_root == null:
		return false
	_clips.clear()
	_walk_nodes(t.tree_root, "parameters/", "", PackedFloat32Array(), -1)
	for c in _clips:
		var clip := (c["node"] as AnimationNodeAnimation).animation
		if t.has_animation(clip) and not _marks(t.get_animation(clip)).is_empty():
			_tree = t
			return true
	_clips.clear()
	return false


func _walk_nodes(n: AnimationNode, path: String, space: String, points: PackedFloat32Array, index: int) -> void:
	if n is AnimationNodeAnimation:
		_clips.append({"node": n, "pos": path + "current_position", "space": space, "points": points, "index": index})
	elif n is AnimationNodeBlendTree:
		var bt := n as AnimationNodeBlendTree
		for child: StringName in bt.get_node_list():
			if child != &"output":
				_walk_nodes(bt.get_node(child), "%s%s/" % [path, child], "", PackedFloat32Array(), -1)
	elif n is AnimationNodeBlendSpace1D:
		var bs := n as AnimationNodeBlendSpace1D
		var pts := PackedFloat32Array()
		for i in bs.get_blend_point_count():
			pts.append(bs.get_blend_point_position(i))
		for i in bs.get_blend_point_count():
			_walk_nodes(bs.get_blend_point_node(i), "%s%d/" % [path, i], path, pts, i)


## True when the first AnimationPlayer under `node` has a clip with contact markers.
func _scan_player(node: Node3D) -> bool:
	var players := node.find_children("*", "AnimationPlayer", true, false)
	if players.is_empty():
		return false
	var ap := players[0] as AnimationPlayer
	for clip: StringName in ap.get_animation_list():
		if not _marks(ap.get_animation(clip)).is_empty():
			_anim = ap
			return true
	return false


## The weight of point `index` in a 1D blend space at `b` (linear between its neighbours).
static func point_weight(points: PackedFloat32Array, index: int, b: float) -> float:
	var p := points[index]
	var lo := -INF
	var hi := INF
	for q in points:
		if q < p:
			lo = maxf(lo, q)
		elif q > p:
			hi = minf(hi, q)
	if is_equal_approx(b, p):
		return 1.0
	if b < p:
		return 1.0 if lo == -INF else clampf((b - lo) / (p - lo), 0.0, 1.0)
	return 1.0 if hi == INF else clampf((hi - b) / (hi - p), 0.0, 1.0)


## True when a playback position moving `prev` -> `cur` (wrapping at `length`) passes one of `times`.
static func crossed(times: PackedFloat32Array, prev: float, cur: float, length: float) -> bool:
	if is_equal_approx(prev, cur):
		return false
	for t in times:
		if cur > prev and t > prev and t <= cur:
			return true
		if cur < prev and (t > prev and t <= length or t <= cur):
			return true
	return false


## Reads the body's animation clock and plays a step for a contact it crossed. `reset` only records the positions.
func _read_clips(reset: bool) -> void:
	if contact_source == &"tree":
		_read_tree(reset)
	elif contact_source == &"player":
		_read_player(reset)


func _read_tree(reset: bool) -> void:
	if not is_instance_valid(_tree):
		_drop_contacts()
		return
	var best_w := -1.0
	var best_clip := &""
	for c in _clips:
		var path := str(c["pos"])
		var cur := float(_tree.get(path))
		var prev := float(_prev_pos.get(path, cur))
		_prev_pos[path] = cur
		if reset:
			continue
		var clip := (c["node"] as AnimationNodeAnimation).animation
		# an action slot holds no clip until play_clip() names one
		var anim := _tree.get_animation(clip) if _tree.has_animation(clip) else null
		if anim == null or not crossed(_marks(anim), prev, cur, anim.length):
			continue
		var w := 1.0
		if str(c["space"]) != "":
			var b := float(_tree.get(str(c["space"]) + "blend_position"))
			w = point_weight(c["points"] as PackedFloat32Array, int(c["index"]), b)
		if w > best_w:
			best_w = w
			best_clip = clip
	if best_clip != &"" and best_w >= float(_cfg().get("min_weight", 0.0)):
		_contact(_is_run_clip(best_clip))


func _read_player(reset: bool) -> void:
	if not is_instance_valid(_anim):
		_drop_contacts()
		return
	var clip := _anim.current_animation if _anim.is_playing() else &""
	var cur := _anim.current_animation_position if clip != &"" else 0.0
	var prev := float(_prev_pos.get(&"player", cur))
	var same := clip == _prev_clip
	_prev_pos[&"player"] = cur
	_prev_clip = clip
	if reset or clip == &"":
		return
	var anim := _anim.get_animation(clip)
	if not same:
		prev = -1e-4  # a clip just started: a contact at its first frame counts
	if crossed(_marks(anim), prev, cur, anim.length):
		_contact(_is_run_clip(clip))


func _is_run_clip(clip: StringName) -> bool:
	var name := String(clip).get_slice("/", String(clip).get_slice_count("/") - 1)
	return name in (_cfg().get("run_clips", []) as Array)


# --------------------------------------------------------------------------- what plays


func _hero_id() -> String:
	var id := ""
	if is_instance_valid(body) and &"hero_id" in body:
		id = str(body.get(&"hero_id"))
	return id if id != "" else str((data.get("foley", {}) as Dictionary).get("gear_default", ""))


func _ground(at: Vector3) -> StringName:
	last_surface = surface_at(data, walker.get_tree(), at, surface)
	return last_surface


func _gait_db(run: bool) -> float:
	return float(data.get("run_db" if run else "walk_db", 0.0))


func _step(at: Vector3, run: bool) -> void:
	var surf := _ground(at)
	var row := row_for(data, surf, &"run" if run else &"walk")
	if row == &"":
		return
	steps += 1
	_walk_steps += 1
	_play(row, at, _gait_db(run))
	var foley := data.get("foley", {}) as Dictionary
	if foley.is_empty():
		return
	var cloth := StringName(str((foley.get("cloth", {}) as Dictionary).get("run" if run else "walk", "")))
	if cloth != &"":
		_play(cloth, at, _gait_db(run) + float(foley.get("cloth_db", 0.0)))
	var gear := StringName(str((foley.get("gear", {}) as Dictionary).get(_hero_id(), "")))
	if gear != &"" and steps % maxi(int(foley.get("gear_every", 1)), 1) == 0:
		_play(gear, at, _gait_db(run) + float(foley.get("gear_db", 0.0)))


func _play(row: StringName, at: Vector3, db: float) -> void:
	if player.is_valid():
		player.call(row, at, {"volume_db": db})


func _check_stop(at: Vector3) -> void:
	var cfg := data.get("stop", {}) as Dictionary
	if cfg.is_empty():
		return
	if speed >= float(cfg.get("from_m_s", INF)) and _walk_steps >= int(cfg.get("min_steps", 1)):
		_stop_armed = true
	elif _stop_armed and speed < float(cfg.get("below_m_s", 0.0)):
		_scuff(&"stop", at, float(cfg.get("db", 0.0)))


func _end_walk(at: Vector3) -> void:
	if _stop_armed:
		_scuff(&"stop", at, float((data.get("stop", {}) as Dictionary).get("db", 0.0)))
	_walk_steps = 0
	_stop_armed = false


func _scuff(kind: StringName, at: Vector3, db: float) -> void:
	if kind == &"stop":
		_stop_armed = false
		_walk_steps = 0
	var row := row_for(data, _ground(at), kind)
	if row == &"":
		return
	if kind == &"stop":
		stops += 1
	else:
		turns += 1
	_play(row, at, db)


func _check_turn(at: Vector3, dx: Vector2, delta: float) -> void:
	var cfg := data.get("turn", {}) as Dictionary
	if cfg.is_empty():
		return
	var heading := atan2(dx.x, dx.y)
	_turn_age += delta
	if not _has_turn_ref or _turn_age > float(cfg.get("window_sec", 0.0)):
		_turn_ref = heading
		_turn_age = 0.0
		_has_turn_ref = true
		return
	if absf(rad_to_deg(angle_difference(_turn_ref, heading))) < float(cfg.get("min_deg", 180.0)):
		return
	_turn_ref = heading
	_turn_age = 0.0
	if _turn_cool > 0.0 or speed < float(cfg.get("min_m_s", 0.0)):
		return
	_turn_cool = float(cfg.get("cooldown_sec", 0.0))
	_scuff(&"turn", at, float(cfg.get("db", 0.0)))
