class_name LodChain
extends RefCounted
## Visibility-range LOD chains (M1-ENV-08/09/10), shared by VegetationPlant, HalunaDresser and the
## import rules (AssetImportRules). Each LOD is the `visibility_parent` child of the next LOD of its
## chain, and Godot draws a child only while its parent is hidden for being too close. So each switch
## is one state machine, the parent's begin check, with the parent's begin margin as the hysteresis:
## exactly one LOD draws at every distance, whatever the camera did before (no hole, no double draw).
## docs/kb/art/environments/vegetation.md "One LOD at every distance". Static only, with no scene
## or autoload dependency, so the editor's post-import pass can call it.

## The default `<name><suffix>N` LOD suffix of the authored .glb meshes.
const SUFFIX := "-lod"


## The sibling `<base><suffix><lod>` of `mi`'s chain (a node may hold several chains), else null.
static func sibling(mi: MeshInstance3D, lod: int, suffix: String = SUFFIX) -> MeshInstance3D:
	if mi.get_parent() == null or suffix == "":
		return null
	var base := String(mi.name)
	var at := base.rfind(suffix)
	if at >= 0 and base.substr(at + suffix.length()).is_valid_int():
		base = base.substr(0, at)
	return mi.get_parent().get_node_or_null(NodePath("%s%s%d" % [base, suffix, lod])) as MeshInstance3D


## LOD `lod`'s visibility range: a Dictionary of begin, end, begin_margin, end_margin and fade (bool).
## `ends` holds each LOD's switch-out distance; `margin` is the hysteresis at each switch; `fade` > 0
## fades the last LOD out over its end +- fade. When `chained` (the chain has LOD lod+1), LOD lod is
## LOD lod+1's visibility child: it keeps no margins of its own, and its end is a loose bound halfway
## into the parent's span, which only matters while the parent hands its children through during its
## own fade. A faded last LOD fades in over its begin margin as well (Godot uses both margins as fade
## spans), which is a 2 x margin crossfade over the opaque LOD below it. Not `chained`: the plain
## switch interval, with no begin margin.
static func range_for(lod: int, ends: PackedFloat32Array, margin: float, fade: float, chained: bool) -> Dictionary:
	var last := ends.size() - 1
	var r := {
		"begin": 0.0 if lod == 0 else ends[lod - 1],
		"begin_margin": 0.0 if lod == 0 else margin,
		"end": ends[lod],
		"end_margin": 0.0,
		"fade": lod == last and fade > 0.0,
	}
	if lod == last:
		r["end_margin"] = fade if fade > 0.0 else margin
	elif chained:
		var parent_leaves := ends[lod + 1] - float(range_for(lod + 1, ends, margin, fade, true)["end_margin"])
		r["end"] = 0.5 * (ends[lod] + parent_leaves)
	else:
		r["begin_margin"] = 0.0
	return r


## Gives `mi` (LOD `lod` of a chain switching at `ends`) its range, and makes it the visibility child
## of `next` (LOD lod+1, or null at the chain's end). Clears any earlier visibility parent.
static func apply(
	mi: MeshInstance3D, lod: int, ends: PackedFloat32Array, margin: float, fade: float, next: MeshInstance3D
) -> void:
	var chained := next != null and lod + 1 < ends.size()
	var r := range_for(lod, ends, margin, fade, chained)
	mi.visibility_range_begin = r["begin"]
	mi.visibility_range_end = r["end"]
	mi.visibility_range_begin_margin = r["begin_margin"]
	mi.visibility_range_end_margin = r["end_margin"]
	mi.visibility_range_fade_mode = (
		GeometryInstance3D.VISIBILITY_RANGE_FADE_SELF
		if r["fade"]
		else GeometryInstance3D.VISIBILITY_RANGE_FADE_DISABLED
	)
	mi.visibility_parent = mi.get_path_to(next) if chained else NodePath()
