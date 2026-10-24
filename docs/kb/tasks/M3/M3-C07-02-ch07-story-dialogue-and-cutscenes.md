---
id: M3-C07-02
title: Ch7 "The Tidecup" story dialogue, cutscenes and flow around the Reefball match
role: cinematics
status: review
owner_session: "m2-slice subagent (C07 story build)"
depends_on: [M3-C07-01, M3-ARC-01]
reviewer: narrative
milestone: M3
request-from: lead
---
## Goal
Lead 2026-10-24 12:00 (the human authorised M3 in parallel; m2-slice owns Act I gameplay and narrative). This is the half of M3-C07-01 that wasn't built. Write Ch7's `.dlg` scripts, cutscenes, flags and chapter flow from `docs/kb/story/beats/act1_ch07.md` (Tamsule port and the Bell). It wraps the Reefball match that the separate Reefball Lead agent owns, at the hand-off in its §5:
- B05 ends on `<<event start_reefball ch07_tidecup_oruvel_sorrin>>`;
- the match returns `ch07_tidecup_played` and, on a win, `ch07_tidecup_won` (a reward only);
- B07 resumes the same either way.

## Acceptance criteria
- [x] The `.dlg` scripts and cutscenes for every story beat, with the flags declared, and `validate_data` and `dlgc --check` clean.
- [x] The chapter flow in `game/data/flow/chapters/ch07.json`. Until the Reefball scene exists, a stand-in step sets `ch07_tidecup_played`.
- [x] A test that no story `.dlg` reads `ch07_tidecup_won` except where the reward is given.
- [x] A headless thread test, port arrival to the Ch8 hand-off, with the stand-in match.

## Notes
- 2026-10-24, the Lead: the Reefball rules engine is M3-RBL-01 (`docs/kb/design/reefball.md`). The story match is `tidecup_opening`: Oruvel (captain Tavi Orse; Rhen dives) against a provisional "Pemakar Terraces", with Oruvel's divers provisionally "Noa" and "Old Ama".
  - **Reconcile those loc rows with act1_ch07.md:** the opponent is the atoll side **Sorrin** (not Tamsule, which wins offscreen), and Rhen takes Pio's place.
  - **Renaming** the loc rows is allowed (the Lead said so).
  - **The outcome is a reward only** (ADR 0020 (h)).
  - **To do here:** the naming-rite cutscene, the match entry and exit flow through SceneRouter/FlowRouting, and the post-match beats.
  - **Not ours:** the match HUD is UI's, and the arena (the water sphere) is env-art's and the PC's.

- 2026-10-24, the m2-slice subagent (C07 story build): **built; review: narrative.** The details are below.
  - **What's built:**
    - 18 scripts in `game/data/dialogue/ch07/` (B01–B05, B07–B10 and the match barks);
    - the flow in `game/data/flow/chapters/ch07.json`;
    - two greybox zones under `game/levels/ch07/` (`Ch07Zone`);
    - `game/data/loc/ch07.csv`, registered in `project.godot`;
    - the test `tests/integration/test_ch07_thread.gd`;
    - `docs/kb/tech/chapter_flow.md` "Ch7", and a PLAYTEST section.
  - **THE REEFBALL SEAM** (for the Reefball agent, M3-C07-03):
    - B05 `ch07_naming.dlg` ends on `<<event start_reefball tidecup_opening>>`. The event is declared in `events.json`.
    - The `naming` beat in zone `ch07/tamsule_bell_galleries` runs `{"if_event": "start_reefball", "steps": [{"beat": "reefball_match"}]}`.
    - **Replace only the steps of the beat `reefball_match`.** Today they are a stand-in: `{"set": "ch07_tidecup_played"}` and `{"go": {"location": "ch07/tamsule_bell_galleries", "spawn": "CatchPool"}}`. The stand-in never sets the win.
    - The real match sets `ch07_tidecup_played` always and `ch07_tidecup_won` on a win only, gives its rewards, and returns to the same location and spawn. The first arrival row there plays B07, identical for both results.
  - **Match id:** `tidecup_opening`, the Lead's, not the Goal's `ch07_tidecup_oruvel_sorrin`.
  - **Names, a rename for the Reefball agent** (their files aren't on this branch, so not edited):
    - the opponent is **Sorrin** (captain Ione Sabe), not "Pemakar Terraces";
    - Rhen dives in **Pio's** place;
    - "Noa" and "Old Ama" give way to the sheet's Brann Ollo, Mae Ketter, Dovic Saan and Tull Arro, whom the moorings scene names.
    - Filed as M3-C07-03.
  - **The win-flag rule:** `test_no_story_script_reads_the_win_flag` scans every `.dlg` (except `test/` fixtures and `REWARD_SCRIPTS`, empty today) and every chapter file. `test_after_the_bell_is_the_same_win_or_lose` checks that B07 plays line for line the same.
  - **The B08 bark is cut.** The optional result-aware bark ("Sorrin's through." / "Sorrin's out.") is cut, so no Ch7 text reads the result (§5.5 allows the cut).
  - **Zones, my call.** The Bell's story beats (B04, B05, B07, B09) play in a separate greybox stand-in zone, `ch07/tamsule_bell_galleries`, not as cutscenes in the port:
    - the galleries, the pool and rim, and the moorings need walkable space between the beats;
    - the arena `ch07/tamsule_bell` stays env-art's and the Reefball agent's.
    - Whether the beats fold into the arena later is M3-C07-04's question.
  - **Entry:** Ch6 isn't built, so `ch07/tamsule` is reached from its own `locations.json` row (spawn `RiverMouth`), and an F5 teleport row was added.
  - **Exit:** `ch08/corrow` isn't built, so B10 hands off to the end card. Ch8 swaps the `leave` beat's last step for a `go`.
  - **Staging decisions:**
    - B04 and B05 are split by player control. B04 ends with Rhen on the pool steps and a checkpoint autosave (`Ch07Zone.checkpoint`, §5.1), and walking to the rim plays B05.
    - B03 starts on the market boats by the gantry (a touch trigger). Talking to the gantry-foot bark doesn't start it.
    - The B02 Reefball board-caller has a short bark (the draw, and quiet for the naming). It is not in the sheet's bark list.
    - Liss's line loses its emphasis ("*not looking*"), since the box has no italics yet.
    - The B08 after-match barks are this build's lines (the market and lane barks from the sheet, plus a gantry bark).
    - The moorings litany's boat names after the Gull, the Second Mooring and the Wicklight are this script's: the Tallow Hen, the Brass Thrush and the Low Lantern. So are the families: Ollo, the Ketters, Dovic's brothers and Old Arro.
  - **Ch5 flags:** Ch7 reads `ch05_boat_for_kell`, `ch05_boat_for_oruvel` and `ch05_kept_leaf_boat`. They're declared here; if M3-C05-02 declares them too, keep one row each on merge. B09 takes `pemakar_leaf_boat` from the bag, which does nothing until Ch5 adds the item.
  - **Party:** Rhen, Asha and Toma, with Ysolde in reserve. Liss and Kerrid have no `characters.json` rows yet, so they are stage actors only.
  - **Follow-ups filed:** M3-C07-03 (the Reefball seam and names), M3-C07-04 (environment), M3-C07-05 (shops, inn, shrine and rewards), M3-C07-06 (audio), M3-C07-07 (characters).
  - **Not done here:** glossary rows (§10 item 20, the Lead's); Grades `ch07`, `ch07_afternoon` and `ch07_bell_shade` (Art; the scripts use no `grade=`).

## Review log
