class_name UndertowHalfRes
extends Node
## Renders the Undertow's raymarched body at a fraction of the game view's resolution
## (M2-RND-01, experimental; UndertowStorm.half_res_body_scale < 1 turns it on).
## The body moves to its own visual layer, a SubViewport sharing the world renders only that layer
## through a camera that copies the game camera every frame (just before drawing), with its own
## TAA disabled (TAA does not keep a transparent SubViewport's alpha); the composite
## (undertow_composite.gdshader) is drawn on the body's proxy cylinder in the game view, so the game
## view's TAA/FSR2 gets the storm's real motion vectors and integrates the half-res frames, and it
## lays the premultiplied result over the frame with an analytic occlusion test against the depth.
##
## Compute mode (M2-RND-01, the default wherever a RenderingDevice exists and the tier's body shader has a
## compute twin): no SubViewport. UndertowBodyEffect marches the body on the game view itself, against
## this frame's opaque depth, and the composite samples its textures and drops each pixel whose opaque
## surface is nearer than what the storm shows there (exact occlusion, inside the volume too).

## The visual layer the body moves to (20; the game camera stops drawing it).
const BODY_LAYER := 1 << 19
const COMPOSITE_SHADER := "res://game/shaders/undertow/undertow_composite.gdshader"

## Fraction of the game view's size the body renders at.
var scale: float = 0.5
## false keeps the SubViewport path even where compute mode is possible (UndertowStorm.half_res_compute).
var allow_compute := true
var viewport: SubViewport
var camera: Camera3D
var composite: MeshInstance3D
var composite_material: ShaderMaterial
## The compute body while in compute mode (else null), on the game camera's Compositor.
var effect: UndertowBodyEffect
var _body: MeshInstance3D
var _connected := false
# The camera whose Compositor holds the effect, and the Compositor we created for it (if we did).
var _effect_camera: Camera3D
var _own_compositor: Compositor


## Builds the SubViewport, its camera and the composite under `host` (a Node3D in the game world).
func setup(host: Node3D, body: MeshInstance3D, render_priority: int) -> void:
	_body = body
	_body.layers = BODY_LAYER
	composite = MeshInstance3D.new()
	composite.name = "HalfResComposite"
	composite.mesh = body.mesh
	composite.transform = body.transform
	composite.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	composite_material = ShaderMaterial.new()
	composite_material.shader = load(COMPOSITE_SHADER) as Shader
	composite_material.render_priority = render_priority
	composite.material_override = composite_material
	host.add_child(composite)
	if not _connected:
		RenderingServer.frame_pre_draw.connect(_sync)
		_connected = true
	if allow_compute and use_compute(body):
		effect = UndertowBodyEffect.new()
		composite_material.set_shader_parameter(&"body_tex", effect.body_texture)
		composite_material.set_shader_parameter(&"front_tex", effect.front_texture)
		composite_material.set_shader_parameter(&"use_front", true)
		return
	viewport = SubViewport.new()
	viewport.name = "HalfResBody"
	viewport.transparent_bg = true
	viewport.use_hdr_2d = true
	viewport.render_target_update_mode = SubViewport.UPDATE_ALWAYS
	camera = Camera3D.new()
	camera.cull_mask = BODY_LAYER
	var env := Environment.new()
	env.background_mode = Environment.BG_CLEAR_COLOR
	env.tonemap_mode = Environment.TONE_MAPPER_LINEAR
	camera.environment = env
	viewport.add_child(camera)
	add_child(viewport)
	camera.current = true
	composite_material.set_shader_parameter(&"body_tex", viewport.get_texture())


## Geometry the composite's occlusion test uses (storm-local wall radius and top).
func set_occluder(center: Vector3, radius_m: float, top_m: float) -> void:
	if composite_material == null:
		return
	composite_material.set_shader_parameter(&"storm_center", center)
	composite_material.set_shader_parameter(&"occluder_radius_m", radius_m)
	composite_material.set_shader_parameter(&"top_m", top_m)


