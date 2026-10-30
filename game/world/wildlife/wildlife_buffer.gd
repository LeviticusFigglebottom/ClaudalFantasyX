class_name WildlifeBuffer
extends RefCounted
## One MultiMesh's per-frame instance data for WildlifeLayer (M3-CRE-611): a 3D transform (12 floats, the basis
## rows then the origin, as MultiMesh.buffer stores it) and the custom data the wildlife shader reads (phase,
## amplitude, mode, mode parameter). A hidden instance gets a zero basis, so it draws nothing.

const FLOATS := 16
const MODE_STILL := 0.0
const MODE_FLAP := 1.0
const MODE_HEAD := 2.0
const MODE_LEGS := 3.0
const MODE_SWIM := 4.0
const MODE_FLUTTER := 5.0
## The firefly: the flutter, its mode parameter the lantern's blink (0 dark .. 1 lit).
const MODE_GLOW := 6.0

var data := PackedFloat32Array()
var count := 0


func _init(instances: int) -> void:
	count = instances
	data.resize(instances * FLOATS)


func put(i: int, xf: Transform3D, phase: float, amp: float, mode: float, param: float) -> void:
	var o := i * FLOATS
	var b := xf.basis
	data[o] = b.x.x
	data[o + 1] = b.y.x
	data[o + 2] = b.z.x
	data[o + 3] = xf.origin.x
	data[o + 4] = b.x.y
	data[o + 5] = b.y.y
	data[o + 6] = b.z.y
	data[o + 7] = xf.origin.y
	data[o + 8] = b.x.z
	data[o + 9] = b.y.z
	data[o + 10] = b.z.z
	data[o + 11] = xf.origin.z
	data[o + 12] = fposmod(phase, TAU)
	data[o + 13] = amp
	data[o + 14] = mode
	data[o + 15] = param


func hide(i: int) -> void:
	var o := i * FLOATS
	for k in FLOATS:
		data[o + k] = 0.0


## The origin of instance i (tests and the timing read positions back).
func origin(i: int) -> Vector3:
	var o := i * FLOATS
	return Vector3(data[o + 3], data[o + 7], data[o + 11])


func visible(i: int) -> bool:
	var o := i * FLOATS
	return data[o] != 0.0 or data[o + 5] != 0.0 or data[o + 10] != 0.0
