extends TestCase
## M1-RND-16: scoped graphics overrides (GraphicsSettings.push_override / pop_override) for storm
## cutscenes: last pushed wins, popping restores the one below, the last pop (or the owner leaving
## the tree) restores the viewport exactly, settings.cfg is never written, listeners (the Undertow's
## temporal-jitter gate) follow in the same frame, and the prewarm stage can match a planned override.


class Listener:
	extends Node
	var calls := 0
	var seen_taa := false

	func _enter_tree() -> void:
		add_to_group(GraphicsSettings.VIEWPORT_STATE_GROUP)

	func on_viewport_state_changed() -> void:
		calls += 1
		seen_taa = get_viewport().use_taa


const STORM_CLOSEUP := {"aa": "taa", "scaling_mode": "fsr"}

var _vp: SubViewport
var _base: GraphicsSettings
var _nodes: Array[Node] = []


func before_each() -> void:
	_base = GraphicsSettings.new()
	_base.set_preset("high")
	_vp = SubViewport.new()
	(Engine.get_main_loop() as SceneTree).current_scene.add_child(_vp)
	# The High preset's viewport state: FSR2 at 0.77, TAA off (FSR2 accumulates itself), as boot leaves it.
	GraphicsSettings.execute(_viewport_ops(_base.plan()), _vp, null)


func _viewport_ops(ops: Array[Dictionary]) -> Array[Dictionary]:
	var out: Array[Dictionary] = []
	for op in ops:
		if op["target"] == GraphicsSettings.TARGET_VIEWPORT:
			out.append(op)
	return out


func _owner(owner_name: String) -> Node:
	var n := Node.new()
	n.name = owner_name
	_vp.add_child(n)
	_nodes.append(n)
	return n


func _done() -> void:
	for n in _nodes:
		if is_instance_valid(n):
			n.free()
	_nodes.clear()
	assert_eq(GraphicsSettings.active_overrides(), 0, "no override outlives its test")
	_vp.free()


func test_push_applies_and_pop_restores_exactly() -> void:
	var before := GraphicsSettings._viewport_state(_vp)
	assert_eq(_vp.scaling_3d_mode, Viewport.SCALING_3D_MODE_FSR2)
	assert_false(_vp.use_taa)
	var h := GraphicsSettings.push_override(_owner("Cutscene"), STORM_CLOSEUP, null, _base)
	assert_true(h > 0, "a handle")
	assert_eq(_vp.scaling_3d_mode, Viewport.SCALING_3D_MODE_FSR, "FSR1 for the close-up")
	assert_true(_vp.use_taa, "native TAA integrates the dither")
	assert_between(_vp.scaling_3d_scale, 0.769, 0.771, "the player's render scale is kept")
	assert_eq(GraphicsSettings.active_overrides(), 1)
	assert_true(GraphicsSettings.pop_override(h))
	assert_eq(GraphicsSettings._viewport_state(_vp), before, "restored exactly")
	assert_false(GraphicsSettings.pop_override(h), "a handle pops once")
	_done()


func test_last_pushed_wins_and_popping_restores_the_one_below() -> void:
	var a := GraphicsSettings.push_override(_owner("A"), STORM_CLOSEUP, null, _base)
	var b := GraphicsSettings.push_override(_owner("B"), {"aa": "fxaa"}, null, _base)
	assert_false(_vp.use_taa, "B's AA wins")
	assert_eq(_vp.screen_space_aa, Viewport.SCREEN_SPACE_AA_FXAA)
	assert_eq(_vp.scaling_3d_mode, Viewport.SCALING_3D_MODE_FSR, "A's scaling still holds under B")
	assert_true(GraphicsSettings.pop_override(b))
	assert_true(_vp.use_taa, "A again")
	assert_eq(_vp.screen_space_aa, Viewport.SCREEN_SPACE_AA_DISABLED)
	assert_true(GraphicsSettings.pop_override(a))
	assert_eq(_vp.scaling_3d_mode, Viewport.SCALING_3D_MODE_FSR2, "the player's state")
	_done()


func test_overlapping_pops_out_of_order_resolve_deterministically() -> void:
	var before := GraphicsSettings._viewport_state(_vp)
	var a := GraphicsSettings.push_override(_owner("A"), STORM_CLOSEUP, null, _base)
	var b := GraphicsSettings.push_override(_owner("B"), {"aa": "fxaa"}, null, _base)
	assert_true(GraphicsSettings.pop_override(a), "the lower one ends first")
	assert_eq(_vp.screen_space_aa, Viewport.SCREEN_SPACE_AA_FXAA, "B still holds")
	assert_eq(_vp.scaling_3d_mode, Viewport.SCALING_3D_MODE_FSR2, "A's scaling is gone with it")
	assert_false(_vp.use_taa)
	assert_true(GraphicsSettings.pop_override(b))
	assert_eq(GraphicsSettings._viewport_state(_vp), before)
	_done()


