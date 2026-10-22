class_name CameraPose
extends RefCounted
## A camera state the director can blend: transform, vertical FOV and depth-of-field values.
## Pure value object (no Nodes), so blends are unit-testable.

const DOF_FAR_ENABLED := "far_enabled"
const DOF_NEAR_ENABLED := "near_enabled"
## |dot(view, up)| above 1 - this counts as looking straight up/down (use another up vector).
const PARALLEL_EPSILON := 0.0001

var origin := Vector3.ZERO
var rotation := Quaternion.IDENTITY
var fov_deg := 0.0
## Same keys as CameraShot.dof_dict().
var dof: Dictionary = {}


static func looking(
	from: Vector3, target: Vector3, fov: float, dof_values: Dictionary, roll_deg: float = 0.0
) -> CameraPose:
	var p := CameraPose.new()
	p.origin = from
	var dir := target - from
	if dir.length_squared() > 0.0:
		var up := Vector3.UP if absf(dir.normalized().dot(Vector3.UP)) < 1.0 - PARALLEL_EPSILON else Vector3.BACK
		var b := Basis.looking_at(dir, up)
		if roll_deg != 0.0:
			b = b.rotated(dir.normalized(), deg_to_rad(roll_deg))
		p.rotation = b.get_rotation_quaternion()
	p.fov_deg = fov
	p.dof = dof_values.duplicate()
	return p


func transform() -> Transform3D:
	return Transform3D(Basis(rotation), origin)


func forward() -> Vector3:
	return Basis(rotation) * Vector3.FORWARD


func copy() -> CameraPose:
	var p := CameraPose.new()
	p.origin = origin
	p.rotation = rotation
	p.fov_deg = fov_deg
	p.dof = dof.duplicate()
	return p


## Interpolates every value; DOF on/off flags are OR'd while a blend is in progress so focus never
## pops off mid-move, and take the target's value at weight 1.
static func blend(a: CameraPose, b: CameraPose, weight: float) -> CameraPose:
	var w := clampf(weight, 0.0, 1.0)
	if w >= 1.0:
		return b.copy()
	if w <= 0.0:
		return a.copy()
	var p := CameraPose.new()
	p.origin = a.origin.lerp(b.origin, w)
	p.rotation = a.rotation.slerp(b.rotation, w)
	p.fov_deg = lerpf(a.fov_deg, b.fov_deg, w)
	for key: String in b.dof:
		var bv: Variant = b.dof[key]
		var av: Variant = a.dof.get(key, bv)
		if bv is bool:
			p.dof[key] = bool(av) or bool(bv)
		else:
			p.dof[key] = lerpf(float(av), float(bv), w)
	return p


## Writes the pose to a Camera3D, creating CameraAttributesPractical for DOF when needed.
func apply_to(camera: Camera3D) -> void:
	camera.global_transform = transform()
	camera.fov = fov_deg
	var wants_dof := bool(dof.get(DOF_FAR_ENABLED, false)) or bool(dof.get(DOF_NEAR_ENABLED, false))
	if camera.attributes != null and not camera.attributes is CameraAttributesPractical:
		return  # physical-camera attributes are authored by hand; leave them alone
	var attrs := camera.attributes as CameraAttributesPractical
	if attrs == null and not wants_dof:
		return
	if attrs == null:
		attrs = CameraAttributesPractical.new()
		camera.attributes = attrs
	attrs.dof_blur_far_enabled = bool(dof.get(DOF_FAR_ENABLED, false))
	attrs.dof_blur_far_distance = float(dof.get("far_distance", attrs.dof_blur_far_distance))
	attrs.dof_blur_far_transition = float(dof.get("far_transition", attrs.dof_blur_far_transition))
	attrs.dof_blur_near_enabled = bool(dof.get(DOF_NEAR_ENABLED, false))
	attrs.dof_blur_near_distance = float(dof.get("near_distance", attrs.dof_blur_near_distance))
	attrs.dof_blur_near_transition = float(dof.get("near_transition", attrs.dof_blur_near_transition))
	attrs.dof_blur_amount = float(dof.get("amount", attrs.dof_blur_amount))
