# `.dlg` Dialogue Format Reference

The decision and rationale are in [ADR 0004](../decisions/0004-dialogue-format.md). This page is the complete syntax reference. It grows with the cue vocabulary as Cinematics adds cues.

**Pipeline:** `game/data/dialogue/<chapter>/<scene>.dlg` → `python3 tools/dlgc.py` → `game/data/dialogue/compiled/<scene>.json` + `game/data/loc/dialogue.csv` → `DialogueRunner` (`game/narrative/`) → `DialogueBox` (`game/ui/dialogue/`).

## How to add a scene

1. Create `game/data/dialogue/<chapter>/<scene>.dlg`, e.g. `ch02/ch02_girl_on_the_beach.dlg`. The **first node's `title:` must equal the file name** (without `.dlg`), and scene names are unique across all chapters (compiled output is flat).
2. Write it (syntax below). Give every spoken line and every option a unique `#line:<id>`. Convention: `<chapter>_<scene-short>_<NNN>`, e.g. `#line:ch02_beach_004`.
3. Declare every `$flag` you use in `game/data/flags.tres` (snake_case key, one-sentence description; keep the dict JSON-compatible).
4. New speaker? Add a row to `game/data/dialogue/speakers.json` and its `name_key` to `game/data/loc/strings.csv`.
5. Run `python3 tools/dlgc.py`. Fix any `file:line:` errors it prints.
6. Run `python3 tools/validate_data.py` (it fails if compiled outputs are stale). Commit the `.dlg`, the compiled JSON, and `dialogue.csv` **together**.
7. Run `godot --headless --path . --import` once if `dialogue.csv` is new, so Godot regenerates `dialogue.en.translation`.
8. Play it: `var r := DialogueRunner.new(); r.load_scene(&"<scene>"); r.start()`, then feed `r.next()` steps to a `DialogueBox`.

Never edit `compiled/*.json` or `dialogue.csv` by hand; they are regenerated. `python3 tools/dlgc.py --check` (also run by the validator and CI) fails if they are out of date.

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

- Headers are `key: value` lines before `---`. `title` is required; others are passed through as `headers`.
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
- A line **without** `Speaker:` is narration (Rhen's older voice-over, captions).
- **Every line needs `#line:<id>`**: lowercase letters, digits, and `_`, unique across the whole project. The loc key is `DLG_<ID>` upper-cased (`DLG_CH02_BEACH_002`).
- Other trailing `#tags` (e.g. `#whisper`) are kept in a `tags` list for the UI or Cinematics.
- Escapes: `\:` for a colon right after a narration line's first word (otherwise `Dawn: grey.` reads as speaker "Dawn"), and `\#` for a literal `#` at the end of a line.
- One line of text per line; there are no multi-line strings. Keep to the voice guide's length rules.

## Cues

```
@camera dock_wide blend=1.5
@anim asha look_at rhen
```

`@name positional... key=value...`. Arguments are split shell-style (`"two words"` is one argument). `true`/`false` become bools and numbers become numbers (they arrive at runtime as float, as JSON gives them). Positional arguments must come before `key=value` ones. The runner returns a cue as a `CUE` step **and** emits `cue_triggered(cue, args, kwargs)`; the cutscene sequencer consumes the same vocabulary.

| Cue | Args | Meaning |
|---|---|---|
| `@camera` | `shot_id [blend=sec]` | Cut or blend to an authored shot |
| `@anim` | `actor clip [loop]` | Play a body animation |
| `@mark` | `actor mark_id [walk|run]` | Move an actor to a scene mark |
| `@face` | `actor expression [sec]` | Override the facial expression (otherwise from `[emotion]`) |
| `@fade` | `in|out sec [color]` | Screen fade |
| `@letterbox` | `on|off` | Cinematic bars |
| `@music` | `cue_id [fade=sec]` | Music change |
| `@vfx` | `effect_id at=actor|mark` | Trigger VFX |
| `@wait` | `sec` | Pause the sequence |

The compiler accepts any lowercase cue name; add new ones to this table when Cinematics implements them.

## Commands

| Command | Meaning |
|---|---|
| `<<if expr>>` … `<<elseif expr>>` … `<<else>>` … `<<endif>>` | Branch. `<<elseif>>`/`<<else>>`/`<<endif>>` must align with their `<<if>>`. Branch bodies may sit at the same column or be indented. |
| `<<set $flag = expr>>` | Write a flag (through `Game.set_flag` in the game). |
| `<<jump node>>` | Continue at another node of this file. |
| `<<event name args...>>` | Emit `event_triggered(name, args)` and `EventBus.dialogue_event(name, args)`. Positional args only, typed like cue args. |
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

## Errors the compiler reports (`path:line: message`)

Missing `#line` on spoken text or an option; duplicate line ids (with the first location); unknown speaker or emotion; unknown jump target; unbalanced `<<if>>` (missing `<<endif>>`, stray `<<else>>`/`<<endif>>`, `<<else>>` twice, misaligned keywords); bad indentation; tabs; unknown commands; malformed expressions; a node missing `===`; a first title that doesn't match the file name; duplicate node titles or scene names.

## Compiled JSON (format 1)

`{"format": 1, "scene", "source", "start", "nodes": {title: {"headers", "ops": [...]}}}` with one op per line. Ops: `line` (`id`, `key`, `speaker`, `emotion`, `voice`, `tags?`), `cue` (`cue`, `args`, `kwargs`), `set` (`flag`, `value` expr), `if_not` (`cond`, `to`), `goto` (`to`), `options` (`choices: [{id, key, to, cond?, tags?}]`, `next`), `jump` (`node`), `event` (`name`, `args`), `stop`. Expressions are prefix arrays: `["lit", v]`, `["flag", name]`, `["not", e]`, `["and"|"or"|"=="|…, a, b]`. Every op carries `src`, its `.dlg` line number. `voice` is reserved (ADR 0004) and empty for now.

## Runtime

- **`DialogueRunner`** (`game/narrative/dialogue_runner.gd`, RefCounted, headless): `load_scene(id)`, `start(node = first)`, `next() -> DialogueStep`, `choose(index)`. Signals: `cue_triggered`, `event_triggered`, `node_started`, `finished`. Flags go through a `DialogueFlagAccess`: `GameFlagAccess` (the Game autoload) by default; tests pass the in-memory base class.
- **`DialogueStep`**: `kind` (`LINE`, `CUE`, `OPTIONS`, `END`), `text_key`, `speaker`, `emotion`, `voice`, `tags`, `cue`/`args`/`kwargs`, `options: Array[DialogueOption]` (`index`, `text_key`). Text is never resolved in the runner; the UI calls `tr(text_key)`.
- **`DialogueBox`** (`game/ui/dialogue/dialogue_box.tscn`): `show_line(step)`, typewriter reveal at `DialogueTextSettings.chars_per_sec` (defaults and allowed range in `game/data/dialogue/text_box.json`; the settings menu calls `set_chars_per_sec`), a `text_blip.ogg` blip every `blip_every_n_chars` with `blip_pitch` from `speakers.json`, `skip_reveal()` on accept, `advance_requested` once the line is shown, and `mouth_flap(speaker, open)` for each revealed vowel (open) and the next non-vowel (close), for Cinematics' procedural lip-flap.
- `speakers.json` rows: `id`, `name_key` (loc), `blip_pitch` (pitch scale, 1.0 = as recorded), `portrait_id` (placeholder until Character Art ships portraits; deliberately not a `*_key`, since it isn't a loc key).
