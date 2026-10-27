extends TestCase
## M2-FP-104: the held-shot camera breath is tiny, eases in from nothing and repeats exactly.

const CFG := {
	"enabled": true,
	"ramp_sec": 1.0,
	"yaw_deg": 0.2,
	"yaw_periods_sec": [7.0, 11.0],
	"pitch_deg": 0.1,
	"pitch_periods_sec": [9.0],
}
const DT := 1.0 / 30.0
const SECONDS := 20.0
const TOLERANCE := 0.000001


func test_it_eases_in_from_still() -> void:
	var b := CutsceneCameraBreath.new(CFG)
	var first := b.step(DT)
	assert_true(first.length() < deg_to_rad(0.001), "the first frame after a cut is still")


func test_it_never_exceeds_its_amplitude() -> void:
	var b := CutsceneCameraBreath.new(CFG)
	var t := 0.0
	while t < SECONDS:
		var off := b.step(DT)
		assert_true(absf(off.x) <= deg_to_rad(0.2) + TOLERANCE, "yaw within 0.2 degrees")
		assert_true(absf(off.y) <= deg_to_rad(0.1) + TOLERANCE, "pitch within 0.1 degrees")
		t += DT


func test_it_is_deterministic_and_reset_starts_over() -> void:
	var a := CutsceneCameraBreath.new(CFG)
	var b := CutsceneCameraBreath.new(CFG)
	for i in 90:
		a.step(DT)
		b.step(DT)
	assert_eq(a.step(DT), b.step(DT), "the same every time")
	a.reset()
	assert_true(a.step(DT).length() < deg_to_rad(0.001), "a reset is a new cut")


func test_disabled_leaves_the_camera_alone() -> void:
	var cam := Camera3D.new()
	var before := cam.transform
	CutsceneCameraBreath.new({"enabled": false}).apply(cam, DT)
	assert_eq(cam.transform, before)
	cam.free()
