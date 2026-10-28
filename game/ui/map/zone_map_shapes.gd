class_name ZoneMapShapes
extends RefCounted
## The zone map's shapes in world space (M2-UI-18), node-free, derived from the zone's own data so
## the map follows the zone as Environment and the slice change it. ZoneMapView draws them.
##
## haluna_layout (game/levels/ch02/haluna/haluna_layout.json):
##   land / foam  the waterline is HalunaTerrain.inland_m's shore curve (terrain.shore_tip_x_m,
##                shore_half_len_m, tip_recede), sampled along z every shore_step_m and closed
##                inland past the visible edge; islets are land discs.
##   sand         the beach between the waterline and the tidewall (runs "beach_head").
##   walls        every wall run's path (the beach head and the lane walls).
##   lanes        the layout's lanes, terrain.lane_width_m wide; pads are its flat yards (discs).
##   buildings / structures  each placed piece listed in zone_map_menu.json "pieces": its
##                footprint turned by yaw_deg (Basis(UP, yaw), as HalunaDresser places it), scaled.
## shell_shrine_trial (game/data/trials/shell_shrine.json "room" and "layout"):
##   floors       the hall: a stadium of two straight walls (hall_half_m) and two half circles
##                (hall_r_m), as ShellShrineLevel builds its collision, plus the passage behind the door.
##   walls        its outline, open where the chamber door stands (door_w).
##   water        the spring, the four basins, the octagonal inner pool and the side pool.
##   rims         the basins' and pools' kerbs; channels: the troughs between them (channel_w).
##   structures   the chamber door.
## greybox_layout (a GreyboxZone's layout JSON, M3-UI-04; every Act I greybox zone): each block's
##   footprint (its size turned by its yaw, Basis(UP, yaw), as GreyboxZone builds it), sorted by
##   its height against zone_map_menu.json "greybox": a block whose top is at most floor_top_m is
##   a floor (solid) or a pad (not solid: lanes, quays, plates); a solid block above that is a
##   building, or a structure when it is at most wall_thick_m across (walls, rails); posts no
##   wider than post_max_m, solid blocks that start overhead_m up, and other non-solid blocks
##   (lamps, sails, glows) are left off. The zone's shape_hints (zone_maps.json) name blocks by
##   id where the height alone would read them wrong: "sea" (open water under everything: the
##   harbour, the river), "water", "floors", "pads", "buildings", "structures" and "skip"; a hint ending
##   in "*" names every block whose id starts with what comes before it (a kit's numbered pieces).
##   A zone dressed from an env-art kit (ADR 0200) keeps its walkable shape in the layout's
##   collision_path file: its blocks are read the same way, and each ramp is a pad (its from-to run,
##   width wide), so the map follows the kit's frame. A layout's own ramps (flights of steps) are pads too.
## Every polygon is a PackedVector2Array of world (x, z) points.

const KIND_HALUNA := &"haluna_layout"
const KIND_SHRINE := &"shell_shrine_trial"
const KIND_GREYBOX := &"greybox_layout"
## A greybox block's map layer (greybox_layer); the hint lists in shape_hints use these names.
const LAYER_SEA := &"sea"
const LAYER_WATER := &"water"
const LAYER_FLOOR := &"floors"
const LAYER_PAD := &"pads"
const LAYER_BUILDING := &"buildings"
const LAYER_STRUCTURE := &"structures"
const LAYER_SKIP := &"skip"
const HINT_LAYERS: Array[StringName] = [
	LAYER_SEA, LAYER_WATER, LAYER_FLOOR, LAYER_PAD, LAYER_BUILDING, LAYER_STRUCTURE, LAYER_SKIP
]
const STYLE_BUILDING := "building"
const OCTAGON := 8

## Open water drawn under everything else (a greybox zone's hinted sea blocks).
var seas: Array[PackedVector2Array] = []
var land: Array[PackedVector2Array] = []
var floors: Array[PackedVector2Array] = []
var sand: Array[PackedVector2Array] = []
var foam: Array[PackedVector2Array] = []
var pads: Array[PackedVector2Array] = []
var lanes: Array[PackedVector2Array] = []
var lane_width_m := 0.0
var water: Array[PackedVector2Array] = []
var rims: Array[PackedVector2Array] = []
var channels: Array[PackedVector2Array] = []
var channel_width_m := 0.0
var buildings: Array[PackedVector2Array] = []
var structures: Array[PackedVector2Array] = []
var walls: Array[PackedVector2Array] = []
## True when open water surrounds the zone (the view fills its background with the sea).
var sea := false


