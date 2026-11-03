class_name ArenaRainWet
extends Node
## The storm arenas (the human's FAST-TRACK 11-03; env-art-b): the arena's ground and kit soaked by the rain. On ready
## (after KitSlotSwaps, which stands before it), every surface under the parent outside `skip` takes a wet copy of
## its material, made once per source material and shared within the arena:
##   a weathering ShaderMaterial (any shader with a `rain_wet` uniform) gets `rain_wet` = amount and `rain_wall`;
##   a StandardMaterial3D darkens toward `standard_darken` and its roughness falls toward `standard_roughness`.
## The sources are never edited, so the zones that share the kit stay dry.

const RAIN_WET := &"rain_wet"
const RAIN_WALL := &"rain_wall"

## How soaked the up-facing faces are (0 dry .. 1 sheeted).
@export_range(0.0, 1.0, 0.01) var amount: float = 0.8
## How wet the walls read relative to the floors (streaks).
@export_range(0.0, 1.0, 0.01) var wall: float = 0.55
## StandardMaterial3D: albedo multiplier at amount 1.
@export_range(0.0, 1.0, 0.01) var standard_darken: float = 0.75
## StandardMaterial3D: roughness at amount 1.
@export_range(0.0, 1.0, 0.01) var standard_roughness: float = 0.2
## Children of the parent left dry (the sea and the storm draw their own water).
@export var skip: Array[StringName] = [&"Sea", &"Undertow"]

var _copies: Dictionary = {}  ## source Material -> its wet copy (or the source when it takes no wetting)


func _ready() -> void:
	var root := get_parent()
	if root == null or amount <= 0.0:
		return
	for c in root.get_children():
		if StringName(c.name) in skip:
			continue
		_soak(c)


## Source material -> its wet copy, for every material wetted (for tests and reviews).
func wet_pairs() -> Dictionary:
	var out := {}
	for src: Material in _copies:
		if _copies[src] != src:
			out[src] = _copies[src]
	return out


## The number of distinct source materials wetted (for tests).
func wetted_count() -> int:
	var n := 0
	for src: Material in _copies:
		if _copies[src] != src:
			n += 1
	return n


func _soak(node: Node) -> void:
	var mi := node as MeshInstance3D
	if mi != null and mi.mesh != null:
		if mi.material_override != null:
			mi.material_override = wet_copy(mi.material_override)
		else:
			for i in mi.mesh.get_surface_count():
				var m := mi.get_active_material(i)
				if m != null:
					var w := wet_copy(m)
					if w != m:
						mi.set_surface_override_material(i, w)
	for c in node.get_children():
		_soak(c)


## The wet copy of `src` (itself when it takes no wetting).
func wet_copy(src: Material) -> Material:
	if _copies.has(src):
		return _copies[src]
	var out: Material = src
	var sm := src as ShaderMaterial
	var std := src as StandardMaterial3D
	if sm != null and sm.shader != null and _has_uniform(sm.shader, RAIN_WET):
		var w := sm.duplicate() as ShaderMaterial
		w.set_shader_parameter(RAIN_WET, amount)
		w.set_shader_parameter(RAIN_WALL, wall)
		out = w
	elif std != null and std.transparency == BaseMaterial3D.TRANSPARENCY_DISABLED:
		var w := std.duplicate() as StandardMaterial3D
		var k := lerpf(1.0, standard_darken, amount)
		w.albedo_color = Color(
			std.albedo_color.r * k, std.albedo_color.g * k, std.albedo_color.b * k, std.albedo_color.a
		)
		w.roughness = lerpf(std.roughness, standard_roughness, amount)
		out = w
	_copies[src] = out
	return out


static func _has_uniform(shader: Shader, uniform: StringName) -> bool:
	for u: Dictionary in shader.get_shader_uniform_list():
		if StringName(str(u.get("name", ""))) == uniform:
			return true
	return false
