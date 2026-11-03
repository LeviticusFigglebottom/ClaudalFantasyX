class_name BattleStatusLooks
extends Node3D
## FAST-TRACK 11-03 (the human's playtest: status effects must be OBVIOUS on the character). Every status a fighter
## holds shows ON the fighter for as long as it lasts (docs/kb/tech/battle_status_looks.md):
##   - an overlay: status_overlay.gdshader as every surface's material_overlay (one at a time, the highest priority);
##   - an aura: a looping GPUParticles3D whose motion is the status's own (bubbles rise, motes fall, sparkles hang...);
##   - a prop: a shell, rings, panes or a ground mark (Shell, Protect, Reflect, Silence, Provoke);
##   - its icon over the head (over the feet for a body taller than icons.feet_over_height_m), with Doom's count.
## Data: game/data/vfx/battle/status_looks.json; icons: assets/vfx/battle/status_icons (tools/vfx/status_icons.py).
## - **Listens only.** It reads combatant.statuses after the engine's signals (on the choreography's contact beat,
##   as BattleVfx does) and never writes combat state.
## - Per fighter the parts live under one "StatusLooks" node parented to its FighterStandIn, so they follow the
##   choreography's moves.

const DATA_PATH := "res://game/data/vfx/battle/status_looks.json"
const OVERLAY_SHADER := preload("res://game/vfx/battle/status_overlay.gdshader")
const DRAW_MATERIAL := "res://game/vfx/battle/materials/battle_spark_draw.tres"
const HOLDER := &"StatusLooks"
const PATTERNS := {
	"rim": 0,
	"pulse": 1,
	"bands_up": 2,
	"bands_down": 3,
	"flicker": 4,
	"hatch": 5,
	"frost": 6,
	"cracks": 7,
}
## The height fractions an aura or a prop sits at (effects.json anchor_heights' keys).
const VISIBILITY_HALF_M := 2.5
const PANES := 3
const RINGS := 3
## Protect's rings: knee, waist and chest, as fractions of the body's height.
const RING_HEIGHTS: Array[float] = [0.25, 0.5, 0.75]
const DOOM := &"doom"
## An icon's (or Doom count's) place in its fighter's row.
const SLOT_META := &"status_slot"

static var _data_cache: Dictionary = {}

var data: Dictionary = {}
var reduced_motion := false
## cid -> {status id: true}: what each fighter shows now (tests read it).
var shown: Dictionary = {}
var _ctl: BattleController
var _engine: BattleEngine
var _anchors: Dictionary = {}
## cid -> {status id -> Node3D (its aura/prop/icon parts)}.
var _parts: Dictionary = {}
## cid -> the status whose overlay is on (or &"").
var _overlay_of: Dictionary = {}
## cid -> {MeshInstance3D: its own material_overlay before ours}.
var _saved_overlay: Dictionary = {}
var _overlay_mats: Dictionary = {}
var _textures: Dictionary = {}
var _draw_mesh: QuadMesh
var _spinners: Array[Node3D] = []
var _spin_rates: Array[float] = []
## cid -> the row's layout {beside, first, step, tex, head_y}; cid -> the side it is on now (1 right, -1 left).
var _rows: Dictionary = {}
var _side: Dictionary = {}


static func load_data() -> Dictionary:
	if _data_cache.is_empty():
		var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(DATA_PATH))
		if typeof(parsed) == TYPE_DICTIONARY:
			_data_cache = parsed as Dictionary
		else:
			push_warning("BattleStatusLooks: cannot read %s" % DATA_PATH)
	return _data_cache


## Builds the view under the controller's stage and connects it to `engine` (BattleVfx.attach calls it).
static func attached(controller: BattleController, engine: BattleEngine) -> BattleStatusLooks:
	var old := controller.stage.get_node_or_null(^"BattleStatusLooks")
	if old != null:
		old.name = &"BattleStatusLooksOld"
		old.queue_free()
		(old as BattleStatusLooks).clear_all()
	var view := BattleStatusLooks.new()
	view.name = "BattleStatusLooks"
	controller.stage.add_child(view)
	view.attach(controller, engine)
	return view


