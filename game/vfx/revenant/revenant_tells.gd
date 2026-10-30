class_name RevenantTells
extends Node3D
## A revenant's tells (M3-RND-03; docs/kb/tech/revenant_tells.md): put one next to the actor (Sefir) in
## any scene. Two effects, each switchable:
##
## - **A reflection that never ripples.** The actor's capsule (its meshes' AABB, padded) goes to the
##   hymn_still_actor_* globals every frame. The water (water_surface_body.gdshaderinc) marches its SSR
##   with a flat normal wherever the mirror ray meets that capsule and the flat march lands on the actor,
##   so his reflection stays a mirror while everyone else's breaks up. Tiers without SSR (Low) show none.
## - **A shadow that is faintly too sharp.** The key (the brightest shadowed DirectionalLight3D, or `lights`)
##   stops casting the actor: his meshes move to the still layer (as CutsceneKeyLight moves a close shot's
##   cast) and the key's shadow_caster_mask drops it. Two copies of the key stand in for it on him alone:
##   one shadowed with shadow_caster_mask = the still layer and a shadow_blur sharper than the key's, and
##   one identical but negative and unshadowed. Where nothing blocks them they cancel exactly, so nothing
##   is lit twice; in his shadow only the positive one is blocked, which removes the key there with a
##   crisper edge than everyone else's shadow gets. (Distant spot lights standing in for the key were tried:
##   Godot 4.6.3 shadowed the light's side of the caster at 200 m, acne and black tiles at 60 m.) The positive
##   copy is one more shadowed directional light, so it shares the directional shadow atlas.
##
## The cutscene key light (CutsceneKeyLight) moves a close shot's cast onto its own layer, which takes the
## still layer off the actor while it is engaged: in those close shots his shadow is the sun's soft one.
## disengage() (also on leaving the tree) restores every layer, caster mask and global.

const CONFIG_PATH := "res://game/data/vfx/revenant_tells.json"
## One capsule per slot: xyz = the capsule's base (world), w = radius (0 = slot free). Heights in
## hymn_still_actor_heights (x = slot 0, y = slot 1).
const SLOT_GLOBALS: Array[StringName] = [&"hymn_still_actor_0", &"hymn_still_actor_1"]
const HEIGHTS_GLOBAL := &"hymn_still_actor_heights"

static var _slot_owners: Array = [null, null]

## The actor (any Node3D; its GeometryInstance3D descendants are the meshes). Resolved when engaging, so
## an actor a parent adds in its own _ready is found.
@export var actor_path: NodePath
@export var still_reflection := true
@export var sharp_shadow := true
## The lights whose shadow of the actor turns sharp. Empty = the brightest shadowed DirectionalLight3D in
## the current scene when engaging (the key; the others keep casting him softly).
@export var lights: Array[NodePath] = []

var config: Dictionary = {}
var actor: Node3D
## [light, its original shadow_caster_mask, positive copy, negative copy] per light.
var pairs: Array = []
var slot := -1
# [GeometryInstance3D, original layers] per actor mesh.
var _meshes: Array = []
# The capsule in the actor's local space: base point, radius and height (before the actor's scale).
var _local_base := Vector3.ZERO
var _local_radius := 0.0
var _local_height := 0.0


static func load_config() -> Dictionary:
	var f := FileAccess.open(CONFIG_PATH, FileAccess.READ)
	if f == null:
		push_error("RevenantTells: cannot read %s" % CONFIG_PATH)
		return {}
	var data: Variant = JSON.parse_string(f.get_as_text())
	return data if data is Dictionary else {}


func _ready() -> void:
	config = load_config()
	engage.call_deferred()


func _exit_tree() -> void:
	disengage()


func still_mask() -> int:
	return 1 << (int(config.get("still_layer", 1)) - 1)


func is_engaged() -> bool:
	return actor != null


## Finds the actor and turns the tells on. Safe to call again (it disengages first).
func engage() -> void:
	disengage()
	if not is_inside_tree():
		return
	actor = get_node_or_null(actor_path) as Node3D
	if actor == null:
		push_warning("RevenantTells: no actor at %s" % actor_path)
		return
	var mask := still_mask()
	var bounds := AABB()
	var first := true
	var to_local := actor.global_transform.affine_inverse()
	for n in actor.find_children("*", "GeometryInstance3D", true, false):
		var g := n as GeometryInstance3D
		_meshes.append([g, g.layers])
		# Only the still layer: a light casts any mesh sharing a layer with its caster mask, so a mesh
		# left on layer 1 too would still cast from the keys. Cameras and lights see layer 18 by default.
		g.layers = mask
		var vi := g as VisualInstance3D
		var box := (to_local * vi.global_transform) * vi.get_aabb()
		bounds = box if first else bounds.merge(box)
		first = false
	var pad := float(config.get("capsule_pad_m", 0.0))
	var center := bounds.get_center()
	_local_base = Vector3(center.x, bounds.position.y - pad, center.z)
	_local_radius = maxf(bounds.size.x, bounds.size.z) * 0.5 + pad
	_local_height = bounds.size.y + 2.0 * pad
	if still_reflection:
		_claim_slot()
	if sharp_shadow:
		for light in _shadow_lights():
			_add_pair(light, mask)
	_update()


