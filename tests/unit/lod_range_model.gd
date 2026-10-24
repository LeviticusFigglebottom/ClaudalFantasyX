extends RefCounted
## A model of Godot 4.6's visibility-range culling for LOD chains (M1-ENV-08/09/10), shared by the LOD
## tests (test_vegetation_plant, test_haluna_dresser_lod, test_post_import). Preload it; it is not a
## test file (the runner only discovers test_*.gd).

## A sweep's first distance and its step (m).
const SWEEP_START_M := 0.5
const SWEEP_STEP_M := 0.25


## Godot 4.6's visibility-range check (RendererSceneCull::_visibility_range_check), as
## game/levels/_tests/vegetation/lod_sweep_probe.gd measured it under lavapipe. -1 too far, 1 too close,
## 0 drawn, 2 drawn while fading (it also hands the instance's visibility children through).
## FADE_DISABLED margins are hysteresis: they widen the range of an instance that was drawn last frame
## and narrow it for one that was not. `seen` holds each instance's last state.
static func range_check(mi: MeshInstance3D, dist: float, seen: Dictionary) -> int:
	var begin_off := -mi.visibility_range_begin_margin
	var end_off := mi.visibility_range_end_margin
	var hard := mi.visibility_range_fade_mode == GeometryInstance3D.VISIBILITY_RANGE_FADE_DISABLED
	if hard and not bool(seen.get(mi, false)):
		begin_off = -begin_off
		end_off = -end_off
	if mi.visibility_range_end > 0.0 and dist > mi.visibility_range_end + end_off:
		seen[mi] = false
		return -1
	if mi.visibility_range_begin > 0.0 and dist < mi.visibility_range_begin + begin_off:
		seen[mi] = false
		return 1
	seen[mi] = true
	if not hard:
		if mi.visibility_range_end > 0.0 and dist > mi.visibility_range_end - end_off:
			return 2
		if mi.visibility_range_begin > 0.0 and dist < mi.visibility_range_begin - begin_off:
			return 2
	return 0


## One culling pass at `dist` over `chain` (chain[i] is LOD i), parents first (Godot culls by
## dependency depth): per LOD, 0 hidden, 1 drawn opaque, 2 drawn fading. A child is culled unchecked
## unless its visibility parent was too close or fading.
static func draws(chain: Array[MeshInstance3D], dist: float, seen: Dictionary) -> Array[int]:
	var drawn: Array[int] = []
	drawn.resize(chain.size())
	var result := {}
	for i in range(chain.size() - 1, -1, -1):
		var mi := chain[i]
		var parent := mi.get_node_or_null(mi.visibility_parent) as MeshInstance3D
		if parent != null and not int(result.get(parent, -1)) in [1, 2]:
			result[mi] = -1
			continue
		result[mi] = range_check(mi, dist, seen)
		drawn[i] = {0: 1, 2: 2}.get(result[mi], 0)
	return drawn


## Distances from SWEEP_START_M up to (not including) `to_m`, SWEEP_STEP_M apart.
static func distances(to_m: float) -> Array[float]:
	var out: Array[float] = []
	var d := SWEEP_START_M
	while d < to_m:
		out.append(d)
		d += SWEEP_STEP_M
	return out


## For a hard (unfaded) chain: every step of `dists` that does not draw exactly one LOD opaque, from a
## still camera (fresh state at each step), sweeping in and sweeping out. Empty means no hole and no
## double draw.
static func hard_sweep_failures(chain: Array[MeshInstance3D], dists: Array[float]) -> Array[String]:
	var bad: Array[String] = []
	var reversed := dists.duplicate()
	reversed.reverse()
	for history: String in ["still", "in", "out"]:
		var seen := {}
		var sweep: Array = reversed if history == "in" else dists
		for x: float in sweep:
			if history == "still":
				seen = {}
			var drawn := draws(chain, x, seen)
			if drawn.count(1) != 1 or drawn.has(2):
				bad.append("%s %.2f m: %s" % [history, x, drawn])
	return bad
