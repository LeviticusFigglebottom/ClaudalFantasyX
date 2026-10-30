class_name WildlifeLayer
extends Node3D
## Ambient, non-combat wildlife for a zone (M3-CRE-611, docs/kb/art/wildlife.md): gulls wheeling and settling on
## perches, shore crabs that scuttle off when the player comes near, fish shoals in the shallows, and (M3-CRE-616)
## insects: moths round the lamps, dragonflies patrolling over water and paddies, fireflies over the fen at dusk
## (Ch10, M4-A2P-056), and kingfishers (the gull's flock, its own meshes) over the fen. A zone adds one
## WildlifeLayer node (at the zone's origin) with `zone_id` set to its location id; the placement is
## game/data/world/wildlife/<zone id with / as _>.json, the kinds and budgets wildlife.json.
##
## Cheap by construction: at most ten MultiMeshes for the whole layer (gulls and kingfishers flying and perched,
## crabs, fish, rays, moths, dragonflies, fireflies; the motion is the wildlife shader's, driven per instance from
## here), no Skeleton3D, no AnimationPlayer, no physics bodies (wildlife never blocks the player); the one exception
## is Ch12's woolback herds, a few skinned actors (WildlifeHerd). A group (a flock, a beach, a shoal, a swarm, a
## herd) pauses while its bounds are off screen and hides past the cull distance.
## Deterministic: every animal's choices come from a seed made from the zone id, and the motion from the frame
## deltas only.

const GULLS_FLYING := &"gull_flying"
const GULLS_PERCHED := &"gull_perched"
const KINGFISHERS_FLYING := &"kingfisher_flying"
const KINGFISHERS_PERCHED := &"kingfisher_perched"
const CRABS := &"crab"
const FISH := &"fish"
const RAYS := &"ray"
const MOTHS := &"moth"
const DRAGONFLIES := &"dragonfly"
const FIREFLIES := &"firefly"
const PLAYER_GROUP := &"player"
const HERDS := &"Herds"
## The starting phase step (seconds) between a herd's animals' first clips.
const HERD_PHASE_S := 1.7
const USEC_PER_MS := 1000.0
const VIS_HIDDEN := 0
const VIS_PAUSED := 1
const VIS_ACTIVE := 2
## `"ground": {"physics": true}`: heights from the zone's collision, cached per cell (x, z quantized).
const PHYSICS_GROUND_CELL_M := 0.25
const PHYSICS_GROUND_TOP_M := 60.0

## The zone's location id (locations.json), e.g. ch02/haluna; it names the data file and seeds the animals.
@export var zone_id: StringName = &""
## Overrides the placement file (tests point it at a fixture). Empty = WildlifeConfig.zone_path(zone_id).
@export_file("*.json") var data_path: String = ""
## The player to flee from. Empty = the first node in group "player".
@export var player_path: NodePath
## The camera that culls. Empty = the viewport's camera.
@export var camera_path: NodePath
## Pause off-screen groups and hide distant ones (off in tests that step without a camera anyway).
@export var cull := true

var kinds: Dictionary = {}
var zone: Dictionary = {}
var budgets: Dictionary = {}
var flocks: Array[WildlifeGullFlock] = []
## Kingfishers (Ch10, M4-A2P-056): the gull's flock, its own kind table, rows and meshes.
var kingfishers: Array[WildlifeGullFlock] = []
var beaches: Array[WildlifeCrabBeach] = []
var shoals: Array[WildlifeShoal] = []
## Rim rays (Ch16, M4-A2P-056): shoals of the `ray` kind, flapping.
var rays: Array[WildlifeShoal] = []
var swarms: Array[WildlifeSwarm] = []
## Woolback herds (Ch12, M4-A2P-056): skinned actors, one node per animal (herd_actors[h][i]) and its player.
var herds: Array[WildlifeHerd] = []
var herd_actors: Array[Array] = []
var herd_players: Array[Array] = []
## Per MultiMesh: the instance buffer (WildlifeBuffer) and the node drawing it.
var buffers: Dictionary = {}
var multimeshes: Dictionary = {}
## Ground height (x, z) -> y from the zone file's `ground`, or empty (flat areas).
var ground := Callable()
## The last step's cost (milliseconds) and how many groups it simulated, paused and hid.
var last_step_ms := 0.0
var active_groups := 0
var paused_groups := 0
var hidden_groups := 0