## Turns the tells off and puts every mesh layer, caster mask and global back.
func disengage() -> void:
	for pair: Array in _meshes:
		if is_instance_valid(pair[0]):
			(pair[0] as GeometryInstance3D).layers = int(pair[1])
	_meshes.clear()
	for p: Array in pairs:
		if is_instance_valid(p[0]):
			(p[0] as DirectionalLight3D).shadow_caster_mask = int(p[1])
		for k in [2, 3]:
			if is_instance_valid(p[k]):
				(p[k] as Node).queue_free()
	pairs.clear()
	if slot >= 0:
		ShaderGlobals.reset(SLOT_GLOBALS[slot])
		_slot_owners[slot] = null
		if _slot_owners.all(func(o: Variant) -> bool: return o == null):
			ShaderGlobals.reset(HEIGHTS_GLOBAL)
		slot = -1
	actor = null


func _process(_delta: float) -> void:
	if actor != null:
		if not is_instance_valid(actor):
			disengage()
			return
		_update()


## The capsule (world): base, radius, height. Valid while engaged.
func capsule() -> Array:
	var xf := actor.global_transform
	var s := xf.basis.get_scale()
	return [xf * _local_base, _local_radius * maxf(s.x, s.z), _local_height * s.y]


func _update() -> void:
	if slot >= 0:
		var c := capsule()
		var base: Vector3 = c[0]
		ShaderGlobals.set_value(SLOT_GLOBALS[slot], Vector4(base.x, base.y, base.z, float(c[1])))
		var h: Vector2 = ShaderGlobals.get_value(HEIGHTS_GLOBAL, Vector2.ZERO)
		h[slot] = float(c[2])
		ShaderGlobals.set_value(HEIGHTS_GLOBAL, h)
	for p: Array in pairs:
		if not is_instance_valid(p[0]):
			continue
		var light := p[0] as DirectionalLight3D
		for k in [2, 3]:
			if not is_instance_valid(p[k]):
				continue
			var twin := p[k] as DirectionalLight3D
			twin.global_transform = light.global_transform
			_copy_light(light, twin)
			twin.visible = light.is_visible_in_tree()


func _claim_slot() -> void:
	var n := mini(int(config.get("max_still_actors", 0)), SLOT_GLOBALS.size())
	for i in n:
		var o: Variant = _slot_owners[i]
		if o == null or not is_instance_valid(o):
			_slot_owners[i] = self
			slot = i
			return
	push_warning("RevenantTells: every still-actor slot is taken; %s's reflection ripples" % actor.name)


func _shadow_lights() -> Array[DirectionalLight3D]:
	var out: Array[DirectionalLight3D] = []
	if not lights.is_empty():
		for p in lights:
			var l := get_node_or_null(p) as DirectionalLight3D
			if l != null and l.shadow_enabled:
				out.append(l)
		return out
	var root: Node = get_tree().current_scene if get_tree().current_scene != null else owner
	if root == null:
		root = get_parent()
	var key: DirectionalLight3D = null
	for n in root.find_children("*", "DirectionalLight3D", true, false):
		var l := n as DirectionalLight3D
		if not l.shadow_enabled or not l.is_visible_in_tree() or l is CutsceneKeyLight:
			continue
		if key == null or l.light_energy > key.light_energy:
			key = l
	if key != null:
		out.append(key)
	return out


func _add_pair(light: DirectionalLight3D, mask: int) -> void:
	var twins: Array[DirectionalLight3D] = []
	for negative in [false, true]:
		var t := DirectionalLight3D.new()
		t.name = "%sTell%s" % [light.name, "Cancel" if negative else "Sharp"]
		t.top_level = true
		t.light_negative = negative
		t.shadow_enabled = not negative
		t.shadow_caster_mask = mask
		t.shadow_blur = float(config.get("shadow_blur", 0.0))
		t.shadow_bias = light.shadow_bias
		t.shadow_normal_bias = light.shadow_normal_bias
		t.directional_shadow_mode = light.directional_shadow_mode
		t.directional_shadow_split_1 = light.directional_shadow_split_1
		t.directional_shadow_split_2 = light.directional_shadow_split_2
		t.directional_shadow_split_3 = light.directional_shadow_split_3
		t.directional_shadow_max_distance = light.directional_shadow_max_distance
		t.light_cull_mask = light.light_cull_mask
		t.light_angular_distance = 0.0
		t.light_indirect_energy = 0.0
		t.light_volumetric_fog_energy = 0.0
		t.light_bake_mode = Light3D.BAKE_DISABLED
		t.sky_mode = DirectionalLight3D.SKY_MODE_LIGHT_ONLY
		add_child(t)
		twins.append(t)
	pairs.append([light, light.shadow_caster_mask, twins[0], twins[1]])
	light.shadow_caster_mask &= ~mask


func _copy_light(light: DirectionalLight3D, twin: DirectionalLight3D) -> void:
	twin.light_color = light.light_color
	twin.light_energy = light.light_energy
	twin.light_intensity_lux = light.light_intensity_lux
	twin.light_temperature = light.light_temperature
	twin.light_specular = light.light_specular
