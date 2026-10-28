class_name BattleBossIntro
extends Node
## A boss's intro at the battle's first turn (M3-BPR-02; docs/kb/tech/battle_presentation.md, Boss intros).
## - **When.** BattleChoreo.attached builds it (no controller line). For an encounter with a row in choreo.json
##   boss_intro.rows it waits for the engine's first turn_started, then for the screen to be uncovered (the router's
##   fade) and the opening banner to finish (at most reveal_wait_max_sec), and plays once. Fight again (a retry
##   rebuilds the engine on the same controller) plays it again only when the row says on_retry. Instant pacing
##   and "skip animations" play none; force_play plays it anyway (its freeze-frame capture).
## - **What.** The camera eases from the default to the row's shot, framed on the boss (camera.shots; a shot that
##   would put the boss outside the safe frame keeps the default), holds while a title card (the boss's name over
##   an epithet, the UI theme, centre-low and clear of the timeline) fades in and out, then eases home. Reduced
##   motion keeps the camera on the default and the card only fades. Nothing flashes.
## - **The first turn waits.** While it waits or plays, BattleHud.holds_battle() is true (BattleHud.holds), so the
##   controller holds its first wait (an enemy's think time); a party turn's command menu stays hidden and input
##   is taken here. Confirm or cancel skips it: the card goes, the camera is home, the turn goes on.
## Presentation only: it writes nothing but the camera, its card and a meta on the controller.

const KEY := "boss_intro"
const NODE_NAME := "BattleBossIntro"
const HOLD := &"boss_intro"
## The controller's meta: the encounter whose intro last played (a retry of it skips the intro).
const META_PLAYED := &"hymn_boss_intro_played"
const ROUTER_PATH := ^"SceneRouter"
const BANNER_NAME := ^"OpeningBanner"
const HELP_LINE := ^"%HelpLine"
const THEME_PATH := "res://game/ui/theme/hymn_theme.tres"
## Announced on EventBus.dialogue_event as the intro starts ([encounter id, title_key]) so audio can play a sting.
const AUDIO_EVENT := &"boss_intro"
## shot_id when the intro plays its hero shot (BattleBossHeroShot, choreo.json boss_intro.hero; M3-BPR-423).
const HERO_SHOT := "hero"
## The boss model's clip played through its intro (M3-CRB-009; the clip name is the contract).
const INTRO_CLIP := &"intro"
const IDLE := 0
const WAITING := 1
const PLAYING := 2
const DONE := 3

## choreo.json "boss_intro".
var cfg: Dictionary = {}
## This encounter's row ({} for none).
var row: Dictionary = {}
## The boss the camera frames (&"" until it plays).
var boss_id: StringName = &""
## The shot framing it ("" when the camera keeps the default).
var shot_id := ""
## Seconds into it, at the battle speed.
var elapsed := 0.0
## Plays even at instant pacing, with skip animations or on a retry (its freeze-frame capture).
var force_play := false
## False holds its clock (captures); advance() still moves it.
var live := true
## Whether the screen is still covered by a transition: () -> bool. Unset = SceneRouter.is_busy(). Tests set it.
var screen_covered: Callable = Callable()

var _state := IDLE
var _wait_sec := 0.0
var _choreo: BattleChoreo
var _ctl: BattleController
var _engine: BattleEngine
var _pose: Dictionary = {}
var _menu_held := false
var _layer: CanvasLayer
var _card: Control
var _title: Label
var _epithet: Label


static func attached(choreo: BattleChoreo, controller: BattleController, engine: BattleEngine) -> BattleBossIntro:
	var s := BattleBossIntro.new()
	s.name = NODE_NAME
	s.cfg = choreo.data.get(KEY, {}) as Dictionary
	s.row = row_for(s.cfg, engine.encounter_id, BattleIds.of(engine.enemies))
	s._choreo = choreo
	s._ctl = controller
	s._engine = engine
	choreo.add_child(s)
	if controller.hud != null:
		controller.hud.holds[HOLD] = s.holding  # replaces a retried battle's
	if not s.row.is_empty():
		engine.turn_started.connect(s._on_first_turn, CONNECT_ONE_SHOT)
	return s