var _built := false
var _ground_cache: Dictionary = {}
var _last_vis := PackedInt32Array()
var _player: Node3D
var _seed := 0


func _ready() -> void:
	build()


func _process(delta: float) -> void:
	var player := _find_player()
	var has_player := player != null
	var p := to_local(player.global_position) if has_player else Vector3.ZERO
	step(delta, p, has_player, _find_camera())


## Loads the data and makes the groups and MultiMeshes (once).
func build() -> void:
	if _built:
		return
	_built = true
	kinds = WildlifeConfig.load_kinds()
	budgets = kinds.get("budgets", {})
	var path := data_path if data_path != "" else WildlifeConfig.zone_path(zone_id)
	zone = WildlifeConfig.load_json(path)
	if zone.is_empty() or kinds.is_empty():
		return
	if zone_id == &"":
		zone_id = StringName(str(zone.get("zone", "")))
	_seed = WildlifeConfig.seed_for(zone_id)
	ground = _resolve_ground(zone.get("ground", {}))
	var k: Dictionary = kinds["kinds"]
	var left := int(budgets.get("gulls", 0))
	for row: Dictionary in zone.get("flocks", []):
		var n := _take(row, left, "gulls")
		left -= n
		flocks.append(WildlifeGullFlock.new(row, k["gull"], _group_seed("gull", row), n))
	left = int(budgets.get("kingfishers", 0))
	for row: Dictionary in zone.get("kingfishers", []):
		var n := _take(row, left, "kingfishers")
		left -= n
		kingfishers.append(WildlifeGullFlock.new(row, k["kingfisher"], _group_seed("kingfisher", row), n))
	left = int(budgets.get("crabs", 0))
	for row: Dictionary in zone.get("beaches", []):
		var n := _take(row, left, "crabs")
		left -= n
		beaches.append(WildlifeCrabBeach.new(row, k["crab"], _group_seed("crab", row), n, ground))
	left = int(budgets.get("fish", 0))
	for row: Dictionary in zone.get("shoals", []):
		var n := _take(row, left, "fish")
		left -= n
		shoals.append(WildlifeShoal.new(row, k["fish"], _group_seed("fish", row), n, ground))
	left = int(budgets.get("rays", 0))
	for row: Dictionary in zone.get("rays", []):
		var n := _take(row, left, "rays")
		left -= n
		rays.append(WildlifeShoal.new(row, k["ray"], _group_seed("ray", row), n, ground, WildlifeBuffer.MODE_FLAP))
	left = int(budgets.get("insects", 0))
	for row: Dictionary in zone.get("swarms", []):
		var n := _take(row, left, "insects")
		left -= n
		swarms.append(WildlifeSwarm.new(row, k["insect"], _group_seed("insect", row), n))
	var gulls := gull_count()
	buffers[GULLS_FLYING] = WildlifeBuffer.new(gulls)
	buffers[GULLS_PERCHED] = WildlifeBuffer.new(gulls)
	var kfs := kingfisher_count()
	buffers[KINGFISHERS_FLYING] = WildlifeBuffer.new(kfs)
	buffers[KINGFISHERS_PERCHED] = WildlifeBuffer.new(kfs)
	buffers[CRABS] = WildlifeBuffer.new(crab_count())
	buffers[FISH] = WildlifeBuffer.new(fish_count())
	buffers[RAYS] = WildlifeBuffer.new(ray_count())
	buffers[MOTHS] = WildlifeBuffer.new(insect_count(WildlifeSwarm.TYPE_MOTH))
	buffers[DRAGONFLIES] = WildlifeBuffer.new(insect_count(WildlifeSwarm.TYPE_DRAGONFLY))
	buffers[FIREFLIES] = WildlifeBuffer.new(insect_count(WildlifeSwarm.TYPE_FIREFLY))
	_make_multimesh(GULLS_FLYING, k["gull"], "flying", _union(flocks))
	_make_multimesh(GULLS_PERCHED, k["gull"], "perched", _union(flocks))
	if k.has("kingfisher"):
		_make_multimesh(KINGFISHERS_FLYING, k["kingfisher"], "flying", _union(kingfishers))
		_make_multimesh(KINGFISHERS_PERCHED, k["kingfisher"], "perched", _union(kingfishers))
	_make_multimesh(CRABS, k["crab"], "body", _union(beaches))
	_make_multimesh(FISH, k["fish"], "body", _union(shoals))
	if k.has("ray"):
		_make_multimesh(RAYS, k["ray"], "body", _union(rays))
	if k.has("insect"):
		_make_multimesh(MOTHS, k["insect"], "moth", _union(swarms_of(WildlifeSwarm.TYPE_MOTH)))
		_make_multimesh(DRAGONFLIES, k["insect"], "dragonfly", _union(swarms_of(WildlifeSwarm.TYPE_DRAGONFLY)))
		_make_multimesh(FIREFLIES, k["insect"], "firefly", _union(swarms_of(WildlifeSwarm.TYPE_FIREFLY)))
	_build_herds(k)
	_write_all()


