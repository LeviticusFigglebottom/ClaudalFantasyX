class_name CreatureAmbientVfx
extends Node3D
## A creature's own ambient VFX (M4-A2P-058): the effects that belong to the body itself and live in its battle
## scene, not a skill's (those are battle-presentation's, game/data/vfx/battle/effects.json). The Mangrove
## Drowner's snagged motes and its drag, the Lamp Engine's lamp halos and its KO lift, the Avalanche Ram's breath
## and the snow its locks shed, the Wakefin's wake. Everything comes from game/data/creatures/creature_vfx.json
## (docs: each boss's art sheet, "Own VFX").
##
## A child of the CreatureActor root. It only reads the actor (current_clip, is_ko, phase, its AnimationPlayer's
## position and its nodes' visibility) and never drives it. An effect is one of:
## - `particles`: a GPUParticles3D on a bone (a BoneAttachment3D), `emit` "always" or in clip windows
##   ({clip: [from_sec, to_sec]}), or one-shot `bursts` on clip times ({clip: at_sec}), every `every_sec`
##   [min, max] (per phase), when the actor is KO'd (`ko_at_sec`) or when a watched node is hidden (`on_hidden`,
##   a break part). `while_visible` emits only while that node shows. Every continuous emitter stops on the KO.
## - `halo`: a steady billboard glow on each listed bone (a bound lamp's light: colour script rule 2, it never
##   flickers), shown only while its `while_visible` node shows.
## - `light`: an OmniLight3D on a bone.
## The row's `ko_dark` turns the halos, the lights and its `materials` (lit surface slots, as this instance's own
## copies) dark from `at_sec` after the KO over `sec`.
## Randomness: every emitter has a fixed seed and the `every_sec` intervals come from a seeded generator, so a
## capture replays the same way.

## Fired when a one-shot effect plays (tests and tools).
signal burst_played(effect_id: StringName)

const DATA_PATH := "res://game/data/creatures/creature_vfx.json"
const KIND_PARTICLES := "particles"
const KIND_HALO := "halo"
const KIND_LIGHT := "light"
const EMIT_ALWAYS := "always"
## A clip played again from earlier than this before its last position counts as a new play (a repeated hit).
const RESTART_EPS_SEC := 0.02

static var _data: Dictionary = {}

## The actor this reads (its parent).
var actor: CreatureActor
## Effect id -> its node (GPUParticles3D, the halos' holder Node3D or the OmniLight3D).
var nodes: Dictionary = {}
## Every one-shot played, in order (tests).
var played: Array[StringName] = []

var _row: Dictionary = {}
var _defs: Dictionary = {}
var _skeleton: Skeleton3D
var _player: AnimationPlayer
var _rng := RandomNumberGenerator.new()
var _last_clip: StringName = &""
var _last_pos := -1.0
var _was_ko := false
var _clock := 0.0
var _next_every: Dictionary = {}  # effect id -> clock time of its next periodic burst
var _pending: Array[Dictionary] = []  # [{id, at}] KO bursts waiting for their time
var _watched: Dictionary = {}  # effect id -> whether its on_hidden node was visible last frame
var _swapped: Array[Node3D] = []  # nodes a burst hid (shown again on a revive)
var _shown: Array[Node3D] = []  # nodes a burst showed (hidden again on a revive)
var _halo_mats: Dictionary = {}  # effect id -> [material, base colour]
var _light_energy: Dictionary = {}  # effect id -> its energy alive
var _halo_spots: Dictionary = {}  # effect id -> the holders of its halos
var _pinned: Dictionary = {}  # holder -> the model-space height it is held at (the water line), level
var _dark: Tween
var _late: Array[StringName] = []  # light effects not built yet
var _dark_mats: Array = []  # [[this instance's copy of a lit surface material, its emission energy alive]]


static func data() -> Dictionary:
	if _data.is_empty():
		var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(DATA_PATH))
		if typeof(parsed) != TYPE_DICTIONARY:
			push_error("CreatureAmbientVfx: could not read %s" % DATA_PATH)
			return {}
		_data = parsed as Dictionary
	return _data


## The creature_vfx.json row for `id` ({} when it has none).
static func row_for(id: StringName) -> Dictionary:
	return (data().get("creatures", {}) as Dictionary).get(String(id), {}) as Dictionary


## A data colour: a palette swatch's hex (the row keeps the swatch name beside it).
static func color_of(entry: Variant) -> Color:
	return Color(str((entry as Dictionary).get("hex", "#FFFFFF"))) if typeof(entry) == TYPE_DICTIONARY else Color.WHITE


