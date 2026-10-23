class_name DebugHooks
extends RefCounted
## Where the debug overlay finds live game systems (M1-ARC-02), without game code depending on
## anything in game/core/debug/ (which release exports strip).
##
## Game code opts in with a group and a duck-typed method, both plain strings, so nothing breaks
## when the debug folder is absent:
##   battle:     a node in GROUP_BATTLE with `func debug_battle_engine() -> BattleEngine`
##               (fallback: the first node in the current scene whose `engine` property holds a
##               BattleEngine, which already covers BattleController)
##   encounters: a node in GROUP_ENCOUNTERS with `func debug_encounter_state() -> Dictionary`
##               (keys in DebugReadouts.ENCOUNTER_KEYS)
##   lattice:    a node in GROUP_LATTICE with `func debug_lattice() -> LatticeProgress` and
##               optionally `func debug_facets() -> FacetInventory` (fallback: Game.state)
## Debug-side code and tests may also register objects directly; a direct registration wins.

const GROUP_BATTLE := &"debug_battle_engine_source"
const GROUP_ENCOUNTERS := &"debug_encounter_provider"
const GROUP_LATTICE := &"debug_lattice_source"
const METHOD_BATTLE := &"debug_battle_engine"
const METHOD_ENCOUNTERS := &"debug_encounter_state"
const METHOD_LATTICE := &"debug_lattice"
const METHOD_FACETS := &"debug_facets"
const ENGINE_PROPERTY := &"engine"

static var _battle: WeakRef
static var _encounters: WeakRef
static var _lattice: WeakRef


static func register_battle_engine(engine: BattleEngine) -> void:
	_battle = weakref(engine) if engine != null else null


static func register_encounter_provider(provider: Object) -> void:
	if provider != null and not provider.has_method(METHOD_ENCOUNTERS):
		push_warning("DebugHooks: encounter provider lacks %s()" % METHOD_ENCOUNTERS)
		return
	_encounters = weakref(provider) if provider != null else null


static func register_lattice_source(source: Object) -> void:
	_lattice = weakref(source) if source != null else null


static func clear() -> void:
	_battle = null
	_encounters = null
	_lattice = null


## The battle the overlay should show, or null.
static func battle_engine(tree: SceneTree = null) -> BattleEngine:
	var direct := _deref(_battle) as BattleEngine
	if direct != null:
		return direct
	var t := _tree(tree)
	if t == null:
		return null
	for n in t.get_nodes_in_group(GROUP_BATTLE):
		if n.has_method(METHOD_BATTLE):
			var e := n.call(METHOD_BATTLE) as BattleEngine
			if e != null:
				return e
	return discover_battle_engine(t.current_scene)


## Fallback: the first node under `root` (depth-first) with a BattleEngine in `engine`.
static func discover_battle_engine(root: Node) -> BattleEngine:
	if root == null:
		return null
	if ENGINE_PROPERTY in root:
		var e := root.get(ENGINE_PROPERTY) as BattleEngine
		if e != null:
			return e
	for child in root.get_children():
		var found := discover_battle_engine(child)
		if found != null:
			return found
	return null


## The encounter provider (an Object with debug_encounter_state()), or null.
static func encounter_provider(tree: SceneTree = null) -> Object:
	var direct := _deref(_encounters)
	if direct != null:
		return direct
	var t := _tree(tree)
	if t == null:
		return null
	for n in t.get_nodes_in_group(GROUP_ENCOUNTERS):
		if n.has_method(METHOD_ENCOUNTERS):
			return n
	return null


## A live Lattice source (an Object with debug_lattice()), or null for "use Game.state".
static func lattice_source(tree: SceneTree = null) -> Object:
	var direct := _deref(_lattice)
	if direct != null:
		return direct
	var t := _tree(tree)
	if t == null:
		return null
	for n in t.get_nodes_in_group(GROUP_LATTICE):
		if n.has_method(METHOD_LATTICE):
			return n
	return null


## The first FieldCameraDirector in the current scene, or null.
static func camera_director(tree: SceneTree = null) -> FieldCameraDirector:
	var t := _tree(tree)
	if t == null or t.current_scene == null:
		return null
	if t.current_scene is FieldCameraDirector:
		return t.current_scene as FieldCameraDirector
	var found := t.current_scene.find_children("*", "FieldCameraDirector", true, false)
	return found[0] as FieldCameraDirector if not found.is_empty() else null


static func _deref(ref: WeakRef) -> Object:
	return ref.get_ref() as Object if ref != null else null


static func _tree(tree: SceneTree) -> SceneTree:
	return tree if tree != null else Engine.get_main_loop() as SceneTree
