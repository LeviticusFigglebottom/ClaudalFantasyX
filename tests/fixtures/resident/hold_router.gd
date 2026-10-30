extends Node
## A stand-in for SceneRouter's swap holds (test_resident_loads): change_started, hold_swap and release_swap.

signal change_started(scene_path: String)

var _holds: Array[Object] = []


func hold_swap(holder: Object) -> void:
	if not _holds.has(holder):
		_holds.append(holder)


func release_swap(holder: Object) -> void:
	_holds.erase(holder)


func holders() -> Array[Object]:
	return _holds
