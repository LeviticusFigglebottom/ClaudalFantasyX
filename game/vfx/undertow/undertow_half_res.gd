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

## The visual layer the body moves to (20; the game camera stops drawing it).
const BODY_LAYER := 1 << 19
const COMPOSITE_SHADER := "res://game/shaders/undertow/undertow_composite.gdshader"

## Fraction of the game view's size the body renders at.
var scale: float = 0.5
var viewport: SubViewport
var camera: Camera3D
var composite: MeshInstance3D
var composite_material: ShaderMaterial
var _body: MeshInstance3D
var _connected := false


## Builds the SubViewport, its camera and the composite under `host` (a Node3D in the game world).
func setup(host: Node3D, body: MeshInstance3D, render_priority: int) -> void:
	_body = body
	_body.layers = BODY_LAYER
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
	composite = MeshInstance3D.new()
	composite.name = "HalfResComposite"
	composite.mesh = body.mesh
	composite.transform = body.transform
	composite.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	composite_material = ShaderMaterial.new()
	composite_material.shader = load(COMPOSITE_SHADER) as Shader
	composite_material.render_priority = render_priority
	composite_material.set_shader_parameter(&"body_tex", viewport.get_texture())
	composite.material_override = composite_material
	host.add_child(composite)
	if not _connected:
		RenderingServer.frame_pre_draw.connect(_sync)
		_connected = true


## Geometry the composite's occlusion test uses (storm-local wall radius and top).
func set_occluder(center: Vector3, radius_m: float, top_m: float) -> void:
	if composite_material == null:
		return
	composite_material.set_shader_parameter(&"storm_center", center)
	composite_material.set_shader_parameter(&"occluder_radius_m", radius_m)
	composite_material.set_shader_parameter(&"top_m", top_m)


func teardown() -> void:
	if _connected:
		RenderingServer.frame_pre_draw.disconnect(_sync)
		_connected = false
	if _body != null and is_instance_valid(_body):
		_body.layers = 1
	if composite != null and is_instance_valid(composite):
		composite.queue_free()
	if viewport != null and is_instance_valid(viewport):
		viewport.queue_free()
	composite = null
	viewport = null


func _exit_tree() -> void:
	teardown()


func _sync() -> void:
	if viewport == null or not is_inside_tree():
		return
	var game := get_viewport()
	var cam := game.get_camera_3d()
	if cam == null:
		return
	cam.cull_mask &= ~BODY_LAYER
	var want := Vector2i(
		maxi(1, roundi(game.get_visible_rect().size.x * scale)), maxi(1, roundi(game.get_visible_rect().size.y * scale))
	)
	if viewport.size != want:
		viewport.size = want
		composite_material.set_shader_parameter(&"body_texel", Vector2(1.0 / want.x, 1.0 / want.y))
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