func _init() -> void:
	data = load_data()
	_anchors = (BattleVfx.load_data().get("anchor_heights", {}) as Dictionary)


func attach(controller: BattleController, engine: BattleEngine) -> void:
	_ctl = controller
	_engine = engine
	var choreo := controller.stage.choreo
	if choreo != null:
		choreo.contact.connect(func(_r: ActionResult) -> void: refresh())
	engine.action_resolved.connect(func(_r: ActionResult) -> void: _refresh_unless_choreo())
	engine.turn_ended.connect(func(_a: BattleCombatant, _c: Array[Dictionary]) -> void: refresh.call_deferred())
	engine.turn_lost.connect(
		func(_a: BattleCombatant, _r: StringName, _c: Array[Dictionary]) -> void: refresh.call_deferred()
	)
	engine.turn_started.connect(func(_a: BattleCombatant) -> void: refresh.call_deferred())
	engine.combatants_joined.connect(func(_a: Array[BattleCombatant]) -> void: refresh.call_deferred())
	engine.battle_finished.connect(func(_o: StringName) -> void: clear_all())
	var settings := UiSettings.shared()
	if settings != null:
		reduced_motion = settings.reduced_motion()
		settings.changed.connect(func(_key: StringName) -> void: reduced_motion = settings.reduced_motion())
	refresh.call_deferred()  # opening statuses (a fixture's, an equipment's)


func _refresh_unless_choreo() -> void:
	if _ctl == null or _ctl.stage.choreo == null or not _ctl.stage.choreo.playing():
		refresh.call_deferred()


## What `c` shows now: its statuses that have a look, in statuses.json order; none once it is down.
func wanted_for(c: BattleCombatant) -> Array[StringName]:
	var out: Array[StringName] = []
	if c == null or c.hp <= 0 or c.withdrawn or c.yielded:
		return out
	var looks := data.get("looks", {}) as Dictionary
	for sid: StringName in _status_order():
		if c.statuses.has(sid) and looks.has(String(sid)):
			out.append(sid)
	return out


## The overlay `ids` show: the highest priority among those with an overlay row (&"" for none).
func overlay_pick(ids: Array[StringName]) -> StringName:
	var best := &""
	var best_p := -INF
	var looks := data.get("looks", {}) as Dictionary
	for sid in ids:
		var ov := (looks.get(String(sid), {}) as Dictionary).get("overlay", {}) as Dictionary
		if not ov.is_empty() and float(ov.get("priority", 0.0)) > best_p:
			best_p = float(ov.get("priority", 0.0))
			best = sid
	return best


## Reads every fighter's statuses and shows them (adds the new, removes the gone).
func refresh() -> void:
	if _engine == null or _ctl == null or not is_inside_tree():
		return
	for c in _engine.party_active + _engine.party_reserve + _engine.enemies + _engine.entries:
		show_for(c)


func show_for(c: BattleCombatant) -> void:
	var f := _ctl.stage.stand_in(c.id) if _ctl.stage.has_fighter(c.id) else null
	var want := wanted_for(c) if f != null and f.visible else ([] as Array[StringName])
	var have := (_parts.get(c.id, {}) as Dictionary).duplicate()
	var now: Dictionary = {}
	for sid in want:
		now[sid] = true
		if not have.has(sid):
			_add_parts(c.id, f, sid)
	for sid: StringName in have:
		if not now.has(sid):
			_remove_parts(c.id, sid)
	shown[c.id] = now
	if f != null:
		_set_overlay(c.id, f, overlay_pick(want))
		_layout_icons(c, f, want)


