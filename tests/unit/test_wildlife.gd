extends TestCase
## M3-CRE-611 (and M3-CRE-616, the insects): the ambient wildlife (game/world/wildlife/,
## docs/kb/art/wildlife.md). The simulations are headless RefCounted classes stepped with fixed deltas; the layer
## is built off the tree (no camera, so every group is active) from the review stage's data and from each zone file.

const DT := 1.0 / 60.0
const STAGE_DATA := "res://game/levels/_tests/wildlife/wildlife_stage.json"
const ZONE_DIR := "res://game/data/world/wildlife/"
const KINDS_FILE := "wildlife.json"
## Hermite approach and take-off curves may swing a little wide of the orbit; the flock stays within this.
const FLOCK_SLACK := 1.25
const EPS := 1e-3

var _kinds: Dictionary = {}


func before_each() -> void:
	_kinds = WildlifeConfig.load_kinds()


func _layer(path: String, zone_id: StringName = &"") -> WildlifeLayer:
	var layer := WildlifeLayer.new()
	layer.data_path = path
	layer.zone_id = zone_id
	layer.build()
	return layer


func _snapshot(layer: WildlifeLayer) -> Array[PackedFloat32Array]:
	var out: Array[PackedFloat32Array] = []
	for key: StringName in [
		WildlifeLayer.GULLS_FLYING,
		WildlifeLayer.GULLS_PERCHED,
		WildlifeLayer.CRABS,
		WildlifeLayer.FISH,
		WildlifeLayer.MOTHS,
		WildlifeLayer.DRAGONFLIES
	]:
		out.append((layer.buffers[key] as WildlifeBuffer).data.duplicate())
	return out


## A player that walks a slow loop through the stage, so the crabs and the shoal react.
func _player_at(frame: int) -> Vector3:
	var t := frame * DT * 0.4
	return Vector3(-0.5 + 1.5 * cos(t), 0.0, 1.0 + 1.2 * sin(t))


func test_same_seed_same_positions_after_n_frames() -> void:
	var a := _layer(STAGE_DATA)
	var b := _layer(STAGE_DATA)
	for f in 900:
		a.step(DT, _player_at(f), true)
		b.step(DT, _player_at(f), true)
	var sa := _snapshot(a)
	var sb := _snapshot(b)
	for k in sa.size():
		assert_eq(sa[k], sb[k], "buffer %d identical after 900 frames" % k)
	var c := _layer(STAGE_DATA, &"_tests/another_seed")
	for f in 900:
		c.step(DT, _player_at(f), true)
	assert_ne(_snapshot(c)[3], sa[3], "another zone id seeds other choices")
	assert_ne(_snapshot(c)[4], sa[4], "the moths too")
	assert_true(a.insect_count() > 0, "the stage has insects")
	a.free()
	b.free()
	c.free()


func _flock_row(perched_at_start: int) -> Dictionary:
	return {
		"id": "t",
		"center": [10.0, -5.0],
		"radius_m": 20.0,
		"altitude_m": [6.0, 12.0],
		"count": 5,
		"perched_at_start": perched_at_start,
		"perches": [[0.0, 2.0, -5.0, 90.0], [14.0, 3.0, 4.0, 0.0], [20.0, 2.5, -15.0, 180.0]]
	}


func test_gulls_stay_in_their_flock_bounds_and_land_on_perches() -> void:
	var kind: Dictionary = _kinds["kinds"]["gull"]
	var flock := WildlifeGullFlock.new(_flock_row(0), kind, 1234, 5)
	var landed := 0
	var took_off := false
	var was_perched: Array[bool] = []
	was_perched.resize(flock.count())
	var max_r := 0.0
	var lo := INF
	var hi := -INF
	for f in 60 * 240:
		flock.step(DT)
		var used := {}
		for i in flock.count():
			var g := flock.gulls[i]
			var h := Vector2(g.pos.x - flock.center.x, g.pos.z - flock.center.z).length()
			max_r = maxf(max_r, h)
			lo = minf(lo, g.pos.y)
			hi = maxf(hi, g.pos.y)
			var perched := g.state == WildlifeGullFlock.State.PERCHED
			if perched:
				var p := flock.perches[g.perch]
				assert_true(g.pos.distance_to(Vector3(p.x, p.y, p.z)) < EPS, "a perched gull stands on its perch")
				assert_false(used.has(g.perch), "one gull per perch")
				used[g.perch] = true
				if not was_perched[i]:
					landed += 1
			elif was_perched[i]:
				took_off = true
			was_perched[i] = perched
	assert_true(landed > 0, "gulls land on perches (%d landings in 4 min)" % landed)
	assert_true(took_off, "and take off again")
	assert_between(max_r, 0.0, flock.radius * FLOCK_SLACK, "horizontal distance from the flock centre")
	var und := float(kind["undulate_m"])
	assert_between(lo, 2.0 - EPS, 12.0 + und, "lowest point is a perch")
	assert_between(hi, 2.0, flock.altitude.y + und + float(kind["takeoff_lift_m"]), "highest point")


