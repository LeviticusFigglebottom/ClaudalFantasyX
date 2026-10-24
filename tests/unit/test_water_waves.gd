extends TestCase
## M1-RND-01: GerstnerWaves (the CPU mirror of water_waves.gdshaderinc), the height query, and
## GPU parity. The parity test runs game/levels/_tests/water/wave_parity_probe.tscn through the
## software renderer when it is installed (ADR 0009) and is skipped (passes) otherwise.

const WAVES_INC := "res://game/shaders/water/water_waves.gdshaderinc"
const LAGOON_WAVES := "res://game/world/water/lagoon_waves.tres"
const PROBE_SCENE := "res://game/levels/_tests/water/wave_parity_probe.tscn"
const RENDER_WRAPPER := "~/.cache/hymn/godot-4.6.3+ds-2/godot-render"
## Vector3/Vector4 store float32, so packed constants are exact to ~1e-7 relative.
const EPS := 1e-6
const HEIGHT_TOLERANCE_M := 1e-4
const FD_STEP_M := 2e-3
const FD_TOLERANCE := 1e-3
const SAMPLE_COUNT := 64
const SAMPLE_RANGE_M := 80.0
const SAMPLE_TIME_S := 37.5


func _wave(dir_deg: float, length_m: float, amp_m: float, steep: float, phase: float = 0.0) -> WaveComponent:
	var c := WaveComponent.new()
	c.direction_deg = dir_deg
	c.wavelength_m = length_m
	c.amplitude_m = amp_m
	c.steepness = steep
	c.phase_rad = phase
	return c


func _wave_set(comps: Array[WaveComponent]) -> WaveSet:
	var s := WaveSet.new()
	s.components = comps
	return s


func _lagoon() -> GerstnerWaves:
	return GerstnerWaves.from_set(load(LAGOON_WAVES) as WaveSet)


func _points() -> Array[Vector2]:
	var rng := RandomNumberGenerator.new()
	rng.seed = 20261022
	var pts: Array[Vector2] = []
	for i in SAMPLE_COUNT:
		pts.append(
			Vector2(rng.randf_range(-SAMPLE_RANGE_M, SAMPLE_RANGE_M), rng.randf_range(-SAMPLE_RANGE_M, SAMPLE_RANGE_M))
		)
	return pts


# --- Shader/CPU contract --------------------------------------------------------------------


func test_constants_and_uniform_names_match_the_shader_include() -> void:
	var src := FileAccess.get_file_as_string(WAVES_INC)
	assert_true(src.contains("#define HYMN_WATER_MAX_WAVES %d" % GerstnerWaves.MAX_WAVES), "MAX_WAVES drifted")
	for u: StringName in [
		GerstnerWaves.UNIFORM_A,
		GerstnerWaves.UNIFORM_B,
		GerstnerWaves.UNIFORM_COUNT,
		GerstnerWaves.UNIFORM_AMPLITUDE_SUM
	]:
		assert_true(src.contains("uniform") and src.contains(String(u)), "include lacks uniform %s" % u)
	# The two sides must use the same phase, displacement and Jacobian expressions.
	for expr in [
		"a.z * dot(a.xy, p0) - a.w * t + b.z",
		"disp.xz += -horiz * a.xy * s;",
		"disp.y += amp * c;",
		"normal = normalize(cross(tz, tx));",
		"jacobian = jxx * jzz - jxz * jxz;",
	]:
		assert_true(src.contains(expr), "shader expression changed, update GerstnerWaves too: %s" % expr)