func _ready() -> void:
	actor = get_parent() as CreatureActor
	if actor == null:
		push_warning("CreatureAmbientVfx: the parent is not a CreatureActor")
		return
	_row = row_for(actor.creature_id)
	var skeletons := actor.find_children("*", "Skeleton3D", true, false)
	_skeleton = skeletons[0] as Skeleton3D if not skeletons.is_empty() else null
	var players := actor.find_children("*", "AnimationPlayer", true, false)
	_player = players[0] as AnimationPlayer if not players.is_empty() else null
	_rng.seed = hash(String(actor.creature_id))
	for e: Variant in _row.get("effects", []):
		var def := e as Dictionary
		var id := StringName(str(def.get("id", "")))
		_defs[id] = def
		match str(def.get("kind", KIND_PARTICLES)):
			KIND_PARTICLES:
				nodes[id] = _build_particles(id, def)
			KIND_HALO, KIND_LIGHT:
				_late.append(id)  # built on the first frame: see build_late()
		if def.has("on_hidden"):
			_watched[id] = _node_visible(str(def["on_hidden"]))
	_own_dark_materials()


## The effect node for `id` (null when the row has none).
func effect(id: StringName) -> Node:
	return nodes.get(id, null) as Node


## Whether effect `id` (a continuous particles one) is emitting now.
func is_emitting(id: StringName) -> bool:
	var p := nodes.get(id, null) as GPUParticles3D
	return p != null and p.emitting


## Builds the halos and lights, on the first frame (_process calls it). They come after the actor's own _ready and
## the stand-in's setup, so neither owns them: the KO fade (which restores each light it found to its energy as it
## fades) and Petrify's stone (which overrides every MeshInstance3D it found, and would turn a halo into a grey
## card) leave them alone; they go dark with the core, on the KO's own time.
func build_late() -> void:
	for id in _late:
		if str((_defs[id] as Dictionary).get("kind", "")) == KIND_HALO:
			nodes[id] = _build_halos(id, _defs[id])
		else:
			_build_light(id, _defs[id])
	_late.clear()
	if _was_ko:
		_set_dark(1.0)


func _process(delta: float) -> void:
	if actor == null:
		return
	if not _late.is_empty():
		build_late()
	_clock += delta
	var ko := actor.is_ko()
	if ko != _was_ko:
		_was_ko = ko
		if ko:
			_on_ko()
		else:
			_on_revive()
	var clip := actor.current_clip
	var pos := _clip_position(clip)
	var started := clip != _last_clip or pos + RESTART_EPS_SEC < _last_pos
	var prev := -1.0 if started else _last_pos
	_hold_pinned()
	for id: StringName in _defs:
		var def: Dictionary = _defs[id]
		if str(def.get("kind", KIND_PARTICLES)) == KIND_HALO and def.has("while_visible"):
			var vis := _node_visible(str(def["while_visible"]))
			for spot: Node3D in _halo_spots.get(id, []):
				spot.visible = vis
		if str(def.get("kind", KIND_PARTICLES)) != KIND_PARTICLES:
			continue
		if def.has("emit"):
			_update_continuous(id, def, clip, pos, ko)
		if ko:
			continue
		var bursts: Dictionary = def.get("bursts", {})
		if bursts.has(String(clip)):
			var at := float(bursts[String(clip)])
			if prev < at and at <= pos:
				fire(id)
		if def.has("every_sec"):
			_update_every(id, def)
		if _watched.has(id):
			var vis := _node_visible(str(def["on_hidden"]))
			if bool(_watched[id]) and not vis:
				fire(id, false)
			_watched[id] = vis
	for i in range(_pending.size() - 1, -1, -1):
		if _clock >= float(_pending[i]["at"]):
			fire(StringName(str(_pending[i]["id"])))
			_pending.remove_at(i)
	_last_clip = clip
	_last_pos = pos


## Plays one-shot effect `id` now (its `swap` nodes hidden and shown with it). False when it is not a particles one,
## or when `check` and its `requires_visible` node is hidden (a KO lift of motes a break has already freed).
func fire(id: StringName, check := true) -> bool:
	var p := nodes.get(id, null) as GPUParticles3D
	if p == null:
		return false
	var def: Dictionary = _defs.get(id, {})
	if check and def.has("requires_visible") and not _node_visible(str(def["requires_visible"])):
		return false
	p.restart()
	p.emitting = true
	var swap: Dictionary = def.get("swap", {})
	for n: Variant in swap.get("hide", []):
		var node := actor.find_child(str(n), true, false) as Node3D
		if node != null and node.visible:
			node.visible = false
			_swapped.append(node)
	for n: Variant in swap.get("show", []):
		var node := actor.find_child(str(n), true, false) as Node3D
		if node != null and not node.visible:
			node.visible = true
			_shown.append(node)
	if _watched.has(id):
		_watched[id] = _node_visible(str(def["on_hidden"]))  # its own swap is not a break
	played.append(id)
	burst_played.emit(id)
	return true


