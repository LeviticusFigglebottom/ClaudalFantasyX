extends TestCase
## The Lead's 10-30 23:05 FAST-TRACK: two engine ERRORs the audio listeners raised in play.
## - UiAudio re-watched a menu that left the tree and came back (the field held resident through a battle) and
##   connected its signals a second time: "already connected", once per hooked signal on every resident return
##   (134 in Ch1–Ch6). A node keeps its connections across the round trip; now it is connected once and its reads
##   resume, and a signal still plays its row exactly once.
## - AshcrownAudio connected the trial's three-argument `ran` through `unbind(0)`, which is an ERROR. Now a signal of
##   three arguments connects plainly and one of more drops only its extras.
## Both tests fail on any engine error raised while they run (QaLogger), not only on script errors.

var log: QaLogger
var _host: Node


class HookedMenu:
	extends Node
	signal closed


class FakeTrial:
	extends RefCounted
	signal ran(tier: int, path: Array[StringName], outcome: StringName)
	signal four(a: int, b: int, c: int, d: int)


func before_each() -> void:
	log = QaLogger.new()
	OS.add_logger(log)
	_host = Node.new()
	(Engine.get_main_loop() as SceneTree).current_scene.add_child(_host)


func _errors() -> Array:
	return log.take().filter(func(e: Dictionary) -> bool: return e["kind"] != QaLogger.KIND_WARNING)


func _done() -> void:
	OS.remove_logger(log)
	_host.free()


func test_a_menu_back_from_a_resident_battle_is_not_connected_twice() -> void:
	var played: Array[StringName] = []
	var ui := UiAudio.new(AudioData.table(AudioData.UI_SFX))
	ui.player = func(id: StringName) -> void: played.append(id)
	_host.add_child(ui)
	var menu := HookedMenu.new()
	menu.set_meta(UiAudio.META_CLASS, "FieldMenu")
	_host.add_child(menu)
	ui.watch(menu)
	ui.step()
	played.clear()
	# the battle: the field leaves the tree, and the watch lets it go
	_host.remove_child(menu)
	ui.step()
	# the return: it comes back and the director watches it again
	_host.add_child(menu)
	ui.watch(menu)
	ui.step()
	assert_eq(_errors(), [], "no engine error on the return")
	played.clear()
	menu.closed.emit()
	ui.step()
	assert_eq(played.count(&"ui_menu_close"), 1, "closing still plays its row, once (%s)" % [played])
	menu.free()
	_done()


func test_the_trials_three_argument_signal_connects_without_unbind_zero() -> void:
	var ash := AshcrownAudio.new(AudioData.table(AudioData.ASHCROWN_SFX))
	var heard: Array = []
	ash.player_at = func(id: StringName, _at: Vector3) -> void: heard.append(id)
	var trial := FakeTrial.new()
	ash._connect(trial, "ran")
	ash._connect(trial, "four")
	assert_eq(_errors(), [], "no engine error connecting `ran` (three arguments) or a four-argument signal")
	assert_true(trial.ran.get_connections().size() == 1, "ran is connected")
	trial.ran.emit(1, [] as Array[StringName], &"nothing")
	trial.four.emit(1, 2, 3, 4)
	assert_eq(_errors(), [], "and no error when they fire")
	_done()
