extends TestCase
## M2-CHR-10: text-driven lip sync with the real game/data/cutscene/lipsync.json. FaceVisemes'
## grapheme pass (digraphs, silent letters, word boundaries, pauses), LipSync's co-articulation
## (dominance blend, bilabial closure, rounding anticipation, the per-shape speed cap) and its
## timing against the DialogueBox's reveal.

const BOX_SCENE := "res://game/ui/dialogue/dialogue_box.tscn"
const DT := 1.0 / 60.0
const EPS := 0.0001
const CPS := 20.0
## Slack on the per-frame cap: the linear interpolation between samples is exact, float32 is not.
const CAP_SLACK := 1.001

var cfg: Dictionary = {}


func before_each() -> void:
	cfg = LipSync.load_config()


# --- grapheme pass --------------------------------------------------------------------------


func test_digraphs_map_to_one_viseme_each() -> void:
	_names_are("the ship", [&"l", &"e", &"st", &"i", &"mbp"], "th, sh")
	_names_are("phone", [&"fv", &"o", &"st"], "ph; the final e is silent")
	_names_are("see food", [&"st", &"i", &"fv", &"u", &"st"], "ee, oo")
	_names_are("chew", [&"st", &"u"], "ch, ew")
	_names_are("out", [&"aa", &"u", &"st"], "ou glides from open to round")


func test_silent_letters_and_word_boundaries() -> void:
	_names_are("knight", [&"st", &"aa", &"i", &"st"], "word-initial kn, igh; gh is silent")
	_names_are("lamb", [&"l", &"aa", &"mbp"], "word-final mb")
	_names_are("love", [&"l", &"o", &"fv"], "silent final e after a vowel earlier in the word")
	_names_are("the", [&"l", &"e"], "but the e of 'the' is spoken")
	_names_are("unknown", [&"u", &"st", &"st", &"o", &"u", &"st"], "kn mid-word: the k is transparent")
	_names_are("hug", [&"u"], "h and hard g take time but no shape")
	_names_are("ice", [&"i", &"st"], "soft c before e")


func test_double_letters_merge_into_one_segment() -> void:
	var segs := FaceVisemes.segments("all", cfg)
	assert_eq(FaceVisemes.names(segs), [&"aa", &"l"] as Array[StringName])
	assert_between(float(segs[1]["len"]), 2.0 - EPS, 2.0 + EPS, "ll spans both letters")


func test_punctuation_rests_over_the_spaces_after_it() -> void:
	var segs := FaceVisemes.segments("Ah, ah.", cfg)
	assert_eq(FaceVisemes.names(segs), [&"aa", &"rest", &"aa", &"rest"] as Array[StringName])
	assert_eq(segs[1]["kind"], FaceVisemes.KIND_PAUSE)
	assert_between(float(segs[1]["at"]), 2.0 - EPS, 2.0 + EPS, "the comma")
	assert_between(float(segs[1]["len"]), 2.0 - EPS, 2.0 + EPS, "and the space after it")


# --- co-articulation ------------------------------------------------------------------------


func test_bilabials_and_labiodentals_close_the_lips() -> void:
	var lip := LipSync.new(cfg)
	lip.start("Up, off.", 40.0, &"", 1)
	var p := _at(lip, 1.5 / 40.0)
	assert_true(float(p.get(&"vis_mbp", 0.0)) > 0.3, "p presses the lips at 40 cps (%.2f)" % p.get(&"vis_mbp", 0.0))
	assert_true(float(p.get(&"vis_u", 0.0)) < 0.02, "and nothing else holds the mouth open")
	var f := _at(lip, 6.0 / 40.0)
	assert_true(float(f.get(&"vis_fv", 0.0)) > 0.2, "ff tucks the lip (%.2f)" % f.get(&"vis_fv", 0.0))


func test_bilabials_close_the_lips_between_open_vowels() -> void:
	var lip := LipSync.new(cfg)
	lip.start("amama", CPS, &"", 1)
	var m_centre := 1.5 / CPS
	var a_centre := 2.5 / CPS
	var at_m := _at(lip, m_centre)
	var at_a := _at(lip, a_centre)
	assert_true(float(at_m.get(&"vis_mbp", 0.0)) > 0.3, "the lips press at m (%.2f)" % at_m.get(&"vis_mbp", 0.0))
	assert_true(
		float(at_m.get(&"vis_aa", 0.0)) < 0.5 * float(at_a.get(&"vis_aa", 0.0)),
		"the jaw closes for m (aa %.2f at m, %.2f at a)" % [at_m.get(&"vis_aa", 0.0), at_a.get(&"vis_aa", 0.0)]
	)


