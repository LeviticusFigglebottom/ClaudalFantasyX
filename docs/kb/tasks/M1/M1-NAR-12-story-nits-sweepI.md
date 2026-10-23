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