## Takes every look off every fighter (the battle's end, a retry).
func clear_all() -> void:
	for cid: StringName in _parts.keys():
		for sid: StringName in (_parts[cid] as Dictionary).keys():
			_remove_parts(cid, sid)
	for cid: StringName in _overlay_of.keys():
		_restore_overlay(cid)
	_overlay_of.clear()
	shown.clear()
	_rows.clear()
	_side.clear()


func _process(delta: float) -> void:
	var rm := data.get("reduced_motion", {}) as Dictionary
	var k := float(rm.get("speed_scale", 1.0)) if reduced_motion else 1.0
	for i in _spinners.size():
		var n := _spinners[i]
		if is_instance_valid(n):
			n.rotation.y += deg_to_rad(_spin_rates[i]) * delta * k
	_place_rows()


## A row beside the head runs right of the actor marker, or left of it for a fighter on the screen's right half, so
## it never leaves the screen at the frame's edge.
func _place_rows() -> void:
	var cam := get_viewport().get_camera_3d() if is_inside_tree() else null
	if cam == null or _ctl == null:
		return
	var half := get_viewport().get_visible_rect().size.x * 0.5
	for cid: StringName in _rows:
		var row := _rows[cid] as Dictionary
		if not bool(row["beside"]) or not _ctl.stage.has_fighter(cid):
			continue
		var f := _ctl.stage.stand_in(cid)
		var head := f.global_position + Vector3.UP * float(row["head_y"])
		if cam.is_position_behind(head):
			continue
		var side := -1 if cam.unproject_position(head).x > half else 1
		if int(_side.get(cid, 0)) == side:
			continue
		_side[cid] = side
		var first := float(row["first"])
		var step := float(row["step"])
		var tex := float(row["tex"])
		for root: Variant in (_parts.get(cid, {}) as Dictionary).values():
			var icon := (root as Node3D).get_node_or_null(^"Icon") as Sprite3D
			if icon != null and icon.has_meta(SLOT_META):
				icon.offset.x = side * (first + float(icon.get_meta(SLOT_META)) * step)
			var count := (root as Node3D).get_node_or_null(^"Count") as Label3D
			if count != null and count.has_meta(SLOT_META):
				count.offset.x = side * (first + float(count.get_meta(SLOT_META)) * step) + tex * 0.42


func _holder(f: FighterStandIn) -> Node3D:
	var h := f.get_node_or_null(NodePath(String(HOLDER))) as Node3D
	if h == null:
		h = Node3D.new()
		h.name = HOLDER
		f.add_child(h)
	return h


func _add_parts(cid: StringName, f: FighterStandIn, sid: StringName) -> void:
	var look := (data.get("looks", {}) as Dictionary).get(String(sid), {}) as Dictionary
	var root := Node3D.new()
	root.name = String(sid)
	_holder(f).add_child(root)
	var height := float(f.spec.get("height", 1.7))
	var hover := float(f.spec.get("hover", 0.0))
	var radius := float(f.spec.get("radius", 0.35))
	if look.has("aura"):
		root.add_child(_aura(look["aura"] as Dictionary, height, hover))
	if look.has("prop"):
		root.add_child(_prop(look["prop"] as Dictionary, height, hover, radius))
	root.add_child(_icon(sid))
	if bool(look.get("count", false)):
		root.add_child(_count_label(sid))
	var per := _parts.get(cid, {}) as Dictionary
	per[sid] = root
	_parts[cid] = per


func _remove_parts(cid: StringName, sid: StringName) -> void:
	var per := _parts.get(cid, {}) as Dictionary
	var root := per.get(sid) as Node3D
	per.erase(sid)
	if root != null and is_instance_valid(root):
		for i in range(_spinners.size() - 1, -1, -1):
			if not is_instance_valid(_spinners[i]) or root.is_ancestor_of(_spinners[i]):
				_spinners.remove_at(i)
				_spin_rates.remove_at(i)
		root.get_parent().remove_child(root)
		root.queue_free()


