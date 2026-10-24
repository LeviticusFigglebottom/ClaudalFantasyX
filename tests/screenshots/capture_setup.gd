class_name CaptureSetup
extends RefCounted
## A shot's "setup" block from tests/screenshots/shots.json (M1-QA-04). It lets the manifest pin what
## a scene would otherwise have to detect the capture to pin (camera checks, CAPTURE_SCENE tests).
##   "globals":    {name: value}  global shader parameters (hymn_wind_time, ...), written and restored
##                                 through ShaderGlobals (M1-ENV-11).
##   "nodes":      {path: {property: value}}  properties of nodes under the shot's scene root
##                 ("." is the root itself).
##   "viewport":   {property: value}  properties of the capture viewport, e.g. use_taa, screen_space_aa.
##   "time_scale": float  Engine.time_scale for the shot. 0.0 is a fixed time: delta-driven animation
##                 (AnimationPlayer, Tween, particles, `delta` in _process) and the shader TIME built-in
##                 stop at their first-frame values. Frame-counting rigs keep counting.
## Globals, nodes and viewport are written before the first settle frame AND re-applied every frame,
## twice: after the scene's own _process (ScreenshotCapture.HOLD_PRIORITY), and again on
## RenderingServer.frame_pre_draw, which comes after the SceneTree's Tweens, timers, physics and
## every AnimationPlayer callback mode (M1-QA-06). A rig, Tween or animation that writes the same
## value each frame therefore cannot override them. A held Node3D (and its subtree) has its pending
## transform notifications flushed at that point, so a held transform is drawn the same frame.
## Everything is restored when the shot ends. Globals go back to their project.godot default, NOT
## to the value the previous scene left: the engine cannot read a global's live value outside the
## editor. So a capture scene must never rely on a global inherited from an earlier shot (set what it
## needs in _ready, or name it in setup.globals): which shots a HYMN_SHOTS subset runs before it
## would otherwise change its frame.
## JSON values are converted to the target's current type: numbers to int/float/bool, [x, y(, z, w)]
## to Vector2/3/4(i), Quaternion or Color, "#rrggbb" to Color, "res://..." to a loaded Resource.
## Other types (Transform3D, Basis, Rect2, Plane, AABB...) are not converted, so a value for one fails
## the shot's type check; Array and Dictionary properties take the JSON value as it is.
## An unknown key, node, property or global fails the shot (a typo must never pass silently).

const KEYS: PackedStringArray = ["globals", "nodes", "viewport", "time_scale"]
const GLOBALS_SECTION := "shader_globals/"

var _spec: Dictionary = {}
var _root: Node = null
var _viewport: Viewport = null
var _saved_props: Array[Array] = []  # [object, property, value]
var _saved_globals: Dictionary = {}
var _saved_time_scale: float = 1.0
var _began: bool = false
var _not_an_object: bool = false


## `spec` is the shot's "setup" value as parsed from JSON (anything but an object fails validate()).
func _init(spec: Variant = {}) -> void:
	if spec is Dictionary:
		_spec = spec
	else:
		_not_an_object = true


func is_empty() -> bool:
	return _spec.is_empty() and not _not_an_object


## Checks the shape of the block (no scene needed). Returns "" or an error.
func validate() -> String:
	var problems: PackedStringArray = []
	if _not_an_object:
		problems.append("setup must be an object")
	for k: Variant in _spec.keys():
		if not KEYS.has(String(k)):
			problems.append("setup: unknown key '%s' (known: %s)" % [k, ", ".join(KEYS)])
	for k in ["globals", "nodes", "viewport"]:
		if _spec.has(k) and not _spec[k] is Dictionary:
			problems.append("setup.%s must be an object" % k)
	var nodes: Variant = _spec.get("nodes", {})
	if nodes is Dictionary:
		for path: Variant in (nodes as Dictionary).keys():
			if not nodes[path] is Dictionary:
				problems.append("setup.nodes['%s'] must be an object of properties" % path)
	if _spec.has("time_scale"):
		var ts: Variant = _spec["time_scale"]
		if not (ts is float or ts is int) or float(ts) < 0.0:
			problems.append("setup.time_scale must be a number >= 0")
	return problems[0] if not problems.is_empty() else ""