## The owner's tree_exiting defers the check to the end of the frame; the tests call that deferred
## step (GraphicsSettings._owner_left) themselves, since the runner does not run frames.
func test_the_owner_leaving_the_tree_pops_it() -> void:
	var before := GraphicsSettings._viewport_state(_vp)
	var owner := _owner("Cutscene")
	var h := GraphicsSettings.push_override(owner, STORM_CLOSEUP, null, _base)
	assert_true(_vp.use_taa)
	_vp.remove_child(owner)
	GraphicsSettings._owner_left(h)
	assert_eq(GraphicsSettings.active_overrides(), 0, "leaving the tree pops it")
	assert_eq(GraphicsSettings._viewport_state(_vp), before)
	_vp.add_child(owner)
	assert_eq(_vp.scaling_3d_mode, Viewport.SCALING_3D_MODE_FSR2, "re-entering does not re-apply it")
	_done()


func test_a_freed_owner_pops_it() -> void:  # M1-NIT-02
	var before := GraphicsSettings._viewport_state(_vp)
	var owner := _owner("Cutscene")
	var h := GraphicsSettings.push_override(owner, STORM_CLOSEUP, null, _base)
	owner.free()
	GraphicsSettings._owner_left(h)
	assert_eq(GraphicsSettings.active_overrides(), 0, "freeing the owner pops it")
	assert_eq(GraphicsSettings._viewport_state(_vp), before)
	_done()


func test_a_reparented_owner_keeps_its_override() -> void:  # M1-NIT-02 (review-sweep-L S2)
	var owner := _owner("Cutscene")
	var h := GraphicsSettings.push_override(owner, STORM_CLOSEUP, null, _base)
	var holder := _owner("Holder")
	owner.reparent(holder)
	GraphicsSettings._owner_left(h)
	assert_eq(GraphicsSettings.active_overrides(), 1, "a reparent is not a pop")
	assert_true(_vp.use_taa, "the override still holds")
	_vp.remove_child(holder)
	GraphicsSettings._owner_left(h)
	assert_eq(GraphicsSettings.active_overrides(), 0, "leaving for good after the reparent still pops")
	_vp.add_child(holder)
	_done()


func test_a_later_base_never_rebases_the_stack() -> void:  # M1-NIT-02 (review-sweep-L S1)
	var low := GraphicsSettings.new()
	low.set_preset("low")
	var planned := GraphicsSettings.override_state(STORM_CLOSEUP, _base)
	var a := GraphicsSettings.push_override(_owner("A"), {"aa": "taa"}, null, _base)
	var b := GraphicsSettings.push_override(_owner("B"), {"scaling_mode": "fsr"}, null, low)
	assert_true(b > 0, "applied")
	assert_eq(GraphicsSettings.override_state(), planned, "both layers on the first push's High base")
	assert_between(_vp.scaling_3d_scale, 0.769, 0.771, "High's render scale, not Low's")
	assert_true(GraphicsSettings.pop_override(b))
	assert_true(GraphicsSettings.pop_override(a))
	_done()


## M2-NIT-03 (review-sweep-M S1): a scene swap. Cutscene A has left the tree but its deferred pop has
## not run when cutscene B pushes with its own base; B's layer must not end up on A's base.
func test_a_push_after_every_older_owner_left_rebases_the_stack() -> void:
	var low := GraphicsSettings.new()
	low.set_preset("low")
	var before := GraphicsSettings._viewport_state(_vp)
	var planned := GraphicsSettings.override_state({"scaling_mode": "fsr"}, low)
	var owner_a := _owner("A")
	var a := GraphicsSettings.push_override(owner_a, {"aa": "taa"}, null, _base)
	_vp.remove_child(owner_a)  # the old scene leaves; its pop is deferred to the end of the frame
	var b := GraphicsSettings.push_override(_owner("B"), {"scaling_mode": "fsr"}, null, low)
	assert_true(b > 0, "applied")
	GraphicsSettings._owner_left(a)  # the end of the frame
	assert_eq(GraphicsSettings.active_overrides(), 1, "only B is left")
	assert_eq(GraphicsSettings.override_state(), planned, "B's layer on B's own Low base")
	assert_true(GraphicsSettings.pop_override(b))
	assert_eq(GraphicsSettings._viewport_state(_vp), before, "the state before A, exactly")
	_vp.add_child(owner_a)
	_done()