func test_rounding_is_anticipated_before_the_vowel() -> void:
	var raw := LipSync.blend_at(FaceVisemes.segments("st oo", cfg), 2.0 / CPS, CPS, cfg)
	assert_true(float(raw.get(&"vis_u", 0.0)) > 0.05, "u rounds the lips across the space before it")
	var lip := LipSync.new(cfg)
	lip.start("tess oo", CPS, &"", 1)
	assert_true(float(_at(lip, 4.8 / CPS).get(&"vis_u", 0.0)) > 0.0, "and the capped curve starts early too")


func test_no_shape_moves_faster_than_its_cap_even_at_the_fastest_reveal() -> void:
	var rates: Dictionary = cfg["max_rate_per_s"]
	for cps: float in [20.0, 40.0, 400.0]:
		var lip := LipSync.new(cfg)
		lip.start("Mama, a big fish! Pop the boat, papa.", cps, &"laugh", 5)
		var last := lip.weights()
		var moved := false
		while lip.is_active():
			lip.advance(DT)
			var now := lip.weights()
			for shape: StringName in lip.viseme_shapes():
				var cap := float(rates.get(String(shape), rates["default"])) * DT * CAP_SLACK + EPS
				var step := absf(float(now.get(shape, 0.0)) - float(last.get(shape, 0.0)))
				moved = moved or step > 0.0
				if step > cap:
					fail("%s jumped %.4f in a frame at %d cps (cap %.4f)" % [shape, step, cps, cap])
					return
			last = now
		assert_true(moved, "the mouth moved at %d cps" % cps)


func test_natural_speech_stays_well_inside_the_viseme_extremes() -> void:
	var lip := LipSync.new(cfg)
	lip.start("Mama, a big fish! Pop the boat, papa.", 40.0, &"", 5)
	var peak := 0.0
	while lip.is_active():
		lip.advance(DT)
		for shape: StringName in lip.viseme_shapes():
			if shape != &"vis_mbp" and shape != &"vis_fv":
				peak = maxf(peak, float(lip.weights().get(shape, 0.0)))
	assert_true(peak > 0.15, "it opens (%.2f)" % peak)
	assert_true(peak <= 0.4, "an untagged line stays well inside the extremes (%.2f)" % peak)


func test_the_emotion_tag_scales_the_mouth() -> void:
	var laugh := _peak_aa(&"laugh")
	var plain := _peak_aa(&"")
	var tired := _peak_aa(&"exhausted")
	assert_true(laugh > plain and plain > tired, "laugh %.2f > untagged %.2f > exhausted %.2f" % [laugh, plain, tired])
	assert_eq(LipSync.intensity_for(&"no_such_tag", cfg), LipSync.intensity_for(&"", cfg), "unlisted = default")


func test_the_idle_drift_is_asymmetric_and_only_while_speaking() -> void:
	var lip := LipSync.new(cfg)
	lip.start("Hush now, hush.", CPS, &"", 9)
	for i in 30:
		lip.advance(DT)
	var w := lip.weights()
	assert_true(float(w.get(&"mouth_dimple_L", 0.0)) > 0.0, "one corner drifts")
	assert_eq(float(w.get(&"mouth_dimple_R", 0.0)), 0.0, "the other does not")
	var again := LipSync.new(cfg)
	again.start("Hush now, hush.", CPS, &"", 9)
	for i in 30:
		again.advance(DT)
	assert_eq(again.weights(), w, "the same seed drifts the same way")
	while lip.is_active():
		lip.advance(DT)
	assert_eq(lip.weights(), {}, "nothing after the line")


# --- timing ---------------------------------------------------------------------------------


func test_timing_follows_the_reveal_speed() -> void:
	for cps: float in [10.0, 20.0]:
		var lip := LipSync.new(cfg)
		lip.start("mama", cps, &"", 1)
		assert_between(lip.speech_end_s(), 4.0 / cps - EPS, 4.0 / cps + EPS, "the last character at %d cps" % cps)
		var open := _at(lip, 1.5 / cps)
		var closed := _at(lip, 2.5 / cps)
		assert_true(
			float(closed.get(&"vis_mbp", 0.0)) > float(open.get(&"vis_mbp", 0.0)),
			"the second m lands on its own character at %d cps" % cps
		)
		assert_true(float(open.get(&"vis_aa", 0.0)) > float(closed.get(&"vis_aa", 0.0)), "and the a on its own")
	var lip := LipSync.new(cfg)
	lip.start("mama", 10.0, &"", 1)
	var tail := float(cfg["tail_s"])
	_run_to(lip, 0.4 + tail + DT)
	assert_false(lip.is_active(), "at rest tail_s after the last character")