func _height_at(key: String, height: float, hover: float) -> float:
	return hover + height * float(_anchors.get(key, 0.5))


## A looping emitter on the fighter: its motion picks the direction, gravity and spread.
func _aura(a: Dictionary, height: float, hover: float) -> GPUParticles3D:
	var p := GPUParticles3D.new()
	p.name = "Aura"
	var rm := data.get("reduced_motion", {}) as Dictionary
	var amount := float(a.get("amount", 8))
	if reduced_motion:
		amount *= float(rm.get("particle_scale", 1.0))
	p.amount = maxi(1, roundi(amount))
	p.lifetime = float(a.get("lifetime_s", 1.0))
	p.explosiveness = 0.0
	p.randomness = 0.4
	p.local_coords = false
	p.preprocess = p.lifetime  # already flowing the frame it appears
	p.position = Vector3(0.0, _height_at(str(a.get("at", "chest")), height, hover), 0.0)
	var mat := ParticleProcessMaterial.new()
	var radius := float(a.get("radius_m", 0.25))
	var speed := float(a.get("speed_m_s", 0.3))
	mat.emission_shape = ParticleProcessMaterial.EMISSION_SHAPE_SPHERE
	mat.emission_sphere_radius = radius
	mat.spread = 25.0
	mat.gravity = Vector3.ZERO
	mat.direction = Vector3.UP
	match str(a.get("motion", "rise")):
		"rise", "rise_fast", "drift_up":
			mat.direction = Vector3.UP
		"fall", "sag":
			mat.direction = Vector3.DOWN
			mat.gravity = Vector3(0.0, -0.6, 0.0)
		"shards", "shards_wide":
			mat.direction = Vector3.UP
			mat.spread = 70.0
			mat.gravity = Vector3(0.0, -3.0, 0.0)
		"burst":
			mat.spread = 50.0
			mat.gravity = Vector3(0.0, 0.8, 0.0)
		"hang":
			mat.emission_shape = ParticleProcessMaterial.EMISSION_SHAPE_SPHERE_SURFACE
		"orbit":
			mat.emission_shape = ParticleProcessMaterial.EMISSION_SHAPE_RING
			mat.emission_ring_axis = Vector3.UP
			mat.emission_ring_radius = radius
			mat.emission_ring_inner_radius = radius * 0.9
			mat.emission_ring_height = 0.02
			mat.orbit_velocity_min = speed
			mat.orbit_velocity_max = speed
			speed = 0.0
	if str(a.get("motion", "")) == "sag":
		mat.emission_shape = ParticleProcessMaterial.EMISSION_SHAPE_RING
		mat.emission_ring_axis = Vector3.UP
		mat.emission_ring_radius = radius
		mat.emission_ring_inner_radius = radius * 0.5
		mat.emission_ring_height = 0.02
	var vk := float(rm.get("speed_scale", 1.0)) if reduced_motion else 1.0
	mat.initial_velocity_min = speed * 0.7 * vk
	mat.initial_velocity_max = speed * vk
	var size: Array = a.get("size_m", [0.05, 0.1])
	mat.scale_min = float(size[0])
	mat.scale_max = float(size[1])
	var c := Color(str(a.get("color", "#FFFFFF")))
	var e := float(a.get("energy", 1.0))
	var ramp := Gradient.new()
	ramp.set_color(0, Color(c.r * e, c.g * e, c.b * e, 0.0))
	ramp.set_color(1, Color(c.r * e, c.g * e, c.b * e, 0.0))
	ramp.add_point(0.15, Color(c.r * e, c.g * e, c.b * e, 1.0))
	ramp.add_point(0.7, Color(c.r * e, c.g * e, c.b * e, 0.9))
	var tex := GradientTexture1D.new()
	tex.gradient = ramp
	mat.color_ramp = tex
	p.process_material = mat
	if _draw_mesh == null:
		_draw_mesh = QuadMesh.new()
		_draw_mesh.material = load(DRAW_MATERIAL) as Material
	p.draw_pass_1 = _draw_mesh
	p.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	var h := VISIBILITY_HALF_M
	p.visibility_aabb = AABB(Vector3(-h, -h, -h), Vector3(2.0 * h, 2.0 * h, 2.0 * h))
	p.emitting = true
	return p


