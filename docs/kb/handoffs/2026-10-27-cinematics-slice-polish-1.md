# Handoff: cinematics (slice-polish), 2026-10-27, #1

Session `session_01KZCgTqxhHKjvMCm1dAosvZ`, branch `claude/m2-slice` (the slice-polish half of the old m2-slice
track; act1-chapters owns Ch4+). Live log: `docs/kb/handoffs/live/slice-polish.md`.

## Done (all pushed; MERGE-READY lines in the live log)
- **Merges:**
  - the integration branch (twice; the second after big9 and big10);
  - `lead/gate-big9` early, for the hero-integration sequencer patch.
- **Playtest fixes (FAST-TRACK):**

| Task | What |
|---|---|
| M2-FP-102 | HeroMotion patch applied (cutscenes drive the hero bodies; walk speed to the gait blend; idle micro-motion; walk_mps 1.0); eased fades and letterbox; Haluna's ten villagers as FieldNpcs with their actors; wildlife in Haluna and the causeway (creatures' commits cherry-picked); the frame viewer `tools/cutscene_frames` |
| M2-FP-103 | The prologue restaged per act_outline (real Rhen, Asha and Toma, Ysolde's model, P02 two-shot, `@light` lantern, glimmer); held poses (`hold_clips`) and clip stand-ins (`clip_stand_ins`); Asha kneels in Cutscene A, Rhen half risen; H06 reframed while Rhen's lying clip is requested |
| M2-FP-104 | Held cutscene shots breathe (`CutsceneCameraBreath`) |
| M2-FP-105 | The tideline (the M2 route's first battle) teaches the timeline and the commands |
| M2-FP-106 | A villager who speaks in a scene turns to Rhen and talks (`CutsceneNpcTalk`) |
| M2-FP-107 | Barks freeze Rhen without hiding the party (`freeze_player`) |
| M2-FP-108 | B06 on env-art's final Saltgrass Causeway (GreyboxZone `dressing`; `tools/causeway/build_causeway_gameplay.py`) |
| M2-FP-109 | Six `slice_*` shots in shots.json via the `SliceCutsceneShot` rig, for the PC to render |
| M2-FP-110 | B05 at the causeway head keeps Asha and Toma in view; their lines play on the followers |
| M3-ARC-04 | The shrine's shaft lamps stop lighting ShaftFog |

- **Requests filed:**
  - M2-CHR-100: the shopkeeper, smith and innkeeper models;
  - M2-RND-100: causeway prewarm, for the PC;
  - Rhen's `lie_in_shallows` (requested_clips.json).

## In progress / waiting
- **RENDER-REQUEST @ e1e63f43**, plus the shrine re-render request after 44a7d65c (live log "Render requests").
  The six `slice_*` shots have no baseline yet, so `test_screenshots::test_repo_manifest_is_valid_and_baselined`
  is red on this branch until I approve the PC's renders.

## Exact next step
1. When the PC posts `RENDERED @ ...: gpu/render-slice-polish-<sha7>`:
   - `git fetch` that branch and VIEW every out and diff PNG;
   - fix what reads grey or flat;
   - copy the approved outs into `tests/screenshots/baselines/` with the llvmpipe metadata
     (TRACK-RULES "RENDERING GOES TO THE PC");
   - commit `M2-FP-109: approve ...`.

   That turns the tools test green.
2. Ch1 to slice quality: put the Oruvel zones on their kits through act1-chapters' KitCollision (ADR 0200,
   `game/levels/act1/kit_collision.gd`) once it reaches the integration branch. Don't build a parallel mechanism.
   The kit previews and swap-in note are in `game/levels/_tests/oruvel_kit/README.md` and M3-ENV-07.
3. When Character builds Rhen's `lie_in_shallows`, `sit`, `trim_wicks` and `sit_steps`: drop the stand-ins in
   `sequencer.json` `clip_stand_ins`, put H06 back toward haluna.md's lying framing, and add `@anim rhen sit` /
   `trim_wicks` to the prologue.

## Known issues
- `cutscene_sequencer.gd` is at about 975 of gdlint's 1000 lines, and `shell_shrine_level.gd` at exactly 1000. Put new
  logic in helpers (CutsceneClips, CutsceneNpcTalk and CutsceneCameraBreath are the pattern).
- The causeway's first visible frame took 1.7 s on lavapipe (M2-RND-100).
- Never `await` real frames inside a Haluna test: a zone outlived one and broke later tests. Step the party by hand.

## Files touched (main)
- `game/cutscene/*`
- `game/flow/haluna_story.gd`
- `game/levels/ch02/haluna/{haluna_zone,haluna_villagers,haluna_actor_pose}.gd`
- `game/levels/prologue/*`
- `game/levels/ch03/{saltgrass_causeway,shell_shrine}/*`
- `game/world/zone/greybox_zone.gd`
- `game/data/cutscene/sequencer.json`, `game/data/dialogue/*`, `game/data/flow/haluna_villagers.json`
- `game/levels/_tests/slice_shots/*`, `tests/screenshots/shots.json`
- `tools/cutscene_frames/*`, `tools/causeway/*`
- tests: `test_haluna_villagers`, `test_cutscene_pose`, `test_cutscene_camera_breath`, `test_fp_prologue`,
  `test_causeway_route`, `test_slice_first_battle`, `test_slice_shots`, `test_causeway_gameplay`
