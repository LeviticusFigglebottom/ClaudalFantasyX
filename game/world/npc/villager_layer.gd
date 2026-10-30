class_name VillagerLayer
extends Node3D
## A zone's villagers alive (M3-CRE-613; docs/kb/tech/field_npc.md "VillagerLayer"). One node at the zone's
## root reads game/data/world/npc/zones/<zone id with / as _>.json and, for each row, turns a stand-in into
## a villager: a FieldNpc carrying the villager's actor scene is added beside the stand-in (same parent, so
## anything that hides the stand-in's group hides the villager too), the stand-in's placeholder meshes are
## hidden, its talk Interactable starts the villager's talk, and the stand-in body (its collision) and the
## `follow` nodes ride along when the villager walks. Rows set the routine: a route, a chat partner, a work
## focus, a storm shelter. The zone's own nodes, ids and dialogue are untouched.
##
## Storms: while the data's `storm_flag` is set (Game.get_flag) every villager here braces; the zone can also
## call set_storm(on) (or FieldNpc.set_storm_all). Deterministic, like FieldNpc: no randomness.
##
## Adopting (the owner split, creatures live log 2026-10-27): a zone that places its own villagers (Haluna's
## HalunaVillagers, slice-polish, under the router's fade) keeps doing so. When a row's stand-in already carries a
## FieldNpc, the layer adopts it instead of adding another: it only wires what needs the zone (the chat partner,
## the work and shelter points, the storm flag); placement, hiding and talk stay the zone's. An adopted villager
## rides inside its body, so a row's route and follow do not apply to it. `VillagerLayer.wire(zone, zone_id)` is
## the one call such a zone makes after placing them.
##
## A row's `actor` (a villager id) dresses it in that villager's model while its own doesn't exist yet; its npc_id
## (talk, tuning, chat) stays its own.
##
## Crowd rows (M3-CRE-659, ADR 0152): `crowd: <person id>` resolves the person in game/data/world/npc/crowd.json:
## their crowd body's actor (assets/crowd/<body>/<body>_actor.tscn), their tints (NpcTints, per instance) and their
## age band's and work clip's tuning (FieldNpc.tuning_over). `offset` [x, y, z] or [x, y, z, yaw_deg] places an
## `attach: child` villager inside its stand-in (several people standing for one group capsule).
##
## `body: <crowd body id>` wears that crowd body with no crowd person (no tints, npc.json tuning); `silhouette:
## "#RRGGBB"` draws the villager as one glowing silhouette in that colour (NpcSilhouette; M3-HER-1142: the figure
## in Corrow's storm wall); `tuning` is merged over the villager's tuning (the figure never glances or turns to the
## party).
##
## Day and night (the Lead, 2026-10-30: Haluna's vignettes): a row's `shown` (`day` or `night`; none: always) shows
## the villager only while the zone's `is_night` (HalunaZone.set_night: the dock at night) is false or true. Hidden, it
## is stopped and not ticked, as HalunaZone's night_hide stops its own villagers.

const DATA_DIR := "res://game/data/world/npc/zones/"
const ACTOR_PATH := "res://assets/characters/villagers/%s/%s_actor.tscn"
const CROWD_PATH := "res://game/data/world/npc/crowd.json"
const CROWD_ACTOR_PATH := "res://assets/crowd/%s/%s_actor.tscn"
## The stand-in children hidden when a row names none.
const DEFAULT_HIDE: Array[String] = ["StandIn", "Facing"]
const SHELTER_SUFFIX := "Shelter"
## Row `attach`: beside the stand-in (it can walk and carries the stand-in) or inside it (a cutscene moves it).
const ATTACH_BESIDE := "beside"
const ATTACH_CHILD := "child"
const WORK_SUFFIX := "Work"
## The child a GreyboxZone stage actor's villager model is named (GreyboxZone `_actor_body`).
const GREYBOX_MODEL := "Model"
## ZoneCast's villager model on an Act I stage actor (M3-CIN-1217; game/levels/act1/zone_cast.gd).
const ZONE_CAST := "Cast"
## Where a row's `at` spot is made when the zone has no stand-in for it (a crowd on a greybox that names no actors).
const CROWD_SPOTS := "CrowdSpots"
## M3-HER-1168: during a scene change, rows are added as many a frame as fit this (their scenes loaded first), and
## the reveal waits this many frames more for the villagers' first ticks.
const SPREAD_BUDGET_MS := 30
const SETTLE_FRAMES := 2
## Row `shown`: only by day, only at night (the zone's `is_night`).
const SHOWN_DAY := "day"
const SHOWN_NIGHT := "night"
const NIGHT_PROPERTY := &"is_night"