func _update_continuous(id: StringName, def: Dictionary, clip: StringName, pos: float, ko: bool) -> void:
	var p := nodes[id] as GPUParticles3D
	var on := not ko
	var emit: Variant = def["emit"]
	if typeof(emit) == TYPE_DICTIONARY:
		var win: Array = (emit as Dictionary).get(String(clip), [])
		on = on and win.size() == 2 and float(win[0]) <= pos and pos <= float(win[1])
	elif str(emit) != EMIT_ALWAYS:
		on = false
	if def.has("while_visible"):
		on = on and _node_visible(str(def["while_visible"]))
	if p.emitting != on:
		p.emitting = on


func _update_every(id: StringName, def: Dictionary) -> void:
	if not _next_every.has(id):
		_next_every[id] = _clock + float(def.get("first_at_sec", 0.0))
	if _clock < float(_next_every[id]):
		return
	fire(id)
	var span: Array = def["every_sec"]
	var by_phase: Dictionary = def.get("every_sec_by_phase", {})
	if by_phase.has(String(actor.phase())):
		span = by_phase[String(actor.phase())]
	_next_every[id] = _clock + _rng.randf_range(float(span[0]), float(span[1]))


func _on_ko() -> void:
	for id: StringName in _defs:
		var def: Dictionary = _defs[id]
		if def.has("ko_at_sec"):
			_pending.append({"id": id, "at": _clock + float(def["ko_at_sec"])})
	if not _row.has("ko_dark"):
		return
	var dk: Dictionary = _row["ko_dark"]
	if _dark != null and _dark.is_valid():
		_dark.kill()
	if not is_inside_tree():
		_set_dark(1.0)
	else:
		_dark = create_tween()
		_dark.tween_interval(float(dk.get("at_sec", 0.0)))
		_dark.tween_method(_set_dark, 0.0, 1.0, maxf(float(dk.get("sec", 0.0)), 0.001))


func _on_revive() -> void:
	_pending.clear()
	if _dark != null and _dark.is_valid():
		_dark.kill()
	_set_dark(0.0)
	for n in _swapped:
		n.visible = true
	for n in _shown:
		n.visible = false
	_swapped.clear()
	_shown.clear()
	_next_every.clear()


## `ko_dark.materials`: the lit surfaces (by material slot) that go dark with the KO (the Engine's lamp glass and its
## core). Each takes this instance's own copy of its material (the same shader, so no new pipeline), whose
## `ko_dark.param` the KO turns down.
func _own_dark_materials() -> void:
	var dk: Dictionary = _row.get("ko_dark", {})
	var slots: Array = dk.get("materials", [])
	if slots.is_empty():
		return
	var param := StringName(str(dk.get("param", "")))
	var copies: Dictionary = {}
	for n in actor.find_children("*", "MeshInstance3D", true, false):
		var mi := n as MeshInstance3D
		if mi.mesh == null:
			continue
		for i in mi.mesh.get_surface_count():
			var cur := mi.get_active_material(i) as ShaderMaterial
			if cur == null or not slots.has(cur.resource_name):
				continue
			if not copies.has(cur):
				var copy := cur.duplicate() as ShaderMaterial
				copies[cur] = copy
				_dark_mats.append([copy, float(copy.get_shader_parameter(param))])
			mi.set_surface_override_material(i, copies[cur] as ShaderMaterial)


## 0: the halos, lights and lit surfaces at their living strength; 1: dark.
func _set_dark(t: float) -> void:
	var param := StringName(str((_row.get("ko_dark", {}) as Dictionary).get("param", "")))
	for pair: Array in _dark_mats:
		(pair[0] as ShaderMaterial).set_shader_parameter(param, float(pair[1]) * (1.0 - t))
	for id: StringName in _halo_mats:
		var pair: Array = _halo_mats[id]
		var c: Color = pair[1]
		(pair[0] as StandardMaterial3D).albedo_color = Color(c.r, c.g, c.b, c.a * (1.0 - t))
	for id: StringName in _light_energy:
		var l := nodes.get(id, null) as OmniLight3D
		if l != null:
			l.light_energy = float(_light_energy[id]) * (1.0 - t)