## The encounter's intro row: its own (rows), else the first foe's by enemy id (by_enemy: a boss whose encounters
## are not written yet, the Act II bosses, gets its intro wherever it appears; M3-BPR-408). {} for none.
static func row_for(cfg: Dictionary, encounter: StringName, enemy_ids: Array[StringName]) -> Dictionary:
	var own := (cfg.get("rows", {}) as Dictionary).get(String(encounter), {}) as Dictionary
	if not own.is_empty():
		return own
	var by := cfg.get("by_enemy", {}) as Dictionary
	for eid in enemy_ids:
		var base := String(eid).get_slice("#", 0)
		if by.has(base):
			var r := (by[base] as Dictionary).duplicate()
			r["enemy"] = base
			return r
	return {}


## The intro under `stage`'s sequencer (null when none).
static func of(stage: BattleStage) -> BattleBossIntro:
	if stage == null or stage.choreo == null:
		return null
	return stage.choreo.get_node_or_null(NodePath(NODE_NAME)) as BattleBossIntro


## True when this battle should play its intro now.
func wants_play() -> bool:
	if row.is_empty():
		return false
	if force_play:
		return true
	if not _choreo.animating():
		return false
	var retry := str(_ctl.get_meta(META_PLAYED, "")) == String(_engine.encounter_id)
	return not retry or bool(row.get("on_retry", false))


## True while it waits for the screen or plays: the battle holds (BattleHud.holds_battle).
func holding() -> bool:
	return _state == WAITING or _state == PLAYING


func playing() -> bool:
	return _state == PLAYING


## True once it has played (or been skipped) this battle.
func done() -> bool:
	return _state == DONE


func _on_first_turn(_actor: BattleCombatant) -> void:
	if not wants_play():
		return
	_ctl.set_meta(META_PLAYED, String(_engine.encounter_id))
	_state = WAITING
	_wait_sec = 0.0
	_hold_menu()
	advance(0.0)


## Starts it now, without waiting for the screen (captures and tests).
func play() -> void:
	_ctl.set_meta(META_PLAYED, String(_engine.encounter_id))
	_begin()


## The whole intro: the camera in, the hold, the camera home.
func total_sec() -> float:
	return (
		float(cfg.get("camera_in_sec", 0.0)) + float(row.get("hold_sec", 0.0)) + float(cfg.get("camera_out_sec", 0.0))
	)


## Seconds of it left at the battle speed (0 when it does not play).
func remaining_sec() -> float:
	return maxf(total_sec() - elapsed, 0.0) / _choreo.speed if playing() else 0.0


func _process(delta: float) -> void:
	if live and holding():
		advance(delta)


func advance(delta: float) -> void:
	if _state == WAITING:
		_wait_sec += delta
		if not _screen_busy() or _wait_sec >= float(cfg.get("reveal_wait_max_sec", 0.0)):
			_begin()
		return
	if _state != PLAYING:
		return
	elapsed += delta * _choreo.speed
	_hold_menu()
	_camera_at(elapsed)
	_card_at(elapsed)
	if elapsed >= total_sec():
		_end()


## While it holds, every input is its own: confirm or cancel skips it, the rest is dropped (the menu is hidden).
func _input(event: InputEvent) -> void:
	if not holding():
		return
	if event.is_action_pressed(&"ui_accept") or event.is_action_pressed(&"ui_cancel"):
		skip()
	get_viewport().set_input_as_handled()


## Ends it now: the card goes, the camera is home, the first turn goes on.
func skip() -> void:
	if holding():
		_end()


func _begin() -> void:
	_state = PLAYING
	elapsed = 0.0
	_hold_menu()
	_frame_boss()
	_play_intro_clip()
	_build_card()
	var bus := get_node_or_null(^"/root/EventBus")
	if bus != null:
		bus.emit_signal(&"dialogue_event", AUDIO_EVENT, [_engine.encounter_id, str(row.get("title_key", ""))])
	advance(0.0)


