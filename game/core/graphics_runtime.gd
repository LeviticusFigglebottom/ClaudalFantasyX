class_name GraphicsRuntime
extends RefCounted
## Applies the player's graphics settings to the running game (M1-ARC-15). GraphicsSettings
## (Rendering-owned) plans and executes; this class decides when and on what:
##   boot(viewport)        boot.gd, before the first scene: loads user://settings.cfg (or the default
##                         preset), applies the global part (Viewport + RenderingServer) and arms
##                         the per-scene hook.
##   apply_scene(root)     SceneRouter, once the new scene is in the tree, on the main thread (HalunaZone
##                         prebuilds on a worker thread, so nothing here may run before that): the
##                         scene's Environment gates and sky_detail uniforms, the vegetation groups,
##                         the shader families, and the per-system tiers (water, weathering, Undertow,
##                         glimmer, characters).
##   select_preset() / set_override() / apply_now()
##                         the graphics settings menu: change, save, then apply everything at once.
##   current_warm_up()     the resident warm-up while it runs (M2-ARC-03: a BootCard waits for it).
## Tests and screenshot captures never call boot(), so nothing is applied there unless they do it
## themselves, and the hook stays disarmed (`armed`).

## True once boot() ran: SceneRouter applies the per-scene part after each swap only when armed.
static var armed := false
## Where the settings persist (tests point it at their own file).
static var config_path := GraphicsSettings.CONFIG_PATH
## The last warm-up warm_resident_shaders() spawned (null before any; freed once it is done). The
## Graphics menu holds its fade until a warm-up its preset change spawned is done (M1-UI-11).
static var last_warmup: ShaderPrewarm

static var _settings: GraphicsSettings
static var _warm_up: WeakRef


## The game's settings (loaded from config_path on first use; the default preset when absent).
static func settings() -> GraphicsSettings:
	if _settings == null:
		_settings = GraphicsSettings.new()
		_settings.load_config(config_path)
	return _settings


## Replaces the shared settings (tests; null makes the next settings() reload from config_path).
static func set_settings(gs: GraphicsSettings) -> void:
	_settings = gs


## Boot: applies the saved (or default) preset's global part and arms the per-scene hook.
static func boot(viewport: Viewport) -> void:
	armed = true
	apply_global(viewport)


## Viewport and RenderingServer operations only (they outlive scene changes).
static func apply_global(viewport: Viewport) -> int:
	return GraphicsSettings.execute(_ops_for(settings().plan(), true), viewport, null)


## The per-scene part, on a scene already in the tree. Returns the number of operations applied plus
## the materials and system tiers changed (for logs and tests).
static func apply_scene(root: Node) -> int:
	if root == null or not root.is_inside_tree():
		return 0
	var gs := settings()
	var applied := GraphicsSettings.execute(_ops_for(gs.plan(), false), root.get_viewport(), scene_environment(root))
	applied += gs.apply_tiers(root)
	return applied + apply_system_tiers(root, gs.preset_id)


## SceneRouter's hook: apply_scene() when boot armed it; a no-op otherwise.
static func on_scene_entered(root: Node) -> int:
	return apply_scene(root) if armed else 0


## Global and per-scene parts at once (after a settings change). `viewport` is the game's root
## viewport; its current scene gets the per-scene part.
static func apply_now(viewport: Viewport) -> int:
	var applied := apply_global(viewport)
	var tree := viewport.get_tree() if viewport != null and viewport.is_inside_tree() else null
	if tree != null and tree.current_scene != null:
		applied += apply_scene(tree.current_scene)
	return applied


## Settings menu: selects a preset (clearing overrides), saves and applies it.
static func select_preset(id: String, viewport: Viewport) -> bool:
	if not settings().set_preset(id):
		return false
	settings().save_config(config_path)
	apply_now(viewport)
	if armed and viewport != null and viewport.is_inside_tree():
		warm_resident_shaders(viewport)  # the new preset's tier variants (M1-RND-22)
	return true