## Pinned holders stay level at their height over the actor (the wake on the water line) and follow the bone in x, z.
func _hold_pinned() -> void:
	for holder: Node3D in _pinned:
		var base := actor.global_transform
		var p := base.affine_inverse() * holder.global_position
		holder.global_transform = Transform3D(base.basis, base * Vector3(p.x, float(_pinned[holder]), p.z))


func _clip_position(clip: StringName) -> float:
	if _player == null or clip == &"" or StringName(_player.current_animation) != clip:
		return 0.0 if _player == null or not _player.has_animation(clip) else _last_pos
	return _player.current_animation_position


func _node_visible(node_name: String) -> bool:
	var n := actor.find_child(node_name, true, false) as Node3D
	return n != null and n.visible


## Where an effect sits: a holder on a BoneAttachment3D of its bone (or on this node when the row names none). `at_m`
## is the spot in the model's rest pose and `offset_m` a shift from the bone's head, both in the model's axes; the
## holder is turned so that its axes are the model's at rest (directions and boxes in the data read that way), and
## from there it moves with the bone.
func _mount(id: StringName, def: Dictionary) -> Node3D:
	var parent: Node3D = self
	var bone := str(def.get("bone", ""))
	var bi := _skeleton.find_bone(bone) if _skeleton != null and bone != "" else -1
	var holder := Node3D.new()
	holder.name = String(id)
	if bi >= 0:
		var att := BoneAttachment3D.new()
		att.name = "%s_%s" % [id, bone]
		att.bone_name = bone
		_skeleton.add_child(att)
		parent = att
		var rest := _skeleton.get_bone_global_rest(bi)
		var spot := rest.origin + _vec3(def.get("offset_m", []), Vector3.ZERO)
		if def.has("at_m"):
			spot = _vec3(def["at_m"], spot)
		holder.transform = rest.affine_inverse() * Transform3D(Basis.IDENTITY, spot)
	else:
		if bone != "":
			push_warning("CreatureAmbientVfx: %s has no bone %s" % [actor.creature_id, bone])
		holder.position = _vec3(def.get("at_m", def.get("offset_m", [])), Vector3.ZERO)
	parent.add_child(holder)
	if def.has("pin_y_m"):
		_pinned[holder] = float(def["pin_y_m"])
	return holder


func _build_particles(id: StringName, def: Dictionary) -> GPUParticles3D:
	var draws: Dictionary = data().get("draws", {})
	var draw: Dictionary = draws.get(str(def.get("draw", "")), {})
	var holder := _mount(id, def)
	var p := GPUParticles3D.new()
	p.name = "Particles"
	var one_shot := not def.has("emit")
	p.one_shot = one_shot
	p.emitting = false
	p.amount = maxi(1, int(def.get("amount", 1)))
	p.lifetime = float(def.get("lifetime_s", 1.0))
	p.explosiveness = float(def.get("explosiveness", 0.0))
	p.randomness = float(def.get("randomness", 0.0))
	p.local_coords = bool(def.get("local_coords", false))
	p.preprocess = float(def.get("preprocess_s", 0.0))
	p.fixed_fps = int(data().get("fixed_fps", 0))
	p.use_fixed_seed = true
	p.seed = absi(hash(String(id))) % int(data().get("seed_buckets", 1))
	p.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	var h := float(def.get("visibility_half_m", data().get("visibility_half_m", 0.0)))
	p.visibility_aabb = AABB(Vector3(-h, -h, -h), Vector3(2.0 * h, 2.0 * h, 2.0 * h))
	p.process_material = _process_material(def)
	var quad := QuadMesh.new()
	quad.size = Vector2.ONE
	if bool(draw.get("flat", false)):
		quad.orientation = PlaneMesh.FACE_Y
	quad.material = load(str(draw.get("material", ""))) as Material
	p.draw_pass_1 = quad
	holder.add_child(p)
	return p


