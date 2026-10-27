extends TestCase
## M3-AUD-13: the battle choreography's sound layers (game/audio/choreo_audio.gd, choreo_sfx.json, sfx_choreo.json).
## Each rule is driven in isolation through a stand-in built at runtime: a Node with a GDScript compiled from
## STANDIN (no class_name) that declares BattleChoreo's signals and methods; ChoreoAudio.matcher names it
## "BattleChoreo" (the real BattleChoreo is driven in tests/integration/test_battle_audio_live.gd, M3-AUD-800).
## Every row exists and imports; the beats play footfalls, a whoosh cresting on the contact and the collapse; the
## contact plays the actor's weapon accent (never on a miss), the Swell, toll and surge rows; the Vowbound's call,
## rise, sink and fall and the party's walk-ins play as each move starts; the Flood braces once the action is done
## (choreo.json's stagger); reduced audio keeps one layer.

const ENCOUNTER := &"sandbox_reef"
const STANDIN := """extends Node
signal beat(kind: StringName, actor_id: StringName)
signal contact(result: ActionResult)
var speed := 1.0
var data: Dictionary = {}
var plan: Dictionary = {}
var styles: Dictionary = {}
var anim := true
var moves_in: Dictionary = {}
var moves_out: Dictionary = {}
var after: Array[Callable] = []
func current() -> Dictionary:
	return plan
func style_id_for(result: ActionResult) -> String:
	return str(styles.get(String(result.skill_id), "melee"))
func animating() -> bool:
	return anim
func entering(cid: StringName) -> Dictionary:
	return moves_in.get(cid, {})
func leaving(cid: StringName) -> Dictionary:
	return moves_out.get(cid, {})
func after_sequence(cb: Callable) -> void:
	if plan.is_empty():
		cb.call()
	else:
		after.append(cb)
"""
## BattleChoreo.plan_for's melee plan (choreo.json melee: approach 0.3, strike 0.3, contact at 0.55, recover 0.15,
## return 0.32).
const MELEE := {
	"style": "melee",
	"approach_end": 0.3,
	"contact": 0.465,
	"strike_end": 0.6,
	"recover_end": 0.75,
	"return_end": 1.07,
	"kos": [],
}

var engine: BattleEngine
var standin: Node
var audio: ChoreoAudio
var heard: Array = []
var settings: UiSettings
var prev_settings: UiSettings


func before_each() -> void:
	engine = BattleEngine.new()
	var party: Array[StringName] = [&"rhen", &"asha", &"toma"]
	var reserve: Array[StringName] = [&"ysolde"]
	engine.setup(BattleDB.load_default(), party, reserve, ENCOUNTER, 7)
	if not engine.vowbound.rows.has(&"ilun"):
		engine.vowbound.rows[&"ilun"] = {"id": "ilun", "caller": "asha"}
	var script := GDScript.new()
	script.source_code = STANDIN
	assert_eq(script.reload(), OK, "the stand-in compiles")
	standin = Node.new()
	standin.set_script(script)
	prev_settings = UiSettings.shared()
	settings = UiSettings.new()
	UiSettings.set_shared(settings)
	heard = []
	audio = ChoreoAudio.new(AudioData.table(ChoreoAudio.TABLE))
	audio.player = func(id: StringName, _opts: Dictionary) -> void: heard.append([id, audio._clock])
	ChoreoAudio.matcher = func(n: Node) -> String: return "BattleChoreo" if n == standin else ""
	audio.attach(standin, engine)


func _teardown() -> void:
	ChoreoAudio.matcher = Callable()
	audio.free()
	standin.free()
	UiSettings.set_shared(prev_settings)


func _result(actor: StringName, skill: StringName, hits: Array) -> ActionResult:
	var r := ActionResult.new()
	r.actor_id = actor
	r.skill_id = skill
	for h: Dictionary in hits:
		r.hits.append(h)
	return r


func _hit(target: StringName, amount := 20, landed := true) -> Dictionary:
	return {"target_id": target, "hit": landed, "amount": amount, "statuses_added": []}


func _foe() -> StringName:
	return engine.enemies[0].id


