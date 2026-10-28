extends TestCase
## M3-CRE-639: a Vowbound's entrance and dismissal play its model's own clips (Ilun's `rise` and `dismiss`, choreo.json
## clip_own) when it has them, the contract clip (`ready`) otherwise.

const ILUN_SCENE := "res://game/creatures/ilun/ilun_battle.tscn"
const PLAIN_SCENE := "res://game/creatures/reef_crab/reef_crab_battle.tscn"


func _clip_for(scene: String, spec: Dictionary) -> StringName:
	var n := (load(scene) as PackedScene).instantiate()
	var tree := Engine.get_main_loop() as SceneTree
	(tree.current_scene if tree.current_scene != null else tree.root).add_child(n)
	var clip := BattleChoreo.spec_clip(n, spec)
	n.get_parent().remove_child(n)
	n.free()
	return clip


func test_ilun_rises_and_folds_on_his_own_clips() -> void:
	var data := BattleChoreo.load_data()
	var vb := data["vowbound"] as Dictionary
	var cine := (data["summon_cinematic"] as Dictionary)["entry"] as Dictionary
	assert_eq(_clip_for(ILUN_SCENE, vb["entry"]), &"rise", "the entry rises")
	assert_eq(_clip_for(ILUN_SCENE, cine), &"rise", "the first call's cinematic rises")
	assert_eq(_clip_for(ILUN_SCENE, vb["dismiss"]), &"dismiss", "the dismissal folds")


func test_a_model_without_them_plays_the_contract_clip() -> void:
	var vb := BattleChoreo.load_data()["vowbound"] as Dictionary
	assert_eq(_clip_for(PLAIN_SCENE, vb["entry"]), &"ready")
	assert_eq(_clip_for(PLAIN_SCENE, vb["dismiss"]), &"ready")
