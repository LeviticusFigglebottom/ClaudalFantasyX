# Live log: battle-presentation environment

**Session:** `session_014EcW9e5tEmjDi5S2HmCECd` (cloud) · **Branch:** `claude/battle-presentation` (from `claude/undertow-lead-handoff-423ixt` 499f074) · **Role:** combat · **Lead:** `session_019iimsngAgPLEram1wcbLpE`

The gap (the human's playtest note): battles had no action animation. This track adds a listen-only presentation layer: choreography, a clip contract, a camera director, the specials, the intro and outro. Docs: `docs/kb/tech/battle_presentation.md`.

## Queue (tasks M2-BPR-01..06, all claimed on this branch, role combat)
| Task | State |
|---|---|
| M2-BPR-01 BattleChoreo sequencer | **core pushed (0cfa455)**: beats from `game/data/battle/choreo.json`, floats and hit VFX land on contact, KO collapse, swap walk-in; the controller hand-off waits `BattleStage.hold_after` (in place; battle_controller.gd still 995 lines). 20 new tests; all 412 battle tests pass. |
| M2-BPR-02 clip contract | names in battle_presentation.md § Clip contract and `BattleClips`; requests sent to characters and creatures |
| M2-BPR-03 camera director, speed/skip settings | worktree agent running |
| M2-BPR-04 specials (Swell finishers, Drownbell, Vowbound) | worktree agent running |
| M2-BPR-05 intro stinger, banner timing, victory pose | **review** (04417ea stinger "tide line" + banner waits for the router fade; 4e052f8 BattleOutro victory hops / escape walk-off) |
| M2-BPR-06 freeze-frame shots | capture states + fixtures pushed (choreo_melee/hit/cast/support/read/ko/swap); shots.json entries and baselines land after the camera merge (the camera reframes them) |

## For other tracks
- **PC GPU (battle VFX owner):** `BattleVfx.attach` now connects to `BattleChoreo.contact` when the stage has a sequencer (one `if`), so hit effects land on the blow, not at resolve. With pacing 0 it fires synchronously as before. BattleBossVfx is unchanged for now (BPR-04 will coordinate the toll beats).
- **creatures:** BattleActorMotion plays action clips at resolve time; once both merge, the sequencer should own *when* (strike/contact beats). Proposal in battle_presentation.md § Clip contract: in-place clips named by the contract, `clip_by_kind` mapping onto them.
- **characters:** hero battle actors: in-place clips named `idle, ready, attack, cast, item, read, defend, finisher, hit, dodge, ko, victory`; a strike clip's contact frame at `contact_at` of its length (choreo.json per style).

## Pillar-4 fixes found in the freeze-frames
- While an action plays the order has already moved on: the timeline head now reads **"Next"** (not "Acting now") and the help line names the action ("Rhen: Attack") until the sequence ends.
- The Read panel opens on the Read's contact beat, not before the reader moves.

## Exact next step
Merge the camera and stinger worktree branches when they report, then BPR-04 specials and BPR-06 shots; then merge the latest integration branch and run the full `tools/ci_local.sh`.

## Log
- 2026-10-24: merged the stinger agent (04417ea); freeze-frame capture states (b6..); BattleOutro (4e052f8). Specials agent spawned. **Two queue items remain after camera + specials: BPR-06 baselines and the pre-merge full gate.**
- 2026-10-24: branch created and pushed; tasks claimed (b-claim commit). BattleChoreo core pushed (0cfa455). Two worktree agents running (BPR-05 stinger/banner, BPR-03 camera).
