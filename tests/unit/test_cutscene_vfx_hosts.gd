extends TestCase
## M3-ARC-1326: an `@vfx` cue goes first to the stage's VFX hosts (CutsceneVfxHosts: the `cutscene_vfx_hosts` group,
## `play_vfx(effect, at_id, kwargs) -> bool`). A host that takes it means no CutsceneMotes placeholder; a host that
## declines (or none at all) leaves the placeholder drawing as before. The cue's kwargs, cues.json's `follow` and
## `anchors` among them, reach the host whole.

const EFFECT := "glimmer_held"
const MARK := &"by_the_stair"
## A stand-in host: takes the cues whose effect is `takes`, and records every offer.
const HOST_SRC := """
extends Node3D
var takes := ""
var offers: Array = []
func play_vfx(effect: String, at_id: StringName, kwargs: Dictionary) -> bool:
	offers.append([effect, at_id, kwargs])
	return effect == takes
"""

var _nodes: Array[Node] = []


func test_a_host_that_takes_the_cue_means_no_placeholder() -> void:
	var stage := _stage()
	var host := _host_node(EFFECT)
	var seq := _sequencer(stage)
	seq._cue_vfx(_step({"at": String(MARK), "follow": "asha_staff", "anchors": "mourners"}))
	assert_eq(_motes(stage), 0, "the host played it: no placeholder")
	var offers: Array = host.get(&"offers")
	assert_eq(offers.size(), 1, "offered once")
	assert_eq(offers[0][0], EFFECT)
	assert_eq(offers[0][1], MARK, "with its mark")
	var kwargs: Dictionary = offers[0][2]
	assert_eq(kwargs.get("follow"), "asha_staff", "follow reaches the host")
	assert_eq(kwargs.get("anchors"), "mourners", "anchors reach the host")
	_done()


func test_a_host_that_declines_leaves_the_placeholder() -> void:
	var stage := _stage()
	var host := _host_node("glimmer_lift")
	var seq := _sequencer(stage)
	seq._cue_vfx(_step({"at": String(MARK)}))
	assert_eq((host.get(&"offers") as Array).size(), 1, "it was offered")
	assert_eq(_motes(stage), 1, "declined: the placeholder draws")
	_done()


func test_with_no_host_the_placeholder_draws() -> void:
	var stage := _stage()
	var seq := _sequencer(stage)
	seq._cue_vfx(_step({"at": String(MARK)}))
	assert_eq(_motes(stage), 1, "no host: the placeholder draws")
	_done()


func test_the_cue_vocabulary_accepts_follow_and_anchors() -> void:
	var cues := JSON.parse_string(FileAccess.get_file_as_string("res://game/data/dialogue/cues.json")) as Dictionary
	var kwargs := (
		(((cues.get("cues", cues) as Dictionary).get("vfx", {})) as Dictionary).get("kwargs", {}) as Dictionary
	)
	assert_true(kwargs.has("follow"), "follow=<actor> or <actor>_staff")
	assert_true(kwargs.has("anchors"), "anchors=<actor group>")


func _stage() -> CutsceneStage:
	var stage := CutsceneStage.new()
	_add(stage)
	var marks := Node3D.new()
	marks.name = "Marks"
	stage.add_child(marks)
	var m := Marker3D.new()
	m.name = String(MARK)
	m.position = Vector3(1.0, 0.0, 2.0)
	marks.add_child(m)
	return stage


func _host_node(takes: String) -> Node3D:
	var script := GDScript.new()
	script.source_code = HOST_SRC
	script.reload()
	var host := Node3D.new()
	host.set_script(script)
	host.set(&"takes", takes)
	host.add_to_group(CutsceneVfxHosts.GROUP)
	_add(host)
	return host


func _sequencer(stage: CutsceneStage) -> CutsceneSequencer:
	var seq := CutsceneSequencer.new()
	_add(seq)
	seq.config = CutsceneSequencer.load_config() if seq.has_method(&"load_config") else seq.config
	if not (seq.config.get("vfx", {}) as Dictionary).has(EFFECT):
		var cfg: Variant = JSON.parse_string(FileAccess.get_file_as_string("res://game/data/cutscene/sequencer.json"))
		seq.config = cfg as Dictionary
	seq._stage = stage
	return seq


func _step(kwargs: Dictionary) -> DialogueStep:
	var step := DialogueStep.new()
	step.cue = &"vfx"
	step.args = [EFFECT]
	step.kwargs = kwargs
	return step


## CutsceneMotes placeholders spawned under the stage.
func _motes(stage: Node) -> int:
	var n := 0
	for c in stage.find_children("*", "", true, false):
		if c is CutsceneMotes:
			n += 1
	return n


func _add(n: Node) -> void:
	(Engine.get_main_loop() as SceneTree).current_scene.add_child(n)
	_nodes.append(n)


func _done() -> void:
	for n in _nodes:
		if is_instance_valid(n):
			n.free()
	_nodes.clear()
