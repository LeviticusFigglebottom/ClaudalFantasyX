class_name BattleVowboundHud
extends RefCounted
## The Vowbound on the battle scene (M2-UI-05; rules in battle_ctb.md § Vowbound, ADR 0027). Glue,
## like BattleBossHud: it gives the engine its Vowbound before begin(), turns the menu rows into
## engine calls, and shows what the engine's `called` and `departed` signals change. It never
## writes combat state itself.
##   - attach(): engine.vowbound from the story (each vowbound.json row's bound_flag, read with
##     Game.get_flag; the engine never reads Game) in a live battle, from the fixture in a capture
##     or test, and with nothing bound in any other battle (the caller sees "Call · None bound").
##   - The caller's Call row (BattleMenus.call_rows) previews the order with the Vowbound in it
##     and says what the call costs: the caller's call_rank delay once the party returns (pillar 4).
##   - The Vowbound's own root page (BattleMenus.vowbound_root_rows): its finisher through
##     perform() (BattleVowbound.unleash), and Dismiss, which previews the order with the party
##     back (BattleVowbound.preview_dismiss).
##   - called / departed: the stage re-seats (the party steps off and the Vowbound stands on
##     vowbound_slot, then the reverse), the party panel shows the Vowbound alone with its HP, MP
##     and Swell gauge and a note naming who stood down, and a departure leads the next command
##     menu's help line ("Ilun has fallen ...").
## The controller reaches it through one-line hooks (it is at its line cap). Hold the instance
## for the whole battle: a signal connection does not keep it alive.

const DEFAULT_TINT := "#A9B8CC"

var ctl: BattleController
## The line the next command menu leads with once the party is back ("" when none).
var pending_note := ""
var _engine: BattleEngine


func _init(controller: BattleController) -> void:
	ctl = controller


## A view of `engine` for `controller`, already attached. Call after setup() and before begin().
static func attached(controller: BattleController, engine: BattleEngine) -> BattleVowboundHud:
	var view := BattleVowboundHud.new(controller)
	view.attach(engine)
	return view


## The ids of `rows` (vowbound.json rows) whose bound_flag is set and whose released_flag (M5-A3P-1705; act3_ch20
## U01-U06: released for good, it leaves the menu) is not. `is_set`: (flag) -> bool.
static func bound_ids(rows: Array, is_set: Callable) -> Array[StringName]:
	var out: Array[StringName] = []
	for row: Variant in rows:
		var d: Dictionary = row
		var flag := StringName(str(d.get("bound_flag", "")))
		var gone := StringName(str(d.get("released_flag", "")))
		if flag != &"" and bool(is_set.call(flag)) and (gone == &"" or not bool(is_set.call(gone))):
			out.append(StringName(str(d.get("id", ""))))
	return out


## bound_ids() read from the live game (Game.get_flag; validate_data checks every bound_flag is
## declared).
static func live_bound(rows: Array) -> Array[StringName]:
	return bound_ids(rows, func(f: StringName) -> bool: return Game.get_flag(f) == true)


## Builds engine.vowbound for this battle and connects to it.
func attach(engine: BattleEngine) -> void:
	_engine = engine
	pending_note = ""
	var rows: Array = []
	var known: Array[StringName] = []
	if ctl.fixture != null:
		rows = ctl.fixture.vowbound_rows
		known = ctl.fixture.vowbound
	else:
		rows = BattleVowbound.load_config()
		if ctl.persist_progress:
			known = live_bound(rows)
	engine.vowbound = BattleVowbound.new(rows, known)
	engine.vowbound.called.connect(_on_called)
	engine.vowbound.departed.connect(_on_departed)
	for vid: StringName in engine.vowbound.rows:
		ctl.hud.timeline.set_identity(vid, ctl.menus.vowbound_name(engine.vowbound, vid), _tint(vid))


# --- player actions (menus, tests and capture scripts) ---------------------------------------


## The current caller calls `vowbound_id`: the party stands down and the Vowbound takes the turn.
## A refusal costs nothing and the help line says why.
func call_vowbound(vowbound_id: StringName) -> bool:
	var caller := _engine.current
	if not _engine.summon(vowbound_id):
		ctl.hud.set_help(ctl.menus.fail_text(_engine.vowbound.refusal(_engine, vowbound_id), caller))
		return false
	ctl.after_action(caller.id)
	return true


