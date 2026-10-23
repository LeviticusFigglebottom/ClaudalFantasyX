---
id: M1-NAR-04
title: Dialogue format requests from Narrative
role: architect
status: review
owner_session: architect-stream-3
depends_on: [M1-NAR-03]
milestone: M1
request-from: "narrative"
reviewer: narrative
---
## Goal
Writer-facing additions to the .dlg format (ADR 0004), requested in the M1-NAR-02 report.

## Acceptance criteria
- [x] Alias speaker name before introduction
- [x] Emotion and VO identity for narration
- [x] Sung-line and do-not-translate conventions
- [x] @sfx cue, reserved @music silence, documented @vfx/@camera grade= options
- [x] dlgc --assign-ids helper
- [x] Declared dialogue event names, validated
- [x] Warning for lines over 25 words
- [x] @wait music=<marker>

## Notes
Also needs a unit test for tools/dialogue_stats.py (done: `tools/tests/test_dialogue_stats.py`).

The full reference is in `docs/kb/tech/dialogue_format.md`. Every addition is backward compatible: optional op fields are written only when used, the format stays 1, and ch02 compiles byte-identical.
- **Alias (per line):** `Asha as "The girl" [smile]: ...`. The name gets its own loc row, `DLG_NAME_ASHA_THE_GIRL`, and the op carries `name_key`, which DialogueBox shows instead of the speaker's name. I chose a per-line alias over a scene-level `@alias` cue because it carries no state, so it stays correct across branches, jumps, and `start(node)`.
- **Narration:** `Narrator(rhen) [tender]: ...` (the identity is optional). `narrator` is a reserved speaker name, and narration still shows no name and follows the `narration_blip` rule. The op carries `narrator`, and `dialogue_stats` counts these lines as `(narration: rhen)`.
- **`#sung`:** no blips and no lip-flap in DialogueBox, plus the `DialogueBodySung` label variation for UI to style. **`#notr`** requires a `#tn:"..."` note. Notes are written to the generated `game/data/dialogue/compiled/translator_notes.tsv`, which is a `.tsv` so Godot doesn't import it.
- **Cues:** `game/data/dialogue/cues.json` holds the cue names, args, keys, option sets (`grades`, `vfx_*`), and the reserved `@music silence`. It also checks `grade:` headers. Adds `@sfx sound [vol=0..1] [at=]`. Unknown cues and keys are now errors. The fixture's undocumented `@camera ... hold=true` became `grade=ch02`.
- **Events:** declared in `game/data/dialogue/events.json`, and their args are checked. `test_only` events are allowed only in `game/data/dialogue/test/`.
- **Long lines:** a dlgc warning over 25 words, shown by the validator. `#long` silences it.
- **`dlgc --assign-ids FILE [--prefix P]`:** uses the file's most common prefix (or the scene name) and counts on from the project-wide maximum. It never renumbers existing ids.
- **`@wait music=<marker> [max=]`:** the runner signals `music_wait_requested` and holds the wait until the sequencer calls `music_marker_reached` or `release_wait`. The contract is in the format doc.
- **Production scenes:** the story text is unchanged. On ch03, the four `#lamptongue` lines are now `#notr` with a translator note, and C08 has `grade=ch03_boss` (Art sync, M1-ART-03). The `steps` header `grade: ch03_steps` is **not** applied, because no doc defines that grade yet. It is one line to add to `cues.json` `grades` once Art lands it.
- **For Narrative:** aliases in ch02 (Asha before line 030) and `Narrator(rhen)` on the `#vo` lines are writing calls, so I left them for you.

## Review log