## crowd.json, read once (crowd_data) and its people by id.
static var _crowd: Dictionary = {}
static var _crowd_people: Dictionary = {}

## The zone (a location id such as ch02/haluna); it names the data file.
@export var zone_id: StringName = &""
## Overrides the data file (tests, review stages).
@export_file("*.json") var data_path: String = ""
## The node the data's paths and coordinates are relative to. Empty: this node's parent (the zone root).
@export var root_path: NodePath
## False: the owner calls build() and tick(delta) itself (tests).
@export var auto_build := true

var data: Dictionary = {}
var villagers: Array[FieldNpc] = []
var storm := false
var night := false
## FieldNpc -> [[Node3D, Transform3D relative to the villager], ...] (keys are checked with is_instance_valid as
## Variants before any cast: see live_villagers)
var _followers: Dictionary = {}
var _storm_flag: StringName = &""
var _built := false
## FieldNpc -> its row's `shown` (only rows that set one)
var _shown: Dictionary = {}


func _ready() -> void:
	process_priority = 10  # after the villagers have moved this frame
	if auto_build:
		# At once, also when added in the zone's own _ready: a zone loaded as the game loads it shows no capsule even
		# before its first frame (big14 gate). Haluna's shop rows sit inside their bodies under `node_name`
		# "Villager", where HalunaVillagers.populate (run after) looks, so it skips them instead of doubling them.
		# During a scene change the fade covers the screen until the reveal, which the spread build holds until the
		# last villager is in, so no capsule is ever seen either way (ADR 0111 amendment 4).
		if _router_changing():
			_build_spread()
		else:
			build()
	set_process(auto_build)


func _process(delta: float) -> void:
	tick(delta)


## The data file for a zone id.
static func path_for(zone: StringName) -> String:
	return DATA_DIR + String(zone).replace("/", "_") + ".json"


static func load_data(path: String) -> Dictionary:
	if not FileAccess.file_exists(path):
		return {}
	var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(path))
	return parsed if parsed is Dictionary else {}


func _root() -> Node3D:
	var r := get_node_or_null(root_path) as Node3D if not root_path.is_empty() else get_parent_node_3d()
	return r if r != null else self


## Creates the villagers (once). Returns how many it made.
func build() -> int:
	if _built:
		return villagers.size()
	_built = true
	var rows := _begin_build()
	var by_id: Dictionary = {}
	for row: Variant in rows:
		_add_row(row, by_id)
	_finish_build(rows, by_id)
	return villagers.size()


## ADR 0111 amendment 4 (the PC's pass 3: Pemakar's entry stayed over 1 s hidden): built during a scene change, the
## layer holds the router's reveal until the last villager is in; the fade stays opaque. M3-HER-1168 (Haluna's reveal
## held 3.1 s, one row a frame at ~180 ms): a row's cost was mostly loading its actor scene (the GLB, its materials and
## textures, 100-250 ms the first time), so every row's actor scene is first loaded on worker threads
## (ResourceLoader.load_threaded_request) while the frames stay light, then the rows are added as many a frame as
## fit SPREAD_BUDGET_MS (a row with its scene loaded costs ~20 ms), and the reveal waits SETTLE_FRAMES more for the
## villagers' first ticks, so no heavy frame shows as the fade lifts.
func _build_spread() -> void:
	if _built:
		return
	_built = true
	var router := get_tree().root.get_node_or_null(^"SceneRouter")
	router.call(&"hold_reveal", self)
	var rows := _begin_build()
	var requested: Array[String] = []
	for row: Variant in rows:
		var path := _actor_path(row)
		if path != "" and not path in requested and ResourceLoader.exists(path) and not ResourceLoader.has_cached(path):
			if ResourceLoader.load_threaded_request(path, "", true) == OK:
				requested.append(path)
	var pending := requested.duplicate()
	while not pending.is_empty():
		await get_tree().process_frame
		if not is_inside_tree():
			router.call(&"release_reveal", self)
			return
		pending = pending.filter(
			func(p: String) -> bool:
				return ResourceLoader.load_threaded_get_status(p) == ResourceLoader.THREAD_LOAD_IN_PROGRESS
		)
	var loaded: Array[Resource] = []  # held until the rows are built, so the cache keeps them
	for path in requested:
		loaded.append(ResourceLoader.load_threaded_get(path))
	var by_id: Dictionary = {}
	var frame_start := Time.get_ticks_usec()
	for i in rows.size():
		_add_row(rows[i], by_id)
		if i < rows.size() - 1 and Time.get_ticks_usec() - frame_start > SPREAD_BUDGET_MS * 1000:
			await get_tree().process_frame
			if not is_inside_tree():
				router.call(&"release_reveal", self)
				return
			frame_start = Time.get_ticks_usec()
	_finish_build(rows, by_id)
	for i in SETTLE_FRAMES:
		await get_tree().process_frame
		if not is_inside_tree():
			break
	router.call(&"release_reveal", self)