func test_gulls_can_start_perched_and_face_their_perch() -> void:
	var kind: Dictionary = _kinds["kinds"]["gull"]
	var flock := WildlifeGullFlock.new(_flock_row(2), kind, 99, 5)
	assert_eq(flock.perched_count(), 2, "two start on perches")
	var xf := flock.transform_of(flock.gulls[0])
	assert_true(xf.basis.z.normalized().is_equal_approx(Vector3(1.0, 0.0, 0.0)), "yaw 90 faces +x (the sea)")
	var fly := WildlifeBuffer.new(5)
	var sit := WildlifeBuffer.new(5)
	flock.write(fly, sit, 0)
	assert_true(sit.visible(0) and not fly.visible(0), "a perched bird draws only in the perched MultiMesh")
	assert_true(fly.visible(4) and not sit.visible(4), "a flying bird only in the flying one")


func _beach_row() -> Dictionary:
	return {"id": "t", "center": [0.0, 0.0], "half_extents": [6.0, 4.0], "yaw_deg": 20.0, "y": 0.3, "count": 6}


func test_crabs_flee_within_radius_and_return_home_later() -> void:
	var kind: Dictionary = _kinds["kinds"]["crab"]
	var beach := WildlifeCrabBeach.new(_beach_row(), kind, 77, 6, Callable())
	var c := beach.crabs[0]
	var home := c.home
	var flee_r := float(kind["flee_radius_m"])
	var start := Vector3(home.x + flee_r * 0.5, 0.0, home.y)
	beach.step(DT, start, true)
	assert_eq(c.state, WildlifeCrabBeach.State.FLEE, "a player inside flee_radius_m startles it")
	var d0 := c.pos.distance_to(Vector2(start.x, start.z))
	for f in 60 * 3:
		beach.step(DT, start, true)
		for k in beach.crabs:
			assert_true(beach.contains(k.pos, EPS), "crabs stay in their area")
	var d1 := c.pos.distance_to(Vector2(start.x, start.z))
	assert_true(d1 > d0 + 0.5, "it scuttled away (%.2f -> %.2f m)" % [d0, d1])
	assert_true(c.amp > 0.5 or c.state == WildlifeCrabBeach.State.WARY, "legs moving while it runs")
	var far := Vector3(100.0, 0.0, 100.0)
	for f in 60 * 40:
		beach.step(DT, far, true)
	var shuffle := float(kind["shuffle_m"]) * sqrt(2.0) + float(kind["arrive_m"])
	for k in beach.crabs:
		assert_true(k.pos.distance_to(k.home) <= shuffle, "every crab is back near home")
		assert_ne(k.state, WildlifeCrabBeach.State.FLEE, "and calm")
	assert_eq(c.y, 0.3, "flat area height without a ground callable")


func test_crabs_ignore_a_player_outside_the_radius_and_use_the_ground() -> void:
	var kind: Dictionary = _kinds["kinds"]["crab"]
	var ground := func(x: float, z: float) -> float: return 0.1 * x + 0.05 * z
	var beach := WildlifeCrabBeach.new(_beach_row(), kind, 5, 4, ground)
	var c := beach.crabs[1]
	var p := Vector3(c.pos.x + float(kind["flee_radius_m"]) + 0.5, 0.0, c.pos.y)
	for f in 30:
		beach.step(DT, p, true)
	assert_ne(c.state, WildlifeCrabBeach.State.FLEE, "outside flee_radius_m nothing happens")
	assert_true(absf(c.y - (0.1 * c.pos.x + 0.05 * c.pos.y)) < EPS, "stands on the ground callable")


## The Act I audit (2026-10-29): `"ground": {"physics": true}` makes crabs follow the zone's collision. It resolves to
## the layer's ray-cast ground, and a ground that cannot answer yet (NAN: the collision not in the physics space in
## the first frames) leaves a crab at its area's flat y instead of NAN.
func test_a_physics_ground_resolves_and_falls_back_to_the_flat_y() -> void:
	var layer := WildlifeLayer.new()
	var g: Callable = layer.call(&"_resolve_ground", {"physics": true})
	assert_true(g.is_valid(), "a physics ground is a callable")
	assert_true(is_nan(float(g.call(0.0, 0.0))), "off the tree it cannot answer yet")
	var kind: Dictionary = _kinds["kinds"]["crab"]
	var beach := WildlifeCrabBeach.new(_beach_row(), kind, 9, 3, func(_x: float, _z: float) -> float: return NAN)
	for c in beach.crabs:
		assert_eq(c.y, 0.3, "a crab keeps its flat y while the ground cannot answer")
	layer.free()