func _ids() -> Array:
	var out: Array = []
	for e: Array in heard:
		out.append(e[0])
	return out


func _step(sec: float) -> void:
	var t := 0.0
	while t < sec:
		audio.advance(1.0 / 60.0)
		t += 1.0 / 60.0


func test_every_row_is_a_sound_that_imports() -> void:
	var rows := AudioData.sfx_rows()
	var ids: Array[String] = []
	_collect(audio.data, ids)
	assert_true(ids.size() > 20, "the table names its rows (%d)" % ids.size())
	for id in ids:
		assert_true(rows.has(id), "%s is an sfx row" % id)
		var row := rows.get(id, {}) as Dictionary
		assert_eq(str(row.get("bus", "")), "Combat", "%s plays on the Combat bus" % id)
		for f: Variant in row.get("files", []):
			assert_true(ResourceLoader.exists(str(f)), "%s: %s imports" % [id, f])
	_teardown()


## The sound values of choreo_sfx.json (the keys that hold rows, as tools/audio/data_check.py reads them).
func _collect(d: Dictionary, out: Array[String]) -> void:
	for st: Dictionary in (d["styles"] as Dictionary).values():
		for k: String in ["approach", "strike", "return", "contact"]:
			var v := str(st.get(k, ""))
			if v != "" and v != ChoreoAudio.WEAPON and not out.has(v):
				out.append(v)
		for k: String in ["strike_by_weapon", "contact_by_weapon"]:
			for v: Variant in (st.get(k, {}) as Dictionary).values():
				if str(v) != "" and not out.has(str(v)):
					out.append(str(v))
	var rest: Array = (d["skills"] as Dictionary).values() + (d["accents"] as Dictionary).values()
	rest += (d["vowbound"] as Dictionary).values() + [d["ko"], d["enter"]["sfx"], d["step_off"]["sfx"]]
	rest.append(d["flood"]["sfx"])
	for v: Variant in rest:
		if v is String and str(v) != "" and not out.has(str(v)):
			out.append(str(v))


func test_whoosh_peaks_match_the_source() -> void:
	# assets_src/sfx/choreo_sfx.py PEAKS: the crest of each whoosh file
	var want := {"whoosh_melee": 0.12, "whoosh_heavy": 0.22, "whoosh_cast": 0.3, "whoosh_throw": 0.1}
	for k: String in want:
		assert_between(float((audio.data["peaks"] as Dictionary).get(k, -1.0)), want[k] - 0.001, want[k] + 0.001, k)
	_teardown()


func test_a_melee_plays_its_steps_whoosh_and_weapon_on_the_beats() -> void:
	standin.set(&"plan", MELEE)
	standin.emit_signal(&"beat", &"approach", &"rhen")
	standin.emit_signal(&"beat", &"strike", &"rhen")  # same frame here; the approach steps are spread over 0.3 s
	_step(0.3)
	assert_eq(_ids().count(&"choreo_step"), 3, "three footfalls over the run in")
	assert_true(_ids().has(&"whoosh_melee"), "the swing")
	var whoosh_at := 0.0
	for e: Array in heard:
		if e[0] == &"whoosh_melee":
			whoosh_at = float(e[1])
	# strike at 0 here, contact 0.165 s later, the crest 0.12 s into the file
	assert_between(whoosh_at, 0.165 - 0.12 - 0.02, 0.165 - 0.12 + 0.02, "the crest lands on the contact")
	standin.emit_signal(&"contact", _result(&"rhen", &"attack", [_hit(_foe())]))
	assert_eq(_ids().back(), &"accent_hooks", "Rhen's reef-hooks on the contact")
	heard.clear()
	standin.emit_signal(&"beat", &"return", &"rhen")
	_step(0.4)
	assert_eq(_ids(), [&"choreo_step", &"choreo_step", &"choreo_step"], "and back to his mark")
	_teardown()


func test_battle_speed_tightens_the_steps() -> void:
	standin.set(&"plan", MELEE)
	standin.set(&"speed", 2.0)
	standin.emit_signal(&"beat", &"approach", &"rhen")
	_step(0.16)
	assert_eq(_ids().count(&"choreo_step"), 3, "all three inside the 0.15 s approach at 2x")
	_teardown()