func _take(row: Dictionary, left: int, what: String) -> int:
	var want := int(row.get("count", 0))
	var n := clampi(want, 0, maxi(left, 0))
	if n < want:
		push_warning(
			"WildlifeLayer %s: %s %s clamped %d -> %d by the %s budget" % [zone_id, what, row.get("id"), want, n, what]
		)
	return n


func _group_seed(kind: String, row: Dictionary) -> int:
	return WildlifeConfig.seed_for(StringName("%s/%s/%s" % [zone_id, kind, row.get("id", "")]))


func _resolve_ground(spec: Dictionary) -> Callable:
	if spec.is_empty():
		return Callable()
	if bool(spec.get("physics", false)):
		return _physics_ground  # the Act I audit: crabs follow uneven ground (a kit's terrain) by its collision

	var base := get_parent() if get_parent() != null else self
	var node := base.get_node_or_null(NodePath(str(spec.get("node", ""))))
	var method := StringName(str(spec.get("method", "")))
	if node == null or not node.has_method(method):
		push_warning("WildlifeLayer %s: no ground %s.%s; areas use their flat y" % [zone_id, spec.get("node"), method])
		return Callable()
	return Callable(node, method)


## The zone collision's height under (x, z): a ray straight down, cached on a PHYSICS_GROUND_CELL_M grid. Until the
## zone's bodies are in the physics space (the first frames) it answers NAN, and the beach keeps its flat y.
func _physics_ground(x: float, z: float) -> float:
	var key := Vector2i(roundi(x / PHYSICS_GROUND_CELL_M), roundi(z / PHYSICS_GROUND_CELL_M))
	if _ground_cache.has(key):
		return float(_ground_cache[key])
	if not is_inside_tree():
		return NAN
	var from := Vector3(x, PHYSICS_GROUND_TOP_M, z)
	var q := PhysicsRayQueryParameters3D.create(from, from - Vector3(0.0, PHYSICS_GROUND_TOP_M * 2.0, 0.0))
	var hit := get_world_3d().direct_space_state.intersect_ray(q)
	if hit.is_empty():
		return NAN
	var y := float((hit["position"] as Vector3).y)
	_ground_cache[key] = y
	return y


func gull_count() -> int:
	var n := 0
	for f in flocks:
		n += f.count()
	return n


func kingfisher_count() -> int:
	var n := 0
	for f in kingfishers:
		n += f.count()
	return n


func crab_count() -> int:
	var n := 0
	for b in beaches:
		n += b.count()
	return n


func fish_count() -> int:
	var n := 0
	for s in shoals:
		n += s.count()
	return n


func ray_count() -> int:
	var n := 0
	for s in rays:
		n += s.count()
	return n


