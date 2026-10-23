---
id: M1-NAR-12
title: Story nits from review-sweep-I on NAR-11
role: narrative
status: review
owner_session: "worktree-agent-ae77f8e225d2b48a3"
depends_on: [M1-NAR-11]
milestone: M1
request-from: "cinematics"
---
## Goal
From the review-sweep-I entries (file:line references there).

## Acceptance criteria
- [x] A watch is recorded that Dace's Ch17 logs are never voiced, played back or addressed to Rhen (they would echo the inspiring game's recorded messages from the father)
- [x] E2's 'oil wick' cannot be read as Mother Kell's wick (act3_ending ~:93)
- [x] decisions_log stale lines fixed (~:200, N-02 ~:19)

## Notes
- **Reviewer: cinematics** (+ IP, as in sweep I). Docs only: no `.dlg`, loc or game data changed.
- **S1 (IP, the Ch17 logs).** A review-sweep-I append note on ADR 0022 and decisions_log **N-26** record the watch: the logs are a written ledger, read on screen in Rhen's hands. They are never voiced in Dace's voice, never played back as a recording, a projection or a glimmer-echo, and never addressed to Rhen as a message. Dace's voice is heard only in E2. I also took the reviewer's suggestion: the entry now ends "Let him be one. After the storm" and breaks off (the next page is blank). That keeps the irony and drops the stated promise to come home. Applied to act_outline Ch17 and rhen_sallow.md Act III; N-25 S4 is corrected inline; the ADR note amends the sweep-H S4 quote and its "17 (S4)" row (append-only, a new row).
- **S2.** act3_ending E2: "Dace sees his old lantern ... still the oil burner he fitted and not glimmer (N-02)", plus a parenthesis that Kell's wick is never fitted to it and stays unburned for E7.
- **S3.** decisions_log: N-24's Lead-verdict quote is marked superseded inline (the "like that" wording), and N-02 item 4 now says Asha saw the lantern's twin. Both are added to N-25's Supersedes list.
- **Nits:** Kell's stall is "on Oruvel's second mooring" in rhen_sallow.md too (it said "two hulls along"). vertical_slice.md H06 says "She never says why". The same words in the comment at `game/data/dialogue/ch02/ch02_girl_on_the_beach.dlg:10` are left for the next narrative commit that touches game data (comment-only; this task is docs only).
- Checks: `validate_data` 0/0 (it includes the banned-terms grep), and the full gate below.

## Review log
- 2026-10-23 cinematics (review-sweep-J, fresh reviewer, + IP): **approve with should-fixes.** No blockers.
  - **What I read:**
    - the task;
    - commit 0588945: the ADR 0022 append note, decisions_log N-24/N-25/N-26, act3_ending E2, act_outline Ch17, rhen_sallow.md, vertical_slice.md H06;
    - a repo grep for "go myself", "oil wick", "two hulls along" and "never says so".
  - **Checks:** `validate_data` 0/0, including banned terms.
  - **IP watch.** The watch is sound: a written ledger, never voiced or played back, never addressed to Rhen, with no stated promise to return. The ADR note is append-only and amends the sweep-H row correctly.
  - **E2.** "Still the oil burner he fitted" no longer collides with Kell's wick.
  - **Should-fix:**
    - **S1 (the broken-off entry contradicts the ledger's order).**
      - act_outline.md:176 says the "After the storm" entry breaks off and "the next page is blank". The same paragraph then goes on: "A season later a Hollowmere trader told him … and the entry says only 'Kell. Of course.'"
      - Read in order, a later entry follows a blank page. The same "next page is blank" is in ADR 0022:220 and decisions_log.md:237, while ADR 0022:186 dates the Kell entry to a season after Corrow.
      - Say the broken-off entry is the ledger's **last**, written the night he went after Imra, and move the Kell sentence before it in the outline. Or drop "the next page is blank". Cinematics needs that order to stage the page-turn.
    - **S2 (the "wick" vocabulary is still split).** decisions_log.md:14 (the N-02 answer) still says Dace fitted the lantern "with an oil wick", the phrase S2 removed from E2. decisions_log.md:145 has the Prologue line "as his oil wick catches". Mark them inline (N-26) or reword them to "oil burner", so the Kell-wick watch has one term. Otherwise the next reader repeats the sweep-I confusion.
  - **Nit:** game/data/dialogue/ch02/ch02_girl_on_the_beach.dlg:10 still says "She never says so" (acknowledged, comment-only).
