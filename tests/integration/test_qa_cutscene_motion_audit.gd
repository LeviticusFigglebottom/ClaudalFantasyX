extends TestCase
## Integration QA (M3-HER-1132): which chapter cutscenes still play placeholder motion. Every in-engine cutscene the
## game plays (HeroGuardSources.cutscenes(): the prologue, Haluna's and every chapter's play steps) runs instantly on
## its own zone's stage, and each @anim cue is sorted by what the actor really does:
##   real   the actor's body or player has the clip (or a built clip stands in for it, CutsceneClips.built)
##   mark   a placeholder clip mark: the actor glides onto a spot instead (CutsceneStage.clip_marks)
##   none   no clip at all: a capsule, or a rig without that clip; the cue does nothing
##   absent the cue names an actor the stage doesn't have
## (`@anim <id> look_at <target>` is a turn the sequencer performs, not a clip: counted as real.)
## plus the capsule actors the scene names, and its "(placeholder)" cue features. One AUDIT line per scene. It
## reports; it doesn't fail: the gaps are tasks (docs/kb/qa/act1_hero_motion_audit.md).

const STANDIN := "StandIn"


func test_every_cutscene_reports_its_motion() -> void:
	var state_was := Game.state
	Game.state = GameStateData.new()
	Game.state.party_ids = [&"rhen", &"asha", &"toma"] as Array[StringName]
	var played := 0
	var scenes := HeroGuardSources.cutscenes()
	for path: String in scenes:
		for scene_id: String in scenes[path]:
			var zone := (load(path) as PackedScene).instantiate() as Node3D
			if "autoplay" in zone:
				zone.set(&"autoplay", false)
			_host().add_child(zone)
			var line := audit(zone, StringName(scene_id))
			zone.free()
			if line != "":
				played += 1
				print("AUDIT %s %s" % [path.get_file(), line])
	Game.state = state_was
	assert_true(played > 0, "cutscenes were audited (%d)" % played)


## Plays `scene_id` instantly on the zone's stage and returns its AUDIT line ("" when it can't play there).
static func audit(zone: Node3D, scene_id: StringName) -> String:
	var stage := zone.get(&"stage") as CutsceneStage if "stage" in zone else null
	if stage == null:
		for n in zone.find_children("*", "Node3D", true, false):
			if n is CutsceneStage:
				stage = n as CutsceneStage
				break
	if stage == null:
		return ""
	var story := zone.get(&"story") as ZoneStory if "story" in zone else null
	if story != null:
		story.autostart = false
	var seq := CutsceneSequencer.new()
	seq.instant = true
	zone.add_child(seq)
	var counts := {"real": 0, "mark": 0, "none": 0, "absent": 0}
	var gaps: Array[String] = []
	var capsules: Array[String] = []
	seq.cue_played.connect(
		func(cue: StringName, args: Array, _kw: Dictionary) -> void:
			if args.is_empty():
				return
			var id := StringName(str(args[0]))
			var actor := stage.actor(id)
			if actor != null and _is_capsule(actor) and not capsules.has(String(id)):
				capsules.append(String(id))
			if cue != &"anim" or args.size() < 2:
				return
			var clip := StringName(str(args[1]))
			var kind := _kind(seq, stage, id, actor, clip)
			counts[kind] = int(counts[kind]) + 1
			if kind != "real":
				gaps.append("%s/%s:%s" % [id, clip, kind])
	)
	seq.play(scene_id, stage)
	var placeholders: Array[String] = []
	for w in seq.warnings:
		if w.contains("(placeholder)"):
			placeholders.append(w.get_slice("): ", 1).trim_suffix(" is not performed yet (placeholder)"))
	seq.free()
	capsules.sort()
	return (
		"%s real=%d mark=%d none=%d absent=%d placeholder_cues=[%s] capsules=[%s] gaps=[%s]"
		% [
			scene_id,
			counts["real"],
			counts["mark"],
			counts["none"],
			counts["absent"],
			", ".join(placeholders),
			", ".join(capsules),
			", ".join(gaps)
		]
	)


static func _kind(
	seq: CutsceneSequencer, stage: CutsceneStage, id: StringName, actor: Node3D, clip: StringName
) -> String:
	if actor == null:
		return "absent"
	if stage.clip_mark(id, clip) != null and not CutsceneClips.has_clip(actor, clip):
		return "mark"
	if clip == CutsceneSequencer.ANIM_LOOK_AT:
		return "real"
	var built := CutsceneClips.built(seq.config, id, actor, clip)
	return "real" if CutsceneClips.has_clip(actor, built) else "none"


## A stage actor still drawn as its stand-in capsule (a visible StandIn mesh, no hero body).
static func _is_capsule(actor: Node3D) -> bool:
	var s := actor.get_node_or_null(STANDIN) as GeometryInstance3D
	return s != null and s.is_visible_in_tree() and HeroMotion.body_of(actor) == null


func _host() -> Node:
	return (Engine.get_main_loop() as SceneTree).current_scene
