---
id: M4-A2P-112
title: "Story's review of Ch10's cutscene staging (claude/m2-slice, M4-A2P-070/M4-CIN-1304): beats, pauses, who is in frame on each line"
role: cinematics
status: todo
owner_session: ""
depends_on: [M4-A2P-001]
reviewer: narrative
milestone: M4
request-from: narrative
---
## Goal
The Lead asked for this on 2026-10-30. The story track reviewed slice-polish's Ch10 staging on `origin/claude/m2-slice`
against the Ch10 scripts (M4-A2P-001) and the beat sheet (act2_ch10.md §1, §7).

Method:
- each scene's cues are walked in order: cameras from `game/data/cutscene/ch10/*.json` and the layouts' shots;
  speakers' positions from the layout actors and every `@mark`;
- each spoken line is tested against the active shot's field of view;
- waits and lines are summed against §1's minutes.

The static check can't follow `track=` moves, so O02 is judged by eye.

## Notes, most important first
1. **Merge conflict ahead: the farewell-tide's flag.** Your `ch10_farewell_tide.dlg` sets `ch10_tide_witnessed`. The story
   track retired it for the lane name `ch10_farewell_tide_seen`, which ui-menus' codex unlocks on. Take
   `<<set $ch10_farewell_tide_seen = true>>` when you merge. The release-gate change in the same hunk is good: keep it.
2. **B11 dawn gate, R10 frames empty air.** R10 (85 mm, Pell's single) aims at `pell_shell` (−1.1, 1.55, 0.5), which is
   where Pell stood at the end of B06 (`causeway_last_root`). `ch10_dawn_gate` never puts him there, so he starts at the
   layout's `pell_gate` (0.5, 0, 0). His four lines (`ch10_dawn_005`–`008`) then play on an empty close-up. R09's
   `gate_asha` (0.6, 0, 0.4) is also 0.4 m from him. **Fixed by story** on claude/act2-plan: `@mark pell causeway_last_root` at the top of `ch10_dawn_gate`, under the
   fade-in (it walks 1.6 m; the sequencer has no instant place).
3. **B06 causeway, Owa's first line is off frame.** `ch10_causeway_001` plays on R02, the layout's own shot (8, 1.6, 1.5)
   looking at (1, 1.3, 0). Owa at `causeway_gate` (6, 0, 0) is about 38° off its axis, beside the lens. Your own review
   asked for "one held single on the eldest". §7 asks for 50 mm singles for each of her looks. **Fix:** stage R02 in
   reedhollow.json (an R02 single on `causeway_gate`, or one per look) and replace the layout's.
4. **B05 what went up, Pell speaks from behind the lens.** O07 (the party looking up, 50 mm low) faces −x.
   `@mark pell root_walk_exit walk` sends Pell to (126, 0, 0.6), behind the camera, and his line "It is the direction."
   (`ch10_up_003`) is spoken from there. It's the scene's button. **Fixed by story** on claude/act2-plan: the line now comes first, then he walks on.
5. **B09 farewell-tide, Ysolde has no place.** `ch10_tide_001` ("Turn around…") plays on T05 (a 22° single on
   `shore_front`). Ysolde turns Asha by the shoulder, but no mark puts Ysolde there. The chapter lane's `tide_*` marks
   (flow `place_actor party on tide_*`) aren't in the layout or your staging. **Fix:** a `shore_front_ysolde` mark beside
   Asha's, or the `tide_*` set; T05 then frames both.
6. **Pacing: the staged scenes are 3–5× shorter than §1.**
   | Scene | Staged (waits plus talk) | §1 |
   |---|---|---|
   | fen_edge | 0.35 min | 1.5 |
   | dead_channel | 0.24 min | 1.0 |
   | what_went_up | 0.25 min | 1.5 |
   | causeway | 0.51 min | 2.5 |
   | why_swim | 0.57 min | 3.0 |
   | farewell_tide | 0.72 min, plus the player's hold | 3.0 |
   | dawn_gate | 0.68 min | 2.0 |

   Some of §1's minutes are walking and held input, but the holds the beat sheet asks for aren't there yet. Story's
   priorities (pillar 2):
   - **B06:** Owa's look at each of them is the beat. Hold each look at ~2 s, not 1 s, the same length for Kerrid
     (rule 4).
   - **B05:** O06 holds "until the last mote has left the top of frame" (§7). It's 4 s now; time it against stills.
   - **B09:** T03's tilt into the stars and F02 want ~8–10 s each before T04.
   - **B11:** a 2 s beat after "Seventy years." before Pell walks.
7. **Checked and fine:**
   - O05's insert carries Pell's three lines off-screen, as §7 intends (a CU on the roots).
   - O02's `track=toma` keeps the line moving while Pell stops, per §7's "does not stop with Pell"; judge "You coming?"
     on stills.
   - The release gate on the tide is right: the clutch turns at the top note, and the song ends on the release.
   - Every `@camera` and `@mark` id the scripts name exists in your staging or the layout.
8. **Not yours, for chapters:** the party heroes' start positions in each Reedhollow scene come from the flow's `place`
   steps. Without them, `why_swim`'s Asha and `what_went_up`'s Rhen and Ysolde have no known position for framing.

## Acceptance criteria
- [ ] Items 1–5 fixed or answered.
- [ ] Item 6: holds timed against stills, or a reply saying the minutes come from play.
- [ ] Stills of R02, R10, O07 and T05 viewed.

## Review log

## Status after slice-polish's newest Ch10 staging (origin/claude/m2-slice @ a9e826427, 2026-10-30, story re-check)
- **1. Farewell-tide flag:** RESOLVED. Their script sets `ch10_farewell_tide_seen`.
- **2. Dawn gate, R10 empty:** RESOLVED IN STORY'S SCRIPT (`@mark pell causeway_last_root`). It reaches their branch with
  the next integration merge of claude/act2-plan (big22 took act2-plan before the fix).
- **3. B06, Owa's first line off R02:** OPEN. No R02 is in `reedhollow.json` yet; the staging stills (4ad355b8e) cover
  O02, R03, F02, T04 and R07.
- **4. B05, Pell's line from behind O07:** RESOLVED IN STORY'S SCRIPT (the line now comes before his exit). It arrives
  with the same merge as item 2.
- **5. B09, Ysolde has no place:** OPEN. There's still no Ysolde or `tide_*` mark; it waits on M4-CIN-1305 (chapters
  placing the stage actors).
- **6. Pacing:** OPEN. The waits are unchanged. The stills are greybox, before the actors.