## M3-CRB-009: the boss model's own `intro` clip, its display while the camera holds on it (none: it idles).
func _play_intro_clip() -> void:
	var f := _ctl.stage.stand_in(boss_id) if boss_id != &"" else null
	var actor := f.creature() if f != null else null
	if actor != null and actor.has_clip(INTRO_CLIP):
		actor.play_clip(INTRO_CLIP)


func _end() -> void:
	_state = DONE
	if _choreo.camera != null:
		_choreo.camera.rest()
	if _layer != null and is_instance_valid(_layer):
		_layer.queue_free()
	_layer = null
	_card = null
	if _menu_held:
		for item in _turn_ui():
			item.modulate.a = 1.0
	_menu_held = false


## A party first turn opens its command menu, help line and actor marker at once: they stay hidden (modulate, so
## the controller's own visibility is untouched) until the intro ends. The timeline and party panel stay.
func _hold_menu() -> void:
	for item in _turn_ui():
		item.modulate.a = 0.0
	_menu_held = true


func _turn_ui() -> Array[CanvasItem]:
	var out: Array[CanvasItem] = []
	if _ctl.hud == null or not is_instance_valid(_ctl.hud):
		return out
	for item: CanvasItem in [_ctl.hud.commands, _ctl.hud.target_cursor, _ctl.hud.get_node_or_null(HELP_LINE)]:
		if item != null:
			out.append(item)
	return out


## True while a transition covers the screen or the opening banner shows: the intro waits its turn.
func _screen_busy() -> bool:
	if _ctl.hud != null:
		var banner := _ctl.hud.get_node_or_null(BANNER_NAME) as OpeningBanner
		if banner != null and (banner.is_showing() or banner.is_pending()):
			return true
	if screen_covered.is_valid():
		return bool(screen_covered.call())
	if not is_inside_tree():
		return false
	var router := get_tree().root.get_node_or_null(ROUTER_PATH)
	return router != null and bool(router.call(&"is_busy"))


# --- the camera ------------------------------------------------------------------------------


## The boss's hero shot (M3-BPR-423), else the row's shot fitted to it and checked against the safe frame (its feet
## and head); {} keeps the default. A row's hero false (or fit false) skips the hero shot. `fallen_ok` frames a
## boss that has just fallen (BattleBossCamera's fall moment).
func _frame_boss(fallen_ok: bool = false) -> void:
	_pose = {}
	shot_id = ""
	boss_id = &""
	var base := str(row.get("enemy", ""))
	for e in _engine.enemies:
		if String(e.id).get_slice("#", 0) == base and (e.is_alive() or fallen_ok):  # M3-BPR-426: a fall's moment
			boss_id = e.id
			break
	var director := _choreo.camera
	var f := _ctl.stage.stand_in(boss_id) if boss_id != &"" else null
	if director == null or director.camera == null or f == null or f.get_parent() == null:
		return
	var slot := (f.get_parent() as Node3D).transform * _choreo.home_origin(boss_id)
	var head := director._parent_inverse() * f.head_position() if f.is_inside_tree() else slot
	var id := str(row.get("shot", ""))
	var pose := director.shot_pose(id, slot, slot, slot)
	var pts: Array[Vector3] = [slot, head]
	var bounds := _bounds(f)
	if row.get("hero", true) != false and row.get("fit", true) != false:  # M3-BPR-423: the boss's hero shot first
		var hero := BattleBossHeroShot.search(self, bounds, slot)
		if not hero.is_empty():
			_pose = hero
			shot_id = HERO_SHOT
			return
	var none: Array[Vector3] = []
	if not pose.is_empty() and bounds.size != Vector3.ZERO and row.get("fit", true) != false:
		var mid := bounds.get_center()  # M3-BPR-404: framed on the model's real size, inside the safe frame
		pts = [Vector3(mid.x, bounds.position.y, mid.z), Vector3(mid.x, bounds.end.y, mid.z)]
		pose = _fit_search(pose, bounds, pts)
	if pose.is_empty() or not director._frames(pose, pts, none):
		return
	_pose = pose
	shot_id = id