## Insects of one type (WildlifeSwarm.TYPE_MOTH, TYPE_DRAGONFLY or TYPE_FIREFLY), or of all with "".
func insect_count(swarm_type: String = "") -> int:
	var n := 0
	for s in swarms:
		if swarm_type == "" or s.swarm_type == swarm_type:
			n += s.count()
	return n


func swarms_of(swarm_type: String) -> Array[WildlifeSwarm]:
	var out: Array[WildlifeSwarm] = []
	for s in swarms:
		if s.swarm_type == swarm_type:
			out.append(s)
	return out


## Draw calls before shadow passes: one per MultiMesh that has instances.
func draw_calls() -> int:
	var n := 0
	for key: StringName in buffers:
		if (buffers[key] as WildlifeBuffer).count > 0:
			n += 1
	return n


## One simulation step in the layer's space. `camera` null = everything is active (tests, headless timing).
## A paused group is neither stepped nor rewritten, and a MultiMesh is uploaded only when something in it changed.
func step(delta: float, player: Vector3, has_player: bool, camera: Camera3D = null) -> void:
	var t0 := Time.get_ticks_usec()
	active_groups = 0
	paused_groups = 0
	hidden_groups = 0
	var crabs: WildlifeBuffer = buffers.get(CRABS)
	var fish: WildlifeBuffer = buffers.get(FISH)
	# the insects' MultiMesh per swarm type, and each type's next instance
	var insect_keys := {
		WildlifeSwarm.TYPE_MOTH: MOTHS, WildlifeSwarm.TYPE_DRAGONFLY: DRAGONFLIES, WildlifeSwarm.TYPE_FIREFLY: FIREFLIES
	}
	var insect_base := {MOTHS: 0, DRAGONFLIES: 0, FIREFLIES: 0}
	var dirty := {}
	var g := _step_flocks(flocks, GULLS_FLYING, GULLS_PERCHED, 0, delta, camera, dirty)
	g = _step_flocks(kingfishers, KINGFISHERS_FLYING, KINGFISHERS_PERCHED, g, delta, camera, dirty)
	var base := 0
	for b in beaches:
		var vis := _visibility(b.bounds, camera)
		if vis == VIS_ACTIVE:
			b.step(delta, player, has_player)
		if _changed(g, vis):
			_write_or_hide(vis, crabs, base, b.count(), b.write)
			dirty[CRABS] = true
		base += b.count()
		g += 1
	base = 0
	for s in shoals:
		var vis := _visibility(s.bounds, camera)
		if vis == VIS_ACTIVE:
			s.step(delta, player, has_player)
		if _changed(g, vis):
			_write_or_hide(vis, fish, base, s.count(), s.write)
			dirty[FISH] = true
		base += s.count()
		g += 1
	base = 0
	var ray_buf: WildlifeBuffer = buffers.get(RAYS)
	for s in rays:
		var vis := _visibility(s.bounds, camera)
		if vis == VIS_ACTIVE:
			s.step(delta, player, has_player)
		if _changed(g, vis):
			_write_or_hide(vis, ray_buf, base, s.count(), s.write)
			dirty[RAYS] = true
		base += s.count()
		g += 1
	for s in swarms:
		var vis := _visibility(s.bounds, camera)
		if vis == VIS_ACTIVE:
			s.step(delta, player, has_player)
		var key: StringName = insect_keys[s.swarm_type]
		if _changed(g, vis):
			_write_or_hide(vis, buffers[key], insect_base[key], s.count(), s.write)
			dirty[key] = true
		insect_base[key] += s.count()
		g += 1
	for h in herds.size():
		var herd := herds[h]
		var vis := _visibility(herd.bounds, camera)
		if vis == VIS_ACTIVE:
			herd.step(delta, player, has_player)
		if _changed(g, vis):
			_place_herd(h, vis)
		g += 1
	_upload(dirty)
	last_step_ms = float(Time.get_ticks_usec() - t0) / USEC_PER_MS