## The actor scene a row's villager will wear (what _make loads), or "" when it wears none of its own (an adopted
## model, a bad row).
func _actor_path(row: Variant) -> String:
	if not row is Dictionary:
		return ""
	var r := row as Dictionary
	var crowd_id := StringName(str(r.get("crowd", "")))
	if crowd_id != &"":
		var body := str(crowd_person(crowd_id).get("body", ""))
		return CROWD_ACTOR_PATH % [body, body] if body != "" else ""
	if r.has("body"):
		var bare := str(r["body"])
		return CROWD_ACTOR_PATH % [bare, bare] if bare != "" else ""
	var actor_id := str(r.get("actor", r.get("npc_id", "")))
	return ACTOR_PATH % [actor_id, actor_id] if actor_id != "" else ""


## True while SceneRouter (when there is one) is changing scene: its fade covers the screen.
func _router_changing() -> bool:
	var router := get_tree().root.get_node_or_null(^"SceneRouter") if is_inside_tree() else null
	return router != null and bool(router.call(&"is_busy"))


func _begin_build() -> Array:
	data = load_data(data_path if data_path != "" else path_for(zone_id))
	_storm_flag = StringName(str(data.get("storm_flag", "")))
	return data.get("villagers", [])


func _add_row(row: Variant, by_id: Dictionary) -> void:
	if row is Dictionary:
		var npc := _make(row as Dictionary)
		if npc != null:
			villagers.append(npc)
			by_id[npc.npc_id] = npc
			var shown := str((row as Dictionary).get("shown", ""))
			if shown == SHOWN_DAY or shown == SHOWN_NIGHT:
				_shown[npc] = shown


func _finish_build(rows: Array, by_id: Dictionary) -> void:
	for row: Variant in rows:
		if not row is Dictionary or not by_id.has(StringName(str(row.get("npc_id", "")))):
			continue
		var mate := StringName(str(row.get("chat_with", "")))
		if by_id.has(mate):
			(by_id[StringName(str(row["npc_id"]))] as FieldNpc).partner = by_id[mate] as FieldNpc
	_check_storm()
	_apply_shown()


## Adds a layer for `zone_id` under `zone` (after the zone has placed any villagers of its own) and builds it; a zone
## that already has its layer (one GreyboxZone adds, M3-CRE-657) keeps it, so no villager shows twice.
static func wire(zone: Node3D, zone_id: StringName) -> VillagerLayer:
	var existing := zone.get_node_or_null(^"VillagerLayer") as VillagerLayer
	if existing != null:
		return existing
	var layer := VillagerLayer.new()
	layer.name = "VillagerLayer"
	layer.zone_id = zone_id
	zone.add_child(layer)
	return layer


## A row's `at` ([x, y, z] or [x, y, z, yaw_deg] in the zone's space): the empty stand-in at `path`
## (CrowdSpots/<name>) made for it, for a zone whose greybox names no actor there (the Act II towns' crowds).
func _spot(root: Node, path: String, at: Variant) -> Node3D:
	var parts := path.split("/")
	if parts.size() != 2 or parts[0] != CROWD_SPOTS or _vec3(at) == Vector3.INF:
		push_warning(
			"VillagerLayer %s: an `at` row's stand-in must be %s/<name>, not %s" % [zone_id, CROWD_SPOTS, path]
		)
		return null
	var holder := root.get_node_or_null(CROWD_SPOTS) as Node3D
	if holder == null:
		holder = Node3D.new()
		holder.name = CROWD_SPOTS
		root.add_child(holder)
	var spot := Node3D.new()
	spot.name = parts[1]
	spot.transform = offset_transform(at)
	holder.add_child(spot)
	return spot


