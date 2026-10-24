class_name FaceVisemes
extends RefCounted
## The grapheme-to-viseme pass of the cutscene lip sync (M2-CHR-10, replacing M2-FP-18's vowel
## track; docs/kb/tech/cutscenes.md, "Faces"). There is no voice, so the line's text is the speech:
## each word is split into grapheme groups (English digraphs and trigraphs, word-start and
## word-end rules, silent letters, soft c/g, double letters) and each group becomes one or more
## segments on the rig's 10 visemes. Punctuation in "pauses" becomes a rest segment that also
## covers the spaces after it. All tables are game/data/cutscene/lipsync.json.
##
## A segment is {"v": StringName viseme, "at": float, "len": float, "kind": StringName}, with `at`
## and `len` in characters of the text (the DialogueBox reveals one character per 1 / cps
## seconds), so the timing follows the reveal and the shapes never depend on the speed.

const KIND_SPEECH := &"speech"
const KIND_PAUSE := &"pause"
const REST := &"rest"
const WORD_START := "^"
const WORD_END := "$"


## The viseme segments of `text`, in order, adjacent same-viseme segments merged.
static func segments(text: String, cfg: Dictionary) -> Array[Dictionary]:
	var lower := text.to_lower()
	var pauses := str(cfg.get("pauses", ""))
	var keys := _sorted_keys(cfg.get("graphemes", {}))
	var out: Array[Dictionary] = []
	var i := 0
	var n := lower.length()
	while i < n:
		var c := lower[i]
		if _is_letter(c):
			var j := i
			while j < n and _is_letter(lower[j]):
				j += 1
			_word(lower.substr(i, j - i), float(i), cfg, keys, out)
			i = j
		elif pauses.contains(c):
			var j := i
			while j < n and (pauses.contains(lower[j]) or lower[j].strip_edges().is_empty()):
				j += 1
			_push(out, REST, float(i), float(j - i), KIND_PAUSE)
			i = j
		else:
			i += 1  # spaces, digits, apostrophes: time with no shape
	return out


## Just the viseme names, in order (tests, debug).
static func names(segs: Array[Dictionary]) -> Array[StringName]:
	var out: Array[StringName] = []
	for s in segs:
		out.append(s["v"])
	return out


static func _word(word: String, offset: float, cfg: Dictionary, keys: Array[String], out: Array[Dictionary]) -> void:
	var graphemes: Dictionary = cfg.get("graphemes", {})
	var letters: Dictionary = cfg.get("letters", {})
	var soft: Dictionary = cfg.get("soft", {})
	var n := word.length()
	var j := 0
	while j < n:
		var matched := false
		for key: String in keys:
			var body := key.trim_prefix(WORD_START).trim_suffix(WORD_END)
			if key.begins_with(WORD_START) and j != 0:
				continue
			if not word.substr(j).begins_with(body):
				continue
			if key.ends_with(WORD_END) and j + body.length() != n:
				continue
			var vs: Array = graphemes[key]
			var share := float(body.length()) / maxf(1.0, float(vs.size()))
			for k in vs.size():
				_push(out, StringName(str(vs[k])), offset + j + k * share, share, KIND_SPEECH)
			j += body.length()
			matched = true
			break
		if matched:
			continue
		var c := word[j]
		var run := 1
		while j + run < n and word[j + run] == c:
			run += 1
		if _silent_final_e(word, j, cfg):
			j += run
			continue
		var v := StringName(str(letters.get(c, "")))
		if soft.has(c):
			var rule: Dictionary = soft[c]
			var next := word[j + run] if j + run < n else ""
			if next != "" and str(rule.get("before", "")).contains(next):
				v = StringName(str(rule.get("v", "")))
		if v != &"":
			_push(out, v, offset + j, float(run), KIND_SPEECH)
		j += run


## A word-final e after a consonant, in a word with an earlier vowel ("love", "are"; not "the").
static func _silent_final_e(word: String, j: int, cfg: Dictionary) -> bool:
	if not bool(cfg.get("silent_final_e", false)) or j != word.length() - 1 or word[j] != "e" or j < 2:
		return false
	var vowels := str(cfg.get("vowel_letters", ""))
	if vowels.contains(word[j - 1]):
		return false
	for k in j - 1:
		if vowels.contains(word[k]):
			return true
	return false


static func _push(out: Array[Dictionary], v: StringName, at: float, span: float, kind: StringName) -> void:
	if not out.is_empty():
		var last: Dictionary = out[-1]
		var end := float(last["at"]) + float(last["len"])
		if last["v"] == v and last["kind"] == kind and is_equal_approx(end, at):
			last["len"] = float(last["len"]) + span
			return
	out.append({"v": v, "at": at, "len": span, "kind": kind})


static func _sorted_keys(graphemes: Dictionary) -> Array[String]:
	var keys: Array[String] = []
	for k: Variant in graphemes.keys():
		keys.append(str(k))
	keys.sort_custom(
		func(a: String, b: String) -> bool:
			var la := a.trim_prefix(WORD_START).trim_suffix(WORD_END).length()
			var lb := b.trim_prefix(WORD_START).trim_suffix(WORD_END).length()
			if la != lb:
				return la > lb
			return a < b
	)
	return keys


static func _is_letter(c: String) -> bool:
	return c >= "a" and c <= "z"