## Woolback herds: the rows, and an actor per animal (the kind's scene) under a Herds node, its loops set.
func _build_herds(k: Dictionary) -> void:
	if not k.has("woolback"):
		return
	var kind: Dictionary = k["woolback"]
	var left := int(budgets.get("woolbacks", 0))
	for row: Dictionary in zone.get("herds", []):
		var n := _take(row, left, "woolbacks")
		left -= n
		herds.append(WildlifeHerd.new(row, kind, _group_seed("woolback", row), n, ground))
	if herds.is_empty():
		return
	var packed := load(str(kind["scene"])) as PackedScene
	if packed == null:
		push_error("WildlifeLayer: cannot load %s" % kind["scene"])
		return
	var root := Node3D.new()
	root.name = HERDS
	add_child(root)
	for h in herds.size():
		var actors: Array[Node3D] = []
		var players: Array[AnimationPlayer] = []
		for i in herds[h].count():
			var actor := packed.instantiate() as Node3D
			actor.name = "%s_%d" % [herds[h].id, i]
			root.add_child(actor)
			var ap := actor.find_children("*", "AnimationPlayer", true, false)[0] as AnimationPlayer
			for clip: StringName in [WildlifeHerd.CLIP_GRAZE, WildlifeHerd.CLIP_WALK]:
				if ap.has_animation(clip):
					ap.get_animation(clip).loop_mode = Animation.LOOP_LINEAR
			actors.append(actor)
			players.append(ap)
		herd_actors.append(actors)
		herd_players.append(players)


func woolback_count() -> int:
	var n := 0
	for h in herds:
		n += h.count()
	return n


## Puts herd h's actors where it says (hidden past the cull distance) and starts the clips it changed; a clip that
## starts with the layer begins at a phase of its own, so two animals never graze in step.
func _place_herd(h: int, vis: int) -> void:
	if h >= herd_actors.size():
		return
	var herd := herds[h]
	for i in herd.count():
		var a := herd.animals[i]
		var actor := herd_actors[h][i] as Node3D
		actor.visible = vis != VIS_HIDDEN
		actor.transform = herd.transform_of(a)
		if a.clip_changed:
			var ap := herd_players[h][i] as AnimationPlayer
			if ap.has_animation(a.clip):
				var first := ap.current_animation == ""
				ap.play(a.clip)
				if first:
					ap.seek(fmod(float(i) * HERD_PHASE_S + float(h), ap.current_animation_length), true)
			a.clip_changed = false


## Steps flocks (gulls or kingfishers) into their flying and perched MultiMeshes, groups numbered from g; returns
## the next group number.
func _step_flocks(
	list: Array[WildlifeGullFlock],
	fly_key: StringName,
	perch_key: StringName,
	g: int,
	delta: float,
	camera: Camera3D,
	dirty: Dictionary
) -> int:
	var flying: WildlifeBuffer = buffers.get(fly_key)
	var perched: WildlifeBuffer = buffers.get(perch_key)
	var base := 0
	for f in list:
		var vis := _visibility(f.bounds, camera)
		if vis == VIS_ACTIVE:
			f.step(delta)
		if _changed(g, vis):
			if vis == VIS_HIDDEN:
				for i in f.count():
					flying.hide(base + i)
					perched.hide(base + i)
			else:
				f.write(flying, perched, base)
			dirty[fly_key] = true
			dirty[perch_key] = true
		base += f.count()
		g += 1
	return g


## Whether group g must be rewritten: always while active, else only when its visibility changed.
func _changed(g: int, vis: int) -> bool:
	if _last_vis.size() <= g:
		_last_vis.resize(g + 1)
		_last_vis[g] = -1
	var changed := vis == VIS_ACTIVE or _last_vis[g] != vis
	_last_vis[g] = vis
	return changed


func _write_or_hide(vis: int, buf: WildlifeBuffer, base: int, n: int, write: Callable) -> void:
	if vis != VIS_HIDDEN:
		write.call(buf, base)
		return
	for i in n:
		buf.hide(base + i)