func _process_material(def: Dictionary) -> ParticleProcessMaterial:
	var base := load(str(data().get("process_material", ""))) as ParticleProcessMaterial
	var mat := base.duplicate() as ParticleProcessMaterial
	mat.emission_box_extents = _vec3(def.get("emission_box_m", []), mat.emission_box_extents)
	mat.direction = _vec3(def.get("direction", []), mat.direction)
	mat.spread = float(def.get("spread_deg", mat.spread))
	var vel: Array = def.get("velocity_m_s", [0.0, 0.0])
	mat.initial_velocity_min = float(vel[0])
	mat.initial_velocity_max = float(vel[1])
	mat.gravity = _vec3(def.get("gravity", []), Vector3.ZERO)
	var damp: Array = def.get("damping", [0.0, 0.0])
	mat.damping_min = float(damp[0])
	mat.damping_max = float(damp[1])
	var size: Array = def.get("size_m", [0.1, 0.1])
	mat.scale_min = float(size[0])
	mat.scale_max = float(size[1])
	var grow: Array = def.get("grow", [1.0, 1.0])  # the size at birth and at death, times the start size
	var curve := Curve.new()
	curve.max_value = maxf(maxf(float(grow[0]), float(grow[1])), 1.0)
	curve.add_point(Vector2(0.0, float(grow[0])))
	curve.add_point(Vector2(1.0, float(grow[1])))
	var curve_tex := CurveTexture.new()
	curve_tex.curve = curve
	mat.scale_curve = curve_tex
	mat.color_ramp = _ramp(def)
	return mat


## The colour over a particle's life: `colors` (swatches, evenly spaced, blended in Oklab so the one sanctioned
## blend, held to lift, never goes muddy) times `energy`, with `alpha` [birth, peak, death] and the peak at `peak_at`.
func _ramp(def: Dictionary) -> GradientTexture1D:
	var cols: Array = def.get("colors", [])
	var alpha: Array = def.get("alpha", [0.0, 1.0, 0.0])
	var peak := float(def.get("peak_at", 0.2))
	var energy := float(def.get("energy", 1.0))
	var g := Gradient.new()
	g.interpolation_color_space = Gradient.GRADIENT_COLOR_SPACE_OKLAB
	var stops: Array[float] = [0.0, peak, 1.0]
	var alphas: Array[float] = [float(alpha[0]), float(alpha[1]), float(alpha[2])]
	var out_cols: Array[Color] = []
	for t in stops:
		out_cols.append(_color_at(cols, t) * energy)
	g.offsets = PackedFloat32Array(stops)
	var packed := PackedColorArray()
	for i in stops.size():
		var c := out_cols[i]
		packed.append(Color(c.r, c.g, c.b, alphas[i]))
	g.colors = packed
	var tex := GradientTexture1D.new()
	tex.gradient = g
	return tex


func _color_at(cols: Array, t: float) -> Color:
	if cols.is_empty():
		return Color.WHITE
	if cols.size() == 1:
		return color_of(cols[0])
	var x := t * float(cols.size() - 1)
	var i := mini(int(x), cols.size() - 2)
	return color_of(cols[i]).lerp(color_of(cols[i + 1]), x - float(i))


func _build_halos(id: StringName, def: Dictionary) -> Node3D:
	var holder := Node3D.new()
	holder.name = String(id)
	add_child(holder)
	var mat := (load(str(data().get("halo_material", ""))) as StandardMaterial3D).duplicate() as StandardMaterial3D
	var c := color_of(def.get("color", {})) * float(def.get("energy", 1.0))
	c.a = float(def.get("alpha", 1.0))
	mat.albedo_color = c
	_halo_mats[id] = [mat, c]
	var quad := QuadMesh.new()
	var s := float(def.get("size_m", 0.5))
	quad.size = Vector2(s, s)
	quad.material = mat
	var spots: Array[Node3D] = []
	for b: Variant in def.get("bones", []):
		var at := def.duplicate()
		at["bone"] = str(b)
		var spot := _mount(StringName("%s_%s" % [id, b]), at)
		spots.append(spot)
		var mi := MeshInstance3D.new()
		mi.name = "Halo"
		mi.mesh = quad
		mi.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
		spot.add_child(mi)
	_halo_spots[id] = spots
	return holder


func _build_light(id: StringName, def: Dictionary) -> void:
	var spot := _mount(id, def)
	var l := OmniLight3D.new()
	l.name = "Light"
	l.light_color = color_of(def.get("color", {}))
	l.light_energy = float(def.get("energy", 1.0))
	l.light_specular = float(def.get("specular", 0.0))
	l.omni_range = float(def.get("range_m", 1.0))
	l.omni_attenuation = float(def.get("attenuation", 1.0))
	l.shadow_enabled = false
	spot.add_child(l)
	nodes[id] = l
	_light_energy[id] = l.light_energy


func _vec3(v: Variant, fallback: Vector3) -> Vector3:
	if typeof(v) != TYPE_ARRAY or (v as Array).size() != 3:
		return fallback
	var a := v as Array
	return Vector3(float(a[0]), float(a[1]), float(a[2]))
