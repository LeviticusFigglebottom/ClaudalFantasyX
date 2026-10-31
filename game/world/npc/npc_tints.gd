class_name NpcTints
extends RefCounted
## Per-person colour on a shared villager body (M3-CRE-659, ADR 0152; docs/kb/tech/field_npc.md "Crowd"). A crowd
## body's cloth comes from one near-neutral atlas tinted by its `cloth_a`, `cloth_b` and `cloth_c` materials'
## `col_albedo`, and its hair by the `hair` material's `col_root` and `col_tip` (assets_src/characters/villagers/
## write_materials.py). apply() gives each such surface of an actor a per-instance override: a copy of the material
## it wears with the person's colour, so two people on one body dress apart. Copies are shared between people with
## the same colour on the same material (one resource per colour, not per person) while any of them lives.

## Material slot (its glTF name, the material's resource_name) -> the shader parameters its colour sets.
const SLOT_PARAMS := {
	&"cloth_a": [&"col_albedo"],
	&"cloth_b": [&"col_albedo"],
	&"cloth_c": [&"col_albedo"],
	&"hair": [&"col_root", &"col_tip"],
}

## key -> WeakRef to the shared copy. Weak (PC row 85): the people's meshes own the copies and free them with
## themselves, so no tinted material outlives the bodies it was set on (a static cache holding them till the script
## unloads frees them after the scene, at shutdown).
static var _cache: Dictionary = {}


## Tints every tintable surface under `actor`; `tints` maps a slot name to a colour (a Color or "#RRGGBB").
## Returns how many surfaces it changed.
static func apply(actor: Node, tints: Dictionary) -> int:
	if actor == null or tints.is_empty():
		return 0
	var changed := 0
	for node: Node in actor.find_children("*", "MeshInstance3D", true, false):
		var mi := node as MeshInstance3D
		if mi.mesh == null:
			continue
		for i in mi.mesh.get_surface_count():
			var worn := mi.get_active_material(i)
			var slot := slot_of(mi, i)
			if worn == null or not tints.has(String(slot)) or not SLOT_PARAMS.has(slot):
				continue
			var tinted := tinted_material(worn, slot, _colour(tints[String(slot)]))
			if tinted != null:
				mi.set_surface_override_material(i, tinted)
				changed += 1
	return changed


## The slot a surface stands for: its glTF material's name (the import keeps it under the override).
static func slot_of(mi: MeshInstance3D, surface: int) -> StringName:
	var own := mi.mesh.surface_get_material(surface)
	if own != null and own.resource_name != "":
		return StringName(own.resource_name)
	var worn := mi.get_active_material(surface)
	return StringName(worn.resource_name) if worn != null else &""


## A copy of `base` with `slot`'s parameters set to `colour` (cached), or null if `base` takes no colour.
static func tinted_material(base: Material, slot: StringName, colour: Color) -> Material:
	var sm := base as ShaderMaterial
	if sm == null:
		return null
	var key := "%s|%s|%d|%s" % [slot, base.resource_path, base.get_instance_id(), colour.to_html(false)]
	var held: Material = (_cache[key] as WeakRef).get_ref() if _cache.has(key) else null
	if held != null:
		return held
	var copy := sm.duplicate() as ShaderMaterial
	for param: StringName in SLOT_PARAMS[slot]:
		copy.set_shader_parameter(param, colour)
	_cache[key] = weakref(copy)
	return copy


## The colour a surface shows for `slot` now (the first of its parameters), or Color(0, 0, 0, 0) if none.
static func colour_of(mi: MeshInstance3D, surface: int) -> Color:
	var sm := mi.get_active_material(surface) as ShaderMaterial
	var slot := slot_of(mi, surface)
	if sm == null or not SLOT_PARAMS.has(slot):
		return Color(0, 0, 0, 0)
	var v: Variant = sm.get_shader_parameter((SLOT_PARAMS[slot] as Array)[0])
	return v as Color if v is Color else Color(0, 0, 0, 0)


static func _colour(v: Variant) -> Color:
	if v is Color:
		return v as Color
	return Color.html(str(v))
