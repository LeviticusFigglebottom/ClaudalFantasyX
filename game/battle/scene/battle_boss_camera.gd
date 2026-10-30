class_name BattleBossCamera
extends Node
## M3-BPR-426 (the Lead: "boss-fight camera choreography: intro, phase change, finisher"): the camera's moments in a
## boss fight, besides its intro (BattleBossIntro) and its big moves (camera.enemy_by_skill). Listens only:
## - **phase change**: once the action that turned it has played, the camera holds a shot of the boss
##   (choreo.json camera.moments.phase), so the change reads;
## - **the fall**: once the finishing blow has played, it holds on the falling boss (moments.fall).
## The boss is the encounter's boss_intro row's enemy, framed as its intro frames it (BattleBossIntro._frame_boss:
## the hero shot, else the fitted shot), recomputed when the moment plays. The director plays each (play_moment):
## none under reduced motion or skipped animations, and the next turn waits for it (BattleChoreo.busy_sec).

var choreo: BattleChoreo
var engine: BattleEngine
var boss_id: StringName = &""
var cfg: Dictionary = {}
var _fell := false


## Builds it when the encounter has a boss intro row whose enemy is in the fight (else null).
static func attached(sequencer: BattleChoreo, battle: BattleEngine) -> BattleBossCamera:
	var moments := (sequencer.data.get("camera", {}) as Dictionary).get("moments", {}) as Dictionary
	if moments.is_empty() or battle == null:
		return null
	var ids: Array[StringName] = []
	for e in battle.enemies:
		ids.append(e.id)
	var intro_cfg := sequencer.data.get(BattleBossIntro.KEY, {}) as Dictionary
	var row := BattleBossIntro.row_for(intro_cfg, battle.encounter_id, ids)
	var base := str(row.get("enemy", ""))
	for e in battle.enemies:
		if base != "" and String(e.id).get_slice("#", 0) == base:
			var b := BattleBossCamera.new()
			b.name = "BattleBossCamera"
			sequencer.add_child(b)  # lives as long as the battle's sequencer (a RefCounted would be freed at once)
			b.choreo = sequencer
			b.engine = battle
			b.boss_id = e.id
			b.cfg = moments
			battle.phase_changed.connect(b._on_phase_changed)
			sequencer.contact.connect(b._on_contact)
			return b
	return null


func _on_phase_changed(enemy: BattleCombatant, _phase_id: StringName) -> void:
	if enemy.id == boss_id and enemy.is_alive():
		choreo.after_sequence(_play.bind("phase"))


func _on_contact(_result: ActionResult) -> void:
	var b := engine.find(boss_id)
	if not _fell and b != null and b.hp <= 0:
		_fell = true
		choreo.after_sequence(_play.bind("fall"))


func _play(which: String) -> void:
	var row := cfg.get(which, {}) as Dictionary
	var intro := BattleBossIntro.of(choreo._ctl.stage)
	if row.is_empty() or choreo.camera == null or intro == null:
		return
	# the intro's own framing of the boss, as it stands now (BattleBossHeroShot, M3-BPR-423)
	intro.hero_override = row.get("hero", {}) as Dictionary
	intro._frame_boss(which == "fall")
	intro.hero_override = {}
	choreo.camera.play_moment(
		StringName(which),
		intro._pose,
		float(row.get("in_sec", 0.0)),
		float(row.get("hold_sec", 0.0)),
		float(row.get("out_sec", 0.0))
	)