## M2-NIT-03 (review-sweep-M S3): the stack keeps a copy of its base, so changing the caller's
## settings afterwards (or the player's cached ones) cannot move an active override.
func test_the_stack_keeps_a_copy_of_its_base() -> void:
	var planned := GraphicsSettings.override_state(STORM_CLOSEUP, _base)
	var h := GraphicsSettings.push_override(_owner("Cutscene"), STORM_CLOSEUP, null, _base)
	_base.set_preset("low")
	assert_eq(GraphicsSettings.override_state(), planned, "still on the High base it was pushed with")
	assert_false(GraphicsSettings._override_settings == _base, "a copy, not the caller's instance")
	assert_true(GraphicsSettings.pop_override(h))
	var copy := _base.copy()
	assert_true(copy.same_as(_base))
	copy.set_preset("high")
	assert_eq(_base.preset_id, "low", "a copy is independent")
	assert_false(copy.same_as(_base))
	_done()


func test_the_player_settings_are_read_once() -> void:  # M1-NIT-02 (review-sweep-L S3)
	var first := GraphicsSettings._override_settings_or_player()
	assert_true(GraphicsSettings._override_settings_or_player() == first, "cached while settings.cfg is unchanged")
	GraphicsSettings._player_settings = null
	assert_false(GraphicsSettings._override_settings_or_player() == first, "read again once invalidated")
	_done()


func test_invalid_overrides_change_nothing() -> void:
	var before := GraphicsSettings._viewport_state(_vp)
	var owner := _owner("Cutscene")
	assert_eq(GraphicsSettings.push_override(owner, {"ssr": false}, null, _base), 0, "not an override key")
	assert_eq(GraphicsSettings.push_override(owner, {"aa": "msaa_16x"}, null, _base), 0, "not an option")
	assert_eq(GraphicsSettings.push_override(owner, {}, null, _base), 0, "nothing to apply")
	var outside := Node.new()
	assert_eq(GraphicsSettings.push_override(outside, STORM_CLOSEUP, null, _base), 0, "no viewport")
	outside.free()
	assert_eq(GraphicsSettings.active_overrides(), 0)
	assert_eq(GraphicsSettings._viewport_state(_vp), before)
	_done()


func test_overrides_never_touch_the_player_settings() -> void:
	var cfg_existed := FileAccess.file_exists(GraphicsSettings.CONFIG_PATH)
	var overrides_before := _base.overrides.duplicate()
	var h := GraphicsSettings.push_override(_owner("Cutscene"), STORM_CLOSEUP, null, _base)
	GraphicsSettings.pop_override(h)
	assert_eq(_base.overrides, overrides_before, "the player's override layer is untouched")
	assert_eq(_base.preset_id, "high")
	assert_eq(FileAccess.file_exists(GraphicsSettings.CONFIG_PATH), cfg_existed, "settings.cfg never written")
	_done()


func test_listeners_follow_in_the_same_frame() -> void:
	var listener := Listener.new()
	_vp.add_child(listener)
	_nodes.append(listener)
	var h := GraphicsSettings.push_override(_owner("Cutscene"), STORM_CLOSEUP, null, _base)
	assert_eq(listener.calls, 1, "told on push")
	assert_true(listener.seen_taa, "and the viewport already has the override")
	GraphicsSettings.pop_override(h)
	assert_eq(listener.calls, 2, "told on pop")
	assert_false(listener.seen_taa)
	_done()


func test_the_undertow_jitter_gate_follows_the_override() -> void:
	var fxaa := GraphicsSettings.new()
	fxaa.set_preset("high")
	fxaa.set_override("scaling_mode", "bilinear")
	fxaa.set_override("aa", "fxaa")
	GraphicsSettings.execute(_viewport_ops(fxaa.plan()), _vp, null)
	var storm := UndertowStorm.new()
	storm.quality = "high"
	_vp.add_child(storm)
	_nodes.append(storm)
	storm.on_viewport_state_changed()
	assert_false(storm.state.temporal_aa, "FXAA: no temporal jitter")
	var h := GraphicsSettings.push_override(_owner("Cutscene"), {"aa": "taa"}, null, fxaa)
	assert_true(storm.state.temporal_aa, "TAA from the push, before any frame")
	GraphicsSettings.pop_override(h)
	assert_false(storm.state.temporal_aa, "and off again on the pop")
	_done()


func test_prewarm_can_match_a_planned_override() -> void:
	var planned := GraphicsSettings.override_state(STORM_CLOSEUP, _base)
	assert_eq(int(planned["scaling_3d_mode"]), Viewport.SCALING_3D_MODE_FSR)
	assert_true(bool(planned["use_taa"]))
	assert_eq(_vp.scaling_3d_mode, Viewport.SCALING_3D_MODE_FSR2, "planning applies nothing")
	var pw := (load(ShaderPrewarm.SCENE_PATH) as PackedScene).instantiate() as ShaderPrewarm
	pw.viewport_state = planned
	_vp.add_child(pw)
	_nodes.append(pw)
	pw.match_viewport(_vp)
	var stage := pw.get_node("Viewport") as SubViewport
	assert_eq(stage.scaling_3d_mode, Viewport.SCALING_3D_MODE_FSR, "the stage compiles the override's pipeline")
	assert_true(stage.use_taa)
	_done()