## The Vowbound leaves on its own turn, which it spends; the party comes back.
func dismiss() -> bool:
	var s := _engine.vowbound.summon
	if s == null or not _engine.dismiss():
		ctl.hud.set_help(ctl.menus.fail_text(_engine.vowbound.dismiss_refusal(_engine), _engine.current))
		return false
	ctl.after_action(s.id)
	return true


## BattleController.act's engine call: the Vowbound's finisher is unleashed (it is no learned
## skill, so engine.perform() would refuse it); every other skill is engine.perform().
func perform(skill_id: StringName, targets: Array[BattleCombatant]) -> ActionResult:
	var vb := _engine.vowbound
	if vb.is_out() and _engine.current == vb.summon and skill_id == vb.finisher(vb.summon):
		return vb.unleash(_engine, targets)
	return _engine.perform(skill_id, targets)


# --- menu hooks ----------------------------------------------------------------------------


## A highlighted root row: a Call row or Dismiss previews the order as it will stand after it
## (the whole order, as the swap preview does) and says what it costs. True when it did.
func highlight(row: Dictionary) -> bool:
	if ctl.state != BattleController.STATE_COMMAND:
		return false
	var vid := StringName(str(row.get(BattleMenus.KEY_VOWBOUND, "")))
	if vid != &"":
		_show_order(_engine.vowbound.preview_call(_engine, vid))
		ctl.hud.set_help(ctl.menus.call_help(_engine, vid))
		return true
	if StringName(str(row.get("id", ""))) == BattleMenus.ROW_DISMISS:
		var after := _engine.vowbound.preview_dismiss(_engine)
		_show_order(after)
		ctl.hud.set_help(ctl.menus.dismiss_help(_engine, after))
		return true
	return false


## A chosen root row the controller does not handle: Call, Dismiss, or the finisher, which goes
## on to `begin_target` (the controller's target pick) with its skill id.
func choose(row: Dictionary, begin_target: Callable) -> void:
	var rid := StringName(str(row.get("id", "")))
	var vid := StringName(str(row.get(BattleMenus.KEY_VOWBOUND, "")))
	if vid != &"":
		call_vowbound(vid)
	elif rid == BattleMenus.ROW_DISMISS:
		dismiss()
	elif rid == BattleMenus.ROW_UNLEASH:
		begin_target.call(ctl.menus.root_skill(_engine, rid))


## Puts the pending departure note on the help line (once). True if it did.
func show_note() -> bool:
	if pending_note == "":
		return false
	ctl.hud.set_help(pending_note)
	pending_note = ""
	return true


# --- what the engine changed ---------------------------------------------------------------


func _on_called(_vowbound: BattleCombatant) -> void:
	pending_note = ""
	_reseat()


func _on_departed(vowbound: BattleCombatant, fell: bool) -> void:
	_reseat()
	pending_note = ctl.menus.departed_text(vowbound, fell)


## The stage and the party panel follow who stands on the field now.
func _reseat() -> void:
	ctl.stage.sync_party(_engine)
	ctl.stage.refresh_ko(_engine)
	var labels: Dictionary = {}
	var tints: Dictionary = {}
	var gauges: Array[StringName] = []
	for c in _engine.party_active:
		labels[c.id] = ctl.menus.display_name(c)
		tints[c.id] = _tint(c.id)
		if c == _engine.vowbound.summon:
			gauges.append(c.id)
	ctl.hud.party.show_members(_engine.party_active, labels, tints, gauges)
	ctl.hud.party.set_current(ctl.current_actor_id())
	if _engine.vowbound.is_out():
		ctl.hud.party.set_note(ctl.menus.stood_down_text(_engine))


func _show_order(after: Array[TurnEntry]) -> void:
	var tl := ctl.hud.timeline
	tl.caption = ctl.menus.turn_caption(&"")
	var color := ctl.hud.get_theme_color(&"focus", HymnThemeBuilder.PALETTE_TYPE)
	if after.is_empty():
		tl.show_turns(ctl.current_actor_id(), _engine.preview(), [], [], color, TurnTimeline.MODE_PREVIEW)
		return
	tl.show_turns(ctl.current_actor_id(), _engine.preview(), after, [], color, TurnTimeline.MODE_PREVIEW, true)


static func _tint(cid: StringName) -> Color:
	return Color.html(str(BattleStage.stand_in_spec(cid).get("tint", DEFAULT_TINT)))
