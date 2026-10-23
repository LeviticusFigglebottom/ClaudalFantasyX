class_name FieldShapes
extends RefCounted
## Deterministic point-in-volume tests for field Area3D nodes (camera volumes, interactables).
## The director polls these every update instead of waiting for physics overlap signals, so camera
## selection is frame-exact, order-independent, and testable headlessly without stepping physics.
## Supported shapes: BoxShape3D, SphereShape3D, CylinderShape3D, CapsuleShape3D (any transform).


## True if `world_point` lies inside any enabled CollisionShape3D child of `area`.
static func area_contains(area: Area3D, world_point: Vector3, epsilon: float = 0.0) -> bool:
	for child in area.get_children():
		var cs := child as CollisionShape3D
		if cs == null or cs.disabled or cs.shape == null:
			continue
		var local := cs.global_transform.affine_inverse() * world_point
		if shape_contains(cs.shape, local, epsilon):
			return true
	return false


## Point in the shape's local space (shape centred on the origin, Y up).
static func shape_contains(shape: Shape3D, p: Vector3, epsilon: float = 0.0) -> bool:
	if shape is BoxShape3D:
		var half := (shape as BoxShape3D).size * 0.5 + Vector3.ONE * epsilon
		return absf(p.x) <= half.x and absf(p.y) <= half.y and absf(p.z) <= half.z
	if shape is SphereShape3D:
		var r := (shape as SphereShape3D).radius + epsilon
		return p.length_squared() <= r * r
	if shape is CylinderShape3D:
		var cyl := shape as CylinderShape3D
		var cr := cyl.radius + epsilon
		return absf(p.y) <= cyl.height * 0.5 + epsilon and Vector2(p.x, p.z).length_squared() <= cr * cr
	if shape is CapsuleShape3D:
		var cap := shape as CapsuleShape3D
		var seg := maxf(cap.height * 0.5 - cap.radius, 0.0)
		var nearest := Vector3(0.0, clampf(p.y, -seg, seg), 0.0)
		var kr := cap.radius + epsilon
		return (p - nearest).length_squared() <= kr * kr
	push_warning("FieldShapes: unsupported shape %s" % shape.get_class())
	return false