## The FieldNpc a zone already put on `stand_in` (itself, or a child), or null.
static func placed_on(stand_in: Node) -> FieldNpc:
	if stand_in is FieldNpc:
		return stand_in as FieldNpc
	for c: Node in stand_in.get_children():
		if c is FieldNpc:
			return c as FieldNpc
	return null


func _make(row: Dictionary) -> FieldNpc:
	var root := _root()
	var id := StringName(str(row.get("npc_id", "")))
	var stand_in := root.get_node_or_null(NodePath(str(row.get("stand_in", "")))) as Node3D
	if stand_in == null and row.has("at"):
		stand_in = _spot(root, str(row.get("stand_in", "")), row["at"])
	var crowd_id := StringName(str(row.get("crowd", "")))
	var person := crowd_person(crowd_id) if crowd_id != &"" else {}
	if crowd_id != &"" and person.is_empty():
		push_warning("VillagerLayer %s: %s names no crowd person %s" % [zone_id, id, crowd_id])
		return null
	var placed := placed_on(stand_in) if stand_in != null else null
	if placed != null and placed != stand_in and not person.is_empty() and not placed in villagers:
		# a crowd person replaces a villager the zone placed earlier in another's model (HalunaVillagers' shop bodies,
		# which populate before the layer builds), so one body shows; a group's other people are the layer's own
		stand_in.remove_child(placed)
		placed.free()
		placed = null
	var adopted := placed if person.is_empty() else null
	var model := stand_in.get_node_or_null(NodePath(GREYBOX_MODEL)) as Node3D if stand_in != null else null
	var cast := stand_in.get_node_or_null(NodePath(ZONE_CAST)) as Node3D if stand_in != null else null
	if cast != null and not person.is_empty():
		# a crowd person replaces ZoneCast's stand-in villager (one of Haluna's, which stand for no other town: ADR
		# 0152), so one body shows and the cutscenes' clips find the crowd person's player
		stand_in.remove_child(cast)
		cast.free()
	elif model == null and cast != null:
		model = cast  # a named villager's own model, cast by ZoneCast: adopted as the greybox model is
	if adopted == null and model != null and not model is FieldNpc:
		return _adopt_model(row, id, stand_in, model, person)
	if adopted != null:
		adopted.shelter = _marker(row.get("shelter", null), String(stand_in.name) + "Villager" + SHELTER_SUFFIX)
		adopted.work_target = _marker(row.get("work_at", null), String(stand_in.name) + "Villager" + WORK_SUFFIX)
		return adopted
	var scene: PackedScene = null
	if not person.is_empty() or row.has("body"):
		# `body` (M3-HER-1142): a crowd body worn by no crowd person (the Corrow storm figure's silhouette)
		var body := str(person.get("body", row.get("body", "")))
		scene = load(CROWD_ACTOR_PATH % [body, body]) as PackedScene if body != "" else null
	else:
		# `actor` (optional): wear another villager's model until this one has its own (M3-CRE-100: the shop bodies).
		var actor_id := str(row.get("actor", id))
		scene = load(ACTOR_PATH % [actor_id, actor_id]) as PackedScene if actor_id != "" else null
	if stand_in == null or scene == null:
		push_warning("VillagerLayer %s: cannot place %s (stand-in %s)" % [zone_id, id, row.get("stand_in", "")])
		return null
	var npc := FieldNpc.new()
	# a crowd person is named for itself: several can stand for one group stand-in; a row's `node_name` overrides
	npc.name = String(stand_in.name) + "Villager" if person.is_empty() else String(crowd_id)
	npc.name = str(row.get("node_name", npc.name))
	npc.npc_id = id
	npc.actor_scene = scene
	npc.auto_process = auto_build
	_dress(npc, person)
	if row.has("silhouette"):
		npc.silhouette = Color.html(str(row["silhouette"]))
	if row.get("tuning", null) is Dictionary:
		npc.tuning_over = FieldNpc.merged(npc.tuning_over, row["tuning"] as Dictionary)
	# `attach: child` (a cutscene-staged actor, which a cutscene moves): the villager rides inside the stand-in and
	# keeps no route; otherwise it stands beside the stand-in and carries the stand-in along when it walks.
	var inside := str(row.get("attach", ATTACH_BESIDE)) == ATTACH_CHILD
	var holder := stand_in if inside else stand_in.get_parent_node_3d()
	if inside:
		npc.transform = offset_transform(row.get("offset", null))
	else:
		npc.transform = Transform3D(Basis(Vector3.UP, stand_in.rotation.y), stand_in.position)
		_set_route(npc, row, holder)
	holder.add_child(npc)
	for child_name: Variant in row.get("hide", DEFAULT_HIDE):
		var hidden := stand_in.get_node_or_null(NodePath(str(child_name))) as Node3D
		if hidden != null:
			hidden.visible = false
	var talk := root.get_node_or_null(NodePath(str(row.get("talk", "")))) as Interactable
	npc.listen_to(talk)
	var follow: Array = [] if inside else [stand_in]
	for p: Variant in row.get("follow", []) if not inside else []:
		var n := root.get_node_or_null(NodePath(str(p))) as Node3D
		if n != null and not n in follow:
			follow.append(n)
	var rel: Array = []
	for n: Node3D in follow:
		rel.append([n, npc.global_transform.affine_inverse() * n.global_transform])
	_followers[npc] = rel
	npc.shelter = _marker(row.get("shelter", null), String(npc.name) + SHELTER_SUFFIX)
	npc.work_target = _marker(row.get("work_at", null), String(npc.name) + WORK_SUFFIX)
	return npc


