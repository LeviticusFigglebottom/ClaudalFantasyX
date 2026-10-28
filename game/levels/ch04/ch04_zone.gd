class_name Ch04Zone
extends Ch01Zone
## A Ch4 greybox zone root (M3-C04-02; docs/kb/tech/chapter_flow.md "Ch4"). It reuses Ch01Zone's story
## calls as they are (rest, give, hide_block / show_block; Ch1's tutorial prompt table goes unused
## here, because Ch4's prompts are battle prompts) and adds the one thing Ch4's two zones need: a zone
## whose dressing follows the story flags, so it comes back right after a battle or a reload.
##   layout "states": [{"flag": f, "hide": [ids], "show": [ids], "place": {actor id: mark id}}]
##     Applied in order once the zone is ready, and again by refresh_states() (a `zone` step after a
##     scene that set a flag). Each row whose flag is set hides and shows its Greybox blocks or stage
##     actors (Ch01Zone.hide_block / show_block: a block's collision goes with it), and stands the
##     stage actors it places on those marks. Rhen is never one.
## Haluna's wake-night uses it for the windows going dark, Asha's shell in the wall, the village going
## home and the stranger at the wall; the ferry for the party crossing to the derelict and back, its
## sails, the wraith and the board. A battle reloads the zone, so this is what keeps it right.
## Kit collision (ADR 0200): the layout's "collision_path" and "ramps" (KitCollision).
## The wake on the real Haluna (ADR 0041): a layout "dressing" that is Haluna's (its Terrain and Dresser) gets
## Haluna's runtime walk collision, configured as ch02/haluna's own Collision node is (read from that scene,
## so the two never drift); "dressing_mood" sets its HalunaMood (&"night"); and a states row's
## "show_sets" / "hide_sets" show or hide the dresser's story sets (env-art's StorySet_<name>: the wake's
## lamps and feast, the shells). Its field camera is ch02/haluna's too: that scene's CameraVolumes (the composed
## lane, market, dock and chapel shots over the hub orbit) are rebuilt here from its SceneState, so the wake's
## field never frames the player through a roof.

const KEY_STATES := "states"
const KEY_PLACE := "place"
const KEY_SHOW_SETS := "show_sets"
const KEY_HIDE_SETS := "hide_sets"
const KEY_MOOD := "dressing_mood"
const HALUNA_SCENE := "res://game/levels/ch02/haluna/haluna.tscn"
const HALUNA_COLLISION := ^"Collision"
const HALUNA_VOLUMES := "CameraVolumes"
const HALUNA_COLLISION_EXPORTS: Array[StringName] = [
	&"walk_rect",
	&"cell_m",
	&"wade_m",
	&"shore_step_m",
	&"wall_height_m",
	&"wall_thickness_m",
	&"shore_gaps",
	&"piece_rules",
	&"default_rule",
	&"ramp_thickness_m",
	&"piece_margin_m"
]

## Haluna's walk collision when the dressing is Haluna's, else null.
var haluna_collision: HalunaCollision


func _ready() -> void:
	super()
	if dressing != null and layout.has(KEY_MOOD):
		dressing.set(&"mood", StringName(str(layout[KEY_MOOD])))
	refresh_states()


## The layout's dressing (GreyboxZone), and Haluna's walk collision when it is Haluna.
func _build_dressing() -> void:
	super()
	if dressing == null:
		return
	var terrain := dressing.get_node_or_null(^"Terrain") as HalunaTerrain
	var dresser := dressing.get_node_or_null(^"Dresser") as HalunaDresser
	if terrain == null or dresser == null:
		return
	for shrine in dressing.find_children("*", "", true, false):  # the dressing's shrine rests the party here
		if shrine is SaveShrine:
			(shrine as SaveShrine).location_id = location_id
	haluna_collision = HalunaCollision.new()
	haluna_collision.name = "HalunaCollision"
	_copy_haluna_collision_exports(haluna_collision)
	haluna_collision.terrain = terrain
	haluna_collision.dresser = dresser
	add_child(haluna_collision)
	haluna_collision.build()
	add_child(_haluna_camera_volumes())