## The shapes of a zone whose source is `source` (MapModel.shape_source), read as `kind`.
## `visible`: the world rectangle the view can show (land closes past it). `metrics`: the map
## block of zone_map_menu.json; `pieces`: its "pieces" block. `greybox`: its "greybox" block and
## `hints`: the zone's shape_hints (both read only for a greybox layout).
static func build(
	kind: StringName,
	source: Dictionary,
	visible: Rect2,
	metrics: Dictionary,
	pieces: Dictionary,
	greybox: Dictionary = {},
	hints: Dictionary = {}
) -> ZoneMapShapes:
	var s := ZoneMapShapes.new()
	match kind:
		KIND_HALUNA:
			s._haluna(source, visible, metrics, pieces)
		KIND_SHRINE:
			s._shrine(source, metrics)
		KIND_GREYBOX:
			s._greybox(source, greybox, hints)
	return s


## A circle of `segments` points around `at`.
static func disc(at: Vector2, radius: float, segments: int) -> PackedVector2Array:
	var out := PackedVector2Array()
	for i in segments:
		out.append(at + Vector2.from_angle(TAU * i / segments) * radius)
	return out


## A rectangle [x, z, w, d] in a piece's frame, turned by `yaw` (radians, Basis(UP, yaw)), scaled
## by `scale` and placed at `at`.
static func footprint(at: Vector2, rect: Array, yaw: float, scale: float) -> PackedVector2Array:
	var x0 := float(rect[0])
	var z0 := float(rect[1])
	var x1 := x0 + float(rect[2])
	var z1 := z0 + float(rect[3])
	var out := PackedVector2Array()
	for c: Vector2 in [Vector2(x0, z0), Vector2(x1, z0), Vector2(x1, z1), Vector2(x0, z1)]:
		var l := c * scale
		out.append(at + Vector2(l.x * cos(yaw) + l.y * sin(yaw), -l.x * sin(yaw) + l.y * cos(yaw)))
	return out


static func _vec(a: Variant) -> Vector2:
	var arr := a as Array
	return Vector2(float(arr[0]), float(arr[1])) if arr != null and arr.size() >= 2 else Vector2.ZERO


static func _path(points: Variant) -> PackedVector2Array:
	var out := PackedVector2Array()
	for p: Variant in points as Array:
		out.append(_vec(p))
	return out


# --- Haluna --------------------------------------------------------------------------------------


func _haluna(layout: Dictionary, visible: Rect2, metrics: Dictionary, pieces: Dictionary) -> void:
	sea = true
	var t: Dictionary = layout.get("terrain", {})
	var segments := int(metrics.get("circle_segments", OCTAGON))
	var step := maxf(float(metrics.get("shore_step_m", 1.0)), 0.1)
	# The waterline, north to south across what the view shows.
	var shore := PackedVector2Array()
	var z := visible.position.y
	while z < visible.end.y + step:
		shore.append(Vector2(shore_x(t, z), z))
		z += step
	var land_poly := shore.duplicate()
	land_poly.append(Vector2(visible.position.x, shore[shore.size() - 1].y))
	land_poly.append(Vector2(visible.position.x, shore[0].y))
	land.append(land_poly)
	foam.append(shore)
	for il: Variant in layout.get("islets", []):
		var a := il as Array
		land.append(disc(Vector2(float(a[0]), float(a[1])), float(a[2]), segments))
	for run: Variant in layout.get("runs", []):
		var path := _path((run as Dictionary).get("path", []))
		if path.size() < 2:
			continue
		walls.append(path)
		if str((run as Dictionary).get("name", "")) == "beach_head":
			sand.append(_beach(t, path))
	lane_width_m = float(t.get("lane_width_m", 0.0))
	for lane: Variant in layout.get("lanes", []):
		lanes.append(_path(lane))
	for p: Variant in layout.get("pads", []):
		var a := p as Array
		pads.append(disc(Vector2(float(a[0]), float(a[1])), float(a[2]), segments))
	for piece: Variant in layout.get("pieces", []):
		var row := piece as Dictionary
		var spec: Dictionary = pieces.get(str(row.get("piece", "")), {})
		if spec.is_empty():
			continue
		var at := _vec(row.get("at", [0.0, 0.0]))
		var yaw := deg_to_rad(float(row.get("yaw_deg", 0.0)))
		var poly := footprint(at, spec.get("footprint", [0, 0, 0, 0]), yaw, float(row.get("scale", 1.0)))
		if str(spec.get("style", "")) == STYLE_BUILDING:
			buildings.append(poly)
		else:
			structures.append(poly)


## The x of the waterline at `z` (HalunaTerrain.inland_m == 0): a parabola that recedes past the
## crescent's tips.
static func shore_x(terrain: Dictionary, z: float) -> float:
	var tip := float(terrain.get("shore_tip_x_m", 0.0))
	var half := maxf(float(terrain.get("shore_half_len_m", 1.0)), 0.001)
	var az := absf(z)
	var x := tip * pow(minf(az, half) / half, 2.0)
	if az > half:
		x -= float(terrain.get("tip_recede", 0.0)) * (az - half)
	return x


