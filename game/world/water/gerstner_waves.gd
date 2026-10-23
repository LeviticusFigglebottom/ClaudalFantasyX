class_name GerstnerWaves
extends RefCounted
## CPU mirror of game/shaders/water/water_waves.gdshaderinc (M1-RND-01). Change both together:
## tests/unit/test_water_waves.gd checks the constants and the maths, and
## game/levels/_tests/water/wave_parity_probe.tscn compares this class with the shader on a real
## renderer (the unit test runs it when the software renderer is installed).
##
## pack() turns a WaveSet into per-wave constants laid out exactly as the shader uniforms:
##   wave_a[i] = (dir.x, dir.z, k, omega)   wave_b[i] = (amplitude_m, horiz_m, phase_rad, 0)
## with k = TAU / wavelength, omega = sqrt(g k), horiz = steepness / (k N). Positions are world XZ
## metres, heights are metres relative to the water node's rest plane, time is hymn_wind_time.

## Mirrors HYMN_WATER_MAX_WAVES in the shader include.
const MAX_WAVES := 8
## Standard gravity (m/s^2), for the deep-water dispersion relation omega^2 = g k.
const GRAVITY := 9.80665
## Fixed-point iterations to find the rest point under a world position. The horizontal map is a
## contraction with factor <= mean steepness, so 8 steps reach < 1 mm even at steepness 0.8.
const INVERT_ITERATIONS := 8
## Shader uniform names (WaterSurface writes these).
const UNIFORM_A := &"water_wave_a"
const UNIFORM_B := &"water_wave_b"
const UNIFORM_COUNT := &"water_wave_count"
const UNIFORM_AMPLITUDE_SUM := &"water_amplitude_sum"

var wave_a := PackedVector4Array()
var wave_b := PackedVector4Array()
var amplitude_sum: float = 0.0


static func from_set(wave_set: WaveSet) -> GerstnerWaves:
	var w := GerstnerWaves.new()
	if wave_set == null:
		return w
	var comps: Array[WaveComponent] = []
	for c in wave_set.components:
		if c != null and comps.size() < MAX_WAVES:
			comps.append(c)
	if wave_set.components.size() > MAX_WAVES:
		push_warning("WaveSet has %d components; only the first %d are used" % [wave_set.components.size(), MAX_WAVES])
	var n := float(maxi(comps.size(), 1))
	for c in comps:
		var rad := deg_to_rad(c.direction_deg)
		var dir := Vector2(sin(rad), -cos(rad))
		var k := TAU / c.wavelength_m
		var omega := sqrt(GRAVITY * k)
		var amp := c.amplitude_m * wave_set.amplitude_scale
		var horiz := c.steepness / (k * n)
		w.wave_a.append(Vector4(dir.x, dir.y, k, omega))
		w.wave_b.append(Vector4(amp, horiz, c.phase_rad, 0.0))
		w.amplitude_sum += amp
	return w


func count() -> int:
	return wave_a.size()


## Shader parameters, zero-padded to MAX_WAVES (the uniform arrays are fixed-size).
func shader_parameters() -> Dictionary:
	var a := wave_a.duplicate()
	var b := wave_b.duplicate()
	a.resize(MAX_WAVES)
	b.resize(MAX_WAVES)
	return {
		UNIFORM_A: a,
		UNIFORM_B: b,
		UNIFORM_COUNT: count(),
		UNIFORM_AMPLITUDE_SUM: maxf(amplitude_sum, 0.0),
	}


## Displacement of the rest point p0 at time t (no LOD fade: gameplay sees the full field).
func displacement(p0: Vector2, t: float) -> Vector3:
	var d := Vector3.ZERO
	for i in wave_a.size():
		var a := wave_a[i]
		var b := wave_b[i]
		var theta := a.z * (a.x * p0.x + a.y * p0.y) - a.w * t + b.z
		var s := sin(theta)
		d.x -= b.y * a.x * s
		d.z -= b.y * a.y * s
		d.y += b.x * cos(theta)
	return d


## Analytic surface normal at the rest point p0 (same formula as the shader).
func normal(p0: Vector2, t: float) -> Vector3:
	var f := _frame(p0, t)
	return f[0]


## Horizontal Jacobian at the rest point p0: 1 = undisturbed, < 1 = compressed (crest foam).
func jacobian(p0: Vector2, t: float) -> float:
	var f := _frame(p0, t)
	return f[1]


## The rest point whose displaced position lies above (or below) world XZ point xz.
func rest_point(xz: Vector2, t: float) -> Vector2:
	var p0 := xz
	for i in INVERT_ITERATIONS:
		var d := displacement(p0, t)
		p0 = xz - Vector2(d.x, d.z)
	return p0


## Surface height (m, relative to the rest plane) at world XZ point xz and time t.
func height_at(xz: Vector2, t: float) -> float:
	return displacement(rest_point(xz, t), t).y


## Surface normal at world XZ point xz and time t.
func normal_at(xz: Vector2, t: float) -> Vector3:
	return normal(rest_point(xz, t), t)


# Returns [normal: Vector3, jacobian: float].
func _frame(p0: Vector2, t: float) -> Array:
	var jxx := 1.0
	var jzz := 1.0
	var jxz := 0.0
	var dhx := 0.0
	var dhz := 0.0
	for i in wave_a.size():
		var a := wave_a[i]
		var b := wave_b[i]
		var theta := a.z * (a.x * p0.x + a.y * p0.y) - a.w * t + b.z
		var wa := b.y * a.z * cos(theta)
		jxx -= wa * a.x * a.x
		jzz -= wa * a.y * a.y
		jxz -= wa * a.x * a.y
		var wh := b.x * a.z * sin(theta)
		dhx -= wh * a.x
		dhz -= wh * a.y
	var tx := Vector3(jxx, dhx, jxz)
	var tz := Vector3(jxz, dhz, jzz)
	return [tz.cross(tx).normalized(), jxx * jzz - jxz * jxz]
