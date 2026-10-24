class_name UndertowBodyEffect
extends CompositorEffect
## The Undertow's raymarched body as a compute pass on the game view (M2-RND-01). Docs: undertow.md,
## "Compute body". UndertowHalfRes adds it to the game camera's Compositor.
## - It runs after the opaque pass (PRE_TRANSPARENT), at `scale` of the internal resolution.
## - It marches the same undertow_march() as the spatial body, against THIS frame's opaque depth, so the
##   storm is occluded exactly, inside the volume too.
## - It writes body_texture (premultiplied colour) and front_texture (the mean distance of what each ray
##   saw). The composite (undertow_composite.gdshader) samples both in the transparent pass, so the storm
##   still sorts after the water.
## The main thread hands over each frame's uniforms with set_frame(), packed by pack(). The view members
## (projection, camera, sizes) are written on the render thread from the frame's own scene data.

## The compute twin of a body shader: res://.../undertow_body_x.gdshader -> undertow_body_x_compute.glsl.
const COMPUTE_SUFFIX := "_compute.glsl"
const GROUP_SIZE := 8
const FMT_BODY := RenderingDevice.DATA_FORMAT_R16G16B16A16_SFLOAT
const FMT_FRONT := RenderingDevice.DATA_FORMAT_R32_SFLOAT

## Compute shaders and pipelines created ahead of the first storm frame (M1-RND-27, ShaderPrewarm
## "compute_twin"): path -> [shader RID, pipeline RID] on the main RenderingDevice, held for the session.
static var _warm: Dictionary = {}
## Warm shaders release_warm() has freed (M2-RND-11): an effect still holding one must not free it again.
static var _released: Dictionary = {}

## The textures the composite samples. Their RIDs are (re)set on the render thread when the size changes.
var body_texture := Texture2DRD.new()
var front_texture := Texture2DRD.new()

var _mutex := Mutex.new()
# Main-thread hand-over (under _mutex).
var _next_params := PackedByteArray()
var _next_shader := ""
# Held, not just its RID, so the lattice can't be freed while a frame may still dispatch with it.
var _next_noise: Texture3D
var _next_scale := 0.5
# Render-thread state.
var _rd: RenderingDevice
var _shader := RID()
var _pipeline := RID()
var _shader_path := ""
var _ubo := RID()
var _sampler_noise := RID()
var _sampler_depth := RID()
var _tex_body := RID()
var _tex_front := RID()
var _size := Vector2i.ZERO
var _offsets := {}


func _init() -> void:
	effect_callback_type = EFFECT_CALLBACK_TYPE_PRE_TRANSPARENT
	for row: Array in UndertowComputeLayout.FIELDS:
		_offsets[row[0]] = int(row[2])
	RenderingServer.call_on_render_thread(_init_render)


func _notification(what: int) -> void:
	if what == NOTIFICATION_PREDELETE and _rd != null:
		# Detach the Texture2DRDs first: a material still sampling a freed RD texture fails to rebuild
		# its uniform set ("Texture (binding: 1, index 0) is not a valid texture").
		body_texture.texture_rd_rid = RID()
		front_texture.texture_rd_rid = RID()
		for rid: RID in [_tex_body, _tex_front, _ubo, _sampler_noise, _sampler_depth, _shader]:
			# A warm pipeline (M1-RND-27) is held for the session, not by this effect.
			if rid.is_valid() and not (rid == _shader and (_owns_warm(rid) or _released.has(rid))):
				_rd.free_rid(rid)


## The compute shader for a spatial body shader path ("" when it has no twin on disk).
static func compute_path_for(body_shader_path: String) -> String:
	if not body_shader_path.ends_with(".gdshader"):
		return ""
	var path := body_shader_path.trim_suffix(".gdshader") + COMPUTE_SUFFIX
	return path if ResourceLoader.exists(path) else ""


## Packs `material`'s uniforms into the std140 block (UndertowComputeLayout); an unset uniform takes its
## declaration's default. `sun_dir` fills hymn_sun_direction. The view members are left for the render
## thread.
static func pack(material: ShaderMaterial, sun_dir: Vector3) -> PackedByteArray:
	var out := PackedByteArray()
	out.resize(UndertowComputeLayout.SIZE)
	for row: Array in UndertowComputeLayout.FIELDS:
		var name := str(row[0])
		if name.begins_with("view_"):
			continue
		var value: Variant = sun_dir if name == "hymn_sun_direction" else material.get_shader_parameter(name)
		if value == null:
			value = row[4]
		_put(out, str(row[1]), int(row[2]), int(row[3]), value, bool(row[5]))
	return out


## Main thread: this frame's uniforms, compute shader, noise lattice and resolution fraction.
func set_frame(params: PackedByteArray, shader_path: String, noise: Texture3D, scale: float) -> void:
	_mutex.lock()
	_next_params = params
	_next_shader = shader_path
	_next_noise = noise
	_next_scale = scale
	_mutex.unlock()