## Before the scene is instanced: validates, then sets the time scale, viewport properties and
## globals. Returns "" or an error (call end() either way).
func begin(viewport: Viewport) -> String:
	var invalid := validate()
	if invalid != "":
		return invalid
	_viewport = viewport
	_began = true
	if not is_empty() and not RenderingServer.frame_pre_draw.is_connected(pre_draw):
		RenderingServer.frame_pre_draw.connect(pre_draw)
	_saved_time_scale = Engine.time_scale
	if _spec.has("time_scale"):
		Engine.time_scale = float(_spec["time_scale"])
	for prop: Variant in (_spec.get("viewport", {}) as Dictionary).keys():
		var err := _set_prop(viewport, String(prop), _spec["viewport"][prop], "viewport")
		if err != "":
			return err
	return _apply_globals(true)


## After the scene's _ready: node properties, then globals again (a rig's _ready may have written them).
func attach(root: Node) -> String:
	_root = root
	var nodes: Dictionary = _spec.get("nodes", {})
	for path: Variant in nodes.keys():
		var node := root.get_node_or_null(NodePath(String(path)))
		if node == null:
			return "setup.nodes: no node '%s' under %s" % [path, root.name]
		var props: Dictionary = nodes[path]
		for prop: Variant in props.keys():
			var err := _set_prop(node, String(prop), props[prop], "nodes['%s']" % path)
			if err != "":
				return err
	return _apply_globals(false)


## Every frame, after the scene's own _process: write the held values again.
func hold() -> void:
	if _viewport != null:
		var vp_props: Dictionary = _spec.get("viewport", {})
		for prop: Variant in vp_props.keys():
			_viewport.set(String(prop), coerce(_viewport.get(String(prop)), vp_props[prop]))
	if _root != null and is_instance_valid(_root):
		var nodes: Dictionary = _spec.get("nodes", {})
		for path: Variant in nodes.keys():
			var node := _root.get_node_or_null(NodePath(String(path)))
			if node == null:
				continue
			var props: Dictionary = nodes[path]
			for prop: Variant in props.keys():
				node.set(String(prop), coerce(node.get(String(prop)), props[prop]))
	var globals: Dictionary = _spec.get("globals", {})
	for g: Variant in globals.keys():
		var name := StringName(String(g))
		ShaderGlobals.set_value(name, coerce(_saved_globals.get(name), globals[g]))


## Just before each frame is drawn (RenderingServer.frame_pre_draw), after Tweens and animation: the
## hold again, then the held Node3D subtrees' transform notifications, which the SceneTree would
## otherwise only flush next frame (after that frame's Tweens wrote over them again).
func pre_draw() -> void:
	hold()
	if _root == null or not is_instance_valid(_root) or not _root.is_inside_tree():
		return
	for path: Variant in (_spec.get("nodes", {}) as Dictionary).keys():
		var node := _root.get_node_or_null(NodePath(String(path)))
		if node != null:
			_flush_transforms(node)


static func _flush_transforms(node: Node) -> void:
	if node is Node3D and (node as Node3D).is_inside_tree():
		(node as Node3D).force_update_transform()
	for child in node.get_children():
		_flush_transforms(child)