## The boss's visible meshes' bounds, in the camera's parent space (an empty AABB when it has none).
func _bounds(f: Node3D) -> AABB:
	var inv := _choreo.camera._parent_inverse()
	var out := AABB()
	var first := true
	for n in f.find_children("*", "VisualInstance3D", true, false):
		var vi := n as VisualInstance3D
		if not vi.is_visible_in_tree() or vi is Light3D or vi is GPUParticles3D:
			continue
		var box := (inv * vi.global_transform) * vi.get_aabb()
		out = box if first else out.merge(box)
		first = false
	return out


## True when `feet` (camera parent space) projects above the title card's top edge, less fit.card_clear_px (the
## card is under the boss, M3-BPR-404: a small boss framed close sank behind it).
func _clears_card(pose: Dictionary, feet: Vector3) -> bool:
	var rect := (cfg.get("card", {}) as Dictionary).get("rect", []) as Array
	if rect.size() < 2:
		return true
	var ref_h := float(ProjectSettings.get_setting("display/window/size/viewport_height", 1))
	var clear := float((cfg.get("fit", {}) as Dictionary).get("card_clear_px", 0.0))
	var bottom := clampf(1.0 - (float(rect[1]) - clear) / maxf(ref_h, 1.0), 0.0, 1.0)
	var pos: Vector3 = pose["pos"]
	var xform := Transform3D(Basis.looking_at((pose["look"] as Vector3) - pos, Vector3.UP), pos)
	return _choreo.camera.in_frame(xform, float(pose["fov"]), feet, {"bottom": bottom})


## The closest fitted pose whose bounds pass the safe frame with the feet clear of the card and no party member
## crowding it: for each orbit (fit.yaw_steps_deg about the boss, the shot's own first), each widening step (x
## fit.widen_step up to widen_max) tries aiming lower first (look_drop up by drop_step to drop_max, which lifts the
## boss). Failing the party everywhere, the first that clears the card; failing that, the closest that passes the
## safe frame; failing that, {}.
func _fit_search(shot: Dictionary, bounds: AABB, pts: Array[Vector3]) -> Dictionary:
	var fc := cfg.get("fit", {}) as Dictionary
	var none: Array[Vector3] = []
	var base := float(fc.get("look_drop", 0.0))
	var step := maxf(float(fc.get("drop_step", 1.0)), 0.01)
	var widen := maxf(float(fc.get("widen_step", 1.1)), 1.01)
	var fallback := {}
	var crowded := {}  # clears the card but a party member crowds the frame
	for yaw: Variant in fc.get("yaw_steps_deg", [0.0]):
		var turned := _orbit(shot, float(yaw))
		var k := 1.0
		while k <= float(fc.get("widen_max", 1.0)) + 0.0001:
			var drop := base
			while drop <= float(fc.get("drop_max", base)) + 0.0001:
				var pose := _fit(turned, bounds, k, drop)
				if _choreo.camera._frames(pose, pts, none):
					if _clears_card(pose, pts[0]):
						if _party_clear(pose):
							return pose
						if crowded.is_empty():
							crowded = pose
					if fallback.is_empty() and is_equal_approx(drop, base) and is_zero_approx(float(yaw)):
						fallback = pose
				drop += step
			k *= widen
	return crowded if not crowded.is_empty() else fallback


## `shot` turned `deg` about the vertical through its look point (the same distance and height).
static func _orbit(shot: Dictionary, deg: float) -> Dictionary:
	if is_zero_approx(deg):
		return shot
	var look := shot["look"] as Vector3
	var pos := look + ((shot["pos"] as Vector3) - look).rotated(Vector3.UP, deg_to_rad(deg))
	return {"pos": pos, "look": look, "fov": shot["fov"]}


