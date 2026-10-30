extends TestCase
## DialogueBox (game/ui/dialogue/dialogue_box.tscn), headless: reveal speed, blips per speaker,
## mouth_flap per vowel, narration, skip, and translation lookup. Plus the data loaders it uses.

const SCENE := "res://game/ui/dialogue/dialogue_box.tscn"
const CPS := 10.0
const LINE_KEY := &"DLG_CH02_BEACH_004"
const LINE_TEXT := "That's a very big spear for a very small conversation."

var box: DialogueBox
var flaps: Array = []
var finished_count: Array[int] = [0]


func before_each() -> void:
	box = (load(SCENE) as PackedScene).instantiate() as DialogueBox
	box.settings = (
		DialogueTextSettings
		. from_dict(
			{
				"chars_per_sec": CPS,
				"min_chars_per_sec": 1.0,
				"max_chars_per_sec": 100.0,
				"blip_every_n_chars": 1,
				"blip_volume_db": 0.0,
				"narration_blip": false,
				"flap_vowels": "aeiouAEIOU",
			}
		)
	)
	# The root is busy while the runner's _ready() runs the tests; host under the runner instead.
	var tree := Engine.get_main_loop() as SceneTree
	(tree.current_scene if tree.current_scene != null else tree.root).add_child(box)
	box.set_process(false)
	box.mouth_flap.connect(func(s: StringName, o: bool) -> void: flaps.append([s, o]))
	box.reveal_finished.connect(func() -> void: finished_count[0] += 1)


func _done() -> void:
	box.free()


func test_scene_loads_with_blip_stream() -> void:
	var blip := box.get_node(^"%Blip") as AudioStreamPlayer
	assert_true(blip.stream != null, "text_blip.ogg is wired")
	assert_false(box.is_revealing())
	_done()


func test_line_text_and_speaker_name_resolve_through_tr() -> void:
	box.show_text(&"rhen", LINE_KEY)
	assert_eq(box.speaker_name(), "Rhen")
	box.skip_reveal()
	assert_eq(box.shown_text(), LINE_TEXT, "dialogue.csv translation is loaded")
	_done()


func test_typewriter_reveals_at_chars_per_sec() -> void:
	box.show_text(&"rhen", LINE_KEY)
	box.advance(0.5)
	assert_eq(box.shown_text(), LINE_TEXT.substr(0, 5))
	box.advance(0.25)
	assert_eq(box.shown_text().length(), 7, "fractional progress accumulates")
	assert_true(box.is_revealing())
	box.advance(100.0)
	assert_false(box.is_revealing())
	assert_eq(finished_count[0], 1)
	_done()


func test_blip_per_non_space_char_with_speaker_pitch() -> void:
	box.show_text(&"toma", LINE_KEY)
	box.advance(0.5)  # "That'" -> 5 non-space chars
	assert_eq(box.blips_played, 5)
	assert_between((box.get_node(^"%Blip") as AudioStreamPlayer).pitch_scale, 0.779, 0.781, "toma's pitch")
	box.advance(0.1)  # "s"
	assert_eq(box.blips_played, 6)
	box.advance(0.1)  # " " -> no blip
	assert_eq(box.blips_played, 6)
	_done()


func test_blip_every_n_chars() -> void:
	box.settings.blip_every_n_chars = 2
	box.show_text(&"asha", LINE_KEY)
	box.advance(0.4)  # "That" -> 4 chars, 2 blips
	assert_eq(box.blips_played, 2)
	_done()


func test_mouth_flap_per_vowel_and_closes_at_end() -> void:
	box.show_text(&"rhen", LINE_KEY)
	box.advance(100.0)
	var opens := 0
	for f: Array in flaps:
		assert_eq(f[0], &"rhen")
		if f[1]:
			opens += 1
	var vowels := 0
	for ch in LINE_TEXT:
		if "aeiouAEIOU".contains(ch):
			vowels += 1
	assert_eq(opens, vowels, "one open per revealed vowel")
	assert_eq(flaps[flaps.size() - 1][1], false, "mouth closes when the line ends")
	_done()


func test_narration_has_no_name_and_no_blip() -> void:
	box.show_text(&"", &"DLG_CH02_BEACH_001")
	box.advance(100.0)
	assert_eq(box.speaker_name(), "")
	assert_eq(box.blips_played, 0)
	_done()


func test_alias_name_replaces_speaker_name() -> void:
	box.show_text(&"asha", LINE_KEY, &"DLG_NAME_ASHA_THE_GIRL")
	assert_eq(box.speaker_name(), "The girl")
	box.advance(0.3)
	assert_between((box.get_node(^"%Blip") as AudioStreamPlayer).pitch_scale, 1.179, 1.181, "still Asha's pitch")
	_done()


func test_alias_from_runner_step() -> void:
	var runner := DialogueRunner.new(DialogueFlagAccess.new())
	runner.forward_events_to_bus = false
	runner.load_scene(&"test_dialogue_fixture")
	runner.start(&"features")
	box.show_line(runner.next())
	assert_eq(box.speaker_name(), "The girl")
	box.show_line(runner.next())
	assert_eq(box.speaker_name(), "Asha", "the alias lasts one line")
	_done()


func test_sung_line_has_no_blips_or_flaps() -> void:
	box.show_text(&"asha", LINE_KEY, &"", true)
	var body := box.get_node(^"%Body") as Label
	assert_eq(body.theme_type_variation, DialogueBox.SUNG_VARIATION)
	box.advance(100.0)
	assert_eq(box.shown_text(), LINE_TEXT, "the text still reveals")
	assert_eq(box.blips_played, 0)
	assert_eq(flaps.size(), 0, "no lip-flap while singing")
	assert_eq(finished_count[0], 1)
	box.show_text(&"asha", LINE_KEY)
	assert_eq(body.theme_type_variation, &"", "the style resets on the next line")
	box.advance(0.3)
	assert_true(box.blips_played > 0, "blips come back")
	_done()