func test_pack_follows_compass_convention_and_dispersion() -> void:
	var w := GerstnerWaves.from_set(_wave_set([_wave(90.0, 10.0, 0.2, 0.5), _wave(180.0, 40.0, 0.4, 1.0, 1.25)]))
	assert_eq(w.count(), 2)
	var a0 := w.wave_a[0]
	assert_between(a0.x, 1.0 - 1e-6, 1.0 + 1e-6, "azimuth 90 travels east (+X)")
	assert_between(a0.y, -1e-6, 1e-6)
	var a1 := w.wave_a[1]
	assert_between(a1.y, 1.0 - 1e-6, 1.0 + 1e-6, "azimuth 180 travels south (+Z)")
	var k := TAU / 10.0
	assert_between(a0.z, k - EPS, k + EPS)
	var omega := sqrt(GerstnerWaves.GRAVITY * k)
	assert_between(a0.w, omega - EPS, omega + EPS, "deep-water dispersion")
	var horiz := 0.5 / (k * 2.0)
	assert_between(w.wave_b[0].y, horiz - EPS, horiz + EPS, "horiz = steepness / (k N)")
	assert_between(w.wave_b[1].z, 1.25 - EPS, 1.25 + EPS, "phase passes through")
	assert_between(w.amplitude_sum, 0.6 - EPS, 0.6 + EPS)


func test_shader_parameters_pad_to_max_and_cap_extra_waves() -> void:
	var comps: Array[WaveComponent] = []
	for i in GerstnerWaves.MAX_WAVES + 3:
		comps.append(_wave(i * 30.0, 5.0 + i, 0.01, 0.3))
	var w := GerstnerWaves.from_set(_wave_set(comps))
	assert_eq(w.count(), GerstnerWaves.MAX_WAVES, "extra components are dropped")
	var few := GerstnerWaves.from_set(_wave_set([_wave(0.0, 5.0, 0.1, 0.3)]))
	var p := few.shader_parameters()
	assert_eq((p[GerstnerWaves.UNIFORM_A] as PackedVector4Array).size(), GerstnerWaves.MAX_WAVES)
	assert_eq((p[GerstnerWaves.UNIFORM_B] as PackedVector4Array).size(), GerstnerWaves.MAX_WAVES)
	assert_eq(p[GerstnerWaves.UNIFORM_COUNT], 1)
	assert_eq((p[GerstnerWaves.UNIFORM_A] as PackedVector4Array)[3], Vector4.ZERO, "padding is zero")


func test_amplitude_scale_scales_heights_not_steepness() -> void:
	var s := _wave_set([_wave(45.0, 12.0, 0.3, 0.6)])
	s.amplitude_scale = 0.5
	var w := GerstnerWaves.from_set(s)
	assert_between(w.wave_b[0].x, 0.15 - EPS, 0.15 + EPS)
	var k := TAU / 12.0
	assert_between(w.wave_b[0].y, 0.6 / k - EPS, 0.6 / k + EPS)


# --- Maths ----------------------------------------------------------------------------------


func test_no_waves_is_a_flat_rest_plane() -> void:
	var w := GerstnerWaves.from_set(null)
	assert_eq(w.displacement(Vector2(3, 4), 10.0), Vector3.ZERO)
	assert_eq(w.height_at(Vector2(3, 4), 10.0), 0.0)
	assert_eq(w.normal_at(Vector2(3, 4), 10.0), Vector3.UP)
	assert_eq(w.jacobian(Vector2(3, 4), 10.0), 1.0)


func test_single_wave_matches_closed_form() -> void:
	var length := 20.0
	var amp := 0.5
	var steep := 0.8
	var w := GerstnerWaves.from_set(_wave_set([_wave(90.0, length, amp, steep, 0.3)]))
	var k := TAU / length
	var omega := sqrt(GerstnerWaves.GRAVITY * k)
	for p in _points():
		var theta := k * p.x - omega * SAMPLE_TIME_S + 0.3
		var d := w.displacement(p, SAMPLE_TIME_S)
		var want := Vector3(-(steep / k) * sin(theta), amp * cos(theta), 0.0)
		assert_true(d.is_equal_approx(want), "closed form at %s: %s vs %s" % [p, d, want])
	# The crest (theta = 0) is at full amplitude and compressed: J = 1 - steepness.
	var crest_x := (omega * SAMPLE_TIME_S - 0.3) / k
	var crest := Vector2(crest_x, 0.0)
	assert_between(w.displacement(crest, SAMPLE_TIME_S).y, amp - 1e-6, amp + 1e-6)
	assert_between(w.jacobian(crest, SAMPLE_TIME_S), 1.0 - steep - 1e-6, 1.0 - steep + 1e-6)