## True when no party member crowds the intro (M3-BPR-404, the playtest's Toma over the timeline): each is either
## wholly off screen (or behind the camera), or wholly inside the HUD-safe frame and at most fit.party_max_h of the
## screen's height.
func _party_clear(pose: Dictionary) -> bool:
	var pos: Vector3 = pose["pos"]
	var xform := Transform3D(Basis.looking_at((pose["look"] as Vector3) - pos, Vector3.UP), pos)
	var inv := xform.affine_inverse()
	var half := tan(deg_to_rad(float(pose["fov"])) * 0.5)
	var aspect := _choreo.camera._aspect()
	var safe := _choreo.camera.data.get("safe_frame", {}) as Dictionary
	var max_h := float((cfg.get("fit", {}) as Dictionary).get("party_max_h", 1.0))
	for c in _engine.party_active:
		var f := _ctl.stage.stand_in(c.id)
		if f == null or not f.is_visible_in_tree():
			continue
		var b := _bounds(f)
		var on_screen := false
		var inside := true
		var lo := INF
		var hi := -INF
		for i in 8:
			var q := inv * b.get_endpoint(i)
			var depth := -q.z
			if depth <= 0.05:
				inside = false  # at or behind the camera: it fills the lens
				continue
			var x := q.x / (depth * half * aspect)
			var y := q.y / (depth * half)
			lo = minf(lo, y)
			hi = maxf(hi, y)
			if absf(x) <= 1.0 and absf(y) <= 1.0:
				on_screen = true
			var left := -1.0 + 2.0 * float(safe.get("left", 0.0))
			var right := 1.0 - 2.0 * float(safe.get("right", 0.0))
			var bottom := -1.0 + 2.0 * float(safe.get("bottom", 0.0))
			var top := 1.0 - 2.0 * float(safe.get("top", 0.0))
			if x < left or x > right or y < bottom or y > top:
				inside = false
		if on_screen and (not inside or (hi - lo) * 0.5 > max_h):
			return false
	return true


## `pose` moved along its own line of sight so the bounds' sphere fits the narrower field of view at `fit.margin`
## (the row's fit_margin overrides it), clamped, times `k`, aimed `drop` (fit.look_drop when negative) of its radius
## below the centre (the boss sits above the title card).
func _fit(pose: Dictionary, bounds: AABB, k: float, drop: float = -1.0) -> Dictionary:
	var fc := cfg.get("fit", {}) as Dictionary
	var margin := float(row.get("fit_margin", fc.get("margin", 1.0)))
	var r := bounds.size.length() * 0.5
	var half := deg_to_rad(float(pose["fov"])) * 0.5
	var aspect := _choreo.camera._aspect()
	var narrow := minf(half, atan(tan(half) * aspect)) if aspect >= 1.0 else atan(tan(half) * aspect)
	var look := bounds.get_center() - Vector3.UP * r * (drop if drop >= 0.0 else float(fc.get("look_drop", 0.0)))
	var dir := ((pose["pos"] as Vector3) - (pose["look"] as Vector3)).normalized()
	var dist := clampf(r * margin / sin(narrow), float(fc.get("min_m", 0.0)), float(fc.get("max_m", 1000.0)))
	dist *= k
	return {"pos": look + dir * dist, "look": look, "fov": pose["fov"]}


## Default -> the boss's shot over camera_in_sec, held, home over the last camera_out_sec. Reduced motion and skip
## animations keep the default.
func _camera_at(t: float) -> void:
	var director := _choreo.camera
	if director == null or director.camera == null or _pose.is_empty() or director.still():
		return
	var home := director._default_pose()
	var w_in := BattleCameraDirector._weight(t, 0.0, float(cfg.get("camera_in_sec", 0.0)))
	var out_sec := float(cfg.get("camera_out_sec", 0.0))
	var w_out := BattleCameraDirector._weight(t, total_sec() - out_sec, total_sec())
	var pose := BattleCameraDirector._mix(BattleCameraDirector._mix(home, _pose, w_in), home, w_out)
	var pos: Vector3 = pose["pos"]
	director.camera.transform = Transform3D(Basis.looking_at((pose["look"] as Vector3) - pos, Vector3.UP), pos)
	director.camera.fov = float(pose["fov"])


# --- the title card --------------------------------------------------------------------------


