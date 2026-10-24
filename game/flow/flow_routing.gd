class_name FlowRouting
extends RefCounted
## Scene changes that are never lost (M2-FP-09, review-sweep-K). SceneRouter ignores a change made
## while it is busy with another (it warns and returns), and WorldReturn.go_to does not know: a
## flow step that latched "done" before such a call could leave the player stuck. Every first-
## playable hand-off goes through `when_free`, which waits until the router is idle, then makes
## the change, so the change is always taken.
## Waiters take turns (M2-FP-11): the first to call goes first, and each later one waits for the
## router to go idle again after the one before it, so two hand-offs waiting on the same busy router
## never both fire on one idle frame (the router would drop the second).
##
## Tests swap `busy` (a Callable() -> bool) and `next_frame` (a Callable() -> Signal) to drive the
## wait by hand, and `record` to capture the changes.

static var busy: Callable = Callable()
static var next_frame: Callable = Callable()
## Tests: when set, change_scene(path) and go_to(location, spawn) call this with [path] or
## [location, spawn] instead of changing scene.
static var record: Callable = Callable()

## Waiters in call order; only the front one may change scene, once the router is idle.
static var _queue: Array[RefCounted] = []


## Makes `change` (a Callable that starts a scene change) as soon as the router is idle. Await it
## or call it as a statement; either way the change happens exactly once.
static func when_free(change: Callable) -> void:
	var ticket := RefCounted.new()
	_queue.append(ticket)
	while _queue.front() != ticket or _is_busy():
		var frame: Variant = _frame()
		if frame == null:
			push_warning("FlowRouting: no scene tree to wait on; changing now")
			break
		await (frame as Signal)
	_queue.erase(ticket)
	change.call()


## Waiters not yet served (tests).
static func waiting() -> int:
	return _queue.size()


## Forgets every waiter (tests whose mocked frame signal will never fire again).
static func reset() -> void:
	_queue.clear()


## A SceneRouter.change_scene to `path`, made once the router is idle.
static func change_scene(path: String) -> void:
	if record.is_valid():
		record.call([path])
		return
	await when_free(func() -> void: _router().call(&"change_scene", path))


## A WorldReturn.go_to(location, spawn), made once the router is idle.
static func go_to(location: StringName, spawn: StringName) -> void:
	if record.is_valid():
		record.call([location, spawn])
		return
	await when_free(func() -> void: (_router().get(&"world_return") as WorldReturn).go_to(location, spawn))


static func _is_busy() -> bool:
	if busy.is_valid():
		return bool(busy.call())
	var r := _router()
	return r != null and bool(r.call(&"is_busy"))


static func _frame() -> Variant:
	if next_frame.is_valid():
		return next_frame.call()
	var tree := Engine.get_main_loop() as SceneTree
	return tree.process_frame if tree != null else null


static func _router() -> Node:
	var tree := Engine.get_main_loop() as SceneTree
	return tree.root.get_node_or_null(^"SceneRouter") if tree != null else null
