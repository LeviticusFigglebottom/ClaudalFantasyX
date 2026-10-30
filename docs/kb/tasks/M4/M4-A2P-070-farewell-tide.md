---
id: M4-A2P-070
title: "Stage the farewell-tide (Ch10): the clutch sings, turns its back, the motes lift"
role: cinematics
status: doing
owner_session: slice-polish → cinematics (claude/m2-slice)
depends_on: [M4-A2P-001, M4-A2P-049, M4-A2P-053]
reviewer: narrative
milestone: M4
request-from: lead
---
## Goal
The act's first showpiece (~90 s under `farewell_tide`): the clutch at the tideline at dusk, the song, the turning away, the motes lifting into the stars, Asha unable to look away.

## Acceptance criteria
- [ ] Cutscene data, cameras, timing; stills viewed against the beat sheet.
- [ ] ADR 0041 §3's final bar (no greybox, stand-in or placeholder the player can see or hear).

## Notes
- Filed by the act2-plan track (2026-10-30) from [act2_plan.md](../../plan/act2_plan.md). Plan §2 Ch10.
- Blocked until the Lead tags `act1-complete` (ADR 0203); then `todo`.

- 2026-10-30 cinematics (ADR 0205; the Lead's 09:01 message): staging started on the act2-plan scripts.
  - Shots T01–T06, F02, R07 and R08 and the marks `shore_front` and `lagoon_motes` are in
    `game/data/cutscene/ch10/reedhollow.json` (CutsceneStaging, M4-CIN-1304).
  - ch10_farewell_tide uses the release gate: the clutch turns at the top note (`@anim clutch turn_back`, the group
    anim), and the rite holds until the player lets go.
  - **Waiting on:** the party and Owa as stage actors, and the hold gate with its two prompts (M4-CIN-1305, the
    chapters track); the Kirru models (M4-A2P-053); the score in two parts (M4-CIN-1301, audio). Stills follow once
    the actors stand on the shore.

## Review log