func test_each_weapon_has_its_own_accent_and_a_miss_has_none() -> void:
	var cases := {
		&"asha": &"accent_staff", &"toma": &"accent_spear", &"ysolde": &"accent_book", &"kerrid": &"accent_cleaver"
	}
	for who: StringName in cases:
		heard.clear()
		standin.emit_signal(&"contact", _result(who, &"attack", [_hit(_foe())]))
		assert_eq(_ids(), [cases[who]], "%s's weapon" % who)
	heard.clear()
	standin.emit_signal(&"contact", _result(&"rhen", &"attack", [_hit(_foe(), 0, false)]))
	assert_eq(_ids(), [], "a miss: the whoosh and the dodge, no touch")
	standin.emit_signal(&"contact", _result(_foe(), &"pinch", [_hit(&"rhen")]))
	assert_eq(_ids(), [&"accent_claw"], "a crab's claws")
	heard.clear()
	standin.emit_signal(&"contact", _result(&"lantern_eel", &"attack", [_hit(&"rhen")]))
	assert_eq(_ids(), [&"accent_teeth"], "an eel bites")
	_teardown()


func test_casts_and_guards() -> void:
	standin.set(&"styles", {"ember": "cast", "brace": "guard", "mend": "support"})
	standin.emit_signal(&"contact", _result(&"ysolde", &"ember", [_hit(_foe())]))
	assert_eq(_ids(), [&"accent_focus"], "Ysolde's focus releases the cast")
	heard.clear()
	standin.emit_signal(&"contact", _result(&"toma", &"brace", [_hit(&"toma", 0)]))
	assert_eq(_ids(), [&"accent_shield"], "Toma sets his shield")
	heard.clear()
	standin.emit_signal(&"contact", _result(&"rhen", &"brace", [_hit(&"rhen", 0)]))
	assert_eq(_ids(), [&"accent_guard"], "a guard without a shield")
	heard.clear()
	standin.emit_signal(&"contact", _result(&"asha", &"mend", [_hit(&"rhen", -30)]))
	assert_eq(_ids(), [], "a heal adds nothing over its own sound")
	_teardown()


func test_swell_finishers_the_toll_and_the_surge() -> void:
	var styles := {"lamp_dive": "dive", "shallows_verse": "verse", "return_tide": "brace", "written_light": "glyph"}
	styles["toll"] = "toll"
	standin.set(&"styles", styles)
	var cases := [
		[&"rhen", &"lamp_dive", &"swell_rhen"],
		[&"asha", &"shallows_verse", &"swell_asha"],
		[&"toma", &"return_tide", &"swell_toma"],
		[&"ysolde", &"written_light", &"swell_ysolde"],
		[_foe(), &"toll", &"toll_wave"],
		[_foe(), &"flood_surge", &"flood_surge"],
	]
	for c: Array in cases:
		heard.clear()
		standin.emit_signal(&"contact", _result(c[0], c[1], [_hit(&"rhen", -10 if c[1] == &"shallows_verse" else 40)]))
		assert_eq(_ids(), [c[2]], "%s" % c[1])
	_teardown()


func test_heavy_weapons_swing_heavy_and_fliers_make_no_steps() -> void:
	var plan := MELEE.duplicate()
	standin.set(&"plan", plan)
	standin.emit_signal(&"beat", &"strike", &"kerrid")
	_step(0.1)
	assert_eq(_ids(), [&"whoosh_heavy"], "the anchor-cleaver")
	heard.clear()
	standin.emit_signal(&"beat", &"approach", &"gull_harrier#2")
	_step(0.4)
	assert_eq(_ids(), [], "a gull flies in")
	_teardown()


func test_a_ko_collapses_but_a_vowbound_is_drawn_under() -> void:
	var plan := MELEE.duplicate()
	plan["kos"] = [_foe()]
	standin.set(&"plan", plan)
	standin.emit_signal(&"beat", &"ko", &"rhen")
	assert_eq(_ids(), [&"ko_collapse"])
	heard.clear()
	plan["kos"] = [&"ilun"]
	standin.emit_signal(&"beat", &"ko", _foe())
	assert_eq(_ids(), [], "Ilun's fall plays as he leaves")
	_teardown()