func test_the_party_flushes_perched_gulls_one_after_another() -> void:
	var kind: Dictionary = _kinds["kinds"]["gull"]
	var calm := WildlifeGullFlock.new(_flock_row(2), kind, 99, 5)
	var flushed := WildlifeGullFlock.new(_flock_row(2), kind, 99, 5)
	var near := flushed.gulls[0]
	var far := flushed.gulls[1]
	var flushed_perch := near.perch  # the bird takes another perch later
	var at := flushed.perches[flushed_perch]
	var player := Vector3(at.x + 2.0, 0.0, at.z)
	assert_true(
		(
			Vector2(at.x, at.z).distance_to(Vector2(flushed.perches[far.perch].x, flushed.perches[far.perch].z))
			> float(kind["flush_radius_m"]) + 2.0
		),
		"the fixture's other perch is out of reach"
	)
	var lifted_at := -1.0
	for f in 90:
		calm.step(DT, player, false)
		flushed.step(DT, player, true)
		if lifted_at < 0.0 and near.state != WildlifeGullFlock.State.PERCHED:
			lifted_at = f * DT
	var delay: Array = kind["flush_delay_s"]
	assert_between(lifted_at, 0.0, float(delay[1]) + DT, "the party lifts the near gull within its flush delay")
	assert_eq(far.state, WildlifeGullFlock.State.PERCHED, "a gull on a far perch stays put")
	assert_eq(calm.perched_count(), 2, "with nobody there, both keep their perches")
	for f in 60 * 120:
		flushed.step(DT, player, true)
		for g in flushed.gulls:
			if g.state == WildlifeGullFlock.State.PERCHED:
				assert_ne(g.perch, flushed_perch, "nothing lands on the perch the party stands by")


func test_a_startle_throws_the_school_apart() -> void:
	var kind: Dictionary = _kinds["kinds"]["fish"]
	var row := {"id": "t", "center": [3.0, -0.3, 2.0], "radius_m": 6.0, "count": 14, "scale": 1.0}
	var calm := WildlifeShoal.new(row, kind, 31, 14, Callable())
	var startled := WildlifeShoal.new(row, kind, 31, 14, Callable())
	for f in 60 * 4:
		calm.step(DT, Vector3(80.0, 0.0, 80.0), true)
		startled.step(DT, Vector3(80.0, 0.0, 80.0), true)
	var at := startled.lead
	for f in 30:
		calm.step(DT, Vector3(80.0, 0.0, 80.0), true)
		startled.step(DT, at, f == 0)
	assert_true(startled.startled(), "the party startled one school")
	assert_true(_school_spread(startled) > 1.3 * _school_spread(calm), "the startled school spreads wider")
	for f in 60 * 12:
		calm.step(DT, Vector3(80.0, 0.0, 80.0), true)
		startled.step(DT, Vector3(80.0, 0.0, 80.0), true)
	assert_false(startled.startled(), "the startle passes")
	assert_true(_school_spread(startled) < 1.3 * _school_spread(calm), "and the school closes up again")


## The fish's mean distance from their own centroid (across the water).
func _school_spread(shoal: WildlifeShoal) -> float:
	var c := Vector3.ZERO
	for fish in shoal.fish:
		c += fish.pos
	c /= float(shoal.count())
	var d := 0.0
	for fish in shoal.fish:
		d += Vector2(fish.pos.x - c.x, fish.pos.z - c.z).length()
	return d / float(shoal.count())


func test_fish_count_and_bounds() -> void:
	var kind: Dictionary = _kinds["kinds"]["fish"]
	var row := {"id": "t", "center": [3.0, -0.3, 2.0], "radius_m": 3.0, "count": 14, "scale": 1.0}
	var shoal := WildlifeShoal.new(row, kind, 31, 14, Callable())
	assert_eq(shoal.count(), 14, "fish count")
	var spread := WildlifeConfig.vec3(kind["spread_m"]) * float(kind["scatter_spread"])  # a startle throws it apart
	var reach := shoal.radius + spread.length() + float(kind["wobble_m"]) + EPS
	var startled := false
	for f in 60 * 120:
		var p := Vector3(3.0 + 2.0 * cos(f * DT * 0.2), 0.0, 2.0) if f % 1200 < 300 else Vector3(50.0, 0.0, 50.0)
		shoal.step(DT, p, true)
		startled = startled or shoal.startled()
		for fish in shoal.fish:
			var h := Vector2(fish.pos.x - shoal.center.x, fish.pos.z - shoal.center.z).length()
			assert_true(h <= reach, "fish within the shoal's area (%.2f <= %.2f)" % [h, reach])
			assert_true(absf(fish.pos.y - shoal.center.y) <= spread.y + float(kind["wobble_m"]) + EPS, "depth band")
	assert_true(startled, "a wading player startles the shoal")
	var buf := WildlifeBuffer.new(14)
	shoal.write(buf, 0)
	assert_true(buf.visible(13), "every fish is drawn")


func _zone_files() -> PackedStringArray:
	var out := PackedStringArray()
	for f in DirAccess.get_files_at(ZONE_DIR):
		if f.ends_with(".json") and f != KINDS_FILE:
			out.append(f)
	return out


