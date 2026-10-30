class_name KerridBurnGlow
extends RefCounted
## Kerrid's rope-burn light (M4-A2P-054; kerrid.md §3 and §9). His GLB carries the `Burns` shell (the burns' emission
## mask, material `burn_glow`, energy 0 by default: nothing shows in Ch5-Ch9) and the VFX sockets (`VFX-burn_<side>_<n>`
## on the forearms, `VFX-palm_<side>` on the hands) where M4-A2P-049's motes leave him. Scene owners call `apply` with
## the scene's glow (0..1, game/data/characters/kerrid_glow.json: `from_ch10` in dim scenes, up to `ch15_peak`) and,
## at H09, a `lift` from 0 to 1 over `lift_seconds` (color_script rule 1: held cyan to released gold). Each Burns
## mesh gets its own copy of the material the first time, so one Kerrid's light never changes another's.

const DATA_PATH := "res://game/data/characters/kerrid_glow.json"

static var _data: Dictionary = {}


## The kerrid_glow.json table (read once).
static func data() -> Dictionary:
	if _data.is_empty():
		var f := FileAccess.open(DATA_PATH, FileAccess.READ)
		if f != null:
			_data = JSON.parse_string(f.get_as_text()) as Dictionary
	return _data


## Sets the burns' light under `root` (a Kerrid model, or any scene holding one): `glow` 0..1 (clamped) and `lift` 0..1
## (held cyan to released gold). Returns how many Burns meshes it lit (1 for one Kerrid, 0 when there is none).
static func apply(root: Node, glow: float, lift: float = 0.0) -> int:
	var d := data()
	var energy := clampf(glow, 0.0, 1.0) * float(d.get("energy_per_unit", 0.0))
	var colour := Color(str(d.get("held", "#7FC6D9"))).lerp(
		Color(str(d.get("lift", "#FFE9B8"))), clampf(lift, 0.0, 1.0)
	)
	var found := 0
	for node: Node in root.find_children(str(d.get("shell", "Burns")), "MeshInstance3D", true, false):
		var mesh := node as MeshInstance3D
		var mat := mesh.get_surface_override_material(0) as StandardMaterial3D
		if mat == null or not mat.has_meta(&"kerrid_burn_glow"):
			var base := mesh.get_active_material(0) as StandardMaterial3D
			if base == null:
				continue
			mat = base.duplicate() as StandardMaterial3D
			mat.set_meta(&"kerrid_burn_glow", true)
			mesh.set_surface_override_material(0, mat)
		mat.emission = colour
		mat.emission_energy_multiplier = energy
		found += 1
	return found


## The VFX sockets under `root` (empties on the forearm and hand bones), for the motes' emitters.
static func sockets(root: Node) -> Array[Node3D]:
	var out: Array[Node3D] = []
	var prefix := str(data().get("socket_prefix", "VFX-"))
	for node: Node in root.find_children(prefix + "*", "Node3D", true, false):
		out.append(node as Node3D)
	return out