## Compiles the current preset's resident shaders under `parent` (ShaderPrewarm.spawn_resident): at boot,
## and after a preset change. Returns the warm-up node (null without a parent in the tree).
static func warm_resident_shaders(parent: Node) -> ShaderPrewarm:
	if parent == null or not parent.is_inside_tree():
		return null
	var node := ShaderPrewarm.spawn_resident(parent, settings().preset_id)
	_warm_up = weakref(node)
	last_warmup = node
	return node


## M2-ARC-03: the last resident warm-up while it runs (null once it has finished or been freed), so a
## caller that did not spawn it (select_preset's) can wait for it, e.g. BootCard.wait_for_node().
static func current_warm_up() -> ShaderPrewarm:
	var node := _warm_up.get_ref() as ShaderPrewarm if _warm_up != null else null
	return node if node != null and node.is_running() else null


## Settings menu: one custom value on top of the preset; saved and applied.
static func set_override(key: String, value: Variant, viewport: Viewport) -> bool:
	if not settings().set_override(key, value):
		return false
	settings().save_config(config_path)
	apply_now(viewport)
	return true


## The Environment of the first WorldEnvironment under `root` (null when the scene has none).
static func scene_environment(root: Node) -> Environment:
	var envs := root.find_children("*", "WorldEnvironment", true, false)
	if root is WorldEnvironment:
		envs.push_front(root)
	return (envs[0] as WorldEnvironment).environment if not envs.is_empty() else null


## Tiers of the systems that keep their own preset maps (graphics_presets.json "system_tiers_note"):
## WaterSurface, WeatheringTide, UndertowStorm, GlimmerField, UnderwaterRig, and character materials. Only nodes
## whose tier differs are touched (a storm or glimmer change rebuilds). Returns how many changed.
static func apply_system_tiers(root: Node, preset: String) -> int:
	var changed := 0
	var nodes: Array[Node] = [root]
	nodes.append_array(root.find_children("*", "", true, false))
	for n in nodes:
		if n is WaterSurface:
			var water := n as WaterSurface
			var wq := WaterSurface.quality_for_preset(preset)
			if water.quality != wq:
				water.quality = wq
				changed += 1
		elif n is WeatheringTide:
			var tide := n as WeatheringTide
			var tq := WeatheringTide.quality_for_preset(preset)
			if tide.quality != tq:
				tide.quality = tq
				changed += 1
		elif n is UndertowStorm:
			var storm := n as UndertowStorm
			if storm.get_quality() != preset and storm.set_quality(preset):
				changed += 1
		elif n is GlimmerField:
			var field := n as GlimmerField
			if field.get_quality() != preset and field.set_quality(preset):
				changed += 1
		elif n is UnderwaterRig:
			var rig := n as UnderwaterRig
			if rig.get_quality() != UnderwaterRig.tier_for_preset(preset) and rig.set_quality(preset):
				changed += 1
		elif n is WaterSphereRig:  # M3-ARC-1324: the Reefball ball and the Tamsule Bell's held drop
			var sphere := n as WaterSphereRig
			if sphere.get_quality() != preset and sphere.set_quality(preset):
				changed += 1
		elif n is SmokeColumn:  # M3-ARC-1324: the Ch6 camp's smoke (its march steps per preset)
			var smoke := n as SmokeColumn
			if smoke.get_quality() != preset and smoke.set_quality(preset):
				changed += 1
	return changed + CharacterShaderTiers.apply_to_tree(root, CharacterShaderTiers.tier_for_preset(preset))


## Global operations (Viewport, RenderingServer) or per-scene ones (Environment, sky, groups).
static func _ops_for(ops: Array[Dictionary], global: bool) -> Array[Dictionary]:
	var out: Array[Dictionary] = []
	for op in ops:
		var target: StringName = op["target"]
		var is_global := target == GraphicsSettings.TARGET_VIEWPORT or target == GraphicsSettings.TARGET_SERVER
		if is_global == global:
			out.append(op)
	return out