## A see-through unshaded material in a prop's colour, its edge brighter (a fresnel rim) for the sphere.
func _prop_material(pr: Dictionary, fresnel: bool) -> StandardMaterial3D:
	var m := StandardMaterial3D.new()
	var c := Color(str(pr.get("color", "#FFFFFF")))
	m.albedo_color = Color(c.r, c.g, c.b, float(pr.get("alpha", 0.5)))
	m.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	m.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	m.cull_mode = BaseMaterial3D.CULL_DISABLED
	m.no_depth_test = false
	if fresnel:
		m.rim_enabled = false
		m.albedo_color.a = float(pr.get("alpha", 0.5)) * 0.35
		m.emission_enabled = false
	return m


func _prop(pr: Dictionary, height: float, hover: float, body_radius: float) -> Node3D:
	var root := Node3D.new()
	root.name = "Prop"
	var kind := str(pr.get("kind", ""))
	var at := _height_at(str(pr.get("at", "chest")), height, hover)
	var r := maxf(
		float(pr.get("radius_m", body_radius * 1.4)),
		body_radius * (0.7 if kind == "ring" else (0.95 if kind == "rings" else 1.25))
	)
	var spin := float(pr.get("spin_deg_s", 0.0))
	match kind:
		"ring", "ground_mark":
			var t := TorusMesh.new()
			var tube := float(pr.get("tube_m", 0.03))
			t.inner_radius = r - tube
			t.outer_radius = r + tube
			t.rings = 48
			var mi := MeshInstance3D.new()
			mi.mesh = t
			mi.material_override = _prop_material(pr, false)
			mi.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
			root.add_child(mi)
			if kind == "ground_mark":  # a crosshair on the ground: the ring and four ticks
				r = maxf(r, body_radius * 1.6)
				t.inner_radius = r - tube
				t.outer_radius = r + tube
				for i in 4:
					var tick := MeshInstance3D.new()
					var b := BoxMesh.new()
					b.size = Vector3(tube * 2.5, tube * 1.5, r * 0.45)
					tick.mesh = b
					tick.material_override = mi.material_override
					tick.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
					var ang := i * PI * 0.5
					tick.position = Vector3(sin(ang), 0.0, cos(ang)) * r
					tick.rotation.y = ang
					root.add_child(tick)
			else:
				r = maxf(r, body_radius * 0.7)
		"sphere":
			var s := SphereMesh.new()
			var sr := maxf(height * 0.5, body_radius) * float(pr.get("radius_scale", 1.15))
			s.radius = sr
			s.height = sr * 2.0
			var mi := MeshInstance3D.new()
			mi.mesh = s
			var sm := ShaderMaterial.new()
			sm.shader = OVERLAY_SHADER
			var c := Color(str(pr.get("color", "#FFFFFF")))
			sm.set_shader_parameter(&"tint", c)
			sm.set_shader_parameter(&"strength", float(pr.get("alpha", 0.5)) * 1.6)
			sm.set_shader_parameter(&"pattern", 0)
			sm.set_shader_parameter(&"rim_power", 1.6)
			mi.material_override = sm
			mi.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
			root.add_child(mi)
			at = hover + height * 0.5
		"rings":
			var tube := float(pr.get("tube_m", 0.02))
			for i in RINGS:
				var t := TorusMesh.new()
				t.inner_radius = r - tube
				t.outer_radius = r + tube
				t.rings = 48
				var mi := MeshInstance3D.new()
				mi.mesh = t
				mi.material_override = _prop_material(pr, false)
				mi.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
				mi.position = Vector3(0.0, hover + height * RING_HEIGHTS[i] - at, 0.0)
				mi.rotation = Vector3(deg_to_rad(8.0 * (i - 1)), 0.0, deg_to_rad(6.0 * (1 - i)))
				root.add_child(mi)
		"panes":
			var size: Array = pr.get("pane_m", [0.28, 0.42])
			for i in PANES:
				var q := QuadMesh.new()
				q.size = Vector2(float(size[0]), float(size[1]))
				var mi := MeshInstance3D.new()
				mi.mesh = q
				mi.material_override = _prop_material(pr, false)
				(mi.material_override as StandardMaterial3D).metallic_specular = 1.0
				mi.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
				var ang := i * TAU / PANES
				mi.position = Vector3(sin(ang), 0.0, cos(ang)) * r
				mi.rotation.y = ang
				root.add_child(mi)
	root.position = Vector3(0.0, at, 0.0)
	if spin != 0.0:
		_spinners.append(root)
		_spin_rates.append(spin)
	return root