func test_the_layer_reads_each_zone_file_within_budget() -> void:
	var files := _zone_files()
	assert_true(files.size() >= 3, "Haluna, the causeway and Pemakar have wildlife files")
	var budgets: Dictionary = _kinds["budgets"]
	for f in files:
		var data := WildlifeConfig.load_json(ZONE_DIR + f)
		var zone_id := StringName(str(data["zone"]))
		assert_eq(WildlifeConfig.zone_path(zone_id), ZONE_DIR + f, "%s is named after its zone id" % f)
		var layer := _layer("", zone_id)
		var want := {"flocks": 0, "kingfishers": 0, "beaches": 0, "shoals": 0, "rays": 0, "swarms": 0, "herds": 0}
		for key: String in want:
			for row: Dictionary in data.get(key, []):
				want[key] += int(row["count"])
		assert_eq(layer.gull_count(), want["flocks"], "%s gulls" % f)
		assert_eq(layer.kingfisher_count(), want["kingfishers"], "%s kingfishers" % f)
		assert_true(layer.kingfisher_count() <= int(budgets["kingfishers"]), "%s kingfisher budget" % f)
		assert_eq(layer.crab_count(), want["beaches"], "%s crabs" % f)
		assert_eq(layer.fish_count(), want["shoals"], "%s fish" % f)
		assert_eq(layer.ray_count(), want["rays"], "%s rays" % f)
		assert_eq(layer.woolback_count(), want["herds"], "%s woolbacks" % f)
		assert_eq(layer.insect_count(), want["swarms"], "%s insects" % f)
		assert_true(layer.insect_count() <= int(budgets["insects"]), "%s insect budget" % f)
		assert_true(layer.gull_count() <= int(budgets["gulls"]), "%s gull budget" % f)
		assert_true(layer.crab_count() <= int(budgets["crabs"]), "%s crab budget" % f)
		assert_true(layer.fish_count() <= int(budgets["fish"]), "%s fish budget" % f)
		assert_true(layer.draw_calls() <= int(budgets["draw_calls"]), "%s draw calls" % f)
		assert_eq(layer.multimeshes.size(), layer.draw_calls(), "%s one MultiMesh per drawn kind" % f)
		for f2 in 120:
			layer.step(DT, Vector3.ZERO, false)
		layer.free()


func test_counts_over_budget_are_clamped() -> void:
	var path := "user://wildlife_over_budget.json"
	var budgets: Dictionary = _kinds["budgets"]
	var data := {
		"zone": "_tests/over_budget",
		"flocks":
		[
			{
				"id": "a",
				"center": [0, 0],
				"radius_m": 10,
				"altitude_m": [5, 8],
				"count": int(budgets["gulls"]) + 5,
				"perches": []
			}
		],
		"beaches": [],
		"shoals":
		[
			{"id": "a", "center": [0, -0.3, 0], "radius_m": 3, "count": int(budgets["fish"]), "scale": 1.0},
			{"id": "b", "center": [9, -0.3, 0], "radius_m": 3, "count": 10, "scale": 1.0}
		]
	}
	var fa := FileAccess.open(path, FileAccess.WRITE)
	fa.store_string(JSON.stringify(data))
	fa.close()
	var layer := _layer(path)
	assert_eq(layer.gull_count(), int(budgets["gulls"]), "gulls clamped to the budget")
	assert_eq(layer.fish_count(), int(budgets["fish"]), "fish clamped across shoals")
	assert_eq(layer.shoals[1].count(), 0, "the later shoal gets what is left")
	assert_eq(layer.draw_calls(), 3, "gulls flying and perched, fish: no crabs, so no crab MultiMesh")
	layer.free()
	DirAccess.remove_absolute(path)


func test_buffers_feed_the_multimeshes() -> void:
	var layer := _layer(STAGE_DATA)
	layer.step(DT, Vector3.ZERO, false)
	for key: StringName in layer.multimeshes:
		var mm := (layer.multimeshes[key] as MultiMeshInstance3D).multimesh
		assert_eq(mm.instance_count, (layer.buffers[key] as WildlifeBuffer).count, "%s instances" % key)
		assert_true(mm.use_custom_data, "%s carries the motion in custom data" % key)
		assert_eq(mm.buffer.size(), mm.instance_count * WildlifeBuffer.FLOATS, "%s buffer layout" % key)
		var mmi := layer.multimeshes[key] as MultiMeshInstance3D
		var mat := mmi.material_override as ShaderMaterial
		assert_true(
			mat != null and mat.shader.resource_path == "res://game/world/wildlife/wildlife.gdshader",
			"%s material" % key
		)
	assert_eq(layer.find_children("*", "CollisionObject3D", true, false).size(), 0, "wildlife never blocks the player")
	layer.free()


func test_zone_seed_is_stable() -> void:
	assert_eq(WildlifeConfig.seed_for(&"ch02/haluna"), WildlifeConfig.seed_for(&"ch02/haluna"), "same id, same seed")
	assert_ne(
		WildlifeConfig.seed_for(&"ch02/haluna"), WildlifeConfig.seed_for(&"ch03/saltgrass_causeway"), "ids differ"
	)
	assert_eq(WildlifeConfig.seed_for(&""), WildlifeConfig.FNV_OFFSET, "FNV-1a offset basis for the empty id")


func _swarm_row(swarm_type: String, perches: Array = []) -> Dictionary:
	return {"id": "t", "type": swarm_type, "center": [4.0, 2.2, -3.0], "radius_m": 1.5, "count": 5, "perches": perches}


