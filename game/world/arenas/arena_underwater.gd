class_name ArenaUnderwater
extends UnderwaterRig
## The underwater look for an arena fought under the sea (M3-ENV-06 `underway_tower`; docs/kb/tech/battle_arenas.md
## "The underwater arena"). It is the Rendering stream's UnderwaterRig (M2-RND-02, M2-RND-09) with one addition the
## rig does not have yet: `light_scale`, a fixed scale on the in-scatter's light level, because the rig lights its
## water with the scene's sun and no occlusion, so inside a building the water would glow like the open sea and drown
## Rhen's lantern (oruvel_underway.md §0, the `ch01_underway_int` sub-frame: 0.33). It never writes the rig's shared
## data cache (UnderwaterRig.load_data); it scales the level the rig computes. A stand-in for the per-area scale
## requested of Rendering in M3-RND-24; M3-RND-25 asks for the arena's whole look under the battle camera. Remove this
## class (the arena points at UnderwaterRig) once the rig carries the scale itself.

## The in-scatter's light level is the rig's (the scene's daylight over the data's light_reference) times this:
## 1.0 in the open, 0.33 inside the drowned tower's galleries, 0.2 in its deep rooms (oruvel_underway.md §0).
@export_range(0.01, 1.0, 0.01) var light_scale: float = 1.0


func light_level() -> float:
	var optics := data.get("optics", {}) as Dictionary
	return maxf(super.light_level() * light_scale, float(optics.get("light_floor", 0.0)))
