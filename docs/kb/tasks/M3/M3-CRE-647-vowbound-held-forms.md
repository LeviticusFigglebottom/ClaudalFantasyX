---
id: M3-CRE-647
title: "The six Vowbound as foes for their Ch20 release fights: held material sets, a release clip each, held battle scenes"
role: character
status: blocked
blocked-by: ADR 0041
owner_session: "creatures (worktree agent)"
reviewer: art
depends_on: [M3-CRE-646]
milestone: M3
request-from: creatures
---
## Goal
act3_roster.md "The Vowbound as foes" (M3-CRE-646). Ilun, Kahre, Virel, Hesk, Nhoa and Ethren are fought and released
in Ch20, one per layer (act_outline.md; vowbound.md "The final fight"). Each keeps one GLB; the foe form gets:
- a **held** material set: `glimmer_held` in place of `glimmer_bound`, otherwise the same, written by
  `common/write_materials.py` from a `held` block in the creature's materials.json into `materials_held/`;
- a **`release`** clip: the form's last unfurling, the light lifting off;
- its own battle scene `game/creatures/<id>/<id>_held_battle.tscn` and creatures.json row `<id>_held`, whose
  `phases` include the release (the material swap back to `glimmer_lift`-tinted light is presentation; motes are VFX).

## Acceptance criteria
- [x] The six held scenes load headless with their clips, including `release`; the ally scenes and GLBs are unchanged
  except for the added clip.
- [x] Every existing creature job verifies identical (the write_materials.py change must not change any other output).
- [x] The validator accepts the `_held` rows (not Vowbound rows; no enemies.json row yet, Combat's).

## Notes (as built, 2026-10-28)
- **Materials:** `write_materials.py` reads an optional `held` block (`emission_from` `#4FB3B0`, `emission_to`
  `#7FC6D9`, `_doc`) and writes `materials_held/<slot>.tres`.
  - Every emissive slot must be `emission_from` and must not pulse. It gets `emission_to` at the same energy. The
    other slots are copied.
  - Without the block, the output is the same as before.
  - The six jobs list `materials_held/*.tres` as an output. 37 PROVENANCE rows are in their own commit.
- **The held-material mechanism:** `CreatureActor.material_dir` (an `@export_dir`) is set in the held scene.
  - In `_ready`, each surface whose current material's `resource_name` is `<slot>` gets `<material_dir>/<slot>.tres`.
    This is the post-import's own slot mapping.
  - The import can't do it: one GLB has one import, and the post-import already bakes `materials/` onto it.
  - Documented in pipeline.md §5.
- **`release` clips:** Ilun 3.3 s; Kahre, Virel, Hesk and Nhoa 3.4 s; Ethren 3.5 s. Each one opens, holds, then lifts
  the root about 1.5 m up and 0.5 m back (−z, away from the party) and ends open, not collapsed. Each sheet's "As
  built: the held form" says what each clip does. The other clips sample identically (0 m skinned difference).
- **Rows** `<id>_held` (no `vowbound` key):
  - `ko` is `release`.
  - `phases.release` is `{"clip": "release", "hold": true}`.
  - `stand_in.yaw_deg` is 90, and the ally's height and radius are kept.
  - `contact` is the ally's.
- **New phase key `hold`** (CreatureActor and validate_creatures.py, with tests):
  - the actor stays on the clip's last frame instead of idling;
  - `settle()` jumps there;
  - a KO whose clip is the held one doesn't replay it.
- **Shots:** six `creature_<id>_held` entries (shots.json, append-only) and stage scenes, plus `<id>_held` rows in the
  portrait manifest, the way earlier Vowbound tasks did. Not rendered.
- **Tests:**
  - `tests/unit/test_creature_vowbound_held.gd`, new;
  - `release` added to each Vowbound test's CLIPS list. Hesk's planted-talon check skips the release, where she lifts
    off by design;
  - tools/tests/test_creatures.py: the held block, the held rows and `hold`. The pipeline tests now walk only rows that
    own a model, so a `_held` row shares its GLB and job.

## Requests
- **Combat / chapter designer:** the Ch20 enemies.json rows with `model` = `res://game/creatures/<id>/<id>_held_battle.tscn`,
  a phase `release` if it should be reachable as a phase (the KO already plays it), and skill ids for `clip_by_skill`.
- **Battle VFX / presentation:** at the release, the 1.5 s hue lerp from glimmer_held to glimmer_lift on the model
  (color_script rule 1) and the rising motes.
- **PC:** render `creature_<id>_held` ×6 and the six `_held` portraits.

## Review log
- 2026-10-28, creatures: **paused by ADR 0041** (Act I at final quality first; the human's directive). The work done so far is merged on claude/creatures as is; nothing reverted. Resume when a new ADR lifts the pause.