func test_moths_loop_round_their_lamp_and_ignore_the_player() -> void:
	var kind: Dictionary = _kinds["kinds"]["insect"]
	var a := WildlifeSwarm.new(_swarm_row("moth"), kind, 616, 5)
	var b := WildlifeSwarm.new(_swarm_row("moth"), kind, 616, 5)
	var h := float(kind["moth"]["height_m"])
	var lo := INF
	var hi := -INF
	var travelled := 0.0
	for f in 60 * 60:
		var before := a.insects[0].pos
		a.step(DT, Vector3(4.0, 0.0, -3.0), true)  # right under the lamp
		b.step(DT, Vector3.ZERO, false)
		travelled += before.distance_to(a.insects[0].pos)
		for m in a.insects:
			var r := Vector2(m.pos.x - a.center.x, m.pos.z - a.center.z).length()
			assert_true(r <= a.radius + EPS, "a moth stays within the swarm's radius (%.3f)" % r)
			assert_true(absf(m.pos.y - a.center.y) <= h + EPS, "and its height band")
			lo = minf(lo, r)
			hi = maxf(hi, r)
	for i in a.count():
		assert_eq(a.insects[i].pos, b.insects[i].pos, "moths ignore the player")
	assert_true(hi - lo > 0.1, "the orbits jitter in and out (%.2f .. %.2f m)" % [lo, hi])
	assert_true(travelled > 10.0, "and keep flying (%.1f m in a minute)" % travelled)
	var buf := WildlifeBuffer.new(5)
	a.write(buf, 0)
	assert_true(buf.visible(4), "every moth is drawn")
	assert_eq(buf.data[14], WildlifeBuffer.MODE_FLUTTER, "with the wing flutter")


func test_dragonflies_hover_dart_and_perch_within_their_area() -> void:
	var kind: Dictionary = _kinds["kinds"]["insect"]
	var row := _swarm_row("dragonfly", [[4.5, 1.6, -2.5, 90.0], [3.2, 1.7, -3.4, 200.0]])
	var patrol := WildlifeSwarm.new(row, kind, 77, 4)
	var t: Dictionary = kind["dragonfly"]
	var slack := float(t["drift_m"]) * WildlifeSwarm.DRIFT_REACH + EPS
	var darts := 0
	var perched := 0
	var was: Array[int] = []
	was.resize(patrol.count())
	for f in 60 * 120:
		patrol.step(DT, Vector3(50.0, 0.0, 50.0), true)
		var used := {}
		for i in patrol.count():
			var d := patrol.insects[i]
			if d.state == WildlifeSwarm.State.PERCHED:
				var p := patrol.perches[d.perch]
				assert_true(d.pos.distance_to(Vector3(p.x, p.y, p.z)) < EPS, "a perched dragonfly sits on its perch")
				assert_false(used.has(d.perch), "one per perch")
				used[d.perch] = true
				if was[i] != WildlifeSwarm.State.PERCHED:
					perched += 1
			else:
				var r := Vector2(d.pos.x - patrol.center.x, d.pos.z - patrol.center.z).length()
				var near_perch := false
				for p in patrol.perches:
					near_perch = near_perch or d.pos.distance_to(Vector3(p.x, p.y, p.z)) < slack
				assert_true(r <= patrol.radius + slack, "within the radius (%.3f)" % r)
				assert_true(
					absf(d.pos.y - patrol.center.y) <= patrol.height + slack or d.state == WildlifeSwarm.State.DART,
					"within the height band while hovering"
				)
				if d.state == WildlifeSwarm.State.DART and was[i] != WildlifeSwarm.State.DART:
					darts += 1
			assert_true(patrol.bounds.grow(EPS).has_point(d.pos), "inside the swarm's bounds")
			was[i] = d.state
	assert_true(darts > 20, "they dart from hover to hover (%d darts in 2 min)" % darts)
	assert_true(perched > 0, "and settle on the perches (%d)" % perched)


func test_a_dragonfly_darts_away_from_the_player() -> void:
	var kind: Dictionary = _kinds["kinds"]["insect"]
	var patrol := WildlifeSwarm.new(_swarm_row("dragonfly"), kind, 5, 4)
	var d := patrol.insects[0]
	var flee_r := float(kind["dragonfly"]["flee_radius_m"])
	var player := Vector3(d.pos.x + flee_r * 0.4, 0.0, d.pos.z)
	var pp := Vector2(player.x, player.z)
	var d0 := Vector2(d.pos.x, d.pos.z).distance_to(pp)
	patrol.step(DT, player, true)
	assert_eq(d.state, WildlifeSwarm.State.DART, "a player inside flee_radius_m sends it off")
	for f in 60:
		patrol.step(DT, player, true)
	var d1 := Vector2(d.pos.x, d.pos.z).distance_to(pp)
	assert_true(d1 > d0 + 0.5, "it darted away (%.2f -> %.2f m)" % [d0, d1])
	var far := WildlifeSwarm.new(_swarm_row("dragonfly"), kind, 5, 4)
	far.step(DT, Vector3(50.0, 0.0, 50.0), true)
	assert_ne(far.insects[0].state, WildlifeSwarm.State.DART, "a far player changes nothing on the first frame")


