extends Node
## QA-10 isolated repro of the Godot 4.6.3 RenderingDevice race: render_pipeline_create() reads
## `vertex_formats` (HashMap, non-const operator[]) outside the RD lock, while vertex_format_create()
## inserts into it under the lock. A worker thread creates pipelines with one fixed vertex format
## (location 0 present); the main thread keeps creating new, unique vertex formats.
## Usage: godot-render --path <this dir> -- --formats=N --mode=race|serial

const VS := """
#version 450
layout(location = 0) in vec3 pos;
void main() { gl_Position = vec4(pos, 1.0); }
"""
const FS := """
#version 450
layout(location = 0) out vec4 col;
void main() { col = vec4(1.0); }
"""

var _rd: RenderingDevice
var _shader: RID
var _fb_fmt: int
var _vfmt: int
var _stop := false
var _ok := 0
var _bad := 0
## fast: an out-of-range primitive makes render_pipeline_create fail right AFTER the vertex-format
## lookup and validation, so the worker hammers the racy lookup without compiling a pipeline.
var _prim := RenderingDevice.RENDER_PRIMITIVE_TRIANGLES
var _forced := false
var _ready_flag := false


func _ready() -> void:
	var formats := 20000
	var mode := "race"
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--formats="):
			formats = int(a.get_slice("=", 1))
		elif a.begins_with("--mode="):
			mode = a.get_slice("=", 1)
	_rd = RenderingServer.create_local_rendering_device()
	var src := RDShaderSource.new()
	src.source_vertex = VS
	src.source_fragment = FS
	var spirv := _rd.shader_compile_spirv_from_source(src)
	_shader = _rd.shader_create_from_spirv(spirv)
	var att := RDAttachmentFormat.new()
	att.format = RenderingDevice.DATA_FORMAT_R8G8B8A8_UNORM
	att.usage_flags = RenderingDevice.TEXTURE_USAGE_COLOR_ATTACHMENT_BIT
	_fb_fmt = _rd.framebuffer_format_create([att])
	_vfmt = _rd.vertex_format_create([_attr(12)])
	print("QA10 race setup shader=%s fb=%d vfmt=%d mode=%s formats=%d" % [_shader.is_valid(), _fb_fmt, _vfmt, mode, formats])
	if mode == "fast" or mode == "forced":
		_prim = 1000
	if mode == "forced":
		# for race_force.py: start the inserts only once the worker is about to look up
		_forced = true
	if mode != "serial":
		mode = "race"
	var t := Thread.new()
	if mode == "race":
		t.start(_pipelines)
	while _forced and not _ready_flag:
		OS.delay_usec(10)
	var t0 := Time.get_ticks_msec()
	var last := 0
	for i in formats:
		last = _rd.vertex_format_create([_attr(16 + i * 4)])
	print("QA10 created formats in %d ms, last id %d (first %d)" % [Time.get_ticks_msec() - t0, last, _vfmt])
	_stop = true
	if mode == "race":
		t.wait_to_finish()
	else:
		_stop = false
		_pipelines_n(2000)
	print("QA10 race done: pipelines ok=%d failed=%d" % [_ok, _bad])
	# RD shutdown frees every vertex format, including a default-inserted one (driver_id 0)
	print("QA10 freeing the local RenderingDevice")
	_rd.free()
	print("QA10 local RenderingDevice freed")
	get_tree().quit(0)


func _attr(stride: int) -> RDVertexAttribute:
	var a := RDVertexAttribute.new()
	a.location = 0
	a.format = RenderingDevice.DATA_FORMAT_R32G32B32_SFLOAT
	a.stride = stride
	return a


func _pipelines() -> void:
	_ready_flag = true
	while not _stop:
		_one()


func _pipelines_n(n: int) -> void:
	for i in n:
		_one()


func _one() -> void:
	var blend := RDPipelineColorBlendState.new()
	blend.attachments = [RDPipelineColorBlendStateAttachment.new()]
	var p := _rd.render_pipeline_create(
		_shader,
		_fb_fmt,
		_vfmt,
		_prim as RenderingDevice.RenderPrimitive,
		RDPipelineRasterizationState.new(),
		RDPipelineMultisampleState.new(),
		RDPipelineDepthStencilState.new(),
		blend
	)
	if p.is_valid():
		_ok += 1
		_rd.free_rid(p)
	else:
		_bad += 1