func test_the_vowbound_call_rise_and_fall() -> void:
	var ilun := BattleCombatant.new()
	ilun.id = &"ilun"
	engine.vowbound.called.emit(ilun)
	assert_eq(_ids(), [&"vowbound_beckon", &"ilun_call"], "the caller calls; his net-float answers")
	heard.clear()
	var outs := {&"rhen": {"t": -0.5, "spec": {"sec": 0.5}}}
	standin.set(&"moves_out", outs)
	audio.advance(0.0)
	assert_eq(_ids(), [], "not before the step-off starts")
	outs[&"rhen"]["t"] = 0.0
	_step(0.5)
	assert_eq(_ids(), [&"choreo_step", &"choreo_step", &"choreo_step"], "the party steps off")
	heard.clear()
	var ins := {&"ilun": {"t": 0.01, "spec": {"sec": 1.3}}}
	standin.set(&"moves_in", ins)
	_step(0.1)
	assert_eq(_ids(), [&"vowbound_rise", &"ilun_rise"], "once, as he rises, with his own wings and float")
	heard.clear()
	ins[&"ilun"] = {"t": 0.0, "spec": {"sec": 2.6}}
	standin.set(&"moves_in", {})
	audio.advance(0.0)
	standin.set(&"moves_in", ins)
	audio.advance(0.0)
	assert_eq(_ids(), [&"vowbound_rise_long", &"ilun_rise"], "the first call's slow rise")
	heard.clear()
	engine.vowbound.departed.emit(ilun, true)
	standin.set(&"moves_out", {&"ilun": {"t": 0.0, "spec": {"sec": 1.5}}})
	audio.advance(0.0)
	assert_eq(_ids(), [&"vowbound_fall", &"ilun_sink"], "struck down: drawn under")
	heard.clear()
	standin.set(&"moves_out", {})
	audio.advance(0.0)
	engine.vowbound.departed.emit(ilun, false)
	standin.set(&"moves_out", {&"ilun": {"t": 0.0, "spec": {"sec": 0.9}}})
	audio.advance(0.0)
	assert_eq(_ids(), [&"vowbound_sink", &"ilun_sink"], "dismissed: he sinks back")
	_teardown()


func test_a_vowbound_without_layers_plays_only_the_shared_rows() -> void:
	var other := BattleCombatant.new()
	other.id = &"unvoiced_vowbound"
	engine.vowbound.called.emit(other)
	assert_eq(_ids(), [&"vowbound_beckon"], "no layer row for it: the shared call only")
	_teardown()


func test_kahre_and_virel_answer_the_call_with_their_own_layer() -> void:
	for vid: StringName in [&"kahre", &"virel"]:
		var v := BattleCombatant.new()
		v.id = vid
		engine.vowbound.called.emit(v)
		assert_eq(_ids(), [&"vowbound_beckon", StringName(String(vid) + "_call")], "%s's keepsake answers" % vid)
		heard.clear()
	_teardown()


func test_instant_pacing_keeps_the_contact_layer_only() -> void:
	standin.set(&"anim", false)
	engine.vowbound.called.emit(BattleCombatant.new())
	engine.phase_changed.emit(engine.enemies[0], &"flood")
	standin.emit_signal(&"contact", _result(&"toma", &"attack", [_hit(_foe())]))
	_step(0.5)
	assert_eq(_ids(), [&"accent_spear"], "nothing moves, so only the accent on the instant contact")
	_teardown()