## M3-CRE-656: a greybox stage actor that already stands as a villager model (GreyboxZone `_actor_body`, a layout row's
## `"model"`, M2-FP-111) becomes a FieldNpc carrying that same model, so it glances, turns to talk and keeps its
## routines instead of only idling. The model moves under the FieldNpc as its `Actor`; the stage actor node stays
## where the cutscenes find it, and the FieldNpc rides inside it (no route or follow, as `attach: child`).
func _adopt_model(
	row: Dictionary, id: StringName, stand_in: Node3D, model: Node3D, person: Dictionary = {}
) -> FieldNpc:
	var npc := FieldNpc.new()
	npc.name = String(stand_in.name) + "Villager"
	npc.npc_id = id
	npc.auto_process = auto_build
	_dress(npc, person)
	npc.transform = model.transform
	stand_in.remove_child(model)
	model.transform = Transform3D.IDENTITY
	model.name = FieldNpc.ACTOR_NAME
	npc.add_child(model)
	stand_in.add_child(npc)
	npc.listen_to(_root().get_node_or_null(NodePath(str(row.get("talk", "")))) as Interactable)
	npc.shelter = _marker(row.get("shelter", null), String(npc.name) + SHELTER_SUFFIX)
	npc.work_target = _marker(row.get("work_at", null), String(npc.name) + WORK_SUFFIX)
	return npc


## A crowd person's colours and tuning on its FieldNpc (before it enters the tree, so its _ready sees them).
func _dress(npc: FieldNpc, person: Dictionary) -> void:
	if person.is_empty():
		return
	npc.tints = (person.get("tints", {}) as Dictionary).duplicate()
	npc.tuning_over = crowd_tuning(person)


## A row's `offset` inside its stand-in: [x, y, z] or [x, y, z, yaw_deg] (FieldNpc yaw: 0 faces -Z); none: identity.
static func offset_transform(spec: Variant) -> Transform3D:
	var at := _vec3(spec)
	if at == Vector3.INF:
		return Transform3D.IDENTITY
	var yaw := deg_to_rad(float(spec[3])) if (spec as Array).size() >= 4 else 0.0
	return Transform3D(Basis(Vector3.UP, yaw), at)


## game/data/world/npc/crowd.json (read once).
static func crowd_data() -> Dictionary:
	if _crowd.is_empty():
		_crowd = load_data(CROWD_PATH)
		for p: Variant in _crowd.get("people", []):
			if p is Dictionary:
				_crowd_people[StringName(str(p.get("id", "")))] = p
	return _crowd


## A crowd person's row in crowd.json, or {}.
static func crowd_person(id: StringName) -> Dictionary:
	crowd_data()
	return _crowd_people.get(id, {}) as Dictionary