func _render_callback(callback_type: int, render_data: RenderData) -> void:
	if _rd == null or callback_type != EFFECT_CALLBACK_TYPE_PRE_TRANSPARENT:
		return
	var buffers := render_data.get_render_scene_buffers() as RenderSceneBuffersRD
	var scene := render_data.get_render_scene_data()
	if buffers == null or scene == null:
		return
	_mutex.lock()
	var params := _next_params
	var path := _next_shader
	var noise_tex := _next_noise
	var scale := _next_scale
	_mutex.unlock()
	if params.size() != UndertowComputeLayout.SIZE or path == "" or noise_tex == null:
		return
	if not _ensure_pipeline(path):
		return
	var noise := RenderingServer.texture_get_rd_texture(noise_tex.get_rid())
	# At a scene change or quit the lattice or the depth can be gone for a frame before we hear of it.
	if not noise.is_valid() or not _rd.texture_is_valid(noise):
		return
	var internal := buffers.get_internal_size()
	var size := Vector2i(maxi(1, ceili(internal.x * scale)), maxi(1, ceili(internal.y * scale)))
	_ensure_targets(size)
	var bytes := params.duplicate()
	# The projection the depth buffer was rendered with. RenderSceneData's camera projection already
	# carries Godot's depth correction (reverse-Z, the flipped Y), so it is the spatial shaders'
	# PROJECTION_MATRIX as is; correcting it again turned every ray around.
	var proj := scene.get_cam_projection()
	_put(bytes, "mat4", _offsets["view_inv_projection"], 0, proj.inverse(), false)
	_put(bytes, "mat4", _offsets["view_camera"], 0, Projection(scene.get_cam_transform()), false)
	_put(bytes, "vec2", _offsets["view_out_size"], 0, Vector2(size), false)
	_put(bytes, "vec2", _offsets["view_depth_size"], 0, Vector2(internal), false)
	_rd.buffer_update(_ubo, 0, bytes.size(), bytes)
	var depth := buffers.get_depth_layer(0)
	if not depth.is_valid() or not _rd.texture_is_valid(depth):
		return
	var uniforms: Array[RDUniform] = [
		_uniform(RenderingDevice.UNIFORM_TYPE_UNIFORM_BUFFER, 0, [_ubo]),
		_uniform(RenderingDevice.UNIFORM_TYPE_SAMPLER_WITH_TEXTURE, 1, [_sampler_noise, noise]),
		_uniform(RenderingDevice.UNIFORM_TYPE_SAMPLER_WITH_TEXTURE, 2, [_sampler_depth, depth]),
		_uniform(RenderingDevice.UNIFORM_TYPE_IMAGE, 3, [_tex_body]),
		_uniform(RenderingDevice.UNIFORM_TYPE_IMAGE, 4, [_tex_front]),
	]
	var uniform_set := UniformSetCacheRD.get_cache(_shader, 0, uniforms)
	var list := _rd.compute_list_begin()
	_rd.compute_list_bind_compute_pipeline(list, _pipeline)
	_rd.compute_list_bind_uniform_set(list, uniform_set, 0)
	_rd.compute_list_dispatch(list, ceili(size.x / float(GROUP_SIZE)), ceili(size.y / float(GROUP_SIZE)), 1)
	_rd.compute_list_end()


func _init_render() -> void:
	_rd = RenderingServer.get_rendering_device()
	if _rd == null:
		return
	_ubo = _rd.uniform_buffer_create(UndertowComputeLayout.SIZE)
	var s := RDSamplerState.new()
	s.min_filter = RenderingDevice.SAMPLER_FILTER_LINEAR
	s.mag_filter = RenderingDevice.SAMPLER_FILTER_LINEAR
	s.repeat_u = RenderingDevice.SAMPLER_REPEAT_MODE_REPEAT
	s.repeat_v = RenderingDevice.SAMPLER_REPEAT_MODE_REPEAT
	s.repeat_w = RenderingDevice.SAMPLER_REPEAT_MODE_REPEAT
	_sampler_noise = _rd.sampler_create(s)
	var d := RDSamplerState.new()
	d.min_filter = RenderingDevice.SAMPLER_FILTER_NEAREST
	d.mag_filter = RenderingDevice.SAMPLER_FILTER_NEAREST
	_sampler_depth = _rd.sampler_create(d)