## The sand: from the tidewall `head` (north to south) out to the waterline and back.
static func _beach(terrain: Dictionary, head: PackedVector2Array) -> PackedVector2Array:
	var out := head.duplicate()
	for i in range(head.size() - 1, -1, -1):
		out.append(Vector2(shore_x(terrain, head[i].y), head[i].y))
	return out


# --- Greybox zones (M3-UI-04) -------------------------------------------------------------------


func _greybox(layout: Dictionary, rules: Dictionary, hints: Dictionary) -> void:
	var floor_top := float(rules.get("floor_top_m", 0.0))
	var overhead := float(rules.get("overhead_m", INF))
	var thin := float(rules.get("wall_thick_m", 0.0))
	var post := float(rules.get("post_max_m", 0.0))
	var collision := _collision_of(layout)
	for r: Variant in layout.get("ramps", []) + collision.get("ramps", []):  # flights, the layout's own too
		pads.append(_ramp(r as Dictionary))
	for b: Variant in layout.get("blocks", []) + collision.get("blocks", []):
		var row := b as Dictionary
		var size: Array = row.get("size", [1.0, 1.0, 1.0])
		var pos: Array = row.get("pos", [0.0, 0.0, 0.0])
		var poly := footprint(
			Vector2(float(pos[0]), float(pos[2])),
			[-float(size[0]) * 0.5, -float(size[2]) * 0.5, size[0], size[2]],
			deg_to_rad(float(row.get("yaw", 0.0))),
			1.0
		)
		var layer := greybox_layer(row, hints, floor_top, overhead, thin, post)
		match layer:
			LAYER_SEA:
				seas.append(poly)
			LAYER_WATER:
				water.append(poly)
			LAYER_FLOOR:
				floors.append(poly)
			LAYER_PAD:
				pads.append(poly)
			LAYER_BUILDING:
				buildings.append(poly)
			LAYER_STRUCTURE:
				structures.append(poly)


## Which layer greybox block `row` draws in (&"skip": left off): a shape hint naming its id wins;
## otherwise its height and size decide (see the class notes).
static func greybox_layer(
	row: Dictionary, hints: Dictionary, floor_top: float, overhead: float, thin: float, post: float
) -> StringName:
	var id := str(row.get("id", ""))
	for layer in HINT_LAYERS:
		for hint: Variant in hints.get(String(layer), []):
			if hint_names(str(hint), id):
				return layer
	var size: Array = row.get("size", [1.0, 1.0, 1.0])
	var pos: Array = row.get("pos", [0.0, 0.0, 0.0])
	var top := float(pos[1]) + float(size[1]) * 0.5
	var bottom := float(pos[1]) - float(size[1]) * 0.5
	var solid := bool(row.get("solid", true))
	if top <= floor_top:
		return LAYER_FLOOR if solid else LAYER_PAD
	if not solid or bottom >= overhead:
		return LAYER_SKIP
	var across := minf(float(size[0]), float(size[2]))
	if maxf(float(size[0]), float(size[2])) <= post:
		return LAYER_SKIP
	return LAYER_STRUCTURE if across <= thin else LAYER_BUILDING


## True when shape hint `hint` names block `id`: the same id, or a prefix of it before a final "*".
static func hint_names(hint: String, id: String) -> bool:
	return id.begins_with(hint.trim_suffix("*")) if hint.ends_with("*") else hint == id


## The layout's collision_path file ({blocks, ramps}; {} when it names none or it can't be read).
static func _collision_of(layout: Dictionary) -> Dictionary:
	var path := str(layout.get("collision_path", ""))
	if path == "" or not FileAccess.file_exists(path):
		return {}
	var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(path))
	return parsed as Dictionary if typeof(parsed) == TYPE_DICTIONARY else {}


## A ramp's footprint: its from-to run on the ground, `width` wide.
static func _ramp(r: Dictionary) -> PackedVector2Array:
	var a := _xz(r.get("from", [0.0, 0.0, 0.0]))
	var b := _xz(r.get("to", [0.0, 0.0, 0.0]))
	var side := (b - a).normalized().orthogonal() * float(r.get("width", 0.0)) * 0.5
	return PackedVector2Array([a + side, b + side, b - side, a - side])


static func _xz(v: Variant) -> Vector2:
	var arr := v as Array
	return Vector2(float(arr[0]), float(arr[2]))


# --- The Shell Shrine ----------------------------------------------------------------------------


