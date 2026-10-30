extends TestCase
## M3-C09-03 with M3-ARC-1326: every `@vfx glimmer_held` cue Ch9's compiled scenes play reaches the real Ebbing on
## `ch09/corrow_night`, through the sequencer's stage VFX hosts, and no placeholder motes spawn. Until the hook
## (game/cutscene/cutscene_vfx_hosts.gd) is on this branch the sequencer has no hosts to offer, and the test only
## checks that the cues exist.

const HOOK := "res://game/cutscene/cutscene_vfx_hosts.gd"
const SHOTS := "res://game/levels/_tests/ebbing/ebbing_shots.tscn"
const SCENES := [
	"res://game/data/dialogue/compiled/ch09_strand.json", "res://game/data/dialogue/compiled/ch09_the_ebbing.json"
]
const SEQUENCER_CONFIG := "res://game/data/cutscene/sequencer.json"
const EFFECT := "glimmer_held"
## The sequencer's placeholder nodes are named Vfx_<effect>_<n>, whatever it draws them with.
const PLACEHOLDER_PREFIX := "Vfx_"


func test_every_ch09_held_cue_plays_the_real_ebbing() -> void:
	var cues := _held_cues()
	assert_true(cues.size() >= 8, "Ch9 cues its held motes (%d)" % cues.size())
	if not ResourceLoader.exists(HOOK):
		return  # the hook lands with M3-ARC-1326; nothing to route the cues through yet
	var rig := (load(SHOTS) as PackedScene).instantiate() as EbbingShotRig
	(Engine.get_main_loop() as SceneTree).current_scene.add_child(rig)
	var stage := rig.zone.find_child("CutsceneStage", true, false) as CutsceneStage
	assert_true(stage != null, "the zone has its cutscene stage")
	var seq := CutsceneSequencer.new()
	rig.add_child(seq)
	seq.config = JSON.parse_string(FileAccess.get_file_as_string(SEQUENCER_CONFIG)) as Dictionary
	seq._stage = stage
	for op: Dictionary in cues:
		var step := DialogueStep.new()
		step.cue = &"vfx"
		step.args = op["args"]
		step.kwargs = op["kwargs"]
		seq._cue_vfx(step)
		var at := StringName(str(step.kwargs.get("at", "")))
		assert_true(rig.ebbing.fields.has(at), "the Ebbing plays %s" % at)
	assert_eq(_placeholders(rig), 0, "no placeholder motes: every held cue went to the Ebbing")
	rig.free()


## The compiled `vfx glimmer_held` ops of Ch9's scenes.
func _held_cues() -> Array[Dictionary]:
	var out: Array[Dictionary] = []
	for path: String in SCENES:
		var data := JSON.parse_string(FileAccess.get_file_as_string(path)) as Dictionary
		for node: Variant in (data.get("nodes", {}) as Dictionary).values():
			for op: Variant in (node as Dictionary).get("ops", []):
				var o := op as Dictionary
				if str(o.get("cue", "")) == "vfx" and (o.get("args", []) as Array).has(EFFECT):
					out.append(o)
	return out


func _placeholders(root: Node) -> int:
	var n := 0
	for c: Node in root.find_children(PLACEHOLDER_PREFIX + "*", "", true, false):
		n += 1
	return n