func test_the_flood_braces_after_the_action_in_slot_order() -> void:
	standin.set(&"data", BattleChoreo.load_data())
	var bell := BattleCombatant.new()
	bell.id = &"drownbell"
	var stagger := float(BattleChoreo.load_data()["bosses"]["drownbell"]["flood"]["stagger_sec"])
	assert_eq(float(audio.flood_for(bell)["stagger_sec"]), stagger, "the stagger is the choreography's own")
	engine.phase_changed.emit(engine.enemies[0], &"flood")
	assert_eq((standin.get(&"after") as Array).size(), 0, "a foe with no flood row braces no one")
	standin.set(&"plan", MELEE)
	engine.phase_changed.emit(bell, &"flood")
	assert_eq(_ids(), [], "it waits for the action playing")
	var after: Array = standin.get(&"after")
	assert_eq(after.size(), 1)
	standin.set(&"plan", {})
	(after[0] as Callable).call()
	_step(0.3)
	assert_eq(_ids(), [&"flood_brace", &"flood_brace", &"flood_brace"], "each of the three")
	var gap := float(heard[2][1]) - float(heard[0][1])
	assert_between(gap, 2.0 * stagger - 0.02, 2.0 * stagger + 0.02, "choreo.json's stagger apart")
	_teardown()


func test_reduced_audio_drops_the_accents_and_steps() -> void:
	settings.set_value(ChoreoAudio.REDUCED_AUDIO, true)
	assert_true(audio.reduced, "followed live")
	standin.set(&"plan", MELEE)
	standin.emit_signal(&"beat", &"approach", &"rhen")
	standin.emit_signal(&"beat", &"strike", &"rhen")
	standin.emit_signal(&"contact", _result(&"rhen", &"attack", [_hit(_foe())]))
	_step(0.4)
	assert_eq(_ids(), [&"whoosh_melee"], "the swing stays; BattleAudio's hit is the one layer")
	_teardown()


func test_the_director_attaches_by_class_name_and_lets_go() -> void:
	assert_true(ChoreoAudio.wants(standin), "the matcher names the stand-in BattleChoreo")
	var other := Node.new()
	assert_false(ChoreoAudio.wants(other), "any other node")
	other.free()
	ChoreoAudio.matcher = Callable()
	assert_false(ChoreoAudio.wants(standin), "no class name, no hook (the real class matches by name)")
	ChoreoAudio.matcher = func(n: Node) -> String: return "BattleChoreo" if n == standin else ""
	var dir := AudioDirector.new()
	_host().add_child(dir)
	dir.setup(AudioData.table(AudioData.MIX), AudioData.table(AudioData.MUSIC), {"sfx": AudioData.sfx_rows()})
	dir.set_process(false)
	var holder := Node.new()
	holder.set_script(_engine_holder())
	holder.set(&"engine", engine)
	_host().add_child(holder)
	holder.add_child(standin)
	var l := ChoreoAudio.attach_to(standin, dir)
	assert_true(l != null and dir.listeners.get(standin) == l, "a listener under the director")
	assert_eq(l.engine, engine, "the engine found on an ancestor")
	assert_eq(ChoreoAudio.attach_to(standin, dir), null, "once")
	assert_true(l.player.is_valid(), "it plays through the director's play_sfx")
	# (recorded here: a real playback left running at exit is reported as a leak)
	l.player = func(id: StringName, _opts: Dictionary) -> void: assert_true(dir.sfx.has(id), "%s is a bank row" % id)
	standin.emit_signal(&"contact", _result(&"rhen", &"attack", [_hit(_foe())]))
	assert_eq(l.played, [&"accent_hooks"] as Array[StringName], "the listener the director built hears it")
	holder.remove_child(standin)
	dir.advance(0.0)
	assert_false(dir.listeners.has(standin), "freed when the choreography leaves (a retry)")
	for p: Node in dir.find_children("*", "AudioStreamPlayer", true, false):
		(p as AudioStreamPlayer).stop()
	holder.free()
	dir.free()
	audio.free()
	standin.free()
	ChoreoAudio.matcher = Callable()
	UiSettings.set_shared(prev_settings)


func test_a_node_without_the_signals_connects_nothing() -> void:
	var bare := Node.new()
	var l := ChoreoAudio.new(audio.data)
	l.attach(bare, null)
	l.advance(0.1)
	assert_eq(l.played, [] as Array[StringName], "no signals, no engine, no sound and no error")
	l.free()
	bare.free()
	_teardown()


func _engine_holder() -> GDScript:
	var s := GDScript.new()
	s.source_code = "extends Node\nvar engine: BattleEngine\n"
	s.reload()
	return s


func _host() -> Node:
	return (Engine.get_main_loop() as SceneTree).current_scene
