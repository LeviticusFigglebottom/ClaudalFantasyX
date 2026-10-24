class_name WaveParityProbe
extends Node
## GPU/CPU parity check for the Gerstner waves (M1-RND-01). Needs a real renderer (godot-render,
## ADR 0009); tests/unit/test_water_waves.gd runs it as a subprocess when the wrapper exists:
##   godot-render --path . --audio-driver Dummy res://game/levels/_tests/water/wave_parity_probe.tscn
## Renders water_wave_probe.gdshader (the same include as the ocean shader) into a float viewport,
## reads it back and compares every pixel with GerstnerWaves. Prints one line
##   PARITY ok=<bool> samples=<n> disp_err_m=<max> normal_err=<max> jacobian_err=<max>
## and quits with exit code 0 (ok) or 1.

const PROBE_SHADER := "res://game/shaders/water/test/water_wave_probe.gdshader"
const WAVES := "res://game/world/water/lagoon_waves.tres"
const GRID := Vector2i(64, 16)
const ORIGIN_M := Vector2(-37.25, 12.5)
const SPACING_M := 1.37
## A late, awkward time: large phase arguments are where float32 drifts first.
const TIME_S := 1234.567
## RGBA16F readback keeps 11 mantissa bits (~1e-3 relative); amplitudes are < 0.5 m.
const DISP_TOLERANCE_M := 2e-3
const NORMAL_TOLERANCE := 4e-3
const JACOBIAN_TOLERANCE := 4e-3
const SETTLE_FRAMES := 3


func _ready() -> void:
	_run.call_deferred()


func _run() -> void:
	if DisplayServer.get_name() == "headless":
		print("PARITY skipped: needs a real renderer (godot-render)")
		get_tree().quit(2)
		return
	var waves := GerstnerWaves.from_set(load(WAVES) as WaveSet)
	var disp_img := await _render(waves, 0)
	var frame_img := await _render(waves, 1)
	var disp_err := 0.0
	var normal_err := 0.0
	var jac_err := 0.0
	for y in GRID.y:
		for x in GRID.x:
			var p0 := ORIGIN_M + Vector2(x, y) * SPACING_M
			var d := waves.displacement(p0, TIME_S)
			var c := disp_img.get_pixel(x, y)
			disp_err = maxf(disp_err, (Vector3(c.r, c.g, c.b) - d).length())
			var f := frame_img.get_pixel(x, y)
			normal_err = maxf(normal_err, (Vector3(f.r, f.g, f.b) - waves.normal(p0, TIME_S)).length())
			jac_err = maxf(jac_err, absf(f.a - waves.jacobian(p0, TIME_S)))
	var ok := disp_err <= DISP_TOLERANCE_M and normal_err <= NORMAL_TOLERANCE and jac_err <= JACOBIAN_TOLERANCE
	print(
		(
			"PARITY ok=%s samples=%d disp_err_m=%.6f normal_err=%.6f jacobian_err=%.6f"
			% [ok, GRID.x * GRID.y, disp_err, normal_err, jac_err]
		)
	)
	get_tree().quit(0 if ok else 1)


func _render(waves: GerstnerWaves, channel: int) -> Image:
	var vp := SubViewport.new()
	vp.size = GRID
	vp.use_hdr_2d = true
	vp.transparent_bg = true
	vp.render_target_update_mode = SubViewport.UPDATE_ALWAYS
	var rect := ColorRect.new()
	rect.size = Vector2(GRID)
	var mat := ShaderMaterial.new()
	mat.shader = load(PROBE_SHADER) as Shader
	var params := waves.shader_parameters()
	for key: StringName in params:
		mat.set_shader_parameter(key, params[key])
	mat.set_shader_parameter(&"origin_m", ORIGIN_M)
	mat.set_shader_parameter(&"spacing_m", SPACING_M)
	mat.set_shader_parameter(&"time_s", TIME_S)
	mat.set_shader_parameter(&"channel", channel)
	rect.material = mat
	vp.add_child(rect)
	add_child(vp)
	for i in SETTLE_FRAMES:
		await RenderingServer.frame_post_draw
	var img := vp.get_texture().get_image()
	img.convert(Image.FORMAT_RGBAF)
	vp.queue_free()
	return img
