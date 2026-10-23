extends TestCase
## M1-UI-09: the toast that tells the player a chapter autosave was skipped because slot 0 holds a
## journey further along (ADR 0018 Amendment 1, EventBus.autosave_finished with ERR_ALREADY_EXISTS).
## It shows for that error only, waits out an autosave hold (a cutscene), and fades away by itself.


class FakeBus:
	extends Node
	signal autosave_finished(reason: StringName, error: int)


var _bus: FakeBus
var _toast: AutosaveToast
var _holder := RefCounted.new()


func before_each() -> void:
	var root := (Engine.get_main_loop() as SceneTree).current_scene
	_bus = FakeBus.new()
	root.add_child(_bus)
	_toast = AutosaveToast.new()
	_toast.event_bus = _bus
	root.add_child(_toast)


func _done() -> void:
	SaveSystem.release_autosave(_holder)
	_toast.free()
	_bus.free()


func _motion() -> Dictionary:
	return AutosaveToast.load_data().get("motion", {}) as Dictionary


func test_the_skipped_autosave_shows_the_toast() -> void:
	assert_false(_toast.is_showing(), "hidden at first")
	_bus.autosave_finished.emit(SaveSystem.REASON_CHAPTER, ERR_ALREADY_EXISTS)
	assert_true(_toast.is_showing(), "ERR_ALREADY_EXISTS shows the toast")
	_toast.advance(float(_motion()["fade_in_sec"]) + 0.01)
	assert_between(_toast.opacity(), 0.99, 1.0, "fully in after the fade")
	_done()


func test_other_results_never_show_it() -> void:
	for err: int in [OK, ERR_UNAVAILABLE, ERR_CANT_CREATE, ERR_FILE_CANT_WRITE]:
		_bus.autosave_finished.emit(SaveSystem.REASON_CHAPTER, err)
		_toast.advance(0.1)
		assert_false(_toast.is_showing(), "no toast for %s" % error_string(err))
		assert_false(_toast.is_pending(), "nothing queued for %s" % error_string(err))
	_done()


func test_it_waits_out_a_cutscene_hold() -> void:
	SaveSystem.hold_autosave(_holder)
	_bus.autosave_finished.emit(SaveSystem.REASON_CHAPTER, ERR_ALREADY_EXISTS)
	assert_false(_toast.is_showing(), "not during the hold")
	assert_true(_toast.is_pending(), "queued for after it")
	_toast.advance(1.0)
	assert_false(_toast.is_showing(), "still held")
	SaveSystem.release_autosave(_holder)
	_toast.advance(0.0)
	assert_true(_toast.is_showing(), "shown once the hold is released")
	assert_false(_toast.is_pending())
	_done()


func test_it_fades_out_and_hides_itself() -> void:
	var m := _motion()
	var total := float(m["fade_in_sec"]) + float(m["hold_sec"]) + float(m["fade_out_sec"])
	_bus.autosave_finished.emit(SaveSystem.REASON_CHAPTER, ERR_ALREADY_EXISTS)
	_toast.advance(float(m["fade_in_sec"]) + float(m["hold_sec"]) + float(m["fade_out_sec"]) * 0.5)
	assert_between(_toast.opacity(), 0.3, 0.7, "half way through the fade out")
	_toast.advance(total)
	assert_false(_toast.is_showing(), "gone after its time")
	assert_eq(_toast.opacity(), 0.0)
	_done()


func test_it_never_takes_input_and_has_its_text() -> void:
	_bus.autosave_finished.emit(SaveSystem.REASON_CHAPTER, ERR_ALREADY_EXISTS)
	for c: Node in _toast.find_children("*", "Control", true, false):
		assert_eq((c as Control).mouse_filter, Control.MOUSE_FILTER_IGNORE, "%s ignores the mouse" % c.name)
	var label := _toast.find_children("*", "Label", true, false)[0] as Label
	assert_ne(label.text, AutosaveToast.TEXT_KEY, "the loc key resolves to text")
	assert_true(label.text.length() > 0)
	assert_eq(_toast.process_mode, Node.PROCESS_MODE_ALWAYS, "it fades while a menu pauses the tree")
	_done()


func test_it_listens_on_the_real_event_bus() -> void:
	var toast := AutosaveToast.new()
	(Engine.get_main_loop() as SceneTree).current_scene.add_child(toast)
	EventBus.autosave_finished.emit(SaveSystem.REASON_CHAPTER, ERR_ALREADY_EXISTS)
	assert_true(toast.is_showing(), "EventBus.autosave_finished reaches it")
	toast.free()
	_done()


func test_install_is_idempotent() -> void:
	var host := Node.new()
	var a := AutosaveToast.install(host)
	assert_eq(a.get_parent(), host)
	assert_eq(AutosaveToast.install(host), a, "a second install returns the first")
	assert_eq(String(a.name), AutosaveToast.NODE_NAME)
	host.free()
	_done()
