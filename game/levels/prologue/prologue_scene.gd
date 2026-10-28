class_name PrologueScene
extends Node3D
## The prologue (SPEC §3.5; M2-FP-03; docs/kb/tech/first_playable_flow.md): New Game lands here
## (locations.json new_game). The dead city of Iskarra at dusk (env-art's kit, M3-ENV-711), staged for the
## `prologue_dead_city` cutscene: one Camera3D under a FieldCameraDirector, a CutsceneStage with
## Shots/P01 and P02, the vigil's cast under Actors (Rhen, Asha and Toma take their HeroFieldActor
## bodies at _ready, Ysolde is her model; M2-FP-103), and Spawns/Start. There is no player; place_at()
## stands in for one, so the location registry (and tools/validate_data.py) count the scene as playable.
##
## When it is the current scene (and `autoplay` is on) it sets `prologue_seen`, plays the cutscene,
## then sends the party to first_playable.json prologue.next_location / next_spawn through
## SceneRouter.world_return. That is a switch: the M2 slice route (ch02/haluna at Beach) until the
## human signs off the M2 review, then Act I (ch01/oruvel_underway at Drop, M3-C01-02; the debug
## chapter select reaches Ch1 before then). Tests instance it with autoplay off and call play().

signal handed_off(location_id: StringName, spawn: StringName)

const KEY_SCENE_ID := "scene_id"
const KEY_NEXT_LOCATION := "next_location"
const KEY_NEXT_SPAWN := "next_spawn"
const VIGILS := ^"City/Vigils"
const VIGIL_FEET := &"Feet"

## Play the cutscene on entering the tree as the current scene. Tests turn it off.
@export var autoplay := true

## The sequencer play() uses; one is made (and added as a child) when unset. Tests set an instant one.
var sequencer: CutsceneSequencer
## How the hand-off travels: (location_id: StringName, spawn: StringName) -> bool. Unset =
## SceneRouter.world_return.go_to. Tests set a recorder.
var travel: Callable = Callable()
## Where the hand-off goes when set; unset = first_playable.json prologue.next_location / next_spawn.
## Tests of the Act I route set it.
var next_location: StringName = &""
var next_spawn: StringName = &""
## True once the hand-off was requested (it happens once).
var finished := false

@onready var stage: CutsceneStage = $CutsceneStage
@onready var director: FieldCameraDirector = $CameraDirector


func _ready() -> void:
	# M2-FP-103: the vigil's heroes wear their real bodies (HeroFieldActor), not capsules.
	HeroFieldActor.attach_stage(stage)
	dress_vigils()
	if autoplay:
		_autoplay.call_deferred()


## M3-ENV-724: the vigils still without a model (City/Vigils: Kerrid, Pell, Liss) stand as cloth-coloured
## capsules centred on the figure. Each takes its hero's field body once hero_motion.json lists one (the
## character track's hero tasks), feet at the capsule's foot, and its capsule goes. Returns the bodies.
func dress_vigils() -> Array[HeroFieldActor]:
	var out: Array[HeroFieldActor] = []
	for n in get_node(VIGILS).get_children():
		var fig := n as MeshInstance3D
		var id := StringName(String(n.name).to_lower())
		if fig == null or fig.mesh == null or HeroFieldActor.scene_path(id) == "":
			continue
		var feet := Marker3D.new()
		feet.name = VIGIL_FEET
		fig.add_child(feet)
		feet.position = Vector3(0.0, fig.get_aabb().position.y, 0.0)
		var body := HeroFieldActor.attach_actor(feet, id)
		if body != null:
			fig.mesh = null
			out.append(body)
	return out


## The player stand-in WorldReturn calls after a swap: the camera is the shot's, so there is
## nothing to move. Returns true (the scene is ready to be seen).
func place_at(_spawn: StringName, _yaw_deg: float = 0.0) -> bool:
	return true


## Sets prologue_seen, plays the cutscene to its end, then hands off. Await it.
func play() -> void:
	Game.set_flag(&"prologue_seen")
	if sequencer == null:
		sequencer = CutsceneSequencer.new()
		sequencer.name = "Sequencer"
		add_child(sequencer)
	var cfg := FirstPlayableConfig.section(FirstPlayableConfig.SECTION_PROLOGUE)
	var scene_id := StringName(str(cfg.get(KEY_SCENE_ID, "")))
	var played: bool = await sequencer.play(scene_id, stage)
	if not played:
		push_error("PrologueScene: could not play '%s'" % scene_id)
	await _router_idle()
	hand_off()


## Sends the party on to the first chapter's location. Returns false when it already did, or when
## the travel could not be requested.
func hand_off() -> bool:
	if finished:
		return false
	finished = true
	var cfg := FirstPlayableConfig.section(FirstPlayableConfig.SECTION_PROLOGUE)
	var loc := next_location if next_location != &"" else StringName(str(cfg.get(KEY_NEXT_LOCATION, "")))
	var spawn := next_spawn if next_location != &"" else StringName(str(cfg.get(KEY_NEXT_SPAWN, "")))
	handed_off.emit(loc, spawn)
	if travel.is_valid():
		return bool(travel.call(loc, spawn))
	if not is_inside_tree():
		return false
	return SceneRouter.world_return.go_to(loc, spawn)


func _autoplay() -> void:
	if is_inside_tree() and get_tree().current_scene == self:
		await play()


## The router ignores a change while its own swap into this scene is still running (a short or
## instant cutscene can end that soon), so the real hand-off waits for it. Returns at once when
## the travel is injected or the scene is not in the tree.
func _router_idle() -> void:
	if travel.is_valid():
		return
	while is_inside_tree() and SceneRouter.is_busy():
		await get_tree().process_frame
