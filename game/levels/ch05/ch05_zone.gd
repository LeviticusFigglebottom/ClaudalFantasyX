class_name Ch05Zone
extends Ch01Zone
## A Ch5 greybox zone root (M3-C05-02; act1_ch05.md; docs/kb/tech/chapter_flow.md "Ch5"). Ch01Zone's
## story calls (rest, give, prompt, hide_block, show_block) plus what Ch5 adds, each reached with a
## ZoneStory `zone` step:
##   give_if(flag, items, lume)  give() only while `flag` is set: B04's "Not yet" keeps the leaf-boat.
##   place_actor(id, mark)       cuts a stage actor onto a mark and shows it.
##   apply_variant()             re-reads the layout's "variants" (below); the step after a flag a
##                               variant reads is set (Kerrid joining, the day after the binding).
## The layout's "variants" is a list of {when, sun?, environment?, environment_res?, hide?: [ids], show?: [ids]} (block
## or stage actor ids; `when` as ZoneStory's). Every row whose `when` holds applies, in order, over
## the layout's own light, so a later row wins: Pemakar's festival night is the layout, the day after
## the binding is a variant. A zone entered with the flags already set (a return from a battle, a
## load) comes up in its variant at once.

const KEY_VARIANTS := "variants"
const KEY_ENVIRONMENT_RES := "environment_res"
const KEY_HOLD_FIELD := "hold"

## Act III (M5-A3P-1001): a no-fail held input for this zone's scenes, as Ch9's Ebbing has (CutsceneHoldGate). Between
## <<event hold_input <id>>> and <<event hold_input_end>> a scene's time runs only while the player holds the field's
## interact action. The file's "hold" block names the action and maps each prompt id to its loc key
## (game/data/flow/act3_field.json). Empty: no gate.
@export_file("*.json") var hold_field_path: String = ""
## The held input, when hold_field_path is set.
var field_hold_gate: CutsceneHoldGate

var _base_environment: Environment
var _environment_res := ""


## Kit collision (ADR 0200): the layout's "collision_path" and "ramps" (KitCollision).
func _build_blocks() -> void:
	KitCollision.merge(self)
	super()
	KitCollision.build_ramps(self)


func _ready() -> void:
	super()
	apply_variant()
	if hold_field_path != "":
		field_hold_gate = CutsceneHoldGate.new()
		field_hold_gate.name = "HoldGate"
		add_child(field_hold_gate)
		field_hold_gate.setup(story.sequencer, read_json(hold_field_path).get(KEY_HOLD_FIELD, {}))


## Gives `items` and `lume` (Ch01Zone.give) only when `flag` is set. Returns true when it gave.
func give_if(flag: String, items: Dictionary, lume: int = 0) -> bool:
	if not bool(Game.get_flag(StringName(flag))):
		return false
	give(items, lume)
	return true


## Puts stage actor `id` on mark `mark` at once and shows it (a cut, not a walk: Kerrid standing at
## the inn gate when the party comes back down in B11). Returns false when either is missing.
func place_actor(id: String, mark: String) -> bool:
	var a := stage.actor(StringName(id))
	var m := stage.mark(StringName(mark))
	if a == null or m == null or a is FieldController:
		push_warning("Ch05Zone %s: cannot place actor '%s' on mark '%s'" % [location_id, id, mark])
		return false
	a.position = m.position
	a.rotation = m.rotation
	a.visible = true
	return true


## A copy of `res` on the zone's WorldEnvironment, or its base one back for "" (ADR 0200: a kit's grade for a
## variant, Ch9's dawn after the night); nothing when it is already up.
func _swap_environment(res: String) -> void:
	var we := get_node(^"WorldEnvironment") as WorldEnvironment
	if _base_environment == null:
		_base_environment = we.environment
	if res == _environment_res:
		return
	_environment_res = res
	var env := load(res) as Environment if res != "" else null
	we.environment = env.duplicate() if env != null else _base_environment


## Applies every "variants" row whose `when` holds (see the class comment).
func apply_variant() -> void:
	var sun_row: Dictionary = _merged("sun")
	var env_row: Dictionary = _merged("environment")
	var rows: Array = []
	for r: Variant in layout.get(KEY_VARIANTS, []):
		if ZoneStory.holds((r as Dictionary).get("when", {})):
			rows.append(r)
	var res := ""
	for r: Dictionary in rows:
		sun_row.merge(r.get("sun", {}), true)
		env_row.merge(r.get("environment", {}), true)
		res = str(r.get(KEY_ENVIRONMENT_RES, res))
	_swap_environment(res)
	sun.light_energy = float(sun_row.get("energy", 1.0))
	sun.light_color = Color.html(str(sun_row.get("color", "#ffffff")))
	sun.rotation_degrees = Vector3(float(sun_row.get("pitch_deg", 0.0)), float(sun_row.get("yaw_deg", 0.0)), 0.0)
	var env := (get_node(^"WorldEnvironment") as WorldEnvironment).environment
	env.background_color = Color.html(str(env_row.get("background", "#000000")))
	env.ambient_light_color = Color.html(str(env_row.get("ambient_color", "#ffffff")))
	env.ambient_light_energy = float(env_row.get("ambient_energy", 1.0))
	for r: Dictionary in rows:
		for id: Variant in r.get("hide", []):
			_set_block(str(id), false)
		for id: Variant in r.get("show", []):
			_set_block(str(id), true)