func test_insects_are_clamped_to_their_budget_and_draw_in_two_multimeshes() -> void:
	var path := "user://wildlife_insects_over_budget.json"
	var budget := int(_kinds["budgets"]["insects"])
	var data := {
		"zone": "_tests/insects_over_budget",
		"swarms":
		[
			{"id": "a", "type": "moth", "center": [0, 2, 0], "radius_m": 1, "count": budget - 4},
			{"id": "b", "type": "dragonfly", "center": [6, 1, 0], "radius_m": 3, "count": 10}
		]
	}
	var fa := FileAccess.open(path, FileAccess.WRITE)
	fa.store_string(JSON.stringify(data))
	fa.close()
	var layer := _layer(path)
	assert_eq(layer.insect_count(), budget, "insects clamped to the budget")
	assert_eq(layer.insect_count(WildlifeSwarm.TYPE_DRAGONFLY), 4, "the later swarm gets what is left")
	assert_eq(layer.draw_calls(), 2, "moths and dragonflies: two MultiMeshes")
	assert_true(layer.draw_calls() <= int(_kinds["budgets"]["draw_calls"]), "within the draw-call budget")
	for key: StringName in [WildlifeLayer.MOTHS, WildlifeLayer.DRAGONFLIES]:
		var mmi := layer.multimeshes[key] as MultiMeshInstance3D
		assert_eq(mmi.cast_shadow, GeometryInstance3D.SHADOW_CASTING_SETTING_OFF, "%s cast no shadow" % key)
		var mat := mmi.material_override as ShaderMaterial
		assert_true(mat != null and mat.resource_path.ends_with("/%s.tres" % key), "%s material" % key)
	for f in 30:
		layer.step(DT, Vector3.ZERO, false)
	layer.free()
	DirAccess.remove_absolute(path)


func test_fireflies_orbit_low_and_blink_each_on_its_own_beat() -> void:
	var kind: Dictionary = _kinds["kinds"]["insect"]
	var ff: Dictionary = kind["firefly"]
	var a := WildlifeSwarm.new(_swarm_row("firefly"), kind, 1010, 5)
	var b := WildlifeSwarm.new(_swarm_row("firefly"), kind, 1010, 5)
	assert_true(a.is_firefly() and a.is_orbiter() and not a.is_moth(), "a firefly flies the moth's orbit")
	var floor_glow := float(ff["glow_floor"])
	var flashes := PackedInt32Array()
	flashes.resize(a.count())
	var lit := PackedByteArray()
	lit.resize(a.count())
	var together := 0
	for f in 60 * 30:
		a.step(DT, Vector3(4.0, 0.0, -3.0), true)
		b.step(DT, Vector3.ZERO, false)
		var on := 0
		for i in a.count():
			var m := a.insects[i]
			assert_true(m.glow >= floor_glow - EPS and m.glow <= 1.0 + EPS, "the lantern stays in its range")
			assert_true(absf(m.pos.y - a.center.y) <= float(ff["height_m"]) + EPS, "and the swarm's height band")
			var now := 1 if m.glow > 0.5 else 0
			if now == 1 and lit[i] == 0:
				flashes[i] += 1
			lit[i] = now
			on += now
		if on == a.count():
			together += 1
	for i in a.count():
		assert_eq(a.insects[i].glow, b.insects[i].glow, "deterministic: the same seed blinks the same")
		# 30 s at one flash every blink_s
		var lo := int(30.0 / float(ff["blink_s"][1])) - 1
		var hi := int(30.0 / float(ff["blink_s"][0])) + 1
		assert_true(flashes[i] >= lo and flashes[i] <= hi, "firefly %d flashed %d times" % [i, flashes[i]])
	assert_true(together < 30, "they do not all flash at once (%d frames)" % together)
	var buf := WildlifeBuffer.new(5)
	a.write(buf, 0)
	assert_eq(buf.data[14], WildlifeBuffer.MODE_GLOW, "the shader's glow mode")
	assert_true(is_equal_approx(buf.data[15], a.insects[0].glow), "carrying the blink (float32)")


func test_a_firefly_swarm_draws_in_its_own_multimesh() -> void:
	var path := "user://wildlife_fireflies.json"
	var data := {
		"zone": "_tests/fireflies",
		"swarms":
		[
			{"id": "a", "type": "moth", "center": [0, 2, 0], "radius_m": 1, "count": 4},
			{"id": "b", "type": "firefly", "center": [6, 0.6, 0], "radius_m": 3, "count": 8}
		]
	}
	var fa := FileAccess.open(path, FileAccess.WRITE)
	fa.store_string(JSON.stringify(data))
	fa.close()
	var layer := _layer(path)
	assert_eq(layer.insect_count(WildlifeSwarm.TYPE_FIREFLY), 8, "eight fireflies")
	assert_eq(layer.draw_calls(), 2, "moths and fireflies: two MultiMeshes")
	var mmi := layer.multimeshes[WildlifeLayer.FIREFLIES] as MultiMeshInstance3D
	var mat := mmi.material_override as ShaderMaterial
	assert_true(mat != null and mat.resource_path.ends_with("/firefly.tres"), "the firefly material")
	assert_true(float(mat.get_shader_parameter("glow_energy")) > 0.0, "whose lantern glows")
	for f in 30:
		layer.step(DT, Vector3.ZERO, false)
	var fb := layer.buffers[WildlifeLayer.FIREFLIES] as WildlifeBuffer
	assert_eq(fb.data[14], WildlifeBuffer.MODE_GLOW, "written in glow mode")
	assert_eq((layer.buffers[WildlifeLayer.MOTHS] as WildlifeBuffer).data[14], WildlifeBuffer.MODE_FLUTTER, "moths not")
	layer.free()
	DirAccess.remove_absolute(path)


