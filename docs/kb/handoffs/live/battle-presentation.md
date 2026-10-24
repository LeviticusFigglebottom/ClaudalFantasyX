# Live log: battle-presentation environment

**Session:** `session_014EcW9e5tEmjDi5S2HmCECd` (cloud) · **Branch:** `claude/battle-presentation` (from `claude/undertow-lead-handoff-423ixt` 499f074) · **Role:** combat · **Lead:** `session_019iimsngAgPLEram1wcbLpE`

The gap (the human's playtest note): battles had no action animation. This track adds a listen-only presentation layer: choreography, a clip contract, a camera director, the specials, the intro and outro. Docs: `docs/kb/tech/battle_presentation.md`.

## Queue (tasks M2-BPR-01..06, all claimed on this branch, role combat)
| Task | State |
|---|---|
| M2-BPR-01 BattleChoreo sequencer | **core pushed (0cfa455)**: beats from `game/data/battle/choreo.json`, floats and hit VFX land on contact, KO collapse, swap walk-in; the controller hand-off waits `BattleStage.hold_after` (in place; battle_controller.gd still 995 lines). 20 new tests; all 412 battle tests pass. |
| M2-BPR-02 clip contract | names in battle_presentation.md § Clip contract and `BattleClips`; requests sent to characters and creatures |
| M2-BPR-03 camera director, speed/skip settings | worktree agent running |
| M2-BPR-04 specials (Swell finishers, Drownbell, Vowbound) | next, on BPR-01/03 |
| M2-BPR-05 intro stinger, banner timing, victory pose | stinger + banner: worktree agent running; victory pose after BPR-01 |
| M2-BPR-06 freeze-frame shots | next |

## For other tracks
- **PC GPU (battle VFX owner):** `BattleVfx.attach` now connects to `BattleChoreo.contact` when the stage has a sequencer (one `if`), so hit effects land on the blow, not at resolve. With pacing 0 it fires synchronously as before. BattleBossVfx is unchanged for now (BPR-04 will coordinate the toll beats).
- **creatures:** BattleActorMotion plays action clips at resolve time; once both merge, the sequencer should own *when* (strike/contact beats). Proposal in battle_presentation.md § Clip contract: in-place clips named by the contract, `clip_by_kind` mapping onto them.
- **characters:** hero battle actors: in-place clips named `idle, ready, attack, cast, item, read, defend, finisher, hit, dodge, ko, victory`; a strike clip's contact frame at `contact_at` of its length (choreo.json per style).

## Exact next step
Merge the camera and stinger worktree branches when they report, then BPR-04 specials and BPR-06 shots; then merge the latest integration branch and run the full `tools/ci_local.sh`.

## Log
- 2026-10-24: branch created and pushed; tasks claimed (b-claim commit). BattleChoreo core pushed (0cfa455). Two worktree agents running (BPR-05 stinger/banner, BPR-03 camera).