func test_a_pause_closes_the_mouth_to_rest() -> void:
	var lip := LipSync.new(cfg)
	lip.start("Aaaa,   aaaa.", 10.0, &"", 1)
	var open := float(_at(lip, 2.0 / 10.0).get(&"vis_aa", 0.0))
	var pause := float(_at(lip, 6.0 / 10.0).get(&"vis_aa", 0.0))
	assert_true(open > 0.2, "open mid-word (%.2f)" % open)
	assert_true(pause < 0.1 * open, "rest in the comma's pause (%.3f)" % pause)


func test_the_curve_ends_with_the_dialogue_box_reveal() -> void:
	var box := (load(BOX_SCENE) as PackedScene).instantiate() as DialogueBox
	box.settings = DialogueTextSettings.from_dict(
		{"chars_per_sec": 25.0, "min_chars_per_sec": 1.0, "max_chars_per_sec": 100.0, "flap_vowels": "aeiou"}
	)
	var tree := Engine.get_main_loop() as SceneTree
	(tree.current_scene if tree.current_scene != null else tree.root).add_child(box)
	box.set_process(false)
	var text := "That is a very big spear."
	box.show_text(&"", StringName(text))
	var lip := LipSync.new(cfg)
	lip.start(text, box.settings.chars_per_sec, &"", 1)
	var t := 0.0
	while box.is_revealing():
		box.advance(DT)
		lip.advance(DT)
		t += DT
	assert_between(lip.speech_end_s(), t - DT - EPS, t + EPS, "the mouth's last character is the box's last")
	box.free()


func _names_are(text: String, expected: Array, msg: String) -> void:
	var want: Array[StringName] = []
	for v: Variant in expected:
		want.append(v)
	assert_eq(FaceVisemes.names(FaceVisemes.segments(text, cfg)), want, "%s (%s)" % [msg, text])


## The lip's weights at absolute time `t` (from a fresh start of the same line).
func _at(lip: LipSync, t: float) -> Dictionary:
	_run_to(lip, t)
	return lip.weights()


func _run_to(lip: LipSync, t: float) -> void:
	var left := t - lip.time_s()
	while left > EPS:
		var step := minf(DT, left)
		lip.advance(step)
		left -= step


func _peak_aa(emotion: StringName) -> float:
	var lip := LipSync.new(cfg)
	lip.start("Aaaa aaaa.", 10.0, emotion, 1)
	var peak := 0.0
	while lip.is_active():
		lip.advance(DT)
		peak = maxf(peak, float(lip.weights().get(&"vis_aa", 0.0)))
	return peak


# --- the reveal's punctuation pauses (M2-UI-27) -----------------------------------------------


func test_the_mouth_rests_while_the_reveal_lingers_at_a_comma() -> void:
	var box := (load(BOX_SCENE) as PackedScene).instantiate() as DialogueBox
	box.settings = DialogueTextSettings.load_default()
	var tree := Engine.get_main_loop() as SceneTree
	(tree.current_scene if tree.current_scene != null else tree.root).add_child(box)
	box.set_process(false)
	var text := "Mama, wait."
	box.show_text(&"", StringName(text))
	var cps := box.settings.chars_per_sec
	var times := box.reveal_times()
	var comma := text.find(",")
	var pause := box.settings.pause_after(text, comma)
	assert_true(pause > 0.1, "the box lingers at the comma")
	var lip := LipSync.new(cfg)
	lip.start(text, cps, &"", 1, times)
	var lead := float(cfg.get("lead_s", 0.0))
	assert_between(
		lip.speech_end_s(),
		times[times.size() - 1] + lead - EPS,
		times[times.size() - 1] + lead + EPS,
		"ends with the box"
	)
	var mid := times[comma] + pause * 0.5 + lead
	var speaking := _peak(_said(text, cps, times), lead + 0.5 / cps, times[comma - 1] + lead)
	var resting := _peak(_said(text, cps, times), mid - pause * 0.15, mid + pause * 0.15)
	assert_true(speaking > 0.3, "the mouth opens on Mama (%.2f)" % speaking)
	assert_true(resting < speaking * 0.35, "and is near rest mid-pause (%.2f vs %.2f)" % [resting, speaking])
	var even := LipSync.new(cfg)
	even.start(text, cps, &"", 1)
	assert_true(even.speech_end_s() < lip.speech_end_s(), "without the times it would finish early, out of step")
	box.free()


func _said(text: String, cps: float, times: PackedFloat64Array) -> LipSync:
	var l := LipSync.new(cfg)
	l.start(text, cps, &"", 1, times)
	return l


## The largest weight of any shape between `from` and `to` (s), stepping the lip sync at DT.
func _peak(lip: LipSync, from: float, to: float) -> float:
	var best := 0.0
	var t := lip.time_s()
	while t < from:
		lip.advance(DT)
		t = lip.time_s()
	while t <= to:
		for v: Variant in lip.weights().values():
			best = maxf(best, float(v))
		lip.advance(DT)
		t = lip.time_s()
	return best
