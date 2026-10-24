---
id: M3-C07-02
title: Ch7 "The Tidecup" story dialogue, cutscenes and flow around the Reefball match
role: cinematics
status: todo
owner_session: ""
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
- [ ] The `.dlg` scripts and cutscenes for every story beat, with the flags declared, and `validate_data` and `dlgc --check` clean.
- [ ] The chapter flow in `game/data/flow/chapters/ch07.json`. Until the Reefball scene exists, a stand-in step sets `ch07_tidecup_played`.
- [ ] A test that no story `.dlg` reads `ch07_tidecup_won` except where the reward is given.
- [ ] A headless thread test, port arrival to the Ch8 hand-off, with the stand-in match.

## Notes
- 2026-10-24, the Lead: the Reefball rules engine is M3-RBL-01 (`docs/kb/design/reefball.md`). The story match is `tidecup_opening`: Oruvel (captain Tavi Orse; Rhen dives) against a provisional "Pemakar Terraces", with Oruvel's divers provisionally "Noa" and "Old Ama".
  - **Reconcile those loc rows with act1_ch07.md:** the opponent is the atoll side **Sorrin** (not Tamsule, which wins offscreen), and Rhen takes Pio's place.
  - **Renaming** the loc rows is allowed (the Lead said so).
  - **The outcome is a reward only** (ADR 0020 (h)).
  - **To do here:** the naming-rite cutscene, the match entry and exit flow through SceneRouter/FlowRouting, and the post-match beats.
  - **Not ours:** the match HUD is UI's, and the arena (the water sphere) is env-art's and the PC's.

## Review log