## ch02/haluna's Collision node's exported tuning, read from its scene without instancing it.
static func _copy_haluna_collision_exports(to: HalunaCollision) -> void:
	var state := (load(HALUNA_SCENE) as PackedScene).get_state()
	for i in state.get_node_count():
		if String(state.get_node_path(i)).trim_prefix("./") != String(HALUNA_COLLISION):
			continue
		for k in state.get_node_property_count(i):
			var key := state.get_node_property_name(i, k)
			if HALUNA_COLLISION_EXPORTS.has(key):
				to.set(key, state.get_node_property_value(i, k))
		return


## ch02/haluna's camera volumes (each a transform, a shot, a priority and its Shape), read from its scene.
static func _haluna_camera_volumes() -> Node3D:
	var root := Node3D.new()
	root.name = "HalunaCameraVolumes"
	var state := (load(HALUNA_SCENE) as PackedScene).get_state()
	for i in state.get_node_count():
		var path := String(state.get_node_path(i)).trim_prefix("./").split("/")
		if path.size() < 2 or path[0] != HALUNA_VOLUMES:
			continue
		var node: Node3D = CameraVolume.new() if path.size() == 2 else CollisionShape3D.new()
		node.name = path[-1]
		for k in state.get_node_property_count(i):
			var key := state.get_node_property_name(i, k)
			if key != &"script":
				node.set(key, state.get_node_property_value(i, k))
		var parent := root if path.size() == 2 else root.get_node_or_null(NodePath(path[1]))
		if parent != null:
			parent.add_child(node)
	return root


## The layout's blocks plus its collision file's; then the ramps (KitCollision).
func _build_blocks() -> void:
	KitCollision.merge(self)
	super()
	KitCollision.build_ramps(self)


## Applies every "states" row whose flag is set (see the class comment).
func refresh_states() -> void:
	for row: Dictionary in layout.get(KEY_STATES, []):
		if not bool(Game.get_flag(StringName(str(row.get("flag", ""))))):
			continue
		for id: Variant in row.get("hide", []):
			hide_block(str(id))
		for id: Variant in row.get("show", []):
			show_block(str(id))
		for id: Variant in row.get(KEY_SHOW_SETS, []):
			_story_set(str(id), true)
		for id: Variant in row.get(KEY_HIDE_SETS, []):
			_story_set(str(id), false)
		var place: Dictionary = row.get(KEY_PLACE, {})
		for id: Variant in place:
			place_actor(str(id), str(place[id]))


## Stands stage actor `id` on mark `mark_id` (its position and facing). False when either is missing.
func place_actor(id: String, mark_id: String) -> bool:
	var a := stage.actor(StringName(id))
	var m := stage.mark(StringName(mark_id))
	if a == null or m == null or a is FieldController:
		push_warning("Ch04Zone %s: cannot place '%s' on '%s'" % [location_id, id, mark_id])
		return false
	a.transform = m.transform  # Actors/ and Marks/ are sibling groups of the stage: one frame
	return true


## Whether the dressing dresser's story set `set_name` shows (false when there is none).
func story_set_shown(set_name: String) -> bool:
	var node := _story_set_node(set_name)
	return node != null and node.visible


func _story_set_node(set_name: String) -> Node3D:
	var dresser := dressing.get_node_or_null(^"Dresser") as HalunaDresser if dressing != null else null
	return dresser.story_set(StringName(set_name)) if dresser != null else null


## Shows or hides the dressing dresser's story set `set_name` (HalunaDresser.story_set).
func _story_set(set_name: String, shown: bool) -> void:
	var node := _story_set_node(set_name)
	if node == null:
		push_warning("Ch04Zone %s: no story set '%s'" % [location_id, set_name])
		return
	node.visible = shown
