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


func test_a_field_interactable_back_from_a_resident_return_connects_used_once() -> void:
	# cloud-qa's `used` count: an Interactable is watched by both UiAudio (the soft touch) and InteractAudio (its
	# own sound), the way the director routes it; out of the tree for the battle and back, twice
	var dir := AudioDirector.new()
	_host.add_child(dir)
	dir.set_process(false)
	var played: Array[StringName] = []
	dir.ui.player = func(id: StringName) -> void: played.append(id)
	var area := Interactable.new()
	_host.add_child(area)
	for round in 3:
		dir.interact.watch(area)
		dir.ui.watch(area)
		dir.ui.step()
		if round < 2:
			_host.remove_child(area)
			dir.ui.step()
			_host.add_child(area)
	assert_eq(_errors(), [], "no engine error over two resident returns")
	assert_eq(area.used.get_connections().size(), 2, "one connection each: UiAudio and InteractAudio")
	# a path that loses the node's mark (a node duplicated, its meta cleared) still never connects twice
	area.remove_meta(UiAudio.META_CONNECTED)
	_host.remove_child(area)
	dir.ui.step()
	_host.add_child(area)
	dir.ui.watch(area)
	assert_eq(_errors(), [], "no engine error with the mark gone")
	assert_eq(area.used.get_connections().size(), 2, "still one each")
	played.clear()
	area.used.emit(area)
	dir.ui.step()
	assert_eq(played.count(&"ui_interact"), 1, "the soft touch plays once (%s)" % [played])
	area.free()
	dir.stop_all_players()
	dir.free()
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