func _build_card() -> void:
	var c := cfg.get("card", {}) as Dictionary
	_layer = CanvasLayer.new()
	_layer.name = "BossIntroCard"
	_layer.layer = int(c.get("layer", 1))
	add_child(_layer)
	_card = Control.new()
	_card.name = "Card"
	_card.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_card.theme = _ctl.hud.theme if _ctl.hud != null and _ctl.hud.theme != null else load(THEME_PATH) as Theme
	HudLayout.place(_card, c)
	_layer.add_child(_card)
	var title_h := float(c.get("title_height", 0.0))
	var w := _card.size.x
	_title = _label(str(c.get("title_variation", "")), Rect2(0.0, 0.0, w, title_h))
	_epithet = _label(str(c.get("epithet_variation", "")), Rect2(0.0, title_h, w, _card.size.y - title_h))
	_title.text = tr(str(row.get("title_key", "")))
	_epithet.text = tr(str(row.get("epithet_key", "")))
	_card.draw.connect(_draw_card)
	_card.modulate.a = 0.0


## The card's alpha at time `t`: in over card_in_sec from card_at_sec, out over card_out_sec ending as the camera
## turns home (camera_in_sec + hold_sec). Eased both ways.
func card_alpha(t: float) -> float:
	var at := float(cfg.get("card_at_sec", 0.0))
	var out_end := float(cfg.get("camera_in_sec", 0.0)) + float(row.get("hold_sec", 0.0))
	var w_in := BattleCameraDirector._weight(t, at, at + float(cfg.get("card_in_sec", 0.0)))
	var w_out := BattleCameraDirector._weight(t, out_end - float(cfg.get("card_out_sec", 0.0)), out_end)
	return minf(w_in, 1.0 - w_out)


func _card_at(t: float) -> void:
	if _card == null:
		return
	var a := card_alpha(t)
	_card.modulate.a = a
	var rise := 0.0 if _choreo.reduced_motion else float(cfg.get("rise_px", 0.0))
	var at := float(cfg.get("card_at_sec", 0.0))
	var w_in := BattleCameraDirector._weight(t, at, at + float(cfg.get("card_in_sec", 0.0)))
	_card.position.y = HudLayout.rect_of(cfg.get("card", {}) as Dictionary).position.y + rise * (1.0 - w_in)


## The card shown now (null when none): tests and captures.
func card() -> Control:
	return _card


func title_text() -> String:
	return _title.text if _card != null else ""


func epithet_text() -> String:
	return _epithet.text if _card != null else ""


## A dark band fading out at both ends behind the words (contrast over a bright sky, art/ui.md §9), and one thin
## gold rule between the name and the epithet.
func _draw_card() -> void:
	var c := cfg.get("card", {}) as Dictionary
	var deep := _card.get_theme_color(&"panel_low", HymnThemeBuilder.PALETTE_TYPE)
	deep.a = float(c.get("band_alpha", 0.0))
	var clear := deep
	clear.a = 0.0
	var size := _card.size
	var fade := size.x * float(c.get("band_fade", 0.0))
	_card.draw_rect(Rect2(fade, 0.0, size.x - fade * 2.0, size.y), deep)
	for edge: Array in [[0.0, fade], [size.x, size.x - fade]]:
		var outer := float(edge[0])
		var inner := float(edge[1])
		var pts := PackedVector2Array(
			[Vector2(outer, 0.0), Vector2(inner, 0.0), Vector2(inner, size.y), Vector2(outer, size.y)]
		)
		_card.draw_polygon(pts, PackedColorArray([clear, deep, deep, clear]))
	var gold := _card.get_theme_color(&"focus_gold", HymnThemeBuilder.PALETTE_TYPE)
	var half := float(c.get("rule_length", 0.0)) * 0.5
	_card.draw_rect(
		Rect2(size.x * 0.5 - half, float(c.get("rule_y", 0.0)), half * 2.0, float(c.get("rule_px", 0.0))), gold
	)


func _label(variation: String, r: Rect2) -> Label:
	var l := Label.new()
	l.theme_type_variation = StringName(variation)
	l.position = r.position
	l.size = r.size
	l.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	l.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	l.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_card.add_child(l)
	return l