func _texture(sid: StringName) -> Texture2D:
	if not _textures.has(sid):
		var path := "%s/%s.svg" % [str((data.get("icons", {}) as Dictionary).get("dir", "")), sid]
		_textures[sid] = load(path) as Texture2D if ResourceLoader.exists(path) else null
	return _textures[sid]


func _icon(sid: StringName) -> Sprite3D:
	var cfg := data.get("icons", {}) as Dictionary
	var s := Sprite3D.new()
	s.name = "Icon"
	s.texture = _texture(sid)
	s.billboard = BaseMaterial3D.BILLBOARD_ENABLED
	s.fixed_size = true
	s.no_depth_test = true
	s.shaded = false
	s.double_sided = true
	s.alpha_cut = SpriteBase3D.ALPHA_CUT_DISABLED
	s.pixel_size = float(cfg.get("pixel_size", 0.0003))
	s.render_priority = int(cfg.get("render_priority", 0))
	s.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	return s


func _count_label(_sid: StringName) -> Label3D:
	var cfg := data.get("icons", {}) as Dictionary
	var l := Label3D.new()
	l.name = "Count"
	l.billboard = BaseMaterial3D.BILLBOARD_ENABLED
	l.fixed_size = true
	l.no_depth_test = true
	l.shaded = false
	l.pixel_size = float(cfg.get("pixel_size", 0.0003))
	l.font_size = int(cfg.get("count_font_px", 64))
	l.outline_size = int(cfg.get("count_outline_px", 12))
	l.outline_modulate = Color(0.0, 0.0, 0.0, 1.0)
	l.render_priority = int(cfg.get("render_priority", 0)) + 1
	l.outline_render_priority = int(cfg.get("render_priority", 0))
	return l


## The icons in one row, statuses.json order, at most max_shown: over the head, starting beside_px right of the head
## point so the actor marker (head + 0.3 m) stays clear; over the feet of a tall body, centred.
func _layout_icons(c: BattleCombatant, f: FighterStandIn, ids: Array[StringName]) -> void:
	var cfg := data.get("icons", {}) as Dictionary
	var per := _parts.get(c.id, {}) as Dictionary
	var height := float(f.spec.get("height", 1.7))
	var hover := float(f.spec.get("hover", 0.0))
	var y := hover + height + float(cfg.get("lift_m", 0.3))
	var feet := height > float(cfg.get("feet_over_height_m", INF))
	if feet:
		y = hover + float(cfg.get("lift_m", 0.3)) * 0.5
	var tex_px := 128.0
	var step := tex_px + float(cfg.get("gap_px", 8))
	var shown_ids: Array[StringName] = []
	for sid in ids:
		if shown_ids.size() < int(cfg.get("max_shown", 5)):
			shown_ids.append(sid)
	var first := -float(shown_ids.size() - 1) * 0.5 * step
	if not feet:
		first = float(cfg.get("beside_px", 0.0)) + tex_px * 0.5
	for sid in ids:
		var root := per.get(sid) as Node3D
		if root == null:
			continue
		var icon := root.get_node_or_null(^"Icon") as Sprite3D
		var i := shown_ids.find(sid)
		if icon != null:
			icon.visible = i >= 0
			if icon.texture != null:
				tex_px = float(icon.texture.get_width())
			icon.position = Vector3(0.0, y - root.position.y, 0.0)
			icon.offset = Vector2(first + float(i) * step, 0.0)
			icon.set_meta(SLOT_META, i)
		var count := root.get_node_or_null(^"Count") as Label3D
		if count != null:
			count.visible = i >= 0
			count.text = str(c.doom_count()) if sid == DOOM else str(int(c.statuses.get(sid, 0)))
			count.position = Vector3(0.0, y - root.position.y, 0.0)
			count.offset = Vector2(first + float(i) * step + tex_px * 0.42, -tex_px * 0.3)
			count.set_meta(SLOT_META, i)
	_rows[c.id] = {"beside": not feet, "first": first, "step": step, "tex": tex_px, "head_y": y}
	_side.erase(c.id)  # placed on the next frame (_place_rows)


