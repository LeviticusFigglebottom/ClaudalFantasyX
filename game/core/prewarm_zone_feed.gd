class_name PrewarmZoneFeed
extends RefCounted
## ADR 0111 amendment 4 (registry "zone_loads"): a transition's prewarm also stages the zone's runtime materials and
## scenes as ResidentLoads brings them in (ResidentLoads.take_prewarm), so their pipelines compile under the cover,
## not in the zone's first frames. A zone's dressing, villagers and wildlife build at runtime, so ShaderPrewarm's own
## scene scan never sees them (the PC's pass 3: the zones with 295-357 materials stayed over 1 s; under 260, under).
## A scene is staged by its SceneState (its meshes and materials), a material as a registry entry on the quad.

var staged := 0
var _loads: ResidentLoads
var _seen := {}
var _per_frame := 1


## The feed for a transition to `for_scene`, or null when the registry turns it off, the run is a boot run, or no
## ResidentLoads is installed.
static func for_transition(config: Dictionary, for_scene: String, boot_run: bool) -> PrewarmZoneFeed:
	var loads := ResidentLoads.shared()
	if not bool(config.get("zone_loads", false)) or boot_run or for_scene == "" or loads == null:
		return null
	var feed := PrewarmZoneFeed.new()
	feed._loads = loads
	feed._per_frame = maxi(int(config.get("zone_loads_per_frame", 1)), 1)
	return feed


## Moves up to a frame's worth of the zone's loaded resources into `prewarm`'s pending draws. Returns how many.
func pull(prewarm: ShaderPrewarm, cap: int) -> int:
	var counter := [0]
	for res in _loads.take_prewarm(_per_frame):
		if res is PackedScene:
			prewarm._harvest_state((res as PackedScene).get_state(), {}, _seen, cap, counter, 0)
		elif res is Material and not _seen.has(res):
			_seen[res] = true
			prewarm._pending.append({"path": res.resource_path})
			counter[0] = int(counter[0]) + 1
	return int(counter[0])


## True while a zone load is still coming in or a loaded one waits to be staged.
func pending() -> bool:
	return is_instance_valid(_loads) and _loads.prewarm_pending()


func per_frame() -> int:
	return _per_frame
