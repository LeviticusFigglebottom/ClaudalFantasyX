extends TestCase
## M3-HER-1151: while SceneRouter instantiates a zone on a worker thread, ShaderGlobals holds its RenderingServer
## writes (a global write walks the materials the thread is creating: "Attempting to initialize the wrong RID").
## The CPU copy stays current throughout; the last value per global is sent when the last hold ends.

const NAME := &"hymn_wind_time"
const FIRST := 1.5
const LAST := 2.5

var _was: Variant


func before_each() -> void:
	_was = ShaderGlobals.get_value(NAME, 0.0)


func test_writes_wait_for_the_hold_and_the_copy_does_not() -> void:
	assert_false(ShaderGlobals.writes_held(), "no hold to begin with")
	ShaderGlobals.hold_writes()
	assert_true(ShaderGlobals.writes_held(), "held")
	ShaderGlobals.set_value(NAME, FIRST)
	ShaderGlobals.set_value(NAME, LAST)
	assert_eq(float(ShaderGlobals.get_value(NAME, 0.0)), LAST, "the CPU copy is current while held")
	assert_eq(ShaderGlobals._held_writes.size(), 1, "one held write per global: the last value")
	assert_eq(float(ShaderGlobals._held_writes[NAME]), LAST)
	ShaderGlobals.release_writes()
	assert_false(ShaderGlobals.writes_held(), "released")
	assert_true(ShaderGlobals._held_writes.is_empty(), "sent on release")
	_restore()


func test_holds_nest() -> void:
	ShaderGlobals.hold_writes()
	ShaderGlobals.hold_writes()
	ShaderGlobals.set_value(NAME, FIRST)
	ShaderGlobals.release_writes()
	assert_true(ShaderGlobals.writes_held(), "still held by the outer hold")
	assert_eq(ShaderGlobals._held_writes.size(), 1, "not sent yet")
	ShaderGlobals.release_writes()
	assert_true(ShaderGlobals._held_writes.is_empty(), "sent when the last hold ends")
	ShaderGlobals.release_writes()  # an extra release is harmless
	assert_false(ShaderGlobals.writes_held())
	_restore()


func test_the_router_holds_writes_around_its_threaded_instantiate() -> void:
	var src := (load("res://game/core/scene_router.gd") as GDScript).source_code
	var body := src.substr(src.find("func _instantiate("))
	body = body.substr(0, body.find("\nfunc ", 1))
	var hold := body.find("ShaderGlobals.hold_writes()")
	var task := body.find("WorkerThreadPool.add_task(")
	var wait := body.find("WorkerThreadPool.wait_for_task_completion(")
	var release := body.find("ShaderGlobals.release_writes()")
	assert_true(hold >= 0 and hold < task, "the hold comes before the thread starts")
	assert_true(release > wait, "the release comes after the thread is done")


func _restore() -> void:
	ShaderGlobals.set_value(NAME, _was)
	_done_ok()


func _done_ok() -> void:
	while ShaderGlobals.writes_held():
		ShaderGlobals.release_writes()