## The overlay on every surface of the fighter (not the target ring, not our own parts), or our overlay off.
func _set_overlay(cid: StringName, f: FighterStandIn, sid: StringName) -> void:
	if StringName(_overlay_of.get(cid, &"")) == sid:
		return
	_restore_overlay(cid)
	_overlay_of[cid] = sid
	if sid == &"":
		return
	var mat := _overlay_material(sid)
	var saved: Dictionary = {}
	for m in surfaces(f):
		saved[m] = m.material_overlay
		m.material_overlay = mat
	_saved_overlay[cid] = saved


func _restore_overlay(cid: StringName) -> void:
	var saved := _saved_overlay.get(cid, {}) as Dictionary
	for m: Variant in saved:
		if is_instance_valid(m):
			(m as MeshInstance3D).material_overlay = saved[m]
	_saved_overlay.erase(cid)
	_overlay_of[cid] = &""


## The fighter's body surfaces: its MeshInstance3Ds but the ground ring (a ShaderMaterial override) and ours.
static func surfaces(f: FighterStandIn) -> Array[MeshInstance3D]:
	var out: Array[MeshInstance3D] = []
	var holder := f.get_node_or_null(NodePath(String(HOLDER)))
	for n in f.find_children("*", "MeshInstance3D", true, false):
		var m := n as MeshInstance3D
		if holder != null and holder.is_ancestor_of(m):
			continue
		var o := m.material_override as ShaderMaterial
		if o != null and o.shader == FighterStandIn.RING_SHADER:
			continue
		out.append(m)
	return out


func _overlay_material(sid: StringName) -> ShaderMaterial:
	if _overlay_mats.has(sid):
		return _overlay_mats[sid]
	var ov := (
		((data.get("looks", {}) as Dictionary).get(String(sid), {}) as Dictionary).get("overlay", {}) as Dictionary
	)
	var m := ShaderMaterial.new()
	m.shader = OVERLAY_SHADER
	m.set_shader_parameter(&"tint", Color(str(ov.get("color", "#FFFFFF"))))
	m.set_shader_parameter(&"strength", float(ov.get("strength", 0.5)))
	m.set_shader_parameter(&"pattern", int(PATTERNS.get(str(ov.get("pattern", "rim")), 0)))
	var rm := data.get("reduced_motion", {}) as Dictionary
	var k := float(rm.get("speed_scale", 1.0)) if reduced_motion else 1.0
	m.set_shader_parameter(&"speed", float(ov.get("speed", 1.0)) * k)
	_overlay_mats[sid] = m
	return m


func _status_order() -> Array[StringName]:
	var out: Array[StringName] = []
	if _engine != null and _engine.db != null:
		for sid: Variant in _engine.db.statuses:
			out.append(StringName(str(sid)))
	return out