func test_fen_kingfishers_fly_low_and_sit_on_the_rails() -> void:
	var layer := _layer("", &"ch10/ossa_fen")
	var data := WildlifeConfig.load_json(ZONE_DIR + "ch10_ossa_fen.json")
	assert_eq(layer.kingfisher_count(), 6, "three pairs")
	assert_eq(layer.gull_count(), 0, "and no gulls inland")
	for key: StringName in [WildlifeLayer.KINGFISHERS_FLYING, WildlifeLayer.KINGFISHERS_PERCHED]:
		var mmi := layer.multimeshes[key] as MultiMeshInstance3D
		assert_true(mmi != null and mmi.multimesh.mesh != null, "%s has its own mesh" % key)
		var mat := mmi.material_override as ShaderMaterial
		assert_true(
			mat != null and mat.resource_path.contains("/kingfisher/"), "%s wears the kingfisher's plumage" % key
		)
	var top := -INF
	var perched_seen := false
	for f in 60 * 60:
		layer.step(DT, Vector3.ZERO, false)
		for k in layer.kingfishers.size():
			var row: Dictionary = (data["kingfishers"] as Array)[k]
			var alt: Array = row["altitude_m"]
			var flock := layer.kingfishers[k]
			for b in flock.gulls:
				top = maxf(top, b.pos.y)
				assert_true(b.pos.y <= float(alt[1]) + float(_kinds["kinds"]["kingfisher"]["undulate_m"]) + EPS, "low")
		perched_seen = perched_seen or (layer.kingfishers[0].perched_count() > 0)
	assert_true(perched_seen, "they sit on the rails")
	assert_true(top < 2.5, "never higher than a person (%.2f m)" % top)
	layer.free()


## fen_kingfisher.md: "it perches long, and plunges". A kingfisher on a row with `water_y` leaves its perch now and then
## in a dive: down to the water ahead (never under it), a moment there, and back to the same perch, which no other bird
## takes meanwhile; a gull (no dive_chance) never dives.
func test_a_kingfisher_plunges_to_the_water_and_back_to_its_perch() -> void:
	var kind: Dictionary = _kinds["kinds"]["kingfisher"]
	var row := {
		"id": "k",
		"center": [0.0, 0.0],
		"radius_m": 6.0,
		"altitude_m": [0.6, 1.6],
		"count": 1,
		"perched_at_start": 1,
		"perches": [[2.0, 0.5, 0.0, 90.0]],
		"water_y": -0.25
	}
	var flock := WildlifeGullFlock.new(row, kind, 4242, 1)
	var bird := flock.gulls[0]
	var dives := 0
	var returns := 0
	var lowest := INF
	var last := bird.state
	for f in 60 * 300:
		flock.step(DT)
		lowest = minf(lowest, bird.pos.y)
		if bird.state == WildlifeGullFlock.State.DIVE and last != WildlifeGullFlock.State.DIVE:
			dives += 1
			assert_eq(bird.perch, 0, "it keeps its perch while it dives")
		if last == WildlifeGullFlock.State.APPROACH and bird.state == WildlifeGullFlock.State.PERCHED:
			assert_true(bird.pos.is_equal_approx(Vector3(2.0, 0.5, 0.0)), "back on its own perch")
			returns += 1
		last = bird.state
	assert_true(dives >= 2, "it plunges, more than once in five minutes (%d)" % dives)
	assert_true(returns >= dives - 1, "and comes back up each time")
	assert_true(absf(lowest - (-0.25)) < 0.05, "down to the water, not under it (%.3f)" % lowest)
	var gull_row := row.duplicate(true)
	var gulls := WildlifeGullFlock.new(gull_row, _kinds["kinds"]["gull"], 4242, 1)
	for f in 60 * 300:
		gulls.step(DT)
		assert_ne(gulls.gulls[0].state, WildlifeGullFlock.State.DIVE, "a gull never dives")
	assert_true(flock.bounds.position.y <= -0.25, "the culling box reaches the water")


## The idle pass (2026-10-30): each woolback grazes at its own pace (graze_pace), the graze clip's playback; the walk
## and the look play at 1.0 (the walk's hooves are planted for walk_speed_mps).
func test_woolbacks_graze_at_their_own_pace() -> void:
	var kind: Dictionary = _kinds["kinds"]["woolback"]
	var range: Array = kind["graze_pace"]
	var herd := WildlifeHerd.new(
		{"id": "h", "center": [0.0, 0.0], "radius_m": 4.0, "count": 4}, kind, 77, 4, Callable()
	)
	var paces: Array[float] = []
	for a in herd.animals:
		assert_between(a.pace, float(range[0]), float(range[1]), "its pace in range")
		paces.append(a.pace)
		a.clip = WildlifeHerd.CLIP_GRAZE
		assert_true(is_equal_approx(herd.playback_of(a), a.pace), "grazing plays at its pace")
		a.clip = WildlifeHerd.CLIP_WALK
		assert_eq(herd.playback_of(a), 1.0, "the walk keeps its planted hooves")
	assert_true(paces.max() - paces.min() > 0.02, "four woolbacks, four paces")