func test_height_at_inverts_horizontal_displacement() -> void:
	var w := _lagoon()
	assert_true(w.count() > 0, "lagoon wave set loads")
	for p0 in _points():
		var d := w.displacement(p0, SAMPLE_TIME_S)
		var xz := p0 + Vector2(d.x, d.z)
		var h := w.height_at(xz, SAMPLE_TIME_S)
		assert_between(h, d.y - HEIGHT_TOLERANCE_M, d.y + HEIGHT_TOLERANCE_M, "height above displaced point %s" % xz)


func test_height_at_converges_for_the_steepest_allowed_set() -> void:
	var w := GerstnerWaves.from_set(_wave_set([_wave(10.0, 8.0, 0.3, 1.0), _wave(100.0, 5.0, 0.2, 1.0)]))
	for p0 in _points():
		var d := w.displacement(p0, SAMPLE_TIME_S)
		var h := w.height_at(p0 + Vector2(d.x, d.z), SAMPLE_TIME_S)
		assert_between(h, d.y - 1e-3, d.y + 1e-3, "converges at steepness 1")


func test_analytic_normal_and_jacobian_match_finite_differences() -> void:
	var w := _lagoon()
	for p0 in _points():
		var c := w.displacement(p0, SAMPLE_TIME_S)
		var dx := (w.displacement(p0 + Vector2(FD_STEP_M, 0), SAMPLE_TIME_S) - c) / FD_STEP_M
		var dz := (w.displacement(p0 + Vector2(0, FD_STEP_M), SAMPLE_TIME_S) - c) / FD_STEP_M
		var tx := Vector3(1, 0, 0) + dx
		var tz := Vector3(0, 0, 1) + dz
		var n_fd := tz.cross(tx).normalized()
		var n := w.normal(p0, SAMPLE_TIME_S)
		assert_true((n - n_fd).length() < FD_TOLERANCE, "normal at %s: %s vs %s" % [p0, n, n_fd])
		assert_true(n.y > 0.0, "normal points up")
		var j_fd := tx.x * tz.z - tx.z * tz.x
		var j := w.jacobian(p0, SAMPLE_TIME_S)
		assert_between(j, j_fd - FD_TOLERANCE, j_fd + FD_TOLERANCE, "Jacobian at %s" % p0)


func test_waves_travel_in_their_direction_over_time() -> void:
	var w := GerstnerWaves.from_set(_wave_set([_wave(90.0, 30.0, 0.4, 0.0)]))
	var k := TAU / 30.0
	var c := sqrt(GerstnerWaves.GRAVITY / k)  # phase speed
	var t0 := 2.0
	var dt := 1.5
	var h0 := w.height_at(Vector2(0, 0), t0)
	var h1 := w.height_at(Vector2(c * dt, 0), t0 + dt)
	assert_between(h1, h0 - 1e-6, h0 + 1e-6, "a crest moves east at the phase speed")


# --- GPU parity (needs the software renderer, ADR 0009) -----------------------------------


func test_gpu_shader_matches_cpu_mirror() -> void:
	var wrapper := OS.get_environment("HYMN_GODOT_RENDER")
	if wrapper == "":
		wrapper = RENDER_WRAPPER.replace("~", OS.get_environment("HOME"))
	if not FileAccess.file_exists(wrapper):
		print("    (skip: no software renderer at %s; python3 tools/dev/fetch_render_deps.py)" % wrapper)
		return
	var out: Array = []
	var args := PackedStringArray(
		["--path", ProjectSettings.globalize_path("res://"), "--audio-driver", "Dummy", PROBE_SCENE]
	)
	var code := OS.execute(wrapper, args, out, true)
	var text := "\n".join(PackedStringArray(out))
	var line := ""
	for l in text.split("\n"):
		if l.begins_with("PARITY"):
			line = l
	assert_true(line != "", "probe printed no PARITY line (exit %d): %s" % [code, text.right(600)])
	assert_true(line.contains("ok=true"), "GPU and CPU waves disagree: %s" % line)
	assert_eq(code, 0, line)
	print("    %s" % line)