## Creates the compute pipeline for `path` on the main RenderingDevice and holds it, so a storm's first
## frame finds it ready (M1-RND-27). Call on the render thread (RenderingServer.call_on_render_thread).
static func warm_pipeline(path: String) -> bool:
	if _warm.has(path):
		return true
	var rd := RenderingServer.get_rendering_device()
	var file := load(path) as RDShaderFile if rd != null else null
	if file == null:
		return false
	var spirv := file.get_spirv()
	if spirv.compile_error_compute != "":
		push_error("UndertowBodyEffect: %s: %s" % [path, spirv.compile_error_compute])
		return false
	var shader := rd.shader_create_from_spirv(spirv)
	var pipeline := rd.compute_pipeline_create(shader)
	if not pipeline.is_valid():
		rd.free_rid(shader)
		return false
	_warm[path] = [shader, pipeline]
	return true


## Frees every warm shader (and so its pipeline) on the main RenderingDevice, at exit (M2-RND-11):
## ShaderPrewarm's resident holder calls it as the tree frees it, so nothing static outlives the
## renderer. Call on the render thread.
static func release_warm() -> void:
	var rd := RenderingServer.get_rendering_device()
	for pair: Array in _warm.values():
		var shader: RID = pair[0]
		if rd != null and shader.is_valid():
			rd.free_rid(shader)
			_released[shader] = true
	_warm.clear()


## Whether `path`'s compute pipeline is held warm (tests, the prewarm bench).
static func is_warm(path: String) -> bool:
	return _warm.has(path)


func _ensure_pipeline(path: String) -> bool:
	if path == _shader_path and _pipeline.is_valid():
		return true
	if _shader.is_valid() and not _owns_warm(_shader) and not _released.has(_shader):
		_rd.free_rid(_shader)  # frees its pipeline too
	if _warm.has(path):
		_shader = (_warm[path] as Array)[0]
		_pipeline = (_warm[path] as Array)[1]
		_shader_path = path
		return true
	var file := load(path) as RDShaderFile
	if file == null:
		return false
	var spirv := file.get_spirv()
	if spirv.compile_error_compute != "":
		push_error("UndertowBodyEffect: %s: %s" % [path, spirv.compile_error_compute])
		return false
	_shader = _rd.shader_create_from_spirv(spirv)
	_pipeline = _rd.compute_pipeline_create(_shader)
	_shader_path = path
	return _pipeline.is_valid()


static func _owns_warm(shader: RID) -> bool:
	for pair: Array in _warm.values():
		if pair[0] == shader:
			return true
	return false


func _ensure_targets(size: Vector2i) -> void:
	if size == _size and _tex_body.is_valid():
		return
	for rid: RID in [_tex_body, _tex_front]:
		if rid.is_valid():
			_rd.free_rid(rid)
	_tex_body = _target(size, FMT_BODY)
	_tex_front = _target(size, FMT_FRONT)
	_size = size
	# Texture2DRD's RID is set on the main thread (as Godot's compute-texture demo does): assigned here,
	# on the render thread, the material kept sampling the placeholder.
	body_texture.set_deferred(&"texture_rd_rid", _tex_body)
	front_texture.set_deferred(&"texture_rd_rid", _tex_front)


func _target(size: Vector2i, format: RenderingDevice.DataFormat) -> RID:
	var f := RDTextureFormat.new()
	f.format = format
	f.width = size.x
	f.height = size.y
	f.usage_bits = RenderingDevice.TEXTURE_USAGE_STORAGE_BIT | RenderingDevice.TEXTURE_USAGE_SAMPLING_BIT
	return _rd.texture_create(f, RDTextureView.new())


static func _uniform(type: RenderingDevice.UniformType, binding: int, ids: Array[RID]) -> RDUniform:
	var u := RDUniform.new()
	u.uniform_type = type
	u.binding = binding
	for id in ids:
		u.add_id(id)
	return u


static func _put(out: PackedByteArray, type: String, offset: int, count: int, value: Variant, srgb: bool) -> void:
	match type:
		"float":
			out.encode_float(offset, float(value))
		"int":
			out.encode_s32(offset, int(value))
		"vec2":
			var v2 := value as Vector2
			out.encode_float(offset, v2.x)
			out.encode_float(offset + 4, v2.y)
		"vec3":
			var v3 := Vector3.ZERO
			if value is Color:
				var c := (value as Color).srgb_to_linear() if srgb else value as Color
				v3 = Vector3(c.r, c.g, c.b)
			else:
				v3 = value as Vector3
			out.encode_float(offset, v3.x)
			out.encode_float(offset + 4, v3.y)
			out.encode_float(offset + 8, v3.z)
		"vec4":
			var items: Array = []
			if count == 0:
				items = [value]
			elif value is PackedVector4Array or value is Array:
				items = Array(value)
			for i in mini(maxi(count, 1), items.size()):
				var v4 := items[i] as Vector4
				for k in 4:
					out.encode_float(offset + 16 * i + 4 * k, v4[k])
		"mat4":
			var m := value as Projection
			for col in 4:
				for row in 4:
					out.encode_float(offset + 16 * col + 4 * row, m[col][row])