func test_woolbacks_graze_look_and_amble_within_their_area() -> void:
	var kind: Dictionary = _kinds["kinds"]["woolback"]
	var row := {"id": "h", "center": [2.0, -3.0], "radius_m": 3.0, "count": 3, "y": 0.5}
	var a := WildlifeHerd.new(row, kind, 1212, 3, Callable())
	var b := WildlifeHerd.new(row, kind, 1212, 3, Callable())
	var seen := {}
	var fastest := 0.0
	for f in 60 * 240:
		var before: Array[Vector2] = []
		for w in a.animals:
			before.append(w.pos)
		a.step(DT, Vector3(50.0, 0.0, 50.0), true)
		b.step(DT, Vector3.ZERO, false)
		for i in a.count():
			var w := a.animals[i]
			seen[w.state] = true
			fastest = maxf(fastest, before[i].distance_to(w.pos) / DT / w.scale)
			assert_true(w.pos.distance_to(a.center) <= a.radius + EPS, "a woolback stays in its area")
			assert_eq(w.y, 0.5, "on the row's ground")
	for i in a.count():
		assert_eq(a.animals[i].pos, b.animals[i].pos, "deterministic, and a player 50 m off changes nothing")
	assert_eq(seen.size(), 3, "it grazes, looks round and ambles")
	assert_true(
		fastest <= float(kind["walk_speed_mps"]) + EPS, "never faster than the walk clip's hooves (%.3f)" % fastest
	)


func test_a_close_player_makes_a_grazing_woolback_look_up() -> void:
	var kind: Dictionary = _kinds["kinds"]["woolback"]
	var row := {"id": "h", "center": [0.0, 0.0], "radius_m": 2.0, "count": 1}
	var h := WildlifeHerd.new(row, kind, 77, 1, Callable())
	var w := h.animals[0]
	w.timer = 1e6  # it would graze on
	var looked := false
	for f in 60 * 20:
		h.step(DT, Vector3(w.pos.x + 1.0, 0.0, w.pos.y), true)
		looked = looked or w.state == WildlifeHerd.State.LOOK
	assert_true(looked, "it looks up at the player")


func test_keth_pass_woolbacks_are_skinned_actors_playing_their_clips() -> void:
	var layer := _layer("", &"ch12/keth_pass")
	assert_eq(layer.woolback_count(), 5, "a pair at the foot, three on the saddle")
	var root := layer.get_node(NodePath(WildlifeLayer.HERDS))
	assert_eq(root.get_child_count(), 5, "one actor each")
	assert_eq(layer.draw_calls(), 0, "no MultiMesh")
	for f in 10:
		layer.step(DT, Vector3.ZERO, false)
	for h in layer.herds.size():
		for i in layer.herds[h].count():
			var actor := layer.herd_actors[h][i] as Node3D
			var ap := layer.herd_players[h][i] as AnimationPlayer
			assert_true(ap.is_playing(), "%s plays a clip" % actor.name)
			assert_eq(str(ap.current_animation), str(layer.herds[h].animals[i].clip), "the one its herd names")
			assert_true(actor.position.is_equal_approx(layer.herds[h].transform_of(layer.herds[h].animals[i]).origin))
	layer.free()


func test_rim_rays_glide_flat_over_the_sand_and_beat_their_fins() -> void:
	var layer := _layer("", &"ch16/pale_rim")
	assert_eq(layer.ray_count(), 16, "three loose groups")
	var mmi := layer.multimeshes[WildlifeLayer.RAYS] as MultiMeshInstance3D
	assert_true((mmi.material_override as ShaderMaterial).resource_path.ends_with("/rim_ray/materials/skin.tres"))
	assert_eq(mmi.cast_shadow, GeometryInstance3D.SHADOW_CASTING_SETTING_ON, "their shadows carry them")
	var start: Array[Vector3] = []
	for r in layer.rays[0].fish:
		start.append(r.pos)
	for f in 60 * 30:
		layer.step(DT, Vector3(0.0, 0.0, 60.0), true)
		for s in layer.rays:
			for r in s.fish:
				assert_true(absf(r.pos.y - 0.04) < EPS, "flat in a hand of water (%.3f)" % r.pos.y)
	assert_true(layer.rays[0].fish[0].pos.distance_to(start[0]) > 0.2, "always moving")
	var buf := layer.buffers[WildlifeLayer.RAYS] as WildlifeBuffer
	assert_eq(buf.data[14], WildlifeBuffer.MODE_FLAP, "the fins beat (the shader's flap)")
	assert_eq((layer.buffers[WildlifeLayer.FISH] as WildlifeBuffer).count, 0, "and no fish here")
	layer.free()