## Whether the body can march as a compute pass here: a RenderingDevice (Forward+ or Mobile, not
## headless or Compatibility) and a compute twin of its shader.
static func use_compute(body: MeshInstance3D) -> bool:
	if RenderingServer.get_rendering_device() == null:
		return false
	var m := body.material_override as ShaderMaterial
	return m != null and m.shader != null and UndertowBodyEffect.compute_path_for(m.shader.resource_path) != ""


func teardown() -> void:
	_detach_effect()
	if effect != null:
		# Stop the dispatch now: the noise lattice may be freed before the effect is. And the composite
		# lets go of the effect's textures before the effect frees them.
		effect.set_frame(PackedByteArray(), "", null, scale)
		if composite_material != null:
			composite_material.set_shader_parameter(&"body_tex", null)
			composite_material.set_shader_parameter(&"front_tex", null)
	effect = null
	if _connected:
		RenderingServer.frame_pre_draw.disconnect(_sync)
		_connected = false
	# Once only: a queue_free()d renderer tears down again in _exit_tree, at the end of the frame, after
	# its replacement may have moved the same body back to BODY_LAYER.
	if _body != null and is_instance_valid(_body):
		_body.layers = 1
	_body = null
	if composite != null and is_instance_valid(composite):
		composite.queue_free()
	if viewport != null and is_instance_valid(viewport):
		viewport.queue_free()
	composite = null
	viewport = null


func _exit_tree() -> void:
	teardown()


func _sync() -> void:
	if (viewport == null and effect == null) or not is_inside_tree():
		return
	var game := get_viewport()
	var cam := game.get_camera_3d()
	if cam == null:
		return
	cam.cull_mask &= ~BODY_LAYER
	if effect != null:
		_sync_effect(cam)
		return
	var want := Vector2i(
		maxi(1, roundi(game.get_visible_rect().size.x * scale)), maxi(1, roundi(game.get_visible_rect().size.y * scale))
	)
	if viewport.size != want:
		viewport.size = want
	viewport.use_taa = false
	camera.global_transform = cam.global_transform
	camera.projection = cam.projection
	camera.fov = cam.fov
	camera.size = cam.size
	camera.near = cam.near
	camera.far = cam.far
	camera.keep_aspect = cam.keep_aspect
	camera.h_offset = cam.h_offset
	camera.v_offset = cam.v_offset


func _sync_effect(cam: Camera3D) -> void:
	if cam != _effect_camera:
		_detach_effect()
		_effect_camera = cam
	# Checked every frame, so camera code that replaces the camera's Compositor can't drop the storm.
	if cam.compositor == null:
		_own_compositor = Compositor.new()
		cam.compositor = _own_compositor
	if not cam.compositor.compositor_effects.has(effect):
		var effects := cam.compositor.compositor_effects
		effects.append(effect)
		cam.compositor.compositor_effects = effects
	var m := _body.material_override as ShaderMaterial
	if m == null or m.shader == null or not _body.is_visible_in_tree():
		effect.set_frame(PackedByteArray(), "", null, scale)
		return
	var noise := m.get_shader_parameter(&"noise_tex") as Texture3D
	var sun := ShaderGlobals.get_value(&"hymn_sun_direction", Vector3.UP) as Vector3
	effect.set_frame(
		UndertowBodyEffect.pack(m, sun), UndertowBodyEffect.compute_path_for(m.shader.resource_path), noise, scale
	)


func _detach_effect() -> void:
	if _effect_camera == null or not is_instance_valid(_effect_camera):
		_effect_camera = null
		return
	if _effect_camera.compositor != null:
		if _effect_camera.compositor == _own_compositor:
			_effect_camera.compositor = null
		else:
			var effects := _effect_camera.compositor.compositor_effects
			effects.erase(effect)
			_effect_camera.compositor.compositor_effects = effects
	_effect_camera = null
	_own_compositor = null