func _shrine(trial: Dictionary, metrics: Dictionary) -> void:
	var g: Dictionary = trial.get("room", {})
	var lay: Dictionary = trial.get("layout", {})
	var segments := int(metrics.get("circle_segments", OCTAGON))
	var half := float(g.get("hall_half_m", 0.0))
	var r := float(g.get("hall_r_m", 0.0))
	var hall := PackedVector2Array()
	var arc := maxi(segments / 2, 2)
	for i in arc + 1:  # the east end, north to south
		var a := PI * i / arc
		hall.append(Vector2(half + r * sin(a), -r * cos(a)))
	for i in arc + 1:  # the west end, south to north
		var a := PI * i / arc
		hall.append(Vector2(-half - r * sin(a), r * cos(a)))
	floors.append(hall)
	var door := _vec(lay.get("door", [0.0, 0.0]))
	var door_w := float(g.get("door_w", 0.0))
	var depth := float(g.get("exit_depth_m", 0.0)) + float(g.get("wall_t", 0.0))
	var out := door.normalized()
	var across := Vector2(-out.y, out.x) * door_w * 0.5
	var passage := PackedVector2Array(
		[door - across, door + out * depth - across, door + out * depth + across, door + across]
	)
	floors.append(passage)
	walls.append_array(_open_outline(hall, door, door_w * 0.5))
	walls.append(passage)
	var d: Array = g.get("door", [0.0, 0.0, 0.0])
	structures.append(footprint(door, [-float(d[0]) * 0.5, -float(d[2]) * 0.5, d[0], d[2]], 0.0, 1.0))
	var basin_r := float(g.get("basin_r", 0.0))
	for b: Variant in (trial.get("basins", {}) as Dictionary).keys():
		var c := disc(_vec(lay.get(str(b), [0.0, 0.0])), basin_r, segments)
		water.append(c)
		rims.append(c)
	var spout: Array = g.get("spring_spout", [0.0, 0.0])
	water.append(disc(_vec(lay.get("source", [0.0, 0.0])), float(spout[0]), segments))
	var pool_ap := float((g.get("pool", [0.0]) as Array)[0]) * 0.5
	var pool := _octagon(_vec(lay.get(str(trial.get("goal", "")), [0.0, 0.0])), pool_ap)
	water.append(pool)
	rims.append(_octagon(_vec(lay.get(str(trial.get("goal", "")), [0.0, 0.0])), pool_ap + float(g.get("rim_t", 0.0))))
	var side := disc(
		_vec(lay.get("side_pool", [0.0, 0.0])), float((g.get("side_pool", [0.0]) as Array)[0]) * 0.5, segments
	)
	water.append(side)
	rims.append(side)
	channel_width_m = float(g.get("channel_w", 0.0))
	_shrine_channels(trial, lay)


## An octagon with apothem `ap` whose faces look along the axes' 45-degree steps, as the inner
## pool's rim is built (ShellShrineLevel._build_inner_pool).
static func _octagon(at: Vector2, ap: float) -> PackedVector2Array:
	var out := PackedVector2Array()
	var corner := ap / cos(PI / OCTAGON)
	for i in OCTAGON:
		out.append(at + Vector2.from_angle(TAU * (i + 0.5) / OCTAGON) * corner)
	return out


## The troughs: the spring into its basin, and each basin to every basin, pool or sluice it can
## pour toward (spill grates lead nowhere and are left off). A trough used both ways is one line.
func _shrine_channels(trial: Dictionary, lay: Dictionary) -> void:
	var into := str(trial.get("source_into", ""))
	channels.append(PackedVector2Array([_vec(lay.get("source", [0.0, 0.0])), _vec(lay.get(into, [0.0, 0.0]))]))
	var seen := {}
	var basins: Dictionary = trial.get("basins", {})
	for b: Variant in basins.keys():
		for to: Variant in (basins[b] as Dictionary).get("outlets", []):
			var key := [str(b), str(to)]
			key.sort()
			if not lay.has(str(to)) or seen.has(str(key)):
				continue
			seen[str(key)] = true
			channels.append(PackedVector2Array([_vec(lay[str(b)]), _vec(lay[str(to)])]))


## The closed outline `loop` as open polylines, leaving out every stretch within `gap` of `at`.
static func _open_outline(loop: PackedVector2Array, at: Vector2, gap: float) -> Array[PackedVector2Array]:
	var out: Array[PackedVector2Array] = []
	var cur := PackedVector2Array()
	for i in loop.size() + 1:
		var p := loop[i % loop.size()]
		if p.distance_to(at) < gap:
			if cur.size() >= 2:
				out.append(cur)
			cur = PackedVector2Array()
			continue
		cur.append(p)
	if cur.size() >= 2:
		out.append(cur)
	return out