## When the shot ends: restore everything this setup changed (viewport, globals, time scale).
func end() -> void:
	if RenderingServer.frame_pre_draw.is_connected(pre_draw):
		RenderingServer.frame_pre_draw.disconnect(pre_draw)
	for i in range(_saved_props.size() - 1, -1, -1):
		var entry: Array = _saved_props[i]
		var obj: Object = entry[0]
		if is_instance_valid(obj):
			obj.set(String(entry[1]), entry[2])
	_saved_props.clear()
	# Through ShaderGlobals (M1-ENV-11): its listeners (AUTO plant shelter on hymn_sun_direction) see
	# the shot's value and the restore, and no stale copy outlives the shot. The saved value is the
	# project.godot default, which is what reset() writes.
	for name: Variant in _saved_globals.keys():
		ShaderGlobals.reset(name as StringName)
	_saved_globals.clear()
	if _began:
		Engine.time_scale = _saved_time_scale
	_root = null
	_viewport = null
	_began = false


## Converts a JSON value to the type of `current` (the target's present value). Unknown types pass through.
static func coerce(current: Variant, value: Variant) -> Variant:
	var nums: Array = value if value is Array else []
	match typeof(current):
		TYPE_BOOL:
			return bool(value)
		TYPE_INT:
			return int(value)
		TYPE_FLOAT:
			return float(value)
		TYPE_STRING:
			return String(value)
		TYPE_STRING_NAME:
			return StringName(String(value))
		TYPE_NODE_PATH:
			return NodePath(String(value))
		TYPE_VECTOR2 when nums.size() == 2:
			return Vector2(nums[0], nums[1])
		TYPE_VECTOR2I when nums.size() == 2:
			return Vector2i(int(nums[0]), int(nums[1]))
		TYPE_VECTOR3 when nums.size() == 3:
			return Vector3(nums[0], nums[1], nums[2])
		TYPE_VECTOR3I when nums.size() == 3:
			return Vector3i(int(nums[0]), int(nums[1]), int(nums[2]))
		TYPE_VECTOR4 when nums.size() == 4:
			return Vector4(nums[0], nums[1], nums[2], nums[3])
		TYPE_QUATERNION when nums.size() == 4:
			return Quaternion(nums[0], nums[1], nums[2], nums[3])
		TYPE_COLOR:
			if value is String:
				return Color(String(value))
			if nums.size() == 3:
				return Color(nums[0], nums[1], nums[2])
			if nums.size() == 4:
				return Color(nums[0], nums[1], nums[2], nums[3])
	if (current == null or current is Object) and value is String and String(value).begins_with("res://"):
		return load(String(value))
	return value


func _set_prop(obj: Object, prop: String, value: Variant, where: String) -> String:
	if not _has_property(obj, prop):
		return "setup.%s: %s has no property '%s'" % [where, obj.get_class(), prop]
	var before: Variant = obj.get(prop)
	var v: Variant = coerce(before, value)
	if before != null and typeof(v) != typeof(before) and not before is Object:
		return "setup.%s.%s: cannot use %s for a %s" % [where, prop, JSON.stringify(value), type_string(typeof(before))]
	_saved_props.append([obj, prop, before])
	obj.set(prop, v)
	return ""


func _apply_globals(first: bool) -> String:
	var globals: Dictionary = _spec.get("globals", {})
	for g: Variant in globals.keys():
		var name := StringName(String(g))
		if first:
			# RenderingServer refuses to read globals outside the editor, so the declaration in
			# project.godot [shader_globals] gives the type, and its default is what end() restores.
			var decl: Variant = ProjectSettings.get_setting(GLOBALS_SECTION + String(name))
			if not decl is Dictionary or not (decl as Dictionary).has("value"):
				return "setup.globals: no global shader parameter '%s' in project.godot" % name
			_saved_globals[name] = (decl as Dictionary)["value"]
			var v: Variant = coerce(_saved_globals[name], globals[g])
			if typeof(v) != typeof(_saved_globals[name]):
				return "setup.globals.%s: cannot use %s for a %s" % [name, JSON.stringify(globals[g]), decl["type"]]
		ShaderGlobals.set_value(name, coerce(_saved_globals[name], globals[g]))
	return ""


static func _has_property(obj: Object, prop: String) -> bool:
	for p: Dictionary in obj.get_property_list():
		if String(p["name"]) == prop:
			return true
	return false
