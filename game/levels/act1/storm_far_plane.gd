class_name StormFarPlane
extends Node
## M3-ENV-1308 / 1314 (env-art-b): keeps the Undertow inside whichever camera is current. The storm stands 10-14 km out
## (undertow.json presets) and a Camera3D's default far plane is 4 km, so a field, cutscene or battle camera never drew
## it. While its parent UndertowStorm is visible, this raises the current camera's far plane past the storm's far side.

## Past the storm's bound (m).
const MARGIN_M := 2000.0


func _process(_delta: float) -> void:
	var storm := get_parent() as UndertowStorm
	if storm == null or not storm.is_visible_in_tree():
		return
	var cam := get_viewport().get_camera_3d()
	if cam != null:
		cam.far = maxf(cam.far, far_needed(storm))


static func far_needed(storm: UndertowStorm) -> float:
	return storm.approach_distance_m + storm.state.bound_radius() + MARGIN_M