## The tuning a crowd person's FieldNpc takes over npc.json's: its age band's, then its work clip's (the clip and
## the work focus).
static func crowd_tuning(person: Dictionary) -> Dictionary:
	var d := crowd_data()
	var out := (
		((d.get("age_tuning", {}) as Dictionary).get(str(person.get("age_band", "")), {}) as Dictionary).duplicate(true)
	)
	var work := str(person.get("work", ""))
	var spec := (d.get("work_tuning", {}) as Dictionary).get(work, {}) as Dictionary
	if work != "" and not spec.is_empty():
		out = FieldNpc.merged(out, spec)
		out = FieldNpc.merged(out, {"clips": {String(FieldNpc.CLIP_WORK): work}})
	return out


## The row's route (zone-root space points, or {"at", "pause_sec", "activity"} entries) in the villager's
## parent space.
func _set_route(npc: FieldNpc, row: Dictionary, holder: Node3D) -> void:
	var root := _root()
	var pts := PackedVector3Array()
	var waits := PackedFloat32Array()
	var acts := PackedStringArray()
	for entry: Variant in row.get("route", []):
		var e: Dictionary = entry if entry is Dictionary else {"at": entry}
		var at := _vec3(e.get("at", []))
		if at == Vector3.INF:
			continue
		pts.append(holder.to_local(root.to_global(at)))
		waits.append(float(e.get("pause_sec", 0.0)))
		acts.append(str(e.get("activity", "")))
	npc.route_points = pts
	npc.route_pauses = waits
	npc.route_activities = acts


## A Marker3D under this layer at a zone-root point [x, y, z] or [x, y, z, yaw_deg] (FieldNpc yaw: 0 faces
## -Z), or null.
func _marker(spec: Variant, marker_name: String) -> Node3D:
	var at := _vec3(spec)
	if at == Vector3.INF:
		return null
	var m := Marker3D.new()
	m.name = marker_name
	add_child(m)
	m.global_position = _root().to_global(at)
	if (spec as Array).size() >= 4:
		m.global_rotation = Vector3(0.0, _root().global_rotation.y + deg_to_rad(float(spec[3])), 0.0)
	return m


static func _vec3(v: Variant) -> Vector3:
	if v is Array and (v as Array).size() >= 3:
		return Vector3(float(v[0]), float(v[1]), float(v[2]))
	return Vector3.INF


## The villager made for `id`, or null.
func villager(id: StringName) -> FieldNpc:
	for n in live_villagers():
		if n.npc_id == id:
			return n
	return null


## The villagers still alive. A zone's teardown can free them before this layer: an object is checked with
## is_instance_valid while it is still a Variant, because casting a freed object to a type is a script error.
func live_villagers() -> Array[FieldNpc]:
	var out: Array[FieldNpc] = []
	for v: Variant in villagers:
		if is_instance_valid(v):
			out.append(v as FieldNpc)
	return out


## Every villager here braces for (or comes out of) the storm.
func set_storm(on: bool) -> void:
	storm = on
	for n in live_villagers():
		n.set_storm(on)


func _check_storm() -> void:
	if _storm_flag == &"":
		return
	var on := bool(Game.get_flag(_storm_flag))
	if on != storm:
		set_storm(on)


## Night falls (or lifts) here: the `shown` rows' villagers appear or go (called by tick from the zone's `is_night`).
func set_night(on: bool) -> void:
	night = on
	_apply_shown()


func _apply_shown() -> void:
	for key: Variant in _shown.keys():
		if not is_instance_valid(key):
			_shown.erase(key)
			continue
		var npc := key as FieldNpc
		var on := (str(_shown[key]) == SHOWN_NIGHT) == night
		npc.visible = on
		npc.process_mode = Node.PROCESS_MODE_INHERIT if on else Node.PROCESS_MODE_DISABLED


func _check_night() -> void:
	var v: Variant = _root().get(NIGHT_PROPERTY)
	if v is bool and bool(v) != night:
		set_night(bool(v))


## One frame: the villagers (when the owner drives them), the storm flag, the night and the riders.
func tick(delta: float) -> void:
	_check_night()
	if not auto_build:
		for n in live_villagers():
			if n.visible:
				n.tick(delta)
	_check_storm()
	for key: Variant in _followers.keys():
		if not is_instance_valid(key):
			_followers.erase(key)
			continue
		var t := (key as Node3D).global_transform
		for pair: Array in _followers[key]:
			var rider: Variant = pair[0]
			if not is_instance_valid(rider):
				continue
			var node := rider as Node3D
			var want := t * (pair[1] as Transform3D)
			if not node.global_transform.is_equal_approx(want):
				node.global_transform = want
