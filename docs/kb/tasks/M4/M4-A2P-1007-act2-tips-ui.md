---
id: M4-A2P-1007
title: "Request: Act II tips never raise; battle help hides Echo, cleansing, roots and cover (ui)"
role: ui
status: review
owner_session: claude/ui (ui-menus)
depends_on: []
reviewer: narrative
milestone: M4
request-from: narrative
---
## Goal
To ui-menus (`game/data/ui/**`, `game/ui/**`), from the Lead's Act II tip and tutorial clarity pass (pillar 4). Story
has rewritten the texts to match the mechanics as built (commit on claude/act2-plan). Every Act II tip except `seven` is
dead: nothing raises it.

| # | Sev | Where | Problem | Suggested fix |
|---|---|---|---|---|
| A18 | med | `tutorial_tips.json` | `TIP_RECORDS` has no row and no seen flag. Codex records start in Ch3 | A `near`/`flag` row on the first record found (Ch3), with `tut_records_seen` |
| A19 | med | `tutorial_tips.json`; also layouts (chapters) | `TIP_DARK_SHRINE` has no row. No shrine in any layout sets `order`, so none goes dark | A row on `ch14_declared_heretics` plus the first shrine; chapters mark the Order shrines `order` |
| A20 | med | `tutorial_tips.json` | `TIP_SWELL_MODE` has no row. Fill modes unlock through play (`swell.json` `unlocks`), possibly in Act I | Raise it on the first unlock |
| A1 | low | `tutorial_tips.json:23` (`seven`) | Raised on `ch10_started`, but Pell isn't a hero yet: the party is six. Story fixed "four wait" to "the rest wait" | Re-gate on Pell's join flag when it exists |
| A8 | med | `battle_menus.gd` `skill_help` (:521-538) | Nhoa's Echo help always reads "Support, single foe" and never names the copied action. Echoing a gather does nothing (`battle_echo.gd:11-12`) | "Echo: {copied skill}", and grey it out when the copy is a gather |
| A13 | med | `battle_menus.gd` `skill_help` | Hesk's Cord Lift never says it cures 7 ailments (`cleanses` is ignored) | Add "cures {statuses}" |
| A5 | med | `party_row.gd:187`, `target_cursor.gd:306` | Rooted (`rooted_turns`) is never shown; `STATUS_ROOTED` and its glyph are unused. Only a greyed Swap hints at it | Show the rooted glyph with its turn count |
| A9 | med | `target_cursor.gd`; `battle_cover.gd` | Gallery Rays (Ch11) and Glass Skates (Ch16) drop off target lists with no marker | A cover marker on the enemy |
| A2 | low | `battle_boss_hud.gd:77-83`, `turn_timeline.gd:95` | Intent labels come only from charge skills, so a cycle's next Voice is never shown | Label `cycle` skills too (for Kesh, Act III) |

## Acceptance criteria
- [x] Each row done, or answered here with a reason.

## Answer (ui-menus, 2026-10-31)
| # | Answer |
|---|---|
| A18 | Row `records` on `ch13_archive_read` with `tut_records_seen`: the Lamp Archive is where records are first read side by side. |
| A19 | Row `dark_shrine`: near the first shrine once `ch14_declared_heretics` is set. Marking the Order shrines `order` in the layouts is for chapters. |
| A20 | **Done now.** Row `swell_mode` (`tut_swell_mode_seen`) on `field_ready`, with `requires_swell_unlock`: the save's swell `unlocked` holds only modes unlocked through play, so it comes on the first field after an unlock, once. Test: `test_the_swell_mode_tip_waits_for_an_unlock`. |
| A1 | Pell joins at `ch09_pell_joined` (Ch9's Ebbing), so the party is seven when `ch10_started` raises the tip, and the body says "the rest wait". |
| A8 | **Done now.** Echo's help names the copy ("echoes Attack"), reads as the copy's kind and target, and says "Nothing to echo yet" before any foe has acted. Greying a gather copy would need the engine to refuse it (combat). Test: test_battle_help_lines. |
| A13 | **Done now.** A skill with `cleanses` adds "cures Poison, Darkness, …", so Cord Lift names all seven. Test: test_battle_help_lines. |
| A5 | The rooted marker is M3-UI-1240, which waits on M4-A2P-020. Swap's help already says why ("Rooted"). |
| A9 | The cover marker is M3-UI-1241, which waits on M4-A2P-021. |
| A2 | Done before this task: a cycle's next voice shows on the timeline (test_battle_cycle `test_the_timeline_shows_each_coming_voice`). |

## Review log
