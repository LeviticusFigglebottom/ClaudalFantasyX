# `.dlg` Dialogue Format Reference

The decision and rationale are in [ADR 0004](../decisions/0004-dialogue-format.md). This page is the complete syntax reference. It grows with the cue vocabulary as Cinematics adds cues.

**Pipeline:** `game/data/dialogue/<chapter>/<scene>.dlg` → `python3 tools/dlgc.py` → `game/data/dialogue/compiled/<scene>.json` + `game/data/loc/dialogue.csv` (+ `compiled/translator_notes.tsv`) → `DialogueRunner` (`game/narrative/`) → `DialogueBox` (`game/ui/dialogue/`).

## How to add a scene

1. Create `game/data/dialogue/<chapter>/<scene>.dlg`, e.g. `ch02/ch02_girl_on_the_beach.dlg`. The **first node's `title:` must equal the file name** (without `.dlg`), and scene names are unique across all chapters (compiled output is flat).
2. Write it (syntax below). Give every spoken line and every option a unique `#line:<id>`. Convention: `<chapter>_<scene-short>_<NNN>`, e.g. `#line:ch02_beach_004`. You can leave the ids off while drafting and run `python3 tools/dlgc.py --assign-ids <file>` (see [Line ids](#line-ids-dlgc---assign-ids)).
3. Declare every `$flag` you use in `game/data/flags.tres` (snake_case key, one-sentence description; keep the dict JSON-compatible).
4. New speaker? Add a row to `game/data/dialogue/speakers.json` and its `name_key` to `game/data/loc/strings.csv`.
5. Run `python3 tools/dlgc.py`. Fix any `file:line:` errors it prints.
6. Run `python3 tools/validate_data.py` (it fails if compiled outputs are stale). Commit the `.dlg`, the compiled JSON, and `dialogue.csv` **together**.
7. Run `godot --headless --path . --import` once if `dialogue.csv` is new, so Godot regenerates `dialogue.en.translation`.
8. Play it: `var r := DialogueRunner.new(); r.load_scene(&"<scene>"); r.start()`, then feed `r.next()` steps to a `DialogueBox`.

Never edit `compiled/*.json`, `compiled/translator_notes.tsv`, or `dialogue.csv` by hand; they are regenerated. `python3 tools/dlgc.py --check` (also run by the validator and CI) fails if they are out of date.

## File structure

```
// Comments start with // (whole line, or after whitespace) and are ignored.
title: ch02_girl_on_the_beach      // required; lowercase snake_case
location: ch02/haluna              // optional extra headers are kept in the JSON
---
...body...
===
title: second_node                 // more nodes may follow in the same file
---
...
===
```

- Headers are `key: value` lines before `---`. `title` is required; others are passed through as `headers`. A `grade:` header must be one of the `grades` in `cues.json` (see [Cues](#cues)).
- The body runs from `---` to `===`. Blank lines are ignored.
- `<<jump>>` targets must be nodes in the **same file**. The scene starts at the first node.

## Lines

```
Asha [soft_smile]: There you are. #line:ch02_beach_002
Toma: Lie still, please. #line:ch02_beach_003
The sea gave me back at dawn. #line:ch02_beach_001
```

- `Speaker [emotion]: text #line:<id>`. The speaker is written as a name (`Asha`) and stored as its lowercase id (`asha`), which must exist in `speakers.json`.
- `[emotion]` is optional. When present it must be an id in **`game/data/dialogue/emotions.json`** (the single source of truth; the compiler and validator read it). Empty means "no change" (neutral by default). It drives the expression blends (SPEC §8.3).
- A line **without** `Speaker:` is narration (Rhen's older voice-over, captions). A line that *nearly* matches a speaker line is an error, not narration ([below](#near-miss-speaker-lines)).
- **Every line needs `#line:<id>`**: lowercase letters, digits, and `_`, unique across the whole project. The loc key is `DLG_<ID>` upper-cased (`DLG_CH02_BEACH_002`).
- Other trailing `#tags` (e.g. `#whisper`) are kept in a `tags` list for the UI or Cinematics. Tags with a meaning are listed [below](#tags-with-a-meaning).
- Escapes: `\:` for a colon in narration that would otherwise read as a speaker (`Dawn: grey.` reads as a caption and warns, and `Old Toma: hm.` is a [near miss](#near-miss-speaker-lines)), and `\#` for a literal `#` at the end of a line.
- One line of text per line; there are no multi-line strings. Keep to the voice guide's length rules: the compiler **warns** (it never fails) on a line or option over **25 words**. Tag a line `#long` when the length is earned (Kerrid in Ch14, Sefir in Ch16, Rhen's narration). Words are counted as `tools/dialogue_stats.py` counts them: runs of letters and digits, where an inner `'` or `-` doesn't split a word.

### Speaker alias (before an introduction)

```
Asha as "The girl" [soft_smile]: There you are. #line:ch02_beach_002
Toma as "???": Lie still. #line:ch02_beach_003
```

- `Speaker as "Display name" [emotion]: text`. **Per line**, with no state to carry: the alias lasts for that line only, so it stays correct across branches, jumps, and `start(node)`. The speaker is still the real one, so the blip pitch, portrait, emotion, and lip-flap are the real speaker's.
- The name gets its own loc row, `DLG_NAME_<SPEAKER>_<SLUG>` (`DLG_NAME_ASHA_THE_GIRL`). A name with no letters or digits gets a short hash (`DLG_NAME_TOMA_X1A2B3C`). The same alias anywhere in the project shares one row. Two different names that make the same key (`"The girl"` and `"The girl!"`) are an error, and so is a key that clashes with a line id.
- In the compiled op it is `name_key`. `DialogueBox` shows `tr(name_key)` instead of the speaker's `name_key`. `\"` writes a quote inside the name.

### Narration with an emotion and a voice identity

```
Narrator(rhen) [tender]: She smiled first. Every time. #line:ch02_beach_035 #vo
Narrator [grief]: The bell rang under the water. #line:ch03_x_001
```

- `Narrator` is a reserved speaker name (no `speakers.json` row may use the id `narrator`). It compiles to narration: `speaker` stays empty, so the box shows no name, and narration's blip rule (`narration_blip` in `text_box.json`) still applies.
- `[emotion]` works as on spoken lines. `(identity)` is optional and must be a `speakers.json` id: it is the voice of a voice-over (`narrator: "rhen"` in the op). Leave it off for captions. The box uses it only for the blip pitch, and only if narration blips are on. `dialogue_stats.py` counts it as `(narration: rhen)`.
- Only `Narrator` takes `(identity)`, and `Narrator` takes no `as "..."` alias. Plain narration (no `Narrator:`) is unchanged.

### Near-miss speaker lines

A typo in a speaker line used to compile silently to narration (or ship stray text), and its raw `Name [emo]:` text reached players. Now each of these is a `path:line:` error with a "did you mean" hint. "Speaker" below means a `speakers.json` id or `Narrator`:

| Written | Error |
|---|---|
| `Asha [smile] as "The girl": Hello.`, `Kerrid [cold] as The Stranger: Hi.` | `the emotion goes after the alias: did you mean 'Asha as "The girl" [smile]:'?` |
| `Asha as The girl: Hello.` | `an alias needs double quotes: did you mean 'Asha as "The girl":'?` (only when `Asha` is a speaker) |
| `Asha (sad) Hi.`, `Asha (sad): Hi.`, `Asha "sad": Hi.`, `Asha {sad}: Hi.`, `Asha <sad>: Hi.` | `an emotion goes in square brackets, before the colon: did you mean 'Asha [sad]: Hi.'?` (one word inside; without a colon, only when it is an emotion, so `Asha (again) laughed.` is prose). `Narrator (rhen): ...` and `Narrator (asha) [grief]: ...` (with or without the colon) suggest `Narrator(rhen):` / `Narrator(asha) [grief]:`. A speaker id in another speaker's parentheses (`Toma (rhen): Lie still.`) says `'rhen' is a speaker, not an emotion, and only Narrator takes a (speaker id) identity` and suggests `Narrator(rhen):` or `Toma [emotion]:` |
| `Asha, [sad]: Hi.` | `stray ',' between the name and the emotion: did you mean 'Asha [sad]: Hi.'?` |
| `Asha： Hi.` (a full-width colon, from an IME) | `a full-width colon after 'Asha': a speaker line needs ':'` |
| `Asha [sad] Hi there.`, `Asha [sad]; Hi.`, `Asha [sad] — Hi.`, `Toma as "???" Lie still.` | `a speaker line needs a ':' after the name: did you mean 'Asha [sad]: Hi there.'?` (the name a speaker, and the brackets or parentheses hold one identifier-like word) |
| `Kerid [sad] Hi.`, `Ahsa as "The girl" Hello.` | `'Kerid' is not a speaker and a speaker line needs a ':' after the name: did you mean 'Kerrid [sad]: Hi.'?` (review-sweep-E: a close misspelling of a speaker id, `SPEAKER_TYPO_CUTOFF`, counts only with a known emotion or a quoted alias as evidence, so `Kerid [sic] was the word.` and `Kerid smiled.` stay prose) |
| `Narator [grief] The bell.`, `Narrater [grief] ...`, `Narator(asha) [grief] ...`; `Narator: The bell.` | M1-NAR-10: `Narrator` is a typo candidate too, with the stricter `NARRATOR_TYPO_CUTOFF` (0.85), so `Narration`, `Narrate` and `Narrow` stay words. Without a colon: `'Narator' is not a speaker and a speaker line needs a ':' after the name: did you mean 'Narrator [grief]: The bell.'?`. With one: `unknown speaker 'Narator'; did you mean 'Narrator'?` (an error, no longer a caption WARN) |
| `Kerid [Sad] Hi.`, `Asha [Sad]: Hi.` | M1-NAR-10: emotion evidence ignores case, and the hint gives the lowercase id (`did you mean 'Kerrid [sad]: Hi.'?`; `unknown emotion '[Sad]'; did you mean '[sad]'?`). A speaker line still needs the exact id |
| `Kerid (sad): Hi.`, `Kerid, [sad] Hi.`, `Asha, [sad] Hi.` | M1-NAR-10: the wrong-bracket and stray-punctuation errors also catch a misspelt name (with a known emotion as evidence: `'Kerid' is not a speaker; an emotion goes in square brackets, ...`), and stray punctuation without a colon counts when the brackets hold a known emotion |
| `Asha [sad]`, `Kerid as "The Stranger"` (nothing after) | M1-NAR-10: `a speaker line needs ': text' after the name: did you mean 'Asha [sad]: ...'?` (an emotion or an alias is required; a misspelt name needs a known emotion or the alias) |
| `Asha: [sad] Hi.` | `the emotion goes before the colon: did you mean 'Asha [sad]: Hi.'?` (a speaker line whose text starts with one bracketed word; it would otherwise show `[sad]` as text) |
| `Asha [sad]:: Hi.` | `two colons after the speaker: did you mean 'Asha [sad]: Hi.'?` (it would ship `: Hi.`; `Asha: \: Hi.` is fine) |
| `Ahsa [sad]: Hi.`, `Kerid: Hi.` | `unknown speaker 'Ahsa'; did you mean 'Asha'?` |
| `[grief] The bell rang.` | `narration takes an emotion only through Narrator: did you mean 'Narrator [grief]: The bell rang.'? (...)` (only one identifier-like word in the brackets: `[The page is water-stained.]` is prose) |
| `Old Toma: Lie still.`, `Toma Vell: Hi.`, `Old Toma [sad]: Lie still.` | `'Old Toma:' looks like a speaker, but this line would compile as narration (...)`, plus `Did you mean 'Toma:' or 'Toma [emotion]:'?` |

The last row is a **heuristic** (tiered in M1-NAR-07, retuned in review-sweep-D). It looks at narration text (tags aside) up to its first unescaped `:` and fires only when that prefix **reads like a name**:

- it starts with a capital letter and has no `.`, `!`, `?`, `,`, `;`, `…`, `—` or `"`;
- every word is capitalized (`Old`, `Toma`) or a `(...)`/`{...}`/`[...]` group, except lowercase joiners inside it (`of`, `the`, `from`, `in`, `on`, `at`, `by`, `de`, `van`, `von`; **not** `and`, so `Asha and Toma:` is prose);
- `I` and compass points (`North`, `East`, ...) are never name words (`I Remember Corrow:`, `North of Corrow:`), and a prefix that starts with `Not`, `Only`, `Even`, `Just`, `Never`, `Then`, `When` and similar is prose (`Not Asha: me.`);
- the colon is not between digits: `At 6:20 the tide turned.` and `Ratio 3:1` never trigger.

Then, by tier (Lead decision, review-sweep-D):

| Prefix | Result |
|---|---|
| has a `[...]` group (`Old Toma [sad]:`) | **error**: that is speaker syntax |
| 1–2 words, one of them a speaker id, a speaker's display name (its `name_key` text in `game/data/loc/*.csv`), or `Narrator` (`Old Toma:`, `Asha Vell:`) | **error** |
| any other name-shaped prefix of 1–6 words: captions and headings (`Chapter Two: The Raft`, `The Hollow: three days later.`, `Interlude: Ysolde`, `The Keeper of Lamps:`) | **WARN** with the `\:` hint; never fails the build |

A bare `Word: text` whose `Word` is not a speaker and not a close misspelling of one (`Interlude: Ysolde`, `Dawn: grey.`) is a caption: it compiles as narration with that WARN. A close misspelling (`Kerid:`) is an `unknown speaker` error. **A new character must be in `speakers.json` before their lines are written**, or their one-word lines compile as narration with a WARN.

So ordinary prose passes with no escapes and no warnings: `Then she said: go.`, `Mother said: run.`, `Asha's answer: nothing.`, `Asha laughed: once.`, `I knew it then: ...`, `The bell rang three times: once for...`, `Chapter 2: the raft.` (a lowercase word, a possessive, or digits before the colon). A spelled-out heading such as `Chapter Two: The Raft` gets the WARN; write `Chapter Two\: The Raft` or tag it `#narration` to silence it. `tools/tests/test_dlgc_narration_corpus.py` holds the prose lines (no errors, no warnings) and the caption lines (one WARN, no error). Options are never checked. Known limits, since there is no grammar: `Asha the girl: Hi.`, `Asha. Hi.` and `Asha - Hi.` compile as narration.

When a flagged line really is narration, write `\:` for the colon, or tag it **`#narration`**, which skips every near-miss check (and the warning) on that line and is not kept in the op's `tags`:

```
Low Tide: the harbour empties. #line:ch05_x_012 #narration
```

`#narration` on a speaker line or an option is an error.

### Tags with a meaning

| Tag | Meaning |
|---|---|
| `#sung` | A sung line. `DialogueBox` reveals it with **no blips and no lip-flap**, and gives the body label the theme type variation `DialogueBodySung` (UI styles it; until then it looks like a normal line). Pace it to the score with `@wait music=<marker>`. |
| `#notr` | Do not translate: the text stays as written in every locale. It **needs** a `#tn:"..."` note saying why. The line still goes to `dialogue.csv` (Godot needs a source string). |
| `#tn:"note"` | A translator note (any line or option, with or without `#notr`). Double quotes, `\"` inside. It is not a tag in the op. ` //` starts a comment even inside a note, so it cuts the note off; the compiler then reports `translator note cut off: " //" starts a comment...`. `//` with no space before it (`http://`) is fine. |
| `#long` | Silences the over-25-words warning for this line. |
| `#narration` | This narration only looks like a speaker line; skip the [near-miss checks](#near-miss-speaker-lines). Not kept in the op. Narration lines only. |
| `#vo` | Narration that is voice-over (checked by `test_dialogue_vs_scenes.gd`). |

`#notr` and `#tn` lines are written to **`game/data/dialogue/compiled/translator_notes.tsv`** (tab-separated, generated): `keys`, `scene`, `do_not_translate` (`yes` or empty), `note`, `en`. It is a `.tsv` so that Godot doesn't import it as a translation. Hand it to translators beside `dialogue.csv`, and keep a `#notr` key's translation identical to `en`.

```
Asha [tender]: Vey ennu, vey ennu, #line:ch03_verse_042 #sung #lamptongue #notr #tn:"Lamptongue: keep as written."
```

## Cues

```
@camera dock_wide blend=1.5
@anim asha look_at rhen
```

`@name positional... key=value...`. Arguments are split shell-style (`"two words"` is one argument). `true`/`false` become bools and numbers become numbers (they arrive at runtime as float, as JSON gives them). Positional arguments must come before `key=value` ones. The runner returns a cue as a `CUE` step **and** emits `cue_triggered(cue, args, kwargs)`; the cutscene sequencer consumes the same vocabulary.

**The vocabulary is data: [`game/data/dialogue/cues.json`](../../../game/data/dialogue/cues.json).** The compiler rejects an unknown cue, the wrong number of positional args, an unknown `key=`, or a value of the wrong type or outside its option set. The validator checks the file's own shape. To add a cue, key, or option value, add it to `cues.json` (Cinematics and Systems), then to this table. Arg types: `id` (letters, digits, `_`), `number`, `int`, `bool`, `string`, `emotion` (from `emotions.json`), and `enum` (inline `values`, or a named `set`). `min`/`max` bound numbers. `one_of` means exactly one of the named args/keys, and `requires` means a key needs another. `reserved` lists first-arg values that are commands rather than ids (`@music silence`, `@camera release`); one given as `{doc, kwargs}` allows only those keys. The `camera_eases` set mirrors the eases in `game/data/world/field_camera.json`, and the validator fails when they drift apart.

**The camera default differs between a shot and a release.** Without `blend=`, a shot *cuts*, but a release *blends*:

```
@camera H06                 # cut to H06
@camera H06 blend=1.5       # blend to H06 over 1.5 s
@camera release             # blend back to the field camera (the volume's own blend)
@camera release blend=0     # cut back
```

| Cue | Args (`[ ]` optional) | Keys | Meaning |
|---|---|---|---|
| `@camera` | `shot` | `blend=sec`, `ease=<camera_eases>`, `grade=<grades>` | Cut (`blend` 0 or none) or blend to an authored shot. `ease=` picks the blend curve (a `field_camera.json` ease; empty = the shot's own). `grade=` also blends the color grade to that color-script frame. **`release` is reserved**: `@camera release [blend=sec] [ease=]` is not a shot, it hands the camera back to the field volumes (`DialogueStep.is_camera_release()`; no `grade=`). Without `blend=` the hand-back *blends* with the volume's resolved blend; `blend=0` cuts. Never name a shot `release`. Contract: [field_camera.md](field_camera.md#scripted-shots-the-cutscene-contract-m1-arc-05). |
| `@anim` | `actor clip [target]` | `loop=bool` | Play a body animation, optionally aimed at a target (actor, mark, or prop) |
| `@mark` | `actor mark [walk\|run]` | | Move an actor to a scene mark |
| `@face` | `actor expression [sec]` | | Override the facial expression (an `emotions.json` id; otherwise from `[emotion]`) |
| `@fade` | `in\|out sec [color]` | | Screen fade |
| `@letterbox` | `on\|off` | | Cinematic bars |
| `@music` | `track` | `fade=sec` | Music change. **`silence` is reserved**: not a track, it fades the bed out to nothing over `fade=` (`DialogueStep.is_music_silence()`). Audio never names a track `silence`. |
| `@sfx` | `sound` | `vol=0..1`, `at=actor\|mark` | One-shot sound. `vol` is a linear gain (1.0 = as authored, the default); `at=` places it in the scene. |
| `@vfx` | `effect` (`<vfx_effects>`) | `at=`, `count=int≥1`, `drift=<vfx_drift>`, `motion=<vfx_motion>`, `rate=<vfx_rate>`, `form=id` | Trigger VFX |
| `@wait` | `[sec]` | `music=marker`, `max=sec` | Pause for `sec`, **or** until the music reaches `marker` ([contract below](#music-waits-wait-musicmarker)). Exactly one of `sec`/`music=`. `max=` (music waits only) is the sequencer's fallback timeout. |

Option sets (`sets` in `cues.json`):

| Set | Values | Notes |
|---|---|---|
| `grades` | `ch02`, `ch02_noon`, `ch02_night`, `ch03`, `ch03_causeway`, `ch03_boss, ch03_steps`, `ch03_shrine_int` | Color-script frames and the Haluna sub-frames ([`color_script.md`](../art/color_script.md), [`haluna.md`](../art/environments/haluna.md)). Also checks the `grade:` header. Add a frame when Art defines it. |
| `vfx_effects` | `glimmer_lift`, `glimmer_held`, `glimmer_bound` | Released, held, and bound light ([`glimmer.md`](glimmer.md)) |
| `vfx_drift` | `down_seaward` | Held light sinks and drifts toward the water |
| `vfx_motion` | `spiral_up` | Released light rises in a slow spiral |
| `vfx_rate` | `slow`, `normal`, `fast` | Emission or motion rate |

The light rules (released rises, held sinks, bound stays still) are checked per scene by `test_dialogue_vs_scenes.gd`, not by the compiler.

### Music waits (`@wait music=<marker>`)

```
@music hush_first_verse fade=0.5
Asha [tender]: Vey ennu, vey ennu, #line:ch03_verse_042 #sung ...
@wait music=verse_line_2 max=6.0
```

The contract between `DialogueRunner` and the cutscene sequencer:

1. `next()` returns the `@wait` as a `CUE` step with `is_music_wait()` true and `wait_marker = &"verse_line_2"`, and `cue_triggered` fires as for any cue.
2. Unless that marker was already reported since the last `@music` cue, the runner enters a wait (`is_waiting_for_marker()`, `waiting_marker()`) and emits `music_wait_requested(marker)`.
3. The sequencer reports each marker as the score passes it with `runner.music_marker_reached(marker)`. That releases a matching wait (it returns true and emits `music_wait_satisfied(marker)`) and records the marker, so a wait that comes after its marker doesn't block. Any `@music` cue forgets the recorded markers, and `start()` resets everything.
4. While a wait is on, the sequencer doesn't call `next()`. On a player skip, or when `max=` runs out, it calls `runner.release_wait()`.
5. A `next()` during a wait is a sequencer bug. The runner logs a warning, releases the wait, and carries on, so dialogue never hangs.

Marker names belong to the music cue's authored markers (Audio). The compiler checks only that they are ids.

## Commands

| Command | Meaning |
|---|---|
| `<<if expr>>` … `<<elseif expr>>` … `<<else>>` … `<<endif>>` | Branch. `<<elseif>>`/`<<else>>`/`<<endif>>` must align with their `<<if>>`. Branch bodies may sit at the same column or be indented. |
| `<<set $flag = expr>>` | Write a flag (through `Game.set_flag` in the game). |
| `<<jump node>>` | Continue at another node of this file. |
| `<<event name args...>>` | Emit `event_triggered(name, args)` and `EventBus.dialogue_event(name, args)`. Positional args only, typed like cue args. **`name` must be declared in [`game/data/dialogue/events.json`](../../../game/data/dialogue/events.json)**, and its args are checked against the row's `args` (same types as cues). Declared now: `zone_unlock zone` and `start_battle encounter`. A row with `test_only: true` (`fixture_event`) is allowed only under `game/data/dialogue/test/`. |
| `<<stop>>` | End the dialogue here. Reaching the end of a node also ends it. |

### Expressions

- Operands: `$flag`, numbers (`3`, `-1.5`), strings in double quotes (`"nested"`), `true`, `false`, and parentheses.
- Operators, loosest first: `or`, `and`, `not`, then one comparison `==`, `!=`, `<`, `>`, `<=`, `>=`.
- An unset flag reads as `false`. Numbers and bools compare numerically (`false` = 0), so `$count >= 3` works before `count` is ever set. Text compares with text. Mixed types are never equal, and ordering them is false (with a warning).
- Truthiness: `false`, `0`, `""` and null are false; everything else is true.

## Options

```
-> It was my father's. #line:ch02_beach_008
    <<set $ch02_rhen_named_lantern = true>>
    Asha [tender]: Then it's a good thing the sea gave you both back. #line:ch02_beach_009
-> Good trade. Don't ask what I gave for it. #line:ch02_beach_010 <<if not $ch02_met_asha>>
    Asha [soft_smile]: Then I won't ask. Not today. #line:ch02_beach_011
Rhen: (continues here after either option) #line:ch02_beach_012
```

- Consecutive `->` lines at the same column form one menu. Each needs `#line:<id>`; the option text goes to `dialogue.csv` like any line.
- The option's body is the following lines indented deeper than the `->`. Bodies may contain anything, including nested option menus and if blocks. After a body, play continues after the whole menu.
- `<<if expr>>` at the end of an option line (before or after the `#line` tag) hides that option when false. If no option is available, the menu is skipped.

## Indentation rules

- Spaces only; a tab in the indentation is an error.
- A node's first line is not indented. Every statement in a block sits at the block's column.
- Deeper indentation is allowed only right after an `->` option (its body) or an `<<if>>`/`<<elseif>>`/`<<else>>` (the branch body). Dedenting must land on a column an enclosing block uses.

## Line ids (`dlgc --assign-ids`)

```
python3 tools/dlgc.py --assign-ids game/data/dialogue/ch02/ch02_girl_on_the_beach.dlg [--prefix ch02_beach]
```

This fills in every spoken line and option that lacks a `#line:` id, **rewriting the file in place**, and then you run `python3 tools/dlgc.py` as usual.

- **Prefix:** `--prefix`, or else the most common `<prefix>` among the file's `<prefix>_<NNN>` ids (the first one seen wins a tie), or else the scene name's first and last words (`ch02_girl_on_the_beach` → `ch02_beach`; a one- or two-word name as is). In that last case it prints a `NOTE` suggesting `--prefix <chapter>_<scene-short>`, since the guess (`ch09_review_scene` → `ch09_scene`) may not be the short name you want.
- **Counter:** it continues from the highest number that prefix uses **anywhere in the project**, in file order, zero-padded to 3 digits (or wider, if the prefix already is). It skips any id already in use. Existing ids are **never** renumbered or moved, so gaps stay gaps.
- **Placement:** ` #line:<id>` goes after the line's text and tags (after an option's `<<if>>`), before any `// comment`.
- It is deterministic, and a second run changes nothing. Any other compile error in the project (an unknown speaker, say) aborts it without touching the file.

## Errors the compiler reports (`path:line: message`)

Missing `#line` on spoken text or an option; a [near-miss speaker line](#near-miss-speaker-lines), or `#narration` on a speaker line or option; duplicate line ids (with the first location); unknown speaker, emotion, or narrator identity; an alias whose key clashes; `#notr` without `#tn`, or a malformed or empty note (or one cut off by ` //`); unknown cue, a wrong arg count, an unknown `key=`, or a value outside its type or option set (`cues.json`); an unknown `grade:` header; an unknown event or wrong event args (`events.json`); unknown jump target; unbalanced `<<if>>` (missing `<<endif>>`, stray `<<else>>`/`<<endif>>`, `<<else>>` twice, misaligned keywords); bad indentation; tabs; unknown commands; malformed expressions; a node missing `===`; a first title that doesn't match the file name; duplicate node titles or scene names.

**Warnings** (`WARN path:line: ...`, never fatal; also shown by `validate_data.py`): a line or option over 25 words without `#long`; narration whose prefix before `:` reads like a name but names no speaker, such as a caption ([near miss](#near-miss-speaker-lines)).

## Compiled JSON (format 1)

`{"format": 1, "scene", "source", "start", "nodes": {title: {"headers", "ops": [...]}}}` with one op per line. Ops: `line` (`id`, `key`, `speaker`, `emotion`, `voice`, `name_key?` alias, `narrator?` voice identity, `tags?`), `cue` (`cue`, `args`, `kwargs`), `set` (`flag`, `value` expr), `if_not` (`cond`, `to`), `goto` (`to`), `options` (`choices: [{id, key, to, cond?, tags?}]`, `next`), `jump` (`node`), `event` (`name`, `args`), `stop`. Expressions are prefix arrays: `["lit", v]`, `["flag", name]`, `["not", e]`, `["and"|"or"|"=="|…, a, b]`. Every op carries `src`, its `.dlg` line number. `voice` is reserved (ADR 0004) and empty for now. The optional fields are written only when present, so scenes that don't use the M1-NAR-04 features compile byte-for-byte as before, and the format number stays 1.

## Runtime

- **`DialogueRunner`** (`game/narrative/dialogue_runner.gd`, RefCounted, headless): `load_scene(id)`, `start(node = first)`, `next() -> DialogueStep`, `choose(index)`. Signals: `cue_triggered`, `event_triggered`, `node_started`, `finished`. Flags go through a `DialogueFlagAccess`: `GameFlagAccess` (the Game autoload) by default; tests pass the in-memory base class.
- **`DialogueStep`**: `kind` (`LINE`, `CUE`, `OPTIONS`, `END`), `text_key`, `speaker`, `emotion`, `voice`, `name_key` (alias, or empty), `narrator` (narration's voice identity, or empty), `tags`, `cue`/`args`/`kwargs`, `wait_marker`, `options: Array[DialogueOption]` (`index`, `text_key`). Helpers: `is_sung()`, `is_do_not_translate()`, `is_music_wait()`, `is_music_silence()`. Text is never resolved in the runner; the UI calls `tr(text_key)`.
- **Music waits:** `music_wait_requested`/`music_wait_satisfied` signals, plus `is_waiting_for_marker()`, `waiting_marker()`, `music_marker_reached(marker)`, and `release_wait()` ([contract](#music-waits-wait-musicmarker)).
- **`DialogueBox`** (`game/ui/dialogue/dialogue_box.tscn`): `show_line(step)` (or `show_text(speaker, text_key, display_name_key = &"", sung = false, narrator = &"")`). The name shows `tr(step.name_key)` when the line has an alias. `#sung` lines reveal with no blips and no `mouth_flap`, in the `DialogueBodySung` style. Typewriter reveal at `DialogueTextSettings.chars_per_sec` (defaults and allowed range in `game/data/dialogue/text_box.json`; the settings menu calls `set_chars_per_sec`), a `text_blip.ogg` blip every `blip_every_n_chars` with `blip_pitch` from `speakers.json`, `skip_reveal()` on accept, `advance_requested` once the line is shown, and `mouth_flap(speaker, open)` for each revealed vowel (open) and the next non-vowel (close), for Cinematics' procedural lip-flap.
- `speakers.json` rows: `id`, `name_key` (loc), `blip_pitch` (pitch scale, 1.0 = as recorded), `portrait_id` (placeholder until Character Art ships portraits; deliberately not a `*_key`, since it isn't a loc key).