func test_narrator_identity_picks_blip_pitch_when_narration_blips() -> void:
	box.settings.narration_blip = true
	box.show_text(&"", &"DLG_CH02_BEACH_001", &"", false, &"toma")
	box.advance(0.3)
	assert_eq(box.speaker_name(), "", "narration still shows no name")
	assert_true(box.blips_played > 0)
	assert_between((box.get_node(^"%Blip") as AudioStreamPlayer).pitch_scale, 0.779, 0.781, "toma's pitch")
	box.show_text(&"", &"DLG_CH02_BEACH_001", &"DLG_NAME_ASHA_THE_GIRL")
	assert_eq(box.speaker_name(), "", "an alias never names narration")
	_done()


func test_skip_reveal_is_silent() -> void:
	box.show_text(&"asha", LINE_KEY)
	box.advance(0.2)
	var blips := box.blips_played
	flaps.clear()
	box.skip_reveal()
	assert_eq(box.shown_text(), LINE_TEXT)
	assert_eq(box.blips_played, blips)
	assert_eq(finished_count[0], 1)
	_done()


func test_show_line_from_runner_step() -> void:
	var runner := DialogueRunner.new(DialogueFlagAccess.new())
	runner.forward_events_to_bus = false
	runner.load_scene(&"ch02_girl_on_the_beach")
	runner.start()
	var step := runner.next()
	while not step.is_line() or step.speaker == &"":
		step = runner.next()
	box.show_line(step)
	assert_eq(box.speaker_name(), "Asha")
	_done()


func test_speed_setting_is_clamped() -> void:
	box.set_chars_per_sec(1000.0)
	assert_eq(box.settings.chars_per_sec, 100.0)
	box.set_chars_per_sec(0.0)
	assert_eq(box.settings.chars_per_sec, 1.0)
	_done()


func test_default_settings_come_from_data() -> void:
	var s := DialogueTextSettings.load_default()
	assert_true(s.chars_per_sec > 0.0)
	assert_true(s.min_chars_per_sec <= s.chars_per_sec and s.chars_per_sec <= s.max_chars_per_sec)
	assert_true(s.blip_every_n_chars >= 1)
	assert_ne(s.flap_vowels, "")
	_done()


func test_speaker_table_loads() -> void:
	var sp := DialogueSpeakers.load_default()
	assert_true(sp.has(&"asha"))
	assert_eq(sp.name_key(&"asha"), &"CHAR_ASHA")
	assert_eq(sp.portrait_id(&"asha"), &"portrait_asha_placeholder")
	assert_eq(sp.blip_pitch(&"nobody"), DialogueSpeakers.UNPITCHED)
	_done()


## Act I final pass (ADR 0041): a spoken line shows its speaker's portrait in the line's emotion (an untagged line
## keeps it); a speaker without a portrait, and narration, show none (dialogue_portrait.json).
func test_the_speaker_s_portrait_shows_beside_the_line() -> void:
	box.show_text(&"rhen", LINE_KEY)
	box.show_portrait(&"rhen", &"worried")
	var frame := box.portrait()
	assert_true(frame != null and frame.picture().texture != null, "Rhen's face")
	assert_eq(frame.emotion(), &"worried")
	box.show_portrait(&"crowd")
	assert_eq(box.portrait(), null, "a speaker with no portrait: none, not a letter")
	box.show_portrait(&"")
	assert_eq(box.portrait(), null, "narration: none")
	assert_eq(DialogueBox.portrait_for(&"inquisitor"), &"moll", "an alias names the character he is")
	# M4-A2P-081: Warden Malcor Venn reads the Ch14 decree [cold] (ch14_the_vows.dlg) with his own face.
	assert_eq(DialogueBox.portrait_for(&"malcor_venn"), &"venn")
	box.show_portrait(&"malcor_venn", &"cold")
	assert_true(box.portrait() != null and box.portrait().picture().texture != null, "Venn's face, cold")
	_done()


## Lead 2026-10-28: each Act I speaker whose model has landed (a hero stage or a villager stage on
## claude/characters) shows a portrait: a new model without a baked face fails here.
func test_every_act1_speaker_with_a_model_has_a_portrait() -> void:
	var dir := "res://game/data/dialogue/compiled"
	var speakers := {}
	for f: String in DirAccess.get_files_at(dir):
		if f.ends_with(".json") and f.begins_with("ch0"):
			var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(dir.path_join(f)))
			_collect_speakers(parsed, speakers)
	var modelled := 0
	for s: String in speakers:
		var who := String(DialogueBox.portrait_for(StringName(s)))
		var stages := [
			"res://game/levels/_tests/characters/villagers/%s_stage.tscn" % s,
			"res://game/levels/_tests/characters/%s/%s_stage.tscn" % [s, s],
		]
		if stages.any(func(p: String) -> bool: return ResourceLoader.exists(p)):
			modelled += 1
			assert_eq(who, s, "%s has a model, so a portrait" % s)
	assert_true(modelled > 20, "the party and the townsfolk were found")
	_done()


func _collect_speakers(v: Variant, out: Dictionary) -> void:
	if v is Dictionary:
		var d := v as Dictionary
		if d.has("speaker") and str(d["speaker"]) != "":
			out[str(d["speaker"])] = true
		for x: Variant in d.values():
			_collect_speakers(x, out)
	elif v is Array:
		for x: Variant in v as Array:
			_collect_speakers(x, out)
