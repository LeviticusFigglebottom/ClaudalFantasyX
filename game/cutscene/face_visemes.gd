class_name FaceVisemes
extends RefCounted
## The mouth shapes a line's text asks for (M2-FP-18; docs/kb/tech/cutscenes.md, "Faces"). The
## DialogueBox opens and closes the mouth as the text reveals (mouth_flap); CutsceneFace takes the
## next syllable from this track on each opening and its closing shape on each closing:
##   open   the syllable's first vowel ("vowels": a -> aa, e -> e, i/y -> i, o -> o, u -> u)
##   close  the lips before the next vowel: the first of the consonants between the two vowel runs
##          that is in "closers" (m/b/p -> mbp, f/v -> fv), else "rest"
## Tables: sequencer.json "visemes". A letter in neither table (digits, punctuation, spaces) only
## separates.


## [{open: StringName, close: StringName}] for `text`, one row per vowel run.
static func track(text: String, cfg: Dictionary) -> Array[Dictionary]:
	var vowels: Dictionary = cfg.get("vowels", {})
	var closers: Dictionary = cfg.get("closers", {})
	var rest := StringName(str(cfg.get("rest", "rest")))
	var out: Array[Dictionary] = []
	var lower := text.to_lower()
	var i := 0
	var n := lower.length()
	while i < n:
		var c := lower[i]
		if not vowels.has(c):
			i += 1
			continue
		var row := {"open": StringName(str(vowels[c])), "close": rest}
		while i < n and vowels.has(lower[i]):
			i += 1
		while i < n and not vowels.has(lower[i]):
			if row["close"] == rest and closers.has(lower[i]):
				row["close"] = StringName(str(closers[lower[i]]))
			i += 1
		out.append(row)
	return out
