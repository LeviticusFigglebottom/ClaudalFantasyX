extends TestCase
## M1-AUD-02: every looping music cue imports as AudioStreamOggVorbis, its sidecar
## (<name>.loop.json, written by tools/audio/render_all.py) is sane, and the loop settings
## from the sidecar apply to the stream and agree with the import settings and the file length.

const LOOPING_CUES: Array[String] = [
	"res://assets/audio/music/battle_standard.ogg",
	"res://assets/audio/music/temple_trial.ogg",
	"res://assets/audio/music/shell_shrine_interior.ogg",
	"res://assets/audio/music/haluna_village.ogg",
	"res://assets/audio/music/haluna_night.ogg",
	"res://assets/audio/music/battle_standard_v2.ogg",
	"res://assets/audio/music/drownbell_p1.ogg",
	"res://assets/audio/music/drownbell_p2.ogg",
	"res://assets/audio/music/saltgrass_causeway.ogg",
	"res://assets/audio/music/lamp_diver.ogg",
	"res://assets/audio/music/sefir_theme.ogg",
	"res://assets/audio/music/tidecup_match.ogg",
	"res://assets/audio/music/terraces_of_ash.ogg",
	"res://assets/audio/music/corrow_seawall.ogg",
	"res://assets/audio/music/hullgnaw.ogg",
	"res://assets/audio/music/spar_wraith.ogg",
	"res://assets/audio/music/cinder_matron_p1.ogg",
	"res://assets/audio/music/cinder_matron_p2.ogg",
	"res://assets/audio/music/undertows_reach_p1.ogg",
	"res://assets/audio/music/undertows_reach_p2.ogg",
	"res://assets/audio/music/undertows_reach_p3.ogg",
]
const SAMPLE_RATE := 44100
const MIN_LENGTH_S := 60.0
const MAX_LENGTH_S := 95.0
const MIN_LOOP_S := 30.0
## Ogg length as Godot reports it may differ from the sidecar by a few ms of codec padding.
const LENGTH_TOLERANCE_S := 0.05


func _sidecar(ogg_path: String) -> Dictionary:
	var json_path := ogg_path.get_basename() + ".loop.json"
	if not FileAccess.file_exists(json_path):
		fail("missing sidecar %s" % json_path)
		return {}
	var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(json_path))
	if not parsed is Dictionary:
		fail("sidecar %s is not a JSON object" % json_path)
		return {}
	return parsed


func test_sidecars_are_consistent() -> void:
	for path in LOOPING_CUES:
		var meta := _sidecar(path)
		if meta.is_empty():
			continue
		var start := int(meta["loop_start_samples"])
		var length := int(meta["loop_length_samples"])
		assert_eq(int(meta["sample_rate"]), SAMPLE_RATE, path)
		assert_true(start >= 0, "%s: loop start >= 0" % path)
		assert_true(length > 0, "%s: loop length > 0" % path)
		assert_eq(start + length, int(meta["total_samples"]), "%s: start + length == total" % path)
		assert_between(float(meta["loop_offset_seconds"]) * SAMPLE_RATE, start - 0.5, start + 0.5, path)
		assert_between(float(meta["loop_length_seconds"]), MIN_LOOP_S, MAX_LENGTH_S, "%s loop body (s)" % path)


func test_streams_load_and_take_loop_settings() -> void:
	for path in LOOPING_CUES:
		var meta := _sidecar(path)
		if meta.is_empty():
			continue
		var stream := load(path) as AudioStreamOggVorbis
		assert_true(stream != null, "%s loads as AudioStreamOggVorbis" % path)
		if stream == null:
			continue
		var length := stream.get_length()
		var total_s := float(meta["total_samples"]) / SAMPLE_RATE
		assert_between(length, MIN_LENGTH_S, MAX_LENGTH_S, "%s length (s)" % path)
		assert_between(length, total_s - LENGTH_TOLERANCE_S, total_s + LENGTH_TOLERANCE_S, "%s vs sidecar" % path)
		# The import settings already carry the loop (render_all.py syncs the .import file).
		assert_true(stream.loop, "%s imports with loop = true" % path)
		assert_between(
			stream.loop_offset,
			float(meta["loop_offset_seconds"]) - 1e-4,
			float(meta["loop_offset_seconds"]) + 1e-4,
			"%s imported loop_offset" % path
		)
		# Apply the sidecar explicitly, as a game-side loader would, and read it back.
		var offset := float(meta["loop_offset_seconds"])
		stream.loop = true
		stream.loop_offset = offset
		assert_true(stream.loop, path)
		assert_between(stream.loop_offset, offset - 1e-6, offset + 1e-6, "%s loop_offset round trip" % path)
		assert_true(stream.loop_offset < length - MIN_LOOP_S, "%s: the loop body is long enough" % path)
		assert_between(
			length - stream.loop_offset,
			float(meta["loop_length_seconds"]) - LENGTH_TOLERANCE_S,
			float(meta["loop_length_seconds"]) + LENGTH_TOLERANCE_S,
			"%s loop body vs sidecar" % path
		)
		var bpm := float(meta["bpm"])
		if bpm > 0.0:
			assert_between(stream.bpm, bpm - 0.01, bpm + 0.01, "%s bpm" % path)
		# With bpm and beat_count both set, Godot loops after beat_count beats counted from the file start, not from
		# loop_offset, so a cue with an intro would wrap early by the intro: the import keeps beat_count 0 and the
		# engine loops at the file's end (render_all.py _sync_import; the sidecar keeps the musical count).
		assert_eq(stream.beat_count, 0, "%s imports with beat_count 0" % path)


func test_playback_instantiates() -> void:
	# The imported stream decodes far enough to create a playback (no codec errors).
	for path in LOOPING_CUES:
		var stream := load(path) as AudioStreamOggVorbis
		if stream == null:
			fail("%s did not load" % path)
			continue
		var playback := stream.instantiate_playback()
		assert_true(playback != null, "%s instantiates a playback" % path)