## VIS_ACTIVE = simulate and draw, VIS_PAUSED = off screen (paused, drawn as it was), VIS_HIDDEN = past the
## cull distance.
func _visibility(bounds: AABB, camera: Camera3D) -> int:
	if camera == null or not cull:
		active_groups += 1
		return VIS_ACTIVE
	var cull_cfg: Dictionary = kinds.get("cull", {})
	var world := global_transform * bounds
	var eye := camera.global_position
	var nearest := eye.clamp(world.position, world.end)
	if nearest.distance_to(eye) > float(cull_cfg.get("distance_m", INF)):
		hidden_groups += 1
		return VIS_HIDDEN
	if bool(cull_cfg.get("frustum", false)) and not _in_frustum(world, camera):
		paused_groups += 1
		return VIS_PAUSED
	active_groups += 1
	return VIS_ACTIVE


static func _in_frustum(box: AABB, camera: Camera3D) -> bool:
	for plane: Plane in camera.get_frustum():
		# the box's corner furthest along the plane's inward side (-normal); all outside = culled
		var c := Vector3(
			box.position.x if plane.normal.x > 0.0 else box.end.x,
			box.position.y if plane.normal.y > 0.0 else box.end.y,
			box.position.z if plane.normal.z > 0.0 else box.end.z
		)
		if plane.is_point_over(c):
			return false
	return true


func _write_all() -> void:
	step(0.0, Vector3.ZERO, false, null)


func _union(groups: Array) -> AABB:
	var out := AABB()
	var first := true
	for g: Variant in groups:
		var b: AABB = g.get("bounds")
		out = b if first else out.merge(b)
		first = false
	return out


func _make_multimesh(key: StringName, kind: Dictionary, mesh_key: String, aabb: AABB) -> void:
	var buf: WildlifeBuffer = buffers[key]
	if buf.count == 0:
		return
	var mesh := _load_mesh(str(kind["scene"]), str((kind["meshes"] as Dictionary)[mesh_key]))
	if mesh == null:
		return
	var mm := MultiMesh.new()
	mm.transform_format = MultiMesh.TRANSFORM_3D
	mm.use_custom_data = true
	mm.mesh = mesh
	mm.instance_count = buf.count
	mm.custom_aabb = aabb
	var mmi := MultiMeshInstance3D.new()
	mmi.name = String(key).to_pascal_case()
	mmi.multimesh = mm
	# one material for the kind, or one per mesh (the insects: {"moth": ..., "dragonfly": ...})
	var mat_ref: Variant = kind["material"]
	var mat_path := str((mat_ref as Dictionary)[mesh_key]) if mat_ref is Dictionary else str(mat_ref)
	var mat := load(mat_path) as Material
	if mat != null:
		mmi.material_override = mat
	var shadow: bool = (kind.get("cast_shadow", {}) as Dictionary).get(mesh_key, false)
	mmi.cast_shadow = (
		GeometryInstance3D.SHADOW_CASTING_SETTING_ON if shadow else GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	)
	add_child(mmi)
	multimeshes[key] = mmi


static func _load_mesh(scene_path: String, node_name: String) -> Mesh:
	var packed := load(scene_path) as PackedScene
	if packed == null:
		push_error("WildlifeLayer: cannot load %s" % scene_path)
		return null
	var inst := packed.instantiate()
	var mi := inst.find_child(node_name, true, false) as MeshInstance3D
	var mesh: Mesh = mi.mesh if mi != null else null
	inst.free()
	if mesh == null:
		push_error("WildlifeLayer: %s has no mesh node %s" % [scene_path, node_name])
	return mesh


func _upload(dirty: Dictionary) -> void:
	for key: StringName in dirty:
		var mmi: MultiMeshInstance3D = multimeshes.get(key)
		if mmi != null:
			mmi.multimesh.buffer = (buffers[key] as WildlifeBuffer).data


func _find_player() -> Node3D:
	if is_instance_valid(_player) and _player.is_inside_tree():
		return _player
	_player = null
	if not player_path.is_empty():
		_player = get_node_or_null(player_path) as Node3D
	elif is_inside_tree():
		_player = get_tree().get_first_node_in_group(PLAYER_GROUP) as Node3D
	return _player


func _find_camera() -> Camera3D:
	if not camera_path.is_empty():
		return get_node_or_null(camera_path) as Camera3D
	return get_viewport().get_camera_3d() if is_inside_tree() else null
